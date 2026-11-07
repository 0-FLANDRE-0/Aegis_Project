#!/usr/bin/env python3
"""Commit B DDG/CG SHADOW equivalence and isolation gate."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parents[3] / "Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html"
SHADOW = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_B_SHADOW.html")
BASE_DIAG = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_U3_DIAGNOSTIC.html")
SHADOW_DIAG = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_B_DIAGNOSTIC.html")
EXPECTED = json.loads((HERE / "BASELINE_AUDIT.json").read_text())
sys.path[:0] = ["/workspace/aegis-ui-a/docs/pip/B", "/workspace/aegis-ui-a/docs/bunkerhill/K"]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def run_profile(browser, body: bytes, profile: str, errors: list[str]) -> dict:
    page = load(browser, body, ship=profile, errors=errors)
    matrix = page.evaluate("()=>__EMITTER_A_BASELINE__.matrix()")
    # ACTIVE_SHIP_PROFILE/RUNTIME are top-level lexical bindings, not window
    # properties.  The diagnostic matrix deliberately exports their public
    # identifiers, so use those rather than depending on browser globals.
    api = page.evaluate("ids=>{const d=__SHIP_EMITTERS_A__.definitions(ids.profileId);return {mode:__SHIP_EMITTERS_A__.mode,definition:d,definitionFrozen:Object.isFrozen(d)&&Object.isFrozen(d.entries)&&d.entries.every(Object.isFrozen),validation:__SHIP_EMITTERS_A__.validate(ids.profileId),runtime:__SHIP_EMITTERS_A__.runtime(ids.entityId),audit:__SHIP_EMITTERS_A__.audit()};}", {"profileId": matrix["profileId"], "entityId": matrix["entityId"]})
    page.close()
    return {"matrix": matrix, "api": api}


def run_scene(browser, body: bytes, active: str, ally: str, errors: list[str]) -> dict:
    page = load(browser, body, ship=active, errors=errors)
    scene = page.evaluate("p=>__EMITTER_A_BASELINE__.fleetScene(p)", {"allyProfileId": ally})
    audit = page.evaluate("()=>__SHIP_EMITTERS_A__.audit()")
    page.close()
    return {"scene": scene, "audit": audit}


def run_legacy_controls(browser, body: bytes, errors: list[str]) -> dict:
    page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    rows = {"hoj": page.evaluate("()=>__SEEKER_U3_DIAG__.hojExerciseC()"),
            "passive": page.evaluate("()=>__SEEKER_U3_DIAG__.passiveSelectionD()")}
    page.close()
    return rows


def main() -> None:
    started = time.monotonic()
    base_body, shadow_body = BASE_DIAG.read_bytes(), SHADOW_DIAG.read_bytes()
    errors: list[str] = []
    profiles: dict[str, object] = {}
    scenes: dict[str, object] = {}
    with sync_playwright() as pw:
        browser = launch(pw)
        for profile in ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"):
            profiles[profile] = run_profile(browser, shadow_body, profile, errors)
        for scene_id, active, ally in (
            ("DDG_CG", "DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"),
            ("CG_DDG", "CG_52_LATE_TICONDEROGA", "DDG_119_LATE_FLIGHT_IIA"),
            ("DDG_DDG", "DDG_119_LATE_FLIGHT_IIA", "DDG_119_LATE_FLIGHT_IIA"),
            ("CG_CG", "CG_52_LATE_TICONDEROGA", "CG_52_LATE_TICONDEROGA"),
        ):
            scenes[scene_id] = run_scene(browser, shadow_body, active, ally, errors)
        predecessor = run_legacy_controls(browser, base_body, errors)
        shadow_controls = run_legacy_controls(browser, shadow_body, errors)
        browser.close()

    matrix_equal = all(profiles[p]["matrix"] == EXPECTED["profiles"][p] for p in profiles)
    scenes_equal = all(scenes[p]["scene"] == EXPECTED["fleetScenes"][p] for p in scenes)
    audits = [q["api"]["audit"] for q in profiles.values()] + [q["audit"] for q in scenes.values()]
    definitions = [q["api"]["definition"] for q in profiles.values()]
    checks = {
        "pageErrorsZero": not errors,
        "legacyOutputMatricesExact": matrix_equal,
        "mixedNpcReceiverPlotsAndRngExact": scenes_equal,
        "shadowCompared": all(q["comparisons"] > 0 for q in audits),
        "shadowMismatchZero": all(q["mismatches"] == 0 for q in audits),
        "shadowRngFree": all(q["rngConsumed"] is False for q in audits),
        "legacyStillTacticalAuthority": all(q["tacticalOutputUsed"] is False and q["mode"] == "SHADOW" for q in audits),
        "profileRegistriesValid": all(q["api"]["validation"]["ok"] and q["api"]["validation"]["entries"] == 4 for q in profiles.values()),
        "profileDefinitionsImmutableData": all(q["api"]["definitionFrozen"] and q["api"]["definition"]["schema"] == "AEGIS_SHIP_EMITTER_EQUIPMENT_A_1" and q["api"]["definition"]["physicalEmission"] is True for q in profiles.values()),
        "profileSpecificNoLeak": definitions[0]["entries"][1]["id"] == "AN_SPQ_9B" and definitions[1]["entries"][1]["id"] == "AN_SPQ_9" and definitions[0]["entries"][2]["id"] == "BRIDGEMASTER_E" and definitions[1]["entries"][2]["id"] == "AN_SPS_73",
        "runtimeUsesExistingOwners": all(q["api"]["runtime"]["duplicateMutableState"] is False for q in profiles.values()),
        "hojUnchanged": predecessor["hoj"] == shadow_controls["hoj"],
        "passiveCandidateSelectionUnchanged": predecessor["passive"] == shadow_controls["passive"],
    }
    result = {"schema":"AEGIS_EMITTER_A_COMMIT_B_GATE_1","status":"PASS" if all(checks.values()) else "FAIL",
        "elapsedS":time.monotonic()-started,"checks":checks,"pageErrors":errors,
        "inputs":{"baselineDiagnosticSha256":hashlib.sha256(base_body).hexdigest(),"shadowDiagnosticSha256":hashlib.sha256(shadow_body).hexdigest(),"shadowProductSha256":hashlib.sha256(SHADOW.read_bytes()).hexdigest()},
        "profiles":profiles,"scenes":scenes,"controls":{"baseline":predecessor,"shadow":shadow_controls}}
    (HERE / "B_GATE.json").write_text(strict(result))
    print(strict({"status":result["status"],"elapsedS":result["elapsedS"],"checks":checks,"pageErrors":errors}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
