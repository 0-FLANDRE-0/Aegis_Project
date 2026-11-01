"""Approved ON-only surface subset, same original seeds, no hit fitting."""
from pathlib import Path
import json,time
from playwright.sync_api import sync_playwright
from harness import P,R,build,serve,launch,sha
from fast_http import load_fast_http
from deadline import check,remaining
E=P/'evidence/surface';E.mkdir(parents=True,exist_ok=True);errors=[];start=time.perf_counter();extra='window.__B2_SURFACE_PROBE__=c=>{__GB_TEST__.reset(c.seed);return runWip13b11MovingWorldGunFixture({rangeKm:c.rangeKm,ownSpeedKt:20,bearingDeg:0});};';raw=build(record=False,extra=extra);server,url=serve(raw)
with sync_playwright()as pw:
 b=launch(pw)
 for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_fast_http(b,url,own=ship,errors=errors);p.set_default_timeout(min(600000,int(remaining()*1000)))
  with(E/(ship+'-ON.jsonl')).open('w')as f:
   for km in[5,10,15]:
    for seed in range(723001,723016):
     check();c={'ship':ship,'on':True,'rangeKm':km,'seed':seed};q=p.evaluate('c=>__B2_SURFACE_PROBE__(c)',c);f.write(json.dumps({**c,'result':q},separators=(',',':'))+'\n');f.flush()
    print(ship,km,flush=True)
  p.close();p.context.close()
 b.close()
server.shutdown();(E/'execution.json').write_text(json.dumps({'cases':90,'errors':errors,'elapsedS':time.perf_counter()-start,'htmlSha256':sha((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes()),'seeds':[723001,723015],'onOnly':True},indent=2)+'\n');assert not errors
