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
    const nominalCovarianceBasketM=ASM_CUE_A_SPEC.basketSigma*harpoonCueHorizontalSigmaB(packet?.P).majorSigmaM,
      checks={packetMapped:!!packet&&packet.x[0]===nominal.positionM.x&&packet.x[1]===nominal.positionM.y&&packet.x[2]===nominal.velocityMps.x&&packet.x[3]===nominal.velocityMps.y,
      allFinite:horizons.every(q=>Number.isFinite(q.searchBasketM)&&Number.isFinite(q.predictionSigmaM)),covarianceGrows:horizons.at(-1).searchBasketM>horizons[0].searchBasketM,
      legacy250mFloorRestored:nominalCovarianceBasketM===225&&horizons[0].searchBasketM===250&&HARPOON_CUE_B_SPEC.trackBasketFloorM===250,
      fixed4kmRemoved:overOld.searchBasketM>4000&&overOld.feasible,physicalLimitRetained:overPhysical.searchBasketM>overPhysical.physicalSearchLimitM&&!overPhysical.feasible,
      routePriorIsNotObservation:route.source==='ROUTE_PLAN_PRIOR'&&route.observationUpdate===false&&route.searchBasketM===HARPOON_PROFILE_A.sim.seekerSearchBasketM&&harpoonCuePacketB(routeMemory())===null,
      missingRejected:missing.feasible===false&&missing.reason==='INS_PREDICTION_BASKET_INSUFFICIENT',deterministic:JSON.stringify(repeatA)===JSON.stringify(repeatB),
      noTruthFields:[...Object.keys(packet??{}),...Object.keys(repeatA)].every(k=>!/(entity|targetId|truthPosition|physicalId)/i.test(k))&&repeatA.truthUsed===false};
    return {schema:'AEGIS_SEEKER_UNIFY_U3_B_DIAGNOSTIC_2',spec:HARPOON_CUE_B_SPEC,checks,pass:Object.values(checks).every(Boolean),packet,nominalCovarianceBasketM,horizons,overOld,overPhysical,route,missing,coreAudits:{harpoon:harpoonCoreAuditA(),seeker:harpoonSeekerCoreAuditC()}};
  }
  function contractB(){return {spec:HARPOON_CUE_B_SPEC,packet:harpoonCuePacketB.toString(),predict:harpoonCuePredictB.toString(),handoff:harpoonCueHandoffB.toString(),routeProgram:harpoonRouteProgramE.toString(),routeGate:harpoonRouteGateE.toString(),gate:harpoonGateA.toString(),seeker:harpoonSeekerA.toString(),journal:harpoonJournalReleaseF1.toString(),attackGuard:attackPathGuardH3.toString()};}
  function covarianceFixtureB(tr,posSigmaM){
    const P=Array.from(tr._kfP),indices=[0,1,3,4];
    for(const r of indices)for(const c of indices)P[r*6+c]=0;
    P[0]=P[7]=posSigmaM**2;P[21]=P[28]=.01**2;tr._kfP=P;return P;
  }
  function scanBoundsForGateB(m,gateM){
    const s=m.seeker,cfg=HARPOON_PROFILE_A.sim,nav=m.ins,pred=harpoonPredictionA(m.memory,m.ageS,m.navPositionM),time=harpoonMemoryElapsedC(m.memory,m.ageS),
      memoryNow={x:m.memory.positionM.x+m.memory.velocityMps.x*time,y:m.memory.positionM.y+m.memory.velocityMps.y*time},track=s.lock??s.candidate,
      cue=track?{x:track.x+track.vx*s.missedS,y:track.y+track.vy*s.missedS}:memoryNow,rangeToBasket=Math.hypot(pred.x-m.navPositionM.x,pred.y-m.navPositionM.y),
      desired=angNorm(Math.atan2(cue.y-m.navPositionM.y,cue.x-m.navPositionM.x)-nav.yawRad),half=Math.min(cfg.seekerGimbalRad,Math.max(cfg.seekerMinSweepRad,Math.atan2(gateM,Math.max(1000,rangeToBasket))));
    return {lo:clamp(desired-half,-cfg.seekerGimbalRad,cfg.seekerGimbalRad),hi:clamp(desired+half,-cfg.seekerGimbalRad,cfg.seekerGimbalRad),desired,half,rangeToBasket};
  }
  function attackGuardConsumerB(gate){
    const launcher=attackLauncherMaskH3,chart=attackChartGuardH3,protectedFn=attackProtectedH3,start=gate.muzzleM,p=gate.memory.positionM,v=gate.memory.velocityMps;
    let t=Math.hypot(p.x-start.x,p.y-start.y)/HARPOON_PROFILE_A.sim.cruiseSpeedMps;
    for(let i=0;i<4;i++)t=Math.hypot(p.x+v.x*t-start.x,p.y+v.y*t-start.y)/HARPOON_PROFILE_A.sim.cruiseSpeedMps;
    const end={x:p.x+v.x*t,y:p.y+v.y*t},dx=end.x-start.x,dy=end.y-start.y,d=Math.max(1,Math.hypot(dx,dy)),axis={x:dx/d,y:dy/d,z:.2},sigma=.5*.04*t*t,
      dynamicThreshold=gate.searchBasketM+ATTACK_POLICY_H3.protectedMarginM+sigma,fixedThreshold=HARPOON_PROFILE_A.sim.seekerSearchBasketM+ATTACK_POLICY_H3.protectedMarginM+sigma,
      distance=.5*(dynamicThreshold+fixedThreshold),row={x:end.x+axis.x*distance,y:end.y+axis.y*distance,vx:0,vy:0,P:new Array(36).fill(0),ageS:0,source:'DIAGNOSTIC_OBSERVED_PROTECTED'};
    try{
      attackLauncherMaskH3=()=>({ok:true});attackChartGuardH3=()=>({ok:true});attackProtectedH3=()=>({rows:[row],blocked:null});
      const dynamic=attackPathGuardH3(ACTIVE_SHIP_RUNTIME,{...gate,axis}),fixedFallback=attackPathGuardH3(ACTIVE_SHIP_RUNTIME,{...gate,axis,searchBasketM:undefined}),dynamicWider=gate.searchBasketM>HARPOON_PROFILE_A.sim.seekerSearchBasketM,
        pass=dynamicWider?!dynamic.ok&&fixedFallback.ok:dynamic.ok&&!fixedFallback.ok;
      return {pass,dynamicWider,dynamicSearchBasketM:gate.searchBasketM,fallbackSearchBasketM:HARPOON_PROFILE_A.sim.seekerSearchBasketM,distance,dynamicThreshold,fixedThreshold,dynamic,fixedFallback};
    }finally{attackLauncherMaskH3=launcher;attackChartGuardH3=chart;attackProtectedH3=protectedFn;}
  }
  function launchFlowB(options={}){
    const d=window.__NAVAL_SIM_DIAG__,rangeKm=Number(options.rangeKm??8),posSigmaM=Number(options.posSigmaM??75),stale=options.stale===true;
    d.setEmcon(false);d.createWip13aSurfaceTargetFixture({entityId:'U3_B_GENERAL_TRACK',rangeKm,bearingDeg:0,headingDeg:90,speedKt:8});
    const sensorRun=d.wip13b9StepSurfaceSensors(1200),row=sensorRun.audit.surfaceTracks.find(q=>q.confirmed)??sensorRun.audit.surfaceTracks[0],trackId=row?.trackId,tr=tracks.get(Number(trackId));
    if(!tr)return {schema:'AEGIS_SEEKER_UNIFY_U3_B_LAUNCH_FLOW_1',pass:false,reason:'NO_CONFIRMED_SURFACE_TRACK',sensorRun};
    d.a3SetOperatorIdentity(trackId,'TRAINING_TARGET');covarianceFixtureB(tr,posSigmaM);
    let staleEvidence=null;
    if(stale){
      const ticks=Math.ceil((HARPOON_PROFILE_A.sim.maxTrackAgeS+.25)/SIM_FIXED_DT),dropout=d.wip13b9StepSurfaceSensors(ticks,{spy:false,spq:false,bme:false}),coasted=tracks.get(Number(trackId));
      staleEvidence={ticks,dropoutMask:dropout.mask,trackRetained:!!coasted,sensorAge:coasted?.sensorAge??null,maxTrackAgeS:HARPOON_PROFILE_A.sim.maxTrackAgeS};
    }
    const tubeId=harpoonRuntimeA().tubes.find(q=>q.loaded)?.id??null,gate=harpoonGateA(trackId,tubeId,{});
    if(stale){
      const pending=harpoonRuntimeA().pending,pass=!gate.ok&&gate.reason==='SURFACE_TRACK_COAST_EXPIRED'&&staleEvidence.trackRetained&&staleEvidence.sensorAge>staleEvidence.maxTrackAgeS&&!pending;
      return {schema:'AEGIS_SEEKER_UNIFY_U3_B_LAUNCH_FLOW_1',case:'STALE_GENERAL_TRACK',pass,trackId,tubeId,staleEvidence,gate,pendingCreated:!!pending,routePriorUsed:false};
    }
    if(!gate.ok)return {schema:'AEGIS_SEEKER_UNIFY_U3_B_LAUNCH_FLOW_1',case:'FRESH_GENERAL_TRACK',pass:false,reason:'GATE_REJECTED',trackId,tubeId,gate};
    const attackConsumer=attackGuardConsumerB(gate),request=harpoonRequestFireA(trackId,tubeId),maxReleaseTicks=Math.ceil((HARPOON_PROFILE_A.sim.releaseDoorDelayS+1)/SIM_FIXED_DT);let missile=null,releaseTicks=0;
    for(;releaseTicks<maxReleaseTicks&&!missile;releaseTicks++){harpoonStepA(SIM_FIXED_DT);simStepCounter++;missile=harpoonWorldA().at(-1)??null;}
    if(!missile)return {schema:'AEGIS_SEEKER_UNIFY_U3_B_LAUNCH_FLOW_1',case:'FRESH_GENERAL_TRACK',pass:false,reason:'NO_ACTUAL_RELEASE',trackId,tubeId,gate,request,attackConsumer,releaseTicks};
    const releaseCue={...missile.cueHandoff},releaseRoute=missile.route;let seekerTicks=0,maxSeekerTicks=Math.ceil((HARPOON_PROFILE_A.sim.boosterBurnS+3)/SIM_FIXED_DT);
    for(;seekerTicks<maxSeekerTicks&&!missile.seeker.active&&missile.alive;seekerTicks++){harpoonStepA(SIM_FIXED_DT);simStepCounter++;}
    // Re-evaluate the live seeker at the post-step state without advancing time.
    // An empty diagnostic observation list prevents a target-return side effect;
    // scanBoundsRad still comes from the production cueHandoff consumer.
    if(missile.seeker.active)harpoonSeekerA(missile,0,[]);
    const dynamicBounds=scanBoundsForGateB(missile,releaseCue.searchBasketM),fixedBounds=scanBoundsForGateB(missile,HARPOON_PROFILE_A.sim.seekerSearchBasketM),actual=missile.seeker.scanBoundsRad,
      close=(a,b)=>Math.abs(a-b)<=1e-10,seekerConsumer={active:missile.seeker.active,actual:[...actual],dynamic:[dynamicBounds.lo,dynamicBounds.hi],fixed4000:[fixedBounds.lo,fixedBounds.hi],
        dynamicMatch:close(actual[0],dynamicBounds.lo)&&close(actual[1],dynamicBounds.hi),distinctFromFixed4000:!close(actual[0],fixedBounds.lo)||!close(actual[1],fixedBounds.hi),rangeToBasket:dynamicBounds.rangeToBasket},
      expectedBasket=Math.max(HARPOON_CUE_B_SPEC.trackBasketFloorM,ASM_CUE_A_SPEC.basketSigma*posSigmaM),
      pass=request.ok&&request.pending&&releaseRoute===null&&gate.cueHandoff.source==='LOCAL_SURFACE_OBSERVATION'&&gate.cueHandoff.observationUpdate===true&&
        Math.abs(gate.searchBasketM-expectedBasket)<1e-8&&Math.abs(releaseCue.searchBasketM-gate.searchBasketM)<1e-8&&releaseCue.source==='LOCAL_SURFACE_OBSERVATION'&&
        attackConsumer.pass&&seekerConsumer.active&&seekerConsumer.dynamicMatch&&seekerConsumer.distinctFromFixed4000;
    return {schema:'AEGIS_SEEKER_UNIFY_U3_B_LAUNCH_FLOW_1',case:posSigmaM>1000?'LARGE_COVARIANCE_GENERAL_TRACK':'FLOOR_GENERAL_TRACK',pass,trackId,tubeId,posSigmaM,expectedBasket,
      gate:{ok:gate.ok,reason:gate.reason,searchBasketM:gate.searchBasketM,predictionSigmaM:gate.predictionSigmaM,cueSource:gate.cueHandoff.source,observationUpdate:gate.cueHandoff.observationUpdate,physicalSearchLimitM:gate.cueHandoff.physicalSearchLimitM},
      request,releaseTicks,missileId:missile.id,releaseCue,releaseRouteUsed:releaseRoute!==null,attackConsumer,seekerTicks,seekerConsumer,routePriorUsed:false};
  }
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
  function passiveSelectionD(){
    if(typeof seekerU3PassiveRfSelectionD!=='function')return {available:false};
    const candidate=(overrides={})=>({family:'SHIP SEARCH RADAR',emitterClass:'SEARCH_RADAR',band:'IJ',frequencyMHz:10000,frequencyProvenance:'DIAGNOSTIC_OBSERVATION',
      worldAz:.1,worldEl:-.02,snr:12,bearingSigmaRad:.01,elevationSigmaRad:.015,d2:.3,innovationDet:1e-4,selectionScore:.3+Math.log(1e-4),receivedW:1e-8,txGain:1,rxGain:1,los:1,...overrides});
    const broad=candidate({family:'BROAD_UNCERTAINTY',d2:.2,innovationDet:1e-2,selectionScore:.2+Math.log(1e-2),frequencyMHz:11000}),
      precise=candidate({family:'PRECISE_OBSERVATION',d2:.8,innovationDet:1e-8,selectionScore:.8+Math.log(1e-8),frequencyMHz:9000}),
      policy=seekerU3PassiveRfSelectionD([broad,precise]),tieA=candidate({family:'TIE_A',d2:.5,innovationDet:1e-6,selectionScore:.5+Math.log(1e-6),frequencyMHz:10000}),
      tieB=candidate({family:'TIE_B',d2:.5,innovationDet:1e-6,selectionScore:.5+Math.log(1e-6),frequencyMHz:9000}),
      tieForward=seekerU3PassiveRfSelectionD([tieA,tieB]),tieReverse=seekerU3PassiveRfSelectionD([tieB,tieA]),audit=seekerU3PassiveRfAuditSnapshotD();
    const selected=seekerU3PassiveRfObservableSignatureD(policy.selected),ranked=seekerU3PassiveRfObservableSignatureD(policy.ranked),legacy=seekerU3PassiveRfObservableSignatureD(policy.legacy),
      tieForwardSignature=seekerU3PassiveRfObservableSignatureD(tieForward.ranked),tieReverseSignature=seekerU3PassiveRfObservableSignatureD(tieReverse.ranked);
    const checks={legacyPrefersLowerD2:legacy.family==='BROAD_UNCERTAINTY',newPolicyPrefersLowerScore:ranked.family==='PRECISE_OBSERVATION',
      activeOrShadowOutput:SEEKER_U3_PASSIVE_RF_MODE_D==='ACTIVE'?selected.family==='PRECISE_OBSERVATION':selected.family==='BROAD_UNCERTAINTY',
      formulaExact:ranked.selectionScore===ranked.d2+Math.log(ranked.innovationDet),deterministicTie:JSON.stringify(tieForwardSignature)===JSON.stringify(tieReverseSignature)&&tieForwardSignature.frequencyMHz===9000,
      observableOnly:Object.keys(ranked).every(key=>!/(sourceId|entityId|platformId|truth|point|position)/i.test(key)),rngFree:audit.rngConsumed===false&&audit.truthFieldsUsed===false};
    return {available:true,mode:SEEKER_U3_PASSIVE_RF_MODE_D,checks,pass:Object.values(checks).every(Boolean),legacy,ranked,selected,tieForward:tieForwardSignature,tieReverse:tieReverseSignature,audit};
  }
  function passiveAuditD(){return typeof seekerU3PassiveRfAuditSnapshotD==='function'?seekerU3PassiveRfAuditSnapshotD():null;}
  window.__SEEKER_U3_DIAG__=Object.freeze({cueMatrixB,contractB,launchFlowB,hojExerciseC,passiveSelectionD,passiveAuditD});
})();
