# GUN_B2B private test assertion migration

The repository's original B1 tests are unchanged. `prepare_tests.py` creates private adapted
copies for this selected HTML.

Only the two user-approved physical-adapter assertions change semantics:

| Old assertion | B2B assertion |
|---|---|
| `nativeFinish`: this fixed stochastic draw must kill the Harpoon | the native AIRBURST result contains a numeric Pk, proving that the native damage path ran |
| `nativeAfterActionJournal`: a kill termination must be written | the recorded native result is one of `KILL`, `MISS`, or `DAMAGED` |

The Harpoon position, 12.5 m offset, seed, RCS, projectile state, coefficients and damage RNG are
unchanged. All other adapted assertions and tolerances are the B2A private fixtures. Exact
machine diffs and hashes are in `ASSERTION_MIGRATIONS.json` and `adapted/*.diff`.
