# SEEKER_UNIFY_C Stage 2 — ASM beam/LOS correction

- IMPLEMENTED: YES
- TESTED: YES
- APPROVED: USER PRE-APPROVED POLICY; FINAL MERGE NOT APPROVED
- UNRESOLVED: NONE IN STAGE 2
- RELEASE: NO

## Gate: PASS

Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html` · SHA-256 `dca6d886b9980b87d3c776e85ae4ff8839eb42128669cbc150b212e0dcaf18ec`

The audit found no public or project definition proving the legacy half-width, LOS, or 0.08 floor was already round-trip.  Per the fixed directive, the existing values are now one-way `SIM_TUNED` values and the ASM active seeker uses `TX_RX_SEPARATE`.  The numeric values themselves were not tuned.

## Results

- 1,590 matrix: 660 range + 390 SAM ARH + 120 cue + 420 ship-radar cases; page errors 0.
- False acquisitions: 20 → 17; new false acquisitions 0.
- SAM exact differences 0; ship-radar exact differences 0; RCS physical-input audit PASS.
- Target TRACK regressions: 6; all 6 captured and numerically explained.
- Full cue matrix: 30 regressions, 0 improvements; all 30 captured and numerically explained.
- S1: TRACK 40 → 40; ownship-first 0; neighbor-ASM-first 0.
- TRACK-C replay: 16 battles / 37 missiles PASS; neighboring-ASM first association 0.
- 60 battles: 60/60 PASS; first associations SHIP 320/320; neighbor/non-ship 0/0.
- Battle totals Stage 1 → Stage 2: {'kills': 301, 'leakers': 17, 'egress': 1, 'other': 1} → {'kills': 300, 'leakers': 17, 'egress': 1, 'other': 2}.  Net leakers and egress are unchanged; one net kill became a guidance-control-loss miss.
- Determinism: PASS.

## Cue TRACK totals

| Weapon | EMCON | Shots | Stage 1 TRACK | Stage 2 TRACK |
|---|---:|---:|---:|---:|
| Kh-32 | OFF | 60 | 60 | 44 |
| Kh-32 | ON | 60 | 60 | 46 |
| Kh-35U | OFF | 60 | 60 | 60 |
| Kh-35U | ON | 60 | 60 | 60 |

The Kh-32 60 km losses are the direct consequence of applying the existing one-way beam factor a second time.  The captured regression dwells have a median added factor of about 0.08 (the unchanged sidelobe floor), reducing representative median SNR from roughly 0.22 to 0.018.  No compensating sensitivity, beamwidth, threshold, RCS, or cue-basket tuning was applied.

## Evidence

- `BEAM_STAGE2_1590_COMPARISON.json`
- `BEAM_STAGE2_RANGE_NUMERIC_EXPLANATIONS.json`
- `BEAM_STAGE2_CUE_NUMERIC_EXPLANATIONS.json`
- `BEAM_STAGE2_SECONDARY_COMPARISON.json`
- `BEAM_STAGE2_EGRESS_37_RESULTS.json`
- `BEAM_STAGE2_60_BATTLE_RESULTS.json`
- `BEAM_STAGE2_RCS_AUDIT.json`
- `BEAM_STAGE2_DETERMINISM.json`

Stage 3 may start only from this PASS artifact.  Broad regression remains deferred until Stage 3 completion, as required by the directive.
