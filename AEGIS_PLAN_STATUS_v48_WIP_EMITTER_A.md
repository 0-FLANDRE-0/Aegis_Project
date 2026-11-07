# AEGIS v48 WIP EMITTER_A status

- Product: `Aegis_SIM_v48_WIP_EMITTER_A.html`
- SHA-256: `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`
- Bytes: `22146163`
- Base: merged SEEKER_UNIFY_U3 (`243c196a…8835`)
- Branch: `emitter-a`
- State: IMPLEMENTED + TESTED; [PR #73](https://github.com/0-FLANDRE-0/Aegis_Project/pull/73) OPEN, pending user merge decision; RELEASE=false

## Completed

- Commit A: baseline audit.
- Commit B: DDG/CG declared registry in SHADOW, exact equivalence.
- Commit C: common adapter ACTIVE, save/UI/API gates.
- Commit D: existing SOV metadata registered inactive, no electronic capability.
- Final one-time MAX_THREAT broad regression: Native 364/364, paired 42/42,
  UI 213/213, WebGL 29/29 PASS; new failures 0.
- PR closure: ACTIVE legacy resolver calls 0, declared calls once per ship;
  SHADOW retains both calls and legacy authority. Closure call/RNG/output,
  performance, clean-clone portability and strict candidate gates PASS.
- Dedicated `AEGIS current candidate` Actions
  [run 42373876872](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/42373876872)
  PASS. The pre-closure broad run was not repeated or relabelled.

## Preserved

- sensor RF/Pd/noise/RCS/beam physics;
- receiver anonymous plot and RNG contracts;
- mutable ShipRuntime observer/EW ownership;
- IFF, ROE, weapons, damage, AI and save schema;
- U3 HOJ and passive RF selection behavior.

## Not completed here

- SOV real emitters/sensors/EW;
- category/equipment-level EMCON UI and policy (EMCON_B);
- inherited debts listed in `docs/electronic/emitter/A/FINAL_REPORT.md`.

PR #73 is open. No main direct commit, merge, release or tag is authorized by this status.
