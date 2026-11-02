// Actual native finalizer/quality/sea-inference-clear functions, isolated VM.
// No browser or model replacement: dependencies return declared fixture metrics
// and count calls. No RF, EKF update, AI, weapon, truth or game-world execution.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),zlib=require('node:zlib');
let acorn;try{acorn=require('acorn');}catch(_){acorn=require('/workspace/aegis-performance-c/docs/performance/C/node_modules/acorn');}
const argv=process.argv.slice(2),arg=(k,d=null)=>argv.includes(k)?argv[argv.indexOf(k)+1]:d,sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const baselinePath=arg('--baseline','/dev/shm/track-b-stable-base.js'),candidatePath=arg('--candidate'),outPath=arg('--out');
const BASE_SHA='616cb07bd7443031c36eece9419c4b7e249eee5d8e3494ed4539683a5b07e8be';
function readSource(file){const raw=fs.readFileSync(file),text=raw.toString('utf8'),m=text.match(/data-c55-index="13">([^<]+)<\/script>/);const source=m?zlib.gunzipSync(Buffer.from(m[1],'base64')).toString('utf8'):text;return {file,fileSha256:sha(raw),mainSha256:sha(source),source};}
function extract(source,name){const re=new RegExp('^  function '+name+'\\(','gm'),hits=[...source.matchAll(re)];if(hits.length!==1)throw Error('CANONICAL_NATIVE_FUNCTION_NOT_UNIQUE:'+name+':'+hits.length);const start=hits[0].index+2,node=acorn.parseExpressionAt(source,start,{ecmaVersion:'latest'});if(node.type!=='FunctionExpression'||node.id?.name!==name)throw Error('AST_FUNCTION_MISMATCH:'+name);return {name,text:source.slice(start,node.end),line:source.slice(0,start).split('\n').length,start,end:node.end};}
const old=readSource(baselinePath);if(old.mainSha256!==BASE_SHA)throw Error('FROZEN_B_MAIN_PIN_CHANGED');
const names=['spyFinalizeAcceptedTrackV31','trackRefreshDerivedQuality','wip11cClearObservedSeaImpactTrack'];
function functions(input){return Object.fromEntries(names.map(n=>[n,extract(input.source,n)]));}
const nativeOld=functions(old);
if(!candidatePath){const report={status:'PREPARED_CANDIDATE_NOT_SUPPLIED',baseline:{file:old.file,mainSha256:old.mainSha256},nativeFunctions:Object.fromEntries(names.map(n=>[n,{line:nativeOld[n].line,sha256:sha(nativeOld[n].text)}])),browserRuns:0,actualGameWorldRuns:0};if(outPath)fs.writeFileSync(outPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));process.exit(0);}
const current=readSource(candidatePath),nativeCurrent=functions(current),expect=arg('--expect-candidate-main-sha');if(expect&&current.mainSha256!==expect)throw Error('CANDIDATE_MAIN_PIN_CHANGED');
for(const n of names.slice(1))if(nativeOld[n].text!==nativeCurrent[n].text)throw Error('PROTECTED_DEPENDENCY_CHANGED:'+n);
const canonical=x=>JSON.stringify(x,(_k,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v),clone=x=>JSON.parse(JSON.stringify(x));
function make(which,legacy,stable,engagement){
 const calls=[],context={TRACK_B_IMPLEMENTATION_MODE:legacy,TRACK_B_STABILIZATION_MODE:stable,engagementControlMode:engagement,Math,Number,Object,Set,
  SENSOR_MODEL:{spy1dv:{reacquireAfterMisses:2}},clamp:(x,a,b)=>Math.max(a,Math.min(b,x)),
  spyDesiredRevisitS:(t,type)=>{calls.push(['spyDesiredRevisitS',t.trackId,type]);return .1;},
  trackCovarianceMetrics:t=>{calls.push(['trackCovarianceMetrics',t.trackId]);return {posSigmaM:22,posMinorSigmaM:6,altSigmaM:12,velSigmaMps:4.2,ellipseAngleRad:.2};},
  wip121RestoreTargetSupportEligibility:id=>{calls.push(['wip121RestoreTargetSupportEligibility',id]);},
  spyScheduler:{measuredThisCycle:{add:id=>{calls.push(['measuredThisCycle.add',id]);}}}};
 vm.createContext(context);vm.runInContext(names.map(n=>which[n].text).join('\n'),context);return {context,calls};
}
const cases=[];
function add(name,type,owner,track={},task={},steps=1){const t={trackId:300000003,confirmed:true,sensorAge:0,memActive:false,reacquiring:false,_spyReacquireHits:0,_spyConsecutiveDwellMisses:0,_spyLastMissReason:'PREVIOUS',_memReason:'PREVIOUS',_spyDwellFailed:true,_wip11cSeaImpactCandidateS:.1,_wip11cObservedSeaImpact:{step:7},measurementSentinel:{rangeM:9000,azRad:.2,elRad:.01,radialMps:-280},_kfX:[1,2,3,4,5,6],_kfP:[1,2,3],...track};const job={type,trackId:owner,seq:17,face:'F2',expectedRevisitS:.1,...task};cases.push({name,track:t,task:job,steps});}
for(const type of ['TRACK_REACQUIRE','PRECISION_REACQUIRE']){
 add(type+':foreign-firm-first',type,300000004);
 add(type+':foreign-firm-two-successes',type,300000004,{}, {},2);
 add(type+':foreign-no-flag',type,300000004,{reacquiring:undefined});
 add(type+':foreign-already-reacquiring-first',type,300000004,{reacquiring:true,_spyReacquireHits:0,_spyConsecutiveDwellMisses:2});
 add(type+':foreign-already-reacquiring-second',type,300000004,{reacquiring:true,_spyReacquireHits:1,_spyConsecutiveDwellMisses:2});
 add(type+':foreign-recovery-sequence',type,300000004,{reacquiring:true,_spyReacquireHits:0,_spyConsecutiveDwellMisses:2},{},2);
 add(type+':own-first',type,300000003);
 add(type+':own-second',type,300000003,{reacquiring:true,_spyReacquireHits:1,_spyConsecutiveDwellMisses:2});
 add(type+':own-recovery-sequence',type,300000003,{reacquiring:true,_spyReacquireHits:0,_spyConsecutiveDwellMisses:2},{},2);
 add(type+':owner-null',type,null);
 add(type+':owner-undefined',type,undefined);
 add(type+':foreign-tentative',type,300000004,{confirmed:false});
 add(type+':foreign-fallback-revisit',type,300000004,{}, {expectedRevisitS:undefined});
 add(type+':foreign-supplied-revisit-zero',type,300000004,{}, {expectedRevisitS:0});
 add(type+':foreign-no-sea-inference',type,300000004,{_wip11cObservedSeaImpact:null});
}
for(const type of ['TRACK_REVISIT','TRACK_CONFIRM','HIGH_THREAT','MISSILE_SUPPORT','SPG_HANDOFF','PRECISION_LOCK','SEARCH_HORIZON']){
 add(type+':ordinary-firm',type,300000004);
 add(type+':ordinary-reacquiring',type,300000004,{reacquiring:true,_spyReacquireHits:1,_spyConsecutiveDwellMisses:3});
}
const observations=[],failures=[];let checks=0,guardedSteps=0,unaffectedSteps=0;
function check(ok,label,detail){checks++;if(!ok)failures.push({label,...detail});}
for(const legacy of ['ACTIVE','SHADOW'])for(const stable of ['ACTIVE','SHADOW'])for(const engagement of ['AUTO','MANUAL','SEMIAUTO'])for(const c of cases){
 const baseline=make(nativeOld,legacy,stable,engagement),candidate=make(nativeCurrent,legacy,stable,engagement),a=clone(c.track),b=clone(c.track),taskA=Object.freeze({...c.task}),taskB=Object.freeze({...c.task});
 for(let step=1;step<=c.steps;step++){
  const beforeA=clone(a),beforeB=clone(b),sentinel=b.measurementSentinel,kf=b._kfX,P=b._kfP,callsBeforeA=baseline.calls.length,callsBeforeB=candidate.calls.length;
  const ra=baseline.context.spyFinalizeAcceptedTrackV31(a,taskA),rb=candidate.context.spyFinalizeAcceptedTrackV31(b,taskB),label=[legacy,stable,engagement,c.name,step].join('/');
  const guard=legacy==='ACTIVE'&&stable==='ACTIVE'&&c.task.trackId!=null&&c.task.trackId!==beforeB.trackId&&!beforeB.reacquiring&&['TRACK_REACQUIRE','PRECISION_REACQUIRE'].includes(c.task.type);
  check(ra===a&&rb===b,label+':native-return-reference',{});
  check(canonical(c.task)===canonical(taskB),label+':task-unchanged',{});
  check(sentinel===b.measurementSentinel&&kf===b._kfX&&P===b._kfP&&canonical(b.measurementSentinel)===canonical(beforeB.measurementSentinel)&&canonical(b._kfX)===canonical(beforeB._kfX)&&canonical(b._kfP)===canonical(beforeB._kfP),label+':measurement-and-filter-untouched',{});
  check(canonical(baseline.calls.slice(callsBeforeA))===canonical(candidate.calls.slice(callsBeforeB)),label+':same-native-dependency-call-sequence',{before:baseline.calls.slice(callsBeforeA),after:candidate.calls.slice(callsBeforeB)});
  if(!guard){unaffectedSteps++;check(canonical(a)===canonical(b),label+':unaffected-exact-old-native',{before:a,after:b});}
  else{
   guardedSteps++;
   // Oracle is the UNMODIFIED native ordinary-return branch. Provenance is
   // independently checked against the actual task below, never discarded.
   const oracle=make(nativeOld,legacy,stable,engagement),ordinary=clone(beforeB),ordinaryType=c.task.type==='PRECISION_REACQUIRE'?'PRECISION_LOCK':'TRACK_REVISIT';oracle.context.spyFinalizeAcceptedTrackV31(ordinary,Object.freeze({...c.task,type:ordinaryType}));
   ordinary._spyLastTaskType=c.task.type;
   check(canonical(ordinary)===canonical(b),label+':actual-native-ordinary-branch',{expected:ordinary,after:b});
   check(b._spyLastTaskType===c.task.type&&b._spyLastFace===c.task.face&&b._spyExpectedRevisitS===(c.task.expectedRevisitS??.1),label+':actual-RF-task-provenance-preserved',{});
   check(b.reacquiring===false&&b._spyReacquireHits===0&&b._spyConsecutiveDwellMisses===0,label+':no-new-foreign-reacquire',{});
  }
  observations.push({legacy,stable,engagement,case:c.name,step,guardApplies:guard,before:{reacquiring:beforeB.reacquiring,hits:beforeB._spyReacquireHits,misses:beforeB._spyConsecutiveDwellMisses},after:{reacquiring:b.reacquiring,hits:b._spyReacquireHits,misses:b._spyConsecutiveDwellMisses,quality:b.fireControlQuality,lifecycle:b.trackLifecycle,sourceTask:b._spyLastTaskType}});
 }
}
const result={schema:'AEGIS_R4_ACTUAL_NATIVE_FINALIZER_VM_1',status:failures.length?'FAIL':'PASS',scope:'ACTUAL_FUNCTION_ISOLATION_WITH_DEPENDENCY_COUNT_STUBS_NOT_NATIVE_GAME_INTEGRATION',baseline:{file:old.file,fileSha256:old.fileSha256,mainSha256:old.mainSha256},candidate:{file:current.file,fileSha256:current.fileSha256,mainSha256:current.mainSha256},functionProof:Object.fromEntries(names.map(n=>[n,{before:sha(nativeOld[n].text),after:sha(nativeCurrent[n].text),same:nativeOld[n].text===nativeCurrent[n].text}])),testFileSha256:sha(fs.readFileSync(__filename)),cases:cases.length,modeCombinations:12,actualNativeSteps:observations.length,checks,guardedSteps,unaffectedSteps,failures,observations,browserRuns:0,actualGameWorldRuns:0,gameCodeChanged:false,expectedValuesChanged:false};
if(outPath){fs.mkdirSync(path.dirname(outPath),{recursive:true});fs.writeFileSync(outPath,JSON.stringify(result,null,2)+'\n');}console.log(JSON.stringify({...result,observations:undefined,failures:failures.slice(0,5)}));if(failures.length)process.exitCode=1;
