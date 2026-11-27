# DEFENSE_OODA_A final report

## 1. Baseline and frozen product

Work was performed only on `defense-ooda-a`, based on the user-merged
`main@68911e39eb2e1bd1196bbe7c3bedfb4ad9312fc2` (PR #79). No commit was made
directly to `main`, and no merge, release, or tag was created.

| Role | File | Bytes | SHA-256 |
|---|---|---:|---|
| Baseline | `Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html` | 22,212,299 | `655d2bdaa8e30e4788334373ea0f87d162ba4de84e1119b8c42f7ad855bd30b0` |
| Result | `Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html` | 22,226,343 | `1d2b25cd22813c0187d8578e1cd1489f821222674ecb01cddd344f98da88d13d` |
| Result packed main | `data-c55-index="13"` | 40,996,998 | `3bc49d064eb4b2b1832c93a7ca0af79cd799acdef644c5ae0ce266ec6a7df211` |

The deterministic stage-D builder reproduces the product byte-for-byte. The
candidate was frozen before the final broad run and was not modified after it.

## 2. IMPLEMENTED

- One common owner-local OODA engine now serves DDG-119 and CG-52 through each
  `ShipProfile.defenseOodaA` declaration. The engine does not branch on ship
  names.
- The runtime implements bounded owner-local queues, concurrent evaluation
  slots, `OBSERVE / ORIENT / DECIDE / READY`, urgent pre-emption, aging, local
  track continuity, capacity degradation, and deterministic fixed-step service.
- Capacity uses the lower of COMBAT/OPERATIONS crew availability and the
  continuous combat-efficiency factor without multiplying correlated damage.
- The provider evaluates only the frozen `AEGIS_DEFENSE_DECISION_INPUT_A1`
  observation DTO and returns advisory `AEGIS_DEFENSE_DECISION_COMMAND_A1`
  order/priority/salvo/HOLD/DEFER fields.
- The four frozen H1 upper-decision consumers use `DEFENSE_OODA_A` in ACTIVE.
  A3, WIP118/119 safety, FCS/SPG, reserve, re-engagement, Network G, EMCON,
  damage, release, H1 radar/EW, H2/H3/H4, and fixed-tick C55 local defense remain
  authoritative in their existing paths.
- Owner-local OODA phase/queue/service metadata is saved as
  `AEGIS_DEFENSE_OODA_STATE_A1`. Raw input DTOs, truth, renderer objects,
  functions, and RNG state are excluded. Legacy save migration and invalid
  zero-mutation import are supported.
- A read-only DEBUG status dialog and `window.__DEFENSE_DECISION_A1__` snapshot
  expose provider, phase, capacity, slots, queue, next-ready time, last reason,
  fallback, and rejection counts without becoming a timing or input source.

All gameplay profile values are tagged
`SIM_TUNED_GAMEPLAY_NOT_REAL_CIC_SPEC`. They are game pacing values and are not
claims about real CIC throughput or reaction time.

## 3. TESTED — stage gates

### Contracts and deterministic engine

- `A_GATE.json`, `B_CONTRACT_GATE.json`, `B_GATE.json`: profile/state/save and
  bounded queue engine passed.
- `C_SHADOW_GATE_ATTEMPT_7.json`: DDG/CG active and foreign owners reached
  READY; actual execution remained `LEGACY_H1`; forbidden differences,
  validation/RNG/truth failures, fallback, and rejection were all zero.
- `D_CONTRACT_GATE.json` and `D_ENGINE_GATE.json`: DDG/CG slots, degradation,
  mission-unavailable HOLD, queue 64/overflow accounting, urgent pre-emption,
  same-ID continuity/new-ID reset, mid-phase save/load, MANUAL/HOLD,
  native-salvo ceiling, re-engagement, invalid/stale rejection, downlink
  provenance-only, 1x/8x/16x exact, and RNG unchanged all passed.
- The engine's frozen reference result is DDG 4 slots/READY at 48 service steps,
  CG 3 effective slots at modernization 0.8, degraded capacity 0.5 with 2 slots,
  and deterministic overflow count 6 for a 70-row saturation input.

### ACTIVE browser and authority boundaries

`D_ACTIVE_GATE.json` ran both ownership directions twice in Chromium:

| Own / ally | First own READY | First ally READY | First release |
|---|---:|---:|---:|
| DDG / CG | 60 | 120 | 120 |
| CG / DDG | 120 | 84 | 120 |

- release before owner READY: 0;
- MANUAL owner launch delta: 0; foreign HOLD launch delta: 0;
- fallback/rejection/validation/RNG/truth audit failure: 0;
- cross-owner mutation and unauthorized authority fields: 0;
- read-only UI state mutation: 0; console/page errors: 0.

The function gate covers 31 protected functions. Against the integration
baseline, 30 are exact; only `exportOperationalState` changes for the optional
owner-local save field. `wip118BuildEngagementControl` remains exact against the
integration baseline. The eleven port-boundary functions have the expected
definition counts, and the protected A3/Network/FCS/reserve/re-engagement/
EMCON/damage/release/C55/H2/H3/H4 paths are exact.

### Natural terminal control

The inherited paired raid uses one diagnostic 16 km measurement for eight
Kh-32 contacts. Frozen OODA service delay reaches READY after that one-shot
track loses downstream FCS quality, so the candidate correctly remains blocked
by native `FCS_QUALITY` rather than manufacturing authority or sensor data.

The natural-sensor control uses a continuously updated Kh-35U track. DDG and CG
both reached READY, released two native ESSM rounds after READY, and recorded
`PROX_DETONATION_KILL`; closest approaches were 3.7646 m and 2.2506 m, with zero
ship hits and display HP 100.

## 4. TESTED — frozen final broad regression

Preflight passed 18/18 before the single authorized MAX_THREAT run. Completed
suites were checkpointed and never rerun. The finished record is
`FINAL_REGRESSION.json`.

| Coverage | Raw assertions | Result |
|---|---:|---|
| Static integrity | 20/20 | PASS |
| Native 13 suites | 364/364 | PASS |
| Paired integration | 34/42 | raw FAIL; classified below |
| Paired determinism | 42/42 | PASS |
| Current EMCON UI | 14/14 | PASS |
| UI | 213/213 | PASS |
| Actual WebGL / eight launches | 29/29 | PASS |
| U4 seeker scenes | 19/19 | PASS |
| HP outcome/save contract | 19/19 | PASS |
| SEEKER_CLOSE matrix | 26/26 | PASS |
| **Total** | **780/788 raw** | **effective gate PASS** |

The eight raw differences are retained and were not rewritten:
`samePhysicalState`, `sameCombatRng`, `raidInventoryDeltaBounded`, and
`sameExistingObserverState` for each DDG/CG raid. They are all consequences of
the same documented ACTIVE decision: legacy H1 expends seven rounds immediately,
whereas OODA waits for the frozen service time and the native FCS-quality gate
then blocks release. The 32 s diagnostic window has no target/interceptor
terminal outcome. `PAIRED_ACTIVE_DELTA_CLASSIFICATION.json` classifies this as
`EXPECTED_ACTIVE_DIAGNOSTIC_DELTA` under directive §9-4; raw status remains
FAIL and the effective release gate is PASS.

- expected values updated: 0;
- tolerances changed: 0;
- game constants changed: 0;
- completed broad suites rerun: 0;
- broad wall time: 3,917.084 s.

## 5. APPROVED

- The user directive authorizes ACTIVE outcome/timing differences caused by
  documented OODA delay, priority, and native-bounded salvo policy while
  requiring every downstream safety invariant to remain intact.
- SHADOW passed before ACTIVE construction. The DDG/CG profile ledger was
  frozen before dynamic combat tests and was not tuned from results.
- The eight raw paired assertions are approved only as an expected ACTIVE
  diagnostic difference. No expectation file or tolerance was changed.
- `CONFIRMED_ONLY` is checked only for feature inactivity; its performance is
  not approved or claimed.

## 6. UNRESOLVED

The following inherited debts remain visible and are not waived:

- `CIWS_SEED_419025_FAIL`;
- `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`;
- WIP12D CIWS fixed-step scale debt;
- Chromium memory/crash and checkout-timeout debt;
- Kh-32 60 km population not run;
- `CONFIRMED_ONLY` performance unverified;
- legacy SARH self-test diagnostic debt.

The generic Integration Baseline hash policy rejects the authorized new save
field; its raw policy failure is preserved separately. The D-specific hash gate
is the governing gate for this stage and passes the exact narrowed change.

## 7. RELEASE

- `RELEASE: NO`
- Target publication is PR #80 from `defense-ooda-a` to `main`.
- The current-candidate Actions job performs exact rebuild, static/function
  boundary audit, contract/save/engine, and SHADOW/ACTIVE browser gates. It does
  not repeat the one-shot broad regression.
- Merge, release, and tag remain user decisions.

