"""Native RAF/WebGL: real ARM input, full-clock flight, measured CIC, observer separation, reset."""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[1]/'bunkerhill/K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args();source=Path(a.html);body=source.read_bytes();sha=hashlib.sha256(body).hexdigest();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);checks={};details={};errors=[];console=[]
def check(k,v):checks[k]=bool(v)
with sync_playwright()as pw:
 b=launch(pw,True);p=load(b,body,webgl=True,errors=errors)
 p.on('console',lambda msg:console.append(msg.text[:1200])if msg.type=='error'else None)
 p.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__;window.__H_C_NATIVE__={draws:0};const render=v.renderer.render;v.renderer.render=function(...args){window.__H_C_NATIVE__.draws++;return render.apply(this,args);};}''')
 p.wait_for_function('window.__H_C_NATIVE__.draws>=2',timeout=60000)
 p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:8});const t=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');h.select(t.trackId);window.__WIP148_3D_VIEW__.close();}''')
 p.locator('#modeAimBtn').click();p.locator('#armSubVlsBtn').click();p.locator('#harpoonTubeA').select_option('MK141-A4')
 p.locator('#harpoonFireA').click();p.locator('#external3dBtn').click();start=p.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false).simStepCounter')
 p.wait_for_function('window.__HARPOON_DIAG_A__.snapshot().missiles[0]?.ageS>=4.8',timeout=240000)
 stop=p.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true).simStepCounter')
 p.evaluate('window.__WIP148_3D_VIEW__.toggleFollowLatest()')
 draw=p.evaluate('window.__H_C_NATIVE__.draws');p.wait_for_function('n=>window.__H_C_NATIVE__.draws>n+1',arg=draw,timeout=60000)
 state=p.evaluate('''()=>({missile:window.__HARPOON_DIAG_A__.snapshot().missiles[0],picture:window.__HARPOON_DIAG_A__.operatorPicture(),renderer:window.__WIP148_3D_VIEW__.harpoonAuditA(),follow:window.__WIP148_3D_VIEW__.statusEl.textContent,auxTitle:document.getElementById('external3DMiniCicScale').parentElement.firstElementChild.textContent,draws:window.__H_C_NATIVE__.draws,faults:{simulation:window.__WIP125_DIAG__.wip150RuntimeFault(),presentation:window.__WIP125_DIAG__.wip150PresentationFault()}})''');details['nativeFlight']=state;details['scheduler']={'start':start,'stop':stop,'manuallyAdvancedPhysicsTicks':0,'manuallyAdvancedGeometryQueues':0}
 check('nativeFullClockTicksAndDrawContinue',stop>start+200 and state['draws']>20)
 check('nativeActualSelectedTubeReleases',state['missile']['tubeId']=='MK141-A4')
 check('nativeSeparationPreserves3p2Seconds',len([e for e in state['missile']['history']if e['event']=='BOOSTER_SEPARATED'and abs(e['ageS']-3.2)<1e-8])==1)
 check('nativeArhTracksAndWingsDeploy',state['missile']['seeker']['mode']=='TRACK'and state['missile']['wingDeploy01']==1)
 check('nativeRadarCorrelatesOwnFile',state['picture']['launches'][0]['trackId']is not None)
 check('nativeBodyNozzleJetAndOpenTubePreserved',state['renderer']['visuals'][0]['jetPlume']and not state['renderer']['visuals'][0]['boostPlume']and not next(c for c in state['renderer']['caps']if c['id']=='MK141-A4')['rearVisible'])
 check('privateFlightDataExplicitObserver',state['follow'].startswith('OBSERVER / NO DL'))
 check('auxCicOwnshipCenteredNoDatalink',state['auxTitle']=='AUX CIC · OWN SHIP · NO DL')
 check('noNativeSimulationOrPresentationFault',all(v is None for v in state['faults'].values()))
 cdp=p.context.new_cdp_session(p)
 def capture(n):(out/n).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
 capture('native-observer-arh.png');p.evaluate('window.__WIP148_3D_VIEW__.close()');p.evaluate('window.__HARPOON_DIAG_A__.refreshUi()')
 details['operatorStatus']=p.locator('#harpoonStatusA').inner_text();check('nativeOperatorHasRadarReportNoSeekerTelemetry','NO DL'in details['operatorStatus']and 'RADAR'in details['operatorStatus']and 'TERMINAL_ARH'not in details['operatorStatus']and 'm/s'not in details['operatorStatus'])
 controls=p.evaluate('''()=>['harpoonTubeA','harpoonFireA','harpoonStatusA'].map(id=>{const r=document.getElementById(id).getBoundingClientRect();return {id,x:r.x,y:r.y,width:r.width,height:r.height,inside:r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight};})''');details['mobileControls']=controls;check('noDatalinkControlsFit640x480',all(q['inside']and q['width']>0 for q in controls))
 capture('native-cic-measured-own.png');p.locator('#external3dBtn').click();draw=p.evaluate('window.__H_C_NATIVE__.draws')
 p.evaluate('''()=>{window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);}''')
 p.wait_for_function('n=>window.__H_C_NATIVE__.draws>n&&window.__WIP148_3D_VIEW__.harpoonVisualsA.size===0',arg=draw,timeout=60000)
 reset=p.evaluate('''()=>({picture:window.__HARPOON_DIAG_A__.operatorPicture(),audit:window.__WIP148_3D_VIEW__.harpoonAuditA(),core:window.__CORE_SELFTEST_FAILURES__})''');details['reset']=reset
 check('nativeResetClearsLaunchKnowledgeAndVisuals',reset['picture']['launches']==[]and reset['audit']['instances']==0)
 check('nativeResetRestoresOriginalEightCovers',len(reset['audit']['caps'])==8 and all(q['rearVisible']and q['quaternion']==[0,0,0,1]for q in reset['audit']['caps']))
 check('coreSelfTestsZero',reset['core']==[]);b.close()
check('pageErrorsZero',not errors);check('consoleErrorsZero',not console)
result={'schema':'HARPOON_C_NATIVE_VERIFICATION','source':source.name,'sha256':sha,'backend':'Chromium SwiftShader','frameAuthority':'NATIVE_RAF','hardwareFpsClaim':False,'checks':checks,'details':details,'errors':errors,'console':console,'pass':all(checks.values())};(out/'native.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'console':console,'pass':result['pass']},ensure_ascii=False));raise SystemExit(0 if result['pass']else 1)
