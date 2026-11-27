#!/usr/bin/env python3
"""Explain the ACTIVE-only delta in the inherited seeded raid fixture.

This does not rerun the broad paired suite.  It replays only the candidate side
with the exact diagnostic raid setup so the OODA phase and downstream WIP119
gate can be observed after the intentionally delayed decision becomes READY.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "docs/bunkerhill/K"))
from browser_i import launch, load  # noqa: E402

PRODUCT_SHA256 = "1d2b25cd22813c0187d8578e1cd1489f821222674ecb01cddd344f98da88d13d"
PROFILES = ["DDG_119_LATE_FLIGHT_IIA", "CG_52_LATE_TICONDEROGA"]


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    raw = args.html.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PRODUCT_SHA256
    args.out.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    scenes: list[dict] = []
    with sync_playwright() as pw:
        browser = launch(pw)
        for profile in PROFILES:
            page = load(browser, raw, ship=profile, errors=errors)
            page.set_default_timeout(180_000)
            scene = page.evaluate(
                """()=>{
                  const d=__NAVAL_SIM_DIAG__,api=__DEFENSE_DECISION_A1__;
                  d.setTerrainDiagBypass(true);
                  const ownerId=__AEGIS_SHIP_STARTUP__.snapshot().entityId;
                  const fixture=d.wip119DiagSpawnRealAsms({count:8,label:'Kh-32',rangeKm:16,bearingsDeg:[-60,-20,20,60]});
                  d.wip119SetMode('AUTO');
                  const points=[0,12,24,48,60,72,84,120,240,480,960,1920],samples=[];let currentStep=0;
                  const vlsCount=()=>{const q=d.exportOperationalStateV48Wip11A().ship.inventory.vls;return Object.values(q).flat().filter(c=>c.type!=='EMPTY').length;};
                  const inputView=q=>q?{step:q.step,revision:q.revision,mode:q.mode,tracks:q.tracks.map(t=>({trackId:t.trackId,classification:t.classification?.domain??t.classification,assessment:t.assessment?.state??t.assessment,authority:t.identification?.engagementAuthority,tgoS:t.kinematics?.tgoS??t.tgoS??null,ageS:t.measurement?.ageS??null}))}:null;
                  const oodaView=q=>q?{phase:q.phase,queueLength:q.queueLength,usedSlots:q.usedSlots,totalSlots:q.totalSlots,nextReadyStep:q.nextReadyStep,rows:q.rows.map(r=>({trackId:r.trackId,phase:r.phase,remainingSteps:r.remainingSteps,readyStep:r.readyStep})),diagnostics:q.diagnostics}:null;
                  const sample=()=>{const a=d.wip119AutonomySnapshot(),c=d.wip118ControlSnapshot(),diag=api.diagnostics(ownerId);return {step:currentStep,input:inputView(api.input(ownerId)),ooda:oodaView(api.ooda(ownerId)),provider:{provider:diag?.provider,mode:diag?.mode,lastCommand:diag?.lastCommand,validationFailures:diag?.validationFailures,rngMismatchCount:diag?.rngMismatchCount,truthAuditFailures:diag?.truthAuditFailures},control:(c.recommendations??[]).map(r=>({trackId:r.trackId,assessment:r.assessment,weapon:r.weapon,status:r.status,reason:r.reason,rounds:r.rounds})),autonomy:{candidateRows:a.candidateRows,fireLog:a.fireLog,totalAutoRounds:a.totalAutoRounds},interceptors:d.interceptorAudit(),loadedVls:vlsCount()};};
                  for(const target of points){if(target>currentStep)d.stepTicks(target-currentStep);currentStep=target;samples.push(sample());}
                  return {ownerId,fixture,samples,core:[...__CORE_SELFTEST_FAILURES__],faults:[__WIP125_DIAG__.wip150RuntimeFault(),__WIP125_DIAG__.wip150PresentationFault()]};
                }"""
            )
            scene["profile"] = profile
            scenes.append(scene)
            page.close()
            print(json.dumps({"profile": profile, "samples": len(scene["samples"])}), flush=True)
        browser.close()
    checks: dict[str, bool] = {"pageErrors": not errors}
    for scene in scenes:
        name = scene["profile"]
        ready = [sample for sample in scene["samples"] if sample.get("ooda", {}).get("phase") == "READY"]
        first_ready = ready[0] if ready else None
        candidates = (first_ready or {}).get("autonomy", {}).get("candidateRows", [])
        checks[f"{name}.providerActive"] = all(sample["provider"]["provider"] == "DEFENSE_OODA_A" and sample["provider"]["mode"] == "ACTIVE" for sample in scene["samples"] if sample["provider"]["provider"])
        checks[f"{name}.reachesReady"] = first_ready is not None
        checks[f"{name}.readyBlockedByFcsQuality"] = bool(candidates) and all(not row["ready"] and row["reason"] == "FCS_QUALITY" for row in candidates)
        checks[f"{name}.noCandidateRelease"] = all(not sample["autonomy"]["fireLog"] and not sample["interceptors"] for sample in scene["samples"])
        checks[f"{name}.invariantsClean"] = all((sample.get("ooda") or {}).get("diagnostics", {}).get(key, 0) == 0 for sample in scene["samples"] for key in ("fallback", "rejected")) and all(sample["provider"].get(key, 0) == 0 for sample in scene["samples"] for key in ("validationFailures", "rngMismatchCount", "truthAuditFailures"))
        checks[f"{name}.faultFree"] = scene["core"] == [] and all(value is None for value in scene["faults"])
    payload = {
        "schema": "AEGIS_DEFENSE_OODA_A_PAIRED_ACTIVE_DELTA_DIAGNOSTIC_1",
        "candidate": {"file": args.html.name, "bytes": len(raw), "sha256": PRODUCT_SHA256},
        "fixture": {"source": "docs/multiship/H4/regression_baseline.py", "kind": "DIAGNOSTIC_SEEDED_MEASUREMENTS", "count": 8, "label": "Kh-32", "rangeKm": 16, "ticks": 1920},
        "checks": checks,
        "pass": all(checks.values()),
        "errors": errors,
        "scenes": scenes,
    }
    args.out.write_text(strict(payload))
    print(strict({"pass": payload["pass"], "failed": [key for key, value in checks.items() if not value], "errors": errors}))
    raise SystemExit(0 if payload["pass"] else 1)


if __name__ == "__main__":
    main()
