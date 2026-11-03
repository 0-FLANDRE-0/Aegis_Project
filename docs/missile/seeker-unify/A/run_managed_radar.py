#!/usr/bin/env python3
"""Drive production surface plot acceptors and TrackStore creation by range."""
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
        for kind in ("DDG", "CG", "SOV", "HULK"):
            for radar in ("SPY1DV", "SPQ9B", "BRIDGEMASTER_E"):
                page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
                try:
                    for distance in (5, 10, 20, 30, 40, 50, 70):
                        opts = [dict(seed=929300 + n, kind=kind, radar=radar, rangeKm=distance) for n in range(5)]
                        rows.extend(page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runManagedRadarCase(o))", opts))
                finally:
                    page.close()
                save(args.out.with_suffix(".progress.json"), {"label": args.label, "kind": kind, "radar": radar, "rows": rows})
        browser.close()
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_A_MANAGED_RADAR_1",
        "label": args.label,
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "pageErrors": errors,
        "rows": rows,
    }
    save(args.out, result)
    print(json.dumps({"label": args.label, "rows": len(rows), "elapsedS": result["elapsedS"], "errors": len(errors)}))


if __name__ == "__main__":
    main()
