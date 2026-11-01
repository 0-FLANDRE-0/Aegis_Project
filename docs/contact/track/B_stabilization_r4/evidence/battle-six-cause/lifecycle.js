// TEST_ONLY / OBSERVED_NATIVE_LIFECYCLE_TRANSITIONS. Inert until install().
// No physical/truth access, extra native query, RF/NIS/filter evaluation or command.
(() => {
 if(window.__REACQ_CAUSE__)throw Error('REACQ_CAUSE_API_ALREADY_PRESENT');
 const records=[],faults=[],sources={},FOCUS=new Set([300000003,300000004]);
 const FROM_S=0,TO_S=45,MAX_RECORDS=65536,MAX_FAULTS=64;
 const counts={finalizeCalls:0,markMissCalls:0,focusedFinalize:0,focusedMarkMiss:0,foreignReacquireFinalize:0,foreignFalseToTrue:0,finalizeFalseToTrue:0,markMissFalseToTrue:0};
 let installed=false,dropped=0,faultDropped=0;
 const own=(o,k)=>o==null?undefined:Object.getOwnPropertyDescriptor(o,k)?.value;
 function fields(o,keys){const q={};for(const k of keys){const v=own(o,k);if(v===null||['boolean','string'].includes(typeof v))q[k]=v;else if(typeof v==='number')q[k]=Number.isFinite(v)?v:String(v);}return q;}
 const clock=()=>({step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT});
 const inWindow=()=>simStepCounter*SIM_FIXED_DT>=FROM_S&&simStepCounter*SIM_FIXED_DT<=TO_S;
 const relevant=t=>inWindow();
 function fault(where,error){if(faults.length<MAX_FAULTS)faults.push({...clock(),where,error:String(error?.stack??error)});else faultDropped++;}
 function safe(where,fn){try{return fn();}catch(error){fault(where,error);return null;}}
 function baseTrack(t){return {...fields(t,['trackId','trackNumber','confirmed','sensorDetected','sensorAge','sensorHits','sensorSource','lastUpdateSeen','_lastMeasurementStep','memActive','reacquiring','trackLifecycle','_memReason','_spyReacquireHits','_spyConsecutiveDwellMisses','_spyDwellFailed','_spyLastMissTask','_spyLastMissReason','_spyExpectedRevisitS','_spyLastTaskType','_spyLastFace','fireControlQuality','kinematicQuality','trackQuality','_a3AuthorityReason','engagementAuthority','_kfNis','_kfRejectedNis','_wip11cSeaImpactCandidateS']),observedSeaImpactLatched:!!own(t,'_wip11cObservedSeaImpact')};}
 function track(t){const out=baseTrack(t),x=own(t,'_kfX'),p=own(t,'_kfP');if(x&&x.length===6)out.kf6=Array.from(x);if(p&&p.length===36)out.Pdiag=[0,7,14,21,28,35].map(i=>p[i]);return out;}
 function task(t){return fields(t,['trackId','type','seq','face','expectedRevisitS','priority','serviceAgeS','serviceDeadlineS']);}
 function push(row){if(records.length<MAX_RECORDS)records.push(row);else dropped++;}
 function before(tr,job){return {...clock(),track:track(tr),task:task(job)};}
 function after(kind,tr,job,prior,returned,value,reason){
  const post=track(tr),jobData=task(job),reacquireType=jobData.type==='TRACK_REACQUIRE'||jobData.type==='PRECISION_REACQUIRE',foreign=reacquireType&&jobData.trackId!==post.trackId,entered=prior?.track?.reacquiring!==true&&post.reacquiring===true;
  if(kind==='FINALIZE'){counts.focusedFinalize++;if(foreign)counts.foreignReacquireFinalize++;if(entered)counts.finalizeFalseToTrue++;if(foreign&&entered)counts.foreignFalseToTrue++;}
  else {counts.focusedMarkMiss++;if(entered)counts.markMissFalseToTrue++;}
  push({...clock(),kind,classification:'OBSERVED_NATIVE_RETURN_ONLY',trackId:post.trackId,task:jobData,before:prior?.track??null,after:post,reason:typeof reason==='string'?reason:null,nativeReturned:returned,nativeReturnSameTrack:returned&&value===tr,foreignReacquireTask:foreign,enteredReacquiring:entered});
 }
 window.__REACQ_CAUSE__=Object.freeze({
  install(){
   if(installed)return {installed:true,alreadyInstalled:true,scope:{fromS:FROM_S,toS:TO_S,trackIds:null,allTracks:true}};
   const finalize=spyFinalizeAcceptedTrackV31,mark=markSpyDwellMiss;sources.spyFinalizeAcceptedTrackV31=String(finalize);sources.markSpyDwellMiss=String(mark);
   spyFinalizeAcceptedTrackV31=function(...args){
    counts.finalizeCalls++;const tr=args[0],job=args[1],take=relevant(tr),prior=take?safe('FINALIZE_BEFORE',()=>before(tr,job)):null;let value,returned=false;
    try{value=finalize.apply(this,args);returned=true;return value;}
    finally{if(take)safe('FINALIZE_AFTER',()=>after('FINALIZE',tr,job,prior,returned,value,null));}
   };
   markSpyDwellMiss=function(...args){
    counts.markMissCalls++;const tr=args[0],job=args[1],take=relevant(tr),prior=take?safe('MARK_MISS_BEFORE',()=>before(tr,job)):null;let value,returned=false;
    try{value=mark.apply(this,args);returned=true;return value;}
    finally{if(take)safe('MARK_MISS_AFTER',()=>after('MARK_MISS',tr,job,prior,returned,value,args[2]));}
   };
   installed=true;return {installed:true,alreadyInstalled:false,scope:{fromS:FROM_S,toS:TO_S,trackIds:null,allTracks:true},nativeFunctionsWrapped:2,originalCallsPerWrapperInvocation:1,additionalNativeQueries:0};
  },
  snapshot(){return {schema:'AEGIS_REACQUISITION_CAUSE_OBSERVER_1',classification:'OBSERVED_NATIVE_RETURN_DIAGNOSTIC',installed,scope:{fromS:FROM_S,toS:TO_S,trackIds:null,allTracks:true},records:records.map(r=>({...r,task:{...r.task},before:r.before?{...r.before}:null,after:{...r.after}})),counts:{...counts},faults:faults.map(r=>({...r})),dropped,faultDropped,maxRecords:MAX_RECORDS,sources:{...sources},originalCallsPerWrapperInvocation:1,additionalNativeQueries:0,physicalTruthReads:0,gameProductChanged:false,expectedValuesChanged:false,releaseApproved:false};}
 });
})();
