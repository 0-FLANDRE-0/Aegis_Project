"""Pre-freeze natural6 qualification: frozen native sampler, normal spawn only."""
from pathlib import Path
import hashlib,importlib.util,json
D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization');spec=importlib.util.spec_from_file_location('frozen_battle',R1/'battle.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def main():
 original=b.HELPER.read_bytes();assert hashlib.sha256(original).hexdigest()=='bbecae524297ecb0f0c32969ad6079f4834dca4547fbcf402e551c5c81a0070b'
 case=json.loads(json.dumps(b.CASES['NATURAL_SATURATION_13']));case['id']='NATURAL_SATURATION_6';case['asms']=case['asms'][:6];b.CASES[case['id']]=case;b.P=P
 source={'schema':'AEGIS_NATURAL6_QUALIFICATION_PLAN_1','case':case,'seed':419027,'fixtureSha256':hashlib.sha256(original).hexdigest(),'originalHelperSource':str(b.HELPER),'sharedRunnerSha256':hashlib.sha256((R1/'battle.py').read_bytes()).hexdigest(),'wrapperSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'onlyNewNormalPlacementCount':True,'physicsSensorAuthorityAiCoefficientsChanged':False,'expectedValuesChanged':False,'initialTrackInjection':False,'maxHeavyBrowserLanes':1,'qualificationRequired':'Actual HOLD incidence and native terminal outcomes/survival; retain every failure, no post-result setup change.'};(D/'CASE_SOURCE.json').write_text(json.dumps(source,indent=2)+'\n');print(json.dumps(source),flush=True);return b.main()
if __name__=='__main__':raise SystemExit(main())
