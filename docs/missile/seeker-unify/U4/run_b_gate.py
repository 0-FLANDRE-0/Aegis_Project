#!/usr/bin/env python3
"""Commit B limited RAM SHADOW -> ACTIVE gate (no broad regression)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "docs/pip/B"), str(ROOT / "docs/bunkerhill/K")]
import browser_backend

browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


SYNTHETIC = r"""()=>{
 const api=window.__SEEKER_U4_B__,sample={azRad:.2,elRad:-.03,snr:4,signal:3.5,extentRad:.001,quality:.82,
   compositeCount:2,elementIndex:31,scanPhaseRad:.5,_debugKind:'ASM',targetId:'MUST_NOT_ESCAPE',faction:'HOSTILE'},
 rf=api.adaptRf(sample,'PLAYER'),ir=api.adaptIr(sample,'OWNER'),ownerRoute=api.route('RF','OWNER',sample),playerRoute=api.route('IR','PLAYER',sample),
 emitters=[
   {name:'off',value:{seekerOn:false,radarOn:false,seeker:{emitting:false,trackQuality:1}}},
   {name:'default',value:{seekerOn:true,seeker:{emitting:true}}},
   {name:'lowLocalQuality',value:{seekerOn:true,seeker:{emitting:true,trackQuality:.25},_seekerQuality:.25}},
   {name:'highLocalQuality',value:{seekerOn:true,seeker:{emitting:true,trackQuality:1},_seekerQuality:1}}
 ].map(q=>({name:q.name,legacy:api.legacyEmitterStrength(q.value),physical:api.physicalEmitterStrength(q.value),routed:api.routedEmitterStrength(q.value)})),
 authority=api.authorityMatrix(),ownership=api.ownershipContract(),snapshot=api.snapshot(),serialized=JSON.stringify({rf,ir,ownerRoute:ownerRoute.common,playerRoute:playerRoute.common}),
 checks={rf2d:rf.dimension==='PASSIVE_RF_2D'&&rf.values.length===2&&rf.covariance.length===4,
   ir2d:ir.dimension==='PASSIVE_IR_2D'&&ir.values.length===2&&ir.covariance.length===4,
   truthFree:!/MUST_NOT_ESCAPE|targetId|faction|debugKind|entityId|objectId/.test(serialized),
   bothOrigins:ownerRoute.common.observationOwner==='SHIP_OWNED_WEAPON'&&playerRoute.common.observationOwner==='PLAYER_WEAPON',
   offPreserved:emitters[0].legacy===0&&emitters[0].physical===0&&emitters[0].routed===0,
   defaultPreserved:Object.is(emitters[1].legacy,emitters[1].physical),
   defectObservable:emitters[2].legacy!==emitters[2].physical&&emitters[3].legacy!==emitters[3].physical,
   modeRoute:emitters.slice(2).every(q=>Object.is(q.routed,api.mode==='ACTIVE'?q.physical:q.legacy)),
   authority:authority.pass,ownership:ownership.defectConfirmed&&ownership.fixedPathIndependent&&ownership.authorityLocal&&ownership.guidanceLocal,
   rngFree:snapshot.rngConsumedByCommonLayer===false,truthOutputFalse:snapshot.truthOutput===false};
 return {mode:api.mode,rf,ir,ownerRoute,playerRoute,emitters,authority,ownership,snapshot,checks,pass:Object.values(checks).every(Boolean)};
}"""


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_product(pw, path: Path, adapter: bool) -> dict:
    errors: list[str] = []
    browser = launch(pw)
    page = load(browser, path.read_bytes(), ship="DDG_119_LATE_FLIGHT_IIA", seed=0xB40001, errors=errors)
    core = page.evaluate("()=>Array.from(window.__CORE_SELFTEST_FAILURES__??[])")
    motion = page.evaluate("()=>__NAVAL_SIM_DIAG__.runWip107RamMotionCase({seed:107401,rangeKm:6,maxTimeS:32})")
    rf = page.evaluate("()=>__NAVAL_SIM_DIAG__.runWip146RamDirectFlightCase({seed:146101,rangeM:8000,targetAltM:12,targetSpeedMps:280,emitter:true,dt:1/120,maxTimeS:14})")
    ir = page.evaluate("()=>__NAVAL_SIM_DIAG__.runWip146RamDirectFlightCase({seed:146102,rangeM:6500,targetAltM:12,targetSpeedMps:280,emitter:false,dt:1/120,maxTimeS:14})")
    synthetic = page.evaluate(SYNTHETIC) if adapter else None
    page.close(); browser.close()
    return {"path":path.name,"sha256":sha(path),"core":core,"motion":motion,"rf":rf,"ir":ir,"synthetic":synthetic,"errors":errors}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--shadow", type=Path, required=True)
    ap.add_argument("--active", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(); started = time.monotonic()
    with sync_playwright() as pw:
        baseline = run_product(pw,args.baseline,False)
        shadow = run_product(pw,args.shadow,True)
        active = run_product(pw,args.active,True)
        repeat = run_product(pw,args.active,True)
    # Commit B deliberately changes only physical emitter signal ownership.
    # SHADOW must remain byte-equivalent; ACTIVE must be deterministic and all
    # other contracts remain valid.  Direct-flight differences are recorded,
    # not hidden or retuned.
    checks = {
      "shadowMotionEqual":shadow["motion"]==baseline["motion"],
      "shadowRfEqual":shadow["rf"]==baseline["rf"],
      "shadowIrEqual":shadow["ir"]==baseline["ir"],
      "activeDeterministic":all(active[k]==repeat[k] for k in ("motion","rf","ir")),
      "shadowContract":bool(shadow["synthetic"] and shadow["synthetic"]["pass"] and shadow["synthetic"]["mode"]=="SHADOW"),
      "activeContract":bool(active["synthetic"] and active["synthetic"]["pass"] and active["synthetic"]["mode"]=="ACTIVE"),
      "activeRoutesBothSensors":active["synthetic"]["snapshot"]["rfRoutes"]>0 and active["synthetic"]["snapshot"]["irRoutes"]>0,
      "ownershipDifferenceObserved":active["synthetic"]["snapshot"]["emitterOwnershipDifferences"]>=2,
      "activeFlightFinite":all(q.get("error") is None and q.get("durationS",0)>0 for q in (active["motion"],active["rf"],active["ir"])),
      "coreSelfTests":all(q["core"]==[] for q in (baseline,shadow,active,repeat)),
      "pageErrorsZero":not any(q["errors"] for q in (baseline,shadow,active,repeat)),
    }
    result={"schema":"AEGIS_SEEKER_UNIFY_U4_B_GATE_1","status":"PASS" if all(checks.values()) else "FAIL",
      "elapsedS":time.monotonic()-started,"broadRegressionRun":False,"representativeBranchesPerMode":12,
      "checks":checks,"baseline":baseline,"shadow":shadow,"active":active,"activeRepeat":repeat,"release":False}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"elapsedS":result["elapsedS"],"checks":checks,
      "allowedOwnershipDelta":{"baseline":baseline["rf"].get("sourceTimeline"),"active":active["rf"].get("sourceTimeline")},
      "activeAudit":active["synthetic"]["snapshot"]},ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["status"]=="PASS" else 1)


if __name__ == "__main__":
    main()
