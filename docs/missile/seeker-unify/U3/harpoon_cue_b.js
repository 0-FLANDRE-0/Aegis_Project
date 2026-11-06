// SEEKER_UNIFY_U3 Commit B: explicit Harpoon launch-memory -> CUE_A adapter.
// The ship EKF owns position/velocity/covariance and the fixed-step clock owns
// the release/observation ages. No entity ID or physical target reference enters
// this adapter. Route plans are deliberately rejected as observations.
const HARPOON_CUE_B_SPEC=Object.freeze({
  schema:'AEGIS_HARPOON_CUE_B_1',source:'SIM_TUNED',resultFitting:false,
  filterSchema:ASM_CUE_A_SPEC.schema,basketSigma:ASM_CUE_A_SPEC.basketSigma,
  trackSource:'LOCAL_SURFACE_OBSERVATION',routeSource:'ROUTE_PLAN_PRIOR',
  covarianceStateOrder:'x,y,vx,vy,ax,ay',truthUsed:false
});
function harpoonCuePacketB(memory){
  if(!memory||memory.cueSource==='ROUTE_PLAN_PRIOR'||memory.schema==='HARPOON_FROZEN_COORDINATE_CUE_E1')return null;
  const p=memory.positionM,v=memory.velocityMps,c=memory.covariance;
  if(!p||!v||!c||c.length!==36||![p.x,p.y,v.x,v.y,...c].every(Number.isFinite))return null;
  const sourceIds=[0,1,3,4],targetIds=[0,1,2,3],P=new Array(36).fill(0);
  for(let r=0;r<4;r++)for(let col=0;col<4;col++)P[targetIds[r]*6+targetIds[col]]=c[sourceIds[r]*6+sourceIds[col]];
  const accelVariance=ASM_CUE_A_SPEC.cueManeuverAccelSigmaMps2**2;P[28]=accelVariance;P[35]=accelVariance;
  const q={schema:ASM_CUE_A_SPEC.schema,x:[p.x,p.y,v.x,v.y,0,0],P,timeS:0,
    source:'LOCAL_SURFACE_OBSERVATION',truthUsed:false};
  asmCueSymmetrizeA(q.P);asmCueApplyBoundsA(q);return q;
}
function harpoonCuePredictB(memory,elapsedS){
  const q=harpoonCuePacketB(memory),dt=Math.max(0,Number(elapsedS)||0);if(!q)return null;
  if(dt>1e-12){const model=asmSingerDiscreteA(dt),nextX=new Array(6).fill(0);for(let r=0;r<6;r++)for(let k=0;k<6;k++)nextX[r]+=model.F[r*6+k]*q.x[k];q.x=nextX;q.P=asmCueCovariancePredictA(q.P,model);asmCueApplyBoundsA(q);}
  q.timeS=dt;return q;
}
function harpoonCueHorizontalSigmaB(P){
  if(!P||P.length!==36)return {majorSigmaM:NaN,minorSigmaM:NaN,angleRad:NaN};
  const xx=Math.max(0,Number(P[0])||0),yy=Math.max(0,Number(P[7])||0),xy=.5*((Number(P[1])||0)+(Number(P[6])||0)),root=Math.hypot(xx-yy,2*xy),major=.5*(xx+yy+root),minor=.5*(xx+yy-root);
  return {majorSigmaM:Math.sqrt(Math.max(0,major)),minorSigmaM:Math.sqrt(Math.max(0,minor)),angleRad:.5*Math.atan2(2*xy,xx-yy)};
}
function harpoonCueMeanB(memory,elapsedS){
  // The Singer state is initialized with zero acceleration. Its exact-discrete
  // mean is therefore the same constant-velocity mean; covariance still uses
  // asmSingerDiscreteA/asmCueCovariancePredictA above.
  const dt=Math.max(0,Number(elapsedS)||0),p=memory.positionM,v=memory.velocityMps;
  return {x:p.x+v.x*dt,y:p.y+v.y*dt,z:p.z+v.z*dt,vx:v.x,vy:v.y,vz:v.z};
}
function harpoonCueHandoffB(memory,predictionHorizonS){
  if(memory?.cueSource==='ROUTE_PLAN_PRIOR'||memory?.schema==='HARPOON_FROZEN_COORDINATE_CUE_E1'){
    return Object.freeze({schema:HARPOON_CUE_B_SPEC.schema,source:'ROUTE_PLAN_PRIOR',observationUpdate:false,
      horizonS:0,predictionSigmaM:HARPOON_PROFILE_A.sim.seekerSearchBasketM*2/3,
      searchBasketM:HARPOON_PROFILE_A.sim.seekerSearchBasketM,physicalSearchLimitM:HARPOON_PROFILE_A.sim.seekerSearchBasketM,
      feasible:true,reason:null,truthUsed:false});
  }
  const horizon=Math.max(0,Number(predictionHorizonS)||0),q=harpoonCuePredictB(memory,horizon),sigma=harpoonCueHorizontalSigmaB(q?.P),cfg=HARPOON_PROFILE_A.sim,
    searchBasketM=ASM_CUE_A_SPEC.basketSigma*sigma.majorSigmaM,
    physicalSearchLimitM=Math.min(cfg.seekerRangeM,Math.tan(cfg.seekerGimbalRad)*cfg.seekerActivationRangeM),
    feasible=!!q&&Number.isFinite(searchBasketM)&&searchBasketM<=physicalSearchLimitM;
  return Object.freeze({schema:HARPOON_CUE_B_SPEC.schema,source:'LOCAL_SURFACE_OBSERVATION',observationUpdate:true,
    horizonS:horizon,positionM:q?{x:q.x[0],y:q.x[1]}:null,velocityMps:q?{x:q.x[2],y:q.x[3]}:null,
    predictionSigmaM:2*sigma.majorSigmaM,searchBasketM,minorSigmaM:sigma.minorSigmaM,majorAxisRad:sigma.angleRad,
    physicalSearchLimitM,feasible,reason:feasible?null:'INS_PREDICTION_BASKET_INSUFFICIENT',truthUsed:false});
}
