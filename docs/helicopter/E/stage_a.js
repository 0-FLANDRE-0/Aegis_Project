// HELI_D / stage A: physical airborne echoes and independently measured AIR IFF.
// Truth/entity keys stop inside sensor front ends. No aircraft-AI pool registration.
const HELO_SENSOR_SPEC_E=Object.freeze({
  rcsBaseM2:Object.freeze({value:3,source:'SIM_TUNED'}),rcsBroadsideM2:Object.freeze({value:5,source:'SIM_TUNED'}),
  extentRangeM:Object.freeze({value:7.5,source:'SIM_TUNED'}),extentCrossM:Object.freeze({value:4,source:'SIM_TUNED'}),extentVerticalM:Object.freeze({value:2.5,source:'SIM_TUNED'}),dopplerSpreadMps:Object.freeze({value:6,source:'SIM_TUNED'}),
  iffRevisitS:Object.freeze({value:.5,source:'SIM_TUNED'}),iffHoldS:Object.freeze({value:3,source:'SIM_TUNED'}),iffMaxRangeM:Object.freeze({value:150000,source:'SIM_TUNED'}),iffMinLos:Object.freeze({value:.05,source:'SIM_TUNED'}),
  iffRangeSigmaM:Object.freeze({value:20,source:'SIM_TUNED'}),iffBearingSigmaDeg:Object.freeze({value:.18,source:'SIM_TUNED'}),iffElevationSigmaDeg:Object.freeze({value:.2,source:'SIM_TUNED'}),
  iffGateSigma:Object.freeze({value:3,source:'SIM_TUNED'}),iffRangeGateFloorM:Object.freeze({value:80,source:'SIM_TUNED'}),iffRangeGateMaxM:Object.freeze({value:1600,source:'SIM_TUNED'}),iffAngleGateFloorDeg:Object.freeze({value:.6,source:'SIM_TUNED'}),iffElevationGateFloorDeg:Object.freeze({value:1.2,source:'SIM_TUNED'}),iffTrackFreshS:Object.freeze({value:2,source:'SIM_TUNED'})
});
const HELO_SENSOR_VALUES_E=Object.freeze(Object.fromEntries(Object.entries(HELO_SENSOR_SPEC_E).map(([k,v])=>[k,v.value])));
// Stage A placeholders are replaced exactly by the separately verified B/C modules.
function heloRadarSnapshotE(h){return {radar:null};}
function heloHawklinkSnapshotE(h){return {link:{connected:false,reason:'NOT_IMPLEMENTED',recentPlotCount:0}};}
function heloHawklinkResetE(owner){}
function heloPublishRadarPlotsE(h,plots){}
function heloAirborneE(h){return !!h&&h.visible===true&&h.onboard===false&&['DEPART','TRANSIT','ARRIVED_HOVER','FOLLOW_SHIP'].includes(h.state);}
function heloSensorOwnerE(h){return ENGAGEMENT_RUNTIME.ships.get(h.ownerEntityId);}
function heloSensorStateE(h){
  const owner=heloSensorOwnerE(h);if(!owner)throw Error('HELO_SENSOR_OWNER_REQUIRED');
  const map=owner.aviation.heloSensorsE??(owner.aviation.heloSensorsE=new Map());let state=map.get(h.id);
  if(!state){state={iffRepliesReceived:0,lastIffReplyAtS:null};map.set(h.id,state);}return state;
}
function heloSensorSnapshotE(h){
  const state=heloSensorOwnerE(h)?.aviation.heloSensorsE?.get(h.id);
  return {iffOn:h.iffOn!==false,radarOn:h.radarOn===true,iffRepliesReceived:state?.iffRepliesReceived??0,lastIffReplyAtS:state?.lastIffReplyAtS??null,
    ...(typeof heloRadarSnapshotE==='function'?heloRadarSnapshotE(h):{}),...(typeof heloHawklinkSnapshotE==='function'?heloHawklinkSnapshotE(h):{})};
}
function heloSensorResetE(owner){
  if(typeof heloHawklinkResetE==='function')heloHawklinkResetE(owner);
  owner?.aviation?.heloSensorsE?.clear();
  for(const ship of ENGAGEMENT_RUNTIME.ships.values()){
    if(ship.combatSystem.observerC)delete ship.combatSystem.observerC.heloIffE;
    for(const tr of ship.combatSystem.trackManager?.tracks?.values()??[])if(tr.iffF?.source==='AIR_IFF_E'){delete tr.iffF;if(tr.identity==='FRIEND')tr.identity=tr._operatorIdentity??'UNKNOWN';}
  }
}
function heloPhysicalReflectorsE(){
  const C=HELO_SENSOR_VALUES_E,out=[];
  for(const h of ENGAGEMENT_RUNTIME.world.entities.helicopters?.values()??[]){
    if(!heloAirborneE(h))continue;
    const id='HELO:'+h.id;out.push({rfId:id,x:metersToWorld(h.positionM.x),y:metersToWorld(h.positionM.y),z:h.positionM.z,
      vx:mpsToWorldSpeed(h.groundVelocityMps.x),vy:mpsToWorldSpeed(h.groundVelocityMps.y),vz:h.groundVelocityMps.z,
      rcsM2:C.rcsBaseM2+C.rcsBroadsideM2,extentRangeM:C.extentRangeM,extentCrossM:C.extentCrossM,extentVerticalM:C.extentVerticalM,dopplerSpreadMps:C.dopplerSpreadMps,
      _sourceSeed:rfSeedWip13A2(id),_truthObject:h,_physicsKind:'HELICOPTER',_debugSourceKind:'AIR_OBJECT',_debugSourceId:id});
  }return out;
}
function heloCiwsSourcesE(){
  return heloPhysicalReflectorsE().map(ref=>({e:{id:ref.rfId,alive:true,x:ref.x,y:ref.y,z:ref.z,vx:ref.vx,vy:ref.vy,vz:ref.vz},key:ref.rfId,rcs:ref.rcsM2,own:false}));
}
function heloFriendlyIffEvidenceE(tr){
  const q=tr?.iffF;return !!q?.authenticatedFriendly&&(q.source!=='AIR_IFF_E'||Number.isFinite(q.expiresAtS)&&q.expiresAtS>simStepCounter*SIM_FIXED_DT);
}
function heloIffReceiverE(ship){
  const observer=observerC(ship);return observer.heloIffE??(observer.heloIffE={rng:{state:rfSeedWip13A2('HELO_AIR_IFF_E:'+BATTLESPACE_SEED+':'+ship.entityId),spare:null},responses:0,associated:0,expired:0});
}
function heloMeasureIffRepliesE(ship){
  // Authentication is transmitter physics. The receiver gets noisy geometry and
  // an authenticated reply bit, never the helicopter's entity key or truth pose.
  const C=HELO_SENSOR_VALUES_E,out=[];
  if(shipEquipmentOfflineV1(ship)||(ship===ACTIVE_SHIP_RUNTIME?emconActive:observerC(ship).emcon))return out;
  const sources=[...(ENGAGEMENT_RUNTIME.world.entities.helicopters?.values()??[])].filter(h=>heloAirborneE(h)&&h.iffOn!==false&&heloSensorOwnerE(h)?.faction===ship.faction);if(!sources.length)return out;
  const rx=observerMountC(ship,resolveShipProfile(ship.profileId).geometry.hardpoints.bridgeMasterE),state=heloIffReceiverE(ship),now=simStepCounter*SIM_FIXED_DT;
  for(const h of sources){
    const tx={x:metersToWorld(h.positionM.x),y:metersToWorld(h.positionM.y),z:h.positionM.z},dx=worldToMeters(tx.x-rx.x),dy=worldToMeters(tx.y-rx.y),dz=tx.z-rx.z,horizontal=Math.hypot(dx,dy),range=Math.hypot(horizontal,dz);
    if(range>C.iffMaxRangeM||terrainAwareRadarLOS(rx.x,rx.y,rx.z,tx.x,tx.y,tx.z)<C.iffMinLos)continue;
    out.push({bearing:angNorm(Math.atan2(dy,dx)+observerNormalC(state.rng)*deg(C.iffBearingSigmaDeg)),elevationRad:Math.atan2(dz,Math.max(1,horizontal))+observerNormalC(state.rng)*deg(C.iffElevationSigmaDeg),rangeM:Math.max(0,range+observerNormalC(state.rng)*C.iffRangeSigmaM),rangeSigmaM:C.iffRangeSigmaM,bearingSigmaDeg:C.iffBearingSigmaDeg,elevationSigmaDeg:C.iffElevationSigmaDeg,authenticatedFriendly:true,measuredAtS:now});
    state.lastReply={...out[out.length-1]};state.responses++;const sensor=heloSensorStateE(h);sensor.iffRepliesReceived++;sensor.lastIffReplyAtS=now;
  }return out;
}
function heloIffExpireE(ship,now){
  const observer=ship.combatSystem.observerC;if(!observer?.heloIffE)return;
  for(const [id,tr]of observer.tracks){if(tr.iffF?.source!=='AIR_IFF_E'||tr.iffF.expiresAtS>now)continue;
    delete tr.iffF;if(tr.identity==='FRIEND')tr.identity=tr._operatorIdentity??'UNKNOWN';tr.engagementAuthority='WITHHELD';
    const state=ship.combatSystem.observerC?.heloIffE;if(state)state.expired++;
    debugLog(`AIR IFF ${ship.entityId} TRK ${id} 응답 만료 · ${tr.identity}`);
  }
}
function heloIffStepE(dt){
  const C=HELO_SENSOR_VALUES_E,ships=[ACTIVE_SHIP_RUNTIME,...physicalShipsB()],now=simStepCounter*SIM_FIXED_DT;
  for(const ship of ships)heloIffExpireE(ship,now);
  if(simStepCounter%Math.max(1,Math.round(C.iffRevisitS/SIM_FIXED_DT))!==0)return;
  for(const ship of ships){
    const replies=heloMeasureIffRepliesE(ship),tracks=observerC(ship).tracks,rx=observerMountC(ship,resolveShipProfile(ship.profileId).geometry.hardpoints.bridgeMasterE),used=new Set();
    for(const reply of replies){let pick=null;
      for(const [id,tr]of tracks){
        if(used.has(id)||(tr.sensorAge??Infinity)>C.iffTrackFreshS)continue;
        const dx=worldToMeters(tr.x-rx.x),dy=worldToMeters(tr.y-rx.y),dz=(tr.z??0)-rx.z,horizontal=Math.hypot(dx,dy),range=Math.hypot(horizontal,dz),cov=trackCovarianceMetrics(tr),sigma=Math.max(1,cov.posSigmaM??100),altSigma=Math.max(1,cov.altSigmaM??sigma),
          dr=Math.abs(range-reply.rangeM),da=Math.abs(angNorm(Math.atan2(dy,dx)-reply.bearing)),de=Math.abs(Math.atan2(dz,Math.max(1,horizontal))-reply.elevationRad),rg=clamp(C.iffGateSigma*Math.hypot(sigma,reply.rangeSigmaM),C.iffRangeGateFloorM,C.iffRangeGateMaxM),
          ag=Math.max(deg(C.iffAngleGateFloorDeg),Math.atan2(C.iffGateSigma*sigma,Math.max(1,range))+C.iffGateSigma*deg(reply.bearingSigmaDeg)),eg=Math.max(deg(C.iffElevationGateFloorDeg),Math.atan2(C.iffGateSigma*altSigma,Math.max(1,range))+C.iffGateSigma*deg(reply.elevationSigmaDeg));
        if(dr>rg||da>ag||de>eg)continue;const score=(dr/rg)**2+(da/ag)**2+(de/eg)**2;if(!pick||score<pick.score)pick={id,tr,score};
      }
      if(!pick)continue;const old=heloFriendlyIffEvidenceE(pick.tr);
      // Keep the operator's independent identity intact so expiry cannot erase an
      // explicit FRIEND/NEUTRAL/HOSTILE annotation. Protection itself is evidence.
      pick.tr.iffF={authenticatedFriendly:true,measuredAtS:reply.measuredAtS,source:'AIR_IFF_E',expiresAtS:now+C.iffHoldS};pick.tr.identity='FRIEND';pick.tr.engagementAuthority='WITHHELD';used.add(pick.id);heloIffReceiverE(ship).associated++;
      if(!old)debugLog(`AIR IFF ${ship.entityId} TRK ${pick.id} 아군 응답 · WITHHELD`);
    }
  }
}
// DIAGNOSTIC_ONLY. Explicit observed-track probes exercise the real release
// gates; normal UI/render code never invokes this port or changes a track.
function heloIffNativeGuardProbeE(trackId){
  const id=Number(trackId),tr=tracks.get(id);if(!tr||tr.iffF?.source!=='AIR_IFF_E'||!heloFriendlyIffEvidenceE(tr))return {ok:false,reason:'AUTHENTICATED_AIR_IFF_TRACK_REQUIRED'};
  const savedSelected=selectedLockId,savedGate=trackEngagementGateA3,calls=[],fingerprint=()=>JSON.stringify({vls:vlsCells,missiles:missiles.map(q=>q.id),ram:ramMissiles.map(q=>q.id),ciws:ciws.map(q=>({id:q.id,ammo:q.ammo}))}),before=fingerprint();let weapon='SM2',ciwsResults=[],counterfactual=null;
  try{
    selectedLockId=id;trackEngagementGateA3=function(target,opts={}){const result=savedGate(target,opts);calls.push({weapon,trackId:Number(target),automatic:opts.automatic===true,ok:result.ok,reason:result.reason});return result;};
    vlsReleaseStandardB1({automatic:true});weapon='ESSM';vlsReleaseEssmB1({automatic:true});
    const control={...tr,iffF:null};updateTrackOperationalStateA3(control,{mode:'AUTO',assessment:wip118ControlState.assessments.get(id)??null});counterfactual={identity:control.identity,threatStatus:control.threatStatus,authority:control.engagementAuthority,reason:control._a3AuthorityReason};
    for(const mount of ciws){const row=c55CmsRows(mount).find(q=>q.trackId===id);if(!row){ciwsResults.push({mountId:mount.id,matched:false});continue;}
      const rec={id:-910000001,st:{...c55BlankState(),...row.state,localHits:12,valid:true,localAgeS:0,quality:1},confirmed:true,ownFireEvidence:false,protectedIdentity:null};
      c55AssociateCms(rec,c55CmsRows(mount));rec.audit=c55ContactAudit(mount,rec);
      const bank=c55Bank(mount),priorFile=bank.files.get(rec.id),priorSelected=mount.trackingTrackId;
      try{bank.files.set(rec.id,rec);mount.trackingTrackId=rec.id;ciwsResults.push({mountId:mount.id,matched:rec.cmsTrackId===id,protectedIdentity:rec.protectedIdentity,decision:rec.audit.reason,releaseAllowed:c55ReleaseAllowed(mount)});}
      finally{if(priorFile)bank.files.set(rec.id,priorFile);else bank.files.delete(rec.id);mount.trackingTrackId=priorSelected;}
    }
  }finally{selectedLockId=savedSelected;trackEngagementGateA3=savedGate;}
  return {ok:true,calls,counterfactual,ciws:ciwsResults,inventoryAndOrdnanceUnchanged:before===fingerprint(),operatorIdentity:tr._operatorIdentity??'UNKNOWN',identity:tr.identity};
}
function heloSensorAuditSnapshotE(){
  return {schema:'AEGIS_HELO_SENSOR_STAGE_A_DIAG_E1',diagnosticOnly:true,constants:JSON.parse(JSON.stringify(HELO_SENSOR_SPEC_E)),physicalAirborneCount:heloPhysicalReflectorsE().length,ciwsSourceCount:heloCiwsSourcesE().length,aircraftAiPoolCount:targetPool.length,
    ships:[ACTIVE_SHIP_RUNTIME,...physicalShipsB()].map(ship=>{const o=ship.combatSystem.observerC,state=o?.heloIffE;return {ownerEntityId:ship.entityId,iff:state?{responses:state.responses,associated:state.associated,expired:state.expired,lastReply:state.lastReply?{...state.lastReply}:null}:null,
      tracks:[...(o?.tracks?.values()??[])].filter(tr=>tr.iffF?.source==='AIR_IFF_E').map(tr=>({trackId:tr.trackId,iff:{...tr.iffF},operatorIdentity:tr._operatorIdentity??'UNKNOWN',identity:tr.identity}))};})};
}
window.__HELO_SENSOR_STAGE_A_E__=Object.freeze({snapshot:heloSensorAuditSnapshotE,nativeGuardProbe:heloIffNativeGuardProbeE});
