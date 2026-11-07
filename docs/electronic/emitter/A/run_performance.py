#!/usr/bin/env python3
"""Compare predecessor and ACTIVE physical-emitter query cost deterministically."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
BASE = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_PERF_U3.html")
ACTIVE = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_PERF_FINAL.html")
sys.path[:0] = [str(REPO_ROOT / "docs/pip/B"), str(REPO_ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def measure(browser, body: bytes, errors: list[str]) -> list[dict]:
    page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    rows = [page.evaluate("n=>__EMITTER_A_PERF__.run(n)", 50000) for _ in range(7)]
    page.close()
    return rows


def main() -> None:
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        baseline = measure(browser, BASE.read_bytes(), errors)
        active = measure(browser, ACTIVE.read_bytes(), errors)
        browser.close()
    b = statistics.median(q["nsPerCall"] for q in baseline)
    a = statistics.median(q["nsPerCall"] for q in active)
    checks = {"pageErrorsZero": not errors,
              "outputExact": all(q["outputRows"] == baseline[0]["outputRows"] for q in [*baseline, *active]),
              "rngUnchanged": all(q["rngUnchanged"] for q in [*baseline, *active]),
              "boundedAbsoluteCost": a < 100_000}
    result = {"schema": "AEGIS_EMITTER_A_PERFORMANCE_1",
              "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
              "inputs": {"baselineSha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
                         "activeSha256": hashlib.sha256(ACTIVE.read_bytes()).hexdigest()},
              "iterationsPerRun": 50000, "runs": 7, "baseline": baseline, "active": active,
              "medianNsPerCall": {"baseline": b, "active": a,
                                  "delta": a - b, "ratio": a / b if b else None},
              "note": "Microbenchmark only; broad UI/WebGL regression is the frame-level guard."}
    (HERE / "PERFORMANCE.json").write_text(strict(result))
    print(strict({"status": result["status"], "checks": checks,
                  "medianNsPerCall": result["medianNsPerCall"]}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
