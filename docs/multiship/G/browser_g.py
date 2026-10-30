"""Shared final-artifact browser setup, native predeparture controls."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch
def load_fleet(browser,body,own='CG_52_LATE_TICONDEROGA',ally='DDG_119_LATE_FLIGHT_IIA',enemy='CG_52_LATE_TICONDEROGA',width=1000,height=760,webgl=False,errors=None,touch=False):
 p=browser.new_page(viewport={'width':width,'height':height},has_touch=touch);p.on('pageerror',lambda e:errors.append(str(e))if errors is not None else None)
 p.add_init_script('window.__NAVAL_SIM_SEED__=1831565813;');p.route('https://aegis.test/**',lambda r:r.fulfill(body=body,content_type='text/html'));p.goto('https://aegis.test/network?view3d='+('1'if webgl else'0'),timeout=90000)
 p.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);c=p.locator('[data-deployment-a]:visible');c.locator('[data-ally-choice]').select_option(ally or'NONE');c.locator('[data-enemy-choice]').select_option(enemy or'NONE');c.locator('[data-target-choice]').select_option('NONE');c.locator('[data-enemy-aircraft-choice]').select_option('OFF');p.locator('#aegisShipSelect').select_option(own);p.locator('#aegisShipConfirmBtn').click()
 p.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__',timeout=120000);p.locator('#wip125DepartBtn').click();p.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');return p
