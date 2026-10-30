"""Actual delayed link, group/manual priority, shared-only readiness and damage."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent/'G'))
from browser_g import launch,load_fleet
FIXTURE=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__,oid=w.activePlayerShipId,aid='SHIP_SCENARIO_ALLY_F',ids=[oid,aid],checks={},trace=[],tick=n=>d.runFramesToTicks(60,1,n),time=()=>d.observerSnapshotC().worldTimeS,snap=id=>d.tacticalSnapshotH1().ships.find(q=>q.entityId===id),ew=id=>d.electronicSnapshotF().ships.find(q=>q.entityId===id).settings,rounds=()=>d.wip119AutonomySnapshot().fireLog.length+d.defenseSnapshotE().ships.find(q=>q.entityId===aid).autonomy.fireLog.length,
 alert=id=>d.electronicReceiverProbeF(id,[{bearing:0,bearingSigmaDeg:1,strength:.9,quality:.9,band:'IJ',type:'MISSILE SEEKER SEARCH',emitterClass:'ACTIVE_SEEKER',measuredAtS:time()}]);
 d.setTerrainDiagBypass(true);tick(120);checks.linkActuallyConnected=d.networkSnapshotG().ships.every(q=>q.peers.some(p=>p.connected));
 for(const id of ids){d.electronicCommandF(id,{emcon:true,auto:false,noiseRequested:false,deceptionRequested:false});d.tacticalCommandH1(id,{resume:true});}
 d.wip119SetMode('AUTO');d.defenseCommandE(aid,{mode:'AUTO'});for(const id of ids)alert(id);tick(12);checks.individualSeekerAlertRadiates=ids.every(id=>!ew(id).emcon&&snap(id).radarOwned);checks.noLocalThreatNoFire=rounds()===0;
 d.networkCommandG(oid,{groupEmcon:'SILENT'});for(let i=0;i<4;i++){for(const id of ids)alert(id);tick(30);}checks.delayedGroupSilentWins=ids.every(id=>ew(id).emcon&&snap(id).groupRadarPriority);checks.groupNoLethalPromotion=rounds()===0;const silent=d.exportOperationalStateV48Wip11A();checks.groupExportsOriginalIndividualBaseline=silent.ship.ew.emcon&&silent.fleet.ships.find(q=>q.entityId===aid).ew.emcon;trace.push({name:'silent',tactical:d.tacticalSnapshotH1(),network:d.networkSnapshotG(),ew:d.electronicSnapshotF()});
 d.networkCommandG(oid,{groupEmcon:'INDIVIDUAL'});for(let i=0;i<4;i++){for(const id of ids)alert(id);tick(30);}checks.individualAIResumesAfterGroup=ids.every(id=>!ew(id).emcon&&!snap(id).groupRadarPriority);checks.individualRequestedBaselineStillSaved=d.exportOperationalStateV48Wip11A().ship.ew.emcon;
 d.networkCommandG(oid,{enabled:false});for(let i=0;i<5;i++){for(const id of ids)alert(id);tick(30);}checks.linkLossKeepsLocalReadiness=ids.every(id=>!ew(id).emcon&&!snap(id).groupRadarPriority);checks.linkLossNoBlindFire=rounds()===0;
 // Reset removes all alert history. Shared THREAT is kept anonymous in G's picture.
 const reset=d.exportOperationalStateV48Wip11A();d.importOperationalStateV48Wip11A(reset);d.setTerrainDiagBypass(true);for(const id of ids){d.networkCommandG(id,{enabled:true});d.electronicCommandF(id,{emcon:true,auto:false,noiseRequested:false,deceptionRequested:false});d.tacticalCommandH1(id,{resume:true});}d.wip119SetMode('AUTO');d.defenseCommandE(aid,{mode:'HOLD'});tick(60);
 const P=Array(36).fill(0);for(const i of [0,7,14])P[i]=64;for(const i of [21,28,35])P[i]=1;const o=w.ships.get(oid).navigation.positionWorld;
 const packet={schema:'AEGIS_LINK_PACKET_G_1',sequence:1000,sentAtS:time(),cooperative:true,group:null,grants:[],reports:[{fileId:91,kind:'TRACK',measuredAtS:time(),stateAtS:time(),stateM:[o.x/.0038+20000,o.y/.0038,30,-250,0,0],covariance:P,domain:'AIR',classification:'ASM',identity:'HOSTILE',assessment:'THREAT',bid:{eligible:false,cost:1000000,weapon:null,inFlight:0}}]};checks.sharedPacketActuallyAccepted=d.networkReceiveProbeG(oid,aid,packet).ok;tick(12);checks.sharedThreatRaisesReadiness=snap(oid).summary.sharedAlerts===1&&!ew(oid).emcon;checks.sharedNoLocalFileOrLethalRelease=snap(oid).priorities.length===0&&rounds()===0;checks.sharedDoesNotInventHostileIdentity=d.networkSnapshotG().ships.find(q=>q.entityId===oid).picture.some(q=>q.sources.some(s=>s.fileId===91)&&q.identity==='UNKNOWN');trace.push({name:'sharedOnly',tactical:d.tacticalSnapshotH1(),network:d.networkSnapshotG()});tick(300);checks.sharedAgesOut=snap(oid).summary.sharedAlerts===0&&ew(oid).emcon;
 // Own equipment reports reduce available FCS and select a degraded posture.
 d.defenseCommandE(aid,{mode:'AUTO'});const r=w.ships.get(aid);for(const mount of r.context.profile.geometry.hardpoints.spg62)r.flooding.setDamage(mount.moduleName,100);tick(180);checks.damageChangesUtility=snap(aid).posture==='DEGRADED'&&snap(aid).summary.availableChannels===0;checks.damageDoesNotGrantFire=rounds()===0;trace.push({name:'damaged',tactical:d.tacticalSnapshotH1()});
 r.crew.offline=()=>true;tick(12);checks.offlineExplicit=snap(aid).summary.offline&&snap(aid).posture==='DEGRADED';checks.offlineNoRelease=rounds()===0;checks.noCoreOrRuntimeFault=window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();return {checks,trace,pass:Object.values(checks).every(Boolean)};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for own,ally in [('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA'),('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA')]:
   page=load_fleet(b,a.html.read_bytes(),own,ally,None,errors=errors);q=page.evaluate(FIXTURE);q.update(own=own,ally=ally);rows.append(q);print(json.dumps({'own':own,'checks':len(q['checks']),'failed':[k for k,v in q['checks'].items()if not v]}),flush=True);page.close()
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'policy.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
