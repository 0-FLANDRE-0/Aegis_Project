// R2 TEST ONLY: copy already-produced native proposal trace scalars.
(()=>{const records=[],faults=[];let installed=false,dropped=0,source=null;
 const own=(o,k)=>o==null?undefined:Object.getOwnPropertyDescriptor(o,k)?.value;
 function fields(o,keys){const q={};for(const k of keys){const v=own(o,k);if(v!==undefined&&(v===null||['number','string','boolean'].includes(typeof v)))q[k]=v;}return q;}
 window.__R2_BATTLE_TRACE__=Object.freeze({install(){if(installed)return;installed=true;const prior=trackBTraceB;source=String(prior);trackBTraceB=function(...args){const result=prior.apply(this,args);try{const e=args[0];if((e?.decision==='COMPONENT'&&e.plotCount>12)||(simStepCounter>=157&&simStepCounter<=160&&['COMPONENT','BATCH'].includes(e?.decision))){if(records.length<1000)records.push({insideNativeTickCounter:simStepCounter,...fields(e,['decision','reason','route','observerShip','tick','timeS','active','mode','stabilizationMode','plotCount','trackCount','certifiedCount','evidenceResolved','lowerBoundCertifiedCount','exactResidualCertifiedCount','residualComponentsSolved','residualRefinementRejected','legacyCount','proposedCount','heldCount'])});else dropped++;}}catch(error){faults.push(String(error?.stack??error));}return result;};},snapshot(){return {schema:'AEGIS_R2_NATIVE_COMPONENT_TRACE_1',records,faults,dropped,source,scope:'Proposal component/BATCH arguments copied after original trace function once; no producer/filter/solver recomputation.'};}});
})();
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

// TEST_ONLY / OBSERVED_NATIVE_RETURN_DIAGNOSTIC. Never a product module.
// Copies consumed observations/own weapons; no tactical truth/entity lookup.
// Explicitly separate AFTER_ACTION_TRUTH_TEST_ONLY snapshots are below.
// Install AFTER frozen battle.js install() has captured original source receipts.
(() => {
  const records = [], largeGraphs = [], afterActionSnapshots = [], faults = [], sources = {}, counts = {};
  const FOCUS = new Set([300000003, 300000004]);
  const FROM_S = 30, TO_S = 41, MAX_RECORDS = 24000, MAX_GRAPHS = 256;
  let installed = false, evaluation = null, dropped = 0, graphDropped = 0, faultDropped = 0, afterActionDropped = 0, lastAfterActionStep = -1;
  const own = (object, key) => object == null ? undefined : Object.getOwnPropertyDescriptor(object, key)?.value;
  function fields(object, keys) {
    const out = {};
    for (const key of keys) {
      const value = own(object, key);
      if (value === null || ['string', 'boolean'].includes(typeof value)) out[key] = value;
      else if (typeof value === 'number') out[key] = Number.isFinite(value) ? value : String(value);
    }
    return out;
  }
  function clock() { return {step: simStepCounter, timeS: simStepCounter * SIM_FIXED_DT}; }
  function inWindow() { const t = simStepCounter * SIM_FIXED_DT; return t >= FROM_S && t <= TO_S; }
  function focused(id) { return inWindow(); }
  function fault(where, error) {
    if (faults.length < 64) faults.push({...clock(), where, error: String(error?.stack ?? error)});
    else faultDropped++;
  }
  function safe(where, read) { try { return read(); } catch (error) { fault(where, error); } }
  function record(kind, data) {
    if (records.length < MAX_RECORDS) records.push({...clock(), kind, ...data});
    else dropped++;
  }
  function trackData(track) {
    if (!track) return null;
    const out = fields(track, ['trackId', 'trackNumber', 'confirmed', 'memActive', 'reacquiring',
      'sensorDetected', 'sensorAge', 'sensorHits', 'sensorSource', 'classification',
      'identity', 'threatStatus', 'engagementAuthority', '_a3AuthorityReason',
      '_lastMeasurementStep', 'trackQuality', 'fireControlQuality', '_kfNis', '_kfRejectedNis']);
    const x = own(track, '_kfX'), p = own(track, '_kfP');
    if (x && x.length === 6) out.kf6 = Array.from(x);
    if (p && p.length === 36) out.Pdiag = [0, 7, 14, 21, 28, 35].map(i => p[i]);
    return out;
  }
  function pendingData(p) {
    return p ? fields(p, ['trackId', 'weapon', 'roundsRemaining', 'nextFireS', 'attemptCounted', 'startedS', 'salvoPolicy']) : null;
  }
  function responseData(id) {
    const r = wip119AutonomyState.responses.get(id);
    return r ? {...fields(r, ['trackId', 'autoEngagements', 'autoRounds', 'lastAutoFireS',
      'reengageThreatSinceS', 'lastAssessment', 'lastReengageRequired', 'lastSeenS', 'handoff']),
      byLayer: fields(own(r, 'autoEngagementsByLayer'), ['ESSM_BLK2_SIM', 'SM2MR_BLKIIIA_SIM', 'SM2ER_BLKIV_SIM', 'SM6_BLKIA_SIM'])} : null;
  }
  function rowData(row) {
    if (!row) return null;
    const out = fields(row, ['trackId', 'assessment', 'trackPresent', 'lostCoast',
      'coastFireControlUsable', 'lostConfidence', 'liveEngagement', 'reengageRequired',
      'weapon', 'salvo', 'recommendedRounds', 'salvoPolicy', 'canReengage',
      'rangeKm', 'altM', 'threatScore', 'cpaM', 'cpaTimeS', 'identity', 'threatStatus', 'engagementAuthority']);
    const plan = own(row, 'firePlan');
    out.firePlan = plan ? {...fields(plan, ['status', 'reason', 'fireDelayS', 'nezStartDelayS',
      'nezEndDelayS', 'interceptS', 'encounterAltM', 'availableG', 'targetEvasiveG', 'gMargin',
      'channelId', 'requiresIlluminator']), reservation: fields(own(plan, 'reservation'),
        ['illId', 'targetId', 'startT', 'endT', 'terminalStartT', 'predictedCpaT', 'weapon'])} : null;
    return out;
  }
  function resultData(result) {
    if (result == null || typeof result !== 'object') return {value: result ?? null};
    return {...fields(result, ['ok', 'ready', 'reason', 'text', 'need', 'waiting', 'nextStep', 'remainingS']),
      row: rowData(own(result, 'row')),
      a3Gate: fields(own(result, 'a3Gate'), ['ok', 'reason']),
      brake: fields(own(result, 'brake'), ['ok', 'reason', 'stableS', 'cooldownS', 'waitS']),
      reserve: fields(own(result, 'reserve'), ['ok', 'reason', 'total', 'have', 'reserve', 'need']),
      limit: {...fields(own(result, 'limit'), ['trackId', 'weapon', 'layerKey', 'totalCount',
        'layerCount', 'absoluteCap', 'adaptiveCap']), budget: fields(own(own(result, 'limit'), 'budget'),
          ['total', 'have', 'reserve', 'usableRounds', 'threatCount', 'roundsPerEngagement', 'fairShareRounds', 'rawCap', 'adaptiveCap', 'absoluteCap'])}};
  }
  function ownState(id) {
    const a = wip118ControlState.assessments.get(id);
    const release = ACTIVE_SHIP_RUNTIME.weapons.vlsReleaseB2;
    return {track: trackData(tracks.get(id)), response: responseData(id),
      assessment: a ? fields(a, ['trackId', 'state', 'trackPresent', 'liveEngagement',
        'reengageRequired', 'everEngaged', 'coastUsable', 'coastFireControlUsable',
        'lostStep', 'lostAgeS', 'lastSeenStep', 'lastAssessmentStep', 'cpaM', 'cpaTimeS', 'closureTgoS', 'harmlessStableS']) : null,
      pending: pendingData(wip119AutonomyState.pending),
      ownSam: missiles.filter(m => own(m, 'assignedTargetId') === id).map(m => fields(m,
        ['id', 'assignedTargetId', 'isESSM', 'isSM2ER', 'isSM6', 'dead', 'life'])),
      release: {...fields(release, ['busy', 'nextStep', 'lastStep', 'releaseCount', 'intervalS']),
        lastReject: fields(own(release, 'lastReject'), ['reason', 'step', 'weapon'])}};
  }
  function pairData(pair) {
    return {...fields(pair, ['i', 'id', 'nis']),
      sanity: fields(own(pair, 'sanity'), ['ok', 'reason', 'distanceM', 'distanceGateM',
        'measurementPositionSigmaM', 'radialInnovationMps', 'radialGateMps', 'positionDimensions']),
      evidence: fields(own(pair, 'evidence'), ['valid', 'dimensions', 'epochS', 'logDetS'])};
  }
  function afterActionData() {
    // AFTER_ACTION_TRUTH_TEST_ONLY. This separate output is never a tactical input.
    // Raw stored units only; no pose, RF, decoy or seeker helpers are invoked.
    const e = ACTIVE_SHIP_RUNTIME.ew.executionF;
    const decoys = ENGAGEMENT_RUNTIME.world.entities.activeDecoys;
    const pose = ['id', 'ownerEntityId', 'kind', 'alive', 'active', 'payloadActive', 'motorActive',
      'phase', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'life', 'ageS', 'maxLife', 'rfGain01',
      'rcsM2', 'baseRcsM2', 'radiusM', 'verticalThicknessM', 'terminalReason'];
    return {...clock(), tag: 'AFTER_ACTION_TRUTH_TEST_ONLY', neverTacticalInput: true,
      units: {WORLD_UNITS_PER_KM, xyAndVxVy: 'EXISTING_RAW_WORLD_UNITS', zVz: 'EXISTING_NATIVE_FIELDS_NO_CONVERSION'},
      ew: {executionPresent: e != null,
        executionScalars: fields(e, ['schema', 'serial', 'ageS', 'lastTick', 'ticks',
          'noiseRequested', 'deceptionRequested', 'auto', 'autoAim', 'bearing']),
        receiverScalars: fields(own(e, 'receiver'), ['lastAtS', 'noiseRatio']),
        ownCommandFlags: {noiseJamActive, deceptJamActive, softKillAutoDoctrine, jammerAutoTrack, jammerBearing, emconActive}},
      ownChaffCount: ownChaffs.length, ownChaffs: ownChaffs.map(q => fields(q, pose)),
      activeDecoyCount: decoys.length, activeDecoys: decoys.map(q => fields(q, pose)),
      aliveEnemyMissiles: enemyMissiles.filter(em => own(em, 'alive') === true).map(em => {
        const seeker = own(em, 'seeker');
        const out = {...fields(em, ['id', 'label', 'alive', 'x', 'y', 'z', 'vx', 'vy', 'vz',
          'phase', 'heading', 'seekerOn', 'seekerLocked', '_blindTerminal', '_outcomeRecorded']),
          seekerPresent: seeker != null, seekerScalars: fields(seeker, ['mode', 'trackValid',
            'lastGuidanceSource', 'lastHitAgeS', 'missAgeS', 'lastDeceptionPhase', 'lastHojMode',
            'lastSnr', 'lastPd', 'lastCleanSnr', 'lastSinr', 'lastJOverN', 'lastJOverS',
            'lastJammerRxW', 'lastReceiverNoiseW', 'lastDeceptionReturnCount', 'lastDeceptionRangePullM',
            'lastDeceptionDopplerBiasMps', 'lastDeceptionAnglePullDeg', 'lastDeceptionReplaySnr',
            'lastHojDirectJOverN', 'lastHojBearingDeg', 'lastAssocDebugKind', 'lastNis'])};
        for (const key of ['track', 'rawAim']) {
          const value = own(seeker, key);
          if (value != null) out['existing_' + key] = fields(value,
            ['x', 'y', 'z', 'vx', 'vy', 'vz', 'xM', 'yM', 'zM', 'vxMps', 'vyMps', 'vzMps',
              'valid', 'ageS', 'rangeM', 'azRad', 'elRad']);
        }
        return out;
      })};
  }
  function install() {
    if (installed) return;
    installed = true;
    const saveSource = (name, original) => { sources[name] = String(original); counts[name] = 0; return original; };

    const evaluate = saveSource('wip119EvaluateRow', wip119EvaluateRow);
    wip119EvaluateRow = function (...args) {
      counts.wip119EvaluateRow++;
      const priorContext = evaluation, id = own(args[0], 'trackId');
      evaluation = focused(id) ? {trackId: id} : null;
      let result, returned = false;
      try { result = evaluate.apply(this, args); returned = true; return result; }
      finally {
        if (evaluation && returned) safe('EVALUATE_ROW', () => record('EVALUATE_ROW', {
          trackId: id, forAuto: own(args[1], 'forAuto') === true,
          result: resultData(result), state: ownState(id)}));
        evaluation = priorContext;
      }
    };

    const fcq = saveSource('trackIsFireControlQuality', trackIsFireControlQuality);
    trackIsFireControlQuality = function (...args) {
      counts.trackIsFireControlQuality++;
      const result = fcq.apply(this, args);
      if (evaluation) safe('ACTUAL_FCQ', () => record('ACTUAL_FCQ', {
        evaluatedTrackId: evaluation.trackId, actualArgument: trackData(args[0]), result}));
      return result;
    };
    const gate = saveSource('trackEngagementGateA3', trackEngagementGateA3);
    trackEngagementGateA3 = function (...args) {
      counts.trackEngagementGateA3++;
      const result = gate.apply(this, args);
      if (evaluation) safe('ACTUAL_A3_GATE', () => record('ACTUAL_A3_GATE', {
        evaluatedTrackId: evaluation.trackId, trackId: args[0],
        options: fields(args[1], ['automatic', 'mode']), result: fields(result, ['ok', 'reason']),
        track: trackData(tracks.get(args[0]))}));
      return result;
    };

    const brake = saveSource('wip119ReengagementBrake', wip119ReengagementBrake);
    wip119ReengagementBrake = function (...args) {
      counts.wip119ReengagementBrake++;
      const result = brake.apply(this, args);
      if (evaluation) safe('ACTUAL_REENGAGE_BRAKE', () => record('ACTUAL_REENGAGE_BRAKE', {
        trackId: evaluation.trackId, result: fields(result, ['ok', 'reason', 'stableS', 'cooldownS', 'waitS']),
        response: responseData(evaluation.trackId)}));
      return result;
    };
    const memory = saveSource('wip119UpdateResponseMemory', wip119UpdateResponseMemory);
    wip119UpdateResponseMemory = function (...args) {
      counts.wip119UpdateResponseMemory++;
      const result = memory.apply(this, args);
      if (inWindow()) safe('ACTUAL_RESPONSE_MEMORY', () => record('ACTUAL_RESPONSE_MEMORY', {
        responses: Array.from(FOCUS, id => ({trackId: id, response: responseData(id)}))}));
      return result;
    };
    const process = saveSource('wip119ProcessPending', wip119ProcessPending);
    wip119ProcessPending = function (...args) {
      counts.wip119ProcessPending++;
      const id = own(wip119AutonomyState.pending, 'trackId');
      const before = focused(id) ? safe('PROCESS_PENDING_BEFORE', () => ownState(id)) : null;
      const result = process.apply(this, args);
      if (before) safe('ACTUAL_PROCESS_PENDING', () => record('ACTUAL_PROCESS_PENDING', {
        trackId: id, before, result: resultData(result), after: ownState(id)}));
      return result;
    };
    const fire = saveSource('wip119FireOne', wip119FireOne);
    wip119FireOne = function (...args) {
      counts.wip119FireOne++;
      const id = own(args[0], 'trackId');
      const before = focused(id) ? safe('FIRE_ONE_BEFORE', () => ownState(id)) : null;
      const result = fire.apply(this, args);
      if (before) safe('ACTUAL_FIRE_ONE', () => record('ACTUAL_FIRE_ONE', {
        trackId: id, before, result: resultData(result), after: ownState(id)}));
      return result;
    };
    const cancel = saveSource('wip119CancelPending', wip119CancelPending);
    wip119CancelPending = function (...args) {
      counts.wip119CancelPending++;
      const id = own(wip119AutonomyState.pending, 'trackId');
      const before = focused(id) ? safe('CANCEL_PENDING_BEFORE', () => pendingData(wip119AutonomyState.pending)) : null;
      const result = cancel.apply(this, args);
      if (before) safe('ACTUAL_CANCEL_PENDING', () => record('ACTUAL_CANCEL_PENDING', {
        trackId: id, reason: args[0] ?? 'MODE_CHANGE', before,
        after: pendingData(wip119AutonomyState.pending)}));
      return result;
    };

    const select = saveSource('trackBSelectB', trackBSelectB);
    trackBSelectB = function (...args) {
      counts.trackBSelectB++;
      const result = select.apply(this, args);
      safe('ACTUAL_LARGE_COMPONENT', () => {
        if (!(result.components ?? []).some(c => c.plots.length > 12 || c.tracks.length > 12)) return;
        if (largeGraphs.length >= MAX_GRAPHS) { graphDropped++; return; }
        const input = args[0];
        largeGraphs.push({...clock(), input: fields(input, ['route', 'observerShip', 'gate',
          'plotCount', 'tick', 'timeS', 'costUnits']), inputPairs: (input.pairs ?? []).map(pairData),
          inputLegacyPairs: (input.legacyPairs ?? []).map(pairData),
          actualSelectedPairs: (result.pairs ?? []).map(pairData),
          actualHeldPlots: Array.from(result.heldPlots ?? []), actualHeldTracks: Array.from(result.heldTracks ?? []),
          ...fields(result, ['active', 'stabilizationActive', 'ambiguous']),
          actualComponents: (result.components ?? []).map(c => ({...fields(c, ['edgeCount', 'ambiguous',
            'reason', 'certifiedCount', 'evidenceResolved', 'lowerBoundCertifiedCount',
            'exactResidualCertifiedCount', 'residualComponentsSolved', 'residualRefinementRejected']),
            plots: Array.from(c.plots), tracks: Array.from(c.tracks)}))});
      });
      return result;
    };
    const tick = saveSource('simulateFixedTick', simulateFixedTick);
    simulateFixedTick = function (...args) {
      counts.simulateFixedTick++;
      const result = tick.apply(this, args);
      // Exactly post-native-tick and at most once per simulated second.
      if (simStepCounter % 60 === 0 && simStepCounter !== lastAfterActionStep) safe('AFTER_ACTION_POST_TICK', () => {
        lastAfterActionStep = simStepCounter;
        if (afterActionSnapshots.length < 256) afterActionSnapshots.push(afterActionData());
        else afterActionDropped++;
      });
      return result;
    };
  }
  window.__DEFENSE_CAUSE__ = Object.freeze({install, snapshot() {
    return structuredClone({schema: 'AEGIS_R2_DEFENSE_NATIVE_RETURN_TRACE_1', installed,
      classification: 'TEST_ONLY_OBSERVED_AND_OWN_WEAPON_STATE_WITH_SEPARATE_AFTER_ACTION_TRUTH',
      scope: {focusTrackIds: null, allTracks: true, brakeResponseSnapshotTrackIds: Array.from(FOCUS), fromS: FROM_S, toS: TO_S,
        fcqAndA3Scope: 'ACTUAL_FOCUSED_EVALUATE_CALLS_ONLY', largeGraphScope: 'ALL_ACTUAL_COMPONENTS_OVER_12'},
      records, largeGraphs, afterActionSnapshots, faults, dropped, graphDropped, faultDropped, afterActionDropped, counts, sources,
      sourceReceiptMeaning: 'String of each prior installed function before this wrapper; select/tick may be frozen battle wrappers. Original product receipts remain battle.nativeSources.',
      originalCallsPerWrapperInvocation: 1, additionalNativeQueries: 0,
      gameProductChanged: false, expectedValuesChanged: false, releaseApproved: false});
  }});
})();

// TEST ONLY. Native sensor->association->AUTO->weapons->terminal pipeline.
// Truth samples are AFTER_ACTION_TRUTH_TEST_ONLY and never tactical inputs.
(() => {
 const events=[],samples=[],faults=[],initial=[],associationReturns=[],observedPlotLineage=[],ordnance=new Map(),lastTargets=new Map(),traceSamples=new Map(),holdStart=new Map(),holdDurations=[];
 const counts={ticks:0,events:0,eventsDropped:0,traceA:0,traceATypes:{},traceADecisions:{},nativeUpdates:0,traceB:0,holds:0,actualHeldPlotAppearances:0,actualSelectedPairAppearances:0,proposalHeldPlotAppearances:0,proposalHeldPlotsByRoute:{},associationReturnsDropped:0,lineageRecordsDropped:0,heldTrackTicks:0,componentMaximum:0,componentsOver12:0,launches:{},intercepts:{},phalanxHits:0,shipHitRecords:0,peakTracks:0};
 let active=false,installed=false,hitCursor=0,fireCursor=0,lastSample=-1,sourceReceipt=null,focusSampleStride=60,focusSampleUntilStep=0;
 const own=(o,k)=>o==null?undefined:Object.getOwnPropertyDescriptor(o,k)?.value;
 function fields(o,keys){const q={};for(const k of keys){const v=own(o,k);if(v!==undefined&&(v===null||['number','string','boolean'].includes(typeof v)))q[k]=v;}return q;}
 const now=()=>({step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT});
 function emit(kind,q={}){counts.events++;if(events.length<8000)events.push({...now(),kind,...q});else counts.eventsDropped++;}
 function safeObserve(fn){try{return fn();}catch(e){faults.push({...now(),error:String(e?.stack??e)});return null;}}
 function target(t){return {...fields(t,['id','label','alive','dead','life','_deathReason','retiredReason','_wip113Outcome','_outcomeRecorded','_warheadState']),retirement:fields(own(t,'_wip11cRetirementQueued'),['cause','step','outcome']),systems:fields(own(t,'_systemDamage'),['seeker','guidance','fuze','warhead','fuel','engine','fins']),behavior:fields(own(t,'_wip113Behavior'),['seekerFailed','guidanceMode','engineStopped','fuelEngineStopped','finsScale','availableG'])};}
 function terminal(t){const q=target(t);return q.alive===false&&!!(q.retirement.cause||q._deathReason||q._wip113Outcome||q.retiredReason);}
 function inventory(){const vls={};for(const[section,cells]of Object.entries(vlsCells)){vls[section]={};for(const c of cells){const k=c.destroyed?'DESTROYED':c.type;vls[section][k]=(vls[section][k]??0)+(k==='ESSM4'?c.essmCount:1);}}return {vls,ciws:ciws.map(m=>fields(m,['id','type','ammo']))};}
 function readTraceA(r){
  counts.traceA++;counts.traceATypes[r.type]=(counts.traceATypes[r.type]??0)+1;if(r.decision)counts.traceADecisions[r.decision]=(counts.traceADecisions[r.decision]??0)+1;
  if(r.type==='UPDATE')counts.nativeUpdates++;
  if(r.type==='UPDATE'&&r.measurement?.kind==='AIR_RADAR'&&simStepCounter*SIM_FIXED_DT<=5){if(observedPlotLineage.length<8000)observedPlotLineage.push({...fields(r,['serial','measurementId','route','observerShip','tick','timeS','trackId','decision','reason','nis','gate','gateUnits']),measurement:{...fields(r.measurement,['kind','sourceSensor','observerShip','measuredAtS','receivedAtS','quality']),model:r.measurement.measurementModel,observed:r.measurement.observed,providedSigmas:r.measurement.uncertainty?.providedSigmas??null},afterStateM:r.after?.stateM??null});else counts.lineageRecordsDropped++;}
  if(r.type==='UPDATE'&&r.decision==='ACCEPT'&&r.trackId!=null)for(const[k,start]of holdStart)if(k.endsWith(':'+r.trackId)&&(!r.observerShip||k.startsWith(String(r.observerShip)+':'))){const q={key:k,startStep:start,endStep:simStepCounter,durationS:(simStepCounter-start)*SIM_FIXED_DT,endEvidence:'NEXT_NATIVE_ACCEPTED_UPDATE',source:r.measurement?.sourceSensor??null};holdDurations.push(q);holdStart.delete(k);emit('HOLD_END',q);}
  if(!r.measurement)return;const k=String(r.trackId??'LOCAL:'+r.mountId)+':'+r.measurement.sourceSensor,n=traceSamples.get(k)??0;
  if(n<3&&(r.type==='UPDATE'||r.type==='MEASUREMENT')){traceSamples.set(k,n+1);emit('OBSERVED_SENSOR_RECORD',{record:{...fields(r,['type','route','trackId','mountId','decision','reason','nis','gate','gateUnits','appliedDimension']),measurement:{...fields(r.measurement,['kind','sourceSensor','observerShip','measuredAtS','receivedAtS','quality']),measuredFields:r.measurement.measuredFields,model:r.measurement.measurementModel,observed:r.measurement.observed}}});}
 }
 function install(){if(installed)return;installed=true;
  sourceReceipt={pipeline:String(simulateFixedTick),samFlight:String(updateMissile),asmFlight:String(updateEnemyMissile),pk:String(computeInterceptPk),applyPk:String(applyInterceptResult),association:typeof trackBSelectB==='function'?String(trackBSelectB):null,rfAssociation:String(trackRadarAssociationNisV31),spawn:String(spawnEnemyMissile),reset:String(_wip75ResetCase)};
  const traceA=trackATraceEventA;trackATraceEventA=function(...args){const serial=TRACK_A_DIAG.serial,result=traceA.apply(this,args);if(active&&TRACK_A_DIAG.serial>serial&&TRACK_A_DIAG.size)safeObserve(()=>readTraceA(TRACK_A_DIAG.ring[(TRACK_A_DIAG.head-1+TRACK_A_DIAG.capacity)%TRACK_A_DIAG.capacity]));return result;};
  if(typeof trackBTraceB==='function'){const traceB=trackBTraceB;trackBTraceB=function(...args){const result=traceB.apply(this,args);if(active&&args[0]?.decision==='HOLD')safeObserve(()=>{counts.proposalHeldPlotAppearances++;const route=args[0].route??'UNSPECIFIED';counts.proposalHeldPlotsByRoute[route]=(counts.proposalHeldPlotsByRoute[route]??0)+1;});return result;};}
  if(typeof trackBSelectB==='function'){const select=trackBSelectB;trackBSelectB=function(...args){const result=select.apply(this,args);if(active)safeObserve(()=>{const input=args[0],held=Array.from(result.heldTracks??[]),components=result.components??[];counts.traceB++;counts.holds+=held.length;counts.actualHeldPlotAppearances+=(result.heldPlots?.size??0);counts.actualSelectedPairAppearances+=(result.pairs?.length??0);if(associationReturns.length<12000)associationReturns.push({...now(),route:input.route,observerShip:input.observerShip,active:result.active===true,stabilizationActive:result.stabilizationActive??null,actualSelectedPairs:(result.pairs??[]).map(p=>fields(p,['i','id','nis'])),actualHeldPlots:Array.from(result.heldPlots??[]),actualHeldTracks:held,componentSemantics:result.active===false?'PROPOSAL_COMPONENTS_LEGACY_A_CONSUMED':'COMPONENTS_FROM_ACTUALLY_CONSUMED_RESULT',components:components.map(c=>({plots:c.plots.length,tracks:c.tracks.length,...fields(c,['edgeCount','ambiguous','reason'])}))});else counts.associationReturnsDropped++;for(const c of components){const n=Math.max(c.plots.length,c.tracks.length);counts.componentMaximum=Math.max(counts.componentMaximum,n);if(n>12){counts.componentsOver12++;if(events.filter(e=>e.kind==='NATURAL_COMPONENT_OVER12').length<3)emit('NATURAL_COMPONENT_OVER12',{route:input.route,plots:c.plots.length,tracks:c.tracks.length,edgeCount:c.edgeCount,reason:c.reason??null,appliedActive:result.active===true});}}for(const id of held){const k=String(input.observerShip)+':'+input.route+':'+id;if(!holdStart.has(k)){holdStart.set(k,simStepCounter);emit('HOLD_BEGIN',{route:input.route,trackId:id,gate:input.gate,plotCount:input.plotCount});}}if(result.ambiguous&&events.filter(e=>e.kind==='FIRST_AMBIGUOUS_COMPONENT').length<8)emit('FIRST_AMBIGUOUS_COMPONENT',{route:input.route,gate:input.gate,pairs:(input.pairs??[]).map(p=>({...fields(p,['i','id','nis']),evidence:fields(p.evidence,['valid','dimensions','epochS','logDetS'])})),actualSelectedPairs:(result.pairs??[]).map(p=>fields(p,['i','id','nis'])),componentSemantics:result.active===false?'PROPOSAL_COMPONENTS_LEGACY_A_CONSUMED':'COMPONENTS_FROM_ACTUALLY_CONSUMED_RESULT',heldPlots:Array.from(result.heldPlots??[]),heldTracks:held,components:components.map(c=>({plots:Array.from(c.plots),tracks:Array.from(c.tracks),...fields(c,['edgeCount','ambiguous','reason'])}))});});return result;};}
  const apply=applyInterceptResult;applyInterceptResult=function(...args){const result=apply.apply(this,args);if(active)safeObserve(()=>{const em=args[1],code=typeof result==='string'?result:result?.result??result?.outcome??'UNSPECIFIED';counts.intercepts[code]=(counts.intercepts[code]??0)+1;emit('NATIVE_INTERCEPT_RESULT',{result:code,weapon:args[2],trackId:args[3],target:target(em)});});return result;};
  const phalanx=applyPhalanxProjectileHit;applyPhalanxProjectileHit=function(...args){const result=phalanx.apply(this,args);if(active)safeObserve(()=>{counts.phalanxHits++;emit('NATIVE_PHALANX_HIT',{result:typeof result==='string'?result:result?.result??null,target:target(args[0])});});return result;};
 }
 function observe(force=false){safeObserve(()=>{
  counts.peakTracks=Math.max(counts.peakTracks,tracks.size);counts.heldTrackTicks+=holdStart.size;for(const m of missiles){const k='SAM:'+m.id;if(!ordnance.has(k)){ordnance.set(k,m);const w=m.weaponType??(m.isESSM?'ESSM':'SAM');counts.launches[w]=(counts.launches[w]??0)+1;emit('NATIVE_WEAPON_LAUNCH',{type:'SAM',...fields(m,['id','weaponType','assignedTargetId','targetId','life'])});}}
  for(const m of ramMissiles){const k='RAM:'+m.id;if(!ordnance.has(k)){ordnance.set(k,m);counts.launches.RAM=(counts.launches.RAM??0)+1;emit('NATIVE_WEAPON_LAUNCH',{type:'RAM',...fields(m,['id','assignedTargetId','targetId','life'])});}}
  for(const t of initial){const q=target(t),s=JSON.stringify({...q,life:undefined});if(lastTargets.get(t.id)!==s){lastTargets.set(t.id,s);emit('AFTER_ACTION_ASM_STATE',{tag:'AFTER_ACTION_TRUTH_TEST_ONLY',target:q});}}
  for(const h of shipHitHistory.slice(hitCursor)){counts.shipHitRecords++;emit('NATIVE_SHIP_HIT_RECORD',{hit:fields(h,Object.keys(h))});}hitCursor=shipHitHistory.length;
  const f=wip119AutonomyState.fireLog;for(const q of f.slice(fireCursor))emit('NATIVE_AUTO_FIRE_LOG',{record:fields(q,Object.keys(q))});fireCursor=f.length;
  if(force||simStepCounter%60===0||(simStepCounter<=focusSampleUntilStep&&simStepCounter%focusSampleStride===0)){if(lastSample===simStepCounter)return;lastSample=simStepCounter;const observed=Array.from(tracks.values(),t=>({...fields(t,['trackId','trackNumber','confirmed','sensorHits','sensorAge','sensorSource','identity','classification','engagementAuthority','_lastMeasurementStep','_kfNis','_kfRejectedNis']),kf6:t._kfX?Array.from(t._kfX):null,Pdiag:t._kfP?[0,7,14,21,28,35].map(i=>t._kfP[i]):null}));samples.push({...now(),tag:'OBSERVED_TRACKS_AND_AFTER_ACTION_TRUTH_SEPARATE',shipHP,ownPositionM:{x:worldToMeters(shipNav.positionWorld.x),y:worldToMeters(shipNav.positionWorld.y)},inventory:inventory(),tracks:observed,truthAfterAction:initial.map(t=>({...fields(t,['id','label','alive']),positionM:{x:worldToMeters(t.x),y:worldToMeters(t.y),z:t.z},velocityMps:{x:worldSpeedToMps(t.vx??0),y:worldSpeedToMps(t.vy??0),z:t.vz??0}}))});}
 });}
 window.__TRACK_STABLE_BATTLE__=Object.freeze({run(c){
  install();window.__R2_BATTLE_TRACE__.install();window.__REACQ_CAUSE__.install();window.__DEFENSE_CAUSE__.install();active=false;events.length=samples.length=faults.length=initial.length=holdDurations.length=associationReturns.length=observedPlotLineage.length=0;ordnance.clear();lastTargets.clear();traceSamples.clear();holdStart.clear();hitCursor=fireCursor=0;lastSample=-1;
  const freshInventory=inventory(),freshGunAuto=gunB1AutoSnapshot().enabled;_wip75ResetCase(c.seed);worldTimeScale=0;simAccumulator=0;BATTLESPACE_DIAG_BYPASS=false;DIAG_SUPPRESS_PATROLS=true;window.__NAVAL_SIM_DIAG__.wip119SetMode('AUTO');focusSampleStride=Math.max(1,Math.round(1/(c.afterActionSampleHz??1)/SIM_FIXED_DT));focusSampleUntilStep=Math.round((c.afterActionFocusS??0)/SIM_FIXED_DT);
  const resetInventory=inventory();if(JSON.stringify(freshInventory)!==JSON.stringify(resetInventory))throw Error('RESET_CHANGED_PROFILE_INVENTORY');if(gunB1AutoSnapshot().enabled!==freshGunAuto)throw Error('RESET_CHANGED_GUN_AUTO_SETTING');
  __TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_A__.clear();if(window.__TRACK_B__){__TRACK_B__.configure({enabled:true,capacity:4096});__TRACK_B__.clear();}
  const startsWithZeroTracks=tracks.size===0;for(const q of c.asms){const b=deg(q.bearingDeg),heading=b+Math.PI+deg(q.headingOffsetDeg??0),r=kmToWorld(q.rangeKm),vx=q.headingOffsetDeg?Math.cos(heading)*q.speedMps:-q.speedMps*Math.cos(b),vy=q.headingOffsetDeg?Math.sin(heading)*q.speedMps:-q.speedMps*Math.sin(b);spawnEnemyMissile({id:enemyMslSerial++,x:aircraft.x()+Math.cos(b)*r,y:aircraft.y()+Math.sin(b)*r,z:q.altM,heading,vx:mpsToWorldSpeed(vx),vy:mpsToWorldSpeed(vy),vz:0,asmType:q.label,lastKnownShipX:aircraft.x(),lastKnownShipY:aircraft.y()});initial.push(enemyMissiles.at(-1));}
  active=true;emit('FIXTURE_START',{setup:c,initialPhysicalCount:initial.length,startsWithZeroTracks,gunAuto:freshGunAuto,mode:engagementControlMode,emcon:emconActive,terrainBypass:BATTLESPACE_DIAG_BYPASS});observe(true);
  let resolvedStep=null,reason='HORIZON_UNRESOLVED';const maxTicks=Math.ceil(c.maxSeconds/SIM_FIXED_DT);for(let i=0;i<maxTicks;i++){simulateFixedTick(SIM_FIXED_DT);counts.ticks++;observe();if(faults.length){reason='DIAGNOSTIC_FAULT';break;}if(shipHP<=0&&floodAttitudePreviewV1.snapshot().irreversible){reason='OWN_SHIP_IRREVERSIBLE_LOSS';emit('NATIVE_OWN_SHIP_LOSS');break;}if(initial.every(terminal)){if(resolvedStep==null){resolvedStep=simStepCounter;emit('ALL_INITIAL_ASMS_NATIVE_TERMINAL');}if(simStepCounter-resolvedStep>=Math.ceil(5/SIM_FIXED_DT)){reason='ALL_INITIAL_ASMS_TERMINAL_PLUS_5S';break;}}}
  observe(true);active=false;for(const[k,start]of holdStart)holdDurations.push({key:k,startStep:start,endStep:simStepCounter,durationS:(simStepCounter-start)*SIM_FIXED_DT,openAtEnd:true});
  const exp=window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),targetResults=initial.map(target),launchCount=Object.values(counts.launches).reduce((a,b)=>a+b,0),resolved=targetResults.every(t=>t.alive===false&&!!(t.retirement.cause||t._deathReason||t._wip113Outcome||t.retiredReason));const qualification={startsWithZeroTracks,nativeSensorUpdates:counts.nativeUpdates>0,nativeAutoWeaponRelease:launchCount>0&&wip119AutonomyState.fireLog.length>0,initialThreatsResolvedOrNativeShipLost:resolved||reason==='OWN_SHIP_IRREVERSIBLE_LOSS',endedByNativeResolution:['ALL_INITIAL_ASMS_TERMINAL_PLUS_5S','OWN_SHIP_IRREVERSIBLE_LOSS'].includes(reason),noSamplerFault:faults.length===0,noDiagnosticDrop:counts.eventsDropped===0};
  return {schema:'AEGIS_TRACK_B_STABILIZATION_NATURAL_BATTLE_1',classification:'NATURAL_PRODUCT_SENSOR_AUTO_WEAPON_PATH_WITH_AFTER_ACTION_ONLY_TRUTH',case:c,mode:engagementControlMode,initialPhysicalCount:initial.length,startsWithZeroTracks,gunAuto:freshGunAuto,traceMode:window.__TRACK_B__?.mode??'TRACK_A',qualification,status:Object.values(qualification).every(Boolean)?'QUALIFYING_COMPLETED_BATTLE':'INCOMPLETE_NOT_DECISIVE',end:{reason,step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT,resolvedStep,remainingSam:missiles.length,remainingRam:ramMissiles.length,remainingInitialThreats:targetResults.filter(t=>t.alive).length},counts,associationReturns,observedPlotLineage,holdDurations,events,samples,targets:targetResults,final:{ship:exp.ship,inventory:inventory(),autonomy:{mode:engagementControlMode,totalAutoRounds:{...wip119AutonomyState.totalAutoRounds},fireLog:wip119AutonomyState.fireLog.map(q=>fields(q,Object.keys(q)))},globalRng:SIM_RNG_STATE,interceptHistory:SIM_TEST_INTERCEPT_HISTORY.map(q=>fields(q,Object.keys(q))),core:window.__CORE_SELFTEST_FAILURES__,runtimeFault:window.__WIP125_DIAG__.wip150RuntimeFault(),presentationFault:window.__WIP125_DIAG__.wip150PresentationFault()},diagnostics:{a:{serial:TRACK_A_DIAG.serial,dropped:TRACK_A_DIAG.dropped,errors:TRACK_A_DIAG.errors},b:typeof TRACK_B_DIAG==='undefined'?null:{serial:TRACK_B_DIAG.serial,dropped:TRACK_B_DIAG.dropped,errors:TRACK_B_DIAG.errors}},faults,nativeSources:sourceReceipt,r3Trace:window.__R2_BATTLE_TRACE__.snapshot(),reacqExtra:window.__REACQ_CAUSE__.snapshot(),defenseExtra:window.__DEFENSE_CAUSE__.snapshot()};
 }});
})();
