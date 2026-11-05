#!/usr/bin/env python3
"""Replay a fixed Stage-1b cue sample twice and require identical decisions."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


HARNESS_ROOT = Path("/workspace/aegis-ui-a")
sys.path[:0] = [
    str(HARNESS_ROOT / "docs/pip/B"),
    str(HARNESS_ROOT / "docs/helicopter/H"),
    str(HARNESS_ROOT / "docs/multiship/G"),
    str(HARNESS_ROOT / "docs/bunkerhill/K"),
]
import browser_backend

browser_backend.install()
from browser_i import launch, load


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    body = args.html.read_bytes()
    # MAX_THREAT is the only performance-validation mode in CUE_A-1.  The
    # cases span both weapons, EMCON states, and representative geometry.
    options = [
        {
            "seed": 839810 + index,
            "label": label,
            "rangeKm": distance,
            "speedKt": speed,
            "turnDeg": turn,
            "emcon": emcon,
            "threatMode": "MAX_THREAT",
        }
        for index, (label, distance, speed, turn, emcon) in enumerate(
            (
                ("Kh-35U", 60, 15, 0, False),
                ("Kh-35U", 100, 30, 30, False),
                ("Kh-35U", 130, 30, 90, True),
                ("Kh-32", 60, 15, 0, False),
                ("Kh-32", 100, 30, 30, False),
                ("Kh-32", 130, 30, 90, True),
            )
        )
    ]
    errors: list[str] = []
    started = time.monotonic()
    with sync_playwright() as pw:
        browser = launch(pw)
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        first = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_C_DIAG__.runCueCase(o))", options)
        second = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_C_DIAG__.runCueCase(o))", options)
        page.close()
        browser.close()
    mismatches = [
        {"index": index, "setup": options[index], "first": left, "second": right}
        for index, (left, right) in enumerate(zip(first, second))
        if left != right
    ]
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    result = {
        "schema": "AEGIS_CUE_A_1_STAGE1B_DETERMINISM_1",
        "status": "PASS" if not mismatches and not errors else "FAIL",
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "mode": "MAX_THREAT",
        "cases": len(options),
        "pageErrors": errors,
        "mismatches": mismatches,
        "elapsedS": time.monotonic() - started,
        "firstSha256": hashlib.sha256(canonical(first)).hexdigest(),
        "secondSha256": hashlib.sha256(canonical(second)).hexdigest(),
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "status", "mode", "cases", "pageErrors", "mismatches", "elapsedS",
        "firstSha256", "secondSha256",
    )}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
