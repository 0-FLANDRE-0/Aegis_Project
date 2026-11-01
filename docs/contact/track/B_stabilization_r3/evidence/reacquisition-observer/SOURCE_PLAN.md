# Reacquisition-state causal observer: diagnostic plan

**Test-copy observer only, not a product patch or a completed measurement.** `extension.js` is inert until `window.__REACQ_CAUSE__.install()` is called after the frozen battle helper has captured its source receipts. It wraps two naturally called functions: `spyFinalizeAcceptedTrackV31` and `markSpyDwellMiss`. Each wrapper preserves original `this`, arguments, return/throw and invokes the original exactly once.

## Question and existing source path

Frozen B input `/dev/shm/track-b-stable-base.js`, SHA `616cb07bd7443031c36eece9419c4b7e249eee5d8e3494ed4539683a5b07e8be`, has these relevant native rules:

- `markSpyDwellMiss` L27112–27122 increments the consecutive-miss count and sets `reacquiring=true` at the existing two-miss threshold. Its caller in focused `executeSpyTask` L27315–27323 runs **before** the global remainder solve. Global HOLD merely skips that global plot; it does not directly call the miss setter.
- `spyFinalizeAcceptedTrackV31` L27261–27283, for `TRACK_REACQUIRE` or `PRECISION_REACQUIRE`, increments `_spyReacquireHits`, sets `reacquiring=(hits<2)`, and raises the miss count to at least the reacquire threshold on the first accepted hit. The second such hit clears the state/counters. An ordinary accepted SPY task clears them immediately. The function does not check `task.trackId===tr.trackId`.
- Both focused acceptance and **every accepted global remainder** call that same finalizer with the enclosing physical dwell's `task` (L27320/L27340). A foreign scheduled file's reacquisition dwell can therefore set the state on a fresh neighboring file after an accepted anonymous global association. This is a source-permitted candidate cause, not proof it happened in the reported R2 interval.
- `updateSensorTrackMeasurement` L27909–27917 refreshes `sensorAge=0`, `lastUpdateSeen=true` and `memActive=false`, but does not clear `reacquiring`. `updateRadar` L40086–40090 deliberately keeps the reacquiring state/counters even after a fresh hit. Fresh age and `memActive=false` thus do not contradict a reacquisition latch.
- `trackRefreshDerivedQuality` L26451–26459 multiplies FC quality by 0.50 while reacquiring. `trackIsFireControlQuality` L27566–27581 rejects reacquiring independently of numeric quality. A3 L26551 and `wip119EvaluateRow` L50187 preserve that rejection. Sea-impact inference L27518–27539 reads this state and can block support, but does not assign `reacquiring` or reset its hit counter.

## Exact observer output

For canonical tracks 300000003/300000004, native calls from 12 through 26 s record actual task owner/type/sequence/face and track ID, with before/after values of:

- `reacquiring`, `_spyReacquireHits`, `_spyConsecutiveDwellMisses`, `_spyDwellFailed`, last miss task/reason;
- memory/lifecycle/reason, sensor age/source/hits/last-measurement step and `lastUpdateSeen`;
- existing quality/authority fields and already stored native NIS;
- already stored observed-sea-impact candidate/latch, without evaluating that inference.

Derived diagnostic flags only label actual records: foreign reacquire-task ownership, false→true transition, and whether the original returned the same track. They are not supplied to a game algorithm. There are no reads of physical objects, truth maps, sensor constructors, filter/NIS helpers or policy getters. `Object.getOwnPropertyDescriptor(...).value` reads stored fields without invoking getters. Source strings are saved at install; bounds are 16,384 records and 64 faults, with explicit drop counters. Any drop/fault makes causal closure incomplete rather than being ignored.

`snapshot()` only copies observer-owned records/counters/source receipts. It does not evaluate game functions or mutate the canonical state. Install is idempotent and does not issue a command. The runner must install once after the original helper's receipt and before the native battle, capture the snapshot after completion, and pin executed extension SHA. No original source or raw evidence is overwritten.

## Required same-product guards

Before interpreting a state transition, compare the exact same pinned product and executable fixture with the established OFF capture: complete final/passive state, actual outcomes/target results, native call/context sequence, all captured association returns, sampled observations/physical after-action state, RNG/ticks/end, and native source receipts. Preserve all raw mismatches. Original call-count=1 and no-extra-query behavior should also be checked with small local mock functions; this is not a substitute for native OFF/ON equality.

Evidence sufficient for the candidate path would be an actual `FINALIZE` record with `task.type` a reacquire task, `task.trackId != tr.trackId`, before `reacquiring=false`, after `true`, and the counter transition 0→1. If the only entry is an actual `MARK_MISS`, report that native reason instead. If entry precedes the window or another direct setter acts outside these wrappers, report the missing lineage rather than infer it.

## Conditional product guard proposal—NOT APPLIED

Only after actual causal proof and an explicit scope decision, consider limiting **new ACTIVE global-remainder** metadata application for a foreign reacquisition task. Keep its real RF waveform/source/type, measurement/noise/covariance, native association result and EKF correction untouched. Prevent that foreign task's mode alone from moving an otherwise firm accepted file into reacquisition; do not bypass an already legitimate reacquisition state or its two-hit recovery requirement. Preserve focused scheduled-target handling, actual miss accounting, sea-impact rules and existing FCS/A3/AI gates.

The precise policy for a foreign coherent observation of a file already reacquiring needs an explicit decision after the trace; do not silently clear it or claim that two-hit recovery is unnecessary. Old B and SHADOW must remain exact. Negative/positive verification must include own scheduled first/second reacquire hits, real two-miss entry, foreign acceptance of a firm file, foreign acceptance of an already-reacquiring file, and HOLD without a native miss call. No threshold, Pd, EKF, weapon or AI coefficient changes are proposed.
