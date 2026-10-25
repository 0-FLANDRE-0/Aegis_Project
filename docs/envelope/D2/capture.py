from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
errors=[]
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,instrument((R/'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html').read_bytes(),(H/'capture-helper.js').read_text()+'\nwindow.__ENV_D2_EXTRA__={SAM_FUZE_SIGNAL_SPEC_A,TRACKED_PASS_POLICY_A};'),own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 data=p.evaluate('__ENV_D2_INPUT__');assert not errors,errors
 (H/'inputs.json').write_text(json.dumps(data,separators=(',',':'))+'\n');(H/'extra-models.json').write_text(json.dumps(p.evaluate('__ENV_D2_EXTRA__'),separators=(',',':'))+'\n');p.close();b.close()
print(json.dumps({'values':len(data['data']),'settings':len(data['settings']),'errors':errors}))
