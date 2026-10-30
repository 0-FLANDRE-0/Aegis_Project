from pathlib import Path
import subprocess,sys,json,time
H=Path(__file__).resolve().parent;R=H.parents[2];rows=[];start=time.perf_counter()
jobs=[('release300',[str(H/'c2_browser.py'),'Aegis_SIM_v48_WIP_MAP_D.html','MAP_D','--suite','release']),('world',[str(H/'verify_delivery_world.py')]),('webgl8',[str(R/'docs/envelope/D/run_observed_webgl.py'),'Aegis_SIM_v48_WIP_MAP_D.html',str(H/'evidence/webgl8')])]
for name,args in jobs:
 cmd=[sys.executable,'-u',*args]
 if name=='webgl8':cmd=['flock','/tmp/aegis-map-d/gpu.lock',*cmd]
 with(H/'evidence'/f'{name}.log').open('w')as f:q=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'name':name,'exitCode':q.returncode});print(rows[-1],flush=True)
 if q.returncode:raise SystemExit(q.returncode)
(H/'evidence/native-execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2))
