# U2 WIP22 ASM + SAM ARH echo/cell SHADOW comparison

## Status header

- IMPLEMENTED: read-only common monostatic `synthesizeEchoes` and power-weighted `resolveCells` SHADOW calculations
- TESTED: 30 ASM scenes, 12 Kh-35U/Kh-32 cue flights, and 36 ESSM B2/SM-6 air/surface scenes
- APPROVED: SHADOW instrumentation only
- UNRESOLVED: three `IMPLEMENTATION_DIVERGENCE` decisions require user direction; one `FP_ORDER` item is not bit-equal
- RELEASE: no release or tag; no U2 component promoted to ACTIVE

Overall: **STOP — IMPLEMENTATION_DIVERGENCE**

## Gate result

| Check | Result |
|---|---:|
| U1 ACTIVE versus U2 SHADOW tactical-result differences | 0 |
| Page errors | 0 |
| ASM synthesis samples | 10,752 |
| SAM synthesis samples | 1,077 |
| ASM resolved-cell samples | 10,752 |
| SAM resolved-cell samples | 1,071 |
| Cell-count mismatches | 0 |
| Cell member-count mismatches | 0 |

The SHADOW layer consumes no RNG and its output is never supplied to a seeker, EKF, guidance, or tactical consumer.

## Difference classification

| Component | Classification | Observed difference | ACTIVE |
|---|---|---:|---|
| SAM ARH monostatic normalized power | `FP_ORDER` | max relative `1.0195689968577725e-15` | No; bit-equal gate not met |
| Monostatic beam/LOS normalization | `IMPLEMENTATION_DIVERGENCE` | ASM common-vs-legacy max relative `0.9920859674324555`; SAM one-beam alternative max relative `0.14800224630674552` | No |
| Resolved-cell extent policy | `IMPLEMENTATION_DIVERGENCE` | ASM max relative `1.0`; SAM max relative `0.6172967281105196` | No |
| Resolved-cell angular policy | `IMPLEMENTATION_DIVERGENCE` | ASM centroid max `0.010135380514274317 rad` (about `0.581 deg`) | No |

The ASM common-cell range centroid differed by at most `7.646010870116189e-05` relative. This is not a tactical result change because the common cell remains SHADOW.

## Decisions required

### 1. Transmit/receive beam and LOS factors

- Existing WIP22 ASM measurement applies one combined off-axis gain and one LOS-quality factor.
- Existing SAM ARH path applies a transmit beam factor and a receive beam factor, plus two LOS-quality factors.
- A monostatic common contract naturally exposes separate transmit and receive factors, but switching ASM to that convention would materially alter SNR and Pd. No choice was made.

### 2. Cell extent

- WIP22 ASM uses power-weighted RMS moments of member position, intrinsic size, and Doppler spread.
- SAM ARH retains member echoes for four-quadrant monopulse and uses maximum member extents in the measurement noise/glint calculation.
- Collapsing SAM to one RMS cell before monopulse would discard member angular structure; making ASM use maxima would change its glint model. No choice was made.

### 3. Angular resolution and representation

- WIP22 ASM gates azimuth and elevation separately, then replaces members with one Cartesian power-centroid composite.
- SAM ARH gates spherical angular separation and preserves the cluster members for the four-quadrant response.
- This is an algorithmic difference rather than a profile coefficient, so it cannot be silently converted into a hardware parameter.

## Tested conditions

- ASM: DDG, CG, Sovremenny, chaff, and no-target/sea-clutter controls at 10/30/50 km and 15/200 m.
- Cue flights: Kh-35U and Kh-32 at 60/130 km with 0/30/90-degree target turns.
- SAM: ESSM Block 2 air mode, SM-6 Block IA air mode, and SM-6 Block IA surface mode against aircraft, ASM, sea clutter, and chaff at 10/30/50 km.

The complete samples and metrics are in `U2_SHADOW_DIFF.json`. U2 stops here under the directive; U3 and later stages were not started.
