"""Two final-model natural full-tick repeats, fresh page/context each time."""
from pathlib import Path
import copy,json
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,sha
from fast_http import load_fast_http
rows=[json.loads(l)for p in(P/'evidence/g7').glob('*.jsonl')for l in p.read_text().splitlines()];assert len(rows)==960
cases=[next(r for r in rows if r['ship']==ship and r['bearing']==90 and r['count']==4 and r['seed']==419010 and r['on'])for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']];out=[];errors=[]
def clean(value):
 q=copy.deepcopy(value);q['result'].pop('elapsedMs',None);q['diagnostic']['b2'].pop('refreshMs',None);return q
profile=r"""
window.__B2_REPEAT_PERF__={ticks:[],refresh:[]};
{const tick=simulateFixedTick,prepare=gunB2PrepareRelease;
 simulateFixedTick=function(){const a=performance.now();try{return tick(...arguments);}finally{__B2_REPEAT_PERF__.ticks.push(performance.now()-a);}};
 gunB2PrepareRelease=function(){const count=gunB2Diagnostics.refreshAttempts,a=performance.now();try{return prepare(...arguments);}finally{if(gunB2Diagnostics.refreshAttempts>count)__B2_REPEAT_PERF__.refresh.push(performance.now()-a);}};
}
"""
raw=build(record=False,extra=(P/'g7_observer.js').read_text()+profile);server,url=serve(raw)
with sync_playwright()as pw:
 b=launch(pw)
 for old in cases:
  assert old['htmlSha256']==sha((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes());c={k:old[k]for k in ['ship','bearing','count','seed','on','caseId']};p=load_fast_http(b,url,own=c['ship'],errors=errors);p.set_default_timeout(600000);new=p.evaluate('c=>({result:__B2_G7_RUN__(c),diagnostic:__B2_G7_LOG__()})',c);perf=p.evaluate('__B2_REPEAT_PERF__');p.close();p.context.close();original={k:old[k]for k in ['result','diagnostic']};out.append({'case':c,'exact':clean(new)==clean(original),'original':original,'repeat':new,'hostCpuDiagnosticMs':perf});print(c['ship'],out[-1]['exact'],flush=True)
 b.close()
server.shutdown();q={'pass':all(r['exact']for r in out)and not errors,'rows':out,'errors':errors,'performanceScope':'Headless host full fixed-tick CPU under concurrent validation, includes diagnostic observer; not render/GPU or phone FPS. No game input altered.','ignoredHostFieldsOnly':['result.elapsedMs','diagnostic.b2.refreshMs']};(P/'evidence/g7-repeat.json').write_text(json.dumps(q,separators=(',',':'))+'\n');raise SystemExit(not q['pass'])
