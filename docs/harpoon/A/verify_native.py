"""Native RAF/WebGL verification of launch hardware, articulation, impact and reset."""
import argparse,base64,hashlib,json,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'bunkerhill'/'K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args()
source=Path(a.html);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);checks={};details={};errors=[];console=[]
def check(name,value):checks[name]=bool(value)
with sync_playwright()as pw:
    b=launch(pw,True);p=load(b,source.read_bytes(),webgl=True,errors=errors)
    p.on('console',lambda msg:console.append(msg.text[:1200])if msg.type=='error'else None)
    p.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__;window.__HARPOON_NATIVE__={draws:0,times:[]};const draw=v.renderer.render;v.renderer.render=function(...args){const t=window.__HARPOON_NATIVE__;t.draws++;t.times.push(performance.now());if(t.times.length>80)t.times.shift();return draw.apply(this,args)};}''')
    p.wait_for_function('window.__HARPOON_NATIVE__.draws>=2',timeout=45000)
    caps=p.evaluate('window.__WIP148_3D_VIEW__.harpoonAuditA()');details['capsBefore']=caps
    check('allEightSourceCapsRegistered',len(caps['caps'])==8 and all(q['sourceTriangles']==34 for q in caps['caps']))
    setup=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:8});const t=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');h.select(t.trackId);return h.gate();}''')
    check('realObservedTrackReady',setup['ok'])
    p.evaluate('window.__WIP148_3D_VIEW__.close()');p.locator('#modeAimBtn').click();p.locator('#armSubVlsBtn').click();p.locator('#harpoonTubeA').select_option('MK141-A3')
    controls=p.evaluate('''()=>{const ids=['harpoonFireA','harpoonTubeA','harpoonStatusA'],rows=ids.map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect();return {id,x:r.x,y:r.y,width:r.width,height:r.height,visible:r.width>0&&r.height>0,inside:r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight};});return {width:innerWidth,height:innerHeight,rows};}''');details['mobileControls']=controls
    check('armVlsControlsFitMobileViewport',all(q['visible']and q['inside']for q in controls['rows']))
    cdp=p.context.new_cdp_session(p)
    def capture(name):(out/name).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
    capture('arm-vls-harpoon.png');p.locator('#harpoonFireA').click();p.evaluate('window.__HARPOON_DIAG_A__.focusedTicks(12)');p.locator('#external3dBtn').click()
    p.evaluate('window.__WIP148_3D_VIEW__.toggleFollowLatest()')
    before=p.evaluate('window.__HARPOON_NATIVE__.draws');p.wait_for_function('n=>window.__HARPOON_NATIVE__.draws>n',arg=before,timeout=45000)
    def inspect():return p.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__,st=window.get3DRenderState(),m=st.harpoons[0],visual=m?v.harpoonVisualsA.get(m.id):null;return {state:m,audit:v.harpoonAuditA(),draws:window.__HARPOON_NATIVE__.draws,follow:v.currentFollowState(st)?.state?.kind,wingRotations:visual?.mesh.userData.wings.map(w=>w.rotation.x),boosterVisible:visual?.mesh.userData.booster.visible,geometry:v.renderer.info.memory,damage:v.damageAuditV48Wip03(),faults:v.renderFaultsV48Wip13I??v._renderFaultsV48Wip13I??null};}''')
    launch=inspect();details['launch']=launch;capture('canister-launch.png')
    check('nativeHarpoonMeshAndFollow',launch['audit']['instances']>=1 and launch['follow']=='HARPOON')
    check('selectedSourceCapOpensOnly',next(q for q in launch['audit']['caps']if q['id']=='MK141-A3')['quaternion']!=[0,0,0,1]and all(q['quaternion']==[0,0,0,1]for q in launch['audit']['caps']if q['id']!='MK141-A3'))
    p.evaluate('window.__HARPOON_DIAG_A__.focusedTicks(55)');before=p.evaluate('window.__HARPOON_NATIVE__.draws');p.wait_for_function('n=>window.__HARPOON_NATIVE__.draws>n',arg=before,timeout=45000)
    boost=inspect();details['boost']=boost;capture('wings-deployed-boost.png')
    check('nativeWingsDeployDuringBoost',boost['state']['boosterAttached']and boost['state']['wingDeploy01']==1 and all(abs(v)<1e-8 for v in boost['wingRotations']))
    p.evaluate('window.__HARPOON_DIAG_A__.focusedTicks(150)');before=p.evaluate('window.__HARPOON_NATIVE__.draws');p.wait_for_function('n=>window.__HARPOON_NATIVE__.draws>n',arg=before,timeout=45000)
    separated=inspect();details['separated']=separated;capture('booster-separated.png')
    check('nativeSeparateBoosterAndBody',not separated['boosterVisible']and separated['audit']['instances']>=2)
    p.evaluate('window.__HARPOON_DIAG_A__.focusedTicks(2200)');before=p.evaluate('window.__HARPOON_NATIVE__.draws');p.wait_for_function('n=>window.__HARPOON_NATIVE__.draws>n+1',arg=before,timeout=60000)
    impact=inspect();details['impact']=impact;details['terminal']=p.evaluate('window.__HARPOON_DIAG_A__.snapshot().missiles[0].impact');capture('native-target-impact.png')
    check('physicalImpactReachedWithNativeRenderer',details['terminal']is not None)
    # Exercise actual orbit pointer input while detailed target damage is being presented.
    rect=p.locator('#external3DCanvas').bounding_box();camera0=p.evaluate('window.__WIP148_3D_VIEW__.camera.matrixWorld.toArray()')
    p.mouse.move(rect['x']+rect['width']*.7,rect['y']+rect['height']*.45);p.mouse.down();p.mouse.move(rect['x']+rect['width']*.7+30,rect['y']+rect['height']*.45+8,steps=4);p.mouse.up()
    before=p.evaluate('window.__HARPOON_NATIVE__.draws');p.wait_for_function('n=>window.__HARPOON_NATIVE__.draws>n+1',arg=before,timeout=60000)
    check('cameraAndDrawContinueAfterImpact',camera0!=p.evaluate('window.__WIP148_3D_VIEW__.camera.matrixWorld.toArray()'))
    resources=p.evaluate('window.__WIP148_3D_VIEW__.harpoonAuditA()')
    before=p.evaluate('window.__HARPOON_NATIVE__.draws')
    p.evaluate('''()=>{window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);}''')
    p.wait_for_function('n=>window.__HARPOON_NATIVE__.draws>n&&window.__WIP148_3D_VIEW__.harpoonVisualsA?.size===0&&window.__WIP148_3D_VIEW__.harpoonAuditA().caps.every(q=>q.quaternion[0]===0&&q.quaternion[1]===0&&q.quaternion[2]===0&&q.quaternion[3]===1)',arg=before,timeout=60000)
    reset=inspect();details['reset']=reset
    check('nativeResetRemovesOrdnanceAndClosesCaps',reset['audit']['instances']==0 and all(q['quaternion']==[0,0,0,1]for q in reset['audit']['caps']))
    check('sharedModelCacheRetainedWithoutTextures',reset['audit']['cachedGeometries']==62 and reset['audit']['textureMaps']==0 and reset['audit']['cachedGeometries']==resources['cachedGeometries'])
    # Native simulation tick, no focused stepping: renderer and gameplay remain live.
    first=p.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false).simStepCounter')
    p.wait_for_function('s=>window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter>s',arg=first,timeout=45000)
    last=p.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true).simStepCounter');check('nativeFixedTicksContinue',last>first)
    check('coreSelfTestsZero',p.evaluate('window.__CORE_SELFTEST_FAILURES__')==[]);b.close()
check('pageErrorsZero',not errors);check('consoleErrorsZero',not console)
result={'schema':'HARPOON_A_NATIVE_WEBGL_VERIFICATION','source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'backend':'Chromium SwiftShader','frameAuthority':'NATIVE_RAF','hardwareFpsClaim':False,'checks':checks,'details':details,'errors':errors,'console':console,'pass':all(checks.values())}
(out/'native.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'console':console,'pass':result['pass']},ensure_ascii=False))
if not result['pass']:raise SystemExit(1)
