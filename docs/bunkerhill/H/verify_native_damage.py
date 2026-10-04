"""Native RAF/WebGL damage, controls, topology and restart; no queue shortcuts."""
from pathlib import Path
import argparse,base64,hashlib,json,os,shutil,time
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--ship',default='CG_52_LATE_TICONDEROGA');p.add_argument('--deadline',type=int,default=240);a=p.parse_args()
src,out=Path(a.html),Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];console=[];checks={};details={}
with sync_playwright()as pw:
    b=pw.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE')or shutil.which('chromium')or None,headless=True,args=['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':640,'height':480});page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:console.append(m.text[:1000])if m.type=='error'else None)
    page.add_init_script('window.__NAVAL_SIM_SEED__=0x6d2b79f5');page.route('https://aegis.test/**',lambda r:r.fulfill(body=src.read_bytes(),content_type='text/html'))
    page.goto('https://aegis.test/candidate?view3d=1',wait_until='load',timeout=90000);page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000)
    page.locator('#aegisShipSelect').select_option(a.ship);page.locator('#aegisShipConfirmBtn').click();page.wait_for_function('window.C55Packaging?.ready&&window.__WIP148_3D_VIEW__?.ready',timeout=120000)
    page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__,d=window.__NAVAL_SIM_DIAG__;v.c12ApplyPreset('LOW');document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);
      window.__NATIVE_DAMAGE_TRACE__={calls:0,draws:0,steps:0,drawTimes:[]};const t=window.__NATIVE_DAMAGE_TRACE__,r=v.render,draw=v.renderer.render,sync=v.syncDamageScarsV1;
      v.render=function(...args){t.calls++;return r.apply(this,args)};v.renderer.render=function(...args){t.draws++;t.drawTimes.push(performance.now());if(t.drawTimes.length>300)t.drawTimes.shift();return draw.apply(this,args)};
      v.syncDamageScarsV1=function(...args){const result=sync.apply(this,args);t.steps+=this.damageBuildStatsV3?.steps??0;return result};}''')
    # Independently decode the immutable supplied asset, then compare every
    # indexed vertex in each compacted chunk. No geometry queue is advanced.
    if a.ship=='CG_52_LATE_TICONDEROGA':
        source=page.evaluate('''async()=>{const v=window.__WIP148_3D_VIEW__,T=v.THREE,read=async(id,json=true)=>{const node=document.getElementById(id),bytes=Uint8Array.from(atob(node.textContent.trim()),c=>c.charCodeAt(0)),buf=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();return json?JSON.parse(new TextDecoder().decode(buf)):buf;},
          meta=await read('cg52-meta'),buf=await read('cg52-geo',false),palette=meta.palette.map(p=>new T.Color(p.color)),rows=[];
          for(const stat of meta.statics)for(let mi=0;mi<stat.meshes.length;mi++){const m=stat.meshes[mi],part=v._bunkerAsset.parts.get('CG52_'+stat.cat+'_'+mi);
            if(!part?.isGroup||!['hull','fittings','weapons'].includes(stat.cat))continue;
            const q=new Uint16Array(buf,m.pos[0],m.pos[1]),position=new Float32Array(q.length),pid=new Uint8Array(buf,m.pid[0],m.pid[1]),color=new Float32Array(q.length);
            for(let i=0;i<q.length/3;i++)for(let k=0;k<3;k++){position[3*i+k]=m.qmin[k]+q[3*i+k]*m.qscale[k];color[3*i+k]=palette[pid[i]][['r','g','b'][k]];}
            const attrs={position:{data:position,size:3},normal:{data:new Int8Array(buf,m.nor[0],m.nor[1]),size:3,normalized:true},color:{data:color,size:3},pid:{data:pid,size:1}};
            if(m.uv)attrs.uv={data:new Float32Array(buf,m.uv[0],m.uv[1]),size:2};
            const idx=m.i32?new Uint32Array(buf,m.idx[0],m.idx[1]):new Uint16Array(buf,m.idx[0],m.idx[1]),bins=new Map();
            for(let i=0;i<idx.length;i+=3){const ids=[idx[i],idx[i+1],idx[i+2]],avg=k=>ids.reduce((n,j)=>n+position[j*3+k],0)/3,key=[Math.floor(avg(0)/24),Math.floor(avg(1)/6),Math.floor(avg(2)/8)].join(':');if(!bins.has(key))bins.set(key,[]);bins.get(key).push(...ids);}
            let mismatches=0,checked=0,unused=0,negative=false;
            for(const [key,ids]of bins){const mesh=part.children.find(o=>o.name===part.name+':'+key),g=mesh?.geometry;if(!g||g.index.count!==ids.length){mismatches++;continue;}
              const used=new Set(g.index.array);unused+=g.attributes.position.count-used.size;
              for(const [name,attr]of Object.entries(attrs)){const actual=g.attributes[name];if(!actual||actual.itemSize!==attr.size||actual.normalized!==!!attr.normalized||actual.array.constructor!==attr.data.constructor){mismatches++;continue;}
                for(let i=0;i<ids.length;i++)for(let k=0;k<attr.size;k++){checked++;if(actual.array[g.index.array[i]*attr.size+k]!==attr.data[ids[i]*attr.size+k])mismatches++;}}
              if(!negative){const actual=g.attributes.position,index=g.index.array[0]*3,original=actual.array[index];actual.array[index]=original+.01;negative=actual.array[index]!==position[ids[0]*3];actual.array[index]=original;}
            }
            rows.push({part:part.name,triangles:idx.length/3,chunks:bins.size,checkedComponents:checked,mismatches,unusedVertices:unused,perturbedVertexRejected:negative});
          }
          return {rows,pass:rows.length===3&&rows.every(q=>q.mismatches===0&&q.unusedVertices===0&&q.perturbedVertexRejected)};}''')
        details['compactSourceAttributes']=source;checks['allCompactedSourceAttributesExact']=source['pass']
    page.wait_for_timeout(1000)
    def observe():return page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__,t=window.__NATIVE_DAMAGE_TRACE__;return {calls:t.calls,draws:t.draws,steps:t.steps,lastDrawAgeMs:performance.now()-(t.drawTimes.at(-1)??performance.now()),damage:v.damageAuditV48Wip03(),stats:v.damageBuildStatsV3,deferrals:v._wip16bOpeningDrawDeferrals??0,camera:v.camera.matrixWorld.toArray(),orbit:{...v.orbit}};}''')
    before=observe();page.evaluate("window.__NAVAL_SIM_DIAG__.runV48Wip03StructuralProbe({hits:2,label:'Kh-32',xM:12,zM:-3.5,side:'STARBOARD'})");started=time.monotonic();samples=[]
    # Orbit via real pointer events while the mandatory holes are pending.
    canvas=page.locator('#external3DCanvas').bounding_box();page.mouse.move(canvas['x']+canvas['width']*.6,canvas['y']+canvas['height']*.45);page.mouse.down();page.mouse.move(canvas['x']+canvas['width']*.6+45,canvas['y']+canvas['height']*.45+12,steps=5);page.mouse.up();page.wait_for_timeout(2500);dragged=observe()
    checks['cameraRespondsDuringPendingDamage']=before['camera']!=dragged['camera']and dragged['draws']>before['draws'];details['cameraDuringDamage']={'before':before['orbit'],'after':dragged['orbit']}
    # Native game RAF must continue fixed simulation ticks alongside 3D work.
    tick0=page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(false).simStepCounter');tick_started=time.monotonic()
    # Software WebGL can take several seconds per native frame. Wait for an
    # observed fixed tick instead of assuming a frame finishes within 2.5 s.
    # This snapshot is read-only; no manual simulate/advance call is allowed.
    page.wait_for_function('tick=>window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter>tick',arg=tick0,polling=200,timeout=30000)
    tick1=page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true).simStepCounter');checks['nativeSimulationContinues']=tick1>tick0;details['nativeTicks']={'before':tick0,'after':tick1,'observedWallS':round(time.monotonic()-tick_started,3)}
    while time.monotonic()-started<a.deadline:
        page.wait_for_timeout(1000);row=observe();samples.append({'elapsedS':round(time.monotonic()-started,2),**row})
        if len(samples)%10==0:print(json.dumps({'elapsedS':samples[-1]['elapsedS'],'draws':row['draws'],'pending':row['damage']['pending'],'steps':row['steps']}),flush=True)
        if not row['damage']['pending']or errors:break
    details['samples']=samples;settled=samples[-1];checks['nativeOpeningCommit']=not settled['damage']['pending']and settled['damage']['dualHullOpenings']and settled['damage']['unmatched']==0
    pending=[q for q in samples if q['damage']['pending']];checks['framesDrawnWhilePending']=bool(pending)and pending[-1]['draws']-before['draws']>=3;checks['noDrawDeferrals']=all(q['deferrals']==0 for q in samples)
    geometry=page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__,T=v.THREE,rows=[];for(const [id,scar]of v.damageScarVisuals??[]){if(!['ENTRY','EXIT'].includes(scar.scar.impactRole))continue;const b=scar.binding,proxy=new T.Mesh(b.mesh.geometry,new T.MeshBasicMaterial({side:T.DoubleSide}));proxy.updateMatrixWorld(true);const ray=new T.Raycaster(b.point.clone().addScaledVector(b.normal,.1),b.normal.clone().negate(),0,.2);rows.push({id,mesh:b.mesh.name,cut:b.mesh.geometry!==v.damageOriginalMeshesV2.get(b.mesh)?.geometry,apertureClear:ray.intersectObject(proxy,false).length===0});proxy.material.dispose();}
      const contract=v.contractAudit();delete contract.renderState;return {openings:rows,contract,cutColorsPreserved:[...v.damageOriginalMeshesV2].filter(([m,s])=>m.geometry!==s.geometry).every(([m])=>m.geometry.attributes.color?.count===m.geometry.attributes.position.count)};}''')
    details['geometry']=geometry;checks['actualRayOpenings']=len(geometry['openings'])==2 and all(q['cut']and q['apertureClear']for q in geometry['openings']);checks['renderContract']=geometry['contract']['pass']
    if a.ship=='CG_52_LATE_TICONDEROGA':checks['cutVertexColorsPreserved']=geometry['cutColorsPreserved']
    cdp=page.context.new_cdp_session(page)
    def capture(name):(out/name).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
    capture('native-impact.png')
    # Open the existing Controls/category drawer before using its real buttons.
    def control_click(ident):
        if page.locator('#c14ControlsToggle').get_attribute('aria-expanded')!='true':page.locator('#c14ControlsToggle').click()
        panel=page.evaluate("id=>{const target=document.getElementById(id);for(const b of document.querySelectorAll('.c15-category')){const p=document.getElementById(b.getAttribute('aria-controls'));if(p?.contains(target))return {id:p.id,open:b.getAttribute('aria-expanded')==='true'};}return null;}",ident)
        if panel and not panel['open']:page.locator('.c15-category[aria-controls="'+panel['id']+'"]').click()
        page.locator('#'+ident).click()
    # Actual 2D/3D button paths, followed by a native renderer frame.
    fingerprint=page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B())');control_click('external3DBackBtn');page.wait_for_timeout(300)
    page.evaluate('window.__WIP148_3D_VIEW__.open()');page.wait_for_timeout(1500)
    checks['viewSwitchNoAuthorityMutation']=fingerprint==page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B())')
    # Restart cancels optional presentation work and restores real source meshes
    # through the next native frame, not a direct syncDamageScars call.
    page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__;window.__NATIVE_ORIGINALS__=[...v.damageOriginalMeshesV2];window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);}''')
    page.wait_for_function('''()=>{const v=window.__WIP148_3D_VIEW__;return !v._damageJobV3&&v.damageScarVisuals?.size===0&&window.__NATIVE_ORIGINALS__.every(([m,s])=>m.geometry===s.geometry);}''',timeout=90000)
    restored=observe();checks['nativeRestartRestoresGeometry']=restored['draws']>settled['draws']and not restored['damage']['pending'];details['restore']=restored
    control_click('external3DInteriorBtn');page.wait_for_timeout(1500)
    interior=page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__;return {interior:v.interiorAuditV48Wip06(),crew:v.crewAuditV48Wip07(),core:window.__CORE_SELFTEST_FAILURES__};}''');details['interior']=interior
    checks['allInteriorGeometryRepresented']=all(interior['interior'][k]for k in ['allSpacesRepresented','allPortalsRepresented','allEquipmentRepresented','superstructureContained']);checks['allInteriorBoundsContained']=interior['interior']['allInteriorContained']and interior['interior']['outsideInteriorVertices']==0;checks['allUpperDecksAndHangarsRepresented']=interior['interior']['verticalShellFilled'];checks['allCrewRepresented']=interior['crew']['allPersonnelRepresented']and interior['crew']['instanceBatches']==1;checks['coreZero']=interior['core']==[]
    if page.locator('#c14ControlsToggle').get_attribute('aria-expanded')=='true':page.locator('#c14ControlsToggle').click()
    capture('native-upper-interior.png');b.close()
checks['pageErrorsZero']=errors==[];checks['consoleErrorsZero']=console==[];result={'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'ship':a.ship,'seed':0x6d2b79f5,'viewport':{'width':640,'height':480},'queueMode':'NATIVE_RAF_ONLY','controlledPresentationSlices':0,'checks':checks,'details':details,'errors':errors,'console':console,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'elapsedS':settled['elapsedS'],'errors':errors,'console':console,'pass':result['pass']},ensure_ascii=False))
if not result['pass']:raise SystemExit(1)
