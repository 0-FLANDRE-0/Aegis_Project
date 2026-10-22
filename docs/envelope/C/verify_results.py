"""Deterministic output, complete matrix and native termination evidence audit."""
import argparse,hashlib,itertools,json,math,gzip
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.first.read_bytes();other=a.second.read_bytes();j=json.loads(raw);checks={};checks['E1.bitIdenticalIndependentRuns']=raw==other
expected=set(itertools.product(['SM2','SM2ER','SM6','ESSM'],[30,1000,5000,10000,15000,20000],[0,250,680,-250]));actual={(r['weapon'],r['altM'],r['targetSpeedMps'])for r in j['table']};checks['E4.envelope96UniqueComplete']=len(j['table'])==96 and actual==expected
checks['E4.everyRowHasNativeReason']=all(r['lastSuccess']or r['firstFailure']and r['firstFailure']['result'].get('reason')for r in j['table'])
checks['E4.lastSuccessAndAdjacentFailure']=all((r['lastSuccess']['result']['success']and r['lastSuccess']['result']['rangeKm']==r['maxRangeKm']and(r['upperCapReached']and r['maxRangeKm']==500 and r['firstFailure']is None or r['firstFailure']['rangeKm']==r['maxRangeKm']+1 and r['firstFailure']['result']['rangeKm']==r['maxRangeKm']+1 and not r['firstFailure']['result']['success']))if r['lastSuccess']else r['maxRangeKm']==0 for r in j['table'])
expected=set(itertools.product(['SM2','SM2ER','SM6','ESSM'],[30,5000,15000],[0,250],[30,60,100,150,200]));actual={(r['weapon'],r['altM'],r['targetSpeedMps'],r['rangeKm'])for r in j['trajectories']};checks['E4.trajectories120UniqueComplete']=len(j['trajectories'])==120 and actual==expected
checks['E4.noEmptyTrajectoryResult']=all(r['reason']and r['terminal']and r['samples']and r['phases']and r['flightTimeS']>0 for r in j['trajectories'])
checks['E4.onlyNativeFuzeSuccess']=all(not r['success']or r['reason']=='INTERCEPT_SUCCESS'and r['fuzeMissM']is not None for r in j['trajectories'])
checks['E4.exhaustiveUpperGrid']=all(r['searchPolicy']=='COARSE_BRACKET_THEN_INTEGER_BISECTION_PLUS_EXHAUSTIVE_UPPER_GRID'for r in j['table'])
checks['R5.interceptPointsRecorded']=all(r['interceptPointKm']==r['lastSuccess']['result']['terminal']['distanceKm'] and math.isfinite(r['interceptPointKm']) if r['lastSuccess'] else r['interceptPointKm'] is None for r in j['table'])
checks['R5.trajectoryInterceptPointsRecorded']=all(q['interceptPointKm']==q['terminal']['distanceKm'] if q['success'] else q['interceptPointKm'] is None for q in j['trajectories'])
checks['R5.finiteNativeTrajectories']=all(all(isinstance(s.get(k),(int,float)) and math.isfinite(s[k]) for k in ['timeS','xM','yM','altitudeM','speedMps','mach']) for q in j['trajectories'] for s in q['samples'])
old=json.loads(gzip.decompress((Path(__file__).resolve().parent.parent/'B/results/results.json.gz').read_bytes()))
def project(old,new):
 if isinstance(old,dict):return {k:project(v,new[k])for k,v in old.items()}
 if isinstance(old,list):return [project(x,y)for x,y in zip(old,new)]if len(old)==len(new)else None
 return new
# Envelope-derived labels may change when the measurement cap grows; compare native fields only.
oldCases={(q['weapon'],q['rangeKm'],q['altM'],q['targetSpeedMps']):{k:v for k,v in q.items()if k not in ['beyondComputedEnvelope','label']} for q in old['trajectories']}
untouched=[q for q in j['trajectories']if q['weapon']in ['SM2','ESSM']]
checks['R1.mrEssm60NativeTracesUnchanged']=len(untouched)==60 and all((base:=oldCases[(q['weapon'],q['rangeKm'],q['altM'],q['targetSpeedMps'])])==project(base,q) for q in untouched)
stage1=json.loads((Path(__file__).resolve().parent/'stage1/verification.json').read_text())
fullByKey={(q['weapon'],q['altM'],q['targetSpeedMps']):q for q in j['table']}
checks['R2.fullMatrixMatchesSixConditionSweep']=all((row:=fullByKey[(q['weapon'],q['altM'],0)])['maxRangeKm']==q['maxRangeKm'] and row['interceptPointKm']==q['interceptPointKm'] for q in stage1['rows'])
reported=[q['reason']for q in j['trajectories']]
reported += [q[k]['result']['reason']for q in j['table']for k in ['lastSuccess','firstFailure']if q[k]is not None]
reported += [p['reason']for q in j['table']for p in q['coarseProbes']]
checks['R5.idealSupportNoTrackingExpiry']=all(not r.startswith('TERMINAL_')for r in reported)
rows=[]
for f in [a.first,a.second]:
 receipt=json.loads(Path(str(f)+'.receipt.json').read_text());rows.append({'filename':f.name,**receipt})
d={'pass':all(checks.values()),'checks':checks,'records':rows,'profileHash':j['profileHash'],'nonMonotonicCoarseRows':sum(r['nonMonotonicCoarse']for r in j['table'])};(a.out/'results-verification.json').write_text(json.dumps(d,indent=2));print(json.dumps(d));raise SystemExit(0 if d['pass']else 1)
