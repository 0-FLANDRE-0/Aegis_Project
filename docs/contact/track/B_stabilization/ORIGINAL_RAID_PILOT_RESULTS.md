# Original Kh-32 raid pilot: TRACK-A / DDG only

Status: **OBSERVED_FOR_REVIEW_NOT_APPROVED**. One authorized pilot completed; no product, fixture source, expectation or tolerance was changed. This is not the missing comparative B/DDG or CG approval.

## Execution and source proof

Product SHA `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`; original source SHA `8d2de4f64cb18e3248156e36fa454daee91b5603e03fee5a8f7bd372e0d5780e`. Ship `DDG_119_LATE_FLIGHT_IIA`, seed 1831565813, original scale-8 native frame loop. One shared browser lease, process 410594. Browser/context closed and lease released at completion.

The first attempt was blocked **before browser launch** by the missing original `B2_OUT` support environment. Its unchanged failure log is `evidence/original-raid-pilot/startup-missing-B2_OUT.log`. Supplying that required environment, not modifying the fixture/support, allowed the single actual browser pilot.

| Check | Observed result |
|---|---|
| Full raw 32 s historical scalar equality | **Exact**, every field; no exclusion/tolerance |
| Full raw 120 s historical scalar equality | **Exact**, every field; no exclusion/tolerance |
| Fixed-tick kernel/pipeline receipt | Original body `a4360bd8…5b1`, installed pipeline `c4f08708…1b1`, unchanged |
| Final native reference restoration | tick/retire/apply all true |
| Final `__ENV_D__.status()` | `match:true`, `changedNativeFunctions:[]` |
| Native/sampler/page faults | 0 / 0 / 0 |
| Maximum-horizon extra tick | Not used |
| Actual simulation | **9,728 ticks / 162.133333 s** |
| Actual elapsed wall | **83.718579 s** (estimate was 344.362 s for an unresolved 600 s run) |

The initial cohort became natively terminal after tick 9,425 (157.083333 s). The preserved frame loop stopped at tick 9,728, **5.05 s later**, satisfying the planned five-second aftermath plus frame-boundary allowance. Final own ship: HP **100**, water **0 m³**, module damage all **0**, native survival **NORMAL**. There were 20 native SAM launches and 31 later ASM spawns; these later missiles remain a separate cohort, not eight initial kills.

Source/kernel proof is unchanged native code plus passive pass-through observers and the exact historical checkpoints. There is no historical full OFF run beyond 120 s to compare against; do not claim a full 162 s paired truth-hash comparison from this one pilot.

## Strict native outcomes: one intercept, seven physical surface-target impacts

| Initial ASM ID | Native event step | Native event time (s) | Actual native reason |
|---|---:|---:|---|
| 1 | 9034 | 150.566667 | `SURFACE_TARGET_IMPACT` |
| 2 | 9424 | 157.066667 | `SURFACE_TARGET_IMPACT` |
| 3 | 8115 | 135.250000 | `SURFACE_TARGET_IMPACT` |
| 4 | 9185 | 153.083333 | `SURFACE_TARGET_IMPACT` |
| 5 | 8807 | 146.783333 | `SURFACE_TARGET_IMPACT` |
| 6 | 8121 | 135.350000 | `INTERCEPT_KILL`; actual `applyInterceptResult` = ESSM `KILL` |
| 7 | 8149 | 135.816667 | `SURFACE_TARGET_IMPACT` |
| 8 | 8386 | 139.766667 | `SURFACE_TARGET_IMPACT` |

Event stamps are the native pre-increment fixed-step clock. The after-tick object `life`/cohort observation can be one step later. The ESSM native fragment record corroborates the one KILL, with miss distance **1.521281 m**. No other native `applyInterceptResult` was recorded, and no native own-ship hit was recorded. No MAX_LIFE, timeout, generic disappearance, or inherited AIR_KILL fallback is counted as a kill.

The historical reused recorder incorrectly labels a dead `_outcomeRecorded` missile AIR_KILL as a fallback. Its raw base output is preserved but explicitly **nonauthoritative**. This report uses only the new helper's actual retirement events and actual intercept return values. In particular, **seven `SURFACE_TARGET_IMPACT` events are not seven defensive kills**.

The old original setup also retains the default **HULK** (`MULTISHIP_DEPLOYMENT_DEFAULT_A`, pinned source L3338). `applyAsmImpactToSurfaceTargetWip13A` L28424–28436 emits `SURFACE_TARGET_IMPACT` for a real non-ownship physical surface-target contact, whereas own-ship contacts take another branch. All seven contacts finish around world `(11.03,-8.62)` km, z≈11–13 m. That agrees with the first `defaultSurfaceTargetPlacementWip13A` candidate (L28465–28469): 14 km, heading offset 52° from the ownship's −90° heading. `spawnSurfaceTraffic` L28480–28487 normally creates `SURFACE_TARGET_HULK_001` there.

The pilot did **not** retain the contacted target entity ID, its full damage history, or the missile's seeker target-estimate history. Consequently the specific HULK identity is supported by the static default path and matching geometry rather than a captured contact ID; why each seeker/trajectory selected that surface contact is not proven here. Actual seven physical surface-target impacts are proven. “All eight attacks were successfully defended” is false; “seven hit the own ship” is also false.

## What resolved the 120 s question

The missiles were progressing, not frozen. They were still high in native climb/diver flight at both previous checkpoint horizons:

| Simulation time | Native initial-cohort phase | Physical altitude range |
|---|---|---:|
| 0 s | 8 `SEPARATE/INITIAL` | 10.000 km |
| 10 s | 8 `CRUISE/CLIMB` | 10.659 km |
| 32 s | 8 `CRUISE/CLIMB` | 18.004–18.742 km |
| 40 s | 8 `CRUISE/CLIMB` | 19.710–21.702 km |
| 50 s | 8 `DIVE/DIVE` | 19.778–24.203 km |
| 100 s | 6 `DIVE`, 2 `TERMINAL` | 4.315–10.573 km |
| 120 s | 1 `DIVE`, 7 `TERMINAL` | 1.911–6.026 km |
| 135.25–157.083 s | Native terminal events above | One ESSM kill; seven surface-target contacts |

Ten-second samples bound phase-transition intervals; they do not provide exact transition timestamps. At 120 s there had not yet been a native intercept/contact in this run, so extending only to that time could not establish final combat outcomes. This pilot supplies the previously missing native progression/termination evidence for **A/DDG**, not a causal proof about every earlier association decision.

## Repeated carrier inputs: physical pair separation actually measured

The original cycling bearing/range creates spawn-order pairs 1/5, 2/6, 3/7 and 4/8. Their physical XYZ and velocity vectors are indeed identical in this pilot at t=0. Subsequent native random/navigation/flight differences cause divergence. Values below are offline Euclidean distances between the separately retained AFTER_ACTION physical records; no truth distance enters tactical code.

| Pair | 0 s separation | 10 s | 32 s | 120 s |
|---|---:|---:|---:|---:|
| 1 / 5 | 0 m | 19.781 m | 241.837 m | 2668.860 m |
| 2 / 6 | 0 m | 27.103 m | 817.969 m | 9524.139 m |
| 3 / 7 | 0 m | 22.204 m | 114.399 m | 297.609 m |
| 4 / 8 | 0 m | 46.940 m | 185.718 m | 7339.815 m |

All four initial velocity differences are **0 m/s**. They are approximately 0.763–5.244 m/s at 10 s. Physical separation is not a sensor-resolution or association decision: signal resolution, observed dimensions/noise/covariance and native NIS still govern those. The pilot has no pose sample exactly at the archived first B HOLD (~3.23 s), and TRACK-A does not execute a B HOLD policy. Therefore this table cannot establish a full 0–120 s B HOLD census, prove the first HOLD unnecessary, or prove all four pairs remain indistinguishable.

## Remaining decision

The pilot now makes an original-cohort result measurable beyond 120 s at modest cost. It does not approve original paired four state failures, seed 419012 or seed 419025. To argue unchanged original ultimate outcomes, a separately authorized comparable B/DDG and A/B CG run still needs the same pinned initialization, raw checkpoint gates, native outcome/resource accounting, and explicit handling of the physical HULK/later patrol cohort. Do not replace this inherited legacy diagnostic setup with the different zero-track natural Kh-35U fixture, and do not weaken ambiguity rules or baselines to force historical hashes.

Primary evidence: `evidence/original-raid-pilot/PLAN.json`, `SUMMARY.json`, `original-expression-result.json`, `track-a-DDG-original-raid.json.gz`, `env-status.json`, the exact expression/helper diffs, and both startup/run logs. This one pilot is complete; **no follow-up browser run was started**.
