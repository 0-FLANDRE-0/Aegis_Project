"""Native WebGL frames, world raft poses, people instances and resource lifetime."""
from pathlib import Path
import argparse,json,hashlib,base64
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);checks={};details={};errors=[];crashes=[]
with sync_playwright()as pw:
 b=launch(pw,webgl=True);page=load(b,served_bytes(a.html),webgl=True,errors=errors);page.on('crash',lambda _:crashes.append('PAGE_CRASH'))
 page.evaluate("""()=>{const v=window.__WIP148_3D_VIEW__,d=window.__NAVAL_SIM_DIAG__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__;v.close();d._resetShipTest();w.scenario.mode='MISSION';w.world.entities.aircraft.length=0;w.world.entities.surfaceContacts.length=0;d.setEmcon(true);d.wip13a3SetManualWeather({hsM:0,windSpeedMps:6,windDirectionDeg:20});window.__AEGIS_ACTIVE_SHIP_RUNTIME__.crew.abandon();d.stepTicks(9600);window.__K_RAFT_DRAWS__={calls:0,lost:0};const orig=v.renderer.render;v.renderer.render=function(...args){window.__K_RAFT_DRAWS__.calls++;return orig.apply(this,args);};v.renderer.domElement.addEventListener('webglcontextlost',()=>window.__K_RAFT_DRAWS__.lost++);v.orbit.yaw=Math.PI;v.orbit.pitch=.38;v.orbit.distance=170;v.open();}""")
 before=page.evaluate('window.__NAVAL_SIM_DIAG__.rescueSnapshotK()');page.wait_for_function('window.__K_RAFT_DRAWS__.calls>=4',timeout=90000)
 audit=page.evaluate('window.__WIP148_3D_VIEW__.rescueRaftAuditK()');details['native']=audit
 checks['all14RaftsDisplayed']=len(audit['rows'])==len(audit['authoritative'])==14
 checks['actual330PeopleInstances']=sum(q['persons']for q in audit['rows'])==330 and all(q['persons']==q['jackets']==q['userData']['persons']for q in audit['rows'])
 states={q['id']:q for q in audit['authoritative']};checks['worldParentAndXY']=all(q['worldParent']and q['parent']=='SURVIVAL_RAFTS_WORLD'and q['position']['x']==states[q['id']]['xM']and q['position']['z']==states[q['id']]['zM']for q in audit['rows'])
 checks['drawsReadOnlyWhilePaused']=before==page.evaluate('window.__NAVAL_SIM_DIAG__.rescueSnapshotK()')and audit['readOnly']
 checks['nativeNoFault']=page.evaluate('window.__WIP125_DIAG__.wip150RuntimeFault()===null&&window.__WIP125_DIAG__.wip150PresentationFault()===null&&window.__K_RAFT_DRAWS__.lost===0')
 cdp=page.context.new_cdp_session(page);(out/'raft-wide-native.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
 # Camera-only close-up fixture: no geometry queue calls or simulation changes.
 page.evaluate("""()=>{const v=window.__WIP148_3D_VIEW__;v._kOriginalSyncCamera=v.syncCamera;v.syncCamera=function(){const raft=this.rescueRaftVisualsK.values().next().value.root,p=raft.position,o=this.renderOriginWip14A;this.camera.position.set(p.x-o.x+8,p.y+6,p.z-o.z+9);this.camera.lookAt(p.x-o.x,p.y+.65,p.z-o.z);};}""");page.wait_for_timeout(1500)
 (out/'raft-close-native.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
 page.evaluate('()=>{window.__WIP148_3D_VIEW__.syncCamera=window.__WIP148_3D_VIEW__._kOriginalSyncCamera;}')
 resources=[]
 for i in range(3):
    q=page.evaluate("""()=>{const v=window.__WIP148_3D_VIEW__,d=window.__NAVAL_SIM_DIAG__;window.__K_RAFT_DISPOSE__=0;const meshes=[];for(const x of v.rescueRaftVisualsK.values()){for(const m of [x.heads,x.jackets]){m.addEventListener('dispose',()=>window.__K_RAFT_DISPOSE__++);meshes.push(m);}}const geometry=v._rescueResourcesK.tube;window.__AEGIS_ACTIVE_SHIP_RUNTIME__.crew.reset();return {expected:meshes.length,geometryUuid:geometry.uuid};}""")
    page.wait_for_function('window.__WIP148_3D_VIEW__.rescueRaftVisualsK.size===0',timeout=90000)
    removed=page.evaluate('({disposed:window.__K_RAFT_DISPOSE__,memory:{...window.__WIP148_3D_VIEW__.renderer.info.memory},world:window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.lifeRafts.length})')
    refill=page.evaluate("""()=>{const v=window.__WIP148_3D_VIEW__,d=window.__NAVAL_SIM_DIAG__,r=window.__AEGIS_ACTIVE_SHIP_RUNTIME__,w=window.__AEGIS_ENGAGEMENT_RUNTIME__;v.close();d._resetShipTest();w.scenario.mode='MISSION';w.world.entities.aircraft.length=0;w.world.entities.surfaceContacts.length=0;d.setEmcon(true);d.wip13a3SetManualWeather({hsM:0,windSpeedMps:6,windDirectionDeg:20});r.crew.abandon();d.stepTicks(9600);v.open();const c=r.crew.snapshot();return {summary:d.rescueSummaryK(),crew:{mode:c.mode,fit:c.fit,injured:c.injured,dead:c.dead,evacuated:c.evacuated},fault:window.__WIP125_DIAG__.wip150PresentationFault()};}""")
    print(json.dumps({'cycle':i,'refill':refill}),flush=True)
    page.wait_for_function('window.__WIP148_3D_VIEW__.rescueRaftVisualsK.size===14',timeout=90000)
    added=page.evaluate('({memory:{...window.__WIP148_3D_VIEW__.renderer.info.memory},geometryUuid:window.__WIP148_3D_VIEW__._rescueResourcesK.tube.uuid,counts:window.__NAVAL_SIM_DIAG__.rescueSummaryK()})')
    resources.append({'cycle':i,'before':q,'removed':removed,'added':added})
 checks['instanceBuffersDisposedOnce']=all(q['removed']['disposed']==q['before']['expected']==28 and q['removed']['world']==0 for q in resources)
 checks['sharedGeometryReused']=all(q['added']['geometryUuid']==q['before']['geometryUuid']for q in resources)
 checks['gpuMemoryStableAcross3Cycles']=len({json.dumps(q['added']['memory'],sort_keys=True)for q in resources})==1
 checks['noContextLoss']=page.evaluate('window.__K_RAFT_DRAWS__.lost===0');checks['coreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[];details['resources']=resources
 page.close();b.close()
checks['pageErrorsZero']=not errors;checks['noCrash']=not crashes
r={'schema':'AEGIS_RESCUE_NATIVE_3D_K_1','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'geometryQueueManuallyAdvanced':False,'checks':checks,'details':details,'errors':errors,'crashes':crashes,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'crashes':crashes,'pass':r['pass']}),flush=True)
if not r['pass']:raise SystemExit(1)
