function harpoonGateA(trackId=selectedLockId,tubeId=harpoonRuntimeA().selectedTubeId,options={}){
  if(!options.attackH3&&(options.routeProgram||harpoonRuntimeA().routeDraft.pointsM.length))return harpoonRouteGateE(trackId,tubeId,options);
  const r=harpoonRuntimeA(),spec=harpoonTubeSpecA(tubeId),tube=r.tubes.find(t=>t.id===tubeId),tr=tracks.get(Number(trackId)),cfg=HARPOON_PROFILE_A.sim,
    bad=(reason,extra={})=>({ok:false,reason,truthUsed:false,...extra});
  if(!spec||!tube)return bad('MK141_NOT_INSTALLED');
  if(!options.attackH3&&(options.automatic===true||options.mode==='AUTO'||options.mode==='SEMIAUTO'))return bad('MANUAL_SURFACE_AUTHORITY_REQUIRED');
  const authority=options.attackH3?attackAuthorityH3(ACTIVE_SHIP_RUNTIME,tr,options.attackH3):surfaceMissileIdentityPolicyWip13C4(tr?._operatorIdentity,'MANUAL',false);
  if(!tr)return bad('NO_TRACK');if(!authority.ok)return bad(authority.reason);
  if(Number(tr.sensorAge)>cfg.maxTrackAgeS)return bad('SURFACE_TRACK_COAST_EXPIRED');
  const readiness=surfaceMissileTrackReadinessWip13C4(tr,{minRangeKm:cfg.minLaunchRangeKm,maxRangeKm:cfg.maxLaunchRangeKm,includeOffboardAgeF1:true});
  if(!readiness.ok)return bad(readiness.reason);if(readiness.measurementAgeS>cfg.maxTrackAgeS)return bad('SURFACE_TRACK_COAST_EXPIRED');
  const P=tr._kfP,t=Math.max(0,(readiness.rangeKm*1000-cfg.seekerActivationRangeM)/cfg.cruiseSpeedMps),
    sigma=2*Math.sqrt(Math.max(P[0]+t*(P[3]+P[18])+t*t*P[21],P[7]+t*(P[10]+P[25])+t*t*P[28],0)+80**2+(t*t*.04)**2);
  if(!Number.isFinite(sigma)||sigma>cfg.acquisitionBasketM)return bad('INS_PREDICTION_BASKET_INSUFFICIENT',{predictionSigmaM:sigma});
  if(!tube.loaded)return bad('TUBE_EMPTY');if(r.pending&&!options.actualRelease)return bad('RELEASE_PENDING');
  if(r.releaseCooldownS>0&&!options.actualRelease)return bad('LAUNCHER_COOLDOWN');
  if(shipEquipmentOfflineV1())return bad('SHIP_EQUIPMENT_OFFLINE');
  if(getModuleDmg(spec.moduleName)>=75)return bad('MK141_LAUNCHER_DAMAGED');
  const frame=shipGameFrameV1(),muzzle=frame.pointToWorld(spec.muzzle),axis=frame.vectorToWorld(spec.axis);
  if(axis.z<.15||muzzle.z<=maritimeSeaLevelAtSimulationMetersWip13A3(muzzle.x,muzzle.y)+.7)return bad('LAUNCH_GEOMETRY_UNSAFE');
  const result={ok:true,reason:null,trackId:Number(trackId),tubeId,predictionSigmaM:sigma,rangeKm:readiness.rangeKm,
    memory:harpoonMemoryA(tr),muzzleM:muzzle,axis,authority,truthUsed:false};
  if(options.attackH3){const safe=attackFinalGuardH3(ACTIVE_SHIP_RUNTIME,tr,options.attackH3,result);if(!safe.ok)return bad(safe.reason);}
  return result;
}
function harpoonAutoTubeGateD(trackId=selectedLockId,options={}){
  const r=harpoonRuntimeA(),bad=reason=>({ok:false,reason,tubeId:null,truthUsed:false,selectionMode:'AUTO'});
  // Once a door starts opening, pin that exact tube. Release rechecks it independently.
  if(r.pending)return {...bad('RELEASE_PENDING'),tubeId:r.pending.tubeId};
  if(!r.tubes.length)return bad('MK141_NOT_INSTALLED');
  const loaded=r.tubes.filter(t=>t.loaded);if(!loaded.length)return bad('TUBE_EMPTY');
  // Preview tube eligibility during cooldown; the final gate still enforces cooldown.
  // actualRelease bypasses only pending/cooldown, never identity, damage or geometry.
  const gates=loaded.map(t=>harpoonGateA(trackId,t.id,{...options,actualRelease:true})),best=harpoonRankTubesD(gates);
  if(!best)return bad(gates[0].reason);
  return {...harpoonGateA(trackId,best.gate.tubeId,options),tubeId:best.gate.tubeId,
    turnRad:best.turnRad,selectionMode:'AUTO'};
}
function harpoonRouteGateE(trackId,tubeId,options={}){
  const r=harpoonRuntimeA(),spec=harpoonTubeSpecA(tubeId),tube=r.tubes.find(t=>t.id===tubeId),cfg=HARPOON_PROFILE_A.sim,
    bad=reason=>({ok:false,reason,truthUsed:false});
  if(!spec||!tube)return bad('MK141_NOT_INSTALLED');
  if(options.automatic===true||options.mode==='AUTO'||options.mode==='SEMIAUTO')return bad('MANUAL_SURFACE_AUTHORITY_REQUIRED');
  // Manual coordinate/search-area release: no invented radar contact or offboard estimate.
  // A selected protected surface file still blocks release. The onboard seeker has no IFF.
  const tr=tracks.get(Number(trackId));
  if(tr&&tr._surfaceExtentEstimateWip13B8){const a=surfaceMissileIdentityPolicyWip13C4(tr._operatorIdentity,'MANUAL',false);if(!a.ok)return bad(a.reason);}
  if(!tube.loaded)return bad('TUBE_EMPTY');if(r.pending&&!options.actualRelease)return bad('RELEASE_PENDING');
  if(r.releaseCooldownS>0&&!options.actualRelease)return bad('LAUNCHER_COOLDOWN');
  if(shipEquipmentOfflineV1())return bad('SHIP_EQUIPMENT_OFFLINE');if(getModuleDmg(spec.moduleName)>=75)return bad('MK141_LAUNCHER_DAMAGED');
  const frame=shipGameFrameV1(),muzzle=frame.pointToWorld(spec.muzzle),axis=frame.vectorToWorld(spec.axis);
  if(axis.z<.15||muzzle.z<=maritimeSeaLevelAtSimulationMetersWip13A3(muzzle.x,muzzle.y)+.7)return bad('LAUNCH_GEOMETRY_UNSAFE');
  const checked=harpoonRouteProgramE((options.routeProgram??r.routeDraft).pointsM,muzzle),program=options.routeProgram??checked;
  if(!checked)return bad('INVALID_WAYPOINT_ROUTE');if(checked.plannedLengthM>cfg.maxLaunchRangeKm*1000)return bad('ROUTE_EXCEEDS_140KM_BUDGET');
  // Fixed geographic search box, not a long extrapolation of an uncertain moving track.
  const memory=deepFreezeShipProfileV48Wip09({schema:'HARPOON_FROZEN_COORDINATE_CUE_E1',trackId:null,positionM:{...program.searchCenterM},
    velocityMps:{x:0,y:0,z:0},covariance:Array(36).fill(0),stateEpoch:'RELEASE_FIXED_COORDINATE',stateAgeS:0,observationAgeS:0,
    launchStep:simStepCounter,identity:'COORDINATE_SEARCH',truthUsed:false,updatesAfterRelease:false});
  return {ok:true,reason:null,trackId:tr?.trackId??null,tubeId,rangeKm:program.plannedLengthM/1000,memory,routeProgram:program,
    muzzleM:muzzle,axis,authority:{ok:true,mode:'MANUAL_COORDINATE_SEARCH'},truthUsed:false};
}
function surfaceMissileTrackReadinessWip13C4(tr,weaponPolicy){
  const bad=(reason,extra={})=>({ok:false,reason,truthUsed:false,...extra});if(!tr)return bad('NO_TRACK');
  if(!(tr.domain==='SURFACE'||tr.classification==='SURFACE'))return bad('NOT_SURFACE_TRACK');
  if(tr.confirmed!==true||tr.sensorDetected===false||tr.memActive||tr.reacquiring||trackLifecycleState(tr)==='DROP')return bad('SURFACE_TRACK_NOT_CONFIRMED');
  if(!tr._kfP||tr._kfP.length!==36||![tr.x,tr.y].every(Number.isFinite))return bad('SURFACE_TRACK_STATE_UNAVAILABLE');
  if(tr.trackId!=null&&tracks.get(tr.trackId)===tr&&wip121TargetSupportBlocked(tr.trackId,tr))return bad('TRACK_SUPPORT_BLOCKED');
  const contributors=surfaceSensorContributorSnapshotWip13B9(tr),ages=Object.values(contributors).map(q=>Number(q.ageS)).filter(Number.isFinite),measurementAgeS=weaponPolicy?.includeOffboardAgeF1&&tr.observationReportsC?Math.min(...ages,Math.max(0,Number(tr.sensorAge)||0)):(ages.length?Math.min(...ages):Math.max(0,Number(tr.sensorAge)||0)),limitS=SURFACE_MISSILE_ENGAGEMENT_PROFILE_V48_WIP13C4.fireControl.maxMeasurementAgeS;
  if(measurementAgeS>limitS)return bad('SURFACE_TRACK_COAST_EXPIRED',{measurementAgeS,limitS});
  const rangeKm=horizDistKm(aircraft.x(),aircraft.y(),tr.x,tr.y),minRangeKm=Number(weaponPolicy?.minRangeKm)||0,maxRangeKm=Number(weaponPolicy?.maxRangeKm)||Infinity;
  if(rangeKm<minRangeKm||rangeKm>maxRangeKm)return bad('SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE',{rangeKm,minRangeKm,maxRangeKm});
  return {ok:true,reason:null,measurementAgeS,rangeKm,contributors,truthUsed:false};
}
