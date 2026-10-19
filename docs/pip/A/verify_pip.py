"""Native chart/input tests. CPU geometry fixture enables the view flag only;
real WebGL rendering and frame-time comparisons run separately in verify_visual.py.
"""
import argparse,base64,hashlib,importlib.util,json,math,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
sys.path.insert(0,str(R/'docs/map/A'));from verify_map import STATE
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--part',choices=['input','invariance'],default='input');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v)
def snap(p):return p.evaluate('__PIP_A__.snapshot()')
def close(p):
 p.keyboard.press('Escape');p.evaluate("()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))if(k!=='CIC')__UI_A__.close(k)}");p.wait_for_timeout(200)
def coords(p,o):return p.evaluate('o=>__PIP_A__.worldToScreen(o.x,o.y)',o)
def pick(p,o,right=False):
 close(p);q=coords(p,o);p.mouse.click(q['x'],q['y'],button='right'if right else'left');p.wait_for_timeout(50)
 if p.evaluate('__MAP_A__.snapshot().candidatesOpen'):p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click()
 return q
def objects(p):return p.evaluate('__MAP_A__.objects()')
def sea(p):
 r=snap(p)['rect'];points=[{'x':r['x']+r['w']*x,'y':r['y']+r['h']*y}for x,y in[(.2,.2),(.8,.2),(.2,.8),(.8,.8),(.5,.1)]]
 return next(q for q in points if not p.evaluate('q=>__MAP_A__.hitTest(q.x,q.y,"PIP")',q))
def screenshot(p,name):
 c=p.context.new_cdp_session(p)
 try:(a.out/name).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']))
 finally:c.detach()
with sync_playwright()as pw:
 b=launch(pw);native=b.new_page
 def page(**kw):
  kw.update(device_scale_factor=2.8125,has_touch=True);p=native(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('geometry fixture'))");return p
 b.new_page=page
 if a.part=='input':
  for width,height in [(1400,900),(832,384),(384,832)]:
   tag=str(width);print('PIP input',width,height,flush=True);p=load_fleet(b,raw,width=width,height=height,errors=errors);p.evaluate("()=>{__NAVAL_SIM_DIAG__.setTerrainDiagBypass(true);__HARPOON_DIAG_A__.forgetCombatTracksDiagnostic();document.getElementById('clearRouteBtn').click();for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k);__WIP148_3D_VIEW__.active=true;__UI_A__.open('CIC');}");p.wait_for_timeout(450);before=p.evaluate(STATE);v=snap(p);ck(tag+'.C.visible',v['visible']);mainKm=p.evaluate('__VIEWPORT_A__.snapshot().twoD.tacticalViewKm');r=v['rect'];anchor={'x':r['cx']+15,'y':r['cy']-12};world=p.evaluate('q=>__PIP_A__.screenToWorld(q.x,q.y)',anchor);p.mouse.move(anchor['x'],anchor['y']);p.mouse.wheel(0,-100);p.wait_for_timeout(80);after=snap(p);back=coords(p,world);ck(tag+'.C.wheelOwnDistance',after['km']==15 and p.evaluate('__VIEWPORT_A__.snapshot().twoD.tacticalViewKm')==mainKm);ck(tag+'.C.wheelAnchorError',math.hypot(back['x']-anchor['x'],back['y']-anchor['y'])<=1)
   def pinch(start,end):
    r=snap(p)['rect'];x=r['cx'];y=r['cy'];el=p.locator('#external3DMiniCicCanvas')
    for typ,i,xx in [('pointerdown',101,x-start/2),('pointerdown',102,x+start/2),('pointermove',101,x-end/2),('pointermove',102,x+end/2),('pointerup',102,x+end/2),('pointerup',101,x-end/2)]:el.dispatch_event(typ,{'pointerId':i,'pointerType':'touch','isPrimary':i==101,'button':0,'clientX':xx,'clientY':y})
   prev=snap(p)['km'];pinch(30,60);ck(tag+'.C.pinchIn',abs(snap(p)['km']-prev/2)<1e-8 and p.evaluate('__VIEWPORT_A__.snapshot().twoD.tacticalViewKm')==mainKm);pinch(60,30);ck(tag+'.C.pinchOut',abs(snap(p)['km']-prev)<1e-8 and p.evaluate('__VIEWPORT_A__.snapshot().twoD.tacticalViewKm')==mainKm)
   pt=sea(p);s=p.evaluate(STATE);p.mouse.click(pt['x'],pt['y']);p.mouse.move(pt['x'],pt['y']);p.mouse.down();p.wait_for_timeout(590);p.mouse.up();ck(tag+'.C.postPinchTapAndLong0',not p.evaluate('__MAP_A__.snapshot().menuOpen')and p.evaluate(STATE)==s);p.wait_for_timeout(320)
   # A real main-vs-PiP common-frame paint. No separate track layer in the inset.
   tid=p.evaluate("__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:2,bearingDeg:0,speedMps:0})");p.wait_for_timeout(100);p.evaluate('__VIEWPORT_A__.draw();__PIP_A__.renderView(__PIP_A__.view())');ids=snap(p)['stats']['lastIds'];ck(tag+'.A.sameTrackIds',ids['MAIN']==ids['PIP']and tid in ids['PIP'])
   # Center the known report, not a truth entity. 19/21 CSS px regardless of DPR.
   tr=next(o for o in objects(p)if o['key']=='TRACK:'+str(tid));p.evaluate('o=>{__PIP_A__.setDistance(5);__PIP_A__.setCenter({x:o.x,y:o.y})}',tr);close(p);q=coords(p,tr);p.mouse.click(q['x']+19,q['y']);ck(tag+'.C.19px',p.evaluate('__MAP_A__.snapshot().lookupTarget')==tr['key']);close(p);p.mouse.click(q['x']+21,q['y']);ck(tag+'.C.21px',p.evaluate('__MAP_A__.snapshot().lookupTarget')is None)
   p.mouse.move(q['x'],q['y']);p.mouse.down();p.mouse.move(q['x']+15,q['y'],steps=3);p.mouse.up();ck(tag+'.B.dragNoSelection',p.evaluate('__MAP_A__.snapshot().lookupTarget')is None);ck(tag+'.B.noCommand',before==p.evaluate(STATE));ck(tag+'.B.dragUnfollows',not snap(p)['follow'])
   p.locator('#pipCenterA').click();ck(tag+'.B.centerFollows',snap(p)['follow']);p.evaluate('__PIP_A__.setDistance(40)');own=next(o for o in objects(p)if o['kind']=='OWN');pick(p,own);p.locator('#mapControlA').click();close(p);pt=sea(p);n=len(p.evaluate(STATE)['ships']);p.mouse.click(pt['x'],pt['y']);ck(tag+'.D.oneNAV',len(p.evaluate(STATE)['ships'])==n+1);pick(p,tr);ck(tag+'.D.objectAdds0',len(p.evaluate(STATE)['ships'])==n+1);p.locator('#mapUndoA').click();ck(tag+'.D.undo',len(p.evaluate(STATE)['ships'])==n)
   close(p);p.evaluate("document.getElementById('modeAimBtn').click();document.getElementById('harpoonRouteE').click()");pt=sea(p);p.mouse.click(pt['x'],pt['y']);n=len(p.evaluate(STATE)['harpoon']['pointsM']);ck(tag+'.F.routeOne',n==1);pick(p,tr);ck(tag+'.F.objectPreserves',len(p.evaluate(STATE)['harpoon']['pointsM'])==n);pick(p,own);ck(tag+'.F.controlReason',p.locator('#mapControlA').is_disabled()and'하푼 계획 작성 중'in p.locator('#uiWindowA-INFO').inner_text());p.locator('#mapUndoA').click();ck(tag+'.F.undo',len(p.evaluate(STATE)['harpoon']['pointsM'])==0);p.evaluate("document.getElementById('harpoonRouteE').click()");close(p)
   pt=sea(p);s=p.evaluate(STATE);orbit=p.evaluate('__WIP148_3D_VIEW__.orbit');p.mouse.click(pt['x'],pt['y'],button='right');ck(tag+'.J.right',p.evaluate('__MAP_A__.snapshot().menuOpen'));menu=p.locator('#mapContextMenuA').bounding_box();screen=p.evaluate('AEGIS_VIEWPORT.threeD');ck(tag+'.J.screenBounds',menu['x']>=screen['x']and menu['y']>=screen['y']and menu['x']+menu['width']<=screen['x']+screen['w']+.1 and menu['y']+menu['height']<=screen['y']+screen['h']+.1);p.keyboard.press('Escape');p.mouse.move(pt['x'],pt['y']);p.mouse.down();p.wait_for_timeout(590);ck(tag+'.J.long',p.evaluate('__MAP_A__.snapshot().menuOpen'));p.mouse.up();ck(tag+'.J.release0',p.evaluate(STATE)==s);p.keyboard.press('Escape');el=p.locator('#external3DMiniCicCanvas');el.dispatch_event('pointermove',{'pointerType':'pen','pointerId':50,'buttons':2,'button':-1,'clientX':pt['x'],'clientY':pt['y']});ck(tag+'.J.pen',p.evaluate('__MAP_A__.snapshot().menuOpen'));p.keyboard.press('Escape');ck(tag+'.C.cameraIsolation',p.evaluate('__WIP148_3D_VIEW__.orbit')==orbit)
   # Three ESM bearings no longer absorb the ownship's hit region.
   p.evaluate("__HARPOON_DIAG_A__.forgetCombatTracksDiagnostic();[0,120,240].forEach(bearingDeg=>__NAVAL_SIM_DIAG__.injectActiveSeekerEsmBearing({bearingDeg}))");p.locator('#pipCenterA').click();close(p);own=next(o for o in objects(p)if o['kind']=='OWN');q=coords(p,own);p.mouse.click(q['x'],q['y']);ck(tag+'.G.ownWithoutCandidates',p.evaluate('__MAP_A__.snapshot().lookupTarget')=='OWN'and not p.evaluate('__MAP_A__.snapshot().candidatesOpen'));screenshot(p,'esm-own-'+tag+'.png');close(p);esm=next(o for o in objects(p)if o['kind']=='ESM');q=coords(p,own);p.mouse.click(q['x']+math.cos(esm['bearingRad'])*42,q['y']+math.sin(esm['bearingRad'])*42);ck(tag+'.G.outerESM',p.evaluate('__MAP_A__.snapshot().lookupTarget')==esm['key'])
   records[tag]={'pip':snap(p),'mainKm':mainKm};ck(tag+'.core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));p.close()
 else:
  sp=importlib.util.spec_from_file_location('inv',R/'docs/viewport/A/verify_invariance.py');inv=importlib.util.module_from_spec(sp);sp.loader.exec_module(inv);rows=[]
  for enabled in [False,True]:
   p=load_fleet(b,raw,ally='DDG_119_LATE_FLIGHT_IIA',enemy='SOVREMENNY_956',width=832,height=384,errors=errors);p.evaluate(inv.SETUP);p.evaluate('on=>{__WIP148_3D_VIEW__.active=true;__UI_A__.open("CIC");__PIP_A__.setEnabled(on)}',enabled)
   for i in range(24):p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(300);__PIP_A__.prepare();__PIP_A__.paint()')
   state=p.evaluate(inv.STATE);data=json.dumps(state,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode();rows.append({'enabled':enabled,'ticks':7200,'hash':hashlib.sha256(data).hexdigest(),'bytes':len(data)});(a.out/('state-on.json'if enabled else'state-off.json')).write_bytes(data);p.close()
  ck('B.120sHash',rows[0]['hash']==rows[1]['hash']);records['hashes']=rows
 b.close()
ck('pageErrors',not errors);d={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/(a.part+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':d['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if d['pass']else 1)
