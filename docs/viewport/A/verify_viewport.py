"""VP_A A-G: real client input and real Three projection, seven CSS sizes.

Framing reference is the existing ownship camera aim point (local 0,11,0);
bow/stern endpoints are measured separately. Projection tests suspend recurring
GPU submission after Three init, leaving RAF/layout/input running normally.
"""
from pathlib import Path
import argparse,hashlib,json,math,random,sys,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/helicopter/H'))
from browser import launch,load_fleet
SIZES=[(1920,1080),(1400,900),(1400,560),(900,900),(600,900),(390,844),(844,390)]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();errors=[];checks={};rows=[];records={}
 def check(k,v):checks[k]=bool(v)
 def settle(p,w,h):
  p.set_viewport_size({'width':w,'height':h});p.wait_for_function('([w,h])=>{const v=AEGIS_VIEWPORT.raw;return Math.abs(v.w-w)<.1&&Math.abs(v.h-h)<.1}',arg=[w,h]);p.wait_for_timeout(330)
 with sync_playwright()as pw:
  b=launch(pw,True);p=load_fleet(b,raw,errors=errors,width=1400,height=900)
  # UI fixture uses anonymous measurements; never injects truth identity into a track.
  sp=__import__('importlib.util',fromlist=['']);spec=sp.spec_from_file_location('passive_ui',ROOT/'docs/helicopter/K/verify_ui.py');m=sp.module_from_spec(spec);spec.loader.exec_module(m);tid=p.evaluate(m.SETUP)
  p.locator('[data-tab=ARM]').click();p.evaluate('__VIEWPORT_A__.setDistance(40)')
  for w,h in SIZES:
   settle(p,w,h);p.evaluate('__VIEWPORT_A__.setPan(0,0);__VIEWPORT_A__.draw()');s=p.evaluate('__VIEWPORT_A__.snapshot()');v=s['viewport']['twoD'];own=s['twoD']['ownship'];target=p.evaluate('()=>{const a=__VIEWPORT_A__,c=a.snapshot().twoD.centerWorld;return a.worldToScreen(c.x+38,c.y+19)}');ratio=math.hypot(target['x']-own['x'],target['y']-own['y'])/v['shortSide'];ce=math.hypot(own['x']-v['cx'],own['y']-v['cy']);check(f'A.{w}x{h}.center',ce<=1)
   # Actual pointer at ownship must map to its world anchor (no ownship attack track exists).
   p.mouse.click(own['x'],own['y']);cursor=p.evaluate('__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state.lockCursor');cp=p.evaluate('c=>__VIEWPORT_A__.worldToScreen(c.x,c.y)',cursor);check(f'C.{w}x{h}.ownCursor',math.hypot(cp['x']-own['x'],cp['y']-own['y'])<=1)
   # Actual target tap + existing LOCK button, after every resize.
   tr=p.evaluate('id=>__NAVAL_SIM_DIAG__.observerFacadeC(__AEGIS_ACTIVE_SHIP_RUNTIME__.entityId).tracks.find(t=>t.trackId===id)',tid);q=p.evaluate('t=>__VIEWPORT_A__.worldToScreen(t.positionM.x*.0038,t.positionM.y*.0038)',tr)
   p.mouse.click(q['x'],q['y']);p.locator('#lockBtn').click();lock=p.evaluate('__EMCON_DESIGNATION_F2__.snapshot()');check(f'C.{w}x{h}.target',lock['selectedLockId']==tid)
   # Coordinate program uses the same map pointer path; panel group only affects controls.
   p.evaluate("()=>{__HARPOON_DIAG_A__.routeToggle();}");tap={'x':v['cx']+v['shortSide']*.21,'y':v['cy']+v['shortSide']*.12};p.mouse.click(tap['x'],tap['y']);route=p.evaluate('__HARPOON_DIAG_A__.routeDraft()');point=route['pointsM'][-1];project=p.evaluate('t=>__VIEWPORT_A__.worldToScreen(t.x*.0038,t.y*.0038)',point);err=math.hypot(project['x']-tap['x'],project['y']-tap['y']);check(f'C.{w}x{h}.route',err<=2);p.evaluate('__HARPOON_DIAG_A__.routeToggle()')
   rows.append({'size':[w,h],'visible':v,'centerErrorPx':ce,'distanceKm':s['twoD']['tacticalViewKm'],'scaleLabel':s['twoD']['scaleLabel'],'scaleBarKm':s['twoD']['scaleBarKm'],'targetDistanceOverShortSide':ratio,'routeErrorPx':err})
  check('A.distanceInvariant',len({r['distanceKm']for r in rows})==1);check('A.scaleLabelInvariant',len({r['scaleLabel']for r in rows})==1);check('A.scaleBarInvariant',len({r['scaleBarKm']for r in rows})==1);check('A.ratio',max(r['targetDistanceOverShortSide']for r in rows)/min(r['targetDistanceOverShortSide']for r in rows)-1<=.01)
  # Real drag, then same world point stays under the visible center at all sizes.
  settle(p,1400,900);p.mouse.move(800,400);p.mouse.down();p.mouse.move(900,460,steps=5);p.mouse.up();anchor=p.evaluate('__VIEWPORT_A__.snapshot().twoD.centerWorld');berr=[]
  for w,h in SIZES:
   settle(p,w,h);q=p.evaluate('a=>({p:__VIEWPORT_A__.worldToScreen(a.x,a.y),v:AEGIS_VIEWPORT.twoD})',anchor);berr.append(math.hypot(q['p']['x']-q['v']['cx'],q['p']['y']-q['v']['cy']))
  records['pan2D']={'centerWorld':anchor,'errorsPx':berr};check('B.panCenter',max(berr)<=1)
  # Native wheel, button steps and pinch (TouchEvent driven through real listener).
  p.evaluate('__VIEWPORT_A__.setDistance(120)');p.mouse.move(422,100);p.mouse.wheel(0,-80);p.wait_for_timeout(80);wheel=p.evaluate('__VIEWPORT_A__.snapshot().twoD.tacticalViewKm');check('zoom.wheel',wheel==40)
  p.evaluate('''()=>{const c=document.getElementById('c'),fire=(type,d)=>{const ts=[new Touch({identifier:1,target:c,clientX:100,clientY:200}),new Touch({identifier:2,target:c,clientX:100+d,clientY:200})];c.dispatchEvent(new TouchEvent(type,{touches:ts,bubbles:true,cancelable:true}));};__VIEWPORT_A__.setDistance(120);fire('touchstart',100);fire('touchmove',200);}''');check('zoom.pinch',abs(p.evaluate('__VIEWPORT_A__.snapshot().twoD.tacticalViewKm')-60)<1e-10)
  p.evaluate('async()=>{const v=__WIP148_3D_VIEW__;await v.open();v.active=false;v.c12ApplyPreset("LOW");v.resetCamera();}')
  def projection():return p.evaluate('''()=>{const v=__WIP148_3D_VIEW__;v.resize();const st=get3DRenderState();v.syncWorldEpochWip14A(st);v.syncRenderOriginWip14A(st);v.applyShipBodyFrame(st);v.scene.updateMatrixWorld(true);v.syncCamera();const a=__VIEWPORT_A__,s=a.snapshot(),L=__AEGIS_ACTIVE_SHIP_RUNTIME__.profileId.startsWith('CG')?172.8:154.6;return {size:[AEGIS_VIEWPORT.raw.w,AEGIS_VIEWPORT.raw.h],s,aim:a.projectShipPoint(),bow:a.projectShipPoint(L/2,0,0),stern:a.projectShipPoint(-L/2,0,0)};}''')
  drows=[]
  for w,h in SIZES:
   settle(p,w,h);r=projection();v=r['s']['viewport']['threeD'];r['centerErrorPx']=math.hypot(r['aim']['x']-v['cx'],r['aim']['y']-v['cy']);r['lengthOverShortSide']=math.hypot(r['bow']['x']-r['stern']['x'],r['bow']['y']-r['stern']['y'])/v['shortSide'];r['endsInside']=all(v['x']<=r[k]['x']<=v['x']+v['w']and v['y']<=r[k]['y']<=v['y']+v['h']for k in ['bow','stern']);check(f'D.{w}x{h}.center',r['centerErrorPx']<=.01*v['shortSide']);check(f'D.{w}x{h}.inside',r['endsInside']);drows.append(r)
  check('D.lengthInvariant',max(r['lengthOverShortSide']for r in drows)/min(r['lengthOverShortSide']for r in drows)-1<=.03);records['projection']=drows
  settle(p,1400,900);p.evaluate('__WIP148_3D_VIEW__.active=true');p.mouse.move(700,400);p.mouse.down(button='right');p.mouse.move(770,445,steps=4);p.mouse.up(button='right');p.evaluate('__WIP148_3D_VIEW__.active=false');pans=[]
  for w,h in SIZES:
   settle(p,w,h);r=projection();v=r['s']['viewport']['threeD'];pans.append({'size':[w,h],'x':(r['aim']['x']-v['cx'])/v['shortSide'],'y':(r['aim']['y']-v['cy'])/v['shortSide'],'pan':r['s']['threeD']['pan']})
  records['pan3D']=pans;check('E.panInvariant',max(math.hypot(r['x']-pans[0]['x'],r['y']-pans[0]['y'])for r in pans)<=.02);check('E.actualPan',abs(pans[0]['x'])>.01)
  # No GPU workload in burst: actual Chromium/CDP sizes, normal viewport RAF.
  p.evaluate('__WIP148_3D_VIEW__.resetCamera();__VIEWPORT_A__.setPan(0,0)');cdp=p.context.new_cdp_session(p);rng=random.Random(173);burst=[(rng.randrange(380,1500),rng.randrange(350,1000))for _ in range(29)]+[(600,900)];start=time.monotonic()
  for w,h in burst:cdp.send('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1,'mobile':False})
  elapsed=time.monotonic()-start;p.wait_for_timeout(500);burstResult=projection();cdp.send('Emulation.setDeviceMetricsOverride',{'width':600,'height':900,'deviceScaleFactor':1,'mobile':False});p.wait_for_timeout(400);singleResult=projection()
  fields=lambda r:{k:r[k]for k in ['aim','bow','stern','lengthOverShortSide']if k in r};check('F.sameResult',fields(burstResult)==fields(singleResult));check('F.finite',all(math.isfinite(v)for k in ['aim','bow','stern']for v in burstResult[k].values()));check('F.30WithinSecond',elapsed<=1);records['burst']={'count':30,'elapsedS':elapsed,'sizes':burst,'burst':burstResult,'single':singleResult}
  # Delayed panel reflow after orientation: RO must catch an event after 150ms.
  cdp.send('Emulation.clearDeviceMetricsOverride');settle(p,390,844);settle(p,844,390);beforeG=p.evaluate('AEGIS_VIEWPORT.twoD.h');beforeGDistance=p.evaluate('__VIEWPORT_A__.snapshot().twoD.tacticalViewKm');p.evaluate("()=>{window.__vpDelayedLayout=null;const start=performance.now();setTimeout(()=>{const e=document.getElementById('controlDeckPanel'),before=e.getBoundingClientRect().toJSON();e.style.height=(before.height+40)+'px';e.style.maxHeight='none';requestAnimationFrame(()=>window.__vpDelayedLayout={before,after:e.getBoundingClientRect().toJSON(),delayMs:performance.now()-start});},200);}");p.wait_for_function('window.__vpDelayedLayout&&Math.abs(AEGIS_VIEWPORT.twoD.y+AEGIS_VIEWPORT.twoD.h-document.getElementById("controlDeckPanel").getBoundingClientRect().top)<.1');p.wait_for_timeout(180);layout=p.evaluate('window.__vpDelayedLayout');records['delayedLayout']=layout;g=projection();v=g['s']['viewport'];check('G.panelAfterDelay',layout['delayMs']>=200 and layout['after']['height']>layout['before']['height']+10 and abs(v['twoD']['y']+v['twoD']['h']-layout['after']['top'])<=1);check('G.twoDCenter',math.hypot(g['s']['twoD']['ownship']['x']-v['twoD']['cx'],g['s']['twoD']['ownship']['y']-v['twoD']['cy'])<=1 if not any(g['s']['twoD']['pan'].values())else True);check('G.threeDCenter',math.hypot(g['aim']['x']-v['threeD']['cx'],g['aim']['y']-v['threeD']['cy'])<=.01*v['threeD']['shortSide']);gv=v['threeD'];gLength=math.hypot(g['bow']['x']-g['stern']['x'],g['bow']['y']-g['stern']['y'])/gv['shortSide'];check('G.lengthInvariant',abs(gLength/drows[-1]['lengthOverShortSide']-1)<=.03);check('G.endpointsInside',all(gv['x']<=g[k]['x']<=gv['x']+gv['w']and gv['y']<=g[k]['y']<=gv['y']+gv['h']for k in ['bow','stern']));check('G.distanceInvariant',g['s']['twoD']['tacticalViewKm']==beforeGDistance);records['delayed']=g
  # Safe-area/VV offsets, independent of unsupported desktop emulation of notches.
  p.evaluate("()=>{document.getElementById('controlDeckPanel').style.height='';document.getElementById('controlDeckPanel').style.maxHeight='';const e=document.getElementById('aegisSafeAreaProbeVpA');e.style.padding='12px 23px 18px 17px';__VIEWPORT_A__.setPan(0,0);AEGIS_VIEWPORT.schedule();}");p.wait_for_timeout(400);r=projection();v=r['s']['viewport'];check('safeArea.inset',v['layout']['x']==17 and v['layout']['y']==12);check('safeArea.offsetProjection',math.hypot(r['aim']['x']-v['threeD']['cx'],r['aim']['y']-v['threeD']['cy'])<1);check('safeArea.viewOffset',r['s']['threeD']['viewOffset']['enabled']);records['safeArea']=r
  p.evaluate("document.getElementById('aegisSafeAreaProbeVpA').style.padding='0px';AEGIS_VIEWPORT.schedule()");cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1.25});p.wait_for_timeout(400);vv=projection();sv=vv['s']['viewport'];check('visualViewport.actualScale',abs(sv['raw']['w']-844/1.25)<1);check('visualViewport.center',math.hypot(vv['aim']['x']-sv['threeD']['cx'],vv['aim']['y']-sv['threeD']['cy'])<=1);edge=sv['panels'][0];check('visualViewport.edgeClipped',not edge['reduces']or abs(sv['twoD']['y']+sv['twoD']['h']-edge['y'])<1);records['visualViewport']=vv;cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1})
  records['nativeFrames']=[]
  for w,h in [(600,900),(390,844)]:
   settle(p,w,h);r=p.evaluate('''()=>{const v=__WIP148_3D_VIEW__,d=__NAVAL_SIM_DIAG__,before=JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());v.active=true;v.render(performance.now());v.active=false;return {readOnly:before===JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B()),glError:v.renderer.getContext().getError(),camera:__VIEWPORT_A__.snapshot().threeD};}''');check(f'native.{w}.readonly',r['readOnly']and r['glError']==0);records['nativeFrames'].append(r);p.screenshot(path=str(a.out/f'ownship-{w}.png'))
  check('core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));b.close()
 out={'pass':all(checks.values())and not errors,'checks':checks,'rows':rows,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'limits':'CSS-size/touch emulation and SwiftShader, not hardware phone performance. D center is original orbit aim point; bow/stern length/containment separately checked. No ownship attack track or direct-tap designation introduced.'};(a.out/'viewport.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors,'burstS':records['burst']['elapsedS']}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
