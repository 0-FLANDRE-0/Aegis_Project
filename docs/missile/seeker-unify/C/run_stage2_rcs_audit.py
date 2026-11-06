#!/usr/bin/env python3
"""Verify Stage-2 RCS inputs remain byte-for-byte equal to the frozen baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
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
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    body = args.html.read_bytes()
    baseline = json.loads(args.baseline.read_text())["rcsAudits"]
    errors: list[str] = []
    candidate = {}
    with sync_playwright() as pw:
        browser = launch(pw)
        for label, ship in (
            ("DDG", "DDG_119_LATE_FLIGHT_IIA"),
            ("CG", "CG_52_LATE_TICONDEROGA"),
        ):
            page = load(browser, body, ship=ship, errors=errors)
            candidate[label] = page.evaluate("()=>__SEEKER_UNIFY_A_DIAG__.rcsAudit()")
            page.close()
        browser.close()

    physical_differences = {}
    consumer_differences = {}
    unexpected_consumers = {}
    for label in ("DDG", "CG"):
        before_physical = {
            key: value for key, value in baseline[label].items() if key != "consumers"
        }
        after_physical = {
            key: value for key, value in candidate[label].items() if key != "consumers"
        }
        if before_physical != after_physical:
            physical_differences[label] = {
                "baseline": before_physical,
                "candidate": after_physical,
            }
        changed_consumers = sorted(
            key
            for key in baseline[label]["consumers"]
            if baseline[label]["consumers"][key]
            != candidate[label]["consumers"][key]
        )
        consumer_differences[label] = changed_consumers
        unexpected = sorted(set(changed_consumers) - {"sam"})
        if unexpected:
            unexpected_consumers[label] = unexpected
    passed = not physical_differences and not unexpected_consumers and not errors
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_BEAM_STAGE2_RCS_AUDIT_1",
        "status": "PASS" if passed else "FAIL",
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "baseline": str(args.baseline),
        "candidate": candidate,
        "physicalDifferences": physical_differences,
        "consumerDifferences": consumer_differences,
        "allowedConsumerDifference": {
            "sam": "Stage-1 U2 ACTIVE adapter replaces the B shadow-era SAM function body; it does not alter RCS inputs"
        },
        "unexpectedConsumerDifferences": unexpected_consumers,
        "pageErrors": errors,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": result["status"],
                "profiles": list(candidate),
                "physicalDifferences": len(physical_differences),
                "unexpectedConsumerDifferences": len(unexpected_consumers),
                "pageErrors": len(errors),
            }
        )
    )
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
