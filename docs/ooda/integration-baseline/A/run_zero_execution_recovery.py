#!/usr/bin/env python3
"""Execute once only suites that the broad harness recorded with zero assertions.

The raw one-shot broad receipt is immutable. This recovery is permitted only
for pre-browser checkout failures: exit nonzero, no result file and exactly
zero executed assertions. Already executed suites are never repeated.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import time


HERE = Path(__file__).resolve().parent
RAW = HERE / "FINAL_REGRESSION_RAW.json"
OUT = HERE / "evidence" / "zero-execution-recovery"
SUMMARY = HERE / "ZERO_EXECUTION_RECOVERY.json"
SOURCE = HERE / "run_final_regression.py"

spec = importlib.util.spec_from_file_location("integration_baseline_final", SOURCE)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main() -> None:
    raw = json.loads(RAW.read_text())
    failed = [row for row in raw["rows"] if row["status"] != "PASS"]
    invalid = [row["suite"] for row in failed if row["executedAssertions"] != 0 or row.get("resultPath") is not None]
    if invalid:
        raise AssertionError(f"recovery would repeat an executed suite: {invalid}")
    names = [row["suite"] for row in failed]
    expected = [*runner.NATIVE, "paired-hp-a", "paired-determinism", "current-emcon-ui", "ui213", "webgl8", "hp-contract"]
    if names != expected:
        raise AssertionError({"actual": names, "expected": expected})
    OUT.mkdir(parents=True, exist_ok=True)
    if any(OUT.iterdir()):
        raise AssertionError("zero-execution recovery is one-shot; output must be empty")
    runner.OUT = OUT
    started = time.perf_counter(); rows = []
    for name in names:
        rows.append(runner.execute(name))
        SUMMARY.write_text(strict({"schema": "AEGIS_INTEGRATION_BASELINE_A_ZERO_EXECUTION_RECOVERY_1", "complete": False, "rawBroad": RAW.name, "reason": "MISSING_CHECKOUT_BROWSER_G_AND_BROWSER_TOOLS_BEFORE_BROWSER_LAUNCH", "recoveredSuites": rows, "wallS": time.perf_counter() - started}))
    failures = [row["suite"] for row in rows if row["status"] != "PASS"]
    payload = {"schema": "AEGIS_INTEGRATION_BASELINE_A_ZERO_EXECUTION_RECOVERY_1", "complete": True, "rawBroad": RAW.name, "rawBroadRerun": False, "reason": "MISSING_CHECKOUT_BROWSER_G_AND_BROWSER_TOOLS_BEFORE_BROWSER_LAUNCH", "missingModulesRestored": ["docs/multiship/G/browser_g.py", "docs/missile/fuze-zem/A/browser_tools.py"], "recoveredSuites": rows, "effectiveFailures": failures, "wallS": time.perf_counter() - started}
    SUMMARY.write_text(strict(payload))
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
