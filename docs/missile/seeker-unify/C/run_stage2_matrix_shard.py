#!/usr/bin/env python3
"""Run one deterministic SEEKER_UNIFY_C Stage-2 diagnostic matrix shard.

The full 1,590-case runner is intentionally sequential.  This shard runner is
only a recovery/throughput harness: each case still executes the same in-game
diagnostic function, but independent range/SAM/cue/radar sets can use separate
browser processes.  Existing completed setups may be supplied and are skipped
exactly; the merge tool restores canonical matrix order.
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


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def setup_key(value: dict) -> str:
    setup = value.get("setup", value)
    # targetId/turnAtS are fixture outputs rather than matrix inputs.
    setup = {k: v for k, v in setup.items() if k not in {"targetId", "turnAtS"}}
    return json.dumps(setup, sort_keys=True, separators=(",", ":"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--section", choices=("range", "sam", "cue", "radar"), required=True)
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()

    started = time.monotonic()
    body = args.html.read_bytes()
    prior: dict = {}
    if args.resume and args.resume.exists():
        prior = json.loads(args.resume.read_text())
    collection_name = {
        "range": "rangeCases",
        "sam": "samArhCases",
        "cue": "cueCases",
        "radar": "radarCases",
    }[args.section]
    completed = {setup_key(row) for row in prior.get(collection_name, [])}
    rows: list[dict] = []
    errors: list[str] = []
    progress_path = args.out.with_suffix(".progress.json")

    def progress(group: str) -> None:
        save(progress_path, {
            "schema": "AEGIS_SEEKER_UNIFY_C_STAGE2_SHARD_PROGRESS_1",
            "label": args.label,
            "section": args.section,
            "group": group,
            "completedBefore": len(completed),
            collection_name: rows,
            "pageErrors": errors,
        })

    with sync_playwright() as pw:
        browser = launch(pw)
        page = None
        group_count = 0

        def evaluate(expression: str, options: list[dict]) -> None:
            nonlocal page, group_count
            pending = [opt for opt in options if setup_key(opt) not in completed]
            if not pending:
                return
            if page is None:
                page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
                group_count = 0
            rows.extend(page.evaluate(expression, pending))
            group_count += 1
            if group_count >= 24:
                page.close()
                page = None
                group_count = 0

        if args.section == "range":
            for kind in ("DDG", "CG", "SOV", "HULK"):
                for speed in (0, 15):
                    for alt in (15, 200):
                        for distance in (10, 20, 30, 40, 45, 50):
                            options = [dict(seed=s, kind=kind, rangeKm=distance, altM=alt, speedKt=speed, control="TARGET") for s in range(629300, 629305)]
                            evaluate("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRangeCase(o))", options)
                progress(kind)
            for control in ("SEA_CLUTTER", "CHAFF", "NO_TARGET"):
                for alt in (15, 200):
                    for distance in (10, 20, 30, 40, 45, 50):
                        options = [dict(seed=s, kind="DDG", rangeKm=distance, altM=alt, speedKt=0, control=control) for s in range(629300, 629305)]
                        evaluate("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRangeCase(o))", options)
                progress(control)
        elif args.section == "sam":
            for path in ("ESSM_BLOCK2_AIR", "SM6_BLOCK_IA_AIR", "SM6_BLOCK_IA_SURFACE"):
                targets = ["AIRCRAFT", "ASM", "SEA_CLUTTER", "CHAFF"] + (["SURFACE"] if path.endswith("SURFACE") else [])
                for target in targets:
                    for distance in (10, 20, 30, 40, 45, 50):
                        options = [dict(seed=s + 200000, path=path, targetKind=target, rangeKm=distance) for s in range(629300, 629305)]
                        evaluate("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runSamArhCase(o))", options)
                progress(path)
        elif args.section == "cue":
            for label in ("Kh-32", "Kh-35U"):
                for distance in (60, 100, 130):
                    for speed, turn in ((15, 0), (30, 0), (30, 30), (30, 90)):
                        options = [dict(seed=s, label=label, rangeKm=distance, speedKt=speed, turnDeg=turn) for s in range(729300, 729305)]
                        evaluate("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runCueCase(o))", options)
                progress(label)
        else:
            for kind in ("DDG", "CG", "SOV", "HULK"):
                for radar in ("SPY1DV", "SPQ9B", "BRIDGEMASTER_E"):
                    for distance in (5, 10, 20, 30, 40, 50, 70):
                        options = [dict(seed=s + 300000, kind=kind, radar=radar, rangeKm=distance) for s in range(629300, 629305)]
                        evaluate("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRadarCase(o))", options)
                progress(kind)
        if page is not None:
            page.close()
        browser.close()

    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_STAGE2_SHARD_1",
        "label": args.label,
        "section": args.section,
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "completedBefore": len(completed),
        "pageErrors": errors,
        collection_name: rows,
    }
    save(args.out, result)
    print(json.dumps({"section": args.section, "rows": len(rows), "skipped": len(completed), "errors": len(errors), "elapsedS": result["elapsedS"]}))


if __name__ == "__main__":
    main()
