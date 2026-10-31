"""Rerun every affected assertion; preserve pre-approval measurements verbatim."""
from pathlib import Path
import concurrent.futures,json,os,subprocess,sys,time
B=Path(__file__).resolve().parent;R=B.parents[3];E=B/'evidence/approval';E.mkdir(exist_ok=True)
manifest=B/'approved-expectations.json';out=E/'fresh'
env={**os.environ,'AIR_ORIGIN_REGRESSION':'1','AIR_ORIGIN_HTML':'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html','AIR_ORIGIN_OUT':str(out),'PYTHONPATH':str(B/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
flag=['--approved-air-origin-baselines',str(manifest)]
jobs=[('paired42',[sys.executable,str(R/'docs/helicopter/F/verify_regression.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B1.html'),str(R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html'),str(out/'paired42'),'--baseline-only']+flag),('world120',[sys.executable,str(R/'docs/map/E/verify_delivery_world.py')]+flag)]
start=time.perf_counter()
def run(job):
 name,cmd=job;at=time.perf_counter()
 with(E/(name+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 row={'name':name,'exitCode':p.returncode,'elapsedS':time.perf_counter()-at};print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:rows=list(pool.map(run,jobs))
(E/'execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start,'pass':all(r['exitCode']==0 for r in rows)},indent=2)+'\n')
raise SystemExit(any(r['exitCode']for r in rows))
