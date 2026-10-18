"""J: explicitly repeat docking, containment and overlay isolation in 3D at 85/130%."""
from pathlib import Path
import sys,argparse,json,hashlib,random,math
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
from verify_ui import PROJECTION
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);checks={};rows=[];errors=[]
STATE="()=>({map:{pan:__VIEWPORT_A__.snapshot().twoD.pan,km:__VIEWPORT_A__.snapshot().twoD.tacticalViewKm},lock:__EMCON_DESIGNATION_F2__.snapshot().selectedLockId,route:__HARPOON_DIAG_A__.routeDraft(),orbit:__WIP148_3D_VIEW__.orbit})"
with sync_playwright()as pw:
 print('load',flush=True);b=launch(pw,True);p=load_fleet(b,a.html.read_bytes(),width=1400,height=900,errors=errors);p.evaluate('async()=>{if(document.fullscreenElement)await document.exitFullscreen();const v=__WIP148_3D_VIEW__;v.c12ApplyPreset("LOW");await v.open();}');p.wait_for_function('__UI_A__.snapshot().windows.CIC.open',polling=50);p.wait_for_timeout(500);c=p.context.new_cdp_session(p)
 print('renderer ready',flush=True)
 for scale in [85,130]:
  print('scale',scale,flush=True)
  p.evaluate('n=>{__UI_A__.setScale(n);__WIP148_3D_VIEW__.active=false;}',scale);rng=random.Random(scale)
  for i in range(30):p.set_viewport_size({'width':rng.randrange(360,1900),'height':rng.randrange(350,1081)})
  p.set_viewport_size({'width':1400,'height':900});p.wait_for_function('Math.abs(AEGIS_VIEWPORT.raw.w-1400)<.1&&Math.abs(AEGIS_VIEWPORT.raw.h-900)<.1',polling=50);p.wait_for_timeout(500);p.evaluate('__UI_A__.preset("PC 가로")');p.wait_for_timeout(500)
  s=p.evaluate('__UI_A__.snapshot()');checks[f'J.{scale}.B.titles']=all(not q['open']or q['title']['x']>=0 and q['title']['y']>=0 and q['title']['x']+q['title']['w']<=1400.1 and q['title']['y']+q['title']['h']<=s['bar']['y']+.1 for q in s['windows'].values())
  print('burst settled',scale,flush=True)
  for edge in ['right','']:
   print('dock',edge,flush=True)
   p.evaluate('edge=>__UI_A__.dock("ARM",edge)',edge);p.wait_for_timeout(500);q=p.evaluate(PROJECTION);e=math.hypot(q['p']['x']-q['v']['cx'],q['p']['y']-q['v']['cy']);checks[f'J.{scale}.C.3D.{edge or "float"}']=e<=q['v']['shortSide']*.01;s=p.evaluate('__VIEWPORT_A__.snapshot()');checks[f'J.{scale}.C.2D.{edge or "float"}']=math.hypot(s['twoD']['ownship']['x']-s['viewport']['twoD']['cx'],s['twoD']['ownship']['y']-s['viewport']['twoD']['cy'])<=1;rows.append({'scale':scale,'edge':edge,'centerErrorPx':e})
  p.evaluate('__UI_A__.preset("PC 가로");__WIP148_3D_VIEW__.active=true');p.wait_for_timeout(500)
  print('isolation',scale,flush=True)
  for selector in ['#uiWindowA-NAV .ui-title-a','#uiStatusBarA','#wip14a14QuickEngage3D .ui-widget-handle-a']:
   r=p.locator(selector).bounding_box();x=r['x']+min(35,r['width']*.15);y=r['y']+r['height']/2;before=p.evaluate(STATE);p.mouse.move(x,y);p.mouse.down();p.mouse.move(x+15,y+9,steps=4);p.mouse.up();p.mouse.move(x,y);p.mouse.wheel(0,-80);p.locator(selector).evaluate("e=>{const t=[new Touch({identifier:1,target:e,clientX:20,clientY:30}),new Touch({identifier:2,target:e,clientX:100,clientY:30})];for(const type of ['touchstart','touchmove','touchend'])e.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:t,bubbles:true,cancelable:true}));e.dispatchEvent(new MouseEvent('click',{bubbles:true}));}");p.wait_for_timeout(100);checks[f'J.{scale}.D.3D.{selector}']=before==p.evaluate(STATE)
 checks['pageErrors']=not errors;b.close()
out={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest()};(a.out/'scaled-3d.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if out['pass']else 1)
