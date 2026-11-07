#!/usr/bin/env python3
"""Capture DDG/CG legacy emitter matrices and immutable SOV registration."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
HTML = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_BASELINE_DIAGNOSTIC.html")
sys.path[:0] = [str(REPO_ROOT / "docs/pip/B"), str(REPO_ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def strict_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main() -> None:
    started = time.monotonic()
    body = HTML.read_bytes()
    errors: list[str] = []
    profiles: dict[str, object] = {}
    scenes: dict[str, object] = {}
    with sync_playwright() as pw:
        browser = launch(pw)
        for profile in ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"):
            page = load(browser, body, ship=profile, errors=errors)
            profiles[profile] = page.evaluate("()=>__EMITTER_A_BASELINE__.matrix()")
            if profile.startswith("DDG"):
                audit = page.evaluate("()=>__EMITTER_A_BASELINE__.profileAudit()")
            page.close()
        for scene_id, active, ally in (
            ("DDG_CG", "DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"),
            ("CG_DDG", "CG_52_LATE_TICONDEROGA", "DDG_119_LATE_FLIGHT_IIA"),
            ("DDG_DDG", "DDG_119_LATE_FLIGHT_IIA", "DDG_119_LATE_FLIGHT_IIA"),
            ("CG_CG", "CG_52_LATE_TICONDEROGA", "CG_52_LATE_TICONDEROGA"),
        ):
            page = load(browser, body, ship=active, errors=errors)
            scenes[scene_id] = page.evaluate("p=>__EMITTER_A_BASELINE__.fleetScene(p)", {"allyProfileId": ally})
            page.close()
        browser.close()
    rows = [q for p in profiles.values() for c in p["cases"] for q in c["rows"]]
    expected_power = sorted({q["value"].get("power") for q in rows if q["value"].get("owner") and q["value"].get("power") is not None})
    sov_rows = audit["sov"]["equipment"]["sensorRegistration"]["sensors"]
    checks = {
        "pageErrorsZero": not errors,
        "profilesCaptured": set(profiles) == {"DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"},
        "compatibilityPowers": expected_power == [120, 650, 750, 1250, 2500],
        "stableAllRadarOrder": all([q["value"]["family"] for q in p["cases"][0]["rows"][:3]] == ["SHIP SEARCH RADAR", "SURFACE SEARCH RADAR", "NAVIGATION RADAR"] for p in profiles.values()),
        "emconSuppressesRadar": all(not [q for q in next(c for c in p["cases"] if c["id"] == "EMCON")["rows"] if q["value"]["emitterClass"] == "SEARCH_RADAR"] for p in profiles.values()),
        "allOffProducesNoShipEmitter": all(not next(c for c in p["cases"] if c["id"] == "ALL_RADARS_OFF")["rows"] for p in profiles.values()),
        "singleFamilyCases": all([len(next(c for c in p["cases"] if c["id"] == q)["rows"]) for q in ("SPY_ONLY", "SPQ_ONLY", "NAV_ONLY")] == [1, 1, 1] for p in profiles.values()),
        "mastBoundaryPreserved": all(len(next(c for c in p["cases"] if c["id"] == "MAST_DAMAGE_79_999")["rows"]) == 3 and len(next(c for c in p["cases"] if c["id"] == "MAST_DAMAGE_80")["rows"]) == 1 for p in profiles.values()),
        "hardpointBoundaryPreserved": all(len(next(c for c in p["cases"] if c["id"] == "HARDPOINT_HEALTH_0_050001")["rows"]) == 3 and len(next(c for c in p["cases"] if c["id"] == "HARDPOINT_HEALTH_0_05")["rows"]) == 2 for p in profiles.values()),
        "mixedAndDuplicateProfiles": all(len(q["owners"]) == 2 for q in scenes.values()),
        "physicalEmitterRngFree": all(q["rngBefore"] == q["rngAfterPhysical"] for q in scenes.values()),
        "receiverRngAndAnonymousPlotsCaptured": all(q["receiverRows"] and all(row["plots"] and row["before"] != row["after"] and all(set(p.keys()) == {"bearing", "bearingSigmaDeg", "strength", "quality", "band", "type", "emitterClass", "measuredAtS"} for p in row["plots"]) for row in q["receiverRows"]) for q in scenes.values()),
        "sovRegistrationInactive": len(sov_rows) == 11 and all(q.get("installed") is False and q.get("active") is False and q.get("emitter") is False for q in sov_rows),
        "sovPhysicalEmissionZero": audit["sov"]["physicalEmitterCount"] == 0,
    }
    result = {
        "schema": "AEGIS_EMITTER_A_BASELINE_AUDIT_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "elapsedS": time.monotonic() - started,
        "diagnosticHtmlSha256": hashlib.sha256(body).hexdigest(),
        "checks": checks,
        "pageErrors": errors,
        "profiles": profiles,
        "fleetScenes": scenes,
        "sovRegistration": sov_rows,
        "functionHashes": {name: hashlib.sha256(source.encode()).hexdigest() for name, source in {
            "electronicPhysicalEmittersF": audit["contracts"]["emitterFunction"],
            "electronicReceiverPlotsF": audit["contracts"]["receiverFunction"],
        }.items()},
        "legacyFunctions": audit["contracts"],
    }
    (HERE / "BASELINE_AUDIT.json").write_text(strict_json(result))
    print(strict_json({k: result[k] for k in ("status", "elapsedS", "checks", "pageErrors")}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
