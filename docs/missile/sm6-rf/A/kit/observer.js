// DIAGNOSTIC ONLY. Inject into a disposable page after live-fixture.js.
// Native mode only observes. Counterfactual modes change an adapter return,
// never the receiver state, signal detections, physical limits, or production file.
let SM6_RF_DIAG_MODE = 'NATIVE';
let SM6_RF_DIAG_ROWS = [];
let SM6_RF_DIAG_MEM = new WeakMap();
const SM6_RF_DIAG_MODES = new Set(['NATIVE','IDEAL_ARH_VALUES_REAL_VALIDITY','WITHHOLD_ARH_AUTHORITY']);
const sm6DiagCopy = v => v == null ? null : JSON.parse(JSON.stringify(v));
function sm6DiagMemo(m) {
  let q=SM6_RF_DIAG_MEM.get(m);
  if(!q){q={calls:{},last:{}};SM6_RF_DIAG_MEM.set(m,q);}
  return q;
}
function sm6DiagMark(m,name,value) {
  const q=sm6DiagMemo(m),old=q.calls[name];
  q.calls[name]={atS:m.life,count:old?.atS===m.life?old.count+1:1};
  q.last[name]={atS:m.life,value:sm6DiagCopy(value)};
}
function sm6DiagTarget() {
  // Truth is confined to read-only diagnostics and the explicitly named
  // ideal-observation counterfactual. Never copy it into a shipping controller.
  return targetPool.find(t=>t?._testFixture) ?? null;
}
function sm6DiagTruth(m) {
  const t=sm6DiagTarget();if(!t)return null;
  const p={x:worldToMeters(t.x),y:worldToMeters(t.y),z:t.z??0};
  const v={x:worldSpeedToMps(t.vx??0),y:worldSpeedToMps(t.vy??0),z:t.vz??0};
  const ownP={x:worldToMeters(m.x),y:worldToMeters(m.y),z:m.z??0};
  const ownV={x:worldSpeedToMps(m.vx??0),y:worldSpeedToMps(m.vy??0),z:m.vz??0};
  return {targetPosM:p,targetVelMps:v,ownPosM:ownP,ownVelMps:ownV,
    relativePosM:{x:p.x-ownP.x,y:p.y-ownP.y,z:p.z-ownP.z},
    relativeVelMps:{x:v.x-ownV.x,y:v.y-ownV.y,z:v.z-ownV.z}};
}
function sm6DiagVectorError(a,b) {
  if(!a||!b)return null;const x=a.x-b.x,y=a.y-b.y,z=a.z-b.z;
  return [x,y,z].every(Number.isFinite)?{x,y,z,magnitude:Math.hypot(x,y,z)}:null;
}
function sm6DiagState(st,m) {
  if(!st)return null;
  const truth=sm6DiagTruth(m),own=st.selfStateM;
  const relativePos=st.posM&&own?.posM?{x:st.posM.x-own.posM.x,y:st.posM.y-own.posM.y,z:st.posM.z-own.posM.z}:null;
  const relativeVel=st.velMps&&own?.velMps?{x:st.velMps.x-own.velMps.x,y:st.velMps.y-own.velMps.y,z:st.velMps.z-own.velMps.z}:null;
  return {isValid:st.isValid,source:st.source,confidence:st.confidence,
    canAcquireAuthority:st.canAcquireAuthority,canHoldAuthority:st.canHoldAuthority,
    posM:sm6DiagCopy(st.posM),velMps:sm6DiagCopy(st.velMps),
    latencySec:st.latencySec,noiseSigmaM:st.noiseSigmaM,qualityNotes:st.qualityNotes,
    relativePositionErrorM:sm6DiagVectorError(relativePos,truth?.relativePosM),
    relativeVelocityErrorMps:sm6DiagVectorError(relativeVel,truth?.relativeVelMps),
    comparisonFrame:own?'ONBOARD_RELATIVE_MINUS_PHYSICAL_RELATIVE':'NO_OWN_STATE_ERROR_NOT_COMPUTED'};
}
function sm6DiagReceiver(s,m) {
  if(!s)return null;const truth=sm6DiagTruth(m),x=s._kfX,P=s._kfP;
  return {mode:s.mode,valid:s.trackValid,confidence:s.confidence,hitAgeS:s.lastHitAgeS,
    missAgeS:s.missAgeS,timeS:s.timeS,dwellAccS:s.dwellAccS,
    x:x?Array.from(x):null,covarianceDiagonal:P?[0,7,14,21,28,35].map(i=>P[i]):null,
    rawWorldPositionErrorM:x?sm6DiagVectorError({x:x[0],y:x[1],z:x[2]},truth?.targetPosM):null,
    rawWorldVelocityErrorMps:x?sm6DiagVectorError({x:x[3],y:x[4],z:x[5]},truth?.targetVelMps):null,
    servoCmdAz:s.servoCmdAz,servoCmdEl:s.servoCmdEl,
    lastNisCached:s.lastNis,lastSnrCached:s.lastSnr,lastPdCached:s.lastPd,
    lastRawEchoCount:s.lastRawEchoCount,lastFrontendEchoCount:s.lastFrontendEchoCount,
    lastClusterCount:s.lastClusterCount,lastCandidateCount:s.lastCandidateCount,
    lastValidatedCandidateCount:s.lastValidatedCandidateCount,
    lastRejectedLowEvidence:s.lastRejectedLowEvidence,
    acquireHits:s.acquireHits,reacquireHits:s.reacquireHits};
}
function sm6DiagSnapshot(m) {
  const q=sm6DiagMemo(m),truth=sm6DiagTruth(m);
  const calls=Object.fromEntries(Object.entries(q.calls).map(([k,v])=>[k,{...v,calledThisTick:v.atS===m.life}]));
  return {lifeS:m.life,truth,rangeM:truth?Math.hypot(truth.relativePosM.x,truth.relativePosM.y,truth.relativePosM.z):null,
    phase:m._v1GuidancePhase,owner:m._v1LaunchControlAuthority?'LAUNCH':m._wip79KappaActive?'KAPPA':m._v1TerminalActive?'TERMINAL':'OTHER_OR_FALLBACK',
    pitchover:!!m.pitchoverPhase,handoffAtS:m._pitchoverCompleteAt??null,
    selectedState:sm6DiagState(m._v1TargetState,m),
    sourceArbiter:m._v1SourceArb?{current:m._v1SourceArb.current,sourceAgeS:m._v1SourceArb.sourceAgeS,
      candidate:m._v1SourceArb.candidate,candidateAgeS:m._v1SourceArb.candidateAgeS,
      switchCount:m._v1SourceArb.switchCount,lastSwitchReason:m._v1SourceArb.lastSwitchReason}:null,
    arh:sm6DiagReceiver(m._arhRfSeeker,m),sarh:sm6DiagReceiver(m._sarhRfSeeker,m),
    seeker:{az:m.seekerAngle,el:m.seekerEl,heading:m.heading,pitch:m.pitch},
    calls,last:q.last};
}
const sm6DiagOriginal = {
  adapter:getArhTargetStateV1,selected:getGuidanceTargetStateV1,
  associate:_arhAssociateMeasurements,ekfUpdate:_arhEkfUpdate,
  pn:computeTruePN3D,apn:computeAPNCorrectionV1,zem:computeZEMCorrectionV1,
  kappa:computeKappaMidcourseAccelV2,bridge:applyAccelCommandToAutopilotV1,
  dynamics:updateSamSixDofLiteDynamics
};
getArhTargetStateV1=function(m,...args) {
  const original=sm6DiagOriginal.adapter(m,...args);
  let effective=original;
  if(m.isSM6&&SM6_RF_DIAG_MODE==='WITHHOLD_ARH_AUTHORITY'&&original) {
    effective={...original,canAcquireAuthority:false,canHoldAuthority:false};
  } else if(m.isSM6&&SM6_RF_DIAG_MODE==='IDEAL_ARH_VALUES_REAL_VALIDITY'&&original?.isValid&&original.posM&&original.velMps) {
    const t=sm6DiagTruth(m);
    if(t)effective={...original,posM:{...t.targetPosM},velMps:{...t.targetVelMps}};
  }
  sm6DiagMark(m,'arhAdapter',{original:sm6DiagState(original,m),effective:sm6DiagState(effective,m)});
  return effective;
};
getGuidanceTargetStateV1=function(m,...args) {
  const out=sm6DiagOriginal.selected(m,...args);
  sm6DiagMark(m,'selected',sm6DiagState(out,m));return out;
};
_arhAssociateMeasurements=function(m,s,measurements,rx,cue) {
  const out=sm6DiagOriginal.associate(m,s,measurements,rx,cue);
  sm6DiagMark(m,'association',{measurementCount:measurements?.length??0,selected:out?{
    rangeM:out.rangeM,azRad:out.azRad,elRad:out.elRad,dopplerPathRateMps:out.dopplerPathRateMps,
    rangeSigmaM:out.rangeSigmaM,azSigmaDeg:out.azSigmaDeg,elSigmaDeg:out.elSigmaDeg,dopplerSigmaMps:out.dopplerSigmaMps,
    snr:out.snr,pd:out.pd,targetEvidence:out.targetEvidence,classification:out.classification,
    decoyLikelihood:out.decoyLikelihood,trackCoherence:out.trackCoherence}:null,
    selectedNis:out?s.lastNis:null,rejectedLowEvidence:s.lastRejectedLowEvidence,
    validatedCandidateCount:s.lastValidatedCandidateCount});
  return out;
};
_arhEkfUpdate=function(s,meas,m,rx,cue) {
  const before=sm6DiagReceiver(s,m),out=sm6DiagOriginal.ekfUpdate(s,meas,m,rx,cue);
  sm6DiagMark(m,'ekfUpdate',{accepted:out,before,after:sm6DiagReceiver(s,m)});
  return out;
};
computeTruePN3D=function(m,...args){const out=sm6DiagOriginal.pn(m,...args);sm6DiagMark(m,'pn',out);return out;};
computeAPNCorrectionV1=function(m,...args){const out=sm6DiagOriginal.apn(m,...args);sm6DiagMark(m,'apn',out);return out;};
computeZEMCorrectionV1=function(m,...args){const out=sm6DiagOriginal.zem(m,...args);sm6DiagMark(m,'zem',out);return out;};
computeKappaMidcourseAccelV2=function(m,...args){const out=sm6DiagOriginal.kappa(m,...args);sm6DiagMark(m,'kappa',out);return out;};
applyAccelCommandToAutopilotV1=function(m,cmd,dt) {
  const out=sm6DiagOriginal.bridge(m,cmd,dt);
  sm6DiagMark(m,'bridge',{input:cmd,output:out,rawG:m._v1GCommand,limitedG:m._v1GAchieved,
    commandDirection:m._v1ControlCommandVec});
  return out;
};
updateSamSixDofLiteDynamics=function(m,dt,yaw,pitch,env) {
  const record=m===TERM_LIVE_LAST_MISSILE_A&&(m.life<8||m.life>=135);
  const before=record?sm6DiagCopy(sm6DiagSnapshot(m)):null;
  const out=sm6DiagOriginal.dynamics(m,dt,yaw,pitch,env);
  if(record)SM6_RF_DIAG_ROWS.push(sm6DiagCopy({
    timeS:m.life,dtS:dt,worldStep:simStepCounter,mode:SM6_RF_DIAG_MODE,
    comparisonBoundary:'PRE_DYNAMICS_CURRENT_WORLD; compare tracking errors in before, not post-step physical positions',
    before,afterPhysical:{ownPosM:{x:worldToMeters(m.x),y:worldToMeters(m.y),z:m.z??0},
      ownVelMps:{x:worldSpeedToMps(m.vx??0),y:worldSpeedToMps(m.vy??0),z:m.vz??0}},
    finalInput:{yaw,pitch},speedMps:Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0),
    physical:{availableG:m.availableG,actualNormalG:m.sam6dofActualNormalG,deliveredG:m.sam6dofDeliveredG,
      normalAccelerationWorld:m._samPrevNormalAccWorld,finYaw:m.finYaw,finPitch:m.finPitch,
      aero:m.sam6dofDebug,env:{massKg:env?.massKg,thrustN:env?.thrustN,qPa:env?.qPa,rhoKgM3:env?.rhoKgM3,mach:env?.mach}}
  }));
  return out;
};
window.__SM6_RF_CAUSAL_DIAG__={
  configure(mode){if(!SM6_RF_DIAG_MODES.has(mode))throw Error('UNKNOWN_DIAGNOSTIC_MODE');SM6_RF_DIAG_MODE=mode;SM6_RF_DIAG_ROWS=[];SM6_RF_DIAG_MEM=new WeakMap();},
  read(){return SM6_RF_DIAG_ROWS;},
  metadata(){return {schema:'SM6_240KM_RF_CAUSAL_DIAGNOSTIC_1',mode:SM6_RF_DIAG_MODE,rows:SM6_RF_DIAG_ROWS.length,
    note:'Counterfactuals are diagnostic adapter changes. Never ship. Raw NIS/SNR are marked cached unless a fresh call is logged.'};}
};

