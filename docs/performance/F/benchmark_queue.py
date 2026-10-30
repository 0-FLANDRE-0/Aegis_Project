"""Serial E/F native RAF: second detached hit arrives after first anchor submission.
All geometry jobs use the original render budget, no drainage or fake clocks.
Paused physics, controlled detached scar inputs; not natural multi-hit combat/FPS.
"""
import argparse,hashlib,json,statistics,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
SETUP=r'''()=>{const v=__WIP148_3D_VIEW__,d=__NAVAL_SIM_DIAG__;__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{allyProfileId:null,enemyProfileId:null,targetShip:'NONE',enemyAircraftEnabled:false});if(!__AEGIS_DEPLOYMENT_A__.setDraft(cfg).ok)throw Error('draft');document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);v.c12ApplyPreset('LOW');v.orbit.distance=125;v.orbit.targetY=5;
 const input=[12,25].map((x,i)=>d.runV48Wip03StructuralProbe({hits:1,label:'Kh-32',xM:x,zM:4,side:'STARBOARD'}).visual.scars.map(s=>({...s,id:'NATIVE'+i+'.'+s.id,p:{...s.p},normal:[...s.normal]})));
 v.syncDamageScarsV1({shipDamageVisual:{scars:[]}});const t=window.__QUEUE_NATIVE_F__={input,phase:0,started:performance.now(),first:null,second:null,draws:0,steps:0},sync=v.syncDamageScarsV1,draw=v.renderer.render;
 v.syncDamageScarsV1=function(st){const scars=t.phase===0?t.input[0]:t.input.flat(),r=sync.call(this,{...st,shipDamageVisual:{...st.shipDamageVisual,scars}});t.steps+=this.damageBuildStatsV3?.steps??0;return r};
 v.renderer.render=function(...args){t.draws++;const scars=t.phase===0?t.input[0]:t.input.flat(),ready=scars.every(s=>{const q=v.damageScarVisuals.get(s.id);return q?.group.parent&&(!q.group.userData.actualHole||JSON.parse(q.binding.mesh.geometry.userData.damageCutKeyV14??'[]').includes(q.binding.damageKeyV14))});const at=performance.now(),r=draw.apply(this,args);if(ready&&t.phase===0){t.first={submissionMs:at-t.started,steps:t.steps,draws:t.draws,pending:!!v._damageJobV3};t.phase=1;t.secondStarted=performance.now();t.steps=0;t.draws=0;}else if(ready&&t.phase===1&&!t.second){t.second={submissionMs:at-t.secondStarted,steps:t.steps,draws:t.draws,pending:!!v._damageJobV3,glError:v.renderer.getContext().getError()};}return r};return {physical:JSON.stringify(d.exportOperationalStateV48Wip11A()),rng:__HARPOON_DIAG_A__.snapshot().rng,scarCounts:input.map(s=>s.length)};}'''
AFTER=r'''()=>({physical:JSON.stringify(__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()),rng:__HARPOON_DIAG_A__.snapshot().rng,core:__CORE_SELFTEST_FAILURES__,runtime:__WIP125_DIAG__.wip150RuntimeFault(),presentation:__WIP125_DIAG__.wip150PresentationFault(),trace:__QUEUE_NATIVE_F__})'''
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];errors=[];ships=['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']
 with sync_playwright()as pw:
  browser=launch(pw,True)
  for rep in range(2):
   for ship in ships[::1 if rep==0 else -1]:
    for name,src in [('baseline',a.baseline),('candidate',a.html)][::1 if (rep+ships.index(ship))%2==0 else -1]:
     page=load(browser,src.read_bytes(),ship,True,errors=errors);before=page.evaluate(SETUP);deadline=time.monotonic()+300
     while True:
      try:page.wait_for_function('__QUEUE_NATIVE_F__.second||__WIP125_DIAG__.wip150PresentationFault()',timeout=10000,polling=500);break
      except TimeoutError:
       print(json.dumps({'repeat':rep,'ship':ship,'version':name,'progress':page.evaluate('({phase:__QUEUE_NATIVE_F__.phase,steps:__QUEUE_NATIVE_F__.steps,draws:__QUEUE_NATIVE_F__.draws})')}),flush=True)
       if time.monotonic()>deadline:raise
     after=page.evaluate(AFTER);capture=f'{ship}-r{rep}-{name}.png';page.screenshot(path=str(a.out/capture));page.close();checks={'secondActualCutSubmitted':after['trace']['second']is not None,'glZero':after['trace']['second']['glError']==0,'physicalFrozen':before['physical']==after['physical'],'rngFrozen':before['rng']==after['rng'],'coreAndFaultsZero':not after['core']and after['runtime']is None and after['presentation']is None};rows.append({'repeat':rep,'ship':ship,'version':name,'before':before,'after':after,'checks':checks,'capture':capture});(a.out/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'repeat':rep,'ship':ship,'version':name,'second':after['trace']['second']}),flush=True)
  browser.close()
 summary=[]
 for ship in ships:
  times={n:[r['after']['trace']['second']['submissionMs']for r in rows if r['ship']==ship and r['version']==n]for n in ['baseline','candidate']};b=statistics.mean(times['baseline']);c=statistics.mean(times['candidate']);summary.append({'ship':ship,'secondSubmissionMs':times,'meanBeforeMs':b,'meanAfterMs':c,'observedReductionPercent':100*(1-c/b)})
 checks={'allNativeChecksPass':all(all(r['checks'].values())for r in rows),'pageErrorsZero':not errors,'oppositeOrder':all([r['version']for r in rows if r['ship']==s and r['repeat']==0]==list(reversed([r['version']for r in rows if r['ship']==s and r['repeat']==1]))for s in ships)}
 q={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'checks':checks,'pass':all(checks.values()),'rows':rows,'summary':summary,'errors':errors,'limits':'Serial paired native RAF/THREE/SwiftShader LOW640x480, paused physics. Detached cumulative diagnostic scar inputs x12 then x25,z4, second arrives at first actual anchor submission. No drain/fake clock. CPU submission time, not hardware GPU completion/mobile FPS or natural multi-hit combat.'};(a.out/'native-queue.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'summary':summary}),flush=True);raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
