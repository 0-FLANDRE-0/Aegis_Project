# Paired raid Stage attribution

- Status: `PASS`
- Product code changes in Stage 0: `0`
- Expected-value/tolerance changes: `0 / 0`
- Truth use: post-run diagnostic attribution only

| Ship | Check | B | C Stage 2 | C final | Attributed change |
|---|---|---|---|---|---|
| CG_52_LATE_TICONDEROGA | samePhysicalState | 27d44382cfec… | 27d44382cfec… | e072ab4596b9… | C_STAGE2_TO_C_FINAL |
| CG_52_LATE_TICONDEROGA | sameCombatRng | 1655152390 | 1502733940 | 2996625611 | B_TO_C_STAGE2, C_STAGE2_TO_C_FINAL |
| CG_52_LATE_TICONDEROGA | raidInventoryDeltaBounded | 114 | 114 | 115 | C_STAGE2_TO_C_FINAL |
| CG_52_LATE_TICONDEROGA | sameExistingObserverState | cba2be8e815e… | 1cc8687d69aa… | 5f372e79d934… | B_TO_C_STAGE2, C_STAGE2_TO_C_FINAL |
| DDG_119_LATE_FLIGHT_IIA | samePhysicalState | 9ed852060561… | 9ed852060561… | a9feb1256331… | C_STAGE2_TO_C_FINAL |
| DDG_119_LATE_FLIGHT_IIA | sameCombatRng | 619673995 | 1502733940 | 2945097295 | B_TO_C_STAGE2, C_STAGE2_TO_C_FINAL |
| DDG_119_LATE_FLIGHT_IIA | raidInventoryDeltaBounded | 90 | 90 | 88 | C_STAGE2_TO_C_FINAL |
| DDG_119_LATE_FLIGHT_IIA | sameExistingObserverState | 43d054f9a47e… | ad7d20cd37ba… | 3480c40b6179… | B_TO_C_STAGE2, C_STAGE2_TO_C_FINAL |

## Gate results

- productHashesMatchDirective: `True`
- harnessErrorsZero: `True`
- shipsExact: `True`
- stage2ReplayExact: `True`
- allEightFinalChangesAttributed: `True`
- safetyChecksRemainTrue: `True`
