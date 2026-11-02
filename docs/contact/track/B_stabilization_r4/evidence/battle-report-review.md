# R4 battle report schema review

This is an offline report scaffold, not a battle result, approval, or additional game run. Main `BATTLE_RESULTS` files are intentionally untouched. The reviewed precedents are R1 `BATTLE_RESULTS` and its authority method, R2 ACTIVE13 `RESULTS`, R3 ACTIVE13 `RESULTS`, R4 SHADOW13 `CONTROL`, the existing raw R4 captures, and `MEASUREMENT_GAP_AUDIT.md`.

## Manifest and status

Use ten unique requested page keys: `{candidate-shadow,candidate-active}` crossed with `NATURAL_SATURATION_13`, `NATURAL_SATURATION_6`, `DDG_CONVERGING_2`, `CG_MULTIPLE_3`, and `DDG_BEARING_CROSSING_2`. Link each key to its actual folder; the two 13-target captures are in `battle-shadow-control` / `battle-active-pilot`, while the other eight belong to `battle-final-matrix`. Count each saved key once. Historical A/oldB captures and failed readiness attempts do not add pages to this denominator.

Suggested top-level JSON fields:

```json
{
  "schema": "AEGIS_TRACK_B_STABILIZATION_R4_BATTLE_RESULTS_1",
  "status": "PENDING | INVALID_EVIDENCE | FAIL | INCOMPLETE | PASS_LIMITED_SCENARIOS",
  "execution": {
    "expectedUniquePages": 10,
    "capturedUniquePages": 0,
    "faultFreeNativePages": 0,
    "qualifyingCompletedBattlePages": 0,
    "lifecycleIncompletePages": 0,
    "pendingPageKeys": [],
    "attemptReceipts": []
  },
  "products": {},
  "sourceFreezeModePairProofs": [],
  "captureManifest": [],
  "rows": [],
  "shadowControls": [],
  "historicalComparisons": [],
  "identityEvaluation": {
    "physicalIdSwapCount": null,
    "physicalFalseMergeCount": null,
    "physicalDuplicateTrackCount": null,
    "status": "UNKNOWN_NO_PHYSICAL_MEASUREMENT_LINEAGE"
  },
  "existingExpectationsChanged": false,
  "inheritedStrictFailuresApproved": false,
  "releaseApproved": false
}
```

The status names above are proposed report categories, not a new acceptance rule. Keep execution validity, completed-battle qualification, physical comparison, and approval separate. Ten valid captures cannot imply ten completed battles. Both existing R4 13-target captures are `INCOMPLETE_NOT_DECISIVE`, `HORIZON_UNRESOLVED` at 90 s; their continued presence prevents an all-ten completed-battle PASS. Existing strict failures and material outcome differences remain explicit regardless of graph or finalizer checks.

`captureManifest` should pin raw gzip, decoded receipt, row summary, passive file, product SHA, setup SHA, original base helper SHA, derived sampler SHA, observer SHA(s), runner SHA(s), and source/mode proof paths/hashes. Compute artifact hashes from their bytes. Do not represent a missing passive hash as an exact match because both values are null. Preserve each run's actual plan/receipt: the current shared `PLAN.json` may describe only the last singleton retry and is not an authoritative ten-page manifest.

The initial CG readiness crash remains an execution-attempt receipt: `TOOLING_INCOMPLETE_PRE_NATIVE_READINESS`, native battle not started, no game failure inferred. Retain `attempts/initial-readiness-crash.json` and passed-page artifacts; do not attribute a new OOM event from cumulative counters without a prior counter baseline. A successful retry fills the missing page key, rather than erasing the failed tool attempt or creating an eleventh battle.

## Per-page evidence

Each row should retain the raw `qualification`, raw battle status, complete `postValidation`, observer faults/drops, native trace errors, and transport/row-count receipts. Bounded native trace-ring overwrite is separate from sampler record loss. Retain `end` verbatim, including remaining initial threats and remaining defensive weapons.

Store these evidence groups separately:

| JSON group | Required contents and meaning |
|---|---|
| `initialThreats` | Initial physical count; one native final object per initial ID; alive IDs; unknown/unexplained terminal IDs; native retirement/death/outcome code histogram with IDs per code. These are unique initial-target states. |
| `interceptEffects` | Callback result counts and complete timeline, including target ID and native result. Callback `KILL` / `STRUCT_FAIL` counts are not unique initial kills; a deduplicated callback set is still separate from authoritative final retirement causes. |
| `shipEffects` | HP; total and per-cell flood water; full module-damage map; full operational export reference; actual damaging hit callbacks separately from `miss:true` and zero-damage callbacks; inventory/launch use and crew values where present. |
| `associationActual` | Native selector calls captured; actual selected pairs and held sets from the same return; held plot/track appearances; per-return one-to-one and selected/held overlap violations; actual component semantics. |
| `associationProposal` | Module proposal HOLD appearances/counts by route, separately labeled. SHADOW proposal decisions are not consumed decisions. |
| `logicalLineage` | Captured measurement/local-file structural evidence, actual time range and record count, repeated-measurement violations and repeated-same-file records separately. Not a physical identity oracle. |

For terminal states, preserve native reasons such as `INTERCEPT_KILL`, `NORMAL_HIT`, `DUD_PENETRATION`, `GUIDANCE_CONTROL_LOSS_MISS`, and `ALIVE`; do not reclassify them to improve an outcome. An alive damaged object is not automatically an effective threat or harmless. HP zero does not by itself prove the fixture's separate irreversible-loss stop condition: report HP and the actual end reason independently.

Historical comparison rows should include exact same-case setup/hash checks; A/oldB raw and product hashes; full native initial-target comparison; alive/terminal IDs and causes; per-module deltas over the union of module keys; total/per-cell flooding deltas; HP, hit/miss, inventory, launch/effect timeline, and end-state differences. Lower flood water does not erase increased surviving objects or changes to individual module damage. An unchanged HP-zero value does not establish equivalent defensive performance.

Historical fixtures may have a different derived observer helper. Record that difference honestly: match the underlying original helper/source lineage and setup SHA, and cite the applicable sampler/shadow controls. Do not set `sameFixtureSha256=true` when only the base helper is identical. A/oldB historical rows are pinned references, not fresh R4 executions or additions to the ten-page count.

## Full oldB SHADOW control

For every claimed case, compare R4 SHADOW to that case's frozen oldB ACTIVE capture. Preserve the existing full guard dimensions: established passive state; complete native final dict; initial ASM states; sampled observed/truth states; end/ticks; native intercept history; global RNG; actual selected/held return signature; appropriate native counters; protected source receipts; native post-validation; lifecycle/component observer faults/drops and the pure/mock observer guard. Each control needs both raw/passive/product paths and hashes.

The existing `battle-shadow-control/CONTROL.json` establishes this for the 13-target case only. Do not automatically turn it into five-case equivalence. Source receipts describe installed outer entrypoints/direct symbols; full underlying byte preservation is supported by frozen product/source proofs. ACTIVE reuse of the identical observer plus a pure/mock guard is not an unexecuted full-world ACTIVE OFF/ON equivalence test.

## Fresh foreign finalizer transitions

Use an explicit numerator, denominator and time/ID scope for each page. Suggested fields:

```json
{
  "observerScope": {
    "configuredFromS": 12,
    "configuredToS": 26,
    "receiverLocalTrackIds": [300000003, 300000004],
    "actualFirstRecordS": null,
    "actualLastRecordS": null
  },
  "allForeignReacquireFinalizeCalls": 0,
  "eligibleFreshForeignFinalizeCalls": 0,
  "foreignFreshFalseToTrueCount": 0,
  "foreignFreshFalseToTrueRate": null,
  "noEligibleOpportunity": true,
  "unknownBeforeOrOwnerRecords": 0,
  "markMissFalseToTrueCount": 0,
  "ownTaskFalseToTrueCount": 0,
  "observerFaultCount": 0,
  "observerDropped": 0,
  "observerFaultDropped": 0
}
```

Define an eligible record as captured `FINALIZE`, actual normal return of the same track, known task and recipient IDs, `TRACK_REACQUIRE` / `PRECISION_REACQUIRE`, foreign task owner, and explicit `before.reacquiring === false`; count explicit `after.reacquiring === true` in the numerator. Retain before-state freshness/firmness evidence such as confirmed, sensorAge, lastUpdateSeen, last measurement step and memActive, and state any extra freshness predicate used. Do not treat a missing before flag as proven false merely because the observer's generic `enteredReacquiring` uses `!== true`. A zero denominator produces rate `null` and “no eligible opportunity,” not a successful exercised transition check.

The existing ACTIVE13 raw supports **0/70** eligible fresh foreign FINALIZE transitions on those two local files in 12–26 s. All 70 are explicitly non-reacquiring, confirmed and sensorAge zero before the native call. Its 24 MARK_MISS false→true appearances remain separate and are not evidence that the foreign-FINALIZE guard failed. The SHADOW13 raw, intentionally consuming frozen oldB, preserves **92/92** such fresh false→true transitions among 101 total foreign finalizations. SHADOW is not expected to have the ACTIVE guard's zero. These are different observed call populations, not a matched 70-event counterfactual or a full-battle/all-file guarantee.

## Update timing and physical correspondence limits

Report three distinct timing measurements:

1. `holdToNextAcceptedUpdate`: all logged actual held-track episodes until the next native `ACCEPT UPDATE` for that receiver-local track across routes. Separate completed intervals from `openAtEnd` intervals. Report count/max (and any distribution) for completed intervals, and censored count/max elapsed separately. A censored interval has no observed next accepted update.
2. `sampledSensorAge`: existing track age samples and actual sample-gap distribution. Most full-battle samples are at 1 Hz; the bearing-crossing focus has denser first-five-second sampling. This is not a continuous maximum age/update-gap measurement.
3. `capturedAcceptedLineageSpacing`: same-local-track accepted record spacing only within the recorded AIR lineage window, with actual first/last times, record count, and routes/sources. It cannot establish a full-90-second maximum native update gap or per-plot physical lineage.

Current ACTIVE13 raw demonstrates why the separation matters: largest completed HOLD→nextACCEPT is **1.183333 s**, while an open-at-horizon interval has **51.016667 s** elapsed. Calling the latter “maximum HOLD-to-next-accepted-update” would invent an unobserved endpoint. Current lineage spans approximately 0.016667–4.983333 s, rather than 90 s.

Physical swaps, false merges, and duplicate physical contacts remain JSON `null` / UNKNOWN under `MEASUREMENT_GAP_AUDIT.md`. Per-return one-to-one violations and duplicate logical IDs in sampled tables can be counted within their recorded scope. Nearest-reference changes/shared-nearest groups, unresolved RF plots, marginal Pdiag residuals, and graph certification are separate descriptive evidence; none certifies physical identity continuity.

## Suggested Markdown presentation

Lead with captured/expected pages, actually qualifying completed battles, unresolved pages and approval status. Then use one compact row per requested R4 page with mode/case, native lifecycle status/end, HP/flood, unique native initial terminal histogram/alive count, actual HOLD plots/tracks, proposal HOLD count, and fresh-foreign numerator/denominator with window. Show 0/0 as unexercised.

Follow with per-case oldB SHADOW controls and a physical comparison table against the pinned references. Link full module/cell/target values and timelines in JSON rather than replacing them with a single HP metric. Explain the three timing scopes and the UNKNOWN physical-identity gap. Preserve the readiness crash receipt and all unresolved outcomes. End with the unchanged-expectation and release-unapproved flags, not an inferred release decision.
