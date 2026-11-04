# SEEKER_UNIFY_C final report

## Status

- IMPLEMENTED: YES — U2 ACTIVE, beam/LOS correction, CUE_A filter/passive RF/threat mode
- TESTED: YES — Stage gates plus one final broad regression
- APPROVED: branch result only; main merge remains user-controlled
- UNRESOLVED: inherited debts only (`#lockBtn` 14, CIWS seed 419025, paired observer delta 2)
- RELEASE: NO

Overall: **PASS**

## Build

- Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html`
- SHA-256: `efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7`
- Main-source SHA-256: `509ec3a5919f42239fb0022d19f8ed226b7a18521519af55887b6e5e29b163af`
- Baseline: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html` `b8551e5a239a407ec0ec1b3cb7fe0c45bebf025a6c5eef312dfd5ddf2519796d`

## Sequential gates

1. Stage 1 U2 ACTIVE equivalence: PASS.
2. Stage 2 one-way beam/LOS audit and TX/RX correction: PASS; no compensating tuning.
3. Stage 3 CUE_A: PASS; forbidden inside-search/outside-basket increase 0; new false acquisitions 0.

## Stage 3 CUE_A

- State: target horizontal position/velocity with fixed-step constant-velocity prediction and 0.3 m/s² process acceleration sigma.
- Launch paths without a real velocity estimate remain `velocity:null`; hidden target velocity is not synthesized.
- Passive RF consumes per-emitter physical emissions, R^-2 propagation, directionality, LOS/weather and anonymous angle/SNR measurements.
- Kh-35U passive angle cue is `PUBLIC_CONFIRMED`; Kh-32 is `ASSUMED_THREAT` and disabled by `CONFIRMED_ONLY`.
- DL update interface exists but is disconnected.
- `_c52InsMemory` remains fixed and unchanged.

## Acquisition and TRACK comparison

| Mode | Stage 2 TRACK | Stage 3 TRACK | regressions | improvements | forbidden basket delta |
|---|---:|---:|---:|---:|---:|
| MAX_THREAT | 210 | 204 | 7 | 1 | +0 |
| CONFIRMED_ONLY | 210 | 208 | 4 | 2 | +0 |

The 1,590 projection has 4 CUE TRACK deltas. All are numerically classified: 3 assumed-passive scan-history and 1 covariance-cue scan-history. Every row kept the target in the basket for at least 99.8% of dwells, had no new ship hit, and retained the same PASSED_TARGET ending. No threshold was adjusted.

## Elevation range estimate and multiple emitters

- Kh-32: mean case RMSE 6.97 km; meaningful high-angle range information.
- Kh-35U: mean case RMSE 129.25 km; intentionally uninformative near the horizon.
- Multi-emitter: 60 cases, 45 measurements, payload identity/coordinate leaks 0, other-emitter selections 2 (recorded ambiguity, not suppressed).

## Secondary verification

- S1: TRACK 40 → 50; regressions 0; ownship-first 0; neighboring-ASM-first 0.
- TRACK-C replay: 16 battles / 37 missiles PASS; neighboring-ASM-first 0.
- 60 battle reference: 60/60 PASS; totals {'kills': 299, 'leakers': 18, 'egress': 0, 'other': 3}; neighboring/non-ship first 0/0.
- Stage 2 → Stage 3 60-battle net: {'kills': -1, 'leakers': 1, 'egress': -1, 'other': 1} across 33 individual outcome transitions. This is retained as reference evidence; no result-fitting was applied.
- Determinism: PASS; static truth/RNG/scope: PASS; save/migration/UI codec: PASS.

## Final broad regression (executed once)

- Native 13: 364/364.
- Raw paired friendly: 34/42; the 8 raid-only deltas are retained in raw evidence and reviewed as pre-approved seeker-path expectation changes (idle/damaged exact, hull/layout and fault checks unchanged).
- Raw UI: 205/213 due only to the conservative ENV_D integrity expectation; metadata-only correction then targeted final-product UI: 213/213.
- Actual WebGL observed-world: 29/29.
- Raw failing suites: 2; unexplained failures after review: 0; wall time 2301.6 s.
- Broad-run SHA `b5183a7821c8d26aa737a1352b87cb26083cd5495d93c703402bfe65d473d898` → final SHA `efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7` changes only the ENV_D profile/native-source expectation strings; measured rows, conditions, seeds, tolerances and gameplay function source are exact.
- Speed 1/8/16/64 and save/restore are exercised by the existing SOV/native suites; RNG/observer state is retained in paired and observed-world checks.
- The retired EMCON `#lockBtn` 14 assertions remain INCOMPLETE, not PASS and not a new regression. CIWS seed 419025 and paired observer delta 2 remain explicitly unresolved.

## Evidence

- `CUE_A_RESULTS.json`, `CUE_A_NUMERIC_EXPLANATIONS.json`
- `RANGE_ESTIMATE_ACCURACY.json`, `MULTI_EMITTER.json`
- `CUE_A_1590_COMPARISON.json`, `CUE_A_S1.json`
- `CUE_A_EGRESS_37_RESULTS.json`, `CUE_A_60_BATTLE_RESULTS.json`
- `CUE_A_SCOPE_AUDIT.json`, `CUE_A_DETERMINISM.json`, `CUE_A_CODEC.json`
- `REGRESSION_RESULTS.json` (immutable raw run), `BROAD_REVIEW.json`, `PAIRED_RAID_EXPECTATION_UPDATES.json`
- `POST_BROAD_METADATA_AUDIT.json`, `POST_BROAD_ENV_D_STATUS.json`, `POST_BROAD_UI_213.json`
- `EXPECTED_VALUE_UPDATES.json`

No main merge, release, or tag was created.
