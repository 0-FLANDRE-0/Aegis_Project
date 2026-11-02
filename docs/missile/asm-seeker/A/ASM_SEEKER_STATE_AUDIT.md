# ASM seeker state and call-graph audit — S0

Status: **IMPLEMENTED / TESTED (static call graph + S1/S2 + S3 60 battles + broad regression) / APPROVED (directive auto-proceed) / UNRESOLVED (45 km coefficient-limited detection) / RELEASE (main merge approved; remote readback pending)**

## Kh-32 / Kh-35U common WIP22 core

Call graph:

`spawnEnemyMissile` -> `createAsmFlightState` + `missileNavB2Init` -> fixed tick `updateEnemyMissile` -> `updateEnemyMissileBaseC52` -> `updateAsmSeeker` -> `asmUpdateSeekerGimbal` + `asmUpdateHojTrack` -> `asmSeekerMeasurement` -> `asmSeekerVisibleRfReturns` -> `asmSeekerCompositeReturns` -> `asmSeekerEchoMeasurement` -> `asmSeekerAssociateMeasurements` -> `asmSeekerEkfUpdate` -> flight phase guidance -> `asmCommandHeading`/`asmCommandHeadingRate` -> common body/velocity dynamics.

States and transitions:

- `OFF`: no RF track; seeker enable sends it to `SEARCH`.
- `SEARCH`: cue-centred raster (Kh-35U) or rosette/spiral (Kh-32). First accepted measurement initializes the EKF and enters `ACQUIRE` with one hit.
- `ACQUIRE`: repeated gated measurements increment the hit counters. Three accepted measurements, including the required strict-evidence count, enter `TRACK`. A bounded coast/window policy can return to `SEARCH` and clears the candidate EKF.
- `TRACK`: confirmed RF track. Missing measurements beyond `coastAfterS` enter `COAST`.
- `COAST`: predicted EKF remains available. Missing measurements beyond `reacquireAfterS` enter `REACQUIRE`; a gated hit can return toward `TRACK`.
- `REACQUIRE`: outward scan and wider association floors. Two accepted measurements return to `TRACK`; `lostAfterS` returns to `SEARCH` and clears the EKF.
- `LOST`: compatibility state; the next enabled update enters `SEARCH`.
- HOJ has its own `OFF/ACQUIRE/TRACK/COAST` angular-only state. It never invents range.

Association has no target/entity ID branch. With no EKF it scores measurements against the launch cue (`insTgtX/Y`) using measured range/azimuth/elevation, evidence and SNR. With an EKF it gates by measurement covariance, innovation/NIS and mode-specific physical floors. Debug IDs survive only in diagnostic fields.

Guidance contract observed in source:

- `em.seekerLocked` is true only for common seeker `TRACK`/`COAST` or active HOJ, not for `ACQUIRE`.
- Kh-35U `SEEKERON` explicitly commands the INS heading until confirmation.
- Kh-32 horizontal PN is gated by `em.seekerLocked && !em._blindTerminal`.
- `asmSeekerAimWorld` can expose a candidate EKF during `ACQUIRE` to internal range/diagnostic helpers, but the audited lateral command sites do not consume it as a confirmed steering source. S1 records the actual command path to verify this dynamically.

## RGM-84D path

Call graph:

`harpoonReleaseA` -> fixed tick `harpoonStepA` -> `harpoonFlightStepA` -> `harpoonRouteStepE` -> `harpoonSeekerA` -> `harpoonRfObservationsA` -> anonymous gated candidates -> candidate/lock filter -> `harpoonFlightStepA` guidance.

States:

- `OFF`: before route completion/activation range and booster timing.
- `SEARCH`: azimuth scan around the INS memory/basket.
- `ACQUIRE`: candidate file; three repeated observations are required.
- `TRACK`: confirmed `seeker.lock` drives guidance.
- `COAST`: last confirmed lock coasts; coast expiry returns to `SEARCH`.

The live caller cannot inject diagnostic observations. The optional argument is used by the existing `harpoonSeekerCoreAuditC` only. Harpoon has no datalink after release.

## S1 hypotheses fixed before runtime tests

1. A multi-reflector search may select the wrong launch-cue-consistent reflector or alternate before confirmation.
2. Unconfirmed common-seeker candidates should not gain lateral steering authority. Static inspection says the normal command path already gates on `seekerLocked`; runtime same-tick command logging must confirm it.
3. Existing TRACK-C egress classification is an endpoint label, not a root cause. The 37 available C samples were traced to the first accepted RF association: every sample initialized on a neighboring `RF_OBJECT`, with no damage before the first confirmed track. See `EGRESS_ROOT_CAUSE.md/.json`.

## Runtime closure

- Diagnostic observer ON/OFF produced byte-identical comparable final JSON and global RNG for the frozen replay.
- Kh-35U S2 matrix: 40/100 expected locks, 0 ACQUIRE-candidate lateral steering commands, and 0/20 no-target false locks across Kh-35U/Kh-32 controls.
- Kh-32 single/dual-reflector preservation: 20/20 expected locks.
- RGM-84D independent physical path: 20/20 expected locks; its separate basket/state implementation was not modified.
