"""The two original normal-release regressions, original AIR/native RF path."""
from pathlib import Path
import gzip,json,sys,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/termination/A'))
from verify_live import instrument,launch,load_fleet
versions=json.loads((H/'builds.json').read_text())['versions'];allcases=json.loads((R/'docs/missile/termination/A/cases/normal.json').read_text());cases=[allcases[152],allcases[153]]
assert all(c['weapon']=='SM6'and c['rangeKm']==240 and c['altM']==5000 and c['seed']==12001 for c in cases)
rows=[];errors=[];start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for variant in ['KAPPA','DZT','HANDOFF','ARH','VERTICAL','LATEST']:
  p=load_fleet(b,instrument((R/versions[variant]['file']).read_bytes()),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000)
  for c in cases:
   result=p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',c);rows.append({'variant':variant,'condition':c,'result':result,'htmlSha256':versions[variant]['htmlSha256']});print(variant,c['enabled'],result['reason'],result['closestM'],flush=True)
  p.close()
 b.close()
(H/'results/part2-air.json.gz').write_bytes(gzip.compress(json.dumps({'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-start},separators=(',',':')).encode(),9,mtime=0));raise SystemExit(1 if errors else 0)
