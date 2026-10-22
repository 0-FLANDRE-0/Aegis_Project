"""Fresh whole-game pages: naturally detected tracks -> native LOCK -> VLS ->
complete fixed ticks. Pair ON/OFF with native target AI; 3D on the ON runs.
"""
import argparse,base64,hashlib,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));from verify_live import instrument
from browser import launch,load_fleet
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];rows=[];checks={}
with sync_playwright()as pw:
 b=launch(pw,True)
 for w in ['SM2','SM2ER','SM6','ESSM']:
  pair=[]
  for enabled in [False,True]:
   page=load_fleet(b,instrument(raw),own='DDG_119_LATE_FLIGHT_IIA',width=1000,height=760,errors=errors);page.set_default_timeout(180000)
   c={'weapon':w,'rangeKm':15 if w=='ESSM'else 30,'bearingDeg':45,'enabled':enabled};page.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c);page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');launchResult=page.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
   if not launchResult.get('launched'):
    debug=page.evaluate('__TERM_LIVE_TEST__.debugObserved()');(a.out/'initial-track-debug.json').write_text(json.dumps(debug,indent=2));raise RuntimeError(str(launchResult))
   if enabled:
    page.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');page.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000,polling=50)
   samples=[]
   for i in range(250):
    page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(120)');s=page.evaluate('__TERM_LIVE_TEST__.observe()');samples.append(s)
    if enabled and i==1:
     d=page.context.new_cdp_session(page);(a.out/(w+'-native-observed-launch.png')).write_bytes(base64.b64decode(d.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']));d.detach()
    if s['dead']:break
   after=page.evaluate('__TERM_LIVE_TEST__.afterAction()');frames=None
   if enabled:
    old=page.evaluate('__WIP148_3D_VIEW__.renderer.info.render.frame');page.wait_for_function('n=>__WIP148_3D_VIEW__.renderer.info.render.frame>n',arg=old,timeout=30000,polling=50);frames=[old,page.evaluate('__WIP148_3D_VIEW__.renderer.info.render.frame')]
   checks[w+f'.{enabled}.nativeSensorTrack']=launchResult.get('localSensorSource')!='TEST';checks[w+f'.{enabled}.nativeRelease']=bool(launchResult.get('releaseRecord'));checks[w+f'.{enabled}.core']=page.evaluate('__CORE_SELFTEST_FAILURES__.length===0');r={'weapon':w,'enabled':enabled,'launch':launchResult,'final':after,'samples':samples,'framesAfterFlight':frames};rows.append(r);pair.append(r);print(w,enabled,after['missile']['reason'],after['targetAlive'],after['missile']['lifeS'],flush=True);page.close();(a.out/'observed-world-progress.json').write_text(json.dumps(rows,separators=(',',':')))
  checks[w+'.noPrematureRelativeToControl']=pair[0]['final']['targetAlive']or not pair[1]['final']['targetAlive']
 b.close()
checks['pageErrors']=not errors;r={'pass':all(checks.values()),'checks':checks,'records':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'method':'fresh whole game pages, full simulateFixedTick, natural radar observations (no injected combat tracks), native lock and VLS authority; target pilot AI retained, chaff deliberately unavailable for a normal-target regression; ON runs use actual WebGL'};(a.out/'observed-world.json').write_text(json.dumps(r,indent=2));print(json.dumps({'pass':r['pass'],'checks':checks,'errors':errors}));raise SystemExit(0 if r['pass']else 1)
