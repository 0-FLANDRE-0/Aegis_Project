# INTEGRATION_BASELINE_A final-correction broad-run stop report

## Status

- Classification: `INCOMPLETE / ZERO_ASSERTION_HARNESS_STOP`
- Attempt: corrected-candidate broad run 1
- Started candidate: `Aegis_SIM_v48_WIP_INTEGRATION_BASELINE_A.html`
- Candidate bytes: `22,212,299`
- Candidate SHA-256: `655d2bdaa8e30e4788334373ea0f87d162ba4de84e1119b8c42f7ad855bd30b0`
- Threat mode: `MAX_THREAT`
- Recorded at: `2026-11-13T16:39:18+09:00`
- Rerun performed: no
- Product pass/fail conclusion: none

The one-shot corrected-candidate broad regression stopped at the first native
suite as required by the final-correction directive. `helicopter-flight`
executed `0 / 85` assertions and returned exit code `1`; no following suite was
started and the attempt was not rerun.

## Observed result

| Stage | Result |
|---|---:|
| Static integrity | `17 / 17 PASS` |
| `helicopter-flight` | `0 / 85`, exit `1` |
| Later suites | not run |
| Broad summary | `complete: false` |

This is a harness/preflight failure, not evidence of a game-product regression.
The traceback ends in `FileNotFoundError` for the tracked baseline product:

`archive/v48/WIP_HELI_CG_A/Aegis_SIM_v48_WIP_HELI_CG_A.html`

The Git object exists in the candidate commit (`16,078,336` bytes, SHA-256
`c94306a78a22b6ba87711ec78089316eadcb289286abb0bbb7d784e433f120f3`),
but the active sparse-checkout excluded archive HTML files. The preflight checked
the common Python modules but did not check this transitive HTML fixture.

## Preserved evidence

| Evidence | SHA-256 |
|---|---|
| `FINAL_CORRECTION_REGRESSION.json` | `ff182e03c0762f54dfa2c20cdcbd10bce2dbef9ae6427e05c10855e94635956d` |
| `static-integrity.json` | `2514d34148d90428d9251fb222fccde51061f3c2de4c4de3292772f258d2a0ce` |
| `source-provenance.json` | `f7873c05c9fda649ac4de005121240e4aa8498adabefac91682777f8e40cadbb` |
| `helicopter-flight.log` | `b435101a58209b7437f37c8de65318dd4cfb4ac86078fe76bd95b031359289e3` |
| `helicopter-flight-execution.json` | `17871565ab6f60201b34eb7cff9e30f9539fe813940515aeb93c6eee291e8306` |
| `helicopter-flight/test-migration.json` | `ac719c12e84ed407a25e86cf41496ee6b0f0a98497b69f81d964df9a3f363338` |

The raw log, partial summary, provenance, and execution record are deliberately
kept under `evidence/final-correction/final-regression/`. They must not be
relabelled as a passing corrected-candidate broad regression.

## Required decision before another broad run

Per the directive, a zero-assertion suite requires stopping and reporting rather
than retrying. A future attempt requires explicit user approval after restoring
the missing pinned archive fixture and extending preflight to all transitive
fixture products. No expected value, tolerance, game constant, or candidate
product byte was changed in response to this stop.
