// SEEKER_UNIFY_C Stage 3: CUE_A target-memory filter.
// Guidance consumes only launch information and anonymous measurements. Physical
// emitter/target geometry is confined to sensor synthesis and diagnostic code.
const ASM_CUE_A_SPEC=Object.freeze({
  schema:'AEGIS_ASM_CUE_A_1',source:'SIM_TUNED',resultFitting:false,
  cueManeuverAccelSigmaMps2:.3,basketSigma:3,vmaxMps:18,
  assumedEmitterHeightM:25,assumedEmitterHeightSigmaM:8,
  minAcqRangeFloorM:1500,minAcqRangeFrac:.5,
  rangeHalfFloorM:1200,rangeHalfFraction:.12,azHalfFloorRad:deg(5),elHalfRad:deg(4),
  propagationEffectiveEarthRadiusM:APS_F.effectiveEarthRadiusM
});
const ASM_CUE_FEATURE_PROVENANCE_A=Object.freeze({
  PUBLIC_CONFIRMED:'PUBLIC_CONFIRMED',ASSUMED_THREAT:'ASSUMED_THREAT',NOT_EQUIPPED:'NOT_EQUIPPED'
});
const ASM_CUE_FEATURES_A=Object.freeze({
  'Kh-35U':Object.freeze({passiveRfBearingElevation:'PUBLIC_CONFIRMED'}),
  'Kh-32':Object.freeze({passiveRfBearingElevation:'ASSUMED_THREAT'})
});
const ASM_CUE_THREAT_MODES_A=Object.freeze(['MAX_THREAT','CONFIRMED_ONLY']);
let THREAT_ASSUMPTION_MODE='MAX_THREAT';
function setThreatAssumptionModeC(mode){
  if(!ASM_CUE_THREAT_MODES_A.includes(mode))throw Error('THREAT_ASSUMPTION_MODE');
  THREAT_ASSUMPTION_MODE=mode;cueAUpdateUiC();return mode;
}
function asmCueFeatureEnabledA(label,key){
  const provenance=ASM_CUE_FEATURES_A[label]?.[key]??ASM_CUE_FEATURE_PROVENANCE_A.NOT_EQUIPPED;
  return provenance===ASM_CUE_FEATURE_PROVENANCE_A.PUBLIC_CONFIRMED||
    (provenance===ASM_CUE_FEATURE_PROVENANCE_A.ASSUMED_THREAT&&THREAT_ASSUMPTION_MODE==='MAX_THREAT');
}
function asmCueEnabledAssumptionsA(){
  const out=[];for(const [label,features] of Object.entries(ASM_CUE_FEATURES_A))for(const [feature,provenance] of Object.entries(features))
    if(provenance==='ASSUMED_THREAT'&&asmCueFeatureEnabledA(label,feature))out.push({label,feature,provenance});return out;
}
// COMPAT_REQUIRED: legacy callers still inspect mode on ASM_CUE_BASKET_U0.
const ASM_CUE_BASKET_U0=Object.freeze({...ASM_CUE_A_SPEC,mode:'ACTIVE'});
function asmCueSymmetrizeA(P){
  for(let r=0;r<4;r++)for(let c=r+1;c<4;c++){const v=.5*((Number(P[r*4+c])||0)+(Number(P[c*4+r])||0));P[r*4+c]=v;P[c*4+r]=v;}
  for(let i=0;i<4;i++)P[i*4+i]=Math.max(1e-9,Number(P[i*4+i])||0);return P;
}
function asmCueInitialPacketA(em){
  const launch=em._cueLaunchA??{},positionM=launch.positionM??{},velocityMps=launch.velocityMps??null,cov=launch.covariance??{};
  const fallbackSigma=Math.max(1,Number(missileNavB2ProfileFor(em)?.initialPosErrorM)||1);
  const posSigma=Math.max(1,Number(cov.positionSigmaM)||fallbackSigma),velSigma=Math.max(1e-6,Number(cov.velocitySigmaMps)||ASM_CUE_A_SPEC.vmaxMps);
  return {positionM:{x:Number.isFinite(positionM.x)?positionM.x:worldToMeters(em.insTgtX),y:Number.isFinite(positionM.y)?positionM.y:worldToMeters(em.insTgtY)},
    velocityMps:velocityMps&&Number.isFinite(velocityMps.x)&&Number.isFinite(velocityMps.y)?{x:velocityMps.x,y:velocityMps.y}:null,
    positionSigmaM:posSigma,velocitySigmaMps:velSigma,timeS:Math.max(0,Number(launch.timeS)||0),source:String(launch.source||'LAUNCH')};
}
function asmTargetCueStateA(em){
  if(em._targetCueA)return em._targetCueA;const a=asmCueInitialPacketA(em),vx=a.velocityMps?.x??0,vy=a.velocityMps?.y??0;
  const ps2=a.positionSigmaM*a.positionSigmaM,vs2=a.velocitySigmaMps*a.velocitySigmaMps;
  return em._targetCueA={schema:ASM_CUE_A_SPEC.schema,x:[a.positionM.x,a.positionM.y,vx,vy],P:[ps2,0,0,0,0,ps2,0,0,0,0,vs2,0,0,0,0,vs2],
    timeS:a.timeS,lastPredictLifeS:a.timeS,source:a.source,updates:0,passiveUpdates:0,dlUpdates:0,lastMeasurement:null,lastPassiveBearingResidualRad:null,lastPassiveBearingConverged:false};
}
function asmCueLimitVelocityA(q){const v=Math.hypot(q.x[2],q.x[3]),lim=ASM_CUE_A_SPEC.vmaxMps;if(v>lim&&v>0){q.x[2]*=lim/v;q.x[3]*=lim/v;}return q;}
function asmCueSyncAimA(em,q){if(!em._c52InsMemory){em.insTgtX=metersToWorld(q.x[0]);em.insTgtY=metersToWorld(q.x[1]);}return q;}
function asmTargetCuePredictA(em){
  const q=asmTargetCueStateA(em);if(em._c52InsMemory)return q;
  const now=Math.max(0,Number(em.life)||0),dt=Math.max(0,now-(Number(q.lastPredictLifeS)||0));if(dt<=1e-12)return asmCueSyncAimA(em,q);
  const x=q.x,P=q.P;x[0]+=x[2]*dt;x[1]+=x[3]*dt;
  const F=[1,0,dt,0,0,1,0,dt,0,0,1,0,0,0,0,1],FP=new Array(16).fill(0),next=new Array(16).fill(0);
  for(let r=0;r<4;r++)for(let c=0;c<4;c++)for(let k=0;k<4;k++)FP[r*4+c]+=F[r*4+k]*P[k*4+c];
  for(let r=0;r<4;r++)for(let c=0;c<4;c++)for(let k=0;k<4;k++)next[r*4+c]+=FP[r*4+k]*F[c*4+k];
  const s2=ASM_CUE_A_SPEC.cueManeuverAccelSigmaMps2**2,d2=dt*dt,d3=d2*dt,d4=d2*d2,Q=[d4/4*s2,0,d3/2*s2,0,0,d4/4*s2,0,d3/2*s2,d3/2*s2,0,d2*s2,0,0,d3/2*s2,0,d2*s2];
  for(let i=0;i<16;i++)P[i]=next[i]+Q[i];asmCueSymmetrizeA(P);asmCueLimitVelocityA(q);q.lastPredictLifeS=now;q.timeS=now;return asmCueSyncAimA(em,q);
}
function asmCueScalarUpdateA(q,H,z,R,wrap=false,predictedOverride=null){
  let predicted=predictedOverride==null?NaN:Number(predictedOverride);if(!Number.isFinite(predicted)){predicted=0;for(let i=0;i<4;i++)predicted+=H[i]*q.x[i];}const residual=wrap?angNorm(z-predicted):z-predicted;
  const PH=new Array(4).fill(0);for(let i=0;i<4;i++)for(let j=0;j<4;j++)PH[i]+=q.P[i*4+j]*H[j];
  let S=Math.max(1e-12,Number(R)||0);for(let i=0;i<4;i++)S+=H[i]*PH[i];if(!Number.isFinite(S)||S<=0)return {ok:false,residual,S};
  const K=PH.map(v=>v/S),old=[...q.P];for(let i=0;i<4;i++)q.x[i]+=K[i]*residual;
  for(let i=0;i<4;i++)for(let j=0;j<4;j++){let hp=0;for(let k=0;k<4;k++)hp+=H[k]*old[k*4+j];q.P[i*4+j]=old[i*4+j]-K[i]*hp;}
  asmCueSymmetrizeA(q.P);asmCueLimitVelocityA(q);return {ok:true,residual,S,nis:residual*residual/S};
}
function asmCueUpdateA(em,packet){
  if(!em||em._c52InsMemory||!packet||!['DL','PASSIVE_RF'].includes(packet.source))return {ok:false,reason:em?._c52InsMemory?'FIXED_C52_MEMORY':'CUE_UPDATE_PACKET'};
  const q=asmTargetCuePredictA(em),cov=packet.covariance??{},pos=packet.positionM,vel=packet.velocityMps,updates=[];
  if(pos&&Number.isFinite(pos.x)&&Number.isFinite(pos.y)){
    const s=Math.max(1,Number(cov.positionSigmaM)||1),R=s*s;updates.push(asmCueScalarUpdateA(q,[1,0,0,0],pos.x,R));updates.push(asmCueScalarUpdateA(q,[0,1,0,0],pos.y,R));
  }
  if(vel&&Number.isFinite(vel.x)&&Number.isFinite(vel.y)){
    const s=Math.max(1e-3,Number(cov.velocitySigmaMps)||1e-3),R=s*s;updates.push(asmCueScalarUpdateA(q,[0,0,1,0],vel.x,R));updates.push(asmCueScalarUpdateA(q,[0,0,0,1],vel.y,R));
  }
  if(!updates.length)return {ok:false,reason:'NO_POSITION_OR_VELOCITY'};q.source=packet.source;q.updates++;if(packet.source==='DL')q.dlUpdates++;q.lastMeasurement={source:packet.source,timeS:Number.isFinite(packet.timeS)?packet.timeS:q.timeS};asmCueSyncAimA(em,q);return {ok:true,updates:updates.length,state:asmTargetCueSnapshotA(em)};
}
function asmCueAngularUpdateA(em,measurement){
  if(!em||em._c52InsMemory||!measurement?.available)return {ok:false,reason:'PASSIVE_MEASUREMENT'};const q=asmTargetCuePredictA(em),own=missileNavB2OwnState(em),dx=q.x[0]-own.posM.x,dy=q.x[1]-own.posM.y,r2=Math.max(1,dx*dx+dy*dy),r=Math.sqrt(r2),zEff=ASM_CUE_A_SPEC.assumedEmitterHeightM-own.posM.z-r2/(2*ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM),den=r2+zEff*zEff;
  const predictedBearing=Math.atan2(dy,dx),HAz=[-dy/r2,dx/r2,0,0],bearing=asmCueScalarUpdateA(q,HAz,measurement.bearingRad,measurement.bearingSigmaRad**2,true,predictedBearing);
  const dx2=q.x[0]-own.posM.x,dy2=q.x[1]-own.posM.y,rB=Math.max(1,Math.hypot(dx2,dy2)),zB=ASM_CUE_A_SPEC.assumedEmitterHeightM-own.posM.z-rB*rB/(2*ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM),denB=rB*rB+zB*zB,dhdr=(rB*(-rB/ASM_CUE_A_SPEC.propagationEffectiveEarthRadiusM)-zB)/Math.max(1,denB),dh=(rB/Math.max(1,denB))*ASM_CUE_A_SPEC.assumedEmitterHeightSigmaM;
  const predictedElevation=Math.atan2(zB,rB),HEl=[dhdr*dx2/rB,dhdr*dy2/rB,0,0],elevation=asmCueScalarUpdateA(q,HEl,measurement.elevationRad,measurement.elevationSigmaRad**2+dh*dh,true,predictedElevation);
  q.source='PASSIVE_RF';q.updates++;q.passiveUpdates++;q.lastMeasurement={source:'PASSIVE_RF',timeS:measurement.sampleTimeS,bearingResidualRad:bearing.residual,elevationResidualRad:elevation.residual,snr:measurement.snr,emitterClass:measurement.emitterClass,band:measurement.band,directRangeEstimateM:measurement.directRangeEstimateM,directRangeSigmaM:measurement.directRangeSigmaM};q.lastPassiveBearingResidualRad=Math.abs(bearing.residual);q.lastPassiveBearingConverged=bearing.ok&&bearing.nis<=ASM_CUE_A_SPEC.basketSigma**2;asmCueSyncAimA(em,q);return {ok:bearing.ok&&elevation.ok,bearing,elevation};
}
function asmTargetCueStateU0(em){return asmTargetCueStateA(em);}
function asmTargetCueU0(em){
  const q=asmTargetCuePredictA(em);return {positionM:{x:q.x[0],y:q.x[1],z:ASM_SEEKER_PROFILES[em.label]?.aimHeightM??5},velocityMps:{x:q.x[2],y:q.x[3]},covariance:[...q.P],rangeRefTimeS:q.timeS,bearingRefTimeS:q.timeS,source:q.source};
}
function asmTargetCuePassiveBearingUpdateU0(em,measurement,profile,correctedBearingRad){
  const q=asmTargetCueStateA(em);q.lastPassiveBearingResidualRad=Math.abs(angNorm(measurement.bearingRad-correctedBearingRad));q.lastPassiveBearingConverged=q.lastPassiveBearingResidualRad<=ASM_CUE_A_SPEC.basketSigma*Math.max(1e-9,Number(profile?.bearingErrorRad)||0);return q.lastPassiveBearingConverged;
}
function asmCueBasketU0(em,own,p){
  const cue=asmTargetCueU0(em),q=asmTargetCueStateA(em),now=Math.max(0,Number(em.life)||0),dx=cue.positionM.x-worldToMeters(own.x),dy=cue.positionM.y-worldToMeters(own.y),dz=cue.positionM.z-(own.z??0),rangeM=Math.max(1,Math.hypot(dx,dy,dz)),horizontalM=Math.max(1,Math.hypot(dx,dy)),ux=dx/horizontalM,uy=dy/horizontalM,cx=-uy,cy=ux;
  const P=q.P,varRange=Math.max(0,ux*ux*P[0]+2*ux*uy*P[1]+uy*uy*P[5]),varCross=Math.max(0,cx*cx*P[0]+2*cx*cy*P[1]+cy*cy*P[5]),rangeHalfM=Math.max(ASM_CUE_A_SPEC.rangeHalfFloorM,ASM_CUE_A_SPEC.rangeHalfFraction*rangeM,ASM_CUE_A_SPEC.basketSigma*Math.sqrt(varRange)),searchHalfAzRad=Number.isFinite(Number(p?.searchSectorAzDeg))?deg(Math.max(0,Number(p.searchSectorAzDeg))):Math.PI,azHalfRad=Math.min(searchHalfAzRad,Math.max(ASM_CUE_A_SPEC.azHalfFloorRad,ASM_CUE_A_SPEC.basketSigma*Math.atan2(Math.sqrt(varCross),horizontalM)));
  return {cue,rangeM,azRad:Math.atan2(dy,dx),elRad:Math.atan2(dz,horizontalM),rangeLowM:Math.max(rangeM-rangeHalfM,ASM_CUE_A_SPEC.minAcqRangeFloorM,ASM_CUE_A_SPEC.minAcqRangeFrac*rangeM),rangeHighM:rangeM+rangeHalfM,azHalfRad,searchHalfAzRad,elHalfRad:ASM_CUE_A_SPEC.elHalfRad,rangeAgeS:Math.max(0,now-q.timeS),bearingAgeS:Math.max(0,now-q.timeS),rangeSigmaM:Math.sqrt(varRange),crossSigmaM:Math.sqrt(varCross)};
}
function asmTargetCueSnapshotA(em){
  const q=asmTargetCueStateA(em);return {schema:q.schema,missileId:em.id,label:em.label,positionM:{x:q.x[0],y:q.x[1]},velocityMps:{x:q.x[2],y:q.x[3]},covariance:[...q.P],timeS:q.timeS,source:q.source,updates:q.updates,passiveUpdates:q.passiveUpdates,dlUpdates:q.dlUpdates,lastMeasurement:q.lastMeasurement?{...q.lastMeasurement}:null};
}
