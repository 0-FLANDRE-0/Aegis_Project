"""Real multi-Kh32 AUTO near impact under native 3D/RAF and fixed ticks."""
from pathlib import Path
import argparse,base64,hashlib,json,time
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--count',type=int,default=6);p.add_argument('--deadline',type=int,default=240);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];crashes=[];samples=[];checks={};started=time.monotonic()
observe='''()=>{const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__,st=d.bunkerRenderState(),t=window.__I_NATIVE_RAID__;return {step:d.ciwsB1Closure.snapshot().simStepCounter,time:st.timeS,hostile:st.enemyAsms.length,sam:st.missiles.length,ram:st.missiles.filter(m=>m.kind==='RAM').length,nearest:st.enemyAsms.length?Math.min(...st.enemyAsms.map(m=>Math.hypot(m.xM-st.ship.worldXM,m.zM-st.ship.worldYM,m.yM))):null,phases:st.enemyAsms.map(m=>m.phase),calls:t.calls,draws:t.draws,lost:t.lost,memory:{...v.renderer.info.memory},damage:v.damageAuditV48Wip03(),scars:st.shipDamageVisual?.scars?.length??0,active:v.active,simFault:window.__WIP125_DIAG__.wip150RuntimeFault(),presentationFault:window.__WIP125_DIAG__.wip150PresentationFault()};}'''
with sync_playwright()as pw:
 b=launch(pw,webgl=True);page=load(b,served_bytes(a.html),webgl=True,seed=174321,errors=errors);page.on('crash',lambda _:crashes.append('BROWSER_PAGE_CRASH'))
 page.evaluate('''n=>{const v=window.__WIP148_3D_VIEW__,d=window.__NAVAL_SIM_DIAG__;v.close();d.spawnRealKh32Regression({rangeKm:95,bearingDeg:0});for(let i=1;i<n;i++)d.wip13cSpawnInboundInsAsm('Kh-32');d.wip119SetMode('AUTO');d.profilerEnableV48Wip11A(true);d.profilerResetV48Wip11A();window.__I_NATIVE_RAID__={calls:0,draws:0,lost:0};const t=window.__I_NATIVE_RAID__,render=v.render,draw=v.renderer.render;v.render=function(...a){t.calls++;return render.apply(this,a)};v.renderer.render=function(...a){t.draws++;return draw.apply(this,a)};v.renderer.domElement.addEventListener('webglcontextlost',()=>t.lost++);}''',a.count)
 prefill=[]
 for frame in range(150):
  page.evaluate('window.__NAVAL_SIM_DIAG__.advanceFrameNoRender(1/60,64)');q=page.evaluate(observe)
  if frame%20==0:prefill.append(q)
  if q['nearest']is not None and q['nearest']<20000:break
  if not q['hostile']:break
 before=page.evaluate(observe);checks['RealThreatsReachNativeWindow']=before['hostile']>0
 page.evaluate('window.__WIP148_3D_VIEW__.open();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false);window.__NAVAL_SIM_DIAG__.setTimeScale(16)');nativeStart=time.monotonic()
 while time.monotonic()-nativeStart<a.deadline:
  page.wait_for_timeout(1000);q=page.evaluate(observe);samples.append({'elapsedWallS':round(time.monotonic()-nativeStart,2),**q})
  if len(samples)%10==0:print(json.dumps({k:q[k]for k in ['time','hostile','sam','ram','draws','scars','simFault','presentationFault']}),flush=True)
  if errors or crashes or q['lost']or q['simFault']or q['presentationFault']:break
  if q['time']-before['time']>=25 and q['hostile']==0 and q['draws']>=8:break
 end=page.evaluate(observe);page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');profiler=page.evaluate('window.__NAVAL_SIM_DIAG__.profilerSnapshotV48Wip11A()')
 checks['NativeFixedTicksContinue']=end['step']>before['step']+60*25;checks['Native3DFramesContinue']=end['draws']>=8 and end['calls']>=end['draws'];checks['ThreatWindowFinished']=end['hostile']==0;checks['NoRAMOnCG']=all(q['ram']==0 for q in samples);checks['NoSimFault']=end['simFault']is None;checks['NoPresentationFault']=end['presentationFault']is None;checks['NoGPUContextLoss']=end['lost']==0;checks['NoPageCrash']=not crashes;checks['NoPageErrors']=not errors;checks['CoreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[]
 cdp=page.context.new_cdp_session(page);(out/'native-raid.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']));page.close();b.close()
r={'schema':'AEGIS_NATIVE_REAL_KH32_RAID_I','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'parameters':vars(a),'bootSeed':174321,'fixedCadenceHz':60,'nativeTimeScale':16,'prefill':'REAL_FIXED_TICKS_IN_2D_UNTIL_20KM_SLANT_RANGE__NO_SYNTHETIC_TRACKS','geometryQueueManuallyAdvanced':False,'checks':checks,'before':before,'prefillSamples':prefill,'samples':samples,'end':end,'profiler':profiler,'errors':errors,'crashes':crashes,'elapsedWallS':time.monotonic()-started,'pass':all(checks.values())};(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'crashes':crashes,'pass':r['pass']},ensure_ascii=False),flush=True)
if not r['pass']:raise SystemExit(1)
