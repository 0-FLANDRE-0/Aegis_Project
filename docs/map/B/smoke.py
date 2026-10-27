import sys,json
from pathlib import Path
sys.path.insert(0,'docs/missile/fuze-zem/A');from browser_tools import launch,load_fleet
from playwright.sync_api import sync_playwright
with sync_playwright()as pw:
 b=launch(pw);err=[];p=load_fleet(b,Path('Aegis_SIM_v48_WIP_MAP_B.html').read_bytes(),errors=err,width=1400,height=900)
 p.evaluate('()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k);document.getElementById("emconBtn").click()}');p.wait_for_timeout(100);p.locator('[data-weapon-b="SM2"]').click();p.locator('[data-salvo-b="2"]').click()
 tid=p.evaluate('__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:10,bearingDeg:0,altM:1000,speedMps:0})');p.wait_for_timeout(200);o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',tid);pt=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o);p.mouse.click(pt['x'],pt['y']);p.wait_for_timeout(300);print('target',p.evaluate('__MAP_B__.snapshot()'),flush=True)
 if p.locator('#mapFireB').is_enabled():
  p.locator('#mapFireB').click();print('fire',p.evaluate('__MAP_B__.snapshot()'),flush=True)
 print('errors',err,flush=True);b.close()
