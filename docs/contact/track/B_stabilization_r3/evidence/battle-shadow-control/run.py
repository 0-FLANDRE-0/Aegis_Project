"""R3 shadow/native battle with explicit passive component/lifecycle observers."""
from pathlib import Path
import hashlib,importlib.util,json
D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization');R2=P.with_name('B_stabilization_r2')
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=module('frozen_battle',R1/'battle.py');trace=module('r2_trace_observer',R2/'evidence/battle-shadow-control/run.py').EXTENSION
def main():
 original=(R1/'battle.js').read_text();reacq=(P/'evidence/reacquisition-observer/extension.js').read_text();assert hashlib.sha256(original.encode()).hexdigest()=='bbecae524297ecb0f0c32969ad6079f4834dca4547fbcf402e551c5c81a0070b';assert hashlib.sha256(reacq.encode()).hexdigest()=='570a75e0ac634c9925cabb098e1a53ce8dc1a9f14d3aa0579a32116c5d49c2a2'
 assert original.count('install();active=false;')==1
 derived=trace+'\n'+reacq+'\n'+original.replace('install();active=false;','install();window.__R2_BATTLE_TRACE__.install();window.__REACQ_CAUSE__.install();active=false;');assert derived.count('faults,nativeSources:sourceReceipt};')==1
 derived=derived.replace('faults,nativeSources:sourceReceipt};','faults,nativeSources:sourceReceipt,r3Trace:window.__R2_BATTLE_TRACE__.snapshot(),reacqExtra:window.__REACQ_CAUSE__.snapshot()};')
 target=D/'sampler.js';target.write_text(derived);b.HELPER=target;b.P=P;case=json.loads(json.dumps(b.CASES['NATURAL_SATURATION_13']));case['id']='NATURAL_SATURATION_6';case['asms']=case['asms'][:6];b.CASES[case['id']]=case
 source={'schema':'AEGIS_R3_BATTLE_LIFECYCLE_SOURCE_1','originalHelperSha256':hashlib.sha256(original.encode()).hexdigest(),'reusedComponentObserverSha256':hashlib.sha256(trace.encode()).hexdigest(),'reacquisitionObserverSha256':hashlib.sha256(reacq.encode()).hexdigest(),'derivedHelperSha256':hashlib.sha256(derived.encode()).hexdigest(),'runnerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sharedRunnerSha256':hashlib.sha256((R1/'battle.py').read_bytes()).hexdigest(),'productChanged':False,'expectedValuesChanged':False,'extraNativeQueries':0,'scope':'Actual functions once; component proposals and lifecycle/task-owner transitions observed, never recomputed.'};(D/'SAMPLER_SOURCE.json').write_text(json.dumps(source,indent=2)+'\n');print(json.dumps(source),flush=True);return b.main()
if __name__=='__main__':raise SystemExit(main())
