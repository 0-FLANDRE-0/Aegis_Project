# U0 results

## Status header

- IMPLEMENTED: TargetCue accessor, independent cue clocks, SHADOW/ACTIVE hard basket
- TESTED: 240-case cue matrix for each of baseline, SHADOW, and ACTIVE
- APPROVED: constants frozen by commit `3bdcde42ce8deac0d6962e6b50ddedcfde7991b8`
- UNRESOLVED: pre-launch track age remains unavailable
- RELEASE: no release; PR only

Overall: **PASS**

- SHADOW outcome differences: 0
- baseline TRACK to U0 unexplained/defect failure: 0
- baseline TRACK to justified outside-search-sector failure: 0
- baseline failure to U0 TRACK: 44
- azimuth basket cap violations: 0
- passive clock update/attempt: 167882/175356 (95.74%)

## ACTIVE failure classification (after-action truth only)

```json
{}
```

## Kh-35U, EMCON OFF

| Range | Motion | Baseline TRACK | U0 TRACK |
|---:|---|---:|---:|
| 100 km | 15 kn straight | 5/5 | 5/5 |
| 100 km | 30 kn straight | 1/5 | 5/5 |
| 100 km | 30 kn + 30 deg | 2/5 | 5/5 |
| 100 km | 30 kn + 90 deg | 5/5 | 5/5 |
| 130 km | 15 kn straight | 4/5 | 5/5 |
| 130 km | 30 kn straight | 0/5 | 5/5 |
| 130 km | 30 kn + 30 deg | 0/5 | 5/5 |
| 130 km | 30 kn + 90 deg | 5/5 | 5/5 |

## Kh-35U, EMCON ON

| Range | Motion | Baseline TRACK | U0 TRACK |
|---:|---|---:|---:|
| 100 km | 15 kn straight | 5/5 | 5/5 |
| 100 km | 30 kn straight | 1/5 | 5/5 |
| 100 km | 30 kn + 30 deg | 1/5 | 5/5 |
| 100 km | 30 kn + 90 deg | 3/5 | 5/5 |
| 130 km | 15 kn straight | 4/5 | 5/5 |
| 130 km | 30 kn straight | 0/5 | 5/5 |
| 130 km | 30 kn + 30 deg | 0/5 | 5/5 |
| 130 km | 30 kn + 90 deg | 0/5 | 5/5 |

## Basket at first TRACK (or first ACQUIRE if TRACK was absent)

```json
{
  "rangeLowM": {
    "min": 7948.602362249469,
    "median": 27496.122292050415,
    "max": 59543.22185364458,
    "count": 240
  },
  "rangeHighM": {
    "min": 21315.916994331776,
    "median": 35392.32575701927,
    "max": 75782.28235918401,
    "count": 240
  },
  "azHalfDeg": {
    "min": 5,
    "median": 5,
    "max": 25.50742021931632,
    "count": 240
  },
  "rangeAgeS": {
    "min": 2.633333333333329,
    "median": 102.78333333332878,
    "max": 402.96666666662884,
    "count": 240
  },
  "bearingAgeS": {
    "min": 0.01666666666665151,
    "median": 5.633333333333013,
    "max": 402.96666666662884,
    "count": 240
  }
}
```
