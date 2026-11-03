# SEEKER_UNIFY_B plan

## Status header

- IMPLEMENTED: planning and pre-change writer audit only
- TESTED: static source inventory only; no outcome/effect test has run
- APPROVED: directive `SEEKER_UNIFY_B_U0_U2_DIRECTIVE.md`
- UNRESOLVED: pre-launch target-track age is not represented by the current launcher cue
- RELEASE: no release; PR only, no merge/tag

## Frozen baseline

- Git commit: `ba9bc114485838b52450164d5af026fd3d8f5e88`
- HTML: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html`
- HTML SHA-256: `53864e5939ca0fce03f50fb3040c2eafccd816027ba92960b53cf7c744ac08f8`
- Output: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html`

## U0 constants frozen before effect tests

The values below are the only new `SIM_TUNED` constants allowed by the directive.
They are frozen before any U0 outcome/effect test and are not to be fitted to results.

| Constant | Frozen value | Provenance |
|---|---:|---|
| `assumedMaxTargetSpeedMps` | 18.0 m/s | `SIM_TUNED`; upper public-range design assumption for a surface combatant |
| `minAcqRangeFloorM` | 1500 m | `SIM_TUNED`; reject salvo neighbours at hundreds of metres |
| `minAcqRangeFrac` | 0.5 | `SIM_TUNED`; prevent the lower edge dropping below half cue range |

Machine-readable copy: `U0_FROZEN_CONSTANTS.json`. Pre-effect-test freeze commit:
`3bdcde42ce8deac0d6962e6b50ddedcfde7991b8`.

## Ordered work

1. U0 TargetCue accessor, independent range/bearing clocks, and time-expanded hard basket.
2. U0 SHADOW comparison, then ACTIVE only after the directive gates pass.
3. Harpoon basket audit without product-code modification.
4. U1 read-only DTO/profile/RNG adapters, SHADOW bit-equivalence, then ACTIVE.
5. U2 common active-monostatic echo/cell layer in SHADOW.
6. Stop on any `IMPLEMENTATION_DIVERGENCE`; never choose one implementation locally.

## Fixed semantic decisions

- Cue clocks use missile age (`em.life`), so launch time is `0` in that clock domain.
- Passive bearing correction may refresh only the bearing clock and only after the
  measured/cue residual is within `3 * bearingErrorRad`.
- Target-memory drift refreshes neither clock.
- `_c52InsMemory` keeps both clocks at launch time.
- There is no current production `SEEKER_MEMORY` writer for `insTgtX/Y`; seeker memory
  resides in the EKF and `_lastSeekerX/Y`, so no cue clock is refreshed from it in U0.
- `velocityMps` and source `DL` are reserved DTO fields only; U0 does not predict cue centre.

