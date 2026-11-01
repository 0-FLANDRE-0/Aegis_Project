# Original Kh-32 raid: one TRACK-A / DDG pilot plan

Plan status at preparation: **STATIC PREFLIGHT PASSED, NOT EXECUTED; browser GO not yet granted**. This is the preserved pre-execution plan. Root subsequently authorized the single pilot; its source/checkpoint proof, actual native results and 83.719 s wall time are recorded in `ORIGINAL_RAID_PILOT_RESULTS.md` and the pinned evidence. The two runtime raw checkpoints passed exactly. This plan itself does not authorize follow-up runs.

Purpose: obtain the missing native phase/position/termination evidence for the original paired raid. A qualifying low-altitude Kh-35U battle cannot by itself approve the four original raid state failures. This pilot is only TRACK-A / DDG; even a useful completed pilot cannot establish the required A/B DDG and CG comparisons.

## Execution budget, reported before running

Historical four-page A/B × DDG/CG 120 s measurement: **275.490 s wall**. Proportional estimate for one 600 s page: **344.362 s ≈ 5.7 min**. Provisionally reserve **5–10 minutes**, because continuing background aircraft/ASM and subsequent combat/damage can increase cost nonlinearly. This is not a guaranteed runtime. The runner acquires one existing `heavy_browser_slot()` lease and always closes its context/browser in `finally`; it must not be launched during the root's exclusive cost window or as a third browser.

There is no automatic B/DDG, CG, or further-horizon expansion. No browser starts unless both `--run` and `--root-go` are present. Default invocation writes the execution plan/diffs only. Root must give a fresh explicit GO after the measurement window.

## Pinned inputs and original setup

- Historical read-from-git revision: `5718f2d25f2e069f9ebd7948360fcf468bcdbb0b`.
- Product: `Aegis_SIM_v48_WIP_TRACK_A.html`, SHA-256 `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`.
- Ship: `DDG_119_LATE_FLIGHT_IIA`; seed `0x6d2b79f5` = 1831565813.
- Original H4 source: `docs/multiship/H4/regression_baseline.py`, file SHA `9c1c7239f31e9a0a15f3d752ab9a2925729758fd0f23fb879d5b7ec6e90479e0`.
- Original `scenario=>` AST expression SHA `1049cc9b70cd6e0718f33966a352cf3edfbf687fa5f64de38d2bba66c4ab2019`; paired effective readout expression SHA `3b54ea341abd67143df73dbc91aff1cd154d9f16a4958a6a9e5630b778b32d04`.
- Existing paired120 recorder SHA `057c658dc4c7df790f5cddfefd09881ca678720c416e8d4220615b0919f2d069`.

The runner reads historical inputs with `git show <revision>:<path>`, asserts the current read-only support files match those git bytes, and pins the HTML before/after. The original startup loader and original B2 regression `sitecustomize` must be installed. Without those prerequisites it is BLOCKED before browser launch.

The initial fixture remains eight native Kh-32 at 16 km / 10 km altitude, four cycling bearings, initial native TEST-track seeding, original AUTO command, terrain bypass, existing aircraft/patrol setting, profile inventory, gun/EW policy, target memory and all dynamics. No reset/suppression/new target scenario is substituted. The original output expression remains responsible for its existing final export.

## Precisely changed test-copy control flow

`original_raid_pilot.py` reuses `B/paired_cause.py:instrument` to expose the same cached scalar accessors, retains its native fixed-tick body/pipeline equality checks, and injects a **new in-memory test helper**. No existing file is rewritten.

The existing paired120 helper is read verbatim and receives only a read-only `checkpoint(step)` accessor in its test copy. Its original scalar/event capture is otherwise unchanged. `original_raid_pilot.js` adds separate AFTER_ACTION pose/cohort records and pass-through native wrappers. Every original wrapped call executes exactly once with original `this`, arguments and return value. No extra RF, seeker, NIS, association, EKF predict/update, RNG, inventory preview, or FCS command is evaluated.

The original effective JS expression has exactly two substitutions:

1. `raid:1920` → `raid:36000` (600 s maximum ordinary horizon).
2. `d.runFramesToTicks(60,scale,ticks)` → `window.__ORIGINAL_RAID_PILOT__.runFramesToTicks(60,scale,ticks,fixture)`.

The latter is a test loop with the original validation/arithmetic and the original `advanceFrameNoRender(1/60,8)` call. That native method still advances the complete installed fixed-tick pipeline. The only loop additions are diagnostic checkpoints, abort gates and terminal-cohort stop criteria. It never replaces or invokes a parallel missile/flight/RF/weapon implementation. The generated PLAN records original/effective/pilot expression hashes, original/copied/new/combined helper hashes and runner/support hashes; `expression.diff` and `helper-accessor.diff` retain the exact substitutions.

## Source and checkpoint gates

Before ticks, assert the instrumented body's original source SHA `8d2de4f64cb18e3248156e36fa454daee91b5603e03fee5a8f7bd372e0d5780e`, unchanged native fixed-tick body hash `a4360bd84ee5401aedfca45439dd0ff78a266101948433a006906b5eb72ad5b1`, and installed pipeline hash `c4f08708d5810c3838be61e8c354e5709178929007056069674a4624b8ffc1b1`. Save original spawn/ASM/SAM/RF/retirement/Pk-application function source hashes too. The helper restores its wrapped references before final ENV status query; no further ticks follow restoration.

At step **1920 (32 s)** and **7200 (120 s)** compare the **entire raw scalar object**, with no ignored field/tolerance, against the same step from the pinned historical `B/evidence/paired-cause-120/baseline-DDG_119_LATE_FLIGHT_IIA.json.gz`. This includes all archived scalar RNG banks, own cached navigation/physics/mass/survival, inventory, observers and object counts. Object key order is normalized for comparison; numeric values and array order are exact. The archive already has the original short-run 32 s bridge proof in its `checkpoint32Checks`; that original raw evidence remains retained.

Default preflight confirmed the historical bridge's six checks are all true, and loaded both full expected rows. Their audit JSON SHA-256 values (Python sorted-key JSON, not a substitute for runtime equality) are `11df86f92baf66d57a2a1a812e518adddae6b33f1ef49020df25243b9acff4ae` at 1920 and `f5a30b61af7cd91051930464b4170adc09e3792a5df360b26fd269c504da0378` at 7200. The pilot expression SHA is `dec108d0a5148a9da9c0f8410239d2e7cae5f831d6cd170e7f0d27a8c8c362e1`. Actual pilot-vs-history equality is still **PENDING** until explicit execution GO.

If either checkpoint differs or the observation code faults, stop and label **BLOCKED** immediately at that frame boundary. Do not continue to 600 s, update expectations, exclude differences or claim product failure/success from an invalid instrumented run. Since both checkpoint steps are multiples of eight, the original scale-8 frame ends exactly on those boundaries. A result that resolves before the established 120 s checkpoint is also invalid relative to the archived unresolved state and cannot be treated as a new success.

## New observations and stop criteria

Retain direct references to exactly the original `fixture`'s eight native ASM objects. Later native spawns are stored in a different list, not mistaken for original threats or used to prevent the initial cohort's decision. Every 10 simulated seconds, plus the two checkpoint/end samples, read primitives only:

- physical world position/velocity converted to metres/m/s, speed, `life` and `maxLife`;
- native `phase`, `flight.cruisePhase`, `flight.timeS`, body/flight/command angles;
- native cruise altitude, INS remembered aim, seeker ON/LOCK and existing seeker mode;
- existing engine time, thrust/drag, fuel/mass and achieved normal/lateral G;
- cached own navigation/HP/survival state; no recomputed geometry or target-truth association.

These are explicitly **AFTER_ACTION_TRUTH_TEST_ONLY**, never supplied to tactical code. Capture actual pass-through `retireTruthAssociationV27` and `applyInterceptResult` results with their native IDs/reasons. The old recorder keeps its existing native launch/system-hit/ship-hit records. A dead flag or disappearance without a recorded native reason does not establish a kill or a resolved threat.

The unchanged historical recorder contains a legacy `(!alive && _outcomeRecorded) → AIR_KILL` fallback. It happened to be inactive in the historical all-alive 120 s output, but is unsafe for this longer run. Its raw output is retained for provenance **and explicitly nonauthoritative**. Only the new helper's `terminalClassification` from an actual native retirement reason, actual per-target intercept results, ship-contact or native own-ship LOST event may support conclusions. A dead target without such a reason stays `UNKNOWN_TERMINAL`; SEA_IMPACT/MAX_LIFE are never promoted to a kill.

Early stop is eligible only after all eight original ASM are `alive=false` with actual native ASM retirement reasons, or native own-ship survival state becomes **LOST**. Continue at least five simulated seconds of aftermath. Because the original native scale-8 frame boundary is preserved, stop can be up to seven ticks (<0.117 s) later than that five-second threshold. The helper does not set survival, HP, missile flags or retire any object itself.

Ordinary horizon is exactly 36,000 ticks = 600 s. The existing native lifetime comparison is **`life > maxLife`**, where `maxLife=600`. If still unresolved at 36,000 ticks, allow **exactly one** `advanceFrameNoRender(SIM_FIXED_DT,1)` step (36,001 total = 600.0167 s), rather than an eight-tick frame. This is an explicitly disclosed administrative-boundary allowance, not a flight/physics change. If a native terminal event occurs too late to fit its five-second aftermath within the cap, retain the event and mark the pilot horizon incomplete for aftermath.

`MAX_LIFE`, missile timeout, battlespace exit, sea impact/miss, DAMAGED and actual KILL/STRUCT_FAIL remain distinct. In particular, all eight timing out near 600 s would explain retirement but would **not** demonstrate successful defensive interception or prove the old paired state deltas harmless.

## Intended commands after static/preflight review

From repository root, with root's browser GO still required:

```bash
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/dev/shm python docs/contact/track/B_stabilization/original_raid_pilot.py
```

The explicit execution command, only after that GO:

```bash
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/dev/shm B2_PHASE1_REGRESSION=1 B2_OUT=/dev/shm/aegis-ciws-dmg-a/docs/contact/track/B_stabilization/evidence/original-raid-pilot B2_HTML=Aegis_SIM_v48_WIP_TRACK_A.html PYTHONPATH=/dev/shm/aegis-ciws-dmg-a/docs/gun/B2/phase1b/test_support python docs/contact/track/B_stabilization/original_raid_pilot.py --run --root-go
```

Outputs live only in `B_stabilization/evidence/original-raid-pilot/`: frozen PLAN/diffs, original-expression result, raw compressed passive record, full raw checkpoint comparisons, source receipts, final ENV status, error evidence if any and SUMMARY. No existing product, baseline or expectation is edited. A useful A/DDG result is a new piece of evidence; comparative B/DDG and CG work would require a separately reviewed plan and cost, and all original strict failures remain unapproved meanwhile.

Execution preparation note: the first authorized launch stopped before opening any browser because the original `sitecustomize` requires `B2_OUT`. Its log is preserved as `startup-missing-B2_OUT.log`. The corrected command above supplies that original support requirement; no support/fixture source or comparison field was changed. A later GO/run is a distinct attempt, and its runtime result supersedes the plan's initial NOT EXECUTED status only after recorded evidence exists.
