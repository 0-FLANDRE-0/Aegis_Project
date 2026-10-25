"""Rerun all 300 original release inputs on the new actual game HTML.
The prior DZT control has identical pinned HTML SHA; it is labelled historical,
never counted as new-product test executions.
"""
from pathlib import Path
import subprocess,json,time,sys
H=Path(__file__).resolve().parent;R=H.parents[3];out=H/'evidence/release-HANDOFF';out.mkdir(parents=True,exist_ok=True);start=time.perf_counter();rows=[];file=json.loads((H/'build.json').read_text())['file']
for kind,cases in [('normals','normal'),('dual','dual'),('faults','fault'),('battery','battery'),('request','release-request')]:
 cmd=['python','docs/missile/termination/A/verify_live.py',file,str(out/(kind+'.json')),'--cases','docs/missile/termination/A/cases/'+cases+'.json','--batch','8'];t=time.perf_counter()
 with(out/(kind+'.log')).open('w')as log:p=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 q={'kind':kind,'exitCode':p.returncode,'elapsedS':time.perf_counter()-t};rows.append(q);print(json.dumps(q),flush=True);(H/'evidence/release-executions.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start,'historicalBaseline':'fuze-zem-a@7d863699c596c30b0df5e34734f17fe11cadc21e docs/missile/fuze-zem/A/evidence/release-DZT','newProductFlights':sum(len(json.loads((out/(r['kind']+'.json')).read_text())['results'])for r in rows)},indent=2)+'\n')
 if p.returncode:sys.exit(p.returncode)
