# Pre-implementation fuze/warhead matching

The B2A G7 120-case evidence contains 631 native burst-speed records. Their median is
662.851207044519 m/s. With the new fragment speed 1029.639208327432 m/s, a 280 m/s head-on
Kh-35U, 12.5 m passing distance and 2 ms processing delay give:

`theta = atan2(12.5, (662.851207044519 + 280) * (0.002 + 12.5 / 1029.639208327432))`

The fixed center is **43.155075229960°**, inside the mandatory 20–80° interval. Implementation
may continue. This is one fixed design point; it is not adapted per shot or selected from kill
results.

| Range | B2A representative burst speed | Body polar angle with new fixed center | Fragment time |
|---:|---:|---:|---:|
| 1 km | 779.354757 m/s | 98.089299° | 0.012262 s |
| 5 km | 621.541844 m/s | 87.377033° | 0.012153 s |
| 9 km | 490.348255 m/s | 79.643639° | 0.012341 s |

Exact machine-readable values and the positive-root arrival calculation are in
`model-parameters.json` and `derive_model.py`.
