// SEEKER_UNIFY_U3 Commit C: common HOJ angular-track state machine.
const SEEKER_U3_HOJ_MODE_C='__MODE__';
const SEEKER_U3_HOJ_AUDIT_C={comparisons:0,mismatches:0,rngMismatches:0};
function seekerEnsureHojStateU3(s){
  if(!s.hoj)s.hoj={mode:'OFF',valid:false,dwellAccS:0,missAgeS:999,acquireHits:0,ageS:0,
    worldAz:0,worldEl:0,azRate:0,elRate:0,lastDirectJOverN:0,lastPd:0,lastAzSigmaDeg:null,lastElSigmaDeg:null,
    lastRxGain:0,lastNoiseRawW:0,lastDeceptionRawW:0,lastLosQ:0,lastMeasureStep:-1,everTracked:false,everGuidance:false,guidanceSwitches:0,lastGuidanceActive:false,maxDirectJOverN:0};
  return s.hoj;
}
function seekerUpdateHojTrackU3(em,s,p,dt,ports){
  const h=ports.ensure(s);h.ageS+=dt;
  if(h.valid){h.worldAz=angNorm(h.worldAz+h.azRate*dt);h.worldEl=clamp(h.worldEl+h.elRate*dt,-deg(70),deg(70));}
  if(!p.hojEnabled||!ports.enabled()){h.mode='OFF';h.valid=false;h.acquireHits=0;h.missAgeS=999;return h;}
  h.dwellAccS+=dt;const period=1/Math.max(1,p.hojHz??40);if(h.dwellAccS+1e-9<period)return h;h.dwellAccS%=period;
  const sig=ports.signal(em,s,p);h.lastDirectJOverN=sig.directJOverN??0;h.maxDirectJOverN=Math.max(h.maxDirectJOverN??0,h.lastDirectJOverN);h.lastRxGain=sig.rxGain??0;h.lastNoiseRawW=sig.noiseRawW??0;h.lastDeceptionRawW=sig.deceptionRawW??0;h.lastLosQ=sig.losQ??0;
  let accepted=false;
  if(sig.active&&(sig.directJOverN??0)>=Math.max(0.01,p.hojMinDirectJOverN??2)){
    const q=Math.sqrt(clamp(sig.directJOverN,0.15,250)),offPenalty=1+0.9*(1-clamp(sig.rxGain,0,1));
    const sa=Math.max(p.hojMinAzSigmaDeg??0.05,(p.hojBaseAzSigmaDeg??0.36)/q*offPenalty),se=Math.max(p.hojMinElSigmaDeg??0.075,(p.hojBaseElSigmaDeg??0.55)/q*offPenalty);
    const pd=clamp(1-Math.exp(-0.55*sig.directJOverN),0.02,0.999);h.lastPd=pd;h.lastAzSigmaDeg=sa;h.lastElSigmaDeg=se;
    if(ports.uniform()<=pd){
      const mz=angNorm(sig.worldAz+ports.normal()*deg(sa)),me=clamp(sig.worldEl+ports.normal()*deg(se),-deg(70),deg(70));
      if(!h.valid){h.worldAz=mz;h.worldEl=me;h.azRate=0;h.elRate=0;h.valid=true;h.mode='ACQUIRE';h.acquireHits=1;}
      else{
        const a=clamp(p.hojFilterAlpha??0.5,0.05,0.95),b=clamp(p.hojFilterBeta??0.1,0,0.5);
        const ez=angNorm(mz-h.worldAz),ee=me-h.worldEl;h.worldAz=angNorm(h.worldAz+a*ez);h.worldEl=clamp(h.worldEl+a*ee,-deg(70),deg(70));
        h.azRate=clamp(h.azRate+b*ez/Math.max(1e-4,period),-deg(35),deg(35));h.elRate=clamp(h.elRate+b*ee/Math.max(1e-4,period),-deg(25),deg(25));
        if(h.mode==='OFF')h.mode='ACQUIRE';h.acquireHits++;
      }
      h.missAgeS=0;h.lastMeasureStep=simStepCounter;accepted=true;
      if(h.acquireHits>=Math.max(1,p.hojAcquireHits??2)){h.mode='TRACK';h.everTracked=true;h.acquireHits=Math.max(1,p.hojAcquireHits??2);}
    }
  }else{h.lastPd=0;h.lastAzSigmaDeg=null;h.lastElSigmaDeg=null;}
  if(!accepted){
    h.missAgeS+=period;
    if(h.mode==='ACQUIRE'&&h.missAgeS>(p.hojAcquireTimeoutS??0.5)){h.mode='OFF';h.valid=false;h.acquireHits=0;}
    else if(h.mode==='TRACK'&&h.missAgeS>(p.hojCoastAfterS??0.28))h.mode='COAST';
    else if(h.mode==='COAST'&&h.missAgeS>(p.hojLostAfterS??1.35)){h.mode='OFF';h.valid=false;h.acquireHits=0;h.azRate=0;h.elRate=0;}
  }
  return h;
}
function asmUpdateHojTrack(em,s,p,dt){
  const ports={ensure:seekerEnsureHojStateU3,enabled:()=>!!em.seekerOn,signal:asmHojEmitterSignal,uniform:simRandom,normal:randn};
  if(SEEKER_U3_HOJ_MODE_C==='ACTIVE')return seekerUpdateHojTrackU3(em,s,p,dt,ports);
  const rngBefore=SIM_RNG_STATE>>>0,shadow=structuredClone(s);seekerUpdateHojTrackU3(em,shadow,p,dt,{...ports,ensure:seekerEnsureHojStateU3});const rngShadow=SIM_RNG_STATE>>>0;
  SIM_RNG_STATE=rngBefore;const result=asmUpdateHojTrackLegacyU3(em,s,p,dt),rngLegacy=SIM_RNG_STATE>>>0;SEEKER_U3_HOJ_AUDIT_C.comparisons++;
  if(JSON.stringify(shadow.hoj)!==JSON.stringify(s.hoj))SEEKER_U3_HOJ_AUDIT_C.mismatches++;
  if(rngShadow!==rngLegacy)SEEKER_U3_HOJ_AUDIT_C.rngMismatches++;
  return result;
}
function seekerU3HojAuditSnapshotC(){return Object.freeze({mode:SEEKER_U3_HOJ_MODE_C,...SEEKER_U3_HOJ_AUDIT_C,dynamicAuditArrays:0});}
