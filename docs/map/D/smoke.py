from pathlib import Path
import sys,json
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/map/C'));from verify_map_helpers import *
E=H/'evidence';E.mkdir(exist_ok=True);errors=[];raw=(R/'Aegis_SIM_v48_WIP_MAP_D.html').read_bytes();fixture=(R/'docs/map/C/test-helper.js').read_text()+'\n'+(H/'extension-fixture.js').read_text()
with sync_playwright()as pw:
 b=launch(pw)
 for own in ['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']:
  p=load_fleet(b,instrument(raw,fixture),own=own,width=832,height=384,errors=errors);p.set_default_timeout(30000);p.evaluate('__MD_TEST__.reset()');p.wait_for_timeout(300);print('loaded',own,errors,flush=True)
  if own.startswith('CG'):
   select(p,'HARPOON',2);tid=p.evaluate('__MD_TEST__.surface({rangeKm:10,bearingDeg:90})');q=target(p,tid);print('HP',json.dumps(q,ensure_ascii=False)[:1400],flush=True);print('preview',p.evaluate('id=>__MD_TEST__.preview(id)',tid),flush=True);p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tick(240)');print('HP fired',p.evaluate('__MAP_D__.snapshot().queue'),p.evaluate('__MAP_D__.snapshot().log'),flush=True);p.evaluate('__MD_TEST__.reset()');p.wait_for_timeout(300)
  p.locator('[data-weapon-b="MK45"]').click();p.locator('[data-ammo-d="HE_127_SIM"]').click();p.locator('[data-gun-mode-d="SINGLE"]').click();tid=p.evaluate('__MD_TEST__.surface({rangeKm:8,bearingDeg:90})');q=target(p,tid);print('GUN',json.dumps(q,ensure_ascii=False)[:1200],flush=True);print('GUN native',p.evaluate('__MAP_D__.snapshot().guns'),flush=True);print('errors',errors,flush=True);p.screenshot(path=str(E/(own+'-smoke.png')));p.close()
 b.close()
