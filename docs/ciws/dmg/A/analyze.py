"""Post-process immutable native evidence. No game execution or coefficient fitting."""
from pathlib import Path
import json,csv,math,collections,gzip,statistics,hashlib
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence';A=P/'analysis';A.mkdir(exist_ok=True)
def read(name):
 f=E/name
 if f.exists():return [json.loads(s)for s in f.open()if s.strip()]
 if f.with_suffix(f.suffix+'.gz').exists():return [json.loads(s)for s in gzip.open(str(f)+'.gz','rt')if s.strip()]
 return []
def save(name,x): (A/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def csvsave(name,rows):
 if not rows:return
 with(A/name).open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def spans(rows,pred):
 out=[];start=None;last=None
 for r in rows:
  yes=pred(r)
  if yes and start is None:start=r['azDeg']
  if not yes and start is not None:out.append([start,last]);start=None
  last=r['azDeg']
 if start is not None:out.append([start,last])
 return out
arcs=[];arcRows=[]
for f in sorted(E.glob('arc-*.json')):
 d=json.loads(f.read_text());rows=d['rows'];info={k:d[k]for k in ['mountId','label','hardpoint','axis','registration','trainHalfRad','arcCenter']};info['elevationDeg']=rows[0]['elDeg'];info['source']=str(f.relative_to(P));info['blockedIntervals']={key:spans(rows,lambda x:bool(x[key]))for key in ['axis2','axis300','muzzle2','muzzle300']};info['nativeBlockedIntervals']=spans(rows,lambda x:not x['native']['ok']);info['forward']={key:[s for s in val if s[0]<=0<=s[1]]for key,val in info['blockedIntervals'].items()};info['zero']=next(x for x in rows if x['azDeg']==0);arcs.append(info)
 for row in rows:
  arcRows.append({'mount':d['mountId'],'elevationDeg':row['elDeg'],'azDeg':row['azDeg'],**{k+'_hit':row[k]['name']if row[k]else''for k in ['axis2','axis300','muzzle2','muzzle300']},**{k+'_distanceM':row[k]['distanceM']if row[k]else''for k in ['axis2','axis300','muzzle2','muzzle300']},'nativeOk':row['native']['ok'],'nativeReason':row['native']['reason']})
save('arc-summary.json',arcs);csvsave('arcs-0.1deg.csv',arcRows)
both=[]
for el in[-1,0,2,5]:
 paths=[E/f'arc-{i}-{el}.json'for i in[0,1]]
 if not all(p.exists()for p in paths):continue
 ds=[json.loads(p.read_text())for p in paths];rs=[{'azDeg':r['azDeg'],'a':r,'b':s}for r,s in zip(ds[0]['rows'],ds[1]['rows'])if -15<=r['azDeg']<=15]
 both.append({'elevationDeg':el,'native':spans(rs,lambda r:not r['a']['native']['ok']and not r['b']['native']['ok']),**{k:spans(rs,lambda r:bool(r['a'][k])and bool(r['b'][k]))for k in ['axis2','axis300','muzzle2','muzzle300']}})
save('both-mounts-forward.json',both)
def evs(d,k):return [x for x in d['events']if x['kind']==k]
def first(xs,pred=lambda x:True):return next((x for x in xs if pred(x)),None)
def ts(x):return x['tS']if x else None
def sumrounds(d,k):return sum(x['rounds']for x in evs(d,k))
def fc_components(e):
 # Exact arithmetic from native phalanxFireControlGate and unmodified model.
 # Logs preserve its real ready result; predicted-miss rejection is inferred
 # only when the independently calculable centre gate passed, never invented.
 r=max(1,e.get('rangeM')or 1);h=1.35 if e['engaged']else 1
 center=min(2.10,max(.55,.42+(r*3.0*.0005)*.32))*h
 err=math.tan(min(math.radians(20),abs(e['turretErrorRad']or 0)))*r
 if not e['solution']:reason='NO_SOLUTION'
 elif err>center:reason='TURRET_CENTER_ERROR' # predicted miss may also fail
 elif not e['ready']:reason='PREDICTED_MISS_ONLY'
 else:reason='READY'
 return {'centerErrorM':err,'centerGateM':center,'reason':reason}
def case_summary(d):
 e=d['events'];res=d['result'];case=d['case'];mounts=d['after']['mounts'];guns={m['id']for m in mounts if m['type']=='GUN'};gun=next(iter(guns),None);ram=next((m['id']for m in mounts if m['type']=='RAM'),None);fc=evs(d,'FIRE_CONTROL_GATE');states=evs(d,'CIWS_STATE');gunfc=[x for x in fc if x['mount']in guns];fc_reasons=collections.Counter(fc_components(x)['reason']for x in gunfc)
 gunfire=evs(d,'CIWS_FIRE');ramfire=evs(d,'RAM_AMMO');ramends=[x for x in evs(d,'WEAPON_END')if x['key'].startswith('RAM:')];target_result=res['targets'][0]['reason']if res['targets']else None
 def state(m,s):return ts(first(states,lambda x:x['mount']==m and x['state']==s))
 primary={m['id']:{x['trackId']for x in states if x['mount']==m['id']and x['trackId']is not None}for m in mounts}
 audits=[x for x in evs(d,'CONTACT_AUDIT')if x.get('localId')in primary.get(x['mount'],set())];reasons=collections.Counter(x['reason']for x in audits);impact=first(evs(d,'SHIP_IMPACT'));hp=first(evs(d,'HP_CHANGE'));confirmed=first(evs(d,'TRACK_STATE'),lambda x:x['confirmed']and x['classification']=='ASM')
 gunVeto=first(audits,lambda x:x['mount']in guns and x['reason'].startswith('PROTECTED'));ramVeto=first(audits,lambda x:x['mount']==ram and x['reason'].startswith('PROTECTED'));entered3=any(x['thresholdKm']==3 for x in evs(d,'RANGE_CROSSING'))
 if impact and gunVeto:category='PROTECTED_FILE_VETO_BEFORE_IMPACT'
 elif not gunfire and not impact and target_result in ['INTERCEPT_KILL','INTERCEPT_STRUCTURAL_FAILURE','DELAYED_STRUCTURAL_FAILURE']:category='SEARAM_BEFORE_3KM'if not entered3 else 'SEARAM_INSIDE_3KM_BEFORE_GUN_RELEASE'
 elif gunfire:category='GUN_INTERMITTENT_RELEASE' if fc_reasons['TURRET_CENTER_ERROR']+fc_reasons['PREDICTED_MISS_ONLY'] else 'GUN_RELEASE'
 elif any(x['reason'] in ['DIRECTION_BLOCKED','TRAVERSE_BLOCKED']for x in audits if x['mount']==gun):category='GEOMETRY_BLOCKED_NO_GUN_FIRE'
 elif gunfc:category='FIRE_CONTROL_GATE_NO_GUN_FIRE'
 else:category='LOCAL_TRACK_OR_THREAT_GATE_NO_GUN_FIRE'
 return {'ship':case['ship'],'bearing':case['bearing'],'seed':case['seed'],'shipHits':res['shipHits'],'hp':res['hpAfter'],'alive':res['shipAlive'],'gunRounds':sumrounds(d,'CIWS_FIRE'),'ramRounds':sumrounds(d,'RAM_AMMO'),'legacyCiwsUsed':res['ciwsUsed'],'samLaunches':sum(x['type']=='SAM'for x in evs(d,'WEAPON_LAUNCH')),'firstTrackS':ts(first(evs(d,'TRACK_STATE'))),'confirmedAsmS':ts(confirmed),'gunFirstAcceptedMeasurementS':ts(first(evs(d,'LOCAL_MEASUREMENT'),lambda x:x['mount']==gun and x['accepted'])),'gunFirstCueS':ts(first(states,lambda x:x['mount']==gun and x['cue']is not None)),'gunSearchS':state(gun,'SEARCH'),'gunTrackS':state(gun,'TRACK'),'gunEngageS':state(gun,'ENGAGE'),'firstGunFireS':ts(first(gunfire)),'ramSearchS':state(ram,'SEARCH'),'ramTrackS':state(ram,'TRACK'),'firstRamFireS':ts(first(ramfire)),'ramEndReasons':'|'.join(x['reason']or''for x in ramends),'targetEndReason':target_result,'impactS':ts(impact),'impactPart':impact['hit']['part']if impact else None,'category':category,'gunFcReadySamples':fc_reasons['READY'],'gunFcCenterRejectedSamples':fc_reasons['TURRET_CENTER_ERROR'],'gunFcPredictedOnlyRejectedSamples':fc_reasons['PREDICTED_MISS_ONLY'],'firstGunProtectedVetoS':ts(gunVeto),'firstRamProtectedVetoS':ts(ramVeto),'entered3km':entered3,'selectedLocalIds':{m:sorted(v)for m,v in primary.items()},'auditTransitions':dict(reasons),'rng':d['after']['rng'],'signatureSha256':d['signatureSha256']}
c1=read('c1.jsonl');d1=read('d1.jsonl');controls=read('controls.jsonl')
byseed={d['case']['seed']:d for d in d1};protection=[]
for name in['protection.jsonl','protection-hp0.jsonl']:
 for d in read(name):
  original=byseed[d['case']['seed']];events=[e for e in d['events']if e['kind']=='PROTECTION_ASSOCIATION'];mountEvents=[]
  for m in[1,2]:
   selected={e['trackId']for e in d['events']if e['kind']=='CIWS_STATE'and e['mount']==m and e['trackId']is not None};own=next((e for e in events if e['mount']==m and e['localId']in selected and e['ownFireEvidence']and e['sourceOwn']),None);revert=next((e for e in events if own and e['step']>own['step']and e['localId']==own['localId']and e['sourceKey']=='ASM:2'and e['ownFireEvidence']),None);mountEvents.append({'mount':m,'ownAssociated':own,'asmReturnsWithOwnFlag':revert})
  protection.append({'seed':d['case']['seed'],'nativeSignatureEqual':d['signatureSha256']==original['signatureSha256'],'rngEqual':d['after']['rng']==original['after']['rng'],'source':'evidence/'+name+'.gz','events':mountEvents})
save('protection-causality.json',protection)
for name,ds in [('c1',c1),('d1',d1),('controls',controls)]:
 rows=[case_summary(d)for d in ds];save(name+'-cases.json',rows);csvsave(name+'-cases.csv',[{k:(json.dumps(v,ensure_ascii=False)if isinstance(v,(dict,list))else v)for k,v in r.items()}for r in rows])
 if name=='c1':
  groups=[]
  for angle in[0,-1,1,-2,2,-5,5,-10,10]:
   rs=[r for r in rows if r['bearing']==angle]
   if rs:groups.append({'bearing':angle,'n':len(rs),'firingCases':sum(r['gunRounds']>0 for r in rs),'gunRoundsSum':sum(r['gunRounds']for r in rs),'gunRoundsMean':statistics.mean(r['gunRounds']for r in rs),'shipHits':sum(r['shipHits']for r in rs),'hpMean':statistics.mean(r['hp']for r in rs),'hpZero':sum(r['hp']==0 for r in rs)})
  save('c1-sensitivity.json',groups);csvsave('c1-sensitivity.csv',groups)
 if name=='d1':save('d1-classification.json',dict(collections.Counter(r['category']for r in rows)))
 timelineKinds={'TRACK_STATE','CONTACT_AUDIT','CIWS_STATE','DIRECTION_BLOCK','RAM_AMMO','CIWS_FIRE','WEAPON_LAUNCH','WEAPON_END','INTERCEPT_RESULT','PHALANX_HIT','RANGE_CROSSING','HP_CHANGE','VLS_COOKOFF'}
 for d in ds:
  timeline=[]
  for e in d['events']:
   if e['kind']in timelineKinds:timeline.append({'step':e['step'],'timeS':e['tS'],'kind':e['kind'],'data':json.dumps({k:v for k,v in e.items()if k not in['step','tS','kind']},ensure_ascii=False,separators=(',',':'))})
  if name!='c1':csvsave(f'{name}-{d["case"]["seed"]}-timeline.csv',timeline)
damage=[]
for group,ds in [('d1',d1),('controls',controls)]:
 for d in ds:
  if not evs(d,'SHIP_IMPACT'):continue
  h=evs(d,'SHIP_IMPACT')[0]['hit'];hp=first(evs(d,'HP_CHANGE'));health=d['after']['health'];status=hp.get('status',{})if hp else{};trace=d['after']['blastTraces'][0]if d['after']['blastTraces']else{};impacts=evs(d,'DAMAGE_IMPACT_AUTHORITY')+evs(d,'DAMAGE_IMPACT_COMPAT');parts=impacts[0]['parts']if impacts else h.get('blastParts',[]);blast={x['name']:x for x in trace.get('damagePacket',{}).get('moduleDamage',[])};components=[]
  for part in parts:
   b=blast.get(part['name'],{});components.append({'name':part['name'],'mergedDamageRaw':part['dmg'],'authorityBlastDamageRaw':b.get('dmg',0),'otherMergedKineticRaw':part['dmg']-b.get('dmg',0),'appliedModuleDeltaBeforeClamp':part['dmg']*3.5,'moduleDamageAfter':health['modules'].get(part['name']),'blastChannels':b.get('channels',{}),'cellIds':b.get('cells',[])})
  req=first(evs(d,'COMPARTMENT_BLAST'));req=req.get('request',{})if req else{};q={'group':group,'seed':d['case']['seed'],'ship':d['case']['ship'],'hp':d['result']['hpAfter'],'impactTimeS':ts(first(evs(d,'SHIP_IMPACT'))),'impactPart':h.get('impactPart'),'detonationPart':h.get('part'),'impactPointM':h.get('impactPoint'),'detonationPointM':trace.get('event',{}).get('detonationPoint'),'charge':trace.get('charge'),'ledger':trace.get('ledger'),'nativeStatus':status,'statusTerms':{'hull':status.get('hullStructuralDamage',0)*1.2,'propulsion':status.get('propulsion',0)*.4,'power':status.get('power',0)*.3,'cdc':health['modules'].get('CDC(전투지휘실)',0)*.1},'survival':health['survival'],'floodSummary':health['flood']['summary'],'floodEvents':health['flood']['events'],'strengthSummary':health['strength']['summary'],'strengthEvents':health['strength']['events'],'fireSummary':health['control']['summary'],'fireEvents':health['control']['events'],'vlsCookoffEvents':evs(d,'VLS_COOKOFF'),'vlsFinalIncidents':{k:[{'i':i,'incident':c.get('incident')}for i,c in enumerate(v)if c.get('incident')]for k,v in d['after']['vls'].items()},'nativeImpactAccepted':[x['accepted']for x in impacts],'genericExplosionMassPassedToStrengthKg':[x.get('explosiveMassKg')for x in health['strength']['events']],'ignitionAudit':h.get('ignitionAudit'),'damageChannels':components,'legacyBlastComparison':h.get('legacyBlastComparison'),'rawSource':f'evidence/{group}.jsonl.gz (seed {d["case"]["seed"]})'};damage.append(q)
save('damage-cases.json',damage)
csvsave('damage-summary.csv',[{'group':q['group'],'ship':q['ship'],'seed':q['seed'],'hp':q['hp'],'impactS':q['impactTimeS'],'impactPart':q['impactPart'],'detonationPart':q['detonationPart'],'sumModuleRaw':sum(x['mergedDamageRaw']for x in q['damageChannels']),'authorityBlastRaw':sum(x['authorityBlastDamageRaw']for x in q['damageChannels']),'kineticResidualRaw':sum(x['otherMergedKineticRaw']for x in q['damageChannels']),'hpWeightedSumBeforeClamp':sum(q['statusTerms'].values()),**{k+'Term':v for k,v in q['statusTerms'].items()},'floodM3':q['floodSummary']['waterM3'],'burning':q['fireSummary']['burning'],'cookoffs':len(q['vlsCookoffEvents']),'survivalIrreversible':q['survival']['irreversible'],'survivalLost':q['survival']['lost'],'energyClosureErrorJ':q['ledger'].get('closureErrorJ')}for q in damage])
historical={}
for f in (R/'docs/gun/B2/phase1/evidence/g7').glob('worker*.jsonl'):
 for ln,s in enumerate(f.open(),1):
  d=json.loads(s)
  if not d['on']and d['count']==1:historical[(d['ship'],d['bearing'],d['seed'])]={**d,'sourceFile':str(f.relative_to(R)),'sourceLine':ln}
comp=[]
for d in c1+d1:
 c=d['case'];old=historical.get((c['ship'],c['bearing'],c['seed']))
 if not old:continue
 keys=['seconds','shipHits','shots','ciwsUsed','hpAfter','shipAlive','targets'];diff={k:{'old':old['result'].get(k),'current':d['result'].get(k)}for k in keys if old['result'].get(k)!=d['result'].get(k)}
 if old['diagnostic']['rng']!=d['after']['rng']:diff['rng']={'old':old['diagnostic']['rng'],'current':d['after']['rng']}
 comp.append({'case':c,'equal':not diff,'difference':diff,'historicalHtmlSha256':old['htmlSha256']})
save('historical-comparison.json',comp)
selected=[historical[(d['case']['ship'],d['case']['bearing'],d['case']['seed'])]for d in c1+d1 if(d['case']['ship'],d['case']['bearing'],d['case']['seed'])in historical]
(E/'historical-selected.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
save('progress.json',{'c1':len(c1),'d1':len(d1),'controls':len(controls),'historicalCompared':len(comp),'historicalDifferences':sum(not x['equal']for x in comp),'equivalence':json.loads((E/'equivalence.json').read_text())['pass']})
print(json.dumps(json.loads((A/'progress.json').read_text()),ensure_ascii=False))
