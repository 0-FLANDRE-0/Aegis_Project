#!/usr/bin/env python3
"""Run one MAX_THREAT Stage-1b cue-matrix shard through real fixed ticks."""
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


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", choices=("Kh-35U", "Kh-32"), required=True)
    args = parser.parse_args()
    started = time.monotonic()
    body = args.html.read_bytes()
    options = [
        dict(seed=seed, label=args.label, rangeKm=distance, speedKt=speed, turnDeg=turn, emcon=emcon, threatMode="MAX_THREAT")
        for emcon in (False, True)
        for distance in (60, 100, 130)
        for speed, turn in ((15, 0), (30, 0), (30, 30), (30, 90))
        for seed in range(729300, 729305)
    ]
    errors: list[str] = []
    rows: list[dict] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        for index in range(0, len(options), 10):
            rows.extend(page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_C_DIAG__.runCueCase(o))", options[index:index + 10]))
            save(args.out.with_suffix(".progress.json"), {"schema": "AEGIS_CUE_A_1_STAGE1B_MATRIX_PROGRESS_1", "label": args.label, "rows": rows, "pageErrors": errors})
        page.close()
        browser.close()
    result = {
        "schema": "AEGIS_CUE_A_1_STAGE1B_MATRIX_SHARD_1",
        "label": args.label,
        "mode": "MAX_THREAT",
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "rows": rows,
        "pageErrors": errors,
    }
    save(args.out, result)
    print(json.dumps({"label": args.label, "rows": len(rows), "errors": len(errors), "elapsedS": result["elapsedS"]}, indent=2))


if __name__ == "__main__":
    main()
