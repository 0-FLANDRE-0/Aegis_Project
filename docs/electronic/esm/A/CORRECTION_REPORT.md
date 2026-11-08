# ESM_A correction closure

## Outcome

The shared-contact tactical regression is fixed and the corrected candidate is
fully validated.

- Product SHA-256: `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- Packed-main SHA-256: `280458afa6207bfbb2a7aa078e47445b4cd449b78b244834a5a267d4360fbbc3`
- Product bytes: `22,182,527`
- Release: `false`

## Root cause and correction

The initial Commit B candidate stored the new likelihood-estimator contacts in
`r.ew.executionF.contacts`, which is consumed by the pre-existing soft-kill
coordinator. The corrected ownership is:

- `r.ew.esmA.contacts`: common raw-history/likelihood estimator, UI, network,
  manual cue, and save lifecycle;
- `r.ew.executionF.contacts`: unchanged native bearing-only projection used by
  legacy tactical consumers.

RF detection probability, noise, beam, LOS, EW RNG, radar, ECM, EMCON,
network SELF/TRACK, weapons, damage, and tactical authority were not tuned or
relaxed.

## User-approved schema delta

The corrected paired comparison retains six raw `samePhysicalState` failures,
one for each DDG/CG idle/raid/damaged case. The user approved them as the
required `state.esmA` save-schema addition. The final runner independently
proved in every case that:

- the baseline has no `state.esmA`;
- the candidate field has schema `AEGIS_ESM_SAVE_A_1`;
- removing only that field makes the complete physical state exact;
- combat RNG, damage/fixed layout, ammunition, existing observer state,
  offboard ports, and fault status remain exact.

No expected value or tolerance was changed.

## Replacement broad regression

The earlier broad run on pre-correction SHA `1f0b041b…82409e` remains
historical evidence only. The user authorized exactly one replacement
MAX_THREAT broad run on the corrected product. It completed with no effective
failures:

| Suite | Result |
|---|---:|
| Static integrity | 17/17 PASS |
| Native 13 | 364/364 PASS |
| Baseline compatibility | raw 36/42; effective 42/42 approved schema delta |
| Candidate determinism | 42/42 PASS |
| Current EMCON UI | 14/14 PASS |
| UI | 213/213 PASS |
| Actual WebGL | 29/29 PASS |

Three zero-assertion test-input startup interruptions were preserved and the
same run resumed at the failed suite. No completed suite was repeated. The
interruptions were missing sparse-checkout inputs or an adapter-root mismatch;
the product was not executed in those attempts.

## Closure state

- IMPLEMENTED: yes
- TESTED: yes, including the authorized corrected-candidate broad run
- APPROVED: schema-only paired deltas and replacement broad execution
- UNRESOLVED: Sovremenny ESM equipment and all new tactical/automatic consumers
- RELEASE: false; no merge, release, or tag
