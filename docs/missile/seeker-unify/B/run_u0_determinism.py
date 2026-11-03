#!/usr/bin/env python3
"""Verify U0 cue output and the global RNG state are repeatable.

This is deliberately a focused stage test, not a broad regression run.  Each
case is reset through the product's normal deterministic diagnostic reset, and
the exact JSON result (including SIM_RNG_STATE) is compared in the same engine
and again after a fresh page load.
"""
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
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    body = args.html.read_bytes()
    jobs = [
        dict(seed=739600 + i, label=label, rangeKm=distance, speedKt=speed,
             turnDeg=turn, emcon=emcon)
        for i, (label, distance, speed, turn, emcon) in enumerate((
            (label, distance, speed, turn, emcon)
            for label in ("Kh-35U", "Kh-32")
            for distance, speed, turn, emcon in (
                (60, 15, 0, False), (60, 30, 30, True),
                (100, 30, 90, False), (130, 30, 0, True),
                (130, 30, 90, False),
            )
        ))
    ]
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        run_a = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))", jobs)
        run_b = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))", jobs)
        page.close()
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        run_c = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))", jobs)
        page.close()
        browser.close()
    encoded = lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    hashes = [hashlib.sha256(encoded(value)).hexdigest() for value in (run_a, run_b, run_c)]
    rng = [[row["result"]["globalRng"] for row in run] for run in (run_a, run_b, run_c)]
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_B_U0_DETERMINISM_1",
        "status": "PASS" if run_a == run_b == run_c and not errors else "FAIL",
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "jobs": len(jobs),
        "comparison": {"samePage": run_a == run_b, "freshPage": run_a == run_c},
        "resultSha256": hashes,
        "globalRng": rng,
        "pageErrors": errors,
        "runs": {"a": run_a, "b": run_b, "c": run_c},
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "jobs", "comparison", "resultSha256", "globalRng", "pageErrors")}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
