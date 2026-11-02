"""Read evidence, never waive a check or alter an expectation."""
from pathlib import Path
import argparse,hashlib,json,time
P=Path(__file__).resolve().parent;R=P.parents[3]
def read(path):
 path=Path(path);return json.loads(path.read_text())if path.exists()else None
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--strict',action='store_true');a=ap.parse_args();build=read(P/'BUILD.json');scope=read(P/'SCOPE.json');reg=read(P/'REGRESSION_RESULTS.json');checks={};counts={};paths=[]
 def check(name,value):checks[name]=bool(value)
 check('currentProductHash',sha(R/build['html'])==build['htmlSha256']);check('inverseEntireMainByteExact',scope['pass']and scope['inverseByteExact']);check('rfEkfIffRoeCoefficientsSavePreserved',all(scope[k]for k in ['rfPhysicsFunctionsByteIdentical','ekfFunctionsAndCoefficientsByteIdentical','iffRoeIdentityFunctionsByteIdentical','weaponDamageAiPhysicsByteIdenticalExceptReviewedAliasBookkeeping'])and scope['coefficientChanges']==scope['saveSchemaChanges']==0)
 for label,where,expected in [('nativeActive','native-active',40),('nativeShadow','native-shadow',37),('currentEmconUi','current-emcon-ui',36),('largeC55Native','large-local',4)]:
  path=P/'evidence'/where/'RESULTS.json';q=read(path);check(label,q and q['pass']and len(q['checks'])==expected and all(q['checks'].values()));counts[label]={'passed':sum(q['checks'].values())if q else 0,'expected':expected};paths.append(path)
 check('allOriginal20RegressionsComplete',reg and reg['candidateSha256']==build['htmlSha256']and len(reg['rows'])==20 and not reg['pending']and all(q['status']=='PASS'for q in reg['rows']))
 if reg:
  native=[q for q in reg['rows']if q['task']not in ['paired-track-a','ui213','webgl8','d1','natural','auto-iff','idle']];counts['originalNative13']={'suites':len(native),'passed':sum(q['passedAssertions']for q in native),'expected':364};check('originalNative364',len(native)==13 and counts['originalNative13']['passed']==364)
  for task,n in [('paired-track-a',42),('ui213',213),('webgl8',29)]:
   q=next((q for q in reg['rows']if q['task']==task),None);check(task,q and q['status']=='PASS'and q['passedAssertions']==n);counts[task]={'passed':q.get('passedAssertions',0)if q else 0,'expected':n}
  check('originalAssertionsUnchanged',read(P/'evidence/regression/original-source-provenance.json')['status']=='PASS'and reg['originalAssertionsChanged']is False)
 for label,where in [('npcDdgCg','npc-local'),('npcCgClose','npc-local-close')]:
  path=P/'evidence'/where/'RESULTS.json';q=read(path);check(label,q and q['pass']and not q['errors']and all(all(r['checks'].values())for r in q['rows']));paths.append(path)
 for label,path,key,value in [('nativeIngress47',P/'evidence/extra-ingress/native-ingress.json','status','PASS'),('twoOwnersRngEnv',P/'evidence/extra-allocation/allocation-and-owners.json','status','PASS'),('nativeRuntimeMatchesR4',P/'RUNTIME_COMPARISON.json','status','PASS'),('diagnosticOffOnExact',P/'evidence/battles/CONTROLS.json','status','PASS'),('postBattleExportEntireValueExact',P/'evidence/battles/EXPORT_CONTROLS.json','status','PASS'),('d1CauseReplaysExact',P/'evidence/d1-cause/RESULTS.json','status','PASS'),('offlineAnalyzerArithmetic',P/'evidence/ANALYZER_SELFTEST.json','pass',True)]:
  q=read(path);check(label,q and q.get(key)==value);paths.append(path)
 allocation=read(P/'evidence/extra-allocation/allocation-and-owners.json');check('allRestoredNativeEnvHashesMatch',allocation and all(q['envMatch']and q['nativeFunctionsRestored']for q in allocation['records']))
 for suite in ['helicopter-flight','isar-clock','harpoon-clock']:
  receipt=read(P/'evidence/regression'/(suite+'-execution.json'));q=read(P/'evidence/regression'/receipt['resultPath'])if receipt else None;check(suite+'.currentHashAndOriginalChecks',q and q['htmlSha256']==build['htmlSha256']and all(q['checks'].values()));paths.append(P/'evidence/regression'/receipt['resultPath']if receipt else P/'MISSING')
 retirement=read(P/'EMCON_RETIREMENT.json');check('legacyEmcon14ExplicitlyRetired',retirement and retirement['oldAssertionCount']==14 and retirement['disposition']=='RETIRED_NOT_COUNTED_PASS'and retirement['restoredLegacyNodes']==0)
 d1=read(P/'D1_STATISTICS.json');check('d1ThirtyPairedPrimaryPass',d1 and d1['pairedCases']==30 and d1['allInitialAsmsNativeTerminal']and d1['primaryPass']);stats=read(P/'STATISTICS.json');check('all60FrozenPairsAndPrimaryPass',stats and stats['pairedCases']==60 and len(stats['pairs'])==60 and stats['allInitialAsmsResolved']and stats['primaryPass'])
 line=read(P/'LINEAGE_RESULTS.json');check('all120PhysicalLineageAuditsComplete',line and line['complete']and line['runs']==120)
 for metric in ['nonOwnMeasurementProtectedContamination','ownLaunchProtectionLost','physicalAsmIncorrectlyFlaggedOwnLaunch']:
  check('candidate.'+metric,line and line['complete']and line['totals']['C'].get(metric,0)==0)
 closure=read(P/'NOISE_ORIGIN_CLOSURE.json');proof=read(P/'evidence/noise-origin/RESULTS.json');paths.extend([P/'NOISE_ORIGIN_CLOSURE.json',P/'evidence/noise-origin/RESULTS.json'])
 check('allMeasuredRfOriginsClosedWithoutInventedPhysicalId',line and line['complete']and closure and closure['status']=='PASS'and closure['physicalUidInvented']is False and closure['sourceProofSha256']==sha(P/closure['sourceProof'])and line['noReflectorOriginClosureSha256']==sha(P/'NOISE_ORIGIN_CLOSURE.json')and proof['status']=='PASS'and all(all(r['checks'].values())for r in proof['rows'])and all(line['totals'][prod].get('UNLINKED',0)==line['totals'][prod].get('AMBIGUOUS_EXACT_FINGERPRINT',0)==0 and line['totals'][prod].get('receiverProcessingNoiseMeasurementsNoReflector',0)==closure['productCounts'][prod]for prod in ['R4','C']))
 check('candidateOwnAndNonOwnLocalCovered',line and line['totals']['C'].get('ownLaunchLocalMeasurements',0)>0 and line['totals']['C'].get('nonOwnLocalMeasurements',0)>0 and line['totals']['C'].get('localProtectionFieldMissing',0)==0)
 budget=read(P/'evidence/BUDGET.json');check('withinFourHourWallCap',time.monotonic()<=budget['deadlineMonotonic'])
 paths +=[P/f for f in ['BUILD.json','SCOPE.json','REGRESSION_RESULTS.json','SOURCE_AUDIT.json','PLAN.json','PLAN_C55_ADDENDUM.json','D1_STATISTICS.json','STATISTICS.json','LINEAGE_RESULTS.json','EMCON_RETIREMENT.json']]
 result={'schema':'AEGIS_TRACK_C_VALIDATION_1','status':'PASS'if all(checks.values())else'INCOMPLETE_OR_FAILED','candidateSha256':build['htmlSha256'],'baselineSha256':build['baselineHtmlSha256'],'checks':checks,'counts':counts,'legacyDomainCount':{'nativeAndPaired':406,'retiredLegacyUi':14,'neverClaimed420Of420':True},'failedOrPending':[k for k,v in checks.items()if not v],'evidenceInputs':{str(p.relative_to(P)):sha(p)for p in paths if p.exists()},'elapsedWallS':time.monotonic()-budget['startMonotonic'],'remainingWallS':budget['deadlineMonotonic']-time.monotonic(),'noExpectationOrToleranceChangedByValidation':True,'approvalAndMergePerformedByValidation':False};(P/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'failedOrPending':result['failedOrPending'],'counts':counts}));return 0 if result['status']=='PASS'or not a.strict else 1
if __name__=='__main__':raise SystemExit(main())
