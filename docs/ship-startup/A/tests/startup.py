#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('baseline');p.add_argument('out');a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
rows=[];errors=[];seed=0x6d2b79f5
def check(name,value,detail=None): rows.append({'name':name,'pass':bool(value),'detail':detail})
with sync_playwright() as pw:
    launch={'headless':True,'args':['--no-sandbox','--disable-dev-shm-usage','--disable-gpu']}
    if os.environ.get('AEGIS_CHROMIUM_EXECUTABLE'):launch['executable_path']=os.environ['AEGIS_CHROMIUM_EXECUTABLE']
    browser=pw.chromium.launch(**launch)
    def load(path,phase):
        page=browser.new_page(viewport={'width':1440,'height':1000})
        page.on('pageerror',lambda e:errors.append({'phase':phase,'error':str(e)}))
        page.evaluate('seed=>window.__NAVAL_SIM_SEED__=seed',seed)
        page.set_content(Path(path).read_text(),wait_until='domcontentloaded',timeout=90000)
        return page
    baseline=load(a.baseline,'baseline')
    baseline.wait_for_function('window.C55Packaging?.ready&&window.__NAVAL_SIM_DIAG__',timeout=90000)
    old=baseline.evaluate('''() => {const d=window.__NAVAL_SIM_DIAG__;return {snapshot:d.exportOperationalStateV48Wip11A(),inventory:window.__WIP125_DIAG__.snapshot()};}''')
    (out/'baseline-operational.json').write_text(json.dumps(old['snapshot'],indent=2))
    baseline.close()

    page=load(a.html,'candidate')
    page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000)
    initial=page.evaluate('''() => ({state:window.__AEGIS_SHIP_STARTUP__.snapshot(),catalog:window.__AEGIS_SHIP_STARTUP__.catalog(),noRuntime:!window.__AEGIS_ACTIVE_SHIP_RUNTIME__&&!window.__AEGIS_ENGAGEMENT_RUNTIME__,noDiag:!window.__NAVAL_SIM_DIAG__,ready:!!window.C55Packaging.ready})''')
    check('selection precedes runtime and simulation',initial['state']['phase']=='SELECTING' and initial['state']['initializationCount']==0 and initial['noRuntime'] and initial['noDiag'] and not initial['ready'],initial)
    check('catalog exposes only registered DDG-119',len(initial['catalog'])==1 and initial['catalog'][0]['id']=='DDG_119_LATE_FLIGHT_IIA')
    rejected=page.evaluate('''() => {const api=window.__AEGIS_SHIP_STARTUP__,before=JSON.stringify(api.snapshot()),results=[null,{},'UNKNOWN','__proto__','constructor'].map(id=>api.select(id));const catalog=api.catalog(),state=api.snapshot();catalog[0].id='BAD';state.phase='DEPARTED';return {results,unchanged:before===JSON.stringify(api.snapshot()),detached:api.catalog()[0].id!=='BAD'};}''')
    check('unknown and prototype selections rejected without mutation',all(q is False for q in rejected['results']) and rejected['unchanged'] and rejected['detached'],rejected)
    page.screenshot(path=str(out/'selection.png'))
    page.locator('#aegisShipConfirmBtn').click()
    page.wait_for_function('window.C55Packaging?.ready||window.C55Packaging?.error',timeout=90000)
    assert page.evaluate('!!window.C55Packaging.ready'),page.evaluate('window.C55Packaging')
    ready=page.evaluate('''() => {const d=window.__NAVAL_SIM_DIAG__,r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__;window.__STARTUP_TEST_REFS__={r,nav:r.navigation,vls:r.weapons.vls,gun:r.weapons.mainGun};return {state:d.shipStartupState(),core:window.__CORE_SELFTEST_FAILURES__,owner:d.runtimeOwnershipAuditV48Wip11A(),single:w.ships.size===1&&w.ships.get(r.entityId)===r,inventory:window.__WIP125_DIAG__.snapshot(),clock:d.ciwsB1Closure.setPaused(false).simStepCounter,allSubsystems:['mass','dynamics','interior','crew','environment','damage'].every(k=>!!r[k])};}''')
    check('exactly one canonical ship initialized before departure',ready['single'] and ready['state']['phase']=='PREPARING' and ready['state']['initializationCount']==1 and ready['state']['entityId']=='SHIP_DDG119_OWN',ready['state'])
    check('core and subsystem ownership preserved',ready['core']==[] and ready['owner']['pass'] and ready['allSubsystems'],{'core':ready['core'],'owner':ready['owner']})
    check('DDG-119 default VLS identical to WIP16B',ready['inventory']==old['inventory'],ready['inventory']['counts'])
    page.wait_for_timeout(500)
    clock=page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false).simStepCounter')
    check('equipment preparation holds simulation clock',clock==ready['clock'],{'before':ready['clock'],'after':clock})
    isolation=page.evaluate('window.__NAVAL_SIM_DIAG__.runShipStartupIsolationAudit()')
    check('independent creation and generic identity/inventory',isolation['pass'],isolation)
    page.screenshot(path=str(out/'equipment.png'))
    check('pre-departure equipment edit allowed',page.evaluate("window.__WIP125_DIAG__.setCell('fwd',0,'SM6')"))
    committed=page.evaluate('window.__WIP125_DIAG__.snapshot().loadout')
    page.locator('#wip125DepartBtn').click()
    page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
    locked=page.evaluate('''() => {const api=window.__AEGIS_SHIP_STARTUP__,d=window.__NAVAL_SIM_DIAG__,before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B()),results=['DDG_119_LATE_FLIGHT_IIA','UNKNOWN'].map(id=>api.select(id));return {results,unchanged:before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B()),phase:api.snapshot().phase,departureAgain:window.__WIP125_DIAG__.confirmDeparture(),editAfterDeparture:window.__WIP125_DIAG__.setCell('fwd',0,'SM2')};}''')
    check('departure locks profile, loadout and duplicate departure',locked['phase']=='DEPARTED' and locked['unchanged'] and all(q is False for q in locked['results']) and locked['departureAgain'] is False and locked['editAfterDeparture'] is False,locked)
    page.evaluate("window.__WIP125_DIAG__.consume('SM6',1);window.__AEGIS_ACTIVE_SHIP_RUNTIME__.navigation.heading=.25;window.__AEGIS_ACTIVE_SHIP_RUNTIME__.weapons.closeIn[0].ammo=0")
    reset=page.evaluate('''() => {const d=window.__NAVAL_SIM_DIAG__,q=window.__STARTUP_TEST_REFS__;d.resetEntireSessionV48Wip11A();const r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__;return {refs:r===q.r&&r.navigation===q.nav&&r.weapons.vls===q.vls&&r.weapons.mainGun===q.gun,heading:r.navigation.heading,ammo:r.weapons.closeIn.map(m=>m.ammo),loadout:window.__WIP125_DIAG__.snapshot().loadout,state:d.shipStartupState(),owner:d.runtimeOwnershipAuditV48Wip11A()};}''')
    check('restart retains selected ship and canonical references',reset['refs'] and reset['owner']['pass'] and reset['state']['initializationCount']==1 and reset['state']['phase']=='DEPARTED',reset['state'])
    check('restart restores profile defaults and committed loadout',reset['heading']==-1.5707963267948966 and reset['ammo']==[1550,11] and reset['loadout']==committed,{'heading':reset['heading'],'ammo':reset['ammo']})
    imported=page.evaluate('''snap => {const d=window.__NAVAL_SIM_DIAG__,validation=d.validateOperationalStateV48Wip11B(snap);if(!validation.ok)return {validation};const result=d.importOperationalStateV48Wip11B(snap),back=d.exportOperationalStateV48Wip11A();return {validation,schema:back.schema,version:back.schemaVersion,identity:back.profileId===snap.profileId&&back.profileRevision===snap.profileRevision&&back.shipId===snap.shipId,vls:JSON.stringify(back.ship.inventory.vls)===JSON.stringify(snap.ship.inventory.vls),nav:JSON.stringify(back.ship.navigation)===JSON.stringify(snap.ship.navigation),closeIn:JSON.stringify(back.ship.inventory.closeIn)===JSON.stringify(snap.ship.inventory.closeIn),owner:d.runtimeOwnershipAuditV48Wip11A()};}''',old['snapshot'])
    check('WIP16B operational save imports with identity and inventory intact',imported.get('validation',{}).get('ok') and all(imported.get(k) for k in ['identity','vls','nav','closeIn']) and imported['owner']['pass'],imported)
    bad=page.evaluate('''() => {const d=window.__NAVAL_SIM_DIAG__,s=d.exportOperationalStateV48Wip11A(),before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());s.profileRevision+='BAD';let rejected=false;try{d.importOperationalStateV48Wip11B(s);}catch(e){rejected=true;}return {rejected,unchanged:before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B()),audit:d.operationalImportSafetyAuditV48Wip11B()};}''')
    check('incompatible save rejected without authoritative mutation',bad['rejected'] and bad['unchanged'],bad)
    check('page errors zero',errors==[],errors)
    result={'schema':'AEGIS_SHIP_STARTUP_LIFECYCLE_CHECK_V1','bootSeed':seed,'rows':rows,'passed':sum(r['pass'] for r in rows),'total':len(rows),'pass':all(r['pass'] for r in rows)}
    (out/'startup.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({'passed':result['passed'],'total':result['total'],'pass':result['pass'],'failed':[r for r in rows if not r['pass']]},ensure_ascii=False,indent=2))
    browser.close()
    if not result['pass']:raise SystemExit(1)

