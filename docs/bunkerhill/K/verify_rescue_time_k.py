"""Fixed-tick escape/rafts must match across the four existing time scales."""
from pathlib import Path
import argparse,json,hashlib
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];rows=[];checks={}
with sync_playwright()as pw:
 b=launch(pw)
 for scale in [1,8,16,64]:
    page=load(b,served_bytes(a.html),errors=errors)
    q=page.evaluate("""scale=>{const d=window.__NAVAL_SIM_DIAG__,r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__;d._resetShipTest();w.world.entities.aircraft.length=0;w.world.entities.surfaceContacts.length=0;d.setEmcon(true);d.wip13a3SetManualWeather({hsM:0,windSpeedMps:6,windDirectionDeg:20});r.crew.abandon();let steps=0,frames=0;while(steps<9600){steps+=d.advanceFrameNoRender(1/60,scale);frames++;}const c=r.crew.snapshot();return {scale,steps,frames,rescue:d.rescueSnapshotK(),crew:{fit:c.fit,injured:c.injured,dead:c.dead,evacuated:c.evacuated},valid:d.validateOperationalStateV48Wip11B(d.exportOperationalStateV48Wip11A()),core:window.__CORE_SELFTEST_FAILURES__};}""",scale)
    rows.append(q);checks[str(scale)+'FullEvacuation']=q['steps']==9600 and q['crew']['evacuated']==330 and len(q['rescue']['rafts'])==14 and q['core']==[] and q['valid']['ok'];page.close()
 b.close()
checks['AllRaftStatesExactAcrossScales']=all(q['rescue']==rows[0]['rescue']and q['crew']==rows[0]['crew']for q in rows)
checks['PageErrorsZero']=not errors;r={'schema':'AEGIS_RESCUE_TIME_SCALES_K_1','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'fixedTickHz':60,'checks':checks,'rows':rows,'errors':errors,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':r['pass']}),flush=True)
if not r['pass']:raise SystemExit(1)
