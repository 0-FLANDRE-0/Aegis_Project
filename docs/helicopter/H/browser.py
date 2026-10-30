"""Native predeparture UI; depart + pause atomically to avoid one racing RAF tick."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/multiship/G'))
from browser_g import launch

def load_fleet(browser,body,own='CG_52_LATE_TICONDEROGA',ally=None,enemy=None,width=1000,height=760,errors=None):
 p=browser.new_page(viewport={'width':width,'height':height});p.on('pageerror',lambda e:errors.append(str(e))if errors is not None else None)
 p.add_init_script('window.__NAVAL_SIM_SEED__=1831565813;');p.route('https://aegis.test/**',lambda r:r.fulfill(body=body,content_type='text/html'));p.goto('https://aegis.test/helo-f1?view3d=0',timeout=90000)
 p.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);c=p.locator('[data-deployment-a]:visible');c.locator('[data-ally-choice]').select_option(ally or'NONE');c.locator('[data-enemy-choice]').select_option(enemy or'NONE');c.locator('[data-target-choice]').select_option('NONE');c.locator('[data-enemy-aircraft-choice]').select_option('OFF');p.locator('#aegisShipSelect').select_option(own);p.locator('#aegisShipConfirmBtn').click()
 p.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__',timeout=120000)
 p.evaluate("()=>{document.getElementById('wip125DepartBtn').click();__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);}")
 return p
