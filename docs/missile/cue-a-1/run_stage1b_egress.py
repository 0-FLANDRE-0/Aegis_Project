#!/usr/bin/env python3
"""Adapt the frozen TRACK-C 37-missile replay to the CUE_A-1 product."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HARNESS_ROOT = Path("/workspace/aegis-ui-a")
sys.path[:0] = [
    str(HARNESS_ROOT / "docs/missile/fuze-zem/A"),
    str(HARNESS_ROOT / "docs/pip/B"),
    str(HARNESS_ROOT / "docs/helicopter/H"),
    str(HARNESS_ROOT / "docs/multiship/G"),
    str(HARNESS_ROOT / "docs/bunkerhill/K"),
]


def main() -> int:
    source = ROOT / "docs/missile/seeker-unify/C/run_stage2_egress_37.py"
    spec = importlib.util.spec_from_file_location("cue_a1_frozen_egress", source)
    if not spec or not spec.loader:
        raise RuntimeError("frozen egress runner unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    module.ORIG = ROOT
    module.EVIDENCE = Path("/dev/shm/cue-a1-stage1b-egress-evidence")
    sys.argv = [
        str(source),
        "--diagnostic", "/dev/shm/cue-a1-stage1b-asm-diag.html",
        "--build-receipt", str(HERE / "STAGE1B_ASM_DIAGNOSTIC_BUILD.json"),
        "--evidence", str(module.EVIDENCE),
        "--plan", "/dev/shm/cue-a1-stage1b-egress-plan.json",
        "--progress", "/dev/shm/cue-a1-stage1b-egress-progress.json",
        "--out", "/dev/shm/cue-a1-stage1b-egress-results.json",
    ]
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
