# EMITTER_A final report

## Status ledger

| State | Result |
|---|---|
| IMPLEMENTED | DDG-119/CG-52 immutable ShipProfile equipment emitter registries; shared ShipRuntime adapter; public read-only registry/runtime/audit API; SOV existing metadata registered inactive. |
| TESTED | A–D gates PASS; one final MAX_THREAT broad regression; DDG/CG mixed/same-class scenes; save/restore and UI ownership; SOV enemy/neutral inactive scenes; performance probe. |
| APPROVED | Directive-defined categories, compatibility units, SHADOW→ACTIVE promotion and inactive-only SOV scope. No expectation or tolerance update was needed. |
| UNRESOLVED | Inherited debts listed below; CONFIRMED_ONLY performance; SOV real electronic capability; future category-level EMCON_B. |
| RELEASE | Not released. No tag, release, main commit or merge. [PR #73](https://github.com/0-FLANDRE-0/Aegis_Project/pull/73) is OPEN for user decision. |

| Target | IMPLEMENTED | TESTED | APPROVED | UNRESOLVED | INHERITED_DEBT | RELEASE |
|---|---|---|---|---|---|---|
| DDG emitter profile | Yes | SHADOW/ACTIVE exact | Directive scope | None in migrated branch | No | No |
| CG emitter profile | Yes | SHADOW/ACTIVE exact | Directive scope | None in migrated branch | No | No |
| ShipRuntime state | Existing owner adapter | Isolation + save round-trip | No duplicate mutable state | Category overrides are EMCON_B | No | No |
| Common emitter API | Yes | schema/ref/API/scope gates | ACTIVE | Future consumers may migrate incrementally | No | No |
| ESM integration | Existing consumer preserved | anonymous plots exact + truth audit | Behavior preserved | No new ESM model | Existing observer debts retained | No |
| Passive RF integration | Existing consumer preserved | U3 diagnostics + broad paired | Behavior preserved | No emitter database generalization | U3 raw paired evidence retained | No |
| HOJ integration | Existing consumer preserved | MAX_THREAT + feature-off check | Behavior preserved | CONFIRMED_ONLY performance | Yes | No |
| Sovremenny registration | 11 inactive metadata rows | enemy/neutral, DDG/CG scenes | Registration only | RF values unverified | No | No |
| Sovremenny active emission | No | Confirmed zero | Explicitly not approved | Future work | No | No |
| Save/import | Schema unchanged | DDG/CG exact round-trip | Preserved | None from EMITTER_A | No | No |
| MAX_THREAT regression | N/A | 364+42+213+29 PASS | Gate passed | None new | Legacy 14 incomplete | No |
| CONFIRMED_ONLY | Feature-off contract only | Static + limited scenes | Limited scope only | Performance UNVERIFIED | Yes | No |

## Result

`Aegis_SIM_v48_WIP_EMITTER_A.html` is 22,146,163 bytes, SHA-256
`04bfb9c991929bed5800e7899f2ffb79087bfd20b79300c9bb01628b7edc98c6`.
It is generated reproducibly from merged U3 product SHA-256
`243c196a69990e1fba9de0993f7904fb569e3adc5b6e84cf52672d3300638835`.

The former DDG/CG branch in `electronicPhysicalEmittersF()` is now a common
adapter over immutable profile equipment declarations. Mutable radar enable,
EMCON, rotor, health/damage and EW allocation remain in the existing
`ShipRuntime` observer/EW owners. No second state source or save field exists.
The consumer output schema, field order, physical order and RNG behavior are
unchanged.

## Registry contract

- Categories: `AIR_SEARCH`, `SURFACE_SEARCH`, `NAV`, `FIRE_CONTROL`, `ECM`.
  Category is equipment role and is intentionally separate from
  `emitterClass`.
- Compatibility power units are explicitly not watts/ERP: SPY `2500`, SPQ
  `650`, NAV `120`, ECM `2000 * resourceUsed`. They were not retuned.
- DDG: SPY-1D(V), SPQ-9B, BridgeMaster E, SLQ-32 EA declaration.
- CG: modernized SPY declaration, SPQ-9, SPS-73, SLQ-32 EA declaration.
- SOV: the existing eleven SOV_A registration rows only. Every row is
  `REGISTERED_INACTIVE`, `installed=false`, `active=false`, and
  `physicalEmission=false`; no RF value was invented.
- Existing missile seeker, aircraft, Nulka, SPG/illuminator and other paths
  remain outside the migrated ship-profile branch and were not duplicated.

## A–D gates

| Gate | Outcome | Evidence |
|---|---|---|
| A baseline | PASS | DDG/CG mode/damage/rotor/ECM matrices, mixed/same-class NPC receiver plots and RNG, SOV pre-state. |
| B SHADOW | 13/13 PASS | Legacy remained authority; declared output exact; SHADOW mismatch 0 and RNG consumption 0. |
| C ACTIVE | 13/13 PASS | ACTIVE authority exact; comparator not run; UI controls and operational save round-trip preserved existing owners. |
| D SOV | 12/12 PASS | Eleven rows exact, no invented RF fields, enemy/neutral emission/receiver/detection/attack all inactive. |

Scope proofs use a pinned-base, fail-closed exact-anchor transform and protected
function hashes. Receiver RF physics, jammer/HOJ, observer, save/import, ARH
evidence and acceptance functions are byte-identical. See `SCOPE_B/C/D.json`.

## Final broad regression

The directive-required broad run was executed exactly once in `MAX_THREAT`:

| Suite | Result |
|---|---:|
| Native 13 | 364 / 364 PASS |
| U3 ↔ EMITTER_A paired | 42 / 42 PASS |
| UI | 213 / 213 PASS |
| Real WebGL observed world | 29 / 29 PASS |
| Legacy `#lockBtn` EMCON UI | 0 / 14, inherited INCOMPLETE; not counted PASS |

Wall time was 2,020.15 seconds. New failures: 0. Expected values and tolerances
changed: 0. `CONFIRMED_ONLY` remains performance-UNVERIFIED by the inherited
policy; its assumed Harpoon HOJ feature-off/no-RNG behavior was rechecked in the
Commit C limited gate.

## Performance

The isolated physical-emitter query median increased from 15.48 µs to 32.10
µs/call (2.07×). The absolute candidate cost is 0.032 ms/call, output and RNG
are exact, and the full UI/WebGL gates passed. This is reported as a measurable
microbenchmark overhead, not hidden as “no change.” No tuning was applied after
the result.

## Inherited unresolved items

- legacy `#lockBtn` EMCON UI 14 assertions remain INCOMPLETE;
- `CIWS_SEED_419025_FAIL`;
- `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`;
- U3 raw paired four intentional differences remain preserved in U3 evidence;
- unrelated WIP12D Actions CIWS speed determinism failure and two checkout
  timeouts;
- `CONFIRMED_ONLY` performance remains UNVERIFIED.

The next planned work is EMCON_B. It must consume this profile registry to add
category/equipment-level controls; it is not implemented here.

## Packages

- Executable-only ZIP: `Aegis_SIM_v48_WIP_EMITTER_A_HTML.zip`
- Report/evidence ZIP: `Aegis_SIM_v48_WIP_EMITTER_A_REPORT.zip`
- Checksums: `SHA256SUMS_v48_WIP_EMITTER_A.txt`

Exact sizes and hashes are in `PACKAGE_MANIFEST.md`. PR #73 is OPEN. GitHub
remote byte-for-byte readback metadata is recorded after publication without
recursively rebuilding the archives.
