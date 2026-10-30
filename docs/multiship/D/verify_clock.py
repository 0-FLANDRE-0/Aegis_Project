"""Two physical ships: equal full-tick results through the real frame accumulator."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
def physical(v):
 if isinstance(v,dict):return {k:physical(q)for k,q in v.items()if k not in ['performance']}
 if isinstance(v,list):return [physical(q)for q in v]
 return v
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
   reference=None
   for scale in [1,8,16,64]:
    page=load(b,a.html.read_bytes(),ship=own,errors=errors)
    row=page.evaluate('''({enemy,scale})=>{const d=window.__NAVAL_SIM_DIAG__;window.__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{enemyProfileId:enemy,targetShip:'NONE'});window.__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();d.setTerrainDiagBypass(true);d.physicalShipProbeB('SHIP_SCENARIO_ENEMY_A');d.physicalShipCommandB('SHIP_SCENARIO_ENEMY_A',{targetSpeedKt:14,targetRudder:10});d.setEmcon(false);d.observerCommandC('SHIP_SCENARIO_ENEMY_A',{emcon:false});const n=d.physicalFleetSnapshotB().ships[0].navigation;d.weaponFixtureD('SHIP_SCENARIO_ENEMY_A',{action:'track',trackId:51,positionM:{x:n.positionWorld.x/.0038+8000,y:n.positionWorld.y/.0038+1000,z:600},velocityMps:{x:-200,y:0,z:0}});d.weaponFixtureD('SHIP_SCENARIO_ENEMY_A',{action:'identity',trackId:51,identity:'HOSTILE'});const release=d.weaponCommandD('SHIP_SCENARIO_ENEMY_A',{observerShipId:'SHIP_SCENARIO_ENEMY_A',trackId:51,weapon:'SM2'});if(!release.ok)throw Error('CLOCK_OWNER_RELEASE_REJECTED:'+JSON.stringify(release));d.profilerEnableV48Wip11A(true);d.profilerResetV48Wip11A();const start=performance.now(),run=d.runFramesToTicks(60,scale,1536),elapsedMs=performance.now()-start;return {run,elapsedMs,worldTime:window.get3DRenderState().sea.environment.timeS,state:d.exportOperationalStateV48Wip11A(),snapshot:d.physicalFleetSnapshotB(),weapons:d.weaponsSnapshotD(),observers:d.observerSnapshotC(),rng:window.__HARPOON_DIAG_A__.snapshot().rng,profiler:d.profilerSnapshotV48Wip11A(),core:window.__CORE_SELFTEST_FAILURES__,fault:window.__WIP125_DIAG__.wip150RuntimeFault()};}''',{'enemy':enemy,'scale':scale})
    signature=physical({k:row[k]for k in ['state','snapshot','weapons','observers','rng','worldTime']});reference=reference or signature
    row.update(own=own,enemy=enemy,scale=scale,checks={'samePhysicalStateAndRng':signature==reference,'fullTickCount':row['run']['steps']==1536 and row['snapshot']['ships'][0]['clock']['tick']==1536,'sharedWorldClock':abs(row['worldTime']-1536/60)<1e-6,'ownedWeaponsOncePerTick':row['weapons']['ships'][0]['ticks']==1536,'shadowBoundedNoRelease':len(row['weapons']['ships'][0]['shadow'])<=64 and all(not r['executed'] for f in row['weapons']['ships'][0]['shadow']for r in f.get('rows',[])),'observerOncePerTick':all(q['tickCount']==1536 for q in row['observers']['ships']),'noFault':row['core']==[]and row['fault']is None});rows.append(row);page.close();print(json.dumps({'own':own,'scale':scale,'checks':row['checks'],'elapsedMs':row['elapsedMs']}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'ticks':1536,'backend':'headless Chromium CPU, terrain bypass, no hardware FPS claim','cases':rows,'errors':errors,'pass':not errors and all(all(r['checks'].values())for r in rows)};(a.out/'clock.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
