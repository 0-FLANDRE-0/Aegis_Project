from pathlib import Path
import json
H=Path(__file__).resolve().parent
cost=json.loads((H/'COST_ESTIMATE.json').read_text());m=json.loads((H/'results/measurement.json').read_text());f=json.loads((H/'evidence/determinism.json').read_text())
result={'initialExpectedHours':cost['expectedHours'],'initialExpectedShots':cost['expectedShots'],'actualSweepHours':m['elapsedS']/3600,'actualSweepShots':m['calls'],'followupHours':f['elapsedS']/3600,'followupShots':f['calls'],'fullSweeps':1,'reducedScopeUsed':False,'reasonForUnderestimate':'The 80-shot pilot underweighted the long-duration failed flights in the exhaustive farther-distance sweep. Original preflight estimate is preserved unchanged.'}
(H/'ACTUAL_COST.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
