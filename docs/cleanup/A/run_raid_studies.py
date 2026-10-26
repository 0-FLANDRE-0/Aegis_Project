from pathlib import Path
import concurrent.futures,json,subprocess,sys,time
H=Path(__file__).resolve().parent;R=H.parents[2];start=time.perf_counter();out=H/'evidence/raid';out.mkdir(exist_ok=True);rows=[]
jobs=[(v,s)for v in ['KAPPA','DZT','HANDOFF','LATEST']for s in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']]
def run(job):
 v,s=job
 with(out/(v+'_'+s+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(H/'raid_study.py'),v,s],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 return {'variant':v,'ship':s,'exitCode':p.returncode}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
 for row in pool.map(run,jobs):rows.append(row);print(json.dumps(row),flush=True)
(out/'execution.json').write_text(json.dumps({'rows':rows,'elapsedS':time.perf_counter()-start},indent=2)+'\n')
