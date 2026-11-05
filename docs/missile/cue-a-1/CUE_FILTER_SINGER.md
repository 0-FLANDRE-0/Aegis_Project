# CUE_A-1 Stage 1b — Singer cue filter

Status: **PASS**  
Mode: **MAX_THREAT** (CONFIRMED_ONLY performance remains UNVERIFIED)  
Frozen implementation: `46889420995ddb545e64f02d700eb2bbdd3ba9f4`  
Product SHA-256: `a1c7ad560a47aaea0e82c90639b6db4e0e9b44eabe9289a8f002523270eabaac`

## Gate summary

- PASS — `exactDiscreteSingerAndDtIndependence`
- PASS — `cueMatrixKeysExact240`
- PASS — `cueMatrixPageErrorsZero`
- PASS — `trackRegressionsZero`
- PASS — `shipHitRegressionsZero`
- PASS — `insideSearchOutsideBasketDidNotIncrease`
- PASS — `falseAcquisitionControlIncreaseZero`
- PASS — `falseAcquisitionControlsBitExact`
- PASS — `s1NoTrackRegressionOrWrongFirstAssociation`
- PASS — `egress37NoNeighborFirstAssociation`
- PASS — `determinismExact`
- PASS — `truthAndFunctionScopeAudit`

## Key results

- Exact-discrete Singer prediction used Van Loan + Higham Padé13. Relative dt errors: {'velocitySigma0': 4.0600585702273683e-13, 'velocitySigma9': 3.7566488296390054e-13}.
- Cue matrix: 240 cells; TRACK regressions 0, hit regressions 0, acquisition-state changes 1.
- Forbidden inside-search/outside-basket failures: 0 → 0.
- False-acquisition controls: 180 cases, new false acquisitions 0, byte differences 0.
- S1: TRACK 50 → 50; ownship/neighbor first selection 0/0.
- TRACK-C egress: 16 battles / 37 missiles; first family {'INTENDED_OWNSHIP': 37}; neighbor-first 0.
- Determinism: 6 representative cases, hashes `3f2665f8b9b2b70d85f07db89c5f4349ad05a38d3fca74cc1fa9df0e5f00a242` / `3f2665f8b9b2b70d85f07db89c5f4349ad05a38d3fca74cc1fa9df0e5f00a242`.
- Scope: 3074 other functions byte-identical; protected changes 0; truth/RNG token hits 0.

## Changed acquisition cell

- `{"emcon":false,"label":"Kh-32","rangeKm":60,"seed":729300,"speedKt":15,"threatMode":"MAX_THREAT","turnAtS":16.666666666666668,"turnDeg":0}`: {'acquire': True, 'track': False, 'shipHit': False, 'failureCategory': 'OTHER', 'firstAcquireS': 7.966666666666667, 'basket': {'rangeLowM': 44914.99372358289, 'rangeHighM': 57164.53746637822, 'rangeHalfM': 6124.771871397665, 'azHalfDeg': 5, 'searchSectorAzDeg': 20, 'rangeAgeS': 0, 'source': 'PASSIVE_RF'}} → {'acquire': False, 'track': False, 'shipHit': False, 'failureCategory': 'OTHER', 'firstAcquireS': None, 'basketAtFirstAcquire': None, 'finalBasket': {'rangeLowM': 24135.202724845316, 'rangeHighM': 30717.530740712224, 'rangeHalfM': 3291.164007933454, 'azHalfDeg': 5, 'searchSectorAzDeg': 20, 'rangeAgeS': 49.183333333331824, 'source': 'PASSIVE_RF'}}. Transient ACQUIRE disappeared, but TRACK/hit/failure class did not change. Candidate truth remained in the basket; this is not an inside-search/outside-basket exclusion.

No TRACK or hit outcome changed in that cell. The after-action audit still recorded 932 in-basket dwells and zero inside-search/outside-basket dwells, so no 3σ INS exception was used.

## Limits

- No broad regression was run in Stage 1; the directive reserves it for one final run after Stage 2.
- CONFIRMED_ONLY has no performance claim in this stage.
- Raw truth-bearing geometry appears only in after-action diagnostic evidence.
