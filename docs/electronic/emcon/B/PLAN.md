# EMCON_B implementation plan

- Base: merged EMITTER_A `main@3dbe3b84bde7a5b23e9713b26a7c8a9ba3823941`
- Branch: `emcon-b`
- Product: `Aegis_SIM_v48_WIP_EMCON_B.html`
- Merge/release: new PR only; no merge, release, or tag without user decision

Commits follow the directive exactly:

1. A — merge-state documentation and master-state audit; no product behavior change.
2. B — per-ShipRuntime detail policy, strict validator, pure decision API in SHADOW.
3. C — ACTIVE physical emitter, sensor measurement, ECM allocator/HOJ gates.
4. D — equipment overrides and profile-derived MAP/FLEET UI; all-radiation macro.
5. E — fleet/network/AI/save lifecycle, legacy migration and zero-mutation validation.
6. Final — one MAX_THREAT broad regression, candidate workflow, packages, pinned readback and PR.

PR #74 corrections 2–3 are closure corrections, not new stages. Correction 2 adds explicit
`AEGIS_SHIP_EMCON_B_2.allRadiationSilent`, makes it a radar/ECM hard-off above overrides,
and replaces the inferred UI macro with one authoritative `전파방사통제` control plus atomic
selected-equipment breakout. Correction 3 replaces implementation-name consumer keys with
neutral capabilities and immutable ShipProfile `consumerId -> equipmentId` bindings, with
strict fail-closed resolution and a non-SPY synthetic profile gate.
The broad regression belongs only to pre-correction SHA `3343f5bb…c33`; the corrected SHA uses
the directive's limited static, Chromium, lifecycle, baseline, lock, and release-smoke closure.

Communication EMCON, SPG-62 registry migration, Sovremenny activation, sensor/EW retuning,
and OODA redesign are explicitly out of scope.
