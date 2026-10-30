"""Serial paired original native RAF/WebGL first visible opening submissions.
No job drainage, fake frame clocks, or physical simulation from a render.
Software WebGL host latency, not a hardware GPU/mobile FPS measurement.
"""
import argparse,base64,hashlib,json,statistics,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
SETUP=r'''()=>{const v=__WIP148_3D_VIEW__,d=__NAVAL_SIM_DIAG__;__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{enemyProfileId:null,allyProfileId:null,targetShip:'NONE',enemyAircraftEnabled:false});const draft=__AEGIS_DEPLOYMENT_A__.setDraft(cfg);if(!draft.ok)throw Error('DRAFT');document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);v.c12ApplyPreset('LOW');v.orbit.distance=125;v.orbit.targetY=5;
 const t=window.__MESH_LATENCY_D__={draws:0,damageCpuMs:0,steps:0,first:null,started:null,shares:[]},draw=v.renderer.render,sync=v.syncDamageScarsV1;
 v.syncDamageScarsV1=function(...a){const start=performance.now(),r=sync.apply(this,a);if(t.started!=null&&!t.first){t.damageCpuMs+=performance.now()-start;t.steps+=this.damageBuildStatsV3?.steps??0;t.shares.push({...this.damageBuildStatsV3,frameWork:{...this.c12FrameWork}})}return r};
 v.renderer.render=function(...a){t.draws++;const at=performance.now();const first=t.started!=null&&!t.first&&[...v.damageScarVisuals.values()].some(q=>q.group.userData.actualHole&&q.group.parent);const r=draw.apply(this,a);if(first)t.first={submissionMs:at-t.started,returnMs:performance.now()-t.started,draws:t.draws-t.drawStart,damageCpuMs:t.damageCpuMs,steps:t.steps,openingRevision:v._damageOpeningRevisionPerfD??null,completeRevision:v._damageGeometryRevisionV11??0,decorationPending:!!v._damageJobV3,glError:v.renderer.getContext().getError(),audit:v.damageAuditV48Wip03()};return r};return {draft,preset:v.c12Preset};}'''
HIT=r'''()=>{const t=__MESH_LATENCY_D__;t.started=performance.now();t.drawStart=t.draws;const start=performance.now(),probe=__NAVAL_SIM_DIAG__.runV48Wip03StructuralProbe({hits:1,label:'Kh-32',xM:12,zM:1.5,side:'STARBOARD'});return {hitCpuMs:performance.now()-start,probe}}'''
STATE=r'''()=>({state:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),rng:__HARPOON_DIAG_A__.snapshot().rng,core:__CORE_SELFTEST_FAILURES__,runtime:__WIP125_DIAG__.wip150RuntimeFault(),presentation:__WIP125_DIAG__.wip150PresentationFault()})'''
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];pairs=[];errors=[];ships=['CG_52_LATE_TICONDEROGA','DDG_119_LATE_FLIGHT_IIA']
 with sync_playwright()as pw:
  browser=launch(pw,True)
  for rep in range(2):
   for i,ship in enumerate(ships if rep==0 else list(reversed(ships))):
    pair={}
    for name,src in [('baseline',a.baseline),('candidate',a.html)][::1 if (rep+ships.index(ship))%2==0 else -1]:
     page=load(browser,src.read_bytes(),ship,True,errors=errors);page.set_viewport_size({'width':480,'height':360});setup=page.evaluate(SETUP);page.wait_for_function('__MESH_LATENCY_D__.draws>=3',timeout=60000);hit=page.evaluate(HIT);state=page.evaluate(STATE);deadline=time.monotonic()+480
     while True:
      try:page.wait_for_function('__MESH_LATENCY_D__.first||__WIP125_DIAG__.wip150PresentationFault()',timeout=10000,polling=500);break
      except TimeoutError:
       print(json.dumps({'repeat':rep,'ship':ship,'version':name,'pending':page.evaluate('({draws:__MESH_LATENCY_D__.draws-__MESH_LATENCY_D__.drawStart,steps:__MESH_LATENCY_D__.steps})')}),flush=True)
       if time.monotonic()>deadline:raise
     trace=page.evaluate('__MESH_LATENCY_D__');after=page.evaluate(STATE);cdp=page.context.new_cdp_session(page);filename=f'native-r{rep}-{ship}-{name}.png';(a.out/filename).write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']));page.close()
     row={'repeat':rep,'ship':ship,'version':name,'setup':setup,'hitCpuMs':hit['hitCpuMs'],'state':state,'stateDigest':digest(state['state']),'trace':trace,'capture':filename,'checks':{'nativeOpeningDisplayed':trace['first'] is not None and trace['first']['audit']['dualHullOpenings'],'nativeGlErrorZero':trace['first']['glError']==0,'physicsFrozenDuringRender':state==after,'coreAndFaultsZero':not state['core']and state['runtime']is None and state['presentation']is None}};rows.append(row);pair[name]=row;(a.out/'native-latency-progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'repeat':rep,'ship':ship,'version':name,'first':trace['first']}),flush=True)
    pairs.append({'repeat':rep,'ship':ship,'checks':{'damageAndSaveStateExact':pair['baseline']['stateDigest']==pair['candidate']['stateDigest'],'combatRngExact':pair['baseline']['state']['rng']==pair['candidate']['state']['rng'],'nativeChecksPass':all(all(r['checks'].values())for r in pair.values()),'candidateOpeningBeforeDecoration':pair['candidate']['trace']['first']['decorationPending']}})
  browser.close()
 summary=[]
 for ship in ships:
  values={n:[q['trace']['first']['submissionMs']for q in rows if q['ship']==ship and q['version']==n]for n in ['baseline','candidate']};b=statistics.mean(values['baseline']);c=statistics.mean(values['candidate']);summary.append({'ship':ship,'submissionMs':values,'meanBeforeMs':b,'meanAfterMs':c,'observedReductionPercent':100*(1-c/b)})
 checks={'allNativeAndStateChecksPass':all(all(p['checks'].values())for p in pairs),'pageErrorsZero':not errors,'oppositeOrderWithinEachShip':all([q['version']for q in rows if q['ship']==s and q['repeat']==0]==list(reversed([q['version']for q in rows if q['ship']==s and q['repeat']==1]))for s in ships)}
 q={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'conditions':{'seed':1831565813,'preset':'LOW','viewport':'480x360','backend':'Chromium native RAF/WebGL SwiftShader','scenario':'Single diagnostic native Kh-32 dud structural hit, paused physics, no foreign ships/aircraft/old target, x12/z1.5/STARBOARD','order':'serial, two passes opposite AB/BA per ship, reversed ship traversal','limits':'First THREE render submission of actual attached cut/fold geometry. Not hardware GPU completion, mobile FPS, natural weapon effectiveness, or simultaneous-hit latency.'},'checks':checks,'pairs':pairs,'rows':rows,'summary':summary,'errors':errors,'pass':all(checks.values())};(a.out/'native-latency.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'summary':summary}));raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
