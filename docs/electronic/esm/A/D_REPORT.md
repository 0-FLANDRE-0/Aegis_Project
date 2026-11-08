# ESM_A Commit D report

## Status

- IMPLEMENTED: historical-origin bearing display, likelihood/estimate/coast presentation, shared main/PiP presentation copy, and constrained manual Harpoon coordinate cue.
- TESTED: DDG-119 and CG-52 twice each; desktop 1400×900 and mobile landscape 832×384; Commit-B/C limited gates rechecked after the mobile-receiver association correction.
- APPROVED: not yet; intermediate branch checkpoint.
- RELEASE: false.

## Presentation contract

Every retained bearing line starts at the receiver position stored with that measurement. `LIKELIHOOD_REGION` renders each ray or ellipse mode independently and never draws an averaged target point. `GEOLOCATED_ESTIMATE` alone receives a point marker plus its 95% covariance ellipse, age, source count and the actual estimator methods. `COAST` keeps the widening ellipse with a dim/dashed presentation and `LOST` is not drawn.

`esmPresentationCopyA()` is the single detached read-only payload used by the main chart and PiP. It contains only the anonymous receiver origins, measured bearings and estimate DTO; it does not contain an emitter entity/target ID, truth position, faction or identity. The information window explicitly reports `UNKNOWN` and no automatic authority.

## Manual cue contract

`esmManualCueCommandA()` is an operator-only route-plan command, not a track lock or launch command. It is enabled only when all of these conditions hold:

- state is a single-mode `GEOLOCATED_ESTIMATE`;
- estimate age is within the existing Harpoon `maxTrackAgeS`;
- the 95% major axis fits inside the existing `seekerSearchBasketM`;
- a loaded Mk 141/Harpoon installation exists;
- a valid existing Harpoon coordinate route can place its search centre on the estimate;
- the unchanged `harpoonRouteGateE()` ammunition, damage, geometry, range, manual-authority and safety checks pass.

The command appends the derived final INS waypoint through `harpoonRouteAddE()`. The subsequent route remains `ROUTE_PLAN_PRIOR`, while the bounded operator record is separately marked `ESM_ESTIMATED_POINT` or `ESM_ESTIMATED_AREA`. It does not write `tracks`, `selectedLockId`, identity, fire-control quality or automatic engagement authority. DDG-119 therefore fails closed with `MK141_NOT_INSTALLED`; CG-52 may create the manual route and must still use the existing release path.

## Mobile-AOA association correction

The first D fixture exposed a Commit-B defect: two observations from the same moving receiver were rejected solely because their bearings differed by more than the angular-noise gate. The correction preserves the strict RF fingerprint gate, but treats a large same-platform bearing change as geometrically plausible only when the two historical rays intersect forward of both origins and inside the predeclared 500 m–200 km hypothesis range. Otherwise the original angular NIS penalty remains. No truth ID/position, RF coefficient, threshold, RNG or estimator promotion rule changed.

`D_PREDECESSOR_RECHECK.json` confirms Commit-B localizer/end-to-end and Commit-C raw-network matrices still pass twice for both ship profiles; native RF detections, bearings and EW RNG remain exact against merged EMCON_B.

## Gate

`D_GATE.json` is PASS in 57.40 s:

- all four DDG/CG deterministic matrices pass and repeat exactly;
- historical origins are fixed and the main/PiP presentation payload is exact;
- hidden-truth text/fields, observer-track writes, identity changes and automatic authority are zero;
- uncertain, multimodal, stale and over-basket cues fail closed;
- CG's converged estimate produces the expected search centre with sub-micrometre numeric error; DDG has no supported weapon;
- desktop/mobile page and console errors are zero and document overflow is zero.

Product candidate SHA-256: `2221ed06f63ff397f149c6e44a0ede994b5ac549dbf15a43e4c8df5a40ff6858`.
