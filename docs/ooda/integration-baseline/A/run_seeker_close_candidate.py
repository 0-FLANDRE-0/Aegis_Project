#!/usr/bin/env python3
"""Build and execute the fixed SEEKER_CLOSE_A 19-shot matrix once."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = args.output / "DIAGNOSTIC_BUILD.json"
    env = {**os.environ, "THREAT_ASSUMPTION_MODE": "MAX_THREAT", "TMPDIR": "/dev/shm", "PYTHONDONTWRITEBYTECODE": "1"}
    with tempfile.TemporaryDirectory(prefix="aegis-seeker-close-") as directory:
        diagnostic = Path(directory) / "SEEKER_CLOSE_DIAGNOSTIC.html"
        subprocess.run([
            sys.executable, str(HERE / "build_seeker_close_diagnostic.py"),
            str(args.product), str(diagnostic), str(receipt),
        ], cwd=ROOT, env=env, check=True)
        subprocess.run([
            sys.executable, str(ROOT / "docs/missile/seeker-close/A/run_diagnostics.py"),
            str(diagnostic), str(args.output), "--receipt", str(receipt),
        ], cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    main()

