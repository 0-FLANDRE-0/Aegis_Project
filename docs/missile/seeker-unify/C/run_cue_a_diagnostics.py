#!/usr/bin/env python3
"""Run the non-matrix CUE_A Stage-3 diagnostics in the real game page."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

sys.path[:0] = [
    "/dev/shm/aegis-ciws-dmg-a/docs/pip/B",
    "/dev/shm/aegis-ciws-dmg-a/docs/helicopter/H",
    "/dev/shm/aegis-ciws-dmg-a/docs/multiship/G",
    "/dev/shm/aegis-ciws-dmg-a/docs/bunkerhill/K",
]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    body = args.html.read_bytes()
    errors: list[str] = []

    velocity_options = [
        {"label": label, "known": known, "seconds": seconds, "speedMps": 15, "rangeM": 100000}
        for label in ("Kh-35U", "Kh-32")
        for known in (False, True)
        for seconds in (60, 120, 180)
    ]
    range_options = [
        {"seed": seed, "label": label, "threatMode": "MAX_THREAT", "rangeKm": distance,
         "altitudeM": 10000 if label == "Kh-32" else 12, "samples": 20}
        for label, distances in (("Kh-35U", (10, 20, 30)), ("Kh-32", (60, 100, 130)))
        for distance in distances
        for seed in range(839500, 839505)
    ]
    multi_options = [
        {"seed": seed, "label": label, "threatMode": mode, "rangeKm": 80,
         "altitudeM": 800, "offsetDeg": offset, "otherRangeKm": other_range}
        for label in ("Kh-35U", "Kh-32")
        for mode in ("MAX_THREAT", "CONFIRMED_ONLY")
        for offset, other_range in ((1, 75), (3, 80), (-3, 85))
        for seed in range(839600, 839605)
    ]

    with sync_playwright() as pw:
        browser = launch(pw)
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        contract = page.evaluate("__SEEKER_UNIFY_C_DIAG__.contract()")
        velocity = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_C_DIAG__.runVelocityCase(o))", velocity_options)
        ranges = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_C_DIAG__.runPassiveRangeCase(o))", range_options)
        multi = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_C_DIAG__.runMultiEmitterCase(o))", multi_options)
        dl = page.evaluate("__SEEKER_UNIFY_C_DIAG__.runDlHookCase()")
        boundary = page.evaluate("__AEGIS_WIP14B2__.selfTest()")
        page.close()
        browser.close()

    range_summary: dict[str, dict] = {}
    for label in ("Kh-35U", "Kh-32"):
        rows = [row for row in ranges if row["setup"]["label"] == label]
        errors_m = [row["afterActionTruth"]["meanErrorM"] for row in rows if row["afterActionTruth"]["meanErrorM"] is not None]
        rmses = [row["afterActionTruth"]["rmseM"] for row in rows if row["afterActionTruth"]["rmseM"] is not None]
        range_summary[label] = {
            "cases": len(rows),
            "availableSamples": sum(row["availableSamples"] for row in rows),
            "meanOfCaseMeanErrorM": statistics.fmean(errors_m) if errors_m else None,
            "medianCaseAbsMeanErrorM": statistics.median(abs(value) for value in errors_m) if errors_m else None,
            "meanCaseRmseM": statistics.fmean(rmses) if rmses else None,
        }

    multi_summary = {
        "cases": len(multi),
        "measurements": sum(bool((row.get("measurement") or {}).get("available")) for row in multi),
        "anonymousPayloadLeaks": [
            {"setup": row["setup"], "keys": row["anonymousPayloadKeys"]}
            for row in multi
            if any(token in key.lower() for key in row["anonymousPayloadKeys"] for token in ("owner", "entity", "profile", "coord", "point"))
        ],
        "nearestOwnerCounts": {},
    }
    for row in multi:
        owner = (row["afterActionTruth"].get("nearestToAnonymousBearing") or {}).get("owner") or "NONE"
        multi_summary["nearestOwnerCounts"][owner] = multi_summary["nearestOwnerCounts"].get(owner, 0) + 1

    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_CUE_A_DIAGNOSTICS_1",
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "pageErrors": errors,
        "contract": contract,
        "velocity": velocity,
        "rangeEstimate": {"summary": range_summary, "rows": ranges},
        "multiEmitter": {"summary": multi_summary, "rows": multi},
        "dlHook": dl,
        "boundarySelfTest": boundary,
    }
    save(args.out, result)
    print(json.dumps({
        "elapsedS": result["elapsedS"], "pageErrors": len(errors),
        "velocityCases": len(velocity), "rangeCases": len(ranges), "multiCases": len(multi),
        "rangeSummary": range_summary, "multiSummary": multi_summary,
        "dl": {"ok": dl.get("result", {}).get("ok"), "connected": dl.get("connected")},
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
