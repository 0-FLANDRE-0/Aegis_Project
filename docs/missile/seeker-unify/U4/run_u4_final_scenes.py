#!/usr/bin/env python3
"""U4 final-only representative seeker flights and clock/lifecycle checks.

This file is called once by ``run_final_regression.py`` after the candidate is
frozen.  It does not patch the product or substitute a second physics model.
Every flight below calls an existing diagnostic that drives the real fixed-tick
weapon path in the packed game.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time


ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "docs/pip/B"), str(ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


PRODUCT_SHA256 = "00d36aad194990b742bed3816de7eaca31ca135aef27fcf1f94106df3a6fc498"
PRODUCT_BYTES = 22_195_923


def strict(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


RUNTIME = r"""()=>{
 const d=window.__NAVAL_SIM_DIAG__;
 const compactSarh=q=>({label:q.label,seed:q.seed,durationS:q.durationS,prox:q.prox,
   missileDeathReason:q.missileDeathReason,targetAlive:q.targetAlive,
   sarhSamples:q.summary?.sarhSamples,sarhEkfErrorMedianM:q.summary?.sarhEkfErrorMedianM});
 const compactAsm=q=>({label:q.label,seed:q.seed,durationS:q.durationS,everAcquire:q.everAcquire,
   everTrack:q.everTrack,acquireTimeS:q.acquireTimeS,coastEntries:q.coastEntries,
   reacquireEntries:q.reacquireEntries,reacquireSuccesses:q.reacquireSuccesses,
   deathReason:q.deathReason,shipHit:q.shipHit});
 const compactScale=q=>({scale:q.scale,seed:q.seed,steps:q.steps,frames:q.frames,kill:q.kill,
   prox:q.prox,reason:q.reason,lifeS:q.lifeS,x:q.x,y:q.y,z:q.z,speedMps:q.speedMps,
   massKg:q.massKg,boosterSeparated:q.boosterSeparated,target:q.target,rng:q.rng});
 const asm=compactAsm(d.runWip108AsmAcquireCase({label:'Kh-35U',speedKt:0,seed:108041,
   headingDeg:90,rangeKm:18,maxTimeS:20,emconActive:true}));
 const harpoon={seeker:__HARPOON_DIAG_A__.seekerAudit(),core:__HARPOON_DIAG_A__.coreAudit(),
   selection:__HARPOON_DIAG_A__.selectionAudit()};
 const sm2=compactSarh(d.runWip107SarhCase({label:'Kh-35U',speedKt:0,seed:107241,
   headingDeg:90,rangeKm:25,maxTimeS:35}));
 // The live ESSM flight begins on the bistatic SARH path and transitions to its
 // Block-2 active seeker.  Commit-A's bounded gate separately proves the
 // SARH-only Block-1 branches without changing the product configuration.
 const essm=d.runWip107EssmCase({label:'Kh-35U',speedKt:0,seed:107341,
   headingDeg:90,rangeKm:12,maxTimeS:25});
 const sm6=__AEGIS_WIP14A6_SM6__.runIntercept({seed:146041,rangeKm:18,altM:1000,
   speedMps:300,maxTimeS:80,arhEnabled:true,recordTrajectory:false});
 const ram=d.runWip107RamMotionCase({seed:107441,rangeKm:6,maxTimeS:32});
 const ramDirect=d.runWip146RamDirectFlightCase({seed:146041,rangeM:6000,
   targetAltM:12,targetSpeedMps:280,emitter:true,maxTimeS:14});
 const timeScale=[1,8,16,64].map(timeScale=>compactScale(
   __AEGIS_WIP14A7_AERO__.timeScaleIntercept({timeScale,seed:147741,rangeKm:18,
     altM:1000,speedMps:300,maxTimeS:45})));
 const scalePhysics=timeScale.map(q=>{const c={...q};delete c.scale;delete c.frames;delete c.steps;return c;});
 const lifecycle=__SEEKER_U4_C__.syntheticMatrix();
 const contract=__SEEKER_U4_C__.contractAudit();
 const esm=__ESM_A__.snapshot();
 const esmText=document.body?.innerText??'';
 return {
   core:Array.from(window.__CORE_SELFTEST_FAILURES__??[]),
   threatMode:String(window.THREAT_ASSUMPTION_MODE??'MAX_THREAT'),
   asm,harpoon,sm2,essm,
   sm6:{seed:sm6.seed,error:sm6.error??null,success:sm6.success,prox:sm6.prox,kill:sm6.kill,
     missileDeathReason:sm6.missileDeathReason,durationS:sm6.durationS,
     firstActiveAtS:sm6.firstActiveAtS??null,firstArhTrackAtS:sm6.firstArhTrackAtS??null,
     finalArhProfileId:sm6.finalArhProfileId??null},
   ram,ramDirect,timeScale,scalePhysics,lifecycle,contract,
   esm:{schema:esm.schema,operational:esm.operational,truthUsedByConsumer:esm.truthUsedByConsumer,
     automaticEngagementAuthority:esm.automaticEngagementAuthority,uiTextPresent:/ESM/.test(esmText)},
   cSnapshot:__SEEKER_U4_C__.snapshot()
 };
}"""


def run_once(pw, product: Path, seed: int) -> dict:
    errors: list[str] = []
    browser = launch(pw)
    page = load(
        browser,
        product.read_bytes(),
        ship="DDG_119_LATE_FLIGHT_IIA",
        seed=seed,
        errors=errors,
    )
    result = page.evaluate(RUNTIME)
    page.close()
    browser.close()
    return {"result": result, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    body = args.product.read_bytes()
    assert len(body) == PRODUCT_BYTES
    assert hashlib.sha256(body).hexdigest() == PRODUCT_SHA256
    packed = re.search(rb'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>', body, re.S)
    assert packed
    main_source = gzip.decompress(base64.b64decode(packed.group(1)))
    esm_ui_static = all(
        needle in main_source
        for needle in (
            b"function electronicCicTextF()",
            b"function mapObservedObjectsA()",
            b"window.__ESM_A__=Object.freeze",
        )
    )
    with sync_playwright() as pw:
        first = run_once(pw, args.product, 0xA4F001)
        repeat = run_once(pw, args.product, 0xA4F001)
    r = first["result"]
    scale = r["timeScale"]
    checks = {
        "pageAndConsoleErrorsZero": not first["errors"] and not repeat["errors"],
        "candidateTwoRunDeterministic": first["result"] == repeat["result"],
        "coreSelfTestsZero": not r["core"],
        "maxThreatMode": r["threatMode"] == "MAX_THREAT",
        "asmActualFlightAcquiresAndTracks": r["asm"]["everAcquire"] and r["asm"]["everTrack"],
        "harpoonContractsPass": all(r["harpoon"][k]["pass"] for k in ("seeker", "core", "selection")),
        "sm2SarhActualFlightIntercepts": r["sm2"]["prox"] and not r["sm2"]["targetAlive"],
        "essmSarhToArhActualFlightIntercepts": r["essm"]["prox"] and r["essm"]["intercept"],
        "sm6DualModeActualFlightFinite": not r["sm6"]["error"] and r["sm6"]["durationS"] > 0,
        "ramActualSchedulerFlightTerminates": r["ram"]["durationS"] > 0 and not r["ram"]["targetAlive"],
        "ramDirectRfIrFlightFinite": r["ramDirect"]["durationS"] > 0
        and r["ramDirect"]["steps"] > 0
        and r["ramDirect"]["finalMode"] in {"MEM", "RF", "IR"},
        "oneEightSixteenPhysicsExact": r["scalePhysics"][0] == r["scalePhysics"][1] == r["scalePhysics"][2],
        "sixtyFourPhysicsExact": len(r["scalePhysics"]) == 4 and r["scalePhysics"][3] == r["scalePhysics"][0],
        # The display-frame loop finishes its current fixed-step batch after a
        # terminal event.  That makes the diagnostic step counter overshoot by
        # at most scale-1 while the frozen physical terminal state stays exact.
        "sixtyFourStepCapObserved": all(
            q["frames"] == math.ceil(scale[0]["frames"] / q["scale"])
            and 0 <= q["steps"] - scale[0]["steps"] < q["scale"]
            for q in scale
        ),
        "lifecycleStateMatrixPass": r["lifecycle"]["pass"] is True,
        "anonymousContractPass": r["contract"]["pass"] is True,
        "commonLayerNoRngOrSaveSchema": r["cSnapshot"]["rngConsumedByCommonLayer"] is False
        and r["cSnapshot"]["saveSchemaChanged"] is False,
        "esmRuntimeAndUiPresent": esm_ui_static
        and r["esm"]["schema"] == "AEGIS_ESM_SNAPSHOT_A_1"
        and r["esm"]["operational"] is True,
        "esmHasNoTruthOrAuthority": r["esm"]["truthUsedByConsumer"] is False
        and r["esm"]["automaticEngagementAuthority"] is False,
    }
    payload = {
        "schema": "AEGIS_SEEKER_UNIFY_U4_FINAL_SCENES_1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "candidate": args.product.name,
        "candidateSha256": PRODUCT_SHA256,
        "threatAssumptionMode": "MAX_THREAT",
        "elapsedS": time.monotonic() - started,
        "checks": checks,
        "esmUiStaticContractPresent": esm_ui_static,
        "first": first,
        "repeat": repeat,
        "harpoonActualFlightEvidence": "native harpoon-f1 suite in the same one-shot broad run",
        "essmBlock1Evidence": "Commit-A bounded SARH-only gate plus this live ESSM SARH-to-ARH flight",
        "confirmedOnly": {
            "scope": "inherited U3 static and limited feature-off evidence only",
            "performance": "UNVERIFIED",
        },
        "release": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(strict(payload))
    print(strict({"status": payload["status"], "elapsedS": payload["elapsedS"], "checks": checks}))
    raise SystemExit(0 if payload["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
