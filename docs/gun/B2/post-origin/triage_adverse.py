"""Two native runs of the adverse seed; passive damage-draw tap, no extra draws."""
from pathlib import Path
import copy,gzip,json,sys,time
from playwright.sync_api import sync_playwright
from source import P,B,D,R,build,NATIVE,sha
sys.path[:0]=[str(D),str(R/'docs/missile/fuze-zem/A')]
from build_fixture import build as old_build
from http_browser import serve,load_http
from browser_tools import instrument,launch
E=P/'evidence';before=[json.loads(l)for l in gzip.decompress((E/'reviewed-before-60.jsonl.gz').read_bytes()).decode().splitlines()];after=[json.loads(l)for p in E.glob('worker*.jsonl')for l in p.read_text().splitlines()]
choose=lambda rows:next(r for r in rows if r['ship']=='DDG_119_LATE_FLIGHT_IIA'and r['bearing']==90 and r['seed']==419023)
tap=r'''
window.__ADVERSE_DRAW_LOG__=[];
{let record=null;const originalRandom=simRandom,originalApply=applyInterceptResult;
 simRandom=function(...args){const value=originalRandom(...args);if(record)record.draws.push(value);return value;};
 applyInterceptResult=function(pk,target,weapon,trackId){const parent=record,row={step:simStepCounter,pk,targetId:target.id,weapon,trackId,draws:[],rngBefore:SIM_RNG_STATE};record=row;let result;try{result=originalApply(...arguments);row.result=result;row.rngAfter=SIM_RNG_STATE;window.__ADVERSE_DRAW_LOG__.push(row);return result;}finally{record=parent;}};
}
window.__ADVERSE_AFTER__=()=>({draws:window.__ADVERSE_DRAW_LOG__,actualShipHits:shipHitHistory.filter(h=>!h.miss).length,core:window.__CORE_SELFTEST_FAILURES__});
'''
def clean(d):
 d=copy.deepcopy(d);d['result'].pop('elapsedMs',None);return d
errors=[];rows=[];started=time.perf_counter()
with sync_playwright()as pw:
 browser=launch(pw)
 for tag,original,raw in [('BEFORE',choose(before),old_build(False,NATIVE)),('AFTER',choose(after),build(False))]:
  body=instrument(raw,tap);server,url=serve(body);page=load_http(browser,url,own=original['ship'],errors=errors);page.set_default_timeout(600000);q=page.evaluate('c=>__POST_ORIGIN_NATIVE__(c)',original);first={k:original['data'][k]for k in q};extra=page.evaluate('__ADVERSE_AFTER__()');rows.append({'tag':tag,'nativeEqualToRecorded':clean(q)==clean(first),'native':q,'diagnostic':extra,'instrumentedHtmlSha256':sha(body)});print(tag,rows[-1]['nativeEqualToRecorded'],'hp',q['result']['hpAfter'],'draw events',len(extra['draws']),flush=True);page.close();page.context.close();server.shutdown()
 browser.close()
result={'pass':not errors and all(r['nativeEqualToRecorded']and not r['diagnostic']['core']for r in rows),'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-started,'targetCase':{'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':419023,'count':1},'policy':'Passive wrapper calls original simRandom and original applyInterceptResult once; draws are recorded after being generated and never supplied back. Exact result/RNG/state equality checked against original records.'};(E/'adverse-native.json').write_text(json.dumps(result,indent=2)+'\n');raise SystemExit(not result['pass'])
