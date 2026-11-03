# Effective surface-reflector RCS audit

All values are square metres. They are audit outputs, not additional tuning
inputs. The DDG/CG own-ship table was measured from the product's production
`computeShipRCS` path at 10 km in the default diagnostic sea state, using the
actual ship heading for 0° bow, 90° beam and 180° stern. `TOP` uses the same
beam bearing at 10 km altitude. The test-only module is inverse-removable and
its build receipt is `DIAGNOSTIC_PRODUCT_V4_BUILD.json`.

## Own ship: section, LOS, aspect and top weighting applied

| Profile | Band | Bow | Beam | Stern | Top |
|---|---:|---:|---:|---:|---:|
| DDG-119 Flight IIA | S | 1,031.81 | 2,897.48 | 919.96 | 2,322.55 |
| DDG-119 Flight IIA | X | 1,811.40 | 5,086.68 | 1,615.03 | 4,077.36 |
| DDG-119 Flight IIA | I/J | 1,868.32 | 5,246.51 | 1,665.78 | 4,205.48 |
| CG-52 Ticonderoga | S | 33,006.25 | 93,077.12 | 33,852.94 | 74,608.45 |
| CG-52 Ticonderoga | X | 57,944.23 | 163,401.84 | 59,430.64 | 130,979.10 |
| CG-52 Ticonderoga | I/J | 59,764.91 | 168,536.13 | 61,298.03 | 135,094.63 |

The public-formula beam anchor is applied before the unchanged section LOS,
top-view and sea-state multipliers. Consequently the observed total can differ
slightly from the bare anchor while retaining the original relative section
distribution.

## NPC DDG/CG aspect envelope

The preserved curve is `(0.10 + 0.36*abs(sin(aspect))) / 0.46`, so the first
number is bow/stern and the second is beam.

| Profile | S range | X range | I/J range |
|---|---:|---:|---:|
| DDG-119 Flight IIA | 592.04–2,723.39 | 1,039.36–4,781.05 | 1,072.02–4,931.28 |
| CG-52 Ticonderoga | 19,018.40–87,484.65 | 33,387.82–153,583.97 | 34,436.91–158,409.77 |

## Project 956 NPC aspect envelope

The offline model-registration LUT is unchanged: projected area is 354 at
0°/180°, 2,034 at 90°/270°, with 15° samples and linear interpolation. It is
normalized by the 90° entry. The resulting ranges are:

| Band | Bow/stern | Beam |
|---|---:|---:|
| S | 11,182.43 | 64,251.61 |
| X | 19,631.36 | 112,797.12 |
| I/J | 20,248.20 | 116,341.35 |

## Empty-container test hulk

The five existing aspect nodes remain in their original order and ratio.

| Band | Five aspect nodes |
|---|---|
| S | 25,191.31 / 77,373.31 / 341,882.06 / 91,768.34 / 41,385.72 |
| X | 40,922.19 / 136,407.31 / 600,192.16 / 159,791.42 / 72,101.01 |
| I/J | 40,920.32 / 141,647.25 / 619,050.95 / 170,501.32 / 76,069.82 |

Generic SMALL/MEDIUM/LARGE contacts remain unchanged at bow/beam/stern
`7/38/12`, `28/180/48`, and `110/780/190` m² respectively. Chaff, Nulka and
distributed sea clutter are not ships and were excluded from the formula.

