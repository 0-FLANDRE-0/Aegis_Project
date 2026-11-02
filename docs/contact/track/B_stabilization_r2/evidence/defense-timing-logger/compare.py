"""Verify each planner logger run against its exact same-product OFF capture."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization');spec=importlib.util.spec_from_file_location('battle_codec',R1/'battle.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def load(directory,tag):
 path=directory/(tag+'.json.gz');row=json.loads((directory/(tag+'-SUMMARY.json')).read_text());return row,b.decode_capture(json.loads(gzip.decompress(path.read_bytes()))),hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 refs={'old-active':R1/'evidence/battle-final','candidate-active':P/'evidence/battle-active-pilot'};rows=[];pending=[]
 for version,folder in refs.items():
  tag=version+'-NATURAL_SATURATION_13'
  if not(D/(tag+'-SUMMARY.json')).exists():pending.append(version);continue
  ar,a,ha=load(folder,tag);zr,z,hz=load(D,tag);extra=z['defenseExtra'];checks={'samePinnedProduct':ar['productSha256']==zr['productSha256'],'sameSetup':ar['setupSha256']==zr['setupSha256'],'fullEstablishedPassiveStateExact':ar['passiveFinalStateSha256']==zr['passiveFinalStateSha256'],'completeNativeFinalDictExact':a['final']==z['final'],'initialNativeTargetsExact':a['targets']==z['targets'],'sampledObservationAndTruthStateExact':a['samples']==z['samples'],'nativeEndAndTicksExact':a['end']==z['end'],'nativeGlobalRngExact':a['final']['globalRng']==z['final']['globalRng'],'nativeInterceptionHistoryExact':a['final']['interceptHistory']==z['final']['interceptHistory'],'allCapturedActualAssociationReturnsExact':a['associationReturns']==z['associationReturns'],'nativePrimitiveCountersExact':a['counts']==z['counts'],'nativeSourceReceiptsExact':ar['nativeSourceHashes']==zr['nativeSourceHashes'],'nativePostValidationClean':all(zr['postValidation'].values()),'extraFaultZero':extra['faults']==[],'extraDropZero':all(extra[k]==0 for k in ['dropped','graphDropped','faultDropped','afterActionDropped']),'pureObserverGuardPass':json.loads((D/'PURE_GUARD.json').read_text())['status']=='PASS'}
  rows.append({'version':version,'status':'PASS'if all(checks.values())else'FAIL','checks':checks,'offRawSha256':ha,'onRawSha256':hz,'offPassiveSha256':ar['passiveFinalStateSha256'],'onPassiveSha256':zr['passiveFinalStateSha256'],'productSha256':zr['productSha256'],'extraRows':{k:len(extra[k])for k in ['records','largeGraphs','afterActionSnapshots']},'nativeOutcome':{'hp':z['final']['ship']['shipHP'],'end':z['end'],'effects':z['counts']['intercepts']}})
 result={'schema':'AEGIS_NATIVE_PLANNER_LOGGER_OFF_ON_GUARDS_1','status':'PENDING'if pending else'PASS'if all(r['status']=='PASS'for r in rows)else'FAIL','pending':pending,'rows':rows,'interpretOnlyAfterBothPass':True,'releaseApproved':False};(D/'OFF_ON_GUARDS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert pending or result['status']=='PASS'
if __name__=='__main__':main()
