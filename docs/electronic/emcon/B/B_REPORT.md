# EMCON_B Commit B report

## Status

- `IMPLEMENTED`: per-ShipRuntime detail-policy state, strict validator, pure decision API.
- `TESTED`: static protected hashes and actual Chromium SHADOW matrix.
- `APPROVED`: Commit-B gate only; no ACTIVE consumer yet.
- `UNRESOLVED`: physical/sensor/ECM ACTIVE connection, UI, network/save lifecycle.
- `RELEASE`: false.

## Contract

- Schema: `AEGIS_SHIP_EMCON_B_1`.
- Defaults: all five categories `RADIATE`; every registered item `INHERIT`.
- Existing master owner is not duplicated.
- Decision priority: registration → operational/damage/offline → radar master → network
  silence → equipment override → category policy. ECM is independent of the radar master.
- `FORCE_RADIATE` cannot bypass inactive registration, equipment disabled, damage, or ship offline.
- Query reports `truthUsed:false`, `rngConsumed:false`; it reads no target or random source.

## Gate

Static gate: PASS. Of the 20 Commit-A function hashes, only the intended
`prepareElectronicF` lifecycle hook and declared-resolver SHADOW observation changed.

Actual Chromium gate: PASS.

- DDG and CG legacy 16-case matrices exact against EMITTER_A.
- master active/silent and ECM request OFF/ON exact.
- mixed DDG/CG, CG/DDG and same-class DDG/DDG, CG/CG owner isolation PASS.
- 64 repeated decisions per profile consumed no observer/EW RNG.
- unknown category/equipment/enum strict reject PASS.
- ship-offline probe cannot radiate.
- SOV inactive state validates, emits zero, and rejects FORCE_RADIATE.
- partial policy is intentionally SHADOW-only and does not alter tactical output.
- page errors 0; console errors 0.

Evidence: `BUILD_B.json`, `B_STATIC.json`, `B_GATE.json`, `changes-B.diff`.
