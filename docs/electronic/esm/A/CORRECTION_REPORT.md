# ESM_A correction checkpoint

## Outcome

The unintended tactical regression is fixed. The common ESM estimator no longer shares the legacy `r.ew.executionF.contacts` map consumed by the existing soft-kill coordinator.

- Corrected product SHA-256: `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- Corrected packed-main SHA-256: `280458afa6207bfbb2a7aa078e47445b4cd449b78b244834a5a267d4360fbbc3`
- Product bytes: `22,182,527`
- Release: `false`

## Root cause and correction

Commit B originally stored the new likelihood-estimator contacts in `r.ew.executionF.contacts`. That map is not presentation-only: the pre-existing soft-kill coordinator reads it. The estimator's deliberately conservative observable-only association therefore changed legacy contact population and final observer scheduling in the two raid cases.

The correction separates ownership:

- `r.ew.esmA.contacts`: raw-history/common AOA-TDOA-FDOA estimator, UI, network and save lifecycle.
- `r.ew.executionF.contacts`: exact native bearing-only projection used by legacy tactical consumers.

The native projection keeps the baseline association and aging rules. RF detection probability, noise, beam, LOS, EW RNG, radar, ECM, EMCON, network SELF/TRACK, weapons and damage code were not tuned or relaxed.

## Verification

All limited gates pass on regenerated diagnostic products:

| Gate | Result |
|---|---|
| Commit B anonymous DTO/localizer/native RF-RNG | PASS |
| Commit C cooperative raw network/AOA-TDOA-FDOA | PASS |
| Commit D UI/manual cue | PASS |
| Commit D predecessor B/C recheck | PASS |
| Commit E DDG/CG/synthetic/lifecycle/SOV/performance | PASS |

The corrected paired comparison has 36/42 raw exact assertions. In all six DDG/CG idle/raid/damaged cases:

- observer state exact: 6/6
- offboard state exact: 6/6
- combat RNG exact: 6/6
- hull damage/fixed layout exact: 6/6
- VLS inventory exact: 6/6
- physical state exact after removing only the newly required `state.esmA` field: 6/6

The six remaining failed assertions are all `samePhysicalState`, solely because the required ESM_A save/lifecycle field is present in the candidate and absent in EMCON_B. No expected value or tolerance was changed.

## Broad-regression evidence scope

The single allowed MAX_THREAT broad run was already consumed by candidate SHA `1f0b041b8c353f0b9014b8dd46cf144041ecb73d22698f938b1b15c87548209e`. It passed native 364/364, UI 213/213 and WebGL 29/29, but exposed the shared-contact-map defect. That evidence is retained with its actual SHA and is not relabeled as direct evidence for the corrected product.

Because the instruction prohibits repeated broad runs, no second broad run was started automatically. The corrected SHA has the complete limited gates and the targeted six-case paired comparison above.

## Status

- IMPLEMENTED: yes
- TESTED: limited B-E gates and corrected paired comparison
- APPROVED: no; user decision required for the six required save-schema deltas
- UNRESOLVED: whether one replacement broad regression is authorized for the corrected SHA
- INHERITED_DEBT: retired EMCON UI 14 assertions remain unexecuted, unchanged
- RELEASE: false
