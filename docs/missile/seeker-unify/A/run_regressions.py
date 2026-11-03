#!/usr/bin/env python3
"""Run the frozen ASM_SEEKER_A broad-regression harness on this product.

The harness and its historical MAP_E retired-node adapter are imported from
the validated baseline checkout.  This wrapper changes only artifact paths,
hash pins and evidence destinations.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
HARNESS_ROOT = Path("/dev/shm/aegis-ciws-dmg-a")
HARNESS = Path("/workspace/aegis-asm-seeker-a/docs/missile/asm-seeker/A/asm_seeker_regression_runner.py")

spec = importlib.util.spec_from_file_location("asm_a_regression", HARNESS)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

runner.P = HERE
runner.R = HARNESS_ROOT
runner.E = HERE / "evidence/regression"
runner.HTML = REPO / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html"
runner.BASE = REPO / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
runner.EXPECTED = "53864e5939ca0fce03f50fb3040c2eafccd816027ba92960b53cf7c744ac08f8"
runner.BASE_SHA = "9a00c8c02bd88ef1322b1b47882a2299184e174230391f9a608347f2b4fb3e5f"


def environment() -> dict[str, str]:
    return {
        **os.environ,
        "TMPDIR": "/dev/shm",
        "PYTHONDONTWRITEBYTECODE": "1",
        "NODE_PATH": "/workspace/aegis-performance-c/docs/performance/C/node_modules",
        "B2_PHASE1_REGRESSION": "1",
        "B2_MODE": "ON",
        "B2_HTML": str(runner.HTML),
        "B2_OUT": str(runner.E),
        "PYTHONPATH": str(HARNESS_ROOT / "docs/gun/B2/phase1b/test_support"),
        "B2_ALLOW_AUTO": "0",
    }


runner.environment = environment

if __name__ == "__main__":
    runner.main()
