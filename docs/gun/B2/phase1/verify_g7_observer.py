from pathlib import Path
import copy,json,time
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch
from fast_http import load_fast_http
E=P/'evidence/g7-pilot';old=[json.loads(l)for f in E.glob('*.jsonl')for l in f.read_text().splitlines()];cases=[]
for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
 for bearing in [0,90]:
  q=next(x for x in old if x['ship']==ship and x['bearing']==bearing and x['seed']==419010 and x['count']==1 and x['on']);cases.append(q)
observer=(P/'g7_observer.js').read_text();raw=build(record=False,extra=observer);server,url=serve(raw);errors=[];rows=[]
with sync_playwright()as pw:
 b=launch(pw)
 for c in cases:
  at=time.perf_counter();p=load_fast_http(b,url,own=c['ship'],errors=errors);boot=time.perf_counter()-at;p.set_default_timeout(600000);q=p.evaluate('c=>({result:__B2_G7_RUN__(c),diagnostic:__B2_G7_LOG__()})',c);p.close();p.context.close();a=copy.deepcopy(c['result']);z=copy.deepcopy(q['result']);a.pop('elapsedMs');z.pop('elapsedMs');rows.append({'caseId':c['caseId'],'exactResult':a==z,'sameRng':q['diagnostic']['rng']==c['diagnostic']['rng'],'fastBootS':boot,'case':{k:c[k]for k in ['ship','bearing','count','seed','on','caseId']},'new':q});print(c['caseId'],a==z,boot,flush=True)
 b.close()
server.shutdown();result={'pass':all(r['exactResult']and r['sameRng']for r in rows)and not errors,'rows':rows,'errors':errors,'observerSource':observer};(P/'evidence/fast-observer.json').write_text(json.dumps(result,separators=(',',':'))+'\n');
if result['pass']:
 with(P/'evidence/g7/validated-startup.jsonl').open('w')as f:
  for r in rows:f.write(json.dumps({**r['case'],**r['new'],'wallS':None,'htmlSha256':__import__('hashlib').sha256((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes()).hexdigest(),'execution':'VALIDATED_FAST_STARTUP_NATIVE_RESULT_PARITY'},separators=(',',':'))+'\n')
raise SystemExit(not result['pass'])
