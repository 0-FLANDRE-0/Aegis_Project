# AEGIS v48 WIP11B — operational import safety hardening

## Scope

- Baseline: `archive/v48/WIP11A/Aegis_SIM_v48_WIP11A.html`
- Remove the active-player ship destruction override.
- Strengthen the operational-state preflight boundary.
- Guarantee zero authoritative mutation for validation-rejected imports.
- Enforce explicit `profileRevision` compatibility.
- Preserve WIP11A ownership, lifecycle, registry and profiler behavior and all WIP11 combat/physics/rendering results.

WIP11B does not add another live ship, change simulation cadence, redesign the snapshot schema, or implement gun/FCS/aviation behavior.

## Active-ship lifecycle guard

`destroyShipRuntime(entityId)` no longer accepts an options object. If `entityId` is the registered active player ship, it always returns:

```text
{ ok:false, reason:"ACTIVE_PLAYER_SHIP", entityId }
```

Extra JavaScript arguments, including the former `{allowActive:true}`, are ignored by the one-argument function and cannot reach a privileged branch. Destroying an unbound secondary runtime remains supported. Rejected active-ship destruction leaves the ship registry and lifecycle revision unchanged.

## Operational import pipeline

The public WIP11A snapshot schema remains `AEGIS_OPERATIONAL_STATE_V48_WIP11A`; valid WIP11A snapshots from the same profile revision continue to round-trip. WIP11B changes the import implementation to:

```text
detached input clone → complete preflight → apply prepared state
```

No transient reset, module reset, navigation write, inventory write, flooding write, crew restore or lifecycle increment occurs before every codec passes.

The preflight report schema is `AEGIS_OPERATIONAL_PREFLIGHT_V48_WIP11B`. It runs seven ordered codecs:

| Codec | Validated authority |
|---|---|
| `envelope` | schema/version, profile ID/revision, ship ID and units |
| `navigation` | required finite navigation fields, booleans and trail points |
| `weapons` | exact VLS shape/coordinates/types, CIWS identities/ammunition and Mk 36 identities/ranges |
| `loads` | exact liquid-load IDs and finite non-negative masses |
| `damageFlooding` | ship HP, registered damage IDs, exact cell/door/pump sets, opening geometry and attitude |
| `crew` | crew schema/mode/time, exact 310-person ID set, casualty totals, spaces, positions, teams and logs |
| `aviation` | operational aviation inventory container and record shape |

Unknown metadata is allowed; unknown authoritative IDs are rejected.

## Profile compatibility

`AEGIS_OPERATIONAL_PROFILE_COMPATIBILITY_V48_WIP11B` contains an explicit accepted-revision list per profile. The current contract accepts only:

```text
DDG_119_LATE_FLIGHT_IIA → V48_WIP11
```

A different or missing `profileRevision` returns `PROFILE_REVISION`. A future incompatible profile must provide a deliberate migration or a newly accepted revision; import does not guess.

## Zero-mutation boundary

The runtime contract declares `invalidInputMutationPolicy: ZERO_AUTHORITATIVE_MUTATION`. The browser regression primes live hostile/friendly ordnance and track state, then attempts six invalid imports:

1. incompatible profile revision;
2. truncated aft VLS array;
3. unknown liquid-load ID;
4. unknown flooding-cell ID;
5. truncated crew roster;
6. non-finite navigation value.

Every case is rejected before apply. Before/after fingerprints are exact-equal across:

- exported ship operational state;
- lifecycle revision and last event;
- registered ships and active ship ID;
- aircraft, surface-contact, hostile-missile, friendly-ordnance, RAM and CIWS-projectile identities;
- track, ESM, sensor-dwell and selected-lock state;
- SPG-62 assignments/reservations and entity serials.

The guarantee is for validation-rejected input. Unexpected internal runtime faults remain fatal defects rather than a supported partial-import mode.

## Detached export correction

Testing exposed a WIP11A aliasing defect: `exportOperationalState()` returned the cached crew snapshot object directly. A caller could mutate the exported object and thereby corrupt the next validation context even though the underlying crew roster was unchanged.

WIP11B deep-clones crew and flooding snapshots before returning them. The self-test mutates an exported crew array and confirms that a fresh export still contains all 310 crew groups.

## Diagnostics and compatibility

Added diagnostic surfaces:

- `operationalImportSafetyV48Wip11B()`
- `operationalProfileCompatibilityV48Wip11B()`
- `operationalImportSafetyAuditV48Wip11B()`
- `operationalImportMutationFingerprintV48Wip11B()`
- `validateOperationalStateV48Wip11B()`
- `importOperationalStateV48Wip11B()`

The WIP11A export/import/validation diagnostic names remain compatibility aliases and now use the hardened implementation.

## Behavior parity

The WIP11B browser contract loads both archived WIP11A and WIP11B at fixed seeds. Kh-35U impact/penetration values and the CIWS fixed-step state, ammunition use, local track, projectiles, RNG state and step count are exact-equal.

The following remain unchanged:

- `60 Hz` fixed simulation tick;
- `120 Hz` maximum flooding/force substep;
- `20 Hz` hydrostatic quadrature;
- SPY scheduler, EKF, seeker, guidance and weapon behavior;
- WIP11 material/protection calculations, mass ledger and 87 physical hitboxes;
- 138 interior spaces, 160 portals, 70 equipment records and 310-person roster;
- 3D rendering, aft geometry, six liferaft contacts and 2D ship drawings.

## Local verification

- Inline JavaScript parse: `PASS`
- Workflow YAML parse: `PASS`
- Crew, interior, BridgeMaster E, ship-profile, material/protection and WIP11B safety static contracts: `6/6 PASS`
- WIP11B targeted destroy/preflight/zero-mutation/round-trip browser contract: `PASS`
- Invalid import matrix: `6/6 rejected`, `6/6 zero-mutation`
- WIP11A fixed-seed behavior parity: exact match
- Full Playwright suite: `17/17 PASS`
- Multi-view WebGL visual probe: `PASS`
- WebGL console/page errors: `0 / 0`
- Aft geometry, six liferaft contacts, material/protection and 2D drawing audits: `PASS`
- Workflow jobs declared: `18`

## Artifact

- File: `Aegis_SIM_v48_WIP11B.html`
- Size: `2,742,422 bytes`
- SHA-256: `93084bb9b0d9a72f0544b244a5ced6f314fb37a224f18f5739163fd10ed3db62`
- WIP11A baseline SHA-256: `d18981ca9db5a525417020e5501dce3c638e27cdc97de0f3558fba2e455b1b7a`

## GitHub Actions acceptance

- Workflow simulator: `Aegis_SIM_v48_WIP11B.html`
- WIP10 transition baseline: `archive/v48/WIP10/Aegis_SIM_v48_WIP10.html`
- WIP11A safety/behavior baseline: `archive/v48/WIP11A/Aegis_SIM_v48_WIP11A.html`
- Expected jobs: `18`
- Replaced job: `runtime-ownership-wip11a` → `runtime-safety-wip11b`
- Required final result: `18/18 jobs passed`
- Remote run: pending user upload and pull request

## Future maintenance

- Adding a field that is not part of the operational snapshot requires no WIP11B work.
- Adding new authoritative snapshot state requires one codec extension plus valid, rejected and zero-mutation fixtures.
- Changing the meaning or shape of existing snapshot state requires a profile-revision migration or an explicit compatibility decision.
- Multi-ship scheduling and per-ship destruction authority remain WIP14 work; the active-player guard must not be weakened as a shortcut.
- WIP12 remains the next feature WIP: gun/projectile terminal effects, fuzes, ricochet, penetration, fragments, blast and material-aware entry/exit damage.

## Repository result

- Root should contain only the newest WIP11B simulator, status and checksum set.
- Exact WIP10, WIP11 and WIP11A artifacts are preserved under `archive/v48/`.
- Tests target WIP11B; transition and behavior-parity tests read their archived baselines.
