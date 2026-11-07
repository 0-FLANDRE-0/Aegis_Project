#!/usr/bin/env python3
"""Commit C ACTIVE equivalence, API, UI and operational-save gate."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_DIAG = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_U3_DIAGNOSTIC.html")
ACTIVE = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_C_ACTIVE.html")
ACTIVE_DIAG = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_C_DIAGNOSTIC.html")
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
    api = page.evaluate(
        "ids=>{const d=__SHIP_EMITTERS_A__.definitions(ids.profileId);return {mode:__SHIP_EMITTERS_A__.mode,definition:d,definitionFrozen:Object.isFrozen(d)&&Object.isFrozen(d.entries)&&d.entries.every(Object.isFrozen),validation:__SHIP_EMITTERS_A__.validate(ids.profileId),runtime:__SHIP_EMITTERS_A__.runtime(ids.entityId),audit:__SHIP_EMITTERS_A__.audit()};}",
        {"profileId": matrix["profileId"], "entityId": matrix["entityId"]},
    )
    save_restore = page.evaluate(
        """id=>{const d=__NAVAL_SIM_DIAG__;
        d.setEmcon(false);d.electronicCommandF(id,{noiseRequested:true,deceptionRequested:true,autoAim:false,bearingRad:.7});
        const before=__SHIP_EMITTERS_A__.runtime(id),saved=d.exportOperationalStateV48Wip11A();
        d.setEmcon(true);d.electronicCommandF(id,{noiseRequested:false,deceptionRequested:false,autoAim:true,bearingRad:0});
        const changed=__SHIP_EMITTERS_A__.runtime(id),imported=d.importOperationalStateV48Wip11A(saved),after=__SHIP_EMITTERS_A__.runtime(id);
        return {before,changed,after,validationOk:imported.validation.ok};}""",
        matrix["entityId"],
    )
    page.close()
    return {"matrix": matrix, "api": api, "saveRestore": save_restore}


def run_scene(browser, body: bytes, active: str, ally: str, errors: list[str]) -> dict:
    page = load(browser, body, ship=active, errors=errors)
    scene = page.evaluate("p=>__EMITTER_A_BASELINE__.fleetScene(p)", {"allyProfileId": ally})
    audit = page.evaluate("()=>__SHIP_EMITTERS_A__.audit()")
    page.close()
    return {"scene": scene, "audit": audit}


def run_controls(browser, body: bytes, errors: list[str]) -> dict:
    page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    rows = {"hoj": page.evaluate("()=>__SEEKER_U3_DIAG__.hojExerciseC()"),
            "passive": page.evaluate("()=>__SEEKER_U3_DIAG__.passiveSelectionD()")}
    page.close()
    return rows


def run_ui(browser, body: bytes, errors: list[str]) -> dict:
    page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
    result = page.evaluate("""()=>{const id=__EMITTER_A_BASELINE__.matrix().entityId,s=()=>({runtime:__SHIP_EMITTERS_A__.runtime(id),chip:document.getElementById('uiEmconChipA')?.textContent.trim(),menu:getComputedStyle(document.getElementById('mapEmconMenuE')).display});
      const before=s();document.getElementById('uiEmconChipA').click();const opened=s();document.getElementById('mapRadarE').click();const radarOn=s();
      document.getElementById('uiEmconChipA').click();document.getElementById('mapEcmJAME').click();const jammer=s();
      const ids=['uiEmconChipA','mapEmconMenuE','mapRadarE','mapEcmOFFE','mapEcmJAME','mapEcmFULLE'];
      return {before,opened,radarOn,jammer,uniqueIds:ids.every(id=>document.querySelectorAll('#'+id).length===1)};}""")
    page.close()
    return result


def main() -> None:
    started = time.monotonic()
    base_body, active_body = BASE_DIAG.read_bytes(), ACTIVE_DIAG.read_bytes()
    errors: list[str] = []
    profiles: dict[str, object] = {}
    scenes: dict[str, object] = {}
    with sync_playwright() as pw:
        browser = launch(pw)
        for profile in ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"):
            profiles[profile] = run_profile(browser, active_body, profile, errors)
        for scene_id, active, ally in (
            ("DDG_CG", "DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"),
            ("CG_DDG", "CG_52_LATE_TICONDEROGA", "DDG_119_LATE_FLIGHT_IIA"),
            ("DDG_DDG", "DDG_119_LATE_FLIGHT_IIA", "DDG_119_LATE_FLIGHT_IIA"),
            ("CG_CG", "CG_52_LATE_TICONDEROGA", "CG_52_LATE_TICONDEROGA"),
        ):
            scenes[scene_id] = run_scene(browser, active_body, active, ally, errors)
        predecessor = run_controls(browser, base_body, errors)
        active_controls = run_controls(browser, active_body, errors)
        ui = run_ui(browser, active_body, errors)
        browser.close()

    audits = [q["api"]["audit"] for q in profiles.values()] + [q["audit"] for q in scenes.values()]
    saves = [q["saveRestore"] for q in profiles.values()]
    checks = {
        "pageErrorsZero": not errors,
        "activeOutputMatricesExact": all(profiles[p]["matrix"] == EXPECTED["profiles"][p] for p in profiles),
        "mixedNpcReceiverPlotsAndRngExact": all(scenes[p]["scene"] == EXPECTED["fleetScenes"][p] for p in scenes),
        "activeAuthority": all(q["mode"] == "ACTIVE" and q["tacticalOutputUsed"] is True for q in audits),
        "legacyComparatorNotRun": all(q["comparisons"] == 0 and q["mismatches"] == 0 for q in audits),
        "registriesValidAndFrozen": all(q["api"]["validation"]["ok"] and q["api"]["definitionFrozen"] for q in profiles.values()),
        "runtimeUsesExistingOwners": all(q["api"]["runtime"]["duplicateMutableState"] is False for q in profiles.values()),
        "operationalSaveRestoreExact": all(q["validationOk"] and q["before"] == q["after"] and q["before"] != q["changed"] for q in saves),
        "uiExistingControlsUnique": ui["uniqueIds"],
        "uiRadarUsesExistingEmconOwner": ui["before"]["runtime"]["emcon"] is True and ui["opened"]["menu"] == "flex" and ui["radarOn"]["runtime"]["emcon"] is False and "EMCON OFF" in ui["radarOn"]["chip"],
        "uiEcmUsesExistingEwOwner": ui["jammer"]["runtime"]["ecm"]["noiseRequested"] is True and ui["jammer"]["runtime"]["ecm"]["deceptionRequested"] is True and "ECM JAM" in ui["jammer"]["chip"],
        "hojUnchanged": predecessor["hoj"] == active_controls["hoj"],
        "passiveCandidateSelectionUnchanged": predecessor["passive"] == active_controls["passive"],
    }
    result = {"schema": "AEGIS_EMITTER_A_COMMIT_C_GATE_1",
              "status": "PASS" if all(checks.values()) else "FAIL",
              "elapsedS": time.monotonic() - started, "checks": checks, "pageErrors": errors,
              "inputs": {"baselineDiagnosticSha256": hashlib.sha256(base_body).hexdigest(),
                         "activeDiagnosticSha256": hashlib.sha256(active_body).hexdigest(),
                         "activeProductSha256": hashlib.sha256(ACTIVE.read_bytes()).hexdigest()},
              "profiles": profiles, "scenes": scenes, "ui": ui,
              "controls": {"baseline": predecessor, "active": active_controls}}
    (HERE / "C_GATE.json").write_text(strict(result))
    print(strict({"status": result["status"], "elapsedS": result["elapsedS"],
                  "checks": checks, "pageErrors": errors}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
