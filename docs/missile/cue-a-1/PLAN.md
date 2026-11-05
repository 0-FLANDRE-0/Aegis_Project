# CUE_A-1 execution plan

## Baseline

- Directive: `CUE_A_1_DIRECTIVE.md` supplied 2026-11-05 (Asia/Seoul).
- PR #69 is open, not merged; baseline therefore follows `seeker-unify-c`.
- Baseline commit: `4faeb4e079b7baddcb1e1b8c1b892af804565938`.
- Baseline product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html`.
- Baseline product SHA-256: `efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7`.
- Stage-2 comparison commit: `cd0d6868784b9fe9763b01781d59bb657129e1dc`.
- Stage-2 product SHA-256: `dca6d886b9980b87d3c776e85ae4ff8839eb42128669cbc150b212e0dcaf18ec`.
- SEEKER_UNIFY_B product SHA-256: `b8551e5a239a407ec0ec1b3cb7fe0c45bebf025a6c5eef312dfd5ddf2519796d`.
- Working branch: `cue-a-1`.
- Broad regression budget: exactly one run, after Stage 2 only.
- Performance validation mode: `MAX_THREAT` only. `CONFIRMED_ONLY` remains static/scene-only and `UNVERIFIED` for performance.

## Sequential gates

1. Stage 0: attribute the eight paired raid expectation differences across B → C Stage 2 and C Stage 2 → C final. No product change.
2. Stage 1a: restore the ASM-only 0.5 km range floor through a frozen profile option; preserve SAM 0.20 km behavior.
3. Stage 1b: replace the cue-motion prediction with the exact-discrete Singer model and bounded unknown-velocity uncertainty.
4. Stage 2: restrict midcourse passive RF to allowed ship-radar families and add observed band/frequency handling and swept rotating-beam synthesis.
5. Run the broad regression exactly once, then package the product and evidence and open a PR. Do not merge, release, or tag.

## Frozen constants for implementation commits

The directive permits only these new values. They must be committed before the corresponding effect tests and are not adjusted from results.

| Constant | Value | Provenance |
|---|---:|---|
| `cueManeuverTauS` | 60 s | `SIM_TUNED` |
| unknown-velocity axis sigma / covariance cap | `vmax / 2 = 9 m/s` | `SIM_TUNED` |
| basket cap | `vmax * age + 3 * sigma_ref` | `PUBLIC_FORMULA` |
| MAX_THREAT passive receive band | 2–18 GHz | `ASSUMED_THREAT` |
| CONFIRMED_ONLY passive receive band | 8–12 GHz | `SIM_TUNED` |
| band centers | S=3.0 GHz, IJ=10.0 GHz | `SIM_TUNED` |
| accuracy reference | 10 GHz | `SIM_TUNED` |

## Preserved boundaries

- Truth is limited to world physics, measurement synthesis, damage, and diagnostic post-analysis.
- Cue filtering, basket construction, association, EKF, guidance, and passive selection receive only observed fields.
- Fixed-step simulation and existing isolated weapon hash RNG remain authoritative.
- Harpoon U3, HOJ, generic emitter hardcoding, per-equipment EMCON UI, Kh-32 60 km investigation, TRACK-D/OODA/HP/defensive-weapon work are excluded.

## Checkpoints

- Stage 0: `PASS`. Both paired runs completed with page/harness errors 0 and an exact Stage-2 replay. Physical-state and VLS deltas occur in C Stage 3 only; combat RNG and existing-observer deltas occur in both B→Stage 2 and Stage 2→final. No product, expected value, or tolerance changed.
- Stage 1a: `PASS`. Candidate SHA-256 `3e7c882be6b39416937f00e3b31d4139666efedcd1fc994d2251945220818c5e`; SAM 24/24 bit exact, ASM bit exact at and above 0.5 km, and all observed differences confined below 0.5 km. Protected functions are byte-identical and reversing the three intended edits restores the baseline main exactly.
- Stage 1b implementation: constants and exact-discrete Singer code prepared; effect tests intentionally pending until the implementation commit is frozen and pushed.
- Stage 2: pending.
- Final broad regression: not run.
