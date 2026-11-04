#!/usr/bin/env python3
"""Run the frozen broad regression once against the completed Stage-3 product."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "docs/missile/seeker-unify/B/run_regressions.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("seeker_unify_c_stage3_regression", SOURCE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    build = json.loads((HERE / "BUILD.json").read_text())
    module.HERE = HERE
    module.REPO = ROOT
    module.runner.P = HERE
    module.runner.R = module.HARNESS_ROOT
    module.runner.E = HERE / "evidence/regression-stage3"
    module.runner.HTML = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_C.html"
    module.runner.BASE = ROOT / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_A.html"
    module.runner.EXPECTED = build["productHtmlSha256"]
    module.runner.BASE_SHA = "53864e5939ca0fce03f50fb3040c2eafccd816027ba92960b53cf7c744ac08f8"
    module.runner.environment = module.environment
    module.runner.main()


if __name__ == "__main__":
    main()
