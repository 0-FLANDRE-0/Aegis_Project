#!/usr/bin/env python3
"""Final non-broad edge/contract checks omitted from the broad suite."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
PRODUCT = REPO_ROOT / "Aegis_SIM_v48_WIP_EMITTER_A.html"
DIAG = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_FINAL_DIAGNOSTIC.html")
sys.path[:0] = [str(REPO_ROOT / "docs/pip/B"), str(REPO_ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def capture(browser, body: bytes, ship: str, errors: list[str]) -> dict:
    page = load(browser, body, ship=ship, errors=errors)
    core = page.evaluate("()=>__EMITTER_A_FINAL_DIAG__.coreSelftest()")
    contract = page.evaluate("()=>__EMITTER_A_FINAL_DIAG__.contract()")
    edge = page.evaluate("()=>__EMITTER_A_FINAL_DIAG__.edge()")
    sov_enemy = page.evaluate("()=>__EMITTER_A_D_DIAG__.sovScene('ENEMY')")
    sov_snapshot = page.evaluate("()=>__EMITTER_A_FINAL_DIAG__.sovSnapshot()")
    threat = page.evaluate("()=>__SEEKER_U3_DIAG__.hojExerciseC()")
    page.close()
    return {"core": core, "contract": contract, "edge": edge, "sovEnemy": sov_enemy,
            "sovSnapshot": sov_snapshot, "threat": threat}


def main() -> None:
    body = DIAG.read_bytes()
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        first = {ship: capture(browser, body, ship, errors) for ship in
                 ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")}
        second = {ship: capture(browser, body, ship, errors) for ship in
                  ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")}
        browser.close()
    profiles = first["DDG_119_LATE_FLIGHT_IIA"]["contract"]["profiles"]
    checks = {
        "pageErrorsZero": not errors,
        "candidateCoreSelftest": all(q["core"]["pass"] for q in first.values()),
        "deterministicRepeatExact": first == second,
        "profileSchemaAndRefsValid": all(q["frozen"] and q["uniqueIds"] and q["uniqueOrders"] and all(all(r[k] for k in ("sensorOk", "hardpointOk", "enabledKeyOk", "mountKindOk")) for r in q["refs"]) for q in profiles),
        "runtimeIsolation": all(q["edge"]["command"]["ok"] and q["edge"]["ownBefore"] == q["edge"]["ownAfter"] and q["edge"]["allyAfter"] == {"enabled": {"SPY": False, "SPQ": False, "NAV": False}, "emcon": True} for q in first.values()),
        "jammerMaxCompatibility": all(len(q["edge"]["maxJammer"]) == 1 and q["edge"]["maxJammer"][0]["value"]["power"] == 2000 for q in first.values()),
        "rotorWrapFinite": all(len([row for row in q["edge"]["wrap"] if row["value"].get("beamAz") is not None]) == 2 and all(isinstance(row["value"]["beamAz"], (int, float)) for row in q["edge"]["wrap"] if row["value"].get("beamAz") is not None) for q in first.values()),
        "anonymousReceiverNoTruthFields": all(q["edge"]["anonymousPlots"]["count"] > 0 and q["edge"]["anonymousPlots"]["forbiddenPresent"] is False for q in first.values()),
        "ddgAndCgWithSovInactive": all(q["sovEnemy"]["sovEmitterCount"] == 0 and q["sovEnemy"]["sovReceiver"]["plots"] == [] and q["sovEnemy"]["sovAttack"]["active"] is False for q in first.values()),
        "sovSnapshotContract": all(len(q["sovSnapshot"]["ships"]) == 1 and q["sovSnapshot"]["ships"][0]["emitters"] == 0 and q["sovSnapshot"]["ships"][0]["esmContacts"] == 0 and q["sovSnapshot"]["ships"][0]["attackActive"] is False for q in first.values()),
        "confirmedOnlyFeatureOff": all(q["threat"]["checks"]["confirmedOnlyOff"] and q["threat"]["checks"]["confirmedOnlyConsumesNoRng"] for q in first.values()),
    }
    result = {"schema": "AEGIS_EMITTER_A_FINAL_LIMITED_GATE_1",
              "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
              "productSha256": hashlib.sha256(PRODUCT.read_bytes()).hexdigest(),
              "diagnosticSha256": hashlib.sha256(body).hexdigest(),
              "pageErrors": errors, "first": first, "second": second}
    (HERE / "FINAL_LIMITED_GATE.json").write_text(strict(result))
    print(strict({"status": result["status"], "checks": checks, "pageErrors": errors}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
