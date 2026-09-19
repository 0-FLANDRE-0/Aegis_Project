# WIP12C internal terminal effects and residual bodies

Status: implemented and locally verified  
Current source: `Aegis_SIM_v48_WIP12C.html`  
Exact baseline: `archive/v48/WIP12B/Aegis_SIM_v48_WIP12B.html`

## Purpose

WIP12C extends the WIP12A/WIP12B terminal contract beyond the parent projectile. A functioning internal detonation can create a small, bounded set of coherent residual bodies. Each body continues through the same event-driven boundary/empty-space/equipment-volume traversal as any other WIP12A projectile and may perforate the far hull.

This is not a thousands-of-fragments particle simulation. Fine fragments remain a statistical damage channel. Only fragments large enough to matter as coherent penetrators become explicit `MACRO_FRAGMENT` bodies.

## Authority rules

| Path | Cascade authority | Damage application |
|---|---|---|
| New/common WIP12A projectile | `COMMON_PACKET_SINGLE_APPLICATION` | Child channels are flattened into the parent packet and committed once |
| Diagnostic 127 mm SAP fixture | `DIAGNOSTIC_COMMON_PACKET` | Same common path, with deterministic geometry and targets |
| Live Kh-32/Kh-35U legacy ASM | `LEGACY_PREACCOUNTED_OBSERVATION_ONLY` | Existing legacy damage remains authoritative; cascade is recorded without a second commit |
| DUD | `NO_FUNCTIONING_DETONATION` | No detonation cascade or macro-body generation |

The legacy observation rule is deliberate. WIP12C may show how large residual bodies would traverse the ship, but it does not silently replace or add to the validated Kh-32/Kh-35U damage result. Migrating that authority requires a separate parity decision.

## Deterministic cascade

`WIP12C_INTERNAL_EFFECTS_CONTRACT` fixes these bounds:

- maximum explicit bodies: `4`;
- minimum body mass: `0.12 kg`;
- minimum body energy: `1,200 J`;
- coordinate space: `SHIP_LOCAL_METRES`;
- fine fragments: `STATISTICAL_DAMAGE_CHANNEL`;
- randomness: event-ID hashing only; no `simRandom()`, `rand()` or `Math.random()` calls.

The pre-detonation projectile state is preserved before WIP12A zeroes speed, integrity and coherent mass at detonation. Macro-body planning uses that state plus the fixed projectile specification. Each child receives its own mass, coherent mass, velocity direction, body axis, integrity, equivalent caliber and inert/no-fuze specification.

Every child calls `wip12aTraceTerminalProjectile()` independently. Geometry is queried again after every contact, so deflection or ricochet changes subsequent contacts. Empty space advances time without resistance; actual equipment volumes and plate boundaries consume state. A body can stop at any internal boundary or inside a material volume, and a far-side opening exists only after the actual outer shell is perforated.

## Mass and energy bookkeeping

The cascade ledger records:

- parent non-explosive mass;
- explicit macro-body mass;
- remaining statistical fragment mass;
- mass closure error;
- parent pre-detonation kinetic energy;
- bounded coupled chemical energy;
- initial macro-body kinetic energy;
- non-negative energy closure slack.

The enforced diagnostics are:

`macro mass + statistical fragment mass = parent non-explosive mass`

and

`macro kinetic energy <= parent kinetic energy + coupled chemical energy`.

This ledger is diagnostic bookkeeping, not a claim of high-fidelity explosive-fragment distribution data.

## Combined DamagePacket

For the common path, child results are flattened into the original parent `DamagePacket`:

- `penetrationCorridors`;
- direct penetration;
- plug and rear spall;
- statistical warhead fragments;
- blast;
- thermal/incendiary effect;
- breaches and far-hull exits;
- structural impulse;
- crew exposure;
- diagnostic patch proposals.

`wip12aApplyDamagePacket()` commits the combined packet exactly once. The existing `impactEventId` guard rejects a second commit. Flooding receives all penetration lines and all new shell openings in one event; crew exposure evaluates all corridors without treating people as ballistic resistance. Fire initiation follows the explicit ignition policy below instead of treating generic damage or structural impulse as fire.

The byte-preserved `damageFloodImpactV1()` remains the legacy ASM entry point. WIP12C common packets use `damageFloodImpactV48Wip12C()` so multi-corridor support cannot perturb legacy results or combat RNG order.

## Physical ship traversal

The ship adapter uses the existing detailed topology as an impact-time material map:

- `138` detailed spaces are cached once and indexed in `10 m` longitudinal bins;
- `70` equipment nodes and `8` inset tank contents form `78` material-filled damage volumes;
- crew occupancy remains a separate, zero-resistance exposure volume;
- boundary material is selected from the local role: light partition, watertight machinery boundary, fire bulkhead, internal deck, magazine, hangar, superstructure shell, upper shell, waterline shell or bottom/bilge shell;
- an open door or aperture has zero plate work, state loss, spall and hole creation;
- nearly coincident room faces are resolved as one shared boundary instead of two invented plates;
- the tapered hull/superstructure exit and its local normal are recomputed from the current position and direction after every deflection.

Static arrays are not pre-sorted into one final path. WIP12A event providers return only the next relevant detailed boundary, damage volume and outer-shell event. A perforated boundary marked `terminalExit` ends traversal as `TARGET_EXIT`; otherwise the updated projectile state is used for another indexed query. Low-energy probes demonstrably stop at the first internal structure without creating a far-hull breach.

A far-hull perforation records the body ID, ship-local exit position, opening area, residual speed and residual mass. It becomes both a breach channel entry and an interior-mode exit marker. The thin-plate result also clamps post-impact speed to the incoming speed, preventing a mass-loss calculation from numerically accelerating the remaining body.

## Fire and ignition policy

Non-explosive penetration is not a generic fire source. The WIP12C contract fixes:

- generic impact ignition: disabled;
- structural impulse ignition: disabled;
- inert plate, plug and fragment impact: zero ignition probability by itself;
- explosive blast: explicit ignition candidate only in the detonation cell;
- thermal/incendiary payload: explicit ignition candidate;
- mechanical ignition: considered only when the path actually crosses a vulnerable material-filled `DAMAGE_VOLUME`.

Mechanical ignition uses an event-ID hash, deposited energy and impact speed. It consumes no combat RNG and is capped before those energy/speed factors are applied:

| Vulnerability class | Maximum probability per actual volume hit |
|---|---:|
| Fuel/lubricant | `1.8%` |
| Aviation fuel | `1.4%` |
| Electrical | `0.8%` |
| Ordnance | `0.6%` |
| Inert structure/equipment | `0%` |

Individual volumes may declare a lower cap. The boiler-room fixture, for example, uses a `1.2%` declared cap and produces a `0.7510648%` probability for its measured energy/speed case. This keeps a rare secondary-fire possibility when a vulnerable module is physically hit without allowing ordinary fragments, hull shock or a non-explosive breach to light compartments routinely.

## Performance bounds

- Traversal runs only when an impact or explicit residual body is resolved; it is not a per-tick or render-frame scan.
- The cached bins restrict each dynamic query to nearby detailed spaces and material volumes.
- Each body is bounded to `80 m` of path and `128` events.
- The cascade creates at most four coherent bodies; fine fragments stay statistical.
- Rendering consumes completed trace data and performs zero geometry queries.

The final local `512`-impact benchmark completed in `137.8 ms` total (`0.2691 ms/impact`), with at most `2` terminal queries for the benchmark path, `65.9975%` candidate reduction, unchanged combat RNG and `0` render-frame queries. These are regression measurements on the verification environment, not a universal hardware performance guarantee.

## Presentation split

WIP12C intentionally separates two views:

| View | Coarse flooding compartments | Detailed 138-space topology/hazards/crew | Terminal paths/blast/macro bodies |
|---|---|---|---|
| Exterior with an open breach | Visible through the breach | Hidden | Hidden |
| Explicit `내부 구조` mode | Hidden | Visible | Visible |

The explicit interior mode makes exterior materials transparent. Detailed spaces and hazards remain clipped to the accepted hull/superstructure envelope. The terminal layer adds:

- parent projectile path;
- boundary, breach and detonation markers;
- blast envelope and statistical fragment cones;
- `TERMINAL_MACRO_PATH` lines;
- `TERMINAL_MACRO_BODY` markers;
- `TERMINAL_MACRO_EXIT` far-hull exit rings.

All of these are presentation-only. Opening or rendering the 3D view does not advance terminal physics or consume combat RNG.

## Deterministic fixture result

Seed `481230` and `TEST_127_SAP` produce:

- root penetration corridor: `1`;
- explicit macro bodies: `3`;
- far-hull exits: `3`;
- parent non-explosive mass: `28.555921620245115 kg`;
- macro mass: `14.588443007487754 kg`;
- statistical fragment mass: `13.967478612757361 kg`;
- mass closure error: `0 kg`;
- macro initial kinetic energy: `5,253,032.218587705 J`;
- energy closure slack: `5,907,267.80442904 J`.

The combined packet creates five breach entries, reaches registered ship targets, produces four crew penetration corridors including the parent path, and is rejected on duplicate application.

## Diagnostic APIs

- `wip12cInternalEffectsContract()`
- `wip12cRunFixture()`
- `wip12cInternalEffectsDiagnostics()`
- `wip12cInternalEffects3DAudit()`
- `wip12cShipTraversalProbe()`
- `wip12cShipTraversalPerformance()`
- `wip12cIgnitionPolicyDiagnostics()`
- `wip12cMechanicalIgnitionApplicationProbe()`
- existing WIP12A trace/packet and WIP12B terminal-event diagnostics

## Deliberately deferred

- surface-target selection, authorization and launch control;
- gun launch, turret, magazine and exterior ballistics;
- production empirical fragment distributions;
- migration of Kh-32/Kh-35U damage authority to the common solver;
- persistent damage-patch accumulation;
- operational-snapshot storage for terminal events or cascades;
- validated homogeneous or face-hardened armor solvers;
- a target ship or multi-ship combat runtime.

The next implementation may consume these terminal results for limited surface engagement, but it must not bypass the one-packet authority or turn presentation objects into physics state.
