#!/usr/bin/env python3
"""Commit C limited common association/state SHADOW -> ACTIVE gate.

This is deliberately not the project-wide MAX_THREAT regression.  It uses at
most 30 representative branches per weapon/state family and fresh pages for
determinism.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "docs/pip/B"), str(ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


RUNTIME = r"""()=>{
 const d=window.__NAVAL_SIM_DIAG__,c=window.__SEEKER_U4_C__;
 const lifecycle=(()=>{const save=d.exportOperationalStateV48Wip11A(),text=JSON.stringify(save),valid=d.validateOperationalStateV48Wip11B(save);return {
   valid:valid.ok===true,noU4SaveSchema:!text.includes('SEEKER_U4'),saveSchema:save.schema??null,shipSchema:save.ship?.schema??null};})();
 const harpoon={seeker:__HARPOON_DIAG_A__.seekerAudit(),core:__HARPOON_DIAG_A__.coreAudit(),selection:__HARPOON_DIAG_A__.selectionAudit()};
 const asm=d.runWip108AsmAcquireCase({label:'Kh-35U',speedKt:0,seed:108041,headingDeg:90,rangeKm:18,maxTimeS:20,emconActive:true});
 const sarh=d.runWip107SarhCase({label:'Kh-35U',speedKt:0,seed:107241,headingDeg:90,rangeKm:25,maxTimeS:35});
 const arh=d.runWip107EssmCase({label:'Kh-35U',speedKt:0,seed:107341,headingDeg:90,rangeKm:12,maxTimeS:25});
 const ram=d.runWip107RamMotionCase({seed:107441,rangeKm:6,maxTimeS:32});
 return {core:Array.from(window.__CORE_SELFTEST_FAILURES__??[]),matrix:c?.syntheticMatrix?.()??null,contract:c?.contractAudit?.()??null,
   lifecycle,harpoon,asm,sarh,arh,ram,snapshot:c?.snapshot?.()??null,u2:{activeComponents:[...(__SEEKER_COMMON_U2__.activeComponents??[])],
   shadowComponents:[...(__SEEKER_COMMON_U2__.shadowComponents??[])],commonStateMode:__SEEKER_COMMON_U2__.commonStateMode??null}};
}"""


def run_product(pw, path: Path, has_c: bool) -> dict:
    errors: list[str] = []
    browser = launch(pw)
    page = load(browser, path.read_bytes(), ship="DDG_119_LATE_FLIGHT_IIA", seed=0xC40001, errors=errors)
    if has_c:
        result = page.evaluate(RUNTIME)
    else:
        result = page.evaluate(RUNTIME.replace("const d=window.__NAVAL_SIM_DIAG__,c=window.__SEEKER_U4_C__;", "const d=window.__NAVAL_SIM_DIAG__,c=null;"))
    page.close(); browser.close()
    return {"path": path.name, "sha256": sha(path), "result": result, "errors": errors}


def tactical(result: dict) -> dict:
    r = result["result"]
    # C-only audit/mode telemetry is intentionally omitted from equivalence.
    return {k: r[k] for k in ("core", "lifecycle", "harpoon", "asm", "sarh", "arh", "ram")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--shadow", type=Path, required=True)
    ap.add_argument("--active", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(); started = time.monotonic()
    with sync_playwright() as pw:
        baseline = run_product(pw, args.baseline, False)
        shadow = run_product(pw, args.shadow, True)
        active = run_product(pw, args.active, True)
        repeat = run_product(pw, args.active, True)
    ss = shadow["result"]["snapshot"] or {}; aa = active["result"]["snapshot"] or {}
    checks = {
        "shadowTacticalExact": tactical(shadow) == tactical(baseline),
        "activeTacticalExact": tactical(active) == tactical(baseline),
        "activeDeterministic": tactical(active) == tactical(repeat),
        "coreSelfTests": all(not q["result"]["core"] for q in (baseline, shadow, active, repeat)),
        "pageErrorsZero": not any(q["errors"] for q in (baseline, shadow, active, repeat)),
        "shadowMode": ss.get("mode") == "SHADOW" and shadow["result"]["u2"]["commonStateMode"] == "SHADOW",
        "activeMode": aa.get("mode") == "ACTIVE" and active["result"]["u2"]["commonStateMode"] == "ACTIVE",
        "shadowComparisonsExact": ss.get("audit", {}).get("associationMismatches") == 0 and ss.get("audit", {}).get("stateMismatches") == 0 and ss.get("audit", {}).get("stateComparisons", 0) > 0,
        "matrix": bool(active["result"]["matrix"] and active["result"]["matrix"]["pass"]),
        "anonymousContract": bool(active["result"]["contract"] and active["result"]["contract"]["pass"]),
        "allFamiliesRouted": all(aa.get("audit", {}).get("families", {}).get(k, 0) > 0 for k in ("ASM", "HARPOON", "SARH", "ARH", "RAM")),
        "eventsCovered": all(aa.get("audit", {}).get("events", {}).get(k, 0) > 0 for k in ("VALID_MEASUREMENT", "HIT_ACCUMULATION", "MISS_COAST", "REACQUIRE", "GIMBAL_LOS_ILLUMINATION_SIGNAL_LOSS", "TIMEOUT_LOST_OFF", "DESTROY_RETIRE")),
        "rngAndSavePreserved": aa.get("rngConsumedByCommonLayer") is False and aa.get("saveSchemaChanged") is False and active["result"]["lifecycle"]["valid"] and active["result"]["lifecycle"]["noU4SaveSchema"],
        "actualFlightsFinite": all(active["result"][k].get("error") is None and active["result"][k].get("durationS", 0) > 0 for k in ("sarh", "arh", "ram")),
    }
    result = {"schema":"AEGIS_SEEKER_UNIFY_U4_C_GATE_1", "status":"PASS" if all(checks.values()) else "FAIL",
      "elapsedS":time.monotonic()-started, "broadRegressionRun":False, "representativeBranchesPerWeaponStateMax":30,
      "checks":checks, "baseline":baseline, "shadow":shadow, "active":active, "activeRepeat":repeat, "release":False}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({"status":result["status"], "elapsedS":result["elapsedS"], "checks":checks,
      "shadowAudit":ss.get("audit"), "activeAudit":aa.get("audit")}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
