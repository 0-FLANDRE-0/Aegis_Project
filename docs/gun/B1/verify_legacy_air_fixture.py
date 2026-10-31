from pathlib import Path
import sys,json
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
from playwright.sync_api import sync_playwright
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();fixture=(R/'docs/map/E/test-helper.js').read_text()+'\n'+(R/'docs/map/D/extension-fixture.js').read_text();records=[]
with sync_playwright()as pw:
 b=launch(pw)
 for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
  p=load_fleet(b,instrument(raw,fixture),own=own);p.set_default_timeout(180000);p.evaluate('__GUN_B1__.setAuto(false);__MD_TEST__.reset();document.querySelector("[data-weapon-b=MK45]").click();document.querySelector("[data-gun-mode-d=SINGLE]").click()');id=p.evaluate('__MB_TEST__.add({rangeKm:10,bearingDeg:30})');p.evaluate('id=>__MAP_B__.pickObject(__MAP_A__.objects().find(o=>o.key==="TRACK:"+id))',id);p.evaluate('__MAP_B__.refresh(true)');q=p.evaluate('__MAP_B__.snapshot().model');records.append({'ship':own,'model':q});print(own,json.dumps(q),flush=True);p.close()
 b.close()
(H/'evidence/legacy-air-probe.json').write_text(json.dumps(records,indent=2)+'\n')
