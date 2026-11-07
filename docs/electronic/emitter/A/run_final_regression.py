#!/usr/bin/env python3
"""Run the single final MAX_THREAT broad regression for EMITTER_A."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
HARNESS_ROOT = Path("/workspace/aegis-ui-a")
HARNESS = Path("/workspace/aegis-asm-seeker-a/docs/missile/asm-seeker/A/asm_seeker_regression_runner.py")
PRODUCT = REPO / "Aegis_SIM_v48_WIP_EMITTER_A.html"
BASELINE = REPO / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html"
PRODUCT_SHA = "04bfb9c991929bed5800e7899f2ffb79087bfd20b79300c9bb01628b7edc98c6"
BASELINE_SHA = "243c196a69990e1fba9de0993f7904fb569e3adc5b6e84cf52672d3300638835"

spec = importlib.util.spec_from_file_location("emitter_a_final_regression", HARNESS)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.P = HERE
runner.R = HARNESS_ROOT
runner.E = HERE / "evidence/final-regression"
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
