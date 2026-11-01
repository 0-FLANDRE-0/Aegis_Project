// TEST ONLY / AFTER_ACTION_TRUTH_TEST_ONLY. No producer, NIS, filter or RNG queries.
// The historical paired120 recorder is installed immediately before this helper.
(() => {
 if(window.__ORIGINAL_RAID_PILOT__)throw Error('ORIGINAL_RAID_PILOT_INSTALLED_TWICE');
 const poses=[],events=[],faults=[],checkpoints=[],initial=[],all=new Map(),retirements=new Map(),interceptsByTarget=new Map();
 const own=(o,k)=>o==null?undefined:Object.getOwnPropertyDescriptor(o,k)?.value;
 const pick=(o,keys)=>Object.fromEntries(keys.flatMap(k=>{const v=own(o,k);return v===null||['number','boolean','string'].includes(typeof v)?[[k,v]]:[];}));
 const canonical=x=>JSON.stringify(x,(_k,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
 const stamp=()=>({step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT});
 let active=false,expected=null,gateFailure=null,cohortResolvedAt=null,lossAt=null,stopAt=null,stopCause=null,baseStart=null,native=null;
 function emit(kind,row={}){events.push({...stamp(),kind,tag:'AFTER_ACTION_TRUTH_TEST_ONLY',...row});}
 function target(t){return {...pick(t,['id','label','alive','life','maxLife','phase','_deathReason','retiredReason','_wip113Outcome','_outcomeRecorded','_warheadState','cruiseAltM','launchDistKm','seekerOn','seekerLocked','_diveStarted','_diveStartKm','_passedTarget','_blindTerminal']),
   positionM:{x:worldToMeters(t.x),y:worldToMeters(t.y),z:t.z},velocityMps:{x:worldSpeedToMps(t.vx??0),y:worldSpeedToMps(t.vy??0),z:t.vz??0},
   speedMps:t.speedMps??null,insAimM:{x:worldToMeters(t.insTgtX),y:worldToMeters(t.insTgtY)},
   flight:pick(own(t,'flight'),['timeS','engineTimeS','cruisePhase','bodyPitch','flightPath','cmdFlightPath','bodyYaw','flightPathYaw','cmdFlightPathYaw','massKg','propellantKg','fuelKg','thrustN','dragN','normalG','lateralG','availableG']),
   seeker:pick(own(t,'seeker'),['mode','timeS','trackValid','lastUpdateS']),
   nativeRetirement:retirements.get(t.id)??null,nativeInterceptResults:interceptsByTarget.get(t.id)??[],
   terminalClassification:t.alive===true?'STILL_ALIVE':retirements.has(t.id)?'NATIVE_TERMINAL:'+retirements.get(t.id).reason:'UNKNOWN_TERMINAL'};}
 function nativeLoss(){return floodAttitudePreviewV1.__pairedCauseRead().state==='LOST';}
 function resolved(t){return t.alive===false&&retirements.has(t.id);}
 function capture(force=false){
  for(const t of enemyMissiles)if(!all.has(t.id)){all.set(t.id,t);emit('NATIVE_ASM_FIRST_SEEN',{cohort:initial.includes(t)?'INITIAL_8':'LATER_SPAWN',id:t.id,label:t.label});}
  if(force||simStepCounter%600===0||simStepCounter===1920||simStepCounter===7200)poses.push({...stamp(),tag:'AFTER_ACTION_TRUTH_TEST_ONLY',own:{shipHP,navigation:pick(shipNav,['heading','speed','targetSpeedKt']),survival:floodAttitudePreviewV1.__pairedCauseRead()},initial:initial.map(target),later:Array.from(all.values()).filter(t=>!initial.includes(t)).map(target)});
 }
 function afterTick(){if(!active)return;try{
  if(simStepCounter===1920||simStepCounter===7200){
   const actual=window.__TRACK_B_PAIRED_CAUSE_120__.checkpoint(simStepCounter),wanted=expected[String(simStepCounter)],match=canonical(actual)===canonical(wanted);
   checkpoints.push({step:simStepCounter,fullRawExact:match,actual,expected:wanted});
   if(!match){gateFailure={step:simStepCounter,reason:'HISTORICAL_FULL_RAW_CHECKPOINT_MISMATCH'};emit('PREFLIGHT_BLOCKED',gateFailure);}
  }
  capture();
  if(initial.length===8&&initial.every(resolved)&&cohortResolvedAt==null){cohortResolvedAt=simStepCounter;emit('INITIAL_8_NATIVE_TERMINAL',{retirements:initial.map(t=>retirements.get(t.id))});if(stopAt==null){stopAt=simStepCounter+Math.ceil(5/SIM_FIXED_DT);stopCause='INITIAL_8_NATIVE_TERMINAL_PLUS_5S';}}
  if(nativeLoss()&&lossAt==null){lossAt=simStepCounter;emit('NATIVE_OWN_SHIP_LOST');if(stopAt==null){stopAt=simStepCounter+Math.ceil(5/SIM_FIXED_DT);stopCause='NATIVE_OWN_SHIP_LOST_PLUS_5S';}}
 }catch(e){faults.push({...stamp(),error:String(e?.stack??e)});gateFailure={step:simStepCounter,reason:'DIAGNOSTIC_OBSERVATION_FAULT'};}}
 window.__ORIGINAL_RAID_PILOT__=Object.freeze({
  start(options){if(active||native)throw Error('ORIGINAL_RAID_PILOT_ALREADY_STARTED');expected=options.checkpoints;
   if(!expected?.['1920']||!expected?.['7200'])throw Error('ORIGINAL_RAID_HISTORICAL_CHECKPOINTS_REQUIRED');
   native={tick:simulateFixedTick,retire:retireTruthAssociationV27,apply:applyInterceptResult,rf:trackRadarAssociationNisV31,asm:updateEnemyMissile,sam:updateMissile,spawn:spawnEnemyMissile};
   baseStart=window.__TRACK_B_PAIRED_CAUSE_120__.start();
   const baseTick=simulateFixedTick;
   retireTruthAssociationV27=function(...args){const result=native.retire.apply(this,args);if(active&&String(args[0]).toUpperCase()==='ASM'){const row={...stamp(),id:Number(args[1]),reason:String(args[2]??'TRUTH_ENDED')};retirements.set(row.id,row);emit('NATIVE_ASM_RETIREMENT',row);}return result;};
   applyInterceptResult=function(...args){const result=native.apply.apply(this,args);if(active){const row={...stamp(),targetId:args[1]?.id??null,weapon:args[2]??null,engagementTrackId:args[3]??null,result:typeof result==='string'?result:result?.result??result?.outcome??'UNSPECIFIED'};if(row.targetId!=null){const rows=interceptsByTarget.get(row.targetId)??[];rows.push(row);interceptsByTarget.set(row.targetId,rows);}emit('NATIVE_INTERCEPT_RESULT',row);}return result;};
   simulateFixedTick=function(...args){const value=baseTick.apply(this,args);afterTick();return value;};
   active=true;return {ready:true,baseStart,step:simStepCounter,tag:'TEST_COPY_ONLY'};
  },
  runFramesToTicks(fps,timeScale,targetTicks,fixture){
   if(!active||initial.length)throw Error('ORIGINAL_RAID_PILOT_BAD_START');
   if(!Array.isArray(fixture)||fixture.length!==8)throw Error('ORIGINAL_RAID_INITIAL_8_REQUIRED');
   for(const row of fixture){const t=enemyMissiles.find(x=>x.id===row.id);if(!t||t.label!=='Kh-32')throw Error('ORIGINAL_RAID_INITIAL_REFERENCE_MISSING');initial.push(t);all.set(t.id,t);}
   capture(true);emit('ORIGINAL_FIXTURE_COHORT',{initialIds:fixture.map(r=>r.id),initialCount:8});
   fps=Math.max(1,Number(fps)||60);timeScale=Math.max(0,Number(timeScale)||1);targetTicks=Math.max(0,Math.floor(Number(targetTicks)||0));
   if(fps!==60||timeScale!==8||targetTicks!==36000||simStepCounter!==0)throw Error('ORIGINAL_RAID_CLOCK_CONTRACT_CHANGED');
   let steps=0,frames=0,extraLifetimeTick=false;
   while(steps<targetTicks&&frames<1000000){
    steps+=window.__NAVAL_SIM_DIAG__.advanceFrameNoRender(1/fps,timeScale);frames++;
    if(gateFailure||simRuntimeFault)break;
    if(stopAt!=null&&simStepCounter>=stopAt){if(simStepCounter<7200){gateFailure={step:simStepCounter,reason:'RESOLVED_BEFORE_HISTORICAL_120S_CHECKPOINT'};}break;}
   }
   // Administrative lifetime uses `life > 600`, so allow exactly ONE native step.
   // Do not let a scale-8 frame accidentally add eight extra steps past the cap.
   if(!gateFailure&&!simRuntimeFault&&steps===36000&&initial.some(t=>!resolved(t))&&(stopAt==null||simStepCounter<stopAt)){
    const n=window.__NAVAL_SIM_DIAG__.advanceFrameNoRender(SIM_FIXED_DT,1);if(n!==1)throw Error('ORIGINAL_RAID_EXTRA_STEP_NOT_ONE');steps+=n;frames++;extraLifetimeTick=true;
   }
   capture(true);
   const reason=gateFailure?'BLOCKED_CHECKPOINT_OR_INSTRUMENTATION':simRuntimeFault?'NATIVE_RUNTIME_FAULT':stopAt!=null&&simStepCounter>=stopAt?stopCause:'HORIZON_REACHED_NOT_BATTLE_SUCCESS';
   emit('PILOT_END',{reason,extraLifetimeTick,initialNativeTerminal:initial.filter(resolved).length,unresolvedInitial:initial.filter(t=>!resolved(t)).map(t=>t.id)});
   return {steps,frames,simStepCounter,simAccumulator,pilotReason:reason,extraLifetimeTick};
  },
  proof(){if(!native)return null;return {pipeline:String(native.tick),retire:String(native.retire),apply:String(native.apply),rf:String(native.rf),asm:String(native.asm),sam:String(native.sam),spawn:String(native.spawn)};},
  stop(){active=false;const base=window.__TRACK_B_PAIRED_CAUSE_120__.stop();capture(true);simulateFixedTick=native.tick;retireTruthAssociationV27=native.retire;applyInterceptResult=native.apply;
   return {schema:'AEGIS_ORIGINAL_RAID_PILOT_1',tag:'AFTER_ACTION_TRUTH_TEST_ONLY',classificationAuthority:'PILOT_NATIVE_RETIREMENT_AND_INTERCEPT_EVENTS_ONLY; LEGACY_BASE_NATIVEOUTCOME_FALLBACK_IS_NONAUTHORITATIVE',checkpoints,gateFailure,faults,poses,events,initial:initial.map(target),later:Array.from(all.values()).filter(t=>!initial.includes(t)).map(target),cohortResolvedAt,lossAt,stopAt,stopCause,step:simStepCounter,base,restoredNativeRefs:{tick:simulateFixedTick===native.tick,retire:retireTruthAssociationV27===native.retire,apply:applyInterceptResult===native.apply}};
  }
 });
})();
