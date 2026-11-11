# INTEGRATION_BASELINE_A final report

## 1. Baseline and publication boundary

The verified base is `main@d5f43c5a7d3550efb2f45d10aaf4195fb60955ae`, the ordinary merge commit of PR #78 SEEKER_CLOSE_A. Its verified head was `50a71069925ff485486e51cd153fc2f3600cd752`; Actions run `42574022086` completed both jobs successfully. PR #78 did not change the product HTML.

Work was performed only on `integration-baseline-a`. PR #79 is not merged. No release or tag was created.

| Role | File | Bytes | SHA-256 |
|---|---|---:|---|
| Baseline | `Aegis_SIM_v48_WIP_HP_A.html` | 22,200,135 | `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa` |
| Result | `Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html` | 22,211,451 | `baf96f9a1350973d045c9ad4f9025a86c10eaeda3c1924ad52498c45b90d0b5b` |
| Baseline packed main | index 13 | 40,927,903 | `0ea0f4535a4d193dc686ba4bba2ba86509a04ba310cad90992324e188996d464` |
| Result packed main | index 13 | 40,956,705 | `ceac2691e092e0db37e3d54a10debfbd67a06ee1798e2859f1450d437ce29097` |

Extraction is exact `data-c55-index="13"` text extraction, base64 decode and gzip decompression. Function hashes use exact UTF-8 source bytes with no normalization. Stage browser evidence used Chromium `151.0.7922.173` and Playwright `1.62.1`.

## 2. Change summary

This stage does not implement a new OODA policy. It freezes the current defense boundary and adds two interfaces around the existing H1 upper-decision calls:

- `AEGIS_DEFENSE_DECISION_INPUT_A1`: owner-addressed, observation-only and recursively frozen;
- `AEGIS_DEFENSE_DECISION_COMMAND_A1`: advisory-only order/priority/salvo/HOLD/DEFER command;
- `LEGACY_H1`: reproduces the native H1 order, recommendation ordering and salvo decision;
- `window.__DEFENSE_DECISION_A1__`: read-only snapshot, validation and audit API.

The adapter is inside the player and foreign-owner lexical WIP118 closures. It does not move or copy CPA/NEZ, inventory preview, SPG planning, WIP119 readiness, A3 authority, Network G, formal release or CIWS authority.

## 3. Function-hash boundary

The baseline freezes 25 protected functions. Candidate results are:

- 24 protected functions exact;
- one intentional change: `wip118BuildEngagementControl`, 3,996 → 4,080 bytes, SHA `b4e96282…ed2bc1f` → `bdb0c13e…1a221a`;
- six new, separately hashed functions:
  - `defenseDecisionInputSnapshotA1` — `48419e84…701874`;
  - `defenseDecisionLegacyCommandA1` — `2a32d952…3dc36`;
  - `defenseDecisionLegacyBeginA1` — `b81a580b…e2bfe`;
  - `defenseDecisionLegacySalvoA1` — `965f9a8c…cd25`;
  - `defenseDecisionRecommendationOrderA1` — `073ee20b…3fcd`;
  - `defenseDecisionValidateCommandA1` — `a25c58ca…396c`.

The detailed exact hashes are in `FUNCTION_HASHES.json` and `FUNCTION_HASHES_CANDIDATE.json`.

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

Baseline and candidate game-state oracle digests are both `c57bfc4ffa50adf3af6bb798dcb73d18758d32c5aec59d6469e1a80a6c9615bf`. Diagnostic wall time and `lastBuildMs/lastAssessmentMs/lastPlanMs` are excluded; game state is not. The contract oracle repeated bit-identically at `fa669dbec3428206a3812cce0c8b10d58d75485af16d3433ff51dd12e6fe61f0`.

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

## 8. Frozen-candidate MAX_THREAT regression

Candidate SHA was frozen before execution. The broad runner was started exactly once.

The raw one-shot receipt must be read literally: static integrity 14/14, U4 scenes 19/19 and SEEKER_CLOSE 26/26 ran and passed (59 total). Nineteen other suites returned before browser launch with zero assertions because the sparse checkout lacked `docs/multiship/G/browser_g.py` and `docs/missile/fuze-zem/A/browser_tools.py`. `FINAL_REGRESSION_RAW.json` preserves those failures unchanged.

After restoring only those repository files, the 19 zero-execution suites received their first actual run on the exact same candidate SHA. Already executed suites were not repeated, and the broad runner was not restarted. That recovery passed 723/723. The reconciled effective result is therefore 782/782 with no effective failures.

| Coverage | Assertions | Result | Evidence source |
|---|---:|---|---|
| Static integrity | 14/14 | PASS | raw one-shot |
| Native 13 suites | 364/364 | PASS | zero-execution first actual run |
| Paired HP_A + determinism | 84/84 | PASS | zero-execution first actual run |
| Current EMCON UI | 14/14 | PASS | zero-execution first actual run |
| UI | 213/213 | PASS | zero-execution first actual run |
| Actual WebGL | 29/29 | PASS | zero-execution first actual run |
| U4 seeker scenes | 19/19 | PASS | raw one-shot |
| HP outcome/save | 19/19 | PASS | zero-execution first actual run |
| SEEKER_CLOSE corrected matrix | 26/26 | PASS | raw one-shot |
| **Total** | **782/782** | **PASS** | combined, same SHA |

Raw wall time was 154.243 s. Zero-execution recovery wall time was 2,463.656 s. Expectations updated: 0. Tolerances changed: 0. `CONFIRMED_ONLY` performance was not run and remains `UNVERIFIED`.

## 9. Raw versus effective classification

The raw 19 failures are not product passes and were not rewritten: they remain `FAIL` with `executedAssertions: 0`. The effective receipt labels them `FAIL_PRE_BROWSER_ZERO_EXECUTION` and points to the separate recovery evidence. This is a checkout/runner setup defect, not a game-result difference. No failed gameplay assertion was reclassified, no suite with executed assertions was rerun, and no expectation was updated.

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
| TESTED | Stage oracles exact; effective broad 782/782; raw/recovery evidence both retained |
| APPROVED | Structural equivalence only; existing safety/execution/CIWS ownership preserved |
| UNRESOLVED | Inherited debt and out-of-scope list in section 10 |
| RELEASE | **NO** — PR #79 only, not merged, no tag |

## 12. Reproduction and artifacts

Commands are in `REPRODUCE.md`. The deterministic builder reproduces the candidate byte-for-byte. `CHECKSUMS.sha256` and `PACKAGE_MANIFEST.md` describe the product and split archives. `REMOTE_RECEIPT.json` records post-push full-byte readback. The final Actions run is recorded there and in the PR after remote execution completes.

