# SEEKER_UNIFY_B final report

## Status header

- IMPLEMENTED: U0 time-expanded pre-EKF ASM cue basket; U1 common DTO, SI-unit, read-only profile, and RNG-adapter boundary; U2 read-only common echo/cell calculations in SHADOW only
- TESTED: U0 cue/S1/1,590-case matrices, Harpoon audit, 60 battle reference, U1 2,400-run equivalence, U2 78 representative scenes, final determinism/RNG audit, and one final broad regression
- APPROVED: U0 ACTIVE and U1 ACTIVE; U2 instrumentation only
- UNRESOLVED: U2 beam/LOS, cell extent, and angular representation policy require user direction; pre-launch cue age and Harpoon time-aged basket remain deferred
- RELEASE: no release or tag; branch PR only, user merges

Overall: **STOP AT U2 IMPLEMENTATION_DIVERGENCE**

The product is safe to inspect as **U0 ACTIVE + U1 ACTIVE + U2 SHADOW**. U2 output is not connected to a seeker, EKF, guidance, engagement decision, or tactical output and consumes no RNG.

## Build identity

| Item | Value |
|---|---|
| Base commit | `ba9bc114485838b52450164d5af026fd3d8f5e88` |
| Base HTML | `Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html` |
| Base HTML SHA-256 | `53864e5939ca0fce03f50fb3040c2eafccd816027ba92960b53cf7c744ac08f8` |
| Product | `Aegis_SIM_v48_WIP_SEEKER_UNIFY_B.html` |
| Product bytes | `22,129,963` |
| Product SHA-256 | `b8551e5a239a407ec0ec1b3cb7fe0c45bebf025a6c5eef312dfd5ddf2519796d` |
| Product main-source SHA-256 | `7c48c8cb024ead14bb9b55eccc615f18d2e93e16832c1f3422d74e3779bd6ab9` |
| U0 frozen-constant commit | `3bdcde42ce8deac0d6962e6b50ddedcfde7991b8` |

## U0 — cue basket

Gate: **PASS (9/9)**.

- Baseline/SHADOW/ACTIVE cue rows: 240 each.
- Baseline TRACK to U0 defect regression: 0.
- Baseline failure to U0 TRACK: 44.
- Azimuth cap violations: 0. `azHalf` uses `min(calculatedHalfAngle, profile.searchSectorAzDeg)` and introduces no new cap constant.
- Passive bearing clock: 167,882 updates / 175,356 attempts (95.74%).
- First-association after-action audit: 320/320 were the intended ship; neighboring ASM first association 0, non-ship first association 0.
- Failure categorization is diagnostic-only and uses after-action truth. All ACTIVE cue rows acquired TRACK, so outside-sector / inside-sector-outside-basket / other failure counts are all 0. The counters remain in the diagnostic path.

### Kh-35U 100/130 km TRACK result

| EMCON | Range | Motion | Baseline | U0 |
|---|---:|---|---:|---:|
| OFF | 100 km | 15 kn straight | 5/5 | 5/5 |
| OFF | 100 km | 30 kn straight | 1/5 | 5/5 |
| OFF | 100 km | 30 kn +30° | 2/5 | 5/5 |
| OFF | 100 km | 30 kn +90° | 5/5 | 5/5 |
| OFF | 130 km | 15 kn straight | 4/5 | 5/5 |
| OFF | 130 km | 30 kn straight | 0/5 | 5/5 |
| OFF | 130 km | 30 kn +30° | 0/5 | 5/5 |
| OFF | 130 km | 30 kn +90° | 5/5 | 5/5 |
| ON | 100 km | 15 kn straight | 5/5 | 5/5 |
| ON | 100 km | 30 kn straight | 1/5 | 5/5 |
| ON | 100 km | 30 kn +30° | 1/5 | 5/5 |
| ON | 100 km | 30 kn +90° | 3/5 | 5/5 |
| ON | 130 km | 15 kn straight | 4/5 | 5/5 |
| ON | 130 km | 30 kn straight | 0/5 | 5/5 |
| ON | 130 km | 30 kn +30° | 0/5 | 5/5 |
| ON | 130 km | 30 kn +90° | 0/5 | 5/5 |

### Basket distribution at first TRACK/ACQUIRE

| Field | Min | Median | Max |
|---|---:|---:|---:|
| rangeLowM | 7,948.60 | 27,496.12 | 59,543.22 |
| rangeHighM | 21,315.92 | 35,392.33 | 75,782.28 |
| azHalfDeg | 5.00 | 5.00 | 25.5074 |
| rangeAgeS | 2.633 | 102.783 | 402.967 |
| bearingAgeS | 0.0167 | 5.633 | 402.967 |

The frozen SIM_TUNED values are `assumedMaxTargetSpeedMps=18`, `minAcqRangeFloorM=1500`, and `minAcqRangeFrac=0.5`. They were committed before effect testing and were not fit afterward.

### Harpoon audit

Harpoon product code was not changed. It acquired 5/5 at every audited 60/100/120 km condition except 100 km and 120 km at 30 kn +90°, where it acquired 0/5. The time-aged Harpoon search basket remains a U3 decision.

## U1 — common contract boundary

Gate: **PASS**.

Six paths × 200 cases were compared between U0 ACTIVE and U1 SHADOW. Baseline plus candidate executed 2,400 runs. Differences, page errors, DTO forbidden-field leaks, and truth use were all 0. After the exact-equivalence result, U1 was promoted to ACTIVE with no calculation branch on the mode marker.

Covered paths: Kh-35U, Kh-32, Harpoon, SARH/ESSM Block 2 ARH, SM-6 Block IA air and surface modes, and RAM passive RF/IR.

## U2 — common echo and cell SHADOW

Gate: **STOP**. No U2 component was promoted.

| Component | Classification | Difference | Decision |
|---|---|---:|---|
| SAM ARH monostatic power | `FP_ORDER` | max relative `1.0195689968577725e-15` | keep SHADOW; bit-equal gate not met |
| Beam/LOS normalization | `IMPLEMENTATION_DIVERGENCE` | ASM max relative `0.9920859674324555`; SAM one-beam alternative `0.14800224630674552` | user must choose one-factor ASM or tx/rx SAM convention |
| Resolved-cell extent | `IMPLEMENTATION_DIVERGENCE` | ASM max relative `1.0`; SAM `0.6172967281105196` | user must choose RMS or max-member semantics |
| Cell angular policy | `IMPLEMENTATION_DIVERGENCE` | ASM centroid max `0.010135380514274317 rad` (~0.581°) | user must choose separate-axis composite or spherical member-preserving semantics |

Representative coverage was ASM 30 scenes, cue 12 flights, and SAM 36 scenes. It included ESSM Block 2 and SM-6 Block IA air/surface modes against aircraft, ASM, sea clutter, and chaff at 10/30/50 km. Tactical differences, page errors, cell-count mismatches, and member-count mismatches were 0.

Static scope verification proves that removing the single U2 block from the final source exactly recreates the U1 ACTIVE source. `tacticalOutputUsed=false`, `rngConsumed=false`, and `truthOutput=false`.

## Final broad regression — executed once

Per the supplemental instruction, broad regression was deferred until the final stop and executed exactly once.

| Suite group | Result |
|---|---:|
| Native 13 suites | 364/364 PASS |
| Paired friendly | 42/42 PASS |
| UI | 213/213 PASS |
| Actual WebGL observed-world | 29/29 PASS |
| New failures | 0 |
| Wall time | 2,160.860 s |

The inherited retired EMCON UI suite still has 14 unexecuted assertions because `#lockBtn` no longer exists. It is recorded as legacy debt, not a pass and not a new SEEKER_UNIFY_B regression. Existing inherited items `CIWS_SEED_419025_FAIL` and `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2` remain separately recorded and were not waived or changed here.

## Determinism and RNG

The final product was wrapped with test-only instrumentation using an inverse-byte-exact diagnostic build. Ten jobs were repeated in the same page and a fresh page. Both comparisons were exact; all three result hashes were `2d4e41744fd7d554669acf4a755b19022c0b0505f5c5eb4b57937fca9643df4f`; global RNG samples were identical; page errors were 0.

## Expected-value policy

No assertion tolerance was changed. The U0 60-battle aggregate changed from 264 kills / 15 leakers / 37 egress / 4 other to 301 / 17 / 1 / 1. This is explained by the seeker-path U0 basket change: old egressing ASMs now reach acquisition/terminal more often. It is a reference aggregate rather than an assertion baseline. The preapproved record is in `EXPECTED_VALUE_UPDATES.json`.

## Delivery packaging

- `Aegis_SIM_v48_WIP_SEEKER_UNIFY_B_HTML.zip` contains exactly one entry: the product HTML. ZIP SHA-256 before publication is `0d89a2eb1a47a25bde1f8eb487c2db461da3f81baf74ef5df896c9ec97613d62`.
- The extracted HTML is byte-identical to the product and has SHA-256 `b8551e5a239a407ec0ec1b3cb7fe0c45bebf025a6c5eef312dfd5ddf2519796d`.
- The report ZIP excludes the executable HTML and contains the reports, raw regression evidence/screenshots, reproduction scripts, and `REPORT_MANIFEST_SHA256.txt`.
- Both ZIP archives passed full CRC checks. Final package hashes are recorded in `SHA256SUMS_v48_WIP_SEEKER_UNIFY_B.txt`.

## Unresolved and next decision

1. Select the U2 beam/LOS convention.
2. Select the cell extent convention.
3. Select the angular clustering/representation convention.
4. Decide whether to normalize the tiny SAM power FP-order difference or keep legacy operation order.
5. U3 remains the proper place for a time-aged Harpoon cue basket.
6. Pre-launch track age is not represented in the current launch cue.

U3 and later stages were not started. main was not modified; release and tag creation are prohibited for this result.
