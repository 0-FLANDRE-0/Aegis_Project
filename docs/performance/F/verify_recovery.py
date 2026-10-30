"""Native GPU smoke/missile cycles and target-retirement display ownership."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
FIXTURE=r'''async()=>{const v=__WIP148_3D_VIEW__,d=__NAVAL_SIM_DIAG__,T=v.THREE,api=__AEGIS_SMOKE_C13__;v.active=false;
 const scene=new T.Scene();scene.add(new T.HemisphereLight(0xffffff,0x333333,2));const camera=new T.PerspectiveCamera(40,1,.1,500);camera.position.set(0,35,110);camera.lookAt(0,20,0);v.camera.position.copy(camera.position);v.camera.lookAt(0,20,0);v.camera.updateMatrixWorld(true);
 const rows=[],checks={};
 for(let cycle=0;cycle<8;cycle++){
  d.wip119DiagSpawnRealAsms({count:4,label:'Kh-32',rangeKm:16});let st=get3DRenderState();v.syncWorldEpochWip14A(st);v.syncEnemyAsmVisuals(st,0);const models=[...v.asmVisuals.values()];for(const q of models){scene.add(q.mesh);q.mesh.position.set(0,20,0)}
  api.configure({capacity:12000,hybrid:false});const pool=v.c13Smoke;pool.time=2;for(let i=0;i<1200;i++)pool.emit({x:(i%30)-15,y:20,z:-Math.floor(i/30),birth:0,life:30,alpha:.6,base:2,growth:.04,color:[.3,.3,.3]});api.flush();for(const b of v._c13SmokeGPU.batches.values())scene.add(b.mesh);v.renderer.render(scene,camera);
  const smokeGeos=[...v._c13SmokeGPU.batches.values()].map(b=>b.mesh.geometry),freed=new Set();for(const g of smokeGeos)g.addEventListener('dispose',()=>freed.add(g));const tex=models[0].mesh.getObjectByName('kh32_body_canonical').material.map;let textureDisposes=0;tex.addEventListener('dispose',()=>textureDisposes++);
  if(cycle%2){d.resetEntireSessionV48Wip11A()}else{const saved=d.exportOperationalStateV48Wip11A();d.importOperationalStateV48Wip11A(saved)}v.syncWorldEpochWip14A(get3DRenderState());v.renderer.render(scene,camera);
  rows.push({cycle,mode:cycle%2?'reset':'import',smokeDisposed:smokeGeos.every(g=>freed.has(g)),textureDisposes,smokeCount:v.c13Smoke.count,asmCount:v.asmVisuals.size,memory:{...v.renderer.info.memory},glError:v.renderer.getContext().getError()});
 }
 const profileId=get3DRenderState().shipProfile.id;__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{allyProfileId:profileId,enemyProfileId:null,targetShip:'NONE',enemyAircraftEnabled:false});if(!__AEGIS_DEPLOYMENT_A__.setDraft(cfg).ok)throw Error('draft');document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);v.syncPhysicalFleetB(get3DRenderState());
 const target=[...v.navalShipPresentersB.values()][0];if(!target)throw Error('physical presenter absent');
 const scars=d.runV48Wip03StructuralProbe({hits:1,label:'Kh-32',xM:12,zM:4,side:'STARBOARD'}).visual.scars;target._damageJobV3=target.buildDamageScarsV3(scars,true);let step=0,n;while(!target._damageOpeningReadyPerfF){n=target._damageJobV3.next();if(n.done||++step>2000000)throw Error('foreign anchor')}
 const geometries=new Set(),disposed=new Set(),textures=new Set(),texturesDisposed=new Set();target.shipRoot.traverse(o=>{if(o.geometry)geometries.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material])if(m?.map)textures.add(m.map)});for(const t of textures)t.addEventListener('dispose',()=>texturesDisposed.add(t));for(const r of target.damageOriginalMeshesV2.values())geometries.add(r.geometry);for(const g of geometries)g.addEventListener('dispose',()=>disposed.add(g));const mainTextures=new Set();v.shipRoot.traverse(o=>{for(const m of Array.isArray(o.material)?o.material:[o.material])if(m?.map)mainTextures.add(m.map)});const ownedTextures=target._bunkerAsset?.ownedTextures??new Set();checks.ownedTexturesDistinct=[...ownedTextures].every(t=>!mainTextures.has(t));checks.sharedTexturesMatchLiveOwner=[...textures].filter(t=>!ownedTextures.has(t)).every(t=>mainTextures.has(t));const oldRoot=target.shipRoot,oldOwner=target.ownerRuntime;
 d.resetEntireSessionV48Wip11A();v.syncWorldEpochWip14A(get3DRenderState());v.syncPhysicalFleetB(get3DRenderState());

 checks.all8CyclesDisposeSmoke=rows.every(r=>r.smokeDisposed);checks.all8CyclesDisposeLastPaintLease=rows.every(r=>r.textureDisposes===1);checks.all8CyclesClearTransientMaps=rows.every(r=>r.smokeCount===0&&r.asmCount===0);checks.noGpuCountGrowthAfterWarmup=rows.slice(2).every(r=>r.memory.geometries<=rows[1].memory.geometries&&r.memory.textures<=rows[1].memory.textures);checks.targetRemoved=!oldRoot.parent&&oldOwner.modelRoots.world===null;checks.targetOwnedTextureDisposed=[...ownedTextures].every(t=>texturesDisposed.has(t));checks.sharedTexturesNotDisposed=[...textures].filter(t=>!ownedTextures.has(t)).every(t=>!texturesDisposed.has(t));checks.profileTextureCoverage=profileId.startsWith('CG')?textures.size===1&&ownedTextures.size===1:textures.size===5&&ownedTextures.size===0;checks.targetGeometryDisposed=geometries.size>0&&[...geometries].every(g=>disposed.has(g));checks.glErrorsZero=rows.every(r=>r.glError===0);checks.coreZero=!__CORE_SELFTEST_FAILURES__.length;checks.faultsZero=!__WIP125_DIAG__.wip150RuntimeFault()&&!__WIP125_DIAG__.wip150PresentationFault();return{checks,rows,targetGeometryCount:geometries.size,targetTextureCount:textures.size,ownedTextureCount:ownedTextures.size};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];cases=[]
 with sync_playwright()as pw:
  b=launch(pw,True)
  for ship in ['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']:
   page=load(b,a.html.read_bytes(),ship,True,errors=errors);r=page.evaluate(FIXTURE);cases.append({'ship':ship,**r});page.close();print(json.dumps({'ship':ship,'checks':r['checks']}),flush=True)
  b.close()
 q={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'cases':cases,'errors':errors,'pass':not errors and all(all(c['checks'].values())for c in cases),'limits':'Eight actual import/reset epochs, native smoke/missile GPU resources. Physical foreign owner replacement after reset exercises its pending-cut presenter disposer; not combat sinking. GPU counters are resource counts, not allocated VRAM bytes.'};(a.out/'recovery.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass']}));raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
