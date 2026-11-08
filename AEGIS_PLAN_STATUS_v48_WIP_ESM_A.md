# AEGIS v48 WIP ESM_A status

- Base: merged EMCON_B `main@babb4d7f6d42cc8d774feadce17d8108b3a24040`
- Baseline product: `Aegis_SIM_v48_WIP_EMCON_B.html`
- Baseline SHA-256: `50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee`
- Branch: `esm-a`
- Product: `Aegis_SIM_v48_WIP_ESM_A.html`
- Candidate: `22,182,527` bytes / SHA-256 `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- State: IMPLEMENTED + TESTED + user-approved schema delta; RELEASE=false

## Delivered scope

- anonymous passive-RF observations with historical receiver origin and
  covariance;
- single-platform AOA likelihood and multi-platform AOA/TDOA/FDOA;
- cooperative raw-observation transport without track/identity/fire authority;
- read-only main/PiP information and an operator-only bounded Harpoon cue;
- DDG-119 and CG-52 receiver profile binding;
- explicit save, legacy migration, reset, destroy, and retirement lifecycle;
- corrected separation of common estimator contacts from the legacy tactical
  bearing projection.

## Validation

- Commit B/C/D/D-predecessor/E gates: PASS.
- Corrected MAX_THREAT broad run: effective `721/721` PASS.
- Native: `364/364`; candidate determinism: `42/42`; current EMCON UI:
  `14/14`; UI: `213/213`; actual WebGL: `29/29`.
- Baseline compatibility is raw `36/42`; all six failures are exactly the
  user-approved `state.esmA` schema field. Removing only that field restores
  complete physical-state equality, with RNG/damage/ammunition/observer/
  offboard equality retained.
- Expected values updated: 0. Tolerances changed: 0.

## Boundaries

- Sovremenny Mineral/MR-184/Band Stand ESM integration is not implemented.
- ESM results do not implicitly enter existing soft-kill/hard-kill tactical
  decisions and do not grant automatic engagement authority.
- The retired direct EMCON UI path was not revived; its current 14-assertion
  mapping passes.
- `main`, merge, release, and tag are unchanged pending user decision.

Detailed evidence is in `docs/electronic/esm/A/FINAL_REPORT.md` and
`docs/electronic/esm/A/FINAL_REGRESSION_CORRECTED.json`.
