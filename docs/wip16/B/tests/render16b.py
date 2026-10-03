import argparse, functools, http.server, json, os, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');args=p.parse_args()
src=Path(args.html).resolve();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(src.parent)))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{server.server_port}/{src.name}?view3d=1',wait_until='load',timeout=90000)
    page.wait_for_function('!!window.__WIP148_3D_VIEW__?.ready && !!window.__NAVAL_SIM_DIAG__?.runV48Wip03StructuralProbe',timeout=90000)
    page.evaluate('''() => {
      const v=window.__WIP148_3D_VIEW__,d=window.__NAVAL_SIM_DIAG__;
      window.__B16_TRACE__={jobs:0,steps:0,commits:0,anchors:[]};const trace=window.__B16_TRACE__;
      const gen=v.buildDamageScarsV3;v.buildDamageScarsV3=function*(...args){trace.jobs++;try{for(const r of gen.apply(this,args)){trace.steps++;yield r;}trace.commits++;}catch(e){trace.error=String(e.stack||e);throw e;}};
      const find=v.findDamageSurfaceV2;v.findDamageSurfaceV2=function(...args){const r=find.apply(this,args);trace.anchors.push({id:args[0].id,mesh:r?.mesh?.name||null,candidates:args[1].length});return r;};
      document.getElementById('wip125DepartBtn')?.click();d.ciwsB1Closure.setPaused(true);
      window.__B16_PROBE__=d.runV48Wip03StructuralProbe({hits:2,label:'Kh-32',xM:12,zM:-3.5,side:'STARBOARD'});
      d.runV48Wip07CrewDamageProbe({readCount:0});
      window.__B16_STATE__=JSON.stringify({flood:d.damageFloodSnapshotV1(),structure:d.v48Wip03StructuralState(),visual:d.v48Wip03DamageVisualState(),interior:d.v48Wip06InteriorState(),crew:d.v48Wip07CrewState()});
      v.resetCamera();if(!v.interiorTopologyVisible)v.toggleInteriorTopology();
    }''')
    started=time.monotonic();samples=[]
    while time.monotonic()-started<65:
      page.wait_for_timeout(1000)
      r=page.evaluate('''() => {const v=window.__WIP148_3D_VIEW__,contract=v.contractAudit();delete contract.renderState;return {damage:v.damageAuditV48Wip03(),stats:v.damageBuildStatsV3,trace:window.__B16_TRACE__,maxStepMs:v._c13MaxDamageStepMs,contract,drawDeferrals:v._wip16bOpeningDrawDeferrals||0};}''')
      samples.append({'elapsedS':round(time.monotonic()-started,2),**r})
      if not r['damage']['pending'] or errors:break
    extra=page.evaluate('''() => {
      const v=window.__WIP148_3D_VIEW__,d=window.__NAVAL_SIM_DIAG__,T=v.THREE,rows=[];
      for(const [id,scar]of v.damageScarVisuals??[]){if(!['ENTRY','EXIT'].includes(scar.scar.impactRole))continue;const b=scar.binding,proxy=new T.Mesh(b.mesh.geometry,new T.MeshBasicMaterial({side:T.DoubleSide}));proxy.updateMatrixWorld(true);const ray=new T.Raycaster(b.point.clone().addScaledVector(b.normal,.1),b.normal.clone().negate(),0,.2);rows.push({id,mesh:b.mesh.name,cut:b.mesh.geometry!==v.damageOriginalMeshesV2.get(b.mesh)?.geometry,apertureClear:ray.intersectObject(proxy,false).length===0});proxy.material.dispose();}
      return {core:window.__CORE_SELFTEST_FAILURES__,interior:v.interiorAuditV48Wip06(),crew:v.crewAuditV48Wip07(),openings:rows,
        renderReadOnly:window.__B16_STATE__===JSON.stringify({flood:d.damageFloodSnapshotV1(),structure:d.v48Wip03StructuralState(),visual:d.v48Wip03DamageVisualState(),interior:d.v48Wip06InteriorState(),crew:d.v48Wip07CrewState()})};
    }''')
    result={'source':src.name,'errors':errors,'samples':samples,'extra':extra}
    (out/'state.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    # CDP capture does not wait for two new animation frames on a software GPU.
    import base64
    cdp=page.context.new_cdp_session(page)
    for name,yaw in [('starboard',1.0),('port',-1.0)]:
      page.evaluate('yaw=>{const v=window.__WIP148_3D_VIEW__;v.orbit.yaw=yaw;v.c12ApplyPreset("LOW");v.syncCamera();v.renderer.render(v.scene,v.camera);}',yaw)
      capture=cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})
      (out/f'{name}.png').write_bytes(base64.b64decode(capture['data']))
    restore=page.evaluate('''() => {const v=window.__WIP148_3D_VIEW__,sources=[...v.damageOriginalMeshesV2??[]];v.syncDamageScarsV1({shipDamageVisual:{scars:[]}});return {hadCuts:sources.some(([m,s])=>m.geometry===s.geometry),allGeometryRestored:sources.length>0&&sources.every(([m,s])=>m.geometry===s.geometry),visualsCleared:v.damageScarVisuals.size===0};}''')
    result['restore']=restore
    checks={'coreZero':extra['core']==[],'pageErrorsZero':errors==[],'contract':r['contract']['pass'],
      'dualHullOpenings':r['damage']['dualHullOpenings'],'settled':not r['damage']['pending'] and r['damage']['unmatched']==0,
      'actualMeshCuts':len(extra['openings'])==2 and all(q['cut'] and q['apertureClear'] for q in extra['openings']),
      'renderReadOnly':extra['renderReadOnly'],'geometryRestore':restore['allGeometryRestored'] and restore['visualsCleared'],
      'interior':extra['interior']['allSpacesRepresented'] and extra['interior']['allPortalsRepresented'] and extra['interior']['allEquipmentRepresented'] and extra['interior']['superstructureContained'],
      'crew':extra['crew']['allPersonnelRepresented'] and extra['crew']['instanceBatches']==1}
    result['checks']=checks;result['pass']=all(checks.values());(out/'state.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'source':src.name,'checks':checks,'trace':r['trace'],'drawDeferrals':r['drawDeferrals'],'pass':result['pass']}))
    browser.close()
server.shutdown()
if not result['pass']:raise SystemExit(1)
