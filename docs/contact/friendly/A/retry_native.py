"""Serial retries of the two browser-crash cases; same original assertions."""
import os,sys,subprocess,json,time
from harness import P,R,OUT
E=P/'evidence/regression';env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','NODE_PATH':'/workspace/aegis-performance-c/docs/performance/C/node_modules','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_HTML':OUT,'B2_OUT':str(E),'PYTHONPATH':str(R/'docs/gun/B2/phase1b/test_support'),'B2_ALLOW_AUTO':'0'};start=time.perf_counter();rows=[]
for name in ['harpoon-f1','helicopter-flight']:
 at=time.perf_counter()
 with(E/(name+'-retry.log')).open('w')as f:
  try:q=subprocess.run([sys.executable,'-u',str(R/'docs/pip/B/run_domain.py'),str(R/OUT),str(E/(name+'-retry')),'--only',name],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=600);code=q.returncode
  except subprocess.TimeoutExpired:code=124
 rows.append({'suite':name,'exit':code,'elapsedS':time.perf_counter()-at});(E/'native-retry-execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2)+'\n');print(rows[-1],flush=True)
raise SystemExit(any(x['exit']for x in rows))
