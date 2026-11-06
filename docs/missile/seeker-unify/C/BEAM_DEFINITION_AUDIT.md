# ASM beam and propagation-definition audit

Audit date: 2026-11-03 UTC  
Code baseline: SEEKER_UNIFY_C Stage 1 (`50fe0d00c516197507e6666af5704661edd60fe6`)

No Stage 2 code change was made before this audit was completed.

## 1. Profile half-angle provenance

The Kh-32 and Kh-35U values are:

| Profile | Search az/el half | Track az/el half | Code provenance found |
|---|---:|---:|---|
| Kh-32 | 3.5° / 3.0° | 1.15° / 1.0° | No one-way or round-trip definition in the profile comment, WIP documentation, or retained migration/audit documents |
| Kh-35U | 4.0° / 3.5° | 1.35° / 1.2° | No one-way or round-trip definition in the profile comment, WIP documentation, or retained migration/audit documents |

`ASM_SEEKER_PROFILES` labels exact seeker quantities as simulation abstractions elsewhere, but the beam fields themselves have no directional convention tag. `PROFILE_MIGRATION_TABLE.json` only maps them to a generic antenna half-beam field. `UNIFY_AUDIT.md` records a monostatic R^-4 path and a 3-D beam but does not define whether this gain is one-way or combined. No retained commit documentation supplies the missing definition.

Conclusion: **definition unclear**. Under the directive's precommitted decision rule, the fields become SIM_TUNED **one-way** pattern parameters and ASM moves to `TX_RX_SEPARATE`.

## 2. What the current `cos²` pattern means

For one axis before the floor, the existing pattern is:

`g(u) = cos²(clamp(u,0,1)·π/2)`, where `u = |offset| / half`.

Thus `offset=half` is a zero of the ideal pattern, not a -3 dB half-power point. The 0.08 floor then replaces that zero.

- One-way, one-axis -3 dB: `u = 0.5`.
- One-way, equal az/el offsets with the product pattern: `u = 0.364056664` on each axis.
- After applying the same one-way pattern on transmit and receive, total one-axis -3 dB: `u = 0.364056664`.
- After applying it twice at equal az/el offsets, total -3 dB: `u = 0.261200553` on each axis.

The numeric half-angle values are not changed. Stage 2 only makes their one-way meaning explicit and applies the existing pattern twice.

## 3. LOS, sea residual, and weather/path meaning

ASM currently stores one `radarLOSQuality(...)` value as `_losQ` and multiplies it once. `radarLOSQuality` is a geometric horizon fade factor; it does not claim to be an already combined monostatic factor. Its directional convention is therefore unclear.

The weather helper is explicit: `maritimeRfWeatherPathFactorWip13A3(band,pathKm)` documents `pathKm` as the **complete outbound+return RF path**. Both ASM and SAM call it with `2*rangeKm`; its returned value is already a round-trip aggregate and must not be squared again.

SAM ARH provides the comparison contract:

- the same beam value is multiplied once as transmit gain and once as receive gain;
- the geometric LOS factor is multiplied twice;
- `weatherQ` is computed once over `2*rangeKm` and included once in the environment aggregate;
- low-altitude clutter/multipath environment factors are included once as aggregate propagation modifiers.

Stage 2 therefore uses `beamTx=beamRx=offGain`, `losTxQ=losRxQ=_losQ`, and `envQ=clutter*weatherQ`. This is the SAM round-trip definition without double-counting the already round-trip weather path.

## 4. Sidelobe floor 0.08

No code comment, WIP document, profile source tag, or retained audit attributes `0.08` to public hardware data. It is an untagged legacy simulation value. The audit classifies it as SIM_TUNED.

The directive requires retaining the value and treating it as one-way. It is therefore applied on transmit and receive:

- one-way floor: `0.08` = -10.9691 dB;
- round-trip product floor: `0.0064` = -21.9382 dB.

HOJ and passive RF remain receive-only and are unchanged.

## 5. Public-source check

The following public pages were inspected for antenna beamwidth or sidelobe data:

1. Astrum Avia, “Guidance system for precision-guided weapons / ARGS-35E” — publishes terminal purpose, azimuth guidance sector ±45°, elevation sector +10° to -20°, and maximum range up to 20 km. It does **not** publish antenna beamwidth or sidelobe level.  
   `http://astrum-avia.com/production/special-systems-complexes/guidance-system-for-precision-guided-weapons/`
2. Kh-35 public summary and its cited archived Radar-MMS material — identifies the ARGS-35E X-band seeker and up-to-20 km acquisition range; no antenna beamwidth or sidelobe value is given.  
   `https://en.wikipedia.org/wiki/Kh-35`
3. RusNavy, Gran-KE announcement — states improved target-detection range/selection and a passive channel, but gives no beamwidth or sidelobe number.  
   `https://rusnavy.com/news/navy/index.php?ELEMENT_ID=12835`
4. Kh-32 public summaries (Wikipedia, GlobalSecurity search results) — describe radar/active terminal guidance but publish no seeker antenna beamwidth or sidelobe value.  
   `https://en.wikipedia.org/wiki/Kh-32`  
   `https://www.globalsecurity.org/wmd/world/russia/kh-32-specs.htm`

Result: no usable public ARGS-35/Gran-KE/Kh-32 beamwidth or sidelobe figure was found. The existing half-angle values and 0.08 floor remain unchanged SIM_TUNED values.

## Stage 2 decision

The definition is unclear, so the precommitted rule applies:

- ASM `beamConvention` changes from `COMBINED_SINGLE` to `TX_RX_SEPARATE`.
- Existing one-way beam pattern is applied twice.
- Existing geometric LOS is applied twice.
- Existing weather attenuation remains one round-trip result computed over `2R`.
- No change to half-angle values, 0.08, `snrRefKm`, reference RCS, thresholds, search sectors, HOJ, or passive RF.

