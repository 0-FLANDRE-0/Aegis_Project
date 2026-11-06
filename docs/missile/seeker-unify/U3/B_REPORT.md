# SEEKER_UNIFY_U3 Commit B report

## Status

| State | Result |
|---|---|
| IMPLEMENTED | Frozen observed-track memory is converted into the common CUE_A six-state Singer covariance contract. General tracking uses `max(legacy 250 m floor, 3σ)` with no 4 km cap; route plans remain a separate 4 km prior. |
| TESTED | Corrected contract matrix, two actual general-track MK141 launches, runtime seeker/protection consumers, actual sensor-dropout stale rejection, six representative scenes, scope hashes, and the final broad regression. |
| APPROVED | B correction gate passed. The 225 m raw covariance case becomes 250 m, 4,800 m remains unclipped, and no unexplained difference, truth consumer, or RNG call was introduced. |
| UNRESOLVED | Route-plan uncertainty modelling remains outside U3. |
| RELEASE | Not released. PR #72 remains open and unmerged. |

## Data contract

Observed launch memory owns four items independently:

- position and velocity: `SHIP_EKF_RELEASE_SNAPSHOT`;
- 6x6 covariance: `SHIP_EKF_RELEASE_SNAPSHOT`;
- observation age and release step: `SIM_FIXED_STEP_RELEASE`;
- post-release state: immutable, with `updatesAfterRelease:false`.

The adapter maps `[x,y,z,vx,vy,vz]` into CUE_A's
`[x,y,vx,vy,ax,ay]`. Position/velocity covariance terms are copied; the
already-approved CUE_A Singer process supplies acceleration covariance and
exact-discrete propagation. The old `4,000 m` general-track comparison is not
used as a cap. The pre-U3 native acquisition expression already imposed a
`250 m` lower bound; U3 initially dropped it by mistake. It is now named
`trackBasketFloorM` with provenance
`LEGACY_HARPOON_NATIVE_250M_FLOOR`, not replaced by a new tuning value. The
existing log field `predictionSigmaM` remains 2-sigma, while `searchBasketM`
is `max(250 m, CUE_A 3-sigma major-axis radius)`.

No replacement range constant was created. Feasibility uses only existing
Harpoon seeker range, activation range, gimbal, and runtime scan-pattern
limits. The resulting geometric ceiling in this profile is approximately
14,000 m.

## Route mode

Route programs and coordinate memories carry `cueSource:'ROUTE_PLAN_PRIOR'`
and `observationUpdate:false`. `harpoonCuePacketB` rejects them as sensor
measurements. Their planned search radius remains the existing 4,000 m and the
2D route drawing remains unchanged.

## Measured contract cases

| Prediction horizon | 2-sigma log value | 3-sigma search basket | Result |
|---:|---:|---:|---|
| 0 s | 150.00 m | 250.00 m | feasible; raw 3σ 225 m is raised by the restored legacy floor |
| 30 s | 294.31 m | 441.46 m | feasible |
| 120 s | 3,433.08 m | 5,149.63 m | feasible; demonstrates removal of fixed 4 km cap |
| 300 s | 16,767.14 m | 25,150.71 m | rejected by existing physical search limit |

A separate 4,800 m basket was accepted without being clipped to 4,000 m, while
an 18,000 m basket was rejected by the existing physical limit. Missing
covariance produced the named gate failure without exception or NaN entering
tactical state.

## Actual launch and stale-observation correction evidence

The correction gate creates a real anonymous radar surface track at 8 km,
sets its operator identity through the normal API, and uses the production
`harpoonGateA → harpoonRequestFireA → harpoonReleaseA → harpoonSeekerA`
path. It does not use a route plan.

| Case | Gate basket | Missile handoff | Seeker scan | Protection consumer |
|---|---:|---:|---|---|
| 75 m position σ | 250 m | 250 m | exact dynamic bounds; differs from hypothetical 4,000 m | dynamic 250 m allows the controlled protected contact; 4,000 m fallback blocks it |
| 1,600 m position σ | 4,800 m | 4,800 m | exact dynamic bounds; differs from hypothetical 4,000 m | dynamic 4,800 m blocks the controlled protected contact; 4,000 m fallback allows it |

Both scenes repeated bit-identically. For stale evidence, all three surface
sensors were disabled for 615 fixed ticks. The retained track reached
`sensorAge=10.2667 s` against the existing 10 s limit; the real upper launch
gate returned `SURFACE_TRACK_COAST_EXPIRED` and created no pending release.
The separate route-prior matrix still reports 4,000 m with
`observationUpdate:false`.

## Consumers audited

- `harpoonSeekerA`: scans and acquisition-gates with `searchBasketM`.
- `harpoonGateA` and its preview copies: use the CUE_A handoff result.
- `attackPathGuardH3`: protects friendly/neutral contacts against the same
  dynamic terminal search area.
- after-action journal and H3 plan diagnostics: record 2-sigma, 3-sigma, and
  source separately.
- route UI: continues to draw the 4 km plan prior.

Six representative natural-seeker scenes were bit-identical to Commit A and
were bit-identical on repeat. Both inherited Harpoon core audits passed.

Static normalization of the pre-correction and corrected packed sources shows
that only `HARPOON_CUE_B_SPEC` and `harpoonCueHandoffB` changed. Twenty-six
named flight, RF, gate, seeker, HOJ, save, and selection functions are
byte-identical. No new tuning constant, RF physics change, or save-schema
change was introduced.

## Evidence

- `B_GATE.json`
- `B_SCOPE.json`
- `B_CORRECTION_GATE.json`
- `B_CORRECTION_COMPAT_GATE.json`
- `B_CORRECTION_SCOPE.json`
- `C_CORRECTION_GATE.json`
- `D_CORRECTION_GATE.json`
- `ACTIONS_RUNNER_GATE.json`
- `BUILD_B_ACTIVE.json`
- `changes-B.diff`
- `changes-through-B.diff`
- `harpoon_cue_b.js`
- `run_b_contract.py`
- `run_b_correction.py`
- `verify_b_scope.py`
- `verify_b_correction_scope.py`
- `verify_actions_runner.py`

