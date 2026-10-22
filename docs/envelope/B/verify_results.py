"""Deterministic output, complete matrix and native termination evidence audit."""
import argparse,hashlib,itertools,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.first.read_bytes();other=a.second.read_bytes();j=json.loads(raw);checks={};checks['E1.bitIdenticalIndependentRuns']=raw==other
expected=set(itertools.product(['SM2','SM2ER','SM6','ESSM'],[30,1000,5000,10000,15000,20000],[0,250,680,-250]));actual={(r['weapon'],r['altM'],r['targetSpeedMps'])for r in j['table']};checks['E4.envelope96UniqueComplete']=len(j['table'])==96 and actual==expected
checks['E4.everyRowHasNativeReason']=all(r['lastSuccess']or r['firstFailure']and r['firstFailure']['result'].get('reason')for r in j['table'])
checks['E4.lastSuccessAndAdjacentFailure']=all((r['lastSuccess']['result']['success']and r['lastSuccess']['result']['rangeKm']==r['maxRangeKm']and(r['upperCapReached']and r['maxRangeKm']==300 and r['firstFailure']is None or r['firstFailure']['rangeKm']==r['maxRangeKm']+1 and r['firstFailure']['result']['rangeKm']==r['maxRangeKm']+1 and not r['firstFailure']['result']['success']))if r['lastSuccess']else r['maxRangeKm']==0 for r in j['table'])
expected=set(itertools.product(['SM2','SM2ER','SM6','ESSM'],[30,5000,15000],[0,250],[30,60,100,150,200]));actual={(r['weapon'],r['altM'],r['targetSpeedMps'],r['rangeKm'])for r in j['trajectories']};checks['E4.trajectories120UniqueComplete']=len(j['trajectories'])==120 and actual==expected
checks['E4.noEmptyTrajectoryResult']=all(r['reason']and r['terminal']and r['samples']and r['phases']and r['flightTimeS']>0 for r in j['trajectories'])
checks['E4.onlyNativeFuzeSuccess']=all(not r['success']or r['reason']=='INTERCEPT_SUCCESS'and r['fuzeMissM']is not None for r in j['trajectories'])
checks['E4.exhaustiveUpperGrid']=all(r['searchPolicy']=='COARSE_BRACKET_THEN_INTEGER_BISECTION_PLUS_EXHAUSTIVE_UPPER_GRID'for r in j['table'])
rows=[]
for f in [a.first,a.second]:
 receipt=json.loads(Path(str(f)+'.receipt.json').read_text());rows.append({'filename':f.name,**receipt})
d={'pass':all(checks.values()),'checks':checks,'records':rows,'profileHash':j['profileHash'],'nonMonotonicCoarseRows':sum(r['nonMonotonicCoarse']for r in j['table'])};(a.out/'results-verification.json').write_text(json.dumps(d,indent=2));print(json.dumps(d));raise SystemExit(0 if d['pass']else 1)
