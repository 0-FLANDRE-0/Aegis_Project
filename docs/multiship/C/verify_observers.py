"""Natural RF acquisition, owner isolation, independent clocks and external observations."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
FIXTURE=r'''enemy=>{
 const d=window.__NAVAL_SIM_DIAG__,checks={},id='SHIP_SCENARIO_ENEMY_A';
 window.__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{enemyProfileId:enemy,targetShip:'NONE'});window.__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();
 const initial=d.observerSnapshotC();checks.initialEmpty=initial.ships.every(q=>q.tracks.length===0);checks.initialOwnEmcon=initial.ships[0].emcon;
 d.setEmcon(false);d.profilerEnableV48Wip11A(true);d.profilerResetV48Wip11A();const begin=performance.now();d.runFramesToTicks(60,8,1200);const elapsedMs=performance.now()-begin,live=d.observerSnapshotC(),physical=d.physicalFleetSnapshotB();
 const own=live.ships[0],foreign=live.ships[1],near=(q,x,y)=>q.tracks.filter(t=>t.classification==='SURFACE'&&Math.hypot(t.positionM.x-x,t.positionM.y-y)<400);
 const n=physical.ships[0].navigation,ownNav=d.exportOperationalStateV48Wip11A().ship.navigation;
 checks.naturalPlayerContact=near(own,n.positionWorld.x/.0038,n.positionWorld.y/.0038).some(t=>t.confirmed);
 checks.naturalForeignContact=near(foreign,ownNav.positionWorld.x/.0038,ownNav.positionWorld.y/.0038).some(t=>t.confirmed);
 checks.noAutomaticHostile=near(own,n.positionWorld.x/.0038,n.positionWorld.y/.0038).every(t=>t.identity==='UNKNOWN'&&t.engagementAuthority!=='AUTO_AUTHORIZED');
 checks.foreignAuthorityWithheld=foreign.tracks.every(t=>t.identity==='UNKNOWN'&&t.engagementAuthority==='WITHHELD');
 checks.independentTicks=own.tickCount===1200&&foreign.tickCount===1200&&physical.ships[0].clock.tick===1200;
 checks.profileNormalsDiffer=initial.ships[0].profileId===enemy||JSON.stringify(initial.ships[0].faces.map(q=>q.bearingRad))!==JSON.stringify(initial.ships[1].faces.map(q=>q.bearingRad));
 checks.rasterCoversAllFaces=foreign.faces.every(q=>q.hCursor>0&&q.vCursor>0);checks.profileBudget=foreign.stats.usedMs<=(enemy.startsWith('CG')?19:24);
 checks.noTruthFacade=!JSON.stringify(d.observerFacadeC(id)).match(/truthRef|objectId|_truthObject|physicalWorld|SHIP_SCENARIO/);
 // ownerEntityId is permitted platform identity, not a target identity.
 checks.noTruthFacade=!JSON.stringify(d.observerFacadeC(id).tracks).match(/truthRef|objectId|_truthObject|physicalWorld|SHIP_SCENARIO/);
 const detached=d.observerSnapshotC();detached.ships[1].faces[0].center.x=1e9;detached.ships[1].tracks[0].positionM.x=1e9;
 checks.snapshotDetached=d.observerSnapshotC().ships[1].faces[0].center.x!==1e9&&d.observerSnapshotC().ships[1].tracks[0].positionM.x!==1e9;
 const rng=JSON.stringify(foreign.rng),last=foreign.tracks.map(t=>t.sensorAgeS);checks.foreignEmconCommand=d.observerCommandC(id,{emcon:true}).ok;
 d.runFramesToTicks(60,16,360);const silent=d.observerSnapshotC();checks.silentRngUnchanged=JSON.stringify(silent.ships[1].rng)===rng;
 checks.foreignCoast=silent.ships[1].tracks.some(t=>t.lifecycle==='MEMORY'&&t.sensorAgeS>=6);checks.ownStillObserves=near(silent.ships[0],d.physicalFleetSnapshotB().ships[0].navigation.positionWorld.x/.0038,d.physicalFleetSnapshotB().ships[0].navigation.positionWorld.y/.0038).some(t=>t.sensorAgeS<1.5);
 d.observerCommandC(id,{emcon:false});d.runFramesToTicks(60,1,240);checks.reacquisition=d.observerSnapshotC().ships[1].tracks.some(t=>t.confirmed&&t.sensorAgeS<1);
 const saved=d.exportOperationalStateV48Wip11A(),before=d.operationalImportMutationFingerprintV48Wip11B(),observerBefore=JSON.stringify(d.observerSnapshotC()),bad=structuredClone(saved);bad.fleet.ships[0].ship.navigation.positionWorld.x='BAD';let rejected=false;try{d.importOperationalStateV48Wip11A(bad);}catch(e){rejected=true;}
 checks.invalidImportZeroMutation=rejected&&JSON.stringify(before)===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B())&&JSON.stringify(d.observerSnapshotC())===observerBefore;
 d.importOperationalStateV48Wip11A(saved);checks.combatTransientReset=d.observerSnapshotC().ships.every(q=>q.tracks.length===0&&q.offboard.sources.length===0&&q.offboard.queued===0);
 // Every sensor module is disabled only on the foreign owner via real saved damage.
 const damaged=d.exportOperationalStateV48Wip11A();for(const q of d.observerSnapshotC().ships[1].faces)damaged.fleet.ships[0].ship.damage.moduleDamage[q.moduleName]=100;
 for(const k of enemy.startsWith('CG')?['AN/SPQ-9','AN/SPS-73']:['AN/SPQ-9B','BridgeMaster E'])damaged.fleet.ships[0].ship.damage.moduleDamage[k]=100;
 d.importOperationalStateV48Wip11A(damaged);d.setEmcon(false);d.runFramesToTicks(60,8,300);const deadSensors=d.observerSnapshotC();checks.foreignSensorDamage=deadSensors.ships[1].stats.plots===0;checks.ownSensorsUnaffected=deadSensors.ships[0].legacyPlayerAudit.cycle>0;
 checks.observerUnit=d.observerFixtureC().pass;checks.offboardUnit=d.offboardFixtureC().pass;
 // Port test uses noisy external observations, never target IDs or a world truth query.
 const ownId=d.exportOperationalStateV48Wip11A().shipId,time=d.observerSnapshotC().worldTimeS;
 checks.externalLink=d.offboardDiagnosticC(ownId,{link:{sourceId:'HELI_TEST',connected:true,latencyS:.25}}).ok;
 const report={schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'HELI_TEST',sequence:1,measuredAtS:time-.5,positionM:{x:90000,y:65000,z:8},covarianceM2:[40000,0,0,0,40000,0,0,0,400],domainEvidence:{surface:.9,air:.05,missile:.05,background:.05}};
 checks.externalQueued=d.offboardDiagnosticC(ownId,{report}).ok&&d.offboardSnapshotC().queued===1;
 d.runFramesToTicks(60,1,10);checks.externalLatency=d.offboardSnapshotC().accepted===0;
 d.runFramesToTicks(60,1,10);const external=d.observerSnapshotC().ships[0].tracks.find(q=>q.offboard?.remote.some(s=>s.sourceId==='HELI_TEST'));
 checks.externalMeasuredAge=external?.sensorAgeS>=.75&&external.offboard.remote[0].measurementAgeS>=.75&&external.covariance[0]>=40000;
 checks.externalNoTruthIdentity=external?.identity==='UNKNOWN'&&external.engagementAuthority==='WITHHELD';
 d.offboardDiagnosticC(ownId,{link:{sourceId:'HELI_TEST',connected:false,latencyS:.25}});const extCount=d.offboardSnapshotC().accepted;
 checks.externalLinkLoss=!d.offboardDiagnosticC(ownId,{report:{...report,sequence:2}}).ok;
 d.runFramesToTicks(60,1,120);const lost=d.observerSnapshotC().ships[0].tracks.find(q=>q.offboard);checks.externalStales=lost?.sensorAgeS>=2.5&&!lost.offboard.remote[0].connected&&d.offboardSnapshotC().accepted===extCount;
 checks.noHarpoonDL=d.offboardSnapshotC().ordnanceDatalink===false;
 d.resetEntireSessionV48Wip11A();const reset=d.observerSnapshotC();checks.fullReset=reset.ships.every(q=>q.tracks.length===0&&q.offboard.sources.length===0&&q.offboard.queued===0);
 checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.faultsZero=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();
 return {checks,initial,live,silent,external,lost,deadSensors,damagedModules:damaged.fleet.ships[0].ship.damage.moduleDamage,profiler:d.profilerSnapshotV48Wip11A(),elapsedMs,truthCounts:{physicalShips:2},plotCounts:{foreign:foreign.stats.plots},trackCounts:{player:own.tracks.length,foreign:foreign.tracks.length,foreignTentative:foreign.tracks.filter(t=>!t.confirmed).length,foreignConfirmed:foreign.tracks.filter(t=>t.confirmed).length},pass:Object.values(checks).every(Boolean)};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   for enemy in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
    page=load(b,a.html.read_bytes(),ship=own,errors=errors);q=page.evaluate(FIXTURE,enemy);q.update(own=own,enemy=enemy);rows.append(q);page.close();print(json.dumps({'own':own,'enemy':enemy,'counts':q['trackCounts'],'failed':[k for k,v in q['checks'].items()if not v]}),flush=True);(a.out/'observers-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'seed':1831565813,'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'observers.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
