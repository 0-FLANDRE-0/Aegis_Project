"""Phase 0 matched G7 trials. Product on disk is SHA-locked and never modified."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time
from playwright.sync_api import sync_playwright
from build_fixture import build,R,B
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet
from http_browser import serve,load_http
p=argparse.ArgumentParser();p.add_argument('--worker',type=int,default=0);p.add_argument('--workers',type=int,default=1);p.add_argument('--seeds',type=int,default=30);p.add_argument('--experiments',default='BASE,B,C,D');p.add_argument('--output',default='trials');p.add_argument('--transport',choices=['http','cdp'],default='http');args=p.parse_args()
flags={'BASE':{},'A':{'stopped':True},'B':{'fresh':True},'C':{'straight':True},'D':{'strict':True}}
jobs=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 for bearing in [0,90]:
  for count in range(1,5):
   for i in range(args.seeds):
    for ex in args.experiments.split(','):jobs.append({'ship':ship,'seed':419010+i,'bearing':bearing,'count':count,'on':True,'experiment':ex,'flags':flags[ex]})
out=B/'evidence'/args.output;out.mkdir(parents=True,exist_ok=True);path=out/f'worker{args.worker}.jsonl';seen=set()
if path.exists():
 for l in path.read_text().splitlines():
  try:seen.add(json.loads(l)['caseId'])
  except ValueError:pass
jobs=[{**q,'caseId':i}for i,q in enumerate(jobs)if i%args.workers==args.worker and i not in seen];errors=[];owner=None;page=None;start=time.perf_counter();raw=build();instrumented_sha=hashlib.sha256(raw).hexdigest();tool_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in Path(__file__).parent.glob('*')if p.is_file()}
jobs.sort(key=lambda c:(c['seed'],c['count'],c['bearing'],c['ship'],c['experiment'])) # coverage across hulls/aspects early; each case is isolated
server,url=serve(raw)if args.transport=='http'else(None,None)
with path.open('a')as f,sync_playwright()as pw:
 browser=launch(pw)
 for n,c in enumerate(jobs):
  # Operational save/load intentionally does not capture all transient JS state
  # (e.g. telegraph/shaft RPM when maneuver.enabled is false). Never share that
  # state across controls or seeds: each case boots an independent game page.
  if page:page.close();page.context.close()
  boot=time.perf_counter();owner=c['ship'];page=load_http(browser,url,own=owner,errors=errors)if args.transport=='http'else load_fleet(browser,raw,own=owner,errors=errors);page.set_default_timeout(600000);boot_s=time.perf_counter()-boot
  t=time.perf_counter();q=page.evaluate('c=>{const s=__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A();const boot={navigation:s.ship.navigation,hp:s.ship.shipHP};const r=__G2D__.run(c);r.caseBootState=boot;return r;}',c);row={**c,'data':q,'wallS':time.perf_counter()-t,'bootS':boot_s,'transport':args.transport,'isolation':'FRESH_GAME_PAGE_PER_CASE','instrumentedHtmlSha256':instrumented_sha};f.write(json.dumps(row,separators=(',',':'))+'\n');f.flush()
  print(json.dumps({'worker':args.worker,'done':n+1,'remaining':len(jobs)-n-1,'caseId':c['caseId'],'experiment':c['experiment'],'wallS':row['wallS'],'elapsedS':time.perf_counter()-start,'shots':q['result']['shots']}),flush=True)
 if page:page.close();page.context.close()
 browser.close()
if server:server.shutdown()
(out/f'worker{args.worker}-complete.json').write_text(json.dumps({'cases':len(jobs)+len(seen),'errors':errors,'elapsedS':time.perf_counter()-start,'instrumentedHtmlSha256':instrumented_sha,'toolHashes':tool_hashes,'htmlSha256':hashlib.sha256((R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes()).hexdigest()},indent=2)+'\n')
