#!/usr/bin/env python3
"""Run the unchanged U4 19-check scene body with the frozen candidate pin."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "docs/missile/seeker-unify/U4/run_u4_final_scenes.py"
spec = importlib.util.spec_from_file_location("integration_baseline_u4_scenes", SOURCE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


if __name__ == "__main__":
    product = Path(sys.argv[1])
    body = product.read_bytes()
    module.PRODUCT_BYTES = len(body)
    module.PRODUCT_SHA256 = hashlib.sha256(body).hexdigest()
    module.main()

