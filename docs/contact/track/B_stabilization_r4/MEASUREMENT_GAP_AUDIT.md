# Actual-combat correspondence: measurement gap and offline audit

This audit can measure logged one-to-one consistency and sampled geometric changes. It cannot certify zero physical false merges, duplicate physical tracks, or identity swaps. Those three physical counts remain **UNKNOWN**, represented as JSON `null`, rather than zero.

No browser, product code, old capture, coefficient, expectation, sensor input, or game save was changed. The tool has no gameplay consumer. All truth use is `AFTER_ACTION_TEST_ONLY` after capture completion.

## Existing observations and their limits

The unchanged sampler is `../B_stabilization/battle.js`, particularly `observe()` at lines 32–38, initial ASM creation at line 44, and the returned record at line 49. The transport decoder is `../B_stabilization/battle.py:55`; `decode_battle_capture.py` documents the original export receipts. The R3 runner is `../B_stabilization_r3/evidence/battle-active-pilot/run.py`. Its diagnostic extensions do not add a physical emitter identity to each recorded measurement.

| Existing field | Available evidence | Boundary |
|---|---|---|
| Sample `step`, `timeS` | Common collection instant | Not a serialized EKF state/prediction epoch |
| Track `kf6` | SI estimated x/y/z and vx/vy/vz | A filter state, not a physical observation or true identity |
| Track `Pdiag` | Six marginal variances | No covariance correlations; cannot reconstruct native NIS or calibrated joint confidence |
| `sensorAge`, `_lastMeasurementStep` | Existing measurement recency metadata | Neither proves the prediction epoch; no offset correction is introduced |
| `truthAfterAction` | Position/velocity/alive of each initially spawned ASM | Omits other world entities, weapons, clutter, and reflector composition |
| `associationReturns` | Logged selected plot index/track ID for each solver return | Logical local mapping; no physical emitter witness; TRACK-A contains no such return records |
| `observedPlotLineage` | Observed measurement ID and logical track update, observed dimensions/noise | Only approximately first five seconds; no emitter ID, RF unresolved-mixture witness, or full-battle physical lineage |
| Track ID/number | Stable logical labels in sampled states | A unique number does not prove that its physical referent stayed the same |

The 13-ASM captures below have 1-second sample gaps. The 6-ASM captures are sampled at 1Hz plus a forced final sample (last gap approximately 0.317s for A/B/R3 and 0.100s for R4). Initial NATURAL_SATURATION_13 threats are 80m apart along nearly the same bearing, with the same label, initial speed and altitude. Later native maneuvers can reduce separation to approximately 2.324m. Equal labels, birth ordering, nearest position, and one-to-one matching therefore cannot serve as independent physical identity evidence.

## Computation: descriptive residuals without a new association model

`after_action_correspondence.py` reads the existing lossless decoder. It validates the outer gzip-envelope hash/byte length where present, stored original/decoded browser receipt equality, omitted-record counts, and decoded row counts. It records the raw, codec, script and captured native-function hashes. Stored JavaScript `JSON.stringify` receipts are preserved; this Python audit does not claim to reexecute the browser's stringify operation independently.

For each finite track state at a recorded sample, the tool compares it with **every explicitly alive initial ASM** at that same recorded sample. It writes all Cartesian position residual components, 3D/horizontal distance, velocity residual components, and individual `residual / sqrt(Pdiag)` values. These marginal standardized components are not a diagonal-NIS substitute, pass/fail gate, probability, or physical assignment.

It also writes:

- The geometrically nearest and runner-up initial-ASM reference and their distance margin. No threshold selects a “correct” correspondence.
- Changes in that nearest reference, with sample gap, old-reference survival and whether the whole live reference set stayed identical. A change caused by a killed reference disappearing is retained and explicitly distinguished.
- Groups of logical tracks sharing the same nearest reference. This is a reproducible geometric fact, **not a confirmed physical duplicate**.
- Per-return repeated plot indices/track IDs, and separately repeated track IDs in a sampled track table. Multiple updates in different turns are not counted as duplicate use.

No interpolation, trajectory extrapolation, timestamp repair, truth correction, Hungarian assignment, fixed distance threshold, uncertainty multiplier, or acceptance coefficient is added. Invalid/missing covariance is left unknown. Truth without an explicit alive flag is not silently treated as live. Dead entities' last positions are excluded from the live-reference comparison.

## Historical and final R4 results

Raw inputs and every output checksum are in `evidence/after-action-reference-audit/INDEX.json` and each label's `SUMMARY.json`. These are descriptive samples from the existing captures, not new game runs.

| Capture | Snapshots / track rows | Distinct logical IDs | Logged returns / one-to-one violations | Nearest-reference changes (same live set) | Shared-nearest group appearances | Median / maximum nearest residual, m |
|---|---:|---:|---:|---:|---:|---:|
| TRACK-A, 13 ASM | 91 / 784 | 13 | Not instrumented | 49 (6) | 100 | 6.654 / 1891.565 |
| Original TRACK-B ACTIVE, 13 ASM | 91 / 962 | 13 | 5304 / 0 | 46 (5) | 98 | 5.856 / 1359.192 |
| R1 candidate cause capture, 13 ASM | 91 / 858 | 14 | 4744 / 0 | 45 (9) | 106 | 5.846 / 2390.964 |
| R3 candidate, 13 ASM | 91 / 1109 | 16 | 5204 / 0 | 55 (26) | 163 | 6.268 / 1274.383 |
| Final R4 candidate, 13 ASM | 91 / 1133 | 17 | 4669 / 0 | 59 (36) | 193 | 7.101 / 3558.613 |
| TRACK-A, moderate 6 ASM | 47 / 292 | 7 | Not instrumented | 19 (4) | 20 | 5.756 / 935.159 |
| Original TRACK-B ACTIVE, moderate 6 ASM | 47 / 292 | 7 | 3180 / 0 | 17 (2) | 20 | 5.887 / 935.432 |
| R3 candidate, moderate 6 ASM | 47 / 292 | 7 | 3186 / 0 | 17 (2) | 20 | 5.819 / 935.485 |
| Final R4 candidate, moderate 6 ASM | 47 / 292 | 7 | 3331 / 0 | 13 (4) | 20 | 5.760 / 866.616 |

All 13-ASM captures ended `HORIZON_UNRESOLVED` at 90s. The moderate captures ended `ALL_INITIAL_ASMS_TERMINAL_PLUS_5S`. Different surviving threat sets, lingering tracks and time on record affect these counts. The table does not rank physical identity accuracy or establish a causal regression.

Final R4-13 still has four initially spawned threats alive and own HP 0. Final R4-6 terminates at 45.1s with five `INTERCEPT_KILL` and one `NORMAL_HIT`, own HP 0 and flooding 0.2429106334538965m³. Original B-6 has own HP 7.674369445732054 and flooding 0; R3-6 has HP 7.404279277316576 and flooding 0. R4-6 is therefore an actual adverse combat outcome and is **not approved**. Its lower descriptive nearest-reference-change count does not offset or explain that regression. This audit does not modify the damage RNG, claim a physical-identity cause, or approve changed expectations.

The raw final R4 captures are `evidence/battle-active-pilot/candidate-active-NATURAL_SATURATION_13.json.gz` and `evidence/battle-final-matrix/candidate-active-NATURAL_SATURATION_6.json.gz`, pinned in the audit index. The separately closed R3-6 capture is `../B_stabilization_r3/evidence/battle-active-six/candidate-active-NATURAL_SATURATION_6.json.gz`.

For example, R1 and R3 logical track `300000009` changes nearest reference from initial ASM 20 to 22 between 13s and 14s, while the live reference set stays the same. Its nearest residual is about 4–7m at those endpoints. This is an observable **sampled geometric reassignment candidate** requiring investigation; the capture cannot establish which physical reflector generated each intervening noisy measurement. It must not be reported as either “proved identity swap” or “no identity swap.”

In contrast, the first shared-nearest group at 12s contains a lingering track about 89m from ASM 4 and another track about 5m from ASM 4, after an earlier reference was killed. Counting that pair automatically as two tracks of one live missile would manufacture a duplicate finding.

## User-facing completion categories

| Requested property | What these captures support | Final status permitted |
|---|---|---|
| Same plot/track used twice in a logged solver return | Direct enumeration for instrumented B returns | Observed 0 violations, within those recorded returns only |
| Duplicate logical track ID in a sampled table | Direct enumeration | Observed 0 in these samples; no claim about unsampled instants |
| Physical false merge | No full physical measurement/composite-echo witness | UNKNOWN |
| Duplicate tracks of the same physical contact | Shared-nearest risk groups only; incomplete world coverage | UNKNOWN |
| Physical ID swap / physical referent continuity | Nearest-reference changes and continuous residuals only | UNKNOWN |
| Per-plot physical lineage over the full battle | First-five-second logical lineage has no emitter witness | UNMEASURED |
| Friendly helicopter/ASM reliability in these specific captures | Captures contain only initially spawned hostile ASM truth references | Not covered by this audit |

The one-to-one assertion and the physical-correspondence status must be shown separately in the final report. R4's finalizer change cannot by itself close the physical-identity measurement gap.

## Reexecution and outputs

The final append used unchanged script SHA-256 `852c80700b1c5aaec774fdc8e79a2cc229116748fca8cfe7b2af1f9588767a80`, all six historical inputs plus `r3-candidate-6`, `r4-candidate-13`, and `r4-candidate-6`. The full nine-input command is saved in `evidence/after-action-reference-audit/TOOL_VALIDATION.json`. New inputs must retain the sampler/transport schema; no browser or product modification is needed. `INDEX.json` pins the actual input bytes. A different seed, fixture, source build, or sampling cadence must retain its own label rather than overwrite a historical comparison label.

Each label contains `SUMMARY.json`, `track-snapshots.csv`, `all-reference-pair-residuals.csv`, `sample-coverage.csv`, `nearest-reference-changes.json`, and `shared-nearest-reference-groups.json`. The complete pair CSV allows later investigation without recomputing or hiding an unselected candidate.

Audit-tool checks cover missing covariance, unknown/dead truth, retirement-induced nearest changes, shared-nearest groups, per-return versus cross-turn uniqueness, residual arithmetic, and no input mutation. Six checks pass. The final nine-capture audit's 55 generated files were byte-identical on reexecution and all raw input hashes were unchanged; see `TOOL_VALIDATION.json`. These are tool checks, not additions to official game regression counts. `evidence/CORRESPONDENCE_CATEGORY_RESULTS.json` separates logical uniqueness, continuous geometric descriptors, unknown physical correspondence and the independently recorded adverse R4-6 combat outcome in a compact machine-readable result.

Closing the physical gap would require a separately reviewed test-only measurement-origin/composite-echo witness, full state epochs and appropriate capture cadence. Such evidence must remain detached after-action data. None is fabricated or added to any current game path here.
