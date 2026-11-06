# SEEKER_UNIFY_C Stage 3 — CUE_A results

Status: **PASS**

- Stage 2 cases: 240
- Stage 3 cases: 480 (MAX_THREAT + CONFIRMED_ONLY)
- Page errors: 0
- Azimuth-basket/search-sector violations: 0

## Gates

- PASS — `allFourShardsPresent`
- PASS — `caseCount`
- PASS — `uniqueCases`
- PASS — `stage2Coverage`
- PASS — `noPageErrors`
- PASS — `azBasketNeverExceedsSearchSector`
- PASS — `insideSearchOutsideBasketDidNotIncrease`

## Stage 1 → Stage 2 → Stage 3 by launch range

Each range cell is TRACK/cases. This is launch-range outcome, not a truth-derived in-flight range.

| missile / EMCON | Stage 1 | Stage 2 | Stage 3 MAX_THREAT | Stage 3 CONFIRMED_ONLY |
|---|---|---|---|---|
| Kh-32 / EMCON_OFF | 60km 20/20 · 100km 20/20 · 130km 20/20 | 60km 4/20 · 100km 20/20 · 130km 20/20 | 60km 0/20 · 100km 20/20 · 130km 20/20 | 60km 4/20 · 100km 20/20 · 130km 20/20 |
| Kh-32 / EMCON_ON | 60km 20/20 · 100km 20/20 · 130km 20/20 | 60km 6/20 · 100km 20/20 · 130km 20/20 | 60km 4/20 · 100km 20/20 · 130km 20/20 | 60km 4/20 · 100km 20/20 · 130km 20/20 |
| Kh-35U / EMCON_OFF | 60km 20/20 · 100km 20/20 · 130km 20/20 | 60km 20/20 · 100km 20/20 · 130km 20/20 | 60km 20/20 · 100km 20/20 · 130km 20/20 | 60km 20/20 · 100km 20/20 · 130km 20/20 |
| Kh-35U / EMCON_ON | 60km 20/20 · 100km 20/20 · 130km 20/20 | 60km 20/20 · 100km 20/20 · 130km 20/20 | 60km 20/20 · 100km 20/20 · 130km 20/20 | 60km 20/20 · 100km 20/20 · 130km 20/20 |

## Stage 2 → Stage 3

| Mode | TRACK | hit | inside-sector/outside-basket | delta | regressions | improvements |
|---|---:|---:|---:|---:|---:|---:|
| CONFIRMED_ONLY | 210 → 208 | 198 → 198 | 0 → 0 | +0 | 4 | 2 |
| MAX_THREAT | 210 → 204 | 198 → 198 | 0 → 0 | +0 | 7 | 1 |

## Launch velocity and disconnected DL hook

| label | time | launch velocity | position error | range sigma | az half |
|---|---:|---|---:|---:|---:|
| Kh-35U | 60 s | null | -900.0 m | 1244.2 m | 5.00° |
| Kh-35U | 120 s | null | -1800.0 m | 3069.4 m | 5.27° |
| Kh-35U | 180 s | null | -2700.0 m | 5848.7 m | 10.04° |
| Kh-35U | 60 s | known | 0.0 m | 620.6 m | 5.00° |
| Kh-35U | 120 s | known | 0.0 m | 2184.0 m | 5.00° |
| Kh-35U | 180 s | known | 0.0 m | 4872.6 m | 8.15° |
| Kh-32 | 60 s | null | -900.0 m | 1244.2 m | 5.00° |
| Kh-32 | 120 s | null | -1800.0 m | 3069.4 m | 5.27° |
| Kh-32 | 180 s | null | -2700.0 m | 5848.7 m | 10.04° |
| Kh-32 | 60 s | known | 0.0 m | 620.6 m | 5.00° |
| Kh-32 | 120 s | known | 0.0 m | 2184.0 m | 5.00° |
| Kh-32 | 180 s | known | 0.0 m | 4872.6 m | 8.15° |

Disconnected production DL: `false`; diagnostic hook update: `PASS`.

`failureAudit` classification is AFTER_ACTION_TRUTH_TEST_ONLY and is never consumed by cue, seeker, association, or guidance code.
