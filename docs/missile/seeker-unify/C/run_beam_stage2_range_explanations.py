#!/usr/bin/env python3
"""Measure the six Stage-2 stationary-DDG regressions in the real seeker path.

The injected observer records RF geometry only and delegates every measurement
to the product function.  Stage-1 and Stage-2 clean S/N are calculated from the
same observed geometry; nothing is fed back into tactical state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    comparison = json.loads(args.comparison.read_text())
    jobs = [
        {"kind": "range", "setup": row["setup"]}
        for row in comparison["targetTrackRegressions"]
    ]
    errors: list[str] = []
    body = args.html.read_bytes()
    started = time.monotonic()
    with sync_playwright() as pw:
        browser = launch(pw)
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        rows = page.evaluate(
            "jobs=>__SEEKER_UNIFY_C_BEAM_EXPLAIN__.run(jobs)", jobs
        )
        page.close()
        browser.close()

    uncaptured = [row["setup"] for row in rows if row["summary"]["attempts"] <= 0]
    unexpected_track = [
        row["setup"] for row in rows if row["result"]["result"]["everTrack"]
    ]
    status = (
        "PASS"
        if len(rows) == len(jobs) and not errors and not uncaptured and not unexpected_track
        else "FAIL"
    )
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_BEAM_STAGE2_RANGE_EXPLANATION_1",
        "status": status,
        "method": "actual Stage-2 measurement path with read-only AFTER_ACTION_DIAGNOSTIC observer",
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "formula": "stage2CleanSnr = stage1CleanSnr * oneWayBeamGain * oneWayLosQ",
        "cases": len(jobs),
        "rows": rows,
        "uncaptured": uncaptured,
        "unexpectedTrack": unexpected_track,
        "pageErrors": errors,
        "elapsedS": time.monotonic() - started,
        "truthUse": "diagnostic source tags select the synthetic target after measurement formation; no tactical feedback",
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": status,
                "cases": len(jobs),
                "uncaptured": len(uncaptured),
                "unexpectedTrack": len(unexpected_track),
                "pageErrors": len(errors),
                "elapsedS": result["elapsedS"],
            }
        )
    )
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
