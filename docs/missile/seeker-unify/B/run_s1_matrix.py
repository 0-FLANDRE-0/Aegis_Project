#!/usr/bin/env python3
"""Run the frozen ASM_SEEKER_A S1 matrix against a diagnostic product."""
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
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    body = args.html.read_bytes()
    jobs = [
        dict(seed=seed, label="Kh-35U", launchRangeKm=distance, separationDeg=separation, maxTimeS=12)
        for distance in (20, 45)
        for separation in (0, 5, 10, 20, 40)
        for seed in range(519000, 519010)
    ]
    rows: list[dict] = []
    errors: list[str] = []
    started = time.monotonic()
    with sync_playwright() as pw:
        browser = launch(pw)
        for offset in range(0, len(jobs), 20):
            page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
            page.evaluate("__ASM_SEEKER_A_DIAG__.configure({enabled:true})")
            rows.extend(page.evaluate("a=>a.map(o=>__ASM_SEEKER_A_DIAG__.runCommon(o))", jobs[offset:offset + 20]))
            page.close()
        browser.close()
    result = {"schema":"AEGIS_SEEKER_UNIFY_B_U0_S1_MATRIX_1","label":args.label,"input":str(args.html),"inputSha256":hashlib.sha256(body).hexdigest(),"elapsedS":time.monotonic()-started,"jobs":len(jobs),"rows":rows,"pageErrors":errors}
    args.out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"label":args.label,"jobs":len(rows),"elapsedS":result["elapsedS"],"errors":len(errors)}))


if __name__ == "__main__":
    main()
