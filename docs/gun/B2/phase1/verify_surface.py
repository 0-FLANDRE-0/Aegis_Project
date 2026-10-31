"""Native inertial-world surface fixture, same seeds before/after; no hit fitting."""
from pathlib import Path
import json,time
from playwright.sync_api import sync_playwright
from harness import P,R,OFF,build,serve,launch,sha
from fast_http import load_fast_http
E=P/'evidence/surface';E.mkdir(parents=True,exist_ok=True)
extra='window.__B2_SURFACE_PROBE__=c=>{__GB_TEST__.reset(c.seed);return runWip13b11MovingWorldGunFixture({rangeKm:c.rangeKm,ownSpeedKt:20,bearingDeg:0});};'
errors=[];start=time.perf_counter()
with sync_playwright()as pw:
 browser=launch(pw)
 for enabled in [False,True]:
  raw=build(record=False,flags={k:enabled for k in OFF},extra=extra);server,url=serve(raw)
  for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   page=load_fast_http(browser,url,own=ship,errors=errors);page.set_default_timeout(600000);path=E/(ship+('-ON'if enabled else'-OFF')+'.jsonl')
   with path.open('w')as f:
    for km in [5,10,15]:
     for seed in range(723001,723031):
      c={'ship':ship,'on':enabled,'rangeKm':km,'seed':seed};q=page.evaluate('c=>__B2_SURFACE_PROBE__(c)',c);f.write(json.dumps({**c,'result':q},separators=(',',':'))+'\n');f.flush()
     print(ship,enabled,km,flush=True)
   page.close();page.context.close()
  server.shutdown()
 browser.close()
(E/'execution.json').write_text(json.dumps({'errors':errors,'elapsedS':time.perf_counter()-start,'cases':360,'htmlSha256':sha((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes())},indent=2)+'\n')
