"""First implementation stage: AIR OFF exactness + alignment-only A/B."""
from pathlib import Path
import concurrent.futures,copy,json,os,subprocess,sys,time
from playwright.sync_api import sync_playwright
from harness import P,B,R,OFF,build,serve,load_http,launch,sha
E=Path(os.environ.get('B2_ALIGNMENT_OUT',str(P/'evidence/alignment')));E.mkdir(parents=True,exist_ok=True)
def worker(i):
 cases=[]
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  for bearing in [0,90]:
   for seed in [419010,419012]:
    for enabled in [False,True]:cases.append({'ship':ship,'bearing':bearing,'seed':seed,'count':1,'on':True,'flags':{},'experiment':'BASE','alignment':enabled})
 rows=[];errors=[];start=time.perf_counter()
 with sync_playwright()as pw:
  browser=launch(pw)
  for c in cases[i::2]:
   flags={**OFF,'alignment':c['alignment']};raw=build(flags=flags);server,url=serve(raw);page=load_http(browser,url,own=c['ship'],errors=errors);page.set_default_timeout(600000);q=page.evaluate('c=>({data:__G2D__.run(c),b2:__GUN_B2__.snapshot()})',c);page.close();page.context.close();server.shutdown();rows.append({'case':c,**q,'productSha256':sha((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes())});print(c['ship'],c['bearing'],c['seed'],c['alignment'],len(q['data']['shots']),flush=True)
  browser.close()
 (E/f'worker{i}.json').write_text(json.dumps({'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-start},separators=(',',':'))+'\n')
if len(sys.argv)>1 and sys.argv[1]!='--collect':worker(int(sys.argv[1]));raise SystemExit()
start=time.perf_counter();env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
def run(i):
 with(E/f'worker{i}.log').open('w')as f:r=subprocess.run([sys.executable,__file__,str(i)],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0
if '--collect'not in sys.argv:
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(run,range(2)))
def clean(d):
 d=copy.deepcopy(d);d['result'].pop('elapsedMs',None);d['refreshSummary'].pop('totalMs',None)
 for x in d['refreshSummary']['samples']:x.pop('elapsedMs',None)
 d.pop('caseBootState',None);return d
old=[json.loads(l)for f in(B/'post-origin/evidence').glob('worker*.jsonl')for l in f.read_text().splitlines()];reports=[json.loads((E/f'worker{i}.json').read_text())for i in range(2)];rows=[r for q in reports for r in q['rows']];checks={}
for r in rows:
 c=r['case'];key=(c['ship'],c['bearing'],c['seed']);ref=next(x for x in old if(x['ship'],x['bearing'],x['seed'])==key)
 if not c['alignment']:checks['OFF_EXACT:'+str(key)]=clean(r['data'])==clean(ref['data'])
 else:checks['CURRENT_TICK:'+str(key)]=bool(r['data']['shots'])and all(s['solutionAgeS']==0 for s in r['data']['shots'])
checks['count16']=len(rows)==16;checks['pageErrors0']=all(not q['errors']for q in reports)
q={'pass':all(checks.values()),'checks':checks,'rows':rows,'elapsedS':time.perf_counter()-start};(E/'results.json').write_text(json.dumps(q,separators=(',',':'))+'\n');print(json.dumps({'pass':q['pass'],'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(not q['pass'])
