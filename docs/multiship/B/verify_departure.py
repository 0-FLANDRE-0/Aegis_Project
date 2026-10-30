"""Initial enemy selection must remain valid before physical deployment exists."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];errors=[]
 with sync_playwright()as pw:
  browser=launch(pw)
  for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   for enemy in ['NONE','DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
    page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5;');page.route('https://aegis.test/**',lambda r:r.fulfill(body=a.html.read_bytes(),content_type='text/html'));page.goto('https://aegis.test/departure?view3d=0',timeout=90000);page.wait_for_selector('#aegisShipSelect',timeout=90000);page.locator('#aegisShipSelect').select_option(own);page.locator('[data-enemy-choice]').select_option(enemy);page.locator('[data-target-choice]').select_option('NONE');page.locator('#aegisShipConfirmBtn').click();page.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__',timeout=120000)
    result=page.evaluate('''enemy=>{const d=window.__NAVAL_SIM_DIAG__,pending=d.exportOperationalStateV48Wip11A(),validation=d.validateOperationalStateV48Wip11A(pending),before=d.physicalFleetSnapshotB(),core=[...window.__CORE_SELFTEST_FAILURES__];document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);const active=d.exportOperationalStateV48Wip11A(),checks={initialCoreZero:core.length===0,preSailSaveValid:validation.ok,preSailStateExplicit:pending.fleet.deploymentState===(enemy==='NONE'?'NONE':'PENDING'),noPrematurePhysicalExecution:before.simulated===1&&pending.fleet.ships.length===0,departureCreatesExpectedShips:d.physicalFleetSnapshotB().simulated===(enemy==='NONE'?1:2),activeStateExplicit:active.fleet.deploymentState===(enemy==='NONE'?'NONE':'ACTIVE'),activeSaveValid:d.validateOperationalStateV48Wip11A(active).ok,noFault:!window.__WIP125_DIAG__.wip150RuntimeFault()};return {checks,core,pendingFleet:pending.fleet,validation,activeFleet:active.fleet,pass:Object.values(checks).every(Boolean)};}''',enemy);result.update(own=own,enemy=enemy);rows.append(result);page.close();print(json.dumps({'own':own,'enemy':enemy,'checks':result['checks']}),flush=True)
  browser.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(r['pass']for r in rows)};(a.out/'departure.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
