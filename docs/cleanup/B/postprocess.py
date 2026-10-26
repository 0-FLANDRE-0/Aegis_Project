"""Wait for the measured table, then verify the exact final deliverable."""
from pathlib import Path
import concurrent.futures,json,os,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2];start=time.perf_counter();E=H/'evidence';E.mkdir(exist_ok=True)
env={**os.environ,'NODE_PATH':os.environ.get('NODE_PATH','/workspace/aegis-performance-f/docs/performance/F/node_modules'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
while True:
 try:
  m=json.loads((H/'results/measurement.json').read_text())
  if len(m['rows'])==120:break
 except(FileNotFoundError,json.JSONDecodeError):pass
 if time.perf_counter()-start>10800:raise RuntimeError('MEASUREMENT_WAIT_TIMEOUT')
 time.sleep(5)
steps=[]
def run(name,cmd):
 t=time.perf_counter()
 with(E/(name+'.log')).open('w')as log:p=subprocess.run(cmd,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
 return{'step':name,'exitCode':p.returncode,'elapsedS':time.perf_counter()-t}
for name,cmd in [('build',[sys.executable,str(H/'build.py')]),('shot-audit',['node',str(H/'audit.cjs')]),('interval-verification',[sys.executable,str(H/'verify_intervals.py')]),('native-equivalence',['node',str(H/'verify_native.cjs')])]:
 r=run(name,cmd);steps.append(r);print(json.dumps(r),flush=True)
 if r['exitCode']:raise RuntimeError(r)
jobs=[('domain',[sys.executable,str(H/'run_domain.py')]),('ui',[sys.executable,str(H/'run_ui.py')]),('delivery',[sys.executable,str(H/'verify_delivery.py')])]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
 for r in pool.map(lambda args:run(*args),jobs):steps.append(r);print(json.dumps(r),flush=True)
(E/'pipeline.json').write_text(json.dumps({'steps':steps,'elapsedS':time.perf_counter()-start},indent=2)+'\n')
if any(r['exitCode']for r in steps):raise RuntimeError('VERIFICATION_FAILED')
r=run('report',[sys.executable,str(H/'report.py')]);print(json.dumps(r),flush=True)
if r['exitCode']:raise RuntimeError(r)
