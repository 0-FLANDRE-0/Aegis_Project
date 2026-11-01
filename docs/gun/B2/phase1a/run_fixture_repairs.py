"""Rerun only two incomplete RF mocks; prior failures and sources stay archived."""
from pathlib import Path
import json,os,signal,subprocess,sys,time
from deadline import check,remaining
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/regression';env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1','B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_ALLOW_AUTO':'1','B2_OUT':str(E/'ON'),'PYTHONPATH':str(P/'test_support')}
while True:
 check();f=E/'execution.json'
 if f.exists()and any(r['name']=='paired42_ON'for r in json.loads(f.read_text())['rows']):break
 time.sleep(5)
rows=[]
for name in ['verify_native','verify_physical_adapter']:
 check();at=time.perf_counter()
 with(E/('rf-metadata-'+name+'.log')).open('w')as f:
  proc=subprocess.Popen([sys.executable,'-u',str(P/'adapted'/(name+'.py'))],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:exit=proc.wait(timeout=remaining())
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);proc.wait();exit=124
 rows.append({'name':name,'exit':exit,'elapsedS':time.perf_counter()-at,'change':'Fixture RF metadata from native .06; coefficients and expected values unchanged. Missing-RCS/axis controls retained.','resourceFailure':False});(E/'fixture-repair-execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
 if exit==124:break
