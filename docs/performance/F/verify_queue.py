"""Native THREE controlled consecutive-hit queue and lifetime fixture; not latency."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
FIXTURE=r'''async candidate=>{
 const d=__NAVAL_SIM_DIAG__,v=__WIP148_3D_VIEW__;v.active=false;const inputs=[];
 for(const x of [12,25,-12])inputs.push(d.runV48Wip03StructuralProbe({hits:1,label:'Kh-32',xM:x,zM:4,side:'STARBOARD'}).visual.scars.map(s=>({...s,id:'X'+x+'.'+s.id,p:{...s.p},normal:[...s.normal]})));
 v.syncDamageScarsV1({shipDamageVisual:{scars:[]}});const physical=JSON.stringify(d.exportOperationalStateV48Wip11A()),rng=__HARPOON_DIAG_A__.snapshot().rng;
 const sig=s=>JSON.stringify(s.map(q=>v.damageScarKeyV14(q))),start=scars=>{v._damageQuickV11=true;v._damageOpeningReadyPerfF=false;v._damageJobSignatureV3=sig(scars);return v._damageJobV3=v.buildDamageScarsV3(scars,true)},finish=()=>{let steps=0,n;do{n=v._damageJobV3.next();if(++steps>2000000)throw Error('drain limit')}while(!n.done);v._damageSurfaceSignatureV2=v._damageJobSignatureV3;v._damageJobV3=null;return steps};
 const hash=async a=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint8Array(a.buffer,a.byteOffset,a.byteLength))),x=>x.toString(16).padStart(2,'0')).join('');
 const shape=async()=>{const objects=[];v.shipRoot.traverse(o=>{if(o.geometry)objects.push(o)});const rows=[];for(const o of objects){const g=o.geometry,attrs={};for(const[k,a]of Object.entries(g.attributes))attrs[k]={itemSize:a.itemSize,hash:await hash(a.array)};rows.push({name:o.name,attrs,index:g.index?await hash(g.index.array):null,groups:g.groups})}return rows};
 const checks={},trace=[];let combined=inputs[0];
 if(!candidate){start(combined);finish();for(const batch of inputs.slice(1)){combined=[...combined,...batch];start(combined);finish();}}
 else{
  for(let i=0;i<inputs.length;i++){
   const job=start(combined);job.next();v._c12DamageShareMs=.25;
   // A changed signature before publication must retain this job.
   const churn=combined.map(s=>({...s,scorchRadius:(s.scorchRadius||0)+.00001}));v.syncDamageScarsV1({shipDamageVisual:{scars:churn}});checks['unpublishedNotCancelled'+i]=v._damageJobV3===job;
   let n,steps=0;while(!v._damageOpeningReadyPerfF){n=job.next();if(n.done||++steps>2000000)throw Error('anchor not published')}
   const anchors=[...v.damageScarVisuals.values()].filter(q=>q.group.userData.actualHole),live=anchors.map(q=>q.binding.mesh.geometry),disposed=new Set();for(const g of live)g.addEventListener('dispose',()=>disposed.add(g));
   checks['allPublishedAnchorsCut'+i]=anchors.length>0&&anchors.every(q=>JSON.parse(q.binding.mesh.geometry.userData.damageCutKeyV14??'[]').includes(q.binding.damageKeyV14));
   if(i<inputs.length-1){combined=[...combined,...inputs[i+1]];v.syncDamageScarsV1({shipDamageVisual:{scars:combined}});checks['newHitReplacesPublishedJob'+i]=v._damageJobV3!==job&&v._damageJobSignatureV3===sig(combined);checks['liveCutsRetainedOnPreemption'+i]=live.every(g=>!disposed.has(g));v._damageJobV3.return();v._damageJobV3=null;}
   else finish();trace.push({batch:i,anchorSteps:steps,scars:combined.length});
  }
 }
 const geometry=await shape();checks.allScarIdsAttached=combined.every(s=>v.damageScarVisuals.get(s.id)?.group.parent);checks.noPhysicsMutation=physical===JSON.stringify(d.exportOperationalStateV48Wip11A());checks.noRngMutation=rng===__HARPOON_DIAG_A__.snapshot().rng;
 const changed=[...v.damageOriginalMeshesV2].filter(([m,r])=>m.geometry!==r.geometry).map(([m])=>m.geometry),originals=[...v.damageOriginalMeshesV2.values()].map(r=>r.geometry),freed=new Set(),originalFreed=new Set();changed.forEach(g=>g.addEventListener('dispose',()=>freed.add(g)));originals.forEach(g=>g.addEventListener('dispose',()=>originalFreed.add(g)));v.syncDamageScarsV1({shipDamageVisual:{scars:[]}});checks.resetDisposesChanged=changed.length>0&&changed.every(g=>freed.has(g));checks.originalBuffersPreserved=originalFreed.size===0;checks.resetMapsEmpty=!v._damageJobV3&&!v.damageScarVisuals.size&&!v.damageOriginalMeshesV2.size;checks.coreZero=!__CORE_SELFTEST_FAILURES__.length;checks.faultsZero=!__WIP125_DIAG__.wip150RuntimeFault()&&!__WIP125_DIAG__.wip150PresentationFault();return{checks,trace,geometry,changedCount:changed.length};}'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);errors=[];cases=[]
 with sync_playwright()as pw:
  browser=launch(pw,True)
  for ship in ['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']:
   pair={}
   for name,src in [('baseline',a.baseline),('candidate',a.html)]:
    page=load(browser,src.read_bytes(),ship,True,errors=errors);pair[name]=page.evaluate(FIXTURE,name=='candidate');page.close();print(json.dumps({'ship':ship,'version':name,'checks':pair[name]['checks']}),flush=True)
   checks={**pair['candidate']['checks'],'finalGeometryExact':pair['baseline']['geometry']==pair['candidate']['geometry'],'baselineChecksPass':all(pair['baseline']['checks'].values())};cases.append({'ship':ship,'checks':checks,'pair':pair})
  browser.close()
 q={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'cases':cases,'errors':errors,'pass':not errors and all(all(c['checks'].values())for c in cases),'limits':'Native original THREE controlled generator steps and detached cumulative scar batches from structural diagnostics. Not natural multi-hit combat, native latency, or FPS.'};(a.out/'queue.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'failed':[(c['ship'],k)for c in cases for k,v in c['checks'].items()if not v]}));raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
