"""Actual mouse/touch consent controls, owner switching and accessible status."""
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
   page=load_fleet(b,a.html.read_bytes(),ally='CG_52_LATE_TICONDEROGA',width=width,height=height,touch=touch,errors=errors);checks={}
   def press(id):
    q=page.locator('#'+id);q.scroll_into_view_if_needed();q.tap()if touch else q.click();page.wait_for_timeout(150)
   def snap():return page.evaluate('__NAVAL_SIM_DIAG__.attackSnapshotH3()')
   oid=snap()['ships'][0]['entityId'];aid='SHIP_SCENARIO_ALLY_F'
   def ship(id):return next(q for q in snap()['ships']if q['entityId']==id)
   press('modeFleetBtn');checks['defaultOffText']=page.locator('#attackToggleH3').inner_text()=='공격 AI OFF';checks['unknownCannotConsent']=page.locator('#attackAuthorizeH3').is_disabled();press('attackToggleH3');checks['ownOptIn']=ship(oid)['settings']['enabled'];checks['onAloneNoAuthority']=ship(oid)['consents']==[]and not ship(oid)['active'];checks['accessiblePressed']=page.locator('#attackToggleH3').get_attribute('aria-pressed')=='true';checks['accessibleStatus']=page.locator('#attackStatusH3').get_attribute('role')=='status';
   page.evaluate('''()=>{const d=__NAVAL_SIM_DIAG__,w=__AEGIS_ENGAGEMENT_RUNTIME__,id=w.activePlayerShipId,n=w.ships.get(id).navigation;d.weaponFixtureD('SHIP_SCENARIO_ALLY_F',{action:'track',trackId:91,positionM:{x:n.positionWorld.x/.0038+10000,y:n.positionWorld.y/.0038,z:8},domain:'SURFACE'});const t=structuredClone(w.ships.get('SHIP_SCENARIO_ALLY_F').combatSystem.trackManager.tracks.get(91));w.ships.get('SHIP_SCENARIO_ALLY_F').combatSystem.trackManager.tracks.delete(91);Object.assign(t,{networkLocalAtS_G:d.observerSnapshotC().worldTimeS});w.ships.get(id).combatSystem.trackManager.tracks.set(91,t);d.fleetCommandG(id,{action:'TRACK',trackId:91});}''')
   page.locator('#fleetIdentityG').select_option('HOSTILE');press('fleetIdentifyG');checks['hostileEnablesConsent']=page.locator('#attackAuthorizeH3').is_enabled();page.locator('#attackRoundsH3').select_option('2');press('attackAuthorizeH3');checks['explicitTwoRoundGrant']=ship(oid)['consents'][0]['remaining']==2;checks['consentStatusVisible']='2발'in page.locator('#attackConsentH3').inner_text();checks['manualModeKeepsDefenseMode']=not ship(oid)['active'];
   press('fleetChangeG');checks['allyOwnSettingsIndependent']=not ship(aid)['settings']['enabled']and ship(oid)['settings']['enabled'];press('attackToggleH3');checks['allyOptIn']=ship(aid)['settings']['enabled'];checks['switchDoesNotCopyOwnConsent']=ship(aid)['consents']==[]and ship(oid)['consents'][0]['remaining']==2;checks['allyUnknownConsentDisabled']=page.locator('#attackAuthorizeH3').is_disabled();press('fleetChangeG');press('attackRevokeH3');checks['revokeClearsSelectedConsent']=ship(oid)['consents']==[]and ship(aid)['settings']['enabled'];checks['revokeButtonDisabledAfter']=page.locator('#attackRevokeH3').is_disabled();press('attackAuthorizeH3');press('attackToggleH3');checks['offRevokesConsent']=not ship(oid)['settings']['enabled']and ship(oid)['consents']==[];press('attackToggleH3');checks['onNeverRecreatesConsent']=ship(oid)['consents']==[];
   page.wait_for_timeout(3400);page.screenshot(path=str(a.out/('mobile.png'if touch else'desktop.png')));checks['fourTabsRemain']=page.locator('.control-deck-tab').count()==4;checks['noHorizontalOverflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');checks['noFault']=page.evaluate('__CORE_SELFTEST_FAILURES__.length===0&&!__WIP125_DIAG__.wip150RuntimeFault()&&!__WIP125_DIAG__.wip150PresentationFault()');rows.append({'touch':touch,'viewport':[width,height],'checks':checks,'snapshot':snap()});page.close();print(json.dumps({'touch':touch,'failed':[k for k,v in checks.items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(all(q['checks'].values())for q in rows)};(a.out/'ui-h3.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
