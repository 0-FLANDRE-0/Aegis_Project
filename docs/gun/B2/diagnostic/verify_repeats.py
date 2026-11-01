"""Fixed, predeclared A/B/C/D replay samples; no outcome-based sample selection."""
from pathlib import Path
import copy,hashlib,json,sys,time
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
cases=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 for i,ex in enumerate(['A','B','C','D']):
  bearing=0 if i%2==0 else 90
  cases.append(next(r for r in rows if(r['ship'],r['bearing'],r['count'],r['seed'],r['experiment'])==(ship,bearing,1,419010,ex)))
def clean(d):
 d=copy.deepcopy(d);d['result'].pop('elapsedMs',None);d['refreshSummary'].pop('totalMs',None)
 for s in d['refreshSummary']['samples']:s.pop('elapsedMs',None)
 return d
def digest(d):return hashlib.sha256(json.dumps(clean(d),sort_keys=True,separators=(',',':')).encode()).hexdigest()
out=B/'evidence/repeats';out.mkdir(parents=True,exist_ok=True);errors=[];results=[];raw=build();server,url=serve(raw);start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for c in cases:
  p=load_http(b,url,own=c['ship'],errors=errors);p.set_default_timeout(600000)
  q=p.evaluate('c=>{const s=__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A();const boot={navigation:s.ship.navigation,hp:s.ship.shipHP};const r=__G2D__.run(c);r.caseBootState=boot;return r;}',c)
  r={'caseId':c['caseId'],'ship':c['ship'],'bearing':c['bearing'],'experiment':c['experiment'],'equal':clean(q)==clean(c['data']),'firstHash':digest(c['data']),'replayHash':digest(q),'replay':q};results.append(r);(out/'progress.json').write_text(json.dumps(results,separators=(',',':'))+'\n');print(c['caseId'],c['experiment'],r['equal'],flush=True);p.close()
 b.close()
server.shutdown();result={'pass':all(r['equal']for r in results)and not errors,'rows':results,'errors':errors,'elapsedS':time.perf_counter()-start,'excludedFields':['result.elapsedMs','refreshSummary.totalMs','refreshSummary.samples[*].elapsedMs']};(out/'results.json').write_text(json.dumps(result,separators=(',',':'))+'\n');raise SystemExit(not result['pass'])
