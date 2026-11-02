
const trackCCauseBatches=[],trackCCauseCandidates=[];
if(typeof trackCC55AssignmentsC==='function'){
 const original=trackCC55AssignmentsC;
 trackCC55AssignmentsC=function(plots,files,cfg){
  const before={step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT,plots:plots.map(p=>({knownOwnLaunch:p.knownOwnLaunch,measurement:{rxM:p.measurement.rxM,ryM:p.measurement.ryM,rzM:p.measurement.rzM,rangeM:p.measurement.rangeM,azRad:p.measurement.azRad,elRad:p.measurement.elRad,positionVarianceM2:p.measurement.positionVarianceM2?.slice()}})),files:[...files.values()].map(r=>({id:r.id,ownFireEvidence:!!r.ownFireEvidence,confirmed:r.confirmed,st:{rxM:r.st.rxM,ryM:r.st.ryM,rzM:r.st.rzM,localAgeS:r.st.localAgeS,localHits:r.st.localHits,P:r.st._c55P?.map(q=>q.slice())}}))};
  const result=original.apply(this,arguments);before.result={pairs:result.pairs.map(q=>({i:q.i,id:q.id,nis:q.nis})),heldPlots:[...result.heldPlots],heldTracks:[...result.heldTracks],components:result.components,reason:result.reason??null};if(plots.length)trackCCauseBatches.push(before);return result;
 };
}
const trackCCauseNativeTrace=trackATraceEventA;
trackATraceEventA=function(type,payload,context={}){
 const result=trackCCauseNativeTrace.apply(this,arguments);
 if(type==='CANDIDATE'&&context.kind==='CIWS_LOCAL_RF')trackCCauseCandidates.push({step:simStepCounter,mountId:context.mountId,trackId:context.trackId,knownOwnLaunch:context.knownOwnLaunch,decision:context.decision,reason:context.reason,distanceM:context.distanceM,gate:context.gate,measurement:{rangeM:payload?.rangeM,azRad:payload?.azRad,elRad:payload?.elRad,rxM:payload?.rxM,ryM:payload?.ryM,rzM:payload?.rzM}});
 return result;
};
window.__TRACK_C_D1_CAUSE__={run(c){
 __TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_C_AA_INTERNAL__.begin();
 const original=simulateFixedTick;simulateFixedTick=function(){const r=original.apply(this,arguments);__TRACK_C_AA_INTERNAL__.sample(CD_A.targets);return r;};
 const result=__CIWS_DMG_A__.run(c,true),lineage=__TRACK_C_AA_INTERNAL__.finish();return {result,lineage,costBatches:trackCCauseBatches,legacyCandidates:trackCCauseCandidates};
}};
