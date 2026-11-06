#!/usr/bin/env python3
"""Run the single final MAX_THREAT broad regression for SEEKER_UNIFY_U3."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
HARNESS_ROOT = Path("/workspace/aegis-ui-a")
HARNESS = Path("/workspace/aegis-asm-seeker-a/docs/missile/asm-seeker/A/asm_seeker_regression_runner.py")
PRODUCT = REPO / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html"
BASELINE = REPO / "Aegis_SIM_v48_WIP_CUE_A_1.html"
PRODUCT_SHA = "243c196a69990e1fba9de0993f7904fb569e3adc5b6e84cf52672d3300638835"
BASELINE_SHA = "0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a"


spec = importlib.util.spec_from_file_location("seeker_unify_u3_final_regression", HARNESS)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.P = HERE
runner.R = HARNESS_ROOT
runner.E = HERE / "evidence/final-regression-b-correction"
runner.HTML = PRODUCT
runner.BASE = BASELINE
runner.EXPECTED = PRODUCT_SHA
runner.BASE_SHA = BASELINE_SHA


def environment() -> dict[str, str]:
    return {
        **os.environ,
        "TMPDIR": "/dev/shm",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NODE_PATH": "/workspace/aegis-performance-c/docs/performance/C/node_modules",
        "B2_PHASE1_REGRESSION": "1",
        "B2_MODE": "ON",
        "B2_HTML": str(PRODUCT),
        "B2_OUT": str(runner.E),
        "PYTHONPATH": str(HARNESS_ROOT / "docs/gun/B2/phase1b/test_support"),
        "B2_ALLOW_AUTO": "0",
    }


runner.environment = environment


if __name__ == "__main__":
    runner.main()
