#!/usr/bin/env python3
"""Exercise production NPC observer radar/TrackStore paths by range.

This is deliberately separate from the direct RF and ownship managed-radar
diagnostics: every row advances ``stepObserversC`` and inspects only the
observer's anonymous track store.
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


SHIPS = ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    body = args.html.read_bytes()
    started = time.monotonic()
    rows: list[dict] = []
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        for target_profile in SHIPS:
            for observer_kind in ("DDG", "CG"):
                page = load(browser, body, ship=target_profile, errors=errors)
                try:
                    opts = [
                        dict(seed=939300 + n, observerKind=observer_kind, rangeKm=distance)
                        for distance in (10, 20, 30, 50, 70)
                        for n in range(3)
                    ]
                    rows.extend(page.evaluate(
                        "a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runNpcRadarCase(o))", opts
                    ))
                finally:
                    page.close()
                save(args.out.with_suffix(".progress.json"), {
                    "label": args.label,
                    "targetProfile": target_profile,
                    "observerKind": observer_kind,
                    "rows": rows,
                })
        browser.close()
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_A_NPC_RADAR_1",
        "label": args.label,
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "pageErrors": errors,
        "rows": rows,
    }
    save(args.out, result)
    print(json.dumps({
        "label": args.label,
        "rows": len(rows),
        "elapsedS": result["elapsedS"],
        "errors": len(errors),
    }))


if __name__ == "__main__":
    main()
