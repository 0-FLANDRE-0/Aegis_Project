"""UI_A native browser A-D/G-J, with CSS-client geometry and real input."""
import argparse,json,sys,math,random,time
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
SIZES=[(1920,1080),(1400,900),(1400,560),(900,900),(600,900),(390,844),(844,390),(384,832),(832,384)]
PROJECTION='''()=>{const v=__WIP148_3D_VIEW__;v.resize();const st=get3DRenderState();v.syncWorldEpochWip14A(st);v.syncRenderOriginWip14A(st);v.applyShipBodyFrame(st);v.scene.updateMatrixWorld(true);v.syncCamera();return {p:__VIEWPORT_A__.projectShipPoint(),v:AEGIS_VIEWPORT.threeD};}'''
INPUT='''()=>({view:__VIEWPORT_A__.snapshot().twoD,lock:__EMCON_DESIGNATION_F2__.snapshot().selectedLockId,cursor:__NAVAL_SIM_DIAG__.wip13cControlDeckStateSnapshot?.(),route:__HARPOON_DIAG_A__.routeDraft(),orbit:__WIP148_3D_VIEW__.orbit})'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};rows=[];errors=[];records={}
 def ck(k,v):checks[k]=bool(v)
 def settle(p,w,h):
  p.set_viewport_size({'width':w,'height':h});p.wait_for_function('([w,h])=>Math.abs(AEGIS_VIEWPORT.raw.w-w)<.1&&Math.abs(AEGIS_VIEWPORT.raw.h-h)<.1',arg=[w,h]);p.wait_for_timeout(350)
 with sync_playwright()as pw:
  b=launch(pw,True)
  native_new_page=b.new_page
  def geometry_page(**kw):
   p=native_new_page(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('geometry fixture: fullscreen tested separately'))");return p
  b.new_page=geometry_page
  for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   p=load_fleet(b,raw,own=own,width=1400,height=900,errors=errors);p.wait_for_timeout(400)
   for scale in [100,85,130]:
    p.evaluate('n=>__UI_A__.setScale(n)',scale)
    for w,h in SIZES:
     settle(p,w,h)
     if (w,h)in[(384,832),(832,384)]:p.context.new_cdp_session(p).send('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':2.8125,'mobile':False});p.wait_for_timeout(200)
     q=p.evaluate('''()=>{const s=__UI_A__.snapshot(),r=e=>e.getBoundingClientRect().toJSON(),ammo=[...document.querySelectorAll('.ui-ammo-a')].map(e=>({rect:r(e),text:e.innerText,overflow:e.scrollWidth-e.clientWidth}));return {s,v:AEGIS_VIEWPORT.snapshot(),map:__VIEWPORT_A__.snapshot().twoD,ammo,scroll:[document.documentElement.scrollWidth,innerWidth],mainZoom:[getComputedStyle(document.getElementById('c')).zoom,getComputedStyle(document.getElementById('external3DCanvas')).zoom]};}''')
     prefix=f'{own}.{scale}.{w}x{h}';bar=q['s']['bar'];ck(prefix+'.barVisible',bar['h']>0 and abs(bar['y']+bar['h']-h)<1);ck(prefix+'.inventoryAll',all(0<=r['rect']['left']and r['rect']['right']<=w+.1 and bar['y']<=r['rect']['top'] and r['rect']['bottom']<=h+.1 and r['overflow']<=1 for r in q['ammo']));ck(prefix+'.noHorizontalScroll',q['scroll'][0]<=w);ck(prefix+'.canvasNotScaled',q['mainZoom']==['1','1']);names=[r['name']for r in q['s']['inventory']];ck(prefix+'.installed',('RGM-84'in names)==own.startswith('CG') and ('RAM'in names)==own.startswith('DDG'))
     ck(prefix+'.titles',all(not r['open']or r['title']['x']>=-.1 and r['title']['y']>=-.1 and r['title']['x']+r['title']['w']<=w+.1 and r['title']['y']+r['title']['h']<=bar['y']+.1 for r in q['s']['windows'].values()))
     ownxy=q['map']['ownship'];v=q['v']['twoD'];ce=math.hypot(ownxy['x']-v['cx'],ownxy['y']-v['cy']);ck(prefix+'.center',ce<=1)
     # The actual map route editor must invert the visible client transform.
     p.evaluate("()=>{__UI_A__.close('NAV');__UI_A__.close('ARM');__UI_A__.close('CIC');__NAVAL_SIM_DIAG__.wip13cSetControlDeckTab('ARM');__UI_A__.close('ARM');}")
     v=p.evaluate('AEGIS_VIEWPORT.twoD');xy={'x':v['cx']-.13*v['shortSide'],'y':v['cy']+.1*v['shortSide']};p.evaluate('__HARPOON_DIAG_A__.routeToggle()');p.mouse.click(xy['x'],xy['y']);draft=p.evaluate('__HARPOON_DIAG_A__.routeDraft()');err=None
     if draft['pointsM']:
      point=draft['pointsM'][-1];project=p.evaluate('t=>__VIEWPORT_A__.worldToScreen(t.x*.0038,t.y*.0038)',point);err=math.hypot(project['x']-xy['x'],project['y']-xy['y'])
     if own.startswith('DDG'):
      p.evaluate("()=>{document.getElementById('modeNavBtn').click();__UI_A__.close('NAV');}");p.wait_for_timeout(80);p.mouse.click(xy['x'],xy['y']);point=p.evaluate('__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state.routePoints.at(-1)');project=p.evaluate('t=>__VIEWPORT_A__.worldToScreen(t.x,t.y)',point);err=math.hypot(project['x']-xy['x'],project['y']-xy['y'])
     ck(prefix+'.tap',err is not None and err<=2)
     if own.startswith('CG'):p.evaluate('__HARPOON_DIAG_A__.routeToggle()')
     rows.append({'profile':own,'scale':scale,'size':[w,h],'barHeightPx':bar['h'],'centerErrorPx':ce,'tapErrorPx':err,'inventory':q['s']['inventory']});p.evaluate("__UI_A__.preset(__UI_A__.snapshot().preset)")
     if (w,h)in[(384,832),(832,384)]:p.context.new_cdp_session(p).send('Emulation.clearDeviceMetricsOverride')
   if own.startswith('DDG'):p.close();continue
   # A real 30-change burst, then layout settlement and title containment.
   cd=p.context.new_cdp_session(p);rng=random.Random(317);start=time.monotonic()
   for i in range(30):cd.send('Emulation.setDeviceMetricsOverride',{'width':rng.randrange(360,1900),'height':rng.randrange(350,1081),'deviceScaleFactor':1,'mobile':False})
   p.wait_for_timeout(500);s=p.evaluate('__UI_A__.snapshot()');v=p.evaluate('AEGIS_VIEWPORT.layout');ck('B.30resize',all(not r['open']or 0<=r['title']['x'] and 0<=r['title']['y'] and r['title']['x']+r['title']['w']<=v['w']+.1 and r['title']['y']+r['title']['h']<=s['bar']['y']+.1 for r in s['windows'].values()));records['burstSeconds']=time.monotonic()-start;cd.send('Emulation.clearDeviceMetricsOverride');settle(p,1400,900);p.evaluate('__UI_A__.setScale(100)');p.wait_for_timeout(350)
   # Native 3D camera/projection, docking and undocking, no truth writes.
   p.evaluate('async()=>{const v=__WIP148_3D_VIEW__;await v.open();v.active=false;v.c12ApplyPreset("LOW");v.resetCamera();}')
   dockrows=[]
   for edge in ['right','','top','','left','']:
    p.evaluate('e=>__UI_A__.dock("ARM",e)',edge);p.wait_for_timeout(350);r=p.evaluate(PROJECTION);err=math.hypot(r['p']['x']-r['v']['cx'],r['p']['y']-r['v']['cy']);ck('C.3D.'+(edge or 'float')+'.center',err<=r['v']['shortSide']*.01);v2=p.evaluate('__VIEWPORT_A__.snapshot()');ck('C.2D.'+(edge or 'float')+'.center',math.hypot(v2['twoD']['ownship']['x']-v2['viewport']['twoD']['cx'],v2['twoD']['ownship']['y']-v2['viewport']['twoD']['cy'])<=1);dockrows.append({'edge':edge,'errorPx':err,'viewport':r['v']})
   records['dock']=dockrows;p.evaluate('__WIP148_3D_VIEW__.close()');p.evaluate('__UI_A__.preset("PC 가로")');p.wait_for_timeout(350)
   # Overlay event isolation. New controls retain normal button handling.
   for scale in [85,100,130]:
    p.evaluate('n=>__UI_A__.setScale(n)',scale);p.wait_for_timeout(350)
    for selector in ['#uiWindowA-NAV .ui-title-a','#uiStatusBarA','#wip14a14QuickEngage3D .ui-widget-handle-a']:
     box=p.locator(selector).bounding_box();x=box['x']+min(35,box['width']*.15);y=box['y']+box['height']/2;before=p.evaluate(INPUT);p.mouse.move(x,y);p.mouse.down();p.mouse.move(x+15,y+9,steps=4);p.mouse.up();p.mouse.move(x,y);p.mouse.wheel(0,-100);p.locator(selector).evaluate("e=>{const t=[new Touch({identifier:1,target:e,clientX:20,clientY:30}),new Touch({identifier:2,target:e,clientX:100,clientY:30})];e.dispatchEvent(new TouchEvent('touchstart',{touches:t,bubbles:true,cancelable:true}));e.dispatchEvent(new TouchEvent('touchmove',{touches:t,bubbles:true,cancelable:true}));e.dispatchEvent(new TouchEvent('touchend',{touches:[],bubbles:true,cancelable:true}));}");p.wait_for_timeout(50);after=p.evaluate(INPUT)
     for q in [before,after]:q['view']={k:q['view'][k]for k in ['tacticalViewKm','pan']}
     ck('D.'+str(scale)+selector,before==after)
   # Time buttons, same exact handler, then the new pause path.
   for n in [1,4,8,16,64]:
    r=p.evaluate("n=>{document.querySelectorAll('.time-btn').forEach(e=>{if(Number(e.dataset.tw)===n)e.click()});const r=__UI_A__.snapshot().time;document.getElementById('uiPauseA').click();return r;}",n);ck('G.scale'+str(n),r['scale']==n)
   start=p.evaluate('__UI_A__.snapshot().time.step');p.wait_for_timeout(300);ck('G.pausedClock',p.evaluate('__UI_A__.snapshot().time.step')==start);ck('E.originalNodes',p.evaluate('__UI_A__.snapshot().originalNodesConnected'));ck('E.duplicateIds',p.evaluate('__UI_A__.snapshot().duplicateIds.length===0'))
   # Persist and reload with a deterministic visible layout.
   p.evaluate('__UI_A__.setScale(100);__UI_A__.preset("PC 가로");__UI_A__.dock("NAV","left")');p.wait_for_timeout(650);saved=p.evaluate('({key:__UI_A__.snapshot().layoutKey,layout:JSON.parse(localStorage.getItem("aegis.ui.a.layout.1"))})');p.reload();p.wait_for_selector('#aegisShipConfirmBtn');p.locator('#aegisShipConfirmBtn').click();p.wait_for_function('window.__UI_A__&&window.C55Packaging?.ready');p.wait_for_timeout(500);restored=p.evaluate('__UI_A__.snapshot()');ck('H.reloadDock',restored['windows']['NAV']['dock']=='left');records['saved']=saved
   p.evaluate("()=>{document.getElementById('wip125DepartBtn').click();__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);}")
   for preset,size in [('PC 가로',(1400,900)),('폰 가로',(844,390)),('세로',(390,844))]:
    settle(p,*size);p.evaluate('name=>__UI_A__.preset(name)',preset);p.wait_for_timeout(400);p.screenshot(path=str(a.out/('preset-'+{'PC 가로':'pc','폰 가로':'phone','세로':'portrait'}[preset]+'.png')))
   ck('core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));p.close();b.close()
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'records':records,'errors':errors};(a.out/'ui.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
