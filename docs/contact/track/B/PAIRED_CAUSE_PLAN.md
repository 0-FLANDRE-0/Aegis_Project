# TRACK-B strict paired raid divergence: causal test plan

Status: **the four strict failures remain FAIL and unapproved**. No product fix,
expected value update, tolerance change, or outcome approval is part of this lane.
The dry-run artifacts are `evidence/paired-cause/PLAN.json` and
`ARCHIVED_FACTS.json`. A planned experiment is not evidence of its result.

## Facts before hypotheses

The source is the actual, archived B paired comparison:
`evidence/regression/paired-track-a/baseline-comparison.json`. Its SHA and build
SHAs are recorded in `ARCHIVED_FACTS.json`. The existing full-field companion is
`evidence/regression/paired-state-deltas.json.gz`.

| Field at the original 32 s boundary | DDG TRACK-A → ACTIVE B | CG TRACK-A → ACTIVE B |
|---|---|---|
| Fixed ticks / frames / time scale | 1920 / 240 / 8, equal | 1920 / 240 / 8, equal |
| Global combat RNG | 2134102897 → same | 2134102897 → same |
| Hull HP / water / module damage / fixed layout | equal, HP 100 | equal, HP 100 |
| Complete final weapon inventory | exact | exact |
| Loaded VLS cells | 90 → 90 | 115 → 115 |
| Final mass and loaded mass, kg | 9651749.633599998 → same | 9749111.2 → same |
| Final mass ledger revision | 9 → 9 | 10 → 10 |
| Final CG vector | exact | exact |
| Actual loading-condition GM0, m | 1.5254404550547696 → same | 1.7460114333199073 → same |
| Heel, rad | 0.0005609569352033292 → 0.0005623081835051285 | -0.005414938108612049 → -0.00541628573375259 |
| `effectiveGMM`, m | 0.0257140455245001 → 0.029480081087069277 | -0.016382652564924736 → -0.015939393388095333 |
| Kh-32 after-action outcomes at this boundary | all 8 still alive, no intercept events, equal | all 8 still alive, no intercept events, equal |
| Original strict checks that failed | physical state; existing observer state | physical state; existing observer state |

`effectiveGMM` is the finite-attitude diagnostic `transverse / sin(heel)`, with a
GM0 fallback near zero heel. The delta in that field is **not a demonstrated
change to GM0, mass, CG, or a stability coefficient**. The source computes it in
`createShipDynamicsV15().attitude()`. Tiny heel differences also change the
derived world heights of flood doors, surface normals, and attached cold aircraft.
Those final-value dependences explain why many fields differ, not why the first
heel difference arose.

The observer output differs substantially: original anonymous plot, scheduler,
track-state and private-RF results differ. Final global RNG equality does not
prove that intermediate global or private streams, sensor work, launches, or load
history were identical. Nor does final inventory equality establish launch-time
equality. The first divergent tick is absent from the archived final snapshots.

Hypothesis to test, **not established**: association differences alter tracking,
engagement scheduling, VLS release timing and therefore loading moments before
the same final inventory is reached. The opposite ordering, an earlier native
physical/RF divergence, must also be checked. No claim of a sole cause is allowed
until the first differing stages have been located.

## Exact fixture and frozen builds

The runner extracts the original `scenario=>{...}` JS literal from
`docs/multiship/H4/regression_baseline.py` by Python AST. The only literal
replacement is the **existing** HELI-F observer/offboard readout insertion from
`docs/helicopter/F/verify_regression.py`. Original commands and final snapshots
are retained. The existing `sitecustomize.py` after-action readout remains in
place when launched under the same environment.

Use original `docs/bunkerhill/K/browser_i.py:load`, not the newer `load_fast_http`
deployment adapter. The loader's default seed is `0x6d2b79f5` (1831565813), viewport
1000×760, view3d=0, actual ship-select/confirm/depart, then the same existing pause
API. Do not explicitly change deployment selections, startup gun settings, RAF,
navigation, or RNG to resemble a different harness.

The actual original raid is unchanged: terrain bypass; spawn 8 real Kh-32 at
16 km and bearings [-60,-20,20,60]; mode AUTO; profiler enable/reset;
`runFramesToTicks(60,8,1920)` once; original operational/physics/observer/offboard
snapshots and original RNG readout. No fake missile model or reduced simulation.

Frozen products:

| Product | HTML SHA-256 |
|---|---|
| TRACK-A | `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a` |
| B SHADOW | `e9af30d8d71209f9eb45d72de58ca509efd261d7126d89ab626e2873d182995d` |
| B ACTIVE | `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6` |

All six original helper/fixture/controller hashes and original/executed JS literal
hashes are written to PLAN.json. A changed product is rejected before/after use.

## Passive instrumentation and its limitations

Only the in-memory served TEST copy is instrumented. Product files remain intact.
Three uniquely anchored additions expose numeric/scalar values from already-computed
closure data: mass/CG/revision and dirty metadata; ship dynamics mass, GM, buoyancy,
rates and hydro/reference ages; survival pose/state. No cache/geometry/profile,
complete diagnostic object or mass-node array is copied. They do not rebuild, recalculate,
snapshot, initialize, advance time, draw RNG, or alter any native field. The test
then copies whitelisted/plain data fields. The helper skips property getters.

After the original loader has fully initialized and paused, `start()` installs a
one-time wrapper forwarding `this`, arguments and return value to the complete
original fixed-tick pipeline exactly once. It captures only after that pipeline
returns. The preexisting MAP_D.mount wrapper installs later at runtime than its
source position suggests; this actual mounted wrapper and the underlying base
function each have a pinned source hash. A test-only reference retains the base
function before existing wrappers install, without ever invoking it separately.
Both runtime `toString()` hashes must match before any trial ticks progress.
The base body bytes are also compared before/after instrumentation. No native
function is called for an extra measurement, NIS,
association, physics update, mass rebuild, bank initialization, or damage event.
There is one initial cache record before the fixture, then exactly 1920 tick
records. Final original snapshots are called only where the original fixture did.

Recorded categories: global/private RF/observer/C55/weapon RNG; tracks' existing
kf6/NIS/measurement step only when native update metadata changes; C55 file counts
and existing RNG/winner/status scalars; actual SAM/RAM counts and new IDs once at
launch; VLS ammunition counts by section/type; cached mass/CG/revision;
navigation; cached heel/draft/GM. The original final after-action readout preserves
the hostile outcomes. Any truth content is explicitly
`AFTER_ACTION_TRUTH_TEST_ONLY`, never fed to simulation or sensor consumers.

B association traces are read from existing records only **if enabled**. No NIS
or producer is recomputed by this helper. Primary controls leave diagnostics OFF.
An optional `--trace-b` repeat enables only the existing diagnostic recorder and
reads its bounded records after each tick; original native final state/RNG must
match the OFF run/archived actual build. Trace overflow is reported, never filled
with invented edges. C55 remains live-legacy with shadow-only diagnostics.

The track timeline contains actual post-update estimates and freshness, **not a
claim to have sampled every RF measurement before association**. The first track
delta is a bound on the first observed difference. Enabled native B traces can
locate the actual association decisions that precede it. More invasive producer
instrumentation would need separate review if this evidence is insufficient.

The original archived final physical/observer/offboard/RNG fields are compared to
the instrumented A and ACTIVE runs. A mismatch means passivity/exact-fixture
equivalence is not established and the causal conclusion remains unresolved.
SHADOW should match TRACK-A in every native timeline category, although B-only
diagnostic metadata is deliberately not compared as native gameplay state.

## Execution, concurrency and outputs

`paired_cause.py` defaults to a dry run with no Playwright/browser startup. A run
takes the same shared `heavy_browser_slot()` flock as all B runners, one browser
at a time and no manually inherited lease. Wait for root's GO before `--run`.
The six pages are DDG/CG × A/SHADOW/ACTIVE. Use `--only` only to resume a lane;
the partial output must not be described as the full six-page comparison.

Run with the same existing regression environment (paths shown for this workspace):

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 \
B2_PHASE1_REGRESSION=1 B2_MODE=ON B2_ALLOW_AUTO=0 \
B2_HTML=Aegis_SIM_v48_WIP_TRACK_B.html \
B2_OUT=/dev/shm/aegis-ciws-dmg-a/docs/contact/track/B/evidence/paired-cause \
PYTHONPATH=/dev/shm/aegis-ciws-dmg-a/docs/gun/B2/phase1b/test_support \
python docs/contact/track/B/paired_cause.py --run \
  --candidate-sha 0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6 \
  --shadow-sha e9af30d8d71209f9eb45d72de58ca509efd261d7126d89ab626e2873d182995d
```

Each page writes a compact tick timeline gzip and the original final result JSON.
Records are retrieved in 120-row JSON-string chunks, not one large nested
Playwright payload. The target is at most 10 MB uncompressed per page.
SUMMARY.json reports actual invoked-source proof, cached initial/end rows,
original archived final-field equality, first differing tick per category, and
actual new-SAM/RAM records with same-tick mass/loading context. These are temporal
facts; assigning causality requires inspecting their order and source paths.
No expectation is updated, and the strict paired failures stay unapproved even
if their causal chain is identified.

The first attempt completed the original A/DDG raid expression, then crashed the
renderer while retrieving an over-wide whole timeline. It is **INCOMPLETE**, not
an outcome. `ATTEMPT_1_FAILURE.json` and the actual first helper are preserved.
The retry changes test record width/retrieval only; no product behavior or
original fixture command is changed.

The next source-proof attempts exposed test-tool assumptions about the existing
wrapper chain, not changes to the original base function. Their receipts remain
INCOMPLETE. The corrected runtime ordering/source proof and complete measured
results, including the authorized 120-second follow-up, are in
`PAIRED_CAUSE_RESULTS.md`. No source-proof mismatch was waived as a game pass.
