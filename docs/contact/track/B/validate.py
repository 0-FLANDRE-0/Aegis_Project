"""Root evidence aggregation. Keep original strict failures and approvals separate."""
from pathlib import Path
import argparse,datetime,hashlib,json
from zoneinfo import ZoneInfo

P=Path(__file__).resolve().parent;R=P.parents[3]
ACTIVE='0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6'
SHADOW='e9af30d8d71209f9eb45d72de58ca509efd261d7126d89ab626e2873d182995d'
BASE='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'

def read(name):
    try:return json.loads((P/name).read_text())
    except (FileNotFoundError,json.JSONDecodeError):return None

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--require-complete',action='store_true');args=ap.parse_args()
    build=read('BUILD.json')or{};shadow=read('BUILD_SHADOW.json')or{}
    scopes=[read(name)or{}for name in ['SCOPE.json','SCOPE_SHADOW.json']]
    unit=read('evidence/solver-unit.json')or{};native=read('evidence/native-integration/SUMMARY.json')or{}
    cohort=read('evidence/cohort-supplement/SUMMARY.json')or{};broad=read('REGRESSION_RESULTS.json')or{}
    runtime=read('evidence/runtime/RUNTIME_SUMMARY.json')or{}
    cause=read('evidence/paired-cause/CAUSE_32_FACTS.json')or{}
    extension=read('evidence/paired-cause-120/OUTCOME_REVIEW.json')or{}
    seed=read('evidence/seed419012-cause/EXECUTION.json')or{}
    seed_analysis=read('evidence/seed419012-cause/ANALYSIS_RECEIPT.json')or{}
    cost=read('evidence/cost-final/SUMMARY.json')or{}
    rows={r['suite']:r for r in broad.get('rows',[])}
    checks={
        'frozenTrackAInput':digest(R/'Aegis_SIM_v48_WIP_TRACK_A.html')==BASE,
        'frozenActiveHtml':digest(R/'Aegis_SIM_v48_WIP_TRACK_B.html')==ACTIVE==build.get('htmlSha256'),
        'frozenShadowHtml':digest(R/'Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html')==SHADOW==shadow.get('htmlSha256'),
        'reversibleCompleteSource':build.get('inverseByteExact')is True and shadow.get('inverseByteExact')is True,
        'bothScope189Plus161ByteEqual':all(s.get('pass')is True and len(s.get('protectedSymbols',[]))==189 and len(s.get('nestedProtectedSymbols',[]))==161 and all(x['equal']for x in s['protectedSymbols']+s['nestedProtectedSymbols'])and not s.get('forbiddenChanged')and not s.get('forbiddenAdded')for s in scopes),
        'sourceModulesMatchBuild':bool(build.get('modules'))and all(digest(P/m['path'])==m['sha256']for m in build['modules']),
        'pureSolver47ActualNativeHungarian':unit.get('status')=='PASS'and unit.get('count')==unit.get('passed')==47 and unit.get('failed')==0 and unit.get('moduleSha256')==digest(P/'association.js'),
        'native90CurrentProduct':native.get('candidateSha256')==ACTIVE and native.get('shadowSha256')==SHADOW and native.get('status')=='PASS'and native.get('activeChecks',{}).get('passed')==90,
        'nativeTraceOffOnAndShadowExact':native.get('shadowOriginalNativeRecordsExact')is True and len(native.get('traceOnOff',[]))==2 and all(x.get('perFixtureGameAndPrivateRngSha256Exact')is True and x.get('fixtureCount')==23 for x in native.get('traceOnOff',[])),
        'bothActualCoreDefectsReproducedAndFixed':cohort.get('status')=='PASS'and cohort.get('candidateSha256')==ACTIVE and cohort.get('activeChecks',{}).get('passed')==14 and len(cohort.get('baselineDefectsActuallyReproduced',{}))==2 and all(cohort.get('baselineDefectsActuallyReproduced',{}).values()),
        'originalNative364':broad.get('candidateSha256')==ACTIVE and broad.get('native13',{}).get('passedAssertions')==364,
        'allOriginalSuitesExecutedWithoutWaiver':broad.get('allRequestedFreshSuitesExecuted')is True and not broad.get('pendingFreshSuites')and broad.get('assertionChanges')is False and broad.get('expectedValuesUpdated')is False,
        'originalPairedStrictFailuresPreserved':rows.get('paired-track-a',{}).get('status')=='FAIL'and rows.get('paired-track-a',{}).get('passedAssertions')==38 and len(rows.get('paired-track-a',{}).get('failedAssertions',[]))==4,
        'originalUi213AndWebgl29':all(rows.get(name,{}).get('status')=='PASS'and rows[name].get('passedAssertions')==count for name,count in [('ui213',213),('webgl8',29)]),
        'allRuntime24ExecutedAndStrictDeltaRetained':runtime.get('candidateSha256')==ACTIVE and runtime.get('shadowSha256')==SHADOW and runtime.get('allTasksComplete')is True and runtime.get('executedJobs')==24 and runtime.get('strictPassJobs')==23 and len(runtime.get('strictFailuresRetained',[]))==1 and runtime.get('status')=='FAIL',
        'd1All30SelectedOutcomesSameNotAutoApproved':runtime.get('activeD1AfterAction',{}).get('selectedGameplayEqualCount')==30 and runtime.get('activeD1AfterAction',{}).get('differentSignatureSeeds')==[419012]and not runtime.get('activeD1AfterAction',{}).get('outcomeWorseningIndicators'),
        'pairedCauseControlsAndNoApproval':len(cause.get('runs',[]))==2 and all(x.get('shadowNativeFieldsExact')is True and x.get('diagnosticOnOffNativeFieldsExact')is True for x in cause.get('runs',[]))and cause.get('strictPairedFailuresRemainUnapproved')is True,
        'extendedOriginalRaidsExecutedNoBattleClaim':len(extension.get('rows',[]))==2 and extension.get('all32CheckpointsExact')is True and extension.get('battleResolutionDemonstrated')is False,
        'seed419012OriginalSignatureAndCleanEnv':seed.get('status')=='PASSIVE_TRACE_EQUIVALENCE_PASS'and len(seed.get('products',[]))==2 and all(x.get('status')=='PASS'and all(x.get('checks',{}).values())for x in seed.get('products',[]))and seed_analysis.get('causalAnalysisPending')is False and seed_analysis.get('automaticApproval')is False,
        'quiescentFinalCostEvidence':cost.get('allTasksComplete')is True and cost.get('candidateSha256')==ACTIVE and cost.get('status')=='PASS',
    }
    pending=[name for name,value in checks.items()if not value]
    data={
        'schema':'AEGIS_TRACK_B_VALIDATION_1','generatedAtKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds'),
        'branch':'track-b-association','sourceCommit':'da73163a808aa6e480f1c26f42bdc1ae13ddb985',
        'baselineHead':'ee960dbb7c796e3c91cbe4b6d3d5f59948a0e561','baselineSha256':BASE,
        'candidateSha256':ACTIVE,'shadowSha256':SHADOW,
        'trackBStatus':'INCOMPLETE','implementedContractStatus':'PASS'if checks['native90CurrentProduct']and checks['bothActualCoreDefectsReproducedAndFixed']else'INCOMPLETE',
        'statusMeaning':'Implementation/evidence delivered for the declared live subset. Original strict changes remain unapproved; this is not full TRACK-B/combined-project closure.',
        'finalEvidenceComplete':not pending,'pendingEvidence':pending,'checks':checks,
        'releaseApproved':False,'finalClosure':'INCOMPLETE','expectedValuesUpdated':False,
        'coefficientChanges':False,'saveSchemaChanges':False,'newTacticalAiOrOoda':False,'stageCOrDImplemented':False,
        'domain':{'total':420,'pass':402,'fail':4,'incomplete':14,'expectedValuesUpdated':False},
        'separateNotAddedTo420':{'unit':47,'nativeOnAssertions':90,'nativeFixtureGroups':23,'coreDefectSupplement':14,'ui':213,'webglAssertions':29,'webglFlights':8,'activeD1Cases':30,'activeD1ExactSignatures':29},
        'newStrictDifferences':[
            {'id':'PAIRED_RAID_4','status':'FAIL','approved':False,'cause':'Actual near-equal native NIS matching hold changes measurement/revisit and SAM launch timing; temporary 708kg loading difference then native hull-response difference. Endpoint32s equality is not a completed battle.','evidence':'PAIRED_CAUSE_RESULTS.md'},
            {'id':'D1_419012_SIGNATURE','status':'FAIL','approved':False,'cause':'Same AIR4D observation has native candidate NIS delta0.337665<=1; HOLD changes canonical estimate and cached cue ranking, while observed local C55 control/physical outcomes are unchanged.','evidence':'SEED419012_CAUSE_REPORT.md'}],
        'unapprovedInheritedIssues':[
            {'id':'CIWS419025','status':'FAIL','fixed':False,'approved':False},
            {'id':'CG_TO_FRIENDLY_OBSERVER_2','status':'KNOWN_DELTA','approved':False},
            {'id':'LEGACY_EMCON_UI14','status':'INCOMPLETE','countedPass':False,'approved':False}],
        'remainingLimits':[
            'Focused SPY, SPQ AIR and C55 live/interleaved association remain the existing behavior; C55/SPQ evidence is explicitly shadow-only.',
            'Surface position-only assignment can reject later Doppler correction; no new EKF or full fallback re-solve is claimed.',
            'Connected component bound12 can hold a dense unresolved graph. Sparse257/stress cases are not a general combat guarantee.',
            'Delayed Hawklink keeps existing position/age-squared covariance semantics; no new past-epoch motion alignment or contact-lineage schema.',
            'The120s extension has no intercept/hit resolution, so it does not establish completed multi-ASM combat equivalence.',
            'Legacy truth-boundary debts from TRACK-A are not claimed fixed across the whole project.'],
        'performanceApproved':False,'mergePrReleaseTagCreated':False,
        'evidence':{'native':'evidence/native-integration/SUMMARY.json','cohort':'evidence/cohort-supplement/SUMMARY.json','broad':'REGRESSION_RESULTS.json','runtime':'evidence/runtime/RUNTIME_SUMMARY.json','cost':'evidence/cost-final/SUMMARY.json','scope':'SCOPE.json'},
    }
    (P/'VALIDATION.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'trackBStatus':data['trackBStatus'],'implementedContractStatus':data['implementedContractStatus'],'finalEvidenceComplete':not pending,'pendingEvidence':pending,'releaseApproved':False},ensure_ascii=False))
    if args.require_complete and pending:raise SystemExit(2)

if __name__=='__main__':main()
