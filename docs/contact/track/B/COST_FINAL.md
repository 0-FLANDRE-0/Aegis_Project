# TRACK-B final quiescent cost measurement

Measurement procedure: **PASS**, 9/9 configurations complete in **151.946 s**. This is evidence completion only; performance and release approval remain false.

Both shared browser leases were held throughout the matrix. Each configuration used one fresh browser; no other browser main existed before a run or after close. The six CPU runs used the original 30 simulated-second moving-helicopter warmup and 2,400 unwrapped native ticks. Allocation used the original two-owner fixture, 120 warmup ticks and 600 measured ticks.

| Run | Configuration | Mean ms/tick | Median | p95 |
|---|---|---:|---:|---:|
| 0 | A OFF | 1.9067 | 1.8000 | 2.9000 |
| 0 | B OFF | 1.8593 | 1.7000 | 2.9000 |
| 0 | B ON | 1.9342 | 1.8000 | 3.0000 |
| 1 | B ON | 1.9153 | 1.8000 | 3.0000 |
| 1 | B OFF | 1.8350 | 1.7000 | 2.8000 |
| 1 | A OFF | 1.8347 | 1.7000 | 2.9000 |

Within repetition 0, B OFF versus A OFF mean cost was −2.487%; within repetition 1 it was +0.018%. B ON versus B OFF was +4.025% and +4.373%. Two repetitions do not establish a general speedup or a statistically significant production overhead. Every raw tick cost and outlier is retained.

| Allocation configuration | Sampled-byte estimate | Sample records | Mean ms/tick* | p95* |
|---|---:|---:|---:|---:|
| A OFF | 1,091,086,792 | 33,235 | 2.9853 | 5.7000 |
| B OFF | 1,090,727,088 | 33,225 | 3.0053 | 5.2000 |
| B ON | 1,091,883,456 | 33,259 | 3.1850 | 5.8000 |

The allocation figures are **statistical sampled-byte estimates**, not exact allocation totals. CDP used interval 32,768 and explicitly included objects collected by major and minor GC. Raw heap profiles are retained. The net live-heap deltas are separately labelled and are not allocation-churn measurements. *Allocation-run tick times include profiling and pass-through counters, so use the unwrapped CPU matrix for CPU assessment.

| Allocation configuration | Nested surface calls / inclusive ms | Parent surface-position calls / inclusive ms | AIR / Cartesian calls |
|---|---:|---:|---:|
| A OFF | 21 / 0.700 | 21 / 0.900 | 0 / 0 |
| B OFF | 21 / 1.000 | 21 / 1.400 | 0 / 0 |
| B ON | 21 / 1.000 | 21 / 1.400 | 0 / 0 |

These counters wrap exactly one original native evaluation. Nested inclusive times overlap and must not be summed. They cover both actual owners together; no per-owner or unexercised AIR-kernel cost is inferred. This is the original short fixture, not a dense raid stress test.

All six CPU passive-state hashes match, and all three two-owner allocation hashes match. Both owners advanced exactly once per fixed tick. Read-only queries preserved the original passive state; wrappers were restored before the awaited ENV status check; ENV hashes matched; core self-test/browser errors were zero. The passive hash uses exactly the unchanged A helper’s explicit navigation, HP/inventory, canonical track covariance, entity whitelist and global/private RNG fields. No optional survival/body preview, geometry or lazy cache getter was added.

Cgroup memory events remained unchanged: `oom=48`, `oom_kill=8`, `max=2191`. Both browser leases were verified free after completion. Frozen products and `verify_runtime.py` (`a173e069…5523`) are unchanged.

Earlier concurrent-load/retained-only samples remain intact under `evidence/runtime/` and are labelled `NOT_FINAL_FOR_COST_ASSESSMENT` by `COST_CONTEXT_NOT_FINAL.json`. Two preliminary follow-up fixture attempts are preserved under `evidence/attempts/cost-final-body-accessor/` and `cost-final-body-preview-aborted/`; neither is included in this fresh nine-run matrix. No raw final samples were discarded.

Machine-readable data: `evidence/cost-final/SUMMARY.json`, `ASSESSMENT.json`, `PROVENANCE.json`; all individual costs, immediate benchmark snapshots, passive states and allocation profiles are present in the same directory.
