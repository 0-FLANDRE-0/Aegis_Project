"""Bounded existing regression lane, separate evidence destination."""
from pathlib import Path
import json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/regression';E.mkdir(parents=True,exist_ok=True)
env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':'/workspace/aegis-performance-c/docs/performance/C/node_modules','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':'Aegis_SIM_v48_WIP_CG_TURRET_A.html','B2_OUT':str(E),'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support')}
jobs=[(n,[sys.executable,'-u',str(P/'run_regression.py'),n],{**env,'B2_ALLOW_AUTO':'1'if n!='map'else'0'})for n in['native','geometry','physical_adapter','map','ui']]
jobs += [('map-ui213',[sys.executable,'-u',str(R/'docs/gun/B1/run_test_migrations.py'),'ui'],{**env,'B2_ALLOW_AUTO':'0'}),('webgl8',[sys.executable,'-u',str(R/'docs/envelope/D/run_observed_webgl.py'),str(R/'Aegis_SIM_v48_WIP_CG_TURRET_A.html'),str(E/'webgl8')],{**env,'B2_ALLOW_AUTO':'0'})]
jobs += [('native-origin-control',[sys.executable,'-u',str(P/'run_regression.py'),'native'],{**env,'B2_ALLOW_AUTO':'1','CG_ORIGIN_CONTROL':'1','B2_OUT':str(E/'origin-control')})]
start=time.perf_counter();rows=[]
for name,cmd,cfg in jobs:
 at=time.perf_counter()
 with(E/(name+'.log')).open('w')as stream:
  try:q=subprocess.run(cmd,cwd=R,env=cfg,stdout=stream,stderr=subprocess.STDOUT,timeout=900);code=q.returncode
  except subprocess.TimeoutExpired:code=124
 row={'suite':name,'exit':code,'elapsedS':time.perf_counter()-at};rows.append(row);(E/'execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2)+'\n');print(row,flush=True)
 # Keep all raw failures; independent suites still run.
raise SystemExit(any(r['exit']for r in rows))
