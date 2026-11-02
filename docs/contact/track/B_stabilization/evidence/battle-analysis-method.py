"""AFTER_ACTION only; no browser, product import, simulation call or feedback."""
from pathlib import Path
import argparse,csv,gzip,hashlib,importlib.util,itertools,json,math

P=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('battle_validator',P/'battle.py');battle=importlib.util.module_from_spec(spec);spec.loader.exec_module(battle)
sha=lambda b:hashlib.sha256(b).hexdigest()
angle=lambda x:math.atan2(math.sin(x),math.cos(x))

def analyze(row,raw):
 samples=raw['samples'];nearest=[];switches=[];previous={};many=[];truth_cross=[];observed_cross=[];last_truth={};last_observed={}
 for s in samples:
  truth=[t for t in s['truthAfterAction']if t.get('alive')];op=s['ownPositionM'];by_closest={}
  brg=lambda x,y:math.atan2(y-op['y'],x-op['x'])
  for a,b in itertools.combinations(truth,2):
   key=(a['id'],b['id']);value=angle(brg(b['positionM']['x'],b['positionM']['y'])-brg(a['positionM']['x'],a['positionM']['y']))
   if key in last_truth and last_truth[key][1]*value<0:truth_cross.append({'ids':key,'fromS':last_truth[key][0],'toS':s['timeS'],'beforeRad':last_truth[key][1],'afterRad':value})
   last_truth[key]=(s['timeS'],value)
  observed=[t for t in s['tracks']if t.get('kf6')]
  for a,b in itertools.combinations(observed,2):
   key=(a['trackId'],b['trackId']);value=angle(brg(b['kf6'][0],b['kf6'][1])-brg(a['kf6'][0],a['kf6'][1]))
   if key in last_observed and last_observed[key][1]*value<0:observed_cross.append({'trackIds':key,'fromS':last_observed[key][0],'toS':s['timeS'],'beforeRad':last_observed[key][1],'afterRad':value,'interpretation':'OBSERVED_BEARING_ORDER_ONLY_NOT_IDENTITY_PROOF'})
   last_observed[key]=(s['timeS'],value)
  for t in observed:
   distances=sorted(({'id':q['id'],'distanceM':math.sqrt(sum((t['kf6'][i]-q['positionM'][k])**2 for i,k in enumerate(['x','y','z'])))}for q in truth),key=lambda q:q['distanceM'])
   if not distances:continue
   sigma=math.sqrt(sum(max(0,x)for x in (t.get('Pdiag')or[])[:3]))if t.get('Pdiag')else None
   margin=distances[1]['distanceM']-distances[0]['distanceM']if len(distances)>1 else None
   q={'timeS':s['timeS'],'trackId':t['trackId'],'confirmed':t.get('confirmed'),'identity':t.get('identity'),'source':t.get('sensorSource'),'sensorAgeS':t.get('sensorAge'),'closest':distances[0],'second':distances[1]if len(distances)>1 else None,'distanceMarginM':margin,'filterPositionSigmaM':sigma,'oneSigmaOverlap':None if margin is None or sigma is None else margin<=sigma,'marginInterpretation':'AFTER_ACTION_GEOMETRIC_MARGIN_HEURISTIC_NOT_A_LIKELIHOOD_OR_IDENTITY_CERTIFICATE','interpretation':'UNKNOWN_NEAREST_GEOMETRY_ONLY','evaluationUniverse':'LIVE_INITIAL_ASMS_ONLY; does not include friendly weapons, decoys or wreckage'}
   nearest.append(q);by_closest.setdefault(distances[0]['id'],[]).append(q)
   old=previous.get(t['trackId'])
   if old and old['closest']['id']!=q['closest']['id']:switches.append({'trackId':t['trackId'],'before':old,'after':q,'priorNearestNoLongerInLiveInitialTruthSet':old['closest']['id']not in {v['id']for v in truth},'interpretation':'UNKNOWN_NOT_A_CERTIFIED_ID_SWAP; retirement can change the evaluation universe'})
   previous[t['trackId']]=q
  for physical,tracks in by_closest.items():
   if len(tracks)>1:many.append({'timeS':s['timeS'],'nearestPhysicalId':physical,'observedTracks':[{'id':t['trackId'],'closestDistanceM':t['closest']['distanceM'],'marginM':t['distanceMarginM'],'sigmaM':t['filterPositionSigmaM']}for t in tracks],'interpretation':'UNKNOWN_MANY_TO_ONE_NEAREST_GEOMETRY; not proof of a duplicate or bad merge'})
 returns=raw.get('associationReturns',[]);one_to_one=[];batches_multi=0
 for r in returns:
  selected=r['actualSelectedPairs'];plot_ids=[p['i']for p in selected];track_ids=[p['id']for p in selected]
  if len(selected)>1:batches_multi+=1
  if len(set(plot_ids))!=len(plot_ids)or len(set(track_ids))!=len(track_ids)or set(plot_ids)&set(r['actualHeldPlots'])or set(track_ids)&set(r['actualHeldTracks']):one_to_one.append(r)
 lineage=raw.get('observedPlotLineage',[]);lineage_buckets={}
 for r in lineage:
  if r.get('decision')not in ['ACCEPT','CREATE']or r.get('measurementId')is None:continue
  key=(r.get('observerShip'),r.get('route'),r.get('tick'),r['measurement'].get('sourceSensor'),r['measurementId']);lineage_buckets.setdefault(key,[]).append(r)
 observed_lineage_multi_file=[];repeated_same_file=[]
 for key,group in lineage_buckets.items():
  ids=sorted({r.get('trackId')for r in group if r.get('trackId')is not None})
  if len(ids)>1:observed_lineage_multi_file.append({'key':key,'receiverLocalTrackIds':ids,'records':group,'interpretation':'ONE_CAPTURED_MEASUREMENT_OBJECT_ACCEPTED_IN_MULTIPLE_LOCAL_FILES; observed structure, not nearest-truth inference'})
  elif len(group)>1:repeated_same_file.append({'key':key,'records':len(group),'trackIds':ids,'interpretation':'UNKNOWN_REPEATED_UPDATE_RECORD; birth/init and native hit increment must be inspected before calling it a duplicate hit'})
 events=raw['events'];first=lambda kind:next((e['timeS']for e in events if e['kind']==kind),None)
 final=raw['final']['ship'];water=sum(c['waterM3']for c in final['damage']['flooding']['cells']);validation=battle.post_validation(raw)
 effects=[e for e in events if e['kind']=='NATIVE_INTERCEPT_RESULT'];holds=raw['holdDurations']
 native_hit_records=[e for e in events if e['kind']=='NATIVE_SHIP_HIT_RECORD'];damaging_hits=[e for e in native_hit_records if(e['hit'].get('dmg')or 0)>0 and not e['hit'].get('miss')];native_ship_misses=[e for e in native_hit_records if e['hit'].get('miss')]
 return {'version':row['version'],'case':row['case'],'status':row['status'],'postValidation':validation,'validatedNoNativeFault':all(validation.values()),'productSha256':row['productSha256'],'fixtureSha256':row['fixtureSha256'],'setupSha256':row['setupSha256'],'passiveFinalStateSha256':row.get('passiveFinalStateSha256'),'rawSha256':sha(json.dumps(raw,separators=(',',':')).encode()),'initialPhysicalCount':raw['initialPhysicalCount'],'end':raw['end'],'hp':final['shipHP'],'waterM3':water,'moduleDamage':final['damage']['moduleDamage'],'nativeTargets':raw['targets'],'counts':raw['counts'],'times':{'firstRecordedSensorUpdateS':first('OBSERVED_SENSOR_RECORD'),'firstAutoFireLogS':first('NATIVE_AUTO_FIRE_LOG'),'firstWeaponLaunchS':first('NATIVE_WEAPON_LAUNCH'),'firstInterceptResultS':first('NATIVE_INTERCEPT_RESULT'),'firstPhysicalAllTerminalS':first('ALL_INITIAL_ASMS_NATIVE_TERMINAL'),'firstDamagingShipHitS':damaging_hits[0]['timeS']if damaging_hits else None,'firstNativeShipMissS':native_ship_misses[0]['timeS']if native_ship_misses else None},'damagingShipHitRecords':len(damaging_hits),'nativeShipMissRecords':len(native_ship_misses),'shipHitRecordMeaning':'Native shipHitHistory includes miss=true zero-damage reports. Primitive count is preserved; damaging and miss records are separated here.','nativeEffectPairs':effects,'actualReturnAudit':{'available':bool(returns),'nativeCallsCaptured':len(returns),'batchesWithMultipleSelectedPlots':batches_multi,'oneToOneOrHeldOverlapViolations':one_to_one,'actualHeldPlotAppearances':raw['counts'].get('actualHeldPlotAppearances'),'actualHeldTrackAppearances':raw['counts']['holds'],'proposalHeldPlotAppearances':raw['counts'].get('proposalHeldPlotAppearances'),'proposalByRoute':raw['counts'].get('proposalHeldPlotsByRoute'),'componentSemantics':sorted({r['componentSemantics']for r in returns}),'actualPairsAndHeldSetsFromSameNativeReturn':bool(returns)},'observedLineageAudit':{'available':bool(lineage),'captureWindowS':[0,5],'records':len(lineage),'distinctReceiverSourceMeasurementEpochKeys':len(lineage_buckets),'sameMeasurementAcceptedInDifferentFiles':observed_lineage_multi_file,'repeatedSameFileRecords':repeated_same_file,'scope':'Reported measurementId/local-file structure only. No truth ID. RF unresolved targets represented by one plot/file are not counted as a bad merge. Unsampled times and continuous identity correctness remain UNKNOWN.'},'holdMetricMeaning':'From actual applied held-track decision to next native ACCEPT UPDATE on that receiver-local track, across routes; not a persistent product/global HOLD flag. counts.holds is held-track appearances, not unique episodes.','holdEpisodes':len(holds),'holdDurations':holds,'holdOpenAtEnd':sum(bool(h.get('openAtEnd'))for h in holds),'maxObservedHoldToAcceptedUpdateS':max((h['durationS']for h in holds),default=0),'componentMetricAvailable':row['nativeSourceHashes'].get('association')is not None,'componentMaximum':raw['counts']['componentMaximum']if row['nativeSourceHashes'].get('association')else None,'componentsOver12':raw['counts']['componentsOver12']if row['nativeSourceHashes'].get('association')else None,'traceRingOverwriteCounts':{'a':raw['diagnostics']['a']['dropped'],'b':raw['diagnostics']['b']['dropped']if raw['diagnostics']['b']else None},'traceOverwriteMeaning':'Expected bounded-ring overwrite; pass-through primitive counters see all generated trace events. This is distinct from helper eventsDropped.','truthBearingCrossings':truth_cross,'observedBearingOrderReversals':observed_cross,'nearestTruthEvidence':nearest,'nearestLabelSwitches':switches,'manyToOneNearestGroups':many,'identitySwapVerdict':'UNKNOWN: geometry evidence retained, not an identity oracle or tactical input','inventory':raw['final']['inventory'],'autonomy':raw['final']['autonomy'],'nativeSourceHashes':row['nativeSourceHashes'],'releaseApproved':False}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('inputs',nargs='+',type=Path);ap.add_argument('--out',type=Path,default=P/'evidence/battle-analysis');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);rows=[]
 for folder in a.inputs:
  folder=folder.resolve()
  for path in sorted(folder.glob('*-SUMMARY.json')):
   row=json.loads(path.read_text());raw_path=path.with_name(path.name[:-len('-SUMMARY.json')]+'.json.gz')
   if 'case'not in row or not raw_path.exists():continue
   raw=battle.decode_capture(json.loads(gzip.decompress(raw_path.read_bytes())));result=analyze(row,raw);result['sourceFiles']={'row':str(path.relative_to(P)),'rowSha256':sha(path.read_bytes()),'raw':str(raw_path.relative_to(P)),'gzipSha256':sha(raw_path.read_bytes())};rows.append(result)
 case_groups={}
 for row in rows:case_groups.setdefault(row['case'],[]).append(row)
 comparisons=[]
 for case,group in case_groups.items():
  reference=next((r for r in group if r['version']=='track-a'),None)
  if reference is None:continue
  for row in group:
   if row is reference:continue
   worse=[]
   if row['hp']<reference['hp']:worse.append('LOWER_HP')
   if row['waterM3']>reference['waterM3']:worse.append('MORE_FLOODING')
   if any(v>reference['moduleDamage'].get(k,0)for k,v in row['moduleDamage'].items()):worse.append('MORE_MODULE_DAMAGE')
   if row['end']['remainingInitialThreats']>reference['end']['remainingInitialThreats']:worse.append('MORE_UNRESOLVED_INITIAL_THREATS')
   protected=['pipeline','samFlight','asmFlight','pk','applyPk','spawn','reset'];source_equal={k:row['nativeSourceHashes'][k]==reference['nativeSourceHashes'][k]for k in protected}
   terminal=lambda r:[{'id':t['id'],'alive':t.get('alive'),'retirementCause':t['retirement'].get('cause'),'nativeOutcome':t.get('_wip113Outcome'),'deathReason':t.get('_deathReason')}for t in r['nativeTargets']]
   comparisons.append({'case':case,'version':row['version'],'sameFixtureSha256':row['fixtureSha256']==reference['fixtureSha256'],'sameSetupSha256':row['setupSha256']==reference['setupSha256'],'protectedActualNativeSourceHashesEqual':source_equal,'outcomeWorseningIndicators':worse,'fullNativeTargetSnapshotEqual':row['nativeTargets']==reference['nativeTargets'],'nativeTerminalCausesEqual':terminal(row)==terminal(reference),'beforeCounts':reference['counts'],'afterCounts':row['counts'],'beforeTargets':reference['nativeTargets'],'afterTargets':row['nativeTargets'],'beforeEnd':reference['end'],'afterEnd':row['end'],'noAutomaticApproval':True})
 result={'schema':'AEGIS_TRACK_B_STABILIZATION_BATTLE_AFTER_ACTION_ANALYSIS_1','methodSha256':sha(Path(__file__).read_bytes()),'rows':rows,'comparisons':comparisons,'counts':{'pages':len(rows),'completedBattlePages':sum(r['status']=='QUALIFYING_COMPLETED_BATTLE'for r in rows),'nativeFaultFreePages':sum(r['validatedNoNativeFault']for r in rows),'comparisons':len(comparisons),'worseningComparisons':sum(bool(r['outcomeWorseningIndicators'])for r in comparisons)},'caseVersionCoverage':{k:sorted(r['version']for r in g)for k,g in case_groups.items()},'scope':'Limited deterministic scenarios, not a general success-rate or identity-accuracy claim. Original strict failures/expectations unchanged.','releaseApproved':False};(a.out/'SUMMARY.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
 with(a.out/'case-results.csv').open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=['case','version','status','hp','waterM3','initialPhysicalCount','endTimeS','remainingInitialThreats','launches','intercepts','holdEpisodes','maxHoldS','componentMaximum','componentsOver12','truthCrossings','observedReversals','nearestLabelSwitches','manyToOneNearestGroups','identityVerdict']);w.writeheader()
  for r in rows:w.writerow({'case':r['case'],'version':r['version'],'status':r['status'],'hp':r['hp'],'waterM3':r['waterM3'],'initialPhysicalCount':r['initialPhysicalCount'],'endTimeS':r['end']['timeS'],'remainingInitialThreats':r['end']['remainingInitialThreats'],'launches':json.dumps(r['counts']['launches']),'intercepts':json.dumps(r['counts']['intercepts']),'holdEpisodes':r['holdEpisodes'],'maxHoldS':r['maxObservedHoldToAcceptedUpdateS'],'componentMaximum':r['componentMaximum'],'componentsOver12':r['componentsOver12'],'truthCrossings':len(r['truthBearingCrossings']),'observedReversals':len(r['observedBearingOrderReversals']),'nearestLabelSwitches':len(r['nearestLabelSwitches']),'manyToOneNearestGroups':len(r['manyToOneNearestGroups']),'identityVerdict':r['identitySwapVerdict']})
 print(json.dumps(result['counts']|{'caseVersionCoverage':result['caseVersionCoverage']},indent=2))

if __name__=='__main__':main()
