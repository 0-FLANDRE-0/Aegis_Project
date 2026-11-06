# SEEKER_UNIFY_U3 final report

## Status

| State | Result |
|---|---|
| IMPLEMENTED | YES — commits A–D are ACTIVE in the product. |
| TESTED | YES — each stage gate ran, followed by one MAX_THREAT broad regression. |
| APPROVED | The user-approved A–D contracts passed their gates. No expectation or tolerance was changed. |
| UNRESOLVED | Four paired exact-state assertions remain raw FAIL but are attributed to the intended D policy; inherited debts and `CONFIRMED_ONLY` performance remain unresolved. |
| RELEASE | NO — PR #72 is OPEN; no merge, release, or tag. |

## Build

- Baseline main: `be19f46794705a18bfd69feba99d7a4b00dd4a0c`
- Baseline product: `Aegis_SIM_v48_WIP_CUE_A_1.html`
- Baseline SHA-256: `0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a`
- Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html`
- Product size: 22,143,087 bytes
- Product SHA-256: `3eecf254b9a586398fb2236068cca722912730d8dc492275f06157407ed6e2ea`
- Packed main-source SHA-256: `e050149c3cfbf1113033df7955c3c2d6a88788879556fb1f333595ff594b4639`

## Sequential implementation

### A — U2 common layer

Harpoon's existing monostatic RF power expression and pre-resolved anonymous
cell ordering/cap now use the U2 profile-selected contract. SHADOW compared
55,441 power values and 3,615 cell resolutions with zero mismatches. Eighteen
representative flight scenes were bit-equal before ACTIVE promotion. Pd, noise,
RCS, beam/gimbal, seeker state and RNG order were preserved.

### B — CUE_A launch-memory adapter

General track mode converts the frozen launch snapshot's position, velocity,
covariance and observation time into the approved CUE_A prediction contract.
The fixed 4 km cap is removed without adding a replacement distance constant;
the existing Harpoon seeker range, gimbal, activation and scan limits remain
the physical boundary. Route mode retains the 4 km plan radius as an explicit
`ROUTE_PLAN_PRIOR` and does not create a measurement update. Valid, stale,
missing and physically infeasible covariance cases passed. Six natural scenes
were deterministic and no truth field entered the adapter.

### C — common HOJ contract

The existing ASM angular HOJ state was moved behind a port contract with its
legacy body and global RNG behavior preserved. Harpoon owns an independent
terminal-only HOJ state and missile RNG. Capability provenance is
`ASSUMED_THREAT`: enabled under `MAX_THREAT`, disabled before signal synthesis
under `CONFIRMED_ONLY`. No Harpoon midcourse passive-RF function was added.
Ninety ASM SHADOW comparisons had zero state/RNG mismatch; six non-jamming
natural scenes remained bit-equal.

### D — passive-RF candidate policy

The existing family/band/geometry/LOS/sensitivity/Mahalanobis gates are
unchanged. Already-gated anonymous candidates are ranked by
`d² + ln(det(S))`; deterministic ties use observable measurement values only.
The selector uses neither emitter identity/truth coordinates nor RNG. SHADOW
was exact to Commit C in all 20 representative scenes. ACTIVE changed six
equipment scenes and three natural scenes exactly where SHADOW recorded a
ranking change; repeated inputs were deterministic and all sampled final
outcomes were retained.

## Final broad regression — executed once

| Suite | Result | Notes |
|---|---:|---|
| Native 13 | 364/364 PASS | Includes helicopter, APS-153, ISAR, EMCON, Harpoon, Sovremenny, save/restore and 1/8/16/64× fixed-clock checks. |
| Paired CUE_A-1 → U3 | 38/42 raw | Four raid exact-state assertions retained as raw FAIL. |
| UI | 213/213 PASS | Headless Canvas2D/UI path. |
| Actual WebGL observed world | 29/29 PASS | SwiftShader WebGL path. |
| Retired EMCON UI | 0/14 INCOMPLETE | Inherited absent `#lockBtn`; not rerun or counted PASS. |

Wall time was 2,287.18 seconds. The raw paired differences are:

- DDG raid: `sameCombatRng`, `sameExistingObserverState`;
- CG raid: `sameCombatRng`, `sameExistingObserverState`.

A targeted stage-attribution run then compared the same six paired scenes at
Commit C: 42/42 passed. Commit D SHADOW is tactically exact to C, while D ACTIVE
intentionally changes the accepted passive-RF emitter. In both final raid
cases, physical state, hull/layout/damage, VLS count, offboard ports, fault
state, sensor-specific RNG and final target outcomes remained equal. Only
track-revisit history and downstream global combat RNG call order changed.
The four original assertions remain visible; expected values and tolerances
were not edited. See `PAIR_STAGE_ATTRIBUTION.json`.

## Information and state boundaries

- No target/entity/platform ID or truth position is emitted into the U2, CUE,
  HOJ or D selection consumer.
- Route planning remains explicitly distinct from observation data.
- Common-layer adapters consume no extra global RNG; Harpoon HOJ uses missile
  RNG only when the assumed feature is enabled and a signal is accepted.
- Fixed tick, operational save schema and read-only 3D renderer are unchanged.
- Existing ASM/SAM RF physics outside the named adapters is byte-preserved by
  the stage scope audits.

## Remaining work

- `EMITTER_A`: profile-driven general emitter registration; not included here.
- `EMCON_B`: category/equipment emission control; not included here.
- Route-prior uncertainty model: deferred; route mode intentionally retains 4 km.
- `CONFIRMED_ONLY` performance: `UNVERIFIED`; limited feature-off/static scenes only.
- Existing debts remain: `CIWS_SEED_419025_FAIL`, paired observer delta 2 and
  retired EMCON UI 14 incomplete assertions.
- Kh-32 60 km pre-existing miss remains a separate investigation.

## Evidence map

- Stage A: `A_EQUIVALENCE.json`, `A_SCOPE.json`, `A_REPORT.md`
- Stage B: `B_GATE.json`, `B_SCOPE.json`, `B_REPORT.md`
- Stage C: `C_GATE.json`, `C_SCOPE.json`, `C_REPORT.md`
- Stage D: `D_GATE.json`, `D_SCOPE.json`, `D_REPORT.md`
- Final: `REGRESSION_RESULTS.json`, `FINAL_REGRESSION_REVIEW.json`,
  `PAIR_STAGE_ATTRIBUTION.json`, `evidence/pair-stage-attribution/`,
  `evidence/final-regression/`
- Reproduction: `build_product.py`, `build_diagnostic.py`, stage runners and
  scope verifiers in this directory

## Delivery packages

- `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3_HTML.zip`: executable HTML only.
- `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3_REPORT.zip`: reports, raw evidence,
  reproduction tools, diffs, archive/status handoff documents and checksums;
  the executable HTML is intentionally excluded.
- `SHA256SUMS_v48_WIP_SEEKER_UNIFY_U3.txt`: product and core evidence hashes.
- `PACKAGE_CHECKSUMS_v48_WIP_SEEKER_UNIFY_U3.txt`: detached package hashes,
  generated after both ZIP files are complete.
