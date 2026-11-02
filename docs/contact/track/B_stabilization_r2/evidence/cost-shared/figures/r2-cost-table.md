# Isolated R2 cost and remaining limits

Source: `docs/contact/track/B_stabilization_r2/evidence/cost-shared/cost-r2.json`; SHA-256 `4eafe260c9b80e05614fa7ce73c90daa734c2bf899a817cc07f9107f28bb8ed3`.
Host tag: **shared**. Instrumented Node host proxy; this is not game FPS or a battle regression.

Original unchanged R1 diagnostic status: **FAIL**, exit 1. Raw failures: localized_ambiguity_13, localized_ambiguity_16, localized_ambiguity_32, localized_ambiguity_64.

New R2 intention contracts: **PASS**; official game regression count: 0.

| Workload | R1 updated/held | R2 updated/held | R2 native calls/run | Mean ms | p95 ms | Hold meaning |
|---|---:|---:|---:|---:|---:|---|
| sparse_chain_clear_13 | 13/0 | 13/0 | 1 | 0.279 | 0.344 | — |
| dense_equal_13 | 0/13 | 0/13 | 1 | 0.618 | 0.743 | EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| localized_ambiguity_13 | 11/2 | 11/2 | 4 | 0.688 | 0.810 | LOCAL_EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| embedded_greedy_trap_13 | 12/1 | 13/0 | 1 | 0.384 | 1.085 | — |
| sparse_chain_clear_16 | 16/0 | 16/0 | 1 | 0.239 | 0.329 | — |
| dense_equal_16 | 0/16 | 0/16 | 1 | 0.775 | 0.850 | EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| localized_ambiguity_16 | 14/2 | 14/2 | 4 | 0.666 | 0.837 | LOCAL_EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| embedded_greedy_trap_16 | 15/1 | 16/0 | 1 | 0.206 | 0.250 | — |
| sparse_chain_clear_32 | 32/0 | 32/0 | 1 | 0.554 | 0.839 | — |
| dense_equal_32 | 0/32 | 0/32 | 1 | 2.532 | 3.004 | EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| localized_ambiguity_32 | 30/2 | 30/2 | 4 | 2.331 | 3.138 | LOCAL_EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| embedded_greedy_trap_32 | 31/1 | 32/0 | 1 | 0.538 | 0.795 | — |
| sparse_chain_clear_64 | 64/0 | 64/0 | 1 | 1.922 | 2.544 | — |
| dense_equal_64 | 0/64 | 0/64 | 1 | 11.842 | 13.241 | EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| localized_ambiguity_64 | 62/2 | 62/2 | 4 | 9.697 | 13.480 | LOCAL_EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| embedded_greedy_trap_64 | 63/1 | 64/0 | 1 | 1.630 | 1.830 | — |
| sparse_chain_clear_128 | 128/0 | 128/0 | 1 | 5.255 | 6.142 | — |
| dense_equal_128 | 0/128 | 0/128 | 1 | 52.235 | 59.611 | EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| localized_ambiguity_128 | 126/2 | 126/2 | 4 | 41.014 | 53.181 | LOCAL_EQUAL_INPUT_COST_EVIDENCE_AMBIGUITY |
| embedded_greedy_trap_128 | 127/1 | 128/0 | 1 | 5.201 | 5.361 | — |
| actual13_step158 | 3/10 | 13/0 | 12 | 1.210 | 1.489 | — |
| no_C_globally_unique13 | 0/13 | 0/13 | 1 | 0.528 | 0.643 | COMPUTATIONAL_CERTIFICATE_INCOMPLETE_DESPITE_GLOBALLY_UNIQUE_INPUT |

The no-C13 input is globally unique in the exact native reference but remains held by R2. This is computational certificate incompleteness, not equal input evidence and not a resolved issue.
The captured13 workload records every internal native call shape/time; first timed run:13×26 global once plus10×20 residual eleven times. R1 single-validation times are retained separately in CSV and are not mixed into R2 timed means.
