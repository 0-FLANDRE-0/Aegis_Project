"""Four native matches + two deterministic replays; not part of the 60 cases."""
from pathlib import Path
import copy,json,sys,time
from playwright.sync_api import sync_playwright
from source import P,D,R,build,sha
sys.path[:0]=[str(D),str(R/'docs/missile/fuze-zem/A')]
from http_browser import serve,load_http
from browser_tools import launch
E=P/'evidence';rows=[json.loads(l)for p in E.glob('worker*.jsonl')for l in p.read_text().splitlines()];assert len(rows)==60
cases=[r for r in rows if r['seed']==419010];assert len(cases)==4
def clean(d):
 d=copy.deepcopy(d)
 if 'result'in d:d['result'].pop('elapsedMs',None)
 if 'refreshSummary'in d:
  d['refreshSummary'].pop('totalMs',None)
  for q in d['refreshSummary']['samples']:q.pop('elapsedMs',None)
 return d
errors=[];records=[];started=time.perf_counter();fingerprints=[];expected=json.loads((E/'static.json').read_text())['runtimeExpectedHashes']
with sync_playwright()as pw:
 browser=launch(pw)
 for native in [True,False]:
  server,url=serve(build(not native))
  for c in cases:
   if not native and c['bearing']!=90:continue
   page=load_http(browser,url,own=c['ship'],errors=errors);page.set_default_timeout(600000)
   fn={k:sha(v.encode())for k,v in page.evaluate('__POST_ORIGIN_SOURCES__()').items()};fingerprints.append({'native':native,'ship':c['ship'],'bearing':c['bearing'],'hashes':fn,'matches':fn==expected})
   if native:
    replay=page.evaluate('c=>__POST_ORIGIN_NATIVE__(c)',c);first={k:c['data'][k]for k in replay}
   else:
    replay=page.evaluate('c=>{const s=__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A();const boot={navigation:s.ship.navigation,hp:s.ship.shipHP};const r=__G2D__.run(c);r.caseBootState=boot;return r;}',c);first=c['data']
   records.append({'kind':'NATIVE_VS_INSTRUMENTED'if native else'DETERMINISTIC_REPLAY','ship':c['ship'],'bearing':c['bearing'],'seed':c['seed'],'equal':clean(first)==clean(replay),'replay':replay});page.close();page.context.close();print(records[-1]['kind'],c['ship'],c['bearing'],records[-1]['equal'],flush=True)
  server.shutdown()
 browser.close()
q={'pass':not errors and all(r['equal']for r in records)and all(r['matches']for r in fingerprints),'records':records,'fingerprints':fingerprints,'errors':errors,'elapsedS':time.perf_counter()-started,'excludedFields':['result.elapsedMs','refreshSummary.totalMs','refreshSummary.samples[*].elapsedMs']};(E/'equivalence.json').write_text(json.dumps(q,separators=(',',':'))+'\n');raise SystemExit(not q['pass'])
