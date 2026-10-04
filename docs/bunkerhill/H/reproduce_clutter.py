from pathlib import Path
import shutil
import json, os, sys, time, hashlib
from playwright.sync_api import sync_playwright

src = Path(sys.argv[1])
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
seed = int(sys.argv[3], 0) if len(sys.argv)>3 else 0x6d2b79f5
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE')or shutil.which('chromium')or None,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
    page=b.new_page(viewport={'width':648,'height':1280});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script(f'window.__NAVAL_SIM_SEED__={seed}')
    page.route('https://aegis.test/**',lambda r:r.fulfill(body=src.read_bytes(),content_type='text/html'))
    page.goto('https://aegis.test/candidate',wait_until='domcontentloaded',timeout=90000)
    page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000)
    page.locator('#aegisShipSelect').select_option('CG_52_LATE_TICONDEROGA');page.locator('#aegisShipConfirmBtn').click()
    page.wait_for_function('window.C55Packaging?.ready&&window.__NAVAL_SIM_DIAG__',timeout=90000)
    page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__;document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);d.setEmcon(false);d.profilerEnableV48Wip11A?.(true);return Object.keys(d);}''')
    if len(sys.argv)>4:
        weather=page.evaluate('hs=>window.__NAVAL_SIM_DIAG__.wip13a3SetManualWeather({hsM:hs,tpS:10})',float(sys.argv[4]))
        print(json.dumps({'weather':weather}),flush=True)
    snapshot='''()=>{const d=window.__NAVAL_SIM_DIAG__,truth=d.trackingTruthAudit(),s=d.spySchedulerAudit(),t=d.a3TrackStates(),fusion=d.wip13b9SurfaceFusionAudit();
      return {truthCounts:{air:truth.air.filter(q=>q.alive).length,asm:truth.asm.filter(q=>q.alive).length,surface:truth.surface.filter(q=>q.alive).length},
        truth,tracks:t.length,confirmedSurface:fusion.surfaceTracks.filter(q=>q.confirmed).length,tentativeSurface:fusion.surfaceTracks.filter(q=>!q.confirmed).length,states:t,
        surfaceTracks:fusion.surfaceTracks.length,spy:{load:s.load,priorityUsedMs:s.priorityUsedMs,searchUsedMs:s.searchUsedMs,candidates:s.candidates,dropped:s.dropped,anonymous:s.anonymousPlots},core:window.__CORE_SELFTEST_FAILURES__};}'''
    samples=[{'simSeconds':0,**page.evaluate(snapshot)}]
    for i in range(1,(int(sys.argv[5])if len(sys.argv)>5 else 6)+1):
        start=time.monotonic()
        page.evaluate('window.__NAVAL_SIM_DIAG__.wip13b9StepSurfaceSensors(1800)')
        sample={'simSeconds':i*30,'elapsedWallS':time.monotonic()-start,**page.evaluate(snapshot)};samples.append(sample)
        print(json.dumps({k:v for k,v in sample.items()if k not in ['truth','states']}),flush=True)
        (out/'reproduction.json').write_text(json.dumps({'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'seed':seed,'samples':samples,'errors':errors},indent=2))
    page.screenshot(path=str(out/'cic.png'))
    (out/'reproduction.json').write_text(json.dumps({'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'seed':seed,'samples':samples,'errors':errors},indent=2))
    b.close()
