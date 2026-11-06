# CUE_A-1 final report

**IMPLEMENTED:** YES — range-floor restoration, exact-discrete Singer cue filter, bounded cue uncertainty, ship-radar-family passive RF and frequency/rotating-beam handling.<br>
**TESTED:** YES — all Stage 0/1/2 gates, one final broad run, post-broad metadata audit/UI confirmation, and one 60-battle reference run.<br>
**APPROVED:** PR CANDIDATE — directive-preapproved changed-path expectations are recorded with tolerance changes 0.<br>
**UNRESOLVED:** inherited `#lockBtn` 14, `CIWS_SEED_419025_FAIL`, `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`; CONFIRMED_ONLY performance remains UNVERIFIED.<br>
**RELEASE:** NO — PR only; main merge, release and tag were not performed.

## 1. Product

- Baseline: `seeker-unify-c@4faeb4e079b7baddcb1e1b8c1b892af804565938`, SHA `efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7`.
- Candidate: `Aegis_SIM_v48_WIP_CUE_A_1.html`, SHA `0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a`, 22,137,235 bytes.
- Performance mode: MAX_THREAT. CONFIRMED_ONLY received static/scene checks only.

## 2. Sequential gates

| Stage | Result | Evidence |
|---|---|---|
| 0 — paired attribution | PASS | All 8 C-era differences attributed; no code/expectation/tolerance change. |
| 1a — ASM range floor | PASS | SAM 24/24 exact; ASM exact at/above 0.5 km; differences confined below 0.5 km. |
| 1b — Singer filter | PASS (12/12 gates) | TRACK/hit regressions 0/0, controls 180 exact, S1 50/50, egress 37/37 intended ship. |
| 2 — passive RF | PASS (12/12 gates) | contaminants 0/50, controls 180 exact, S1 50/50, egress 37/37 intended ship. |
| Final broad | PASS WITH INHERITED DEBT | Native13 364/364, real WebGL 29/29; expected paired 8 classified. |
| Post-broad metadata check | PASS | ENV_D match, changed gameplay functions 0, targeted UI 213/213. |

No gate was bypassed. No result-dependent tuning was made.

## 3. Paired eight-item cause record

Stage 0 shows physical/VLS differences first occur in C Stage 2→final, while combat RNG/observer differences have both B→C Stage 2 and C Stage 2→final contributions. The final candidate's exact before/after values and safety invariants are in `EXPECTED_VALUE_UPDATES.json`; all eight are changed-path preapprovals. Both ships remain HP 100, fixed hull/damage layout and ports match, and both sides are fault-free. Assertion logic and tolerances changed by 0.

## 4. Singer dt result and fixed-tick table

- Method: Van Loan block exponential with Higham Padé13.
- 180 s, initial velocity sigma 0: one-step `3529.2813585273 m`, 1/60 s ticks `3529.2813585259 m`, relative error `4.060e-13`.
- 180 s, initial velocity sigma 9 m/s: one-step `3883.3267835257 m`, 1/60 s ticks `3883.3267835243 m`, relative error `3.757e-13`.

| Weapon | Velocity input | t (s) | position sigma (m) | velocity sigma (m/s) | cap (m) | range half (m) | limiter |
|---|---|---:|---:|---:|---:|---:|---|
| Kh-35U | null | 60 | 582.25 | 9.00 | 1980 | 12000.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-35U | null | 120 | 968.05 | 9.00 | 3060 | 12000.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-35U | null | 180 | 1317.21 | 9.00 | 4140 | 12000.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-35U | known | 60 | 491.75 | 9.00 | 1980 | 12108.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-35U | known | 120 | 906.09 | 9.00 | 3060 | 12216.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-35U | known | 180 | 1274.95 | 9.00 | 4140 | 12324.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-32 | null | 60 | 582.25 | 9.00 | 1980 | 12000.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-32 | null | 120 | 968.05 | 9.00 | 3060 | 12000.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-32 | null | 180 | 1317.21 | 9.00 | 4140 | 12000.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-32 | known | 60 | 491.75 | 9.00 | 1980 | 12108.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-32 | known | 120 | 906.09 | 9.00 | 3060 | 12216.00 | FRACTION_0_12 / FLOOR_5_DEG |
| Kh-32 | known | 180 | 1274.95 | 9.00 | 4140 | 12324.00 | FRACTION_0_12 / FLOOR_5_DEG |

All 12 diagnostic cases were stepped at 1/60 s. Their range half-width was set by the existing 0.12R floor; azimuth by the existing 5° floor. The physical cap and 3-sigma values remain recorded in `CUE_FILTER_SINGER.json`.

## 5. C final → Stage 1 → Stage 2 outcomes

| Weapon / EMCON | C final TRACK/hit | Stage 1 TRACK/hit | Stage 2 TRACK/hit |
|---|---:|---:|---:|
| Kh-35U / OFF | 60 / 59 | 60 / 59 | 60 / 59 |
| Kh-35U / ON | 60 / 59 | 60 / 59 | 60 / 59 |
| Kh-32 / OFF | 40 / 40 | 40 / 40 | 45 / 40 |
| Kh-32 / ON | 44 / 40 | 44 / 40 | 44 / 40 |

Stage 1 removed one transient Kh-32 ACQUIRE without changing TRACK, hit, or failure class. Stage 2 changed ten Kh-32 EMCON-OFF cells through the mandated 3 GHz wavelength scaling; it improved TRACK by five while ship hits remained 40. Forbidden in-search/out-of-basket failures stayed 0.

## 6. Passive receiver/equipment result

- Equipment: 150 baseline + 150 candidate rows; ALL_OFF produced 0 samples.
- ALL_ON/NAV_OFF/SPQ_OFF are normally selected by `SHIP SEARCH RADAR`; SPY_OFF falls back to `SURFACE SEARCH RADAR` where observable.
- Mean receive interval: 0.2 s for SPY-dominated rows and 0.44 s for SPY_OFF rotating-radar rows.
- Kh-32 ALL_ON mean absolute error: bearing 0.763°, elevation 0.803°; SPY_OFF: 0.257° / 0.263°.
- Kh-35U ALL_ON mean absolute error: bearing 1.192°, elevation 1.628°; SPY_OFF: 0.392° / 0.538°.
- Direct elevation-derived range is diagnostic only and never overwrites target-memory range. Full per-condition family, SNR, errors, and intervals are in `STAGE2_PASSIVE_TESTS.json` and `PASSIVE_RF_EMITTER_BAND.json`.

## 7. Contaminants and CONFIRMED_ONLY

- Friendly ESSM/SM-6 active seekers, aircraft radar, active Nulka, and ship jammer: selected 0/50.
- HOJ functions remained byte-identical; no new false acquisition in 180 controls.
- CONFIRMED_ONLY: Kh-32 passive disabled; Kh-35U accepted X-band only. Performance is explicitly **UNVERIFIED**.

## 8. Final regression and post-run correction

The one broad run took 2672.311 s. Native13 passed 364/364 and actual WebGL observed-world passed 29/29. Raw paired was 34/42 with exactly the eight preapproved state differences. Raw UI was 205/213: all eight failures were `tableMatch`, caused by ENV_D retaining the old `spawnEnemyMissile` integrity hash after Stage 2 added observed emitter metadata.

After the broad run, only ENV_D integrity metadata was advanced. Audit proved measured rows, conditions, seeds, normalized table, gameplay function source and tolerances changed by 0. `__ENV_D__.status()` then matched, and a bounded UI rerun passed 213/213. The raw broad file remains `REGRESSION_RESULTS_RAW.json`; reviewed disposition is `REGRESSION_RESULTS.json`.

The 60-battle reference (not a gate) completed 60/60: 301 kills, 19 leakers, 0 egress, 0 other versus C final 299/18/0/3. All 320 first associations were SHIP; neighbor/non-ship first associations were 0.

## 9. Remaining limits

- Legacy EMCON `#lockBtn` 14 assertions remain INCOMPLETE, not counted as PASS.
- `CIWS_SEED_419025_FAIL` and the two inherited CG observer differences remain open debts.
- Kh-32 60 km root-cause investigation, generic emitter work, HOJ changes, Harpoon U3, TRACK-D/OODA/HP/defensive-weapon work are out of scope.
- No main merge, release, or tag was made.
