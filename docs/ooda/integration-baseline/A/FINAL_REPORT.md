# INTEGRATION_BASELINE_A final report

## 1. Baseline and publication boundary

The verified base is `main@d5f43c5a7d3550efb2f45d10aaf4195fb60955ae`, the ordinary merge commit of PR #78 SEEKER_CLOSE_A. Its verified head was `50a71069925ff485486e51cd153fc2f3600cd752`; Actions run `42574022086` completed both jobs successfully. PR #78 did not change the product HTML.

Work was performed only on `integration-baseline-a`. PR #79 is not merged. Corrected package-head PR Actions run `43415982293` and workflow_dispatch run `43417371723` both completed successfully. No release or tag was created.

| Role | File | Bytes | SHA-256 |
|---|---|---:|---|
| Baseline | `Aegis_SIM_v48_WIP_HP_A.html` | 22,200,135 | `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa` |
| Result | `Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html` | 22,212,299 | `655d2bdaa8e30e4788334373ea0f87d162ba4de84e1119b8c42f7ad855bd30b0` |
| Baseline packed main | index 13 | 40,927,903 | `0ea0f4535a4d193dc686ba4bba2ba86509a04ba310cad90992324e188996d464` |
| Result packed main | index 13 | 40,958,311 | `c95b6022dd28ff87f95cb2a02af6f082ee25653bcd372137cf6d722cc0e8764d` |

Extraction is exact `data-c55-index="13"` text extraction, base64 decode and gzip decompression. Function hashes use exact UTF-8 source bytes with no normalization. Stage browser evidence used Chromium `151.0.7922.173` and Playwright `1.62.1`.

## 2. Change summary

This stage does not implement a new OODA policy. It freezes the current defense boundary and adds two interfaces around the existing H1 upper-decision calls. The final correction also limits crew data to an owner-local, deep-frozen operational summary and extends the protected boundary audit without changing weapon, sensor, damage, RNG or save behavior:

- `AEGIS_DEFENSE_DECISION_INPUT_A1`: owner-addressed, observation-only and recursively frozen;
- `AEGIS_DEFENSE_DECISION_COMMAND_A1`: advisory-only order/priority/salvo/HOLD/DEFER command;
- `LEGACY_H1`: reproduces the native H1 order, recommendation ordering and salvo decision;
- `window.__DEFENSE_DECISION_A1__`: read-only snapshot, validation and audit API.

The adapter is inside the player and foreign-owner lexical WIP118 closures. It does not move or copy CPA/NEZ, inventory preview, SPG planning, WIP119 readiness, A3 authority, Network G, formal release or CIWS authority.

## 3. Function-hash boundary

The corrected gate freezes 31 protected functions. Candidate results are:

- 30 protected functions exact;
- one intentional change: `wip118BuildEngagementControl`, 3,996 → 4,080 bytes, SHA `b4e96282…ed2bc1f` → `bdb0c13e…1a221a`;
- eleven new boundary functions are separately hashed, including `defenseDecisionCrewInputA1`, `defenseDecisionTrackInputA1`, the snapshot/legacy begin-salvo-finish adapters, validation, forbidden-path audit and recursive freeze helper;
- all six HP/save authority boundaries are included in the 30 exact protected functions.

The corrected exact hashes and gate result are under `evidence/final-correction/commit-b/`.

## 4. Ownership result

| Domain | Existing owner retained | Port relationship |
|---|---|---|
| Observation / Track Manager | Per-ship observer, EKF, covariance, age and A3 evidence | Read-only copy into owner DTO |
| H1 upper decision | Per-ship H1 | `LEGACY_H1` advisory replacement point |
| WIP118/WIP119 | Per-owner lexical control/execution context | CPA/NEZ/planning and all readiness gates retained |
| A3 / Network G / FCS | Existing local safety authorities | Always run after advisory; cannot be bypassed |
| VLS/RAM/Phalanx/gun/Harpoon | Existing weapon execution owners | No callable release field in command |
| C55/local CIWS | Mount-local fixed-tick RF and capability | Entirely outside OODA cadence and command authority |
| H1 radar/EW | Existing H1/operator override | Not moved into provider |
| H2/H3/H4 | Navigation, surface attack and team owners | Not represented in command DTO |
| UI/diagnostics | Presentation only | Read-only snapshots; no automatic execution |

Active-player aliases are pinned to `ACTIVE_SHIP_RUNTIME`. Foreign friendly ships execute inside owner-local lexical roots for tracks, missiles, CIWS, inventory, damage and RNG. The audit found no unresolved active/foreign mutable-root leak.

## 5. Input and command contracts

### Input

The input root carries owner/profile, fixed step/time/revision/mode, owner-local track rows, inventory before/after reserve, SPG/channel summary, ship mission/afloat/display-HP and continuous damage factors, Network G advisory provenance, observed ESM cue metadata and operator overrides. Track rows carry observed position/velocity/covariance/time/age, lifecycle, separated A3 evidence, existing WIP118 CPA/TGO/engagement state and local/remote provenance.

It contains no truth object/reference/ID, hidden enemy state, actual hidden position/velocity, faction/hostile truth, unobserved projectile collection, predicted-hit truth or renderer object. Friendly IDs are routing provenance only. A local track ID remains an address in that owner's track file.

### Command

The only accepted fields are schema/provider/owner, input step/revision, unique local track order, finite priority rows, bounded desired-salvo rows, advisory HOLD/DEFER and a bounded reason. Validation fails closed for owner mismatch, stale step/revision, unknown or duplicate IDs, extra authority fields, non-finite or out-of-range values, mutability and cross-owner consumption.

The command cannot change identity/authority, create a reservation or lease, call a release function, bypass reserve/re-engagement/EMCON/damage/FCS, command H2/H3/H4, or suppress/initiate local CIWS.

## 6. SHADOW to ACTIVE and owner results

| Scope | Builds | Exact comparisons | Mismatches |
|---|---:|---:|---:|
| Active DDG/CG | 6 | 18 | 0 |
| Foreign-friendly CG/DDG | 2 | 4 | 0 |
| Total | 8 | 22 | 0 |

Baseline and candidate game-state oracle digests are both `c57bfc4ffa50adf3af6bb798dcb73d18758d32c5aec59d6469e1a80a6c9615bf`. Diagnostic wall time and `lastBuildMs/lastAssessmentMs/lastPlanMs` are excluded; game state is not. The corrected contract oracle repeated bit-identically at `b3c3e8d3cd5005b9a5403e81bd3c0bd2c3a2d67d85f4d2a0feac80c355550234`. The dedicated crew contract passed 25/25 and repeated at digest `649d34b03516568ed53ce934a161921b6293253c078377ca2a226ea8678fc4c7`.

Contract audits found:

- forbidden truth fields: 0;
- provider/input RNG mismatch: 0;
- operational-save mutation: 0;
- command validation failure during real consumption: 0;
- console/page errors: 0;
- safety authority owned by port: false;
- execution authority owned by port: false;
- immediate-CIWS authority owned by port: false.

## 7. Launch, ammunition, RNG, save and HP equivalence

The baseline/candidate browser oracle records recommendation order, weapon and salvo, safety refusal reason, actual release/ammunition deltas, network lease/gate result, CIWS/CMS events, RNG endpoints and operational save snapshots for both ship profiles and active/foreign roles. Its normalized digest is exact.

The final paired suites add 42/42 HP_A baseline comparisons and 42/42 repeated determinism checks. HP outcome/save contract is 19/19. Current EMCON UI is 14/14, UI is 213/213 and actual WebGL is 29/29. No expectation or gameplay tolerance was changed.

## 8. Corrected-candidate MAX_THREAT regression

The authoritative corrected candidate is 22,212,299 bytes at SHA-256 `655d2bdaa8e30e4788334373ea0f87d162ba4de84e1119b8c42f7ad855bd30b0`. Its bytes and SHA were pinned before either attempt and never changed.

### Attempt 1 — preserved stop

The first corrected broad attempt stopped immediately when `helicopter-flight` could not find the tracked `archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html` fixture. It executed zero assertions. The runner did not continue to later suites. The stop receipt, subprocess logs and preflight gap are preserved under `evidence/final-correction/final-regression/` and summarized in `BROAD_RUN_STOP_REPORT.md`; they remain failure evidence and are not counted as a pass.

### Attempt 2 — user-authorized corrected rerun

The user explicitly authorized one second broad run without changing candidate bytes/SHA, expectations, tolerances or game constants. Sparse checkout was expanded to the pinned WIP_HELI_CG_A fixture and all tracked `docs/` and `tests/` indirect inputs. Preflight then verified 12/12 conditions: product, baseline and fixture bytes/SHA; preservation of attempt 1; all explicit suite inputs; all tracked docs/tests materialized; the exact fixture sparse pattern; and 21-suite count.

Attempt 2 was executed exactly once. All 22 rows passed:

| Coverage | Assertions | Result |
|---|---:|---|
| Static integrity | 17/17 | PASS |
| Native 13 suites | 364/364 | PASS |
| Paired HP_A + determinism | 84/84 | PASS |
| Current EMCON UI | 14/14 | PASS |
| UI | 213/213 | PASS |
| Actual WebGL | 29/29 | PASS |
| U4 seeker scenes | 19/19 | PASS |
| HP outcome/save | 19/19 | PASS |
| SEEKER_CLOSE corrected matrix | 26/26 | PASS |
| **Total** | **785/785** | **PASS** |

Wall time was 6,239.128 s. Expectations updated: 0. Tolerances changed: 0. Game constants changed: 0. `CONFIRMED_ONLY` performance was not run and remains `UNVERIFIED`.

## 9. Evidence classification

Three evidence generations remain separate:

1. the historical pre-correction 782/782 evidence, which belongs to the earlier candidate and is not the corrected candidate's final proof;
2. corrected attempt 1, which is an immutable zero-assertion infrastructure stop and remains FAIL;
3. corrected attempt 2, the only authorized rerun, which passed 785/785 after exhaustive input preflight.

No failed gameplay assertion was reclassified, no expectation or tolerance was changed, and the attempt-1 logs were not overwritten. `FINAL_CORRECTION_REGRESSION_ATTEMPT_2.json` is the authoritative corrected-candidate broad receipt.

## 10. Inherited debt and unimplemented scope

The following remain unresolved and are not waived:

- `CIWS_SEED_419025_FAIL`;
- `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`;
- WIP12D CIWS scale result 42 versus 47 rounds;
- legacy Chromium memory/crash and checkout timeout;
- Kh-32 60 km population study;
- `CONFIRMED_ONLY` performance;
- SOV Mineral/Band Stand/MR-184 and Moskit targeting;
- communications EMCON and active FIRE_CONTROL emitter registry;
- enemy-aircraft rebuild, physical hull-break rule and external-save cross-field policy;
- inherited core self-test diagnostics `SARH WIP61 confidence continuity missing` and `SARH confidence still double-penalizes raw SNR`.

Sovremenny remains NAV-only with no active sensor, weapon or EW capability. No actual OODA processing capacity, evaluation slot, reaction delay, modernization level or damage-based decision policy was implemented.

## 11. Final state classification

| State | Result |
|---|---|
| IMPLEMENTED | Contracts, ownership freeze, LEGACY_H1 provider and narrow ACTIVE adapter complete |
| TESTED | Stage oracles exact; corrected attempt 2 broad 785/785; attempt 1 stop evidence retained |
| APPROVED | Structural equivalence only; existing safety/execution/CIWS ownership preserved |
| UNRESOLVED | Inherited debt and out-of-scope list in section 10 |
| RELEASE | **NO** — PR #79 only, not merged, no tag |

## 12. Reproduction and artifacts

Commands are in `REPRODUCE.md`. The deterministic builder reproduces the candidate byte-for-byte. `CHECKSUMS.sha256` and `PACKAGE_MANIFEST.md` describe the product and split archives. `REMOTE_RECEIPT.json` records post-push full-byte readback. Corrected package-head PR Actions run `43415982293` and workflow_dispatch run `43417371723` are SUCCESS; the receipt records the last full-byte artifact verification.

