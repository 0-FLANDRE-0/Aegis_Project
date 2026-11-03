// SEEKER_UNIFY_B test-only U0 probes. Debug identity is copied only into
// after-action evidence and is never consumed by tactical code.
(() => {
  // AFTER_ACTION_TRUTH diagnostic only. This wrapper records whether the real
  // ship was inside the physical search sector and the U0 acquisition basket
  // when a seeker dwell occurred. The result is never returned to gameplay.
  let cueTruthAudit=null;
  const u0TruthOriginalMeasurement=asmSeekerMeasurement;
  asmSeekerMeasurement=function(em,s,p){
    if(cueTruthAudit&&cueTruthAudit.missileId===em?.id){
      const own=missileNavB2Kinematics(em),basket=asmCueBasketU0(em,own,p),dx=worldToMeters(aircraft.x()-own.x),dy=worldToMeters(aircraft.y()-own.y),dz=8-(own.z??0),rangeM=Math.max(1,Math.hypot(dx,dy,dz)),horizontalM=Math.max(1,Math.hypot(dx,dy));
      const azErrRad=Math.abs(angNorm(Math.atan2(dy,dx)-basket.azRad)),elErrRad=Math.abs(angNorm(Math.atan2(dz,horizontalM)-basket.elRad)),searchAzRad=deg(Math.max(0,Number(p?.searchSectorAzDeg)||0)),searchElRad=deg(Math.max(0,Number(p?.searchSectorElDeg)||0));
      const inSector=azErrRad<=searchAzRad&&elErrRad<=searchElRad,inBasket=rangeM>=basket.rangeLowM&&rangeM<=basket.rangeHighM&&azErrRad<=basket.azHalfRad&&elErrRad<=basket.elHalfRad;
      cueTruthAudit.dwells++;if(inSector)cueTruthAudit.insideSearchSectorDwells++;else cueTruthAudit.outsideSearchSectorDwells++;
      if(inBasket)cueTruthAudit.insideBasketDwells++;if(inSector&&!inBasket)cueTruthAudit.insideSectorOutsideBasketDwells++;
      cueTruthAudit.minAzErrorDeg=Math.min(cueTruthAudit.minAzErrorDeg,azErrRad*180/Math.PI);cueTruthAudit.maxAzErrorDeg=Math.max(cueTruthAudit.maxAzErrorDeg,azErrRad*180/Math.PI);
      cueTruthAudit.minRangeResidualM=Math.min(cueTruthAudit.minRangeResidualM,Math.min(Math.abs(rangeM-basket.rangeLowM),Math.abs(rangeM-basket.rangeHighM)));
    }
    return u0TruthOriginalMeasurement.apply(this,arguments);
  };
  function cueFailureAuditResult(everTrack){
    const q=cueTruthAudit;if(!q)return null;
    let category='SUCCESS',reason='TRACK_ACQUIRED';
    if(!everTrack){
      if(q.dwells===0){category='OTHER';reason='NO_SEEKER_DWELL';}
      else if(q.insideSearchSectorDwells===0){category='OUTSIDE_SEARCH_SECTOR';reason='TRUTH_NEVER_ENTERED_PROFILE_SEARCH_SECTOR';}
      else if(q.insideBasketDwells===0&&q.insideSectorOutsideBasketDwells>0){category='INSIDE_SEARCH_OUTSIDE_BASKET';reason='TRUTH_ENTERED_SEARCH_SECTOR_BUT_NEVER_U0_BASKET';}
      else{category='OTHER';reason=q.insideBasketDwells>0?'INSIDE_BASKET_WITHOUT_TRACK':'MIXED_GEOMETRY_OR_RF_DETECTION';}
    }
    return {tag:'AFTER_ACTION_TRUTH_TEST_ONLY',category,reason,dwells:q.dwells,insideSearchSectorDwells:q.insideSearchSectorDwells,outsideSearchSectorDwells:q.outsideSearchSectorDwells,insideBasketDwells:q.insideBasketDwells,insideSectorOutsideBasketDwells:q.insideSectorOutsideBasketDwells,minAzErrorDeg:Number.isFinite(q.minAzErrorDeg)?q.minAzErrorDeg:null,maxAzErrorDeg:q.maxAzErrorDeg,minRangeResidualM:Number.isFinite(q.minRangeResidualM)?q.minRangeResidualM:null};
  }
  function reset(seed,emcon){
    _wip75ResetCase(seed);worldTimeScale=0;simAccumulator=0;BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;
    enemyMissiles.length=0;missiles.length=0;ramMissiles.length=0;targetPool.length=0;tracks.clear();resetSurfaceContacts();ownChaffs.length=0;
    applyDeploymentA(prepareDeploymentA({schema:DEPLOYMENT_POLICY_F.schema,targetShip:'NONE',enemyProfileId:null,allyProfileId:null,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:seed>>>0,allyEmcon:true,enemyEmcon:true}));
    emconActive=!!emcon;resetShipboardRadarRfRngWip13B13();
  }
  function cueState(em){
    const s=em.seeker,q=em._targetCueU0;
    return {basket:s?.lastCueBasketU0?{...s.lastCueBasketU0}:null,legacyPass:s?.cueLegacyPassCountU0??null,expandedPass:s?.cueExpandedPassCountU0??null,expandedOnly:s?.cueExpandedOnlyCountU0??null,
      passive:q?{attempts:q.passiveCorrectionAttempts,updates:q.passiveBearingClockUpdates,lastResidualRad:q.lastPassiveBearingResidualRad??null,lastConverged:q.lastPassiveBearingConverged??null,rangeRefTimeS:q.rangeRefTimeS,bearingRefTimeS:q.bearingRefTimeS,source:q.source}:null};
  }
  function runCueCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||729300,label=String(opts.label??'Kh-35U'),rangeKm=Number(opts.rangeKm??100),speedKt=Number(opts.speedKt??30),turnDeg=Number(opts.turnDeg??0),emcon=!!opts.emcon;reset(seed,emcon);
    const ax=aircraft.x(),ay=aircraft.y(),speed=speedKt*.514444,launchX=ax-kmToWorld(rangeKm),launchY=ay,initialCourse=0,turnAtS=Math.max(4,rangeKm*1000/(label==='Kh-32'?1200:280)/3);
    shipNav.heading=initialCourse;shipNav.speed=speed;shipNav.vx=mpsToWorldSpeed(speed);shipNav.vy=0;
    spawnEnemyMissile({id:730000+seed,x:launchX,y:launchY,z:label==='Kh-32'?10000:200,heading:0,vx:mpsToWorldSpeed(label==='Kh-32'?1200:280),vy:0,vz:0,asmType:label,lastKnownShipX:ax,lastKnownShipY:ay});
    const em=enemyMissiles.at(-1);cueTruthAudit={missileId:em.id,dwells:0,insideSearchSectorDwells:0,outsideSearchSectorDwells:0,insideBasketDwells:0,insideSectorOutsideBasketDwells:0,minAzErrorDeg:Infinity,maxAzErrorDeg:0,minRangeResidualM:Infinity};let everAcquire=false,everTrack=false,firstAcquireS=null,firstTrackS=null,firstAcquireBasket=null,firstTrackBasket=null,firstAccepted=null,closestM=Infinity,passedForS=0,endedBy='TIMEOUT',ticks=0;
    const maxTicks=Math.ceil(Math.min(610,rangeKm*1000/(label==='Kh-32'?650:180)+180)/SIM_FIXED_DT),hitCount0=shipHitHistory.length;
    for(;ticks<maxTicks&&em.alive;ticks++){
      if(ticks*SIM_FIXED_DT>=turnAtS&&turnDeg!==0){const c=deg(turnDeg);shipNav.heading=c;shipNav.vx=mpsToWorldSpeed(Math.cos(c)*speed);shipNav.vy=mpsToWorldSpeed(Math.sin(c)*speed);}
      shipNav.previousPositionWorld={...shipNav.positionWorld};shipNav.positionWorld.x+=shipNav.vx*SIM_FIXED_DT;shipNav.positionWorld.y+=shipNav.vy*SIM_FIXED_DT;
      updateEnemyMissile(em,SIM_FIXED_DT);simStepCounter++;
      const d=Math.hypot(worldToMeters(em.x-aircraft.x()),worldToMeters(em.y-aircraft.y()),(em.z??0)-8);if(d<closestM){closestM=d;passedForS=0;}else if(d>closestM+200)passedForS+=SIM_FIXED_DT;
      const s=em.seeker,mode=s?.mode;if(!firstAccepted&&(s?.acceptedDiscreteCount??0)+(s?.acceptedSeaOnlyCount??0)>0)firstAccepted={timeS:ticks*SIM_FIXED_DT,kind:s.lastAssocDebugKind??null,id:s.lastAssocDebugId??null,evidence:s.lastAcceptedEvidence??null};
      if(mode==='ACQUIRE'&&!everAcquire){everAcquire=true;firstAcquireS=ticks*SIM_FIXED_DT;firstAcquireBasket=cueState(em);}
      if(mode==='TRACK'&&!everTrack){everTrack=true;firstTrackS=ticks*SIM_FIXED_DT;firstTrackBasket=cueState(em);}
      if(passedForS>8){endedBy='PASSED_TARGET';break;}
    }
    if(shipHitHistory.length>hitCount0)endedBy='GAME_SHIP_HIT';else if(!em.alive)endedBy=em._outcome??em._deathReason??'GAME_TERMINATED';
    const failureAudit=cueFailureAuditResult(everTrack);cueTruthAudit=null;
    return {setup:{seed,label,rangeKm,speedKt,turnDeg,turnAtS,emcon},result:{everAcquire,everTrack,firstAcquireS,firstTrackS,firstAcquireBasket,firstTrackBasket,firstAccepted,failureAudit,finalCue:cueState(em),finalMode:em.seeker?.mode??null,closestM,endedBy,alive:!!em.alive,flightTimeS:ticks*SIM_FIXED_DT,shipHit:shipHitHistory.length>hitCount0,rejectReason:em.seeker?.lastRejectReasonWip13C8??null,globalRng:SIM_RNG_STATE>>>0}};
  }
  function cueContract(){
    return {available:typeof ASM_CUE_BASKET_U0!=='undefined',profile:typeof ASM_CUE_BASKET_U0==='undefined'?null:{...ASM_CUE_BASKET_U0},targetCue:typeof asmTargetCueU0==='undefined'?null:asmTargetCueU0.toString(),basket:typeof asmCueBasketU0==='undefined'?null:asmCueBasketU0.toString(),passive:asmApplyPassiveBearingB2.toString(),association:asmSeekerAssociateMeasurements.toString()};
  }
  function runHarpoonCueCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||739300,rangeKm=Number(opts.rangeKm??100),speedKt=Number(opts.speedKt??30),turnDeg=Number(opts.turnDeg??0);reset(seed,false);
    const cfg=HARPOON_PROFILE_A.sim,baseX=worldToMeters(aircraft.x())+160000,baseY=worldToMeters(aircraft.y())+160000,targetX=baseX+rangeKm*1000,targetY=baseY,targetSpeed=speedKt*.514444;
    const target=spawnSurfaceTargetWip13A({entityId:'SEEKER_UNIFY_HARPOON_'+seed,x:metersToWorld(targetX),y:metersToWorld(targetY),heading:0,speedKt,mobilityMode:'DEAD_IN_WATER'});
    target.vx=mpsToWorldSpeed(targetSpeed);target.vy=0;target.heading=0;
    const positionM={x:baseX,y:baseY,z:cfg.cruiseHeightM},velocityMps={x:cfg.cruiseSpeedMps,y:0,z:0},axis={x:1,y:0,z:0},serial=739000+seed;
    const covariance=new Float64Array(36);covariance[0]=covariance[7]=75**2;covariance[21]=covariance[28]=.04**2;
    const memory={schema:'HARPOON_FROZEN_LAUNCH_TRACK_A1',trackId:null,positionM:{x:targetX,y:targetY,z:8},velocityMps:{x:targetSpeed,y:0,z:0},covariance,stateEpoch:'RELEASE_CURRENT_EKF',stateAgeS:0,observationAgeS:0,launchStep:simStepCounter,identity:'HOSTILE',truthUsed:false,updatesAfterRelease:false};
    const m={id:serial,entityClass:'WORLD_ORDNANCE',ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,weaponKey:'HARPOON',label:'RGM-84D',alive:true,ageS:0,phase:'INS_CRUISE',positionM:{...positionM},velocityMps:{...velocityMps},navPositionM:{...positionM},ins:harpoonInsInitC(positionM,velocityMps,axis,serial),radarAltitudeM:cfg.cruiseHeightM,speedMps:cfg.cruiseSpeedMps,yawRad:0,pitchRad:0,
      launchAxis:{...axis},launchPositionM:{...positionM},launchMuzzleM:{...positionM},launchRearM:{...positionM},tubeId:'DIAGNOSTIC',carrierVelocityMps:{x:0,y:0,z:0},canisterSpeedMps:0,route:null,memory,massKg:HARPOON_PROFILE_A.public.bodyMassKg,fuelKg:cfg.fuelKg,boosterAttached:false,wingDeploy01:1,tailDeploy01:1,tailCommandRad:0,thrustN:0,pathM:cfg.fuzeArmDistanceM+1,tubeCleared:true,fuzeArmed:true,rng:rfSeedWip13A2('HARPOON_AUDIT:'+seed),seeker:{active:false,mode:'OFF',timerS:0,azRelRad:0,elRelRad:0,scanDirection:1,scanReversals:0,scanBoundsRad:[0,0],candidate:null,lock:null,lockCount:0,missedS:0,lastObservations:[],observations:0},history:[],outcome:null,rcsM2:.06};
    harpoonSyncWorldCoordinatesA(m);let everAcquire=false,everTrack=false,firstAcquireS=null,firstTrackS=null,closestM=Infinity,passedForS=0,ticks=0,endedBy='TIMEOUT';
    const nominalFlightS=rangeKm*1000/Math.max(1,cfg.cruiseSpeedMps-targetSpeed),turnAtS=Math.max(4,nominalFlightS/3),maxTicks=Math.ceil(Math.min(cfg.maxLifeS,nominalFlightS+180)/SIM_FIXED_DT);
    for(;ticks<maxTicks&&m.alive;ticks++){
      if(ticks*SIM_FIXED_DT>=turnAtS&&turnDeg!==0){const c=deg(turnDeg);target.heading=c;target.vx=mpsToWorldSpeed(Math.cos(c)*targetSpeed);target.vy=mpsToWorldSpeed(Math.sin(c)*targetSpeed);}
      target.x+=target.vx*SIM_FIXED_DT;target.y+=target.vy*SIM_FIXED_DT;
      // Audit only the unchanged INS-memory + ARH seeker path. Advancing the
      // receiver at the profile cruise speed avoids introducing contact/damage
      // physics into a basket audit while retaining real RF observations,
      // independent seeker RNG, scan, gates, and state transitions.
      m.ageS+=SIM_FIXED_DT;m.positionM.x+=m.velocityMps.x*SIM_FIXED_DT;m.positionM.y+=m.velocityMps.y*SIM_FIXED_DT;m.positionM.z+=m.velocityMps.z*SIM_FIXED_DT;
      m.navPositionM={...m.positionM};m.radarAltitudeM=cfg.cruiseHeightM;harpoonSyncWorldCoordinatesA(m);harpoonSeekerA(m,SIM_FIXED_DT);simStepCounter++;
      const d=Math.hypot(m.positionM.x-worldToMeters(target.x),m.positionM.y-worldToMeters(target.y),(m.positionM.z??0)-8);if(d<closestM){closestM=d;passedForS=0;}else if(d>closestM+200)passedForS+=SIM_FIXED_DT;
      if(m.seeker.mode==='ACQUIRE'&&!everAcquire){everAcquire=true;firstAcquireS=ticks*SIM_FIXED_DT;}
      if(m.seeker.mode==='TRACK'&&!everTrack){everTrack=true;firstTrackS=ticks*SIM_FIXED_DT;}
      if(passedForS>12){endedBy='PASSED_TARGET';break;}
    }
    if(!m.alive)endedBy=m.outcome??m._deathReason??'GAME_TERMINATED';
    return {setup:{seed,rangeKm,speedKt,turnDeg,turnAtS},result:{everAcquire,everTrack,firstAcquireS,firstTrackS,finalMode:m.seeker.mode,closestM,endedBy,alive:!!m.alive,flightTimeS:ticks*SIM_FIXED_DT,scanReversals:m.seeker.scanReversals,observations:m.seeker.observations,searchBasketM:cfg.seekerSearchBasketM,memoryVelocityMps:{...memory.velocityMps}}};
  }
  window.__SEEKER_UNIFY_B_DIAG__=Object.freeze({runCueCase,runHarpoonCueCase,cueContract});
})();
