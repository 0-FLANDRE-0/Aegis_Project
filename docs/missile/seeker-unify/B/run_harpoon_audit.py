#!/usr/bin/env python3
"""Measure the existing Harpoon launch-memory basket without changing it."""
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
    jobs = [
        dict(seed=seed, rangeKm=distance, speedKt=speed, turnDeg=turn)
        for distance in (60, 100, 120)
        for speed, turn in ((15, 0), (30, 0), (30, 30), (30, 90))
        for seed in range(739300, 739305)
    ]
    rows: list[dict] = []
    errors: list[str] = []
    started = time.monotonic()
    with sync_playwright() as pw:
        browser = launch(pw)
        for offset in range(0, len(jobs), 10):
            page = load(browser, body, ship="CG_52_LATE_TICONDEROGA", errors=errors)
            rows.extend(page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runHarpoonCueCase(o))", jobs[offset:offset + 10]))
            page.close()
        browser.close()
    result = {"schema":"AEGIS_SEEKER_UNIFY_B_HARPOON_BASKET_AUDIT_1","input":str(args.html),"inputSha256":hashlib.sha256(body).hexdigest(),"elapsedS":time.monotonic()-started,"jobs":len(jobs),"rows":rows,"pageErrors":errors,"productCodeModified":False}
    args.out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"jobs":len(rows),"elapsedS":result["elapsedS"],"errors":len(errors)}))


if __name__ == "__main__":
    main()
