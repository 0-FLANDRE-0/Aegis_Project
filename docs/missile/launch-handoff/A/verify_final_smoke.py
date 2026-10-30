"""Final untouched root bytes, with console/page error capture before navigation."""
from pathlib import Path
import json,sys,hashlib
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet
file=R/'Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html';raw=file.read_bytes();errors=[];console=[]
with sync_playwright()as pw:
 b=launch(pw);prior=b.new_page
 def page(**kw):
  p=prior(**kw);p.on('console',lambda m:console.append({'type':m.type,'text':m.text})if m.type=='error'else None);return p
 b.new_page=page
 p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 core=p.evaluate('__CORE_SELFTEST_FAILURES__');table=p.evaluate('__ENV_D__.status()');p.close();b.close()
out={'htmlSha256':hashlib.sha256(raw).hexdigest(),'pageErrors':errors,'consoleErrors':console,'coreFailures':core,'rangeTable':table,'pass':not errors and not console and not core}
(H/'final-evidence/final-smoke.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'consoleErrors':len(console),'pageErrors':len(errors),'coreFailures':len(core)}));raise SystemExit(0 if out['pass']else 1)
