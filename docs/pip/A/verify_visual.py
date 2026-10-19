"""Real WebGL screenshot/cycle and paired software-render frame-time measurement.
No phone hardware claim. Identical seed, CG, LOW camera and DPR in both builds.
"""
import argparse,base64,hashlib,json,math,statistics,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('base',type=Path);ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v)
def capture(p,n):
 s=p.context.new_cdp_session(p)
 try:(a.out/n).write_bytes(base64.b64decode(s.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']))
 finally:s.detach()
def close_windows(p):p.evaluate("()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))if(k!=='CIC')__UI_A__.close(k)}")
with sync_playwright()as pw:
 b=launch(pw,True);native=b.new_page
 def page(**kw):
  kw.update(device_scale_factor=2.8125,has_touch=True);p=native(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('geometry fixture'))");return p
 b.new_page=page
 for w,h in [(1400,900),(832,384)]:
  print('WebGL',w,h,flush=True);p=load_fleet(b,a.html.read_bytes(),width=w,height=h,errors=errors);p.locator('#uiShipA').click();p.locator('#mapControlA').click();p.evaluate("()=>{document.getElementById('modeAimBtn').click();__HARPOON_DIAG_A__.routeToggle();__HARPOON_DIAG_A__.routeAdd({x:3000,y:2000});}");close_windows(p)
  state=p.evaluate('()=>({ui:__MAP_A__.snapshot(),plan:__HARPOON_DIAG_A__.routeDraft(),nav:__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state.routePoints})');slots=lambda q:{k:q['ui'][k]for k in ['lookupTarget','controlPlatform','currentTool','firingDesignatedTarget']};p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready&&__PIP_A__.snapshot().stats.pip>0',timeout=180000,polling=50);p.wait_for_timeout(400);capture(p,f'3d-pip-{w}.png');q=p.evaluate('__PIP_A__.snapshot()');ck(f'D.{w}.ready',p.evaluate('__WIP148_3D_VIEW__.ready&&__WIP148_3D_VIEW__.active'));p.evaluate('__PIP_A__.resetMetrics()');p.wait_for_timeout(1200);ck(f'E.{w}.hiddenMain0',p.evaluate('__PIP_A__.snapshot().stats.hiddenMain===0'))
  for i in range(5):
   p.locator('#pipSwapA').click();p.wait_for_function('!__WIP148_3D_VIEW__.active');p.evaluate('__WIP148_3D_VIEW__.open()');p.wait_for_function('__PIP_A__.snapshot().visible');p.wait_for_timeout(100)
  after=p.evaluate('()=>({ui:__MAP_A__.snapshot(),plan:__HARPOON_DIAG_A__.routeDraft(),nav:__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state.routePoints})');ck(f'D.{w}.fiveCycles',slots(after)==slots(state)and after['plan']==state['plan']and after['nav']==state['nav']);records[str(w)]={'pip':q,'window':p.locator('#uiWindowA-CIC').bounding_box()}
  p.evaluate('__PIP_A__.setDistance(.5)');p.wait_for_timeout(150);capture(p,f'zoom-500m-{w}.png');ck(f'F.{w}.meters','500 m'in p.locator('#external3DMiniCicScale').inner_text());p.evaluate('__PIP_A__.setDistance(.1)');p.wait_for_timeout(150);capture(p,f'zoom-100m-{w}.png');ck(f'core.{w}',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));p.close()
 # Serial sessions with all other GPU test jobs stopped before this script is invoked.
 perf=[]
 for label,path in [('MAP_A',a.base),('PIP_A',a.html),('PIP_A',a.html),('MAP_A',a.base)]:
  print('frame benchmark',label,len(perf)+1,flush=True);p=load_fleet(b,path.read_bytes(),width=832,height=384,errors=errors);close_windows(p);p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000,polling=50);p.wait_for_timeout(2000)
  times=p.evaluate('''async()=>{const t=[];let last=await new Promise(r=>requestAnimationFrame(r));for(let i=0;i<90;i++){const now=await new Promise(r=>requestAnimationFrame(r));t.push(now-last);last=now;}return t;}''');s=sorted(times);perf.append({'build':label,'samples':len(times),'meanMs':statistics.mean(times),'p95Ms':s[math.ceil(len(s)*.95)-1],'timesMs':times,'renderer':p.evaluate('()=>{const r=__WIP148_3D_VIEW__.renderer;const gl=r.getContext(),ext=gl.getExtension("WEBGL_debug_renderer_info");return {vendor:ext?gl.getParameter(ext.UNMASKED_VENDOR_WEBGL):"unknown",renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):"unknown",dpr:devicePixelRatio,canvas:{width:r.domElement.width,height:r.domElement.height}}}')});(a.out/'performance-progress.json').write_text(json.dumps(perf,indent=2)+'\n');p.close()
 records['performance']=perf;ck('I.samples',all(q['samples']==90 for q in perf));b.close()
ck('pageErrors',not errors);d={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.base.read_bytes()).hexdigest(),'backend':'Headless Chromium SwiftShader software WebGL; not physical phone FPS'};(a.out/'visual.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':d['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if d['pass']else 1)
