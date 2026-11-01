"""Aggregate every case/shot, including no-fire and right-censored flights.
No feedback from this report is used to tune an experiment or game coefficient.
"""
from pathlib import Path
import collections,csv,hashlib,json,math,statistics,sys
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
def read_rows(path):
 result=[]
 for p in sorted(path.glob('worker*.jsonl')):
  for line in p.read_text().splitlines():
   try:result.append(json.loads(line))
   except ValueError:pass # a running writer can have one incomplete last line
 if path==E/'trials'and(E/'a-stop-corrected').exists():
  corrected=read_rows(E/'a-stop-corrected');replacement={r['caseId']:r for r in corrected}
  assert len(corrected)==len(replacement)==480 and set(replacement)=={r['caseId']for r in result if r['experiment']=='A'},'A_CORRECTION_INCOMPLETE'
  result=[replacement[r['caseId']]if r['experiment']=='A'else r for r in result]
 return sorted(result,key=lambda x:x['caseId'])
def stats(values):
 a=sorted(float(x)for x in values if x is not None and math.isfinite(float(x)))
 def q(p):
  t=(len(a)-1)*p;i=int(t);return a[i]+(a[min(len(a)-1,i+1)]-a[i])*(t-i)
 return {'n':len(a),'mean':statistics.mean(a),'sigma':statistics.pstdev(a),'p10':q(.1),'median':q(.5),'p90':q(.9),'min':a[0],'max':a[-1]}if a else {'n':0,'mean':None,'sigma':None,'p10':None,'median':None,'p90':None,'min':None,'max':None}
def norm(v):return math.sqrt(sum(v[k]**2 for k in ['x','y','z']))if v else None
def resolve(r,v):
 if r is None:return {'along':None,'cross':None,'vertical':None}
 n=norm(v)or 1;h=math.hypot(v['x'],v['y'])or 1;return {'along':sum(r[k]*v[k]for k in ['x','y','z'])/n,'cross':(-r['x']*v['y']+r['y']*v['x'])/h,'vertical':r['z']}
def budget(s):
 """Exact bookkeeping identity at native swept CPA; not a new flight model.
 R(shell-target)=position+staleness+velocity+motion+ballistic_phase.
 Terms correlate/cancel. Their variances must NOT be added as independent.
 """
 c=s.get('cpa');a=s.get('solveTarget');tr=s.get('observation');t=s.get('truthAtRelease')
 if not(c and a and tr and t):return None
 tau=c['ageS'];keys=['x','y','z']
 vel={'x':a['vxMps'],'y':a['vyMps'],'z':a['vzMps']};obs0={k:a[k+'M']for k in keys};tp=t['positionM'];tv=t['velocityMps'];now=c['targetPositionM'];shell={k:now[k]+c['relativeM'][k]for k in keys}
 terms={'position':{k:tr['positionM'][k]-tp[k]for k in keys},'staleness':{k:obs0[k]-tr['positionM'][k]for k in keys},'velocity':{k:(vel[k]-tv[k])*tau for k in keys},'motion':{k:-(now[k]-tp[k]-tv[k]*tau)for k in keys},'ballisticPhase':{k:shell[k]-(obs0[k]+vel[k]*tau)for k in keys}}
 closure={k:sum(q[k]for q in terms.values())-c['relativeM'][k]for k in keys}
 return {'terms':{name:resolve(v,c['shellVelocityMps'])for name,v in terms.items()},'closureErrorM':norm(closure)}
def compare_old(rows):
 old={}
 for q in read_rows(R/'docs/gun/B1/evidence/effects'):
  if q['on']:old[q['ship'],q['bearing'],q['count'],q['seed']]=q['result']
 different=[];checked=0
 for r in rows:
  if r['experiment']!='BASE':continue
  a=dict(old[r['ship'],r['bearing'],r['count'],r['seed']]);b=dict(r['data']['result']);a.pop('elapsedMs',None);b.pop('elapsedMs',None);checked+=1
  if a!=b:different.append({'caseId':r['caseId'],'key':[r['ship'],r['bearing'],r['count'],r['seed']],'differentFields':[k for k in set(a)|set(b)if a.get(k)!=b.get(k)]})
 return {'checked':checked,'different':different,'allExact':not different,'comparisonKind':'HISTORICAL_NONPAIRED_RESET_PROTOCOL','policy':'Only elapsedMs ignored. Historical G7 reused pages; Phase0 uses fresh JS windows for every case. Differences are listed, not treated as product regressions. Native/instrumented equivalence is tested separately.'}
def summarize(rows):
 shots=[s for r in rows for s in r['data']['shots']];bursts=[s for s in shots if s.get('burst')];aliveBursts=[s for s in bursts if s.get('assignedTargetAliveBeforeBurst')];outcomes=collections.Counter(s['outcome']for s in shots)
 metrics={'solutionAgeS':stats(s['solutionAgeS']for s in shots),'originDisplacementM':stats(norm(s['originDeltaM'])for s in shots),'ownshipSpeedMps':stats(norm(s['shipVelocityMps'])for s in shots),'trunnionSpeedMps':stats(norm(s['ownVelocityMps'])for s in shots),'crossLimitM':stats(s['pointing']['limitM']for s in shots),'pointingCrossM':stats(s['pointing']['crossMissM']for s in shots),'pointingVerticalM':stats(s['pointing']['verticalMissM']for s in shots),'firstShotSlewS':stats(s['slewS']for s in shots if s['firstShot']),'cpaM':stats(s['cpa']['missM']for s in shots if s['cpa']),'arrivalAllAssignedAliveM':stats(s['assignedArrivalDiagnostic']['arrivalMissM']for s in aliveBursts),'arrivalNativeAsmM':stats(a['arrivalMissM']for s in bursts for a in s['burst']['results']if a['kind']=='ASM'),'nativeAsmPk':stats(a['pk']for s in bursts for a in s['burst']['results']if a['kind']=='ASM')}
 for name,getter in [('cpa',lambda s:s['cpa']['resolvedM']if s['cpa']else None),('origin',lambda s:resolve(s['originDeltaM'],s['launchVelocityMps'])),('observationPosition',lambda s:resolve(s['trackPositionErrorM'],s['launchVelocityMps'])),('observationVelocity',lambda s:resolve(s['trackVelocityErrorMps'],s['launchVelocityMps'])),('stalePrediction',lambda s:resolve(s.get('stalePredictionShiftM'),s['launchVelocityMps']))]:
  for axis in ['along','cross','vertical']:metrics[name+'.'+axis]=stats((getter(s)or{}).get(axis)for s in shots)
 for axis in ['along','cross','vertical']:metrics['targetAcceleration.'+axis]=stats(s['acceleration']['mean'][axis]for s in shots)
 metrics['cpaResolvedLiveTargetM']=stats(s['cpa']['missM']for s in aliveBursts if s['cpa'])
 for axis in ['along','cross','vertical']:metrics['cpaResolvedLiveTarget.'+axis]=stats(s['cpa']['resolvedM'][axis]for s in aliveBursts if s['cpa'])
 for axis in ['along','cross','vertical']:metrics['targetAccelerationRms.'+axis]=stats(math.sqrt(s['acceleration']['square'][axis]/s['acceleration']['seconds'])for s in shots if s['acceleration']['seconds']>0)
 metrics['nativeAssignedArrivalM']=stats(a['arrivalMissM']for s in bursts for a in s['burst']['results']if a['kind']=='ASM'and a['id']==(s.get('truthAtRelease')or{}).get('id'))
 budgets=[budget(s)for s in aliveBursts];budgets=[q for q in budgets if q]
 for name in ['position','staleness','velocity','motion','ballisticPhase']:
  for axis in ['along','cross','vertical']:metrics['budget.'+name+'.'+axis]=stats(q['terms'][name][axis]for q in budgets)
 metrics['budget.closureErrorM']=stats(q['closureErrorM']for q in budgets)
 caseFirst=[]
 for r in rows:
  s=r['data']['shots'];cues=[a['step']for a in r['data']['result']['auto']['log']if a['kind']=='AUTO_CUE']
  if s and cues:caseFirst.append((min(a['launchStep']for a in s)-min(cues))/60)
 metrics['caseFirstAutoCueToFirstReleaseS']=stats(caseFirst)
 metrics['caseFirstReleaseS']=stats(min(s['launchStep']for s in r['data']['shots'])/60 for r in rows if r['data']['shots'])
 return {'trials':len(rows),'shots':len(shots),'bursts':len(bursts),'assignedAliveBursts':len(aliveBursts),'outcomes':dict(outcomes),'etFractionResolved':outcomes['MFF_ET_BACKUP']/len(bursts)if bursts else None,'proxFractionResolved':outcomes['MFF_PROXIMITY']/len(bursts)if bursts else None,'noFireTrials':sum(not r['data']['shots']for r in rows),'shipHits':sum(r['data']['result']['shipHits']for r in rows),'gunPreCiwsKillsLegacyCounter':sum(r['data']['result']['gunPreCiwsKills']for r in rows),'nativeAsmFatalEffects':sum(a['kind']=='ASM'and a['result']in ['KILL','STRUCT_FAIL']for s in bursts for a in s['burst']['results']),'missingTruthAssociationShots':sum(not s['truthAtRelease']for s in shots),'liveAtEndShots':outcomes['LIVE_AT_SCENARIO_END'],'nativeRefreshAttempts':sum(r['data']['refreshSummary']['attempts']for r in rows),'nativeRefreshMs':sum(r['data']['refreshSummary']['totalMs']for r in rows),'metrics':metrics}
rows=read_rows(E/'trials');groups={}
for ex in ['BASE','A','B','C','D']:
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  for bearing in [0,90]:
   q=[r for r in rows if(r['experiment'],r['ship'],r['bearing'])==(ex,ship,bearing)]
   if q:groups[f'{ex}|{ship}|{bearing}']=summarize(q)
out={'schema':'AEGIS_GUN_B2_PHASE0_SUMMARY_1','cases':len(rows),'expectedCases':2400,'complete':len(rows)==2400 and len({r['caseId']for r in rows})==2400,'counts':dict(collections.Counter(r['experiment']for r in rows)),'shots':sum(len(r['data']['shots'])for r in rows),'oldG7Comparison':compare_old(rows),'groups':groups,'instrumentedHashes':sorted({r['instrumentedHtmlSha256']for r in rows})}
out['perCondition']={f'{ex}|{ship}|{bearing}|{count}':summarize(q)for ex in ['BASE','A','B','C','D']for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']for bearing in [0,90]for count in range(1,5)if(q:=[r for r in rows if(r['experiment'],r['ship'],r['bearing'],r['count'])==(ex,ship,bearing,count)])}
out['sourceSelection']={'primaryCases':2400,'retainedOriginalNonA':1920,'correctedA':480,'originalAAlsoPreserved':480,'rawMatrixExecutions':2880,'policy':'Original trials remain unchanged. Only experiment A is replaced by matching caseId/inputs from a-stop-corrected. Strict stop tolerance is unchanged.','audit':'evidence/a-stop-audit.json'}
(E/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
with(E/'condition-metrics.csv').open('w',newline='')as f:
 names=['experiment','ship','bearing','incomingCount','metric','n','mean','sigma','p10','median','p90','min','max'];w=csv.DictWriter(f,fieldnames=names,lineterminator='\n');w.writeheader()
 for key,q in out['perCondition'].items():
  ex,ship,bearing,count=key.split('|')
  for name,value in q['metrics'].items():w.writerow({'experiment':ex,'ship':ship,'bearing':bearing,'incomingCount':count,'metric':name,**value})
with(E/'case-summary.csv').open('w',newline='')as f:
 names=['caseId','experiment','ship','bearing','count','seed','shots','bursts','et','prox','live','shipHits','hpAfter','rng','step','wallS'];w=csv.DictWriter(f,fieldnames=names,lineterminator='\n');w.writeheader()
 for r in rows:
  d=r['data'];ss=d['shots'];o=collections.Counter(s['outcome']for s in ss);w.writerow({**{k:r[k]for k in ['caseId','experiment','ship','bearing','count','seed','wallS']},'shots':len(ss),'bursts':sum(bool(s['burst'])for s in ss),'et':o['MFF_ET_BACKUP'],'prox':o['MFF_PROXIMITY'],'live':o['LIVE_AT_SCENARIO_END'],'shipHits':d['result']['shipHits'],'hpAfter':d['result']['hpAfter'],'rng':d['rng'],'step':d['step']})
with(E/'shot-summary.csv').open('w',newline='')as f:
 names=['caseId','experiment','ship','bearing','count','seed','shell','trackId','outcome','launchStep','computedStep','solutionAgeS','firstShot','slewS','originShiftM','shipSpeedMps','pointingCrossM','pointingVerticalM','crossLimitM','cpaM','cpaAlongM','cpaCrossM','cpaVerticalM','assignedArrivalM','assignedAliveBeforeBurst','assignedNativeArrivalM','assignedNativePk','maxNativeAsmPk','triggerKind','triggerId','burstAgeS','programmedTofS'];w=csv.DictWriter(f,fieldnames=names,lineterminator='\n');w.writeheader()
 for r in rows:
  for s in r['data']['shots']:
   c=s['cpa']or{};a=c.get('resolvedM',{});burst=s.get('burst')or{};asm=[q for q in burst.get('results',[])if q['kind']=='ASM'];assigned=next((q for q in asm if q['id']==(s.get('truthAtRelease')or{}).get('id')),{});w.writerow({**{k:r[k]for k in ['caseId','experiment','ship','bearing','count','seed']},'shell':s['id'],'trackId':s['trackId'],'outcome':s['outcome'],'launchStep':s['launchStep'],'computedStep':s['computedStep'],'solutionAgeS':s['solutionAgeS'],'firstShot':s['firstShot'],'slewS':s['slewS'],'originShiftM':norm(s['originDeltaM']),'shipSpeedMps':norm(s['shipVelocityMps']),'pointingCrossM':s['pointing']['crossMissM'],'pointingVerticalM':s['pointing']['verticalMissM'],'crossLimitM':s['pointing']['limitM'],'cpaM':c.get('missM'),'cpaAlongM':a.get('along'),'cpaCrossM':a.get('cross'),'cpaVerticalM':a.get('vertical'),'assignedArrivalM':s.get('assignedArrivalDiagnostic',{}).get('arrivalMissM'),'assignedAliveBeforeBurst':s.get('assignedTargetAliveBeforeBurst'),'assignedNativeArrivalM':assigned.get('arrivalMissM'),'assignedNativePk':assigned.get('pk'),'maxNativeAsmPk':max((q['pk']for q in asm),default=None),'triggerKind':burst.get('triggerKind'),'triggerId':burst.get('triggerId'),'burstAgeS':burst.get('ageS'),'programmedTofS':s['solution']['timeOfFlightS']})
print(json.dumps({**{k:out[k]for k in ['complete','cases','counts','shots']},'historicalCompared':out['oldG7Comparison']['checked'],'historicalDifferent':len(out['oldG7Comparison']['different'])}))
