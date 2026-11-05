// CUE_A-1 TEST_ONLY diagnostics. No object created here is inserted into the
// game world, and no after-action truth enters the product filter.
(() => {
  function fixture(label='Kh-35U',known=false,rangeM=100000,speedMps=15,positionSigmaM=300){
    const em={id:981001,label,life:0,insTgtX:metersToWorld(rangeM),insTgtY:0};
    em._cueLaunchA={source:'DIAGNOSTIC_OBSERVATION',positionM:{x:rangeM,y:0},velocityMps:known?{x:speedMps,y:0}:null,
      covariance:{positionSigmaM,velocitySigmaMps:known?1:ASM_CUE_A_SPEC.unknownVelocityAxisSigmaMps},timeS:0};
    return em;
  }
  function runVelocityTickCase(options={}){
    const label=String(options.label??'Kh-35U'),known=!!options.known,seconds=Math.max(0,Number(options.seconds)||0),rangeM=Math.max(1,Number(options.rangeM)||100000),speedMps=Math.max(0,Number(options.speedMps)||15),em=fixture(label,known,rangeM,speedMps),ticks=Math.round(seconds/SIM_FIXED_DT);
    const initial=asmTargetCueSnapshotA(em);for(let i=1;i<=ticks;i++){em.life=i*SIM_FIXED_DT;asmTargetCuePredictA(em);}
    const basket=asmCueBasketU0(em,{x:0,y:0,z:10},ASM_SEEKER_PROFILES[label]),final=asmTargetCueSnapshotA(em);
    return {setup:{label,known,seconds,rangeM,speedMps,ticks,dt:SIM_FIXED_DT},initial,final,
      sigma:{positionM:Math.sqrt(final.covariance[0]),velocityMps:Math.sqrt(final.covariance[14]),accelerationMps2:Math.sqrt(final.covariance[28])},
      basket:{capM:basket.capM,rangeHalfM:basket.rangeHalfM,rangeHalfLimiter:basket.rangeHalfLimiter,azHalfDeg:basket.azHalfRad*180/Math.PI,azHalfLimiter:basket.azHalfLimiter,rangeSigmaM:basket.rangeSigmaM,crossSigmaM:basket.crossSigmaM}};
  }
  function runCapReferenceCase(){
    const em=fixture('Kh-35U',false,100000,15);em.life=10;asmTargetCuePredictA(em);const initial=asmTargetCueSnapshotA(em);
    asmCueUpdateA(em,{source:'PASSIVE_RF',velocityMps:{x:2,y:1},covariance:{velocitySigmaMps:2},timeS:10});const passive=asmTargetCueSnapshotA(em);
    asmCueUpdateA(em,{source:'DL',positionM:{x:100100,y:50},covariance:{positionSigmaM:75},timeS:10});const dl=asmTargetCueSnapshotA(em);
    return {initial,passive,dl};
  }
  function runDeterministicBatch(options){return options.map(runVelocityTickCase);}
  window.__CUE_A1_STAGE1B_DIAG__=Object.freeze({runVelocityTickCase,runCapReferenceCase,runDeterministicBatch});
})();
