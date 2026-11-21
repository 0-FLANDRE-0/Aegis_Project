# DEFENSE_OODA_A Commit D — ACTIVE gate report

## Frozen candidate

- Product: `Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html`
- Bytes: `22,226,343`
- SHA-256: `1d2b25cd22813c0187d8578e1cd1489f821222674ecb01cddd344f98da88d13d`
- Packed main index: `13`
- Packed JS bytes: `40,996,998`
- Packed JS SHA-256: `3bc49d064eb4b2b1832c93a7ca0af79cd799acdef644c5ae0ce266ec6a7df211`
- Builder rebuild: byte-exact
- Commit C rebuild SHA-256: `2892bf1b54fc7ea5f18d98bde768b985614c11bcbd42d328691fe6c994048034` (frozen C evidence remains reproducible)

## IMPLEMENTED

- Provider selection is `DEFENSE_OODA_A / ACTIVE` only in builder stage D.
- The frozen four H1 upper judgment consumer boundaries use the owner-local OODA command. Radar/EW ownership and every downstream authority/release gate remain native.
- Provider validation accepts only the frozen provider enum. Invalid/stale OODA commands retain the native fallback path and increment explicit diagnostics.
- A DEBUG-page `DEFENSE OODA 상태` control exposes a read-only owner summary: provider/mode/phase, capacity, slots, queue, next-ready step/game seconds, last reason, fallback, and rejection counts.
- The UI is injected only for stage D. It has no timer and performs no simulation write.
- The read-only API adds `statusText()` in D without exposing a mutable runtime root.

## TESTED

### ACTIVE browser gate

Evidence: `D_ACTIVE_GATE.json`, seed `481803`, Chromium `156.0.8078.79`, Playwright `1.62.1`.

- Both own/ally orderings were executed twice: DDG-own/CG-ally and CG-own/DDG-ally.
- Repeated deterministic view: exact.
- Actual command provider for both owners: `DEFENSE_OODA_A`.
- First READY/release steps:
  - DDG own: READY 60, CG ally READY 120, first release 120.
  - CG own: READY 120, DDG ally READY 84, first release 120.
- Release before own READY: 0.
- MANUAL own release delta: 0. Foreign HOLD fire delta: 0.
- Fallback: 0 for all owners/scenes. Rejected command: 0. Validation/RNG/truth audit failures: 0.
- Owner-local rows, current-track-only rows, command-field whitelist, native/local CIWS independence: pass.
- Network downstream gate was not bypassed (`NETWORK_PROTECTED_IDENTITY` was retained where applicable).
- Diagnostic dialog and API text existed; opening/closing the dialog changed no simulation/OODA state.
- Console/page errors: 0.

### Save and deterministic engine gates

- `D_CONTRACT_GATE.json`: DDG/CG own+ally state, legacy migration, invalid import zero-mutation, active round-trip exact: pass.
- `D_ENGINE_GATE.json`: repeat exact, DDG/CG slots, degradation/unavailable, queue 64/overflow, urgent preemption, local-ID continuity, mid-phase save/load, MANUAL HOLD, native salvo upper bound/re-engagement, invalid/stale rejection, downlink provenance-only, 1x/8x/16x fixed-step exact, RNG unchanged: pass.
- `D_BOUNDARY_STATIC_GATE.json`: truth/RNG/execution/save calls absent from the advisory boundary and call direction preserved: 12/12 pass.

### Function hash gate

Evidence: `FUNCTION_HASHES_D.json`, `D_FUNCTION_HASH_GATE.json`.

- Protected functions: 31.
- Versus the corrected integration baseline: 30/31 exact; only `exportOperationalState` changes to add the optional owner-local OODA save field.
- `wip118BuildEngagementControl` is exact versus the corrected integration baseline. Its difference versus HP_A is the already-approved immutable integration port.
- All A3, Network G, FCS/SPG/resource/re-engagement, EMCON/damage/release, C55/CIWS, H2/H3/H4 protected functions are exact.
- Eleven boundary functions have exact definition counts. Six intentional changes are the active provider adapter/validation set; the five input/freeze/forbidden projection functions are exact.
- The pre-existing generic Integration Baseline gate rejects any save-export change; that expected policy mismatch is preserved as `D_FUNCTION_HASH_GATE_LEGACY_POLICY_FAIL.json`. The D-specific gate records and validates the narrower authorized save change.

## APPROVED

- Commit C SHADOW gate passed before ACTIVE construction (`C_SHADOW_GATE_ATTEMPT_7.json`).
- SHADOW forbidden differences were zero and frozen C rebuild remains byte-exact.
- The fixed profile values and gameplay source tag remain unchanged.
- No expectation value, tolerance, weapon, sensor, damage, or tactical coefficient was changed for D.

## UNRESOLVED / pending final gate

- The frozen final candidate still requires the single authorized `MAX_THREAT` broad regression after full fixture/assertion/browser preflight.
- Actual WebGL, current EMCON UI, speed/save/UI-wide regression evidence will be taken from that one final run; the D-limited browser gate does not claim to replace it.
- Inherited debts remain: `CIWS_SEED_419025_FAIL`, `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`, WIP12D CIWS fixed-step scale debt, Chromium memory/crash and checkout timeout debt, Kh-32 60 km population not run, `CONFIRMED_ONLY` performance unverified, and legacy SARH self-test diagnostic debt.

## RELEASE

- `false` — no merge, release, or tag. Final one-shot regression, packaging, remote readback, Actions, and PR are not part of this D checkpoint and remain pending.
