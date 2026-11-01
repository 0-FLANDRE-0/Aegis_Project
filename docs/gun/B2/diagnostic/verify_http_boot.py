"""Exact same game/results against route.fulfil, only byte transport differs."""
from pathlib import Path
import copy,json,sys,time
from playwright.sync_api import sync_playwright
from build_fixture import build,R,B
from http_browser import serve,load_http
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch
rows=[]
for p in(B/'evidence/trials').glob('worker*.jsonl'):
 for line in p.read_text().splitlines():
  try:rows.append(json.loads(line))
  except ValueError:pass
cases=[r for r in rows if r['seed']==419010 and r['count']==1 and r['experiment']=='BASE'];assert len(cases)==4
def clean(d):
 d=copy.deepcopy(d);d['result'].pop('elapsedMs',None);d['refreshSummary'].pop('totalMs',None)
 for s in d['refreshSummary']['samples']:s.pop('elapsedMs',None)
 return d
out=B/'evidence/http-boot';out.mkdir(parents=True,exist_ok=True);errors=[];results=[];raw=build();server,url=serve(raw);start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for c in cases:
  at=time.perf_counter();p=load_http(b,url,own=c['ship'],errors=errors);boot=time.perf_counter()-at;p.set_default_timeout(600000)
  q=p.evaluate('c=>{const s=__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A();const boot={navigation:s.ship.navigation,hp:s.ship.shipHP};const r=__G2D__.run(c);r.caseBootState=boot;return r;}',c)
  r={'caseId':c['caseId'],'ship':c['ship'],'bearing':c['bearing'],'equal':clean(q)==clean(c['data']),'routeBootS':c['bootS'],'httpBootS':boot,'http':q};results.append(r);(out/'progress.json').write_text(json.dumps(results,separators=(',',':'))+'\n');print(c['caseId'],r['equal'],r['routeBootS'],r['httpBootS'],flush=True);p.close()
 b.close()
server.shutdown();result={'pass':all(r['equal']for r in results)and not errors,'rows':results,'errors':errors,'elapsedS':time.perf_counter()-start};(out/'results.json').write_text(json.dumps(result,separators=(',',':'))+'\n');raise SystemExit(not result['pass'])
