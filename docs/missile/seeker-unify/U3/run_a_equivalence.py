#!/usr/bin/env python3
"""Commit A SHADOW -> ACTIVE representative Harpoon equivalence gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path[:0] = [
    "/workspace/aegis-ui-a/docs/pip/B",
    "/workspace/aegis-ui-a/docs/bunkerhill/K",
]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def cases() -> list[dict]:
    # Six geometry branches x three independent seeds. This remains below the
    # directive's 30 representative cases per branch ceiling.
    rows = []
    seed = 973100
    for range_km, speed_kt, turn_deg in (
        (40, 0, 0),
        (40, 30, 45),
        (80, 15, 0),
        (80, 30, 90),
        (120, 30, 0),
        (120, 30, 45),
    ):
        for _ in range(3):
            rows.append({"seed": seed, "rangeKm": range_km, "speedKt": speed_kt, "turnDeg": turn_deg})
            seed += 1
    return rows


def run_build(pw, path: Path, jobs: list[dict], inspect: bool) -> dict:
    body = path.read_bytes()
    browser = launch(pw)
    errors: list[str] = []
    rows: list[dict] = []
    snapshot = None
    for start in range(0, len(jobs), 6):
        page = load(browser, body, ship="CG_52_LATE_TICONDEROGA", errors=errors)
        rows.extend(page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runHarpoonCueCase(o))", jobs[start:start + 6]))
        if inspect:
            snapshot = page.evaluate("()=>window.__SEEKER_COMMON_U2__.harpoonSnapshot()")
        page.close()
    browser.close()
    return {"sha256": hashlib.sha256(body).hexdigest(), "rows": rows, "snapshot": snapshot, "pageErrors": errors}


def diffs(a: list, b: list) -> list[dict]:
    return [{"index": i, "before": x, "after": y} for i, (x, y) in enumerate(zip(a, b)) if x != y]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--shadow", type=Path, required=True)
    ap.add_argument("--active", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    jobs = cases()
    started = time.monotonic()
    with sync_playwright() as pw:
        baseline = run_build(pw, args.baseline, jobs, False)
        shadow = run_build(pw, args.shadow, jobs, True)
        active = run_build(pw, args.active, jobs, True)
    shadow_diff = diffs(baseline["rows"], shadow["rows"])
    active_diff = diffs(baseline["rows"], active["rows"])
    s = shadow["snapshot"] or {}
    a = active["snapshot"] or {}
    shadow_contract = (
        s.get("mode") == "SHADOW"
        and s.get("powerComparisons", 0) > 0
        and s.get("cellComparisons", 0) > 0
        and s.get("powerMismatches") == 0
        and s.get("cellMismatches") == 0
        and s.get("rngConsumedByCommonLayer") is False
        and s.get("truthOutput") is False
        and s.get("tacticalOutputUsed") is False
    )
    active_contract = (
        a.get("mode") == "ACTIVE"
        and a.get("powerComparisons") == 0
        and a.get("cellComparisons") == 0
        and a.get("rngConsumedByCommonLayer") is False
        and a.get("truthOutput") is False
        and a.get("tacticalOutputUsed") is True
    )
    page_errors = {k: v["pageErrors"] for k, v in (("baseline", baseline), ("shadow", shadow), ("active", active))}
    passed = not shadow_diff and not active_diff and shadow_contract and active_contract and not any(page_errors.values())
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_U3_A_EQUIVALENCE_1",
        "status": "PASS" if passed else "FAIL",
        "elapsedS": time.monotonic() - started,
        "cases": len(jobs),
        "jobs": jobs,
        "bitEqual": {"baselineVsShadow": not shadow_diff, "baselineVsActive": not active_diff},
        "differences": {"shadow": shadow_diff, "active": active_diff},
        "snapshots": {"shadow": s, "active": a},
        "contractPass": {"shadow": shadow_contract, "active": active_contract},
        "pageErrors": page_errors,
        "inputs": {"baseline": baseline["sha256"], "shadow": shadow["sha256"], "active": active["sha256"]},
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "elapsedS", "cases", "bitEqual", "snapshots", "contractPass", "pageErrors")}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
