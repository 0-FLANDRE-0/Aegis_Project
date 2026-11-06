# SEEKER_UNIFY_C Stage 3 — launch cue source audit

Status: **pre-effect audit complete** (2026-11-04). This document fixes the
input contract before CUE_A effect testing. It is not a claim about real weapon
performance.

## Production writers

| Path | Position supplied at launch | Velocity supplied at launch | Classification | CUE_A handling |
|---|---|---|---|---|
| Airborne hostile ASM, `spawnEnemyMissile(fromTarget)` | `fromTarget.lastKnownShipX/Y`, then the pre-existing 0.15–0.60 km launch-memory error | none | **UNRESOLVED**: the upstream aircraft radar/RWR code forms `lastKnownShipX/Y` from truth geometry plus simulated measurement error, rather than a persisted track estimate | initialize position from the launch memory; initialize velocity as unknown (`null`), never from target truth |
| Formation/shared aircraft contact | leader/shared `lastKnownShipX/Y` with the existing formation-sharing error | none | **UNRESOLVED** for the same truth-plus-noise upstream path | same contract as the airborne writer |
| Sovremenny NPC | no production Kh-35U/Kh-32 launcher is connected in the current SOV_A profile | none | not a cue writer | no CUE_A object is created |
| Other ship/scenario NPC paths | no production call to `spawnEnemyMissile` was found; friendly Harpoon and H3 ship attack paths are separate systems | none | out of scope | unchanged |

The product currently has no trustworthy production target-velocity estimate
for hostile ASM launch. CUE_A therefore uses the directive's fixed
`18 m/s` velocity uncertainty and a zero-mean unknown velocity state. It does
not infer velocity from target identity, profile, or hidden target motion.

## Diagnostic-only writers

Calls from WIP14/ASM diagnostic fixtures and direct `enemyMissiles.push(...)`
fixtures are test setup, not production launch sources. They may provide an
explicit cue position, velocity and covariance through the diagnostic CUE_A
hook. If velocity is omitted, the production unknown-velocity rule applies.
Exact test placement is labelled **AFTER_ACTION_TRUTH / DIAGNOSTIC_ONLY** and
must not be used as a tactical input.

## Preserved exception

`_c52InsMemory` is an intentional fixed-memory fixture/legacy contract. It is
preserved: CUE_A prediction and RF/DL updates do not alter its remembered
target point.

## Boundary contract

The launch adapter may pass only:

- position and its covariance;
- optional velocity and its covariance (currently absent in production);
- measurement/reference time and source label.

It may not pass a target/entity id, profile id, truth reference, future path,
or hidden velocity. The onboard state is `[x, y, vx, vy]` plus a 4x4 covariance.
All propagation runs on fixed simulation time. Rendering remains read-only.

## Audited code paths

- `spawnEnemyMissile`
- hostile-aircraft radar/RWR updates of `lastKnownShipX/Y`
- formation contact sharing
- `asmTargetCueU0`, `asmCueBasketU0`, `asmTargetMemoryDriftB2`
- WIP14B2 boundary/navigation fixtures
- Sovremenny and H3 ship attack registrations
