"""Native RAF/WebGL → measured CIC contact, read-only owner rotors and reset."""
import argparse,base64,hashlib,importlib.util,json,re,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch
spec=importlib.util.spec_from_file_location('physical_native_support',HERE.parent/'B/verify_native.py');support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
def capture(page,path):path.write_bytes(base64.b64decode(page.context.new_cdp_session(page).send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw,True)
  for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
   page=support.boot(b,a.html.read_bytes(),own,enemy);page.on('pageerror',lambda e:errors.append(str(e)));page.wait_for_function('window.__WIP148_3D_VIEW__.navalShipPresentersB.size===1',timeout=120000)
   page.evaluate("()=>{const d=window.__NAVAL_SIM_DIAG__;d.setEmcon(false);d.ciwsB1Closure.setPaused(false);d.setTimeScale(8);window.__WIP148_3D_VIEW__.focusPhysicalShipB('SHIP_SCENARIO_ENEMY_A');}")
   page.wait_for_function("window.__NAVAL_SIM_DIAG__.observerSnapshotC().ships.every(q=>q.tracks.some(t=>t.classification==='SURFACE'&&t.confirmed))||window.__WIP125_DIAG__.wip150RuntimeFault()",timeout=120000)
   page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');page.wait_for_timeout(1000)
   snapshot=page.evaluate('window.__NAVAL_SIM_DIAG__.observerSnapshotC()');render=page.evaluate("(()=>{const v=window.__WIP148_3D_VIEW__,p=v.navalShipPresentersB.get('SHIP_SCENARIO_ENEMY_A'),q=p.ownerRuntime.combatSystem.observerC.rotors,parts=p._bunkerAsset?.parts??p._bunker?.parts,spq=p.spq9bRotor??parts?.get('SPQ9'),nav=p.bridgeMasterERotor??parts?.get('SPS73');return {draw:v.renderer.info.render,radar:q,rotorMirrors:spq&&nav?Math.abs(spq.rotation.y+q.SPQ)<1e-7&&Math.abs(nav.rotation.y+q.NAV)<1e-7:null,state:window.__NAVAL_SIM_DIAG__.physicalFleetSnapshotB()};})()")
   before=page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.observerSnapshotC())');capture(page,a.out/(own+'-3d.png'))
   if not page.locator('#external3DBackBtn').is_visible():
    page.get_by_role('button',name=re.compile('CONTROLS')).click()
    page.get_by_role('button',name=re.compile('^SYSTEM')).click()
   page.locator('#external3DBackBtn').click();page.wait_for_timeout(800);capture(page,a.out/(own+'-cic.png'))
   unchanged=page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.observerSnapshotC())')==before
   core=page.evaluate('window.__CORE_SELFTEST_FAILURES__');faults=page.evaluate('[window.__WIP125_DIAG__.wip150RuntimeFault(),window.__WIP125_DIAG__.wip150PresentationFault()]')
   checks={'naturalPlayerSurfaceContact':any(t['classification']=='SURFACE'and t['confirmed']for t in snapshot['ships'][0]['tracks']),'naturalForeignSurfaceContact':any(t['classification']=='SURFACE'and t['confirmed']for t in snapshot['ships'][1]['tracks']),'nativeObserverAndPhysicsTick':snapshot['ships'][1]['tickCount']==render['state']['ships'][0]['clock']['tick']and snapshot['ships'][1]['tickCount']>0,'nativeDraws':render['draw']['calls']>0,'rotorsActuallyAdvance':any(abs(v)>1e-6 for v in render['radar'].values()),'rotorMeshMirrorsState':render['rotorMirrors']is True,'CicSwitchReadOnly':unchanged,'coreAndFaultZero':core==[]and all(v is None for v in faults)}
   page.evaluate('window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A()');checks['resetClearsBothObservers']=page.evaluate('window.__NAVAL_SIM_DIAG__.observerSnapshotC().ships.every(q=>q.tracks.length===0&&q.offboard.queued===0)')
   rows.append({'own':own,'enemy':enemy,'checks':checks,'snapshot':snapshot,'render':render,'core':core,'faults':faults});page.close();print(json.dumps({'own':own,'checks':checks}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'backend':'Chromium SwiftShader 393x852 native RAF, no manual physics/geometry ticks, no hardware FPS claim','cases':rows,'errors':errors,'pass':not errors and all(all(q['checks'].values())for q in rows)};(a.out/'native.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
