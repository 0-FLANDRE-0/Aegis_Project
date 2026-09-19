# AEGIS v48 WIP12C — Internal terminal effects and residual bodies

## Scope

- Baseline: `archive/v48/WIP12B/Aegis_SIM_v48_WIP12B.html`
- Resolve internal detonation, multi-corridor damage and bounded coherent residual bodies through the WIP12A kernel.
- Let large residual bodies cross equipment, bulkheads and the far hull while keeping fine fragments statistical.
- Preserve exact Kh-32/Kh-35U legacy damage and combat-RNG authority without double application.
- Restore coarse flooding compartments for exterior breach views.
- Show detailed spaces, hazards, crew, parent penetration, blast and macro-body paths only in explicit interior inspection.

WIP12C does not activate surface engagement, gun launch, exterior ballistics, a target ship, production heavy-armor solvers, persistent damage patches or operational-snapshot storage for terminal cascades.

## Implemented contracts

### Internal cascade

- A functioning detonation can generate at most four deterministic `MACRO_FRAGMENT` children.
- Event-ID hashing supplies deterministic direction, mass and energy allocation without consuming combat RNG.
- Pre-detonation state is preserved before the parent is zeroed at detonation.
- Every child is an inert WIP12A projectile with independent mass, coherent mass, integrity, direction and body axis.
- Every child uses event-driven traversal and re-queries geometry after state or direction changes.
- DUD and non-functioning fuze paths generate no cascade.

### Conservation diagnostics

- Parent non-explosive mass is divided between explicit macro bodies and statistical fine fragments.
- The fixture enforces zero mass-closure error.
- Macro-body kinetic energy is bounded by parent kinetic energy plus a limited coupled chemical-energy budget.
- The ledger records energy slack instead of silently creating energy.

### Detailed material traversal and bounds

- Impact-time providers query the next detailed boundary, material volume and outer-shell exit after every direction/state change; an initial straight-line candidate list is never treated as the final path.
- The cached ship material map contains `138` detailed spaces and `78` material volumes (`70` equipment nodes plus `8` inset tank volumes), indexed in `10 m` longitudinal bins.
- Local boundary roles select distinct material profiles for machinery watertight boundaries, light partitions, fire bulkheads, decks, magazines, hangars, superstructure and hull shell regions.
- Open portals are genuine zero-resistance apertures. They create no plate loss, spall or new hole.
- The tapered hull exit and local surface normal are recomputed dynamically. Perforating a terminal outer shell ends traversal as `TARGET_EXIT`; a body with insufficient state stops internally with no far-side breach.
- Post-impact speed cannot exceed pre-impact speed, even when projectile mass is shed.
- Each body is bounded to `80 m` and `128` events. Queries occur only at impact time, never during render frames.

### Damage authority

- Common children flatten their corridors and damage channels into the parent `DamagePacket`.
- The parent packet is applied once; duplicate `impactEventId` is rejected.
- Flooding accepts multiple penetration lines and additional far-hull openings in one idempotent event.
- Crew damage evaluates all penetration corridors while crew occupancy remains zero-resistance geometry.
- Thermal/incendiary and explosive detonation candidates reach the existing fire consumer explicitly.
- The original `damageFloodImpactV1()` remains byte-exact for legacy ASM use.
- Live Kh-32/Kh-35U cascades use `LEGACY_PREACCOUNTED_OBSERVATION_ONLY` and never commit a second damage packet.

### Ignition policy

- Generic impact damage and structural impulse cannot start a fire.
- Inert hull, bulkhead, plug and non-explosive fragment effects have zero ignition probability by themselves.
- Mechanical ignition is evaluated only on an actual hit to a vulnerable material-filled volume and uses deterministic event-ID hashing rather than combat RNG.
- Class caps are fuel/lubricant `1.8%`, aviation fuel `1.4%`, electrical `0.8%`, ordnance `0.6%` and inert `0%`; individual volumes may lower the cap further.
- Deposited energy and impact speed scale the already-small cap. The verified boiler-room case had a `0.7510648%` chance and ignited only for its selected deterministic event ID.
- Explosive blast is scoped to its detonation cell; thermal/incendiary payload remains a direct ignition source.

### Presentation

- Exterior breach view rebuilds `COMPARTMENT_INTERIOR_V8` coarse flooding compartments and clips visibility through open damage.
- Explicit interior mode hides that coarse layer and shows the detailed 138-space topology, per-space hazards and crew.
- Exterior materials become transparent only in explicit interior mode.
- Parent paths, detonation/blast, macro-body paths, body markers and far-hull exit markers are visible only in explicit interior mode.
- Renderer state is presentation-only and has no terminal-physics or RNG feedback.

## Deterministic evidence

The WIP12C browser fixture uses seed `481230` and `TEST_127_SAP`.

| Measurement | Result |
|---|---:|
| Root corridor | `1` |
| Macro bodies | `3` |
| Far-hull exits | `3` |
| Combined breach rows | `5` |
| Parent non-explosive mass | `28.555921620245115 kg` |
| Macro mass | `14.588443007487754 kg` |
| Statistical fragment mass | `13.967478612757361 kg` |
| Mass closure error | `0 kg` |
| Macro initial kinetic energy | `5,253,032.218587705 J` |
| Energy closure slack | `5,907,267.80442904 J` |

The committed packet produces one flooding event and one crew-damage event, reaches four penetration lines including the root path, creates fire state, and rejects the second application as `DUPLICATE_IMPACT_EVENT`.

The live Kh-35U normal-impact probe retains legacy authority while recording four macro bodies and zero far-hull exits: the detailed material path stops those particular bodies before the opposite shell. Its DUD probe records zero bodies and zero exits. Both report unchanged combat RNG state.

The detailed traversal probe crosses a `WATERTIGHT_MACHINERY` boundary and a locally normalled `SHELL_WATERLINE` far hull, while its low-speed companion stops at the internal structure and creates no exit. The material-volume probe crosses `1.612168 m` of boiler equipment and drops from `1200` to `1198.087 m/s`.

The final `512`-impact performance probe measured `137.8 ms` total (`0.2691 ms/impact`), no more than `2` terminal queries on that path, `65.9975%` candidate reduction, zero render-frame queries and unchanged combat RNG. The saturated fuel/lubricant diagnostic ignited `57/4096` deterministic samples (`1.3916%`), below the `1.8%` hard cap; inert and shock-only probes ignited none.

## Diagnostic surface

- `wip12cInternalEffectsContract()`
- `wip12cRunFixture()`
- `wip12cInternalEffectsDiagnostics()`
- `wip12cInternalEffects3DAudit()`
- `wip12cShipTraversalProbe()`
- `wip12cShipTraversalPerformance()`
- `wip12cIgnitionPolicyDiagnostics()`
- `wip12cMechanicalIgnitionApplicationProbe()`
- WIP12A trace, packet and legacy-parity diagnostics
- WIP12B live-event, fuze and 3D presentation diagnostics

## Local verification

- Inline JavaScript parse: `PASS`
- WIP12C static contract: `40/40 checks PASS`
- Static contract files: `10/10 PASS`
- WIP12A static contract: `30/30 PASS`
- WIP11C wreckage/BDA static contract: `32/32 PASS`
- WIP12C browser contract: `2/2 PASS`
- WIP12A active-source browser regression: `2/2 PASS`
- Archived WIP12B browser regression: `2/2 PASS`
- Full Playwright suite: `34/34 PASS` using both local Three.js compatibility variable names
- Core selftest failures: `0`
- WIP12C browser console/page errors: `0 / 0`
- Deterministic repeat, bounded child count, common child traversal and combat-RNG invariance: `PASS`
- Mass closure, energy bound, far-hull exits and combined packet single application: `PASS`
- Detailed material traversal, dynamic local hull exit, internal stop and no-speed-creation invariants: `PASS`
- Indexed `512`-impact performance, zero render-frame queries and combat-RNG invariance: `PASS`
- Multi-path flooding/crew, explicit explosive/thermal ignition, rare vulnerable-module mechanical ignition and inert no-fire policy: `PASS`
- Legacy normal-hit observation-only and DUD no-cascade behavior: `PASS`
- Exterior coarse/detailed interior split and terminal-effect interior-only visibility: `PASS`
- Detailed topology: `138/138`; hull/superstructure outside vertices: `0 / 0`
- Rendered macro paths/bodies/exits exactly match source event counts: `PASS`

The first local full-suite attempt passed `32/34`; its two failures were 3D readiness timeouts because those historical tests read `THREE_JS_LOCAL` while only `THREE_LOCAL_FILE` was supplied. Both tests passed immediately with the correct compatibility variable, and the final complete run supplied both variables and passed `34/34`.

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP12C.html`
- Historical WIP12B jobs: `archive/v48/WIP12B/Aegis_SIM_v48_WIP12B.html`
- New jobs: `internal-terminal-effects-wip12c-contract`, `internal-terminal-effects-wip12c`
- Expected jobs: `26`
- Required final result before merge: `26/26 jobs passed`
- Branch: `feat/v48-wip12c-internal-effects-residual-bodies`

## Artifact

- File: `Aegis_SIM_v48_WIP12C.html`
- Size: `2,989,191 bytes`
- SHA-256: `55c4c71ee05053820743ae3ce6cdf80cd07b34a92643062309700ff61530567d`
- Exact WIP12B baseline SHA-256: `61dfcff533f7708df65e1939e3f5cd10448a6492ed0903b4dc2f17af50663f91`

## Deferred work and next handoff

WIP13 should add a bounded surface-engagement controller that consumes the WIP12C terminal contract for target authorization, launch and FCS. It must keep current interceptor flight/fuze authority and the one-packet damage boundary.

WIP14 remains the target-ship and multi-profile combat step. Kh-32/Kh-35U migration from observation-only residual cascades to authoritative common damage, naval-gun operation, production fragment models, persistent patches, heavy armor and snapshot changes remain independent approval points.
