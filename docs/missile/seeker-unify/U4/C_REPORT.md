# SEEKER_UNIFY_U4 Commit C — common association/state ACTIVE

## State

- **IMPLEMENTED:** anonymous common association selector and common state execution engine for ASM, Harpoon, SARH, ARH and RAM.
- **TESTED:** Commit-B baseline vs C SHADOW vs C ACTIVE, fresh-page ACTIVE repeat, representative real flights, lifecycle/save boundary and synthetic transition matrix.
- **APPROVED:** no new tuning or behavior delta; ACTIVE tactical outputs are exact to Commit B for the limited gate.
- **UNRESOLVED:** the project-wide `MAX_THREAT` regression and observed-world/UI coverage are intentionally deferred to the one final run after the product candidate is frozen.
- **RELEASE:** no.

## Migration boundary

`association_state_c.js` owns the common dispatch, anonymous score selection,
transition event vocabulary and state-step implementations.  It receives only
numeric candidate scores or the missile's own local track state.  It does not
receive entity/profile/faction/hostile identifiers or physical truth positions,
and it consumes no RNG.

| Family | Association owner after C | State owner after C | Preserved hook |
|---|---|---|---|
| ASM | common stable max-score selection; ASM builds NIS/absolute-gated candidates | common dispatcher invokes the specialized ASM acquisition/HOJ policy | HOJ / RF EKF / INS and strong-evidence acquisition |
| Harpoon | common stable min-score selection; Harpoon builds route/memory-gated candidates | common dispatcher invokes the Harpoon local state policy | route-plan prior / INS memory / RF track |
| SARH | common stable max-score selection | common RF transition step | illumination and both bistatic LOS/beam paths |
| ARH | common stable max-score selection | common RF transition step | SARH↔ARH source arbiter |
| RAM | common anonymous angular gate | common angular transition step | MEM/RF/IR authority and guidance |

The weapon front ends still own prediction, covariance, NIS and absolute gates,
measurement generation and their existing local RNG handles.  Guidance laws,
release authority, HOJ, route execution and source arbitration were not changed.
There is no cross-weapon mutable tactical singleton.  The only module-global
mutable object is read-only diagnostic counting; it is never read by tactical
code.

No save field or schema was added.  The existing weapon owners continue to
initialize, reset, save/load where already supported, destroy and retire their
local state.

## Limited SHADOW → ACTIVE gate

Evidence: `C_GATE.json`, `BUILD_C_SHADOW.json`, `BUILD_C_ACTIVE.json`.

- Status: **PASS** in 68.94 s; broad regression executed: **no**.
- C SHADOW tactical result vs Commit-B ACTIVE: exact.
- C ACTIVE tactical result vs Commit-B ACTIVE: exact.
- C ACTIVE fresh-page same-seed repeat: exact.
- SHADOW association comparisons: 5,002; mismatches: 0.
- SHADOW state comparisons: 1,648; mismatches: 0.
- Common-layer RNG calls: 0; truth/ID decision fields: 0; page/core errors: 0.
- Operational save validates and contains no U4 state/save schema.
- All event classes were exercised: valid measurement, hit accumulation,
  coast, reacquire, signal/illumination loss, timeout/lost/off and retire.

Representative outcomes were unchanged on all three products:

- ASM Kh-35U: acquired and reached TRACK during the 20 s case.
- Harpoon: all 10 seeker state checks plus core/launcher selection audits passed.
- SARH SM-2: 24.05 s, proximity kill.
- ARH ESSM Block 2: 13.15 s, proximity kill/intercept.
- RAM: the selected inherited seed leaked and hit the ship at 20.8 s on the
  Commit-B baseline, C SHADOW and C ACTIVE identically.  It is not hidden or
  reclassified as a pass; it proves no C regression and remains broad-regression
  evidence rather than a tuning target.

## Protected contracts

Build receipts prove unchanged hashes for allocation/source arbitration,
SARH reflector/receiver/illuminator physics, missile-body guidance integration,
surface release gate, RAM authority/guidance, ASM HOJ and Harpoon route stepping.
The static contract audit also confirms no common decision function references
entity ID, target ID, profile ID, faction, hostile state or truth references.

The next allowed operation is to commit and push this C checkpoint, freeze the
single final ACTIVE product, then execute the project-wide broad regression
exactly once.
