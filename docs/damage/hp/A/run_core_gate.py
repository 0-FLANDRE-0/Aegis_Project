#!/usr/bin/env python3
"""Commit-B-only HP outcome gate; excludes save/UI consumer closure."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "docs/pip/B"), str(ROOT / "docs/bunkerhill/K"), str(ROOT / "docs/helicopter/H")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from browser import load_fleet
from playwright.sync_api import sync_playwright

from run_contract_gate import KH35_GATE, SCALE_GATE, SOV_GATE


PLAYER_B_GATE = r"""()=>{
 const d=__NAVAL_SIM_DIAG__;d._resetShipTest();
 for(const b of d.wip101ShipHitboxes())d.wip101SetModuleDamage(b.name,100);
 d.ciwsB1Closure.advance({timeScale:1,simSeconds:1/60,fps:60});
 const p=d.shipDynamics().pose;
 return {core:Array.from(__CORE_SELFTEST_FAILURES__??[]),self:__HP_A__.selfTest(),outcome:__HP_A__.snapshot(),survival:{state:p.state,irreversible:p.irreversible,lost:p.lost},events:__HP_A__.events()};
}"""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


NUMERIC_TOLERANCE = 1e-12


def equal_physics(actual, expected) -> bool:
    """Exact for structure/discrete state; bounded only for finite JS numbers."""
    if isinstance(actual, bool) or isinstance(expected, bool):
        return type(actual) is type(expected) and actual == expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) <= NUMERIC_TOLERANCE
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(equal_physics(actual[key], expected[key]) for key in actual)
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(equal_physics(a, b) for a, b in zip(actual, expected))
    return actual == expected


def max_numeric_delta(actual, expected) -> float:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return 0.0
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected))
    if isinstance(actual, dict) and isinstance(expected, dict):
        return max((max_numeric_delta(actual[key], expected[key]) for key in actual.keys() & expected.keys()), default=0.0)
    if isinstance(actual, list) and isinstance(expected, list):
        return max((max_numeric_delta(a, b) for a, b in zip(actual, expected)), default=0.0)
    return 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    raw = args.product.read_bytes()
    baseline = json.loads((ROOT / "docs/damage/hp/A/evidence/commit-a/baseline-repro.json").read_text())
    errors: list[str] = []
    players = {}
    with sync_playwright() as pw:
        for ship in ("DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"):
            local: list[str] = []
            browser = launch(pw); page = load(browser, raw, ship=ship, seed=0x48A002, errors=local)
            players[ship] = page.evaluate(PLAYER_B_GATE)
            page.close(); browser.close(); errors += local
        local = []; browser = launch(pw); page = load(browser, raw, ship="DDG_119_LATE_FLIGHT_IIA", seed=729300, errors=local)
        kh35 = page.evaluate(KH35_GATE); page.close(); browser.close(); errors += local
        local = []; browser = launch(pw); page = load_fleet(browser, raw, enemy="SOVREMENNY_956", errors=local)
        page.evaluate("window.requestAnimationFrame=()=>0"); sov = page.evaluate(SOV_GATE)
        page.close(); browser.close(); errors += local
        scales = []
        for scale in (1, 8, 16):
            local = []; browser = launch(pw); page = load(browser, raw, ship="DDG_119_LATE_FLIGHT_IIA", seed=0x48A003, errors=local)
            scales.append(page.evaluate(SCALE_GATE, scale)); page.close(); browser.close(); errors += local

    expected = baseline["kh35FixedScene"]
    physics = {
        "flight": equal_physics(kh35["flight"], expected["flight"]),
        "damageSeverityPct": equal_physics(kh35["after"]["damageSeverityPct"], expected["after"]["damageSeverityPct"]),
        "flood": equal_physics(kh35["after"]["flood"], expected["after"]["flood"]),
        "crew": equal_physics(kh35["after"]["crew"], expected["after"]["crew"]),
        "survival": equal_physics(kh35["after"]["survival"], expected["after"]["survival"]),
        "rng": kh35["rngState"] == expected["rngState"],
    }
    physics_delta = {
        "flight": max_numeric_delta(kh35["flight"], expected["flight"]),
        "damageSeverityPct": max_numeric_delta(kh35["after"]["damageSeverityPct"], expected["after"]["damageSeverityPct"]),
        "flood": max_numeric_delta(kh35["after"]["flood"], expected["after"]["flood"]),
        "crew": max_numeric_delta(kh35["after"]["crew"], expected["after"]["crew"]),
        "survival": max_numeric_delta(kh35["after"]["survival"], expected["after"]["survival"]),
        "rng": 0,
    }
    reversible = [row for row in sov["rows"] if not row["survival"]["irreversible"]]
    first_irreversible = next(row for row in sov["rows"] if row["survival"]["irreversible"])
    scale_physics = [{k: v for k, v in row.items() if k != "scale"} for row in scales]
    checks = {
        "pageAndConsoleErrorsZero": not errors,
        "coreSelfTestsZero": all(not row["core"] for row in players.values()) and not kh35["core"] and not sov["core"],
        "outcomeSelfTest": all(row["self"]["pass"] for row in players.values()),
        "playerDdgCgFalseZeroGuard": all(row["outcome"]["displayHp"] == 1 and not row["outcome"]["irreversible"] for row in players.values()),
        "kh35PhysicsPreservedWithinNumericTolerance": all(physics.values()),
        "kh35ReversiblePositive": kh35["after"]["outcome"]["displayHp"] >= 1 and not kh35["after"]["outcome"]["irreversible"],
        "recoverableCriticalPositive": any(row["survival"]["state"] == "CRITICAL" for row in reversible) and all(row["outcome"]["displayHp"] > 0 for row in reversible),
        "irreversibleOnlyZero": first_irreversible["outcome"]["displayHp"] == 0,
        "lossCallbacksExactlyOnce": sov["atLoss"]["events"]["counts"]["irreversibleLoss"] == 1 and sov["atLoss"]["events"]["counts"]["sunk"] == 1,
        "duplicateTicksNoDuplicateCallbacks": sov["duplicateTick"]["events"]["counts"] == sov["atLoss"]["events"]["counts"],
        "timeScaleOneEightSixteenExact": scale_physics[0] == scale_physics[1] == scale_physics[2],
    }
    payload = {
        "schema": "AEGIS_HP_A_COMMIT_B_GATE_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "product": args.product.name,
        "productBytes": len(raw),
        "productSha256": sha(raw),
        "elapsedS": time.monotonic() - started,
        "checks": checks,
        "kh35PhysicsComparison": physics,
        "kh35PhysicsNumericTolerance": NUMERIC_TOLERANCE,
        "kh35PhysicsMaxAbsoluteDelta": physics_delta,
        "players": players,
        "kh35": kh35,
        "sov": sov,
        "timeScales": scales,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": payload["status"], "elapsedS": payload["elapsedS"], "failed": [key for key, value in checks.items() if not value], "errors": errors}))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
