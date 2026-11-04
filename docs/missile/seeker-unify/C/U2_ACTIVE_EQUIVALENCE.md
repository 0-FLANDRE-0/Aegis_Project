# U2 ACTIVE legacy-equivalence gate

Status: **PASS**

## Frozen implementation

- ASM WIP22: combined-single beam/LOS, power-weighted RMS extent, separate-axis angular clustering.
- SAM ARH: separate transmit/receive beam and LOS, maximum-member extent, spherical member-preserving clustering.
- Provenance: `LEGACY_EQUIVALENCE`; no hardware claim and no new tuned coefficient.
- U2 SHADOW double computation and dynamic audit arrays were removed.

## Results

| Gate | Cases | Result | Differences | Page errors |
|---|---:|---|---:|---:|
| Six seeker paths × 200 | 1,200 | PASS | 0 | 0 |
| Representative ASM/cue/SAM matrix | 78 | PASS | 0 | 0 |
| Determinism (10 jobs × same/fresh page) | 3 identical runs | PASS | 0 | 0 |
| Browser-visible non-target function hashes | 1,025 | PASS | 0 | 0 |

The 1,200-case run covered Kh-35U, Kh-32, Harpoon, SARH/ESSM Block 2 ARH, SM-6 Block IA ARH (air and surface), and RAM. Exact serialized results were equal. Elapsed time was 2,650.17 seconds.

The 78-case matrix covered 30 ASM, 12 cue, and 36 SAM cases. Exact tactical outputs were equal. U2 reported `ACTIVE`, active components `synthesizeEchoes` and `resolveCells`, zero SHADOW components, zero dynamic audit arrays, no RNG consumption, and no truth output.

## Initial candidate failure and correction

The first candidate stopped before tactical case 1 because synchronous core self-tests accessed the frozen U2 option object before its lexical initialization. The option object was moved ahead of those self-tests; no option, arithmetic, coefficient, RNG path, or tactical rule changed. `U2_STAGE1_INIT_FAILURE.md` preserves the evidence.

Stage 1 therefore meets the directive's bit-equality gate and Stage 2 may begin.

