from pathlib import Path
import subprocess,sys,json,time
H=Path(__file__).resolve().parent;R=H.parents[2];rows=[];start=time.perf_counter()
for name in ['native','ui','edges']:
 cmd=[sys.executable,'-u',str(H/f'verify_d_{name}.py')]
 if name!='native':cmd=['flock','/tmp/aegis-map-e/gpu.lock',*cmd]
 with(H/'evidence'/f'd-{name}-execution.log').open('w')as log:q=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 rows.append({'name':name,'exitCode':q.returncode});print(rows[-1],flush=True);(H/'evidence/d-execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2)+'\n')
 if q.returncode:raise SystemExit(q.returncode)
