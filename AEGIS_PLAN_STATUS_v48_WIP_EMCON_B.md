# AEGIS v48 WIP EMCON_B status

- Base: merged EMITTER_A `main@3dbe3b84bde7a5b23e9713b26a7c8a9ba3823941`
- Baseline product: `Aegis_SIM_v48_WIP_EMITTER_A.html`
- Baseline SHA-256: `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`
- Branch: `emcon-b`
- Product target: `Aegis_SIM_v48_WIP_EMCON_B.html`
- State: Commits A–B IMPLEMENTED + TESTED; B SHADOW gate approved; C–E not yet implemented; RELEASE=false

## Commit A

- Corrected the archived PR #73 state from OPEN to user-merged.
- Classified existing master owners, compatibility readers, physical/sensor/weapon gates,
  UI routing, and diagnostics.
- Frozen 20 baseline function hashes, the exact 40,783,829-byte packed main script
  hash, and representative merged EMITTER_A evidence.
- Product HTML behavior change: none.

## Remaining

- C: ACTIVE physical emission, sensor measurement and ECM allocator/HOJ gates.
- D: equipment override and profile-derived MAP/FLEET UI.
- E: fleet/network/AI/save lifecycle.
- Final: one MAX_THREAT broad regression, candidate Actions, packages/readback, new PR.

No main mutation, merge, release, or tag is authorized by this status.

## Commit B

- Added `AEGIS_SHIP_EMCON_B_1` per-owner detail policy without duplicating the master.
- Strictly rejects unknown profile/category/equipment/enum and inactive FORCE requests.
- Pure query applies registration, operational, master, network, override and category priority.
- Actual resolver stays authoritative; SHADOW observes its single output without a second resolver call.
- Static protected-hash gate and actual Chromium DDG/CG/mixed/same-class/offline/SOV/ECM matrix PASS.
- Default policy is exact with EMITTER_A, query RNG consumption 0, page/console errors 0.
