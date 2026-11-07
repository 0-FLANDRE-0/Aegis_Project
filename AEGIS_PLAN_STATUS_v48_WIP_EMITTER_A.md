# AEGIS v48 WIP EMITTER_A status

- Product: `Aegis_SIM_v48_WIP_EMITTER_A.html`
- SHA-256: `04bfb9c991929bed5800e7899f2ffb79087bfd20b79300c9bb01628b7edc98c6`
- Bytes: `22146163`
- Base: merged SEEKER_UNIFY_U3 (`243c196a…8835`)
- Branch: `emitter-a`
- State: IMPLEMENTED + TESTED; PR pending user merge decision; RELEASE=false

## Completed

- Commit A: baseline audit.
- Commit B: DDG/CG declared registry in SHADOW, exact equivalence.
- Commit C: common adapter ACTIVE, save/UI/API gates.
- Commit D: existing SOV metadata registered inactive, no electronic capability.
- Final one-time MAX_THREAT broad regression: Native 364/364, paired 42/42,
  UI 213/213, WebGL 29/29 PASS; new failures 0.

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

No main direct commit, merge, release or tag is authorized by this status.
