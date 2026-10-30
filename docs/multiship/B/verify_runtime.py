"""Full fixed ticks, real physical damage, restore/reset and ownership guards."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
FIXTURE=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,checks={},cases=[],snap=()=>d.physicalFleetSnapshotB(),fp=()=>JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());
 const originalRng=window.__HARPOON_DIAG_A__.snapshot().rng;
 checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.isolation=d.multiShipIsolationAuditA().pass;
 const depart=(enemy,target='NONE')=>{window.__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{enemyProfileId:enemy,targetShip:target});window.__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();};
 for(const target of ['NONE','HULK'])for(const enemy of [null,'DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']){
  depart(enemy,target);const initial=snap(),ms=d.multiShipSnapshotA(),saved=d.exportOperationalStateV48Wip11A();
  const id=enemy?'SHIP_SCENARIO_ENEMY_A':null,k=target+'.'+enemy;
  checks[k+'.activeCount']=initial.simulated===(enemy?2:1)&&ms.registered===(enemy?2:1);
  checks[k+'.validSave']=d.validateOperationalStateV48Wip11A(saved).ok;
  checks[k+'.departureLock']=window.__AEGIS_DEPLOYMENT_A__.setDraft({...saved.deployment,targetShip:'NONE'}).errors.includes('DEPLOYMENT_LOCKED_AFTER_DEPARTURE');
  if(enemy){
   const ownBefore=JSON.stringify(saved.ship),rng=window.__HARPOON_DIAG_A__.snapshot().rng;
   const impact=d.physicalShipProbeB(id);const after=d.exportOperationalStateV48Wip11A();
   checks[k+'.independentImpact']=impact.accepted&&JSON.stringify(after.ship)===ownBefore&&window.__HARPOON_DIAG_A__.snapshot().rng===rng;
   const openings=after.fleet.ships[0].ship.damage.flooding.openings;checks[k+'.realHullOpenings']=['ENTRY','EXIT'].every(role=>openings.some(o=>o.areaM2>0&&o.z<0&&o.impactRole===role));
   d.runFramesToTicks(60,1,180);const moved=snap().ships[0];
   checks[k+'.actualNavigation']=Math.hypot(moved.navigation.positionWorld.x-initial.ships[0].navigation.positionWorld.x,moved.navigation.positionWorld.y-initial.ships[0].navigation.positionWorld.y)>0;
   checks[k+'.oncePerFixedTick']=moved.clock.tick-initial.ships[0].clock.tick===180;
   checks[k+'.hydraulicFeedback']=moved.flood.waterM3>0&&Math.abs(moved.survival.draftM)>0&&moved.dynamics.waterMassKg>0;
   checks[k+'.profileRoster']=moved.crew.total===(enemy.startsWith('DDG')?310:330);
   checks[k+'.worldWaveOrigin']=Math.abs(moved.wave.shipEarthM.x-moved.navigation.positionWorld.x/0.0038)<3&&Math.abs(moved.wave.shipEarthM.y-moved.navigation.positionWorld.y/0.0038)<3;
   const savedMoving=d.exportOperationalStateV48Wip11A(),validation=d.validateOperationalStateV48Wip11A(savedMoving);
   checks[k+'.damagedSaveValid']=validation.ok;
   d.importOperationalStateV48Wip11A(savedMoving);const restored=snap().ships[0];
   checks[k+'.restorePositionAndWater']=JSON.stringify(restored.navigation.positionWorld)===JSON.stringify(moved.navigation.positionWorld)&&Math.abs(restored.flood.waterM3-moved.flood.waterM3)<1e-8&&restored.clock.tick===moved.clock.tick;
   checks[k+'.restoreOpeningRoles']=JSON.stringify(d.exportOperationalStateV48Wip11A().fleet.ships[0].ship.damage.flooding.openings.map(o=>[o.id,o.impactRole,o.kind,o.areaM2,o.seal01]))===JSON.stringify(savedMoving.fleet.ships[0].ship.damage.flooding.openings.map(o=>[o.id,o.impactRole,o.kind,o.areaM2,o.seal01]));
   d.runFramesToTicks(60,1,1);checks[k+'.resumeTick']=snap().ships[0].clock.tick===moved.clock.tick+1;
   const row=ms.ships.find(r=>r.role==='ENEMY');checks[k+'.correctInventory']=row.vlsCells===(enemy.startsWith('DDG')?96:122)&&row.closeInTypes.join(',')===(enemy.startsWith('DDG')?'GUN,RAM':'GUN,GUN');
   cases.push({own:saved.profileId,enemy,target,initial:initial.ships[0],moved,validation});
  }
  d.resetEntireSessionV48Wip11A();checks[k+'.resetCount']=snap().simulated===(enemy?2:1);
 }
 const valid=d.exportOperationalStateV48Wip11A();
 const bads=[q=>q.fleet.schema='BAD',q=>q.fleet.ships.push(q.fleet.ships[0]),q=>q.fleet.ships[0].profileId='BAD',q=>q.fleet.ships[0].ship.navigation.positionWorld.x='BAD',q=>q.fleet.ships[0].ship.damage.flooding.cells[0].waterM3=-1,q=>q.fleet.ships[0].ship.crew.groups[0].spaceId='BAD',q=>q.fleet.ships[0].ship.rescue.ownerEntityId=valid.shipId,q=>q.fleet.ships[0].clock.tick=-1,q=>q.fleet.ships[0].survival.draftM=1e20,q=>q.fleet.ships=[]];
 for(let i=0;i<bads.length;i++){const bad=structuredClone(valid);bads[i](bad);const before=fp();let rejected=false;try{d.importOperationalStateV48Wip11A(bad);}catch(e){rejected=String(e.message).startsWith('Operational state rejected:');}checks['invalidFleet.'+i]=rejected&&fp()===before;}
 const legacy=structuredClone(valid);delete legacy.fleet;checks.legacyMigration=d.validateOperationalStateV48Wip11A(legacy).ok;
 const id='SHIP_SCENARIO_ENEMY_A',before=fp();checks.foreignPlayerCommandRejected=!d.physicalShipCommandB(valid.shipId,{targetSpeedKt:8}).ok&&fp()===before;
 checks.invalidCommandAtomic=!d.physicalShipCommandB(id,{targetSpeedKt:4,targetRudder:999}).ok&&fp()===before;
 checks.motionCommand=d.physicalShipCommandB(id,{targetSpeedKt:14,targetRudder:15}).ok;
 d.runFramesToTicks(60,1,600);checks.rudderPhysics=snap().ships[0].navigation.rudder>10&&snap().ships[0].navigation.turnRate!==0;
 const live=d.exportOperationalStateV48Wip11A();live.fleet.ships[0].ship.damage.flooding.cells.forEach(c=>c.waterM3=c.capacityM3*.8);live.fleet.ships[0].ship.damage.flooding.pumps.forEach(p=>p.enabled=false);
 const ownBefore=JSON.stringify(live.ship);d.importOperationalStateV48Wip11A(live);d.physicalShipCommandB(id,{abandon:true});
 d.runFramesToTicks(60,8,12000);const evacuation=snap().ships[0];
 checks.physicalSinking=evacuation.survival.lost&&evacuation.crew.mode==='LOST';
 checks.raftControllerActive=evacuation.rescue.rafts.length>0&&evacuation.rescue.rafts.every(q=>q.ownerEntityId===id&&q.personIds.length<=25);
 checks.crewConservation=evacuation.crew.fit+evacuation.crew.injured+evacuation.crew.dead+evacuation.crew.evacuated===evacuation.crew.total;
 const evacuationSave=d.exportOperationalStateV48Wip11A();checks.rescueSaveValid=d.validateOperationalStateV48Wip11A(evacuationSave).ok;
 d.importOperationalStateV48Wip11A(evacuationSave);checks.rescueRestore=JSON.stringify(snap().ships[0].rescue.rafts)===JSON.stringify(evacuation.rescue.rafts);
 depart(null);checks.retireCleansForeignRafts=window.get3DRenderState().lifeRafts.every(q=>q.ownerEntityId!==id)&&snap().simulated===1;
 depart('CG_52_LATE_TICONDEROGA');d.physicalShipCommandB(id,{abandon:true});d.runFramesToTicks(60,8,18000);const healthyRescue=snap().ships[0];checks.fullRosterRafts=healthyRescue.crew.evacuated===330&&healthyRescue.rescue.rafts.length===14&&healthyRescue.rescue.rafts.reduce((n,q)=>n+q.personIds.length,0)===330;
 checks.faultsZero=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();
 return {checks,cases,evacuation,pass:Object.values(checks).every(Boolean)};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright() as pw:
  browser=launch(pw)
  for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   page=load(browser,a.html.read_bytes(),ship=own,errors=errors);result=page.evaluate(FIXTURE);result['own']=own;rows.append(result);page.close();(a.out/'runtime-progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'own':own,'pass':result['pass'],'failed':[k for k,v in result['checks'].items()if not v]}),flush=True)
  browser.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(r['pass']for r in rows)};(a.out/'runtime.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass'] else 1)
if __name__=='__main__':main()
