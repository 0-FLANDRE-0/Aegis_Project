"""Hash-bound post-hoc provenance closure; no new physical UID or game write."""
from pathlib import Path
import hashlib,json
import battles
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 source=P/'evidence/noise-origin/RESULTS.json';result=json.loads(source.read_text());assert result['status']=='PASS'and result['measurementsResolved']==10 and len(result['rows'])==10
 rows=[]
 for r in result['rows']:
  assert r['status']=='PASS'and all(r['checks'].values())
  plan=json.loads((P/'evidence/noise-origin/runs'/r['id']/'JOB.json').read_text());raw=P/'evidence/noise-origin/runs'/r['id']/('candidate-active-'+plan['case']['id']+'.json.gz');assert sha(raw)==r['rawSha256']
  original,_=battles.load(battles.selected_out(r['id']));records=original['trackCLineage']['records']
  for match in r['matches']:
   e=match['event'];assert e['event']=='UNRESOLVED_RF_LINEAGE'and e['lineageStatus']=='UNLINKED'and match['exactOriginProven']and len(match['generatorMatches'])==1
   g=match['generatorMatches'][0];assert g['step']==e['step']and g['source']==e['source']and g['fields']==e['fields']and g['origin']=='NATIVE_RECEIVER_PROCESSING_FALSE_ALARM_NO_REFLECTOR'
   exact={k:v for k,v in e.items()if k!='event'};assert sum(q==exact for q in records)==1
   rows.append({'id':r['id'],'exactOriginalRecord':exact,'origin':g['origin'],'physicalUid':None,'newPhysicalLabelInvented':False,'nativeGeneratorOutput':g,'replayRawSha256':r['rawSha256']})
 assert len(rows)==10
 sourcejs=Path('/dev/shm/track-c-base.js').read_text();start=sourcejs.index('function spyFalsePlotV31(');end=sourcejs.index('\nfunction ',start+1);fn=sourcejs[start:end]
 path=P/'evidence/noise-origin/unchanged-native-false-plot.js';path.write_text(fn+'\n')
 for name in ['active','shadow']:assert fn in Path('/dev/shm/track-c-'+name+'.js').read_text()
 q={'schema':'AEGIS_TRACK_C_EXACT_NO_REFLECTOR_ORIGIN_1','status':'PASS','sourceProof':'evidence/noise-origin/RESULTS.json','sourceProofSha256':sha(source),'generatorSourceSha256':sha(path),'resolvedMeasurements':10,'productCounts':{'R4':6,'C':4},'allReplaysFinalLineageAndPrivateRngExact':True,'physicalUidInvented':False,'gameOrStatisticalTrialsModified':False,'rows':rows}
 (P/'NOISE_ORIGIN_CLOSURE.json').write_text(json.dumps(q,indent=2)+'\n');print({k:v for k,v in q.items()if k!='rows'})
if __name__=='__main__':main()
