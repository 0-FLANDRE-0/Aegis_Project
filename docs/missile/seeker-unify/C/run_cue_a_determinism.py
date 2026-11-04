#!/usr/bin/env python3
"""Replay a fixed CUE_A sample twice and require byte-identical JSON rows."""
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
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    body = args.html.read_bytes()
    options = [
        {"seed": 839810 + index, "label": label, "rangeKm": 60, "speedKt": 30,
         "turnDeg": 30, "emcon": emcon, "threatMode": mode}
        for index, (label, mode, emcon) in enumerate(
            (label, mode, emcon)
            for label in ("Kh-35U", "Kh-32")
            for mode in ("MAX_THREAT", "CONFIRMED_ONLY")
            for emcon in (False, True)
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
        for index, (left, right) in enumerate(zip(first, second)) if left != right
    ]
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_CUE_A_DETERMINISM_1",
        "status": "PASS" if not mismatches and not errors else "FAIL",
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "cases": len(options), "pageErrors": errors, "mismatches": mismatches,
        "elapsedS": time.monotonic() - started,
        "firstSha256": hashlib.sha256(json.dumps(first, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "secondSha256": hashlib.sha256(json.dumps(second, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "cases", "pageErrors", "mismatches", "elapsedS", "firstSha256", "secondSha256")}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
