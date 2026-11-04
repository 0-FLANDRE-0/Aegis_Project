# SEEKER_UNIFY_C verification bundle

Final status: **PASS**

## Product

`Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html` — `efba68cafa07ee3d2d986a80d59bcf169f51dbba59453dd4aab31ed8110fb4b7`

## Reproduce

```bash
python3 docs/missile/seeker-unify/C/build_product.py
python3 docs/missile/seeker-unify/C/verify_stage3_scope.py --baseline <stage2.html> --candidate Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html --out /tmp/scope.json
python3 docs/missile/seeker-unify/C/run_cue_a_codec.py --html Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html --out /tmp/codec.json
```

The full matrix/battle commands and frozen receipts are retained beside the result files. `run_stage3_regressions.py` is the one-shot broad harness; do not rerun it as part of a stage-only comparison.

See `REPORT.md` and `CUE_A_FINAL_RESULTS.json` for the gate decision.
