# WIP12B live ordnance terminal effects and damage visualization

Status: implemented and locally verified  
Current source: `Aegis_SIM_v48_WIP12B.html`  
Exact baseline: `archive/v48/WIP12A/Aegis_SIM_v48_WIP12A.html`

## Purpose

WIP12B connects every currently active missile family to the WIP12A terminal-effects contract and makes ship-impact history inspectable in 3D. It does not replace proven combat authorities merely to obtain a common schema.

The integration rule is:

- Kh-32 and Kh-35U keep the exact WIP11B/WIP11C impact, penetration, DUD and damage path.
- SM-2, ESSM and RAM keep their existing flight, target-detection, fragment-Pk and kill-result authority.
- WIP12B observes those already-resolved results and emits one common terminal event for tracing and presentation.
- A separate direct surface-impact entry point uses the WIP12A thin-plate kernel for future limited surface engagement. No surface firing command is enabled in WIP12B.

## Live ordnance registry

| Key | Live authority | Terminal integration | Fuze channels |
|---|---|---|---|
| `KH32` | Legacy ASM impact/damage | Exact compatibility adapter | contact/direct-action, DUD |
| `KH35U` | Legacy ASM impact/damage | Exact compatibility adapter | contact/direct-action, DUD |
| `SM2` | Existing interceptor fragment/Pk | Common terminal event; WIP12A surface-impact resolver available | proximity, contact/direct-action, DUD |
| `ESSM` | Existing interceptor fragment/Pk | Common terminal event; WIP12A surface-impact resolver available | proximity, contact/direct-action, DUD |
| `RAM` | Existing interceptor fragment/Pk | Common terminal event; WIP12A surface-impact resolver available | proximity, contact/direct-action, DUD |

Every entry uses a `TerminalProjectileSpec` with separate total and coherent penetrator masses. The registry does not imply that a whole missile airframe remains a rigid penetrator.

The existing source set establishes a distinct ESSM Block 2 target-detection device but did not establish the exact public identity of its direct-action backup during this pass. That channel is therefore labeled `SIM_WORKING_ASSUMPTION_PUBLIC_IDENTITY_UNRESOLVED`; it is not presented as a newly verified hardware fact. SM-2 and RAM retain their existing source-backed architecture labels while their unpublished numerical behavior remains simulation-tuned.

## Fuze arbitration

The common terminal contract exposes three paths:

- `PROXIMITY`: a valid target-detection event detonates before physical contact;
- `CONTACT_DIRECT_ACTION`: an independent backup fires at a resolved physical contact;
- `DUD`: no blast, warhead-fragment or thermal channel is created.

The earliest valid event wins. A proximity event has no hull boundary result or breach. A direct-action surface event resolves the boundary first and then detonates at that contact under the WIP12A co-timed ordering rule. These contracts are ready for later surface-fire control, but WIP12B does not select a surface target or launch an interceptor at one.

## Damage authority and idempotence

`WIP12B_TERMINAL_EVENTS` is a bounded 32-event transient ledger. Every event carries:

- `impactEventId`, source projectile and target identity;
- coordinate space and reference frame;
- integration mode, fuze path and terminal result;
- `ImpactTrace`, `DamagePacket` or a presentation summary where available;
- the authority that already applied damage.

Duplicate `impactEventId` values resolve to the existing event. Live ASM records are marked `OBSERVED_ALREADY_APPLIED` / `LEGACY_ASM_DAMAGE_PATH`; live interceptor records are marked `EXISTING_INTERCEPT_FRAGMENT_PK`. WIP12B never applies either result a second time and consumes no combat RNG while translating it.

The ledger is an engagement transient. It resets with engagement, session and diagnostic resets and is not added to the operational snapshot. Persistent damage patches remain disabled.

## 3D terminal presentation

Ship-local terminal events create presentation-only objects under the ship root:

- projectile path line;
- boundary-contact and breach markers;
- detonation marker and blast envelope;
- bounded fragment-direction cones.

The renderer reads terminal events but never integrates penetration, fuze, damage or combat state. Target-local air-intercept records remain available for diagnostics but are not incorrectly attached to the own-ship model. The terminal-effect layer and the 2D penetration/blast overlays are visible only while the explicit `내부 구조` inspection mode is active; the external view retains ordinary impact markers without exposing the internal trace.

## Detailed interior damage presentation

The former coarse `COMPARTMENT_INTERIOR_V8` flood-cell boxes are retired. They represented a whole flooding cell as an opaque interior block and could cover the detailed WIP06 compartment model after a hit.

WIP12B instead uses the existing detailed spaces and portals:

- an open damage hole makes the detailed topology layer available through the damaged exterior;
- interior mode makes exterior materials transparent and keeps detailed spaces visible;
- flood, fire and smoke overlays are generated per detailed space from the authoritative interior hazard snapshot;
- detailed space and hazard geometry is subdivided and clipped against the actual tapered hull or upper-structure envelope;
- crew remains visible only in explicit interior mode;
- all hazard and terminal geometry is marked presentation-only with zero physics feedback.

The browser audit represents all `138/138` detailed spaces and reports `0` hull vertices and `0` upper-structure vertices outside the accepted exterior envelope. The former rectangular room and hazard AABBs are therefore no longer allowed to protrude through the ship skin.

## Funnel geometry correction

Both funnels consume `ACTIVE_SHIP_PROFILE.geometry.funnels` as their canonical source:

| Funnel | Aft extension | Forward extension | Final longitudinal bounds |
|---|---:|---:|---:|
| Forward | `1.75 m` | `0.50 m` | `x = 5.25 … 17.10 m` |
| Aft | `1.25 m` | `1.00 m` | `x = -17.65 … -5.80 m` |

Those bounds drive the 3D shell, foundation and cap, physical external hitbox, RCS aim volume, WIP06 exhaust trunks and the top/side 2D indicator correction. The associated SPG-62 blind half-angles are `41°`, `45°` and `54°` for the forward, aft-high and aft-low mounts. Static and live WebGL audits verify the consumer coupling and actual mesh bounds; the browser canvas fixture also verifies that the four extension regions survive the legacy drawing layer and produce visible pixels.

## Diagnostic APIs

- `wip12bTerminalEffectsContract()`
- `wip12bLiveOrdnance()`
- `wip12bResolveSurfaceTerminal()`
- `wip12bTerminalDiagnostics()`
- `wip12bTerminalEvents()`
- `wip12bResetTerminalEvents()`
- `wip12bRecordInterceptorTerminalEffect()`
- `wip12bInteriorHazardPresentationProbe()`
- `wip12bTerminal3DAudit()`
- `wip12bInteriorDamage3DAudit()`
- `wip12bFunnelGeometryAudit()`
- `wip12bFunnelGeometry3DAudit()`

## Deliberately deferred

- surface-target selection, authorization and launch control;
- a live anti-ship mode for SM-2, ESSM or RAM;
- gun launch, turret and magazine operation;
- external ballistics and naval gunfire solution generation;
- migration of Kh-32/Kh-35U away from the exact legacy compatibility path;
- persistent terminal-event or damage-patch snapshot state;
- validated homogeneous or face-hardened armor solvers;
- a new target ship or multi-ship combat runtime.

The next implementation should consume this contract rather than bypass it: a surface-fire controller chooses and authorizes a target, the existing weapon flight model reaches a proximity/contact/DUD terminal event, and only then does the WIP12A/WIP12B pipeline produce the impact trace and damage packet.
