# ESM_A final report

## Status ledger

| State | Result |
|---|---|
| IMPLEMENTED | Anonymous raw ESM DTO; receiver origin/velocity/covariance and clock/frequency-reference state; AOA likelihood and cooperative AOA/TDOA/FDOA; read-only main/PiP presentation; bounded operator-only Harpoon coordinate cue; DDG/CG profile receivers; save/reset/retire lifecycle. |
| TESTED | Commit B–E limited gates, predecessor recheck, corrected paired matrix, one corrected-candidate MAX_THREAT broad run, exact rebuild/static candidate gate, current EMCON UI, real WebGL. |
| APPROVED | The six `state.esmA`-only paired deltas and the one replacement broad run on corrected SHA `5dcc6201…dad7`. |
| UNRESOLVED | Sovremenny Mineral/MR-184/Band Stand adapter; any new ESM tactical consumer, automatic identity, or engagement authority; communication EMCON. |
| RELEASE | `false`; no merge, release, or tag. PR remains the user decision boundary. |

## Product

`Aegis_SIM_v48_WIP_ESM_A.html` is `22,182,527` bytes with SHA-256
`5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`.
It rebuilds from merged EMCON_B SHA-256
`50cbf50faaf434bc2af9bd182dc4fc46df56006748fdcd3a8dba8a137ccf96ee`.
The packed-main SHA-256 is
`280458afa6207bfbb2a7aa078e47445b4cd449b78b244834a5a267d4360fbbc3`.

## Implemented contract

- Raw observations contain measured receiver pose/velocity/covariance,
  measured angles/covariance, optional measured frequency/timing/fingerprint,
  quality, and timestamps. They do not carry emitter/target/entity IDs,
  faction, hostile status, or hidden truth position.
- Local association and the likelihood estimator own
  `ShipRuntime.ew.esmA.contacts`. The pre-existing bearing-only tactical
  projection independently remains in `ShipRuntime.ew.executionF.contacts`.
- Cooperative transport sends anonymous raw measurements and does not create
  observer tracks, identity, or engagement authority.
- The UI consumes a detached presentation copy. A converged estimate may only
  create an operator-requested, bounded Harpoon coordinate/area cue through the
  existing manual release gates.
- DDG-119 and CG-52 use distinct profile-bound passive receiver declarations.
  Save/import, legacy empty migration, reset, destroy, and retirement have
  explicit lifecycle handling.
- Sovremenny retains its inactive baseline: receiver profile absent, raw
  observations 0, contacts 0, network reports 0, and physical emitters 0.

## Corrected ownership defect

The first implementation reused `r.ew.executionF.contacts` for the common
likelihood estimator. That map is a legacy soft-kill coordinator input, so a
presentation/intelligence association policy unintentionally changed tactical
scheduling. The corrected product gives the estimator a separate
`r.ew.esmA.contacts` map and keeps the native projection's original association
and aging contract.

The correction did not change RF Pd/noise/RCS/beam/LOS, EW RNG, radar or ECM,
network SELF/TRACK, IFF/ROE, weapons, guidance, damage, or ship physics.
Protected function hashes remain exact.

## Limited gates

| Gate | Outcome |
|---|---|
| Commit B local DTO/AOA/RF-RNG | PASS |
| Commit C cooperative raw network and AOA/TDOA/FDOA | PASS |
| Commit D read-only UI and manual cue | PASS |
| Commit D predecessor B/C recheck | PASS |
| Commit E profile/lifecycle/SOV/performance | PASS |

Commit E also proves two-run determinism, save lifecycle, DDG/CG profile
separation, damage/offline fail-closed behavior, silent receive with zero
transmit, no observer-track/authority writes, inactive Sovremenny behavior, and
the performance budget.

## User-approved paired delta

The final EMCON_B → ESM_A paired comparison deliberately preserves the six raw
failures rather than rewriting their expected values:

- DDG idle / raid / damaged: `samePhysicalState`;
- CG idle / raid / damaged: `samePhysicalState`.

For every case the baseline has no `state.esmA`, the candidate field is
`AEGIS_ESM_SAVE_A_1`, and removing only this field makes the complete physical
state exact. The existing comparison also reports combat RNG, hull damage and
fixed layout, VLS inventory, observer state, offboard ports, and fault status
exact. The user approved this required schema-only addition. Expected values
updated: `0`; tolerances changed: `0`.

## Corrected-candidate broad regression

The earlier pre-correction broad result remains historical and is not used as
final evidence. One replacement MAX_THREAT run was authorized and executed on
the corrected product:

| Suite | Raw result | Effective result |
|---|---:|---:|
| Static integrity | 17/17 | 17/17 PASS |
| Native 13 | 364/364 | 364/364 PASS |
| EMCON_B → ESM_A paired | 36/42 | 42/42 approved schema delta |
| ESM_A determinism | 42/42 | 42/42 PASS |
| Current EMCON UI | 14/14 | 14/14 PASS |
| UI | 213/213 | 213/213 PASS |
| Actual WebGL observed world | 29/29 | 29/29 PASS |
| **Total** | **715/721** | **721/721 PASS** |

Wall time was `2,365.73 s`. The run stopped on three zero-assertion startup
interruptions and resumed at the same suite after restoring missing sparse
test inputs or correcting the identical-byte adapter root. No completed suite
was rerun. All interruption logs are retained and explicitly classified as
`PRODUCT_NOT_EXECUTED`.

The current EMCON UI adapter maps the retired `#lockBtn`/external-3D controls to
the current MAP_B/EMCON surface while preserving 14 assertions. It passes
14/14. The retired direct path is not revived or counted as a current test.

## Publication boundary

- Branch: `esm-a`.
- Candidate authority: `AEGIS_CURRENT_PRODUCT.json`, stage `ESM_A`.
- The candidate workflow rebuilds the product exactly, runs the fail-closed
  ESM static gate, E-stage Chromium gate, and current EMCON UI gate. It does
  not repeat the broad regression.
- Executable and report ZIPs are separate; the report ZIP contains no HTML.
- `main`, release, and tag remain unchanged. The user retains merge authority.

## Packages

- `Aegis_SIM_v48_WIP_ESM_A_HTML.zip`: one executable HTML.
- `Aegis_SIM_v48_WIP_ESM_A_REPORT.zip`: reports, source modules, diffs, and
  validation evidence; zero HTML files.
- `SHA256SUMS_v48_WIP_ESM_A.txt`: product and archive hashes.

Exact sizes and hashes are in `PACKAGE_MANIFEST.md` after package generation.
