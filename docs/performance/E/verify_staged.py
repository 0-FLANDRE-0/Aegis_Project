"""Native THREE on original pages: controlled geometry differential and cancellation.
Generator drainage is explicitly a shape/lifetime fixture, not native latency evidence.
"""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
FIXTURE=r'''async options=>{
 const d=__NAVAL_SIM_DIAG__,v=__WIP148_3D_VIEW__,T=v.THREE;
 v.active=false; // Controlled geometry fixture: native RAF latency is measured separately.
 const probe=d.runV48Wip03StructuralProbe({hits:2,label:'Kh-32',xM:12,zM:options.zM,side:'STARBOARD'}),state=window.get3DRenderState();
 v._damageJobV3?.return();v._damageJobV3=null;
 v.syncDamageScarsV1({shipDamageVisual:{scars:[]}});
 const before=JSON.stringify(d.exportOperationalStateV48Wip11A()),rng=__HARPOON_DIAG_A__.snapshot().rng;
 const hash=async array=>{const b=new Uint8Array(array.buffer,array.byteOffset,array.byteLength),h=await crypto.subtle.digest('SHA-256',b);return Array.from(new Uint8Array(h),x=>x.toString(16).padStart(2,'0')).join('')};
 const geometry=async()=>{const rows=[],objects=[];v.shipRoot.traverse(o=>{if(o.geometry)objects.push(o)});for(const o of objects){const g=o.geometry,attrs={};for(const k of Object.keys(g.attributes).sort()){const a=g.attributes[k];attrs[k]={type:a.array.constructor.name,itemSize:a.itemSize,normalized:a.normalized,count:a.count,hash:await hash(a.array)}}rows.push({name:o.name,kind:o.type,attrs,index:g.index?await hash(g.index.array):null,groups:g.groups,bounds:g.boundingBox?{min:g.boundingBox.min.toArray(),max:g.boundingBox.max.toArray()}:null,sphere:g.boundingSphere?{center:g.boundingSphere.center.toArray(),radius:g.boundingSphere.radius}:null})}return rows};
 const run=(scars,quick)=>{let steps=0,early=null;const job=v.buildDamageScarsV3(scars,quick),started=performance.now();for(;;){const n=job.next();steps++;if(!early&&v.damageScarVisuals.size)early={step:steps,count:v.damageScarVisuals.size,revision:v._damageOpeningRevisionPerfD??null,anchorsComplete:[...v.damageScarVisuals.values()].filter(q=>q.group.userData.actualHole).every(q=>JSON.parse(q.binding.mesh.geometry.userData.damageCutKeyV14??'[]').includes(q.binding.damageKeyV14))};if(n.done)break;if(steps>2000000)throw Error('GEOMETRY_FIXTURE_NOT_FINISHED')}v._damageSurfaceSignatureV2='CONTROLLED_FIXTURE';return {steps,cpuMs:performance.now()-started,early}};
 const scars=state.shipDamageVisual.scars.map(s=>({...s,p:{...s.p},normal:[...s.normal]})),rows=[];
 for(const [label,quick,input]of [['quick',true,scars],['detail',false,scars],['sealed',true,scars.map((s,i)=>({...s,sealed:i===0?1:s.sealed}))]]){
  rows.push({label,run:run(input,quick),geometry:await geometry(),scars:[...v.damageScarVisuals].map(([id,q])=>({id,actualHole:q.group.userData.actualHole,attached:!!q.group.parent,key:v.damageScarKeyV14(q.scar)}))});
 }
 const later=d.runV48Wip03StructuralProbe({hits:1,label:'Kh-32',xM:25,zM:options.zM,side:'STARBOARD'}).visual.scars;
 const combined=[...scars,...later.map(s=>({...s,id:'ADDED.'+s.id,p:{...s.p},normal:[...s.normal]}))];
 const incrementalRun=run(combined,true),incrementalGeometry=await geometry();
 const finalPhysical=JSON.stringify(d.exportOperationalStateV48Wip11A());
 v.syncDamageScarsV1({shipDamageVisual:{scars:[]}});
 const resetEmpty=v.damageScarVisuals.size===0&&[...v.damageOriginalMeshesV2].length===0;
 // Cancel after the first visible opening, before decoration completes.
 const job=v.buildDamageScarsV3(scars,true);let next,step=0;
 do{next=job.next();step++;if(step>2000000)throw Error('CANCEL_FIXTURE_NOT_FINISHED')}while(!next.done&&!v.damageScarVisuals.size);
 const hadPending=!next.done,attached=[...v.damageOriginalMeshesV2].filter(([m,r])=>m.geometry!==r.geometry).map(([m])=>m.geometry),untouched=[...v.damageOriginalMeshesV2].filter(([m,r])=>m.geometry===r.geometry).map(([m])=>m.geometry),disposed=new Set();for(const g of attached)g.addEventListener('dispose',()=>disposed.add(g));const originalDisposed=new Set();for(const g of untouched)g.addEventListener('dispose',()=>originalDisposed.add(g));job.return();v._damageSurfaceSignatureV2='CONTROLLED_CANCEL';
 const retainedLive=attached.every(g=>!disposed.has(g)),cancelRows=await geometry();v.syncDamageScarsV1({shipDamageVisual:{scars:[]}});
 return {incremental:{run:incrementalRun,geometry:incrementalGeometry},probe:{label:probe.label,hits:probe.hits},rows,cancellation:{hadPending,retainedLive,attachedCount:attached.length,geometry:cancelRows,resetDisposed:attached.every(g=>disposed.has(g)),empty:v.damageScarVisuals.size===0,originalsRetained:originalDisposed.size===0},checks:{noPhysicsMutation:finalPhysical===JSON.stringify(d.exportOperationalStateV48Wip11A()),rngUnchanged:rng===__HARPOON_DIAG_A__.snapshot().rng,resetEmpty,coreZero:__CORE_SELFTEST_FAILURES__.length===0,faultsZero:!__WIP125_DIAG__.wip150RuntimeFault()&&!__WIP125_DIAG__.wip150PresentationFault()}};
}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];cases=[]
 with sync_playwright()as pw:
  browser=launch(pw,True)
  for ship,zM in [(s,z)for s in ['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']for z in [1.5,4]]:
   pair={}
   for version,src in [('baseline',a.baseline),('candidate',a.html)]:
    page=load(browser,src.read_bytes(),ship,True,errors=errors);pair[version]=page.evaluate(FIXTURE,{'zM':zM});page.close();print(json.dumps({'ship':ship,'version':version,'steps':[q['run']['steps']for q in pair[version]['rows']]}),flush=True)
   b,c=pair['baseline'],pair['candidate'];checks={**c['checks'],'quickFinalGeometryExact':b['rows'][0]['geometry']==c['rows'][0]['geometry'],'detailFinalGeometryExact':b['rows'][1]['geometry']==c['rows'][1]['geometry'],'sealedFinalGeometryExact':b['rows'][2]['geometry']==c['rows'][2]['geometry'],'incrementalFinalGeometryExact':b['incremental']['geometry']==c['incremental']['geometry'],'firstPublishedAnchorsAreCut':c['rows'][0]['run']['early']['anchorsComplete'],'allScarBindingsExact':all(x['scars']==y['scars']for x,y in zip(b['rows'],c['rows'])),'openingPublishedBeforeDecoration':c['rows'][0]['run']['early']['step']<c['rows'][0]['run']['steps']and b['rows'][0]['run']['early']['step']<b['rows'][0]['run']['steps'],'cancelVisibleRetainsLiveGeometry':c['cancellation']['hadPending']and c['cancellation']['retainedLive']and c['cancellation']['attachedCount']>0,'cancelResetDisposesLiveGeometry':c['cancellation']['resetDisposed']and c['cancellation']['empty'],'cancelResetRetainsUnchangedOriginals':c['cancellation']['originalsRetained']};cases.append({'ship':ship,'zM':zM,'checks':checks,'pair':pair})
  browser.close()
 q={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'fixture':'Native THREE original-page controlled generator completion, no latency/FPS claim','cases':cases,'errors':errors,'pass':not errors and all(all(c['checks'].values())for c in cases)};(a.out/'staged.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'failed':[(c['ship'],k)for c in cases for k,v in c['checks'].items()if not v]}));raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
