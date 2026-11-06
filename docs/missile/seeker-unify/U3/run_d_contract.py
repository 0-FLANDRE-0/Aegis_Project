#!/usr/bin/env python3
"""Commit D passive-RF candidate SHADOW -> ACTIVE contract gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path[:0] = ["/workspace/aegis-ui-a/docs/pip/B", "/workspace/aegis-ui-a/docs/bunkerhill/K"]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


EQUIPMENT_JOBS = [
    {"seed": 986000 + index, "label": label, "rangeKm": distance,
     "altitudeM": 10000 if label == "Kh-32" else 1200, "condition": "ALL_ON",
     "samples": 12, "threatMode": "MAX_THREAT"}
    for index, (label, distance) in enumerate(
        ([("Kh-35U", 60), ("Kh-35U", 100), ("Kh-32", 60), ("Kh-32", 100)]) * 3
    )
]
CUE_JOBS = [
    {"seed": 986100 + index, "label": label, "rangeKm": distance,
     "speedKt": 30, "turnDeg": turn, "emcon": False}
    for index, (label, distance, turn) in enumerate((
        ("Kh-35U", 60, 0), ("Kh-35U", 100, 45), ("Kh-32", 60, 0), ("Kh-32", 100, 45)
    ))
]
CONFIRMED_JOBS = [
    {"seed": 986200 + index, "label": label, "rangeKm": 60,
     "altitudeM": 10000 if label == "Kh-32" else 1200}
    for index, label in enumerate(("Kh-35U", "Kh-32", "Kh-35U", "Kh-32"))
]


def run(pw, path: Path) -> dict:
    body = path.read_bytes(); browser = launch(pw); errors: list[str] = []
    page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    selection = page.evaluate("()=>__SEEKER_U3_DIAG__.passiveSelectionD()")
    audit_after_synthetic = page.evaluate("()=>__SEEKER_U3_DIAG__.passiveAuditD()")
    equipment = page.evaluate("a=>a.map(o=>__CUE_A1_STAGE2_DIAG__.runEquipmentCase(o))", EQUIPMENT_JOBS)
    cue = page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runCueCase(o))", CUE_JOBS)
    confirmed = page.evaluate("a=>a.map(o=>__CUE_A1_STAGE2_DIAG__.runConfirmedBandCase(o))", CONFIRMED_JOBS)
    repeat = page.evaluate("a=>a.map(o=>__CUE_A1_STAGE2_DIAG__.runEquipmentCase(o))", EQUIPMENT_JOBS)
    audit = page.evaluate("()=>__SEEKER_U3_DIAG__.passiveAuditD()")
    page.close(); browser.close()
    return {"sha256": hashlib.sha256(body).hexdigest(), "selection": selection,
            "equipment": equipment, "cue": cue, "confirmed": confirmed, "auditAfterSynthetic": audit_after_synthetic,
            "repeat": repeat, "audit": audit, "errors": errors}


def differences(left: list, right: list) -> list[dict]:
    return [{"index": i, "left": a, "right": b} for i, (a, b) in enumerate(zip(left, right)) if a != b]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--shadow", type=Path, required=True)
    ap.add_argument("--active", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(); started = time.monotonic()
    with sync_playwright() as pw:
        baseline, shadow, active = run(pw, args.baseline), run(pw, args.shadow), run(pw, args.active)
    shadow_equipment = differences(baseline["equipment"], shadow["equipment"])
    shadow_cue = differences(baseline["cue"], shadow["cue"])
    shadow_confirmed = differences(baseline["confirmed"], shadow["confirmed"])
    active_equipment = differences(baseline["equipment"], active["equipment"])
    active_cue = differences(baseline["cue"], active["cue"])
    active_confirmed = differences(baseline["confirmed"], active["confirmed"])
    active_changed = bool(active_equipment or active_cue or active_confirmed)
    shadow_observed_difference = (shadow["audit"] or {}).get("differences", 0) > (shadow["auditAfterSynthetic"] or {}).get("differences", 0)
    checks = {
        "shadowSelectorContract": bool(shadow["selection"].get("pass")),
        "activeSelectorContract": bool(active["selection"].get("pass")),
        "shadowTacticalEquipmentEqual": not shadow_equipment,
        "shadowTacticalCueEqual": not shadow_cue,
        "shadowConfirmedScenesEqual": not shadow_confirmed,
        "shadowComparedRealCandidates": (shadow["audit"] or {}).get("comparisons", 0) > (shadow["auditAfterSynthetic"] or {}).get("comparisons", 0),
        "activeDifferencesExplainedByShadowPolicy": shadow_observed_difference if active_changed else not shadow_observed_difference,
        "activeRepeatedInputDeterministic": active["equipment"] == active["repeat"],
        "confirmedKh32FeatureOff": all(row.get("measurement") is None for row in active["confirmed"] if row["setup"]["label"] == "Kh-32"),
        "rngFree": bool((active["audit"] or {}).get("rngConsumed") is False),
        "truthFreeSelector": bool((active["audit"] or {}).get("truthFieldsUsed") is False),
        "pageErrorsZero": not any(q["errors"] for q in (baseline, shadow, active)),
    }
    passed = all(checks.values())
    result = {
        "schema": "AEGIS_SEEKER_UNIFY_U3_D_GATE_1", "status": "PASS" if passed else "FAIL",
        "elapsedS": time.monotonic() - started, "checks": checks,
        "sceneCounts": {"equipment": len(EQUIPMENT_JOBS), "naturalCue": len(CUE_JOBS), "confirmedOnly": len(CONFIRMED_JOBS), "perBranch": len(EQUIPMENT_JOBS) + len(CUE_JOBS) + len(CONFIRMED_JOBS)},
        "differences": {"shadowEquipment": shadow_equipment, "shadowCue": shadow_cue, "shadowConfirmed": shadow_confirmed,
                        "activeEquipment": active_equipment, "activeCue": active_cue, "activeConfirmed": active_confirmed},
        "baseline": baseline, "shadow": shadow, "active": active,
        "confirmedOnlyPerformance": "UNVERIFIED_FEATURE_OFF_AND_LIMITED_SCENES_ONLY",
    }
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "elapsedS": result["elapsedS"], "checks": checks,
                      "shadowAudit": shadow["audit"], "activeAudit": active["audit"],
                      "activeDifferenceCounts": {"equipment": len(active_equipment), "cue": len(active_cue), "confirmed": len(active_confirmed)}}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()

