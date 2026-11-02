"""Two guarded diagnostic pages; widen only test-only passive observer scope."""
from pathlib import Path
import hashlib,importlib.util,json
D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization');R2=P.with_name('B_stabilization_r2');R3=P.with_name('B_stabilization_r3')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=module('frozen_battle',R1/'battle.py');trace=module('r2_component',R2/'evidence/battle-shadow-control/run.py').EXTENSION
def replace_once(source,old,new):
 assert source.count(old)==1,(old,source.count(old));return source.replace(old,new)
def main():
 original=(R1/'battle.js').read_text();reacq_original=(R3/'evidence/reacquisition-observer/extension.js').read_text();planner_original=(R2/'evidence/defense-timing-logger/extension.js').read_text()
 assert hashlib.sha256(original.encode()).hexdigest()=='bbecae524297ecb0f0c32969ad6079f4834dca4547fbcf402e551c5c81a0070b'
 assert hashlib.sha256(reacq_original.encode()).hexdigest()=='570a75e0ac634c9925cabb098e1a53ce8dc1a9f14d3aa0579a32116c5d49c2a2'
 assert hashlib.sha256(planner_original.encode()).hexdigest()=='3bb3b5ed110f20797f3ea54f96741f5484e126da787d70c9a2aa7bffbc71ce93'
 reacq=replace_once(reacq_original,'const FROM_S=12,TO_S=26,MAX_RECORDS=16384,MAX_FAULTS=64;','const FROM_S=0,TO_S=45,MAX_RECORDS=65536,MAX_FAULTS=64;')
 reacq=replace_once(reacq,"const relevant=t=>inWindow()&&FOCUS.has(own(t,'trackId'));","const relevant=t=>inWindow();")
 reacq=replace_once(reacq,'function track(t){return','function baseTrack(t){return')
 reacq=replace_once(reacq,' function task(t){'," function track(t){const out=baseTrack(t),x=own(t,'_kfX'),p=own(t,'_kfP');if(x&&x.length===6)out.kf6=Array.from(x);if(p&&p.length===36)out.Pdiag=[0,7,14,21,28,35].map(i=>p[i]);return out;}\n function task(t){")
 reacq=reacq.replace('trackIds:Array.from(FOCUS)','trackIds:null,allTracks:true')
 planner=replace_once(planner_original,'const FROM_S = 12, TO_S = 26, MAX_RECORDS = 12000, MAX_GRAPHS = 256;','const FROM_S = 30, TO_S = 41, MAX_RECORDS = 24000, MAX_GRAPHS = 256;')
 planner=replace_once(planner,'function focused(id) { return inWindow() && FOCUS.has(id); }','function focused(id) { return inWindow(); }')
 # Diagnostic descriptors only; all native call/return wrappers are unchanged.
 planner=replace_once(planner,'focusTrackIds: Array.from(FOCUS)','focusTrackIds: null, allTracks: true, brakeResponseSnapshotTrackIds: Array.from(FOCUS)')
 derived=trace+'\n'+reacq+'\n'+planner+'\n'+replace_once(original,'install();active=false;','install();window.__R2_BATTLE_TRACE__.install();window.__REACQ_CAUSE__.install();window.__DEFENSE_CAUSE__.install();active=false;')
 derived=replace_once(derived,'faults,nativeSources:sourceReceipt};','faults,nativeSources:sourceReceipt,r3Trace:window.__R2_BATTLE_TRACE__.snapshot(),reacqExtra:window.__REACQ_CAUSE__.snapshot(),defenseExtra:window.__DEFENSE_CAUSE__.snapshot()};')
 for name,text in [('sampler.js',derived),('lifecycle.js',reacq),('planner.js',planner)]:
  (D/name).write_text(text)
 source={'schema':'AEGIS_R4_SIX_CAUSAL_PASSIVE_OBSERVER_1','originalHelperSha256':hashlib.sha256(original.encode()).hexdigest(),'originalLifecycleSha256':hashlib.sha256(reacq_original.encode()).hexdigest(),'originalPlannerSha256':hashlib.sha256(planner_original.encode()).hexdigest(),'lifecycleSha256':hashlib.sha256(reacq.encode()).hexdigest(),'plannerSha256':hashlib.sha256(planner.encode()).hexdigest(),'derivedHelperSha256':hashlib.sha256(derived.encode()).hexdigest(),'lifecycleScope':'all receiver-local tracks0–45s; capacity65536; kf6/Pdiag are direct cached values','plannerScope':'all receiver-local tracks30–41s; actual original planner/FCQ/gate returns only; no extra queries','wholeStateGuardRequiredBeforeInterpretation':True,'productOrExpectedValuesChanged':False,'extraNativeCalls':0}
 (D/'SOURCE.json').write_text(json.dumps(source,indent=2)+'\n');print(json.dumps(source),flush=True)
 b.HELPER=D/'sampler.js';b.P=P;c=json.loads(json.dumps(b.CASES['NATURAL_SATURATION_13']));c['id']='NATURAL_SATURATION_6';c['asms']=c['asms'][:6];b.CASES[c['id']]=c
 return b.main()
if __name__=='__main__':raise SystemExit(main())
