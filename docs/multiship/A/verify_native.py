"""Real startup controls, native RAF/WebGL and continued rendering after impact."""
import argparse,base64,hashlib,json,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch
def main():
    p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];console=[];rows=[]
    with sync_playwright()as pw:
        browser=launch(pw,True)
        for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
            page=browser.new_page(viewport={'width':393,'height':852},ignore_https_errors=True);page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console.append(m.text)if m.type=='error' else None)
            page.on('requestfailed',lambda r:console.append({'url':r.url,'failure':r.failure}))
            page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5;');page.route('https://aegis.test/**',lambda r:r.fulfill(body=a.html.read_bytes(),content_type='text/html'));page.goto('https://aegis.test/native?view3d=1',timeout=90000)
            page.wait_for_selector('#aegisShipSelect',timeout=90000);page.locator('#aegisShipSelect').select_option(own);page.locator('[data-target-choice]').select_option('NONE');page.locator('[data-enemy-choice]').select_option(enemy)
            ui=page.evaluate('''()=>({snapshot:window.__AEGIS_DEPLOYMENT_A__.snapshot(),bounds:[...document.querySelectorAll('#aegisShipSelectionOverlay select')].map(e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,inside:r.left>=0&&r.right<=innerWidth};})})''')
            cdp=page.context.new_cdp_session(page);(a.out/(own+'-startup.png')).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
            page.locator('#aegisShipConfirmBtn').click();page.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__&&(window.__WIP148_3D_VIEW__?.ready||window.__WIP148_3D_VIEW__?._loadError)',timeout=120000)
            page.locator('#wip125DepartBtn').click();page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__;d.ciwsB1Closure.setPaused(true);v.c12ApplyPreset('LOW');window.__MULTI_NATIVE_A__={draws:0,frameMs:[],last:null};const render=v.renderer.render;v.renderer.render=function(...args){const n=performance.now(),s=window.__MULTI_NATIVE_A__;if(s.last!==null)s.frameMs.push(n-s.last);s.last=n;s.draws++;return render.apply(this,args);};}''')
            page.wait_for_function('window.__MULTI_NATIVE_A__.draws>=3',timeout=60000)
            before=page.evaluate('''()=>({ships:window.__NAVAL_SIM_DIAG__.multiShipSnapshotA(),draws:window.__MULTI_NATIVE_A__.draws,tick:window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter})''')
            page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false)')
            deadline=time.monotonic()+240
            while True:
                try:page.wait_for_function('n=>window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter>=n+60',arg=before['tick'],timeout=15000);break
                except TimeoutError:
                    print(json.dumps({'own':own,'stage':'native-RAF-progress','tick':page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter')}),flush=True)
                    if time.monotonic()>deadline:raise
            page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
            impact=page.evaluate("window.__NAVAL_SIM_DIAG__.runV48Wip03StructuralProbe({hits:2,label:'Kh-32',xM:12,zM:-3.5,side:'STARBOARD'})")
            n=page.evaluate('window.__MULTI_NATIVE_A__.draws');page.wait_for_function('n=>window.__MULTI_NATIVE_A__.draws>n+2&&!window.__WIP148_3D_VIEW__.damageAuditV48Wip03().pending',arg=n,timeout=240000)
            page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false)');start=page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter');page.wait_for_function('n=>window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter>n+4',arg=start,timeout=60000);page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
            after=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,s=window.__MULTI_NATIVE_A__;const frames=s.frameMs.slice().sort((a,b)=>a-b);return {ships:d.multiShipSnapshotA(),damage:window.__WIP148_3D_VIEW__.damageAuditV48Wip03(),draws:s.draws,tick:d.ciwsB1Closure.snapshot().simStepCounter,core:window.__CORE_SELFTEST_FAILURES__,faults:[window.__WIP125_DIAG__.wip150RuntimeFault(),window.__WIP125_DIAG__.wip150PresentationFault()],frameTiming:{backend:'SwiftShader',hardwareFpsClaim:false,samples:frames.length,averageMs:frames.reduce((a,b)=>a+b,0)/frames.length,p95Ms:frames[Math.floor(frames.length*.95)],maxMs:frames.at(-1)}};}''')
            (a.out/(own+'-damage.png')).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
            checks={'mobileSelectionFits':all(b['inside']for b in ui['bounds']),'startupChoicesPersist':before['ships']['deployment']['committed']['enemyProfileId']==enemy and before['ships']['deployment']['committed']['targetShip']=='NONE','twoRegisteredOneSimulated':before['ships']['registered']==2 and before['ships']['simulated']==1,'nativeFramesAndTicksContinue':after['draws']>before['draws']+3 and after['tick']>start,'controlledDamageCreatesRealHullOpenings':after['damage']['dualHullOpenings']and not after['damage']['pending'],'postImpactRenderingContinues':after['draws']>n+2,'selectedPlayerPreserved':after['ships']['ships'][0]['profileId']==own,'faultsZero':after['core']==[]and all(x is None for x in after['faults'])}
            rows.append({'own':own,'enemy':enemy,'checks':checks,'startup':ui,'before':before,'impact':impact,'after':after});page.close();(a.out/'native-progress.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'own':own,'checks':checks}),flush=True)
        browser.close()
    report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'backend':'Chromium SwiftShader, actual UI and RAF; no hardware FPS claim','cases':rows,'errors':errors,'console':console,'pass':not errors and not console and all(all(r['checks'].values())for r in rows)};(a.out/'native.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'errors':errors,'console':console}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
