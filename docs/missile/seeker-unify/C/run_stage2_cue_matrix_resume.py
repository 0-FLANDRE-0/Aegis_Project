#!/usr/bin/env python3
"""Resume the 240-case Stage-2 cue matrix from a validated progress file."""
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


def setup_key(value: dict) -> str:
    setup = value.get("setup", value)
    setup = {key: item for key, item in setup.items() if key != "turnAtS"}
    return json.dumps(setup, sort_keys=True, separators=(",", ":"))


def jobs() -> list[dict]:
    return [
        dict(
            seed=seed,
            label=label,
            rangeKm=distance,
            speedKt=speed,
            turnDeg=turn,
            emcon=emcon,
        )
        for label in ("Kh-35U", "Kh-32")
        for distance in (60, 100, 130)
        for speed, turn in ((15, 0), (30, 0), (30, 30), (30, 90))
        for seed in range(729300, 729305)
        for emcon in (False, True)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--progress", type=Path, required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    body = args.html.read_bytes()
    work = jobs()
    prior = json.loads(args.progress.read_text()) if args.progress.exists() else {}
    rows = list(prior.get("rows", []))
    errors = list(prior.get("pageErrors", []))
    completed = {setup_key(row) for row in rows}
    pending = [job for job in work if setup_key(job) not in completed]
    if len(completed) != len(rows):
        raise AssertionError("duplicate setup in progress file")
    if any(setup_key(job) not in {setup_key(item) for item in work} for job in rows):
        raise AssertionError("progress file contains a non-matrix setup")

    started = time.monotonic()
    with sync_playwright() as pw:
        browser = launch(pw)
        for offset in range(0, len(pending), 20):
            page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
            batch = pending[offset : offset + 20]
            rows.extend(
                page.evaluate(
                    "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))", batch
                )
            )
            page.close()
            save(
                args.progress,
                {
                    "label": args.label,
                    "completed": len(rows),
                    "total": len(work),
                    "rows": rows,
                    "pageErrors": errors,
                },
            )
            print(json.dumps({"completed": len(rows), "total": len(work), "errors": len(errors)}), flush=True)
        browser.close()

    by_key = {setup_key(row): row for row in rows}
    ordered = [by_key[setup_key(job)] for job in work]
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_B_U0_CUE_MATRIX_1",
        "label": args.label,
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedResumeS": time.monotonic() - started,
        "completedBefore": len(completed),
        "jobs": len(work),
        "rows": ordered,
        "pageErrors": errors,
    }
    save(args.out, result)
    print(
        json.dumps(
            {
                "label": args.label,
                "jobs": len(ordered),
                "completedBefore": len(completed),
                "elapsedResumeS": result["elapsedResumeS"],
                "errors": len(errors),
            }
        )
    )
    raise SystemExit(0 if len(ordered) == len(work) and not errors else 1)


if __name__ == "__main__":
    main()
