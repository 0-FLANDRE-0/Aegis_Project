#!/usr/bin/env python3
"""Exercise the full fixed-tick simulator under rough seas at 1/8/16/64x."""
from pathlib import Path
import shutil
import argparse, hashlib, json, os, time
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');a=p.parse_args()
src,out=Path(a.html),Path(a.out);out.mkdir(parents=True,exist_ok=True)
rows=[];states=[];errors=[];seed=0x6d2b79f5
def check(name,value,detail=None):rows.append({'name':name,'pass':bool(value),'detail':detail})
with sync_playwright()as pw:
    browser=pw.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE')or shutil.which('chromium')or None,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
    for scale in [1,8,16,64]:
        context=browser.new_context();context.add_init_script(f'window.__NAVAL_SIM_SEED__={seed}');page=context.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('https://aegis.test/**',lambda r:r.fulfill(body=src.read_bytes(),content_type='text/html'))
        page.goto('https://aegis.test/',wait_until='domcontentloaded',timeout=90000);page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000)
        page.locator('#aegisShipSelect').select_option('CG_52_LATE_TICONDEROGA');page.locator('#aegisShipConfirmBtn').click()
        page.wait_for_function('window.C55Packaging?.ready&&window.__NAVAL_SIM_DIAG__',timeout=90000)
        page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,e=window.__AEGIS_ENGAGEMENT_RUNTIME__;
          document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);d._resetShipTest();
          // Existing isolated-world fixture suppresses scenario spawning; remove
          // its missile through canonical ownership before exercising live RF.
          d.createUndetectedAsmFixture();e.world.entities.hostileMissiles.length=0;
          d.createWip13aSurfaceTargetFixture({rangeKm:14,bearingDeg:-38,speedKt:4.4});
          d.setTerrainDiagBypass(true);d.wip13a3SetManualWeather({hsM:8,tpS:10});d.setEmcon(false);d.setTimeScale(1);}''')
        begin=time.monotonic()
        state=page.evaluate('''scale=>{const d=window.__NAVAL_SIM_DIAG__,clock=d.runFramesToTicks(60,scale,3840),
          t=d.trackingTruthAudit(),fusion=d.wip13b9SurfaceFusionAudit(),spy=d.spySchedulerAudit();
          return {clock,truth:{air:t.air.filter(q=>q.alive).length,asm:t.asm.filter(q=>q.alive).length,surface:t.surface.filter(q=>q.alive).length},
            plots:spy.anonymousPlots,files:fusion.surfaceTracks.map(q=>({trackId:q.trackId,confirmed:q.confirmed,contributors:q.contributors,kinematics:q.kinematics})),
            counts:{tentative:fusion.surfaceTracks.filter(q=>!q.confirmed).length,confirmed:fusion.surfaceTracks.filter(q=>q.confirmed).length,total:d.a3TrackStates().length},
            spy:{load:spy.load,searchUsedMs:spy.searchUsedMs,dropped:spy.dropped},core:window.__CORE_SELFTEST_FAILURES__};}''',scale)
        state.update(timeScale=scale,elapsedWallS=round(time.monotonic()-begin,3));states.append(state)
        check(f'{scale}x exactly 3840 fixed ticks',state['clock']['steps']==3840 and state['clock']['simStepCounter']==3840,state['clock'])
        check(f'{scale}x real surface contact stays firm',state['truth']=={'air':0,'asm':0,'surface':1}and state['counts']['confirmed']==1,state['counts'])
        check(f'{scale}x bounded files and search served',len(state['files'])<=3 and state['counts']['total']<=4 and state['spy']['searchUsedMs']>0,state['spy'])
        check(f'{scale}x core zero',not state['core'])
        print(json.dumps({'scale':scale,'elapsedWallS':state['elapsedWallS'],'counts':state['counts'],'plots':state['plots']}),flush=True)
        context.close()
    reference={k:states[0][k]for k in ['truth','plots','files','counts','spy']}
    for state in states[1:]:
        candidate={k:state[k]for k in reference}
        check(f'{state["timeScale"]}x full sensor results match 1x exactly',candidate==reference)
    check('page errors zero',not errors,errors)
    result={'schema':'AEGIS_CG52_ROUGH_SEA_FULL_TICK_TIMESCALE_V1','source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
            'bootSeed':seed,'hsM':8,'fixedTicks':3840,'simSeconds':64,'rows':rows,'states':states,'errors':errors,
            'passed':sum(q['pass']for q in rows),'total':len(rows),'pass':all(q['pass']for q in rows)and not errors}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'total':result['total'],'pass':result['pass'],'failed':[q['name']for q in rows if not q['pass']]}));browser.close()
    if not result['pass']:raise SystemExit(1)
