"""Independent rigid-source SPG pose checks and native missile retirement."""
from pathlib import Path
import argparse,base64,hashlib,json,time
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--main-override');p.add_argument('--baseline');p.add_argument('--cycles',type=int,default=4);a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];checks={};details={}
parts=json.loads((Path(__file__).resolve().parent/'spg-rigid-components.json').read_text())['assemblies']
pose_js='''async labels=>{const v=window.__WIP148_3D_VIEW__,T=v.THREE,read=async(id,json=true)=>{const bytes=Uint8Array.from(atob(document.getElementById(id).textContent.trim()),c=>c.charCodeAt(0)),buf=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();return json?JSON.parse(new TextDecoder().decode(buf)):buf;},meta=await read('cg52-meta'),buf=await read('cg52-geo',false),rows=[];
 for(let i=0;i<4;i++){const m=meta.assemblies.find(a=>a.id==='spg'+i).root.meshes[0],raw=new Uint16Array(buf,m.pos[0],m.pos[1]),pos=new Float32Array(raw.length),idx=new Uint16Array(buf,m.idx[0],m.idx[1]);for(let n=0;n<raw.length;n++)pos[n]=m.qmin[n%3]+raw[n]*m.qscale[n%3];
 const fixedParts=new Set(labels[i].components.filter(c=>c.min[1]<-.5||c.triangles===332).map(c=>c.id)),byTriangle=new Map();for(let n=0;n<idx.length;n+=3)byTriangle.set([idx[n],idx[n+1],idx[n+2]].join(':'),{tri:n/3,fixed:fixedParts.has(labels[i].triangleLabels[n/3])});
 const mount=v.spgMounts.get(i),meshes=[];mount.yaw.traverse(o=>{if(o.isMesh&&o.userData.sourceCG52)meshes.push(o)});
 const savedPitch=mount.pitch.rotation.z,savedYaw=mount.yaw.rotation.y;let maxError=0,represented=0,splitComponents=new Set(),ownerByComponent=new Map(),angles=[];
 for(const mesh of meshes){const ix=mesh.geometry.index.array;for(let n=0;n<ix.length;n+=3){const tri=byTriangle.get([ix[n],ix[n+1],ix[n+2]].join(':'));if(!tri)throw Error('SOURCE_SPG_TRIANGLE_NOT_FOUND');represented++;const label=labels[i].triangleLabels[tri.tri],owner=mesh.parent===mount.pitch?'PITCH':'BASE',old=ownerByComponent.get(label);if(old&&old!==owner)splitComponents.add(label);ownerByComponent.set(label,owner);}}
 for(const elevation of [0,15,45,85])for(const yaw of [-150,0,130]){const pitch=(i<2?1:-1)*elevation*Math.PI/180;mount.pitch.rotation.z=pitch;mount.yaw.rotation.y=yaw*Math.PI/180;mount.yaw.updateWorldMatrix(true,true);const inverse=mount.yaw.matrixWorld.clone().invert();let error=0;
   for(const mesh of meshes){const g=mesh.geometry,mat=inverse.clone().multiply(mesh.matrixWorld),ix=g.index.array;for(let n=0;n<ix.length;n+=3){const tri=byTriangle.get([ix[n],ix[n+1],ix[n+2]].join(':'));for(let j=0;j<3;j++){const k=ix[n+j],expected=new T.Vector3(pos[k*3],pos[k*3+1],pos[k*3+2]);if(!tri.fixed)expected.y-=.95;if(!tri.fixed)expected.applyAxisAngle(new T.Vector3(0,0,1),pitch);if(!tri.fixed)expected.y+=.95;const actual=new T.Vector3().fromBufferAttribute(g.attributes.position,k).applyMatrix4(mat);error=Math.max(error,actual.distanceTo(expected));}}}
   maxError=Math.max(maxError,error);angles.push({elevation,yaw,maxPositionErrorM:error});}
 mount.pitch.rotation.z=savedPitch;mount.yaw.rotation.y=savedYaw;mount.yaw.updateWorldMatrix(true,true);
 rows.push({id:i,sourceTriangles:idx.length/3,representedTriangles:represented,splitComponents:[...splitComponents],partOwners:[...ownerByComponent],maxPositionErrorM:maxError,angles});}
 return {rows,contract:v.contractAudit(),pass:rows.every(r=>r.representedTriangles===r.sourceTriangles&&r.splitComponents.length===0&&r.maxPositionErrorM<1e-6)};}'''
resource_setup='''()=>{const v=window.__WIP148_3D_VIEW__;window.__I_RESOURCES__={created:[],draws:0,lost:0};const t=window.__I_RESOURCES__,render=v.renderer.render;v.renderer.render=function(...args){t.draws++;return render.apply(this,args)};v.renderer.domElement.addEventListener('webglcontextlost',()=>t.lost++);return {draws:t.draws,memory:{...v.renderer.info.memory}};}'''
async_def='''()=>{const d=window.__NAVAL_SIM_DIAG__,e=window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities;d.createTerminalAsmFixture({label:'Kh-32',rangeKm:.09,bearingDeg:0,altM:27,speedMps:1200});const base=e.hostileMissiles[0];for(let i=1;i<6;i++){const q=structuredClone(base);q.id=base.id+i*10000;q.x=base.x-i*.3;q.y=base.y+i*.6;e.hostileMissiles.push(q);}return e.hostileMissiles.map(m=>m.id);}'''
watch='''()=>{const v=window.__WIP148_3D_VIEW__,t=window.__I_RESOURCES__,row={geometries:[],materials:[],textures:[],before:{...v.renderer.info.memory},draws:t.draws},gs=new Set(),ms=new Set(),ts=new Set();for(const r of v.asmVisuals.values())r.mesh.traverse(o=>{if(o.geometry)gs.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])if(m)ms.add(m)});for(const m of ms)for(const value of Object.values(m))if(value?.isTexture)ts.add(value);for(const [set,key]of [[gs,'geometries'],[ms,'materials'],[ts,'textures']])for(const object of set){const r={id:object.id,disposed:0};object.addEventListener('dispose',()=>r.disposed++);row[key].push(r);}t.created.push(row);return {geometries:gs.size,materials:ms.size,textures:ts.size,before:row.before,draws:t.draws};}'''
def inspect(page,tag):
    q=page.evaluate(pose_js,parts);details[tag+'SPG']=q
    before=page.evaluate(resource_setup);cycles=[]
    for cycle in range(a.cycles):
        ids=page.evaluate(async_def);page.wait_for_function('()=>window.__WIP148_3D_VIEW__.asmVisuals.size===6',timeout=90000)
        created=page.evaluate(watch);page.evaluate('window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.hostileMissiles.forEach(m=>m.alive=false)');page.wait_for_function('()=>window.__WIP148_3D_VIEW__.asmVisuals.size===0',timeout=90000)
        retired=page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__,t=window.__I_RESOURCES__,r=t.created.at(-1);return {memory:{...v.renderer.info.memory},draws:t.draws,disposed:{geometries:r.geometries.map(q=>q.disposed),materials:r.materials.map(q=>q.disposed),textures:r.textures.map(q=>q.disposed)},lost:t.lost};}''');cycles.append({'ids':ids,'created':created,'retired':retired})
    details[tag+'Resources']={'before':before,'cycles':cycles}
    (out/'intermediate.json').write_text(json.dumps({'checks':checks,'details':details,'errors':errors},indent=2)+'\n')
    return q,cycles
with sync_playwright()as pw:
 b=launch(pw,webgl=True)
 if a.baseline:
  page=load(b,served_bytes(a.baseline),webgl=True,errors=errors);q,cycles=inspect(page,'baseline');checks['BaselineSplitDishReproduced']=not q['pass']and any(r['splitComponents']for r in q['rows']);checks['BaselineRetirementLeakReproduced']=all(all(n==0 for n in c['retired']['disposed']['geometries'])for c in cycles);page.close()
 page=load(b,served_bytes(a.html,a.main_override),webgl=True,errors=errors);q,cycles=inspect(page,'candidate');checks['AllFourSPGsRigidAll48Poses']=q['pass'];checks['SourceTrianglesPreserved']=q['contract']['pass']
 checks['RetiredGeometryDisposedExactlyOnce']=all(c['created']['geometries']>0 and all(n==1 for n in c['retired']['disposed']['geometries'])for c in cycles)
 checks['RetiredMaterialsDisposedExactlyOnce']=all(all(n==1 for n in c['retired']['disposed']['materials'])for c in cycles)
 checks['RetiredOwnedTexturesDisposedExactlyOnce']=all(c['created']['textures']>0 and all(n==1 for n in c['retired']['disposed']['textures'])for c in cycles)
 checks['NativeFramesContinueEveryCycle']=all(c['retired']['draws']>c['created']['draws']for c in cycles);checks['NoContextLoss']=all(c['retired']['lost']==0 for c in cycles)
 # Native camera/effector inspection only; it cannot alter weapon state.
 fingerprint=page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B())')
 page.evaluate('''()=>{const v=window.__WIP148_3D_VIEW__,sync=v.syncShipFittings,camera=v.syncCamera;window.__I_RESTORE_POSE__=()=>{v.syncShipFittings=sync;v.syncCamera=camera};v.syncShipFittings=function(st){const copy={...st,illum:{...st.illum,spg62Mounts:[{illId:2,elRad:Math.PI/4,azWorldRad:st.ship.headingRad+Math.PI}]}};return sync.call(this,copy)};v.syncCamera=function(){camera.call(this);const p=this.spgMounts.get(2).yaw.getWorldPosition(new this.THREE.Vector3());this.camera.position.copy(p).add(new this.THREE.Vector3(-6,3,-7));this.camera.lookAt(p.clone().add(new this.THREE.Vector3(0,1,0)));};window.__I_POSE_DRAW__=window.__I_RESOURCES__.draws;}''')
 page.wait_for_function('()=>window.__I_RESOURCES__.draws>window.__I_POSE_DRAW__',timeout=90000);cdp=page.context.new_cdp_session(page);(out/'spg62-rigid-45deg.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']));page.evaluate('window.__I_RESTORE_POSE__()')
 checks['PresentationNoPhysicsMutation']=fingerprint==page.evaluate('JSON.stringify(window.__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B())');checks['CoreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[];page.close();b.close()
checks['PageErrorsZero']=not errors
r={'schema':'AEGIS_SPG_RIGID_AND_RESOURCE_RETIREMENT_I','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'diagnosticOnlyMemoryOverride':bool(a.main_override),'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())}
(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':r['pass']},ensure_ascii=False),flush=True)
if not r['pass']:raise SystemExit(1)
