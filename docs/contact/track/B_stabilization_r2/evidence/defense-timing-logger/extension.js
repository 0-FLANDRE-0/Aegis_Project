// TEST_ONLY / OBSERVED_NATIVE_RETURN_DIAGNOSTIC. Never a product module.
// Copies consumed observations/own weapons; no tactical truth/entity lookup.
// Explicitly separate AFTER_ACTION_TRUTH_TEST_ONLY snapshots are below.
// Install AFTER frozen battle.js install() has captured original source receipts.
(() => {
  const records = [], largeGraphs = [], afterActionSnapshots = [], faults = [], sources = {}, counts = {};
  const FOCUS = new Set([300000003, 300000004]);
  const FROM_S = 12, TO_S = 26, MAX_RECORDS = 12000, MAX_GRAPHS = 256;
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
  function focused(id) { return inWindow() && FOCUS.has(id); }
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
      scope: {focusTrackIds: Array.from(FOCUS), fromS: FROM_S, toS: TO_S,
        fcqAndA3Scope: 'ACTUAL_FOCUSED_EVALUATE_CALLS_ONLY', largeGraphScope: 'ALL_ACTUAL_COMPONENTS_OVER_12'},
      records, largeGraphs, afterActionSnapshots, faults, dropped, graphDropped, faultDropped, afterActionDropped, counts, sources,
      sourceReceiptMeaning: 'String of each prior installed function before this wrapper; select/tick may be frozen battle wrappers. Original product receipts remain battle.nativeSources.',
      originalCallsPerWrapperInvocation: 1, additionalNativeQueries: 0,
      gameProductChanged: false, expectedValuesChanged: false, releaseApproved: false});
  }});
})();
