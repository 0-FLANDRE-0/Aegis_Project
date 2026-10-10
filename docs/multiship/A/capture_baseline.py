"""Read the selected ship's live baseline through existing diagnostic APIs.

Uses the original packed HTML. Timings describe this browser/host, not mobile FPS.
The same fixtures are used for the candidate comparison.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "docs/bunkerhill/K"))
from browser_i import launch, load

def capture(page, ticks):
    return page.evaluate("""ticks => {
      const d=window.__NAVAL_SIM_DIAG__;
      const names=Object.keys(d);
      const before=d.exportOperationalStateV48Wip11A();
      d.setTerrainDiagBypass(true);
      const enable=names.find(k=>/profiler/i.test(k)&&/enable|set/i.test(k));
      if(enable)d[enable](true);
      const t0=performance.now(), run=d.runFramesToTicks(60,1,ticks);
      const totalMs=performance.now()-t0;
      const after=d.exportOperationalStateV48Wip11A();
      return {before,after,run,totalMs,hitboxes:d.wip101ShipHitboxes(),profiler:d.profilerSnapshotV48Wip11A(),
        ownership:d.runtimeOwnershipAuditV48Wip11A(),
        dynamics:d.shipDynamics(),profile:d.shipProfileV48Wip11(),
        core:window.__CORE_SELFTEST_FAILURES__,
        faults:{simulation:window.__WIP125_DIAG__.wip150RuntimeFault(),
          presentation:window.__WIP125_DIAG__.wip150PresentationFault()},
        fixtureApis:names.filter(k=>/profiler|spawn|damage|flood|impact|reset|closure/i.test(k))};
    }""", ticks)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("html",type=Path)
    parser.add_argument("out",type=Path)
    parser.add_argument("--ticks",type=int,default=240)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    body=args.html.read_bytes()
    errors=[]
    cases=[]
    with sync_playwright() as pw:
        browser=launch(pw)
        for ship in ["DDG_119_LATE_FLIGHT_IIA","CG_52_LATE_TICONDEROGA"]:
            page=load(browser,body,ship=ship,errors=errors)
            result=capture(page,args.ticks)
            result["ship"]=ship
            cases.append(result)
            page.close()
            print(json.dumps({"ship":ship,"ticks":args.ticks,"totalMs":result["totalMs"]}),flush=True)
        browser.close()
    checks={"coreZero":all(c["core"]==[] for c in cases),
        "ownershipPass":all(c["ownership"]["pass"] for c in cases),
        "faultsZero":all(all(v is None for v in c["faults"].values()) for c in cases),
        "pageErrorsZero":not errors}
    report={"schema":"AEGIS_MULTI_SHIP_A_BASELINE","html":args.html.name,
        "sha256":hashlib.sha256(body).hexdigest(),"ticks":args.ticks,
        "backend":"headless Chromium, software CPU fixture; not a device FPS claim",
        "checks":checks,"cases":cases,"errors":errors,"pass":all(checks.values())}
    (args.out/"baseline.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    blueprint={"schema":"AEGIS_PROFILE_DAMAGE_REGISTRATION_MULTI_SHIP_A",
        "baselineSha256":report["sha256"],
        "profiles":{c["ship"]:{"profileRevision":c["profile"]["revision"],
            "hitboxes":c["hitboxes"]} for c in cases}}
    (args.out/"damage-registration.json").write_text(json.dumps(blueprint,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"checks":checks,"pass":report["pass"]}),flush=True)
    raise SystemExit(0 if report["pass"] else 1)

if __name__=="__main__":main()
