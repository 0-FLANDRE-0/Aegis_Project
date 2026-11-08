# ESM_A implementation plan

## Boundary

One `esm-a` branch, one product and one PR implement TRACK-D's common ESM foundation. Commits A–E follow the directive without introducing ESM_B or TRACK-D1. SOV Mineral/Band Stand receive, SOV ESM UI and Moskit cue/fire remain disabled.

## Commit sequence

1. **A — merged-baseline audit:** exact EMCON_B rebuild, ownership table, frozen hashes and archive correction; no product behavior change.
2. **B — raw DTO + local AOA:** strict anonymous measurement boundary, bounded history, honest bearing/region/point/coast/lost lifecycle.
3. **C — cooperative raw network:** separate ESM_RAW reports, observable-only correlation, AOA/TDOA/FDOA constraints and AOA fallback.
4. **D — UI + cue:** historical origins, regions/ellipse/coast rendering and manual bounded area/point cue only.
5. **E — profiles + lifecycle:** DDG/CG real profile binding, receive/EA independence, save/import/reset/destroy and synthetic receiver portability.

Intermediate commits run only stage-specific deterministic gates plus unchanged-function hashes. MAX_THREAT broad regression runs once, after the final candidate is frozen.

## Predeclared SIM_TUNED constants

These values are fixed before behavioral tests. They model game uncertainty and are not fitted to outcomes.

| Name | Value | Unit | Rationale |
|---|---:|---|---|
| `historyMax` | 24 | observations/contact | bounded history under inherited 96-contact cap |
| `rangeHypothesisMinM` | 500 | m | prevents receiver-self singularity without inventing a point |
| `rangeHypothesisMaxM` | 200000 | m | finite game search region; still region-valued |
| `originBaselineMinM` | 500 | m | rejects negligible own-motion geometry |
| `crossingAngleMinDeg` | 12 | deg | avoids near-parallel AOA overconfidence |
| `geolocateMajor95MaxM` | 4000 | m | point-promotion ceiling; also compatible with existing route-plan prior |
| `coastAfterS` | 1.0 | s | visible coast before inherited 12 s contact expiry |
| `clockBiasSigmaS` | 2e-7 | s | explicit cooperative clock uncertainty (~60 m light range) |
| `clockDriftSigmaSps` | 2e-9 | s/s | nonzero receiver clock drift uncertainty |
| `arrivalTimeSigmaS` | 6e-8 | s | SIM_TUNED receiver timestamp uncertainty |
| `frequencyReferenceSigmaHz` | 2 | Hz | explicit nonzero frequency-reference uncertainty |
| `frequencyMeasurementSigmaHz` | 4 | Hz | SIM_TUNED RF frequency measurement uncertainty |
| `sourceMotionNuisanceSigmaMps` | 25 | m/s | prevents FDOA overconfidence for unknown emitter motion |
| `fingerprintGateNis` | 9 | — | 3σ observable-only fingerprint gate |
| `associationAmbiguityDeltaNis` | 1 | — | ambiguous candidates remain separate rather than forced merged |
| `rawPairWindowS` | 0.21 | s | one inherited 0.2 s receiver revisit plus numeric margin |
| `performanceBudgetMs` | 2.0 | ms/fixed step | maxContacts with three cooperative receivers |

Inherited and unchanged: receiver revisit `0.2 s`, hold `12 s`, max contacts `96`, RF Pd/noise/beam/LOS, isolated EW RNG and all radar/ECM/EMCON parameters.

## Truth and authority rules

- Truth may be read only inside physical RF/sensor synthesis. A strict whitelist produces the raw DTO.
- Raw/network/contact/save/UI/diagnostic data contain no emitter entity ID, truth position, truth velocity, faction or object reference.
- Association uses measured time, bearing/elevation, band and optional RF fingerprint with covariance only.
- ESM estimates never create observer tracks, identity, HOSTILE status, fire-control quality or automatic engagement authority.
- A manual cue retains `ESM_ESTIMATED_AREA` or `ESM_ESTIMATED_POINT` provenance and must pass existing weapon/ROE/safety gates.
