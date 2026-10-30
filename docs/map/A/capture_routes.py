"""Supplemental ownship/route context-menu screenshots (not extra test counts)."""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];records=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,raw,width=1400,height=900,errors=errors)
 def close():
  p.keyboard.press('Escape');p.evaluate("()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k)}");p.wait_for_timeout(220)
 def choose(o,right=False):
  close();q=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o);p.mouse.click(q['x'],q['y'],button='right'if right else'left')
  if p.evaluate('__MAP_A__.snapshot().candidatesOpen'):p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click()
 def capture(name):
  assert p.locator('#mapContextMenuA').is_visible();session=p.context.new_cdp_session(p)
  try:(a.out/name).write_bytes(base64.b64decode(session.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']))
  finally:session.detach()
  records.append({'file':name,'menuText':p.locator('#mapContextMenuA').inner_text()})
 p.evaluate("()=>{document.getElementById('clearRouteBtn').click();__VIEWPORT_A__.setDistance(40)}");own=next(o for o in p.evaluate('__MAP_A__.objects()')if o['kind']=='OWN');choose(own,True);capture('menu-ownship.png');choose(own);p.locator('#mapControlA').click()
 for dx,dy in [(-200,150),(-300,220)]:
  close();v=p.evaluate('AEGIS_VIEWPORT.twoD');p.mouse.click(v['cx']+dx,v['cy']+dy)
 wp=next(o for o in p.evaluate('__MAP_A__.objects()')if o['kind']=='WP');choose(wp,True);assert'마지막 점만 취소 가능'in p.locator('#mapContextMenuA').inner_text();capture('menu-waypoint.png')
 close();p.evaluate("document.getElementById('modeAimBtn').click();document.getElementById('harpoonRouteE').click()");assert p.evaluate('__MAP_A__.snapshot().currentTool')=='HARPOON_INS'
 for dx,dy in [(230,160),(310,230)]:
  close();v=p.evaluate('AEGIS_VIEWPORT.twoD');p.mouse.click(v['cx']+dx,v['cy']+dy)
 hwp=next(o for o in p.evaluate('__MAP_A__.objects()')if o['kind']=='HWP');choose(hwp,True);capture('menu-harpoon-waypoint.png');p.close();b.close()
assert not errors,errors
(a.out/'route-screenshots.json').write_text(json.dumps({'htmlSha256':hashlib.sha256(raw).hexdigest(),'presentationExamplesOnly':True,'records':records,'errors':errors},ensure_ascii=False,indent=2)+'\n');print('Ownship, WP and Harpoon-WP menus captured')
