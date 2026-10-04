#!/usr/bin/env python3
"""Real-browser rough-sea, real-contact and selected-source 2D regressions."""
from pathlib import Path
import shutil
import argparse, base64, hashlib, json, os, time
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('baseline');p.add_argument('out');a=p.parse_args()
src,baseline=Path(a.html),Path(a.baseline);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
rows=[];details={};errors=[];seed=0x6d2b79f5
def check(name,value,detail=None):rows.append({'name':name,'pass':bool(value),'detail':detail})
def save():
    result={'schema':'AEGIS_BUNKERHILL_CLUTTER_AND_2D_F_V1','source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
            'bootSeed':seed,'rows':rows,'details':details,'errors':errors,'passed':sum(r['pass']for r in rows),
            'total':len(rows),'pass':all(r['pass']for r in rows)and not errors}
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE')or shutil.which('chromium')or None,
        headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
    context=None
    def fresh(path,ship='CG_52_LATE_TICONDEROGA'):
        global context
        if context:context.close()
        context=b.new_context(viewport={'width':648,'height':1280});page=context.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.add_init_script(f'window.__NAVAL_SIM_SEED__={seed}')
        # Observe the actual drawing transform; do not infer orientation from a
        # label or alter drawing/physics state. Source image +X points to bow.
        page.add_init_script('''(()=>{const orig=CanvasRenderingContext2D.prototype.drawImage;window.__INDICATOR_TRANSFORMS__={};CanvasRenderingContext2D.prototype.drawImage=function(img,...args){if(this.canvas.id==='shipDetailCanvas'&&img instanceof HTMLImageElement&&img.naturalWidth===1730){const m=this.getTransform();window.__INDICATOR_TRANSFORMS__[img.naturalHeight]={a:m.a,d:m.d,width:img.naturalWidth,height:img.naturalHeight,bowPixelX:m.a*img.naturalWidth+m.e,sternPixelX:m.e};}return orig.call(this,img,...args)};})();''')
        page.route('https://aegis.test/**',lambda r:r.fulfill(body=path.read_bytes(),content_type='text/html'))
        page.goto('https://aegis.test/candidate',wait_until='domcontentloaded',timeout=90000)
        page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000)
        page.locator('#aegisShipSelect').select_option(ship);page.locator('#aegisShipConfirmBtn').click()
        page.wait_for_function('window.C55Packaging?.ready&&window.__NAVAL_SIM_DIAG__',timeout=90000)
        page.evaluate("()=>{document.getElementById('wip125DepartBtn').click();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);window.__NAVAL_SIM_DIAG__.setEmcon(false);}")
        check(path.name+' / '+ship+' core zero',page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[])
        return page
    # Empty physical contact world, real sea/terrain field, normal RF receivers.
    # Clearing is fixture-only through canonical world ownership, never a live
    # processor truth-ID or source-kind filter.
    histories=[]
    for hs,seconds in [(0,600),(6,120),(7,120),(8,600)]:
        page=fresh(src)
        page.evaluate('''hs=>{const d=window.__NAVAL_SIM_DIAG__,e=window.__AEGIS_ENGAGEMENT_RUNTIME__;d._resetShipTest();
            e.world.entities.aircraft.length=0;e.world.entities.hostileMissiles.length=0;
            d.setTerrainDiagBypass(false);d.wip13a3SetManualWeather({hsM:hs,tpS:10});d.setEmcon(false);}''',hs)
        history=[]
        for end in range(30,seconds+1,30):
            wall=time.monotonic()
            sample=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__;d.wip13b9StepSurfaceSensors(1800);
              const t=d.trackingTruthAudit(),f=d.wip13b9SurfaceFusionAudit(),s=d.spySchedulerAudit();
              return {truth:{air:t.air.filter(q=>q.alive).length,asm:t.asm.filter(q=>q.alive).length,surface:t.surface.filter(q=>q.alive).length},
                tracks:d.a3TrackStates().length,surfaceTracks:f.surfaceTracks.length,firm:f.surfaceTracks.filter(q=>q.confirmed).length,
                spy:{load:s.load,candidates:s.candidates,dropped:s.dropped,priorityUsedMs:s.priorityUsedMs,searchUsedMs:s.searchUsedMs}};}''')
            sample.update(simSeconds=end,elapsedWallS=round(time.monotonic()-wall,3));history.append(sample)
            if end%120==0:print(json.dumps({'stage':'empty-world','hsM':hs,**sample}),flush=True)
        histories.append({'hsM':hs,'seconds':seconds,'samples':history})
        check(f'Hs {hs}m empty contact truth',all(sum(r['truth'].values())==0 for r in history))
        check(f'Hs {hs}m no false surface files',all(r['surfaceTracks']==0 for r in history),{'peak':max(r['surfaceTracks']for r in history)})
        check(f'Hs {hs}m background track count bounded',max(r['tracks']for r in history)<=2,{'peak':max(r['tracks']for r in history)})
        check(f'Hs {hs}m SPY search remains serviced',sum(r['spy']['searchUsedMs']for r in history)>0)
        details['emptyWorld']=histories;save()
    # An independent stationary/moving physical ship must still be observable.
    physical=[]
    for speed in [0,4.4]:
        page=fresh(src)
        page.evaluate('''speed=>{const d=window.__NAVAL_SIM_DIAG__,e=window.__AEGIS_ENGAGEMENT_RUNTIME__;d._resetShipTest();e.world.entities.aircraft.length=0;
          d.setTerrainDiagBypass(true);d.createWip13aSurfaceTargetFixture({rangeKm:14,bearingDeg:-38,speedKt:speed});
          d.wip13a3SetManualWeather({hsM:8,tpS:10});d.setEmcon(false);}''',speed)
        states=[]
        for end in range(30,181,30):
            q=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__;d.wip13b9StepSurfaceSensors(1800);return d.wip13b9SurfaceFusionAudit();}''')
            states.append({'simSeconds':end,'audit':q})
        final=states[-1]['audit'];files=final['surfaceTracks'];contributors=set(k for q in files for k in q['contributors'])
        check(f'{speed} kt rough-sea physical contact remains firm',any(q['confirmed']for q in files),{'files':len(files)})
        check(f'{speed} kt all three surface sensors contribute',{'SPY1DV','SPQ9B','BRIDGEMASTER_E'}<=contributors,sorted(contributors))
        check(f'{speed} kt no phantom surface accumulation',max(len(q['audit']['surfaceTracks'])for q in states)<=3)
        check(f'{speed} kt anonymous measured tracks',final['anonymousContributors']and all(not q['truthRefExposed']for q in files))
        physical.append({'speedKt':speed,'hsM':8,'samples':states});details['physicalContact']=physical;save()
        print(json.dumps({'stage':'physical-contact','speedKt':speed,'files':len(files),'contributors':sorted(contributors)}),flush=True)
    # Actual 2D canvas before/after. D snapshot also verifies save compatibility.
    page=fresh(baseline)
    old_save=page.evaluate('window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()')
    # Compare the full inventory against the D -> D round-trip contract. D's
    # existing import normalizes inactive Mk36 reload.startedStep (-1 -> 0).
    # Comparing with this reference verifies that F introduces no new changes.
    d_roundtrip=page.evaluate('s=>{const d=window.__NAVAL_SIM_DIAG__;d.importOperationalStateV48Wip11B(s);return d.exportOperationalStateV48Wip11A();}',old_save)
    page.locator('#shipDetailBtn').click();page.wait_for_timeout(300)
    old_cg=page.locator('#shipDetailCanvas').evaluate('(c)=>c.toDataURL()')
    (out/'cg52-before-D.png').write_bytes(base64.b64decode(old_cg.split(',',1)[1]))
    page=fresh(src)
    imported=page.evaluate('s=>{const d=window.__NAVAL_SIM_DIAG__,v=d.validateOperationalStateV48Wip11B(s);if(!v.ok)return v;d.importOperationalStateV48Wip11B(s);return {ok:true,profile:d.exportOperationalStateV48Wip11A().profileId,inventory:d.exportOperationalStateV48Wip11A().ship.inventory};}',old_save)
    check('D CG operational save remains compatible',imported['ok']and imported['profile']==old_save['profileId']and imported['inventory']==d_roundtrip['ship']['inventory'],{'sameInventoryAsDToDRoundtrip':imported.get('inventory')==d_roundtrip['ship']['inventory']})
    page.locator('#shipDetailBtn').click()
    page.wait_for_function('window.__NAVAL_SIM_DIAG__.bunkerIndicatorAudit().imagesReady.every(q=>q.ready)',timeout=30000)
    page.wait_for_timeout(200)
    audit=page.evaluate('window.__NAVAL_SIM_DIAG__.bunkerIndicatorAudit()');details['indicatorAudit']=audit
    check('CG indicator uses full original source identity',audit['pass']and audit['sourceTriangles']==740819,audit['checks'])
    check('CG indicator has both guns, both Phalanx, four SPG',len(audit['overlays']['guns'])==2 and len(audit['overlays']['closeIn'])==2 and len(audit['overlays']['illuminators'])==4)
    pristine=page.locator('#shipDetailCanvas').evaluate('(c)=>c.toDataURL()')
    check('CG indicator differs from old DDG background',pristine!=old_cg)
    transforms=page.evaluate('window.__INDICATOR_TRANSFORMS__');details['drawTransforms']=transforms
    for view,height in [('top','208'),('side','555')]:
        q=transforms.get(height,{})
        check(f'CG {view} actual rendered bow faces left',q.get('a',0)<0 and q.get('d',0)>0 and q.get('bowPixelX',1)>=0 and q.get('bowPixelX',1)<q.get('sternPixelX',0),q)
    (out/'cg52-after-F.png').write_bytes(base64.b64decode(pristine.split(',',1)[1]));page.screenshot(path=str(out/'cg52-mobile-ship-panel.png'))
    before=page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B())')
    for _ in range(6):page.locator('#shipDetailBtn').click();page.locator('#shipDetailBtn').click()
    page.wait_for_timeout(350)
    after=page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B())')
    check('2D drawing/toggle does not mutate canonical state',before==after)
    page.evaluate("window.__NAVAL_SIM_DIAG__.runV48Wip03StructuralProbe({hits:2,label:'Kh-32',xM:12,zM:-3.5,side:'STARBOARD'})")
    page.wait_for_timeout(300)
    scar=page.evaluate('window.__WIP12E_REV5_2D_SCAR_AUDIT__');damaged=page.locator('#shipDetailCanvas').evaluate('(c)=>c.toDataURL()')
    check('real CG damage scars appear in top and side',scar['sourceScars']>0 and scar['topDrawn']==scar['sourceScars']and scar['sideDrawn']==scar['sourceScars']and damaged!=pristine,scar)
    (out/'cg52-after-F-damaged.png').write_bytes(base64.b64decode(damaged.split(',',1)[1]))
    page.evaluate('window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A()');page.wait_for_timeout(250)
    restored=page.locator('#shipDetailCanvas').evaluate('(c)=>c.toDataURL()')
    check('CG reset clears persistent 2D damage and restores source',restored==pristine,{'scarAudit':page.evaluate('window.__WIP12E_REV5_2D_SCAR_AUDIT__')})
    for path,label in [(baseline,'D'),(src,'F')]:
        page=fresh(path,'DDG_119_LATE_FLIGHT_IIA');page.locator('#shipDetailBtn').click();page.wait_for_timeout(300)
        data=page.locator('#shipDetailCanvas').evaluate('(c)=>c.toDataURL()');details['ddg2D'+label]=hashlib.sha256(base64.b64decode(data.split(',',1)[1])).hexdigest()
        (out/f'ddg119-{label}.png').write_bytes(base64.b64decode(data.split(',',1)[1]))
    check('DDG 2D canvas remains byte-identical',details['ddg2DD']==details['ddg2DF'],{'D':details['ddg2DD'],'F':details['ddg2DF']})
    check('all page errors zero',not errors,errors)
    result=save();print(json.dumps({'passed':result['passed'],'total':result['total'],'pass':result['pass'],'failed':[r['name']for r in rows if not r['pass']]}));b.close()
    if not result['pass']:raise SystemExit(1)
