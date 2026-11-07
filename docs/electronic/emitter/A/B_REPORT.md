# EMITTER_A Commit B — DDG/CG SHADOW report

## Status

- IMPLEMENTED: immutable profile equipment emitter registries for DDG-119 and CG-52; common read-only runtime resolver; SHADOW comparator.
- TESTED: deterministic profile matrix, mixed/same-class NPC scenes, receiver anonymous plots and RNG, profile isolation, existing HOJ and passive candidate selection.
- APPROVED: directive-defined compatibility values and categories only. ACTIVE authority is not enabled in this commit.
- UNRESOLVED: SOV registration is intentionally deferred to Commit D. C55/SPQ AIR inherited scope is unchanged.
- RELEASE: no release/tag; branch checkpoint only.

## Contract

The equipment registry owns immutable declarations only. Mutable enable, EMCON,
rotor, health/damage, EW request and resource allocation state continues to come
from the existing `ShipRuntime` observer/EW owners. No second mutable state or
new power unit was introduced. Compatibility values remain SPY 2500, SPQ 650,
NAV 120 and ECM `2000 * resourceUsed`.

Registry categories are distinct from `emitterClass`: `AIR_SEARCH`,
`SURFACE_SEARCH`, `NAV`, `FIRE_CONTROL`, and `ECM`. DDG and CG equipment ids are
profile-specific; current physical output order remains SPY → SPQ → NAV → ECM.

## Gate result

`B_GATE.json` is PASS. All 13 checks passed:

- legacy output matrices byte-for-value exact;
- DDG→CG, CG→DDG, DDG→DDG and CG→CG receiver plots and RNG exact;
- SHADOW comparisons executed with zero mismatch and no RNG consumption;
- legacy output remained tactical authority;
- four-entry registries validated and were deeply frozen;
- DDG SPQ-9B/BridgeMaster E and CG SPQ-9/SPS-73 remained isolated;
- existing runtime owners were used with `duplicateMutableState=false`;
- U3 HOJ and passive RF candidate-selection diagnostics were unchanged.

The first gate invocation exposed only a diagnostic-harness error: top-level
lexical `ACTIVE_SHIP_PROFILE` was read as a `window` property. The harness was
corrected to consume the public profile/entity identifiers already returned by
the baseline diagnostic. No product code changed for that correction.

See `SCOPE_B.json` for the named-function hash boundary and
`changes-B-shadow.diff` for the generated packed-main source diff.
