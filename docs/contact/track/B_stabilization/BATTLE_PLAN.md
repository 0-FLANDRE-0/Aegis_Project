# Stabilization battle fixtures: plan before measurement

Status: **19 pages captured; main15 complete, natural13 regression under diagnosis**. Existing paired strict
differences, seed 419025 and other inherited failures stay unapproved. This lane
does not alter a product function, coefficient, expectation or tolerance.

## Why a new fixture is needed

The unchanged H4 paired raid starts Kh-32 in their full high-altitude launch
sequence. At both 32 and 120 seconds the original after-action output had all
initial eight ASM alive, no intercept/impact event, and additional background
spawns. Those checkpoints can show causal state changes but do not establish
preserved defensive battle outcomes.

The starting point here is the existing natural D1 setup in
`docs/gun/B1/test-fixture.js:scenario`: native Kh-35U creation at 11 km / 10 m,
280 m/s, with a fresh seeded ship and no seeded CMS file. D1 is normally MANUAL
with gun AutoAA OFF. This **new** battle explicitly uses the existing overall
AUTO command and preserves the fresh product's other gun/EW/AI settings. It is
therefore not a repeat or replacement of the D1 30-seed regression.

## Frozen scenario candidates

A single-target sanity pilot precedes the limited two-battle matrix:

| ID | Own ship | Seed | Native initial ASM placement |
|---|---|---:|---|
| PILOT_SINGLE | DDG-119 | 419021 | 1 Kh-35U, bearing 90°, 11 km, altitude 10 m, inbound 280 m/s |
| DDG_CONVERGING_2 | DDG-119 | 419022 | 2 Kh-35U, bearings 87°/93°, ranges 11.0/11.3 km, altitude 10 m, inbound 280 m/s |
| CG_MULTIPLE_3 | CG-52 | 419024 | 3 Kh-35U, bearings 84°/90°/96°, ranges 11.0/11.3/11.6 km, altitude 10 m, inbound 280 m/s |

The converging paths are intended to exercise close/crossing observed bearings.
Whether actual reported trajectories cross or become spatially ambiguous is
measured after the pilot; a merely converging case will not be mislabeled a
proven crossing. If it does not exercise a crossing, normal initial positions
and headings can be revised before freezing the matrix, with the change and
new pilot recorded. No dynamics or detection coefficient is adjusted.

Normal scenario preparation: fresh native ship-select/depart with no ally,
enemy ship, target ship or background aircraft; existing deterministic reset;
stationary ship heading 0; terrain bypass **false**; EMCON off through the
existing command; AUTO through `wip119SetMode`. Existing profile inventory,
module health, sensors, IFF, ROE, EW, PN/Kappa, flight, fuze/Pk and AI remain
intact. No ammo is removed, no emitter/illuminator/damage function is replaced,
and no threat is manually classified HOSTILE to make AUTO fire.

The only physical threat creation is normal `spawnEnemyMissile` using the same
initial data structure as D1. Do not call `_wip75SyncTrack`, `trackIdForTruth`, a
track fixture/identity override, ideal observation injection, or direct fire.
Native sensor/RF → measurement → local association → classification/authority
→ AUTO → normal VLS/CIWS/RAM → native terminal/damage code runs continuously
inside the complete existing fixed-tick pipeline.

## Pilot qualification and stop conditions

Start with TRACK-A only, then existing B SHADOW/ACTIVE only if the case qualifies.
The product candidate is not run until root freezes it.

A qualifying battle must demonstrate actual local sensor reports from zero
initial tracks, AUTO weapon release without a test fire command, and a native
terminal result for every initially spawned ASM. A ship hit or native miss is
a legitimate outcome; `alive=false` or disappearance alone is never a kill.

The maximum pilot horizon is 90 s. Termination is explicit:

1. All initial threats have a native terminal state, then continue the original
   simulation for 5 s of aftermath and report any remaining defensive weapons.
2. An irreversible native own-ship loss ends the defensive battle; surviving
   threats are reported as such, not kills.
3. Horizon reached with unresolved threats or no sensor/AUTO/terminal chain:
   `INCOMPLETE_NOT_DECISIVE`, never PASS. Do not turn off a weapon or change a
   coefficient to force a qualifying result.

## Evidence and information boundary

Events copy actual producer/association results using pass-through calls only:
original function exactly once, unchanged `this`/arguments/return. No extra RF,
NIS, filter or solver calculation. Per tick retain small primitives/counters;
keep detailed events only on change and numeric ship/track summaries at 1 Hz.
Record actual base/pipeline/association/flight function source hashes, product
SHA, fixture seed/setup hash, fixed ticks and event counts. Max two cooperating
heavy browsers overall; this lane acquires only one shared flock lease.

Outputs distinguish:

- **Observed product evidence**: measurement dimensions/timestamps/source;
  receiver-local IDs, filter state/age/NIS; chosen/held/unassigned decisions and
  HOLD intervals; detection, first AUTO release, native weapon end and battle
  termination timelines; real inventory and hull/flood/module/survival changes.
- **AFTER_ACTION_TRUTH_TEST_ONLY**: initial physical object references and final
  native death/retirement/damage flags. Nearest-truth distances, ID continuity,
  possible swaps/duplicates are evaluated after simulation and never supplied
  to association, identification, firing or AI. One closest truth is not enough
  to prove a swap in an ambiguous crossing: retain distances/margins and mark
  ambiguous evaluation separately.

Primitive counts remain visible: initial ASM count, detected local files,
confirmed files, peak files, native launches by type, effects/terminal causes,
remaining threats, own hits, ammunition use, sampler/native trace errors and
dropped diagnostic records. No result is discarded because it is a failure.

## Cost and execution order

Before pilot: estimate 2–4 pilot pages, roughly 2–5 minutes. Then measure actual
cost and freeze qualifying setups. Two battles × five versions (TRACK-A,
existing B SHADOW/ACTIVE, stabilization SHADOW/ACTIVE) give 10 pages, provisionally
5–12 minutes. A failed pilot is retained and the estimate revised. Only A/existing
B run before the stabilization candidate is frozen. No full ENV remeasurement.

First artifacts: `battle.py`, `battle.js`, `evidence/battle-pilot/`. Final matrix
will use the same executable fixture and setup hashes across all versions.

## Final freeze and expanded coverage

The single-target pilot qualified. The final main matrix has the two rows above
plus `DDG_BEARING_CROSSING_2`: DDG, seed419022, two native Kh-35U at
89.9°/90.1°, 11.0/11.16km, and initial inbound headings offset −5°/+5°.
Native truth bearing order reverses between0.9 and1.0s, and reported local-file
bearing order reverses between0.8 and0.9s. These are separate observations;
neither establishes a physical collision or an identity swap. Early wider
`DDG_CROSSING_2` did not reproduce crossing and remains a labeled pilot only.
The narrow placement was frozen before its five-version final matrix. The
crossing case samples after-action geometry at10Hz for its first5s, then1Hz.

The final19 requested pages are three main cases ×five versions, plus
`NATURAL_SATURATION_13` ×four versions (A, oldACTIVE, newSHADOW, newACTIVE).
The latter uses seed419027, thirteen Kh-35U at bearing90°, altitude10m,
280m/s and ranges10.8+i×0.08km. The normal RF/measurement pipeline decides
whether an association component actually exceeds12. No RF, geometry gate,
target dynamics or solver parameter is changed to force that result.

Final candidate SHA pins are ACTIVE
`87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18`
and SHADOW
`75b845f5b353c576ea191a2508578edcb29b4110a69cbf97e532df6562747d4f`.
The sampler is `battle.js` SHA
`bbecae524297ecb0f0c32969ad6079f4834dca4547fbcf402e551c5c81a0070b`.
Every page records actual fixed-tick pipeline, SAM/ASM flight, Pk/applyPk,
spawn/reset and association source hashes before pass-through installation.

Actual selected pairs and held sets are read from the same native selector
return. NewSHADOW consumes oldACTIVE behavior, while its module trace describes
the new proposal. OldSHADOW consumes A behavior and its components describe a
proposal. These meanings are recorded separately. No proposalHOLD is reported
as applied HOLD. Duration means time from an applied held-track return to the
next accepted native update on that receiver-local file, across routes.

The final15 main pages have native terminal outcomes for all initial threats,
HP100, no ship hits/flooding and no appliedHOLD. They guard ordinary/crossing
AUTO battles; they do not establish all HOLD-defense safety. The separate
inherited D1seed419012 reference is overallMANUAL with native autonomous RAM,
and is not folded into this denominator. See `BATTLE_RESULTS.json` and `.md`
for authoritative completeness, counters, latencies and unresolved limits.

## Transport-only tooling repair

The first oldACTIVE saturation attempt completed its simulation but exceeded
the10MiB capture budget at13,747,415 serialized bytes before persistence.
Its result object was lost; the execution-error receipt is retained under
`evidence/battle-errors/1793558387765145030.json`. This is a toolingINCOMPLETE,
not a gameFAIL or gamePASS. A valid A saturation capture is retained/reused.

The rerun preserves `battle.js`, products, setups, stop conditions and every
record/field. Only final transport losslessly encodes repetitive association
and observed-lineage dictionaries into ordered columnar arrays. Missing fields
remain distinct from null. Before export the browser decodes the entire result
and asserts exact `JSON.stringify` equality, including key order, and records
the original/decoded SHA256. Node-only replay of16 existing captures confirms
the same deep/serialized equality without native calls; receipts are in
`evidence/battle-final/TRANSPORT_ROUNDTRIP.json`. Analysis restores original
objects before all comparisons. Capture data must still fit10MiB.

The main15 batch took740.219s wall time including its shared-lease wait;
individual completed main-page loops took roughly10–20s. The A saturation
loop took64.952s and reached the unchanged90s horizon with HP0 and one initial
ASM still alive. Its lifecycle qualification remains INCOMPLETE; the criterion
is not weakened after seeing the result. The three remaining saturation pages were replayed with only this lossless
transport change (259.248s wall for the three-page batch). All19 raw pages are
now present. Four saturation pages remain lifecycleINCOMPLETE. NewACTIVE has
three unresolved initial ASM versus oldACTIVE one, and different module damage;
these are unapproved worsening indicators. NewACTIVE has fewer damaging hits
(3 versus5); a fourth native shipHitHistory record is a zero-damage miss, kept
separate. Source-level cause and independent feature ablations continue under
`BATTLE_CAUSE_PLAN.md`. No result is approved from the15 ordinary battle passes.
