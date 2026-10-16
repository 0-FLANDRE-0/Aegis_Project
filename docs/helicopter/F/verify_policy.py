"""Native fixed-tick Hawklink, transient loss/coast and local-only Harpoon authority."""
import argparse,base64,gzip,hashlib,json,re,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch,load_fleet
FLIGHT=r'''({unitsPerKm})=>{
 const d=__NAVAL_SIM_DIAG__,api=__HELO__,checks={},snap=()=>api.snapshot(),h=()=>snap().aircraft[0],h2=()=>snap().aircraft[1],a=h().id,b=h2().id,sid=d.exportOperationalStateV48Wip11A().shipId,tick=n=>d.stepTicks(n),link=()=>h().sensorsE.link,port=()=>d.offboardSnapshotC();
 d.setTerrainDiagBypass(true);d.setEmcon(true);api.command(a,'FOLLOW_SHIP');api.command(a,'LAUNCH');api.command(b,'FOLLOW_SHIP');api.command(b,'LAUNCH');tick(22000);
 checks.twoAirborne=![h(),h2()].some(x=>x.onboard);checks.bothSourcesOwnedByMother=port().sources.filter(x=>['H1','H2'].includes(x.sourceId)).length===2&&port().sources.every(x=>!['H1','H2'].includes(x.sourceId)||x.connected);checks.emconKeepsConnection=link().connected;
 checks.defaultRadarsOff=!h().radarOn&&!h2().radarOn&&link().transmittedTotal===0;d.createSurfaceFixture({rangeKm:6,bearingDeg:0,speedKt:0,sizeClass:'LARGE'});api.command(a,'SET_RADAR_MODE',{mode:'SHORT'});
 let firstQueued=null,firstDelivered=null;for(let i=0;i<900;i++){tick(1);const q=port();if(firstQueued===null&&q.queued)firstQueued=d.observerSnapshotC().worldTimeS;if(firstDelivered===null&&q.accepted)firstDelivered=d.observerSnapshotC().worldTimeS;}
 checks.realRadarTransmits=link().transmittedTotal>0;checks.latencyActuallyApplied=firstQueued!==null&&firstDelivered!==null&&firstDelivered-firstQueued>=.4-1/60-1e-8;
 checks.emconStillDelivers=port().accepted>0&&link().connected;checks.motherReturnGeometricallyBlanked=link().selfRejectedTotal>0;
 const before=d.observerFacadeC(sid),surfaces=before.tracks.filter(t=>t.source==='OFFBOARD_C'&&t.classification==='SURFACE'),ship=get3DRenderState().ship;
 checks.farMeasuredSurfaceRetained=surfaces.some(t=>Math.hypot(t.positionM.x-ship.worldXM,t.positionM.y-ship.worldYM)>1000);
 checks.noMotherZeroRangeGhost=surfaces.every(t=>Math.hypot(t.positionM.x-ship.worldXM,t.positionM.y-ship.worldYM)>180);
 checks.reportFacadeAnonymous=!JSON.stringify(before).match(/truthRef|rfId|_truthObject|physicalWorld|objectId/);
 checks.noFleetRelayOfHawklinkOnly=surfaces.length>0&&surfaces.every(t=>!d.networkReportsProbeG(sid).some(q=>q.kind==='TRACK'&&q.fileId===t.trackId));
 // Queue a new anonymous fix through H1. Then move ONLY the mother's navigation
 // fixture, preserving real aircraft world positions and the queued transport.
 const n=__AEGIS_ACTIVE_SHIP_RUNTIME__.navigation,original={x:n.positionWorld.x,y:n.positionWorld.y,px:n.previousPositionWorld.x,py:n.previousPositionWorld.y};
 const now=d.observerSnapshotC().worldTimeS,p={schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'H1',sequence:link().sequence+1,measuredAtS:now,positionM:{x:ship.worldXM+12000,y:ship.worldYM,z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.01,missile:.01,background:.01}};
 const queued=d.offboardDiagnosticC(sid,{report:p}),beforeLossAccepted=port().accepted;n.positionWorld.x+=60*unitsPerKm;n.previousPositionWorld.x+=60*unitsPerKm;api.command(a,'SET_RADAR_MODE',{mode:'STBY'});tick(1);
 checks.losLossBeforeDrain=queued.ok&&!link().connected&&link().reason==='LOS'&&port().queued===0&&port().accepted===beforeLossAccepted;
 const disconnectedBefore=link().transmittedTotal;api.command(a,'SET_RADAR_MODE',{mode:'SHORT'});tick(600);checks.noOutageBuffer=port().queued===0&&link().transmittedTotal===disconnectedBefore;
 n.positionWorld.x+=120*unitsPerKm;n.previousPositionWorld.x+=120*unitsPerKm;tick(1);checks.maximumRangeReason=link().reason==='RANGE';
 const coast=d.observerFacadeC(sid),coasted=surfaces.some(t=>coast.tracks.some(q=>q.trackId===t.trackId&&q.sensorAgeS>4));checks.linkLossCoastsExistingFile=coasted;tick(1500);const dropped=d.observerFacadeC(sid);checks.linkLossEventuallyDrops=surfaces.every(t=>!dropped.tracks.some(q=>q.trackId===t.trackId));
 api.command(a,'SET_RADAR_MODE',{mode:'STBY'});n.positionWorld.x=original.x;n.positionWorld.y=original.y;n.previousPositionWorld.x=original.px;n.previousPositionWorld.y=original.py;const acceptedBeforeReconnect=port().accepted;tick(60);checks.reconnectNoReplay=link().connected&&port().queued===0&&port().accepted===acceptedBeforeReconnect;
 const detached=api.snapshot(),oldConnected=link().connected;detached.aircraft[0].sensorsE.link.connected=!oldConnected;checks.linkSnapshotDetached=link().connected===oldConnected;
 const transmitted=link().transmittedTotal;tick(1200);checks.radarOffStopsNewReports=link().transmittedTotal===transmitted;checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;
 return {checks,firstQueued,firstDelivered,link:link(),sources:port().sources,accepted:port().accepted,surfaceCount:surfaces.length,coastingCount:coast.tracks.length,afterDropCount:dropped.tracks.length};
}'''
AUTHORITY=r'''()=>{
 const d=__NAVAL_SIM_DIAG__,har=__HARPOON_DIAG_A__,checks={},sid=d.exportOperationalStateV48Wip11A().shipId,ship=get3DRenderState().ship,tick=n=>d.stepTicks(n),now=()=>d.observerSnapshotC().worldTimeS,facade=()=>d.observerFacadeC(sid),report=(sourceId,sequence,point)=>({schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId,sequence,measuredAtS:now(),positionM:{...point,z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:.01,background:.01}});
 d.setTerrainDiagBypass(true);d.setEmcon(true);har.forgetCombatTracksDiagnostic();d.offboardDiagnosticC(sid,{link:{sourceId:'HELI_PROBE',connected:true,latencyS:.4}});
 for(let i=1;i<=5;i++){d.offboardDiagnosticC(sid,{report:report('HELI_PROBE',i,{x:ship.worldXM+6000,y:ship.worldYM})});tick(60);}
 const pure=facade().tracks.find(t=>t.source==='OFFBOARD_C');checks.pureRemoteConfirmed=!!pure?.confirmed&&pure.classification==='SURFACE'&&pure.offboard?.localAgeS===null;
 d.a3SetOperatorIdentity(pure.trackId,'TRAINING_TARGET');const pureGate=har.gate(pure.trackId);checks.pureRemoteHarpoonBlocked=!pureGate.ok&&pureGate.reason==='LOCAL_SURFACE_OBSERVATION_REQUIRED';checks.nativeSamFcsBlocked=!d.a3EngagementGate(pure.trackId,false).ok;
 const inv=JSON.stringify(har.export()),pending=JSON.stringify(har.snapshot().pending),fire=har.fire(pure.trackId);checks.actualPureRemoteRequestZeroAmmo=fire.ok===false&&JSON.stringify(har.export())===inv&&JSON.stringify(har.snapshot().pending)===pending;
 checks.fleetReleaseBlocked=!d.fleetCommandG(sid,{action:'FIRE',trackId:pure.trackId,weapon:'HARPOON'}).ok;checks.pureRemoteNotRelayed=!d.networkReportsProbeG(sid).some(q=>q.kind==='TRACK'&&q.fileId===pure.trackId);
 // Coordinate/search-area release remains a separate operator-authorized path.
 d.wip13cSetControlDeckTab('ARM');har.routeToggle();const added=har.routeAdd({x:ship.worldXM+10000,y:ship.worldYM+1000}),coordinate=har.gate(null);checks.coordinateSearchPreserved=added.ok&&coordinate.ok&&coordinate.authority?.mode==='MANUAL_COORDINATE_SEARCH';har.routeToggle();
 har.forgetCombatTracksDiagnostic();d.setEmcon(false);d.createSurfaceFixture({rangeKm:6,bearingDeg:0,speedKt:0,sizeClass:'LARGE'});tick(1500);
 const local=facade().tracks.find(t=>t.confirmed&&t.classification==='SURFACE'&&t.source!=='OFFBOARD_C');checks.actualNativeSurfaceFixture=!!local;
 if(local){d.a3SetOperatorIdentity(local.trackId,'TRAINING_TARGET');const localGate=har.gate(local.trackId);checks.nativeGateStillPasses=localGate.ok;d.setEmcon(true);d.offboardDiagnosticC(sid,{link:{sourceId:'MIX',connected:true,latencyS:0}});d.offboardDiagnosticC(sid,{report:report('MIX',1,local.positionM)});tick(1);const mixed=facade().tracks.find(t=>t.trackId===local.trackId),mixedGate=har.gate(local.trackId);checks.remoteMixKeepsLocalStamp=mixed.source==='OFFBOARD_C'&&Number.isFinite(mixed.offboard?.localAgeS)&&mixed.offboard.localAgeS<har.profile().sim.maxTrackAgeS;checks.freshMixedLocalAllowed=mixedGate.ok;
  const rounds=Math.ceil(har.profile().sim.maxTrackAgeS)+2;for(let i=2;i<=rounds+1;i++){d.offboardDiagnosticC(sid,{report:report('MIX',i,local.positionM)});tick(60);}const expired=facade().tracks.find(t=>t.trackId===local.trackId),expiredGate=har.gate(local.trackId);checks.remoteUpdatesDoNotFreshenLocal=expired.sensorAgeS<2&&expired.offboard.localAgeS>har.profile().sim.maxTrackAgeS;checks.expiredMixedLocalBlocked=!expiredGate.ok&&expiredGate.reason==='LOCAL_SURFACE_OBSERVATION_REQUIRED';
 }else for(const k of ['nativeGateStillPasses','remoteMixKeepsLocalStamp','freshMixedLocalAllowed','remoteUpdatesDoNotFreshenLocal','expiredMixedLocalBlocked'])checks[k]=false;
 checks.corePass=__CORE_SELFTEST_FAILURES__.length===0;return {checks,pureGate,coordinate,local:local??null};
}'''
FOREIGN=r'''()=>{
 const d=__NAVAL_SIM_DIAG__,checks={},tick=n=>d.stepTicks(n),sid=d.exportOperationalStateV48Wip11A().shipId,ally=d.observerSnapshotC().ships.find(s=>s.ownerEntityId!==sid).ownerEntityId,facade=()=>d.observerFacadeC(ally),now=()=>d.observerSnapshotC().worldTimeS,cfg=__HARPOON_DIAG_A__.profile().sim;let seq=0;
 d.setTerrainDiagBypass(true);d.setEmcon(true);d.defenseCommandE(ally,{mode:'HOLD'});d.physicalShipCommandB(ally,{targetSpeedKt:0,targetRudder:0});
 const ship=get3DRenderState().ship,expected={x:ship.worldXM+8000,y:ship.worldYM};d.createSurfaceFixture({rangeKm:8,bearingDeg:0,speedKt:0,sizeClass:'LARGE'});tick(1800);
 const local=facade().tracks.find(t=>t.confirmed&&t.classification==='SURFACE'&&t.source!=='OFFBOARD_C'&&Math.hypot(t.positionM.x-expected.x,t.positionM.y-expected.y)<800);checks.actualForeignLocalMeasurement=!!local;
 if(!local)return {checks,facade:facade()};
 const id=local.trackId,report=positionM=>({schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'FOREIGN_MIX',sequence:++seq,measuredAtS:now(),positionM:{...positionM,z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:.01,background:.01}});
 d.observerCommandC(ally,{emcon:true});d.offboardDiagnosticC(ally,{link:{sourceId:'FOREIGN_MIX',connected:true,latencyS:0}});d.offboardDiagnosticC(ally,{report:report(local.positionM)});tick(1);
 let tr=facade().tracks.find(t=>t.trackId===id);checks.foreignMixedInitialLocalStamp=tr?.source==='OFFBOARD_C'&&Number.isFinite(tr.offboard?.localAgeS)&&tr.offboard.localAgeS<cfg.maxTrackAgeS;
 const initialLocalAge=tr.offboard.localAgeS,initialAt=now();for(let i=0;i<Math.ceil(cfg.maxTrackAgeS)+2;i++){d.offboardDiagnosticC(ally,{report:report(local.positionM)});tick(60);}
 tr=facade().tracks.find(t=>t.trackId===id);checks.foreignRemoteNeverFreshensLocal=tr.offboard.localAgeS>=initialLocalAge+now()-initialAt-1e-7&&tr.sensorAgeS<2;
 d.weaponFixtureD(ally,{action:'identity',trackId:id,identity:'TRAINING_TARGET'});const stale=d.weaponCommandD(ally,{weapon:'HARPOON',trackId:id,observerShipId:ally,mode:'MANUAL'});checks.foreignStaleLocalReleaseBlocked=!stale.ok&&stale.reason==='LOCAL_SURFACE_OBSERVATION_REQUIRED';
 d.observerCommandC(ally,{emcon:false});tick(900);tr=facade().tracks.find(t=>t.trackId===id);checks.foreignNativeReacquisitionRefreshesProvenance=!!tr&&tr.source!=='OFFBOARD_C'&&tr.offboard?.localAgeS<2;
 if(tr){const reacquired={...tr.positionM};d.observerCommandC(ally,{emcon:true});d.offboardDiagnosticC(ally,{report:report(reacquired)});tick(1);tr=facade().tracks.find(t=>t.trackId===id);checks.foreignFreshStampSurvivesNextRemote=tr?.source==='OFFBOARD_C'&&tr.offboard?.localAgeS<2;d.weaponFixtureD(ally,{action:'identity',trackId:id,identity:'TRAINING_TARGET'});const fresh=d.weaponCommandD(ally,{weapon:'HARPOON',trackId:id,observerShipId:ally,mode:'MANUAL'});checks.foreignFreshMixedActualRequestAllowed=fresh.ok;return {checks,stale,fresh,track:tr};}
 checks.foreignFreshStampSurvivesNextRemote=false;checks.foreignFreshMixedActualRequestAllowed=false;return {checks,stale,facade:facade()};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();html=raw.decode();main=gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',html,re.S)[1])).decode();scale=float(re.search(r'const WORLD_UNITS_PER_KM_FIXED = ([0-9.]+)',main)[1]);errors=[]
 with sync_playwright()as pw:
  b=launch(pw);page=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',ally=None,enemy=None,errors=errors);flight=page.evaluate(FLIGHT,{'unitsPerKm':scale});page.close();page=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',ally=None,enemy=None,errors=errors);authority=page.evaluate(AUTHORITY);page.close();page=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',ally='CG_52_LATE_TICONDEROGA',enemy=None,errors=errors);foreign=page.evaluate(FOREIGN);b.close()
 checks={**{'flight.'+k:v for k,v in flight['checks'].items()},**{'authority.'+k:v for k,v in authority['checks'].items()},**{'foreign.'+k:v for k,v in foreign['checks'].items()}};out={'pass':all(checks.values())and not errors,'checks':checks,'flight':flight,'authority':authority,'foreign':foreign,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'stage-c.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
