"""Physical Kh-35U, no seeded CMS file: native sensors -> utility -> native defense."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'G'))
from browser_g import launch,load_fleet
FIXTURE=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__,oid=w.activePlayerShipId,aid='SHIP_SCENARIO_ALLY_F',ids=[oid,aid],checks={},trace=[];d.setTerrainDiagBypass(true);d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:13,altM:40,speedMps:300});for(const id of ids){w.ships.get(id).combatSystem.trackManager.tracks.clear();d.networkCommandG(id,{enabled:false});d.electronicCommandF(id,{emcon:false,auto:false,noiseRequested:false,deceptionRequested:false});d.tacticalCommandH1(id,{resume:true});}d.wip119SetMode('AUTO');d.defenseCommandE(aid,{mode:'AUTO'});checks.startsWithZeroTracks=ids.every(id=>w.ships.get(id).combatSystem.trackManager.tracks.size===0);
 for(let i=0;i<70;i++){d.runFramesToTicks(60,1,30);trace.push({time:d.observerSnapshotC().worldTimeS,tactical:d.tacticalSnapshotH1(),own:d.wip119AutonomySnapshot(),ally:d.defenseSnapshotE().ships.find(q=>q.entityId===aid),observers:d.observerSnapshotC(),esm:d.electronicSnapshotF()});}
 for(const id of ids){checks[id+'.actualMeasuredLocalThreat']=trace.some(q=>q.tactical.ships.find(r=>r.entityId===id).summary?.localThreats>0);checks[id+'.utilityPostureFromMeasuredThreat']=trace.some(q=>['DEFEND','SATURATED'].includes(q.tactical.ships.find(r=>r.entityId===id).posture));checks[id+'.noSharedFcs']=trace.every(q=>q.tactical.ships.find(r=>r.entityId===id).summary?.sharedAlerts===0);}
 checks.actualNativeSamRelease=trace.some(q=>q.own.fireLog.length>0||q.ally.autonomy.fireLog.length>0);checks.sensorsRemainIndependent=trace.every(q=>q.tactical.ships.length===2);checks.utilityMemoryBounded=trace.every(q=>q.tactical.ships.every(r=>r.log.length<=64&&r.priorities.length<=96));checks.noFault=window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();return {checks,trace,pass:Object.values(checks).every(Boolean)};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own,ally in [('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA'),('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA')]:
   page=load_fleet(b,a.html.read_bytes(),own,ally,None,errors=errors);q=page.evaluate(FIXTURE);q.update(own=own,ally=ally);rows.append(q);print(json.dumps({'own':own,'checks':len(q['checks']),'failed':[k for k,v in q['checks'].items()if not v]}),flush=True);page.close()
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'fixtureScope':'One physical 40m Kh-35U per hull combination, zero initial CMS files, fixed seed, terrain bypass; no general interception probability claim','cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'natural-h1.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
