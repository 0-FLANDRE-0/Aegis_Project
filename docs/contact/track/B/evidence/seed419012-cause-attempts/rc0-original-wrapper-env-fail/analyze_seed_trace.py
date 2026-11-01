"""Read-only analysis of saved 419012 passive traces; no game or browser input."""
from pathlib import Path
import argparse,csv,gzip,hashlib,json
from trace_seed import diff

P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(path):return json.load(gzip.open(path,'rt'))
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,default=P/'evidence/seed419012-cause');args=parser.parse_args();p=args.out
 traces={label:read(p/(label+'-diagnostics.json.gz'))for label in ['baseline','active']};frames={label:{r['step']:r for r in d['records']if r['kind']=='PASSIVE_RECEIVER_FRAME'}for label,d in traces.items()};common=sorted(set(frames['baseline'])&set(frames['active']))
 receipts={label:json.loads((p/(label+'-receipt.json')).read_text())for label in traces}
 first={}
 with gzip.open(p/'all-captured-frame-differences.jsonl.gz','wt')as out:
  count=0
  for step in common:
   a,b=[frames[label][step]['value']for label in traces]
   for row in diff(a,b):
    row={'step':step,'timeS':step/60,**row};out.write(json.dumps(row,separators=(',',':'))+'\n');count+=1
    category=row['path'].split('/')[1];first.setdefault(category,row)
 holds=[r for r in traces['active']['records']if r['kind']=='ALREADY_EMITTED_B_TRACE'and r['value'].get('decision')=='HOLD']
 first_hold=holds[0]if holds else None
 native_candidates={}
 if first_hold:
  for label in traces:
   native_candidates[label]=[r for r in traces[label]['records']if r['step']==first_hold['step']and r['kind']=='ALREADY_EMITTED_A_TRACE'and r['value'].get('type')=='CANDIDATE'and r['value'].get('route')=='SPY_BATCH']
 a_candidates=native_candidates.get('baseline',[]);native_nis={r['value']['trackId']:r['value']['nis']for r in a_candidates}
 updates={label:[{'step':r['step'],'timeS':r['timeS'],'trackId':r['value'].get('trackId'),'source':r['value'].get('measurement',{}).get('sourceSensor'),'decision':r['value'].get('decision'),'hits':r['value'].get('after',{}).get('sensorHits'),'reason':r['value'].get('reason')}for r in traces[label]['records']if r['kind']=='ALREADY_EMITTED_A_TRACE'and r['value'].get('type')=='UPDATE'and r['value'].get('route')=='PLAYER_MEASUREMENT']for label in traces}
 cue_changes={}
 for label in traces:
  last=None;changes=[]
  for step in common:
   r=frames[label][step];v=r['value'];value={'mounts':v['mounts'],'cmsAssociation':[{'mountId':b['mountId'],'files':[{'id':f['id'],'cmsTrackId':f.get('cmsTrackId')}for f in b['files']]}for b in v['c55']]}
   compact={'cues':[[m['id'],m.get('cuedTarget'),m.get('trackingTrackId')]for m in v['mounts']],'cmsAssociation':value['cmsAssociation']}
   if compact!=last:changes.append({'step':step,'timeS':r['timeS'],**compact});last=compact
  cue_changes[label]=changes
 def local(value):return [{'mountId':b['mountId'],'winner':b.get('winner'),'status':b.get('status'),'reason':b.get('reason'),'files':[{k:v for k,v in f.items()if k!='cmsTrackId'}for f in b['files']]}for b in value['c55']]
 def mount_control(value):return [{k:v for k,v in m.items()if k!='cuedTarget'}for m in value['mounts']]
 local_exact=all(local(frames['baseline'][step]['value'])==local(frames['active'][step]['value'])for step in common)
 mount_exact=all(mount_control(frames['baseline'][step]['value'])==mount_control(frames['active'][step]['value'])for step in common)
 original={label:read(p/(label+'-original-result-after-action.json.gz'))['row']for label in traces}
 after_diff=list(diff(original['baseline']['after'],original['active']['after']))
 with gzip.open(p/'all-cross-version-original-output-differences.jsonl.gz','wt')as out:
  cross_count=0
  for row in diff(original['baseline'],original['active']):out.write(json.dumps(row,separators=(',',':'))+'\n');cross_count+=1
 summary={'schema':'AEGIS_TRACK_B_SEED419012_CAUSAL_ANALYSIS_1','status':'PARTIAL_CAUSAL_EVIDENCE_STRICT_DELTA_UNAPPROVED','sourceFiles':[{'name':label+'-diagnostics.json.gz','sha256':sha((p/(label+'-diagnostics.json.gz')).read_bytes())}for label in traces],'instrumentationControls':{label:{'exactOffSignature':r['checks']['exactOriginalOffSignature'],'allFailedChecks':[k for k,v in r['checks'].items()if not v],'allOriginalReferenceDifferences':r['allRawDifferenceCount'],'env':r['env']}for label,r in receipts.items()},'envExplanation':'The unchanged original diagnostic.js wraps spawnEnemyMissile and applyInterceptResult, so awaited ENV status correctly reports those test bindings as different. Profile hashes match. No clean restored-binding ENV proof was executed in these two runs. This failure is preserved, not silently passed.','window':{'firstStep':common[0],'lastStep':common[-1],'frames':len(common),'firstRowsTracks':{label:frames[label][common[0]]['value']['tracks']for label in traces}},'firstDifferentByCategory':first,'firstCapturedHold':first_hold,'nativeCandidateRecordsAtHold':native_candidates,'sameObservedMeasurementAtFirstHold':bool(len(a_candidates)==2 and len(native_candidates.get('active',[]))==2 and [r['value']['measurement']for r in a_candidates]==[r['value']['measurement']for r in native_candidates['active']]),'sameNativeCandidateNisAtFirstHold':{label:{str(r['value']['trackId']):r['value']['nis']for r in values}for label,values in native_candidates.items()},'nativeCandidateNisDifference':abs(native_nis.get(300000001,0)-native_nis.get(300000002,0))if len(native_nis)==2 else None,'canonicalUpdates':updates,'cueAndCmsTransitions':cue_changes,'selectedDiagnosticComparisonsNotReplacementStrictTests':{'allCapturedLocalC55FileFieldsExceptCmsTrackIdExact':local_exact,'allCapturedMountFieldsExceptCuedTargetExact':mount_exact,'allFrameFieldsPreservedInRawDifferenceStream':True,'rawFrameDifferenceCount':count,'rawOriginalOutputDifferenceCount':cross_count,'fullAfterActionAfterFieldDifferences':after_diff},'actualObservedChain':['Both canonical files already exist at the first captured frame29.0s; no CREATE occurs in the captured window. Earlier birth/source history is outside this trace.','At native tick1796, identical SPY_SEARCH_HORIZON measurement has two eligible native AIR4D NIS values separated by0.3376654351748743. A accepts track300000002; B reports AMBIGUOUS_ASSOCIATION and withholds this update.','The first passive estimated-track divergence is post-tick frame1797. Subsequent native focused revisit/source update schedules and estimates differ.','The first captured C55 CMS-association and mount-cue differences occur at frame1800. Negative local C55 file IDs and all captured local estimated/control fields remain exact when separately displaying the differing CMS/cue labels.','At termination the full original after-action output differs only in the two mount cue fields. The original strict signature difference remains FAIL, not an approved new baseline.'],'sourcePathAudit':{'c55CmsRows':'Pinned A source L37288–37297 obtains observed CMS states; L37402 sorts eligible cue rows by native kin.ttiS.','c55AssociateCms':'L37299–37315 ranks local-to-observed-CMS geometric distance and writes cmsTrackId; no truth resolution in this association.','updateCueing':'L37965–37968 assigns c55Bank(mount).cues[0].trackId to m.cuedTarget.','localFireControl':'L37955/L37421 select local negative C55 files for actual tracking/fire, while cue data remains separate.'},'unknowns':['Cached b.cues TTI values were not captured, so their numerical rank cannot be reconstructed as actual recorded values. Source-path explanation is distinct from a measured TTI ranking.','No earlier-than29.0s canonical birth timeline was captured. This evidence does not prove duplicate elimination or explain initial creation of the preexisting second file.','This is temporal and code-path evidence for the captured branch, not proof that future battle outcomes are unaffected.','Awaited ENV mismatch is confined to the original diagnostic wrappers as reported, but clean after-restoration ENV status was not measured.'],'claimsExplicitlyNotMade':['Duplicate elimination','Truth target identity equality','Strict D1 baseline approval','All future combat unchanged','Full TRACK-B closure'],'automaticApproval':False,'expectedValuesUpdated':False,'releaseApproved':False}
 (p/'ANALYSIS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 with(p/'canonical-updates.csv').open('w')as out:
  writer=csv.DictWriter(out,fieldnames=['product','step','timeS','trackId','source','decision','hits','reason']);writer.writeheader()
  for label,rows in updates.items():
   for row in rows:writer.writerow({'product':label,**row})
 print(json.dumps({'status':summary['status'],'firstDifferentFrames':{k:v['step']for k,v in first.items()},'nativeNisDifference':summary['nativeCandidateNisDifference'],'localDynamicsExact':local_exact,'localControlExact':mount_exact,'afterActionDifferences':after_diff,'rawFrameDifferenceCount':count,'rawOriginalOutputDifferenceCount':cross_count,'automaticApproval':False},ensure_ascii=False))
if __name__=='__main__':main()
