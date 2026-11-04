# SEEKER_UNIFY_C Stage 3 — passive RF source and assumption audit

Status: **pre-effect audit complete** (2026-11-04). Numeric receiver and filter
values below are fixed before effect tests and carry `SIM_TUNED` provenance.

## Feature provenance

| Weapon | Passive RF azimuth/elevation feature | Provenance | Evidence decision |
|---|---|---|---|
| Kh-35U/Kh-35UE family | enabled | `PUBLIC_CONFIRMED` | the archived Tactical Missiles Corporation Kh-35UE product page and the cited Kh-35 table describe active/passive radar guidance; detailed thresholds and angle accuracy are not public |
| Kh-32 | enabled only in `MAX_THREAT` | `ASSUMED_THREAT` | public summaries support radar homing/new seeker, but the audit found no sufficient public confirmation of passive RF angle cueing |

Sources consulted:

- Tactical Missiles Corporation, “Kh-35UE”, archived 2020-10-21:
  <https://web.archive.org/web/20201021181950/http://eng.ktrv.ru/production/military_production/anti-ship_missiles/kh-35ue.html>
- Wikipedia, “Kh-35”, current page inspected 2026-11-04; the guidance row cites the above manufacturer page:
  <https://en.wikipedia.org/wiki/Kh-35>
- Wikipedia, “Kh-22” (Kh-32 subsection), inspected 2026-11-04:
  <https://en.wikipedia.org/wiki/Kh-22>

Wikipedia is used only to locate and cross-check public claims. It is not used
to invent unpublished receiver sensitivity, angular error, or range.

## Fixed simulation model

The adapter consumes `electronicPhysicalEmittersF()` rather than global ship or
EMCON state. Physical source coordinates and owner references stay inside RF
synthesis. The emitted measurement contains no source coordinates, owner id,
entity id, or truth reference.

Received power follows the existing electronic-receiver convention:

`Pr = Pt * Gtx * Grx * 0.008 * LOS * equipment/weather / (4*pi*R^2)`

The existing one-way range anchors are converted once into sensitivity rather
than retained as binary range gates, using the ownship SPY reference power
`Pt=2500` and unity gains/LOS:

| Weapon | frozen legacy anchor | derived sensitivity |
|---|---:|---:|
| Kh-35U | 150 km | `7.07355302630646e-11` |
| Kh-32 | 250 km | `2.5464790894703257e-11` |

These are `SIM_TUNED` compatibility anchors, not public hardware claims. No
post-test threshold fitting is allowed.

The model additionally preserves the existing passive update cadence and
bearing-error profiles, applies emitter and receiver directional gain, RF LOS,
weather/equipment status, and R^-2 propagation. Elevation geometry uses the
directive's fixed assumed emitter height `25 +/- 8 m` and the existing 4/3
Earth propagation convention. Low-elevation uncertainty is explicitly larger.
The elevation-sigma multiplier reuses the existing RAM passive-RF horizon form
`1 + 0.75*exp(-|elevation|/2deg)`; `0.75` and `2deg` are existing model values,
not new CUE_A tuning constants. This leaves high-angle Kh-32 observations close
to the base angular error while making near-horizon Kh-35U elevation much less
informative.
Angle measurements update the onboard CUE_A covariance through a nonlinear
bearing/elevation EKF; an elevation-derived direct range is diagnostic only and
does not overwrite the cue range.

## Modes and boundary

- `MAX_THREAT` (default): `PUBLIC_CONFIRMED` and `ASSUMED_THREAT` features.
- `CONFIRMED_ONLY`: only `PUBLIC_CONFIRMED`; therefore Kh-32 passive RF cueing
  is disabled while its active seeker remains unchanged.
- A disconnected DL update hook is present for future integration. It cannot
  receive data until an explicit producer is connected.

The operational save stores the selected threat-assumption mode. Older saves
migrate to `MAX_THREAT`; sensor/weapon state and the existing save schema are
otherwise unchanged.

## Anonymous passive measurement fields

`source`, `sequence`, `sampleTimeS`, `available`, measured azimuth/elevation,
their sigmas, SNR/confidence, emitter class/band, and diagnostic direct-range
estimate/sigma. No tactical consumer receives truth coordinates or identity.
