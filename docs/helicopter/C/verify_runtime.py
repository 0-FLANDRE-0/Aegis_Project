"""Native UI, deterministic full fixed ticks, pose ownership and strict import."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet
FIXTURE=r'''()=>{
 const d=__NAVAL_SIM_DIAG__,api=__HELO__,checks={},rows=[],snap=()=>api.snapshot(),ticks=n=>d.stepTicks(n),s0=snap(),[a,b]=s0.aircraft,
  rng=()=>__HARPOON_DIAG_A__.snapshot().rng,seed=rng(),ammo=()=>{const i=d.exportOperationalStateV48Wip11A().ship.inventory;return JSON.stringify({vls:Object.values(i.vls).flat().map(c=>[c.type,c.essmCount,c.destroyed]),closeIn:i.closeIn.map(c=>c.ammo),harpoon:i.harpoon});},inv=ammo(),counts=d.lifecycleStateV48Wip11A().entityCounts;
 const state=()=>JSON.stringify(snap());checks.twoDistinctAirframes=a.id!==b.id&&s0.aircraft.length===2;checks.constantsTagged=Object.values(s0.constants).every(v=>['PUBLIC_SPEC','SIM_TUNED'].includes(v.source));
 checks.recoveryRejected=!api.command(a.id,'RECOVERY').ok;checks.altitudeCommandRejected=!api.command(a.id,'ALTITUDE',{z:100}).ok;
 checks.noInvalidPointMutation=(()=>{const before=state();return !api.command(a.id,'WAYPOINT',{x:NaN,y:0}).ok&&before===state();})();
 checks.launchFirst=api.command(a.id,'LAUNCH').ok;checks.duplicateLaunchRejected=!api.command(a.id,'LAUNCH').ok;checks.launchSecond=api.command(b.id,'LAUNCH').ok;
 checks.queuedCancel=api.command(b.id,'CANCEL_QUEUE').ok&&snap().queue.length===1;api.command(b.id,'LAUNCH');
 const massBefore=d.exportOperationalStateV48Wip11A().ship.liquidLoads,saveQueued=d.exportOperationalStateV48Wip11A();checks.queuedSaveValid=d.validateOperationalStateV48Wip11B(saveQueued).ok;
 const invalid=structuredClone(saveQueued);delete invalid.ship.aviation.aircraft[0].positionM.x;const before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());let threw=false;try{d.importOperationalStateV48Wip11A(invalid);}catch(e){threw=true;}checks.invalidImportZeroWrites=threw&&before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());
 const invalidType=structuredClone(saveQueued);invalidType.ship.aviation.aircraft[0].localM.x=false;checks.booleanPositionRejected=!d.validateOperationalStateV48Wip11B(invalidType).ok;
 let elapsed=0;for(const [n,next]of [[600,'TRAVERSE'],[1200,'SPREAD'],[1800,'START'],[2700,'PRE_LAUNCH_CHECK'],[600,'LIFT_HOVER']]){ticks(n);elapsed+=n;const s=snap();checks['phase'+next]=s.aircraft[0].state===next&&s.aircraft[0].stateTick===0;checks['secondWaiting'+next]=s.aircraft[1].state==='QUEUED';rows.push({ticks:elapsed,first:s.aircraft[0],second:s.aircraft[1]});}
 const h=snap().aircraft[0],localBefore={...h.localM};ticks(299);checks.liftAttachedThroughLastTick=snap().aircraft[0].onboard&&snap().aircraft[0].state==='LIFT_HOVER';checks.liftNearFive=snap().aircraft[0].localM.z-localBefore.z>4.99;
 ticks(1);checks.detachAt7200=snap().aircraft[0].state==='DEPART'&&!snap().aircraft[0].onboard;checks.secondStillWaitsAtDetach=snap().aircraft[1].state==='QUEUED';
 const nav=__AEGIS_ACTIVE_SHIP_RUNTIME__.navigation,render=get3DRenderState().ship,k=Math.abs(nav.positionWorld.x)>1e-6?render.worldXM/nav.positionWorld.x:render.worldYM/nav.positionWorld.y,g=snap().aircraft[0].groundVelocityMps;
 checks.inheritsShipVelocity=Math.abs(g.x-nav.vx*k)<1e-9&&Math.abs(g.y-nav.vy*k)<1e-9;
 const depart=JSON.stringify(snap().aircraft[0].positionM),velocity=JSON.stringify(snap().aircraft[0].airVelocityMps),heading=snap().aircraft[0].headingRad;
 api.command(a.id,'WAYPOINT',{x:snap().aircraft[0].positionM.x+1800,y:snap().aircraft[0].positionM.y+1000});checks.retargetPreservesCurrentPoseAndVelocity=depart===JSON.stringify(snap().aircraft[0].positionM)&&velocity===JSON.stringify(snap().aircraft[0].airVelocityMps)&&heading===snap().aircraft[0].headingRad;
 let secondStart=null;for(let i=0;i<1800;i++){ticks(1);const s=snap();if(s.aircraft[1].state==='HANGAR_OPEN'){secondStart=i+1;break;}}
 checks.secondStartsAfterClearance=secondStart!==null&&secondStart>0;checks.singleDeckOwner=snap().deckOwnerId===b.id;checks.firstAltitudeBounded=snap().aircraft[0].altitudeM<=50;
 ticks(18000);const end=snap();checks.firstArrived=end.aircraft[0].state==='ARRIVED_HOVER';checks.secondArrived=end.aircraft[1].state==='ARRIVED_HOVER';checks.both50MSL=end.aircraft.every(h=>Math.abs(h.altitudeM-50)<1e-7);checks.deckReleased=end.deckOwnerId===null;
 checks.noWeaponsFromHelos=ammo()===inv;checks.noSensorOrEnemyRegistration=d.lifecycleStateV48Wip11A().entityCounts.aircraft===counts.aircraft;
 checks.noFuelConsumption=JSON.stringify(d.exportOperationalStateV48Wip11A().ship.liquidLoads)===JSON.stringify(massBefore);
 const saved=d.exportOperationalStateV48Wip11A();checks.flightSaveValid=d.validateOperationalStateV48Wip11B(saved).ok;const flight=JSON.stringify(saved.ship.aviation);d.importOperationalStateV48Wip11A(saved);checks.flightRestoresExact=flight===JSON.stringify(d.exportOperationalStateV48Wip11A().ship.aviation);
 const badAltitude=structuredClone(saved);badAltitude.ship.aviation.aircraft[0].positionM.z=100;checks.fixedAltitudeSaveRejected=!d.validateOperationalStateV48Wip11B(badAltitude).ok;
 const detached=api.snapshot();detached.aircraft[0].positionM.x=999999;checks.snapshotDetached=snap().aircraft[0].positionM.x!==999999;
 checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;checks.fixedClock60=d.simulationUpdateContractV48Wip11A().fixedTickHz===60;
 return {checks,rows,secondStartTicks:secondStart,final:end,rngBefore:seed,rngAfter:rng()};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True);checks={};errors=[]
 with sync_playwright()as pw:
  b=launch(pw);page=load_fleet(b,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors)
  result=page.evaluate(FIXTURE);checks.update(result['checks']);page.close();b.close()
 out={'pass':all(checks.values())and not errors,'checks':checks,'runtime':result,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest()};(a.out/'runtime.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
