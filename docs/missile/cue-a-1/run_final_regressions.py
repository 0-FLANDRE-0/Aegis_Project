#!/usr/bin/env python3
"""Run the directive's single frozen broad regression against CUE_A-1."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "docs/missile/seeker-unify/B/run_regressions.py"
HARNESS_ROOT = Path("/workspace/aegis-ui-a")
BASELINE = Path("/workspace/aegis-seeker-unify-a/Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html")


def main() -> None:
    spec = importlib.util.spec_from_file_location("cue_a_1_final_regression", SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    build = json.loads((HERE / "BUILD.json").read_text())

    # The historical /dev/shm checkout was ephemeral.  Point the unchanged
    # frozen adapters at their persistent source tree; no assertion or expected
    # value is altered.
    module.HARNESS_ROOT = HARNESS_ROOT
    module.HERE = HERE
    module.REPO = ROOT
    module.runner.P = HERE
    module.runner.R = HARNESS_ROOT
    module.runner.E = HERE / "evidence/regression-final"
    module.runner.HTML = ROOT / build["product"]
    module.runner.BASE = BASELINE
    module.runner.EXPECTED = build["productHtmlSha256"]
    module.runner.BASE_SHA = "53864e5939ca0fce03f50fb3040c2eafccd816027ba92960b53cf7c744ac08f8"
    module.runner.environment = module.environment
    module.runner.main()


if __name__ == "__main__":
    main()
