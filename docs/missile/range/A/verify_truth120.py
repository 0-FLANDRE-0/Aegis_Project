"""Paired 120-second truth/RNG hash on pinned ALL4_TERM and RANGE_A."""
import argparse,hashlib,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/pip/B'));import browser_backend;browser_backend.install()
sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
base=R/'archive/v48/WIP_ALL4_TERM/Aegis_SIM_v48_WIP_ALL4_TERM.html';rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for tag,src in [('baseline',base),('candidate',a.candidate)]:
  page=load_fleet(b,src.read_bytes(),own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
  state=page.evaluate('''()=>{const d=__NAVAL_SIM_DIAG__;d.stepTicks(7200);return JSON.stringify({ship:d.exportOperationalStateV48Wip11A().ship,dynamics:d.shipDynamics(),world:__AEGIS_ENGAGEMENT_RUNTIME__.world,rng:__HARPOON_DIAG_A__.snapshot().rng},(k,v)=>v instanceof Map?[...v]:v instanceof Set?[...v]:v)}''')
  core=page.evaluate('__CORE_SELFTEST_FAILURES__');page.close();(a.out/(tag+'-truth.json')).write_text(state);rows.append({'version':tag,'htmlSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'truthSha256':hashlib.sha256(state.encode()).hexdigest(),'bytes':len(state.encode()),'ticks':7200,'seconds':120,'core':core})
 b.close()
checks={'same120sTruthHash':rows[0]['truthSha256']==rows[1]['truthSha256'],'core0':all(not r['core']for r in rows),'pageErrors0':not errors};out={'pass':all(checks.values()),'checks':checks,'records':rows,'errors':errors,'conditions':'same seeded departure, DDG, no enemy/ally/target/air; native whole simulateFixedTick 7200 times; no pause-time progression'};(a.out/'truth120.json').write_text(json.dumps(out,indent=2));print(json.dumps(out));raise SystemExit(0 if out['pass']else 1)
