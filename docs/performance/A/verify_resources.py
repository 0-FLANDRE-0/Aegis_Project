"""Actual native Kh32 builds: pixel/geometry parity and shared texture disposal.
64-model candidate test measures unique source pixels, not VRAM or mobile FPS.
Catalog intentionally retains its current model while closed; switching disposes it.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
BUILD=r'''async count=>{
const d=__NAVAL_SIM_DIAG__,v=__WIP148_3D_VIEW__,T=v.THREE;v.close();
d.wip119DiagSpawnRealAsms({count:1,label:'Kh-32',rangeKm:16});const st=get3DRenderState().enemyAsms[0];
const hash=async data=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data))).map(x=>x.toString(16).padStart(2,'0')).join('');
const start=performance.now(),models=Array.from({length:count},()=>v.buildEnemyAsmMesh(st)),buildMs=performance.now()-start;
const body=m=>m.getObjectByName('kh32_body_canonical'),textures=new Set(models.map(m=>body(m).material.map)),tex=body(models[0]).material.map;
const pixels=await hash(tex.image.getContext('2d').getImageData(0,0,tex.image.width,tex.image.height).data);
const shape=[];models[0].traverse(o=>{if(!o.isMesh)return;const g=o.geometry,m=o.material;shape.push({name:o.name,position:o.position.toArray(),rotation:o.rotation.toArray(),index:g.index?Array.from(g.index.array):null,attributes:Object.fromEntries(Object.entries(g.attributes).map(([k,a])=>[k,{itemSize:a.itemSize,array:Array.from(a.array)}])),material:{color:m.color?.getHex(),roughness:m.roughness,metalness:m.metalness,side:m.side,opacity:m.opacity,hasMap:!!m.map}});});
const geometry=await hash(new TextEncoder().encode(JSON.stringify(shape)));
let disposed=0;for(const t of textures)t.addEventListener('dispose',()=>disposed++);
const scene=new T.Scene(),camera=new T.PerspectiveCamera(40,1,.1,100);camera.position.set(0,0,22);camera.lookAt(0,0,0);scene.add(new T.HemisphereLight(0xffffff,0x333333,2));scene.add(models[0]);v.renderer.render(scene,camera);scene.remove(models[0]);
for(let i=0;i<count/2;i++)v.disposeOrdnanceVisualV1({mesh:models[i]});const afterPartial=disposed;
scene.add(models.at(-1));v.renderer.render(scene,camera);const remainingRendered=v.renderer.info.render.calls>0&&body(models.at(-1)).material.map===tex;scene.remove(models.at(-1));
for(let i=count/2;i<count;i++)v.disposeOrdnanceVisualV1({mesh:models[i]});const afterAll=disposed;
v.disposeOrdnanceVisualV1({mesh:models[0]});const afterRepeated=disposed;
const fresh=v.buildEnemyAsmMesh(st),freshTex=body(fresh).material.map;const recreated=freshTex!==tex;
v.disposeOrdnanceVisualV1({mesh:fresh});
return {count,buildMs,pixels,geometry,meshCount:shape.length,uniqueTextures:textures.size,uniqueCanvas:new Set([...textures].map(t=>t.image)).size,sourcePixelBytes:[...textures].reduce((n,t)=>n+t.image.width*t.image.height*4,0),dimensions:[tex.image.width,tex.image.height],afterPartial,afterAll,afterRepeated,remainingRendered,recreated,core:__CORE_SELFTEST_FAILURES__,faults:[__WIP125_DIAG__.wip150RuntimeFault(),__WIP125_DIAG__.wip150PresentationFault()]};
}'''
LIFECYCLE=r'''async()=>{
const d=__NAVAL_SIM_DIAG__,v=__WIP148_3D_VIEW__,cat=__WIP200_MISSILE_CATALOG__;v.close();const body=m=>m.getObjectByName('kh32_body_canonical');
d.wip119DiagSpawnRealAsms({count:1,label:'Kh-32',rangeKm:16});let st=get3DRenderState();v.syncWorldEpochWip14A(st);v.syncEnemyAsmVisuals(st,0);
const live=[...v.asmVisuals.values()][0],tex=body(live.mesh).material.map;let disposes=0;tex.addEventListener('dispose',()=>disposes++);
// MAIN wreck uses the same canonical builder and dimensions as the live missile.
const s=st.enemyAsms[0],wreck=v.buildAsmWreckMesh({...s,id:98765,pieceType:'MAIN'});v.wreckVisuals.set('perf-a-fixture',{mesh:wreck});
const liveAndWreckShare=body(wreck).material.map===tex;
await cat.open();cat.select('KH32');cat.close();const catalogTex=body(cat.currentMesh).material.map,catalogShare=catalogTex===tex,closedRetainsModel=!!cat.currentMesh;
const saved=d.exportOperationalStateV48Wip11A(),beforeEpoch=st.sim.presentationEpoch;d.importOperationalStateV48Wip11A(saved);st=get3DRenderState();v.syncWorldEpochWip14A(st);
const epochAdvanced=st.sim.presentationEpoch!==beforeEpoch,worldMapsCleared=v.asmVisuals.size===0&&v.wreckVisuals.size===0,retainedCatalogNotDisposed=disposes===0;
cat.select('SM2');const finalDisposed=disposes===1;
cat.select('KH32');const newTex=body(cat.currentMesh).material.map,recreated=newTex!==tex;cat.select('SM2');
d.wip119DiagSpawnRealAsms({count:1,label:'Kh-32',rangeKm:16});st=get3DRenderState();v.syncEnemyAsmVisuals(st,0);const lastTex=body([...v.asmVisuals.values()][0].mesh).material.map;let resetDisposes=0;lastTex.addEventListener('dispose',()=>resetDisposes++);
d.resetEntireSessionV48Wip11A();v.syncWorldEpochWip14A(get3DRenderState());
return {liveAndWreckShare,catalogShare,closedRetainsModel,epochAdvanced,worldMapsCleared,retainedCatalogNotDisposed,finalDisposed,recreated,resetClearsVisuals:v.asmVisuals.size===0,resetLastTextureDisposed:resetDisposes===1,core:__CORE_SELFTEST_FAILURES__,faults:[__WIP125_DIAG__.wip150RuntimeFault(),__WIP125_DIAG__.wip150PresentationFault()]};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];pair={}
 with sync_playwright()as pw:
  browser=launch(pw,True)
  for name,source,count in [('baseline',a.baseline,2),('candidate',a.candidate,64)]:
   page=load(browser,source.read_bytes(),webgl=True,errors=errors);pair[name]=page.evaluate(BUILD,count)
   if name=='candidate':
    life=page.evaluate(LIFECYCLE);page.screenshot(path=str(a.out/'resources-cg.png'))
   page.close()
  browser.close()
 b,c=pair['baseline'],pair['candidate'];checks={'paintPixelsExact':b['pixels']==c['pixels'],'geometryAndMaterialsExact':b['geometry']==c['geometry'],'baselineDuplicatesProven':b['uniqueTextures']==2 and b['uniqueCanvas']==2,'candidate64ShareOne':c['uniqueTextures']==1 and c['uniqueCanvas']==1,'partialRemovalKeepsTexture':c['afterPartial']==0 and c['remainingRendered'],'lastRemovalDisposesOnce':c['afterAll']==c['afterRepeated']==1,'subsequentBuildRecreates':c['recreated'],'faultsZero':all(q['core']==[]and all(f is None for f in q['faults'])for q in pair.values())and life['core']==[]and all(f is None for f in life['faults']),'pageErrorsZero':not errors}
 checks.update({k:v for k,v in life.items()if k not in ['core','faults']});report={'sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),'checks':checks,'pair':pair,'lifecycle':life,'errors':errors,'pass':all(checks.values()),'limits':'Native 2 baseline vs64 candidate models; pixels/geometry parity and disposal, not hardware FPS/actual VRAM. Closed catalog retains its model by existing design.'}
 (a.out/'resources.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pass':report['pass'],'failed':[k for k,v in checks.items()if not v],'uniqueTextures':c['uniqueTextures'],'sourcePixelBytes':c['sourcePixelBytes']}));raise SystemExit(0 if report['pass']else 1)
if __name__=='__main__':main()
