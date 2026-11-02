"""Aggregate current RC2 evidence without changing expectations or approvals."""
from pathlib import Path
import argparse,datetime,hashlib,json
from zoneinfo import ZoneInfo
P=Path(__file__).resolve().parent;R=P.parents[3]
FINAL='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
BASE='cfc74427e3d30efafec187c3fd99924f5063e74d8dbe3f8e36caebd68d149cda'
MODULE='b5fc75792e4bc7f05b7dc8f7e67f0195af3240b2f4a9aeb04b0b8bf85daf1810'
def read(rel):
 try:return json.loads((P/rel).read_text())
 except (FileNotFoundError,json.JSONDecodeError):return None
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--require-complete',action='store_true');a=ap.parse_args()
 build=read('BUILD.json')or{};scope=read('SCOPE.json')or{};unit=read('evidence/contract-unit.json')or{}
 runtime=read('evidence/candidate/RUNTIME_SUMMARY.json');reg=read('REGRESSION_RESULTS.json');baseline=read('evidence/baseline/summary.json')or{}
 checks={
 'baselineInputByteIdentical':digest(R/'Aegis_SIM_v48_WIP_FRIENDLY_CONTACT_A.html')==BASE,
 'finalHtmlFrozen':digest(R/'Aegis_SIM_v48_WIP_TRACK_A.html')==FINAL and build.get('htmlSha256')==FINAL,
 'sourceModuleFrozen':digest(P/'measurement-contract.js')==MODULE,
 'inverseRestoresEntireBaseline':build.get('inverseByteExact')is True,
 'scopeAll189ProtectedByteIdentical':scope.get('pass')is True and scope.get('candidateHtmlSha256')==FINAL and len(scope.get('protectedSymbols',[]))==189 and all(v['equal']for v in scope.get('protectedSymbols',[]))and not scope.get('forbiddenChanged'),
 'pureContract52':unit.get('status')=='PASS'and unit.get('assertionCount')==52 and unit.get('passed')==52 and unit.get('failed')==0 and unit.get('moduleSha256')==MODULE and unit.get('randomCalls')==0 and unit.get('wallClockCalls')==0,
 'freshBaseline30':baseline.get('d1',{}).get('count')==30 and baseline.get('d1',{}).get('archiveSignatureMatches')==30,
 'runtimeCurrentComplete':bool(runtime and runtime.get('candidateSha256')==FINAL and runtime.get('status')=='PASS'and runtime.get('allTasksComplete')is True),
 'runtimeNoProofFailure':bool(runtime and runtime.get('proofs')and all(v.get('status')=='PASS'for v in runtime['proofs'].values())),
 'regressionCurrentArtifact':bool(reg and reg.get('candidateSha256')==FINAL and not reg.get('rc1Superseded')),
 }
 rows={r['suite']:r for r in (reg or{}).get('rows',[])};native=(reg or{}).get('native13',{})
 checks['native13Current364']=native.get('suiteCount')==13 and native.get('assertionCount')==364 and native.get('passedAssertions')==364
 for name,count in [('paired-friendly',42),('ui213',213),('webgl8',29)]:
  q=rows.get(name,{ });checks[name+'Current']=q.get('status')=='PASS'and q.get('passedAssertions')==count and q.get('expectedAssertions',count)==count
 checks['noNewRegressionFailures']=bool(reg and not reg.get('newFailures'))
 checks['expectationsNotUpdated']=bool(reg and reg.get('expectedValuesUpdated')is False and reg.get('assertionChanges')is False and build.get('expectationChanges')is False)
 pending=[k for k,v in checks.items()if not v];has_failure=bool((reg or{}).get('newFailures'))or bool(runtime and runtime.get('status')=='FAIL')
 complete=not pending;status='PASS'if complete else'FAIL'if has_failure else'INCOMPLETE'
 result={
 'schema':'AEGIS_TRACK_A_VALIDATION_1','generatedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'),
 'branch':'track-a-contract-trace','baselineBranch':'friendly-contact-a','baselineHead':'4ba64ba0cace9124497a710d00df1b174984ffdc',
 'candidate':'Aegis_SIM_v48_WIP_TRACK_A.html','candidateSha256':FINAL,'baselineSha256':BASE,'moduleSha256':MODULE,
 'sourceCommits':{'baselineAudit':'7e7ba089a689a0c876e5c99881d4631127a2a491','initialImplementation':'34c29992b2160428bf823136a6b765a546a1e34e','finalMetadataFix':'bae3cb3da79ba8de74220c9b53e99d7b884becea'},
 'trackAStatus':status,'trackAStatusMeaning':'Current measurement-view and passive-trace implementation/behavior verification only; not baseline release approval.',
 'finalEvidenceComplete':complete,'checks':checks,'checkMeanings':{'noNewRegressionFailures':'No new failure observed among executed checks; completion requires all separate current-artifact checks.'},'pending':pending,'releaseApproved':False,'finalClosure':'INCOMPLETE',
 'coefficientChanges':False,'expectedValuesUpdated':False,'saveSchemaChanges':False,'newTacticalAiOrOoda':False,
 'stageImplementation':{'BaselineAudit':True,'TRACK-A':True,'TRACK-B':False,'TRACK-C':False,'TRACK-D':False},
 'unapprovedInheritedIssues':[
  {'id':'CIWS419025','status':'FAIL','scope':'INHERITED_FROM_FRIENDLY_CONTACT_A','fixed':False,'approved':False,'evidence':'evidence/baseline/trace419025-phalanx-rng-summary.json','note':'Two global RNG draws at PF hit observed; preserves hit outcome, does not repair or approve it.'},
  {'id':'CG_VS_FRIENDLY_PAIRED_OBSERVER_2','status':'KNOWN_DELTA','approved':False,'expectationsUpdated':False,'evidence':'evidence/baseline/paired-current-summary.json'},
  {'id':'LEGACY_EMCON_UI14','status':'INCOMPLETE','approved':False,'countedPass':False,'note':'Retired #lockBtn DOM; bounded RC1 attempt linked, current DOM census unchanged. Not a final RC2 PASS.'},
  {'id':'LEGACY_INFORMATION_BOUNDARY_DEBT','status':'KNOWN_DELTA','approved':False,'fixed':False,'evidence':'TRACK_AUDIT.md','note':'Whole baseline is not claimed truth-clean; new diagnostic path is separately audited.'}],
 'evidenceIndex':{'baseline':'evidence/baseline/summary.json','runtime':'evidence/candidate/RUNTIME_SUMMARY.json','regressions':'REGRESSION_RESULTS.json','contract':'evidence/contract-unit.json','scope':'SCOPE.json','historicalNotFinal':['evidence/rc1-candidate/','evidence/regression/RC1/']},
 'counts':{'originalCgVsFriendlyDomain':{'total':420,'passed':404,'knownDeltaUnapproved':2,'incomplete':14},'currentFriendlyVsTrackADomain':{'total':420,'nativePassed':native.get('passedAssertions',0),'pairedPassed':rows.get('paired-friendly',{}).get('passedAssertions',0),'legacyUiIncomplete':14},'separateNotAddedTo420':{'pureUnit':52,'componentFixture':47,'currentUi':213,'webglAssertions':29,'webglFlights':8,'ciwsCases':30,'naturalReproConditions':3},'fixedClockAssertionsAlreadyIncludedInNative13':24},
 'performanceApproval':False,'performanceInterpretation':'Measured host wall-time and statistical allocation estimates; no speedup or hardware/mobile-FPS claim; retain outliers and diagnostic-ON overhead.',
 'mergeOrPrOrReleaseOrTagCreated':False,
 }
 (P/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'trackAStatus':status,'finalEvidenceComplete':complete,'pending':pending,'releaseApproved':False},ensure_ascii=False))
 if a.require_complete and not complete:raise SystemExit(2)
if __name__=='__main__':main()
