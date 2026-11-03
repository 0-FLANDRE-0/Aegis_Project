# Surface-ship RCS sources

## Result

No official or peer-reviewed absolute RCS measurement for the individual
DDG-119, CG-52, or Project 956 variants was found.  The implementation
therefore does **not** label any class RCS as a public measured value.  It uses
one public ship-scale formula for absolute scale, public full-load displacement
for the three real classes, and preserves the game's pre-existing relative
aspect/section curves.

| Source | Evidence used | Tag |
|---|---|---|
| M. I. Skolnik, “An Empirical Formula for the Radar Cross Section of Ships at Grazing Incidence,” *IEEE Transactions on Aerospace and Electronic Systems*, AES-10(2), 1974, DOI [10.1109/TAES.1974.307935](https://doi.org/10.1109/TAES.1974.307935) | `sigma = 52 sqrt(f_MHz) D_kt^(3/2)` square metres; grazing-incidence ship-scale reference | `PUBLIC_FORMULA` |
| FAS, [DDG-51 Arleigh Burke-class](https://man.fas.org/dod-101/sys/ship/ddg-51.htm) | Sloped surfaces and reduced radar signature are qualitative evidence for a reduction relative to the unmodified empirical scale; no dB number is asserted | `PUBLIC_QUALITATIVE` |
| FAS, [CG-47 Ticonderoga-class](https://man.fas.org/dod-101/sys/ship/cg-47.htm) | 9,600 long-ton full load class figure and Spruance-derived conventional form; no class RCS number | `PUBLIC_VALUE`, `PUBLIC_QUALITATIVE` |
| [Arleigh Burke-class public specification table](https://en.wikipedia.org/wiki/Arleigh_Burke-class_destroyer) | Flight IIA 9,500 long tons full load, converted to 9.6524456336 thousand metric tonnes | `PUBLIC_VALUE` |
| [Sovremenny-class public specification table](https://en.wikipedia.org/wiki/Sovremenny-class_destroyer) | 7,940 t full load | `PUBLIC_VALUE` |
| In-game empty-container hulk mass, 24,200 t | test object has no public class analogue | `SIM_TUNED` |

## Frequencies and reduction

The formula is evaluated independently at S=3,050 MHz, X=9,400 MHz, and
I/J=10,000 MHz.  S and X use existing public-value radar profile frequencies.
The exact anti-ship seeker carrier is not public in this build, so 10 GHz is an
explicit `SIM_TUNED` X/I-J-band centre.

The Burke reduction is 15 dB `SIM_TUNED`: the midpoint of a deliberately
recorded 10–20 dB design assumption informed only by public qualitative shaping
evidence.  It was fixed before running acquisition or combat diagnostics and
was not fitted to any range result.  CG-52 and Project 956 retain 0 dB formula
reduction because no defensible class-specific public reduction was located.

## Computed beam references (m²)

| Profile | S | X | I/J | Formula reduction |
|---|---:|---:|---:|---:|
| DDG-119 Flight IIA | 2,723.39 | 4,781.05 | 4,931.28 | 15 dB |
| CG-52 Ticonderoga | 87,484.65 | 153,583.97 | 158,409.77 | 0 dB |
| Project 956 | 64,251.61 | 112,797.12 | 116,341.35 | 0 dB |
| Empty-container test hulk | 341,882.06 | 600,192.16 | 619,050.95 | 0 dB |

These are normalization anchors, not constant omnidirectional signatures.
Existing bow/quarter/beam/stern and top/section weighting still determines the
instantaneous value supplied to the common RF echo field.

