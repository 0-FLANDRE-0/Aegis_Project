"""Mouse/touch native FLEET settings, independent owners and mobile layout."""
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
   def snap():return page.evaluate('__NAVAL_SIM_DIAG__.teamSnapshotH4()')
   oid=snap()['ships'][0]['entityId'];aid='SHIP_SCENARIO_ALLY_F'
   def ship(id):return next(q for q in snap()['ships']if q['entityId']==id)
   press('modeFleetBtn');checks['defaultOff']=page.locator('#teamToggleH4').inner_text()=='함대 전술 OFF';press('teamToggleH4');checks['ownOptIn']=ship(oid)['settings']['enabled'];checks['accessiblePressed']=page.locator('#teamToggleH4').get_attribute('aria-pressed')=='true';checks['accessibleStatus']=page.locator('#teamStatusH4').get_attribute('role')=='status';checks['noImplicitAttackConsent']=page.evaluate('__NAVAL_SIM_DIAG__.attackSnapshotH3().ships.every(q=>!q.consents.length)');
   page.locator('#teamMissionH4').select_option('SURFACE_ACTION');page.locator('#teamFormationH4').select_option('PORT_SCREEN');page.locator('#teamSpacingH4').select_option('4000');page.wait_for_timeout(1100);checks['draftNotOverwritten']=page.locator('#teamFormationH4').input_value()=='PORT_SCREEN'and page.locator('#teamSpacingH4').input_value()=='4000';press('teamApplyH4');checks['missionApplied']=ship(oid)['settings']['mission']=='SURFACE_ACTION';checks['formationApplied']=ship(oid)['settings']['formation']=='PORT_SCREEN'and ship(oid)['settings']['spacingM']==4000;press('teamRoeH4');checks['explicitSelfDefenseRoe']=ship(oid)['settings']['surfaceRoe']=='SELF_DEFENSE';checks['roePressed']=page.locator('#teamRoeH4').get_attribute('aria-pressed')=='true';
   press('fleetChangeG');checks['allyIndependentDefaults']=not ship(aid)['settings']['enabled']and ship(aid)['settings']['formation']=='LINE_ASTERN';checks['ownerSelectionResetsDraft']=page.locator('#teamMissionH4').input_value()=='ESCORT'and page.locator('#teamSpacingH4').input_value()=='2000';press('teamToggleH4');page.locator('#teamFormationH4').select_option('STARBOARD_SCREEN');page.locator('#teamSpacingH4').select_option('1000');press('teamApplyH4');checks['allyOwnFormation']=ship(aid)['settings']['formation']=='STARBOARD_SCREEN'and ship(aid)['settings']['spacingM']==1000;checks['ownNotOverwritten']=ship(oid)['settings']['formation']=='PORT_SCREEN'and ship(oid)['settings']['spacingM']==4000;
   page.locator('#teamSpacingH4').select_option('4000');press('fleetChangeG');checks['switchBackUsesOwnSavedSettings']=page.locator('#teamFormationH4').input_value()=='PORT_SCREEN'and page.locator('#teamSpacingH4').input_value()=='4000';press('fleetChangeG');checks['allyUnappliedDraftDiscarded']=page.locator('#teamSpacingH4').input_value()=='1000';press('teamToggleH4');checks['offSelectedOnly']=not ship(aid)['settings']['enabled']and ship(oid)['settings']['enabled'];checks['manualControlsNotChanged']=page.evaluate('__NAVAL_SIM_DIAG__.maneuverSnapshotH2().ships[0].settings.enabled===false');
   page.wait_for_timeout(1500);page.locator('#teamStatusH4').scroll_into_view_if_needed();page.screenshot(path=str(a.out/('mobile.png'if touch else'desktop.png')));checks['fourTabsRemain']=page.locator('.control-deck-tab').count()==4;checks['noHorizontalOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');checks['noFault']=page.evaluate('__CORE_SELFTEST_FAILURES__.length===0&&!__WIP125_DIAG__.wip150RuntimeFault()&&!__WIP125_DIAG__.wip150PresentationFault()');rows.append({'touch':touch,'viewport':[width,height],'checks':checks,'snapshot':snap()});page.close();print(json.dumps({'touch':touch,'failed':[k for k,v in checks.items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(all(q['checks'].values())for q in rows)};(a.out/'ui-h4.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
