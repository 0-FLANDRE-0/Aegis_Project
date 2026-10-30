"""UI_A1: real mobile client coordinates, stacking/dragging and native authority controls.
Geometry fixture rejects fullscreen only; production fullscreen code is byte-identical.
"""
import argparse,base64,hashlib,json,math,random,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
sys.path.insert(0,str(R/'docs/ui/A'));from verify_ui import PROJECTION
SIZES=[(384,832),(832,384),(390,844),(844,390),(600,900),(1400,900)]
INPUT="()=>({pan:__VIEWPORT_A__.snapshot().twoD.pan,km:__VIEWPORT_A__.snapshot().twoD.tacticalViewKm,lock:__EMCON_DESIGNATION_F2__.snapshot().selectedLockId,route:__HARPOON_DIAG_A__.routeDraft(),orbit:__WIP148_3D_VIEW__.orbit})"
SNAP="()=>({s:__UI_A__.snapshot(),v:AEGIS_VIEWPORT.twoD,own:__VIEWPORT_A__.snapshot().twoD.ownship,ammo:[...document.querySelectorAll('.ui-ammo-a')].map(e=>({name:e.innerText,r:e.getBoundingClientRect().toJSON(),overflow:e.scrollWidth-e.clientWidth})),scroll:document.documentElement.scrollWidth,canvasZoom:getComputedStyle(document.getElementById('c')).zoom})"
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);checks={};rows=[];records={};errors=[];raw=a.html.read_bytes()
 def ck(k,v):checks[k]=bool(v)
 def snap(p):return p.evaluate('__UI_A__.snapshot()')
 def settle(p,w,h):
  p.set_viewport_size({'width':w,'height':h});p.wait_for_function('([w,h])=>Math.abs(AEGIS_VIEWPORT.raw.w-w)<.1&&Math.abs(AEGIS_VIEWPORT.raw.h-h)<.1',arg=[w,h],polling=50);p.wait_for_timeout(380)
 def drag(p,sel,dx,dy):
  r=p.locator(sel).bounding_box();x=r['x']+20;y=r['y']+r['height']/2;p.mouse.move(x,y);p.mouse.down();p.mouse.move(x+dx,y+dy,steps=6);p.mouse.up();p.wait_for_timeout(120)
 def isolate(p,selector,key):
  before=p.evaluate(INPUT);r=p.locator(selector).bounding_box();x=r['x']+7;y=r['y']+r['height']/2;p.mouse.move(x,y);p.mouse.down();p.mouse.move(x+7,y+5,steps=3);p.mouse.up();p.mouse.wheel(0,-90)
  p.locator(selector).evaluate("e=>{const t=[new Touch({identifier:1,target:e,clientX:20,clientY:30}),new Touch({identifier:2,target:e,clientX:90,clientY:30})];for(const type of ['touchstart','touchmove','touchend'])e.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:t,bubbles:true,cancelable:true}));}");p.wait_for_timeout(70);ck(key,before==p.evaluate(INPUT))
 def capture(p,name):
  # Read the rendered surface directly; avoid screenshot animation/font settling
  # timeouts when another software WebGL regression is running. No DOM/clock writes.
  p.evaluate("async()=>{__VIEWPORT_A__.draw();await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))}")
  session=p.context.new_cdp_session(p)
  try:(a.out/name).write_bytes(base64.b64decode(session.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']))
  finally:session.detach()
 with sync_playwright()as pw:
  b=launch(pw,True);native=b.new_page
  def page(**kw):
   kw['device_scale_factor']=2.8125;kw['has_touch']=True;p=native(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('geometry fixture'))");p.add_init_script("addEventListener('load',()=>{const timer=setInterval(()=>{if(window.__MAP_A__){window.__MAP_A__.setMode(false);clearInterval(timer)}},20)})");return p
  b.new_page=page
  for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   print('matrix',own,flush=True);p=load_fleet(b,raw,own=own,width=384,height=832,errors=errors);p.evaluate("document.getElementById('uiPauseA').click()");p.wait_for_timeout(350)
   for scale in [100,85,130]:
    p.evaluate('n=>__UI_A__.setScale(n)',scale)
    for w,h in SIZES:
     settle(p,w,h);q=p.evaluate(SNAP);s=q['s'];bar=s['bar'];prefix=f'{own}.{scale}.{w}x{h}';v=q['v'];err=math.hypot(q['own']['x']-v['cx'],q['own']['y']-v['cy'])
     ck(prefix+'.allInventory',all(r['r']['left']>=-.1 and r['r']['right']<=w+.1 and r['r']['top']>=bar['y']-.1 and r['r']['bottom']<=h+.1 and r['overflow']<=1 for r in q['ammo']))
     ck(prefix+'.barOnscreen',bar['h']>0 and abs(bar['y']+bar['h']-h)<1 and q['scroll']<=w)
     ck(prefix+'.canvasUnscaled',q['canvasZoom']=='1');ck(prefix+'.visibleCenter',err<=1)
     ck(prefix+'.titlesContained',all(not r['open']or r['title']['x']>=-.1 and r['title']['y']>=-.1 and r['title']['x']+r['title']['w']<=w+.1 and r['title']['y']+r['title']['h']<=bar['y']+.1 for r in s['windows'].values()))
     names=[r['name']for r in s['inventory']];ck(prefix+'.installed',('RGM-84'in names)==own.startswith('CG') and ('RAM'in names)==own.startswith('DDG'))
     ck(prefix+'.nodes',s['originalNodesConnected']and s['duplicateIds']==[])
     if s['compact']and scale==100:
      ck(prefix+'.thinBar',bar['h']<=64)
      fonts=p.evaluate("()=>({title:parseFloat(getComputedStyle(document.querySelector('#uiWindowA-NAV .ui-window-name-a')).fontSize),fire:document.getElementById('external3DFireBtn').getBoundingClientRect().height})");ck(prefix+'.smallTextSafeFire',fonts['title']==10 and fonts['fire']>=40);ck(prefix+'.widgetLabelsFit',p.locator('#wip14a14QuickEngage3D button').evaluate_all('es=>es.every(e=>e.scrollWidth<=e.clientWidth+1&&e.scrollHeight<=e.clientHeight+1)'))
     # Popup must fit at all scales and choose modes without changing authority merely on open.
     before=s['modeMenu']['mode'];p.locator('#uiModeChipA').click();menu=p.locator('#uiModeMenuA').bounding_box();chip=p.locator('#uiModeChipA').bounding_box();ck(prefix+'.popupGeometry',menu['y']+menu['height']<=chip['y']+.1 and menu['x']>=0 and menu['x']+menu['width']<=w+.1);ck(prefix+'.popupOnly',snap(p)['modeMenu']['mode']==before and p.locator('#uiModeMenuA button').count()==3);p.keyboard.press('Escape')
     rows.append({'ship':own,'scale':scale,'size':[w,h],'barHeightPx':bar['h'],'centerErrorPx':err,'compact':s['compact'],'inventory':s['inventory']})
     (a.out/'progress.json').write_text(json.dumps({'phase':'matrix','rows':rows,'failed':[k for k,v in checks.items()if not v]}))
   if own.startswith('DDG'):p.close();continue
   settle(p,384,832);p.evaluate('__UI_A__.setScale(100);__UI_A__.preset("세로")');p.wait_for_timeout(400);capture(p,'mobile-portrait.png')
   # EMCON is the actual native button; no unrelated window activation.
   before=snap(p);state=p.evaluate(INPUT);p.locator('#uiEmconChipA').click();after=snap(p);ck('emcon.directNative',before['modeMenu']['emcon']!=after['modeMenu']['emcon']);ck('emcon.noWindowChange',{k:(v['open'],v['collapsed'])for k,v in before['windows'].items()}=={k:(v['open'],v['collapsed'])for k,v in after['windows'].items()});ck('emcon.noInputLeak',state==p.evaluate(INPUT));p.locator('#uiEmconChipA').click();ck('emcon.reverse',snap(p)['modeMenu']['emcon']==before['modeMenu']['emcon'])
   for mode in ['SEMIAUTO','AUTO','MANUAL']:
    p.locator('#uiModeChipA').click();p.locator(f'[data-engagement-mode-a1="{mode}"]').click();s=snap(p);ck('mode.'+mode,s['modeMenu']['mode']==mode and not s['modeMenu']['open'] and s['windows']['ARM']['collapsed'])
   p.locator('#uiModeChipA').click();capture(p,'mobile-mode-popup.png');isolate(p,'#uiModeMenuA','mode.inputIsolation');p.keyboard.press('Escape');ck('mode.escape',not snap(p)['modeMenu']['open']);p.locator('#uiModeChipA').click();p.mouse.click(370,300);ck('mode.outside',not snap(p)['modeMenu']['open'])
   # Clicking the bottom info opens the same window and unfolds it.
   p.locator('#uiInventoryA').click();ck('window.inventoryUnfold',not snap(p)['windows']['ARM']['collapsed']);p.locator('#uiShipA').click();ck('window.shipInfo',snap(p)['windows']['INFO']['open']);p.evaluate('__UI_A__.open("NAV")');p.wait_for_timeout(200)
   # Put NAV underneath ARM with a real title drag. Tapping/dragging must not reflow.
   drag(p,'#uiWindowA-NAV .ui-title-a',10,40);p.locator('#uiInventoryA').click();s=snap(p);nr=s['windows']['NAV'];ar=s['windows']['ARM'];ck('window.overlap',max(nr['x'],ar['x'])<min(nr['x']+nr['w'],ar['x']+ar['w']) and max(nr['y'],ar['y'])<min(nr['y']+nr['h'],ar['y']+ar['h']))
   r=p.locator('#uiWindowA-NAV .ui-title-a').bounding_box();p.mouse.click(r['x']+15,r['y']+r['height']/2);n=snap(p)['windows']['NAV'];ck('window.tapRaises',n['order']>snap(p)['windows']['ARM']['order']);ck('window.focusNoReflow',all(abs(n[k]-nr[k])<.1 for k in ['x','y','w','h']))
   drag(p,'#uiWindowA-NAV .ui-title-a',12,36);n2=snap(p)['windows']['NAV'];ck('window.realTitleDrag',abs(n2['x']-n['x']-12)<1 and abs(n2['y']-n['y']-36)<1);ck('window.mobileNoAutoDock',n2['dock']=='')
   drag(p,'#uiWindowA-NAV .ui-title-a',-100,0);ck('window.edgeStillFloating',snap(p)['windows']['NAV']['dock']=='')
   # Resize from the actual bottom-right handle.
   r=p.locator('#uiWindowA-NAV .ui-resize-a').bounding_box();n=snap(p)['windows']['NAV'];p.mouse.move(r['x']+r['width']-3,r['y']+r['height']-3);p.mouse.down();p.mouse.move(r['x']+r['width']+17,r['y']+r['height']+17,steps=5);p.mouse.up();n2=snap(p)['windows']['NAV'];ck('window.resize',abs(n2['w']-n['w']-20)<1 and abs(n2['h']-n['h']-20)<1)
   capture(p,'mobile-overlapping-windows.png')
   for selector in ['#uiWindowA-NAV .ui-title-a','#uiStatusBarA','#wip14a14QuickEngage3D .ui-widget-handle-a']:isolate(p,selector,'input.'+selector)
   # Stack and restored normal geometry stay above other windows after maximize/restore.
   p.locator('#uiWindowA-NAV button[title="최대화 / 복원"]').click();p.locator('#uiWindowA-NAV button[title="최대화 / 복원"]').click();ck('window.restoreInFront',snap(p)['windows']['NAV']['order']>snap(p)['windows']['ARM']['order'])
   p.wait_for_timeout(450);saved=p.evaluate('JSON.parse(localStorage.getItem("aegis.ui.a.layout.2"))');before=snap(p);p.reload();p.wait_for_selector('#aegisShipConfirmBtn');p.locator('#aegisShipConfirmBtn').click();p.wait_for_function('window.__UI_A__&&C55Packaging?.ready');p.wait_for_timeout(400);after=snap(p)
   ck('storage.schema2',saved['schema']==2);ck('storage.restores',all(all(abs(before['windows'][id][k]-after['windows'][id][k])<.1 for k in ['x','y','w','h','order']) for id in ['NAV','ARM']));records['savedLayout']=saved
   p.evaluate("()=>{document.getElementById('wip125DepartBtn').click();document.getElementById('uiPauseA').click()}");rng=random.Random(317)
   for i in range(30):p.set_viewport_size({'width':rng.randrange(350,1000),'height':rng.randrange(350,950)})
   settle(p,832,384);s=snap(p);ck('resize.30ContainsTitles',all(not r['open']or r['title']['x']>=-.1 and r['title']['y']>=-.1 and r['title']['x']+r['title']['w']<=832.1 and r['title']['y']+r['title']['h']<=s['bar']['y']+.1 for r in s['windows'].values()));p.evaluate('__UI_A__.preset("폰 가로")');p.wait_for_timeout(350);capture(p,'mobile-landscape.png')
   # The unchanged renderer uses the smaller bar and existing viewport transform.
   print('3D',flush=True);p.evaluate('async()=>{const v=__WIP148_3D_VIEW__;v.c12ApplyPreset("LOW");await v.open();}');p.wait_for_function('__UI_A__.snapshot().windows.CIC.open');p.wait_for_timeout(400)
   r=p.evaluate(PROJECTION);err=math.hypot(r['p']['x']-r['v']['cx'],r['p']['y']-r['v']['cy']);ck('3D.center',err<=r['v']['shortSide']*.01);records['3D']={'centerErrorPx':err,'viewport':r['v']}
   p.locator('#uiModeChipA').click();p.locator('[data-engagement-mode-a1="SEMIAUTO"]').click();ck('3D.nativeMode',snap(p)['modeMenu']['mode']=='SEMIAUTO');before=snap(p)['modeMenu']['emcon'];p.locator('#uiEmconChipA').click();ck('3D.nativeEmcon',snap(p)['modeMenu']['emcon']!=before)
   isolate(p,'#uiWindowA-NAV .ui-title-a','3D.windowInputIsolation');isolate(p,'#wip14a14QuickEngage3D .ui-widget-handle-a','3D.widgetInputIsolation');p.locator('#uiModeChipA').click();capture(p,'mobile-3d.png');p.keyboard.press('Escape');p.evaluate('__WIP148_3D_VIEW__.close()')
   settle(p,1400,900);p.evaluate('__UI_A__.setScale(100);__UI_A__.preset("PC 가로")');p.wait_for_timeout(400);capture(p,'desktop.png');ck('desktop.rightDockPreserved',snap(p)['windows']['ARM']['dock']=='right');ck('core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));p.close()
  for failure in ['blocked','corrupt','oldSchema']:
   p=b.new_page(viewport={'width':384,'height':832});p.on('pageerror',lambda e:errors.append(str(e)))
   script="Object.defineProperty(window,'localStorage',{get(){throw Error('blocked')}})"if failure=='blocked'else "localStorage.setItem('aegis.ui.a.layout.2','{broken');"if failure=='corrupt'else "localStorage.setItem('aegis.ui.a.layout.2',JSON.stringify({schema:1,layouts:{}}));localStorage.setItem('aegis.ui.a.preferences.1',JSON.stringify({schema:1,scale:115,landscape:true}));"
   p.add_init_script(script);p.route('https://aegis.test/**',lambda r:r.fulfill(body=raw,content_type='text/html'));p.goto('https://aegis.test/compact?view3d=0',timeout=90000);p.wait_for_selector('#aegisShipConfirmBtn');p.locator('#aegisShipConfirmBtn').click();p.wait_for_function('window.__UI_A__&&C55Packaging?.ready');s=snap(p);ck('storage.'+failure,s['compact']and s['preset']=='세로'and s['scale']==(1.15 if failure=='oldSchema'else 1)and s['originalNodesConnected']);p.close()
  b.close()
 ck('pageErrors',not errors);out={'pass':all(checks.values()),'htmlSha256':hashlib.sha256(raw).hexdigest(),'checks':checks,'rows':rows,'records':records,'errors':errors};(a.out/'compact.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
