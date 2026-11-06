// CUE_A-1 Stage 2 TEST_ONLY diagnostics. Truth is used only for after-action
// error reporting; production selection receives anonymous emitter metadata.
(() => {
  function reset(seed=849300,mode='MAX_THREAT'){
    _wip75ResetCase(seed);worldTimeScale=0;simAccumulator=0;BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;
    enemyMissiles.length=0;missiles.length=0;ramMissiles.length=0;targetPool.length=0;tracks.clear();resetSurfaceContacts();ownChaffs.length=0;
    applyDeploymentA(prepareDeploymentA({schema:DEPLOYMENT_POLICY_F.schema,targetShip:'NONE',enemyProfileId:null,allyProfileId:null,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:seed>>>0,allyEmcon:true,enemyEmcon:true}));
    emconActive=false;setThreatAssumptionModeC(mode);resetShipboardRadarRfRngWip13B13();resetSpq9bState();resetBridgeMasterEState();
  }
  function controlledLaunchCue(em,positionM){
    em._cueLaunchA={source:'DIAGNOSTIC_OBSERVATION',positionM:{...positionM},velocityMps:null,covariance:{positionSigmaM:300,velocitySigmaMps:ASM_CUE_A_SPEC.unknownVelocityAxisSigmaMps},timeS:0};
    delete em._targetCueA;em.insTgtX=metersToWorld(positionM.x);em.insTgtY=metersToWorld(positionM.y);return em;
  }
  function spawnFixture(opts={}){
    const seed=(Number(opts.seed)>>>0)||849300,label=String(opts.label??'Kh-35U'),mode=String(opts.threatMode??'MAX_THREAT'),rangeKm=Math.max(1,Number(opts.rangeKm??60)),altitudeM=Math.max(1,Number(opts.altitudeM??(label==='Kh-32'?10000:1200)));reset(seed,mode);
    const ax=aircraft.x(),ay=aircraft.y(),launchX=ax-kmToWorld(rangeKm),launchY=ay,speed=label==='Kh-32'?1200:280;
    spawnEnemyMissile({id:849300+seed,x:launchX,y:launchY,z:altitudeM,heading:0,vx:mpsToWorldSpeed(speed),vy:0,vz:0,asmType:label,lastKnownShipX:ax,lastKnownShipY:ay});
    const em=enemyMissiles.at(-1);Object.assign(em,{x:launchX,y:launchY,z:altitudeM,heading:0,vx:mpsToWorldSpeed(speed),vy:0,vz:0,speedMps:speed,seekerOn:false,life:0});
    em.flight.bodyYaw=em.flight.flightPathYaw=em.flight.cmdFlightPathYaw=0;em.flight.bodyPitch=em.flight.flightPath=em.flight.cmdFlightPath=0;
    controlledLaunchCue(em,{x:worldToMeters(ax),y:worldToMeters(ay)});delete em._passiveRfB2;missileNavB2Init(em,true);
    return {em,seed,label,mode,rangeKm,altitudeM,ax,ay};
  }
  function setEquipment(condition){
    const o=observerC(ACTIVE_SHIP_RUNTIME),all=condition==='ALL_ON';
    o.enabled.SPY=all||condition!=='SPY_OFF'&&condition!=='ALL_OFF';
    o.enabled.SPQ=all||condition!=='SPQ_OFF'&&condition!=='ALL_OFF';
    o.enabled.NAV=all||condition!=='NAV_OFF'&&condition!=='ALL_OFF';
    return {SPY:o.enabled.SPY,SPQ:o.enabled.SPQ,NAV:o.enabled.NAV};
  }
  function setRotorTime(timeS){
    spq9bRotorAngle=angNorm(TAU*(Number(ACTIVE_SHIP_PROFILE.sensors.spq9b.rpm)||0)/60*timeS);
    bridgeMasterERotorAngle=angNorm(TAU*(Number(ACTIVE_SHIP_PROFILE.sensors.bridgeMasterE.nominalRpm)||0)/60*timeS);
    const o=observerC(ACTIVE_SHIP_RUNTIME);o.rotors.SPQ=spq9bRotorAngle;o.rotors.NAV=bridgeMasterERotorAngle;
  }
  function emitterTruthForMeasurement(em,measurement){
    if(!measurement?.available)return null;let best=null;
    for(const source of electronicPhysicalEmittersF()){
      if(measurement.family&&source.family!==measurement.family)continue;
      const dx=worldToMeters(source.point.x-em.x),dy=worldToMeters(source.point.y-em.y),dz=(Number(source.point.z)||0)-(Number(em.z)||0),horizontalM=Math.max(1,Math.hypot(dx,dy)),az=Math.atan2(dy,dx),el=Math.atan2(dz,horizontalM)-horizontalM/(2*ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM),error=Math.hypot(angNorm(measurement.bearingRad-az),angNorm(measurement.elevationRad-el));
      if(!best||error<best.error)best={family:source.family,band:source.band,az,el,error};
    }
    return best;
  }
  function runEquipmentCase(opts={}){
    const f=spawnFixture(opts),condition=String(opts.condition??'ALL_ON'),enabled=setEquipment(condition),sampleCount=Math.max(1,Math.floor(Number(opts.samples??12))),rows=[];
    for(let i=0;i<sampleCount;i++){
      const timeS=i*ASM_PASSIVE_RF_B2_PROFILES[f.label].cadenceS;f.em.life=timeS;setRotorTime(timeS);missileNavB2Update(f.em,ASM_PASSIVE_RF_B2_PROFILES[f.label].cadenceS);asmTargetCuePredictA(f.em);
      const measurement=asmPassiveRfMeasurementB2(f.em),truth=emitterTruthForMeasurement(f.em,measurement),synthesis=f.em._passiveRfB2?.lastSynthesis?structuredClone(f.em._passiveRfB2.lastSynthesis):null;
      rows.push({timeS,available:!!measurement?.available,family:measurement?.family??null,band:measurement?.band??null,frequencyMHz:measurement?.frequencyMHz??null,snr:measurement?.snr??0,bearingSigmaDeg:measurement?.bearingSigmaRad!=null?measurement.bearingSigmaRad*180/Math.PI:null,elevationSigmaDeg:measurement?.elevationSigmaRad!=null?measurement.elevationSigmaRad*180/Math.PI:null,bearingErrorDeg:truth?angNorm(measurement.bearingRad-truth.az)*180/Math.PI:null,elevationErrorDeg:truth?angNorm(measurement.elevationRad-truth.el)*180/Math.PI:null,synthesis});
    }
    const available=rows.filter(q=>q.available),intervals=[];for(let i=1;i<available.length;i++)intervals.push(available[i].timeS-available[i-1].timeS);
    return {setup:{seed:f.seed,label:f.label,threatMode:f.mode,rangeKm:f.rangeKm,altitudeM:f.altitudeM,condition,samples:sampleCount,enabled},summary:{available:available.length,families:Object.fromEntries([...new Set(available.map(q=>q.family))].map(k=>[k,available.filter(q=>q.family===k).length])),meanReceiveIntervalS:intervals.length?intervals.reduce((a,b)=>a+b,0)/intervals.length:null},rows,afterActionTruth:{tag:'AFTER_ACTION_TRUTH_TEST_ONLY'}};
  }
  function syntheticContaminant(kind,point){
    const common={point:{...point},band:'IJ',frequencyMHz:10000,power:1e9,beamAz:null};
    if(kind==='ESSM_ARH')return {...common,family:'MISSILE SEEKER TRACK',emitterClass:'ACTIVE_SEEKER'};
    if(kind==='SM6_ARH')return {...common,family:'MISSILE SEEKER SEARCH',emitterClass:'ACTIVE_SEEKER'};
    if(kind==='AIR_RADAR')return {...common,family:'AIR SEARCH RADAR',emitterClass:'SEARCH_RADAR'};
    if(kind==='NULKA')return {...common,family:'RF INTERFERENCE',emitterClass:'JAMMER'};
    return {...common,family:'RF INTERFERENCE',emitterClass:'JAMMER'};
  }
  function runContaminantCase(opts={}){
    const f=spawnFixture({...opts,rangeKm:Number(opts.rangeKm??60),altitudeM:Number(opts.altitudeM??1200)}),kind=String(opts.kind??'ESSM_ARH'),original=electronicPhysicalEmittersF,point={x:f.ax,y:f.ay,z:30};let measurement,state;
    try{
      electronicPhysicalEmittersF=()=>[syntheticContaminant(kind,point)];f.em.life=0;measurement=asmPassiveRfMeasurementB2(f.em);state=structuredClone(f.em._passiveRfB2??null);
    }finally{electronicPhysicalEmittersF=original;}
    return {setup:{seed:f.seed,label:f.label,threatMode:f.mode,kind},selected:!!measurement?.available,measurement,state,afterActionTruth:{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',syntheticKind:kind}};
  }
  function runConfirmedBandCase(opts={}){
    const label=String(opts.label??'Kh-35U'),f=spawnFixture({...opts,label,threatMode:'CONFIRMED_ONLY',rangeKm:Number(opts.rangeKm??60),altitudeM:Number(opts.altitudeM??1200)}),sources=[
      {point:{x:f.ax,y:f.ay,z:30},band:'S',frequencyMHz:3000,power:1e9,family:'SHIP SEARCH RADAR',emitterClass:'SEARCH_RADAR',beamAz:null},
      {point:{x:f.ax,y:f.ay,z:30},band:'S',frequencyMHz:3050,power:1e9,family:'NAVIGATION RADAR',emitterClass:'SEARCH_RADAR',beamAz:null},
      {point:{x:f.ax,y:f.ay,z:30},band:'IJ',frequencyMHz:10000,power:1e9,family:'SURFACE SEARCH RADAR',emitterClass:'SEARCH_RADAR',beamAz:null}
    ],original=electronicPhysicalEmittersF;let measurement,state;
    try{electronicPhysicalEmittersF=()=>sources;measurement=asmPassiveRfMeasurementB2(f.em);state=structuredClone(f.em._passiveRfB2??null);}finally{electronicPhysicalEmittersF=original;}
    return {setup:{seed:f.seed,label,mode:'CONFIRMED_ONLY'},measurement,state,performance:'UNVERIFIED'};
  }
  function runBeamUnitCases(){
    if(typeof asmPassivePositiveSweepOffsetA!=='function')return {stage2:false};
    const mk=(beamAz,double,toward)=>asmPassiveEmitterGainA({beamAz,beamwidthDeg:.6,rpm:30,double},toward,.2);
    return {stage2:true,crossed:mk(0,false,deg(-18)),missed:mk(0,false,deg(90)),doubleCrossed:mk(0,true,deg(162)),spy:asmPassiveEmitterGainA({beamAz:null},0,.2)};
  }
  function contract(){
    return {stage2:typeof ASM_MIDCOURSE_PASSIVE_FAMILIES!=='undefined',families:typeof ASM_MIDCOURSE_PASSIVE_FAMILIES!=='undefined'?[...ASM_MIDCOURSE_PASSIVE_FAMILIES]:null,receiveBands:typeof ASM_PASSIVE_RF_RECEIVE_BANDS_A!=='undefined'?ASM_PASSIVE_RF_RECEIVE_BANDS_A:null,frequencyReferenceMHz:typeof ASM_PASSIVE_ACCURACY_REFERENCE_MHZ_A!=='undefined'?ASM_PASSIVE_ACCURACY_REFERENCE_MHZ_A:null,selection:asmPassiveRfMeasurementB2.toString(),hoj:electronicHojF.toString(),hojTrack:asmUpdateHojTrack.toString(),physicalEmitters:electronicPhysicalEmittersF.toString()};
  }
  window.__CUE_A1_STAGE2_DIAG__=Object.freeze({runEquipmentCase,runContaminantCase,runConfirmedBandCase,runBeamUnitCases,contract});
})();
