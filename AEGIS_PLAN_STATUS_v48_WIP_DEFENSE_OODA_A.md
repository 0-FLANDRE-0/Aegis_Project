# AEGIS v48 WIP — DEFENSE_OODA_A status

## Publication

- Branch: `defense-ooda-a`
- Base main: `68911e39eb2e1bd1196bbe7c3bedfb4ad9312fc2`
- Base product: `Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html`
- Result: `Aegis_SIM_v48_WIP_DEFENSE_OODA_A.html`
- Result bytes/SHA-256: `22,226,343` / `1d2b25cd22813c0187d8578e1cd1489f821222674ecb01cddd344f98da88d13d`
- Pull request target: #80 (`defense-ooda-a` → `main`)
- Merge/release/tag: none

## IMPLEMENTED

- DDG/CG use one ShipProfile-driven owner-local OODA engine with fixed-step
  OBSERVE/ORIENT/DECIDE/READY service, bounded queue, slots, urgent pre-emption,
  aging, crew/damage capacity, and frozen modernization pacing.
- `DEFENSE_OODA_A` is ACTIVE at only the four frozen H1 upper-decision consumer
  boundaries. Commands remain advisory and native-salvo bounded.
- A3, Network G, FCS/SPG, reserve, re-engagement, EMCON, damage, release,
  H1 radar/EW, H2/H3/H4, and C55 local CIWS authority remain native.
- `AEGIS_DEFENSE_OODA_STATE_A1` preserves bounded owner-local service state
  across save/load; invalid import is zero-mutation and legacy saves migrate to
  clean state.
- Read-only DEBUG/API diagnostics expose provider, phase, capacity, slots,
  queue, ready time, reason, fallback, and rejection counts.

## TESTED

- A–D contract/engine/SHADOW/ACTIVE gates pass. SHADOW preceded ACTIVE.
- Function boundary: 30/31 protected functions exact versus the integration
  baseline; only authorized `exportOperationalState` save-field wiring changes.
- ACTIVE browser: both DDG/CG owner directions, repeat exact, release before
  READY 0, MANUAL/HOLD launch 0, fallback/rejection/truth/RNG failure 0,
  console/page error 0.
- Natural Kh-35U controls: both ships release two native ESSM rounds after
  READY and record `PROX_DETONATION_KILL`, ship hits 0.
- Frozen final MAX_THREAT broad run: 788/788 executed, 780 raw pass and eight
  preserved paired-raid ACTIVE differences; §9-4 effective failures 0.
- Current EMCON 14/14, UI 213/213, WebGL 29/29, U4 19/19, HP 19/19,
  SEEKER_CLOSE 26/26.
- Expectations updated 0; tolerances changed 0; game constants changed 0.

## APPROVED

- Profile values were frozen before dynamic combat tests and retain
  `SIM_TUNED_GAMEPLAY_NOT_REAL_CIC_SPEC` provenance.
- The eight raw paired differences are retained as raw FAIL and classified
  `EXPECTED_ACTIVE_DIAGNOSTIC_DELTA`: legacy expends seven rounds immediately;
  ACTIVE waits for frozen OODA service and then respects downstream
  `FCS_QUALITY`. No safety authority was bypassed.
- Natural sensor terminal controls demonstrate normal READY→release→kill for
  both ship profiles.

## UNRESOLVED

- `CIWS_SEED_419025_FAIL`
- `CG_VS_FRIENDLY_PAIRED_OBSERVER_DELTA_2`
- WIP12D CIWS fixed-step scale debt
- Chromium memory/crash and checkout-timeout debt
- Kh-32 60 km population not run
- `CONFIRMED_ONLY` performance unverified
- legacy SARH self-test diagnostic debt

## RELEASE

- `RELEASE: NO`
- Current-candidate Actions performs exact rebuild and limited contract/
  SHADOW/ACTIVE gates only; it does not repeat the one-shot broad regression.
- PR creation is allowed. Merge, release, and tag remain user decisions.
