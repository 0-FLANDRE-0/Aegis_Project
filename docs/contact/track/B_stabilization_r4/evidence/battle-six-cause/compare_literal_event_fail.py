"""Whole-native ON/OFF guard, required before causal interpretation."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization');R3=P.with_name('B_stabilization_r3')
s=importlib.util.spec_from_file_location('codec',R1/'battle.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
TAG='candidate-active-NATURAL_SATURATION_6'
def load(folder):
 p=folder/(TAG+'.json.gz');return json.loads((folder/(TAG+'-SUMMARY.json')).read_text()),b.decode_capture(json.loads(gzip.decompress(p.read_bytes()))),hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=[]
 for label,off in [('R3',R3/'evidence/battle-active-six'),('R4',P/'evidence/battle-final-matrix')]:
  ar,a,ah=load(off);zr,z,zh=load(D/label);l=z['reacqExtra'];f=z['defenseExtra'];t=z['r3Trace']
  checks={'productPinExact':ar['productSha256']==zr['productSha256'],'setupExact':ar['setupSha256']==zr['setupSha256'],'fullEstablishedPassiveStateExact':ar['passiveFinalStateSha256']==zr['passiveFinalStateSha256'],'completeNativeFinalDictExact':a['final']==z['final'],'nativeTargetStatesExact':a['targets']==z['targets'],'allSamplesExact':a['samples']==z['samples'],'nativeEndExact':a['end']==z['end'],'allOriginalNativeEventsExact':a['events']==z['events'],'allActualAssociationReturnsExact':a['associationReturns']==z['associationReturns'],'acceptedFiveSecondLineageExact':a['observedPlotLineage']==z['observedPlotLineage'],'allOriginalCountersExact':a['counts']==z['counts'],'nativeGlobalRngExact':a['final']['globalRng']==z['final']['globalRng'],'allCapturedNativeSourceHashesExact':ar['nativeSourceHashes']==zr['nativeSourceHashes'],'nativePostValidationClean':all(zr['postValidation'].values()),'lifecycleFaultDropZero':not l['faults']and l['dropped']==0 and l['faultDropped']==0,'plannerFaultDropZero':not f['faults']and all(f.get(k,0)==0 for k in ['dropped','graphDropped','faultDropped','afterActionDropped']),'componentFaultDropZero':not t['faults']and t['dropped']==0,'transportRoundTripExact':z['transportReceipt']['jsonStringifyExact']and z['transportReceipt']['omittedRecords']==0 and z['transportReceipt']['omittedFields']==0}
  rows.append({'product':label,'status':'PASS'if all(checks.values())else'FAIL','checks':checks,'offPath':str(off.relative_to(P.parent)),'offRawSha256':ah,'onPath':str((D/label).relative_to(P.parent)),'onRawSha256':zh,'offProductSha256':ar['productSha256'],'nativeEnd':z['end'],'lifecycleCount':len(l['records']),'plannerCount':len(f['records']),'lifecycleScope':l['scope'],'plannerScope':f['scope']})
 value={'schema':'AEGIS_R4_SIX_WIDENED_OBSERVER_GUARDS_1','status':'PASS'if all(r['status']=='PASS'for r in rows)else'FAIL','rows':rows,'interpretOnlyAfterPass':True,'productOrExpectationsChanged':False,'extraNativeQueries':0};(D/'GUARDS.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value));assert value['status']=='PASS'
if __name__=='__main__':main()
