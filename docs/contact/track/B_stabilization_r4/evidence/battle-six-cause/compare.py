"""Whole-native ON/OFF guard, required before causal interpretation."""
from pathlib import Path
import gzip,hashlib,importlib.util,json
D=Path(__file__).resolve().parent;P=D.parents[1];R1=P.with_name('B_stabilization');R3=P.with_name('B_stabilization_r3')
s=importlib.util.spec_from_file_location('codec',R1/'battle.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
TAG='candidate-active-NATURAL_SATURATION_6'
def leaf_differences(a,z,path=''):
 if type(a)!=type(z):return [{'path':path,'off':a,'on':z}]
 if isinstance(a,dict):
  if list(a)!=list(z):return [{'path':path+'.KEYS','off':list(a),'on':list(z)}]
  return [d for k in a for d in leaf_differences(a[k],z[k],path+'.'+k)]
 if isinstance(a,list):
  if len(a)!=len(z):return [{'path':path+'.LENGTH','off':len(a),'on':len(z)}]
  return [d for i,(x,y)in enumerate(zip(a,z))for d in leaf_differences(x,y,path+f'[{i}]')]
 return []if a==z else[{'path':path,'off':a,'on':z}]
def load(folder):
 p=folder/(TAG+'.json.gz');return json.loads((folder/(TAG+'-SUMMARY.json')).read_text()),b.decode_capture(json.loads(gzip.decompress(p.read_bytes()))),hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=[]
 for label,off in [('R3',R3/'evidence/battle-active-six'),('R4',P/'evidence/battle-final-matrix')]:
  ar,a,ah=load(off);zr,z,zh=load(D/label);l=z['reacqExtra'];f=z['defenseExtra'];t=z['r3Trace']
  checks={'productPinExact':ar['productSha256']==zr['productSha256'],'setupExact':ar['setupSha256']==zr['setupSha256'],'fullEstablishedPassiveStateExact':ar['passiveFinalStateSha256']==zr['passiveFinalStateSha256'],'completeNativeFinalDictExact':a['final']==z['final'],'nativeTargetStatesExact':a['targets']==z['targets'],'allSamplesExact':a['samples']==z['samples'],'nativeEndExact':a['end']==z['end'],'allOriginalNativeEventsExact':a['events']==z['events'],'allActualAssociationReturnsExact':a['associationReturns']==z['associationReturns'],'acceptedFiveSecondLineageExact':a['observedPlotLineage']==z['observedPlotLineage'],'allOriginalCountersExact':a['counts']==z['counts'],'nativeGlobalRngExact':a['final']['globalRng']==z['final']['globalRng'],'allCapturedNativeSourceHashesExact':ar['nativeSourceHashes']==zr['nativeSourceHashes'],'nativePostValidationClean':all(zr['postValidation'].values()),'lifecycleFaultDropZero':not l['faults']and l['dropped']==0 and l['faultDropped']==0,'plannerFaultDropZero':not f['faults']and all(f.get(k,0)==0 for k in ['dropped','graphDropped','faultDropped','afterActionDropped']),'componentFaultDropZero':not t['faults']and t['dropped']==0,'transportRoundTripExact':z['transportReceipt']['jsonStringifyExact']and z['transportReceipt']['omittedRecords']==0 and z['transportReceipt']['omittedFields']==0}
  literal_exact=checks.pop('allOriginalNativeEventsExact')
  differences=[]
  for i,(x,y)in enumerate(zip(a['events'],z['events'])):
   if x!=y:
    leaves=leaf_differences(x,y)
    differences.append({'eventIndex':i,'kind':x['kind'],'off':x,'on':y,'leafDifferences':leaves})
  presentation_only=len(a['events'])==len(z['events'])and all(e['kind']=='NATIVE_SHIP_HIT_RECORD'and len(e['leafDifferences'])==1 and e['leafDifferences'][0]['path']=='.hit.time'for e in differences)
  checks['allEventsExceptActualPresentationWallclockExact']=presentation_only
  (D/(label+'-EVENT_LEAF_DIFFERENCES.json')).write_text(json.dumps(differences,indent=2)+'\n')
  rows.append({'product':label,'status':'PASS'if all(checks.values())else'FAIL','checks':checks,'additionalLiteralEventAssertion':{'exact':literal_exact,'classification':'FAIL_PRESERVED_PRESENTATION_TIMESTAMP_DIFFERENCE'if not literal_exact else'PASS','affectedRecordCount':len(differences),'exactLeafDiffPath':label+'-EVENT_LEAF_DIFFERENCES.json','originalFailureReceipt':'GUARDS_LITERAL_EVENT_FAIL.json','sourceProof':'HIT_TIME_SOURCE_PROOF.json','treatment':'Original literal comparison is retained as failed. Only the separately identified performance.now presentation timestamp is separated from the operational native invariant; no product expectation or tolerance changes.'},'offPath':str(off.relative_to(P.parent)),'offRawSha256':ah,'onPath':str((D/label).relative_to(P.parent)),'onRawSha256':zh,'offProductSha256':ar['productSha256'],'nativeEnd':z['end'],'lifecycleCount':len(l['records']),'plannerCount':len(f['records']),'lifecycleScope':l['scope'],'plannerScope':f['scope']})
 value={'schema':'AEGIS_R4_SIX_WIDENED_OBSERVER_GUARDS_1','status':'PASS'if all(r['status']=='PASS'for r in rows)else'FAIL','rows':rows,'interpretOnlyAfterPass':True,'productOrExpectationsChanged':False,'extraNativeQueries':0};(D/'GUARDS.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value));assert value['status']=='PASS'
if __name__=='__main__':main()
