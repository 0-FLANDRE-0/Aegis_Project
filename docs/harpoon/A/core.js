// World ordnance and ship-owned Mk 141 inventory. No combat state is owned by Three.js.
function createHarpoonLauncherRuntimeA(profile){
  return {schema:'MK141_RUNTIME_A1',selectedTubeId:profile.weapons.harpoon?.tubes[0]?.id??null,
    tubes:(profile.weapons.harpoon?.tubes??[]).map(t=>({id:t.id,loaded:true,capOpen01:0})),
    pending:null,releaseCooldownS:0,lastResult:null};
}
function harpoonRuntimeA(){return ACTIVE_SHIP_RUNTIME.weapons.harpoon;}
function harpoonWorldA(){return ENGAGEMENT_RUNTIME.world.entities.antiShipOrdnance;}
function harpoonBoostersA(){return ENGAGEMENT_RUNTIME.world.entities.harpoonBoosters;}
function harpoonCopyA(value){return JSON.parse(JSON.stringify(value));}
function harpoonRandomA(m){m.rng=(Math.imul(1664525,m.rng)+1013904223)>>>0;return m.rng/4294967296;}
function harpoonNoiseA(m){return (harpoonRandomA(m)+harpoonRandomA(m)+harpoonRandomA(m)+harpoonRandomA(m)-2)*Math.sqrt(3);}
function harpoonTubeSpecA(id){return ACTIVE_SHIP_PROFILE.weapons.harpoon?.tubes.find(t=>t.id===id)??null;}
function harpoonMemoryA(tr){
  // Track IDs identify only combat-system tracks, never a physical entity.
  const x=tr._kfX??[worldToMeters(tr.x),worldToMeters(tr.y),tr.z??0,worldSpeedToMps(tr.vx??0),worldSpeedToMps(tr.vy??0),tr.vz??0];
  return deepFreezeShipProfileV48Wip09({schema:'HARPOON_FROZEN_LAUNCH_TRACK_A1',trackId:tr.trackId??null,
    positionM:{x:x[0],y:x[1],z:x[2]},velocityMps:{x:x[3],y:x[4],z:x[5]},covariance:Array.from(tr._kfP),
    observationAgeS:Math.max(0,Number(tr.sensorAge)||0),launchStep:simStepCounter,identity:normalizeTrackOperatorIdentityA3(tr._operatorIdentity),
    truthUsed:false,updatesAfterRelease:false});
}
function harpoonPredictionA(memory,ageS,ownPositionM){
  const p=memory.positionM,v=memory.velocityMps,s=HARPOON_PROFILE_A.sim.cruiseSpeedMps;
  let tgo=Math.hypot(p.x+v.x*ageS-ownPositionM.x,p.y+v.y*ageS-ownPositionM.y)/s;
  for(let i=0;i<4;i++)tgo=Math.hypot(p.x+v.x*(ageS+tgo)-ownPositionM.x,p.y+v.y*(ageS+tgo)-ownPositionM.y)/s;
  return {x:p.x+v.x*(ageS+tgo),y:p.y+v.y*(ageS+tgo),z:HARPOON_PROFILE_A.sim.terminalHeightM,tgoS:tgo};
}
function harpoonGateA(trackId=selectedLockId,tubeId=harpoonRuntimeA().selectedTubeId,options={}){
  const r=harpoonRuntimeA(),spec=harpoonTubeSpecA(tubeId),tube=r.tubes.find(t=>t.id===tubeId),tr=tracks.get(Number(trackId)),cfg=HARPOON_PROFILE_A.sim,
    bad=(reason,extra={})=>({ok:false,reason,truthUsed:false,...extra});
  if(!spec||!tube)return bad('MK141_NOT_INSTALLED');
  if(options.automatic===true||options.mode==='AUTO'||options.mode==='SEMIAUTO')return bad('MANUAL_SURFACE_AUTHORITY_REQUIRED');
  const authority=surfaceMissileIdentityPolicyWip13C4(tr?._operatorIdentity,'MANUAL',false);
  if(!tr)return bad('NO_TRACK');if(!authority.ok)return bad(authority.reason);
  const readiness=surfaceMissileTrackReadinessWip13C4(tr,{minRangeKm:cfg.minLaunchRangeKm,maxRangeKm:cfg.maxLaunchRangeKm});
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
  return {ok:true,reason:null,trackId:Number(trackId),tubeId,predictionSigmaM:sigma,rangeKm:readiness.rangeKm,
    memory:harpoonMemoryA(tr),muzzleM:muzzle,axis,authority,truthUsed:false};
}
function harpoonRequestFireA(trackId=selectedLockId,tubeId=harpoonRuntimeA().selectedTubeId){
  const gate=harpoonGateA(trackId,tubeId),r=harpoonRuntimeA();
  if(!gate.ok){r.lastResult=gate.reason;notify('HARPOON 발사 불가 · '+gate.reason);return gate;}
  r.pending={trackId:gate.trackId,tubeId,remainingS:HARPOON_PROFILE_A.sim.releaseDoorDelayS};
  r.lastResult='DOOR_OPENING';return {ok:true,pending:true,tubeId};
}
function harpoonReleaseA(pending){
  // Recheck authority, track freshness, ammunition, damage and attitude AT release.
  const gate=harpoonGateA(pending.trackId,pending.tubeId,{actualRelease:true}),r=harpoonRuntimeA();
  if(!gate.ok){r.lastResult='CANCELLED:'+gate.reason;notify('HARPOON 발사 취소 · '+gate.reason);return null;}
  const tube=r.tubes.find(t=>t.id===pending.tubeId),cfg=HARPOON_PROFILE_A.sim,axis=gate.axis,
    point=shipGamePointStateV1(harpoonTubeSpecA(pending.tubeId).muzzle),serial=++ENGAGEMENT_RUNTIME.world.antiShipSerial,
    pos={x:gate.muzzleM.x-axis.x*2.315,y:gate.muzzleM.y-axis.y*2.315,z:gate.muzzleM.z-axis.z*2.315},
    vel={x:point.vxMps+axis.x*4,y:point.vyMps+axis.y*4,z:point.vzMps+axis.z*4};
  const m={id:serial,entityClass:'WORLD_ORDNANCE',ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,weaponKey:'HARPOON',label:'RGM-84D',alive:true,ageS:0,phase:'CANISTER',positionM:pos,velocityMps:vel,
    navPositionM:{...pos},navDrift:{x:Math.cos(serial*2.7)*cfg.navDriftMps,y:Math.sin(serial*2.7)*cfg.navDriftMps},
    speedMps:Math.hypot(vel.x,vel.y,vel.z),yawRad:Math.atan2(axis.y,axis.x),pitchRad:Math.atan2(axis.z,Math.hypot(axis.x,axis.y)),
    launchAxis:{...axis},launchPositionM:{...pos},launchMuzzleM:{...gate.muzzleM},
    launchRearM:shipGameFrameV1().pointToWorld(harpoonTubeSpecA(pending.tubeId).rear),tubeId:pending.tubeId,
    carrierVelocityMps:{x:point.vxMps,y:point.vyMps,z:point.vzMps},canisterSpeedMps:4,
    memory:gate.memory,massKg:HARPOON_PROFILE_A.public.launchMassKg,fuelKg:cfg.fuelKg,boosterAttached:true,
    wingDeploy01:0,tailDeploy01:0,tailCommandRad:0,thrustN:0,pathM:0,tubeCleared:false,fuzeArmed:false,
    rng:rfSeedWip13A2('HARPOON:'+BATTLESPACE.seed+':'+serial),seeker:{active:false,mode:'OFF',timerS:0,azRelRad:0,
      lock:null,lockCount:0,missedS:0,lastObservations:[],observations:0},history:[],outcome:null,rcsM2:.06};
  tube.loaded=false;tube.capOpen01=1;r.releaseCooldownS=cfg.releaseIntervalS;r.lastResult='RELEASED:'+serial;
  harpoonWorldA().push(m);harpoonSyncWorldCoordinatesA(m);getShipMassLedgerV32().markWeaponsDirty('MK141_HARPOON_RELEASE');
  notify('HARPOON H'+serial+' 발사 · '+pending.tubeId+' · INS → ARH');return m;
}
function harpoonSyncWorldCoordinatesA(m){
  m.x=metersToWorld(m.positionM.x);m.y=metersToWorld(m.positionM.y);m.z=m.positionM.z;
  m.vx=mpsToWorldSpeed(m.velocityMps.x);m.vy=mpsToWorldSpeed(m.velocityMps.y);m.vz=m.velocityMps.z;
}
// PHYSICAL ECHO SYNTHESIS boundary: private reflector rows terminate here.
// Anonymous range/bearing/Doppler/extent observations contain no source identity.
function harpoonRfObservationsA(m,beamAz){
  const cfg=HARPOON_PROFILE_A.sim,rx={x:m.x,y:m.y,z:m.z},hint=harpoonPredictionA(m.memory,m.ageS,m.navPositionM),focus=Math.hypot(hint.x-m.navPositionM.x,hint.y-m.navPositionM.y),
    field={receiver:rx,band:'IJ',beamAz,beamEl:0,beamHalfAzRad:cfg.seekerBeamHalfRad,beamHalfElRad:Math.PI/9,
      maxRangeKm:cfg.seekerRangeM/1000,minRangeM:100,focusRangeM:focus,rangeResolutionM:35,azimuthCells:3,rangeCells:6},out=[];
  for(const q of physicalRfReflectorRegistryWip13A3({band:'IJ',excludeObject:m,seaField:field})){
    const dx=worldToMeters(q.x-m.x),dy=worldToMeters(q.y-m.y),dz=(q.z??0)-m.z,range=Math.hypot(dx,dy,dz),az=Math.atan2(dy,dx),el=Math.atan2(dz,Math.hypot(dx,dy)),off=angNorm(az-beamAz);
    if(range<25||range>cfg.seekerRangeM||Math.abs(off)>cfg.seekerBeamHalfRad||Math.abs(el)>Math.PI/9)continue;
    const los=terrainAwareRadarLOS(m.x,m.y,m.z,q.x,q.y,q.z??0,1.4);if(los<=.01)continue;
    const rcs=rfReflectorRcsM2Wip13A2(q,'IJ',m.x,m.y,m.z),gain=Math.exp(-2.7726*(off/cfg.seekerBeamHalfRad)**2),
      weather=maritimeRfWeatherPathFactorWip13A3('IJ',range*.002),snr=cfg.seekerReferenceSnr*(rcs/cfg.seekerReferenceRcsM2)*(cfg.seekerReferenceRangeM/range)**4*gain*los*weather;
    if(snr<cfg.seekerMinSnr||harpoonRandomA(m)>clamp(1-Math.exp(-snr/7),.05,.997))continue;
    const rvx=worldSpeedToMps(q.vx??0)-m.velocityMps.x,rvy=worldSpeedToMps(q.vy??0)-m.velocityMps.y,rvz=(q.vz??0)-m.velocityMps.z,
      radial=(rvx*dx+rvy*dy+rvz*dz)/range,noise=Math.sqrt(12/Math.max(3,snr));
    out.push({rangeM:Math.max(1,range+harpoonNoiseA(m)*cfg.seekerRangeSigmaM*noise),
      bearingRad:angNorm(az+harpoonNoiseA(m)*cfg.seekerAzSigmaRad*noise),elevationRad:el+harpoonNoiseA(m)*.002*noise,
      radialMps:radial+harpoonNoiseA(m)*.6*noise,verticalExtentM:Math.max(0,(q.extentVerticalM??0)+harpoonNoiseA(m)*.35),
      rangeExtentM:Math.max(0,(q.extentRangeM??0)+harpoonNoiseA(m)*2),dopplerSpreadMps:q.dopplerSpreadMps??0,snr,noiseScale:noise});
  }
  // Bound retained observations irrespective of terrain/scenario size.
  return out.sort((a,b)=>b.snr-a.snr).slice(0,96);
}
function harpoonSeekerA(m,dt){
  const s=m.seeker,cfg=HARPOON_PROFILE_A.sim,pred=harpoonPredictionA(m.memory,m.ageS,m.navPositionM),
    memoryNow={x:m.memory.positionM.x+m.memory.velocityMps.x*m.ageS,y:m.memory.positionM.y+m.memory.velocityMps.y*m.ageS},
    cue=s.lock?{x:s.lock.x+s.lock.vx*s.missedS,y:s.lock.y+s.lock.vy*s.missedS}:memoryNow,
    rangeToBasket=Math.hypot(pred.x-m.navPositionM.x,pred.y-m.navPositionM.y);
  if(!s.active&&m.ageS>=HARPOON_PROFILE_A.public.boosterBurnS&&rangeToBasket<=cfg.seekerActivationRangeM){s.active=true;s.mode='SEARCH';}
  if(!s.active)return;
  const P=m.memory.covariance,t=m.ageS,cxx=Math.max(0,P[0]+t*(P[3]+P[18])+t*t*P[21]),cyy=Math.max(0,P[7]+t*(P[10]+P[25])+t*t*P[28]),
    cxy=P[1]+t*(P[4]+P[19])+t*t*P[22],lambda=(cxx+cyy+Math.hypot(cxx-cyy,2*cxy))*.5,
    cueGate=Math.min(cfg.seekerSearchBasketM,Math.max(250,3*Math.sqrt(lambda+75**2+(t*t*.04)**2))),
    desired=clamp(angNorm(Math.atan2(cue.y-m.navPositionM.y,cue.x-m.navPositionM.x)-m.yawRad),-cfg.seekerGimbalRad,cfg.seekerGimbalRad),
    scan=s.lock?0:Math.sin(m.ageS*1.8)*Math.min(.25,Math.atan2(cueGate,Math.max(1000,rangeToBasket))),
    command=clamp(desired+scan,-cfg.seekerGimbalRad,cfg.seekerGimbalRad);
  s.azRelRad+=clamp(command-s.azRelRad,-1.8*dt,1.8*dt);s.timerS+=dt;s.missedS+=dt;
  if(s.timerS+1e-10<cfg.seekerPeriodS)return;s.timerS-=cfg.seekerPeriodS;
  const obs=harpoonRfObservationsA(m,m.yawRad+s.azRelRad),gate=s.lock?cfg.seekerTrackGateM+12*s.missedS:cueGate,
    reference=s.lock?{x:s.lock.x+s.lock.vx*s.missedS,y:s.lock.y+s.lock.vy*s.missedS}:memoryNow,candidates=[];
  s.lastObservations=obs;s.observations+=obs.length;
  for(const o of obs){
    // Surface evidence is measured vertical extent/Doppler, never a truth kind.
    if(o.verticalExtentM<1.4||o.dopplerSpreadMps>4)continue;
    const horizontal=o.rangeM*Math.cos(o.elevationRad),x=m.navPositionM.x+horizontal*Math.cos(o.bearingRad),y=m.navPositionM.y+horizontal*Math.sin(o.bearingRad),error=Math.hypot(x-reference.x,y-reference.y);
    if(error>gate)continue;
    const unit={x:Math.cos(o.bearingRad),y:Math.sin(o.bearingRad)},expectedRadial=((s.lock?.vx??m.memory.velocityMps.x)-m.velocityMps.x)*unit.x+((s.lock?.vy??m.memory.velocityMps.y)-m.velocityMps.y)*unit.y;
    if(Math.abs(o.radialMps-expectedRadial)>20+(s.lock?0:10))continue;
    candidates.push({o,x,y,score:error/Math.max(35,gate)-.06*Math.log1p(o.snr)});
  }
  candidates.sort((a,b)=>a.score-b.score);const best=candidates[0];
  if(best){
    if(!s.lock)s.lock={x:best.x,y:best.y,vx:m.memory.velocityMps.x,vy:m.memory.velocityMps.y};
    else{const h=Math.max(cfg.seekerPeriodS,s.missedS),px=s.lock.x+s.lock.vx*h,py=s.lock.y+s.lock.vy*h,ex=best.x-px,ey=best.y-py;
      s.lock.x=px+.42*ex;s.lock.y=py+.42*ey;s.lock.vx=clamp(s.lock.vx+.04*ex/h,-35,35);s.lock.vy=clamp(s.lock.vy+.04*ey/h,-35,35);}
    s.missedS=0;s.lockCount++;s.mode=s.lockCount>=2?'TRACK':'ACQUIRE';m.phase=s.mode==='TRACK'?'TERMINAL_ARH':m.phase;
  }else if(s.missedS>cfg.seekerCoastS){s.lock=null;s.lockCount=0;s.mode='SEARCH';}
  else if(s.lock)s.mode='COAST';
}
function harpoonFinishA(m,reason){
  if(!m.alive)return;m.alive=false;m.outcome=reason;m.endedStep=simStepCounter;
  m.history.push({ageS:m.ageS,event:reason,positionM:{...m.positionM}});
}
function harpoonImpactA(m,contact){
  const entity=contact.entity,frame=surfaceTargetFrameWip13A(entity),tv=surfaceTargetContactVelocityWip13C9(entity,contact.hit.point),
    relative={x:m.velocityMps.x-tv.x,y:m.velocityMps.y-tv.y,z:m.velocityMps.z-tv.z},speed=Math.hypot(relative.x,relative.y,relative.z),dir=wip12aUnit(frame.vectorToBody(relative)),cfg=HARPOON_PROFILE_A.sim,
    spec=wip12aProjectileSpec({id:'RGM84D_BLOCK1C_CONTACT_A1',sourceClass:'PUBLIC_WARHEAD_FILL__SIM_TUNED_TERMINAL',
      caliberM:.343,lengthM:3.84,massKg:m.massKg,penetratorMassKg:123.5,noseShape:'MISSILE_OGIVE',hardness01:.82,shatterResistance01:.45,ductility01:.5,
      payloadType:'HE',explosiveMassKg:97.5,tntEquivalentFactor:cfg.explosiveTntFactor,fuzeType:'LEGACY_IMPACT_DELAY',armMode:'IMPACT',
      minArmTimeS:cfg.fuzeArmS,minArmDistanceM:cfg.fuzeArmDistanceM,delayS:cfg.fuzeDelayS,qualificationProfileId:'ANTI_SHIP_DELAY_8'}),
    geometry=surfaceTargetTerminalGeometryWip13C4(entity,contact.hit.point,dir,.343),eventId='TARGET_HARPOON:'+entity.entityId+':'+m.id,
    state=wip12aMakeProjectileState(spec,{position:geometry.startLocal,direction:dir,bodyAxis:dir,speedMps:speed,massKg:m.massKg,
      flightState:{launchCleared:m.tubeCleared,timeS:m.ageS,distanceM:m.pathM},fuze:{safetyArmed:m.fuzeArmed,armed:m.fuzeArmed}}),
    terminal=wip12aTraceTerminalProjectile(spec,state,geometry.geometry,{impactEventId:eventId,sourceProjectileId:'HARPOON-'+m.id,targetEntityId:entity.entityId,maxPathM:geometry.maxPathM}),
    applied=applyWip12fPacketToSurfaceTargetWip13C4(entity,{id:'HARPOON-'+m.id,weaponKey:'HARPOON',massKg:m.massKg,diameterM:.343,velocityMps:m.velocityMps},terminal,geometry,speed,
      {terminalSpec:spec,weaponKey:'HARPOON',source:'RGM84D_LIVE',weaponLabel:'RGM-84D',projectileDiameterM:.343,impactMassKg:m.massKg,
        velocityMps:m.velocityMps,visualEventType:'SURFACE_TARGET_MISSILE_IMPACT',seed:m.rng,fuzePath:m.fuzeArmed?'CONTACT_DELAY':'UNARMED_KINETIC',integrationMode:'LIVE_HARPOON_CONTACT_DELAY'});
  m.impact={eventId,targetEntityId:entity.entityId,speedMps:speed,armed:m.fuzeArmed,terminationReason:terminal.terminationReason,
    explosiveMassKg:applied.explosiveMassKg,perforated:applied.perforated,throughHull:applied.throughHull,revision:applied.result?.revision};
  harpoonFinishA(m,'SURFACE_CONTACT');notify('HARPOON H'+m.id+' 표적함 명중 · '+Math.round(speed)+'m/s');
}
function harpoonSeparateBoosterA(m){
  const dir={x:Math.cos(m.pitchRad)*Math.cos(m.yawRad),y:Math.cos(m.pitchRad)*Math.sin(m.yawRad),z:Math.sin(m.pitchRad)},offset=-1.92;
  harpoonBoostersA().push({id:'HB-'+m.id,alive:true,ageS:0,massKg:HARPOON_PROFILE_A.sim.boosterDryKg,
    positionM:{x:m.positionM.x+dir.x*offset,y:m.positionM.y+dir.y*offset,z:m.positionM.z+dir.z*offset},
    velocityMps:{x:m.velocityMps.x-dir.x*2,y:m.velocityMps.y-dir.y*2,z:m.velocityMps.z-dir.z*2},
    yawRad:m.yawRad,pitchRad:m.pitchRad,rollRad:0,spinRadS:.7+(m.id%3)*.15});
  m.boosterAttached=false;m.massKg=HARPOON_PROFILE_A.public.bodyMassKg;
  m.history.push({ageS:m.ageS,event:'BOOSTER_SEPARATED',positionM:{...m.positionM},speedMps:m.speedMps});
}
function harpoonFlightStepA(m,dt){
  if(!m.alive)return;const cfg=HARPOON_PROFILE_A.sim,pub=HARPOON_PROFILE_A.public,old={...m.positionM};
  m.ageS+=dt;
  const carrier=m.carrierVelocityMps,elapsed=m.ageS-dt,
    clearance=(m.positionM.x-m.launchPositionM.x-carrier.x*elapsed)*m.launchAxis.x+(m.positionM.y-m.launchPositionM.y-carrier.y*elapsed)*m.launchAxis.y+(m.positionM.z-m.launchPositionM.z-carrier.z*elapsed)*m.launchAxis.z;
  if(!m.tubeCleared&&clearance>=4.63){m.tubeCleared=true;m.clearAgeS=m.ageS;m.phase='BOOST';
    m.yawRad=Math.atan2(m.velocityMps.y,m.velocityMps.x);m.pitchRad=Math.atan2(m.velocityMps.z,Math.hypot(m.velocityMps.x,m.velocityMps.y));
    m.history.push({ageS:m.ageS,event:'CANISTER_CLEARED'});}
  if(m.tubeCleared){m.wingDeploy01=clamp((m.ageS-m.clearAgeS)/cfg.wingDeployS,0,1);m.tailDeploy01=clamp((m.ageS-m.clearAgeS)/cfg.tailDeployS,0,1);}
  if(m.boosterAttached&&m.ageS+1e-9>=pub.boosterBurnS)harpoonSeparateBoosterA(m);
  harpoonSeekerA(m,dt);
  const lock=m.seeker.lock,pred=harpoonPredictionA(m.memory,m.ageS,m.navPositionM),terminal=lock&&m.seeker.mode!=='SEARCH',
    tgo=terminal?Math.hypot(lock.x-m.navPositionM.x,lock.y-m.navPositionM.y)/Math.max(50,m.speedMps):pred.tgoS,
    aim=terminal?{x:lock.x+lock.vx*(tgo+m.seeker.missedS),y:lock.y+lock.vy*(tgo+m.seeker.missedS)}:pred,
    targetYaw=Math.atan2(aim.y-m.navPositionM.y,aim.x-m.navPositionM.x),
    seaMeasured=maritimeSeaLevelAtSimulationMetersWip13A3(m.positionM.x,m.positionM.y)+Math.sin(m.ageS*2.1+m.id)*cfg.altimeterErrorM,
    wantedZ=seaMeasured+(terminal?cfg.terminalHeightM:cfg.cruiseHeightM),
    desiredVz=clamp((wantedZ-m.navPositionM.z)*.35,-40,20),targetPitch=Math.asin(clamp(desiredVz/Math.max(50,m.speedMps),-.32,.25)),
    rho=asmAirDensityKgM3(m.positionM.z),q=.5*rho*m.speedMps*m.speedMps,
    maxNormal=Math.min(cfg.maxNormalG*9.80665,q*cfg.wingAreaM2*cfg.maxCl/Math.max(1,m.massKg))*m.wingDeploy01,
    maxRate=maxNormal/Math.max(20,m.speedMps);
  let yawRate=0,pitchRate=0;
  if(!m.boosterAttached){
    yawRate=clamp(angNorm(targetYaw-m.yawRad)*.9,-maxRate,maxRate);
    pitchRate=clamp((targetPitch-m.pitchRad)*1.2,-maxRate,maxRate);
    m.phase=terminal?'TERMINAL_ARH':(m.seeker.active?'INS_SEARCH':'INS_CRUISE');
  }
  // Point-mass wind-axis dynamics. Lift supplies gravity compensation and bounded
  // turn acceleration; thrust/drag/gravity change speed, never a prescribed speed.
  const pitchForce=pitchRate*m.speedMps+9.80665*Math.cos(m.pitchRad),sideForce=yawRate*m.speedMps*Math.cos(m.pitchRad),
    requiredNormal=Math.hypot(pitchForce,sideForce),forceScale=requiredNormal>maxNormal?maxNormal/Math.max(1e-9,requiredNormal):1,
    netPitchRate=(pitchForce*forceScale-9.80665*Math.cos(m.pitchRad))/Math.max(4,m.speedMps),
    netYawRate=sideForce*forceScale/Math.max(4,m.speedMps*Math.cos(m.pitchRad));
  m.normalAccelerationMps2=requiredNormal*forceScale;
  const induced=m.normalAccelerationMps2/9.80665,
    drag=q*cfg.dragAreaM2*(cfg.referenceCd+.015*induced*induced),
    throttle=m.boosterAttached?1:clamp((drag+m.massKg*(cfg.cruiseSpeedMps-m.speedMps)*.22)/pub.jetMaxThrustN,.1,1);
  m.thrustN=m.boosterAttached?pub.boosterThrustN:(m.fuelKg>0?pub.jetMaxThrustN*throttle:0);
  if(m.boosterAttached)m.massKg=pub.launchMassKg-cfg.boostPropellantKg*Math.min(1,m.ageS/pub.boosterBurnS);
  else{m.fuelKg=Math.max(0,m.fuelKg-cfg.fuelFlowKgS*dt);m.massKg=pub.bodyMassKg-cfg.fuelKg+m.fuelKg;}
  const accel=(m.thrustN-drag)/Math.max(1,m.massKg)-9.80665*Math.sin(m.pitchRad);
  m.speedMps=Math.max(0,m.speedMps+accel*dt);
  if(m.tubeCleared){m.yawRad=angNorm(m.yawRad+netYawRate*dt);m.pitchRad=clamp(m.pitchRad+netPitchRate*dt,-1.45,1.45);
    m.velocityMps={x:m.speedMps*Math.cos(m.pitchRad)*Math.cos(m.yawRad),y:m.speedMps*Math.cos(m.pitchRad)*Math.sin(m.yawRad),z:m.speedMps*Math.sin(m.pitchRad)};
  }else{
    // Canister reaction constrains relative motion to its registered axis. The
    // released round retains the muzzle's ship translation/angular velocity.
    m.canisterSpeedMps=Math.max(0,m.canisterSpeedMps+accel*dt);
    m.velocityMps={x:carrier.x+m.launchAxis.x*m.canisterSpeedMps,y:carrier.y+m.launchAxis.y*m.canisterSpeedMps,z:carrier.z+m.launchAxis.z*m.canisterSpeedMps};
    m.speedMps=Math.hypot(m.velocityMps.x,m.velocityMps.y,m.velocityMps.z);
  }
  m.tailCommandRad=clamp(netYawRate*2,-.18,.18);
  m.positionM={x:old.x+m.velocityMps.x*dt,y:old.y+m.velocityMps.y*dt,z:old.z+m.velocityMps.z*dt};
  m.navPositionM.x+=(m.velocityMps.x+m.navDrift.x)*dt;m.navPositionM.y+=(m.velocityMps.y+m.navDrift.y)*dt;
  m.navPositionM.z=m.positionM.z+Math.sin(m.ageS*.7+m.id)*cfg.altimeterErrorM;
  m.pathM+=m.speedMps*dt;m.fuzeArmed=m.tubeCleared&&m.ageS>=cfg.fuzeArmS&&m.pathM>=cfg.fuzeArmDistanceM;harpoonSyncWorldCoordinatesA(m);
  const contact=surfaceTargetFirstAsmContactWip13A({x:metersToWorld(old.x),y:metersToWorld(old.y),z:old.z},{x:m.x,y:m.y,z:m.z});
  if(contact){harpoonImpactA(m,contact);return;}
  if(m.z<=terrainElevationAt(m.x,m.y)&&terrainElevationAt(m.x,m.y)>0){harpoonFinishA(m,'TERRAIN_IMPACT');return;}
  if(m.z<=maritimeSeaLevelAtSimulationMetersWip13A3(m.positionM.x,m.positionM.y)){harpoonFinishA(m,'SEA_IMPACT');return;}
  if(m.fuelKg<=0){if(m.fuelOutAgeS==null){m.fuelOutAgeS=m.ageS;m.history.push({ageS:m.ageS,event:'JET_FUEL_EXHAUSTED'});}m.phase='ENGINE_OUT_GLIDE';}
  if(m.ageS>=cfg.maxLifeS){harpoonFinishA(m,'FLIGHT_ENDURANCE_EXPIRED');return;}
  if(m.ageS>15&&m.speedMps<70)harpoonFinishA(m,'INSUFFICIENT_AIRSPEED');
  if([m.positionM.x,m.positionM.y,m.positionM.z,m.speedMps,m.massKg,m.yawRad,m.pitchRad].some(v=>!Number.isFinite(v)))throw Error('HARPOON_NONFINITE_PHYSICS');
}
function harpoonStepA(dt){
  const r=harpoonRuntimeA();if(!r.tubes.length)return;
  r.releaseCooldownS=Math.max(0,r.releaseCooldownS-dt);
  for(const tube of r.tubes){const opening=!tube.loaded||r.pending?.tubeId===tube.id;tube.capOpen01=clamp(tube.capOpen01+(opening?1:-1)*dt/HARPOON_PROFILE_A.sim.releaseDoorDelayS,0,1);}
  if(r.pending){r.pending.remainingS-=dt;if(r.pending.remainingS<=1e-9){const request=r.pending;r.pending=null;harpoonReleaseA(request);}}
  for(const m of harpoonWorldA())harpoonFlightStepA(m,dt);
  for(const b of harpoonBoostersA())if(b.alive){
    b.ageS+=dt;const v=b.velocityMps,speed=Math.hypot(v.x,v.y,v.z),drag=.5*1.225*.035*speed/Math.max(1,b.massKg);
    v.x-=v.x*drag*dt;v.y-=v.y*drag*dt;v.z-=v.z*drag*dt+9.80665*dt;
    b.positionM.x+=v.x*dt;b.positionM.y+=v.y*dt;b.positionM.z+=v.z*dt;b.pitchRad+=b.spinRadS*dt;b.rollRad+=b.spinRadS*.6*dt;
    if(b.positionM.z<=Math.max(maritimeSeaLevelAtSimulationMetersWip13A3(b.positionM.x,b.positionM.y),terrainElevationAt(metersToWorld(b.positionM.x),metersToWorld(b.positionM.y)))||b.ageS>45)b.alive=false;
  }
  // Fixed caps: retain only recent outcome diagnostics, never an unbounded history.
  while(harpoonWorldA().length>32&&!harpoonWorldA()[0].alive)harpoonWorldA().shift();
  for(let i=harpoonBoostersA().length-1;i>=0;i--)if(!harpoonBoostersA()[i].alive)harpoonBoostersA().splice(i,1);
}
function harpoonResetA(full=false){
  harpoonWorldA().length=0;harpoonBoostersA().length=0;const r=harpoonRuntimeA();r.pending=null;r.releaseCooldownS=0;r.lastResult=null;
  if(full){r.tubes.forEach(t=>{t.loaded=true;t.capOpen01=0;});ENGAGEMENT_RUNTIME.world.antiShipSerial=0;}
}
function harpoonExportA(){return {schema:'MK141_INVENTORY_A1',selectedTubeId:harpoonRuntimeA().selectedTubeId,tubes:harpoonRuntimeA().tubes.map(t=>({id:t.id,loaded:t.loaded}))};}
function harpoonValidateA(inventory,errors,expected=harpoonRuntimeA().tubes){
  const value=inventory.harpoon;
  if(!value){if(expected.length)errors.push('HARPOON_INVENTORY_REQUIRED');return;}
  if(value.schema!=='MK141_INVENTORY_A1'||!Array.isArray(value.tubes)||value.tubes.length!==expected.length){errors.push('HARPOON_INVENTORY_SCHEMA_OR_LENGTH');return;}
  const ids=new Set();for(const t of value.tubes){if(!expected.some(e=>e.id===t?.id)||ids.has(t?.id)||typeof t?.loaded!=='boolean')errors.push('HARPOON_TUBE_ID_OR_STATE');ids.add(t?.id);}
  if(expected.length&&!expected.some(t=>t.id===value.selectedTubeId)||!expected.length&&value.selectedTubeId!=null)errors.push('HARPOON_SELECTED_TUBE');
}
function harpoonRestoreA(value){const r=harpoonRuntimeA();r.selectedTubeId=value?.selectedTubeId??r.selectedTubeId;for(const t of r.tubes){t.loaded=value.tubes.find(e=>e.id===t.id).loaded;t.capOpen01=t.loaded?0:1;}}
function harpoonRenderStatesA(){return harpoonWorldA().filter(m=>m.alive).map(m=>({id:'HARPOON-'+m.id,label:'RGM-84D',displayName:'RGM-84D Harpoon Block 1C',kind:'HARPOON',dead:false,xM:m.positionM.x,yM:m.positionM.z,zM:m.positionM.y,
  worldXM:m.positionM.x,worldYM:m.positionM.y,
  headingRad:m.yawRad,pitchRad:m.pitchRad,lifeS:m.ageS,phase:m.phase,speedMps:m.speedMps,boosterAttached:m.boosterAttached,wingDeploy01:m.wingDeploy01,
  tailDeploy01:m.tailDeploy01,tailCommandRad:m.tailCommandRad,thrustN:m.thrustN,tubeCleared:m.tubeCleared,tubeId:m.tubeId,
  seekerMode:m.seeker.mode,motorActive:m.thrustN>20,guidanceState:m.phase,guidanceAuthority:m.seeker.lock?'ARH':'INS',launchMuzzleM:{...m.launchMuzzleM},launchRearM:{...m.launchRearM},
  seeker:{active:m.seeker.active,type:'ARH',mode:m.seeker.mode,locked:m.seeker.mode==='TRACK',quality:clamp(m.seeker.lockCount/8,0,1),
    azRelRad:m.yawRad+m.seeker.azRelRad,elRad:0,fovFullDeg:16,fovAzFullDeg:16,fovElFullDeg:40,
    outerFovAzFullDeg:90,outerFovElFullDeg:90,outerAzRelRad:m.yawRad,outerElRad:m.pitchRad,
    rangeM:HARPOON_PROFILE_A.sim.seekerRangeM,displayRangeCapM:2500,visualClass:'ARH_RF_BEAM',scanPattern:m.seeker.lock?'TRACK':'CUE_SWEEP',
    scanOffsetAzDeg:m.seeker.azRelRad*180/Math.PI,gimbalAzDeg:m.seeker.azRelRad*180/Math.PI}}));}
function harpoonBoosterRenderStatesA(){return harpoonBoostersA().filter(b=>b.alive).map(b=>({id:b.id,xM:b.positionM.x,yM:b.positionM.z,zM:b.positionM.y,
  headingRad:b.yawRad,pitchRad:b.pitchRad,rollRad:b.rollRad,lifeS:b.ageS}));}
function harpoonUpdateUIA(){
  const host=document.getElementById('harpoonControlsA');if(!host)return;const r=harpoonRuntimeA();host.hidden=!r.tubes.length;if(!r.tubes.length)return;
  const select=document.getElementById('harpoonTubeA');for(const o of select.options){const t=r.tubes.find(t=>t.id===o.value);o.textContent=o.value.replace('MK141-','')+' '+(t?.loaded?'●':'○');}
  select.value=r.selectedTubeId;const gate=harpoonGateA(),button=document.getElementById('harpoonFireA');button.disabled=!gate.ok;
  button.textContent='HARPOON '+r.tubes.filter(t=>t.loaded).length+'/8'+(r.pending?' · OPENING':' · FIRE');
  const live=harpoonWorldA().filter(m=>m.alive),status=document.getElementById('harpoonStatusA');
  status.textContent=live.length?live.map(m=>'H'+m.id+' '+m.phase+' '+Math.round(m.speedMps)+'m/s').join(' · '):(gate.ok?'RGM-84D · INS → ARH · READY':gate.reason);
  status.title='RGM-84D Block 1C · 공개 제원 / SIM-TUNED 비행·탐색기 · Mk 141 전용';
}
function harpoonBindUIA(){
  const select=document.getElementById('harpoonTubeA');if(!select)return;
  for(const t of harpoonRuntimeA().tubes){const o=document.createElement('option');o.value=t.id;select.appendChild(o);}
  select.addEventListener('change',()=>{harpoonRuntimeA().selectedTubeId=select.value;harpoonUpdateUIA();});
  bindPress(document.getElementById('harpoonFireA'),()=>{harpoonRequestFireA();harpoonUpdateUIA();});harpoonUpdateUIA();
}
function harpoonDrawCicA(ctx,sym){
  ctx.save();ctx.strokeStyle='#ffd08a';ctx.fillStyle='#ffd08a';ctx.lineWidth=1.5*sym;ctx.font=`${9*sym}px monospace`;
  for(const m of harpoonWorldA())if(m.alive&&m.tubeCleared){
    const a=m.yawRad;ctx.beginPath();ctx.moveTo(m.x+Math.cos(a)*7*sym,m.y+Math.sin(a)*7*sym);ctx.lineTo(m.x+Math.cos(a+2.5)*5*sym,m.y+Math.sin(a+2.5)*5*sym);ctx.lineTo(m.x+Math.cos(a-2.5)*5*sym,m.y+Math.sin(a-2.5)*5*sym);ctx.closePath();ctx.stroke();ctx.fillText('H'+m.id+' '+(m.seeker.lock?'ARH':'INS'),m.x+9*sym,m.y-5*sym);
    if(m.seeker.active){const radius=metersToWorld(2500),center=a+m.seeker.azRelRad,half=HARPOON_PROFILE_A.sim.seekerBeamHalfRad;ctx.globalAlpha=.20;ctx.beginPath();ctx.moveTo(m.x,m.y);ctx.arc(m.x,m.y,radius,center-half,center+half);ctx.closePath();ctx.fill();ctx.globalAlpha=1;}
  }ctx.restore();
}
function harpoonDiagnosticsA(){
  return {profile:()=>harpoonCopyA(HARPOON_PROFILE_A),installation:()=>harpoonCopyA(ACTIVE_SHIP_PROFILE.weapons.harpoon??null),
    snapshot:()=>({inventory:harpoonExportA(),pending:harpoonCopyA(harpoonRuntimeA().pending),missiles:harpoonCopyA(harpoonWorldA()),boosters:harpoonCopyA(harpoonBoostersA()),rng:SIM_RNG_STATE}),
    gate:(id,tube,options)=>harpoonGateA(id,tube,options),fire:(id,tube)=>harpoonRequestFireA(id,tube),
    select:(id)=>{selectedLockId=Number(id);harpoonUpdateUIA();},
    focusedTicks:(n=1)=>{for(let i=0;i<n;i++){updateMaritimeEnvironmentWip13A3(SIM_FIXED_DT);updateSurfaceContacts(SIM_FIXED_DT);harpoonStepA(SIM_FIXED_DT);simStepCounter++;}return harpoonWorldA().map(m=>({id:m.id,alive:m.alive,phase:m.phase,outcome:m.outcome,ageS:m.ageS}));},
    fixedTicks:(n=1)=>{for(let i=0;i<n;i++)simulateFixedTick(SIM_FIXED_DT);return harpoonRenderStatesA();},
    reset:(full=false)=>harpoonResetA(full),export:harpoonExportA,refreshUi:harpoonUpdateUIA,
    forgetCombatTracksDiagnostic:()=>{tracks.clear();selectedLockId=null;return {diagnosticOnly:true,missilesUnaffected:harpoonWorldA().length};},
    predict:(memory,age,pos)=>harpoonPredictionA(memory,age,pos),coreAudit:harpoonCoreAuditA};
}
function harpoonCoreAuditA(){
  const profile=HARPOON_PROFILE_A,installation=CG_52_LATE_TICONDEROGA_PROFILE.weapons.harpoon,
    detached=createHarpoonLauncherRuntimeA(CG_52_LATE_TICONDEROGA_PROFILE),
    tr={trackId:-84,_operatorIdentity:'TRAINING_TARGET',_kfX:new Float64Array([10000,500,8,10,2,0]),_kfP:new Float64Array(36)},
    memory=harpoonMemoryA(tr),before=JSON.stringify(memory),prediction=harpoonPredictionA(memory,20,{x:0,y:0,z:0}),
    valid={schema:'MK141_INVENTORY_A1',selectedTubeId:detached.selectedTubeId,tubes:detached.tubes.map(t=>({id:t.id,loaded:t.loaded}))},
    errors=[],bad=harpoonCopyA(valid),badErrors=[];
  tr._kfX[0]=99999;tr._kfP[0]=99999;bad.tubes[1].id=bad.tubes[0].id;
  harpoonValidateA({harpoon:valid},errors,detached.tubes);harpoonValidateA({harpoon:bad},badErrors,detached.tubes);
  const checks={profileImmutable:Object.isFrozen(profile)&&Object.isFrozen(profile.sim),
    sourceEightUniqueTubes:installation.tubes.length===8&&new Set(installation.tubes.map(t=>t.id)).size===8,
    sourceAxisUnitAndUpward:installation.tubes.every(t=>Math.abs(Math.hypot(t.axis.x,t.axis.y,t.axis.z)-1)<1e-8&&t.axis.z>.5&&t.lengthM>profile.public.lengthM),
    sourceCapsComplete:installation.tubes.every(t=>t.capFaces.length===34)&&new Set(installation.tubes.flatMap(t=>t.capFaces)).size===272,
    isolatedDetachedInventory:detached!==harpoonRuntimeA()&&detached.tubes!==harpoonRuntimeA().tubes,
    ddgNoInstallation:DDG_119_LATE_FLIGHT_IIA_PROFILE.weapons.harpoon==null,
    modelRigidRoles:HARPOON_MODEL_META_A.meshes.filter(m=>m.role==='WING').length===4&&HARPOON_MODEL_META_A.meshes.filter(m=>m.role==='TAIL').length===4,
    trackMemoryDeepCopiedAndFrozen:before===JSON.stringify(memory)&&Object.isFrozen(memory)&&Object.isFrozen(memory.covariance),
    insPredictionLeadsStoredVelocity:prediction.x>10200&&prediction.y>540&&prediction.tgoS>0,
    protectedIdentityDenied:['UNKNOWN','FRIEND','NEUTRAL'].every(id=>!surfaceMissileIdentityPolicyWip13C4(id,'MANUAL',false).ok),
    manualAuthorityOnly:surfaceMissileIdentityPolicyWip13C4('TRAINING_TARGET','MANUAL',false).ok&&!surfaceMissileIdentityPolicyWip13C4('HOSTILE','AUTO',true).ok,
    saveNormalAndDuplicateBoundary:errors.length===0&&badErrors.includes('HARPOON_TUBE_ID_OR_STATE'),
    warheadFillSeparatedFromAssembly:profile.public.explosiveMassKg<profile.public.warheadAssemblyKg,
    modelCreditRetained:HARPOON_MODEL_META_A.attribution.author==='Civorsky'&&HARPOON_MODEL_META_A.attribution.license==='CC BY 4.0'};
  return {schema:'HARPOON_A_CORE_AUDIT',checks,pass:Object.values(checks).every(Boolean)};
}
