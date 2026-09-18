# AEGIS v48 WIP12A — Common terminal-ballistics foundation

## Scope

- Baseline: `archive/v48/WIP11C/Aegis_SIM_v48_WIP11C.html`
- Introduce one shared terminal-projectile state, traversal, trace and damage-transfer contract without forcing every collision regime through one penetration equation.
- Distinguish physical boundaries, resistance-free empty space, material-filled equipment volumes and resistance-free crew exposure volumes.
- Resolve traversal as an event-driven sequence that requeries geometry after every deflection, ricochet or state change.
- Advance fuzes by elapsed time and arbitrate fuze expiry against the next boundary, material-volume exit and projectile stop.
- Implement the modern thin-ductile-plate, light-structure and material-volume paths; explicitly reject unimplemented homogeneous and face-hardened armor solvers.
- Keep the existing Kh-35U and Kh-32 penetration path behind an exact compatibility adapter, including combat-RNG state.
- Produce channel-separated `DamagePacket` records and apply them to existing flooding, structure, crew and equipment consumers through a separate idempotent adapter.
- Define a diagnostic-only damage-patch contract while leaving persistent patch state and snapshot migration disabled.

WIP12A does not implement gun launch, turret or magazine operation, exterior ballistics, naval gunfire FCS, production heavy-armor solvers, a new target ship or persistent damage accumulation.

## Common projectile contract

`TerminalProjectileSpec` separates the incoming object's total `massKg` from the `penetratorMassKg` that can remain coherent through impact. Geometry, body material and mechanical properties, payload, fuze and terminal model family remain fixed for the event.

`TerminalProjectileState` carries the values that can change during traversal:

- ship-local position;
- normalized velocity `direction` and normalized projectile `bodyAxis`;
- speed, remaining total mass and coherent mass;
- integrity and optional spin slot;
- elapsed time;
- armed/functioning state and remaining fuze delay.

Kinetic energy, coherent energy, momentum and yaw are derived from state. In particular, yaw is calculated from `direction` and `bodyAxis`; a scalar yaw angle is not authoritative because it cannot preserve the direction of three-dimensional misalignment.

All kernel geometry uses `SHIP_LOCAL_METRES` and SI quantities. World-to-ship conversion is complete before traversal begins. Obliquity is defined as `0°` for a normal impact and `90°` for grazing incidence.

## Space and traversal authority

The traversal contract separates four kinds of space:

| Kind | Authority |
|---|---|
| `BOUNDARY` | Runs the selected plate/structure solver and may change projectile state. |
| `EMPTY` | Changes position, elapsed time and fuze time only. It consumes no speed, mass, coherent mass or integrity. |
| `DAMAGE_VOLUME` | Represents actual material such as an engine, generator, VLS or tank and consumes volumetric work only across the occupied distance. |
| `CREW_EXPOSURE` | Records direct, spall and fragment corridors for the crew consumer but supplies zero projectile resistance. |

Traversal does not sort the initial ray once and treat that list as final. After every contact it updates the state, advances past a bounded epsilon and requeries the current ray through the geometry adapter. The diagnostic deflection case reaches `W12A_REQUERIED_CONTACT` and excludes the stale straight-ray target.

At each segment the kernel compares the time to the next contact or volume exit, projectile stop and fuze expiry. The earliest event wins under deterministic tie rules. This permits detonation in the middle of empty space or inside a decelerating material volume instead of converting the fuze delay into one fixed distance.

## Solver and impact results

The registry selects by collision regime rather than weapon name:

- active: `THIN_DUCTILE_PLATE`, `LIGHT_STRUCTURE`, `VOLUME_CRUSH`;
- declared but explicitly unsupported: `HOMOGENEOUS_ARMOR`, `FACE_HARDENED_ARMOR`.

`BoundaryImpactResult` uses independent axes:

- traversal: `RICOCHET`, `STOPPED`, `PARTIAL`, `PERFORATED`;
- projectile failure: `INTACT`, `DEFORMED`, `FRACTURED`, `SHATTERED`;
- plate failure: denting, ductile hole, plugging, petaling, cracking, spall-only or none.

This allows results such as `PERFORATED + SHATTERED` without misreporting plate traversal. Every material event records before/after state, effective thickness and obliquity, hole/plug/spall data, mass and coherent-mass loss, integrity loss, yaw and direction change.

The diagnostic `ImpactBudget` records kinetic energy, plate/volume work, deformation, debris, unresolved dissipation, mass closure and momentum/target impulse. Fixtures reject created mass or energy beyond the declared tolerance.

## Trace, damage and idempotence

`ImpactTrace` records every event in order, including empty-space travel, contact/volume identity, before/after projectile state, fuze transitions, requery count and terminal position.

`DamagePacket` is calculation output rather than direct mutation. It separates:

- direct penetration;
- plug and rear spall;
- warhead fragments;
- blast;
- thermal/incendiary effects;
- breaches/flooding openings;
- structural impulse;
- crew exposure.

The trace and packet share an `impactEventId` as well as projectile and target identity. `wip12aApplyDamagePacket()` is the only WIP12A adapter that forwards the packet to existing damage consumers, and it rejects a repeated event ID. A deterministic application fixture produced one opening, one structural-impact evaluation, one crew-damage event with four injuries, and VLS/equipment damage; the second application returned `DUPLICATE_IMPACT_EVENT` and changed no state.

Aramid is not added to direct steel-equivalent penetration resistance. The paired fixture preserves direct plate work while reducing rear-spall and fragment channels.

## Diagnostic projectiles

The six kernel fixtures are intentionally simulation-tuned rather than claims about a named production round:

| Fixture | Primary contract |
|---|---|
| `TEST_12P7_AP` | small coherent penetrator and thin plate |
| `TEST_30_AP` | residual velocity after perforation |
| `TEST_30_HEI` | direct, fragment and incendiary channel separation |
| `TEST_76_SAP` | delayed fuze and compartment detonation |
| `TEST_127_HE` | external/shallow detonation, blast and fragments |
| `TEST_127_SAP` | multiple boundaries, material volume and internal detonation |

Each fixture also receives an independent boundary envelope covering ricochet, stop, partial perforation, complete perforation and projectile shatter. Additional fixtures cover DUD, unsupported armor, direction-change requery, contact/fuze tie ordering, in-volume fuze expiry, empty-space invariants, crew/material separation and aramid channel behavior.

## Legacy ASM compatibility

The active Kh-35U/Kh-32 impact path now enters the common terminal-ballistics API in `LEGACY_ASM_PENETRATION_COMPAT` mode. The adapter calls the byte-preserved WIP11C `solveResidualPenetration()` authority rather than the new thin-plate solver.

The compatibility regression verifies exact penetration output for normal and oblique Kh-35U/Kh-32 cases, preserves the existing DUD/breach/flood/impulse path and proves that the wrapper consumes no combat RNG. WIP12A does not migrate live ASM behavior to the new discrete-boundary model.

## Damage patch boundary

WIP12A defines a diagnostic patch record with surface ID, local coordinates, radius, remaining thickness, hole area, crack severity and residual strength. It does not create a persistent patch ledger, accumulate repeated hits across authoritative state, or change snapshot codec/revision behavior.

## Diagnostic API

- `wip12aTerminalBallisticsContract()`
- `wip12aDiagnosticProjectiles()`
- `wip12aRunFixture()`
- `wip12aTerminalDiagnostics()`
- `wip12aLegacyAsmCompat()`
- `wip12aApplyDamagePacket()`
- `wip12aDamagePacketIdempotence()`
- `wip12aPerformance()`
- `wip12aBoundarySurface()`
- `wip12aDamageVolume()`
- `wip12aCrewExposureVolume()`

## Local verification

- Inline JavaScript parse: `PASS`
- Workflow YAML parse: `PASS`
- Workflow jobs declared: `22`
- Existing crew, interior, BridgeMaster E, ship-profile, material/protection and WIP11B import-safety static contracts: `6/6 PASS`
- WIP11C static contract: `32/32 checks PASS`
- WIP12A static contract: `29/29 checks PASS`
- WIP12A browser contract: `2/2 PASS`
- Full Playwright suite: `30/30 PASS` using the local Three.js dependency path
- Six fixture normal runs and six complete boundary envelopes: `PASS`
- `PERFORATED + SHATTERED` independent-axis case: `PASS`
- EMPTY speed/mass/coherent-mass/integrity invariants with elapsed fuze time: `PASS`
- Direction-change geometry requery and stale-contact rejection: `PASS`
- Fuze/contact/exit/stop arbitration and deterministic tie policy: `PASS`
- DUD, material-only volume work and resistance-free crew exposure: `PASS`
- Mass, kinetic-energy and momentum diagnostic closure: `PASS`
- Aramid direct-work invariance with reduced spall/fragment channels: `PASS`
- Existing flooding, structure, crew, VLS/equipment consumer connection and duplicate-event rejection: `PASS`
- Legacy ASM output and combat-RNG state exact parity: `PASS`
- Identical `TEST_127_SAP` results at `1×`, `8×` and `16×`: `PASS`
- `64×` overload probe: 4,096 impacts, 43,008 events and 16,384 geometry queries in `95.1 ms` total (`0.02322 ms/impact`) in the final local headless run; this is instrumentation, not a hardware performance guarantee.
- Existing CIWS, Kh-32/ESSM ghost-track/BDA, flooding, structure, crew, VLS/material, snapshot zero-mutation and multi-view WebGL regressions: `PASS`
- WebGL console/page errors: `0 / 0`

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP12A.html`
- WIP12A exact baseline: `archive/v48/WIP11C/Aegis_SIM_v48_WIP11C.html`
- Added jobs: `terminal-ballistics-wip12a-contract`, `terminal-ballistics-wip12a`
- Expected jobs: `22`
- Required final result before merge: `22/22 jobs passed`
- Branch: `feat/v48-wip12a-terminal-ballistics-kernel`

## Artifact

- File: `Aegis_SIM_v48_WIP12A.html`
- Size: `2,880,628 bytes`
- SHA-256: `60705246ef0b659dadf67e23ca9b84bf7dc2cb477857d9714223291c564c3729`
- Exact WIP11C baseline SHA-256: `464e1fc4a7e3ef9565bc32ce42e7e5a112041a977ee96fb7bdb5920f7410c01f`

## Deferred work and next handoff

WIP12A is a foundation, not an activated gun system. The following remain deliberately deferred:

- production projectile data and live gun-ammunition integration;
- turret, magazine and firing operation;
- exterior ballistics, dispersion, atmosphere and wind;
- naval gunfire FCS, planned as WIP13;
- validated homogeneous and face-hardened armor solvers;
- persistent damage-patch accumulation and its snapshot migration;
- a target ship and multi-profile combat, planned as WIP14.

Before any live projectile migrates to the new solver, it needs its own sourced or explicitly simulation-tuned data, regime validation, same-seed regression and a deliberate compatibility decision. Existing ASM behavior remains on the legacy adapter until that separate migration is approved.
