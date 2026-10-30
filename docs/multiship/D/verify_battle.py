"""Actual Harpoon launch → INS/ARH → opposite full ShipRuntime; no scripted hit."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[2]/'docs/bunkerhill/K'));from browser_i import launch,load
from verify_weapons import SETUP
FIXTURE=r'''foreign=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,id='SHIP_SCENARIO_ENEMY_A',checks={},samples=[];
 const saved=d.exportOperationalStateV48Wip11A(),own=saved.ship.navigation,enemy=saved.fleet.ships[0].ship.navigation;
 Object.assign(own,{positionWorld:{x:0,y:0},previousPositionWorld:{x:0,y:0},heading:0,previousHeadingWorld:0,speed:0,targetSpeedKt:0,vx:0,vy:0});
 Object.assign(enemy,{positionWorld:{x:(foreign?-8000:8000)*.0038,y:0},previousPositionWorld:{x:(foreign?-8000:8000)*.0038,y:0},heading:0,previousHeadingWorld:0,speed:0,targetSpeedKt:0,vx:0,vy:0});d.importOperationalStateV48Wip11A(saved);d.setTerrainDiagBypass(true);d.setEmcon(false);d.observerCommandC(id,{emcon:false});
 let tid,release;if(foreign){d.weaponFixtureD(id,{action:'track',trackId:31,domain:'SURFACE',positionM:{x:0,y:0,z:8}});d.weaponFixtureD(id,{action:'identity',trackId:31,identity:'HOSTILE'});tid=31;release=d.weaponCommandD(id,{observerShipId:id,trackId:tid,weapon:'HARPOON'});}
 else {d.runFramesToTicks(60,8,600);const t=d.observerSnapshotC().ships[0].tracks.filter(q=>q.classification==='SURFACE'&&q.confirmed&&Math.hypot(q.positionM.x-8000,q.positionM.y)<500)[0];if(!t)throw Error('NO_NATURAL_NAVAL_RADAR_CONTACT');tid=t.trackId;d.a3SetOperatorIdentity(tid,'TRAINING_TARGET');h.select(tid);release=h.fire(tid);}
 const firingShipId=foreign?id:d.exportOperationalStateV48Wip11A().shipId,targetShipId=foreign?d.exportOperationalStateV48Wip11A().shipId:id,
  sourceBefore=(foreign?d.exportOperationalStateV48Wip11A().fleet.ships[0]:d.exportOperationalStateV48Wip11A()).ship.damage.moduleDamage;
 d.setEmcon(true);checks.authorizedRelease=release.ok;
 for(let i=0;i<48;i++){d.runFramesToTicks(60,8,60);const m=h.snapshot().missiles.at(-1);if(m){samples.push({ageS:m.ageS,positionM:m.positionM,velocityMps:m.velocityMps,seekerMode:m.seeker.mode,boosterAttached:m.boosterAttached,alive:m.alive,outcome:m.outcome,impact:m.impact,ownerEntityId:m.ownerEntityId,memory:m.memory});if(!m.alive)break;}}
 const m=h.snapshot().missiles.at(-1),after=d.exportOperationalStateV48Wip11A(),targetDamage=(foreign?after:after.fleet.ships[0]).ship.damage.moduleDamage,sourceAfter=(foreign?after.fleet.ships[0]:after).ship.damage.moduleDamage;
 checks.ownerAddress=m?.ownerEntityId===firingShipId;checks.fixedBoost=samples.some(q=>q.ageS<3.2&&q.boosterAttached)&&samples.some(q=>q.ageS>3.2&&!q.boosterAttached);
 checks.insArh=samples.some(q=>q.seekerMode==='SEARCH')&&samples.some(q=>q.seekerMode==='TRACK');checks.memoryFrozen=JSON.stringify(samples[0]?.memory)===JSON.stringify(samples.at(-1)?.memory)&&m.memory.updatesAfterRelease===false&&m.memory.truthUsed===false;
 checks.actualNavalContact=m?.outcome==='NAVAL_CONTACT'&&m.impact?.targetEntityId===targetShipId&&m.impact.accepted;
 checks.realReceiverDamage=Object.values(targetDamage).some(q=>q>0);checks.launcherDamageIsolated=JSON.stringify(sourceBefore)===JSON.stringify(sourceAfter);
 checks.noTelemetry=h.operatorPicture().telemetryAvailable===false&&h.profile().dataLink===false;
 checks.ownLaunchKnowledgeIsolated=!foreign||h.operatorPicture().launches.length===0;
 if(foreign){const eventId=m.impact.eventId;d.importOperationalStateV48Wip11A(saved);h.reset(true);d.setTerrainDiagBypass(true);d.setEmcon(true);d.observerCommandC(id,{emcon:false});d.weaponFixtureD(id,{action:'track',trackId:31,domain:'SURFACE',positionM:{x:0,y:0,z:8}});d.weaponFixtureD(id,{action:'identity',trackId:31,identity:'HOSTILE'});const repeat=d.weaponCommandD(id,{observerShipId:id,trackId:31,weapon:'HARPOON'});for(let i=0;i<48;i++){d.runFramesToTicks(60,8,60);if(h.snapshot().missiles.at(-1)&&!h.snapshot().missiles.at(-1).alive)break;}const second=h.snapshot().missiles.at(-1);checks.resetAllowsReusedProjectileEventId=repeat.ok&&second?.impact?.eventId===eventId&&second.impact.accepted&&Object.values(d.exportOperationalStateV48Wip11A().ship.damage.moduleDamage).some(v=>v>0);}
 checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.noFault=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();
 return {checks,foreign,release,firingShipId,targetShipId,samples,targetDamage,operatorPicture:h.operatorPicture(),pass:Object.values(checks).every(Boolean)};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright() as pw:
  b=launch(pw)
  for foreign in [True,False]:
   page=load(b,a.html.read_bytes(),ship='DDG_119_LATE_FLIGHT_IIA' if foreign else 'CG_52_LATE_TICONDEROGA',errors=errors);page.evaluate(SETUP,'CG_52_LATE_TICONDEROGA' if foreign else 'DDG_119_LATE_FLIGHT_IIA');q=page.evaluate(FIXTURE,foreign);rows.append(q);page.close();print(json.dumps({'foreign':foreign,'failed':[k for k,v in q['checks'].items() if not v],'final':q['samples'][-1]['outcome']}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass'] for q in rows)};(a.out/'battle.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
