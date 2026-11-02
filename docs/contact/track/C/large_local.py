"""Native shared solver stress using anonymous observed states/covariance, no RF tuning."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3]
sys.path[:0]=[str(R/'docs/missile/fuze-zem/A'),str(R/'docs/gun/B2/phase1b'),str(R/'docs/gun/B2/diagnostic')]
from browser_tools import instrument,launch
from http_browser import serve
from fast_http import load_fast_http
from playwright.sync_api import sync_playwright
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
HELPER=r'''window.__TRACK_C_LARGE_NATIVE__={run(){
 const before=__TRACK_RUNTIME_A__.state(),cfg=CIWS_LOCAL_TRACK_MODEL.GUN;
 function fixture(n,spacing){return {files:new Map(Array.from({length:n},(_,i)=>[-9000-i,{id:-9000-i,ownFireEvidence:false,st:{rxM:i*spacing,ryM:0,rzM:0,localHits:10,localAgeS:0,_c55P:[[.1,0,4],[.1,0,4],[.1,0,4]]}}])),plots:Array.from({length:n},(_,i)=>({knownOwnLaunch:false,measurement:{rxM:i*spacing,ryM:0,rzM:0,rangeM:100,positionVarianceM2:[.5,.5,.5]}}))};}
 const separated=fixture(13,3),equal=fixture(48,0),a=performance.now(),r=__TRACK_C__.c55Assignments(separated.plots,separated.files,cfg),b=performance.now(),q=__TRACK_C__.c55Assignments(equal.plots,equal.files,cfg),c=performance.now();
 return {checks:{dense13DistinctNotAllHeld:r.pairs.length===13&&r.heldPlots.size===0,dense13ActuallyConnectedComponent:r.components.some(x=>x.plots.length===13&&x.tracks.length===13),dense48UnobservableConservativeHold:q.pairs.length===0&&q.heldPlots.size===48&&q.heldTracks.size===48,privateWorldAndRngUnchanged:before===__TRACK_RUNTIME_A__.state()},dense13:{pairs:r.pairs,components:r.components,held:r.heldPlots.size,wallMs:b-a},dense48:{pairs:q.pairs.length,components:q.components,held:q.heldPlots.size,wallMs:c-b},inputMeaning:'Synthetic anonymous KF states/covariances and measured R are fixture input only; no game coefficients/RF/KF parameters changed.'};
}};'''
def main():
 out=P/'evidence/large-local';out.mkdir(parents=True,exist_ok=True);build=json.loads((P/'BUILD.json').read_text());body=(R/build['html']).read_bytes();assert hashlib.sha256(body).hexdigest()==build['htmlSha256'];slots=module('slots_large_c',P.with_name('B')/'regression_runner.py');old=module('passive_large_c',P.with_name('A')/'verify_runtime.py');server,url=serve(instrument(body,HELPER+'\n'+old.PASSIVE_HELPER));errors=[];at=time.monotonic()
 try:
  with slots.heavy_browser_slot(),sync_playwright()as pw:
   browser=launch(pw);page=load_fast_http(browser,url,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);q=page.evaluate('__TRACK_C_LARGE_NATIVE__.run()');browser.close()
 finally:server.shutdown()
 q.update(pass_=all(q['checks'].values())and not errors,errors=errors,htmlSha256=build['htmlSha256'],helperSha256=hashlib.sha256(HELPER.encode()).hexdigest(),wallS=time.monotonic()-at);q['pass']=q.pop('pass_');(out/'RESULTS.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));return 0 if q['pass']else 1
if __name__=='__main__':raise SystemExit(main())
