# ESM_A status

- Branch: `esm-a`
- Baseline: merged EMCON_B `main@babb4d7f6d42cc8d774feadce17d8108b3a24040`
- Product: `Aegis_SIM_v48_WIP_ESM_A.html`
- Product bytes: `22,182,527`
- Product SHA-256: `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- Implementation: Commits A–E plus corrected estimator/tactical-contact ownership split
- Final corrected MAX_THREAT broad regression: PASS, effective `721/721`
- Expected values updated: `0`
- Tolerances changed: `0`
- Release: `false`

## Status ledger

| State | Result |
|---|---|
| IMPLEMENTED | Anonymous raw passive-RF observations; local AOA likelihood; cooperative raw AOA/TDOA/FDOA; read-only UI; bounded manual Harpoon coordinate cue; DDG/CG receiver profiles; save/reset/retire lifecycle. |
| TESTED | B/C/D/D-predecessor/E limited gates; corrected paired comparison; one authorized corrected-candidate MAX_THREAT broad run; current EMCON UI; exact rebuild/static candidate gate. |
| APPROVED | The six raw `samePhysicalState` deltas caused solely by the new `state.esmA` save field; one replacement broad run on the corrected product. |
| UNRESOLVED | Sovremenny Mineral/MR-184/Band Stand receiver integration; any new ESM tactical consumer or automatic engagement authority; communication-EMCON policy. |
| RELEASE | `false`; no merge, release, or tag. PR and remote Actions remain the user decision boundary. |

## Final regression

The corrected run completed in `2,365.73 s` and retained every raw result:

- static integrity: `17/17`;
- native 13 suites: `364/364`;
- EMCON_B → ESM_A paired: raw `36/42`, effective `42/42` after the explicit user-approved schema classification;
- ESM_A → ESM_A determinism: `42/42`;
- current EMCON UI: `14/14`;
- UI: `213/213`;
- actual WebGL observed world: `29/29`.

The six raw failures are exactly DDG/CG × idle/raid/damaged
`samePhysicalState`. Removing only `state.esmA` makes the complete physical
state exact in all six cases; combat RNG, hull damage/fixed layout, VLS
inventory, observer state, offboard state, and fault status are also exact.

Three zero-assertion sparse-checkout/startup interruptions are retained in the
evidence and were resumed without rerunning any completed suite. They are not
product failures and are not counted as additional broad runs.

The retired direct `#lockBtn`/external-3D EMCON test was not revived. Its
current-contract 14-assertion MAP_B adapter ran and passed; the retired direct
path remains recorded as inherited test debt.

See `FINAL_REPORT.md` and `FINAL_REGRESSION_CORRECTED.json` for the complete
scope and evidence ledger.
