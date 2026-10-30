from pathlib import Path
import sys,json
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/map/D'));from verify_map_helpers import *
errors=[];raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();fixture=(R/'docs/map/D/test-helper.js').read_text()+'\n'+(R/'docs/map/D/extension-fixture.js').read_text()
with sync_playwright()as pw:
 b=launch(pw)
 for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_fleet(b,instrument(raw,fixture),own=own,width=832,height=384,errors=errors);p.set_default_timeout(15000);print('load',own,p.evaluate('__MAP_E__.snapshot()'),errors,flush=True)
  p.locator('#uiEmconChipA').click();p.locator('#mapEcmJAME').click();print('JAM',p.evaluate('__MAP_E__.snapshot()'),flush=True);p.locator('#mapAllRadiationE').click();p.locator('#mapAllRadiationE').click();print('restore',p.evaluate('__MAP_E__.snapshot()'),flush=True)
  p.locator('[data-decoy-e="SRBOC"]').click();p.locator('#mapDecoyFireE').click();print('chaff',p.evaluate('__MAP_E__.snapshot()'),flush=True)
  p.evaluate('__MD_TEST__.reset()');p.wait_for_timeout(400);print('reset',errors,flush=True)
  p.locator('#uiWindowAddButtonA').click();p.locator('#armsBtn').click();print('arms',p.locator('#armsPanel').is_visible(),flush=True)
  p.screenshot(path=str(H/'evidence'/('smoke-'+own+'.png')));p.close()
 b.close()
print(json.dumps(errors));assert not errors
