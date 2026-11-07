#!/usr/bin/env python3
"""Commit D inactive-SOV registration and DDG/CG preservation gate."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parents[3] / "Aegis_SIM_v48_WIP_EMITTER_A.html"
DIAG = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_D_DIAGNOSTIC.html")
EXPECTED = json.loads((HERE / "BASELINE_AUDIT.json").read_text())
sys.path[:0] = ["/workspace/aegis-ui-a/docs/pip/B", "/workspace/aegis-ui-a/docs/bunkerhill/K"]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def profile(browser, body: bytes, profile_id: str, errors: list[str]) -> dict:
    page = load(browser, body, ship=profile_id, errors=errors)
    matrix = page.evaluate("()=>__EMITTER_A_BASELINE__.matrix()")
    page.close()
    return matrix


def fleet(browser, body: bytes, own: str, ally: str, errors: list[str]) -> dict:
    page = load(browser, body, ship=own, errors=errors)
    scene = page.evaluate("p=>__EMITTER_A_BASELINE__.fleetScene(p)", {"allyProfileId": ally})
    page.close()
    return scene


def main() -> None:
    started = time.monotonic()
    body = DIAG.read_bytes()
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        matrices = {p: profile(browser, body, p, errors) for p in
                    ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA")}
        scenes = {}
        for scene_id, own, ally in (
            ("DDG_CG", "DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"),
            ("CG_DDG", "CG_52_LATE_TICONDEROGA", "DDG_119_LATE_FLIGHT_IIA"),
            ("DDG_DDG", "DDG_119_LATE_FLIGHT_IIA", "DDG_119_LATE_FLIGHT_IIA"),
            ("CG_CG", "CG_52_LATE_TICONDEROGA", "CG_52_LATE_TICONDEROGA"),
        ):
            scenes[scene_id] = fleet(browser, body, own, ally, errors)
        page = load(browser, body, ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        sov = page.evaluate("()=>{const d=__SHIP_EMITTERS_A__.definitions('SOVREMENNY_956');return {definition:d,frozen:Object.isFrozen(d)&&Object.isFrozen(d.entries)&&d.entries.every(Object.isFrozen),validation:__SHIP_EMITTERS_A__.validate('SOVREMENNY_956')};}")
        deployments = {role: page.evaluate("r=>__EMITTER_A_D_DIAG__.sovScene(r)", role)
                       for role in ("ENEMY", "NEUTRAL")}
        page.close()
        browser.close()

    expected_sov = EXPECTED["sovRegistration"]
    entries = sov["definition"]["entries"]
    metadata_exact = all(
        entry["id"] == source["id"].upper() and entry["system"] == source["system"] and
        entry["nato"] == source.get("nato") and entry["role"] == source["role"] and
        entry["hardpointM"] == {"x": source["simPosM"][0], "y": source["simPosM"][1], "z": source["simPosM"][2]} and
        entry["confidence"] == source["confidence"] and entry["provenance"] == source.get("basis", "MODEL_REGISTRATION")
        for entry, source in zip(entries, expected_sov)
    )
    checks = {
        "pageErrorsZero": not errors,
        "ddgCgMatricesExact": all(matrices[p] == EXPECTED["profiles"][p] for p in matrices),
        "ddgCgFleetScenesExact": all(scenes[p] == EXPECTED["fleetScenes"][p] for p in scenes),
        "sovRegistryValidFrozen": sov["validation"]["ok"] and sov["frozen"] and len(entries) == 11,
        "sovExistingMetadataExact": metadata_exact,
        "sovNoInventedRfValues": all(not any(k in q for k in ("power", "powerPerResource", "frequencyMHz", "beamwidthDeg", "rpm")) for q in entries),
        "sovAllRegisteredInactive": sov["definition"]["physicalEmission"] is False and all(q["outputKind"] == "REGISTERED_INACTIVE" and q["physicalEmission"] is False and q["installed"] is False and q["active"] is False for q in entries),
        "sovEnemyAndNeutralDeployed": all(any(q["profileId"] == "SOVREMENNY_956" and q["role"] == role for q in deployments[role]["owners"]) for role in deployments),
        "sovPhysicalEmissionZero": all(q["sovEmitterCount"] == 0 for q in deployments.values()),
        "sovReceiverAndOwnDetectionInactive": all(q["sovReceiver"]["plots"] == [] and q["sovObserver"]["normals"] == 0 and q["sovObserver"]["tracks"] == 0 for q in deployments.values()),
        "sovAttackInactive": all(q["sovAttack"]["active"] is False and q["sovAttack"]["evaluations"] == 0 and q["sovAttack"]["plans"] == [] for q in deployments.values()),
        "sovPhysicalResolverRngFree": all(q["rngBefore"] == q["rngAfter"] for q in deployments.values()),
    }
    result = {"schema": "AEGIS_EMITTER_A_COMMIT_D_GATE_1",
              "status": "PASS" if all(checks.values()) else "FAIL",
              "elapsedS": time.monotonic() - started, "checks": checks, "pageErrors": errors,
              "inputs": {"productSha256": hashlib.sha256(PRODUCT.read_bytes()).hexdigest(),
                         "diagnosticSha256": hashlib.sha256(body).hexdigest()},
              "matrices": matrices, "fleetScenes": scenes, "sov": sov, "deployments": deployments}
    (HERE / "D_GATE.json").write_text(strict(result))
    print(strict({"status": result["status"], "elapsedS": result["elapsedS"],
                  "checks": checks, "pageErrors": errors}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
