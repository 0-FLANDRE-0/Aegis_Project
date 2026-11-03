#!/usr/bin/env python3
"""Run the same browser-engine matrix against one diagnostic HTML."""
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


def save(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    started = time.monotonic()
    body = args.html.read_bytes()
    errors: list[str] = []
    ranges: list[dict] = []
    sam: list[dict] = []
    cues: list[dict] = []
    radars: list[dict] = []
    audits: dict[str, dict] = {}
    progress_path = args.out.with_suffix(".progress.json")
    def progress(section: str, **detail: object) -> None:
        save(progress_path, {"schema": "AEGIS_SEEKER_UNIFY_A_DIAGNOSTIC_PROGRESS_1", "label": args.label, "section": section, **detail, "rcsAudits": audits, "rangeCases": ranges, "samArhCases": sam, "cueCases": cues, "radarCases": radars, "pageErrors": errors})
    with sync_playwright() as pw:
        browser = launch(pw)
        batch_page = None
        batch_count = 0
        def evaluate_cases(expression: str, opts: list[dict], ship: str = "DDG_119_LATE_FLIGHT_IIA") -> list[dict]:
            """Bound renderer lifetime while amortizing the 22 MB game load.

            The game intentionally owns many long-lived registries.  Reusing a
            renderer across hundreds of diagnostic resets makes the browser,
            rather than the simulation, the limiting resource and previously
            produced Target crashed/infinite evaluate failures.  A renderer is
            therefore retired after 24 five-seed comparison units (120 cases).
            Each case still calls the complete game reset fixture.
            """
            nonlocal batch_page, batch_count
            if batch_page is None:
                batch_page = load(browser, body, ship=ship, errors=errors)
                batch_count = 0
            result = batch_page.evaluate(expression, opts)
            batch_count += 1
            if batch_count >= 24:
                batch_page.close()
                batch_page = None
                batch_count = 0
            return result

        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        audits["DDG"] = page.evaluate("__SEEKER_UNIFY_A_DIAG__.rcsAudit()")
        page.close()
        for kind in ["DDG", "CG", "SOV", "HULK"]:
            for speed in [0, 15]:
                for alt in [15, 200]:
                    for distance in [10, 20, 30, 40, 45, 50]:
                        opts = [dict(seed=s, kind=kind, rangeKm=distance, altM=alt, speedKt=speed, control="TARGET") for s in range(629300, 629305)]
                        ranges.extend(evaluate_cases("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRangeCase(o))", opts))
            progress("range", kind=kind)
        for control in ["SEA_CLUTTER", "CHAFF", "NO_TARGET"]:
            for alt in [15, 200]:
                for distance in [10, 20, 30, 40, 45, 50]:
                    opts = [dict(seed=s, kind="DDG", rangeKm=distance, altM=alt, speedKt=0, control=control) for s in range(629300, 629305)]
                    ranges.extend(evaluate_cases("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRangeCase(o))", opts))
        for path in ["ESSM_BLOCK2_AIR", "SM6_BLOCK_IA_AIR", "SM6_BLOCK_IA_SURFACE"]:
            targets = ["AIRCRAFT", "ASM", "SEA_CLUTTER", "CHAFF"] + (["SURFACE"] if path.endswith("SURFACE") else [])
            for target in targets:
                for distance in [10, 20, 30, 40, 45, 50]:
                    opts = [dict(seed=s + 200000, path=path, targetKind=target, rangeKm=distance) for s in range(629300, 629305)]
                    sam.extend(evaluate_cases("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runSamArhCase(o))", opts))
            progress("sam", path=path)
        for label in ["Kh-32", "Kh-35U"]:
            for distance in [60, 100, 130]:
                for speed, turn in [(15, 0), (30, 0), (30, 30), (30, 90)]:
                    opts = [dict(seed=s, label=label, rangeKm=distance, speedKt=speed, turnDeg=turn) for s in range(729300, 729305)]
                    cues.extend(evaluate_cases("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runCueCase(o))", opts))
            progress("cue", missileLabel=label)
        for kind in ["DDG", "CG", "SOV", "HULK"]:
            for radar in ["SPY1DV", "SPQ9B", "BRIDGEMASTER_E"]:
                for distance in [5, 10, 20, 30, 40, 50, 70]:
                    opts = [dict(seed=s + 300000, kind=kind, radar=radar, rangeKm=distance) for s in range(629300, 629305)]
                    radars.extend(evaluate_cases("a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRadarCase(o))", opts))
            progress("radar", kind=kind)
        if batch_page is not None:
            batch_page.close()
            batch_page = None
        cg_page = load(browser, body, ship="CG_52_LATE_TICONDEROGA", errors=errors)
        audits["CG"] = cg_page.evaluate("__SEEKER_UNIFY_A_DIAG__.rcsAudit()")
        browser.close()
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_A_DIAGNOSTICS_1",
        "label": args.label,
        "input": str(args.html),
        "inputSha256": hashlib.sha256(body).hexdigest(),
        "elapsedS": time.monotonic() - started,
        "pageErrors": errors,
        "rcsAudits": audits,
        "rangeCases": ranges,
        "samArhCases": sam,
        "cueCases": cues,
        "radarCases": radars,
    }
    save(args.out, result)
    print(json.dumps({"label": args.label, "elapsedS": result["elapsedS"], "range": len(ranges), "sam": len(sam), "cue": len(cues), "radar": len(radars), "errors": len(errors)}))


if __name__ == "__main__":
    main()
