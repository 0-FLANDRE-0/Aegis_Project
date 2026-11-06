# SEEKER_UNIFY_U3 Commit B report

## Status

| State | Result |
|---|---|
| IMPLEMENTED | Frozen observed-track memory is converted into the common CUE_A six-state Singer covariance contract. General tracking uses its 3-sigma basket; route plans remain a separate 4 km prior. |
| TESTED | Contract matrix, missing/old/large covariance branches, six natural seeker scenes repeated twice, A/B scene comparison, core audits, and 14 unchanged-function hashes. |
| APPROVED | B gate passed. No unexplained difference, exception, truth consumer, or RNG call was introduced. |
| UNRESOLVED | Route-plan uncertainty modelling remains outside U3. C-D and final broad regression remain pending. |
| RELEASE | Not released. Branch checkpoint only. |

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
used. The existing log field `predictionSigmaM` remains 2-sigma, while
`searchBasketM` is the CUE_A 3-sigma major-axis radius.

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
| 0 s | 150.00 m | 225.00 m | feasible |
| 30 s | 294.31 m | 441.46 m | feasible |
| 120 s | 3,433.08 m | 5,149.63 m | feasible; demonstrates removal of fixed 4 km cap |
| 300 s | 16,767.14 m | 25,150.71 m | rejected by existing physical search limit |

A separate 4,800 m basket was accepted, while an 18,000 m basket was rejected.
Missing covariance produced the named gate failure without exception or NaN
entering tactical state.

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

## Evidence

- `B_GATE.json`
- `B_SCOPE.json`
- `BUILD_B_ACTIVE.json`
- `changes-B.diff`
- `changes-through-B.diff`
- `harpoon_cue_b.js`
- `run_b_contract.py`
- `verify_b_scope.py`

