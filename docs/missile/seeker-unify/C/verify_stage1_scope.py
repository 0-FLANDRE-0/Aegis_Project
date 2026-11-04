#!/usr/bin/env python3
"""Compare browser-visible function source hashes outside the U2 Stage 1 scope."""
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


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def global_functions(pw, path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    browser = launch(pw)
    page = load(browser, path.read_bytes(), ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    rows = page.evaluate("""()=>Object.fromEntries(Object.getOwnPropertyNames(window).sort().flatMap(name=>{
      let value;try{value=window[name];}catch(_){return [];}return typeof value==='function'?[[name,Function.prototype.toString.call(value)]]:[];
    }))""")
    page.close()
    browser.close()
    return rows, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with sync_playwright() as pw:
        before, before_errors = global_functions(pw, args.baseline)
        after, after_errors = global_functions(pw, args.candidate)
    shared = sorted(set(before) & set(after))
    changed = sorted(name for name in shared if before[name] != after[name])
    removed = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    allowed_changed = {
        "asmSeekerCompositeReturns", "asmSeekerEchoMeasurement", "_arhNormalizedMonostaticPower", "_arhClusterEchoes",
    }
    allowed_removed = {
        "seekerU2Finite", "seekerU2Push", "seekerU2Rel", "seekerU2Reset", "seekerU2Snapshot", "seekerMonostaticPowerU2",
        "seekerAsmPowerPairU2", "seekerSamPowerPairU2", "seekerEchoesUnresolvedU2", "seekerCompareAsmCellsU2", "seekerCompareSamCellsU2",
    }
    allowed_added = {
        "seekerResolveAsmCellsLegacyEquivalentU2", "seekerResolveSamCellsLegacyEquivalentU2", "seekerSynthesizeMonostaticPowerU2",
        "seekerResolveCellsU2", "seekerResolvedCellStatisticsU2", "seekerU2ActiveSnapshot",
    }
    unexpected = {
        "changed": sorted(set(changed) - allowed_changed),
        "removed": sorted(set(removed) - allowed_removed),
        "added": sorted(set(added) - allowed_added),
    }
    status = "PASS" if not any(unexpected.values()) and not before_errors and not after_errors else "FAIL"
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_C_STAGE1_FUNCTION_SCOPE_2",
        "status": status,
        "baselineGlobalFunctionCount": len(before),
        "candidateGlobalFunctionCount": len(after),
        "unchangedSharedFunctions": len(shared) - len(changed),
        "changed": [{"name": name, "beforeSha256": sha(before[name]), "afterSha256": sha(after[name])} for name in changed],
        "removed": [{"name": name, "sha256": sha(before[name])} for name in removed],
        "added": [{"name": name, "sha256": sha(after[name])} for name in added],
        "unexpected": unexpected,
        "pageErrors": {"baseline": before_errors, "candidate": after_errors},
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()

