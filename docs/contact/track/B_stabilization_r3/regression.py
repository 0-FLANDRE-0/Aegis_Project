"""R3 Stable-B regression lane over unchanged original fixtures and assertions.

Default/--prepare never start a browser. --run requires the root-frozen product
SHA. TRACK-A and delivered B evidence are read-only historical references.
One fresh R3 run is compared with A, delivered B and historical R1; R2 guarded natural evidence remains separate.
R1 results are comparison inputs only, never fresh R3 passes.
"""
from pathlib import Path
import argparse,base64,concurrent.futures,gzip,hashlib,importlib.util,itertools,json,os,re,runpy,shutil,subprocess,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3];B=P.parent/'B';A=P.parent/'A';E=P/'evidence/regression'
R1=P.parent/'B_stabilization';R1_E=R1/'evidence/regression';R2=P.parent/'B_stabilization_r2'
BASE_A=R/'Aegis_SIM_v48_WIP_TRACK_A.html';BASE_B=R/'Aegis_SIM_v48_WIP_TRACK_B.html'
SHA_A='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
SHA_B='0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6'
SHA_R1='87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18'
SHA_R2='c8a9266fe12d6543cf09a1e851af5a0c717e73117945291c5bb5babc9670d584'
R1_REGRESSION_PINS_SHA='bd8532098490e60afc213289250561d8f2fea60dcef3884ae8dd2c8686025267'
R2_HISTORICAL_PINS_SHA='e18249c21b3f67a34b63e38407ea2f621e793ad9e93109584991441751a7f108'
SOURCE_HEAD='1d92554026d15f417d987aec519007ea9657a6b6'
sha=lambda data:hashlib.sha256(data).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
original=module('stabilization_unchanged_b_regressions',B/'regression_runner.py')
runtime=module('stabilization_unchanged_a_fixture_support',A/'verify_runtime.py')
state_diff=module('stabilization_unchanged_b_state_diff',B/'verify_runtime.py')
semantic=module('stabilization_r2_unchanged_d1_summary',B/'analyze_d1.py')
NAMES=['d1','paired-track-a',*original.NATIVE,'ui213','webgl8']
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')
def packed(path,value):
 data=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode();path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(gzip.compress(data,6,mtime=0));return {'path':str(path.relative_to(P)),'rawSha256':sha(data),'gzipSha256':sha(path.read_bytes())}
def lines(path):
 if not path.exists():path=Path(str(path)+'.gz')
 with(gzip.open(path,'rt')if path.suffix=='.gz'else path.open())as stream:
  for row in stream:
   if row.strip():yield json.loads(row)
def references():
 a=original.reference_evidence();manifest={}
 for line in(B/'CHECKSUMS.sha256').read_text().splitlines():
  digest,path=line.split(None,1);manifest[path.strip()]=digest
 selected=['BUILD.json','VALIDATION.json','REGRESSION_RESULTS.json','PAIRED_DELTA_REVIEW.json','PAIRED_CAUSE_RESULTS.md','SEED419012_CAUSE_REPORT.md','evidence/runtime/RUNTIME_SUMMARY.json','evidence/runtime/active/d1-comparison.json','evidence/runtime/active/friendly/ciws-d1.jsonl.gz','evidence/regression/paired-track-a/baseline-comparison.json','evidence/native-integration/SUMMARY.json','evidence/cost-final/SUMMARY.json']
 rows=[]
 for name in selected:
  path=B/name;actual=sha(path.read_bytes())if path.exists()else None;rows.append({'path':str(path.relative_to(R)),'sha256':actual,'manifestSha256':manifest.get(name),'match':actual is not None and actual==manifest.get(name)})
 pin_path=P/'R1_REGRESSION_PINS.json';pin_raw=pin_path.read_bytes();pins=json.loads(pin_raw)
 r1_rows=[{'path':name,'sha256':sha((R/name).read_bytes()),'expectedSha256':digest,'match':sha((R/name).read_bytes())==digest}for name,digest in pins['files'].items()]
 r1_report=json.loads((R1/'REGRESSION_RESULTS.json').read_text())
 r2_pin_raw=(P/'R2_HISTORICAL_PINS.json').read_bytes();r2_pins=json.loads(r2_pin_raw)
 r2_rows=[{'path':name,'sha256':sha((R/name).read_bytes()),'expectedSha256':digest,'match':sha((R/name).read_bytes())==digest}for name,digest in r2_pins['files'].items()]
 checks={'trackAReferenceValid':a['status']=='PASS','trackAHtmlPinned':sha(BASE_A.read_bytes())==SHA_A,'deliveredBHtmlPinned':sha(BASE_B.read_bytes())==SHA_B,'allSelectedBEvidenceChecksumsMatch':all(r['match']for r in rows),'r1RegressionPinManifestExact':sha(pin_raw)==R1_REGRESSION_PINS_SHA,'r1HtmlPinned':sha((R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_A.html').read_bytes())==SHA_R1,'r1RawEvidenceAllPinned':all(r['match']for r in r1_rows),'r1CompletedSeventeenJobsSameSha':r1_report['candidateSha256']==SHA_R1 and len(r1_report['rows'])==17 and not r1_report['pendingSuites']}
 checks.update(r2HistoricalPinManifestExact=sha(r2_pin_raw)==R2_HISTORICAL_PINS_SHA,r2HtmlPinned=sha((R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_B.html').read_bytes())==SHA_R2,r2SelectedHistoricalEvidencePinned=all(r['match']for r in r2_rows))
 return {'schema':'AEGIS_TRACK_B_STABLE_R3_REGRESSION_REFERENCE_1','sourceHead':SOURCE_HEAD,'status':'PASS'if all(checks.values())else'INCOMPLETE','checks':checks,'trackA':a,'deliveredB':rows,'r1HistoricalRegression':{'candidateSha256':SHA_R1,'files':r1_rows,'historicalOnly':True,'freshR3Execution':False},'r2HistoricalNaturalAndGraphEvidence':{'candidateSha256':SHA_R2,'files':r2_rows,'originalSeventeenJobs':'NOT_EXECUTED_R2','historicalOnly':True,'freshR3Execution':False},'originalTestSources':original.test_source_provenance(),'inheritedStrictResults':{'trackBOriginalDomain':{'pass':402,'fail':4,'incomplete':14},'trackBD1Exact':29,'trackBD1Cases':30,'unapproved419025':True,'unapprovedOriginalPairedObserverTwo':True},'reuseMeaning':'Hash-matched A/B/R1 comparison references only. Every R3 result requires fresh current-SHA execution. R2 never executed original17 jobs. No historical failure is approved.','releaseApproved':False}
def configure(candidate,pinned,out):
 global E
 E=out;original.P=P;original.E=E;original.REFERENCE=BASE_A;original.REFERENCE_SHA=SHA_A;original.configure(candidate,pinned)

def product_source_proof(candidate,pinned):
 """Inspect the delivered packed JS bytes; no game/browser execution."""
 html=candidate.read_bytes();build=json.loads((P/'BUILD.json').read_text());scope=json.loads((P/'SCOPE.json').read_text());assert sha(html)==pinned==build['htmlSha256']==scope['candidateHtmlSha256']
 match=re.search(rb'data-c55-index="13">([^<]+)</script>',html);assert match,'Actual packed MAIN index13 missing'
 main=gzip.decompress(base64.b64decode(match[1]));module=(P/'association.js').read_bytes();declared=next(m for m in build['modules']if m['path']=='association.js')
 checks={'actualPackedMainMatchesFrozenBuild':sha(main)==build['mainSha256'],'activeModuleSourceMatchesRenderedBuild':sha(module)==declared['sourceSha256']==declared['renderedSha256'],'actualPackedSourceContainsExactlyOneCurrentModule':main.count(module)==1,'legacyBStillActive':main.count(b"const TRACK_B_IMPLEMENTATION_MODE='ACTIVE';")==1,'stabilizationActive':main.count(b"const TRACK_B_STABILIZATION_MODE='ACTIVE';")==1,'packedHtmlInverseByteExactBuildProof':build.get('packedHtmlInverseByteExact')is True,'scopePassCurrentProduct':scope.get('pass')is True}
 assert all(checks.values()),checks
 path=E/'candidate-packed-association.js.gz';path.write_bytes(gzip.compress(module,6,mtime=0))
 value={'schema':'AEGIS_TRACK_B_STABLE_R3_PACKED_PRODUCT_PROOF_1','candidate':str(candidate.relative_to(R)),'candidateSha256':pinned,'packedScriptIndex':13,'actualMainSha256':sha(main),'modulePath':'docs/contact/track/B_stabilization_r3/association.js','actualEmbeddedModuleSha256':sha(module),'embeddedModuleCopy':str(path.relative_to(P)),'buildSha256':sha((P/'BUILD.json').read_bytes()),'scopeSha256':sha((P/'SCOPE.json').read_bytes()),'checks':checks,'status':'PASS','scopeMeaning':'Packed production bytes contain the modified native association module; no diagnostic replacement or surrogate model. Dynamic original fixtures execute this HTML separately.','gameCodeExecutedByThisProof':False,'releaseApproved':False};save(E/'PRODUCT_SOURCE_PROOF.json',value);return value

def d1_worker(candidate):
 # The exact original script is executed, only HTML/evidence paths redirected.
 runtime.CANDIDATE=candidate;runtime.E=E/'d1';runtime.redirect_existing();F=R/'docs/contact/friendly/A';sys.path.insert(0,str(F));script=F/'ciws.py';sys.argv=[str(script),'d1'];runpy.run_path(str(script),run_name='__main__')

def compare_d1(pinned):
 candidate=E/'d1/friendly/ciws-d1.jsonl';summaries={}
 for label,reference in [('track-a',A/'evidence/candidate/friendly/ciws-d1.jsonl.gz'),('delivered-b',B/'evidence/runtime/active/friendly/ciws-d1.jsonl.gz'),('r1-stable-a',R1_E/'d1/friendly/ciws-d1.jsonl')]:
  rows=[]
  for before,after in itertools.zip_longest(lines(reference),lines(candidate)):
   assert before is not None and after is not None,'D1 count differs';assert before['case']==after['case'],'Original fixed seeds differ'
   old,new=semantic.gameplay(before),semantic.gameplay(after);worse=[]
   if new['hpAfter']<old['hpAfter']:worse.append('LOWER_HP')
   if new['shipHits']>old['shipHits']:worse.append('MORE_SHIP_IMPACTS')
   if old['shipAlive']and not new['shipAlive']:worse.append('NEW_SHIP_LOSS')
   seed=after['case']['seed'];delta=state_diff.differences(before,after)
   detail=packed(E/'d1'/('compare-'+label)/(str(seed)+'-all-leaf-differences.json.gz'),delta)
   rows.append({'seed':seed,'sameOriginalSignature':before['signatureSha256']==after['signatureSha256'],'referenceSignature':before['signatureSha256'],'candidateSignature':after['signatureSha256'],'selectedGameplaySummaryEqual':old==new,'selectedGameplaySummaryNotAssertionReplacement':True,'referenceGameplay':old,'candidateGameplay':new,'outcomeWorseningIndicators':worse,'allLeafDifferences':detail,'leafDifferences':len(delta),'approved':False})
  assert len(rows)==30
  summaries[label]={'status':'PASS'if all(r['sameOriginalSignature']for r in rows)else'FAIL','sameOriginalSignatures':sum(r['sameOriginalSignature']for r in rows),'cases':30,'differentSeeds':[r['seed']for r in rows if not r['sameOriginalSignature']],'outcomeWorseningIndicators':[{'seed':r['seed'],'indicators':r['outcomeWorseningIndicators']}for r in rows if r['outcomeWorseningIndicators']],'rows':rows,'referencePath':str(reference.relative_to(R))}
 execution=json.loads((E/'d1/friendly/ciws-d1-execution.json').read_text())
 value={'schema':'AEGIS_TRACK_B_STABLE_R3_D1_COMPARISON_1','candidateSha256':pinned,'status':summaries['track-a']['status']if not execution['errors']else'FAIL','checks':{'originalThirtyCases':all(v['cases']==30 for v in summaries.values()),'browserErrorsZero':not execution['errors']},'originalExecution':execution,'comparisonPolicy':'Original TRACK-A strict signatures remain unchanged. Delivered-B and historical R1 differences are additional raw comparisons, not new expectations or approval.','references':summaries,'seed419025':next(r for r in summaries['track-a']['rows']if r['seed']==419025),'originalScriptOrFixtureChanged':False,'expectedValuesUpdated':False,'releaseApproved':False};save(E/'d1/COMPARISON.json',value)
 return {'status':value['status'],'expectedAssertions':30,'executedAssertions':30,'passedAssertions':summaries['track-a']['sameOriginalSignatures'],'failedAssertions':['seed'+str(seed)for seed in summaries['track-a']['differentSeeds']],'resultPath':'d1/COMPARISON.json','comparisonNotAddedToDomain420':True}

def paired_history(pinned):
 new=json.loads((E/'paired-track-a/baseline-comparison.json').read_text());old_path=B/'evidence/regression/paired-track-a/baseline-comparison.json';old=json.loads(old_path.read_text());assert old['candidateSha256']==SHA_B and old['baselineSha256']==SHA_A
 r1_path=R1_E/'paired-track-a/baseline-comparison.json';r1=json.loads(r1_path.read_text());assert r1['candidateSha256']==SHA_R1 and r1['baselineSha256']==SHA_A
 assert new['candidateSha256']==pinned and new['baselineSha256']==SHA_A
 rows=[]
 for current in new['cases']:
  prior=next(r for r in old['cases']if r['ship']==current['ship']and r['scenario']==current['scenario'])
  r1_prior=next(r for r in r1['cases']if r['ship']==current['ship']and r['scenario']==current['scenario'])
  # Every raw leaf is retained. This does not replace either original check.
  delta=state_diff.differences(prior['pair']['candidate'],current['pair']['candidate'])
  r1_delta=state_diff.differences(r1_prior['pair']['candidate'],current['pair']['candidate'])
  rows.append({'ship':current['ship'],'scenario':current['scenario'],'trackAToDeliveredBOriginalChecks':prior['checks'],'trackAToR1OriginalChecks':r1_prior['checks'],'trackAToR3OriginalChecks':current['checks'],'deliveredBToR3AllLeafDifferences':delta,'deliveredBDifferentLeaves':len(delta),'r1ToR3AllLeafDifferences':r1_delta,'r1DifferentLeaves':len(r1_delta),'automaticApproval':False})
 return packed(E/'paired-four-version.json.gz',{'schema':'AEGIS_TRACK_B_STABLE_R3_PAIRED_FOUR_VERSION_1','candidateSha256':pinned,'trackASha256':SHA_A,'deliveredBSha256':SHA_B,'r1Sha256':SHA_R1,'deliveredBSourceSha256':sha(old_path.read_bytes()),'r1SourceSha256':sha(r1_path.read_bytes()),'r2OriginalPairedComparison':'NOT_EXECUTED_R2','cases':rows,'expectedValuesUpdated':False,'releaseApproved':False})

def r1_raw_comparison(name,row,pinned):
 """Retain every R1/current raw result leaf, including host metadata differences.

 This additional comparison never changes original assertions or stage status.
 D1/paired have richer source-specific full-leaf comparisons above.
 """
 prior=json.loads((R1/'REGRESSION_RESULTS.json').read_text())
 old_row=next(r for r in prior['rows']if r['suite']==name)
 meta={k:row.get(k)for k in ['status','executedAssertions','passedAssertions','failedAssertions']}
 old_meta={k:old_row.get(k)for k in meta}
 value={'schema':'AEGIS_TRACK_B_STABLE_R3_R1_RAW_RESULT_DELTA_1','suite':name,'referenceCandidateSha256':SHA_R1,'candidateSha256':pinned,'originalR1Result':old_meta,'freshR3Result':meta,'originalResultFieldsEqual':old_meta==meta,'comparisonIsNotAnAssertionOrApproval':True,'expectedValuesUpdated':False,'releaseApproved':False}
 if name not in ['d1','paired-track-a']and row.get('resultPath')and old_row.get('resultPath'):
  old_path=R1_E/old_row['resultPath'];new_path=E/row['resultPath']
  if old_path.exists()and new_path.exists():
   delta=state_diff.differences(json.loads(old_path.read_text()),json.loads(new_path.read_text()))
   value.update(referenceResultPath=str(old_path.relative_to(R)),referenceResultSha256=sha(old_path.read_bytes()),freshResultPath=str(new_path.relative_to(P)),freshResultSha256=sha(new_path.read_bytes()),allLeafDifferences=delta,differentLeaves=len(delta),unfilteredHostMetadataRetained=True)
  else:value.update(rawComparisonStatus='INCOMPLETE',missingPaths=[str(p)for p in [old_path,new_path]if not p.exists()])
 elif name not in ['d1','paired-track-a']:
  value.update(rawComparisonStatus='INCOMPLETE',reason='Original worker did not return a raw result path; no comparison fabricated.')
 return packed(E/'r1-comparison'/(name+'-raw-delta.json.gz'),value)

def execute(name,candidate,pinned):
 at=time.perf_counter();assert sha(candidate.read_bytes())==pinned;controller_sha=sha(Path(__file__).read_bytes());sources=original.test_source_provenance();assert sources['status']=='PASS'
 if name=='d1':
  command=[sys.executable,'-u',str(Path(__file__).resolve()),'--worker-d1','--candidate',str(candidate),'--sha',pinned,'--out',str(E)]
  with original.heavy_browser_slot()as lease:
   with(E/'d1.log').open('w')as log:
    try:result=subprocess.run(command,cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT,timeout=1800);code=result.returncode
    except subprocess.TimeoutExpired:code=124
  outcome=compare_d1(pinned)if code==0 else{'status':'INCOMPLETE'if code==124 else'FAIL','expectedAssertions':30,'executedAssertions':0,'passedAssertions':0,'failedAssertions':['Original D1 worker incomplete; preserve raw logs']}
  row={'suite':name,'command':command,'exitCode':code,'lease':lease,'wallS':time.perf_counter()-at,**outcome};save(E/'d1-execution.json',row)
 else:
  row=original.execute(name)
  if name=='paired-track-a'and(E/'paired-track-a/baseline-comparison.json').exists():row['fourVersionEvidence']=paired_history(pinned)
 row['r1HistoricalRawComparison']=r1_raw_comparison(name,row,pinned)
 assert sha(candidate.read_bytes())==pinned,'Candidate changed during original tests'
 assert sha(Path(__file__).read_bytes())==controller_sha,'Controller changed during original worker'
 assert original.test_source_provenance()['files']==sources['files'],'Original fixture/helper changed during worker'
 row.update(candidateSha256=pinned,controllerSha256=controller_sha,originalSourceProvenance=sources,expectedValuesUpdated=False,deltaApproved=False);return row

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_C.html');parser.add_argument('--sha');parser.add_argument('--shadow',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_C_SHADOW.html');parser.add_argument('--shadow-sha');parser.add_argument('--only',nargs='+',choices=NAMES);parser.add_argument('--out',type=Path,default=E);parser.add_argument('--prepare',action='store_true');parser.add_argument('--run',action='store_true');parser.add_argument('--resume',action='store_true');parser.add_argument('--retry-closed',action='store_true',help='Explicitly archive/re-run a selected closed result; default resume preserves FAIL as FAIL without duplicate firing');parser.add_argument('--parallel',type=int,choices=[1,2],default=1);parser.add_argument('--worker-d1',action='store_true');args=parser.parse_args();candidate=args.candidate.resolve();out=args.out.resolve();assert out.is_relative_to(P),'Only new stabilization output paths are allowed';configure(candidate,args.sha,out)
 if args.worker_d1:
  assert args.sha and sha(candidate.read_bytes())==args.sha;E.mkdir(parents=True,exist_ok=True);d1_worker(candidate);return
 reference=references();names=args.only or NAMES
 plan={'schema':'AEGIS_TRACK_B_STABLE_R3_REGRESSION_PLAN_1','readOnlyOrPrepare':not args.run,'browserProcessesStarted':0,'reference':reference,'candidate':str(candidate),'candidateSha256':args.sha,'shadow':str(args.shadow.resolve()),'shadowSha256':args.shadow_sha,'shadowMeaning':'Delivered B ACTIVE remains live while R3 stabilization proposal is shadowed; NOT R1 ACTIVE or old TRACK_B_SHADOW.','jobs':[{'suite':name,'command':original.job(name)if name!='d1'else'Exact original friendly/A ciws.py d1; one fresh R3 run compared with A, delivered B and historical R1'}for name in names],'thisLaneConcurrency':args.parallel,'sharedBrowserLimit':2,'releaseApproved':False}
 if not args.run:
  if args.prepare:save(E/'REFERENCE_AUDIT.json',reference);save(E/'PLANNED_JOBS.json',plan)
  print(json.dumps(plan,ensure_ascii=False,indent=2));return
 assert args.sha and sha(candidate.read_bytes())==args.sha,'Root-frozen candidate SHA required';assert reference['status']=='PASS'and reference['originalTestSources']['status']=='PASS','Reference/source provenance mismatch'
 if args.shadow_sha:assert sha(args.shadow.read_bytes())==args.shadow_sha
 E.mkdir(parents=True,exist_ok=True);save(E/'REFERENCE_AUDIT.json',reference);source_proof=product_source_proof(candidate,args.sha);rows=[];phase_start=time.perf_counter();prior_wall=0;destination=P/'REGRESSION_RESULTS.json'
 if args.resume and destination.exists():
  prior=json.loads(destination.read_text());assert prior['candidateSha256']==args.sha and prior.get('shadowSha256')==args.shadow_sha;rows=prior['rows'];prior_wall=prior.get('wallS',0)
 pending=[]
 for name in names:
  prior=next((r for r in rows if r['suite']==name),None)
  if prior and not args.retry_closed:continue
  if prior:
   archive=E/'attempts'/(name+'-'+str(time.time_ns()));archive.mkdir(parents=True)
   if(E/name).exists():shutil.copytree(E/name,archive/'raw-before-retry')
   save(archive/'HISTORICAL.json',{'priorExecution':prior,'historicalOnly':True});rows=[r for r in rows if r['suite']!=name]
  pending.append(name)
 def checkpoint():
  native=[r for r in rows if r['suite']in original.NATIVE];pair=next((r for r in rows if r['suite']=='paired-track-a'),None)
  report={'schema':'AEGIS_TRACK_B_STABLE_R3_REGRESSION_RESULTS_1','candidateSha256':args.sha,'shadowSha256':args.shadow_sha,'referenceTrackASha256':SHA_A,'referenceDeliveredBSha256':SHA_B,'referenceHistoricalR1Sha256':SHA_R1,'referenceHistoricalR2Sha256':SHA_R2,'r2OriginalSeventeenJobs':'NOT_EXECUTED_R2','controllerSha256':sha(Path(__file__).read_bytes()),'productSourceProof':source_proof,'rows':rows,'native13Passed':sum(r['passedAssertions']for r in native),'native13Expected':364,'pairedPassed':pair['passedAssertions']if pair else None,'pairedExpected':42,'domainPassed':sum(r['passedAssertions']for r in native)+(pair['passedAssertions']if pair else 0),'legacyUiIncomplete':14,'requestedSuites':names,'pendingSuites':[n for n in names if not any(r['suite']==n for r in rows)],'assertionChanges':False,'expectedValuesUpdated':False,'releaseApproved':False,'inheritedUnapproved':['CIWS419025_FAIL','ORIGINAL_CG_FRIENDLY_OBSERVER_TWO','LEGACY_UI14_INCOMPLETE'],'parallel':args.parallel,'wallS':prior_wall+time.perf_counter()-phase_start,'currentPhaseWallS':time.perf_counter()-phase_start,'workerWallSumS':sum(r['wallS']for r in rows),'timeMeaning':'Cumulative controller phase wall, excluding gaps between root-authorized phases; worker wall sums overlap under parallel2.'}
  save(destination,report)
 checkpoint();running={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel)as pool:
  while pending or running:
   while pending and len(running)<args.parallel and not(E/'STOP_AFTER_CURRENT').exists():
    # Start one native lane plus a UI/WebGL lane before pairing two long native
    # jobs. Global shared leases still enforce the same overall browser cap2.
    tail=next((n for n in pending if n in ['ui213','webgl8']),None)
    name=tail if running and tail and not any(n in ['ui213','webgl8']for n in running.values())else pending[0]
    pending.remove(name);running[pool.submit(execute,name,candidate,args.sha)]=name
   if not running:break
   done,_=concurrent.futures.wait(running,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in done:
    row=future.result();del running[future];rows.append(row);checkpoint();print(json.dumps({k:v for k,v in row.items()if k not in['command','errors','originalSourceProvenance']},ensure_ascii=False),flush=True)
 checkpoint()
 raise SystemExit(1 if any(r['status']=='FAIL'for r in rows)else 2 if any(not any(r['suite']==n for r in rows)for n in names)else 0)

if __name__=='__main__':main()
