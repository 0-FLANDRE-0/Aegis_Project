# EMITTER_A Commit A — baseline audit

Status: TESTED / PASS

## Existing producer

`electronicPhysicalEmittersF()` owns four shipborne output branches in this
stable order:

1. SPY search radar — compatibility power `2500`
2. SPQ surface-search radar — compatibility power `650`
3. navigation radar — compatibility power `120`
4. SLQ-32 abstraction — compatibility power `2000 * resourceUsed`

The values are game compatibility units, not watts or ERP. No RF coefficient
is being reinterpreted or retuned by EMITTER_A.

Aircraft radars, missile active seekers, and Nulka are appended after the ship
loop. They are explicitly outside this migration.

## Existing consumers

- `electronicReceiverPlotsF`: anonymous ESM bearing measurements. `owner` is
  used only for self-coupling rejection. The optional `ship` reference is used
  only to re-evaluate jammer pod availability and position.
- `electronicJammerSampleF`, `electronicJammerAtReceiverF`,
  `electronicRadarInterferenceF`, and `electronicHojF`: existing ECM coupling.
- `emconDesignationSnapshotF2` and diagnostics: count/inspect physical outputs.
- passive-RF ASM/Harpoon consumers read the anonymous emitter field, not a
  profile/entity truth identity.

## Mutable ownership

- Radar enable, EMCON, and NPC rotor phase: per-ship `observerC(runtime)`.
- Player rotor compatibility phase: existing player globals
  `spq9bRotorAngle` and `bridgeMasterERotorAngle`.
- ECM request, bearing, and allocator: player legacy state or per-ship
  `runtime.ew.executionF` / `runtime.ew.slq32Allocator`.
- Damage and mount health: existing per-ship damage/crew state.

The declarative migration must adapt these owners. It must not introduce a
second mutable enable/rotor/allocator state.

## Profile registration findings

- DDG-119: SPY, AN/SPQ-9B, BridgeMaster E, and legacy DDG EW reference are
  present through sensor/hardpoint data and existing EW fallback.
- CG-52: SPY, AN/SPQ-9, AN/SPS-73, and twin SLQ-32 pod registration are present.
- Sovremenny: 11 registered sensor positions exist, but every row is explicitly
  `installed:false`, `active:false`, and `emitter:false`. The ship capability
  flags also disable sensors and EW. Registration may be made declarative, but
  physical emission must remain zero.

## Executed evidence

`BASELINE_AUDIT.json` captures both playable profiles across eight deterministic
states: all radars, each radar family disabled, EMCON, rotated auxiliaries,
noise ECM, and deception ECM. It also records exact property order for every
legacy output and the predecessor producer/receiver source strings.

All checks passed with zero page errors. The diagnostic HTML was injected into
a temporary copy and is not a product artifact; inverse removal of the probe is
byte-exact to the pinned U3 main script.
