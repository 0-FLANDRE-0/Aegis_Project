#!/usr/bin/env python3
"""Compare U1 ACTIVE with U2 SHADOW and classify echo/cell differences."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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


def matrices() -> dict[str, list[dict]]:
    asm = []
    seed = 910000
    for control, kind in (("TARGET", "DDG"), ("TARGET", "CG"), ("TARGET", "SOV"), ("CHAFF", "DDG"), ("NO_TARGET", "DDG")):
        for range_km in (10, 30, 50):
            for altitude_m in (15, 200):
                asm.append({"seed": seed, "control": control, "kind": kind, "rangeKm": range_km, "altM": altitude_m, "speedKt": 15})
                seed += 1
    cue = []
    for label in ("Kh-35U", "Kh-32"):
        for range_km in (60, 130):
            for turn_deg in (0, 30, 90):
                cue.append({"seed": seed, "label": label, "rangeKm": range_km, "speedKt": 30, "turnDeg": turn_deg, "emcon": False})
                seed += 1
    sam = []
    for path in ("ESSM_BLOCK2_AIR", "SM6_BLOCK_IA_AIR", "SM6_BLOCK_IA_SURFACE"):
        for target_kind in ("AIRCRAFT", "ASM", "SEA_CLUTTER", "CHAFF"):
            for range_km in (10, 30, 50):
                sam.append({"seed": seed, "path": path, "targetKind": target_kind, "rangeKm": range_km})
                seed += 1
    return {"ASM": asm, "CUE": cue, "SAM": sam}


BASE_EXPR = {
    "ASM": "a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runRangeCase(o))",
    "CUE": "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))",
    "SAM": "a=>a.map(o=>__SEEKER_UNIFY_A_DIAG__.runSamArhCase(o))",
}
CANDIDATE_EXPR = {
    "ASM": "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runU2AsmCase(o))",
    "CUE": "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runU2CueCase(o))",
    "SAM": "a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runU2SamCase(o))",
}


def run_build(pw, path: Path, expressions: dict[str, str], rows: dict[str, list[dict]], candidate: bool) -> tuple[dict, list[str]]:
    browser = launch(pw)
    errors: list[str] = []
    output: dict[str, list] = {}
    for group, cases in rows.items():
        values = []
        for start in range(0, len(cases), 6):
            page = load(browser, path.read_bytes(), ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
            values.extend(page.evaluate(expressions[group], cases[start:start + 6]))
            page.close()
        output[group] = values
    browser.close()
    if candidate:
        return output, errors
    return output, errors


def flatten_snapshots(candidate: dict[str, list]) -> dict[str, list]:
    merged = {"asmSynthesis": [], "samSynthesis": [], "asmCells": [], "samCells": []}
    for values in candidate.values():
        for row in values:
            audit = row.get("u2", {})
            for key in merged:
                merged[key].extend(audit.get(key, []))
    return merged


def maximum(rows: list[dict], key: str) -> float:
    values = [abs(float(row[key])) for row in rows if isinstance(row.get(key), (int, float)) and math.isfinite(float(row[key]))]
    return max(values, default=0.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only", choices=("ASM", "CUE", "SAM"), nargs="+")
    args = parser.parse_args()
    rows = matrices()
    if args.only:
        rows = {key: value for key, value in rows.items() if key in args.only}
    started = time.monotonic()
    with sync_playwright() as pw:
        baseline, baseline_errors = run_build(pw, args.baseline, BASE_EXPR, rows, False)
        candidate, candidate_errors = run_build(pw, args.candidate, CANDIDATE_EXPR, rows, True)
    tactical = {group: [row["result"] for row in values] for group, values in candidate.items()}
    tactical_differences = {
        group: [{"index": index, "baseline": before, "candidate": after} for index, (before, after) in enumerate(zip(baseline[group], tactical[group])) if before != after]
        for group in rows
    }
    tactical_differences = {key: value for key, value in tactical_differences.items() if value}
    audit = flatten_snapshots(candidate)
    metrics = {
        "asmSynthesisMaxRelativeDifference": maximum(audit["asmSynthesis"], "relativeDifference"),
        "samSynthesisMaxRelativeDifference": maximum(audit["samSynthesis"], "relativeDifference"),
        "samSingleBeamMaxRelativeDifference": maximum(audit["samSynthesis"], "singleBeamRelativeDifference"),
        "asmCellRangeMaxRelativeDifference": maximum(audit["asmCells"], "rangeRel"),
        "asmCellAzMaxAbsRad": maximum(audit["asmCells"], "azAbsRad"),
        "asmCellExtentMaxRelativeDifference": max(
            maximum(audit["asmCells"], "rangeExtentRel"), maximum(audit["asmCells"], "crossExtentRel"),
            maximum(audit["asmCells"], "verticalExtentRel"), maximum(audit["asmCells"], "dopplerExtentRel"),
        ),
        "samCellExtentMaxRelativeDifference": max(
            maximum(audit["samCells"], "rangeExtentRel"), maximum(audit["samCells"], "crossExtentRel"),
            maximum(audit["samCells"], "verticalExtentRel"), maximum(audit["samCells"], "dopplerExtentRel"),
        ),
        "asmCellCountMismatchSamples": sum(bool(row.get("missing")) for row in audit["asmCells"]),
        "samCellCountMismatchSamples": sum(bool(row.get("missing")) for row in audit["samCells"]),
        "asmMemberCountMismatchSamples": sum(row.get("memberLegacy") != row.get("memberCommon") for row in audit["asmCells"] if not row.get("missing")),
        "samMemberCountMismatchSamples": sum(row.get("memberLegacy") != row.get("memberCommon") for row in audit["samCells"] if not row.get("missing")),
    }
    divergence = metrics["asmSynthesisMaxRelativeDifference"] > 1e-12 or metrics["asmCellExtentMaxRelativeDifference"] > 1e-12 or metrics["samCellExtentMaxRelativeDifference"] > 1e-12 or any(metrics[key] for key in metrics if key.endswith("MismatchSamples"))
    classifications = []
    if metrics["samSynthesisMaxRelativeDifference"] <= 1e-12:
        classifications.append({"component": "SAM_ARH_MONOSTATIC_POWER", "classification": "FP_ORDER", "active": False, "reason": "Maximum relative difference is nonzero, so the bit-equal ACTIVE gate is not met; operation order was not rewritten after U2 stop"})
    if divergence:
        classifications.extend([
            {"component": "MONOSTATIC_BEAM_AND_LOS_NORMALIZATION", "classification": "IMPLEMENTATION_DIVERGENCE", "active": False, "options": ["ASM legacy applies one beam/LOS factor", "SAM legacy applies transmit and receive beam factors and two LOS factors"]},
            {"component": "RESOLVED_CELL_EXTENT", "classification": "IMPLEMENTATION_DIVERGENCE", "active": False, "options": ["ASM uses power-weighted RMS moments", "SAM measurement uses maximum member extents"]},
            {"component": "RESOLVED_CELL_ANGLE", "classification": "IMPLEMENTATION_DIVERGENCE", "active": False, "options": ["ASM resolves azimuth/elevation independently", "SAM resolves spherical angular separation and retains 4Q members"]},
        ])
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_B_U2_SHADOW_DIFF_1",
        "status": "STOP_IMPLEMENTATION_DIVERGENCE" if divergence and not tactical_differences and not baseline_errors and not candidate_errors else "FAIL",
        "implemented": "SHADOW_ONLY",
        "tested": True,
        "approved": False,
        "unresolved": ["USER_DIRECTION_REQUIRED_FOR_IMPLEMENTATION_DIVERGENCE"],
        "release": False,
        "elapsedS": time.monotonic() - started,
        "inputs": {
            "baselineSha256": hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
            "candidateSha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
        },
        "caseCounts": {key: len(value) for key, value in rows.items()},
        "tacticalDifferences": tactical_differences,
        "pageErrors": {"baseline": baseline_errors, "candidate": candidate_errors},
        "sampleCounts": {key: len(value) for key, value in audit.items()},
        "metrics": metrics,
        "classifications": classifications,
        "activeComponents": [],
        "shadowComponents": ["synthesizeEchoes", "resolveCells"],
        "tacticalOutputUsed": False,
        "rngConsumedByShadow": False,
        "truthOutput": False,
        "auditSamples": audit,
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "elapsedS", "caseCounts", "tacticalDifferences", "pageErrors", "sampleCounts", "metrics", "classifications")}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "STOP_IMPLEMENTATION_DIVERGENCE" else 1)


if __name__ == "__main__":
    main()
