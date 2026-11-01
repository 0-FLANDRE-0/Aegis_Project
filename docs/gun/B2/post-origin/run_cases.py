"""Exactly DDG/CG x0/90 x15 fixed seeds, one target, BASE flags only."""
from pathlib import Path
import argparse,json,sys,time
from playwright.sync_api import sync_playwright
from source import B,D,P,R,build,provenance,sha
sys.path[:0]=[str(D),str(R/'docs/missile/fuze-zem/A')]
from http_browser import serve,load_http
from browser_tools import launch
parser=argparse.ArgumentParser();parser.add_argument('--worker',type=int,required=True);parser.add_argument('--workers',type=int,default=2);a=parser.parse_args()
E=P/'evidence';E.mkdir(exist_ok=True);jobs=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 for bearing in [0,90]:
  for seed in range(419010,419025):jobs.append({'caseId':len(jobs),'ship':ship,'bearing':bearing,'seed':seed,'count':1,'on':True,'experiment':'BASE','flags':{}})
assert len(jobs)==60
path=E/f'worker{a.worker}.jsonl';seen=set()
if path.exists():seen={json.loads(line)['caseId']for line in path.read_text().splitlines()}
jobs=[c for c in jobs if c['caseId']%a.workers==a.worker and c['caseId']not in seen];jobs.sort(key=lambda c:(c['seed'],c['bearing'],c['ship']))
raw=build();server,url=serve(raw);rows=[];errors=[];started=time.perf_counter();fingerprint=None
with path.open('a')as f,sync_playwright()as pw:
 browser=launch(pw)
 for i,c in enumerate(jobs):
  at=time.perf_counter();page=load_http(browser,url,own=c['ship'],errors=errors);page.set_default_timeout(600000)
  if fingerprint is None:fingerprint={k:sha(v.encode())for k,v in page.evaluate('__POST_ORIGIN_SOURCES__()').items()}
  result=page.evaluate('c=>{const s=__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A();const boot={navigation:s.ship.navigation,hp:s.ship.shipHP};const r=__G2D__.run(c);r.caseBootState=boot;return r;}',c)
  row={**c,'data':result,'wallS':time.perf_counter()-at,'isolation':'FRESH_GAME_PAGE_PER_CASE','transport':'http','instrumentedHtmlSha256':sha(raw),'productHtmlSha256':provenance()['productHtmlSha256']};f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush();page.close();page.context.close();rows.append(c['caseId']);print(json.dumps({'worker':a.worker,'done':i+1,'caseId':c['caseId'],'ship':c['ship'],'bearing':c['bearing'],'seed':c['seed'],'shots':result['result']['shots'],'wallS':row['wallS']}),flush=True)
 browser.close()
server.shutdown();q={'cases':len(rows)+len(seen),'caseIds':rows,'errors':errors,'elapsedS':time.perf_counter()-started,'instrumentedHtmlSha256':sha(raw),'runtimeFunctionHashes':fingerprint,'provenance':provenance()};(E/f'worker{a.worker}-complete.json').write_text(json.dumps(q,indent=2)+'\n');raise SystemExit(bool(errors))
