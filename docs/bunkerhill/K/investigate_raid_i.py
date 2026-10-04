"""Real Kh-32 flight, sensors and AUTO; no synthetic tracks or render queue calls."""
import argparse,hashlib,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--main-override');p.add_argument('--count',type=int,default=6);p.add_argument('--seconds',type=int,default=200);p.add_argument('--scale',type=int,default=16);p.add_argument('--seed',type=int,default=174321);a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];samples=[];peaks={'ram':0,'bullets':0,'sam':0};phases=set();began=time.monotonic();exception=None
with sync_playwright()as pw:
 b=launch(pw);page=load(b,served_bytes(a.html,a.main_override),seed=a.seed,errors=errors)
 setup=page.evaluate('''n=>{const d=window.__NAVAL_SIM_DIAG__;d.spawnRealKh32Regression({rangeKm:95,bearingDeg:0});for(let i=1;i<n;i++)d.wip13cSpawnInboundInsAsm('Kh-32');d.wip119SetMode('AUTO');d.profilerEnableV48Wip11A(true);d.profilerResetV48Wip11A();return {snapshot:d.ciwsB1Closure.snapshot(),world:d.runtimeEntityCountsV48Wip11A?.()??null,entities:window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.hostileMissiles.length};}''',a.count)
 for frame in range(a.seconds*60//a.scale):
  try:
   q=page.evaluate('''scale=>{const d=window.__NAVAL_SIM_DIAG__;d.advanceFrameNoRender(1/60,scale);const e=window.__AEGIS_ENGAGEMENT_RUNTIME__.world.entities,c=d.ciwsB1Closure.snapshot();return {step:c.simStepCounter,mounts:c.mounts??null,ram:e.ramOrdnance.filter(m=>m.alive).length,bullets:e.ciwsProjectiles.length,sam:e.ordnance.filter(m=>!m.dead).length,hostile:e.hostileMissiles.filter(m=>m.alive).length,phases:e.hostileMissiles.filter(m=>m.alive).map(m=>m.phase),fault:window.__WIP125_DIAG__.wip150RuntimeFault()};}''',a.scale)
  except Exception as e:exception=str(e);break
  for key in peaks:peaks[key]=max(peaks[key],q[key])
  phases.update(q.pop('phases'))
  if frame%60==0:samples.append(q);print(json.dumps({'frame':frame,'wallS':round(time.monotonic()-began,1),**{k:q[k]for k in ['step','ram','bullets','sam','hostile','fault']}}),flush=True)
  if q['fault']or errors:break
 end=page.evaluate('''()=>({closure:window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot(),profile:window.__NAVAL_SIM_DIAG__.profilerSnapshotV48Wip11A(),hits:window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A().ship.damage,fault:window.__WIP125_DIAG__.wip150RuntimeFault(),runtimeCounts:window.__NAVAL_SIM_DIAG__.runtimeEntityCountsV48Wip11A?.()??null})''')
 b.close()
r={'schema':'AEGIS_REAL_KH32_RAID_INVESTIGATION_I','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'diagnosticOnlyMemoryOverride':bool(a.main_override),'parameters':vars(a),'setup':setup,'peaks':peaks,'phases':sorted(phases),'samples':samples,'end':end,'errors':errors,'exception':exception,'elapsedWallS':time.monotonic()-began,'completedWithoutFault':not(exception or errors or end['fault'])}
(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k]for k in ['peaks','phases','errors','exception','elapsedWallS','completedWithoutFault']}),flush=True)
if not r['completedWithoutFault']:raise SystemExit(1)
