# AEGIS v48 WIP12D — Kh-32 residual-body overpenetration

## Scope

- Baseline: `archive/v48/WIP12C/Aegis_SIM_v48_WIP12C.html`
- Restore physically meaningful translational motion to large Kh-32 remnants after a functioning detonation.
- Let a perforating but shattered macro fragment continue through later structure while it retains bounded mass, coherence, speed and energy.
- Re-query separated ship geometry after an outside flight, so a residual can re-enter, stop, ricochet or perforate again.
- Turn every perforated physical hull crossing into a real flood-model opening and apply only bounded residual mechanical work.
- Replace a detached explosion sphere with a conserved speed/path-weighted teardrop using the authoritative blast sources.
- Record final exits and bounded presentation-only paths to the sea.
- Make overlapping interior effects readable with an impact-focus view and bounded draw calls.
- Preserve primary legacy ASM authority, scalar blast budget, DUD behavior and combat RNG.
- Apply the final cumulative funnel-length correction to 3D, collision, RCS, interior trunks and 2D indicators, then move the aft-high SPG-62 clear and derive its blind sector from the new taper.

WIP12D does not replay legacy blast/thermal/crew damage or activate a generic fragment packet, surface engagement, gun launch, exterior ballistics, target ships, production heavy-armor solvers, water-entry damage, persistent damage patches or operational-snapshot storage for terminal cascades. It does activate one deduplicated residual supplement limited to capped direct mechanical damage and actual hull openings.

### Funnel and aft SPG-62 geometry

- Forward funnel: `x=3.50…17.10 m`, centre `10.30 m`, half-length `6.80 m`.
- Aft funnel: `x=-18.15…-4.55 m`, centre `-11.35 m`, half-length `6.80 m`.
- The same authority drives the exterior loft/foundation, impact AABB, RCS region, S1–S6 exhaust trunks, side silhouette and 2D top/side indicator.
- The aft-high SPG-62 and pedestal move from `x=-19.7 m` to `x=-20.0 m`.
- Conservative plan clearance is `0.40 m`; tapered-height clearance is `1.4994666667 m`.
- Funnel tangent half-angles are `0° / 48.1796677° / 19.3760505°`; outward-rounded/final forward, aft-high and aft-low masks are `41° / 49° / 54°` after retaining larger pre-existing structural masks.
- This changes real contact geometry, not the legacy penetration formula. Seed `481232` now contacts the extended forward funnel first, so its updated spatial golden intentionally differs from the earlier WIP12D candidate while remaining exact on repeat and RNG-neutral.

## Implemented contracts

### Kh-32 residual motion

- The residual effective-energy ratio is sampled from the existing legacy penetration state at the actual detonation distance.
- Physical pre-detonation kinetic energy is reconstructed as raw entry kinetic energy multiplied by that ratio; speed follows its square root.
- Up to four deterministic macro bodies inherit bounded parent translation plus `2.4%` TNT-equivalent chemical coupling.
- Generation uses the impact-event hash and consumes no combat RNG.
- DUD and non-functioning fuze paths create no macro bodies.

### Perforated-shatter continuation

- `traversalOutcome` and `projectileFailure` remain independent; `PERFORATED + SHATTERED` is valid.
- A terminal outer-shell perforation becomes `TARGET_EXIT` before shattered-projectile termination is considered.
- Opt-in `MACRO_FRAGMENT` bodies can continue after shatter while residual mass is at least `0.12 kg`, coherent mass `0.035 kg`, speed `35 m/s` and kinetic energy `15 kJ`.
- Continuation is limited to six shatter events per body, four bodies per cascade and 128 traversal events per body.
- Thickness/caliber ratio contributes to thin-plate shatter severity.
- Every state or direction change retains WIP12A event-driven geometry re-query.

### Authority and conservation

- Kh-32 authoritative damage remains `LEGACY_ASM_DAMAGE_PATH`.
- Residual cascade authority is `LEGACY_PREACCOUNTED_OBSERVATION_ONLY`; `mergeDamage:false` prevents double application.
- `${impactEventId}:RESIDUAL_SUPPLEMENT` is a separate idempotent event with zero explosive/thermal mass and no legacy blast sources.
- Mechanical damage is capped at `0.16 units/MJ`, `8` per row, `18` per target and `42` total.
- Every perforated sea-boundary crossing is passed to `additionalShellOpenings`; duplicate event IDs are rejected.
- The mass ledger closes parent non-explosive mass into macro and statistical fragment mass.
- The energy ledger records parent kinetic energy, inherited translation, coupled chemical energy, macro kinetic energy and non-negative closure slack.
- Existing WIP12C rare vulnerable-volume ignition policy remains unchanged; inert fragments and structural shock alone do not ignite.

### Exit, re-entry, blast shape and presentation

- Far-hull exits retain position, direction, body axis, hole area, residual mass/coherent mass, speed and kinetic energy.
- Outside-to-inside traversal is limited to three re-entries, eight exterior crossings, `220 m`, `2.5 s` and 512 samples per leg; outside air consumes no penetration energy.
- Every re-entry builds a contact surface from the actual hull or detailed structure space, invokes its material solver and resumes indexed WIP12A traversal from the new state.
- The actual-ship diagnostic proves `EXIT → REENTRY → EXIT` from the forward S5 funnel through a `12.35 m` air gap and the aft S5 funnel, with three positive-area `FUNNEL_SKIN` holes.
- Above-water exits get a precomputed `SEA_ENTRY` display arc; below-water exits get immediate `SUBMERGED_WATER_ENTRY`.
- Post-exit display is capped at `8 s`, `1,800 m` and `18` points and cannot feed back into damage or physics.
- High-speed coherent blast travel produces at least head/peak/tail sources when long enough; source power remains exactly conserved and both damage and 3D consume the same sources.
- The 3D blast is a connected variable-radius teardrop plus core, not a standalone sphere.
- Residual tubes, body markers, exit rings and sea-entry markers appear only in explicit interior view.
- `피격 중심` uses six local clipping planes and object-AABB culling; `전체 내부` restores all detailed compartments.
- Focus selection rebuilds only for an event/damage revision. Flood/fire/smoke overlays use at most three batches.

## Deterministic evidence

The WIP12D browser fixture uses seed `481232` and the live `100 km` Kh-32 scenario.

| Measurement | Result |
|---|---:|
| Hit time | `92.78333333333333 s` |
| Reported impact speed | `991 m/s` |
| Legacy impact energy | `2,849.804054661079 MJ` |
| Primary blast budget / damaged parts | `191 / 17` |
| Teardrop sources / power sum | `3 / 1.0` |
| Leading spatial damage | `제1보일러실 47 / 제1발전실 43` |
| Legacy impact part | `전방연돌` |
| Pre-detonation residual effective energy | `129.38173011895725 MJ` |
| Reconstructed parent speed | `900.1216723041238 m/s` |
| Macro bodies / total mass | `4 / 124.32102720875949 kg` |
| Macro initial kinetic energy | `96.54254026518716 MJ` |
| Shatter continuations | `10` |
| Internal stops / far-hull exits | `2 / 2` |
| Actual residual hull openings | `2` |
| Residual mechanical supplement | `9.343133985302943 units` |
| Surface / submerged water entries | `1 / 1` |
| Mass-closure error | `0 kg` |

Far-hull results were `10.722724034843171 kg @ 1,178.1228847278182 m/s` and `13.136861608517457 kg @ 1,135.2887420868176 m/s`. Same-seed repeat is exact. A DUD produces zero macro bodies and zero exits. This live seed reaches the sea without re-entry; the actual funnel-to-funnel probe covers that branch.

The same seed preserves raw impact energy `2,849.804054661079 MJ`, penetration score `4.318827711120478` and RNG, while the corrected funnel envelope intentionally changes its first contact to `전방연돌`, physical path to `22.52876902577326 m`, budget to `191` and spatial rows to `17` parts headed by `제1보일러실 47` and `제1발전실 43`. This is a geometry/contact-selection delta, not a migration away from the legacy solver.

The flood probe applies a `0.045 m²` submerged opening once, rejects its duplicate, and records `0.06548389609820644 m³` sea inflow after `0.5 s` at approximately `0.13097 m³/s`. It applies mechanical damage without blast replay and leaves burning count and combat RNG unchanged.

## Performance evidence

- WIP12C indexed traversal probe: `256` impacts in `68.7 ms`, or `0.268359375 ms/impact`; maximum two queries on the probed path, `65.9722%` candidate reduction, zero render-frame queries and unchanged combat RNG.
- 3D full-interior scene: `2,342` draw calls.
- 3D impact-focus scene: `298` draw calls, an `87.28%` reduction; more than `1,000` off-focus objects culled.
- Hazard presentation: no more than three batches.

## Diagnostic surface

- `wip12dResidualOverpenetrationContract()`
- `wip12dResidualOverpenetrationDiagnostics()`
- `wip12dResidualEventDiagnostics()`
- `wip12dResidualSupplementProbe()`
- `wip12dShipReentryProbe()`
- `wip12dResidualOverpenetration3DAudit()`
- inherited WIP12A/WIP12B/WIP12C diagnostics

## Local verification

- Inline JavaScript parse: `PASS`
- WIP12D static contract: `36/36 checks PASS`
- WIP12A static contract: `30/30 checks PASS`
- WIP11C wreckage/BDA static contract: `32/32 checks PASS`
- WIP11B runtime-safety static contract: `16/16 checks PASS`
- Static contract files: `11/11 PASS`
- WIP12D browser contract: `2/2 PASS`
- Full Playwright suite: `36/36 PASS` (`32/32` against WIP12D plus archived WIP12B/WIP12C `4/4`)
- Core selftest failures: `0`
- Browser console/page errors: `0 / 0`
- Real Kh-32 legacy golden, same-seed exact repeat, DUD no-cascade and combat-RNG invariance: `PASS`
- Independent perforation/shatter axes, bounded continuation, monotonic boundary state, mass closure and energy bound: `PASS`
- Far-hull exit residual thresholds, surface/submerged water presentation and no render feedback: `PASS`
- Real ship-geometry re-entry, ordered exterior holes, material re-solve, idempotent breach/flood supplement and no generic fire: `PASS`
- Conserved three-source Kh-32 teardrop and matching connected 3D envelope: `PASS`
- Interior-only visibility, depth-independent paths, focus/full restoration, hazard batching and draw-call bound: `PASS`
- Workflow YAML parse: `PASS`, `28` jobs

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP12D.html`
- Historical WIP12B jobs: `archive/v48/WIP12B/Aegis_SIM_v48_WIP12B.html`
- Historical WIP12C jobs: `archive/v48/WIP12C/Aegis_SIM_v48_WIP12C.html`
- New jobs: `residual-overpenetration-wip12d-contract`, `residual-overpenetration-wip12d`
- Expected jobs: `28`
- Required final result before merge: `28/28 jobs passed`
- Branch: `feat/v48-wip12d-kh32-residual-overpenetration`

## Artifact

- File: `Aegis_SIM_v48_WIP12D.html`
- Size: `3,058,349 bytes`
- SHA-256: `8ae85b69e28e71e54137ede0fd6110bbfa358fea7b04c2a88446bf3d44f7a90c`
- Exact WIP12C baseline SHA-256: `55c4c71ee05053820743ae3ce6cdf80cd07b34a92643062309700ff61530567d`

## Deferred work and next handoff

WIP12E is the immediate next step. It should replace the legacy scalar blast redistribution with a bounded compartment/portal pressure-and-impulse solver that distinguishes incident and reflected pressure, positive-phase impulse, blast wind, hot gas, dynamic breaches and exterior venting. It must first run in shadow mode, then become the sole blast authority without replaying the legacy channel. The old Kh-32 scalar budget `191` becomes a calibration comparison rather than an exact post-migration requirement; penetration, fuze location, macro residuals, physical openings, flooding and combat RNG remain regression authorities. The full scope and acceptance contract are recorded in `docs/WIP12E_COMPARTMENT_BLAST_HANDOFF.md`.

WIP13 should follow WIP12E and add a bounded surface-engagement controller that consumes the terminal-event contract for target authorization, anti-ship launch and FCS while retaining the current interceptor fuze and one-authority damage boundaries.

WIP14 remains the target-ship and multi-profile step. Replacement of the primary legacy ASM authority with common packets, production fragment models, water-entry damage, naval-gun operation, persistent patches, heavy armor and snapshot changes remain independent approval points.
