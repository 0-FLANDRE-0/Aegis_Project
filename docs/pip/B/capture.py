"""Actual WebGL/PiP screenshots and dense DOM measurements; no mocked 3D scene."""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from browser_backend import install
install()
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];records={}
def shot(p,name):
 s=p.context.new_cdp_session(p)
 try:(a.out/name).write_bytes(base64.b64decode(s.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']))
 finally:s.detach()
def close(p):p.evaluate('()=>{for(const id of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(id)}')
with sync_playwright()as pw:
 b=launch(pw,True);native=b.new_page
 def page(**kw):
  kw['device_scale_factor']=2.8125;kw['has_touch']=True;p=native(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('screenshot fixture'))");return p
 b.new_page=page
 for w,h in [(1400,900),(832,384)]:
  print('capture',w,h,flush=True);p=load_fleet(b,a.html.read_bytes(),width=w,height=h,errors=errors);close(p)
  p.evaluate('__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:10,bearingDeg:0,altM:1000,speedMps:120})');p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready&&__PIP_A__.snapshot().visible&&__PIP_A__.snapshot().stats.pip>0',timeout=180000,polling=100);p.wait_for_timeout(300);shot(p,f'pip-webgl-{w}.png');records[str(w)]={'pip':p.evaluate('__PIP_A__.snapshot()'),'renderer':p.evaluate('()=>{const gl=__WIP148_3D_VIEW__.renderer.getContext(),e=gl.getExtension("WEBGL_debug_renderer_info");return {name:e?gl.getParameter(e.UNMASKED_RENDERER_WEBGL):"unknown",active:__WIP148_3D_VIEW__.active,ready:__WIP148_3D_VIEW__.ready}}')}
  p.evaluate('__PIP_A__.setDistance(.5)');p.wait_for_timeout(250);shot(p,f'pip-500m-{w}.png')
  if w==1400:
   p.evaluate('__WIP148_3D_VIEW__.close()');close(p);p.wait_for_timeout(250);o=p.evaluate('__MAP_A__.objects().find(o=>o.kind==="TRACK")');xy=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o);p.mouse.click(xy['x'],xy['y']);p.evaluate('document.getElementById("lockBtn").click();__AEGIS_WIP14A14_ENGAGEMENT_UI__.uiSnapshot()');p.evaluate('__PIP_A__.prepare();__VIEWPORT_A__.draw()');p.wait_for_function('document.getElementById("lockedTargetTextB").textContent.startsWith("T")',timeout=60000);p.wait_for_timeout(150);p.evaluate('__UI_A__.close("INFO")');shot(p,'locked-target.png');p.evaluate('__UI_A__.close("LOCKED");__UI_A__.open("INFO")');p.mouse.click(1050,240,button='right');p.wait_for_timeout(80);shot(p,'dense-info-menu.png')
   metrics=p.evaluate('''()=>{const r=e=>e.getBoundingClientRect().toJSON(),style=e=>{const s=getComputedStyle(e),a=getComputedStyle(e,'::after');return {fontPx:parseFloat(s.fontSize),lineHeight:s.lineHeight,padding:s.padding,heightPx:e.getBoundingClientRect().height,widthPx:e.getBoundingClientRect().width,hitTop:a.top,hitBottom:a.bottom}},info=document.getElementById('uiWindowA-INFO'),menu=document.getElementById('mapContextMenuA');return {info:{...style(info.querySelector('.map-info-a')),window:r(info)},menu:style(menu),normalButton:style(menu.querySelector('button')),precision:style(document.getElementById('mapPrecisionA')),title:style(info.querySelector('.ui-title-a')),titleButton:style(info.querySelector('.ui-title-a button'))}}''');records['density100']=metrics;p.keyboard.press('Escape');p.evaluate('__UI_A__.close("INFO");__AEGIS_WIP14A14_ENGAGEMENT_UI__.clearLock();__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:10,bearingDeg:0,altM:1000,speedMps:120})');p.mouse.click(xy['x'],xy['y']);p.wait_for_timeout(80);shot(p,'dense-candidates.png');records['candidateWidthPx']=p.locator('#mapCandidatesA').bounding_box()['width']
  p.close()
 b.close()
out={'pass':not errors,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'backend':'Actual SwiftShader WebGL; test-only CPU Canvas2D'};(a.out/'screenshots.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({'pass':out['pass'],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
