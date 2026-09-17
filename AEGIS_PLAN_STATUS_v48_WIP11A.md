# AEGIS v48 WIP11A — runtime ownership boundary cleanup

## Scope

- Baseline: `archive/v48/WIP11/Aegis_SIM_v48_WIP11.html`
- Preserve WIP11 combat, sensor, damage, flooding, stability, crew, material/protection and rendering results.
- Establish one canonical mutable runtime for the player ship and a separate engagement/world owner.
- Isolate accepted geometry and compatibility paths without deleting the archived migration fixtures.
- Add registry, lifecycle, operational-state and performance-measurement foundations required before multiple ships or aviation entities are simulated.

WIP11A is an architectural cleanup. It does not add another live ship, helicopter simulation, gun ammunition, FCS behavior or a new damage model.

## Runtime ownership

| Authority | Owns | Status |
|---|---|---|
| `ACTIVE_SHIP_PROFILE` | immutable DDG-119 configuration | unchanged WIP11 profile |
| `ACTIVE_SHIP_RUNTIME` | navigation, combat-system bindings, weapons, EW, damage/flooding, interior, crew, mass, dynamics and aviation state | canonical |
| `ENGAGEMENT_RUNTIME` | registered ship instances, world entities, terrain, scenario and lifecycle state | canonical |
| legacy globals | compatibility references used by the existing single-file call sites | `COMPAT_REQUIRED` |

The new runtime schema is `AEGIS_SHIP_RUNTIME_V48_WIP11A`; the world schema is `AEGIS_ENGAGEMENT_RUNTIME_V48_WIP11A`. Existing `ACTIVE_SHIP_RUNTIME_V48_WIP09` consumers read the same runtime object, so no second source of truth is introduced.

Friendly SAM/RAM objects receive the active ship entity ID. Hostile and diagnostic ordnance receive explicit force/launcher ownership. Truth arrays remain in the engagement world and are not moved into the ship runtime or track manager.

## Canonical and compatibility cleanup

- `ownshipReference` is the canonical stationary tactical-map anchor. `aircraft` remains a compatibility alias until the remaining old call sites are migrated.
- Live exterior geometry now reads `CANONICAL_SHIP_EXTERNAL_GEOMETRY` directly. The two surviving compacted central-deck objects are authored at their accepted final values and remain in their original array order.
- WIP164/WIP165 geometry and compaction functions remain available only as diagnostic/migration fixtures.
- Canonical API aliases were added for `boundaryMaterialMetrics`, `shipHullContainsPoint` and `shipLocalToWorld`. Archived WIP-named functions remain compatibility aliases.
- `AEGIS_AUTHORITY_MANIFEST_V48_WIP11A` classifies current, compatibility and diagnostic paths. The older `computeSarhIllumQ()` remains a live compatibility/telemetry path; it was not falsely declared dead or removed.

## Registry foundation

`AEGIS_REGISTRY_FACADE_V48_WIP11A` provides common lookup for:

- ship profiles;
- sensor suites;
- VLS weapon descriptors;
- SAM component/loft/6DOF profiles;
- RAM and hostile ASM profiles.

This facade composes the accepted registries. It does not rewrite guidance, radar scheduling or weapon physics.

## Lifecycle contract

The following lifecycle operations are explicit and independently testable:

- `resetEngagementTransientV48Wip11A()`
- `resetShipNavigationV48Wip11A()`
- `resetScenarioWorldV48Wip11A()`
- `resetEntireSessionV48Wip11A()`
- `spawnShipRuntime()`
- `destroyShipRuntime()`

`startNewSea()` and the UI RESET action compose these functions instead of maintaining separate manual reset lists. A spawned secondary runtime is deliberately `UNBOUND`; WIP11A does not place it in the simulation tick. Destroying the active player ship is rejected unless a future authoritative caller explicitly changes that policy.

## Operational-state boundary

Schema: `AEGIS_OPERATIONAL_STATE_V48_WIP11A`

The snapshot preserves:

- navigation and trail state;
- VLS, CIWS and Mk 36 inventories;
- liquid loads;
- module damage;
- flooding cells, openings, doors, pumps and attitude;
- crew casualty, location and treatment state;
- aviation inventory.

Import validates schema version, profile ID, ship ID, navigation and VLS shape. Tracks, plots, airborne ordnance, EW contacts, illuminator reservations and other engagement-transient objects reset on combat entry.

Explicitly deferred from exact restore:

- damage-control fire timeline;
- structural-fatigue history;
- rigid-body rates.

## Update authority and profiler

`AEGIS_SIMULATION_UPDATE_CONTRACT_V48_WIP11A` records the accepted cadence without changing it:

| Subsystem | Cadence |
|---|---:|
| Fixed simulation tick | `60 Hz` |
| Flooding/force integration maximum step | `120 Hz` |
| Hydrostatic quadrature | `20 Hz` |
| Crew movement | `5 Hz` |
| Crew physiology | `1 Hz` |

The opt-in `AEGIS_SUBSYSTEM_PROFILER_V48_WIP11A` records a bounded sample window with average, p95 and maximum milliseconds plus entity counts. It defaults disabled and therefore does not add timing reads to ordinary ticks. No cadence or physics optimization was made in this WIP.

## Diagnostic reliability correction

The SARH/ARH monopulse structural self-test previously inherited the random page seed for its probability-of-detection draw. A rare miss could fail an unrelated browser job. WIP11A assigns deterministic receiver states only to those two self-test fixtures. Live seeker streams and combat probability behavior are unchanged.

## Behavior parity

The WIP11A browser contract loads both WIP11 and WIP11A and compares fixed-seed outputs. The following are exact-equal:

- Kh-35U impact energy, momentum, hull passage, residual energy, openings and rigid-body impulse;
- CIWS fixed-step state, ammunition expenditure, local-track values, projectiles, RNG state and step count.

The WIP11 profile revision, WIP11 material/protection schema, calibrated displacement/GM, 87 physical hitboxes, 138 interior spaces, 160 portals, 70 equipment records and 310-person crew contract remain unchanged.

## Local verification

- Inline JavaScript parse: `PASS`
- Crew, interior, BridgeMaster E, ship-profile, material/protection and WIP11A runtime static contracts: `6/6 PASS`
- WIP11A ownership/lifecycle/snapshot/registry/profiler browser contract: `PASS`
- Full Playwright suite: `17/17 PASS`
- BridgeMaster E repeat check after deterministic self-test correction: `5/5 PASS`
- Multi-view WebGL visual probe: `PASS`
- WebGL console/page errors: `0 / 0`
- Aft geometry, six liferaft contacts, material/protection and 2D drawing audits: `PASS`
- Workflow YAML parse: `PASS` (`18` jobs)

## Artifact

- File: `Aegis_SIM_v48_WIP11A.html`
- Size: `2,724,154 bytes`
- SHA-256: `d18981ca9db5a525417020e5501dce3c638e27cdc97de0f3558fba2e455b1b7a`
- WIP11 baseline SHA-256: `38acac296e67541a9fb6c9b6166f638aac407d73fb63221fe7064b8c9dadfb8a`

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP11A.html`
- WIP10 transition baseline: `archive/v48/WIP10/Aegis_SIM_v48_WIP10.html`
- WIP11 behavior baseline: `archive/v48/WIP11/Aegis_SIM_v48_WIP11.html`
- Expected jobs: `18`
- Added job: `runtime-ownership-wip11a`
- Required final result: `18/18 jobs passed`
- Remote run: pending user upload and PR

## Deferred work

- Existing call sites still use compatibility globals; migrate them incrementally when each subsystem is touched.
- `spawnShipRuntime()` creates identity/ownership state only. Multi-ship scheduling, sensors, collisions, rendering and AI remain WIP14 work.
- The registry facade does not yet move all profile data out of the single HTML source.
- Operational snapshots intentionally do not promise exact mid-tick combat continuation.
- Terrain spatial broad-phase and performance optimization require profiler evidence first.
- WIP12 remains the next feature WIP: gun/projectile terminal effects, fuzes, ricochet, penetration, fragments, blast and material-aware entry/exit damage.

## Repository result

- Root contains only the newest WIP11A simulator, status and checksum set.
- Exact WIP10 and WIP11 artifacts are preserved under `archive/v48/WIP10/` and `archive/v48/WIP11/`.
- Tests target WIP11A; transition and behavior-parity tests read the appropriate archived baselines.
