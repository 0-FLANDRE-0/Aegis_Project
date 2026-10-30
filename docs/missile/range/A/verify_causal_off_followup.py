"""Check whether the new 120s causal scenario also misses with termination disabled."""
import argparse,hashlib,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/termination/A'));from verify_live import instrument
from browser import launch,load_fleet
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[]
with sync_playwright()as pw:
 b=launch(pw);page=load_fleet(b,instrument(raw),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);c={'weapon':'SM6','rangeKm':100,'bearingDeg':45,'seed':12002,'enabled':False};page.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c);ticks=900;page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');q=page.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
 while not q.get('launched')and ticks<3600:
  page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(300)');ticks+=300;q=page.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
 assert q.get('launched'),q
 samples=[]
 for i in range(250):
  page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(120)');s=page.evaluate('__TERM_LIVE_TEST__.observe()');samples.append(s)
  if s['dead']:break
 after=page.evaluate('__TERM_LIVE_TEST__.afterAction()');core=page.evaluate('__CORE_SELFTEST_FAILURES__');b.close()
r={'htmlSha256':hashlib.sha256(raw).hexdigest(),'case':c,'preLaunchTicks':ticks,'launch':q,'afterAction':after,'samples':samples,'core':core,'errors':errors,'counterfactualMiss':after['targetAlive'],'completed':after['missile']['dead']and not core and not errors,'scope':'single extra natural-sensor/target-AI scenario from the causal hash test; not a change to normal regression criteria'};(a.out/'causal-off-followup.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:r[k]for k in ['counterfactualMiss','completed','afterAction','errors']}));raise SystemExit(0 if r['completed']else 1)
