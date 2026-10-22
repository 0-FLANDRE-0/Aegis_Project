"""Real WebGL + complete simulateFixedTick pipeline, native target AI retained."""
import argparse,base64,hashlib,json,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(H));from verify_live import instrument
from browser import launch,load_fleet
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];rows=[];checks={}
with sync_playwright()as pw:
 b=launch(pw,True);p=load_fleet(b,instrument(raw),own='DDG_119_LATE_FLIGHT_IIA',width=1000,height=760,errors=errors);p.set_default_timeout(180000)
 p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready&&__WIP148_3D_VIEW__.active',timeout=180000,polling=50)
 for w in ['SM2','SM2ER','SM6','ESSM']:
  q=p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',{'weapon':w,'rangeKm':15 if w=='ESSM'else 30,'altM':5000,'maxTimeS':0,'useRequest':True});checks[w+'.nativeRequest']=q.get('releaseRequest')and bool(q.get('releaseRecord'))
  samples=[]
  for i in range(80):
   p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(60)');s=p.evaluate('__TERM_LIVE_TEST__.observe()');samples.append(s)
   if i==2:
    p.wait_for_timeout(250);cdp=p.context.new_cdp_session(p);(a.out/(w+'-launch.png')).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']));cdp.detach()
   if s['dead']:break
  before=p.evaluate('__WIP148_3D_VIEW__.renderer.info.render.frame');p.wait_for_function('n=>__WIP148_3D_VIEW__.renderer.info.render.frame>n',arg=before,timeout=30000,polling=50);after=p.evaluate('__WIP148_3D_VIEW__.renderer.info.render.frame');checks[w+'.fullWorldFlight']=samples[-1]['lifeS']>3;checks[w+'.noException']=not errors;checks[w+'.webglContinues']=after>before
  last=samples[-1];term=last.get('term')or{};reason=last.get('reason')or''
  checks[w+'.terminationClockValid']=not reason.startswith('TERMINAL_')or(reason=='TERMINAL_MISS_POST_CROSS'and last['lifeS']>=term['predictedCrossS']+2.5 and last['lifeS']>=term['lastGoodS']+2.5)or(reason=='TERMINAL_SEARCH_NO_ACQUISITION'and last['lifeS']>=max(term['firstActiveS'],term.get('lastSupportS',0))+12)
  rows.append({'weapon':w,'final':last,'samples':samples,'webglFrameBefore':before,'webglFrameAfter':after});print(w,last['reason'],last['lifeS'],before,after,flush=True)
 checks['core']=p.evaluate('__CORE_SELFTEST_FAILURES__.length===0');renderer=p.evaluate('()=>{const g=__WIP148_3D_VIEW__.renderer.getContext(),e=g.getExtension("WEBGL_debug_renderer_info");return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):"unknown"}');b.close()
q={'pass':all(checks.values()),'checks':checks,'records':rows,'errors':errors,'renderer':renderer,'htmlSha256':hashlib.sha256(raw).hexdigest(),'method':'full simulateFixedTick via stepTicks, actual target AI/sensors/weapon allocation retained; test-only initial target/loadout/launch setup'};(a.out/'full-world-3d.json').write_text(json.dumps(q,indent=2));print(json.dumps({'pass':q['pass'],'checks':checks,'errors':errors}));raise SystemExit(0 if q['pass']else 1)
