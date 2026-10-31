"""G7 final model, native full ticks, a fresh game page for every trial."""
from pathlib import Path
import concurrent.futures,json,os,subprocess,sys,time
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,sha
from fast_http import load_fast_http
E=Path(os.environ.get('B2_G7_OUT',str(P/'evidence/g7')));E.mkdir(parents=True,exist_ok=True)
def worker(w,n):
 jobs=[{'ship':ship,'bearing':bearing,'count':count,'seed':419010+s,'on':on}for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']for bearing in [0,90]for count in range(1,5)for s in range(30)for on in [False,True]]
 path=E/f'worker{w}.jsonl';seen={json.loads(l)['caseId']for f in E.glob('*.jsonl')for l in f.read_text().splitlines()};jobs=[{**c,'caseId':i}for i,c in enumerate(jobs)if i%n==w and i not in seen];jobs.sort(key=lambda c:(c['seed'],c['count'],c['bearing'],c['ship'],c['on']))
 productSha=sha((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes())
 existing=[json.loads(l)for f in E.glob('*.jsonl')for l in f.read_text().splitlines()]
 assert all(r['htmlSha256']==productSha for r in existing),'G7_CACHE_REQUIRES_IDENTICAL_HTML_USE_B2_G7_OUT_FOR_FRESH_RUN'
 raw=build(record=False,extra=(P/'g7_observer.js').read_text());server,url=serve(raw);errors=[];start=time.perf_counter()
 with path.open('a')as f,sync_playwright()as pw:
  b=launch(pw)
  for j,c in enumerate(jobs):
   p=load_fast_http(b,url,own=c['ship'],errors=errors);p.set_default_timeout(600000);at=time.perf_counter();q=p.evaluate('c=>({result:__B2_G7_RUN__(c),diagnostic:__B2_G7_LOG__()})',c);p.close();p.context.close();f.write(json.dumps({**c,**q,'wallS':time.perf_counter()-at,'htmlSha256':productSha},separators=(',',':'))+'\n');f.flush()
   if j%5==0:print(json.dumps({'worker':w,'done':j+1,'total':len(jobs),'elapsedS':time.perf_counter()-start}),flush=True)
  b.close()
 server.shutdown();(E/f'worker{w}-complete.json').write_text(json.dumps({'cases':len(jobs)+sum(i%n==w for i in seen),'reusedCases':sum(i%n==w for i in seen),'errors':errors,'elapsedS':time.perf_counter()-start,'htmlSha256':productSha},indent=2)+'\n')
if len(sys.argv)>1:worker(int(sys.argv[1]),int(sys.argv[2]));raise SystemExit()
env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
def run(w):
 with(E/f'worker{w}.log').open('w')as f:r=subprocess.run([sys.executable,'-u',__file__,str(w),'3'],env=env,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 return {'worker':w,'exit':r.returncode}
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:rows=list(pool.map(run,range(3)))
(E/'execution.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
