# CUE_A-1 Stage 2 passive-RF source audit

Status: **implementation frozen; effect tests pending** (2026-11-05).

This note supersedes the Stage 3 source description under
`docs/missile/seeker-unify/C/PASSIVE_RF_SOURCES.md` only for CUE_A-1. It does
not change the existing sensitivity anchors, HOJ path, seeker modes, RF LOS,
weather loss, or isolated measurement RNG.

## Candidate boundary

`ASM_MIDCOURSE_PASSIVE_FAMILIES` contains only these observable family labels:

- `SHIP SEARCH RADAR` (SPY)
- `SURFACE SEARCH RADAR` (SPQ-9B)
- `NAVIGATION RADAR` (BridgeMaster/SPS-73 installation profile)

`ACTIVE_SEEKER`, `AIR SEARCH RADAR`, and every `JAMMER`/`RF INTERFERENCE`
source are rejected before geometry is evaluated. Jammer handling remains
exclusively in the byte-preserved `electronicHojF` / `asmUpdateHojTrack` path.
The passive candidate record keeps measured family, emitter class, band,
frequency, received power/SNR, angle, and gate distance. It does not retain
the emitter owner, ship, entity id, or source coordinate. Physical coordinates
are used only inside measurement synthesis to form propagation and angle.

## Frequency and receiver modes

Emitter-profile `frequencyMHz` is authoritative when present. Otherwise the
existing band label is represented by the frozen directive center:

| input | frequency | provenance |
|---|---:|---|
| S band fallback | 3000 MHz | `SIM_TUNED_BAND_CENTER` |
| IJ band fallback | 10000 MHz | `SIM_TUNED_BAND_CENTER` |
| DDG BridgeMaster E | 3050 MHz | existing equipment profile |
| CG SPS-73 installation | 9400 MHz | existing equipment profile |

The default `MAX_THREAT` receiver spans 2000–18000 MHz
(`ASSUMED_THREAT`). `CONFIRMED_ONLY` spans 8000–12000 MHz (`SIM_TUNED`).
Kh-32 passive RF retains its `ASSUMED_THREAT` feature gate and is therefore
entirely disabled in `CONFIRMED_ONLY`; no performance claim is made for that
mode.

The 10 GHz reference interprets the pre-existing bearing error and receive
search half-width at X band. Both scale by `10000/frequencyMHz`. The existing
`cos^2` receive pattern and 0.08 floor, sensitivity values, multipath term, and
0.2 s cadence are unchanged.

## Rotating transmitter beam

| source | -3 dB full width used | speed | panel model | provenance |
|---|---:|---:|---|---|
| DDG BridgeMaster E | 2.0 deg | 30 rpm | one panel | existing profile, public BridgeMaster baseline |
| CG SPS-73 installation | 1.2 deg | 30 rpm | one panel | existing CG profile, `SIM_TUNED` |
| SPQ-9B | 0.6 deg | 30 rpm | two panels, 180 deg apart | existing auxiliary observation-model value, `SIM_TUNED_EXISTING_OBSERVATION_MODEL` |
| SPY | averaged (`beamAz:null`) | n/a | fixed gain 1 | existing RF-scene contract |

For rotating sources, the transmitter gain uses the directive Gaussian
`max(0.015, exp(-4 ln(2) (off/theta3)^2))`. The interval from the preceding
passive sample to the current sample is swept at the emitter profile RPM. A
main beam whose center passes within `theta3/2` of the missile bearing during
that interval yields gain 1; otherwise the nearest interval endpoint supplies
the maximum sidelobe gain. The SPQ-9B second face is evaluated independently.

The SPQ width above is the directive-selected existing 0.6-degree observation
value. The separate full-width constant used by another legacy air-channel
render/detection path is not modified.
