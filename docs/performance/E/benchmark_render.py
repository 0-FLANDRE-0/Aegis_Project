"""Serial paired native RAF/THREE CPU submit time and buffer transfer observations.
No forced frames, physical clock advance, model override, or hardware-FPS claim.
"""
import argparse,hashlib,json,statistics,sys,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
SETUP=r'''o=>{const v=__WIP148_3D_VIEW__,d=__NAVAL_SIM_DIAG__;__WIP125_DIAG__.forcePreSail();const cfg=d.exportOperationalStateV48Wip11A().deployment;Object.assign(cfg,{enemyProfileId:null,allyProfileId:null,targetShip:'NONE',enemyAircraftEnabled:false});__AEGIS_DEPLOYMENT_A__.setDraft(cfg);document.getElementById('wip125DepartBtn').click();d.ciwsB1Closure.setPaused(true);v.c12ApplyPreset('LOW');v.orbit.distance=235;
 if(o.missiles)for(let i=0;i<o.missiles;i+=16)d.wip119DiagSpawnRealAsms({count:Math.min(16,o.missiles-i),label:'Kh-32',rangeKm:16,bearingsDeg:[-60,-20,20,60]});
 __AEGIS_SMOKE_C13__.audit();const pool=v.c13Smoke;for(let i=0;i<o.smoke;i++)pool.emit({x:(i%40)*1.6-32,y:15+(i%9),z:-30-Math.floor(i/40),birth:pool.time-2,life:25,base:.7+(i%8)*.1,growth:.12,alpha:.42,kind:[1,5,6][i%3],span:3,ax:1,rotation:i*.173,color:[.3,.27,.21],endColor:[.12,.13,.14]});
 const t=window.__NATIVE_RENDER_E__={frames:[],bytes:0},render=v.render,gl=v.renderer.getContext(),sub=gl.bufferSubData.bind(gl);
 gl.bufferSubData=function(target,offset,data,...rest){const length=rest.length>1?rest[1]:(data.length-(rest[0]??0));t.bytes+=length*data.BYTES_PER_ELEMENT;return sub(target,offset,data,...rest)};
 v.render=function(now){const start=performance.now();t.bytes=0;const r=render.call(this,now);t.frames.push({cpuMs:performance.now()-start,bufferSubDataBytes:t.bytes,calls:this.renderer.info.render.calls,triangles:this.renderer.info.render.triangles,geometries:this.renderer.info.memory.geometries,textures:this.renderer.info.memory.textures,particles:this.c13Smoke.count,glError:gl.getError()});return r};return {missiles:o.missiles,smoke:o.smoke};}'''
STATE=r'''()=>({state:__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B(),weapons:__NAVAL_SIM_DIAG__.weaponsSnapshotD(),rng:__HARPOON_DIAG_A__.snapshot().rng,core:__CORE_SELFTEST_FAILURES__,runtime:__WIP125_DIAG__.wip150RuntimeFault(),presentation:__WIP125_DIAG__.wip150PresentationFault()})'''
def digest(q):return hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[];pairs=[];errors=[]
 CG='CG_52_LATE_TICONDEROGA';DDG='DDG_119_LATE_FLIGHT_IIA';cases=[dict(ship=CG,missiles=0,smoke=0),dict(ship=CG,missiles=64,smoke=0),dict(ship=CG,missiles=64,smoke=1200),dict(ship=DDG,missiles=0,smoke=1200)]
 with sync_playwright()as pw:
  browser=launch(pw,True)
  for rep in range(2):
   for o in cases if rep==0 else list(reversed(cases)):
    pair={}
    for name,src in [('baseline',a.baseline),('candidate',a.html)][::1 if (rep+cases.index(o))%2==0 else -1]:
     page=load(browser,src.read_bytes(),o['ship'],True,errors=errors);page.set_viewport_size({'width':480,'height':360});page.evaluate(SETUP,o);page.wait_for_function('__NATIVE_RENDER_E__.frames.length>=4',timeout=90000);state=page.evaluate(STATE);page.evaluate('__NATIVE_RENDER_E__.frames=[]')
     page.wait_for_function('__NATIVE_RENDER_E__.frames.length>=8||__WIP125_DIAG__.wip150PresentationFault()',timeout=120000);frames=page.evaluate('__NATIVE_RENDER_E__.frames.slice(0,8)');after=page.evaluate(STATE);page.close()
     row={'repeat':rep,'config':o,'version':name,'state':state,'frames':frames,'meanCpuMs':statistics.mean(f['cpuMs']for f in frames),'meanBufferSubDataBytes':statistics.mean(f['bufferSubDataBytes']for f in frames),'checks':{'eightNativeFrames':len(frames)==8,'physicalFrozen':state==after,'coreAndFaultsZero':not state['core']and state['runtime']is None and state['presentation']is None,'glErrorZero':all(f['glError']==0 for f in frames)}};rows.append(row);pair[name]=row;(a.out/'native-render-progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'repeat':rep,'config':o,'version':name,'cpuMs':row['meanCpuMs'],'bytes':row['meanBufferSubDataBytes'],'checks':row['checks']}),flush=True)
    pairs.append({'repeat':rep,'config':o,'checks':{'physicalAndCombatRngExact':digest(pair['baseline']['state'])==digest(pair['candidate']['state']),'sameSubmittedTrianglesAndCalls':all((b['calls'],b['triangles'],b['particles'])==(c['calls'],c['triangles'],c['particles'])for b,c in zip(pair['baseline']['frames'],pair['candidate']['frames'])),'allNativeChecks':all(all(r['checks'].values())for r in pair.values())}})
  browser.close()
 summary=[]
 for o in cases:
  vals={n:[q['meanCpuMs']for q in rows if q['config']==o and q['version']==n]for n in ['baseline','candidate']};before=statistics.mean(vals['baseline']);after=statistics.mean(vals['candidate']);summary.append({'config':o,'cpuMs':vals,'meanBeforeMs':before,'meanAfterMs':after,'observedReductionPercent':100*(1-after/before),'meanBeforeTransferBytes':statistics.mean(q['meanBufferSubDataBytes']for q in rows if q['config']==o and q['version']=='baseline'),'meanAfterTransferBytes':statistics.mean(q['meanBufferSubDataBytes']for q in rows if q['config']==o and q['version']=='candidate')})
 checks={'allPairsPass':all(all(p['checks'].values())for p in pairs),'pageErrorsZero':not errors,'oppositeOrderWithinCase':all([r['version']for r in rows if r['config']==o and r['repeat']==0]==list(reversed([r['version']for r in rows if r['config']==o and r['repeat']==1]))for o in cases)}
 q={'sha256':hashlib.sha256(a.html.read_bytes()).hexdigest(),'baselineSha256':hashlib.sha256(a.baseline.read_bytes()).hexdigest(),'conditions':{'backend':'Native RAF/THREE/WebGL SwiftShader LOW480x360','seed':1831565813,'physics':'Paused; no fake frame clocks or diagnostic job drainage','workload':'Original ownship, native diagnostic64Kh32 distant models and optional1200 controlled smoke particles. Camera at ownship235m; distant missiles may be frustum culled, this is not64 simultaneous closeup missiles. Smoke age2 at fixed time, representing repeat-buffer frames, not all advancing smoke.','samples':'4 warm native frames,8 measured frames per page, two passes opposite AB/BA and reverse case traversal; serial after regression jobs','limits':'CPU render/THREE submission and native driver bufferSubData byte observations. Not actual GPU completion/hardware or phone FPS, natural combat effects, or an advancing-frame performance certification.'},'checks':checks,'pairs':pairs,'rows':rows,'summary':summary,'errors':errors,'pass':all(checks.values())};(a.out/'native-render.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'summary':summary}),flush=True);raise SystemExit(0 if q['pass']else 1)
if __name__=='__main__':main()
