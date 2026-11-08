# EMCON_B final report

## 1. Status

| State | Result |
|---|---|
| `IMPLEMENTED` | Commits A–E: baseline audit, per-ship category/equipment policy, ACTIVE physical/sensor/ECM gates, registry-derived UI, network/save lifecycle |
| `TESTED` | Commit gates, legacy lock debt, one MAX_THREAT broad run, and local candidate-equivalent static/Chromium gates |
| `APPROVED` | Commit-local A–E gates and frozen candidate behavior; remote candidate Actions is recorded in PR #74 after publication |
| `UNRESOLVED` | `CONFIRMED_ONLY` performance; physical SPG-62 registry; communication EMCON; inherited Chromium/harness debts listed below |
| `INHERITED_DEBT` | CIWS seed 419025, CG friendly paired observer delta 2, U3 raw paired delta 4, legacy WIP12D speed determinism, Kh-32 60 km, and the broad-run harness items below |
| `RELEASE` | `false`; no tag or release; merge remains the user's decision |

Base is merged EMITTER_A `main@3dbe3b84bde7a5b23e9713b26a7c8a9ba3823941` (PR #73). The frozen EMITTER_A product is 22,146,163 bytes with SHA-256 `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`.

The EMCON_B candidate is `Aegis_SIM_v48_WIP_EMCON_B.html`, 22,157,395 bytes, SHA-256 `3343f5bbe7d6adac0694656ebafef538c3b7407d7ce642225fff94207c142c33`. Packed main SHA-256 is `03113901632b9cebb33c8d829be37c60dba2f090abc9dbfe23b3d34773167bfe`.

## 2. Implemented contract

The original master owners remain authoritative:

- own ship radar master: `emconActive`;
- other ship radar master: `observerC(runtime).emcon`;
- existing equipment enable, damage, power and health states remain higher-priority operational gates;
- existing EW request/allocator state remains the ECM authority.

EMCON_B adds only `AEGIS_SHIP_EMCON_B_1` detail state per ShipRuntime. Effective priority is:

1. registered, installed and physically emitting equipment;
2. existing offline/damage/power/enabled gate;
3. radar master silence;
4. network `SILENT` lease;
5. equipment override (`FORCE_SILENT`, `FORCE_RADIATE`, `INHERIT`);
6. category policy (`RADIATE`, `SILENT`).

`FORCE_RADIATE` cannot bypass steps 1–4 or equipment damage/offline. ECM is independent of radar master: a jammer emits only when category policy, preserved technique request and allocator all permit it. Hawklink/Link communication remains outside radar EMCON.

### Active equipment scope

DDG-119 and CG-52 consume profile registry entries for SPY (`AIR_SEARCH`), SPQ-9/9B (`SURFACE_SEARCH`), BridgeMaster E/SPS-73 (`NAV`) and SLQ-32 EA (`ECM`). `FIRE_CONTROL` exists as a policy/UI contract row but has zero active registered equipment. No SPG-62 RF model was added. Sovremenny entries remain `REGISTERED_INACTIVE` and cannot be forced to radiate.

## 3. Commit gates

| Gate | Result |
|---|---|
| A baseline audit | 20 function hashes, packed-main hash and representative EMITTER_A snapshots frozen; product behavior change 0 |
| B SHADOW | DDG/CG legacy 16-case matrices exact; mixed/same-class isolation; RNG consumption 0; invalid/inactive requests rejected |
| C ACTIVE | physical output and own/NPC SPY, surface and NAV measurements gated together; blocked receiver RNG 0; ECM allocator/output/coupling/HOJ 0 while requests persist |
| D UI | profile-derived DOM exact; owner routing/isolation; no render mutation; 390/832/1400 px in bounds; all-radiation macro exact restore |
| E lifecycle | 16/16 Chromium checks; network overlay/restore, save round-trip, legacy migration, invalid zero-mutation, reset/destroy/auth; page and console errors 0 |

Default policy physical matrices remain exact with EMITTER_A for DDG and CG. No RF/Pd/noise/RCS/beam, EKF, weapon, guidance, damage or communication-link coefficient changed.

## 4. Legacy `#lockBtn` debt

The 14 requested browser cases ran at widths 390 and 1100 and pass 14/14. MAP_E intentionally retired the visible `#lockBtn` node, while the retained native listener still supplies the command path. A test-only adapter exercised that retained path without entering the release product. This is classified as historical harness selector debt, not a product bypass. Page errors and console errors are both zero. Evidence: `LOCK_DEBT_14.json` and `screenshots/LOCK_DEBT_*.png`.

## 5. Final broad run

The MAX_THREAT broad runner executed exactly once on the frozen candidate. Wall time was 2,224.21 seconds. It did not mutate the product, expectations or tolerances.

### Completed PASS rows

- helicopter flight: 85/85;
- ISAR classes: 8/8;
- ISAR clock: 12/12;
- Sovremenny native: 30/30;
- Sovremenny casualty: 13/13;
- Sovremenny visual: 10/10;
- paired: 42/42;
- real WebGL launch: 29/29.

### Incomplete/inherited rows

- APS-153, ISAR native/UI, legacy EMCON native and Harpoon F1/clock reached Chromium `Target crashed` before assertions on existing large diagnostic modal/journal paths. The EMITTER_A APS-153 comparison reproduced the same pre-assertion crash. These rows are `INCOMPLETE_INHERITED_RUNNER_DEBT`, not PASS and not a failed product assertion.
- Sovremenny deployment is 13/15 (`selectedSOV`, `creditVisible`). The unchanged EMITTER_A baseline reproduces the same two false assertions and same values, so it is inherited harness debt.
- UI213 stopped at the existing 832.CG.PIP fixture-point-covered condition; `nativeHold` and `feedReject` were also false before the stop. A limited EMITTER_A comparison reproduced the same values and fixture condition. This is inherited harness debt.

The raw `FINAL_REGRESSION.json` intentionally preserves the runner's mechanical `newFailures` list. The evidence-based disposition is recorded separately in `FINAL_REGRESSION_CLASSIFICATION.json`; raw failures were not deleted or converted to PASS.

## 6. Candidate approval gates

The final candidate path is manifest-driven and whitelists `EMITTER_A` and `EMCON_B`; unknown stages fail. The workflow no longer guesses a product by filename and result-only documents do not recursively trigger it.

Local workflow-equivalent evidence on the frozen candidate:

- strict manifest/baseline bytes and SHA: PASS;
- exact stage-E rebuild: PASS;
- static candidate checks: 11/11;
- JavaScript syntax: PASS;
- baseline Chromium gate: 6/6, including default ACTIVE and master SILENT exact; page/console errors 0;
- lifecycle Chromium gate: 16/16; page/console errors 0.

The remote Actions run is intentionally recorded in PR #74 rather than committed back into a trigger loop.

## 7. Save, network and ownership

- Operational snapshot exports authoritative detail state for own and physical fleet ships.
- Legacy saves receive profile-derived `RADIATE`/`INHERIT` defaults while preserving the old master boolean.
- Unknown category/equipment/enum/profile data is rejected in clone-first preflight; failed import mutation is zero.
- Group leases are transient overlays and never rewrite category or equipment detail state.
- `INDIVIDUAL`/expiry restores prior master/detail settings; direct operator detail under a group overlay is audited as `MANUAL_DETAIL_UNDER_GROUP_OVERLAY`.
- Reset creates profile defaults; destroy removes owner detail/all-radiation memory and leaves no dangling reference.
- Tactical AI still writes only the existing master policy.

## 8. Files and protected scope

Primary product modules are `emcon_policy.js`, `emcon_active_runtime.js`, `emcon_ui.js` and `emcon_lifecycle.js`; the final HTML is generated by `build_product.py`. Test-only diagnostics are injected into disposable HTML and inverse removal is byte-exact. The release candidate contains no `__EMCON_B_E_DIAG__` symbol.

Protected systems left unchanged include sensor RF constants, EKF/tracking, IFF/ROE, weapon/guidance/fuze, damage/ship physics, communication links, SPG-62 registration and Sovremenny capabilities. Exact intermediate diffs and gate JSON are under this directory.

## 9. Publication state

- Branch: `emcon-b`;
- PR: #74, new PR, merge prohibited until user decision;
- `main`: unchanged by this work;
- release/tag: none;
- executable ZIP and report ZIP are separate;
- remote bytes/SHA readback is recorded in `REMOTE_PUBLICATION.json` after push.

`CONFIRMED_ONLY` performance remains `UNVERIFIED`; only feature disposition/static limited checks are claimed. The next work must not reinterpret radar EMCON as communication EMCON or claim FIRE_CONTROL equipment control until physical SPG-62 registration is separately implemented and validated.
