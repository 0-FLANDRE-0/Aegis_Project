"""Native RAF/WebGL owner AUTO launch, independent mounts and read-only camera.

An explicit measured HOSTILE fixture exercises authorization, not sensor truth.
Natural anonymous contacts are separately tested by verify_closein/natural.
"""
import argparse,base64,hashlib,importlib.util,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[2]/'docs/bunkerhill/K'));from browser_i import launch
spec=importlib.util.spec_from_file_location('native_support_e',HERE.parent/'B/verify_native.py');support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright()as pw:
  b=launch(pw,True)
  for own,enemy in [('DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA'),('CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA')]:
   page=support.boot(b,a.html.read_bytes(),own,enemy);page.on('pageerror',lambda e:errors.append(str(e)))
   page.wait_for_function('window.__WIP148_3D_VIEW__.navalShipPresentersB.size===1||window.__WIP125_DIAG__.wip150PresentationFault()',timeout=120000)
   page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,id='SHIP_SCENARIO_ENEMY_A',n=d.physicalFleetSnapshotB().ships[0].navigation;d.observerCommandC(id,{emcon:false});d.weaponFixtureD(id,{action:'track',trackId:21,positionM:{x:n.positionWorld.x/.0038+18000,y:n.positionWorld.y/.0038,z:15},velocityMps:{x:-250,y:0,z:0}});d.weaponFixtureD(id,{action:'identity',trackId:21,identity:'HOSTILE'});const v=window.__WIP148_3D_VIEW__,render=v.renderer.render;window.__NATIVE_DEFENSE_E__={draws:0};v.renderer.render=function(...args){window.__NATIVE_DEFENSE_E__.draws++;return render.apply(this,args);};v.focusPhysicalShipB(id);d.setTimeScale(8);d.ciwsB1Closure.setPaused(false);}''')
   page.wait_for_function('''()=>{const d=window.__NAVAL_SIM_DIAG__,s=d.weaponsSnapshotD().ships[0];return (s.ticks>=64&&s.sam.length>0&&window.__NATIVE_DEFENSE_E__.draws>=3)||window.__WIP125_DIAG__.wip150RuntimeFault();}''',timeout=120000)
   page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
   page.wait_for_function('window.__WIP148_3D_VIEW__.missileVisuals.size>0||window.__WIP125_DIAG__.wip150PresentationFault()',timeout=60000)
   state=page.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__,st=window.get3DRenderState();return {defense:d.defenseSnapshotE().ships[0],weapons:d.weaponsSnapshotD().ships[0],fleet:d.physicalFleetSnapshotB(),meshes:[...v.missileVisuals.keys()],spg:[...v.navalShipPresentersB.get('SHIP_SCENARIO_ENEMY_A').spgMounts.keys()],ownMissiles:st.missiles.map(m=>m.id),worldMissiles:st.navalMissilesD.map(m=>m.id),draw:v.renderer.info.render};}''')
   (a.out/(enemy+'-auto.png')).write_bytes(base64.b64decode(page.context.new_cdp_session(page).send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
   before=page.evaluate("JSON.stringify({w:window.__NAVAL_SIM_DIAG__.weaponsSnapshotD(),a:window.__NAVAL_SIM_DIAG__.defenseSnapshotE()},(k,v)=>k==='performance'?undefined:v)");draws=page.evaluate('window.__NATIVE_DEFENSE_E__.draws');page.evaluate('window.__WIP148_3D_VIEW__.focusPhysicalShipB(null)');page.wait_for_function('n=>window.__NATIVE_DEFENSE_E__.draws>n+2',arg=draws,timeout=60000)
   unchanged=before==page.evaluate("JSON.stringify({w:window.__NAVAL_SIM_DIAG__.weaponsSnapshotD(),a:window.__NAVAL_SIM_DIAG__.defenseSnapshotE()},(k,v)=>k==='performance'?undefined:v)")
   w=state['weapons'];checks={'defaultAuto':state['defense']['mode']=='AUTO','actualAutoRounds':sum(state['defense']['autonomy']['totalAutoRounds'].values())>0,'singleFixedClock':w['ticks']==state['fleet']['ships'][0]['clock']['tick']==state['defense']['ticks'],'nativeSamMesh':any(str(m['id']) in key for m in w['sam']for key in state['meshes']),'correctSpgMounts':len(state['spg'])==(4 if enemy.startswith('CG')else 3),'foreignPresentationWithoutTelemetry':len(state['worldMissiles'])>0 and all(m['id']not in state['ownMissiles']for m in w['sam']),'nativeDraw':state['draw']['calls']>0,'cameraReadOnly':unchanged,'noFaults':page.evaluate('window.__CORE_SELFTEST_FAILURES__.length===0&&!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault()')};rows.append({'own':own,'enemy':enemy,'checks':checks,'state':state});page.close();print(json.dumps({'enemy':enemy,'failed':[k for k,v in checks.items()if not v]}),flush=True)
  b.close()
 report={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'backend':'Chromium SwiftShader native RAF/WebGL; no hardware FPS claim','cases':rows,'errors':errors,'pass':not errors and all(all(q['checks'].values())for q in rows)};(a.out/'native.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
