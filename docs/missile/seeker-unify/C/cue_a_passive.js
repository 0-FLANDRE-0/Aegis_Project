// SEEKER_UNIFY_C Stage 3: anonymous passive-RF bearing/elevation measurements.
// Sensitivities are frozen inversions of the legacy 150/250 km SPY reference:
// Pr=2500 W * .008 m2 /(4*pi*R^2), unity pattern/LOS/weather.
const ASM_PASSIVE_RF_B2_PROFILES=Object.freeze({
  'Kh-35U':Object.freeze({source:'SIM_TUNED',featureProvenance:'PUBLIC_CONFIRMED',referenceRangeKm:150,passiveRxSensitivityW:7.07355302630646e-11,cadenceS:.2,bearingErrorRad:deg(.65),ttlS:.5}),
  'Kh-32':Object.freeze({source:'SIM_TUNED',featureProvenance:'ASSUMED_THREAT',referenceRangeKm:250,passiveRxSensitivityW:2.5464790894703257e-11,cadenceS:.2,bearingErrorRad:deg(.45),ttlS:.5})
});
function asmPassiveEmitterGainA(source,towardRad){
  if(source.beamAz==null)return 1;const off=Math.abs(angNorm(towardRad-source.beamAz));
  if(source.emitterClass==='ACTIVE_SEEKER')return Math.max(.005,Math.exp(-((off/deg(25))**2)));
  if(source.double)return Math.max(.015,Math.exp(-((Math.min(off,Math.abs(Math.PI-off))/deg(35))**2)));
  return Math.max(.015,Math.exp(-((off/deg(35))**2)));
}
function asmPassiveReceiverGainA(em,profile,worldAz,worldEl,boresight){
  const seeker=ASM_SEEKER_PROFILES[em.label]??ASM_SEEKER_PROFILES['Kh-35U'],ha=deg(seeker.searchBeamHalfAzDeg),he=deg(seeker.searchBeamHalfElDeg),az=Math.abs(angNorm(worldAz-boresight.az)),el=Math.abs(angNorm(worldEl-boresight.el));
  const azGain=az<ha?Math.cos(az/ha*Math.PI/2)**2:0,elGain=el<he?Math.cos(el/he*Math.PI/2)**2:0;
  // Existing ASM one-way sidelobe floor; Stage 2's monostatic squaring does not apply to receive-only RF.
  return Math.max(.08,azGain*elGain);
}
function asmCuePredictedAnglesA(em,q,own){
  const dx=q.x[0]-own.posM.x,dy=q.x[1]-own.posM.y,r2=Math.max(1,dx*dx+dy*dy),r=Math.sqrt(r2),Re=ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM,zEff=ASM_CUE_A_SPEC.assumedEmitterHeightM-own.posM.z-r2/(2*Re),el=Math.atan2(zEff,r),Haz=[-dy/r2,dx/r2,0,0],dhdr=(r*(-r/Re)-zEff)/Math.max(1,r2+zEff*zEff),Hel=[dhdr*dx/r,dhdr*dy/r,0,0];
  const variance=H=>{let v=0;for(let i=0;i<4;i++)for(let j=0;j<4;j++)v+=H[i]*q.P[i*4+j]*H[j];return Math.max(0,v);};
  const heightTerm=(r/Math.max(1,r2+zEff*zEff)*ASM_CUE_A_SPEC.assumedEmitterHeightSigmaM)**2;
  return {az:Math.atan2(dy,dx),el,Haz,Hel,varAz:variance(Haz),varEl:variance(Hel)+heightTerm};
}
function asmPassiveDirectRangeEstimateA(elevationRad,elevationSigmaRad,ownHeightM){
  const Re=ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM,t=Math.tan(elevationRad),dh=ASM_CUE_A_SPEC.assumedEmitterHeightM-ownHeightM,disc=t*t+2*dh/Re;
  if(!(disc>0))return {rangeM:null,sigmaM:null};const root=Math.sqrt(disc),roots=[Re*(-t-root),Re*(-t+root)].filter(v=>v>0&&Number.isFinite(v)),rangeM=Math.min(...roots),den=rangeM/Re+t;if(!(rangeM>0)||!Number.isFinite(rangeM)||Math.abs(den)<1e-9)return {rangeM:null,sigmaM:null};
  const sec2=1/Math.max(1e-12,Math.cos(elevationRad)**2),drde=-rangeM*sec2/den,drdh=1/den,sigmaM=Math.hypot(drde*elevationSigmaRad,drdh*ASM_CUE_A_SPEC.assumedEmitterHeightSigmaM);
  return {rangeM,sigmaM:Number.isFinite(sigmaM)?sigmaM:null};
}
function asmPassiveRfMeasurementB2(em){
  const p=ASM_PASSIVE_RF_B2_PROFILES[em.label],timeS=Number(em.life)||0;if(!p||!asmCueFeatureEnabledA(em.label,'passiveRfBearingElevation'))return null;
  const s=em._passiveRfB2??(em._passiveRfB2={nextS:timeS,sequence:0,sample:null,lastAppliedSequence:0});
  if(timeS+1e-9>=s.nextS){
    s.sequence++;s.nextS=timeS+p.cadenceS;const q=asmTargetCuePredictA(em),ownEst=missileNavB2OwnState(em),prediction=asmCuePredictedAnglesA(em,q,ownEst),physical=asmSeekerPhysicalObserverStateB2(em),candidates=[];
    for(const source of electronicPhysicalEmittersF()){
      const dx=worldToMeters(source.point.x)-physical.x,dy=worldToMeters(source.point.y)-physical.y,dz=(Number(source.point.z)||0)-physical.z;if(dx===0&&dy===0&&dz===0)continue;const horizontalM=Math.max(1,Math.hypot(dx,dy)),rangeM=Math.max(100,Math.hypot(dx,dy,dz)),worldAz=Math.atan2(dy,dx),worldEl=Math.atan2(dz,horizontalM)-horizontalM/(2*ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM),los=terrainAwareRadarLOS(em.x,em.y,em.z??0,source.point.x,source.point.y,source.point.z??0);if(los<=.005)continue;
      const txGain=asmPassiveEmitterGainA(source,angNorm(worldAz+Math.PI)),rxGain=asmPassiveReceiverGainA(em,p,worldAz,worldEl,prediction),weather=maritimeRfWeatherPathFactorWip13A3(source.band,rangeM/1000),receivedW=source.power*txGain*.008*rxGain*los*weather/(4*Math.PI*rangeM*rangeM),snr=receivedW/p.passiveRxSensitivityW;if(!(snr>=1))continue;
      const bearingSigmaRad=p.bearingErrorRad*Math.sqrt(1+1/Math.max(1,snr)),elevationSigmaRad=bearingSigmaRad*(1+.75*Math.exp(-Math.abs(worldEl)/deg(2))),Sa=Math.max(1e-12,prediction.varAz+bearingSigmaRad**2),Se=Math.max(1e-12,prediction.varEl+elevationSigmaRad**2),dAz=angNorm(worldAz-prediction.az),dEl=angNorm(worldEl-prediction.el),d2=dAz*dAz/Sa+dEl*dEl/Se;if(d2>ASM_CUE_A_SPEC.basketSigma**2)continue;
      candidates.push({source,worldAz,worldEl,snr,bearingSigmaRad,elevationSigmaRad,d2,receivedW,txGain,rxGain,los});
    }
    candidates.sort((a,b)=>a.d2-b.d2);const best=candidates[0];
    if(best){
      const bearingRad=angNorm(best.worldAz+_samB1HashSigned(em,0x6e51,s.sequence)*best.bearingSigmaRad),elevationRad=angNorm(best.worldEl+_samB1HashSigned(em,0x6e52,s.sequence)*best.elevationSigmaRad),direct=asmPassiveDirectRangeEstimateA(elevationRad,best.elevationSigmaRad,ownEst.posM.z);
      s.sample={source:'PASSIVE_RF_CUE_A',sequence:s.sequence,sampleTimeS:timeS,available:true,bearingRad,elevationRad,snr:best.snr,bearingSigmaRad:best.bearingSigmaRad,elevationSigmaRad:best.elevationSigmaRad,confidence:clamp(best.snr/(best.snr+1),0,1),emitterClass:String(best.source.emitterClass||'UNKNOWN'),band:String(best.source.band||'IJ'),directRangeEstimateM:direct.rangeM,directRangeSigmaM:direct.sigmaM};
      s.lastSynthesis={candidateCount:candidates.length,selectedGateD2:best.d2,receivedW:best.receivedW,txGain:best.txGain,rxGain:best.rxGain,los:best.los};
    }else{s.sample={source:'PASSIVE_RF_CUE_A',sequence:s.sequence,sampleTimeS:timeS,available:false,bearingRad:null,elevationRad:null,snr:0,bearingSigmaRad:null,elevationSigmaRad:null,confidence:0,emitterClass:null,band:null,directRangeEstimateM:null,directRangeSigmaM:null};s.lastSynthesis={candidateCount:0,selectedGateD2:null};}
  }
  return s.sample&&timeS-s.sample.sampleTimeS<=p.ttlS?{...s.sample}:null;
}
function asmApplyPassiveBearingB2(em,dt){
  // TARGET_MEMORY_CONSUMER: anonymous bearing/elevation only. The optional range
  // value is measurement-derived diagnostic output and never overwrites cue range.
  if(em._c52InsMemory)return false;const meas=asmPassiveRfMeasurementB2(em),state=em._passiveRfB2;if(!meas?.available||state.lastAppliedSequence===meas.sequence)return false;
  state.lastAppliedSequence=meas.sequence;return !!asmCueAngularUpdateA(em,meas).ok;
}
function asmTargetMemoryDriftB2(em,amplitudeWorld){
  // CUE_A process covariance replaces the old deterministic point drift. It is
  // fixed-dt, consumes no RNG, and cannot modify the frozen C52 memory path.
  if(!em._c52InsMemory)asmTargetCuePredictA(em);
}

window.__ASM_CUE_A__=Object.freeze({
  schema:ASM_CUE_A_SPEC.schema,spec:ASM_CUE_A_SPEC,featureProvenance:ASM_CUE_FEATURE_PROVENANCE_A,features:ASM_CUE_FEATURES_A,
  mode:()=>THREAT_ASSUMPTION_MODE,setMode:setThreatAssumptionModeC,enabledAssumptions:()=>asmCueEnabledAssumptionsA().map(q=>({...q})),
  snapshot:missileId=>{const em=enemyMissiles.find(q=>String(q.id)===String(missileId));return em?asmTargetCueSnapshotA(em):null;},
  cueUpdate:(missileId,packet)=>{const em=enemyMissiles.find(q=>String(q.id)===String(missileId));return em?asmCueUpdateA(em,packet):{ok:false,reason:'MISSILE_NOT_FOUND'};},
  passiveProfile:label=>ASM_PASSIVE_RF_B2_PROFILES[label]?{...ASM_PASSIVE_RF_B2_PROFILES[label]}:null,
  truthOutput:false,dlConnected:false,rng:'ISOLATED_DETERMINISTIC_HASH'
});
