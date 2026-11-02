# Fresh measurements with reacquiring=true: source lineage review

**Read-only source/raw review and diagnostic preparation. No product patch, browser run, expectation or tolerance change.** The separate CIWS audit owns defense-logger interpretation and the native OFF/ON observer run. The source references below are the frozen B main `/dev/shm/track-b-stable-base.js`, SHA `616cb07bd7443031c36eece9419c4b7e249eee5d8e3494ed4539683a5b07e8be`; R2 retains these lifecycle/quality rules.

## Direct writers and clearing paths

| Native path | Actual state effect |
|---|---|
| `markSpyDwellMiss`, L27112–27122 | Sets `_spyDwellFailed`, increments `_spyConsecutiveDwellMisses`, stores actual task/reason, and sets `reacquiring=true` at the existing miss threshold (default 2). It does not reset `_spyReacquireHits`. |
| Focused `executeSpyTask`, L27315–27323 | If the scheduled track gets no accepted focused plot, calls the miss function with `NO_ASSOCIATED_PLOT` or `NO_PLOT`. This occurs **before** the global remainder selection. |
| `updateRadar`, L40074–40090 | On an unupdated file, consumes the already-set dwell-failure/miss count: enough misses sets reacquiring and keeps memory false until the higher hard-MEM threshold. An overdue age without that failure goes to COAST/STALE memory, not directly to reacquiring. After a fresh update, it preserves reacquisition/counters when `tr.reacquiring` is already true. |
| `spyFinalizeAcceptedTrackV31`, L27261–27283 | For `TRACK_REACQUIRE`/`PRECISION_REACQUIRE`, increments `_spyReacquireHits`; first accepted hit sets true, second clears true and resets counters. For an ordinary accepted task it clears reacquisition/miss/hit state immediately. |
| `spyFinalizeAcceptedSurfaceTrackWip13B9`, L27287–27294 | Clears reacquiring, memory, miss/reacquire counts and related surface state on an accepted surface observation. |
| Generic `updateSensorTrackMeasurement`, L27909–27917 | Sets fresh age, hits, last measurement, `lastUpdateSeen=true`, `memActive=false`; **does not clear reacquiring**. SPQ/visual/external freshness is therefore not by itself the SPY lifecycle-clear operation. |
| Observed sea-impact inference, L27518–27539 | Reads existing reacquiring/memory/misses/age and observed KF descent, can block/release support. It does **not** assign `reacquiring` or `_spyReacquireHits`. Associated SPY acceptance clears its inference at L27264, separately from reacquisition handling. |

GLOBAL HOLD itself skips a global plot at L27330–27331. It neither calls `markSpyDwellMiss` nor increments that counter. Fewer accepted updates can still indirectly change future prediction, scheduler selection, focused-gate outcomes or missed-dwell recovery, but that longer causal chain must be traced; it cannot be replaced by a direct HOLD→miss claim.

## An accepted-update path can also enter reacquisition

The finalizer's branch tests only **the enclosing task type**, without checking that `task.trackId` owns the accepted file:

```js
if(task.type==='TRACK_REACQUIRE'||task.type==='PRECISION_REACQUIRE'){
  tr._spyReacquireHits=(tr._spyReacquireHits??0)+1;
  tr.reacquiring=tr._spyReacquireHits<2;
  // first hit also raises consecutive misses to at least the reacquire threshold
}
```

The global remainder at L27340 passes the same enclosing task to **every** accepted file, including a file different from the scheduled track. Therefore a successful anonymous global update from another track's reacquisition dwell can move an otherwise firm/fresh neighboring file into `reacquiring=true` on its first reacquire-mode hit. That is an accepted-update/task-metadata integration path, distinct from a real focused miss and distinct from a global HOLD.

This source path exists but is **not yet proven to be the actual cause** of the reported R2 003 interval. The current defense logger records age/source/flag/quality but not actual task owner, `_spyReacquireHits`, or all direct-setter before/after states. Repeated `SPY1DV_TRACK_REACQUIRE` source labels are compatible with this path but do not establish it; own scheduled reacquisition is also compatible.

## Why fresh age and half quality are consistent

`trackRefreshDerivedQuality` L26451–26459 multiplies computed fire-control quality by **0.50** when reacquiring. `trackIsFireControlQuality` L27566–27581 separately rejects a reacquiring file regardless of the numerical quality. A3 L26551 requires confirmed, non-memory, non-reacquiring FCS-ready state; `wip119EvaluateRow` L50187 returns the direct `FCS_QUALITY` reason before the subsequent automatic A3 gate.

Thus a fresh measurement can drive age to zero and accurate covariance while the lifecycle's two-hit reacquisition latch still withholds fire. The observed roughly 0.483→0.966 quality change is consistent with that explicit factor; it is not evidence of an RF power, Pd, EKF-gain, or PN coefficient defect. This review proposes no change to those coefficients or the existing readiness gate.

Selected actual R2 defense-logger rows for 003 (`B_stabilization_r2/evidence/defense-timing-logger/candidate-active-NATURAL_SATURATION_13.json.gz`, `defenseExtra.records`):

| Time | Age | Stored source | reacquiring / memory | Quality | Direct result |
|---|---:|---|---|---:|---|
| 16.0 s | 0.016667 s | TRACK_REACQUIRE | false / false | 0.972202 | REENGAGE_HYST |
| 16.2 s | 0.066667 s | TRACK_REACQUIRE | true / false | 0.482672 | FCS_QUALITY |
| 16.6 s | 0 s | TRACK_REACQUIRE | true / false | 0.487977 | FCS_QUALITY |
| 17.2 s | 0 s | TRACK_REACQUIRE | true / false | 0.488666 | FCS_QUALITY |
| 17.4 s | **0.116667 s** | TRACK_REACQUIRE | true / false | 0.480717 | FCS_QUALITY |
| 17.6 s | 0.066667 s | TRACK_REACQUIRE | false / false | 0.965869 | ready |

Do not describe the entire interval as age≤0.066667: the raw 17.4 s row is larger. No sample was removed; it remains fresh while the separate latch is set. The table does not identify which native writer entered/re-entered that state.

## Minimal causal observer and conditional scope

Prepared `evidence/reacquisition-observer/extension.js` and `SOURCE_PLAN.md` wrap actual finalizer/miss calls exactly once and copy before/after stored fields, actual `task.trackId/type/seq/face`, accepted `tr.trackId`, hit/miss counters, freshness/memory/lifecycle/quality and stored sea-impact inference. They are inert until install, have bounded records/drop/fault counts, use no truth or extra native queries, and never feed an algorithm.

Helper SHA at preparation: `570a75e0ac634c9925cabb098e1a53ce8dc1a9f14d3aa0579a32116c5d49c2a2`. `node --check` passed. A local **mock-only** check preserved one original call, exact this/argument/return/throw, inert installation, idempotent installation and pure snapshots (2 mock finalizer calls including one throw, 1 miss call, 3 records, zero observer faults). Native OFF/ON equivalence and actual transition evidence are still the CIWS runner's responsibility; the mock is not game validation.

After actual proof, a possible narrow ACTIVE-global-remainder guard would distinguish a physical dwell's reacquisition waveform from ownership of the recipient file's lifecycle: do not let a foreign task mode alone start reacquisition on a firm accepted file. Keep the real measurement source/type/quality/noise and EKF update unchanged, keep actual own scheduled miss/reacquire handling, and preserve an already legitimate file's two-hit recovery. The exact treatment of a foreign observation of an already-reacquiring file requires a decision; it must not silently clear the latch. Old B/SHADOW exact behavior and all FCS/A3/AI gates remain protected. **No such guard has been applied here.**
