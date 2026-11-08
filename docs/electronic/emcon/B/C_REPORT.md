# EMCON_B Commit C report — ACTIVE physical and measurement gates

Status: `IMPLEMENTED` / `TESTED` / `APPROVED` (commit-local gate) / `RELEASE=false`

## Scope

- `electronicShipPhysicalEmittersDeclaredA` now consumes the common per-equipment decision.
- Own-ship SPY, SPQ-9/9B, and BridgeMaster E/SPS-73 measurement paths consume the
  `AIR_SEARCH`, `SURFACE_SEARCH`, and `NAV` category decisions respectively.
- NPC observer SPY and auxiliary radar paths use the same owner-addressed contract.
- NAV shoreline returns are inhibited with the NAV receiver, rather than remaining as a
  display-only fake radar return while the category is silent.
- ECM category silence immediately drives allocator shares and `resourceUsed` to zero,
  suppresses physical jammer output, receiver coupling, and HOJ evidence, while preserving
  the operator's noise/deception request for resumption.
- Surface and helicopter IFF reply collection follows the AIR_SEARCH transmit gate.

No RF/Pd/noise/RCS/beam constants, EKF, communication links, SPG-62 RF, SOV capability,
weapon doctrine, damage physics, or save schema changed in this commit.

## Protected behavior

- Default policy physical-emitter matrices are byte-for-byte JSON-exact with merged EMITTER_A
  for DDG-119 and CG-52.
- Existing master ownership remains `emconActive` / `observerC(r).emcon`.
- Hawklink and Link/network communications are not gated by radar EMCON.
- The shipped product contains no diagnostic probe.

## Deterministic Chromium gate

Final `C_GATE.json`: `PASS`; page errors 0; console errors 0.

- DDG/CG default matrices exact: PASS
- AIR/SURFACE/NAV category physical isolation: PASS
- Own-ship blocked measurement calls: 0; blocked sensor RNG change: 0
- NPC blocked measurement calls: 0; blocked sensor RNG change: 0
- Active control measurements observed for every tested receiver
- Blocked rotor/accumulator state held while time/track-age paths remain available
- ECM request preserved: PASS
- ECM allocator/resource/physical output under silence: 0
- HOJ jammer evidence under silence: 0
- Re-radiation resumes from the preserved request: PASS
- Mixed and same-class coverage: DDG+CG, CG+DDG, DDG+DDG, CG+CG

The diagnostic extension is injected only into a disposable `/tmp` build and its inverse
removal is byte-exact. It is not present in `Aegis_SIM_v48_WIP_EMCON_B.html`.

## Build

- Baseline HTML SHA-256: `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`
- Commit-C candidate HTML SHA-256: `a99efb7f94298e7777e58e653c32ed742d31fe91d36b7338cdbea8a4db349087`
- Candidate packed-main SHA-256: `eba3f379ed6779c6689472e4c2dc539002c55e0d74427a8423a5d9ab47a3e646`

This is an intermediate checkpoint. The final one-time broad regression, candidate workflow,
publication packages, remote readback, and PR are intentionally deferred until Commit E.
