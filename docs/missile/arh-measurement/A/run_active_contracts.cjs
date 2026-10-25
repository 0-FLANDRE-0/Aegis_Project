// Isolated measurement contracts with the captured CURRENT actual SM6 profile.
// No shipping source, coefficient or game RNG is changed.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const T=__dirname,dir=path.join(T,'active');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
const variants=['DZT','HANDOFF'];const output=[];
for(const variant of variants){
 const cap=JSON.parse(fs.readFileSync(path.join(dir,variant+'-capture.json'))),p=structuredClone(cap.profile);
 if(!cap.runtime.isSM6||cap.runtime.profileId!=='SM6_BLKIA_SIM'||cap.rfModel!=='RF_V2')throw Error('WRONG_ACTIVE_PROFILE');
 if(hash(cap.functions._arhV2MonopulseMeasurement)!=='9b206aa5727f5bffc11513f0bea56e0d82615352689454b0c3144fd57368579a')throw Error('WRONG_MEASUREMENT_SOURCE');
 const ctx={Math,TAU:2*Math.PI,SM6_ARH_RF_V2_PROFILE:Object.freeze(p),getArhSeekerModel:()=>cap.rfModel,getEssmArhProfile:()=>{throw Error('NOT_SM6');},_arhSeekerRandom:()=>0,_arhSeekerRandn:()=>0};vm.createContext(ctx);
 const names=['clamp','deg','lerp','angNorm','_mIdx','getSamArhProfile','_arhV2MonopulseMeasurement','_arhMonopulseMeasurement','_arhDecorateMeasurementFromCluster','_arhMeasurementCov','_sarhUnitGeometry','_sarhMeasurementModel','_sarhMeasurementJacobian'];
 for(const name of names){if(hash(cap.functions[name])!==cap.functionHashes[name])throw Error('SOURCE_HASH_'+name);vm.runInContext('globalThis['+JSON.stringify(name)+']=('+cap.functions[name]+')',ctx);}
 function observe(c={},normal=()=>0){
  ctx._arhSeekerRandn=normal;
  const m={isSM6:true,isESSM:false,_v1ArhState:c.state??'TRACK',seekerAngle:ctx.deg(c.boresightAzDeg??0),seekerEl:ctx.deg(c.boresightElDeg??0)};
  const cluster=[{azRad:ctx.deg(c.targetAzDeg??0),elRad:ctx.deg(c.targetElDeg??0),rangeM:26000,dopplerPathRateMps:0,baseReceivedPowerNorm:1,receivedPowerNorm:1,snr:20,trackCoherence:1,decoyLikelihood:0,targetEvidence:1,eccmFrontend:{pass:1,lowDoppler01:0,clutterMask:0}}];
  const direct=ctx._arhV2MonopulseMeasurement(m,cluster),dispatched=ctx._arhMonopulseMeasurement(m,cluster),raw=structuredClone(dispatched),decorated=ctx._arhDecorateMeasurementFromCluster(dispatched,cluster),R=Array.from(ctx._arhMeasurementCov(decorated));
  const az=cluster[0].azRad,el=cluster[0].elRad,r=26000,x=[r*Math.cos(el)*Math.cos(az),r*Math.cos(el)*Math.sin(az),r*Math.sin(el),0,0,0],rx={x:0,y:0,z:0,vx:0,vy:0,vz:0};const model=ctx._sarhMeasurementModel(x,rx,rx);
  return {input:c,direct:structuredClone(direct),raw,decorated:structuredClone(decorated),covarianceR:R,modelExpectedAzRad:model.h[1],modelExpectedElRad:model.h[2]};
 }
 // Geometry uses zero noise. Native/VM dispatch equality is only asserted with
 // fixed draws, never by consuming two independent Monte Carlo measurements.
 const geometry=[];
 for(const axis of ['Az','El']){
  for(const target of [-.5,-.1,0,.1,.5])geometry.push({axis,kind:'POINT_IDENTITY',...observe({['target'+axis+'Deg']:target})});
  for(const boresight of [-.5,-.1,0,.1,.5])geometry.push({axis,kind:'BORESIGHT_INVARIANCE',...observe({['boresight'+axis+'Deg']:boresight})});
 }
 for(const state of ['ACQUIRE','REACQUIRE'])geometry.push({axis:'Az',kind:'OTHER_TRACKING_STATE',...observe({state,targetAzDeg:.5})});
 function gaussian(seed){let s=seed>>>0;const u=()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return((s>>>0)+.5)/4294967296;};return()=>Math.sqrt(-2*Math.log(u()))*Math.cos(2*Math.PI*u());}
 const normal=gaussian(0x71c42a19),N=20000,sum=[0,0],sq=[0,0];let noiseSample=null;
 // One dispatch per noise observation. The direct-call branch above would
 // consume a second independent noise sample, so it is not used here.
 const m={isSM6:true,_v1ArhState:'TRACK',seekerAngle:0,seekerEl:0};const cluster=[{azRad:0,elRad:0,rangeM:26000,dopplerPathRateMps:0,baseReceivedPowerNorm:1,receivedPowerNorm:1,snr:20,trackCoherence:1,decoyLikelihood:0,targetEvidence:1,eccmFrontend:{pass:1}}];
 ctx._arhSeekerRandn=normal;
 for(let i=0;i<N;i++){const raw=ctx._arhMonopulseMeasurement(m,cluster),d=ctx._arhDecorateMeasurementFromCluster(raw,cluster);for(const[j,a]of['azRad','elRad'].entries()){const v=d[a]*180/Math.PI;sum[j]+=v;sq[j]+=v*v;}noiseSample=d;}
 ctx._arhSeekerRandn=()=>1;const hi=ctx._arhMonopulseMeasurement(m,cluster);ctx._arhSeekerRandn=()=>-1;const lo=ctx._arhMonopulseMeasurement(m,cluster);const R=Array.from(ctx._arhMeasurementCov(noiseSample));
 const noise=['az','el'].map((axis,j)=>{const generatedSigmaDeg=(hi[axis+'Rad']-lo[axis+'Rad'])/2*180/Math.PI,reportedSigmaDeg=noiseSample[axis+'SigmaDeg'],effectiveRSigmaDeg=Math.sqrt(R[j===0?5:10])*180/Math.PI;return{axis,samples:N,meanDeg:sum[j]/N,empiricalSigmaDeg:Math.sqrt((sq[j]-sum[j]*sum[j]/N)/(N-1)),generatedSigmaDeg,reportedSigmaDeg,effectiveRSigmaDeg,sigmaRatio:generatedSigmaDeg/effectiveRSigmaDeg,varianceRatio:(generatedSigmaDeg/effectiveRSigmaDeg)**2};});
 const tests=[
  {name:'CURRENT_SM6_POINT_ANGLE_IDENTITY',pass:geometry.filter(g=>g.kind==='POINT_IDENTITY').every(g=>Math.abs(g.raw[g.axis==='Az'?'azRad':'elRad']-ctx.deg(g.input['target'+g.axis+'Deg']))<1e-10)},
  {name:'CURRENT_SM6_BORESIGHT_INVARIANCE',pass:geometry.filter(g=>g.kind==='BORESIGHT_INVARIANCE').every(g=>Math.abs(g.raw[g.axis==='Az'?'azRad':'elRad'])<1e-10)},
  {name:'CURRENT_SM6_R_COVERS_GENERATED_NOISE',pass:noise.every(n=>n.generatedSigmaDeg<=n.effectiveRSigmaDeg*1.1)}];
 const pipelineChecks={dispatchMatchesDirect:geometry.every(g=>JSON.stringify(g.direct)===JSON.stringify(g.raw)),decorateDoesNotCorrectAnglesOrSigma:geometry.every(g=>['azRad','elRad','azSigmaDeg','elSigmaDeg'].every(k=>g.raw[k]===g.decorated[k])),modelUsesAbsoluteGeometricAngles:geometry.every(g=>Math.abs(g.modelExpectedAzRad-ctx.deg(g.input.targetAzDeg??0))<1e-12&&Math.abs(g.modelExpectedElRad-ctx.deg(g.input.targetElDeg??0))<1e-12),cleanPointClassification:geometry.every(g=>g.decorated.classification==='TRACK_ECHO'),rEqualsReportedSigma:noise.every(n=>Math.abs(n.reportedSigmaDeg-n.effectiveRSigmaDeg)<1e-12),monteCarloMatchesGeneratedSigma:noise.every(n=>Math.abs(n.empiricalSigmaDeg/n.generatedSigmaDeg-1)<.03)};
 output.push({variant,htmlSha256:cap.htmlSha256,profileId:p.id,profileSha256:cap.profileSha256,measurementFunctionSha256:cap.functionHashes._arhV2MonopulseMeasurement,profile:p,scope:'Captured actual SM6 RF_V2 configuration, synthetic clean point at 26km/power1/SNR20; detection draw0, standard Gaussian independent diagnostic stream. Not a missile flight.',geometry,noise,tests,pipelineChecks,contractFailures:tests.filter(t=>!t.pass).length});
}
const result={schema:'AEGIS_ARH_MEASUREMENT_CONTRACT_A_ACTIVE_SM6',variants:output,productChanges:0,coefficientChanges:0,newFlightSteps:0};fs.writeFileSync(path.join(dir,'active-contract-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(output.map(r=>({variant:r.variant,profile:r.profileId,failures:r.contractFailures,noise:r.noise,pipelineChecks:r.pipelineChecks,point:r.geometry.find(g=>g.kind==='POINT_IDENTITY'&&g.axis==='Az'&&g.input.targetAzDeg===.5).raw.azRad*180/Math.PI,fixedPoint:r.geometry.find(g=>g.kind==='BORESIGHT_INVARIANCE'&&g.axis==='Az'&&g.input.boresightAzDeg===.5).raw.azRad*180/Math.PI})),null,2));
if(output.some(r=>Object.values(r.pipelineChecks).some(x=>!x)))throw Error('DIAGNOSTIC_PIPELINE_CHECK_FAILED');
process.exitCode=output.some(r=>r.contractFailures)?1:0;
