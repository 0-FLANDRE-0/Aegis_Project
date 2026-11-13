# AEGIS_DEFENSE_DECISION_INPUT_A1

`AEGIS_DEFENSE_DECISION_INPUT_A1` is an owner-addressed, deep-frozen observation snapshot. It is built at the current fixed step without advancing simulation state or consuming RNG. A local `trackId` is an address in that owner's track file, not a truth-entity identifier.

## Root

| Field | Unit / meaning | Owner |
|---|---|---|
| `ownerEntityId`, `profileId` | receiving ship and profile | ship runtime |
| `step`, `simulationTimeS`, `revision` | fixed tick, seconds, WIP118 revision | simulation / WIP118 |
| `mode` | `AUTO`, `MANUAL`, or `HOLD` | existing engagement control |
| `tracks[]` | owner-local observed/received track rows | track manager / WIP118 |
| `inventory` | installed and post-reserve counts | weapon inventory / H1 reserve policy |
| `support` | SPG health, assignments, reservations | existing FCS state |
| `ship` | mission/afloat/display-HP, limited crew summary and continuous damage factors | HP_A / crew / damage model |
| `network` | enabled sharing/cooperative policy; remote FCS remains false | Network G |
| `esmCues[]` | observed active-seeker cues with source, time, uncertainty | owner-local ESM execution |
| `operatorOverrides` | existing H1 radar/EW manual flags and EMCON state | operator/H1 |

## Track row

- `measurement.positionM`: observed Cartesian metres (`x/y/z`), or `null`.
- `measurement.velocityMps`: observed metres/second, or `null`.
- `measurement.covariance`: copied 6x6 owner-local EKF covariance, or `null`.
- `measurement.measuredAtStep`, `measuredAtS`, `ageS`, `sensorSource`: measurement timing/provenance.
- `lifecycle`: confirmed, detected, coast, reacquire, memory, assessment state and lost age.
- `identification`: the existing A3-separated classification, identity, threat status and engagement authority.
- `assessment`: existing WIP118 state, CPA, TGO, engagement count and re-engagement flags.
- `engagements`: owner-local current defensive weapon engagement counts.
- `network`: advisory lease/assignment and local/remote report provenance. It does not grant remote fire control.

## Limited crew summary

`ship.crew` is a projection of the same owner's existing crew snapshot. It contains only:

- `mode` and `combatUnavailable`;
- total, fit, injured, dead and evacuated counts;
- `duty`, `fit` and existing deterministic `availability` for `COMBAT` and `OPERATIONS`.

It does not contain the roster, personal IDs, compartments, routes, individual injuries, casualty log, duty-station labels or damage events. Missing source values remain `null`; no normal availability is invented. `LEGACY_H1` does not read this projection, and the projection is not exported into operational saves.

## Immutability and side-effect contract

- Every object and array is recursively frozen before publication.
- Repeated `input(ownerId)` calls preserve operational-save bytes and simulation RNG exactly.
- The snapshot is transient. No field is added to the game-save schema.
- Active DDG/CG and foreign-friendly owners use the same contract through their own lexical weapon contexts.

## Forbidden information

The input must not contain or derive hidden enemy truth objects, truth/entity IDs, actual hidden positions or velocities, faction/hostility truth, hidden survival state, unobserved projectile arrays, predicted-hit truth, or renderer/Three.js objects. The product audit recursively checks forbidden field names and the browser oracle independently repeats the check. Both report zero findings.

Friendly sender/owner entity IDs may appear only as routing provenance. They are not target truth IDs and never substitute for a local track ID.

## Evidence

- `CONTRACT_ORACLE.json`: DDG and CG, active and foreign owner, frozen input and read-only checks.
- `CONTRACT_ORACLE_REPEAT.json`: bit-identical repeat.
- `evidence/final-correction/commit-a/CREW_CONTRACT_ORACLE.json`: owner-local normal/injured/unavailable fixtures, read-only mutation audit and `LEGACY_H1` equivalence.
- `evidence/final-correction/commit-a/CREW_CONTRACT_ORACLE_REPEAT.json`: bit-identical crew-contract repeat.
- `OWNERSHIP_MATRIX.md`: producer/consumer ownership and truth-access audit.

