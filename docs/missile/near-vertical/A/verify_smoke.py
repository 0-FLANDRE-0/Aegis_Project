from pathlib import Path
import hashlib,json,sys
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet
raw=(R/'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html').read_bytes();errors=[];console=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.on('console',lambda m:console.append({'type':m.type,'text':m.text})if m.type=='error'else None);core=p.evaluate('__CORE_SELFTEST_FAILURES__');table=p.evaluate('window.__ENV_A__?.status?.()??null');p.close();b.close()
out={'schema':'AEGIS_NEAR_VERTICAL_PATH_FIX_A_SMOKE_1','pass':not errors and not console and not core,'htmlSha256':hashlib.sha256(raw).hexdigest(),'pageErrors':errors,'consoleErrors':console,'coreFailures':core,'rangeTable':table};(H/'smoke.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'pageErrors':len(errors),'consoleErrors':len(console),'coreFailures':len(core),'rangeTable':table},indent=2));raise SystemExit(0 if out['pass']else 1)
