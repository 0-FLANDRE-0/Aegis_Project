#!/usr/bin/env python3
"""Commit C HOJ SHADOW -> ACTIVE and threat-mode gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path[:0]=["/workspace/aegis-ui-a/docs/pip/B","/workspace/aegis-ui-a/docs/bunkerhill/K"]
import browser_backend
browser_backend.install()
from browser_i import launch,load
from playwright.sync_api import sync_playwright


JOBS=[{"seed":975000+i,"rangeKm":r,"speedKt":s,"turnDeg":t} for i,(r,s,t) in enumerate(((40,0,0),(40,30,45),(60,30,90),(80,15,0),(100,30,45),(120,30,0)))]


def run(pw,path:Path,exercise:bool)->dict:
    body=path.read_bytes();browser=launch(pw);errors=[];page=load(browser,body,ship="CG_52_LATE_TICONDEROGA",errors=errors)
    scenes=page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runHarpoonCueCase(o))",JOBS)
    hoj=page.evaluate("()=>__SEEKER_U3_DIAG__.hojExerciseC()") if exercise else None
    repeat=page.evaluate("()=>__SEEKER_U3_DIAG__.hojExerciseC()") if exercise else None
    page.close();browser.close();return {"sha256":hashlib.sha256(body).hexdigest(),"scenes":scenes,"hoj":hoj,"repeat":repeat,"errors":errors}


def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument("--baseline",type=Path,required=True);ap.add_argument("--shadow",type=Path,required=True);ap.add_argument("--active",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);args=ap.parse_args();started=time.monotonic()
    with sync_playwright() as pw:baseline=run(pw,args.baseline,False);shadow=run(pw,args.shadow,True);active=run(pw,args.active,True)
    shadow_audit=shadow["hoj"]["asmAudit"];active_audit=active["hoj"]["asmAudit"]
    scene_differences=[{"index":i,"input":JOBS[i],"baseline":a,"active":b} for i,(a,b) in enumerate(zip(baseline["scenes"],active["scenes"])) if a!=b]
    checks={"shadowBehavior":shadow["hoj"]["pass"],"shadowCompared":shadow_audit["comparisons"]>0,"shadowStateEqual":shadow_audit["mismatches"]==0,
      "shadowRngEqual":shadow_audit["rngMismatches"]==0,"activeBehavior":active["hoj"]["pass"],"activeNoShadowWork":active_audit["comparisons"]==0,
      "deterministicShadow":shadow["hoj"]==shadow["repeat"],"deterministicActive":active["hoj"]==active["repeat"],"noJammerSceneEqual":not scene_differences,
      "pageErrors":not any(q["errors"] for q in (baseline,shadow,active))}
    passed=all(checks.values());result={"schema":"AEGIS_SEEKER_UNIFY_U3_C_GATE_1","status":"PASS" if passed else "FAIL","elapsedS":time.monotonic()-started,"checks":checks,"sceneCases":len(JOBS),"sceneDifferences":scene_differences,"shadow":shadow,"active":active,"baseline":{"sha256":baseline["sha256"],"scenes":baseline["scenes"],"errors":baseline["errors"]},"confirmedOnlyPerformance":"UNVERIFIED_LIMITED_FEATURE_OFF_SCENE_ONLY"}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n");print(json.dumps({"status":result["status"],"elapsedS":result["elapsedS"],"checks":checks,"shadowAudit":shadow_audit,"activeAudit":active_audit,"sceneDifferences":len(scene_differences)},ensure_ascii=False,indent=2));raise SystemExit(0 if passed else 1)


if __name__=="__main__":main()
