#!/usr/bin/env python3
"""Natural radar -> OODA READY -> native VLS -> terminal outcome gate."""
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
SEED = 481_804


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
            page = load(browser, raw, ship=profile, seed=SEED, errors=errors)
            page.set_default_timeout(180_000)
            setup = page.evaluate(
                """seed=>{
                  const d=__NAVAL_SIM_DIAG__,api=__DEFENSE_DECISION_A1__,ownerId=__AEGIS_SHIP_STARTUP__.snapshot().entityId;
                  d.setSeed(seed);d.setBattlespaceSeed(seed);d.setEmcon(false);
                  d.tacticalCommandH1(ownerId,{enabled:true});d.wip119SetMode('AUTO');
                  const enemyId=d.createUndetectedAsmFixture({label:'Kh-35U',rangeKm:12,bearingDeg:0,altM:25,speedMps:260});
                  const before=d.snapshot();window.__DEFENSE_OODA_TERMINAL_A={ownerId,enemyId,beforeHitCount:before.shipHitCount};
                  return {ownerId,enemyId,provider:api.provider,mode:api.mode,before:{shipHP:before.shipHP,shipHitCount:before.shipHitCount}};
                }""",
                SEED,
            )
            samples: list[dict] = []
            first_track = first_ready = first_release = terminal = None
            max_fire_log = max_interceptors = 0
            for index in range(100):
                sample = page.evaluate(
                    """()=>{
                      const d=__NAVAL_SIM_DIAG__,api=__DEFENSE_DECISION_A1__,t=__DEFENSE_OODA_TERMINAL_A;
                      const step=d.stepTicks(120);
                      const input=api.input(t.ownerId),ooda=api.ooda(t.ownerId),diag=api.diagnostics(t.ownerId),auto=d.wip119AutonomySnapshot(),truth=d.trackingTruthAudit().asm.find(q=>q.id===t.enemyId)??null,interceptors=d.interceptorAudit(),audit=d.snapshot();
                      return {step,input:input?{step:input.step,revision:input.revision,tracks:input.tracks.map(q=>({trackId:q.trackId,classification:q.classification?.domain??q.classification,assessment:q.assessment?.state??q.assessment,authority:q.identification?.engagementAuthority,source:q.measurement?.source??q.measurement?.sensorSource??null,ageS:q.measurement?.ageS??null}))}:null,ooda:ooda?{phase:ooda.phase,queueLength:ooda.queueLength,usedSlots:ooda.usedSlots,totalSlots:ooda.totalSlots,nextReadyStep:ooda.nextReadyStep,diagnostics:ooda.diagnostics}:null,provider:diag?{provider:diag.provider,mode:diag.mode,validationFailures:diag.validationFailures,rngMismatchCount:diag.rngMismatchCount,truthAuditFailures:diag.truthAuditFailures,lastCommand:diag.lastCommand}:null,autonomy:{candidateRows:auto.candidateRows,fireLog:auto.fireLog,totalAutoRounds:auto.totalAutoRounds},interceptors,truth,afterAction:{shipHP:audit.shipHP,shipHitCount:audit.shipHitCount,shipLastOutcome:audit.shipLastOutcome,interceptHistory:audit.interceptHistory},core:[...__CORE_SELFTEST_FAILURES__],faults:[__WIP125_DIAG__.wip150RuntimeFault(),__WIP125_DIAG__.wip150PresentationFault()]};
                    }"""
                )
                samples.append(sample)
                if first_track is None and sample.get("input", {}).get("tracks"):
                    first_track = sample["step"]
                if first_ready is None and sample.get("ooda", {}).get("phase") == "READY":
                    first_ready = sample["step"]
                fire_count = len(sample["autonomy"]["fireLog"])
                interceptor_count = len(sample["interceptors"])
                max_fire_log = max(max_fire_log, fire_count)
                max_interceptors = max(max_interceptors, interceptor_count)
                if first_release is None and (fire_count or interceptor_count):
                    first_release = sample["step"]
                if first_release is not None and (sample["truth"] is None or not sample["truth"].get("alive", True)):
                    terminal = sample["step"]
                    break
                if index % 10 == 9:
                    print(json.dumps({"profile": profile, "step": sample["step"], "track": first_track, "ready": first_ready, "release": first_release, "targetAlive": sample["truth"] is not None and sample["truth"].get("alive")}), flush=True)
            final = samples[-1]
            scenes.append({
                "profile": profile,
                "setup": setup,
                "timing": {"firstTrackStep": first_track, "firstReadyStep": first_ready, "firstReleaseStep": first_release, "terminalStep": terminal},
                "maxFireLog": max_fire_log,
                "maxInterceptors": max_interceptors,
                "samples": samples,
                "final": final,
            })
            page.close()
            print(json.dumps({"profile": profile, "timing": scenes[-1]["timing"], "finalTruth": final["truth"]}), flush=True)
        browser.close()
    checks: dict[str, bool] = {"pageErrors": not errors}
    for scene in scenes:
        name = scene["profile"]
        timing = scene["timing"]
        final = scene["final"]
        checks[f"{name}.naturalTrack"] = timing["firstTrackStep"] is not None and all(track.get("source") != "TEST" for sample in scene["samples"] for track in (sample.get("input") or {}).get("tracks", []))
        checks[f"{name}.oodaReady"] = timing["firstReadyStep"] is not None
        checks[f"{name}.nativeVlsRelease"] = scene["maxFireLog"] > 0 and scene["maxInterceptors"] > 0 and timing["firstReleaseStep"] is not None
        checks[f"{name}.releaseAfterReady"] = timing["firstReadyStep"] is not None and timing["firstReleaseStep"] is not None and timing["firstReleaseStep"] >= timing["firstReadyStep"]
        checks[f"{name}.terminalOutcome"] = timing["terminalStep"] is not None and (final["truth"] is None or not final["truth"].get("alive", True))
        checks[f"{name}.terminalIsInterceptNotShipHit"] = final["afterAction"]["shipHitCount"] == scene["setup"]["before"]["shipHitCount"] and any(
            (str(event.get("result", "")) in {"KILL", "STRUCT_FAIL", "DAMAGED", "AIR_KILL"} or str(event.get("deathReason", "")) == "PROX_DETONATION_KILL")
            and event.get("missedTarget") is not True
            for event in final["afterAction"]["interceptHistory"]
        )
        checks[f"{name}.oodaInvariants"] = all((sample.get("ooda") or {}).get("diagnostics", {}).get(key, 0) == 0 for sample in scene["samples"] for key in ("fallback", "rejected")) and all((sample.get("provider") or {}).get(key, 0) == 0 for sample in scene["samples"] for key in ("validationFailures", "rngMismatchCount", "truthAuditFailures"))
        checks[f"{name}.faultFree"] = all(not sample["core"] and all(value is None for value in sample["faults"]) for sample in scene["samples"])
    payload = {
        "schema": "AEGIS_DEFENSE_OODA_A_NATURAL_TERMINAL_GATE_1",
        "candidate": {"file": args.html.name, "bytes": len(raw), "sha256": PRODUCT_SHA256},
        "seed": SEED,
        "scenario": {"source": "NATIVE_SENSOR_NO_SYNTHETIC_TRACK", "label": "Kh-35U", "rangeKm": 12, "altM": 25, "speedMps": 260, "fixedTickHz": 60},
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
