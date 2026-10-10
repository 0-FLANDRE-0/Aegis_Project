"""DIAGNOSTIC_ONLY measured FCS fixtures through actual link, AUTO and VLS release."""
import argparse,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_g import launch,load_fleet
FIXTURE=r'''()=>{
 const d=window.__NAVAL_SIM_DIAG__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__,oid=w.activePlayerShipId,aid='SHIP_SCENARIO_ALLY_F',checks={},cases=[],now=()=>Math.round(d.observerSnapshotC().worldTimeS*60),own=()=>w.ships.get(oid),ally=()=>w.ships.get(aid),tick=n=>d.runFramesToTicks(60,1,n),base=d.exportOperationalStateV48Wip11A();
 const reset=()=>{d.importOperationalStateV48Wip11A(base);d.setTerrainDiagBypass(true);d.setEmcon(false);d.electronicCommandF(aid,{emcon:false,auto:false,noiseRequested:false,deceptionRequested:false});d.wip119SetMode('MANUAL');d.defenseCommandE(aid,{mode:'HOLD'});tick(60);};
 const tracks=r=>r.combatSystem.trackManager.tracks,rounds=id=>id===oid?d.wip119AutonomySnapshot().fireLog.filter(q=>q.trackId===91).length:d.defenseSnapshotE().ships.find(q=>q.entityId===id).autonomy.fireLog.filter(q=>q.trackId===91).length;
 const fixture=()=>{const n=ally().navigation;d.weaponFixtureD(aid,{action:'track',trackId:91,positionM:{x:n.positionWorld.x/.0038+18000,y:n.positionWorld.y/.0038,z:30},velocityMps:{x:-250,y:0,z:0}});d.weaponFixtureD(aid,{action:'identity',trackId:91,identity:'HOSTILE'});const tr=tracks(ally()).get(91),cp=structuredClone(tr);cp.trackId=91;cp._kfX=Float64Array.from(tr._kfX);cp._kfP=Float64Array.from(tr._kfP);tracks(own()).set(91,cp);return tr;};
 const fresh=()=>{for(const r of [own(),ally()]){const tr=tracks(r).get(91);if(tr)Object.assign(tr,{sensorDetected:true,sensorAge:0,confirmed:true,memActive:false,reacquiring:false,_lastMeasurementStep:now(),networkLocalAtS_G:now()/60});}};
 reset();fixture();d.wip119SetMode('AUTO');d.defenseCommandE(aid,{mode:'AUTO'});const trace=[];for(let i=0;i<15;i++){fresh();tick(12);trace.push({step:now(),network:d.networkSnapshotG(),own:d.wip119AutonomySnapshot(),ally:d.defenseSnapshotE().ships.find(q=>q.entityId===aid)});}
 const total=rounds(oid)+rounds(aid),selected=[oid,aid].filter(id=>rounds(id)>0),net=d.networkSnapshotG();checks.correlatedMeasuredLocalFiles=trace.some(q=>q.network.ships.every(s=>s.picture.some(f=>f.localTrackId===91)));
 checks.primaryActuallyReleases=total>0;checks.onlyOneOwnerReleases=selected.length===1;checks.otherOwnerWithheld=net.ships.some(q=>q.stats.withheld>0);checks.nativeRoundsRemainBounded=total<=2;checks.realAssignedLease=trace.some(q=>q.network.ships.some(s=>s.leases.some(l=>l.trackId===91&&selected.includes(l.primary))));cases.push({name:'naturalTransportNativeAuto',selected,total,trace});
 // Isolated consent checks use the same measured file and actual delivered leases.
 const nonPrimary=[oid,aid].find(id=>!selected.includes(id)),gate=id=>d.networkVlsGateProbeG(id,91,{automatic:true});
 if(nonPrimary){checks.assignedPeerWithheld=gate(nonPrimary).reason==='NETWORK_ASSIGNED_PEER';checks.manualNotReassigned=d.networkVlsGateProbeG(nonPrimary,91,{automatic:false}).ok;const r=w.ships.get(nonPrimary),tr=tracks(r).get(91),X=tr._kfX.slice();tr._kfX[0]=r.navigation.positionWorld.x/.0038+1000;tr._kfX[1]=r.navigation.positionWorld.y/.0038;tr._kfX[3]=-250;tr._kfX[4]=0;tr.x=tr._kfX[0]*.0038;tr.y=tr._kfX[1]*.0038;tr.vx=-250*.0038;tr.vy=0;checks.emergencySelfDefense=gate(nonPrimary).reason==='EMERGENCY_SELF_DEFENSE';tr._kfX=X;tr.x=X[0]*.0038;tr.y=X[1]*.0038;tr.vx=X[3]*.0038;tr.vy=X[4]*.0038;
 d.networkCommandG(selected[0],{enabled:false});fresh();tick(180);fresh();checks.linkLossRestoresIndividual=gate(nonPrimary).ok;}
 // A hostile remote label never upgrades an unknown local track.
 reset();fixture();d.wip119SetMode('AUTO');d.defenseCommandE(aid,{mode:'AUTO'});tracks(own()).get(91)._operatorIdentity='UNKNOWN';tracks(own()).get(91).classificationConfidence=.01;tracks(own()).get(91).intentConfidence=0;
 fresh();tick(12);const report=d.networkReportsProbeG(aid).find(q=>q.fileId===91);const packet={schema:'AEGIS_LINK_PACKET_G_1',sequence:1000,sentAtS:now()/60,cooperative:true,reports:report?[report]:[],group:null,grants:[]};d.networkReceiveProbeG(oid,aid,packet);fresh();tick(12);checks.sharedHostileDoesNotAuthorizeUnknown=tracks(own()).get(91).engagementAuthority!=='AUTO_AUTHORIZED';
 // A fresh matching friendly report is restrictive at the real native release port.
 const local=tracks(ally()).get(91);local._operatorIdentity='FRIEND';d.weaponFixtureD(aid,{action:'identity',trackId:91,identity:'FRIEND'});fresh();const fr=d.networkReportsProbeG(aid).find(q=>q.fileId===91);packet.sequence++;packet.sentAtS=now()/60;packet.reports=[fr];checks.friendReportAccepted=d.networkReceiveProbeG(oid,aid,packet).ok;fresh();tick(12);checks.measuredSharedFriendWithholds=d.networkVlsGateProbeG(oid,91,{automatic:true}).reason==='NETWORK_PROTECTED_IDENTITY';
 checks.noTruthAuthority=!d.networkSnapshotG().remoteFireControl;checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.faultZero=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();return {checks,cases,pass:Object.values(checks).every(Boolean)};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright() as pw:
  b=launch(pw)
  for own,ally in [('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA'),('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA')]:
   page=load_fleet(b,a.html.read_bytes(),own,ally,None,errors=errors);q=page.evaluate(FIXTURE);q.update(own=own,ally=ally);rows.append(q);print(json.dumps({'own':own,'failed':[k for k,v in q['checks'].items()if not v]}),flush=True);page.close()
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'cooperation.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
