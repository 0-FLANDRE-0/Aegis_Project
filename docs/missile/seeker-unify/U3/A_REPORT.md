# SEEKER_UNIFY_U3 Commit A report

## Status

| State | Result |
|---|---|
| IMPLEMENTED | Harpoon monostatic echo power and its already-resolved anonymous observation ordering/cap are selected through the U2 profile contract. |
| TESTED | 18 representative Harpoon scenes, 55,441 echo-power comparisons, 3,615 cell-list comparisons, static hashes for 10 unchanged functions. |
| APPROVED | SHADOW and ACTIVE gates passed with byte-identical tactical results and zero unexplained difference. |
| UNRESOLVED | U3 B-D and the final broad regression are intentionally not part of this checkpoint. |
| RELEASE | Not released. Branch checkpoint only; no merge, tag, or release. |

## Ownership and lifetime audit

- The physical RF registry remains the owner of reflector inputs.
- `harpoonRfObservationsA` still owns body-relative measurement construction,
  seeker RNG calls, Pd draw, noise, and anonymous output lifetime.
- U2 receives only scalar monostatic-power inputs and a pre-resolved anonymous
  observation array. It stores neither array nor contact identity.
- The common layer consumes no RNG and returns no truth reference.
- Harpoon state machine, launch authority, save schema, memory, prediction,
  gimbal, beam, range, scan, and damage paths are unchanged.

## SHADOW to ACTIVE gate

The test matrix used six geometry branches (`40/80/120 km`, stationary or
moving surface contact, straight/45/90-degree turn) with three independent
seeds per branch. Each build ran the same 18 cases.

| Check | Result |
|---|---:|
| CUE_A-1 vs SHADOW tactical result | 18/18 bit equal |
| CUE_A-1 vs ACTIVE tactical result | 18/18 bit equal |
| SHADOW power comparisons | 55,441 |
| SHADOW power mismatches | 0 |
| SHADOW cell comparisons | 3,615 |
| SHADOW cell mismatches | 0 |
| Maximum absolute power difference | 0 |
| Page errors | 0 |

The ACTIVE path therefore replaces only the duplicated expression and sort/cap
adapter. No gameplay constant was added and no expected value or tolerance was
changed.

## Evidence

- `A_EQUIVALENCE.json`
- `A_SCOPE.json`
- `BUILD_A_SHADOW.json`
- `BUILD_A_ACTIVE.json`
- `changes-A-active.diff`
- `run_a_equivalence.py`
- `verify_a_scope.py`

