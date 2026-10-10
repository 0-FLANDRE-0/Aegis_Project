"""Three physical ships: equal full-tick results through the real frame accumulator."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
def physical(v):
 if isinstance(v,dict):return {k:physical(q)for k,q in v.items()if k not in ['performance','lastBuildMs','lastAssessmentMs']}
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
    row=page.evaluate('''({own,enemy,scale})=>{const d=window.__NAVAL_SIM_DIAG__;window.__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{enemyProfileId:enemy,allyProfileId:own,targetShip:'NONE',enemyAircraftEnabled:false});window.__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();d.setTerrainDiagBypass(true);d.physicalShipProbeB('SHIP_SCENARIO_ENEMY_A');d.physicalShipCommandB('SHIP_SCENARIO_ENEMY_A',{targetSpeedKt:14,targetRudder:10});d.setEmcon(false);d.observerCommandC('SHIP_SCENARIO_ENEMY_A',{emcon:false});const n=d.physicalFleetSnapshotB().ships.find(q=>q.entityId==='SHIP_SCENARIO_ENEMY_A').navigation;d.weaponFixtureD('SHIP_SCENARIO_ENEMY_A',{action:'track',trackId:51,positionM:{x:n.positionWorld.x/.0038+18000,y:n.positionWorld.y/.0038,z:15},velocityMps:{x:-250,y:0,z:0}});d.weaponFixtureD('SHIP_SCENARIO_ENEMY_A',{action:'identity',trackId:51,identity:'HOSTILE'});d.profilerEnableV48Wip11A(true);d.profilerResetV48Wip11A();const start=performance.now(),run=d.runFramesToTicks(60,scale,1536),elapsedMs=performance.now()-start;return {run,elapsedMs,worldTime:window.get3DRenderState().sea.environment.timeS,state:d.exportOperationalStateV48Wip11A(),snapshot:d.physicalFleetSnapshotB(),electronic:d.electronicSnapshotF(),weapons:d.weaponsSnapshotD(),defense:d.defenseSnapshotE(),observers:d.observerSnapshotC(),rng:window.__HARPOON_DIAG_A__.snapshot().rng,profiler:d.profilerSnapshotV48Wip11A(),core:window.__CORE_SELFTEST_FAILURES__,fault:window.__WIP125_DIAG__.wip150RuntimeFault()};}''',{'own':own,'enemy':enemy,'scale':scale})
    signature=physical({k:row[k]for k in ['state','snapshot','weapons','observers','defense','rng','worldTime','electronic']});reference=reference or signature
    row.update(own=own,enemy=enemy,scale=scale,checks={'samePhysicalStateAndRng':signature==reference,'fullTickCount':row['run']['steps']==1536 and all(q['clock']['tick']==1536 for q in row['snapshot']['ships']),'sharedWorldClock':abs(row['worldTime']-1536/60)<1e-6,'ownedWeaponsOncePerTick':all(q['ticks']==1536 for q in row['weapons']['ships']),'actualAutoFlight':sum(next(q for q in row['defense']['ships']if q['entityId']=='SHIP_SCENARIO_ENEMY_A')['autonomy']['totalAutoRounds'].values())>0 and len(row['defense']['ships'][0]['autonomy']['fireLog'])<=256,'electronicOncePerTick':all(q['ticks']==1536 for q in row['electronic']['ships']),'threeShips':len(row['electronic']['ships'])==3,'defenseOncePerTick':all(q['ticks']==1536 for q in row['defense']['ships']),'observerOncePerTick':all(q['tickCount']==1536 for q in row['observers']['ships']),'noFault':row['core']==[]and row['fault']is None});rows.append(row);page.close();print(json.dumps({'own':own,'scale':scale,'checks':row['checks'],'elapsedMs':row['elapsedMs']}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'ticks':1536,'backend':'headless Chromium CPU, terrain bypass, no hardware FPS claim','cases':rows,'errors':errors,'pass':not errors and all(all(r['checks'].values())for r in rows)};(a.out/'clock.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
