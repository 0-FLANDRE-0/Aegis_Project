#!/usr/bin/env python3
"""Bounded HP_A product-path gate; not the one-shot broad regression."""
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


PLAYER_GATE = r"""()=>{
 const d=__NAVAL_SIM_DIAG__,compact=()=>{const c=d.v48Wip07CrewState(),s=d.shipDynamics().pose;return {outcome:__HP_A__.snapshot(),survival:{state:s.state,irreversible:s.irreversible,lost:s.lost,equipmentOffline:s.equipmentOffline,waterM3:s.waterM3,heelRad:s.heelRad,trimRad:s.trimRad,draftM:s.draftM},crew:{mode:c.mode,combatUnavailable:c.combatUnavailable,equipmentOffline:c.equipmentOffline,fit:c.fit,dead:c.dead},status:d.wip101ShipStatus(),rng:d.snapshot().simRngState,events:__HP_A__.events()};};
 d._resetShipTest();for(const b of d.wip101ShipHitboxes())d.wip101SetModuleDamage(b.name,100);d.ciwsB1Closure.advance({timeScale:1,simSeconds:1/60,fps:60});const falseZeroGuard=compact();
 const save=d.exportOperationalStateV48Wip11A(),savedSurvival=save.ship.survival;save.ship.shipHP=0;const validation=d.validateOperationalStateV48Wip11A(save);d.importOperationalStateV48Wip11A(save);const staleHpRestore=compact(),restoreAudit=__HP_A__.restoreAudit();
 const mission=d.exportOperationalStateV48Wip11A();mission.ship.crew.mode='MISSION_KILLED';mission.ship.crew.reason='HP_A deterministic authority fixture';mission.ship.shipHP=0;d.importOperationalStateV48Wip11A(mission);const missionKill=compact();
 const beforeInvalid=JSON.stringify(d.exportOperationalStateV48Wip11A()),invalid=d.exportOperationalStateV48Wip11A();invalid.ship.survival.state='INVALID';let rejectReason=null;try{d.importOperationalStateV48Wip11A(invalid);}catch(err){rejectReason=String(err?.message??err);}const invalidZeroMutation=beforeInvalid===JSON.stringify(d.exportOperationalStateV48Wip11A());
 d._resetShipTest();const reset=compact();
 return {core:Array.from(__CORE_SELFTEST_FAILURES__??[]),self:__HP_A__.selfTest(),falseZeroGuard,savedSurvival,validation,staleHpRestore,restoreAudit,missionKill,rejectReason,invalidZeroMutation,reset};
}"""


KH35_GATE = r"""()=>{
 const d=__NAVAL_SIM_DIAG__,read=()=>{const s=d.snapshot(),st=d.wip101ShipStatus(),f=d.damageFloodSnapshotV1(),c=d.v48Wip07CrewState(),p=d.shipDynamics().pose;return {shipHP:s.shipHP,outcome:__HP_A__.snapshot(),damageSeverityPct:st.damageSeverityPct,flood:{waterM3:f.summary.waterM3,floodingPct:f.summary.floodingPct,openings:f.summary.openings},crew:{mode:c.mode,combatUnavailable:c.combatUnavailable,equipmentOffline:c.equipmentOffline,dead:c.dead},survival:{state:p.state,equipmentOffline:p.equipmentOffline,lost:p.lost,irreversible:p.irreversible,waterM3:p.waterM3,heelRad:p.heelRad,trimRad:p.trimRad}};};
 d._resetShipTest();const q=d.runWip108AsmAcquireCase({label:'Kh-35U',speedKt:15,seed:729300,headingDeg:90,rangeKm:60,maxTimeS:220,emconActive:false});d.ciwsB1Closure.advance({timeScale:1,simSeconds:2,fps:60});return {flight:{durationS:q.durationS,shipHit:q.shipHit,deathReason:q.deathReason,everAcquire:q.everAcquire,everTrack:q.everTrack},after:read(),rngState:d.snapshot().simRngState,core:Array.from(__CORE_SELFTEST_FAILURES__??[])};
}"""


SOV_GATE = r"""()=>{
 const d=__NAVAL_SIM_DIAG__,id='SHIP_SCENARIO_ENEMY_A',r=__AEGIS_ENGAGEMENT_RUNTIME__.ships.get(id);d.setTerrainDiagBypass(true);d.setEmcon(true);d.wip13a3SetManualWeather({hsM:0,windSpeedMps:0,precipitation01:0});r.dynamics.haltHorizontalContact();Object.assign(r.navigation,{speed:0,targetSpeedKt:0,shaftRpm:0,vx:0,vy:0});d.stepTicks(60);
 const contacts=[];for(const x of [-31,-13,5,23]){const q=d.weaponFixtureD(id,{action:'contact',weapon:'HARPOON',xM:x,zM:-1.2,side:'PORT'});contacts.push({ok:q.ok,duplicateRejected:q.duplicateRejected,termination:q.terminationReason,blastKg:q.impacts.at(-1)?.explosiveMassKg,speedMps:q.impacts.at(-1)?.speedMps});}
 const rows=[];for(let i=0;i<90;i++){if(i===2)for(const door of r.flooding.connections)r.flooding.setDoor(door.id,true);d.stepTicks(600);const s=__SOV_A__.snapshot().ships[0],o=__HP_A__.runtimeSnapshot(id),ev=__HP_A__.runtimeEvents(id);rows.push({index:i,outcome:o,survival:{state:s.survival.state,irreversible:s.survival.irreversible,lost:s.survival.lost,equipmentOffline:s.survival.equipmentOffline,waterM3:s.survival.waterM3,heelRad:s.survival.heelRad,trimRad:s.survival.trimRad,draftM:s.survival.draftM},flood:{waterM3:s.flood.waterM3,structuralLoss01:s.flood.structuralLoss01},events:ev});if(s.survival.lost)break;}
 const atLoss=rows.at(-1);d.stepTicks(120);const duplicateTick={outcome:__HP_A__.runtimeSnapshot(id),events:__HP_A__.runtimeEvents(id)};
 return {contacts,rows,atLoss,duplicateTick,core:Array.from(__CORE_SELFTEST_FAILURES__??[])};
}"""


SCALE_GATE = r"""scale=>{const d=__NAVAL_SIM_DIAG__;d._resetShipTest();d.runWip101Stage3RepresentativeImpact('Kh-35U',true);d.ciwsB1Closure.advance({timeScale:scale,simSeconds:2,fps:60});const p=d.shipDynamics().pose,c=d.v48Wip07CrewState();return {scale,outcome:__HP_A__.snapshot(),survival:{state:p.state,irreversible:p.irreversible,lost:p.lost,waterM3:p.waterM3,heelRad:p.heelRad,trimRad:p.trimRad,draftM:p.draftM},crew:{mode:c.mode,fit:c.fit,dead:c.dead},rng:d.snapshot().simRngState};}"""


def run_player(pw, raw: bytes, ship: str, seed: int) -> tuple[dict, list[str]]:
    errors: list[str] = []
    browser = launch(pw)
    page = load(browser, raw, ship=ship, seed=seed, errors=errors)
    result = page.evaluate(PLAYER_GATE)
    page.close(); browser.close()
    return result, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    started = time.monotonic(); raw = args.product.read_bytes()
    baseline = json.loads((ROOT / "docs/damage/hp/A/evidence/commit-a/baseline-repro.json").read_text())
    all_errors: list[str] = []
    with sync_playwright() as pw:
        ddg, errors = run_player(pw, raw, "DDG_119_LATE_FLIGHT_IIA", 0x48A002); all_errors += errors
        cg, errors = run_player(pw, raw, "CG_52_LATE_TICONDEROGA", 0x48A002); all_errors += errors
        browser = launch(pw); errors = []; page = load(browser, raw, ship="DDG_119_LATE_FLIGHT_IIA", seed=729300, errors=errors); kh35 = page.evaluate(KH35_GATE); page.close(); browser.close(); all_errors += errors
        browser = launch(pw); errors = []; page = load_fleet(browser, raw, enemy="SOVREMENNY_956", errors=errors); page.evaluate("window.requestAnimationFrame=()=>0"); sov = page.evaluate(SOV_GATE); page.close(); browser.close(); all_errors += errors
        scales = []
        for scale in (1, 8, 16):
            browser = launch(pw); errors = []; page = load(browser, raw, ship="DDG_119_LATE_FLIGHT_IIA", seed=0x48A003, errors=errors); scales.append(page.evaluate(SCALE_GATE, scale)); page.close(); browser.close(); all_errors += errors
    reversible_rows = [q for q in sov["rows"] if not q["survival"]["irreversible"]]
    critical_rows = [q for q in reversible_rows if q["survival"]["state"] == "CRITICAL"]
    first_irreversible = next(q for q in sov["rows"] if q["survival"]["irreversible"])
    expected = baseline["kh35FixedScene"]
    kh35_physics_keys = {
        "flight": equal_physics(kh35["flight"], expected["flight"]),
        "damageSeverityPct": equal_physics(kh35["after"]["damageSeverityPct"], expected["after"]["damageSeverityPct"]),
        "flood": equal_physics(kh35["after"]["flood"], expected["after"]["flood"]),
        "crew": equal_physics(kh35["after"]["crew"], expected["after"]["crew"]),
        "survival": equal_physics(kh35["after"]["survival"], expected["after"]["survival"]),
        "rng": kh35["rngState"] == expected["rngState"],
    }
    kh35_physics_delta = {
        "flight": max_numeric_delta(kh35["flight"], expected["flight"]),
        "damageSeverityPct": max_numeric_delta(kh35["after"]["damageSeverityPct"], expected["after"]["damageSeverityPct"]),
        "flood": max_numeric_delta(kh35["after"]["flood"], expected["after"]["flood"]),
        "crew": max_numeric_delta(kh35["after"]["crew"], expected["after"]["crew"]),
        "survival": max_numeric_delta(kh35["after"]["survival"], expected["after"]["survival"]),
        "rng": 0,
    }
    scale_physics = [{k:v for k,v in q.items() if k != "scale"} for q in scales]
    checks = {
        "pageAndConsoleErrorsZero": not all_errors,
        "coreSelfTestsZero": not ddg["core"] and not cg["core"] and not kh35["core"] and not sov["core"],
        "outcomeSelfTest": ddg["self"]["pass"] and cg["self"]["pass"],
        "playerDdgFalseZeroGuard": ddg["falseZeroGuard"]["outcome"]["displayHp"] == 1 and not ddg["falseZeroGuard"]["outcome"]["irreversible"],
        "playerCgFalseZeroGuard": cg["falseZeroGuard"]["outcome"]["displayHp"] == 1 and not cg["falseZeroGuard"]["outcome"]["irreversible"],
        "staleStoredHpIgnored": ddg["staleHpRestore"]["outcome"]["displayHp"] == 1 and ddg["restoreAudit"][-1]["mismatch"],
        "authoritativeSurvivalRoundTrip": ddg["savedSurvival"]["state"] == ddg["staleHpRestore"]["survival"]["state"],
        "missionKillSeparated": ddg["missionKill"]["outcome"]["missionState"] == "MISSION_KILL" and ddg["missionKill"]["outcome"]["displayHp"] > 0 and not ddg["missionKill"]["outcome"]["irreversible"],
        "invalidSaveFailClosedZeroMutation": bool(ddg["rejectReason"]) and ddg["invalidZeroMutation"],
        "resetClearsOutcome": ddg["reset"]["outcome"]["missionState"] == "OPERATIONAL" and ddg["reset"]["outcome"]["displayHp"] == 100 and ddg["reset"]["events"]["counts"] == {"missionKill":0,"irreversibleLoss":0,"sunk":0},
        "kh35PhysicsPreservedWithinNumericTolerance": all(kh35_physics_keys.values()),
        "kh35ReversiblePositive": kh35["after"]["outcome"]["displayHp"] >= 1 and not kh35["after"]["outcome"]["irreversible"],
        "sovContactsPreserved": len(sov["contacts"]) == 4 and all(q["ok"] and q["duplicateRejected"] for q in sov["contacts"]),
        "recoverableCriticalPositive": bool(critical_rows) and all(q["outcome"]["displayHp"] >= 1 for q in critical_rows),
        "irreversibleOnlyZero": first_irreversible["outcome"]["displayHp"] == 0 and all(q["outcome"]["displayHp"] > 0 for q in reversible_rows),
        "actualLossZero": sov["atLoss"]["survival"]["lost"] and sov["atLoss"]["outcome"]["displayHp"] == 0,
        "lossCallbacksExactlyOnce": sov["atLoss"]["events"]["counts"]["irreversibleLoss"] == 1 and sov["atLoss"]["events"]["counts"]["sunk"] == 1,
        "duplicateTicksNoDuplicateCallbacks": sov["duplicateTick"]["events"]["counts"] == sov["atLoss"]["events"]["counts"],
        "timeScaleOneEightSixteenExact": scale_physics[0] == scale_physics[1] == scale_physics[2],
    }
    payload = {
        "schema": "AEGIS_HP_A_CONTRACT_GATE_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "product": args.product.name,
        "productBytes": len(raw),
        "productSha256": sha(raw),
        "elapsedS": time.monotonic() - started,
        "checks": checks,
        "kh35PhysicsComparison": kh35_physics_keys,
        "kh35PhysicsNumericTolerance": NUMERIC_TOLERANCE,
        "kh35PhysicsMaxAbsoluteDelta": kh35_physics_delta,
        "ddg": ddg,
        "cg": cg,
        "kh35": kh35,
        "sov": sov,
        "timeScales": scales,
        "errors": all_errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": payload["status"], "elapsedS": payload["elapsedS"], "failed": [k for k,v in checks.items() if not v], "errors": all_errors}))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
