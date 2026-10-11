"""Real desktop mouse/mobile touch: owner-local maneuver controls and NAV route."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'G'))
from browser_g import launch,load_fleet
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for width,height,touch in [(1100,820,False),(430,900,True)]:
   page=load_fleet(b,a.html.read_bytes(),width=width,height=height,touch=touch,errors=errors);checks={}
   def press(id):
    q=page.locator('#'+id);q.scroll_into_view_if_needed();q.tap()if touch else q.click();page.wait_for_timeout(150)
   def snap():return page.evaluate('window.__NAVAL_SIM_DIAG__.maneuverSnapshotH2()')
   oid=snap()['ships'][0]['entityId'];aid='SHIP_SCENARIO_ALLY_F'
   def ship(id):return next(q for q in snap()['ships']if q['entityId']==id)
   press('modeFleetBtn');press('maneuverToggleH2');checks['ownOptInButton']=ship(oid)['settings']['enabled'];checks['manualModeWaits']=not ship(oid)['active'];page.locator('#fleetModeG').select_option('AUTO');checks['masterStillRequired']=not ship(oid)['active'];press('tacticalToggleH1');checks['autoAndMasterActivate']=ship(oid)['active'];
   page.locator('#fleetSpeedG').fill('22');page.locator('#fleetRudderG').fill('10');press('fleetNavG');checks['ownNavManualHold']=ship(oid)['settings']['manualNav']and not ship(oid)['active'];checks['resumeAvailable']=page.locator('#maneuverResumeH2').is_enabled();press('maneuverToggleH2');press('maneuverToggleH2');checks['toggleKeepsManualPriority']=ship(oid)['settings']['manualNav'];press('maneuverResumeH2');checks['explicitResumeClearsNav']=ship(oid)['active']and not ship(oid)['settings']['manualNav'];
   press('fleetChangeG');page.locator('#fleetSpeedG').fill('14');page.locator('#fleetRudderG').fill('-5');press('fleetNavG');checks['allyNativeNavHold']=ship(aid)['settings']['manualNav']and not ship(oid)['settings']['manualNav'];press('maneuverResumeH2');checks['allyResumeIndependent']=not ship(aid)['settings']['manualNav'];checks['statusAccessible']=page.locator('#maneuverStatusH2').get_attribute('role')=='status';checks['statusHasText']=bool(page.locator('#maneuverStatusH2').inner_text());
   page.wait_for_timeout(3400);page.screenshot(path=str(a.out/('mobile.png'if touch else'desktop.png')));press('fleetChangeG');press('modeNavBtn');press('rudL');checks['nativeRudderButtonYieldsOwn']=ship(oid)['settings']['manualNav'];press('modeFleetBtn');press('maneuverResumeH2');press('modeNavBtn');press('spdU');checks['nativeTelegraphButtonYieldsOwn']=ship(oid)['settings']['manualNav'];press('modeFleetBtn');press('maneuverResumeH2');press('modeNavBtn');
   canvas=page.locator('canvas').first;box=canvas.bounding_box();x,y=box['x']+box['width']*.8,box['y']+box['height']*.2
   page.touchscreen.tap(x,y)if touch else page.mouse.click(x,y);checks['actualMapWaypointYields']=ship(oid)['settings']['manualNav'];checks['actualWaypointAdded']=page.evaluate('window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A().ship.navigation.manualRudderV15')is False
   press('modeFleetBtn');press('maneuverResumeH2');press('modeNavBtn');press('undoWpBtn');checks['nativeUndoYields']=ship(oid)['settings']['manualNav'];press('modeFleetBtn');press('maneuverResumeH2');press('modeNavBtn');press('clearRouteBtn');checks['nativeClearYields']=ship(oid)['settings']['manualNav'];checks['fourTabsRemain']=page.locator('.control-deck-tab').count()==4;checks['noFault']=page.evaluate('window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault()');rows.append({'touch':touch,'viewport':[width,height],'checks':checks,'snapshot':snap()});page.close();print(json.dumps({'touch':touch,'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(all(q['checks'].values())for q in rows)};(a.out/'ui-h2.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
