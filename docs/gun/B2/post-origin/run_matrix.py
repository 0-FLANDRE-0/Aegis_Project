"""Two independent browser worker processes, not delegated agents."""
from pathlib import Path
import concurrent.futures,json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence';E.mkdir(exist_ok=True)
started=time.perf_counter();env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
def run(i):
 at=time.perf_counter()
 with(E/f'worker{i}.log').open('w')as f:p=subprocess.run([sys.executable,str(P/'run_cases.py'),'--worker',str(i),'--workers','2'],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 return {'worker':i,'exitCode':p.returncode,'elapsedS':time.perf_counter()-at}
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:rows=list(pool.map(run,range(2)))
q={'rows':rows,'elapsedS':time.perf_counter()-started,'pass':all(r['exitCode']==0 for r in rows)};(E/'execution.json').write_text(json.dumps(q,indent=2)+'\n');raise SystemExit(not q['pass'])
