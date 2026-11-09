#!/usr/bin/env python3
"""Run only the skipped U4 scene suite after correcting its product pin.

The one-shot broad runner invoked the inherited U4 script, but that script
asserted U4's byte count before opening a browser. This wrapper changes only
those two harness constants and executes the same scene code once.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "docs/missile/seeker-unify/U4/run_u4_final_scenes.py"
spec = importlib.util.spec_from_file_location("hp_a_u4_scene_recovery", SOURCE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.PRODUCT_BYTES = 22_200_135
module.PRODUCT_SHA256 = "9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa"


if __name__ == "__main__":
    module.main()
