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

