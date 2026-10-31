from pathlib import Path
import subprocess,sys,json,time
H=Path(__file__).resolve().parent;R=H.parents[2];rows=[];start=time.perf_counter()
jobs=[('UI88',['verify_ui88.py','Aegis_SIM_v48_WIP_MAP_E.html',str(H/'evidence/ui88')]),('MAPB91',['verify_map_b.py']),('extras',['verify_extra.py']),('network',['verify_network.py']),('warnings',['verify_warnings.py']),('new-ui',['verify_ui_c.py']),('motion',['verify_motion_c.py']),('rules',['verify_rules_c.py']),('rings',['verify_rings_c.py']),('dom',['verify_dom_c.py'])]
for name,args in jobs:
 cmd=[sys.executable,'-u',str(H/args[0]),*args[1:]]
 if name in ['extras','new-ui','motion']:cmd=['flock','/tmp/aegis-map-e/gpu.lock',*cmd]
 with(H/'evidence'/f'{name}.log').open('w')as f:q=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'name':name,'exitCode':q.returncode});print(rows[-1],flush=True)
 (H/'evidence/ui-execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2))
 if q.returncode:raise SystemExit(q.returncode)
