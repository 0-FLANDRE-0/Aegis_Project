#!/usr/bin/env python3
"""Run the CUE_A-1 Stage-2 passive-RF equipment, mixing and accuracy tests."""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


HARNESS_ROOT = Path("/workspace/aegis-ui-a")
sys.path[:0] = [str(HARNESS_ROOT / p) for p in ("docs/pip/B", "docs/helicopter/H", "docs/multiship/G", "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load


def batches(page, expression: str, jobs: list[dict], size: int = 20) -> list[dict]:
    rows: list[dict] = []
    for offset in range(0, len(jobs), size):
        rows.extend(page.evaluate(expression, jobs[offset:offset + size]))
    return rows


def run_page(browser, body: bytes, errors: list[str]) -> dict:
    page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    equipment_jobs = [
        {"seed": seed, "label": label, "rangeKm": distance, "altitudeM": 10000 if label == "Kh-32" else 1200,
         "condition": condition, "samples": 12, "threatMode": "MAX_THREAT"}
        for label in ("Kh-35U", "Kh-32")
        for distance in (60, 100, 130)
        for seed in range(849300, 849305)
        for condition in ("ALL_ON", "SPY_OFF", "SPQ_OFF", "NAV_OFF", "ALL_OFF")
    ]
    contaminant_jobs = [
        {"seed": seed, "label": label, "kind": kind, "threatMode": "MAX_THREAT"}
        for label in ("Kh-35U", "Kh-32")
        for kind in ("ESSM_ARH", "SM6_ARH", "AIR_RADAR", "NULKA", "SHIP_JAMMER")
        for seed in range(849500, 849505)
    ]
    range_jobs = [
        {"seed": seed, "label": label, "threatMode": "MAX_THREAT", "rangeKm": distance,
         "altitudeM": 10000 if label == "Kh-32" else 12, "samples": 20}
        for label, distances in (("Kh-35U", (10, 20, 30)), ("Kh-32", (60, 100, 130)))
        for distance in distances for seed in range(839500, 839505)
    ]
    multi_jobs = [
        {"seed": seed, "label": label, "threatMode": "MAX_THREAT", "rangeKm": 80,
         "altitudeM": 800, "offsetDeg": offset, "otherRangeKm": other_range}
        for label in ("Kh-35U", "Kh-32")
        for offset, other_range in ((1, 75), (3, 80), (-3, 85))
        for seed in range(839600, 839605)
    ]
    confirmed_jobs = [
        {"seed": seed, "label": label, "rangeKm": 60, "altitudeM": 10000 if label == "Kh-32" else 1200}
        for label in ("Kh-35U", "Kh-32") for seed in (849700, 849701)
    ]
    value = {
        "contract": page.evaluate("__CUE_A1_STAGE2_DIAG__.contract()"),
        "beam": page.evaluate("__CUE_A1_STAGE2_DIAG__.runBeamUnitCases()"),
        "equipment": batches(page, "a=>a.map(o=>__CUE_A1_STAGE2_DIAG__.runEquipmentCase(o))", equipment_jobs, 10),
        "contaminants": batches(page, "a=>a.map(o=>__CUE_A1_STAGE2_DIAG__.runContaminantCase(o))", contaminant_jobs, 10),
        "rangeAccuracy": batches(page, "a=>a.map(o=>__SEEKER_UNIFY_C_DIAG__.runPassiveRangeCase(o))", range_jobs, 10),
        "multiEmitter": batches(page, "a=>a.map(o=>__SEEKER_UNIFY_C_DIAG__.runMultiEmitterCase(o))", multi_jobs, 10),
        "confirmedOnly": batches(page, "a=>a.map(o=>__CUE_A1_STAGE2_DIAG__.runConfirmedBandCase(o))", confirmed_jobs, 4),
    }
    page.close()
    return value


def summarize_equipment(rows: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for label in ("Kh-35U", "Kh-32"):
        out[label] = {}
        for condition in ("ALL_ON", "SPY_OFF", "SPQ_OFF", "NAV_OFF", "ALL_OFF"):
            selected = [row for row in rows if row["setup"]["label"] == label and row["setup"]["condition"] == condition]
            samples = [sample for row in selected for sample in row["rows"] if sample["available"]]
            intervals = [row["summary"]["meanReceiveIntervalS"] for row in selected if row["summary"]["meanReceiveIntervalS"] is not None]
            out[label][condition] = {
                "cases": len(selected), "availableSamples": len(samples),
                "families": {family: sum(sample["family"] == family for sample in samples) for family in sorted({sample["family"] for sample in samples})},
                "meanAbsBearingErrorDeg": statistics.fmean(abs(sample["bearingErrorDeg"]) for sample in samples) if samples else None,
                "meanAbsElevationErrorDeg": statistics.fmean(abs(sample["elevationErrorDeg"]) for sample in samples) if samples else None,
                "meanReceiveIntervalS": statistics.fmean(intervals) if intervals else None,
            }
    return out


def summarize_range(rows: list[dict]) -> dict:
    out = {}
    for label in ("Kh-35U", "Kh-32"):
        selected = [row for row in rows if row["setup"]["label"] == label]
        means = [row["afterActionTruth"]["meanErrorM"] for row in selected if row["afterActionTruth"]["meanErrorM"] is not None]
        rmses = [row["afterActionTruth"]["rmseM"] for row in selected if row["afterActionTruth"]["rmseM"] is not None]
        out[label] = {"cases": len(selected), "availableSamples": sum(row["availableSamples"] for row in selected),
                      "meanOfCaseMeanErrorM": statistics.fmean(means) if means else None,
                      "meanCaseRmseM": statistics.fmean(rmses) if rmses else None}
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    before_body, after_body = args.baseline.read_bytes(), args.candidate.read_bytes()
    started = time.monotonic();before_errors: list[str] = [];after_errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        before = run_page(browser, before_body, before_errors)
        after = run_page(browser, after_body, after_errors)
        browser.close()
    before_equipment, after_equipment = summarize_equipment(before["equipment"]), summarize_equipment(after["equipment"])
    contaminant_selected = [{"setup": row["setup"], "selected": row["selected"]} for row in after["contaminants"] if row["selected"]]
    confirmed = after["confirmedOnly"]
    confirmed_checks = {
        "kh32PassiveDisabled": all(row["measurement"] is None for row in confirmed if row["setup"]["label"] == "Kh-32"),
        "kh35OnlyXBandSelected": all((row["measurement"] or {}).get("frequencyMHz") == 10000 and (row["measurement"] or {}).get("family") == "SURFACE SEARCH RADAR" for row in confirmed if row["setup"]["label"] == "Kh-35U"),
        "performance": "UNVERIFIED",
    }
    protected_equal = before["contract"]["hoj"] == after["contract"]["hoj"] and before["contract"]["hojTrack"] == after["contract"]["hojTrack"]
    checks = {
        "stage2ContractActive": bool(after["contract"]["stage2"]),
        "beamSweepCrossingAndFloor": after["beam"] == {"stage2": True, "crossed": 1, "missed": .015, "doubleCrossed": 1, "spy": 1},
        "equipmentRowsComplete": len(before["equipment"]) == 150 and len(after["equipment"]) == 150,
        "allOffReceivesNothing": all(after_equipment[label]["ALL_OFF"]["availableSamples"] == 0 for label in after_equipment),
        "contaminantSelectionsZero": not contaminant_selected,
        "contaminantRowsComplete": len(after["contaminants"]) == 50,
        "hojFunctionsByteEqual": protected_equal,
        "rangeAccuracyRowsComplete": len(after["rangeAccuracy"]) == 30,
        "multiEmitterRowsComplete": len(after["multiEmitter"]) == 30,
        "confirmedOnlyStaticScenes": all(value is True or key == "performance" for key, value in confirmed_checks.items()),
        "pageErrorsZero": not before_errors and not after_errors,
    }
    result = {
        "schema": "AEGIS_CUE_A_1_STAGE2_PASSIVE_RF_TESTS_1", "status": "PASS" if all(checks.values()) else "FAIL",
        "baseline": {"path": str(args.baseline), "sha256": hashlib.sha256(before_body).hexdigest()},
        "candidate": {"path": str(args.candidate), "sha256": hashlib.sha256(after_body).hexdigest()},
        "elapsedS": time.monotonic() - started, "checks": checks,
        "summary": {"equipmentBefore": before_equipment, "equipmentAfter": after_equipment,
                    "contaminantsSelectedAfter": contaminant_selected,
                    "rangeBefore": summarize_range(before["rangeAccuracy"]), "rangeAfter": summarize_range(after["rangeAccuracy"]),
                    "confirmedOnly": confirmed_checks},
        "before": before, "after": after, "pageErrors": {"before": before_errors, "after": after_errors},
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"status": result["status"], "elapsedS": result["elapsedS"], "checks": checks,
                      "equipmentBefore": before_equipment, "equipmentAfter": after_equipment,
                      "rangeBefore": result["summary"]["rangeBefore"], "rangeAfter": result["summary"]["rangeAfter"],
                      "confirmedOnly": confirmed_checks}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
