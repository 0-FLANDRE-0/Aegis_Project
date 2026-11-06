#!/usr/bin/env python3
"""Run the U3-B floor, live handoff, consumer, and stale-observation gates."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path[:0] = ["/workspace/aegis-ui-a/docs/pip/B", "/workspace/aegis-ui-a/docs/bunkerhill/K"]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


CASES = (
    {"name": "floor-general-track", "options": {"rangeKm": 8, "posSigmaM": 75}},
    {"name": "large-covariance-general-track", "options": {"rangeKm": 8, "posSigmaM": 1600}},
    {"name": "stale-general-track", "options": {"rangeKm": 8, "posSigmaM": 75, "stale": True}},
)


def run_case(pw, body: bytes, case: dict) -> tuple[dict, list[str]]:
    errors: list[str] = []
    browser = launch(pw)
    page = load(browser, body, ship="CG_52_LATE_TICONDEROGA", errors=errors)
    try:
        row = page.evaluate("o=>__SEEKER_U3_DIAG__.launchFlowB(o)", case["options"])
    finally:
        page.close()
        browser.close()
    return row, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    body = args.html.read_bytes()
    started = time.monotonic()
    with sync_playwright() as pw:
        browser = launch(pw)
        bootstrap_errors: list[str] = []
        page = load(browser, body, ship="CG_52_LATE_TICONDEROGA", errors=bootstrap_errors)
        matrix = page.evaluate("()=>__SEEKER_U3_DIAG__.cueMatrixB()")
        contract = page.evaluate("()=>__SEEKER_U3_DIAG__.contractB()")
        page.close()
        browser.close()
        first: list[dict] = []
        second: list[dict] = []
        page_errors: dict[str, list[str]] = {"bootstrap": bootstrap_errors}
        for case in CASES:
            row, errors = run_case(pw, body, case)
            first.append(row)
            page_errors[case["name"] + "-first"] = errors
        for case in CASES:
            row, errors = run_case(pw, body, case)
            second.append(row)
            page_errors[case["name"] + "-second"] = errors

    deterministic = first == second
    floor = first[0]
    large = first[1]
    stale = first[2]
    checks = {
        "matrix": matrix["pass"],
        "legacy225To250": matrix["nominalCovarianceBasketM"] == 225
        and matrix["horizons"][0]["searchBasketM"] == 250,
        "largeCovarianceNotClipped": matrix["overOld"]["searchBasketM"] == 4800
        and matrix["overOld"]["searchBasketM"] > 4000,
        "routePriorSeparateAndFixed": matrix["route"]["source"] == "ROUTE_PLAN_PRIOR"
        and matrix["route"]["observationUpdate"] is False
        and matrix["route"]["searchBasketM"] == 4000,
        "floorLiveLaunch": floor["pass"] and floor["gate"]["searchBasketM"] == 250,
        "largeLiveLaunch": large["pass"] and large["gate"]["searchBasketM"] == 4800,
        "liveCueHandoff": all(
            row["releaseCue"]["searchBasketM"] == row["gate"]["searchBasketM"]
            and row["gate"]["cueSource"] == "LOCAL_SURFACE_OBSERVATION"
            and not row["releaseRouteUsed"]
            for row in (floor, large)
        ),
        "seekerConsumesDynamicBasket": all(
            row["seekerConsumer"]["dynamicMatch"]
            and row["seekerConsumer"]["distinctFromFixed4000"]
            for row in (floor, large)
        ),
        "attackGuardConsumesDynamicBasket": all(row["attackConsumer"]["pass"] for row in (floor, large)),
        "actualStaleRejected": stale["pass"]
        and stale["staleEvidence"]["sensorAge"] > stale["staleEvidence"]["maxTrackAgeS"]
        and stale["gate"]["reason"] == "SURFACE_TRACK_COAST_EXPIRED"
        and not stale["pendingCreated"],
        "deterministic": deterministic,
        "noPageErrors": not any(page_errors.values()),
        # Earlier diagnostic modules wrap harpoonSeekerA, so Function#toString
        # is not authoritative for that consumer. The two live launches above
        # call the production seeker and compare its scan bounds instead.
        "attackConsumerContractPresent": "gate.searchBasketM" in contract["attackGuard"],
    }
    passed = all(checks.values())
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_U3_B_CORRECTION_GATE_1",
        "status": "PASS" if passed else "FAIL",
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "checks": checks,
        "matrix": matrix,
        "cases": list(CASES),
        "first": first,
        "second": second,
        "pageErrors": page_errors,
        "contractEvidence": {
            "attackGuardUsesDynamic": "gate.searchBasketM" in contract["attackGuard"],
            "seekerFunctionToStringWrapped": "cueHandoff.searchBasketM" not in contract["seeker"],
            "seekerEvidence": "LIVE_SCAN_BOUNDS_MATCH_DYNAMIC_AND_DIFFER_FROM_FIXED_4000",
        },
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "elapsedS": result["elapsedS"], "checks": checks}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
