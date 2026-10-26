from pathlib import Path
import collections,gzip,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def physical(v):
 if isinstance(v,dict):
  d={k:physical(x)for k,x in v.items()if k not in ['performance','aviation']}
  if v.get('schema')=='AEGIS_OFFBOARD_PORT_C_1':d.pop('helicopterImplemented',None);d['sources']=[s for s in d.get('sources',[])if s.get('sourceId')not in ['H1','H2']]
  if v.get('schema')=='AEGIS_SHIP_OBSERVER_C_1'and'deferred'in d:d['deferred']=[s for s in d['deferred']if s!='helicopterFlightAndSensors']
  return d
 if isinstance(v,list):return [physical(x)for x in v]
 return v
def identity(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def target_outcome(t):return (t.get('retirement')or{}).get('cause')or t.get('reason')or ('PENDING'if t['alive']else'UNCLASSIFIED_NATIVE_TERMINAL')
def metrics(j):
 s=j['snapshots'][-1];a=s['after'];ship=s['state'];inv=ship['inventory'];targets={str(t['id']):target_outcome(t)for t in a['targets']if t['initial']}
 return {'samLaunches':len(a['sams']),'samNativeKills':sum(t['reason']in ['PROX_DETONATION_KILL','PROX_DETONATION_STRUCT_FAIL']for t in a['sams']),'initialTargets':targets,'initialAllTerminal':all(not t['alive']for t in a['targets']if t['initial']),'allNativeTargetOutcomes':{str(t['id']):target_outcome(t)for t in a['targets']},'nativeTargetCount':len(a['targets']),'shipHP':ship['shipHP'],'shipAlive':ship['shipHP']>0,'moduleDamage':ship['damage']['moduleDamage'],'waterM3':sum(c['waterM3']for c in ship['damage']['flooding']['cells']),'loadedVlsCells':sum(c['type']!='EMPTY'for cells in inv['vls'].values()for c in cells),'closeInAmmo':{str(c['id']):c['ammo']for c in inv['closeIn']},'endTimeS':180,'endReason':'FIXED_180S_DIAGNOSTIC_HORIZON','allAirborneAsmClear':not any(t['alive']for t in a['targets']),'alliedShips':'NONE_IN_ORIGINAL_FIXTURE'}
versions=['KAPPA','DZT','HANDOFF','ARH','VERTICAL','LATEST'];history={v:json.loads((H/'evidence/history'/v/'baseline-comparison.json').read_text())for v in versions};revert=json.loads((H/'evidence/history/REVERT_LAUNCH_ONLY/summary.json').read_text());assert revert['pass']
studies={};checks={};comparisons=[];approved={};six=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 for v in ['KAPPA','DZT','HANDOFF','LATEST']:
  j=json.loads(gzip.decompress((H/'evidence/raid'/(v+'_'+ship+'.json.gz')).read_bytes()));studies[v,ship]=j
  original=next(c['pair']['candidate']for c in history[v]['cases']if c['ship']==ship);current=j['snapshots'][0]
  for key in ['state','dynamics','rng','observers','offboard']:checks[v+'.'+ship+'.readOnly32.'+key]=physical(original[key])==physical(current[key])
 current=metrics(studies['LATEST',ship]);previous={v:metrics(studies[v,ship])for v in ['KAPPA','DZT','HANDOFF']};guards={}
 for v in ['KAPPA','DZT']:
  b=previous[v];guards[v+'.launchesNotHigher']=current['samLaunches']<=b['samLaunches'];guards[v+'.killsNotLower']=current['samNativeKills']>=b['samNativeKills'];guards[v+'.hpNotLower']=current['shipHP']>=b['shipHP'];guards[v+'.survival']=current['shipAlive']or not b['shipAlive'];guards[v+'.waterNotHigher']=current['waterM3']<=b['waterM3'];guards[v+'.vlsNotLower']=current['loadedVlsCells']>=b['loadedVlsCells'];guards[v+'.closeInAmmoNotLower']=all(current['closeInAmmo'][k]>=a for k,a in b['closeInAmmo'].items());guards[v+'.moduleDamageNotHigher']=all(current['moduleDamage'].get(k,0)<=b['moduleDamage'].get(k,0)for k in current['moduleDamage'].keys()|b['moduleDamage'].keys());guards[v+'.initialTargetsTerminal']=current['initialAllTerminal']
  # Compare the original eight native outcomes, not an aggregate hit rate.
  safe={'INTERCEPT_KILL','INTERCEPT_STRUCTURAL_FAILURE','WARHEAD_AIRBURST','DELAYED_STRUCTURAL_FAILURE','GUIDANCE_CONTROL_LOSS_MISS'}
  guards[v+'.noNeutralizedTargetBecameImpact']=all(x not in safe or current['initialTargets'][k]in safe for k,x in b['initialTargets'].items());guards[v+'.sameEvaluationEnd']=current['endTimeS']==b['endTimeS']and current['endReason']==b['endReason']
 classification='a'if all(guards.values())else'b';comparisons.append({'ship':ship,'classification':classification,'guards':guards,'before':previous,'current':current})
 for name in ['samePhysicalState','raidInventoryDeltaBounded','sameExistingObserverState']:
  row={'ship':ship,'assertion':name,'buildStatus':{v:next(c['checks'][name]for c in history[v]['cases']if c['ship']==ship)for v in versions},'firstFail':'HANDOFF','causalRevertPass':revert['checks'][ship+':'+name],'cause':'updateMissileBodyB3 launch-handoff gate; single-function revert restores original assertions','classification':classification,'action':'BASELINE_UPDATE'if classification=='a'else'PRESERVE_FAILURE_NO_COEFFICIENT_CHANGE'};six.append(row)
 if classification=='a':
  row=next(c for c in history['LATEST']['cases']if c['ship']==ship);b=row['pair']['baseline'];n=row['pair']['candidate'];old={'physical':physical({k:b[k]for k in ['state','dynamics']}),'observer':physical(b['observers']),'loadedVlsCells':sum(c['type']!='EMPTY'for cells in b['state']['inventory']['vls'].values()for c in cells)};new={'physical':physical({k:n[k]for k in ['state','dynamics']}),'observer':physical(n['observers']),'loadedVlsCells':sum(c['type']!='EMPTY'for cells in n['state']['inventory']['vls'].values()for c in cells)}
  approved[ship]={'scenario':'raid','classification':'a','assertions':['samePhysicalState','raidInventoryDeltaBounded','sameExistingObserverState'],'old':old,'expected':new,'oldHash':identity(old),'newHash':identity(new),'reason':'Native outcomes/damage/survival/weapon expenditure non-worse versus both Kappa and DZT; exact state changes are caused by the launch-handoff correction.'}
assert all(checks.values()),[k for k,v in checks.items()if not v]
assert set(approved)=={'DDG_119_LATE_FLIGHT_IIA'}
raw=(R/'Aegis_SIM_v48_WIP_ENV_D_REMEASURE_A.html').read_bytes();import base64,re
main=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1]));stripped=re.sub(rb'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',b'',main)
manifest={'schema':'AEGIS_CLEAN_A_APPROVED_RAID_BASELINES_1','gameCoreWithoutEnvelopeSha256':sha(stripped),'referenceHtmlSha256':sha(raw),'normalizer':'Unchanged HELI_F physical()','evidence':'docs/cleanup/A/evidence/part1.json','entries':approved,'nonApproved':{'CG_52_LATE_TICONDEROGA':'b: +1 SAM/VLS and 61 additional CIWS rounds at 180s, with unchanged 2 native KILLs and HP100; do not update its three expectations.'}}
(H/'approved-raid-baselines.json').write_text(json.dumps(manifest,indent=2)+'\n');out={'schema':'AEGIS_CLEAN_A_PART1_1','six':six,'comparisons':comparisons,'readOnlyChecks':checks,'gameCodeChanged':False,'minimumFixDecision':'No unambiguous minimal correction for CG resource regression without changing firing policy or a validated flight path; report unchanged.'};(H/'evidence/part1.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'classification':{r['ship']:r['classification']for r in comparisons},'approvedAssertions':len(approved)*3,'unresolvedAssertions':6-len(approved)*3,'readOnlyChecks':len(checks)}))
