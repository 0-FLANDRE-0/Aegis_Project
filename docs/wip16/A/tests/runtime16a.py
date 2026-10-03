#!/usr/bin/env python3
import asyncio,json,sys,os
from pathlib import Path
from playwright.async_api import async_playwright
if len(sys.argv)!=2: raise SystemExit("usage: runtime16a.py RESULT.html")
HTML=Path(sys.argv[1]).read_text(encoding='utf-8')
async def main():
  async with async_playwright() as p:
    launch={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']}
    if os.environ.get('AEGIS_CHROMIUM_EXECUTABLE'):
      launch['executable_path']=os.environ['AEGIS_CHROMIUM_EXECUTABLE']
    b=await p.chromium.launch(**launch)
    errors=[]
    async def fresh(phase):
      context=await b.new_context()
      page=await context.new_page()
      page.on('pageerror',lambda e:errors.append({'phase':phase,'error':str(e)}))
      await page.set_content(HTML,wait_until='domcontentloaded',timeout=90000)
      await page.wait_for_function('window.C55Packaging?.ready&&window.__NAVAL_SIM_DIAG__',timeout=90000)
      return page
    page=await fresh('benchmark')
    rows=[]
    def row(name,ok,detail=None): rows.append({"name":name,"pass":bool(ok),"detail":detail})

    # Run the same-seed Phalanx benchmark before any diagnostic audit that can
    # mutate simulation/diagnostic RNG or transient world state. Each phase
    # gets a fresh context so spotting/audits cannot contaminate the benchmark.

    core=await page.evaluate('window.__CORE_SELFTEST_FAILURES__')
    row("core selftest zero",len(core)==0,core)
    prof=await page.evaluate('window.__WIP16_PHALANX_FC__?.profile?.()')
    row("WIP16 profile exposed",prof and prof.get("schema")=="PHALANX_FIRE_CONTROL_STABILIZATION_V48_1_WIP16A",prof)
    opts={"bearingsDeg":[-20,0,20],"seeds":[23001,23002],"rangeKm":4,"altM":12,"speedMps":280,"maxTimeS":20}
    ph=await page.evaluate('o=>window.__NAVAL_SIM_DIAG__.runWip103PhalanxMeasurement(o)',opts)
    a=ph["aggregate"]; ship=sum(1 for c in ph["cases"] if c["summary"]["shipHit"])
    regions={}
    for c in ph["cases"]:
      for e in c["hitEvents"]: regions[e.get("hitRegion")]=regions.get(e.get("hitRegion"),0)+1
    row("Phalanx 6-case hit rate >= 1%",a["hitRate"]>=.01,a)
    row("Phalanx 6-case no ship hit",ship==0,{"shipHits":ship,"outcomes":a["outcomes"]})
    row("body/control surfaces both physical",regions.get("BODY",0)>0 and regions.get("CONTROL_SURFACE",0)>0,regions)
    row("firing center tightened",a["turretErrDeg"]["median"]<.05,a["turretErrDeg"])
    page=await fresh('spotting')
    spot=await page.evaluate('o=>window.__NAVAL_SIM_DIAG__.runWip104PhalanxSpottingMeasurement(o)',{"bearingsDeg":[0],"seeds":[21001,21002],"rangeKm":4,"altM":12,"speedMps":280,"maxTimeS":20})
    row("closed-loop spotting remains active",spot["aggregate"]["firstCorrectionDelayFromFireS"]["median"] is not None and spot["aggregate"]["firstCorrectionDelayFromFireS"]["median"]<2.5,spot["aggregate"].get("firstCorrectionDelayFromFireS"))
    page=await fresh('regression')
    bal=await page.evaluate('window.__WIP203_PHALANX_DIAG__.audit()')
    row("Mk244 3.0mil unchanged",abs(bal["profile"]["dispersion80DiameterMil"]-3.0)<1e-12,bal["fixedDispersion"])
    man=await page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB3Maneuver.audit()')
    row("CIWS maneuver estimator preserved",man["straight"]["accelMps2"]<3 and man["maneuver"]["estimatedAyMps2"]>12 and man["prediction"]["enabled"],man)
    dmg=await page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB3Damage.audit()')
    gun=dmg["mounts"][0]["rows"]
    row("CIWS damage ordering preserved",gun[0]["oneSecondRounds"]>gun[1]["oneSecondRounds"]>gun[2]["oneSecondRounds"]>gun[3]["oneSecondRounds"],[q["oneSecondRounds"] for q in gun])
    surf=await page.evaluate('window.__NAVAL_SIM_DIAG__.runWip13aSurfaceTargetDiagnostics()')
    row("WIP13A surface/flood checks preserved",all(surf["checks"].values()),surf["checks"])
    ts=await page.evaluate('window.__NAVAL_SIM_DIAG__.runWip13aTimeScaleRegression()')
    row("WIP13A time-scale preserved",ts.get("pass") is True,ts)
    row("page errors zero",len(errors)==0,errors)
    out={"schema":"AEGIS_WIP16A_RUNTIME_CHECK","passed":sum(x["pass"] for x in rows),"total":len(rows),"pass":all(x["pass"] for x in rows),"rows":rows,
         "phaseIsolation":"FRESH_BROWSER_CONTEXT_PER_PHASE","phalanxSixCase":ph,"spotting":spot}
    print(json.dumps(out,ensure_ascii=False,indent=2))
    await b.close()
    if not out["pass"]: raise SystemExit(1)
asyncio.run(main())
