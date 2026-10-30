from pathlib import Path
import sys,json,base64
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/map/B'));from verify_map_helpers import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_MAP_C.html').read_bytes()
with sync_playwright()as pw:
 b=launch(pw);errors=[]
 for w,h in [(1400,900),(832,384),(384,832)]:
  p=load_fleet(b,instrument(raw,(R/'docs/map/B/test-helper.js').read_text()),errors=errors,width=w,height=h);p.evaluate('__MB_TEST__.reset()');p.wait_for_timeout(500)
  print(w,'startup',p.evaluate('()=>({view:__VIEWPORT_A__.snapshot().viewport.twoD,bar:document.getElementById("uiStatusBarA").getBoundingClientRect().toJSON(),clock:document.getElementById("mapTimeBlockC").getBoundingClientRect().toJSON(),slot:document.getElementById("mapFireSlotC").getBoundingClientRect().toJSON(),emcon:document.getElementById("uiEmconChipA").getBoundingClientRect().toJSON(),overflow:document.documentElement.scrollWidth>innerWidth})'),flush=True)
  p.locator('[data-weapon-b="SM6"]').click();p.locator('[data-salvo-b="2"]').click();tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');p.wait_for_timeout(150);o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',tid);a=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o);p.mouse.click(a['x'],a['y']);p.wait_for_timeout(350);print(w,'selected',p.evaluate('()=>({b:__MAP_B__.snapshot(),c:__MAP_C__.snapshot(),tag:document.getElementById("mapEngagementB").innerText,fire:document.getElementById("mapFireB").outerHTML})'),flush=True)
  c=p.context.new_cdp_session(p);(H/'evidence'/('smoke-'+str(w)+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']));c.detach();p.close()
 print('errors',errors,flush=True);b.close();assert not errors
