# Stage 3 CUE TRACK delta explanations

Status: **PASS**

This is a reporting-only AFTER_ACTION audit. No value from this file is read by the simulation.

| seed / motion | class | in-basket dwells | closest delta | end evidence | ship hit |
|---|---|---:|---:|---|---|
| 729302 / 30 kt / 0° | ASSUMED_PASSIVE_RF_SCAN_HISTORY_DELTA | 892/893 (99.888%) | 0.003 m | DISTRIBUTED_BACKGROUND_EVIDENCE | False → False |
| 729302 / 30 kt / 30° | ASSUMED_PASSIVE_RF_SCAN_HISTORY_DELTA | 892/892 (100.000%) | 0.083 m | BELOW_DETECTION | False → False |
| 729302 / 30 kt / 90° | ASSUMED_PASSIVE_RF_SCAN_HISTORY_DELTA | 884/884 (100.000%) | 0.414 m | DISTRIBUTED_BACKGROUND_EVIDENCE | False → False |
| 729304 / 15 kt / 0° | COVARIANCE_CUE_SCAN_HISTORY_DELTA | 1086/1086 (100.000%) | 8.313 m | DISTRIBUTED_BACKGROUND_EVIDENCE | False → False |

All rows kept the target inside the search basket and ended as the same no-hit PASSED_TARGET outcome. The lost diagnostic TRACKs are deterministic scan-history changes in weak RF evidence, not a new inside-search/outside-basket failure. No compensating threshold or seeker tuning was applied.
