// Observation-only fire control. Physical entity collections are forbidden here.
function gunB1IsAir(tr){return !!tr&&tr.domain!=='SURFACE'&&tr.classification!=='SURFACE'&&(tr.domain==='AIR'||tr.isASM===true||['ASM','AIR','FIGHTER','BOMBER','DRONE','HELICOPTER'].includes(tr.classification));}
function gunB1AirPolicy(tr,automatic=false){
 if(!tr)return {ok:false,reason:'NO_TRACK'};if(!gunB1IsAir(tr))return {ok:false,reason:'NOT_AIR_TRACK'};
 const identity=normalizeTrackOperatorIdentityA3(tr._operatorIdentity??tr.identity);
 if(['FRIEND','NEUTRAL'].includes(identity)||['FRIEND','NEUTRAL'].includes(tr.identity)||heloFriendlyIffEvidenceE(tr)||networkProtectionG(ACTIVE_SHIP_RUNTIME,tr)||harpoonTrackIdentityC(tr,ACTIVE_SHIP_RUNTIME))return {ok:false,reason:'PROTECTED_IDENTITY'};
 if(wip121TargetSupportBlocked(Number(tr.trackId??tr.id),tr))return {ok:false,reason:'TRACK_SUPPORT_BLOCKED'};
 if(automatic&&tr.classification!=='ASM'&&tr.isASM!==true&&!trackKinematicThreatCue(tr)?.missileLike)return {ok:false,reason:'NOT_MISSILE_LIKE'};
 return {ok:true,identity};
}
function gunB1AirReady(tr){
 const p=gunB1AirPolicy(tr);if(!p.ok)return p;
 if(tr.confirmed!==true||trackLifecycleState(tr)==='DROP')return {ok:false,reason:'AIR_TRACK_NOT_CONFIRMED'};
 const ageS=tr._lastMeasurementStep!=null?Math.max(0,(simStepCounter-tr._lastMeasurementStep)*SIM_FIXED_DT):Math.max(0,Number(tr.sensorAge)||0);
 if(ageS>GUN_B1_SPEC.maxMeasurementAgeS)return {ok:false,reason:'AIR_TRACK_COAST_EXPIRED',ageS};
 if(!tr._kfX||!tr._kfP||tr.z==null)return {ok:false,reason:'AIR_TRACK_3D_STATE_REQUIRED'};
 const x=Number(tr.x),y=Number(tr.y),z=Number(tr.z),u=trackCovarianceMetrics(tr),P=tr._kfP,
 sigmaZ=P&&Number.isFinite(P[14])?Math.sqrt(Math.max(0,P[14])):Number(tr.altitudeSigmaM),sigmaVz=P&&Number.isFinite(P[35])?Math.sqrt(Math.max(0,P[35])):Number(tr.vzSigmaMps),
 positionSigmaM=Math.max(u.posSigmaM,sigmaZ),velocitySigmaMps=Math.max(u.vxSigmaMps,u.vySigmaMps,sigmaVz);
 if(![x,y,z,positionSigmaM,velocitySigmaMps].every(Number.isFinite))return {ok:false,reason:'AIR_TRACK_3D_STATE_REQUIRED'};
 if(positionSigmaM>GUN_B1_SPEC.maxPositionSigmaM)return {ok:false,reason:'POSITION_UNCERTAINTY',positionSigmaM};
 if(velocitySigmaMps>GUN_B1_SPEC.maxVelocitySigmaMps)return {ok:false,reason:'VELOCITY_UNCERTAINTY',velocitySigmaMps};
 return {ok:true,ageS,positionSigmaM,velocitySigmaMps,covariance:u,sigmaZ,sigmaVz,covariance6x6:Array.from(P),source:String(tr.sensorSource??'COMPOSITE_TRACK'),
 targetState:{xM:worldToMeters(x),yM:worldToMeters(y),zM:z,vxMps:worldSpeedToMps(tr.vx??0),vyMps:worldSpeedToMps(tr.vy??0),vzMps:Number(tr.vz??0),covariance6x6:Array.from(P)}};
}
function gunB1AirQuality(tr,solution){
 const r=gunB1AirReady(tr);if(!r.ok)return {...r,status:'FCQ_BLOCKED',firePermitted:false};
 const tof=Number(solution?.timeOfFlightS);if(!Number.isFinite(tof)||tof>GUN_B1_SPEC.maxTofS)return {ok:false,status:'FCQ_BLOCKED',firePermitted:false,reason:'AIR_PREDICTION_TOO_LONG',timeOfFlightS:tof};
 const ready=r.ageS<=GUN_B1_SPEC.readyAgeS&&r.positionSigmaM<=GUN_B1_SPEC.readyPositionSigmaM&&r.velocitySigmaMps<=GUN_B1_SPEC.readyVelocitySigmaMps&&tof<=GUN_B1_SPEC.readyTofS;
 return {...r,status:ready?'FCQ_READY':'FCQ_DEGRADED',firePermitted:true,timeOfFlightS:tof,predictedImpactSigmaM:{cross:Math.hypot(r.positionSigmaM,tof*r.velocitySigmaMps)},truthUsed:false};
}
function gunB1AirReleaseGate(trackId,solution,options={}){
 const tr=tracks.get(Number(trackId)),p=gunB1AirPolicy(tr,options.automatic===true);if(!p.ok)return p;
 if(!solution?.ok||solution.trackId!==Number(trackId)||solution.airDomain!==true)return {ok:false,reason:solution?.reason??'CURRENT_SOLUTION_REQUIRED'};
 const spec=options.module??ACTIVE_SHIP_RUNTIME.weapons.mainGun.spec;
 if(shipEquipmentOfflineV1()||wip13b1GunHardwareHealth(spec)<=.02)return {ok:false,reason:'GUN_OFFLINE'};
 const ageS=Math.max(0,(simStepCounter-Number(solution.computedStep??simStepCounter))*SIM_FIXED_DT);
 if(ageS>spec.fireControl.maxReleaseSolutionAgeS)return {ok:false,reason:'STALE_FIRING_SOLUTION'};
 const quality=gunB1AirQuality(tr,solution);if(!quality.firePermitted)return {ok:false,reason:quality.reason??'AIR_FIRE_CONTROL_QUALITY_INSUFFICIENT',fireControlTrackQuality:quality};
 return {ok:true,reason:null,trackId:Number(trackId),identity:p.identity,fireControlTrackQuality:quality,truthUsed:false};
}
function gunB1SolveAirTrack(spec,hp,state,profile,trackId,ammoId,options={}){
 const tr=tracks.get(Number(trackId)),ready=gunB1AirReady(tr);if(!ready.ok)return {...ready,trackId:Number(trackId),airDomain:true};
 const off=spec.mount.trunnionOffsetM,az=Number(state.bodyAzRad)||0,origin=shipGamePointStateV1({x:hp.x+off.x*Math.cos(az)-off.y*Math.sin(az),y:hp.y+off.x*Math.sin(az)+off.y*Math.cos(az),z:hp.z+off.z});
 const solution=wip13b1SolveTrackState(spec,ammoId,ready.targetState,{originM:{x:origin.xM,y:origin.yM,z:origin.zM},platformVelocityMps:{x:origin.vxMps,y:origin.vyMps,z:origin.vzMps},environment:options.environment??maritimeEnvironmentSnapshotWip13A3(),seedSolution:options.seedSolution??null});
 const out={...solution,trackId:Number(trackId),airDomain:true,truthUsed:false,computedStep:simStepCounter,sensorSource:ready.source,trackCovariance:{...ready.covariance,zSigmaM:ready.sigmaZ,vzSigmaMps:ready.sigmaVz,matrix6x6:ready.covariance6x6}};if(!solution.ok)return out;
 const body=shipGameAimBodyV1(solution.azimuthRad,solution.elevationRad);if(profile.id==='CG_52_LATE_TICONDEROGA')body.az=bunkerGunAzimuth(spec,body.az);
 Object.assign(out,{bodyAzRad:body.az,bodyElevationRad:body.el,targetAltitudeM:ready.targetState.zM});
 if(body.az<spec.mount.trainMinRad||body.az>spec.mount.trainMaxRad||body.el<spec.mount.elevationMinRad||body.el>spec.mount.elevationMaxRad)return {...out,ok:false,reason:'MOUNT_ENVELOPE'};
 const clearance=wip13b1GunClearance(spec,body.az,body.el,Math.min(300,solution.rangeM));if(!clearance.ok)return {...out,ok:false,reason:clearance.reason,clearance};
 if(terrainAwareRadarLOS(metersToWorld(origin.xM),metersToWorld(origin.yM),origin.zM,tr.x,tr.y,ready.targetState.zM)<=.02)return {...out,ok:false,reason:'TERRAIN_MASKED'};
 out.clearance=clearance;out.fireControlTrackQuality=gunB1AirQuality(tr,out);return out;
}
function gunB1ReleaseGate(id,solution,options={}){return solution?.airDomain?gunB1AirReleaseGate(id,solution,options):wip13b1SurfaceGunReleaseGate(id,solution,options);}
