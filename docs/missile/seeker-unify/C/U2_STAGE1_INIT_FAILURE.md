# Stage 1 initial candidate initialization failure

The first frozen candidate (`77227e4757d605a75be19d13a2dcac9c99d612e1`) did not enter the 1,200-case candidate run. The baseline completed all 1,200 cases with zero page errors; candidate page initialization timed out before case 1.

Console evidence:

```text
ReferenceError: Cannot access 'SEEKER_U2_PROFILE_OPTIONS' before initialization
    at seekerSynthesizeMonostaticPowerU2
    at _arhNormalizedMonostaticPower
    at runCoreUnitSelfTests
```

Cause: the common function declaration was hoisted, while its frozen lexical profile-options object was initialized near the end of the packaged script. Synchronous core self-tests call `_arhNormalizedMonostaticPower` earlier during script evaluation.

Correction: initialize the frozen common U2 core immediately before the extracted ASM strategy, which is earlier than all synchronous core self-tests. No profile option, arithmetic, RF coefficient, RNG path, or tactical rule changed. The failed candidate produced no tactical test result and is not treated as an expected-value change.

