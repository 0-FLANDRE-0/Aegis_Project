#!/usr/bin/env python3
"""Verify ACTIVE/SHADOW resolver call counts and exact tactical output."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ACTIVE = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_CLOSURE_ACTIVE.html")
SHADOW = Path("/tmp/Aegis_SIM_v48_WIP_EMITTER_A_CLOSURE_SHADOW.html")
sys.path[:0] = ["/workspace/aegis-ui-a/docs/pip/B", "/workspace/aegis-ui-a/docs/bunkerhill/K"]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def capture(browser, body: bytes, own: str, ally: str | None, errors: list[str]) -> dict:
    page = load(browser, body, ship=own, errors=errors)
    result = page.evaluate("ally=>__EMITTER_A_CLOSURE_DIAG__.resolverCalls(ally)", ally)
    page.close()
    return result


def main() -> None:
    active_body, shadow_body = ACTIVE.read_bytes(), SHADOW.read_bytes()
    scenes = {
        "DDG": ("DDG_119_LATE_FLIGHT_IIA", None),
        "CG": ("CG_52_LATE_TICONDEROGA", None),
        "DDG_CG": ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"),
        "CG_DDG": ("CG_52_LATE_TICONDEROGA", "DDG_119_LATE_FLIGHT_IIA"),
        "DDG_DDG": ("DDG_119_LATE_FLIGHT_IIA", "DDG_119_LATE_FLIGHT_IIA"),
        "CG_CG": ("CG_52_LATE_TICONDEROGA", "CG_52_LATE_TICONDEROGA"),
    }
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        active = {key: capture(browser, active_body, own, ally, errors)
                  for key, (own, ally) in scenes.items()}
        shadow = {key: capture(browser, shadow_body, own, ally, errors)
                  for key, (own, ally) in scenes.items()}
        browser.close()
    checks = {
        "pageErrorsZero": not errors,
        "activeLegacyCallsZero": all(row["legacyCalls"] == 0 for row in active.values()),
        "activeDeclaredOncePerShip": all(row["declaredCalls"] == row["shipCount"] for row in active.values()),
        "shadowLegacyOncePerShip": all(row["legacyCalls"] == row["shipCount"] for row in shadow.values()),
        "shadowDeclaredOncePerShip": all(row["declaredCalls"] == row["shipCount"] for row in shadow.values()),
        "activeAndShadowOutputExact": all(active[key]["output"] == shadow[key]["output"] for key in scenes),
        "rngExact": all(row["rngExact"] and row["rngBefore"] == row["rngAfter"]
                        for row in [*active.values(), *shadow.values()]),
    }
    result = {
        "schema": "AEGIS_EMITTER_A_CLOSURE_CALL_GATE_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "pageErrors": errors,
        "inputs": {
            "activeDiagnosticSha256": hashlib.sha256(active_body).hexdigest(),
            "shadowDiagnosticSha256": hashlib.sha256(shadow_body).hexdigest(),
        },
        "active": active,
        "shadow": shadow,
    }
    (HERE / "CLOSURE_CALL_GATE.json").write_text(strict(result))
    print(strict({"status": result["status"], "checks": checks, "pageErrors": errors}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
