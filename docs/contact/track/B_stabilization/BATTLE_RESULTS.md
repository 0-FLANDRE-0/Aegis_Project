# Natural battle validation — FAIL

Completed 19/19 requested pages; 0 pending. Main full-AUTO matrix: PASS. Existing strict failures remain unapproved.

Mode meaning: old SHADOW consumes TRACK-A behavior; new SHADOW consumes frozen old B ACTIVE. Proposal diagnostics are separate from actual selected/held return sets.

| Case | Version | Result | End s | HP | Water m³ | Native effects | Actual HOLD plots/tracks | Proposal HOLD plots |
|---|---|---|---:|---:|---:|---|---:|---:|
| DDG_CONVERGING_2 | A | QUALIFYING_COMPLETED_BATTLE | 17.883 | 100 | 0.000 | {"KILL": 2} | 0/0 | 0 |
| DDG_CONVERGING_2 | old SHADOW | QUALIFYING_COMPLETED_BATTLE | 17.883 | 100 | 0.000 | {"KILL": 2} | 0/0 | 0 |
| DDG_CONVERGING_2 | old ACTIVE | QUALIFYING_COMPLETED_BATTLE | 17.883 | 100 | 0.000 | {"KILL": 2} | 0/0 | 0 |
| DDG_CONVERGING_2 | new SHADOW | QUALIFYING_COMPLETED_BATTLE | 17.883 | 100 | 0.000 | {"KILL": 2} | 0/0 | 0 |
| DDG_CONVERGING_2 | new ACTIVE | QUALIFYING_COMPLETED_BATTLE | 17.883 | 100 | 0.000 | {"KILL": 2} | 0/0 | 0 |
| CG_MULTIPLE_3 | A | QUALIFYING_COMPLETED_BATTLE | 19.633 | 100 | 0.000 | {"KILL": 3} | 0/0 | 0 |
| CG_MULTIPLE_3 | old SHADOW | QUALIFYING_COMPLETED_BATTLE | 19.633 | 100 | 0.000 | {"KILL": 3} | 0/0 | 0 |
| CG_MULTIPLE_3 | old ACTIVE | QUALIFYING_COMPLETED_BATTLE | 19.633 | 100 | 0.000 | {"KILL": 3} | 0/0 | 0 |
| CG_MULTIPLE_3 | new SHADOW | QUALIFYING_COMPLETED_BATTLE | 19.633 | 100 | 0.000 | {"KILL": 3} | 0/0 | 0 |
| CG_MULTIPLE_3 | new ACTIVE | QUALIFYING_COMPLETED_BATTLE | 19.633 | 100 | 0.000 | {"KILL": 3} | 0/0 | 0 |
| DDG_BEARING_CROSSING_2 | A | QUALIFYING_COMPLETED_BATTLE | 26.933 | 100 | 0.000 | {"MISS": 4, "KILL": 2} | 0/0 | 0 |
| DDG_BEARING_CROSSING_2 | old SHADOW | QUALIFYING_COMPLETED_BATTLE | 26.933 | 100 | 0.000 | {"MISS": 4, "KILL": 2} | 0/0 | 0 |
| DDG_BEARING_CROSSING_2 | old ACTIVE | QUALIFYING_COMPLETED_BATTLE | 26.933 | 100 | 0.000 | {"MISS": 4, "KILL": 2} | 0/0 | 0 |
| DDG_BEARING_CROSSING_2 | new SHADOW | QUALIFYING_COMPLETED_BATTLE | 26.933 | 100 | 0.000 | {"MISS": 4, "KILL": 2} | 0/0 | 0 |
| DDG_BEARING_CROSSING_2 | new ACTIVE | QUALIFYING_COMPLETED_BATTLE | 26.933 | 100 | 0.000 | {"MISS": 4, "KILL": 2} | 0/0 | 0 |
| NATURAL_SATURATION_13 | A | INCOMPLETE_NOT_DECISIVE | 90.000 | 0 | 90.948 | {"MISS": 8, "KILL": 8, "DAMAGED": 1} | 0/0 | 0 |
| NATURAL_SATURATION_13 | old ACTIVE | INCOMPLETE_NOT_DECISIVE | 90.000 | 0 | 61.032 | {"KILL": 7, "DAMAGED": 2, "MISS": 1} | 494/765 | 494 |
| NATURAL_SATURATION_13 | new SHADOW | INCOMPLETE_NOT_DECISIVE | 90.000 | 0 | 61.032 | {"KILL": 7, "DAMAGED": 2, "MISS": 1} | 494/765 | 361 |
| NATURAL_SATURATION_13 | new ACTIVE | INCOMPLETE_NOT_DECISIVE | 90.000 | 0 | 33.957 | {"KILL": 6, "DAMAGED": 1, "MISS": 8} | 356/589 | 356 |

Candidate vs frozen oldACTIVE comparison (separate from A historical comparison):
- DDG_CONVERGING_2 / new SHADOW: no observed worsening in recorded hull/flood/modules/remaining-threat/native-hit indicators. Lifecycle completeness is reported separately; resource changes are recorded, not waived or tuned.
- DDG_CONVERGING_2 / new ACTIVE: no observed worsening in recorded hull/flood/modules/remaining-threat/native-hit indicators. Lifecycle completeness is reported separately; resource changes are recorded, not waived or tuned.
- CG_MULTIPLE_3 / new SHADOW: no observed worsening in recorded hull/flood/modules/remaining-threat/native-hit indicators. Lifecycle completeness is reported separately; resource changes are recorded, not waived or tuned.
- CG_MULTIPLE_3 / new ACTIVE: no observed worsening in recorded hull/flood/modules/remaining-threat/native-hit indicators. Lifecycle completeness is reported separately; resource changes are recorded, not waived or tuned.
- DDG_BEARING_CROSSING_2 / new SHADOW: no observed worsening in recorded hull/flood/modules/remaining-threat/native-hit indicators. Lifecycle completeness is reported separately; resource changes are recorded, not waived or tuned.
- DDG_BEARING_CROSSING_2 / new ACTIVE: no observed worsening in recorded hull/flood/modules/remaining-threat/native-hit indicators. Lifecycle completeness is reported separately; resource changes are recorded, not waived or tuned.
- NATURAL_SATURATION_13 / new SHADOW: no observed worsening in recorded hull/flood/modules/remaining-threat/native-hit indicators. Lifecycle completeness is reported separately; resource changes are recorded, not waived or tuned.
- NATURAL_SATURATION_13 / new ACTIVE: MORE_MODULE_DAMAGE, MORE_UNRESOLVED_INITIAL_THREATS. Lifecycle completeness is reported separately; resource changes are recorded, not waived or tuned.

Initial local tracks are zero in every captured page. Threats are native Kh-35U spawns, followed by native RF measurement, association, AUTO release and actual terminal/damage functions. No synthetic track/identity/ideal observations or test fire command is used. Native terminal causes are retained; dead alone is not a kill.

All sampler own-event/lineage/association-return drops and native core/runtime/trace errors are post-validated. Native bounded-ring overwrite is reported separately and is not mistaken for a dropped sampler event.

Shadow exact snapshot controls: 7/7 currently PASS; sampler v1→final controls: 9/9 PASS.

HOLD duration means time from an actually returned held-track decision to the next accepted native update on that receiver-local track, across sensors/routes. It is not a product/global persistent HOLD timer. counts.holds counts held-track appearances; selected pairs/held sets are stored per native call.

The main three AUTO scenarios have no actual HOLD so they establish an ordinary/crossing battle regression guard, not general HOLD-defense safety. D1 seed419012 (overall MANUAL, C55 autonomous RAM, native terminal30.63s) is a separate inherited reference and is not folded into this denominator.

Identity/merge accuracy remains UNKNOWN where only nearest-truth geometry is available. Detailed distances, closest/second margins, native filter sigma and measurementId/local-file lineage are retained. A physical pair unresolved into one RF plot and one file is not counted as a bad merge. Observed bearing-order reversal is not by itself an ID swap.

Natural component >12 coverage: OBSERVED. The deterministic anonymous native-graph stress tests are separate evidence. No geometry/gate/physics parameter is altered to force a large component.

Raw references, hashes, exact runtime source receipts and full snapshot consistency checks are in BATTLE_RESULTS.json; detailed after-action rows are in evidence/battle-analysis/DETAILS.json.gz. No product or existing expectation is modified by this harness; releaseApproved remains false.

Frozen R1 natural13 regression is under causal diagnosis. See BATTLE_CAUSE_PLAN.md, evidence/battle-analysis/NATURAL13_CAUSE.json, GUARDED_LOGGER_ORDERING.json/.md, and evidence/battle-ablation/RESULTS.json/.md. Independent ablations and diagnostic logger guards are extra tests; they do not overwrite this19-page matrix or approve its worsening indicators.

Native timeline plot: [battle-native-timelines.svg](evidence/battle-analysis/battle-native-timelines.svg). Native shipHitHistory may include zero-damage miss entries; damaging/miss callbacks and unique initial-target terminal outcomes are separate in the JSON. Present system damage0 means native zero damage, with missing keys preserved.

Executed but incomplete:
- track-a / NATURAL_SATURATION_13: HORIZON_UNRESOLVED, 1 initial threat(s) remain.
- old-active / NATURAL_SATURATION_13: HORIZON_UNRESOLVED, 1 initial threat(s) remain.
- candidate-shadow / NATURAL_SATURATION_13: HORIZON_UNRESOLVED, 1 initial threat(s) remain.
- candidate-active / NATURAL_SATURATION_13: HORIZON_UNRESOLVED, 3 initial threat(s) remain.
