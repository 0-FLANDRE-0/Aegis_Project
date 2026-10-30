// TEST_ONLY read-only measurement wrappers. Never embedded into the game HTML.
let diagCaseA=null;
const diagFuzeNativeA=_wip99Stage2CandidateDecision;
_wip99Stage2CandidateDecision=function(m,t,x,y,z,dot,rcs){
 const q=diagFuzeNativeA(m,t,x,y,z,dot,rcs);
 if(diagCaseA&&diagCaseA.fuze.length<512)diagCaseA.fuze.push({lifeS:m.life,rangeM:Math.hypot(x,y,z),allow:q.allow,reason:q.reason,beam:q.beam,detection:q.detection,opportunityDraws:m._fuzeOpportunityRngA?.draws??null});
 return q;
};

if(typeof samFuzeSignalSweepA==='function'){
 const diagSignalNativeA=samFuzeSignalSweepA;
 samFuzeSignalSweepA=function(m,t,rel,vel,context,rcs){
  const q=diagSignalNativeA(m,t,rel,vel,context,rcs);
  if(diagCaseA&&diagCaseA.fuze.length<512)diagCaseA.fuze.push({lifeS:m.life,rangeM:Math.hypot(rel.x,rel.y,rel.z),allow:q.allow,reason:q.reason,beam:q.beam,detection:q.detection});
  return q;
 };
}

// Measurement functions below do not advance any RNG.
const diagPnNativeA=computeTruePN3D,diagApnNativeA=computeAPNCorrectionV1,diagZemNativeA=computeZEMCorrectionV1;
computeTruePN3D=function(m,...args){const q=diagPnNativeA(m,...args);m._diagPnA=q;return q;};
computeAPNCorrectionV1=function(m,...args){const q=diagApnNativeA(m,...args);m._diagApnA=q;return q;};
computeZEMCorrectionV1=function(m,...args){const q=diagZemNativeA(m,...args);m._diagZemA=q;return q;};
function diagVecGA(q){return q?Math.hypot(q.ax??0,q.ay??0,q.az??0)/G0:0;}
function diagTelemetryA(m){return {
 phase:m._v1GuidancePhase??null,authority:m._v1GuidanceAuthority??null,
 pnG:diagVecGA(m._diagPnA),apnG:diagVecGA(m._diagApnA),zemG:diagVecGA(m._diagZemA),
 zemRawG:m._v1ZemRawG??null,zemCapG:m._v1ZemCapG??null,
 predictedCpaM:m._v1PredCPA??null,predictedCpaTimeS:m._v1PredCPATime??null,
 commandG:m._v1GCommand??null,achievedG:m._v1GAchieved??null,availableG:m.availableG??null,
 saturated:!!m._v1Saturated,cmdOmegaYaw:m.cmdOmegaYaw??null,cmdOmegaPit:m.cmdOmegaPit??null,
 controlCommand:m._v1ControlCommandVec?{...m._v1ControlCommandVec}:null,qbar:m.qbar??null,heading:m.heading??null,pitch:m.pitch??null,
 targetObservation:m._v1TargetState?{source:m._v1TargetState.source,isValid:m._v1TargetState.isValid,confidence:m._v1TargetState.confidence,posM:{...m._v1TargetState.posM},velMps:{...m._v1TargetState.velMps}}:null,
 term:m._gameFlightTerm?JSON.parse(JSON.stringify(m._gameFlightTerm)):null,
 };}
function diagStepA(m,t){
 if(!diagCaseA)return;
 const dx=worldToMeters(t.x-m.x),dy=worldToMeters(t.y-m.y),dz=t.z-m.z,r=Math.hypot(dx,dy,dz),d=diagCaseA;
 const v=diagTelemetryA(m);
 if((v.commandG??0)>(d.maxDemand?.telemetry.commandG??-1))d.maxDemand={lifeS:m.life,rangeM:r,telemetry:v};
 if(d.lastRange!=null){
  const slope=r-d.lastRange;
  if(slope>=0&&d.lastSlope<0)d.passes.push({lifeS:m.life,rangeM:Math.min(r,d.lastRange),nativeClosestM:m._everClosest==null?null:m._everClosest*1000,telemetry:v});
  d.lastSlope=slope;
 }
 d.lastRange=r;
 const phase=m._v1GuidancePhase??'';
 if(phase!==d.lastPhase){d.phases.push({lifeS:m.life,phase,rangeM:r,telemetry:v});d.lastPhase=phase;}
}
