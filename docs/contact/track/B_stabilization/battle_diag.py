"""Run the ordinary battle fixture with optional bounded pass-through cause log.

Uses battle.py CLI unchanged. Derived test helper is explicit and hashed. This
never changes a product or original expectation. Interpret logs only after a
same-product OFF/ON native-state equivalence guard.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,sys

P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('battle_with_cause_log',P/'battle.py');battle=importlib.util.module_from_spec(spec);spec.loader.exec_module(battle)
def main():
 original=battle.HELPER.read_text();extra=(P/'battle_diag.js').read_text()
 anchor='install();active=false;'
 assert original.count(anchor)==1
 derived=extra+'\n'+original.replace(anchor,'install();window.__TRACK_BATTLE_CAUSE__.install();active=false;')
 anchor='faults,nativeSources:sourceReceipt};'
 assert derived.count(anchor)==1
 derived=derived.replace(anchor,'faults,nativeSources:sourceReceipt,causalExtra:window.__TRACK_BATTLE_CAUSE__.snapshot()};')
 target=Path('/dev/shm')/('aegis-battle-cause-'+str(os.getpid())+'.js');target.write_text(derived);battle.HELPER=target
 marker={'schema':'AEGIS_BATTLE_CAUSE_LOGGER_SOURCE_1','originalHelperSha256':hashlib.sha256(original.encode()).hexdigest(),'extensionSha256':hashlib.sha256(extra.encode()).hexdigest(),'derivedHelperSha256':hashlib.sha256(derived.encode()).hexdigest(),'wrapperRunnerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'productChanged':False,'extraNativeCalls':0,'approval':'REQUIRES_OFF_ON_EQUIVALENCE_GUARD'}
 if '--out'in sys.argv:
  out=Path(sys.argv[sys.argv.index('--out')+1]);out.mkdir(parents=True,exist_ok=True);(out/'LOGGER_SOURCE.json').write_text(json.dumps(marker,indent=2)+'\n')
 print(json.dumps(marker),flush=True)
 return battle.main()

if __name__=='__main__':raise SystemExit(main())
