# Harpoon basket audit

## Status header

- IMPLEMENTED: no Harpoon product-code change
- TESTED: 60/100/120 km x four target motions x five deterministic seeds
- APPROVED: audit-only scope from the B directive
- UNRESOLVED: time-aged Harpoon search basket is deferred to U3
- RELEASE: audit evidence only

The fixture advances a detached RGM-84D receiver at the existing profile cruise speed and calls the unchanged `harpoonSeekerA` RF observation, independent RNG, scan, validation, gate, and state-machine path. Contact/damage physics is intentionally excluded because this audit measures acquisition, not impact.

| Range | Motion | TRACK |
|---:|---|---:|
| 60 km | 15 kn straight | 5/5 |
| 60 km | 30 kn straight | 5/5 |
| 60 km | 30 kn + 30 deg | 5/5 |
| 60 km | 30 kn + 90 deg | 5/5 |
| 100 km | 15 kn straight | 5/5 |
| 100 km | 30 kn straight | 5/5 |
| 100 km | 30 kn + 30 deg | 5/5 |
| 100 km | 30 kn + 90 deg | 0/5 |
| 120 km | 15 kn straight | 5/5 |
| 120 km | 30 kn straight | 5/5 |
| 120 km | 30 kn + 30 deg | 5/5 |
| 120 km | 30 kn + 90 deg | 0/5 |

## Finding

Straight motion and 30-degree turns remain inside the existing velocity-propagated launch memory and acquire in all tested cells. A 90-degree turn fails at 100 and 120 km (0/5) because lateral displacement from the frozen launch velocity exceeds the fixed 4,000 m search basket. This is the same information-age class of problem as U0, but Harpoon has its own memory/covariance/route contract and is deliberately left for U3.
