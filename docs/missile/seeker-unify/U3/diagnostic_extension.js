// Test-only U3 probes. No result is consumed by tactical code.
(() => {
  function covariance(posSigmaM=75,velSigmaMps=.04){const P=new Array(36).fill(0);P[0]=P[7]=posSigmaM**2;P[21]=P[28]=velSigmaMps**2;return P;}
  function trackMemory(opts={}){return {schema:'HARPOON_FROZEN_LAUNCH_TRACK_A1',trackId:null,
    positionM:{x:Number(opts.x??100000),y:Number(opts.y??20000),z:8},velocityMps:{x:Number(opts.vx??12),y:Number(opts.vy??3),z:0},
    covariance:opts.missingCovariance?null:covariance(Number(opts.posSigmaM??75),Number(opts.velSigmaMps??.04)),stateEpoch:'RELEASE_CURRENT_EKF',stateAgeS:0,
    observationAgeS:Number(opts.observationAgeS??0),launchStep:simStepCounter,identity:'HOSTILE',cueSource:'LOCAL_SURFACE_OBSERVATION',
    positionVelocityOwner:'SHIP_EKF_RELEASE_SNAPSHOT',covarianceOwner:'SHIP_EKF_RELEASE_SNAPSHOT',timeOwner:'SIM_FIXED_STEP_RELEASE',truthUsed:false,updatesAfterRelease:false};}
  function routeMemory(){return {schema:'HARPOON_FROZEN_COORDINATE_CUE_E1',trackId:null,positionM:{x:100000,y:20000,z:0},velocityMps:{x:0,y:0,z:0},
    covariance:new Array(36).fill(0),stateEpoch:'RELEASE_FIXED_COORDINATE',stateAgeS:0,observationAgeS:0,launchStep:simStepCounter,identity:'COORDINATE_SEARCH',
    cueSource:'ROUTE_PLAN_PRIOR',observationUpdate:false,positionVelocityOwner:'OPERATOR_ROUTE_PLAN',covarianceOwner:'NONE_NOT_A_MEASUREMENT',timeOwner:'RELEASE_FIXED_COORDINATE',truthUsed:false,updatesAfterRelease:false};}
  function cueMatrixB(){
    const nominal=trackMemory(),packet=harpoonCuePacketB(nominal),horizons=[0,30,120,300].map(horizonS=>harpoonCueHandoffB(nominal,horizonS)),
      overOld=harpoonCueHandoffB(trackMemory({posSigmaM:1600,velSigmaMps:.01}),0),overPhysical=harpoonCueHandoffB(trackMemory({posSigmaM:6000,velSigmaMps:.01}),0),
      route=harpoonCueHandoffB(routeMemory(),0),missing=harpoonCueHandoffB(trackMemory({missingCovariance:true}),30),repeatA=harpoonCueHandoffB(nominal,120),repeatB=harpoonCueHandoffB(nominal,120);
    const checks={packetMapped:!!packet&&packet.x[0]===nominal.positionM.x&&packet.x[1]===nominal.positionM.y&&packet.x[2]===nominal.velocityMps.x&&packet.x[3]===nominal.velocityMps.y,
      allFinite:horizons.every(q=>Number.isFinite(q.searchBasketM)&&Number.isFinite(q.predictionSigmaM)),covarianceGrows:horizons.at(-1).searchBasketM>horizons[0].searchBasketM,
      fixed4kmRemoved:overOld.searchBasketM>4000&&overOld.feasible,physicalLimitRetained:overPhysical.searchBasketM>overPhysical.physicalSearchLimitM&&!overPhysical.feasible,
      routePriorIsNotObservation:route.source==='ROUTE_PLAN_PRIOR'&&route.observationUpdate===false&&route.searchBasketM===HARPOON_PROFILE_A.sim.seekerSearchBasketM&&harpoonCuePacketB(routeMemory())===null,
      missingRejected:missing.feasible===false&&missing.reason==='INS_PREDICTION_BASKET_INSUFFICIENT',deterministic:JSON.stringify(repeatA)===JSON.stringify(repeatB),
      noTruthFields:[...Object.keys(packet??{}),...Object.keys(repeatA)].every(k=>!/(entity|targetId|truthPosition|physicalId)/i.test(k))&&repeatA.truthUsed===false};
    return {schema:'AEGIS_SEEKER_UNIFY_U3_B_DIAGNOSTIC_1',spec:HARPOON_CUE_B_SPEC,checks,pass:Object.values(checks).every(Boolean),packet,horizons,overOld,overPhysical,route,missing,coreAudits:{harpoon:harpoonCoreAuditA(),seeker:harpoonSeekerCoreAuditC()}};
  }
  function contractB(){return {spec:HARPOON_CUE_B_SPEC,packet:harpoonCuePacketB.toString(),predict:harpoonCuePredictB.toString(),handoff:harpoonCueHandoffB.toString(),routeProgram:harpoonRouteProgramE.toString(),routeGate:harpoonRouteGateE.toString(),gate:harpoonGateA.toString(),seeker:harpoonSeekerA.toString(),journal:harpoonJournalReleaseF1.toString(),attackGuard:attackPathGuardH3.toString()};}
  function hojExerciseC(){
    if(typeof seekerUpdateHojTrackU3!=='function')return {available:false};
    const priorMode=THREAT_ASSUMPTION_MODE,originalSignal=asmHojEmitterSignal,globalBefore=SIM_RNG_STATE>>>0,stepBefore=simStepCounter,
      signal={active:true,noiseW:1,directJOverN:35,rxGain:1,worldAz:.31,worldEl:-.02,noiseRawW:35,deceptionRawW:0,losQ:1};
    try{
      asmHojEmitterSignal=()=>({...signal});SIM_RNG_STATE=0x735103;const auditBefore=seekerU3HojAuditSnapshotC();
      const asmState={hoj:null,gimbalAz:0,gimbalEl:0,_kfX:null,trackValid:false,mode:'SEARCH',missAgeS:999},asmMissile={seekerOn:true,x:0,y:0,z:20,heading:0,flight:{bodyPitch:0}};
      for(let i=0;i<90;i++){asmUpdateHojTrack(asmMissile,asmState,ASM_SEEKER_PROFILES['Kh-35U'],SIM_FIXED_DT);simStepCounter++;}
      const asmResult=structuredClone(asmState.hoj),auditAfter=seekerU3HojAuditSnapshotC(),asmAudit={mode:auditAfter.mode,comparisons:auditAfter.comparisons-auditBefore.comparisons,mismatches:auditAfter.mismatches-auditBefore.mismatches,rngMismatches:auditAfter.rngMismatches-auditBefore.rngMismatches,dynamicAuditArrays:auditAfter.dynamicAuditArrays};
      const makeHarpoon=seed=>({id:seed,x:0,y:0,z:15,yawRad:0,pitchRad:0,rng:seed>>>0,seeker:{active:true,mode:'SEARCH',azRelRad:0,elRelRad:0,lock:null,missedS:999,hoj:null}});
      setThreatAssumptionModeC('MAX_THREAT');const max=makeHarpoon(0x735104),maxStart=max.rng;for(let i=0;i<90;i++){harpoonUpdateHojC(max,SIM_FIXED_DT);simStepCounter++;}const maxResult=harpoonHojSnapshotC(max);
      setThreatAssumptionModeC('CONFIRMED_ONLY');const confirmed=makeHarpoon(0x735104),confirmedStart=confirmed.rng;for(let i=0;i<90;i++){harpoonUpdateHojC(confirmed,SIM_FIXED_DT);simStepCounter++;}const confirmedResult=harpoonHojSnapshotC(confirmed);
      const checks={asmTrack:asmResult.mode==='TRACK'&&asmResult.valid,harpoonMaxThreatTrack:maxResult.mode==='TRACK'&&maxResult.valid&&maxResult.guidanceActive,
        confirmedOnlyOff:confirmedResult.enabled===false&&confirmedResult.mode==='OFF'&&!confirmedResult.valid,confirmedOnlyConsumesNoRng:confirmed.rng===confirmedStart,
        harpoonUsesIndependentRng:max.rng!==maxStart,stateObjectsIsolated:asmState.hoj!==max.seeker.hoj&&max.seeker.hoj!==confirmed.seeker.hoj,
        assumedThreat:maxResult.provenance==='ASSUMED_THREAT',noMidcoursePassiveRf:!harpoonUpdateHojC.toString().includes('asmPassiveRfMeasurementB2')};
      return {available:true,mode:SEEKER_U3_HOJ_MODE_C,checks,pass:Object.values(checks).every(Boolean),asmResult,asmAudit,maxThreat:maxResult,confirmedOnly:confirmedResult,
        functionContracts:{common:seekerUpdateHojTrackU3.toString(),harpoon:harpoonUpdateHojC.toString(),guidance:harpoonHojGuidanceActiveC.toString()}};
    }finally{asmHojEmitterSignal=originalSignal;setThreatAssumptionModeC(priorMode);SIM_RNG_STATE=globalBefore;simStepCounter=stepBefore;}
  }
  window.__SEEKER_U3_DIAG__=Object.freeze({cueMatrixB,contractB,hojExerciseC});
})();
