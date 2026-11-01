// TEST COPY ONLY. Records already-produced diagnostic events and passive receiver
// estimates; never regenerates RF, NIS, EKF, assignment, FCS or physical caches.
(() => {
 if(window.__TRACK_B_SEED_TRACE__)throw Error('SEED_TRACE_INSTALLED_TWICE');
 const records=[],faults=[],counts={aEvents:0,bEvents:0,frames:0,nativeTickCalls:0,aWrapperCalls:0,bWrapperCalls:0};
 const nativeA=trackATraceEventA,nativeB=typeof trackBTraceB==='function'?trackBTraceB:null,nativeTick=simulateFixedTick,nativeSpawn=spawnEnemyMissile,nativeIntercept=applyInterceptResult;
 const lowerS=29,upperS=30.65,maxBytes=8*1024*1024;
 let armed=false,bytes=0,overflow=false,serial=0;
 const own=(o,k)=>o==null?undefined:Object.getOwnPropertyDescriptor(o,k)?.value;
 const finite=v=>typeof v==='number'&&Number.isFinite(v),simple=v=>v===null||['string','boolean'].includes(typeof v)||finite(v);
 function pick(o,keys){const out={};for(const k of keys){const v=own(o,k);if(simple(v))out[k]=v;}return out;}
 const numberArray=v=>v&&(Array.isArray(v)||ArrayBuffer.isView(v))?Array.from(v,x=>finite(x)?x:null):null;
 function within(){const t=simStepCounter*SIM_FIXED_DT;return armed&&t>=lowerS&&t<=upperS;}
 function append(kind,value){
  if(!within()||overflow)return;
  try{const record={serial:++serial,kind,step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT,value},text=JSON.stringify(record);if(bytes+text.length*2>maxBytes){overflow=true;faults.push({step:simStepCounter,reason:'TRACE_BYTE_BOUND_REACHED'});return;}bytes+=text.length*2;records.push(JSON.parse(text));}
  catch(e){faults.push({step:simStepCounter,reason:String(e?.stack??e)});}
 }
 function canonical(){return [...tracks.values()].map(t=>({...pick(t,['trackId','trackNumber','sensorSource','sensorAge','sensorHits','confirmed','domain','classification','identity','threatStatus','engagementAuthority','trackLifecycle','memActive','ttl','_lastMeasurementStep','lastMeasurementS','_kfNis','_kfRejectedNis','_kfRejectedCount','_radar3dAirStepFC','_surface2DOnlyFC','_surfaceMotionPriorWip13B13']),stateM:numberArray(own(t,'_kfX')),covariance:numberArray(own(t,'_kfP'))}));}
 function c55(){return [...CIWS_C55.banks].map(([mountId,b])=>({mountId,...pick(b,['winner','status','reason']),cues:(b.cues??[]).map((q,order)=>({order,...pick(q,['trackId','sigmaM','identity','cueEligible']),estimatedState:pick(q.state,['rxM','ryM','rzM','rvxMps','rvyMps','rvzMps']),nativeKinematics:pick(q.kin,['ttiS','rangeM','closingMps','tCpaS','cpaM','impactS'])})),files:[...b.files.values()].map(f=>({...pick(f,['id','cmsTrackId','confirmed','ownFireEvidence','protectedIdentity','lastSeenS','lastCmsS','createdS']),local:pick(f.st,['rxM','ryM','rzM','rvxMps','rvyMps','rvzMps','localHits','localAgeS','quality','valid','rangeM','localNis'])}))}));}
 function frame(){if(!within())return;counts.frames++;append('PASSIVE_RECEIVER_FRAME',{tracks:canonical(),c55:c55(),mounts:ciws.map(m=>pick(m,['id','type','state','ammo','trackingTrackId','cuedTarget','firing','tracking']))});}
 const wrappedA=function(){counts.aWrapperCalls++;const before=TRACK_A_DIAG.serial,result=nativeA.apply(this,arguments);if(within()&&TRACK_A_DIAG.serial>before&&TRACK_A_DIAG.size){const record=TRACK_A_DIAG.ring[(TRACK_A_DIAG.head-1+TRACK_A_DIAG.capacity)%TRACK_A_DIAG.capacity];counts.aEvents++;append('ALREADY_EMITTED_A_TRACE',record);}return result;};
 const wrappedB=nativeB?function(){counts.bWrapperCalls++;const before=TRACK_B_DIAG.serial,result=nativeB.apply(this,arguments);if(within()&&TRACK_B_DIAG.serial>before&&TRACK_B_DIAG.records.length){counts.bEvents++;append('ALREADY_EMITTED_B_TRACE',TRACK_B_DIAG.records[TRACK_B_DIAG.records.length-1]);}return result;}:null;
 const wrappedTick=function(){counts.nativeTickCalls++;const result=nativeTick.apply(this,arguments);frame();return result;};
 window.__TRACK_B_SEED_TRACE__=Object.freeze({
  start(){if(armed||records.length)throw Error('SEED_TRACE_ALREADY_STARTED');trackATraceEventA=wrappedA;if(nativeB)trackBTraceB=wrappedB;simulateFixedTick=wrappedTick;armed=true;return {classification:'TEST_ONLY_PASSIVE_NATIVE_EVENT_WATCH',windowS:[lowerS,upperS],maxBytes,nativeFunctionsInvokedOncePerWrapperCall:true};},
  stop(){armed=false;trackATraceEventA=nativeA;if(nativeB)trackBTraceB=nativeB;return {classification:'DIAGNOSTIC_ESTIMATES_NOT_TRUTH',count:records.length,bytesUpperBound:bytes,maxBytes,overflow,faults:JSON.parse(JSON.stringify(faults)),counts:{...counts}};},
  info(){return {count:records.length,bytesUpperBound:bytes,overflow,faults:JSON.parse(JSON.stringify(faults)),counts:{...counts},windowS:[lowerS,upperS],nativeSources:{a:String(nativeA),b:nativeB?String(nativeB):null,tick:String(nativeTick),originalSpawnEnemyMissile:String(nativeSpawn),originalApplyInterceptResult:String(nativeIntercept)}};},
  restoreOriginalDiagnosticEnvBindings(){if(armed)throw Error('STOP_CAPTURE_BEFORE_RESTORING_TEST_BINDINGS');spawnEnemyMissile=nativeSpawn;applyInterceptResult=nativeIntercept;return {scope:'TEST_ONLY_RESTORE_TWO_ORIGINAL_DIAGNOSTIC_WRAPPERS_AFTER_UNCHANGED_RUN',spawnBindingExact:spawnEnemyMissile===nativeSpawn,interceptBindingExact:applyInterceptResult===nativeIntercept,noFurtherTicksIssued:true};},
  read(start,count){return JSON.parse(JSON.stringify(records.slice(start,start+count)));}
 });
})();
