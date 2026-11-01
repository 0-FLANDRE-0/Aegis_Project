# GUN_B2B parameter provenance

This stage remains a fictional game model (`SIM_TUNED`). Public references constrain selected
inputs; they do not turn the simulation into a claim about weapon performance.

| Input | Value used | Tag and source |
|---|---:|---|
| Mk 80 projectile mass | 30.7 kg | `PUBLIC_SPEC`; [NavWeaps 5"/54 Mark 45](https://www.navweaps.com/Weapons/WNUS_5-54_mk45.php) and [Wikipedia summary](https://en.wikipedia.org/wiki/5-inch/54-caliber_Mark_45_gun) |
| Explosive load | 3.7 kg Comp B | `USER_SELECTED_PUBLIC_SUMMARY`; Wikipedia reports this value. NavWeaps instead reports about 3.515 kg Composition A-3 for most conventional rounds, so the disagreement is retained here rather than hidden. |
| Fragmenting case mass | 25 kg (sensitivity 24–26 kg) | `SIM_TUNED`; 30.7 − 3.7 leaves 27 kg. No verifiable public component masses for the fuze, driving band, base and other non-fragmenting parts were found in this review, so 2 kg is reserved for them. |
| Comp B specific weight | 0.0621 lb/in³ | `PUBLIC_REF`; SAND94-2255, *A Design Guide and Specification for Small Explosive Containment Structures*, table 5. |
| Comp B Gurney constant | 9,100 ft/s = 2,773.68 m/s | `PUBLIC_REF`; SAND94-2255 table 5. UN IATG 01.80 table 21 independently gives 2,774 m/s. |
| Comp B Mott B | 0.0554 lb^1/2 in^-7/6 | `PUBLIC_REF`; SAND94-2255 table 6. |
| Mott geometry | 127 mm OD, 80.499 mm equivalent ID, 23.251 mm wall, 422.938 mm effective length | `SIM_TUNED_EQUIVALENT_CYLINDER`; case and charge volumes are preserved using 7,800 kg/m³ mild steel and the cited Comp B specific weight. These are not claimed to be measured Mk 80 wall dimensions. |
| V50 reference fragment | 1.1 g | `SIM_TUNED_MAPPING_FROM_PUBLIC_REFERENCE`; NIJ 0117.01 table 8 specifies a nominal 1.1 g .22-caliber fragment-simulating projectile. The game's existing Kh-35U/Kh-32 V50 values have no documented reference mass, so assigning them to this mass is a stated game-model assumption. |

The Mott equation follows the dimensionally consistent form also reproduced in European
Commission JRC119310, annex A:

`MA = B * t^(5/6) * di^(1/3) * (1 + t/di)`, `mu = MA²`, `N0 = M/(2mu)`.

SAND94-2255 PDF: <https://digital.library.unt.edu/ark:/67531/metadc1271718/m2/1/high_res_d/10120233.pdf>

UN IATG 01.80: <https://data.unsaferguard.org/iatg/en/V3_IATG-01.80_en.pdf>

JRC119310: <https://publications.jrc.ec.europa.eu/repository/bitstream/JRC119310/00surveyprobits_final-1.pdf>

NIJ 0117.01: <https://www.ojp.gov/pdffiles1/nij/249560.pdf>

## Remaining SIM_TUNED assumptions

- Equivalent-cylinder geometry and 25 kg fragmenting mass.
- Mapping the existing target V50/width values to the 1.1 g reference mass.
- All fragmenting mass remains in the existing 90° ±20° body-frame band; no undocumented
  out-of-band loss factor is introduced.
- The existing game impact-speed proxy `hypot(fragmentSpeed, relativeSpeed)` is retained.
- The old `coneAspectFactor` and SAM-derived cluster treatment are not used for this natural
  Mott population. Band membership already supplies the body-frame geometry, and the Mott
  fragments are counted as independent expected fragments.

The projectile's in-flight mass remains the existing 31.75 kg. The 25 kg value belongs only to
the terminal fragment/Gurney calculation.
