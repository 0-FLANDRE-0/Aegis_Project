"""Real pointer/touch operator controls and camera; isolated diagnostic observations.

Fixtures create measured KF files only. They do not install production shortcuts.
"""
import argparse,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_g import launch,load_fleet
SETUP=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__,aid='SHIP_SCENARIO_ALLY_F',oid=w.activePlayerShipId;
 d.setTerrainDiagBypass(true);d.setEmcon(false);d.wip119SetMode('MANUAL');d.defenseCommandE(aid,{mode:'HOLD'});d.defenseCommandE('SHIP_SCENARIO_ENEMY_A',{mode:'HOLD'});
 const saved=d.exportOperationalStateV48Wip11A();for(const inv of [saved.ship.inventory,saved.fleet.ships.find(s=>s.entityId===aid).ship.inventory])for(const [i,type]of ['SM2','SM2ER','SM6','ESSM4'].entries())Object.assign(inv.vls.fwd[i],{type,essmCount:type==='ESSM4'?4:0});
 d.importOperationalStateV48Wip11A(saved);d.setTerrainDiagBypass(true);d.setEmcon(false);d.defenseCommandE(aid,{mode:'HOLD'});d.electronicCommandF(aid,{emcon:false});d.defenseCommandE('SHIP_SCENARIO_ENEMY_A',{mode:'HOLD'});
 window.__FLEET_FIXTURE_G__=(id,domain='AIR',distanceM=8000)=>{
  const r=w.ships.get(id),n=r.navigation,c=Math.cos(n.heading),s=Math.sin(n.heading),positionM={x:n.positionWorld.x/.0038+c*distanceM,y:n.positionWorld.y/.0038+s*distanceM,z:domain==='SURFACE'?8:600},velocityMps={x:domain==='SURFACE'?0:-200*c,y:domain==='SURFACE'?0:-200*s,z:0};
  d.weaponFixtureD(aid,{action:'track',trackId:77,positionM,velocityMps,domain});
  if(id===oid){const source=w.ships.get(aid).combatSystem.trackManager.tracks.get(77);w.ships.get(oid).combatSystem.trackManager.tracks.set(77,structuredClone(source));}
  d.fleetSelectG(id);d.fleetCommandG(id,{action:'TRACK',trackId:77});return d.fleetSnapshotG();
 };return {oid,aid};
}'''
PORTS=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__,oid=w.activePlayerShipId,aid='SHIP_SCENARIO_ALLY_F',checks={},trace=[],snap=()=>d.fleetSnapshotG(),ship=id=>snap().ships.find(r=>r.entityId===id),inv=id=>JSON.stringify(ship(id).inventory),tick=n=>d.runFramesToTicks(60,1,n);
 const own=w.ships.get(oid),ally=w.ships.get(aid),before=d.exportOperationalStateV48Wip11A();
 for(const id of [oid,aid]){
  const beforeNav=JSON.stringify([own.navigation,ally.navigation]);checks[id+'.invalidNavAtomic']=!d.fleetCommandG(id,{action:'NAV',speedKt:99,rudderDeg:0}).ok&&beforeNav===JSON.stringify([own.navigation,ally.navigation]);
  checks[id+'.invalidCommandFields']=!d.fleetCommandG(id,{action:'NAV',speedKt:10,rudderDeg:0,truthRef:1}).ok;
  window.__FLEET_FIXTURE_G__(id);const other=id===oid?aid:oid,otherInv=inv(other),startInv=inv(id);
  checks[id+'.unknownWithheld']=!d.fleetCommandG(id,{action:'FIRE',trackId:77,weapon:'SM2'}).ok&&inv(id)===startInv;
  d.fleetCommandG(id,{action:'IDENTITY',trackId:77,identity:'FRIEND'});checks[id+'.friendWithheld']=!d.fleetCommandG(id,{action:'FIRE',trackId:77,weapon:'SM2'}).ok&&inv(id)===startInv;
  d.fleetCommandG(id,{action:'IDENTITY',trackId:77,identity:'HOSTILE'});d.fleetCommandG(id,{action:'MODE',mode:'AUTO'});
  checks[id+'.autoManualPortWithheld']=!d.fleetCommandG(id,{action:'FIRE',trackId:77,weapon:'SM2'}).ok&&inv(id)===startInv;
  d.fleetCommandG(id,{action:'MODE',mode:'MANUAL'});
  const tr=w.ships.get(id).combatSystem.trackManager.tracks.get(77);tr.sensorAge=9;tr._lastMeasurementStep=-999;
  checks[id+'.staleWithheld']=!d.fleetCommandG(id,{action:'FIRE',trackId:77,weapon:'SM2'}).ok;
  for(const weapon of ['SM2','SM2ER','SM6','ESSM']){
   window.__FLEET_FIXTURE_G__(id);d.fleetCommandG(id,{action:'IDENTITY',trackId:77,identity:'HOSTILE'});const before=ship(id).inventory[weapon],q=d.fleetCommandG(id,{action:'FIRE',trackId:77,weapon});
   checks[id+'.nativeRelease.'+weapon]=q.ok&&ship(id).inventory[weapon]===before-1;trace.push({id,weapon,q});tick(60);
  }
  checks[id+'.otherInventoryUnchanged']=inv(other)===otherInv;
  window.__FLEET_FIXTURE_G__(id,'SURFACE',6000);d.fleetCommandG(id,{action:'IDENTITY',trackId:77,identity:'HOSTILE'});
  const gun=r=>r.weapons.gunMounts?.values().next().value??r.weapons.mainGun,shots=gun(w.ships.get(id)).snapshot().shotsFired;
  const gunRequest=d.fleetCommandG(id,{action:'FIRE',trackId:77,weapon:'GUN',mountId:ship(id).guns[0].id});
  for(let i=0;i<10;i++){window.__FLEET_FIXTURE_G__(id,'SURFACE',6000);d.fleetCommandG(id,{action:'IDENTITY',trackId:77,identity:'HOSTILE'});tick(30);}
  checks[id+'.nativeGunRelease']=gunRequest.ok&&gun(w.ships.get(id)).snapshot().shotsFired>shots;trace.push({id,weapon:'GUN',q:gunRequest,after:gun(w.ships.get(id)).snapshot()});
  window.__FLEET_FIXTURE_G__(id,'SURFACE',30000);d.fleetCommandG(id,{action:'IDENTITY',trackId:77,identity:'HOSTILE'});const hBefore=ship(id).inventory.HARPOON,hq=d.fleetCommandG(id,{action:'FIRE',trackId:77,weapon:'HARPOON'});tick(60);
  checks[id+'.nativeHarpoonOrAbsent']=hBefore>0? hq.ok&&ship(id).inventory.HARPOON===hBefore-1:!hq.ok&&ship(id).inventory.HARPOON===0;trace.push({id,weapon:'HARPOON',q:hq,before:hBefore,after:ship(id).inventory.HARPOON});

  checks[id+'.missingLocalTrackWithheld']=!d.fleetCommandG(id,{action:'FIRE',trackId:999,weapon:'SM2'}).ok;
  const copy=snap();copy.ships[0].inventory.SM2=-1;checks[id+'.detachedSnapshot']=ship(oid).inventory.SM2>=0;
 }
 checks.enemyControlRejected=!d.fleetSelectG('SHIP_SCENARIO_ENEMY_A').ok&&!d.fleetCommandG('SHIP_SCENARIO_ENEMY_A',{action:'NAV',speedKt:10,rudderDeg:0}).ok;
 checks.sameLocalIdSeparateFiles=own.combatSystem.trackManager.tracks.get(77)!==ally.combatSystem.trackManager.tracks.get(77);
 checks.rolesAndProfilesStayPut=w.activePlayerShipId===oid&&own.role==='PLAYER'&&ally.role==='ALLY'&&own.profileId===before.profileId;
 const nav1={...own.navigation.positionWorld},nav2={...ally.navigation.positionWorld};d.fleetCommandG(oid,{action:'NAV',speedKt:22,rudderDeg:-10});d.fleetCommandG(aid,{action:'NAV',speedKt:14,rudderDeg:15});tick(120);
 checks.independentPhysicalCommands=own.navigation.targetSpeedKt===22&&ally.navigation.targetSpeedKt===14&&own.navigation.targetRudder===-10&&ally.navigation.targetRudder===15;
 checks.allyActuallyMoves=Math.hypot(ally.navigation.positionWorld.x-nav2.x,ally.navigation.positionWorld.y-nav2.y)>0;
 const saved=d.exportOperationalStateV48Wip11A();d.fleetSelectG(aid);d.importOperationalStateV48Wip11A(saved);checks.importResetsSelection=snap().selectedShipId===oid;checks.importResetsLocalTargets=snap().ships.every(s=>s.selectedTrackId===null&&s.tracks.length===0);
 checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.faultsZero=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();return {checks,trace,pass:Object.values(checks).every(Boolean)};
}'''
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--suite',choices=['ui','camera'],default='ui');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw,a.suite=='camera')
  for own,ally,width,height in [('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA',1100,800),('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA',393,852)]:
   p=load_fleet(b,a.html.read_bytes(),own,ally,own,width,height,a.suite=='camera',errors,touch=width<640);checks={};click=lambda selector:p.locator(selector).tap()if width<640 else p.locator(selector).click()
   if a.suite=='camera':
    p.wait_for_function('window.__WIP148_3D_VIEW__?.ready&&window.__WIP148_3D_VIEW__.navalShipPresentersB.size===2',timeout=120000)
    p.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__;v.c12ApplyPreset('LOW');window.__FLEET_DRAWS_G__=0;const draw=v.renderer.render;v.renderer.render=function(...args){window.__FLEET_DRAWS_G__++;return draw.apply(this,args);};}''');p.wait_for_function('window.__FLEET_DRAWS_G__>2',timeout=60000);before=p.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),(k,v)=>k==="performance"?undefined:v)')
    camera=lambda:p.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__;return {focus:v.navalFocusB,position:v.camera.position.toArray(),label:document.getElementById('external3DNavalShipBtn').textContent,target:v.navalShipPresentersB.get('SHIP_SCENARIO_ALLY_F').shipRoot.getWorldPosition(new v.THREE.Vector3()).toArray()};}''')
    start=camera();click('#external3DNavalShipBtn');p.wait_for_function('window.__WIP148_3D_VIEW__.navalFocusB==="SHIP_SCENARIO_ALLY_F"');p.wait_for_function('window.__WIP148_3D_VIEW__.camera.position.distanceTo(window.__WIP148_3D_VIEW__.navalShipPresentersB.get("SHIP_SCENARIO_ALLY_F").shipRoot.getWorldPosition(new window.__WIP148_3D_VIEW__.THREE.Vector3()))<310',timeout=90000);focused=camera();checks['realPointerOrTouch']=focused['focus']=='SHIP_SCENARIO_ALLY_F'and focused['label']=='자함 보기';checks['cameraActuallyMoves']=sum((x-y)**2 for x,y in zip(start['position'],focused['position']))>10000
    checks['cameraNearAlliedHull']=sum((x-y)**2 for x,y in zip(focused['position'],focused['target']))<310**2
    draws=p.evaluate('window.__FLEET_DRAWS_G__');click('#external3DNavalShipBtn');p.wait_for_function('n=>window.__FLEET_DRAWS_G__>n+2',arg=draws,timeout=90000);back=camera();checks['returnsToOwnship']=back['focus']is None and back['label']=='아군함 보기'
    checks['cameraStateReadOnly']=before==p.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),(k,v)=>k==="performance"?undefined:v)')
    p.evaluate('window.__WIP148_3D_VIEW__.close()');click('#modeFleetBtn');click('#fleetChangeG');click('#fleetViewG');p.wait_for_function('window.__WIP148_3D_VIEW__.active&&window.__WIP148_3D_VIEW__.navalFocusB==="SHIP_SCENARIO_ALLY_F"');checks['selectedShipViewWorks']=True
    p.evaluate('window.__WIP148_3D_VIEW__.resetCamera()');checks['resetResyncsLabel']=p.locator('#external3DNavalShipBtn').inner_text()=='아군함 보기';p.screenshot(path=str(a.out/(own+'-camera.png')))
    trace={'before':start,'focused':focused,'after':back}
   else:
    p.evaluate(SETUP);before=p.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),(k,v)=>k==="performance"?undefined:v)');click('#modeFleetBtn');checks['fourTabs']=p.locator('.control-deck-tab[data-tab]').count()==4 and p.locator('#controlDeckFleetPage').is_visible();click('#fleetChangeG');checks['switchActuallySelectsAlly']=p.evaluate('window.__NAVAL_SIM_DIAG__.fleetSnapshotG().selectedShipId')=='SHIP_SCENARIO_ALLY_F';checks['selectionDoesNotMoveState']=before==p.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),(k,v)=>k==="performance"?undefined:v)')
    p.locator('#fleetSpeedG').fill('22');p.locator('#fleetRudderG').fill('15');click('#fleetNavG');snap=p.evaluate('window.__NAVAL_SIM_DIAG__.fleetSnapshotG()');checks['nativeNavUi']=snap['ships'][1]['speedKt']==22 and snap['ships'][1]['rudderDeg']==15 and snap['ships'][0]['speedKt']!=22
    p.locator('#fleetModeG').select_option('AUTO');checks['nativeAllyMode']=p.evaluate('window.__NAVAL_SIM_DIAG__.fleetSnapshotG().ships[1].mode')=='AUTO';p.locator('#fleetModeG').select_option('MANUAL');
    p.evaluate("window.__FLEET_FIXTURE_G__('SHIP_SCENARIO_ALLY_F')");p.locator('#fleetTrackG').select_option('77');p.locator('#fleetIdentityG').select_option('HOSTILE');click('#fleetIdentifyG');p.locator('#fleetWeaponG').select_option('SM2');n=p.evaluate('window.__NAVAL_SIM_DIAG__.fleetSnapshotG().ships[1].inventory.SM2');click('#fleetFireG');checks['nativeManualUiRelease']=p.evaluate('window.__NAVAL_SIM_DIAG__.fleetSnapshotG().ships[1].inventory.SM2')==n-1
    p.locator('#networkRadioG').scroll_into_view_if_needed();click('#networkRadioG');checks['networkCommandSelectedOwner']=p.evaluate('window.__NAVAL_SIM_DIAG__.networkSnapshotG().ships.find(s=>s.entityId==="SHIP_SCENARIO_ALLY_F").settings.enabled')is False and p.evaluate('window.__NAVAL_SIM_DIAG__.networkSnapshotG().ships[0].settings.enabled')is True
    p.screenshot(path=str(a.out/(own+'-fleet.png')));p.evaluate(SETUP);port=p.evaluate(PORTS);checks.update(port['checks']);trace=port['trace']
   checks['noCoreOrRuntimeFaults']=p.evaluate('window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault()');rows.append({'own':own,'ally':ally,'viewport':[width,height],'input':'touch'if width<640 else'pointer','checks':checks,'trace':trace});p.close();(a.out/('fleet-'+a.suite+'-progress.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'suite':a.suite,'own':own,'failed':[k for k,v in checks.items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'suite':a.suite,'backend':'Chromium SwiftShader native RAF camera'if a.suite=='camera'else'Chromium actual UI and measured diagnostic files','cases':rows,'errors':errors,'pass':not errors and all(all(q['checks'].values())for q in rows)};(a.out/('fleet-'+a.suite+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
