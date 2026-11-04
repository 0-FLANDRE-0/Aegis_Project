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

