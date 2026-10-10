"""Actual desktop pointer and emulated mobile touch for selected-owner AI controls."""
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
    q=page.locator('#'+id);q.scroll_into_view_if_needed();q.tap()if touch else q.click();page.wait_for_timeout(250)
   def snap():return page.evaluate('window.__NAVAL_SIM_DIAG__.tacticalSnapshotH1()')
   oid=snap()['ships'][0]['entityId'];aid='SHIP_SCENARIO_ALLY_F'
   def ship(id):return next(q for q in snap()['ships']if q['entityId']==id)
   press('modeFleetBtn');press('tacticalToggleH1');checks['ownOptInNativeButton']=ship(oid)['settings']['enabled'];checks['manualDoesNotAct']=not ship(oid)['active'];page.locator('#fleetModeG').select_option('AUTO');checks['autoActivates']=ship(oid)['active'];press('fleetEmconG');checks['manualRadarHeld']=ship(oid)['settings']['manualRadar'];checks['resumeOffered']=page.locator('#tacticalResumeH1').is_enabled();press('tacticalResumeH1');checks['resumeNativeClearsRadarHold']=not ship(oid)['settings']['manualRadar'];
   press('fleetChangeG');press('tacticalToggleH1');checks['allyToggleIndependent']=not ship(aid)['settings']['enabled']and ship(oid)['settings']['enabled'];press('tacticalToggleH1');checks['allyNativeEnable']=ship(aid)['settings']['enabled'];checks['unneededResumeDisabled']=not page.locator('#tacticalResumeH1').is_enabled();checks['statusAccessible']=page.locator('#tacticalStatusH1').get_attribute('role')=='status';checks['hasExplanation']=page.locator('#tacticalStatusH1').inner_text()!='';
   page.screenshot(path=str(a.out/('mobile.png'if touch else'desktop.png')));press('fleetChangeG');checks['switchKeepsOwnAI']=ship(oid)['settings']['enabled'];checks['fourTabsRemain']=page.locator('.control-deck-tab').count()==4;checks['coreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__.length')==0;checks['noFault']=page.evaluate('!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault()');rows.append({'touch':touch,'viewport':[width,height],'checks':checks,'snapshot':snap()});page.close();print(json.dumps({'touch':touch,'failed':[k for k,v in checks.items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(all(q['checks'].values())for q in rows)};(a.out/'ui.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
