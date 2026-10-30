"""Actual common RF/terrain propagation at surface and elevated receiver heights."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
FIXTURE=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,checks={};window.__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;cfg.enemyProfileId='CG_52_LATE_TICONDEROGA';cfg.targetShip='NONE';window.__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();
 const save=d.exportOperationalStateV48Wip11A(),q=save.fleet.ships[0].ship.navigation;const own=save.ship.navigation.positionWorld;Object.assign(q.positionWorld,{x:own.x+60000*.0038,y:own.y});q.previousPositionWorld={...q.positionWorld};q.speed=q.targetSpeedKt=q.vx=q.vy=0;d.importOperationalStateV48Wip11A(save);d.setEmcon(false);
 const near=(t)=>Math.hypot(t.x/.0038-own.x/.0038-60000,t.y/.0038-own.y/.0038)<500;
 // Separate terrain from the common Earth horizon for this height comparison.
 d.setTerrainDiagBypass(true);const surface=d.observerPhysicalAuditC({receiverHeightM:35}),airborne=d.observerPhysicalAuditC({receiverHeightM:600});
 checks.surfaceHorizonBlocked=surface.dwell.echoes.filter(near).length===0;checks.elevatedReceiverSees=airborne.dwell.echoes.some(near);
 d.runFramesToTicks(60,8,600);const far=d.observerSnapshotC();checks.noSurfaceTruthTrack=far.ships[0].tracks.every(t=>Math.hypot(t.positionM.x-own.x/.0038-60000,t.positionM.y-own.y/.0038)>500);
 checks.noElevatedProbeInjection=far.ships[0].offboard.accepted===0;
 d.setTerrainDiagBypass(false);const islands=d.battlespaceSnapshot().islandState;
 const terrainSamples=[];for(const isl of islands){if(!isl.points?.length)continue;const xs=isl.points.map(q=>q.x),ys=isl.points.map(q=>q.y),cy=(Math.min(...ys)+Math.max(...ys))*.5,ax=Math.min(...xs)-2000*.0038,bx=Math.max(...xs)+2000*.0038;
   terrainSamples.push({id:isl.id,low:d.terrainLosFactor({x:ax,y:cy,z:15},{x:bx,y:cy,z:12}),high:d.terrainLosFactor({x:ax,y:cy,z:3000},{x:bx,y:cy,z:3000})});}
 checks.realTerrainAvailable=terrainSamples.length>0;checks.islandOcclusion=terrainSamples.some(q=>q.low<.1&&q.high>.9);
 return {checks,surface,airborne,far,terrainSamples,pass:Object.values(checks).every(Boolean)};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[]
 with sync_playwright()as pw:
  b=launch(pw);page=load(b,a.html.read_bytes(),errors=errors);r=page.evaluate(FIXTURE);b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':[r],'errors':errors,'pass':r['pass']and not errors};(a.out/'propagation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(r['checks']));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
