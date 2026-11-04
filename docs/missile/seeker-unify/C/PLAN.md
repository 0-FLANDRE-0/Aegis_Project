# SEEKER_UNIFY_C execution plan

## Pinned baseline

- Repository commit: `052846b10199e0b198be574d339b552bd7484658`
- Baseline product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html`
- Baseline SHA-256: `b8551e5a239a407ec0ec1b3cb7fe0c45bebf025a6c5eef312dfd5ddf2519796d`
- Working branch: `seeker-unify-c`

## Sequential gates

1. U2 ACTIVE legacy-equivalence extraction. No tactical behavior change is permitted.
2. ASM beam/LOS definition audit, followed by the directive-mandated physical correction only if the audit establishes one-way or unclear semantics.
3. CUE_A observed-information filter, passive RF measurement path, elevation range diagnostic, disconnected data-link hook, and threat-mode policy.

The broad regression is run exactly once, after the final completed stage (or at the stopping point). Stage work uses only the changed-function hash audit and the stage-specific matrices.

## Frozen Stage 1 profile contract

The values in `U2_FROZEN_PROFILE_OPTIONS.json` are provenance `LEGACY_EQUIVALENCE`: they describe the existing implementation and are not hardware claims or new tuning constants.

- ASM WIP22: `COMBINED_SINGLE`, `POWER_WEIGHTED_RMS`, `AXIS_SEPARATE_COMPOSITE`.
- SAM ARH: `TX_RX_SEPARATE`, `MAX_MEMBER`, `SPHERICAL_MEMBER_PRESERVING`.

No Stage 2 or Stage 3 constant is introduced or adjusted during the Stage 1 equivalence gate.

## Stage 2 checkpoint

- Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html`
- Product SHA-256: `dca6d886b9980b87d3c776e85ae4ff8839eb42128669cbc150b212e0dcaf18ec`
- Main-script SHA-256: `53799ce92aebd732581661c682ccec903eda36b521a0c9452f1ec6a3c9ae06a8`
- Gate: `PASS` (`BEAM_FIX_RESULTS.json`)
- Physical decision: legacy ASM active-seeker beam/LOS semantics were undocumented or unclear, so the existing values are frozen as one-way `SIM_TUNED` values and applied with `TX_RX_SEPARATE` as required by the directive.
- No beamwidth, sensitivity, RCS, threshold, search-sector, cue-basket, HOJ, or passive-RF tuning was made.
- 1,590 matrix page errors 0; new false acquisitions 0; SAM and ship-radar exact differences 0.
- Six target and thirty full-cue TRACK regressions are all captured by numeric evidence. Unexplained failures: 0.
- S1 100 cases: TRACK 40 → 40, ownship-first 0, neighboring-ASM-first 0.
- TRACK-C replay: 16 battles / 37 missiles `PASS`, neighboring-ASM-first 0.
- Reference battles: 60/60 `PASS`, first associations 320/320 intended ship, neighboring/non-ship 0/0. Totals 301/17/1/1 → 300/17/1/2; leakers and egress unchanged, one net intercept kill became `GUIDANCE_CONTROL_LOSS_MISS`.
- Broad regression remains intentionally deferred until Stage 3 completes or reaches a stopping gate.

## Stage 3 final checkpoint

- Implementation and evidence commit: `2caf7c4e6e51f4b85b97d8eeb1ed5383c8d452de`
- Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html`
- Product SHA-256: `efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7`
- Main-script SHA-256: `509ec3a5919f42239fb0022d19f8ed226b7a18521519af55887b6e5e29b163af`
- Final gate: `PASS` (20/20 gates in `CUE_A_FINAL_RESULTS.json`).
- CUE_A implements the four-state fixed-tick constant-velocity filter, process covariance, anonymous passive-RF updates, provenance/assumption modes, an explicitly disconnected data-link hook, and unresolved-launch velocity handling without truth identifiers or game RNG.
- CUE matrix: 480 Stage-3 cases; forbidden inside-search/outside-basket failures did not increase.
- Combined matrix: 1,590 cases, page errors 0, new false acquisitions 0, target TRACK regressions 0, SAM exact differences 0, ship-radar exact differences 0. Four CUE TRACK deltas all have numeric scan-history explanations.
- S1: Stage 2 TRACK 40 to Stage 3 TRACK 50, wrong first associations 0. TRACK-C replay: 16 jobs / 37 missiles PASS, wrong first associations 0.
- Reference combat: 60/60 completed. Stage 3 totals were 299 kills, 18 leakers, 0 egress, and 3 other outcomes; no neighboring-ASM/non-ship first association was introduced. These results are evidence, not tuning targets.
- Broad regression was executed exactly once on the completed Stage-3 behavior. Raw results are retained in `REGRESSION_RESULTS.json`; the eight paired-raid differences are documented as seeker-path expectation changes in `BROAD_REVIEW.json` and `PAIRED_RAID_EXPECTATION_UPDATES.json`, with tolerance changes 0.
- The later ENV_D correction changed only embedded expectation strings. `POST_BROAD_METADATA_AUDIT.json` proves no gameplay source change, and the final-product UI suite then passed 213/213.
- Delivery artifacts are `downloads/Aegis_SIM_v48_WIP_SEEKER_UNIFY_C_HTML.zip`, `downloads/Aegis_SIM_v48_WIP_SEEKER_UNIFY_C_REPORT.zip`, and `downloads/SEEKER_UNIFY_C_SHA256SUMS.txt`.

## Explicitly unresolved inherited debt

- Legacy `#lockBtn` EMCON UI: 14 cases remain `INCOMPLETE`; they are not reported as passing.
- `CIWS_SEED_419025_FAIL` remains inherited and unresolved.
- `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2` remains inherited and unresolved.
- No release, tag, direct `main` commit, or automatic merge is authorized. The `seeker-unify-c` branch stops at a pull request for user merge.

