# R4 finalizer ownership guard: independent design review

**Scope: source review and isolated actual-function execution. No product/source patch or browser run by this reviewer.** Root owns the implementation/build; the CIWS agent owns actual battle observer interpretation. Native full-world regression remains a separate requirement.

## Evidence and frozen change

The guarded R3 SHADOW observer established the candidate path while preserving its old-B-consuming native result: `B_stabilization_r3/evidence/battle-shadow-control/OWNERSHIP_PROOF.json/.md` records 101 foreign reacquisition finalizations and **92 observed foreign fresh false→true transitions**, with the first captured event at step721, task001→file003, quality0.991927→0.495964. Its window is 12–26 s; “first captured” is not automatically the first event in the entire battle. The separate ACTIVE R3 evidence is not an approved outcome replacement.

R4 changes the lifecycle consumer only, using patch manifest SHA `4e9299549de853906bca3c72fbf079bbd14ee911159039a2ccf02d5301ff46a3`. The actual added predicate is:

```js
const foreignFirmReturn =
  TRACK_B_IMPLEMENTATION_MODE === 'ACTIVE' &&
  TRACK_B_STABILIZATION_MODE === 'ACTIVE' &&
  task.trackId != null && task.trackId !== tr.trackId &&
  !tr.reacquiring &&
  (task.type === 'TRACK_REACQUIRE' || task.type === 'PRECISION_REACQUIRE');
```

The original reacquisition branch adds only `&& !foreignFirmReturn`. A guarded event consequently takes the **existing ordinary coherent-return branch**. No new lifecycle algorithm, quality formula, RF parameter, filter gain, hit threshold, readiness gate, identity policy or weapon coefficient is introduced.

Actual frozen products reviewed:

| Product | HTML SHA-256 | Main SHA-256 |
|---|---|---|
| R4 ACTIVE / STABLE_D | `48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab` | `6163ada1a49dc86ce8b179b81650fa2da78ecc8d9273015142a721748abf6a64` |
| R4 SHADOW | `3c7d2490e7e0d6fe94452e43d8f22132fbdd8add83986208bf7173068c478444` | `2ca44bf9914907e9f3c294791bc2d34431013e9045cfb9b19adf069db8e1f730` |

## Why this is a consumer-metadata correction

In the frozen B source `/dev/shm/track-b-stable-base.js` (SHA `616cb07bd7443031c36eece9419c4b7e249eee5d8e3494ed4539683a5b07e8be`), `spyFinalizeAcceptedTrackV31` L27261–27283 previously used the enclosing physical dwell's reacquisition type for any accepted track. Actual production calls are focused scheduled acceptance L27320 and global remainder acceptance L27340. Focused acceptance passes the scheduled track; only the global spillover naturally reaches another file. A diagnostic helper at L54656 also calls the finalizer without a task owner, and R4 deliberately preserves that original path.

The guard compares **canonical receiver track IDs** to the scheduler's intended receiver track ID. It does not read a physical entity, truth ID, faction, weapon label or a desired outcome. The foreign file's measurement was already accepted through the unchanged native association/EKF path. The correction prevents the scheduled file's task-mode metadata alone from creating a new recovery state on that other file.

The guard has these important limits:

- A file already reacquiring bypasses the guard and keeps its original first/second-hit recovery semantics, including a foreign coherent return.
- A scheduled owner match bypasses the guard. Its first successful recovery hit may still remain reacquiring; the second clears it as before.
- Null/undefined task owners bypass the guard. Ordinary task kinds bypass it. Either SHADOW flag bypasses it.
- The predicate does not require `confirmed=true`; “firm” in the variable name is narrower than the actual condition. An unconfirmed, non-reacquiring foreign file also takes the ordinary branch. The native tentative/confirmation logic is preserved, including the existing precision-task confirmation rule; this does not grant fire-control authority to an unconfirmed file.
- A truthy legacy `reacquiring` value is treated conservatively as already reacquiring by the actual `!tr.reacquiring` predicate. The ordinary canonical domain uses booleans.

Actual RF provenance is retained: `_spyLastTaskType` remains the **real** TRACK/PRECISION_REACQUIRE waveform/task, face and expected revisit remain actual task values, and the measurement's source/type/noise/covariance is not renamed to simulate another radar mode. The guard changes only which existing lifecycle-finalization branch consumes that already accepted return.

## Legitimate state and indirect effects

The native ordinary branch clears miss/recovery counters, memory reason and reacquisition, then computes the existing quality. The original first-reacquire branch halves quality while its flag is true. Therefore removing an unearned flag can naturally remove its half-quality penalty and permit the unchanged FCS/A3/AUTO readiness path to proceed. This is the intended consequence; **do not describe total AUTO outcomes as unchanged inside the guard**.

No EKF equation/gain or RF model is edited. Nevertheless later prediction uses the reacquiring flag to select existing process uncertainty, and later scheduler tasks depend on recovery state. A corrected flag can therefore change subsequent P, scheduling, native RF samples/RNG branching and combat outcomes. These indirect changes require actual regression evidence; an isolated-function test cannot prove full trajectory/RNG equivalence after a legitimate guard application.

The actual miss setter remains untouched, as do observed-sea-impact inference/clear rules, the original two-hit threshold, numeric quality formulas, FCS gates and AI policies. Do not compensate for a failed live case by changing those coefficients.

## Independent actual-function results

`tests_finalize_r4.cjs` extracts canonical native functions from the **actual packed HTML**, using Acorn `parseExpressionAt` on the short function scope. It executes the real finalizer, real `trackRefreshDerivedQuality`, and real `wip11cClearObservedSeaImpactTrack` in a fresh VM. Only their external dependencies provide declared fixture covariance metrics and count calls; no lifecycle/quality model is rewritten. No RF, EKF update, AI, weapon or game-world loop executes.

For each actual ACTIVE and SHADOW packed input separately:

| Result | Value |
|---|---:|
| Fixture cases | 44 |
| Legacy/stabilization flag × AUTO/MANUAL/SEMIAUTO combinations | 12 |
| Actual native finalizer transitions | 600 |
| Assertions | **3096 / 3096 PASS** |
| Guard-applied transitions | 48 |
| Unaffected exact-old-native transitions | 552 |
| Failures | 0 |
| Browser / game-world runs | 0 / 0 |

The 600 transitions include multi-hit sequences. Both packed inputs contain the same guarded finalizer body; VM flag variation checks its protected branches, not a user-facing mode switch. These are not two independent native battle regressions and must not be added to full-world test counts.

Native finalizer source hash changes `34cbc03c…37461`→`58b47d33…09cfe`. Actual native quality hash `5b3f6f62…e76cb5` and actual sea-clear hash `e46579f8…155179` are byte-identical. Dependency call order/counts, caller task, measurement/filter object references and stored values remain unchanged in every isolated case. Actual task provenance is asserted independently rather than discarded. Already-reacquiring/scheduled-owner/null-owner/ordinary-task and all SHADOW conditions are exact old-native comparisons.

Evidence: `evidence/finalize-native-vm.json` and `evidence/finalize-native-vm-shadow.json`. The test file SHA recorded by both is `f2e72bdc49df9468ec1fdf06c7a01be4abf2b19631d0b9b6933019f2b61b654d`. Actual full-world safety, natural-13 outcomes and inherited failures remain pending their own reported evidence. No existing expected value is approved by this review.
