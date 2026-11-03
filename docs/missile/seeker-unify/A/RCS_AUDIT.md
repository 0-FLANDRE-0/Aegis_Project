# RCS implementation audit

## Contract and flow

All audited RF equations interpret target RCS as square metres.  A provider
returns an aspect- and band-dependent `rcs`/`apparentRcsM2`; the receiving
radar or seeker normalizes it by its own `snrReferenceRcsM2`.  No consumer uses
dBsm and no conversion is implicit.

`physicalRfReflectorRegistryWip13A2` is the common surface-object collection
point.  Shipboard SPY/SPQ/BridgeMaster, APS-153, SAM ARH surface mode, Harpoon,
and the WIP22 ASM path ultimately consume the same physical reflectors.  The
own-ship WIP22 helper formerly bypassed the band argument; this change supplies
I/J explicitly while leaving its target selection, evidence and state machine
untouched.

## Preserved relative geometry

- DDG/CG own ship: every section's `rcsBase`, aim point, bow/beam/stern/top
  factors, LOS priority, LOS weight and sea-state weight are unchanged.  A
  single total-scale multiplier is applied before summation.
- NPC DDG/CG: the legacy `0.10 + 0.36 abs(sin(aspect))` curve is retained and
  divided by its 0.46 beam value.
- Project 956: the registered 15-degree projected-area LUT is retained and
  divided by its 90-degree entry.
- Test hulk: all five aspect knots per band retain their exact ratios.
- Generic contacts: unchanged, because their SMALL/MEDIUM/LARGE category does
  not establish displacement or class.

The measured band/aspect totals are recorded in `RCS_EFFECTIVE_ASPECTS.md`.
That audit uses the actual ship heading; it also records the Project 956 LUT,
the hulk's five nodes and the unchanged generic-contact values.

## Corrections and non-corrections

| Factor | Status |
|---|---|
| Aspect | existing curves preserved |
| Top view | existing own-ship top weighting preserved |
| Section/aim points | preserved |
| Geometric LOS/occlusion | preserved |
| Sea-state reduction | preserved |
| Radar horizon | unchanged and tested separately |
| Pd/noise/clutter/beam/gimbal/evidence thresholds | byte-unchanged |
| Guidance/propulsion/damage | byte-unchanged |

## Scope guard

The product diff contains 58 changed source lines: one immutable provenance and
formula block, provider normalization, and explicit band plumbing.  It contains
no edits to seeker acceptance, Pd, noise, clutter, beam, gimbal, cue basket,
guidance, propulsion, fuze, damage, IFF, ROE or track association code.  The
diagnostic scripts live outside the product HTML and are not injected in the
deliverable.

