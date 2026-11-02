"""Offline AFTER_ACTION analysis; never imports or controls a running world."""
from pathlib import Path
import argparse,collections,gzip,hashlib,importlib.util,json
import numpy as np
P=Path(__file__).resolve().parent
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=mod('c_native_captures',P/'battles.py')
def save(path,q):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
def digest(q):return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def passive(out):
 f=next(Path(out).glob('*-PASSIVE.json.gz'));return json.loads(gzip.decompress(f.read_bytes()))
def controls():
 root=P/'evidence/battles/runs';names=['S6-419027-R4','CONTROL-S6-419027-C_SHADOW','CONTROL-S6-419027-C_OFF','S6-419027-C'];raw={};checks={}
 for name in names:raw[name]=b.load(root/name/'attempt1')[0]
 for a,z,label in [(names[0],names[1],'R4vsShadow'),(names[2],names[3],'COffOn')]:
  checks[label+'NativeFinalExact']=raw[a]['final']==raw[z]['final'];checks[label+'PassiveExact']=passive(root/a/'attempt1')==passive(root/z/'attempt1')
 result={'status':'PASS'if all(checks.values())else'FAIL','checks':checks,'hashes':{n:{'final':digest(raw[n]['final']),'passive':digest(passive(root/n/'attempt1'))}for n in names},'products':b.products(),'meaning':'Candidate diagnostic read/drain and physical test probes do not alter native final state/RNG; SHADOW does not consume proposals.'};save(P/'evidence/battles/CONTROLS.json',result);print(json.dumps(result));return result
def lineage(raw, verified_noise=()):
 aa=raw['trackCLineage'];counts=collections.Counter();events=[];live={};switches=[];last_by_physical={};life=collections.defaultdict(list);labels={q['uid']:q for q in aa['labels']};duplicate_pairs_seen=set();death_steps={q['id']:min((s['step']for s in q['states']if not s['alive']),default=None)for q in aa['seeker']}
 def physical_class(uid):
  q=labels.get(uid,{})
  if any(str(k).startswith(('OWN_SAM:','OWN_RAM:'))for k in q.get('keys',[])):return'OWN_LAUNCHED_INTERCEPTOR'
  if any(str(k).startswith('ASM:')for k in q.get('keys',[])):return'TARGET_ASM'
  return q.get('kind','UNRECORDED')
 for q in aa['lifecycle']:life[q['step']].append(q)
 def key(q):return(q['ownerEntityId'],q['store'],q['trackId'])
 for q in aa['records']:
  counts['allRfAssociationRecords']+=1
  if not q['fields']:counts['noEchoNoAssignmentDiagnostics']+=1;continue
  counts['actualMeasuredRfRecords']+=1
  if q['lineageStatus']!='EXACT_RF_OBJECT_OR_EXACT_MEASURED_POLAR_CLONE':
   proven=[v for v in verified_noise if v['exactOriginalRecord']==q]
   if proven:
    assert len(proven)==1 and q['physicalUid']is None and proven[0]['physicalUid']is None
    counts['receiverProcessingNoiseMeasurementsNoReflector']+=1
    events.append({'event':'NATIVE_RECEIVER_PROCESSING_FALSE_ALARM_NO_REFLECTOR',**q,'exactGeneratorReplayProof':proven[0]})
    if q['type']=='UPDATE'and q['decision']in ['ACCEPT','CREATE']:
     counts['acceptedFilterUpdates']+=1;counts['acceptedFilterUpdates:'+q['store']]+=1
    # This really is a native noise-file birth, not a reflector or a label.
    # Keep the original UNLINKED raw record and exact replay proof; never invent a UID.
    continue
   counts[q['lineageStatus']]+=1;events.append({'event':'UNRESOLVED_RF_LINEAGE',**q});continue
  counts['exactPhysicalMeasurementFilterLinks']+=1
  if q['decision']not in ['ACCEPT','CREATE','ASSOCIATE_WITHOUT_HIT']:continue
  k=key(q);after=q['after']or{};before=q['before']or{};uid=q['physicalUid'];t=q['timeS']
  if q['knownOwnLaunch']is True and physical_class(uid)=='TARGET_ASM':counts['physicalAsmIncorrectlyFlaggedOwnLaunch']+=1;events.append({'event':'ACTUAL_ASM_OWN_SOURCE_FLAG_MISMATCH',**q})
  # Apply recorded native DROP transitions, never guess target identity from geometry.
  for step in [s for s in life if s<=q['step']]:
   for e in life.pop(step):
    if e['event']=='DROP':live.pop(key(e),None)
    elif key(e)in live:live[key(e)].update(confirmed=e['confirmed'],memory=e['memory'],reacquiring=e['reacquiring'])
  old=live.get(k,{}).get('uid')
  if q['decision']=='ASSOCIATE_WITHOUT_HIT':
   counts['metadataAssociationsWithoutAdditionalFilterHit']+=1
   if old and old!=uid:counts['metadataOnlyAssociationDisagreesWithFilterLineage']+=1;events.append({'event':'METADATA_ONLY_ASSOCIATION_DIFFERENCE_NO_KF_UPDATE',**q,'lastActualFilterPhysicalUid':old})
   continue
  if q['type']!='UPDATE':continue
  counts['acceptedFilterUpdates']+=1
  counts['acceptedFilterUpdates:'+q['store']]+=1
  if q['store'].startswith('C55:'):
   counts['ownLaunchLocalMeasurements'if q['knownOwnLaunch']is True else'nonOwnLocalMeasurements']+=1
   if not isinstance(after.get('ownFireEvidence'),bool):counts['localProtectionFieldMissing']+=1
  prior_alive=q['priorPhysicalAlive']if q['priorPhysicalUid']==old else None
  if old and prior_alive is None:
   ids=[int(s[4:])for s in labels.get(old,{}).get('keys',[])if s.startswith('ASM:')and s[4:].isdigit()]
   if len(ids)==1 and ids[0]in death_steps:
    death=death_steps[ids[0]]
    if death is None or q['step']<death-1:prior_alive=True
    elif q['step']>=death:prior_alive=False
  q={**q,'rawLastAssociationPhysicalUid':q['priorPhysicalUid'],'priorPhysicalUid':old,'priorPhysicalAlive':prior_alive,'priorContract':'Last actual KF update, not SPQ metadata association; exact native liveness when label matches, otherwise initial-ASM after-action death window. Boundary ambiguity remains null.'}
  if q['knownOwnLaunch']is False and after.get('ownFireEvidence')is True:counts['nonOwnMeasurementProtectedContamination']+=1;events.append({'event':'OWN_FIRE_CONTAMINATION',**q})
  if q['knownOwnLaunch']is True and after.get('ownFireEvidence')is False:counts['ownLaunchProtectionLost']+=1;events.append({'event':'OWN_FIRE_PROTECTION_LOST',**q})
  if old and old!=uid:
   cat='LIVE_PHYSICAL_REASSIGNMENT'if q['priorPhysicalAlive']is True else'POST_TERMINAL_FILE_REUSE'if q['priorPhysicalAlive']is False else'PREDECESSOR_PHYSICAL_LIVENESS_NOT_RECORDED';counts[cat]+=1;entry={'event':cat,**q};events.append(entry)
   if q['priorPhysicalAlive']:
    classification='firmPhysicalFalseMerge'if before.get('confirmed')else'tentativePhysicalReassignment';counts[classification]+=1;counts[classification+':'+q['store']+':'+physical_class(old)+'->'+physical_class(uid)]+=1
    for s in switches:
     if s['step']==q['step']and s['ownerEntityId']==q['ownerEntityId']and s['store']==q['store']and s['priorPhysicalUid']==uid and s['physicalUid']==old and s['trackId']!=q['trackId']:
      counts['reciprocalIdSwapSameEpoch']+=1;counts['firmReciprocalIdSwap'if before.get('confirmed')and(s['before']or{}).get('confirmed')else'tentativeReciprocalSwap']+=1;events.append({'event':'RECIPROCAL_ID_SWAP','first':s,'second':q})
    switches=[s for s in switches if s['step']>=q['step']];switches.append(q)
  elif old==uid and(before.get('memActive')or before.get('reacquiring')):counts['nativeMemoryReacquisitionSamePhysical']+=1;events.append({'event':'NORMAL_NATIVE_MEMORY_REACQUISITION',**q})
  physical_key=(q['ownerEntityId'],q['store'],uid)
  if q['decision']=='CREATE'and physical_key in last_by_physical:
   prior_key=last_by_physical[physical_key]
   if prior_key not in live:counts['reinitializedAfterNativeDrop']+=1
  firm=bool(after.get('confirmed'));memory=bool(after.get('memActive'));reacquiring=bool(after.get('reacquiring'))
  if firm and not memory and not reacquiring:
   for other,r in live.items():
    # C55 firing freshness .22s is the unchanged native policy, not a new tracking gate.
    fresh=not q['store'].startswith('C55:')or t-r['lastS']<=.22
    if other!=k and other[:2]==k[:2]and r['uid']==uid and r['confirmed']and not r['memory']and not r['reacquiring']and fresh:
     signature=(*sorted([other,k]),uid)
     if signature not in duplicate_pairs_seen:counts['simultaneouslyFirmSamePhysicalFilePairs']+=1;events.append({'event':'FIRM_DUPLICATE_FILES_SAME_OWNER_STORE','otherFile':list(other),'current':q});duplicate_pairs_seen.add(signature)
  live[k]={'uid':uid,'confirmed':firm,'memory':memory,'reacquiring':reacquiring,'lastS':t,'duplicates':live.get(k,{}).get('duplicates',set())};last_by_physical[physical_key]=k
 trace=(aa.get('candidateTrace')or{}).get('records',[]);counters=collections.Counter();hold_since={};hold_max=collections.defaultdict(float)
 for q in trace:
  counters[q['event']]+=1
  if 'heldTracks'not in q:continue
  namespace=(q.get('ownerEntityId'),q.get('mountId'),q['event']);held=set(q['heldTracks']);now=q['timeS']
  for k,at in list(hold_since.items()):
   if k[:3]==namespace:
    hold_max[q['event']]=max(hold_max[q['event']],now-at)
    if k[3]not in held:hold_since.pop(k)
  for tid in held:hold_since.setdefault((*namespace,tid),now)
 egress=[];seeker={q['id']:q for q in aa['seeker']}
 for target in raw['targets']:
  if not target['alive']:continue
  q=seeker.get(target['id'],{});eg=q.get('qualifiedEgress')or{};last=eg.get('lastAccepted');members=(last or{}).get('members',[]);names=' '.join(members).upper();debug=str((last or{}).get('debugId','')).upper();is_decoy=any(s in names+' '+debug for s in ['NULKA','CHAFF'])
  exclusively_decoy=bool(members)and all(any(s in str(m).upper()for s in ['NULKA','CHAFF','SEA_CLUTTER'])for m in members)and is_decoy
  if exclusively_decoy and eg.get('trackValid')and eg.get('guidance')=='RF_EKF':cause='DECOY_LURE';reason='Last accepted signal comprised decoy/clutter and native seeker retained RF guidance at egress.'
  elif eg.get('seekerOn')and(not eg.get('trackValid')or eg.get('mode')in ['SEARCH','REACQUIRE']):cause='SEEKER_LOSS';reason='Native seeker had no valid track or remained in search/reacquisition at qualified egress.'
  else:cause='OTHER';reason='No unambiguous decoy-only causal signal; mixed/other RF or coast retained. No hidden-state causal guess.'
  egress.append({'id':target['id'],'cause':cause,'reason':reason,'qualified':eg,'acceptedSignalTransitions':q.get('accepted',[]),'nativeStateTransitions':q.get('states',[])})
 return {'counts':dict(counts),'candidateEvents':dict(counters),'maximumRecordedHoldEpisodeS':dict(hold_max),'egress':egress,'events':events,'limitations':['Physical labels are AFTER_ACTION only; no geometric/truth guess for an unmatched measurement.','Only actual native UPDATE corrections advance filter physical lineage; SPQ preferred metadata/no-extra-hit associations are separate, never a fabricated KF update.','Separate owners and C55 mount stores are never counted as duplicates.','A known-live physical reassignment of an already-confirmed file is counted separately from tentative reassignment, native-memory reacquisition and terminal reuse. Unrecorded liveness is not assumed dead.','Reciprocal same-epoch swaps and unique duplicate file pairs are separate counters. C55 duplicate freshness uses native .22s.','No RF echo / NO_ASSIGNMENT diagnostics are reported separately and do not pretend to be measurements.']}
def all_lineage(partial=False):
 rows=[];closure_path=P/'NOISE_ORIGIN_CLOSURE.json';closure=json.loads(closure_path.read_text())if closure_path.exists()else None
 if closure:
  assert closure['status']=='PASS'and closure['resolvedMeasurements']==10 and closure['physicalUidInvented']is False
  assert hashlib.sha256((P/closure['sourceProof']).read_bytes()).hexdigest()==closure['sourceProofSha256']
  proof=json.loads((P/closure['sourceProof']).read_text());assert proof['status']=='PASS'and all(all(r['checks'].values())for r in proof['rows'])
 for job in b.prepare()['jobs']:
  out=b.selected_out(job['id'])
  if not(out/'EXECUTION.json').exists():
   assert partial,job['id'];continue
  receipt=json.loads((out/'EXECUTION.json').read_text())
  if receipt['status']!='VALID':
   assert partial,receipt;continue
  raw,metric=b.load(out);detail=lineage(raw,[r for r in closure['rows']if r['id']==job['id']]if closure else []);blob=gzip.compress(json.dumps(detail,ensure_ascii=False,separators=(',',':')).encode(),6,mtime=0);dest=out/'LINEAGE_ANALYSIS.json.gz';dest.write_bytes(blob);rows.append({'id':job['id'],'product':job['product'],'counts':detail['counts'],'candidateEvents':detail['candidateEvents'],'maximumRecordedHoldEpisodeS':detail['maximumRecordedHoldEpisodeS'],'egress':[{k:v for k,v in q.items()if k not in ['acceptedSignalTransitions','nativeStateTransitions']}for q in detail['egress']],'analysisSha256':hashlib.sha256(blob).hexdigest()})
 result={'schema':'AEGIS_TRACK_C_AFTER_ACTION_AUDIT_1','runs':len(rows),'expectedRuns':120,'complete':len(rows)==120,'rows':rows,'totals':{prod:dict(sum((collections.Counter(r['counts'])for r in rows if r['product']==prod),collections.Counter()))for prod in ['R4','C']},'noTacticalTruthBackfeed':True,'noReflectorOriginClosureSha256':hashlib.sha256(closure_path.read_bytes()).hexdigest()if closure else None};save(P/'LINEAGE_RESULTS.json',result);print(json.dumps({'lineageRuns':len(rows),'totals':result['totals']}))
def exact_worse(d):
 d=np.array(d,dtype=float);d=d[d!=0]
 if not len(d):return 1.0
 assert len(d)<=24,'Refuse infeasible enumeration rather than use a different test'
 numbers=np.arange(1<<len(d),dtype=np.uint32);sums=np.zeros(len(numbers))
 for i,v in enumerate(d):sums+=np.where((numbers>>i)&1,v,-v)
 return float(np.mean(sums>=d.sum()))
def paired_analysis(pairs,seeds,strata):
 metrics=['leakers','damagingHitRounds','kills','egress','floodM3'];blocks=np.array([[sum(q['C'][k]-q['R4'][k]for q in pairs if q['seed']==s)for k in metrics]for s in seeds]);rng=np.random.default_rng(20261102);sample=np.zeros((200000,len(metrics)))
 for indices in strata:
  values=blocks[indices];chosen=rng.integers(0,len(values),(200000,len(values)));sample+=values[chosen].sum(axis=1)
 cis=np.quantile(sample,[.025,.975],axis=0).T;out={}
 for i,k in enumerate(metrics):
  delta=float(blocks[:,i].sum());ci=cis[i].tolist();p=exact_worse(blocks[:,i]);decision='CLEARLY_WORSE'if(delta>0 and p<=.05)or ci[0]>0 else'WITHIN_USER_SAMPLING_VARIATION_OR_BETTER'if ci[0]<=0<=ci[1]or ci[1]<=0 else'INCONCLUSIVE'
  out[k]={'R4Total':sum(q['R4'][k]for q in pairs),'CTotal':sum(q['C'][k]for q in pairs),'differenceCMinusR4':delta,'seedBlockDifferences':blocks[:,i].tolist(),'oneSidedExactWorseP':p if i<2 else None,'paired95PercentIntervalForTotalDifference':ci,'decision':decision if i<2 else'DESCRIPTIVE_ONLY_NOT_USED_FOR_APPROVAL','primary':i<2}
 return {'pairedCases':len(pairs),'metrics':out,'primaryPass':all(out[k]['decision']=='WITHIN_USER_SAMPLING_VARIATION_OR_BETTER'for k in metrics[:2]),'hpUsedForApproval':False,'analysisSeed':20261102,'bootstrapDraws':200000,'method':'Frozen TRACK-B seed-block sign flip and stratified paired bootstrap; user sampling-variation decision, not formal noninferiority.'}
def statistics():
 rows=[]
 for job in b.prepare()['jobs']:rows.append(b.load(b.selected_out(job['id']))[1])
 assert len(rows)==120 and len({q['id']for q in rows})==120
 assert all(sum(q['initialCount']for q in rows if q['product']==prod)==320 for prod in ['R4','C'])
 lookup={(q['scenario'],q['seed'],q['product']):q for q in rows};pairs=[];plan=json.loads((P/'PLAN.json').read_text())
 for scenario,n in plan['scenarios'].items():
  if scenario=='D1':continue
  for seed in plan['seeds20'][:n]:pairs.append({'scenario':scenario,'seed':seed,**{p:lookup[(scenario,seed,p)]for p in ['R4','C']}})
 result=paired_analysis(pairs,plan['seeds20'],[list(range(10)),list(range(10,20))]);result.update(schema='AEGIS_TRACK_C_FROZEN_COMBAT_STATISTICS_1',products=b.products(),pairs=pairs,allInitialAsmsResolved=True);save(P/'STATISTICS.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['pairs','products']}))
def d1():
 paths={'R4':P/'evidence/extra-r4-d1/friendly/ciws-d1.jsonl','C':P/'evidence/regression/d1/friendly/ciws-d1.jsonl'};source={p:[json.loads(l)for l in path.read_text().splitlines()]for p,path in paths.items()};plan=json.loads((P/'PLAN.json').read_text());pairs=[]
 for seed in plan['d1Seeds']:
  pair={'seed':seed,'scenario':'D1'}
  for product in ['R4','C']:
   q=next(x for x in source[product]if x['case']['seed']==seed);assert len(q['result']['targets'])==1 and not q['result']['targets'][0]['alive'],'D1_MUST_REACH_NATIVE_TERMINAL'
   hits=[e['hit']for e in q['events']if e['kind']=='SHIP_IMPACT'];assert len(hits)==len(q['after']['hits']);contacts=[h for h in hits if not h.get('miss')];damaging=[h for h in hits if(h.get('dmg')or 0)>0 and not h.get('miss')];target=q['result']['targets'][0];cause=target['reason'];kill=cause in ['INTERCEPT_KILL','INTERCEPT_STRUCTURAL_FAILURE','PHALANX_KILL','DELAYED_STRUCTURAL_FAILURE','WARHEAD_AIRBURST'];leaker=bool(contacts)
   assert kill or leaker or hits or cause,'UNCLASSIFIED_D1_NATIVE_TERMINAL'
   pair[product]={'leakers':int(leaker),'damagingHitRounds':len(damaging),'kills':int(kill),'egress':0,'floodM3':q['after']['health']['flood']['summary']['waterM3'],'legacyShipHitsCounter':q['result']['shipHits'],'explicitMissCallbacks':sum(bool(h.get('miss'))for h in hits),'signatureSha256':q['signatureSha256'],'globalRng':q['after']['rng'],'endStep':q['after']['step'],'nativeCause':cause,'nativeHitRecords':hits,'ramOrCiwsUsed':q['result']['ciwsUsed'],'gunShots':q['result']['shots']}
  pairs.append(pair)
 result=paired_analysis(pairs,plan['d1Seeds'],[list(range(30))]);result.update(schema='AEGIS_TRACK_C_D1_PAIRED_STATISTICS_1',pairs=pairs,products=b.products(),allInitialAsmsNativeTerminal=True,sourceHashes={p:hashlib.sha256(path.read_bytes()).hexdigest()for p,path in paths.items()},originalLegacyCounterTotals={p:sum(q[p]['legacyShipHitsCounter']for q in pairs)for p in ['R4','C']},contract='D1_ANALYSIS_CONTRACT.json');save(P/'D1_STATISTICS.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['pairs','products']}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('task',choices=['controls','lineage','statistics','d1']);ap.add_argument('--partial',action='store_true');a=ap.parse_args();{'controls':controls,'lineage':lambda:all_lineage(a.partial),'statistics':statistics,'d1':d1}[a.task]()
