"""Real startup/loadout controls: OFF survives departure, respawn, reset, new sea and import."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw)
  for width,height,own,on in [(1000,760,'DDG_119_LATE_FLIGHT_IIA',False),(393,852,'CG_52_LATE_TICONDEROGA',False),(1000,760,'CG_52_LATE_TICONDEROGA',True)]:
   page=b.new_page(viewport={'width':width,'height':height});page.on('pageerror',lambda e:errors.append(str(e)));page.add_init_script('window.__NAVAL_SIM_SEED__=1831565813;');page.route('https://aegis.test/**',lambda r:r.fulfill(body=a.html.read_bytes(),content_type='text/html'));page.goto('https://aegis.test/candidate?view3d=0',wait_until='load',timeout=90000);page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000)
   choice=page.locator('[data-deployment-a]:visible [data-enemy-aircraft-choice]');default_on=choice.input_value()=='ON';choice.select_option('ON'if on else'OFF');page.locator('#aegisShipSelect').select_option(own);page.screenshot(path=str(a.out/(own+'-'+str(on)+'-startup.png')));page.locator('#aegisShipConfirmBtn').click();page.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__',timeout=120000)
   checks={'defaultOn':default_on,'loadoutSync':page.locator('[data-deployment-a]:visible [data-enemy-aircraft-choice]').input_value()==('ON'if on else'OFF')};page.screenshot(path=str(a.out/(own+'-'+str(on)+'-loadout.png')));page.locator('#wip125DepartBtn').click();page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
   q=page.evaluate('''on=>{const d=window.__NAVAL_SIM_DIAG__,checks={},counts=()=>window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.aircraft.length,cfg=d.exportOperationalStateV48Wip11A().deployment;checks.committed=cfg.enemyAircraftEnabled===on;const initial=counts();checks.initialPolicy=on?initial>0:initial===0;d.runFramesToTicks(60,16,1020);checks.respawnPolicy=on?counts()>0:counts()===0;
    const saved=d.exportOperationalStateV48Wip11A(),before=JSON.stringify(saved),bad=structuredClone(saved);bad.deployment.enemyAircraftEnabled='OFF';let rejected=false;try{d.importOperationalStateV48Wip11A(bad);}catch(e){rejected=true;}checks.badBooleanAtomic=rejected&&JSON.stringify(d.exportOperationalStateV48Wip11A())===before;
    const missing=structuredClone(saved);delete missing.deployment.enemyAircraftEnabled;checks.newSchemaMissingRejected=!d.validateOperationalStateV48Wip11A(missing).ok;
    const legacy=structuredClone(saved);legacy.deployment.schema='AEGIS_DEPLOYMENT_MULTI_SHIP_A_1';delete legacy.deployment.enemyAircraftEnabled;for(const key of ['allyProfileId','placementSeed','allyEmcon','enemyEmcon'])delete legacy.deployment[key];checks.legacyValidated=d.validateOperationalStateV48Wip11A(legacy).ok;
    checks.lockedAfterDeparture=window.__AEGIS_DEPLOYMENT_A__.setDraft({...cfg,enemyAircraftEnabled:!on}).errors.includes('DEPLOYMENT_LOCKED_AFTER_DEPARTURE');
    document.getElementById('newSeaBtn').click();checks.newSeaPolicy=on?counts()>0:counts()===0;d.importOperationalStateV48Wip11A(saved);checks.savedPolicyRestored=d.exportOperationalStateV48Wip11A().deployment.enemyAircraftEnabled===on;d.importOperationalStateV48Wip11A(legacy);checks.legacyRestoresOn=d.exportOperationalStateV48Wip11A().deployment.enemyAircraftEnabled===true;d.importOperationalStateV48Wip11A(saved);document.getElementById('resetBtn').click();checks.resetPolicy=on?true:counts()===0;
    checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.faultZero=!window.__WIP125_DIAG__.wip150RuntimeFault();return {checks,initial,after:counts(),config:d.exportOperationalStateV48Wip11A().deployment};}''',on)
   # Exercise the delayed reset callback without advancing combat through a renderer.
   page.wait_for_timeout(1200);q['checks']['delayedResetSpawnPolicy']=on or page.evaluate('window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.aircraft.length===0')
   q['checks'].update(checks);q.update(width=width,height=height,own=own,enabled=on);q['pass']=all(q['checks'].values());rows.append(q);page.close();print(json.dumps({'own':own,'enabled':on,'viewport':[width,height],'failed':[k for k,v in q['checks'].items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':not errors and all(q['pass']for q in rows)};(a.out/'departure.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
