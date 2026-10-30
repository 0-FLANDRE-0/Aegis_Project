"""Empty CMS -> real surface RF plots -> operator ID/consent -> H3/native flight.

Identification is an explicit scenario operator command on the observed file;
absence of IFF never invents HOSTILE. No target truth is injected into a track.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'G'))
from browser_g import launch,load_fleet
FIXTURE=r'''()=>{
 const d=__NAVAL_SIM_DIAG__,w=__AEGIS_ENGAGEMENT_RUNTIME__,h=__HARPOON_DIAG_A__,oid=w.activePlayerShipId,aid='SHIP_SCENARIO_ALLY_F',eid='SHIP_SCENARIO_ENEMY_A',checks={},rows=[];
 const s=d.exportOperationalStateV48Wip11A(),set=(n,x)=>Object.assign(n,{positionWorld:{x:x*.0038,y:0},previousPositionWorld:{x:x*.0038,y:0},heading:0,previousHeadingWorld:0,speed:0,targetSpeedKt:0,vx:0,vy:0,rudder:0,targetRudder:0});set(s.ship.navigation,0);set(s.fleet.ships.find(q=>q.entityId===aid).ship.navigation,-1500);set(s.fleet.ships.find(q=>q.entityId===eid).ship.navigation,12000);
 for(const q of s.fleet.ships){q.attack.enabled=q.entityId===eid;q.ew.emcon=false;q.ew.auto=false;q.ew.noiseRequested=false;q.ew.deceptionRequested=false;}
 d.importOperationalStateV48Wip11A(s);d.setTerrainDiagBypass(true);d.setEmcon(false);d.tacticalCommandH1(oid,{enabled:true});d.wip119SetMode('AUTO');d.attackCommandH3(oid,{enabled:true});for(const r of w.ships.values())r.combatSystem.trackManager.tracks.clear();checks.cmsInitiallyEmpty=[...w.ships.values()].every(r=>r.combatSystem.trackManager.tracks.size===0);
 let ownTr=null,enemyTr=null;const local=(id,min,max)=>[...w.ships.get(id).combatSystem.trackManager.tracks.values()].filter(tr=>tr.confirmed&&tr.domain==='SURFACE'&&tr.sensorDetected!==false&&tr.sensorAge<=2&&!tr.truthRef&&!['FRIEND','NEUTRAL'].includes(tr.identity)&&Math.hypot(tr.x-w.ships.get(id).navigation.positionWorld.x,tr.y-w.ships.get(id).navigation.positionWorld.y)/.0038>min&&Math.hypot(tr.x-w.ships.get(id).navigation.positionWorld.x,tr.y-w.ships.get(id).navigation.positionWorld.y)/.0038<max).sort((a,b)=>a.trackId-b.trackId)[0];
 for(let i=0;i<100&&!ownTr;i++){d.runFramesToTicks(60,1,30);ownTr=local(oid,10000,13000);enemyTr=local(eid,10000,13000);rows.push({phase:'acquire',time:d.observerSnapshotC().worldTimeS,ownSurface:d.observerSnapshotC().ships[0]?.tracks,attack:d.attackSnapshotH3()});}
 checks.naturalOwnSurfaceConfirmed=!!ownTr;checks.enemyUnidentifiedNoFirstStrike=w.ships.get(eid).weapons.harpoon.tubes.every(q=>q.loaded);
 if(ownTr){checks.localFileAnonymous=!ownTr.truthRef&&ownTr.sensorSource!=='OFFBOARD_C';checks.ownExplicitHostile=d.fleetCommandG(oid,{action:'IDENTITY',trackId:ownTr.trackId,identity:'HOSTILE'}).ok;checks.ownExplicitConsent=d.attackCommandH3(oid,{authorizeTrackId:ownTr.trackId,rounds:1}).ok;}
 for(let i=0;i<160;i++){
  d.runFramesToTicks(60,1,30);if(!enemyTr)enemyTr=local(eid,10000,13000);
  if(enemyTr&&!checks.enemyMeasuredDesignation){checks.enemyMeasuredDesignation=d.weaponFixtureD(eid,{action:'identity',trackId:enemyTr.trackId,identity:'HOSTILE'}).ok;}
  const missiles=h.snapshot().missiles;rows.push({phase:'engage',time:d.observerSnapshotC().worldTimeS,attack:d.attackSnapshotH3(),diagnosticOnlyFlights:missiles.map(m=>({id:m.id,ownerEntityId:m.ownerEntityId,alive:m.alive,phase:m.phase,seeker:m.seeker,memory:m.memory,ins:m.ins,ageS:m.ageS,outcome:m.outcome,positionM:m.positionM})),picture:h.operatorPicture(),defense:d.defenseSnapshotE(),ownDefense:d.wip119AutonomySnapshot()});
 }
 const released=id=>rows.some(q=>q.attack.ships.find(s=>s.entityId===id)?.log.some(x=>x.action==='RELEASE'));
 checks.ownRealSensorToActualHarpoon=released(oid);checks.enemyRealSensorToActualHarpoon=released(eid);checks.nativeInsNoUpdates=rows.filter(q=>q.diagnosticOnlyFlights).every(q=>q.diagnosticOnlyFlights.every(m=>m.ins&&m.memory.updatesAfterRelease===false));checks.actualSeekerSearch=rows.some(q=>q.diagnosticOnlyFlights?.some(m=>m.seeker.mode==='SEARCH'));checks.nativeTrackingOrDefense=rows.some(q=>q.diagnosticOnlyFlights?.some(m=>m.seeker.mode==='TRACK')||q.ownDefense?.fireLog.length>0||q.defense?.ships.some(s=>s.autonomy.fireLog.length>0));checks.noAttackFlightTelemetry=rows.every(q=>q.attack.dataLink===false&&q.attack.remoteFireControl===false&&q.attack.ships.every(s=>!('missiles'in s)&&!('positionM'in s)));checks.noBlindOperatorPosition=rows.filter(q=>q.picture).every(q=>!q.picture.telemetryAvailable&&q.picture.launches.every(l=>l.positionM==null||['RADAR','ESTIMATE'].includes(l.source)&&l.measurementAgeS<=4));d.setEmcon(true);d.runFramesToTicks(60,1,300);const blind=h.operatorPicture();checks.actualBlindPositionAbsent=blind.launches.every(l=>l.positionM===null&&l.source==='NOT_OBSERVED');checks.salvoBudget=rows.at(-1).attack.ships.find(q=>q.entityId===oid).log.filter(q=>q.action==='RELEASE').length===1&&rows.at(-1).attack.ships.find(q=>q.entityId===eid).log.filter(q=>q.action==='RELEASE').length<=2;checks.coreZero=__CORE_SELFTEST_FAILURES__.length===0;checks.noFault=!__WIP125_DIAG__.wip150RuntimeFault()&&!__WIP125_DIAG__.wip150PresentationFault();return {checks,rows,pass:Object.values(checks).every(Boolean)};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[]
 with sync_playwright()as pw:
  b=launch(pw);page=load_fleet(b,a.html.read_bytes(),errors=errors);q=page.evaluate(FIXTURE);page.close();b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'checks':q['checks'],'scenario':q,'errors':errors,'pass':not errors and q['pass']};(a.out/'surface.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':len(q['checks']),'failed':[k for k,v in q['checks'].items()if not v]}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
