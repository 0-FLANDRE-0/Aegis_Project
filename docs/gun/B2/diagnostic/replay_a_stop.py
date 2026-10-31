"""Re-run all A cases from the sealed original matrix, retaining original IDs."""
from pathlib import Path
import argparse,hashlib,json,sys,time
from playwright.sync_api import sync_playwright
from build_a_stop import build_corrected,B,R
from http_browser import serve,load_http
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch
p=argparse.ArgumentParser();p.add_argument('--worker',type=int,default=0);p.add_argument('--workers',type=int,default=4);p.add_argument('--probe',action='store_true');args=p.parse_args()
source=[]
for f in(B/'evidence/trials').glob('worker*.jsonl'):
 source.extend(json.loads(l)for l in f.read_text().splitlines())
if args.probe:
 # A failing post-impact condition, plus BASE/B/C/D proving the guard's isolation.
 ids=[1061,1060,1062,1063,1064]
 jobs=[r for r in source if r['caseId']in ids];out=B/'evidence/a-stop-probe'
else:
 jobs=[r for r in source if r['experiment']=='A'];jobs.sort(key=lambda r:r['caseId']);jobs=jobs[args.worker::args.workers];out=B/'evidence/a-stop-corrected'
out.mkdir(parents=True,exist_ok=True);path=out/f'worker{args.worker}.jsonl';seen={json.loads(l)['caseId']for l in path.read_text().splitlines()}if path.exists()else set();jobs=[r for r in jobs if r['caseId']not in seen]
raw=build_corrected();sha=hashlib.sha256(raw).hexdigest();server,url=serve(raw);errors=[];start=time.perf_counter();page=None
with path.open('a')as f,sync_playwright()as pw:
 browser=launch(pw)
 for n,r in enumerate(jobs):
  c={k:r[k]for k in ['caseId','ship','seed','bearing','count','on','experiment','flags']}
  if page:page.close();page.context.close()
  t=time.perf_counter();page=load_http(browser,url,own=c['ship'],errors=errors);page.set_default_timeout(600000);boot=time.perf_counter()-t;t=time.perf_counter()
  data=page.evaluate('c=>{const s=__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A();const boot={navigation:s.ship.navigation,hp:s.ship.shipHP};const r=__G2D__.run(c);r.caseBootState=boot;return r;}',c)
  row={**c,'data':data,'bootS':boot,'wallS':time.perf_counter()-t,'transport':'http','isolation':'FRESH_GAME_PAGE_PER_CASE','instrumentedHtmlSha256':sha,'diagnosticRevision':'A_NATIVE_INTERNAL_SWAY_STOP_1','replacesOriginalInstrumentedSha256':r['instrumentedHtmlSha256']}
  f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush();print(json.dumps({'worker':args.worker,'caseId':c['caseId'],'done':n+1,'remaining':len(jobs)-n-1,'shots':len(data['shots']),'elapsedS':time.perf_counter()-start}),flush=True)
 if page:page.close();page.context.close()
 browser.close()
server.shutdown()
(out/f'worker{args.worker}-complete.json').write_text(json.dumps({'cases':len(jobs)+len(seen),'errors':errors,'instrumentedHtmlSha256':sha,'elapsedS':time.perf_counter()-start},indent=2)+'\n')
