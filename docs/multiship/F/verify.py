"""Real predeparture controls, three owners, anonymous RF and actual soft-kill releases."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch
FIXTURE=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,world=window.__AEGIS_ENGAGEMENT_RUNTIME__,checks={},aid='SHIP_SCENARIO_ALLY_F',eid='SHIP_SCENARIO_ENEMY_A',ownId=world.activePlayerShipId;
 const ship=id=>world.ships.get(id),tick=n=>d.runFramesToTicks(60,1,n),save=()=>d.exportOperationalStateV48Wip11A(),snapshot=()=>d.electronicSnapshotF(),state=id=>snapshot().ships.find(q=>q.entityId===id);
 const stable=x=>JSON.stringify(x,(key,value)=>key==='performance'?undefined:value),base=save(),position=q=>q.navigation.positionWorld,distance=(a,b)=>Math.hypot(position(a).x-position(b).x,position(a).y-position(b).y)/.0038;
 checks.threeOwners=world.ships.size===3&&d.physicalFleetSnapshotB().simulated===3;
 checks.roles=ship(aid).role==='ALLY'&&ship(eid).role==='ENEMY'&&ship(ownId).role==='PLAYER';checks.factions=ship(aid).faction===ship(ownId).faction&&ship(eid).faction!==ship(ownId).faction;
 checks.allyNear=distance(ship(ownId),ship(aid))>=400&&distance(ship(ownId),ship(aid))<2000;checks.enemyRange=distance(ship(ownId),ship(eid))>=10000&&distance(ship(ownId),ship(eid))<=30000;
 checks.independent=ship(aid).weapons!==ship(eid).weapons&&ship(aid).ew.contacts!==ship(eid).ew.contacts&&ship(aid).combatSystem.observerC.rng!==ship(eid).combatSystem.observerC.rng;
 checks.sourceInventory=base.fleet.ships.every(q=>q.ship.inventory.softKill15B.nulka.launchers.length===4&&q.ship.inventory.softKill15B.nulka.launchers.every(l=>l.tubes.length===2));
 checks.cgHasNoRam=[...world.ships.values()].filter(q=>q.profileId==='CG_52_LATE_TICONDEROGA').every(q=>q.weapons.closeIn.every(m=>m.type!=='RAM'));
 checks.saveValid=d.validateOperationalStateV48Wip11A(base).ok;
 const mutations={duplicate:q=>q.fleet.ships[1].entityId=q.fleet.ships[0].entityId,faction:q=>q.fleet.ships[0].faction='HOSTILE',role:q=>q.fleet.ships[0].role='ENEMY',ew:q=>q.fleet.ships[0].ew.emcon='ON',ownEw:q=>q.ship.ew.auto=1,missingEw:q=>delete q.ship.ew,missingAlly:q=>delete q.deployment.allyProfileId,seed:q=>q.deployment.placementSeed=-1,ammo:q=>q.fleet.ships[0].ship.inventory.softKill15B.nulka.logistics.expendedRounds++};
 for(const [name,mutate]of Object.entries(mutations)){const q=structuredClone(base);mutate(q);const before=stable(save()),revision=world.lifecycle.revision;let rejected=false;try{d.importOperationalStateV48Wip11A(q);}catch(e){rejected=true;}checks['atomic.'+name]=rejected&&before===stable(save())&&revision===world.lifecycle.revision;}
 d.importOperationalStateV48Wip11A(base);const roundtrip=save();const persisted=q=>({deployment:q.deployment,ships:[q.ship,...q.fleet.ships.map(r=>r.ship)].map(r=>({ew:r.ew,position:r.navigation.positionWorld,heading:r.navigation.heading,targetSpeedKt:r.navigation.targetSpeedKt,targetRudder:r.navigation.targetRudder,inventory:JSON.parse(JSON.stringify(r.inventory,(k,v)=>k==='startedStep'?undefined:v)),liquidLoads:r.liquidLoads,moduleDamage:r.damage.moduleDamage,water:r.damage.flooding.cells.map(c=>[c.id,c.waterM3]),crew:[r.crew.total,r.crew.fit,r.crew.injured,r.crew.dead,r.crew.evacuated]})),fleetEw:q.fleet.ships.map(r=>r.ew)});checks.roundtrip=JSON.stringify(persisted(roundtrip))===JSON.stringify(persisted(base));
 const legacy=structuredClone(base);legacy.deployment={schema:'AEGIS_DEPLOYMENT_MULTI_SHIP_E_1',targetShip:'NONE',enemyProfileId:base.deployment.enemyProfileId,enemyAircraftEnabled:false};legacy.fleet.ships=legacy.fleet.ships.filter(q=>q.entityId===eid);legacy.fleet.schema='AEGIS_NAVAL_PHYSICAL_FLEET_B_1';for(const q of legacy.fleet.ships){delete q.role;delete q.faction;delete q.ew;delete q.ship.inventory.softKill15B;delete q.ship.inventory.mk36;}delete legacy.ship.ew;
 checks.legacyValidated=d.validateOperationalStateV48Wip11A(legacy).ok;d.importOperationalStateV48Wip11A(legacy);checks.legacyRestored=save().deployment.allyProfileId===null&&world.ships.size===2;d.importOperationalStateV48Wip11A(base);
 // Passive naval measurements arrive while own search radars are silent.
 d.setEmcon(true);for(const id of [aid,eid])d.electronicCommandF(id,{emcon:false,auto:false,noiseRequested:false,deceptionRequested:false});tick(600);
 const passive=state(ownId);checks.passiveNavalDetected=passive.contacts.some(c=>c.type==='SHIP SEARCH RADAR');checks.esmAnonymous=passive.contacts.every(c=>!('truthRef'in c)&&!('objectId'in c)&&!('ownerEntityId'in c)&&!('x'in c)&&!('y'in c)&&c.rangeKm===null&&c.identity==='UNKNOWN');
 checks.ownSilentStillReceives=passive.settings.emcon&&passive.ticks>=600;
 for(const id of [aid,eid])d.electronicCommandF(id,{emcon:true});tick(840);checks.silentCoastsAndExpires=state(ownId).contacts.length===0;
 // Receiver-specific band, range, directional emission and equipment damage.
 d.setTerrainDiagBypass(true);const jammer=ship(eid),rx=position(ship(ownId)),jn=jammer.navigation;
 jn.positionWorld={x:rx.x+.0038*5000,y:rx.y};jn.heading=Math.PI/2;jn.previousHeadingWorld=jn.heading;
 d.electronicCommandF(eid,{noiseRequested:true,deceptionRequested:true,auto:false,autoAim:false,bearingRad:Math.PI});tick(120);
 const radarOpts=band=>({observerShipId:ownId,receiver:{x:rx.x,y:rx.y,z:20},band,beamAz:0,beamEl:0,beamHalfAzRad:.1,beamHalfElRad:.1});
 const received=d.electronicRadarProbeF(radarOpts('X'));checks.noiseReceived=received.noise>0;checks.replayReceived=received.replay>0;checks.bandIsolation=d.electronicRadarProbeF(radarOpts('S')).noise===0;
 checks.sharedResource=state(eid).allocator.resourceUsed<=1.0000001&&state(eid).allocator.noiseShare>0&&state(eid).allocator.deceptionShare>0;
 jn.positionWorld={x:rx.x+.0038*10000,y:rx.y};const far=d.electronicRadarProbeF(radarOpts('X'));checks.rangeAttenuation=far.noise<received.noise;checks.receiverBeamRejects=d.electronicRadarProbeF({...radarOpts('X'),beamAz:Math.PI/2}).noise<far.noise;
 d.electronicCommandF(eid,{noiseRequested:false,deceptionRequested:false});tick(1);checks.offStopsRf=d.electronicRadarProbeF(radarOpts('X')).noise===0;
 d.electronicCommandF(eid,{noiseRequested:true});tick(120);for(const box of jammer.geometry.boxes.filter(q=>q.name.includes('SLQ-32')||jammer.profileId.startsWith('DDG')&&['GEN_1','GEN_2','GEN_3','CDC'].includes(q.system)))jammer.flooding.setDamage(box.name,100);checks.damageStopsRf=d.electronicRadarProbeF(radarOpts('X')).noise===0;
 d.importOperationalStateV48Wip11A(base);d.setTerrainDiagBypass(true);d.setEmcon(false);
 // Authenticated measured IFF can label an existing radar contact, not create one.
 const a=ship(aid),op=position(ship(ownId));d.weaponFixtureD(aid,{action:'track',trackId:96,positionM:{x:op.x/.0038,y:op.y/.0038,z:8},velocityMps:{x:0,y:0,z:0}});const friend=a.combatSystem.trackManager.tracks.get(96);friend.domain='SURFACE';friend.classification='SURFACE';tick(30);checks.iffProtects=friend.identity==='FRIEND'&&friend.engagementAuthority==='WITHHELD';
 const replies=d.friendlyIffProbeF(aid);checks.iffRepliesMeasured=replies.length>0&&replies.every(q=>q.authenticatedFriendly&&!('entityId'in q)&&!('x'in q)&&!('truthRef'in q));
 // Real owner-native releases consume only the selected owner's inventory.
 d.electronicCommandF(aid,{auto:false,noiseRequested:false,deceptionRequested:false});d.defenseCommandE(aid,{mode:'HOLD'});
 const an=a.navigation,bearing=an.heading+Math.PI/2,tid=91,point={x:an.positionWorld.x/.0038+Math.cos(bearing)*4000,y:an.positionWorld.y/.0038+Math.sin(bearing)*4000,z:15};
 d.weaponFixtureD(aid,{action:'track',trackId:tid,positionM:point,velocityMps:{x:-250*Math.cos(bearing),y:-250*Math.sin(bearing),z:0}});d.weaponFixtureD(aid,{action:'identity',trackId:tid,identity:'HOSTILE'});
 d.electronicReceiverProbeF(aid,[{bearing,bearingSigmaDeg:.6,strength:1,quality:1,band:'IJ',type:'MISSILE SEEKER TRACK',emitterClass:'ACTIVE_SEEKER',measuredAtS:d.observerSnapshotC().worldTimeS}]);
 const before=state(aid).logistics,otherBefore=stable(save().fleet.ships.find(q=>q.entityId===eid).ship.inventory),ownBefore=stable(save().ship.inventory);
 const nulka=d.electronicReleaseF(aid,'NULKA'),srboc=d.electronicReleaseF(aid,'SRBOC'),after=state(aid).logistics;
 checks.actualNulka=nulka.ok&&after.nulka.expendedRounds===before.nulka.expendedRounds+1;checks.actualSrboc=srboc.ok&&after.srboc.expendedRounds>before.srboc.expendedRounds;
 checks.releaseIsolation=ownBefore===stable(save().ship.inventory)&&otherBefore===stable(save().fleet.ships.find(q=>q.entityId===eid).ship.inventory);
 checks.conservation=after.nulka.conserved&&after.srboc.conserved;
 const physical=world.world.entities.activeDecoys.find(q=>q.id===nulka.id);checks.registeredMuzzle=!!physical&&physical.ownerEntityId===aid&&Math.hypot(physical.x-a.weapons.nulka.lastLaunch.muzzle.origin.xM*.0038,physical.y-a.weapons.nulka.lastLaunch.muzzle.origin.yM*.0038)<1e-9;
 const spent=save();checks.spentSaveValid=d.validateOperationalStateV48Wip11A(spent).ok;d.importOperationalStateV48Wip11A(spent);checks.spentRestored=state(aid).logistics.nulka.expendedRounds===after.nulka.expendedRounds&&state(aid).logistics.srboc.expendedRounds===after.srboc.expendedRounds;checks.combatTransientCleared=world.world.entities.activeDecoys.length===0&&state(aid).contacts.length===0;
 checks.truthPlotRejected=d.electronicReceiverProbeF(aid,[{truthRef:123}]).reason==='ANONYMOUS_EW_PLOT_REQUIRED';checks.invalidCommand=d.electronicCommandF(aid,{truthRef:123}).reason==='EW_COMMAND_FIELDS';checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.faultZero=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();
 return {checks,pass:Object.values(checks).every(Boolean),base,roundtrip,passive,received,far,nulka,srboc,after};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);p.add_argument('--webgl',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];errors=[]
 with sync_playwright()as pw:
  browser=launch(pw,webgl=a.webgl)
  for width,height,own,ally,enemy in [(1000,760,'DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA'),(393,852,'CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA')]:
   page=browser.new_page(viewport={'width':width,'height':height});page.on('pageerror',lambda e:errors.append(str(e)));page.add_init_script('window.__NAVAL_SIM_SEED__=1831565813;');page.route('https://aegis.test/**',lambda r:r.fulfill(body=a.html.read_bytes(),content_type='text/html'));page.goto('https://aegis.test/candidate?view3d='+('1'if a.webgl else'0'),wait_until='load',timeout=90000);page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000)
   controls=page.locator('[data-deployment-a]:visible');controls.locator('[data-ally-choice]').select_option(ally);controls.locator('[data-enemy-choice]').select_option(enemy);controls.locator('[data-target-choice]').select_option('NONE');controls.locator('[data-enemy-aircraft-choice]').select_option('OFF');page.locator('#aegisShipSelect').select_option(own);page.screenshot(path=str(a.out/(own+'-startup.png')));page.locator('#aegisShipConfirmBtn').click();page.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__',timeout=120000)
   sync=page.locator('[data-deployment-a]:visible [data-ally-choice]').input_value()==ally and page.locator('[data-deployment-a]:visible [data-enemy-choice]').input_value()==enemy;page.screenshot(path=str(a.out/(own+'-loadout.png')));page.locator('#wip125DepartBtn').click();page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');q=page.evaluate(FIXTURE);q['checks']['uiSynchronized']=sync;q['pass']=all(q['checks'].values());q.update(own=own,ally=ally,enemy=enemy,viewport=[width,height]);rows.append(q);print(json.dumps({'own':own,'failed':[k for k,v in q['checks'].items()if not v]}),flush=True);page.screenshot(path=str(a.out/(own+'-cic.png')));page.close()
  browser.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
