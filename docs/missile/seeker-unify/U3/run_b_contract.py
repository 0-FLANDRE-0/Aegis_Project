#!/usr/bin/env python3
"""Execute the U3-B data-contract and limited Harpoon scene gates."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path[:0] = ["/workspace/aegis-ui-a/docs/pip/B", "/workspace/aegis-ui-a/docs/bunkerhill/K"]
import browser_backend
browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument("--html",type=Path,required=True);ap.add_argument("--baseline",type=Path);ap.add_argument("--out",type=Path,required=True);args=ap.parse_args()
    body=args.html.read_bytes();errors=[];started=time.monotonic()
    jobs=[{"seed":974000+i,"rangeKm":r,"speedKt":s,"turnDeg":t} for i,(r,s,t) in enumerate(((40,0,0),(40,30,45),(60,30,90),(80,15,0),(100,30,45),(120,30,0)))]
    with sync_playwright() as pw:
        browser=launch(pw);page=load(browser,body,ship="CG_52_LATE_TICONDEROGA",errors=errors)
        matrix=page.evaluate("()=>__SEEKER_U3_DIAG__.cueMatrixB()")
        first=page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runHarpoonCueCase(o))",jobs)
        second=page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runHarpoonCueCase(o))",jobs)
        contract=page.evaluate("()=>__SEEKER_U3_DIAG__.contractB()")
        page.close();browser.close()
        baseline_rows=None;baseline_errors=[]
        if args.baseline:
            baseline_body=args.baseline.read_bytes();browser=launch(pw);page=load(browser,baseline_body,ship="CG_52_LATE_TICONDEROGA",errors=baseline_errors)
            baseline_rows=page.evaluate("a=>a.map(o=>__SEEKER_UNIFY_B_DIAG__.runHarpoonCueCase(o))",jobs);page.close();browser.close()
    deterministic=first==second
    route_contract=("ROUTE_PLAN_PRIOR" in contract["routeProgram"] and "ROUTE_PLAN_PRIOR" in contract["routeGate"] and "observationUpdate:false" in contract["routeGate"])
    # The inherited diagnostic layer intentionally wraps harpoonSeekerA, so its
    # Function#toString is not a reliable static source audit here. Dynamic
    # seeker cases above exercise it; static product scope is checked separately.
    consumers=("gate.searchBasketM" in contract["attackGuard"] and "searchBasketM:gate.searchBasketM" in contract["journal"])
    core_pass=matrix["coreAudits"]["harpoon"]["pass"] and matrix["coreAudits"]["seeker"]["pass"]
    passed=matrix["pass"] and deterministic and route_contract and consumers and core_pass and not errors
    differences=[] if baseline_rows is None else [{"index":i,"input":jobs[i],"baseline":a,"candidate":b} for i,(a,b) in enumerate(zip(baseline_rows,first)) if a!=b]
    if baseline_errors:passed=False
    result={"schema":"AEGIS_SEEKER_UNIFY_U3_B_GATE_1","status":"PASS" if passed else "FAIL","elapsedS":time.monotonic()-started,"inputSha256":hashlib.sha256(body).hexdigest(),"baselineSha256":hashlib.sha256(args.baseline.read_bytes()).hexdigest() if args.baseline else None,"matrix":matrix,"sceneCases":len(jobs),"sceneDeterministic":deterministic,"sceneRows":first,"baselineRows":baseline_rows,"behaviorDifferences":differences,"allowedDifferenceBasis":"CUE_A covariance basket replaces fixed 4 km only","routeContractPass":route_contract,"consumerPass":consumers,"coreAuditPass":core_pass,"contract":contract,"pageErrors":{"candidate":errors,"baseline":baseline_errors}}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n");print(json.dumps({k:result[k] for k in ("status","elapsedS","sceneCases","sceneDeterministic","routeContractPass","consumerPass","coreAuditPass","pageErrors")},ensure_ascii=False,indent=2));raise SystemExit(0 if passed else 1)


if __name__ == "__main__":main()
