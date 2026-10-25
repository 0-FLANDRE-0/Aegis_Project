from pathlib import Path
import sys,json,hashlib
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet
rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for name,file in [('DZT',(R/'archive/v48/WIP_FUZE_ZEM_A/Aegis_SIM_v48_WIP_FUZE_ZEM_A.html')),('HANDOFF',Path(json.loads((H/'build.json').read_text())['file']))]:
  raw=file.read_bytes();p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);q={'variant':name,'htmlSha256':hashlib.sha256(raw).hexdigest(),'coreFailures':p.evaluate('__CORE_SELFTEST_FAILURES__'),'rangeTable':p.evaluate('__ENV_D__.status()')};rows.append(q);p.close()
 b.close()
checks={'bothCore0':all(not q['coreFailures']for q in rows),'pageErrors0':not errors,'tableStillHistorical':all(q['rangeTable']['recalculationRequired']for q in rows)};o={'pass':all(checks.values()),'checks':checks,'rows':rows,'errors':errors};(H/'final-evidence/core.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({'pass':o['pass'],'checks':checks}));raise SystemExit(0 if o['pass']else 1)
