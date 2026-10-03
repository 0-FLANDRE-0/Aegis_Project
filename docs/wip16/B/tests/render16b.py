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
      d.runV48Wip07CrewDamageProbe({readCount:0});v.resetCamera();if(!v.interiorTopologyVisible)v.toggleInteriorTopology();
    }''')
    started=time.monotonic();samples=[]
    while time.monotonic()-started<65:
      page.wait_for_timeout(1000)
      r=page.evaluate('''() => {const v=window.__WIP148_3D_VIEW__;return {damage:v.damageAuditV48Wip03(),stats:v.damageBuildStatsV3,trace:window.__B16_TRACE__,maxStepMs:v._c13MaxDamageStepMs,contract:v.contractAudit(),frames:v.c11Profiler?.snapshot?.()?.frames};}''')
      samples.append({'elapsedS':round(time.monotonic()-started,2),**r})
      if not r['damage']['pending'] or errors:break
    (out/'state.json').write_text(json.dumps({'source':src.name,'errors':errors,'samples':samples},indent=2),encoding='utf-8')
    page.screenshot(path=str(out/'render.png'))
    print(json.dumps({'source':src.name,'errors':errors,'damage':r['damage'],'trace':r['trace'],'contractPass':r['contract']['pass']}))
    browser.close()
server.shutdown()
