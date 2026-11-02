"""Existing assertions with the already-approved retired-node/container adapter.
No changed expected values. Results stay under this task's evidence directory.
"""
from pathlib import Path
import os,sys,json,time,subprocess,concurrent.futures
from harness import P,R,OUT,BASE
E=P/'evidence/regression';E.mkdir(parents=True,exist_ok=True)
env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':'/workspace/aegis-performance-c/docs/performance/C/node_modules','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':OUT,'B2_OUT':str(E),'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'0'}
domain=['helicopter-flight','isar-native','emcon-native','emcon-ui','harpoon-f1','harpoon-clock','sov-native','sov-casualty','sov-deployment','sov-visual']
jobs=[(name,[sys.executable,'-u',str(R/'docs/pip/B/run_domain.py'),str(R/OUT),str(E/name),'--only',name])for name in domain]
jobs += [('ui213',[sys.executable,'-u',str(P/'cpu2d_ui.py')]),('webgl8',[sys.executable,'-u',str(R/'docs/envelope/D/run_observed_webgl.py'),str(R/OUT),str(E/'webgl8')]),('paired-current',[sys.executable,'-u',str(R/'docs/helicopter/F/verify_regression.py'),str(R/BASE),str(R/OUT),str(E/'paired-current'),'--baseline-only'])]
start=time.perf_counter();rows=[]
def run(job):
 name,cmd=job;at=time.perf_counter()
 with(E/(name+'.log')).open('w')as f:
  try:q=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900);code=q.returncode
  except subprocess.TimeoutExpired:code=124
 return {'suite':name,'exit':code,'elapsedS':time.perf_counter()-at}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 for future in concurrent.futures.as_completed([pool.submit(run,j)for j in jobs]):
  row=future.result();rows.append(row);(E/'execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2)+'\n');print(row,flush=True)
raise SystemExit(any(r['exit']for r in rows))
