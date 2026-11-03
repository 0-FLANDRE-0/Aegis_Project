# U0 stage gate

## Status header

- IMPLEMENTED: time-expanded TargetCue basket with independent range/bearing clocks and existing profile search-sector cap
- TESTED: cue 240 x baseline/SHADOW/ACTIVE, S1 100, primary matrix 1,590, deterministic replay 10 x 3, reference battles 60
- APPROVED: constants frozen before effect tests; existing `searchSectorAzDeg` used as the azimuth ceiling
- UNRESOLVED: pre-launch observation age; Harpoon time-aged basket deferred to U3
- RELEASE: no release; PR only

Overall: **PASS**

```json
{
  "cueShadowAndActive": true,
  "azimuthUsesProfileCap": true,
  "s1NoRegressionOrOwnshipFirst": true,
  "matrix1590": true,
  "determinismAndGlobalRng": true,
  "harpoonAuditOnly": true,
  "battleReferenceComplete": true,
  "neighborAsmFirstAssociationZero": true,
  "nonShipFirstAssociationZero": true
}
```

## Key results

- U0 cue regressions: 0
- U0 cue improvements: 44
- after-action failure categories: {}
- profile azimuth-cap violations: 0
- 1,590 matrix: PASS; new false acquisitions 0
- S1: PASS; ownship first selections 0
- deterministic result hashes: 2d4e41744fd7d554669acf4a755b19022c0b0505f5c5eb4b57937fca9643df4f, 2d4e41744fd7d554669acf4a755b19022c0b0505f5c5eb4b57937fca9643df4f, 2d4e41744fd7d554669acf4a755b19022c0b0505f5c5eb4b57937fca9643df4f
- 60-battle reference: 60/60, totals={'kills': 301, 'leakers': 17, 'egress': 1, 'other': 1}, neighbor ASM first=0, non-ship first=0

Broad regression is intentionally not run at U0: the user supplement requires it exactly once after the final stage, or at the stop point.
