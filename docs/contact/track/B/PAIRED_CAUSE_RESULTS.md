# Strict paired raid differences: measured causal chain

The DDG and CG `samePhysicalState` / `sameExistingObserverState` checks remain
**four FAILs, unapproved**. This document explains observed changes; it does not
change an expected value or approve release. Inherited friendly-contact seed
419025 and its paired observer differences also remain independently unapproved.

## Original 32-second fixture controls

The original H4/HELI-F raid was run for DDG/CG × TRACK-A/SHADOW/ACTIVE using the
original loader, seed, settings, command literal and fixed-tick pipeline.
Products are pinned in `PAIRED_CAUSE_PLAN.md`. All six pages captured an initial
record and 1920 actual tick returns, with zero sampler faults. Total wall time
was 171.112 s. A separate ACTIVE diagnostic ON/OFF guard took 58.521 s.

| Check | DDG | CG |
|---|---:|---:|
| TRACK-A final state/dynamics/observers/offboard/RNG vs original archive | 5/5 exact | 5/5 exact |
| ACTIVE final state/dynamics/observers/offboard/RNG vs original archive | 5/5 exact | 5/5 exact |
| TRACK-A vs SHADOW, all 1921 recorded native rows | exact | exact |
| ACTIVE recorder OFF vs ON, all recorded native rows | exact | exact |
| Cached end physics vs the original final physics readout | exact | exact |
| Repeated trace serials in the incremental capture | 0 | 0 |
| Default/OFF record bytes, A / ACTIVE | 8,732,838 / 8,868,102 | 8,002,294 / 7,975,437 |

The runtime base fixed-tick body SHA is
`a4360bd84ee5401aedfca45439dd0ff78a266101948433a006906b5eb72ad5b1`.
The actual installed native MAP_D.mount pipeline wrapper SHA is
`c4f08708d5810c3838be61e8c354e5709178929007056069674a4624b8ffc1b1`.
Both were checked against the frozen game source before progressing any test
ticks. The forwarding sampler was installed after the original loader finished;
it called the complete existing pipeline exactly once with unchanged arguments.

The broader 32-second ON trace artifacts are 11,174,666 / 10,108,128 bytes
uncompressed (DDG/CG). DDG exceeds the 10 MiB recording target. This is a test
record-width limitation, not a waived gameplay check; the following 120-second
sampler collects B candidate details only during 3.0–3.8 s and uses 1 Hz scalars
to avoid repeating the broad trace. The earlier failed over-wide retrieval and
source-proof tool assumptions are preserved as INCOMPLETE attempt receipts.

Evidence: `evidence/paired-cause/SUMMARY.json`, `CAUSE_32_FACTS.json`,
`timeline-cause.csv`, per-product timelines/results/source receipts, and
`evidence/paired-cause-trace/SUMMARY.json`. The sampler copies existing values;
it does not call a producer, NIS calculation, filter, assignment solver, lazy
mass snapshot or local-bank initializer. Actual post-update track streams are
distinct from unsampled raw RF measurements.

## First differences, in measured order

Times below use the after-fixed-tick boundary. Native B events also carry their
own pre-increment tick/measurement epoch, explicitly shown for the first HOLD.

| Stage | DDG first change | CG first change |
|---|---:|---:|
| Actual B near-ambiguity HOLD | native tick 194 / 3.233333 s; observed after tick 195 / 3.25 s | native tick 197 / 3.283333 s; observed after tick 198 / 3.30 s |
| Recorded track-update/KF/NIS stream | tick 195 / 3.25 s | tick 198 / 3.30 s |
| Private SPY RF RNG | tick 213 / 3.55 s | tick 204 / 3.40 s |
| C55 CMS-cue/status | tick 522 / 8.70 s | tick 526 / 8.766667 s |
| SAM count, VLS inventory, mass dirty marker | tick 528 / 8.80 s | tick 528 / 8.80 s |
| Cached mass/CG, GM0, heel and draft | tick 529 / 8.816667 s | tick 529 / 8.816667 s |

There is no recorded global combat RNG difference anywhere in the original
1921-row comparison. Private SPY RNG changes later than the initial HOLD/track
update change. RF draws therefore cannot be identified as the first divergence
in this observed sequence. This does not assert that every raw RF measurement
was independently captured; actual precomputed candidate edges are sampled by
the follow-up described below.

The real B recorder identifies the first route as `OWN_SPY_GLOBAL`, with active
`AMBIGUOUS_ASSOCIATION` holds for plots 0 and 1. The native greedy assignments
would have used tracks 300000005 / 300000001 (DDG) and 300000004 / 300000008 (CG).
These are observed receiver-local track numbers, not truth-based associations.
The first affected native candidate NIS alternatives are recorded by a test-only
pass-through of the already-computed `trackBSelectB` inputs/returns in the
120-second run. The watch never calls an extra solver or NIS function.

## The first physical difference is explained by a real loading history

Both A fixtures release SAM #2 at tick 528 / 8.80 s. ACTIVE B releases it at tick
540 / 9.00 s, with a different assigned local track. The VLS consumption marks
the existing mass ledger dirty at 528. At the next fixed tick, the existing
`damageFloodTickV1` → survival step → `createShipDynamicsV15().attitude()` →
`load()` consumes the updated native weapon ledger.

| Cached value at tick 529 | DDG A → B | CG A → B |
|---|---|---|
| Mass, kg | 9,654,581.633599998 → 9,655,289.633599998 | 9,752,651.2 → 9,753,359.2 |
| Difference | B retains exactly 708 kg | B retains exactly 708 kg |
| Ledger revision | 5 → 4 | 5 → 4 |
| CG Y, m | 0.0008834200131251561 → 0.0007393250026007987 | -0.009476817138070796 → -0.009619817394994202 |
| GM0, m | 1.5241001757668942 → 1.5239327349946112 | 1.7450671101999182 → 1.7449948733356875 |
| Heel, rad | 0.0005878619431665158 → 0.0005878574703120607 | -0.00498638831739386 → -0.0049863947422456355 |

That 708 kg is the existing SM-2 inventory mass, not a new coefficient. All
recorded physical scalars are identical until this loading change. VLS shot
times and target choices then continue to differ, even though the final
inventory, mass, CG, GM0 and global RNG match at 32 s. The attitude integrator
retains the history of those different load timings. Derived flood-door world
heights, attached cold aircraft coordinates, and the finite-attitude
`effectiveGMM = transverse / sin(heel)` consequently differ too. The final
`effectiveGMM` delta is not a change to the actual GM0 coefficient.

| DDG shot | A time, s | B time, s |
|---|---:|---:|
| 1 | 0.016667 | 0.016667 |
| 2 | 8.80 | 9.00 |
| 3 | 9.60 | 9.80 |
| 4 | 10.40 | 10.60 |
| 5 | 11.20 | 11.40 |
| 6 | 12.40 | 12.20 |

| CG shot | A time, s | B time, s |
|---|---:|---:|
| 1 | 0.016667 | 0.016667 |
| 2 | 8.80 | 9.00 |
| 3 | 9.60 | 9.80 |
| 4 | 10.40 | 10.60 |
| 5 | 11.20 | 11.40 |
| 6 | 12.00 | 12.20 |
| 7 | 12.80 | 13.00 |

The established chain is active ambiguity hold → changed local update/scheduler
history → changed target/release schedule → existing ledger/physics response.
There was no separate physical coefficient adjustment. This explains the first
physical mismatch without using a truth-based correction or new tolerance.
It does **not** establish equal battle outcomes: all eight Kh-32 are still alive
at the original 32-second checkpoint, and neither version has an intercept event
there.

## Authorized 120-second follow-up

Four new checks, A/ACTIVE × DDG/CG, extend only the original raid horizon from
1920 to 7200 ticks. They use one continuous native loop, preserve the original
setup and original final export/readout, and compare the 32-second cached
checkpoint against the already-verified original runs. They are new tests, not
revised historical expectations. The sampler reads retained real ASM object
references and existing outcome/damage flags after action; `alive=false` alone
is never labeled a kill. Per-ASM native outcomes, hull HP/water/module damage,
survival, inventory, launch/hit/end events, actual source hashes and critical B
candidate costs are retained. Results are reported separately on completion.

No product fix, expectation approval, main merge or coefficient change has been
made in this causal lane.

## Actual candidate costs at the first HOLD

The follow-up is complete. The test watch forwarded `trackBSelectB` exactly once
and copied its actual precomputed input pairs, native legacy pairs and returned
selected/held sets only during 3.0–3.8 s. It did not call a second solver, RF
producer or NIS function. Runtime association function hashes are in each
120-second source receipt. This is stronger evidence than the HOLD marker alone.

| DDG candidate NIS, native tick 194 | Track 300000001 | Track 300000005 |
|---|---:|---:|
| Plot 0 | 1.3612367832995447 | 1.285267308109795 |
| Plot 1 | 12.24192434020135 | 12.214635483876915 |

The two complete matchings sum to 13.527191648311146 and 13.57587226717646;
their difference is **0.04868061886531372 NIS**. Native legacy pairs were
plot 0→300000005 and plot 1→300000001. B returned `selected=[]`, both plots and
both tracks held, component reason `NEAR_EQUAL_MATCHING_HOLD`.

| CG candidate NIS, native tick 197 | Track 300000004 | Track 300000008 |
|---|---:|---:|
| Plot 0 | 2.573072745081327 | 2.2334880531059516 |
| Plot 1 | 7.146456732744346 | 6.291520024782093 |

The two complete matchings sum to 8.864592769863421 and 9.379944785850297;
their difference is **0.5153520159868759 NIS**. Native legacy pairs were
plot 0→300000004 and plot 1→300000008. B again returned no selected pair and
held both plots/tracks for `NEAR_EQUAL_MATCHING_HOLD`.

All eight recorded candidate edges pass the native gate 64 and the added
position/radial sanity checks. The observed 22.5–100.2 m position innovations
and 5.0–17.4 m/s radial innovations are below their unchanged B policy caps.
Neither independent-sanity rejection nor component-size capping caused these
first holds. Both matching deltas are below the existing B heuristic ΔNIS=1.
That heuristic is an association choice, not a calibrated likelihood.

Raw costs and exact input/returned sets:
`evidence/paired-cause-120/CRITICAL_NATIVE_EDGES.json` and the ACTIVE per-page
JSON gzip. The sums above are simple offline additions of already-computed
native values, not a new NIS model or a re-executed native assignment.

## New 120-second observations and their limit

All four continuous 7200-tick checks completed in **275.490 s**. Each page's
32-second cached physics/navigation/mass/survival, inventory, original RNG fields
and SAM/RAM/ASM counts exactly match its verified 32-second run: **24/24 checks**.
The records are 274,121–357,277 bytes per page, under the 10 MiB budget. Actual
native base and mounted pipeline wrapper source hashes match on all four pages.

| At 120 s | DDG A → B | CG A → B |
|---|---|---|
| HP | 100 → 100 | 100 → 100 |
| Flooding, m³ | 0 → 0 | 0 → 0 |
| Module damage | all 0 → all 0 | all 0 → all 0 |
| Survival state | NORMAL → NORMAL | NORMAL → NORMAL |
| Initial Kh-32, native `alive` | 8/8 → 8/8 | 8/8 → 8/8 |
| Later original-setting spawns | 13 Kh-35U → 13 Kh-35U | 13 Kh-35U → 13 Kh-35U |
| Native intercept / system-hit / ship-hit events | 0 / 0 / 0 → same | 0 / 0 / 0 → same |
| Observed SAM/RAM launches | 17 → 16 | 15 → 19 |
| Loaded VLS cells | 82 → 85 | 110 → 106 |
| CIWS/RAM remaining | 1550 / 11 → same | 1550 / 1550 → same |

The original final after-action readout independently agrees that all 21 ASM
remain alive and has no intercept events. The sampler preserves native
`_wip113Outcome`, `_outcomeRecorded`, retirement cause, subsystem damage and
behavior flags; it does not infer a kill from `alive=false`. The native outcome
label for every observed ASM at this horizon is `STILL_ALIVE`.

**This still does not demonstrate a resolved battle or successful interception
preservation.** No new hull-damage/survival worsening was observed by 120 s, but
the original raid has not produced interception or impact outcomes at that
boundary. The resource differences and the still-open scenario must be reviewed;
they do not authorize an expectation update. No longer battle or altered setup
has been started. The separate 120-second results are new tests, not additions
to the original 420-domain or 42-paired assertion totals.

One diagnostic limitation is explicit: `WEAPON_END` recording requires an
existing native `_deathReason` tag. This run does not claim complete SAM end
classification for missiles removed without such a captured tag. Native
collection counts, original intercept events and per-ASM flags are reported
without converting missing events to successes.

Evidence: `evidence/paired-cause-120/PLAN.json`, `horizon-only.diff`,
`SUMMARY.json`, `OUTCOME_REVIEW.json`, per-page raw results and compact event/
checkpoint captures. The only original fixture-command change is
`raid:1920`→`raid:7200`; all original helper modules, expectations and product
files remain unchanged. Four paired strict FAILs and inherited 419025 remain
unapproved.
