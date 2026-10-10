"""Native RAF/WebGL, owner source geometry, moving frame and post-impact recovery."""
import argparse,base64,hashlib,json,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch
FINGERPRINT=r'''root=>{const rows=[];root.traverse(o=>{if(!o.isMesh||!o.geometry?.attributes.position)return;for(let p=o;p&&p!==root;p=p.parent)if(p.userData.damageInterior||p.userData.interiorTopologyV48Wip06||p.userData.crewInteriorV48Wip07||p.userData.damageScar)return;
 const g=o.geometry,position=g.attributes.position,ix=g.index,values=position.array;let hash=2166136261,finite=true;for(let i=0;i<values.length;i++){finite=finite&&Number.isFinite(values[i]);hash=Math.imul(hash^Math.round(values[i]*10000),16777619)>>>0;}rows.push({name:o.name,vertices:position.count,indices:ix?.count??0,hash,finite});});return rows.sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));}'''
def boot(browser,body,own,enemy=None):
 page=browser.new_page(viewport={'width':393,'height':852},ignore_https_errors=True);page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5;');page.route('https://aegis.test/**',lambda r:r.fulfill(body=body,content_type='text/html'));page.goto('https://aegis.test/native?view3d=1',timeout=90000);page.wait_for_selector('#aegisShipSelect',timeout=90000);page.locator('#aegisShipSelect').select_option(own);page.locator('[data-target-choice]').select_option('NONE');page.locator('[data-enemy-choice]').select_option(enemy or 'NONE');page.locator('#aegisShipConfirmBtn').click();page.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__&&(window.__WIP148_3D_VIEW__?.ready||window.__WIP148_3D_VIEW__?._loadError)',timeout=120000);page.locator('#wip125DepartBtn').click();page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);window.__WIP148_3D_VIEW__.c12ApplyPreset("LOW")');return page
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[];references={}
 with sync_playwright()as pw:
  b=launch(pw,True)
  for profile in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   page=boot(b,a.baseline.read_bytes(),profile);references[profile]=page.evaluate('('+FINGERPRINT+')(window.__WIP148_3D_VIEW__.shipRoot)');page.close()
  for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
   page=boot(b,a.candidate.read_bytes(),own,enemy);page.on('pageerror',lambda e:errors.append(str(e)));page.wait_for_function('window.__WIP148_3D_VIEW__.navalShipPresentersB.size===1||window.__WIP125_DIAG__.wip150PresentationFault()',timeout=120000)
   fingerprint=page.evaluate('('+FINGERPRINT+')(window.__WIP148_3D_VIEW__.navalShipPresentersB.get("SHIP_SCENARIO_ENEMY_A").shipRoot)')
   page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__;v.focusPhysicalShipB('SHIP_SCENARIO_ENEMY_A');window.__NATIVE_FLEET_B__={draws:0,frameMs:[],last:null};const render=v.renderer.render;v.renderer.render=function(...args){const q=window.__NATIVE_FLEET_B__,now=performance.now();if(q.last!==null)q.frameMs.push(now-q.last);q.last=now;q.draws++;return render.apply(this,args);};}''');page.wait_for_function('window.__NATIVE_FLEET_B__.draws>=3',timeout=60000)
   before=page.evaluate('''()=>({fleet:window.__NAVAL_SIM_DIAG__.physicalFleetSnapshotB(),audit:window.__WIP148_3D_VIEW__.physicalFleetAuditB(),draws:window.__NATIVE_FLEET_B__.draws})''')
   cdp=page.context.new_cdp_session(page);(a.out/(own+'-fleet.png')).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
   page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false)');page.wait_for_function('n=>window.__NAVAL_SIM_DIAG__.physicalFleetSnapshotB().ships[0].clock.tick>n+60',arg=before['fleet']['ships'][0]['clock']['tick'],timeout=120000);page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
   probe=page.evaluate('window.__NAVAL_SIM_DIAG__.physicalShipProbeB("SHIP_SCENARIO_ENEMY_A")');print(json.dumps({'stage':'impact-wait','own':own}),flush=True)
   deadline=time.monotonic()+240
   while True:
    try:
     page.wait_for_function('''()=>{const v=window.__WIP148_3D_VIEW__.navalShipPresentersB.get('SHIP_SCENARIO_ENEMY_A');return (v.damageScarVisuals.size>=2&&!v._damageJobV3)||window.__WIP125_DIAG__.wip150PresentationFault();}''',timeout=30000);break
    except TimeoutError:
     progress=page.evaluate('''()=>({audit:window.__WIP148_3D_VIEW__.physicalFleetAuditB(),draws:window.__NATIVE_FLEET_B__.draws,fault:window.__WIP125_DIAG__.wip150PresentationFault()})''')
     print(json.dumps({'stage':'damage-progress','own':own,'progress':progress}),flush=True)
     if time.monotonic()>=deadline:raise
   preserved=page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),(k,v)=>k==="performance"?undefined:v)');start=page.evaluate('window.__NATIVE_FLEET_B__.draws');page.evaluate('window.__WIP148_3D_VIEW__.focusPhysicalShipB(null)');page.wait_for_function('n=>window.__NATIVE_FLEET_B__.draws>n+2',arg=start,timeout=60000)
   presentationReadOnly=page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),(k,v)=>k==="performance"?undefined:v)')==preserved
   page.evaluate('window.__WIP148_3D_VIEW__.focusPhysicalShipB("SHIP_SCENARIO_ENEMY_A");window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false)');tick=page.evaluate('window.__NAVAL_SIM_DIAG__.physicalFleetSnapshotB().ships[0].clock.tick');page.wait_for_function('n=>window.__NAVAL_SIM_DIAG__.physicalFleetSnapshotB().ships[0].clock.tick>n+5',arg=tick,timeout=120000);page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
   after=page.evaluate('''()=>({fleet:window.__NAVAL_SIM_DIAG__.physicalFleetSnapshotB(),audit:window.__WIP148_3D_VIEW__.physicalFleetAuditB(),draws:window.__NATIVE_FLEET_B__.draws,frames:window.__NATIVE_FLEET_B__.frameMs,core:window.__CORE_SELFTEST_FAILURES__,faults:[window.__WIP125_DIAG__.wip150RuntimeFault(),window.__WIP125_DIAG__.wip150PresentationFault()],render:window.__WIP148_3D_VIEW__.renderer.info.render})''')
   (a.out/(own+'-damage.png')).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
   root=after['audit']['roots'][0];nav=after['fleet']['ships'][0]['navigation'];checks={'twoSimulated':before['fleet']['simulated']==2,'correctProfileSourceGeometry':fingerprint==references[enemy],'finiteSourceVertices':all(q['finite']for q in fingerprint),'registeredFittings':root['lidCount']==(122 if enemy.startswith('CG')else 96)and root['spgCount']==(4 if enemy.startswith('CG')else 3)and root['seaRamPresent']==enemy.startswith('DDG'),'properOwnerWorldRoot':root['parent']=='PHYSICAL_NAVAL_SHIPS_B'and abs(root['root'][0]-nav['positionWorld']['x']/0.0038)<1e-6 and abs(root['root'][2]-nav['positionWorld']['y']/0.0038)<1e-6,'realHullDamage':probe['accepted']and root['scars']>=2 and all(any(h['actualHole']and h['attached']and h['role']==role for h in root['holes'])for role in ['ENTRY','EXIT']),'nativeDrawAndPhysicsContinue':after['draws']>before['draws']and after['fleet']['ships'][0]['clock']['tick']>tick,'presentationReadOnly':presentationReadOnly,'noFaults':after['core']==[]and all(q is None for q in after['faults'])}
   # Retirement/recreation must discard owner jobs and roots, even for the same ID.
   for _ in range(2):page.evaluate('window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A()');page.wait_for_function('''()=>{const v=window.__WIP148_3D_VIEW__,p=v.navalShipPresentersB.get('SHIP_SCENARIO_ENEMY_A');return p&&p.ownerRuntime.clock.tick===0&&p.damageScarVisuals.size===0;}''',timeout=90000)
   checks['resetDisposesOldRoot']=page.evaluate('window.__WIP148_3D_VIEW__.navalShipLayerB.children.length===1')
   rows.append({'own':own,'enemy':enemy,'checks':checks,'before':before,'probe':probe,'after':after,'sourceFingerprint':fingerprint});page.close();(a.out/'native-progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'own':own,'checks':checks}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'backend':'Chromium SwiftShader native RAF/WebGL; no queue forcing, no hardware FPS claim','references':references,'cases':rows,'errors':errors,'pass':not errors and all(all(r['checks'].values())for r in rows)};(a.out/'native.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
