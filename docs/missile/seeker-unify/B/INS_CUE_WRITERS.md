# `insTgtX/Y` writer inventory

## Status header

- IMPLEMENTED: exhaustive static inventory against SEEKER_UNIFY_A main source
- TESTED: assignment and object-literal scans for both fields
- APPROVED: classification vocabulary from the B directive
- UNRESOLVED: launcher cue has no pre-launch observation timestamp
- RELEASE: documentation only

No unclassified (`기타`) production writer was found. The source scan covered direct
assignment, compound assignment, and object-literal initialization for both fields.

| Writer/location | Classification | Clock effect in U0 | Notes |
|---|---|---|---|
| `spawnEnemyMissile` object literal | `LAUNCH` | initialize range and bearing clocks to missile launch age `0` | `lastKnownShipX/Y` has no timestamp; launch time is intentionally used |
| `asmApplyPassiveBearingB2` | `PASSIVE_BEARING` | bearing clock only, after the 3-sigma convergence test | retained range is not an RF range measurement |
| `asmTargetMemoryDriftB2` | `DRIFT` | none | isolated deterministic uncertainty stream |
| `updateEnemyMissile` `_c52InsMemory` restore closure | `FIXED_MEMORY` | none; both stay at launch time | restores frozen remembered aim before and after base update |
| `runWip13a2AsmDiversionFixture` | `TEST_FIXTURE` | fixture must reinitialize cue after overriding target | diagnostic-only exact target placement |
| `_wip103SpawnStraightKh35` | `TEST_FIXTURE` | fixture must reinitialize cue after overriding target | diagnostic-only straight approach |
| `wip13cSpawnInboundInsAsm` | `TEST_FIXTURE` + `FIXED_MEMORY` | fixture reinitializes cue; fixed-memory clocks remain at launch | deliberate exact remembered coordinate |
| `_wip108DirectShiftProbe` | `TEST_FIXTURE` | none needed for the world-frame shift assertion | directly probes that stored inertial coordinates do not shift |
| `runWip13b12ArhSeaClutterValidationFixture` literal | `TEST_FIXTURE` | lazy cue initialization | isolated association fixture |
| `runCoreUnitSelfTests` literals | `TEST_FIXTURE` | lazy cue initialization | isolated unit fixtures |
| `runWip116ReservationPerf` literals | `TEST_FIXTURE` | lazy cue initialization | reservation/performance fixtures, including `SAT-ASM` |
| `wip14b2BoundaryFixture` literal | `TEST_FIXTURE` | lazy cue initialization | boundary snapshot fixture |

## Seeker-memory check

There is no production assignment from seeker measurements back into `insTgtX/Y`.
Accepted seeker measurements update the EKF and mirror its estimate into
`seekerTgtX/Y` and `_lastSeekerX/Y`. Consequently the directive's conditional
`SEEKER_MEMORY` clock refresh has no applicable U0 writer. Adding one would alter the
existing ownership contract and is therefore not done.

## Read-only consumers

Guidance range, cue-angle, and fallback aim functions continue to consume the INS cue.
Only the pre-EKF association basket is routed through the new TargetCue accessor; U0
does not change guidance, gimbal, RF synthesis, Pd, noise, or post-EKF association.

