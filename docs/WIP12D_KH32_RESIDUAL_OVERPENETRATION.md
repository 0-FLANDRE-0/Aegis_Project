# WIP12D Kh-32 residual-body overpenetration

## Purpose

WIP12D corrects the WIP12C observation-only cascade for a high-speed Kh-32 hit. A functioning Kh-32 detonation can leave a small, bounded set of large casing or airframe remnants with substantial translational velocity. Those remnants now keep moving through the WIP12A event-driven terminal-ballistics kernel, can perforate and shatter at the same boundary, can be stopped by internal structure, can leave and re-enter separated hull or superstructure regions, and can finally enter the sea.

The existing WIP11B/WIP11C Kh-32 impact path remains the primary authority. WIP12D does not replay its blast, thermal or crew effects: the residual cascade stays `LEGACY_PREACCOUNTED_OBSERVATION_ONLY` with `mergeDamage:false`. It now has one deliberately narrow, idempotent supplement for physical residual-body consequences only: bounded direct mechanical damage and every perforated sea-boundary opening. The user-requested path-shaped blast keeps the legacy scalar damage budget but intentionally changes its spatial distribution, so spatial damage rows are no longer claimed byte-for-byte identical to WIP12C.

## Authority and scope

- A live Kh-32 hit still uses `LEGACY_ASM_PENETRATION_COMPAT` for authoritative damage.
- WIP12D never reapplies the legacy blast or generic fragment packet. A separate `${impactEventId}:RESIDUAL_SUPPLEMENT` event applies only capped mechanical work and real shell openings.
- A DUD creates no detonation cascade.
- Residual generation uses an event-ID hash and consumes no combat RNG.
- Outside flight is solved only at impact time. A body can re-enter real indexed ship geometry; only the final exit-to-water arc is presentation-only.
- Rendering cannot change physics, damage, flooding or RNG.
- The active common-kernel extension is opt-in and limited to `terminal.modelFamily === 'MACRO_FRAGMENT'`; ordinary WIP12A projectiles retain their previous shatter behavior.

WIP12D does not claim a production fragment distribution or exact classified Kh-32 breakup model. Fragment counts, energy coupling and strength values are deterministic `SIM_TUNED` validation parameters constrained by mass, energy and runtime budgets.

## Funnel geometry correction

The cumulative user-directed funnel bounds are authoritative in `ACTIVE_SHIP_PROFILE.geometry.funnels`:

| Structure | Aft bound | Forward bound | Centre | Half-length |
|---|---:|---:|---:|---:|
| Forward funnel | `3.50 m` | `17.10 m` | `10.30 m` | `6.80 m` |
| Aft funnel | `-18.15 m` | `-4.55 m` | `-11.35 m` | `6.80 m` |

The same bounds drive the 3D loft and foundation, exterior impact AABB, RCS aim region, S1–S6 exhaust trunks, side silhouette and 2D top/side damage indicator. The aft-high SPG-62 and its pedestal move `0.30 m` aft to `x=-20.0 m`. This leaves `0.40 m` in the deliberately conservative full-footprint plan projection and `1.4994666667 m` between the physical SPG hitbox and the tapered funnel at their overlapping height.

The blind sector is not eyeballed. At each SPG height, the audit interpolates the funnel's longitudinal face and half-width and computes its azimuth tangent. The aft-high result is `48.1796677°`, rounded outward to `49°`; the aft-low funnel tangent is only `19.3760505°`, so its existing `54°` structural mask remains dominant. Final forward/aft-high/aft-low blind half-angles are therefore `41° / 49° / 54°`.

This is a real collision-geometry change. The legacy ASM formula and RNG authority remain untouched, but a path intersecting the newly extended funnel can select a different first contact and therefore a different spatial damage result. Seed `481232` now strikes the forward funnel first; the updated golden below records that intentional geometry delta.

## Recovering pre-detonation motion

The legacy Kh-32 trace correctly zeroes its projectile state after detonation. WIP12C consequently observed zero post-detonation parent speed, which made every generated macro body stop or shatter before a meaningful far-hull exit.

WIP12D samples the legacy residual effective energy at the actual detonation distance and reconstructs a physical pre-detonation state without changing the legacy damage calculation:

\[
r_E = \operatorname{clamp}\left(\frac{E_{\text{legacy,residual}}}{E_{\text{legacy,entry}}},0,1\right)
\]

\[
E_{\text{physical,det}} = E_{\text{raw,entry}}r_E,\qquad
v_{\text{det}} = v_{\text{entry}}\sqrt{r_E}
\]

The explicit macro bodies inherit bounded translational energy from this velocity. Their total initial kinetic budget is:

\[
E_{\text{macro}} \leq E_{\text{inherited translation}} + 0.024E_{\text{TNT}}
\]

with a `0.92` translational-retention factor. The ledger records parent kinetic energy, inherited translation, coupled chemical energy, macro initial energy and non-negative closure slack.

## Independent perforation and projectile failure

Traversal outcome and projectile failure remain separate axes. In particular, the following is valid and expected:

- `traversalOutcome: PERFORATED`
- `projectileFailure: SHATTERED`

A perforating macro fragment can therefore shed most of its mass and coherence yet continue as a smaller residual chunk. Continuation is permitted only when all thresholds remain satisfied:

| Limit | Value |
|---|---:|
| Maximum macro bodies per cascade | `4` |
| Maximum shatter continuations per body | `6` |
| Minimum residual mass | `0.12 kg` |
| Minimum coherent mass | `0.035 kg` |
| Minimum residual speed | `35 m/s` |
| Minimum residual kinetic energy | `15,000 J` |
| Maximum traversal events per body | `128` |

Thin-plate shatter severity also includes the plate-thickness/projectile-caliber ratio. Far-hull exit is resolved immediately after a perforation, before a shattered result is considered an internal termination. Every direction change still causes a fresh geometry query.

## Exit, re-entry, real breaches and sea entry

After each perforated exterior crossing, the body state is advanced outside the ship with gravity and zero material resistance. The bounded impact-time search then selects the earliest sea entry or real ship-envelope re-entry. Re-entry creates a new material surface at the contact point and invokes the normal WIP12A solver; the body can perforate, ricochet, stop or shatter there. Limits are three re-entries, eight exterior crossings, `220 m`, `2.5 s` and 512 outside samples per leg.

The actual-geometry diagnostic leaves the forward S5 funnel, crosses `12.35 m` of outside air, re-enters the aft S5 funnel and exits again. Its ordered roles are `EXIT → REENTRY → EXIT`; all three contacts use `FUNNEL_SKIN`, consume energy and produce an independent positive-area hole record.

Each valid far-hull exit records:

- body ID and exit surface ID;
- ship-local exit position, velocity direction and body axis;
- residual mass, coherent mass, speed and kinetic energy;
- exit-hole area.

Every perforated physical hull crossing becomes an `additionalShellOpening` in the existing flood model. Openings use their actual position, normal and area, so submerged or wave-wet holes admit water and can propagate the existing flooding, stability and structural consequences. The supplement is deduplicated by event ID. Its mechanical damage is capped at `0.16 units/MJ`, `8` per row, `18` per target and `42` total; explosive mass, thermal mass and legacy blast sources are all zero in this pass.

After the final exit, an above-water body receives a bounded ballistic display arc to the sea plane. A body already below the waterline receives an immediate `SUBMERGED_WATER_ENTRY`. Arcs are limited to `8 s`, `1,800 m` and `18` points and are never integrated during a render frame. WIP12D does not add water-entry shock or underwater damage.

## Velocity-shaped blast envelope

The authoritative WIP101 conservative chain-blast source builder now retains at least a head, velocity-weighted peak and tail sample when a sufficiently fast projectile has at least `0.75 m` of coherent post-fuze travel. Slow or effectively stationary detonations still collapse toward one spherical source.

- Source power fractions sum to exactly `1`.
- Radius follows each source's cube-root power share.
- The damage consumer uses these same sources; the 3D view renders a connected variable-radius teardrop from them instead of inventing a separate sphere.
- The damage consumer preserves the scalar budget produced by the legacy path; no blast is replayed by the residual supplement.

## Interior presentation and performance

Residual paths, final body markers, far-hull exit rings and sea-entry markers appear only in explicit `내부 구조` view. Macro paths use depth-independent tubes so they remain readable amid overlapping compartments.

The new `피격 중심` mode combines six ship-local clipping planes with object-AABB culling around the latest impact. `전체 내부` restores the complete model. Focus selection is rebuilt only when the impact event or damage revision changes; ship motion updates plane placement without walking the entire scene graph again.

Flood, fire and smoke interior overlays are emitted in at most three geometry batches. In the deterministic 3D fixture, the same scene measured `2,342` draw calls in full-interior mode and `298` in impact-focus mode, an `87.28%` reduction. This is a rendering optimization only.

## Deterministic Kh-32 evidence

The browser fixture uses seed `481232` and a `100 km` Kh-32 case. Its golden intentionally includes the corrected forward-funnel collision envelope.

| Measurement | Result |
|---|---:|
| Hit time | `92.78333333333333 s` |
| Reported impact speed | `991 m/s` |
| Raw impact kinetic energy | `2,849.804054661079 MJ` |
| Legacy penetration score | `4.318827711120478` |
| Physical path length | `22.52876902577326 m` |
| Pre-detonation residual effective energy | `129.38173011895725 MJ` |
| Reconstructed parent kinetic energy | `2,349.6351723595605 MJ` |
| Reconstructed parent speed | `900.1216723041238 m/s` |
| Conserved primary blast damage budget | `191` |
| Spatially damaged parts after teardrop distribution | `17` |
| Blast source nodes / power sum | `3 / 1.0` |
| Macro bodies | `4` |
| Total macro mass | `124.32102720875949 kg` |
| Macro initial kinetic energy | `96.54254026518716 MJ` |
| Shatter-continuation events | `10` |
| Internal stops | `2` |
| Far-hull exits | `2` |
| Actual residual shell openings | `2` |
| Residual mechanical supplement | `9.343133985302943 units` |
| Sea entries | `2` |

The two far-hull residuals are:

| Residual mass | Exit speed | Exit kinetic energy | Water result |
|---:|---:|---:|---|
| `10.722724034843171 kg` | `1,178.1228847278182 m/s` | `7.441428573074592 MJ` | `SEA_ENTRY` |
| `13.136861608517457 kg` | `1,135.2887420868176 m/s` | `8.465922562527178 MJ` | `SUBMERGED_WATER_ENTRY` |

Two residuals terminate internally after shatter and two perforate the opposite shell to create real openings. One exit is above water and one is already submerged. Repeating the seed produces an exact diagnostic match, and the combat RNG state is unchanged. This particular live seed has no re-entry because both exit vectors reach the sea first; the real forward-funnel-to-aft-funnel probe covers the re-entry branch.

The teardrop distribution retains total damage `191` across `17` parts. The leading rows are `제1보일러실 47` and `제1발전실 43`. This spatial change is intentional and replaces the old one-sphere distribution rather than claiming parity for per-part rows.

The isolated submerged-hole probe registers a `0.045 m²` opening. After `0.5 s`, it admits `0.06548389609820644 m³` of seawater at approximately `0.13097 m³/s`; replaying the same supplement event is rejected and starts no fire.

## Fire policy

WIP12D does not loosen WIP12C ignition rules. Inert fragments, plate plugs and structural shock do not directly start fires. Only an actual mechanical hit on a vulnerable fuel, electrical or ordnance material volume can use the existing rare deterministic ignition path, while explosive and thermal/incendiary channels remain explicit sources.

## Diagnostic APIs

- `wip12dResidualOverpenetrationContract()`
- `wip12dResidualOverpenetrationDiagnostics()`
- `wip12dResidualEventDiagnostics(impactEventId)`
- `wip12dResidualSupplementProbe()`
- `wip12dShipReentryProbe()`
- `wip12dResidualOverpenetration3DAudit()`
- WIP12A trace and packet diagnostics
- WIP12B live terminal-event diagnostics
- WIP12C detailed traversal and ignition diagnostics

## Deliberately deferred

- WIP12E compartment/portal pressure, reflected-pressure, impulse, blast-wind, dynamic-breach and exterior-vent authority described in `WIP12E_COMPARTMENT_BLAST_HANDOFF.md`;
- replacement of the primary Kh-32/Kh-35U legacy damage authority with common-kernel packets;
- unbounded or individually simulated fine fragments;
- render-frame ballistics;
- water-entry and underwater damage;
- persistent damage patches and snapshot migration;
- production homogeneous/KC armor solvers;
- surface target approval, anti-ship launch control and FCS;
- gun launch, magazines and exterior ballistics.
