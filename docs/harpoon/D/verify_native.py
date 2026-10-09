"""Native RAF/WebGL and real mobile buttons: successive auto-selected tube releases."""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[1]/'bunkerhill/K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args()
source=Path(a.html);body=source.read_bytes();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
checks={};details={};errors=[];console=[]
def check(k,v):checks[k]=bool(v)
with sync_playwright()as pw:
 b=launch(pw,True);p=load(b,body,webgl=True,errors=errors)
 p.on('console',lambda m:console.append(m.text)if m.type=='error'else None)
 p.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__;window.__H_D_NATIVE__={draws:0};const render=v.renderer.render;
  v.renderer.render=function(...args){window.__H_D_NATIVE__.draws++;return render.apply(this,args);};}''')
 p.wait_for_function('window.__H_D_NATIVE__.draws>=2',timeout=60000)
 p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;
  d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:8});
  const t=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);
  d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');h.select(t.trackId);window.__WIP148_3D_VIEW__.close();}''')
 p.locator('#modeAimBtn').click();p.locator('#armSubVlsBtn').click()
 tubes=[];scheduler=[]
 for i,age in enumerate([1.8,.3]):
  p.evaluate('window.__HARPOON_DIAG_A__.refreshUi()');tubes.append(p.evaluate('window.__HARPOON_DIAG_A__.autoTube().tubeId'))
  p.locator('#harpoonFireA').click();p.locator('#external3dBtn').click()
  start=p.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false).simStepCounter')
  p.wait_for_function('q=>window.__HARPOON_DIAG_A__.snapshot().missiles[q.i]?.ageS>=q.age',arg={'i':i,'age':age},timeout=180000)
  stop=p.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true).simStepCounter');scheduler.append({'start':start,'stop':stop})
  n=p.evaluate('window.__H_D_NATIVE__.draws');p.wait_for_function('n=>window.__H_D_NATIVE__.draws>n+1',arg=n,timeout=60000)
  if i==0:p.evaluate('window.__WIP148_3D_VIEW__.close()')
 state=p.evaluate('''()=>({snapshot:window.__HARPOON_DIAG_A__.snapshot(),renderer:window.__WIP148_3D_VIEW__.harpoonAuditA(),
  draws:window.__H_D_NATIVE__.draws,core:window.__CORE_SELFTEST_FAILURES__,
  faults:{simulation:window.__WIP125_DIAG__.wip150RuntimeFault(),presentation:window.__WIP125_DIAG__.wip150PresentationFault()}})''')
 details['nativeReleases']=state;details['scheduler']={'runs':scheduler,'manuallyAdvancedPhysicsTicks':0,'manuallyAdvancedGeometryQueues':0}
 check('nativeTwoButtonPressesAutoSelectDistinctTubes',len(set(tubes))==2 and [m['tubeId']for m in state['snapshot']['missiles']]==tubes)
 check('nativeFrameClockAndRenderingContinue',all(q['stop']>q['start']for q in scheduler)and state['draws']>10)
 check('nativeCorrectTwoPhysicalTubeCoversOpen',len([t for t in state['snapshot']['inventory']['tubes']if not t['loaded']])==2 and all(not next(c for c in state['renderer']['caps']if c['id']==tid)['rearVisible']for tid in tubes))
 check('nativeCoreAndRuntimeFaultsZero',state['core']==[]and all(v is None for v in state['faults'].values()))
 p.evaluate('window.__WIP148_3D_VIEW__.close();window.__HARPOON_DIAG_A__.refreshUi()')
 controls=p.evaluate('''()=>['harpoonTubeA','harpoonFireA','harpoonStatusA'].map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect();return {id,text:e.textContent,x:r.x,y:r.y,width:r.width,height:r.height,inside:r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight};})''');details['controls640x480']=controls
 check('mobileAutoLabelAndFireControlsFit',all(q['inside']and q['width']>0 for q in controls))
 check('mobilePanelKeepsNoDatalinkStatus','NO DL'in controls[2]['text']and 'TERMINAL_ARH'not in controls[2]['text']and 'm/s'not in controls[2]['text'])
 cdp=p.context.new_cdp_session(p);(out/'native-auto-tubes.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
 p.locator('#external3dBtn').click();n=p.evaluate('window.__H_D_NATIVE__.draws')
 p.evaluate('window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
 p.wait_for_function('n=>window.__H_D_NATIVE__.draws>n&&window.__WIP148_3D_VIEW__.harpoonVisualsA.size===0',arg=n,timeout=60000)
 reset=p.evaluate('''()=>({inventory:window.__HARPOON_DIAG_A__.snapshot().inventory,picture:window.__HARPOON_DIAG_A__.operatorPicture(),renderer:window.__WIP148_3D_VIEW__.harpoonAuditA()})''');details['reset']=reset
 check('nativeResetRestoresAllEightTubesAndClearsKnowledge',all(t['loaded']for t in reset['inventory']['tubes'])and not reset['picture']['launches']and reset['renderer']['instances']==0 and all(c['rearVisible']for c in reset['renderer']['caps']))
 b.close()
check('nativePageErrorsZero',not errors);check('nativeConsoleErrorsZero',not console)
report={'schema':'HARPOON_D_NATIVE_VERIFICATION','source':source.name,'sha256':hashlib.sha256(body).hexdigest(),'backend':'Chromium SwiftShader','frameAuthority':'NATIVE_RAF','hardwareFpsClaim':False,'checks':checks,'details':details,'errors':errors,'console':console,'pass':all(checks.values())}
(out/'native.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'pass':report['pass'],'errors':errors,'console':console},ensure_ascii=False));raise SystemExit(0 if report['pass']else 1)
