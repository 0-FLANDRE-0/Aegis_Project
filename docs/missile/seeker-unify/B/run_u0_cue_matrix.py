#!/usr/bin/env python3
"""Run the directive U0 cue matrix in one browser engine."""
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    body = args.html.read_bytes()
    rows: list[dict] = []
    errors: list[str] = []
    started = time.monotonic()
    jobs = [
        dict(seed=seed, label=label, rangeKm=distance, speedKt=speed, turnDeg=turn, emcon=emcon)
        for label in ("Kh-35U", "Kh-32")
        for distance in (60, 100, 130)
        for speed, turn in ((15, 0), (30, 0), (30, 30), (30, 90))
        for seed in range(729300, 729305)
        for emcon in (False, True)
    ]
    with sync_playwright() as pw:
        browser = launch(pw)
        for offset in range(0, len(jobs), 20):
            page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
            batch = jobs[offset:offset + 20]
            rows.extend(page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))", batch))
            page.close()
            save(args.out.with_suffix(".progress.json"), {"label": args.label, "completed": len(rows), "total": len(jobs), "rows": rows, "pageErrors": errors})
        browser.close()
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_B_U0_CUE_MATRIX_1",
        "label": args.label,
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "jobs": len(jobs),
        "rows": rows,
        "pageErrors": errors,
    }
    save(args.out, result)
    print(json.dumps({"label": args.label, "jobs": len(rows), "elapsedS": result["elapsedS"], "errors": len(errors)}))


if __name__ == "__main__":
    main()
