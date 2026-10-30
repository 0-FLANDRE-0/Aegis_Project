"""Real fixed-step routes, undo, sharp navigation changes, moving station and codec."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet
FIXTURE=r'''()=>{
 const d=__NAVAL_SIM_DIAG__,api=__HELO__,get=()=>api.snapshot(),id=get().aircraft[0].id,checks={},samples=[];
 checks.bothParkedOutboard=get().aircraft.every(h=>Math.abs(h.localM.y)>5.2);checks.parkTailClearance=get().aircraft.every(h=>h.localM.x+8<-32.3);
 const invalidBefore=JSON.stringify(get());checks.invalidRouteNoWrites=!api.command(id,'ROUTE_APPEND',{x:false,y:0}).ok&&invalidBefore===JSON.stringify(get());
 for(const p of [{x:800,y:400},{x:1000,y:500},{x:1200,y:600}])api.command(id,'ROUTE_APPEND',p);
 checks.appendOrder=get().aircraft[0].route.map(p=>p.x).join(',')==='800,1000,1200';const current=JSON.stringify(get().aircraft[0].waypointM);api.command(id,'UNDO_ROUTE');checks.undoLastOnly=get().aircraft[0].route.length===2&&get().aircraft[0].route.at(-1).x===1000&&JSON.stringify(get().aircraft[0].waypointM)===current;
 api.command(id,'CLEAR_ROUTE');for(let i=0;i<32;i++)api.command(id,'ROUTE_APPEND',{x:1000+i,y:1000});const capacity=JSON.stringify(get());checks.routeCapacityNoWrites=!api.command(id,'ROUTE_APPEND',{x:2000,y:2000}).ok&&capacity===JSON.stringify(get());api.command(id,'CLEAR_ROUTE');api.command(id,'LAUNCH');d.stepTicks(600);
 for(let i=0;i<=20;i++){samples.push(get().aircraft[0]);if(i<20)d.stepTicks(60);}checks.deckPointFurtherAft=samples.at(-1).localM.x<-64;checks.smoothYawPresent=samples.some(h=>Math.abs(h.localYawRad)>.12);checks.yawEndsAligned=Math.abs(samples.at(-1).localYawRad)<1e-8;
 d.stepTicks(6600);const h0=get().aircraft[0],p=h0.positionM,pose=()=>JSON.stringify({p:get().aircraft[0].positionM,v:get().aircraft[0].airVelocityMps,h:get().aircraft[0].headingRad});const before=pose();
 api.command(id,'WAYPOINT',{x:p.x+350,y:p.y});api.command(id,'ROUTE_APPEND',{x:p.x+350,y:p.y+350});api.command(id,'ROUTE_APPEND',{x:p.x,y:p.y+350});checks.routeCommandPreservesMotion=before===pose();
 const save=d.exportOperationalStateV48Wip11A();checks.routeSaveValid=d.validateOperationalStateV48Wip11B(save).ok;const bad=structuredClone(save);bad.ship.aviation.aircraft[0].route[0].x=false;checks.badRouteTypeRejected=!d.validateOperationalStateV48Wip11B(bad).ok;
 const nullable=structuredClone(save);nullable.ship.aviation.aircraft[0].route=null;checks.nullRouteRejected=!d.validateOperationalStateV48Wip11B(nullable).ok;
 const fingerprint=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());let threw=false;try{d.importOperationalStateV48Wip11A(bad);}catch(e){threw=true;}checks.invalidRouteImportZeroWrites=threw&&fingerprint===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());
 const progressed=[];for(let i=0;i<24;i++){d.stepTicks(600);progressed.push(get().aircraft[0].routeIndex);}let h=get().aircraft[0];checks.allThreeWaypointsPassed=h.routeIndex===3&&h.state==='ARRIVED_HOVER';checks.finalStopsAtLast=Math.hypot(h.positionM.x-p.x,h.positionM.y-(p.y+350))<2&&h.groundSpeedKt<1;checks.waypointsPassedInOrder=progressed.every((n,i)=>!i||n>=progressed[i-1]);
 d.setShipMotionTest(12,0);const preFollow=pose();api.command(id,'FOLLOW_SHIP');checks.followNoMotionSnap=preFollow===pose();d.stepTicks(12000);h=get().aircraft[0];checks.followStationCaptured=h.state==='FOLLOW_SHIP'&&h.distanceM<3&&Math.abs(h.altitudeM-50)<1e-7;
 const followSave=d.exportOperationalStateV48Wip11A();checks.followSaveValid=d.validateOperationalStateV48Wip11B(followSave).ok;const saved=JSON.stringify(followSave.ship.aviation);d.importOperationalStateV48Wip11A(followSave);checks.followRestoresExact=saved===JSON.stringify(d.exportOperationalStateV48Wip11A().ship.aviation);
 d.setShipRudderTest(8);d.stepTicks(9000);h=get().aircraft[0];checks.followsMovingTurningShip=h.distanceM<8&&Math.abs(h.altitudeM-50)<1e-7;
 const preRetarget=pose();api.command(id,'WAYPOINT',{x:h.positionM.x-2000,y:h.positionM.y+1000});checks.followToRouteContinuous=preRetarget===pose()&&get().aircraft[0].navigationMode==='ROUTE';
 checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;checks.noSensorRegistration=d.lifecycleStateV48Wip11A().entityCounts.aircraft===0;
 d.resetEntireSessionV48Wip11A();const other=get().aircraft[1].id;api.command(other,'LAUNCH');d.stepTicks(600);const samples2=[];for(let i=0;i<=20;i++){samples2.push(get().aircraft[1]);if(i<20)d.stepTicks(60);}
 checks.starboardYawPresent=samples2.some(h=>Math.abs(h.localYawRad)>.12);checks.starboardEndsAligned=Math.abs(samples2.at(-1).localYawRad)<1e-8;
 return {checks,samples,samples2,progressed,followFinal:h,final:get()};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[]
 with sync_playwright()as pw:
  b=launch(pw);page=load_fleet(b,a.html.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);result=page.evaluate(FIXTURE);b.close()
 out={'pass':all(result['checks'].values())and not errors,'checks':result['checks'],'runtime':result,'errors':errors,'htmlSha256':hashlib.sha256(a.html.read_bytes()).hexdigest()};(a.out/'extensions.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(out['checks']),'failed':[k for k,v in out['checks'].items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
