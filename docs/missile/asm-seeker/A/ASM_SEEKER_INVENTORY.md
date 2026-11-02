# ASM seeker inventory — S0

Status: **IMPLEMENTED (audit + minimal common-core correction) / TESTED (S1/S2 + S3 60 battles + broad regression) / APPROVED (directive auto-proceed) / UNRESOLVED (45 km coefficient-limited detection) / RELEASE (main merge approved; remote readback pending)**

## Pinned input

- Git: `e10b1bdf8822655d3b9d5c29491161e5e24ee203`
- HTML: `Aegis_SIM_v48_WIP_TRACK_C.html`
- HTML SHA-256: `3f2af4c1e18ef30ce4b8dfe4cc2b28f2b91cf96c62306e8f9c55df4a8c508c81`
- Unpacked packed-script SHA-256: `b036ce98279685c884896b918f9fc05f26b2980811c05e3eed39b25016d5827f`

The inventory was produced from packed script index 13. Debug fixtures and launch helpers were searched in addition to the live registries.

## Live seeker implementations

| Weapon | Live profile/implementation | Launch path | RF input | Tactical guidance input |
|---|---|---|---|---|
| Kh-35U | `ASM_PROFILES['Kh-35U']`, `ASM_SEEKER_PROFILES['Kh-35U']` (`KH35U_ARH_MONOPULSE_SIM`) | aircraft/diagnostic fixture -> `spawnEnemyMissile` -> `updateEnemyMissile` | `physicalRfReflectorRegistryWip13A3` -> anonymous common WIP22 measurements | common seeker EKF after confirmed TRACK/COAST; INS before confirmation |
| Kh-32 | `ASM_PROFILES['Kh-32']`, `ASM_SEEKER_PROFILES['Kh-32']` (`KH32_ARH_MONOPULSE_SIM`) | aircraft/diagnostic fixture -> `spawnEnemyMissile` -> `updateEnemyMissile` | same common WIP22 path | common seeker EKF after confirmed TRACK/COAST; INS before confirmation; vertical planner remains a separate flight-profile channel |
| RGM-84D Harpoon | `HARPOON_PROFILE_A` (`RGM84D_BLOCK1C_E1`) and `harpoonSeekerA` | `harpoonReleaseA` -> `harpoonFlightStepA` | `harpoonRfObservationsA` -> anonymous reflector measurements | `seeker.lock` only in TRACK/COAST; INS/route before confirmation |

No fourth live or debug-only anti-ship seeker profile was found. `ASM_PROFILES` and `ASM_SEEKER_PROFILES` each contain only Kh-32 and Kh-35U. Harpoon intentionally lives outside that common WIP22 registry and uses an independent per-round RNG and navigation memory.

## Kh-35U values under audit

All non-public signal, gate and state-machine values remain `SIM_TUNED`.

- `searchMaxKm: 50`
- `searchSectorAzDeg: 28`
- `searchPattern: RASTER_3BAR`
- `acquireHits: 3`
- `assocAcquireAngleFloorDeg: 1.8`
- `assocAcquireRangeFloorM: 450`
- `unresolvedAngleDeg: 0.75`

No listed profile value was changed in S0/S1/S2. S2 only made the already existing launch-cue residual scales hard prerequisites for the first EKF initialization.

## Public evidence boundary

- The directive's review source identifies ARGS-35E (Kh-35E) acquisition/lock range as up to 20 km.
- The directive's review source identifies Kh-35U/Kh-35UE lock range as up to 50 km (Rosoboronexport).
- Official source URLs checked on 2026-11-02: `https://www.ktrv.ru/production/military_production/missile_systems_and_aircraft_armament/args_35e/` and `https://roe.ru/eng/catalog/aerospace-systems/air-to-surface-missile/kh-35ue/`. Both returned HTTP 503 from the build environment, so this report records the directive-supplied public facts without pretending that the pages were successfully archived.

These public range claims do not establish the simulation's detailed beam, gate, Pd, noise, scan or guidance constants. Those remain explicitly simulation-tuned.
