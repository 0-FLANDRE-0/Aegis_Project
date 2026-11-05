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
- Stage 1b: `PASS`. Frozen implementation commit `46889420995ddb545e64f02d700eb2bbdd3ba9f4`; product SHA-256 `a1c7ad560a47aaea0e82c90639b6db4e0e9b44eabe9289a8f002523270eabaac`. Van Loan + Higham Padé13 reproduced the 180 s anchors with relative dt errors `4.06e-13` / `3.76e-13`. The 240-cell MAX_THREAT matrix had TRACK/hit regressions 0/0 and forbidden basket-failure delta 0; 180 false-acquisition controls were byte-identical; S1 remained 50/50 TRACK; all 37 TRACK-C replay missiles first-associated the intended ownship; representative decisions were deterministic; truth/scope audit passed with 3,074 other functions byte-identical. One Kh-32 60 km cell lost a transient ACQUIRE but remained non-TRACK/non-hit in both builds and never left the basket, so the gate is unaffected. Evidence: `CUE_FILTER_SINGER.md/.json`.
- Stage 2: `PASS`. Frozen implementation commit `48a268f79e1f40e46c2d7ab96f9ead721276f2a2`; product SHA-256 `83e3d76a50b6db4616cd7b5dcb013361617477dd90dfa4ea6352248ada84932c`. All 12 gates passed: equipment 150+150 rows, contaminant 50 rows with selections 0, controls 180 rows bit exact, cue matrix 240 rows with TRACK/hit regressions 0/0 and forbidden basket failures 0→0, S1 50/50, and all TRACK-C 37 missiles first-associated the intended ownship. Kh-32 EMCON-OFF TRACK improved 40→45 while ship hits stayed 40; the ten changed cells are attributed to the mandated 3 GHz wavelength scaling. HOJ and 3,093 other functions are byte-identical. CONFIRMED_ONLY static/scene checks passed and performance remains `UNVERIFIED`. Evidence: `PASSIVE_RF_EMITTER_BAND.md/.json`.
- Final broad regression: not run.
