"""Two-product guarded native planner-return diagnosis, never a product patch."""
from pathlib import Path
import hashlib,importlib.util,json
D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization');spec=importlib.util.spec_from_file_location('frozen_natural_battle',R1/'battle.py');battle=importlib.util.module_from_spec(spec);spec.loader.exec_module(battle)
def main():
 original=(R1/'battle.js').read_text();extension=(D/'extension.js').read_text();assert hashlib.sha256(original.encode()).hexdigest()=='bbecae524297ecb0f0c32969ad6079f4834dca4547fbcf402e551c5c81a0070b'
 assert original.count('install();active=false;')==1
 derived=extension+'\n'+original.replace('install();active=false;','install();window.__DEFENSE_CAUSE__.install();active=false;')
 assert derived.count('faults,nativeSources:sourceReceipt};')==1
 derived=derived.replace('faults,nativeSources:sourceReceipt};','faults,nativeSources:sourceReceipt,defenseExtra:window.__DEFENSE_CAUSE__.snapshot()};')
 target=D/'sampler.js';target.write_text(derived);battle.HELPER=target;battle.P=P
 source={'schema':'AEGIS_NATIVE_DEFENSE_RETURN_LOGGER_SOURCE_1','originalHelperSha256':hashlib.sha256(original.encode()).hexdigest(),'extensionSha256':hashlib.sha256(extension.encode()).hexdigest(),'derivedHelperSha256':hashlib.sha256(derived.encode()).hexdigest(),'runnerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sharedRunnerSha256':hashlib.sha256((R1/'battle.py').read_bytes()).hexdigest(),'productChanged':False,'expectedValuesChanged':False,'extraNativeCalls':0,'interpretation':'Require independent OFF_ON whole-native/passive/RNG guard per product before interpreting diagnostic records.'};(D/'SAMPLER_SOURCE.json').write_text(json.dumps(source,indent=2)+'\n');print(json.dumps(source),flush=True);return battle.main()
if __name__=='__main__':raise SystemExit(main())
