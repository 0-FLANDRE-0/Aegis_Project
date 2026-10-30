"""Load final product bytes and check core/browser/range-table status."""
from pathlib import Path
import hashlib,json,sys
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet
build=json.loads((H/'build.json').read_text());file=R/'Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html';raw=file.read_bytes();errors=[];console=[]
with sync_playwright() as pw:
 b=launch(pw);prior=b.new_page
 def page(**kw):
  p=prior(**kw);p.on('console',lambda m:console.append({'type':m.type,'text':m.text}) if m.type=='error' else None);return p
 b.new_page=page;p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);core=p.evaluate('__CORE_SELFTEST_FAILURES__');table=p.evaluate('__ENV_D__.status()');p.close();b.close()
out={'schema':'AEGIS_ARH_MEASUREMENT_FIX_A_SMOKE_1','htmlSha256':hashlib.sha256(raw).hexdigest(),'htmlBytes':len(raw),'expectedProduct':hashlib.sha256(raw).hexdigest()==build['finalHtmlSha256'],'pageErrors':errors,'consoleErrors':console,'coreFailures':core,'rangeTable':table};out['pass']=out['expectedProduct']and not errors and not console and not core and table['recalculationRequired'];(H/'smoke.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'pageErrors':len(errors),'consoleErrors':len(console),'coreFailures':len(core),'rangeTableRecalculationRequired':table['recalculationRequired']}));raise SystemExit(0 if out['pass'] else 1)
