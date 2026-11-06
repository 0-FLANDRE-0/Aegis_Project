// SEEKER_UNIFY_C Stage 3 TEST_ONLY / AFTER_ACTION_TRUTH diagnostics.
// Truth below is used only after anonymous measurement generation and never
// enters cue, association, seeker EKF or guidance outputs.
(() => {
  function reset(seed=839300,mode='MAX_THREAT',emcon=false){
    _wip75ResetCase(seed);worldTimeScale=0;simAccumulator=0;BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;
    enemyMissiles.length=0;missiles.length=0;ramMissiles.length=0;targetPool.length=0;tracks.clear();resetSurfaceContacts();ownChaffs.length=0;
    applyDeploymentA(prepareDeploymentA({schema:DEPLOYMENT_POLICY_F.schema,targetShip:'NONE',enemyProfileId:null,allyProfileId:null,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:seed>>>0,allyEmcon:true,enemyEmcon:true}));
    emconActive=!!emcon;setThreatAssumptionModeC(mode);resetShipboardRadarRfRngWip13B13();
  }
  function controlledLaunchCue(em,positionM,velocityMps=null,positionSigmaM=300,velocitySigmaMps=ASM_CUE_A_SPEC.vmaxMps){
    em._cueLaunchA={source:'DIAGNOSTIC_OBSERVATION',positionM:{...positionM},velocityMps:velocityMps?{...velocityMps}:null,covariance:{positionSigmaM,velocitySigmaMps},timeS:0};delete em._targetCueA;em.insTgtX=metersToWorld(positionM.x);em.insTgtY=metersToWorld(positionM.y);return em;
  }
  function runCueCase(opts={}){
    const mode=String(opts.threatMode??'MAX_THREAT');setThreatAssumptionModeC(mode);const row=window.__SEEKER_UNIFY_B_DIAG__.runCueCase(opts),em=enemyMissiles.at(-1);
    return {...row,setup:{...row.setup,threatMode:mode},cueA:em?asmTargetCueSnapshotA(em):null,passiveSynthesis:em?._passiveRfB2?.lastSynthesis?{...em._passiveRfB2.lastSynthesis}:null};
  }
  function runVelocityCase(opts={}){
    const label=String(opts.label??'Kh-35U'),seconds=Math.max(0,Number(opts.seconds??120)),speedMps=Math.max(0,Number(opts.speedMps??15)),known=!!opts.known,rangeM=Math.max(1000,Number(opts.rangeM??100000)),em={id:839401,label,life:0,insTgtX:metersToWorld(rangeM),insTgtY:0};
    controlledLaunchCue(em,{x:rangeM,y:0},known?{x:speedMps,y:0}:null,300,known?1:ASM_CUE_A_SPEC.vmaxMps);const initial=asmTargetCueSnapshotA(em);em.life=seconds;asmTargetCuePredictA(em);const own={x:0,y:0,z:10},basket=asmCueBasketU0(em,own,ASM_SEEKER_PROFILES[label]),snap=asmTargetCueSnapshotA(em),truthX=rangeM+speedMps*seconds;
    return {setup:{label,seconds,speedMps,known,rangeM},initial,final:snap,basket:{rangeLowM:basket.rangeLowM,rangeHighM:basket.rangeHighM,rangeSigmaM:basket.rangeSigmaM,crossSigmaM:basket.crossSigmaM,azHalfDeg:basket.azHalfRad*180/Math.PI},afterActionTruth:{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',truthX,errorM:snap.positionM.x-truthX}};
  }
  function spawnPassiveFixture(opts={}){
    const seed=(Number(opts.seed)>>>0)||839500,label=String(opts.label??'Kh-32'),mode=String(opts.threatMode??'MAX_THREAT'),rangeKm=Math.max(1,Number(opts.rangeKm??100)),altitudeM=Math.max(1,Number(opts.altitudeM??(label==='Kh-32'?10000:12)));reset(seed,mode,false);
    const ax=aircraft.x(),ay=aircraft.y(),launchX=ax-kmToWorld(rangeKm),launchY=ay,speed=label==='Kh-32'?1200:280;
    spawnEnemyMissile({id:839500+seed,x:launchX,y:launchY,z:altitudeM,heading:0,vx:mpsToWorldSpeed(speed),vy:0,vz:0,asmType:label,lastKnownShipX:ax,lastKnownShipY:ay});
    const em=enemyMissiles.at(-1);Object.assign(em,{x:launchX,y:launchY,z:altitudeM,heading:0,vx:mpsToWorldSpeed(speed),vy:0,vz:0,speedMps:speed,seekerOn:false,life:0});em.flight.bodyYaw=em.flight.flightPathYaw=em.flight.cmdFlightPathYaw=0;em.flight.bodyPitch=em.flight.flightPath=em.flight.cmdFlightPath=0;
    controlledLaunchCue(em,{x:worldToMeters(ax),y:worldToMeters(ay)},null,300,ASM_CUE_A_SPEC.vmaxMps);delete em._passiveRfB2;missileNavB2Init(em,true);return {em,seed,label,mode,rangeKm,altitudeM,ax,ay};
  }
  function runPassiveRangeCase(opts={}){
    const f=spawnPassiveFixture(opts),samples=[],steps=Math.max(1,Math.floor(Number(opts.samples??12)));
    for(let i=0;i<steps;i++){
      f.em.life=i*ASM_PASSIVE_RF_B2_PROFILES[f.label].cadenceS;missileNavB2Update(f.em,ASM_PASSIVE_RF_B2_PROFILES[f.label].cadenceS);asmTargetCuePredictA(f.em);const m=asmPassiveRfMeasurementB2(f.em);if(m?.available){samples.push({...m,cueBefore:asmTargetCueSnapshotA(f.em)});asmApplyPassiveBearingB2(f.em,SIM_FIXED_DT);}
    }
    const actualRangeM=Math.hypot(worldToMeters(f.ax-f.em.x),worldToMeters(f.ay-f.em.y)),est=samples.filter(q=>Number.isFinite(q.directRangeEstimateM)),errors=est.map(q=>q.directRangeEstimateM-actualRangeM),mean=errors.length?errors.reduce((a,b)=>a+b,0)/errors.length:null,rmse=errors.length?Math.sqrt(errors.reduce((a,b)=>a+b*b,0)/errors.length):null;
    return {setup:{seed:f.seed,label:f.label,threatMode:f.mode,rangeKm:f.rangeKm,altitudeM:f.altitudeM,samples:steps},availableSamples:samples.length,measurements:samples.map(q=>({sampleTimeS:q.sampleTimeS,snr:q.snr,bearingSigmaDeg:q.bearingSigmaRad*180/Math.PI,elevationSigmaDeg:q.elevationSigmaRad*180/Math.PI,directRangeEstimateM:q.directRangeEstimateM,directRangeSigmaM:q.directRangeSigmaM,emitterClass:q.emitterClass,band:q.band})),synthesis:f.em._passiveRfB2?.lastSynthesis?{...f.em._passiveRfB2.lastSynthesis}:null,cue:asmTargetCueSnapshotA(f.em),afterActionTruth:{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',actualRangeM,meanErrorM:mean,rmseM:rmse}};
  }
  function runMultiEmitterCase(opts={}){
    const f=spawnPassiveFixture({...opts,rangeKm:Number(opts.rangeKm??80),altitudeM:Number(opts.altitudeM??800)}),offsetDeg=Number(opts.offsetDeg??3),otherRangeKm=Number(opts.otherRangeKm??80),prepared=prepareDeploymentA({schema:DEPLOYMENT_POLICY_F.schema,targetShip:'NONE',enemyProfileId:'CG_52_LATE_TICONDEROGA',allyProfileId:null,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:(f.seed+1)>>>0,allyEmcon:true,enemyEmcon:false});applyDeploymentA(prepared);
    const other=prepared.enemy,theta=deg(offsetDeg),r=kmToWorld(otherRangeKm);other.navigation.positionWorld.x=f.em.x+r*Math.cos(theta);other.navigation.positionWorld.y=f.em.y+r*Math.sin(theta);other.navigation.previousPositionWorld={...other.navigation.positionWorld};other.navigation.heading=Math.PI;const observer=observerC(other);observer.emcon=false;observer.enabled.SPY=true;observer.enabled.SPQ=true;observer.enabled.NAV=true;
    f.em.life=0;missileNavB2Update(f.em,SIM_FIXED_DT);const measurement=asmPassiveRfMeasurementB2(f.em),emitters=electronicPhysicalEmittersF().map((q,index)=>{const dx=worldToMeters(q.point.x-f.em.x),dy=worldToMeters(q.point.y-f.em.y);return {index,owner:q.owner??null,emitterClass:q.emitterClass,band:q.band,bearingRad:Math.atan2(dy,dx),rangeM:Math.hypot(dx,dy)};});
    let nearest=null;if(measurement?.available)for(const e of emitters){const err=Math.abs(angNorm(measurement.bearingRad-e.bearingRad));if(!nearest||err<nearest.errorRad)nearest={...e,errorRad:err};}
    return {setup:{seed:f.seed,label:f.label,threatMode:f.mode,rangeKm:f.rangeKm,altitudeM:f.altitudeM,offsetDeg,otherRangeKm},measurement,anonymousPayloadKeys:Object.keys(measurement??{}),afterActionTruth:{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',emitters,nearestToAnonymousBearing:nearest,targetOwner:ACTIVE_SHIP_RUNTIME.entityId,otherOwner:other.entityId},cue:asmTargetCueSnapshotA(f.em)};
  }
  function runDlHookCase(){
    const em={id:839700,label:'Kh-35U',life:5,insTgtX:metersToWorld(100000),insTgtY:0};controlledLaunchCue(em,{x:100000,y:0},null,300,ASM_CUE_A_SPEC.vmaxMps);const before=asmTargetCueSnapshotA(em),result=asmCueUpdateA(em,{source:'DL',positionM:{x:101000,y:500},velocityMps:{x:10,y:2},covariance:{positionSigmaM:100,velocitySigmaMps:2},timeS:5}),after=asmTargetCueSnapshotA(em);return {before,result,after,connected:false};
  }
  function contract(){return {schema:ASM_CUE_A_SPEC.schema,spec:ASM_CUE_A_SPEC,features:ASM_CUE_FEATURES_A,mode:THREAT_ASSUMPTION_MODE,passiveProfiles:ASM_PASSIVE_RF_B2_PROFILES,dlConnected:false,truthOutput:false,functions:{predict:asmTargetCuePredictA.toString(),update:asmCueUpdateA.toString(),measurement:asmPassiveRfMeasurementB2.toString(),basket:asmCueBasketU0.toString()}};}
  window.__SEEKER_UNIFY_C_DIAG__=Object.freeze({runCueCase,runVelocityCase,runPassiveRangeCase,runMultiEmitterCase,runDlHookCase,contract});
})();
