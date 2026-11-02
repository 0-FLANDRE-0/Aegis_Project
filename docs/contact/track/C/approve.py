"""Conditional user approvals, exact values and exact reviewed product only.

No game code, original assertion or tolerance is changed. Default verifies;
--create is refused until every directive5 validation gate has passed.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,time
P=Path(__file__).resolve().parent;R=P.parents[3]
def read(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def value_hash(q):return hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
projection=module('unchanged_air_origin_projection_c',R/'docs/radar/air-origin/A/approved_expectations.py')
def gates(enforce_budget=False):
 q=read(P/'VALIDATION.json');assert q['status']=='PASS'and all(q['checks'].values()),'ALL_DIRECTIVE5_GATES_REQUIRED'
 if enforce_budget:assert time.monotonic()<=read(P/'evidence/BUDGET.json')['deadlineMonotonic'],'FOUR_HOUR_WALL_CAP'
 build=read(P/'BUILD.json');assert sha(R/build['html'])==q['candidateSha256']==build['htmlSha256'];assert read(P/'STATISTICS.json')['primaryPass']and read(P/'D1_STATISTICS.json')['primaryPass'];return build
def entry(key,old,new,cause,**extra):
 assert old!=new
 return {'id':key,'oldExpected':old,'newExpected':new,'oldValueSha256':value_hash(old),'newValueSha256':value_hash(new),'causePath':cause,'tolerance':'EXACT_EQUALITY','authority':'TRACK_C directive sections4,5,6; conditional result met',**extra}
def create():
 build=gates(enforce_budget=True);entries=[];historical=R/'docs/contact/friendly/A/evidence/regression/paired-current/baseline-comparison.json';report=read(historical);assert report['candidateSha256']=='cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda';assert read(R/'docs/contact/friendly/A/SCOPE.json')['pass'];assert read(R/'docs/contact/friendly/A/BUILD.json')['inverseByteExact']
 for row in report['cases']:
  if all(row['checks'].values()):continue
  assert row['scenario']=='raid'and[k for k,v in row['checks'].items()if not v]==['sameExistingObserverState']
  old=projection.pair_value(row['pair']['baseline'],'sameExistingObserverState');new=projection.pair_value(row['pair']['candidate'],'sameExistingObserverState')
  entries.append(entry('HISTORICAL_FRIENDLY:'+row['ship']+':raid:sameExistingObserverState',old,new,'friendly-contact-a accepted3D AIR evidence →16s surface-prior guard → native owner EKF/classification/scheduler state; physical state, combat RNG, hull layout, inventory, offboard and faults remain original exact PASS.',kind='HISTORICAL_OBSERVER_EXACT',ship=row['ship'],historicBaselineHtmlSha256=report['baselineSha256'],historicReviewedHtmlSha256=report['candidateSha256'],sourceReport=str(historical.relative_to(R)),sourceReportSha256=sha(historical),reason='User directive4: difference is within already-approved friendly-contact-a observation-dimension/continuity scope, audited by C1. Not a new C physical regression.'))
 assert len(entries)==2
 old30=read(R/'docs/contact/friendly/A/analysis/ciws30.json');old25=next(q for q in old30['rows']if q['seed']==419025);assert old25['beforeHits']==0 and old25['afterHits']==1;d1=read(P/'D1_STATISTICS.json');now25=next(q for q in d1['pairs']if q['seed']==419025);assert now25['R4']['leakers']==now25['C']['leakers']==1
 entries.append(entry('CIWS419025:physicalContactLeakers',0,1,'Original component-isolated CIWS own-fire partition repair enables legitimate Phalanx shots; real subsequent multi-weapon damage/RNG branches change. Current30 paired seeds: primary4→4 leakers and4→4 damaging callbacks. No damage/Pk/seeker compensation.',kind='INHERITED_OUTCOME',seed=419025,currentReviewedSignature=now25['C']['signatureSha256'],historicalLegacyCounterTotals={'before':old30['beforeHits'],'after':old30['afterHits']},historicalLegacyCountersNotPhysicalContactEstimate=True,sourceCause='docs/contact/friendly/A/REPORT.md §3; docs/contact/track/C/D1_STATISTICS.json',reason='User directive4 conditional acceptance; records the surviving hit, not a claimed zero-hit repair. HP excluded.'))
 differences=[q for q in d1['pairs']if q['R4']['signatureSha256']!=q['C']['signatureSha256']];assert{q['seed']for q in differences}=={419015,419026};cause=read(P/'evidence/d1-cause/RESULTS.json');assert cause['status']=='PASS'and all(q['signatureExactToOriginalD1']for q in cause['rows'])
 for row in differences:
  entries.append(entry('D1:'+str(row['seed'])+':signatureSha256',row['R4']['signatureSha256'],row['C']['signatureSha256'],'D1_CAUSE_REPORT.md and evidence/d1-cause/ANALYSIS.json: same actual local RF measurement, metre-nearest versus native P+R NIS assignment; first forks at350/100; downstream timing/physical/RNG differences preserved.30-seed primary outcomes identical.',kind='CURRENT_D1_EXACT',seed=row['seed'],reason='User directive6 conditional exact expectation update after5 passes; this is real behavior change, not metadata-only.'))
 q={'schema':'AEGIS_TRACK_C_CONDITIONAL_EXACT_APPROVALS_1','reviewedHtmlSha256':build['htmlSha256'],'reviewedMainSha256':build['mainSha256'],'referenceR4HtmlSha256':build['baselineHtmlSha256'],'statisticalResultSha256':sha(P/'STATISTICS.json'),'d1StatisticalResultSha256':sha(P/'D1_STATISTICS.json'),'validationSha256':sha(P/'VALIDATION.json'),'entries':entries,'retiredLegacyEmconUi':{'count':14,'reason':'User directive4 explicit retirement of removed #lockBtn precondition; current UI36/native27/UI213 replacements retained.','evidence':'EMCON_RETIREMENT_MATRIX.md'},'currentPaired42ExpectationChanges':0,'otherExpectationsChanged':0,'tolerancesChanged':0,'originalResultsPreserved':True,'gameCodeChangedByApproval':False};(P/'APPROVED_EXPECTATIONS.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');return q
def verify(q):
 build=gates();assert q['schema']=='AEGIS_TRACK_C_CONDITIONAL_EXACT_APPROVALS_1';assert q['reviewedHtmlSha256']==build['htmlSha256']and q['reviewedMainSha256']==build['mainSha256'];assert q['statisticalResultSha256']==sha(P/'STATISTICS.json')and q['d1StatisticalResultSha256']==sha(P/'D1_STATISTICS.json')and q['validationSha256']==sha(P/'VALIDATION.json');assert len(q['entries'])==5 and q['otherExpectationsChanged']==q['tolerancesChanged']==0
 checks={}
 for e in q['entries']:
  assert value_hash(e['oldExpected'])==e['oldValueSha256']and value_hash(e['newExpected'])==e['newValueSha256'];assert e['reason']and e['causePath']
  if e['kind']=='HISTORICAL_OBSERVER_EXACT':
   report=read(R/e['sourceReport']);assert sha(R/e['sourceReport'])==e['sourceReportSha256']and report['candidateSha256']==e['historicReviewedHtmlSha256'];row=next(r for r in report['cases']if r['ship']==e['ship']and r['scenario']=='raid');assert projection.pair_value(row['pair']['baseline'],'sameExistingObserverState')==e['oldExpected'];checks[e['id']]=projection.pair_value(row['pair']['candidate'],'sameExistingObserverState')==e['newExpected']
  elif e['kind']=='CURRENT_D1_EXACT':
   row=next(r for r in read(P/'D1_STATISTICS.json')['pairs']if r['seed']==e['seed']);assert row['R4']['signatureSha256']==e['oldExpected'];checks[e['id']]=row['C']['signatureSha256']==e['newExpected']
  else:
   row=next(r for r in read(P/'D1_STATISTICS.json')['pairs']if r['seed']==419025);checks[e['id']]=row['C']['leakers']==e['newExpected']and row['C']['signatureSha256']==e['currentReviewedSignature']
 assert all(checks.values());paired=read(P/'evidence/regression/paired-track-a/baseline-comparison.json');assert all(all(c['checks'].values())for c in paired['cases']);changed={e['seed']:e for e in q['entries']if e['kind']=='CURRENT_D1_EXACT'};d1checks=[r['C']['signatureSha256']==changed[r['seed']]['newExpected']if r['seed']in changed else r['C']['signatureSha256']==r['R4']['signatureSha256']for r in read(P/'D1_STATISTICS.json')['pairs']];assert len(d1checks)==30 and all(d1checks)
 result={'schema':'AEGIS_TRACK_C_APPROVED_EXACT_COMPARISONS_1','status':'PASS','checks':checks,'currentPairedPassed':42,'currentPairedExpected':42,'currentD1ExactPassedAfterOnlyTwoRecordedUpdates':sum(d1checks),'currentD1Expected':30,'historicalObserverApprovals':2,'inherited419025OutcomeApprovals':1,'currentD1ExactApprovals':2,'legacyUiRetiredNotCountedPassed':14,'originalAssertionsChanged':0,'tolerancesChanged':0,'actualNewGameRuns':0,'meaning':'Offline exact re-evaluation bound to the reviewed C product and frozen statistical decision; never a replacement for native executions.'};(P/'APPROVED_COMPARISONS.json').write_text(json.dumps(result,indent=2)+'\n');return result
def current(q,result):
 path=R/'docs/contact/track/CURRENT.json';previous=json.loads(subprocess.check_output(['git','show','d328c941:'+str(path.relative_to(R))],cwd=R));build=read(P/'BUILD.json');data={'schema':'AEGIS_TRACK_C_LIFECYCLE_CURRENT_1','status':'SCOPED_ACTIVE_CONDITIONALLY_USER_APPROVED','activePromotionApproved':True,'active':{'file':build['html'],'sha256':build['htmlSha256']},'baseline':{'file':'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html','sha256':build['baselineHtmlSha256']},'currentReport':'docs/contact/track/C/REPORT.md','statisticalResultSha256':sha(P/'STATISTICS.json'),'implementedActive':previous['implementedActive']+['C55_OWN','C55_NPC','SPQ_AIR'],'deferredShadowOnly':[],'readOnlyLifecycleAndEvidenceViews':True,'physicalIdMetricsAfterActionOnly':True,'universalZeroMisassociationClaimed':False,'expectationsUpdatedThisStage':5,'tolerancesUpdated':0,'legacyUiRetired':14,'postApprovalExactResults':result,'inheritedNotApproved':[],'remainingScopeNotes':['Nonzero physical reassignment/duplicate counts reported, not claimed eliminated.','Existing C55 CMS protection latch and manual-vs-AIR-IFF expiry policies unchanged.','ASM seeker egress audit classification only; seeker/HP/OODA/TRACK-D not modified.'],'mainMergeAuthorizedByConditionalResult':True,'actualMergeReceipt':'docs/contact/track/C/MERGE_READBACK.json (post-merge branch receipt)','mergeExecutedByThisOfflineReport':False,'previousStage':previous};path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--create',action='store_true');a=ap.parse_args();q=create()if a.create else read(P/'APPROVED_EXPECTATIONS.json');result=verify(q)
 if a.create:current(q,result)
 print(json.dumps({k:v for k,v in result.items()if k!='checks'}))
if __name__=='__main__':main()
