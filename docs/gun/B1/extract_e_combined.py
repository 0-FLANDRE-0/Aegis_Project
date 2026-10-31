"""Split the one actual 287-check MAP_E execution into its documented scopes.
No re-execution, no assertion change: UI277 and native11 share pageErrors0.
"""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;E=H/'evidence/regression/map/E/evidence/e-new';p=E/'results.json';raw=p.read_bytes();q=json.loads(raw);assert q['pass']and len(q['checks'])==287
native={k:v for k,v in q['checks'].items()if k.startswith(('DDG_119_LATE_FLIGHT_IIA.','CG_52_LATE_TICONDEROGA.'))or k=='pageErrors0'};ui={k:v for k,v in q['checks'].items()if k.startswith(('1400.','832.'))or k=='pageErrors0'};assert len(native)==11 and len(ui)==277 and set(native)|set(ui)==set(q['checks'])and set(native)&set(ui)=={'pageErrors0'}
for name,checks in [('native-results.json',native),('ui-results.json',ui)]:
 out={'pass':all(checks.values()),'checks':checks,'errors':q['errors'],'htmlSha256':q['htmlSha256'],'derivedFromCombined':{'path':'results.json','sha256':hashlib.sha256(raw).hexdigest(),'uniqueAssertions':287,'sharedCheck':'pageErrors0','note':'Both scopes executed in the same actual browser run; this file is a lossless check-ID grouping, not a new run.'}};(E/name).write_text(json.dumps(out,indent=2)+'\n')
print('MAP_E combined287 -> UI277 / native11 (pageErrors0 shared)')
