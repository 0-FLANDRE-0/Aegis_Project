# CUE_A elevation range-estimate accuracy

Direct range is diagnostic-only; it never overwrites the tactical cue. Error uses AFTER_ACTION_TRUTH_TEST_ONLY.

| missile | cases | samples | mean case bias | median | mean case RMSE | interpretation |
|---|---:|---:|---:|---:|---:|---|
| Kh-35U | 15 | 300 | 68.64 km | 67.65 km | 129.25 km | low-elevation geometry is effectively uninformative |
| Kh-32 | 15 | 300 | 1.30 km | 1.28 km | 6.97 km | meaningful high-altitude range information |

Kh-35U cases use 10/20/30 km at 12 m; Kh-32 cases use 60/100/130 km at 10,000 m, five deterministic seeds per range and 20 samples per case.
