# AEGIS v48 WIP12B — Live ordnance terminal effects and damage visualization

## Scope

- Baseline: `archive/v48/WIP12A/Aegis_SIM_v48_WIP12A.html`
- Register Kh-32, Kh-35U, SM-2, ESSM and RAM under the WIP12A projectile/trace/packet contracts.
- Preserve existing ASM damage and interceptor fragment/Pk outcomes without double application or new combat-RNG consumption.
- Model proximity, contact/direct-action and DUD as explicit terminal paths for all current interceptor families.
- Provide a future surface-impact entry point for limited anti-ship use while leaving target selection, launch authorization and FCS disabled.
- Visualize ship-local penetration paths, contacts, breaches, detonation and fragment direction only while explicit interior inspection is enabled.
- Replace the opaque coarse flooding-cell proxy with detailed WIP06 compartment and per-space hazard presentation.
- Clip detailed spaces and hazards to the physical hull/superstructure envelope so post-hit interior presentation cannot protrude through the exterior.
- Extend both funnels from one canonical contract and propagate the new bounds to 3D, hitboxes, RCS aim volumes, internal trunks, 2D indication and SPG-62 masks.

WIP12B does not activate surface engagement, gun launch, exterior ballistics, a target ship, production heavy-armor solvers, persistent damage patches or operational-snapshot storage for terminal events.

## Implemented contracts

### Live ordnance

`WIP12B_LIVE_ORDNANCE` contains five families:

| Weapon | Integration mode | Terminal paths |
|---|---|---|
| Kh-32 | `LEGACY_ASM_COMPAT` | contact/direct-action, DUD |
| Kh-35U | `LEGACY_ASM_COMPAT` | contact/direct-action, DUD |
| SM-2 | `COMMON_FRAGMENT_TERMINAL_EVENT` | proximity, contact/direct-action, DUD |
| ESSM | `COMMON_FRAGMENT_TERMINAL_EVENT` | proximity, contact/direct-action, DUD |
| RAM | `COMMON_FRAGMENT_TERMINAL_EVENT` | proximity, contact/direct-action, DUD |

All five entries separate `massKg` from `penetratorMassKg`. Kh-32 and Kh-35U retain the exact legacy compatibility adapter. SM-2, ESSM and RAM retain existing flight, target-detector, fragmentation and kill-result authority; WIP12B translates the result after it has already been decided.

The ESSM direct-action backup remains an explicit simulation working assumption because this pass did not establish its exact public identity. It is not silently upgraded to a sourced hardware claim.

### Fuze resolution

`wip12bResolveSurfaceTerminal()` supports deterministic proximity, contact/direct-action and DUD resolution:

- proximity detonates before a hull boundary and creates no breach;
- contact resolves the WIP12A boundary event before co-timed detonation;
- DUD traverses available boundaries/volumes but creates no warhead blast or fragment channels.

This resolver is exposed for diagnostics and later FCS integration. WIP12B does not add a player command, target authorization or live surface firing path.

### Live event bridge

Existing live outcomes emit one `AEGIS_TERMINAL_EVENT_V48_WIP12B` record. A bounded 32-event ledger deduplicates on `impactEventId`, resets with engagement/session lifecycles and is excluded from operational snapshots.

- Normal and DUD Kh-35U/Kh-32 hits are observed after the legacy path applies damage.
- WIP11C residual wreck impacts emit bounded compatibility records.
- SM-2/ESSM/RAM intercept results emit proximity or contact records after existing fragment/Pk resolution.
- No bridge function calls `simRandom()` or `rand()`.

### 3D terminal effects

`get3DRenderState()` exposes `terminalEffectsRevision` and a detached terminal-event snapshot. The renderer creates ship-local path lines, boundary/breach/detonation markers, blast envelopes and fragment cones, but the layer and 2D penetration/blast overlays are visible only in explicit interior mode. Ordinary exterior hit markers remain available. All objects are presentation-only and have no physics feedback.

### Interior visibility bug fix

The opaque coarse `COMPARTMENT_INTERIOR_V8` flooding proxy is disposed and no longer rebuilt. Open damage holes reveal the detailed WIP06 topology, and explicit interior mode makes exterior materials transparent. Detailed room and hazard meshes are tessellated against the physical hull and upper-structure envelopes; the verified topology represents all `138` spaces with `0` outside vertices. Flood, fire and smoke use detailed space IDs instead of whole coarse flood cells. Crew visibility remains tied to explicit interior mode.

### Funnel geometry correction

`ACTIVE_SHIP_PROFILE.geometry.funnels` is the single authority for both funnels. Relative to the previous ends, the forward funnel extends `1.75 m` aft and `0.5 m` forward (`x = 5.25 … 17.10 m`), while the aft funnel extends `1.25 m` aft and `1.0 m` forward (`x = -17.65 … -5.80 m`). The same values drive 3D shells/foundations/caps, external hitboxes, RCS aim volumes, WIP06 exhaust trunks, and the top/side 2D correction overlay. SPG-62 blind half-angles are now `41° / 45° / 54°` for forward, aft-high and aft-low mounts.

## Diagnostic surface

- `wip12bTerminalEffectsContract()`
- `wip12bLiveOrdnance()`
- `wip12bResolveSurfaceTerminal()`
- `wip12bTerminalDiagnostics()`
- `wip12bTerminalEvents()` / `wip12bResetTerminalEvents()`
- `wip12bRecordInterceptorTerminalEffect()`
- `wip12bInteriorHazardPresentationProbe()`
- `wip12bTerminal3DAudit()`
- `wip12bInteriorDamage3DAudit()`
- `wip12bFunnelGeometryAudit()`
- `wip12bFunnelGeometry3DAudit()`

## Local verification

- Inline JavaScript parse: `PASS`
- WIP12B static contract: `29/29 checks PASS`
- WIP12A static contract against the archived WIP11C authority: `30/30 checks PASS`
- WIP11C wreckage/BDA static contract: `32/32 checks PASS`
- WIP11B import-safety and WIP11 material/protection static contracts: `PASS`
- Crew, interior, BridgeMaster E and ship-profile static contracts: `PASS`
- WIP12B browser contract: `2/2 PASS`
- Full Playwright suite: `32/32 PASS` using the local Three.js dependency path
- WIP12A browser regression: `2/2 PASS`
- Five live families and separated total/penetrator mass: `PASS`
- SM-2/ESSM/RAM proximity, contact/direct-action and DUD registry paths: `PASS`
- Contact-before-co-timed-detonation, proximity-before-boundary and DUD-without-warhead-effect: `PASS`
- Duplicate event suppression and reset behavior: `PASS`
- Live normal/DUD ASM result observation with no second damage application: `PASS`
- Existing ASM compatibility output and combat RNG parity: `PASS`
- Open damage, coarse proxy retirement, detailed topology visibility and per-space flood/fire/smoke clipping: `PASS`
- Detailed topology spaces: `138/138`; hull/superstructure outside vertices: `0 / 0`
- One ship-local terminal event rendered as one path plus four contact/effect markers: `PASS`
- Terminal path/blast hidden outside interior mode and visible inside it: `PASS`
- Interior-mode exterior transparency: `PASS`
- Canonical funnel authority and actual 3D bounds, hitbox/RCS/trunk/SPG coupling plus visible 2D extension pixels: `PASS`
- WIP12B browser console/page errors: `0 / 0`

The full suite includes existing CIWS, Kh-32/ESSM ghost-track and BDA, wreckage/water effects, ship mass, impact, structure, stability, flooding, interior, crew, material, runtime import-safety and 3D geometry regressions.

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP12B.html`
- WIP12A exact baseline: `archive/v48/WIP12A/Aegis_SIM_v48_WIP12A.html`
- New jobs: `live-terminal-effects-wip12b-contract`, `live-terminal-effects-wip12b`
- Expected jobs: `24`
- Required final result before merge: `24/24 jobs passed`
- Branch: `feat/v48-wip12b-live-ordnance-visualization`

## Artifact

- File: `Aegis_SIM_v48_WIP12B.html`
- Size: `2,930,747 bytes`
- SHA-256: `61dfcff533f7708df65e1939e3f5cd10448a6492ed0903b4dc2f17af50663f91`
- Exact WIP12A baseline SHA-256: `60705246ef0b659dadf67e23ca9b84bf7dc2cb477857d9714223291c564c3729`

## Deferred work and next handoff

WIP13 should add a bounded surface-engagement controller that consumes the WIP12B terminal contract. The recommended first slice is limited surface-target authorization and launch plumbing for current interceptors, with deterministic fixtures and no new target ship. Naval-gun launch/FCS should be admitted only under a separately fixed scope.

WIP14 remains the target-ship and multi-profile combat step. Kh-32/Kh-35U solver migration, persistent damage patches, production heavy armor and operational-snapshot changes remain independent approval points.
