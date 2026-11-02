"""TRACK-B broad regression lane; original tests and expectations stay intact.

Default is a read-only dry run. --run requires a frozen candidate SHA. A raw
strict-comparison failure stays FAIL, even when a changed association is an
intended B behavior. Separate full-field deltas support review, never approval.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse,concurrent.futures,fcntl,gzip,hashlib,importlib.util,json,os,subprocess,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3];A=P.parent/'A';E=P/'evidence/regression'
REFERENCE=R/'Aegis_SIM_v48_WIP_TRACK_A.html'
REFERENCE_SHA='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('track_a_unchanged_regression_commands',A/'regression_runner.py')
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
NATIVE=original.NATIVE
assert len(NATIVE)==13 and sum(x[2]for x in NATIVE.values())==364
REQUESTED_SUITE_NAMES=[]

def source_head():
 return subprocess.check_output(['git','rev-parse','ee960db'],cwd=R,text=True).strip()

def test_source_provenance():
 """Compare original test/helper bytes to the pinned TRACK-A git reference."""
 paths=['docs/pip/B/run_domain.py','docs/map/A/verify_regressions.py','docs/viewport/A/verify_regressions.py',
  'docs/gun/B2/phase1b/test_support/sitecustomize.py','docs/map/E/legacy_test_adapter.py',
  'docs/pip/B/browser_backend.py','docs/contact/friendly/A/cpu2d_ui.py','docs/envelope/D/run_observed_webgl.py',
  'docs/missile/termination/A/verify_observed_world.py','docs/helicopter/F/verify_regression.py',
  *[x[0]for x in NATIVE.values()]]
 rows=[];head=source_head()
 for name in paths:
  current=sha((R/name).read_bytes());before=sha(subprocess.check_output(['git','show',head+':'+name],cwd=R))
  rows.append({'path':name,'sha256':current,'referenceSha256':before,'unchanged':current==before})
 return {'referenceHead':head,'status':'PASS'if all(r['unchanged']for r in rows)else'INCOMPLETE','files':rows,'controllerSha256':sha(Path(__file__).read_bytes()),
  'assertionChanges':False,'expectedValuesUpdated':False}

def reference_evidence():
 manifest={}
 for line in(A/'CHECKSUMS.sha256').read_text().splitlines():
  if line.strip():digest,path=line.split(None,1);manifest[path.strip()]=digest
 selected=['VALIDATION.json','BUILD.json','SCOPE.json','REGRESSION_RESULTS.json',
  'regression_runner.py','verify_runtime.py','evidence/candidate/RUNTIME_SUMMARY.json',
  'evidence/candidate/friendly/ciws-d1.jsonl.gz','evidence/candidate/helo-hover-off.json',
  'evidence/candidate/helo-route-off.json','evidence/candidate/harpoon-route-off.json',
  'evidence/candidate/trace419025-off.json','evidence/candidate/friendly/idle-and-dom.json']
 rows=[]
 for name in selected:
  path=A/name;actual=sha(path.read_bytes())if path.exists()else None
  rows.append({'path':str(path.relative_to(R)),'sha256':actual,'manifestSha256':manifest.get(name),'match':actual is not None and actual==manifest.get(name)})
 v=json.loads((A/'VALIDATION.json').read_text());rt=json.loads((A/'evidence/candidate/RUNTIME_SUMMARY.json').read_text())
 checks={'referenceHtmlSha256':sha(REFERENCE.read_bytes())==REFERENCE_SHA,
  'referenceAuthoritativeStageAPass':v.get('trackAStatus')=='PASS'and v.get('finalEvidenceComplete')is True and v.get('candidateSha256')==REFERENCE_SHA,
  'referenceRuntimeComplete':rt.get('status')=='PASS'and rt.get('allTasksComplete')is True and rt.get('candidateSha256')==REFERENCE_SHA,
  'allReusedFilesMatchPublishedManifest':all(r['match']for r in rows),
  'referenceReleaseUnapprovedPreserved':v.get('releaseApproved')is False}
 return {'schema':'AEGIS_TRACK_B_REFERENCE_EVIDENCE_1','referenceHead':source_head(),'referenceHtml':REFERENCE.name,'referenceSha256':REFERENCE_SHA,
  'status':'PASS'if all(checks.values())else'INCOMPLETE','checks':checks,'files':rows,
  'evidenceReuseMeaning':'Hash-verified TRACK-A evidence, not a new B run or approval of inherited outcomes.','releaseApproved':False}

@contextmanager
def heavy_browser_slot():
 """Cooperating B runners share two flock leases; no browser is launched here."""
 start=time.perf_counter();handle=None;slot=None
 while handle is None:
  for i in range(2):
   f=open(f'/dev/shm/aegis-track-b-browser-{i}.lock','a+')
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:f.close();continue
   handle=f;slot=i;break
  if handle is None:time.sleep(.25)
 try:yield {'slot':slot,'waitS':time.perf_counter()-start,'scope':'COOPERATING_RUNNERS_ONLY_USE_SAME_HELPER'}
 finally:fcntl.flock(handle,fcntl.LOCK_UN);handle.close()

def configure(candidate,candidate_sha):
 original.HTML=candidate;original.BASE=REFERENCE;original.E=E
 original.EXPECTED=candidate_sha;original.BASE_SHA=REFERENCE_SHA

def job(name):
 if name=='paired-track-a':return [sys.executable,'-u',str(R/'docs/helicopter/F/verify_regression.py'),str(REFERENCE),str(original.HTML),str(E/name),'--baseline-only']
 return original.job(name)

def paired_extract(code):
 path=E/'paired-track-a/baseline-comparison.json';checks={};errors=[]
 if path.exists():
  data=json.loads(path.read_text());errors=data.get('errors',[])
  checks={r['ship']+':'+r['scenario']+':'+k:v for r in data['cases']for k,v in r['checks'].items()}
 failed=[k for k,v in checks.items()if not v];log=(E/'paired-track-a.log').read_text(errors='replace')
 if code==0 and len(checks)==42 and not failed and not errors:status='PASS';reason=None
 elif code==124 or'Target crashed'in log or'Target closed'in log:status='INCOMPLETE';reason='Original worker timeout/browser failure; not PASS'
 else:status='FAIL';reason='Original strict comparison failed or output incomplete; delta needs cause review, not an updated expectation'
 return {'status':status,'reason':reason,'expectedAssertions':42,'executedAssertions':len(checks),'passedAssertions':sum(bool(v)for v in checks.values())if status!='INCOMPLETE'else 0,
  'failedAssertions':failed,'errors':errors,'resultPath':str(path.relative_to(E))if path.exists()else None}

def all_field_deltas():
 """Retain every differing JSON leaf, including timing fields in their own group.

The original raw pair is retained too. Categorization does not waive an original
assertion or silently exclude x/P, classification, identity, freshness or RNG.
"""
 source=E/'paired-track-a/baseline-comparison.json'
 if not source.exists():return None
 data=json.loads(source.read_text());missing=object();rows=[]
 def pointer(x):return str(x).replace('~','~0').replace('/','~1')
 def walk(a,b,path=''):
  if a is missing or b is missing:
   if (a is not missing and isinstance(a,(dict,list))and not a)or(b is not missing and isinstance(b,(dict,list))and not b):
    yield {'path':path,'beforePresent':a is not missing,'afterPresent':b is not missing,'before':None if a is missing else a,'after':None if b is missing else b}
   elif a is not missing and isinstance(a,dict):
    for k,v in a.items():yield from walk(v,missing,path+'/'+pointer(k))
   elif b is not missing and isinstance(b,dict):
    for k,v in b.items():yield from walk(missing,v,path+'/'+pointer(k))
   elif a is not missing and isinstance(a,list):
    for i,v in enumerate(a):yield from walk(v,missing,path+'/'+str(i))
   elif b is not missing and isinstance(b,list):
    for i,v in enumerate(b):yield from walk(missing,v,path+'/'+str(i))
   else:yield {'path':path,'beforePresent':a is not missing,'afterPresent':b is not missing,'before':None if a is missing else a,'after':None if b is missing else b}
  elif type(a)!=type(b):yield {'path':path,'before':a,'after':b,'typeChanged':True}
  elif isinstance(a,dict):
   for k in sorted(set(a)|set(b)):yield from walk(a.get(k,missing),b.get(k,missing),path+'/'+pointer(k))
  elif isinstance(a,list):
   if len(a)!=len(b):yield {'path':path+'/~length','before':len(a),'after':len(b)}
   for i in range(max(len(a),len(b))):yield from walk(a[i]if i<len(a)else missing,b[i]if i<len(b)else missing,path+'/'+str(i))
  elif a!=b:yield {'path':path,'before':a,'after':b}
 for case in data['cases']:
  changes=list(walk(case['pair']['baseline'],case['pair']['candidate']))
  for c in changes:
   c['diagnosticTimingOrHeapField']=c['path'].startswith('/heapEstimateBytes/')or c['path']=='/elapsedMs'or c['path'].endswith(('/avgMs','/p95Ms','/maxMs'))
  rows.append({'ship':case['ship'],'scenario':case['scenario'],'originalChecks':case['checks'],'classification':'UNAPPROVED_DIFFERENCE_REQUIRES_REVIEW'if any(not v for v in case['checks'].values())else'ORIGINAL_ASSERTIONS_PASS',
   'allDifferingLeafCount':len(changes),'changes':changes,'noChangedFieldExcluded':True})
 out={'schema':'AEGIS_TRACK_B_PAIRED_ALL_FIELD_DELTAS_1','referenceSha256':REFERENCE_SHA,'candidateSha256':original.EXPECTED,'source':str(source.relative_to(P)),
  'allFieldsRetained':True,'originalExpectedValuesChanged':False,'automaticApproval':False,'cases':rows}
 target=E/'paired-state-deltas.json.gz';target.write_bytes(gzip.compress(json.dumps(out,separators=(',',':')).encode(),6,mtime=0))
 return {'path':str(target.relative_to(P)),'sha256':sha(target.read_bytes()),'cases':len(rows),'changedLeaves':sum(r['allDifferingLeafCount']for r in rows),'reviewOnly':True}

def execute(name):
 assert sha(original.HTML.read_bytes())==original.EXPECTED
 assert sha(REFERENCE.read_bytes())==REFERENCE_SHA
 command=job(name);at=time.perf_counter()
 with heavy_browser_slot()as lease:
  running=time.perf_counter()
  with(E/(name+'.log')).open('w')as log:
   try:p=subprocess.run(command,cwd=R,env=original.environment(),stdout=log,stderr=subprocess.STDOUT,timeout=150 if name=='emcon-ui'else 1200);code=p.returncode
   except subprocess.TimeoutExpired:code=124
  result=paired_extract(code)if name=='paired-track-a'else original.extract(name,code)
  row={'suite':name,'command':command,'exitCode':code,'executionS':time.perf_counter()-running,'wallS':time.perf_counter()-at,'lease':lease,**result}
  if name=='paired-track-a':row['allFieldDeltaEvidence']=all_field_deltas()
  row['expectedValuesChanged']=False;row['deltaApproved']=False
  if row['status']=='FAIL':row['reviewPending']=True
  (E/(name+'-execution.json')).write_text(json.dumps(row,indent=2)+'\n')
  return row

def report(rows,reference,candidate,start):
 native=[r for r in rows if r['suite']in NATIVE];pair=next((r for r in rows if r['suite']=='paired-track-a'),None)
 out={'schema':'AEGIS_TRACK_B_EXISTING_REGRESSIONS_1','referenceHead':source_head(),'reference':REFERENCE.name,'referenceSha256':REFERENCE_SHA,
  'candidate':str(candidate.relative_to(R))if candidate.is_relative_to(R)else str(candidate),'candidateSha256':original.EXPECTED,
  'referenceEvidence':reference,'comparisonMeaning':'Original assertions unchanged. Any new full-state/observer/physics difference remains visible and unapproved.','rows':rows,
  'native13':{'suiteCount':len(native),'expectedSuiteCount':13,'executedAssertions':sum(r['executedAssertions']for r in native),'passedAssertions':sum(r['passedAssertions']for r in native),'expectedAssertions':364},
  'currentVsTrackADomain':{'totalExpected':420,'passed':sum(r['passedAssertions']for r in native)+(pair['passedAssertions']if pair else 0),'pairedExpected':42,'pairedPassed':pair['passedAssertions']if pair else None,'retiredUiIncomplete':14},
  'inheritedCgVsFriendlyDomain':{'total':420,'passed':404,'observerKnownDeltaUnapproved':2,'retiredUiIncomplete':14},
  'assertionChanges':False,'expectedValuesUpdated':False,'automaticDeltaApproval':False,'releaseApproved':False,
  'requestedFreshSuites':REQUESTED_SUITE_NAMES,'pendingFreshSuites':[name for name in REQUESTED_SUITE_NAMES if not any(r['suite']==name for r in rows)],
  'allRequestedFreshSuitesExecuted':all(any(r['suite']==name for r in rows)for name in REQUESTED_SUITE_NAMES),
  'inheritedUnresolved':['CIWS419025_FAIL','CG_FRIENDLY_PAIRED_OBSERVER_2_UNAPPROVED','RETIRED_EMCON_UI14_INCOMPLETE'],
  'newStrictFailures':[r['suite']for r in rows if r['status']=='FAIL'],'incomplete':[r['suite']for r in rows if r['status']=='INCOMPLETE'],'wallS':time.perf_counter()-start}
 (P/'REGRESSION_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n');return out

def main():
 global REQUESTED_SUITE_NAMES
 ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B.html');ap.add_argument('--sha')
 ap.add_argument('--only',nargs='+',choices=[*NATIVE,'paired-track-a','ui213','webgl8','emcon-ui']);ap.add_argument('--run',action='store_true')
 ap.add_argument('--resume',action='store_true');ap.add_argument('--parallel',type=int,choices=[1,2],default=1);args=ap.parse_args()
 candidate=args.candidate.absolute();configure(candidate,args.sha);reference=reference_evidence();sources=test_source_provenance();names=args.only or[*NATIVE,'paired-track-a','ui213','webgl8']
 REQUESTED_SUITE_NAMES=list(names)
 if not args.run:
  print(json.dumps({'dryRun':True,'noBrowserLaunched':True,'reference':reference,'candidate':str(candidate),'candidateShaRequiredForRun':True,
   'sourceProvenance':sources,'parallel':args.parallel,'jobs':[{'suite':n,'command':job(n)}for n in names],'legacyUi14':'INCOMPLETE, not executed unless explicitly selected','automaticDeltaApproval':False},indent=2));return
 assert args.sha and sha(candidate.read_bytes())==args.sha,'--run requires the actual frozen candidate --sha'
 assert reference['status']=='PASS','Published TRACK-A evidence failed hash/provenance checks'
 assert sources['status']=='PASS','Original assertion/fixture/helper bytes differ from the pinned TRACK-A reference'
 E.mkdir(parents=True,exist_ok=True);(E/'reference-evidence.json').write_text(json.dumps(reference,indent=2)+'\n')
 (E/'source-provenance.json').write_text(json.dumps(sources,indent=2)+'\n')
 rows=[];start=time.perf_counter()
 if not args.only or'emcon-ui'not in args.only:
  rows.append({'suite':'emcon-ui','status':'INCOMPLETE','expectedAssertions':14,'executedAssertions':0,'passedAssertions':0,'failedAssertions':[],
   'reason':'Inherited retired #lockBtn UI debt; not waived or counted PASS. No new B execution unless explicitly selected.'})
 if args.resume and(P/'REGRESSION_RESULTS.json').exists():
  old=json.loads((P/'REGRESSION_RESULTS.json').read_text());assert old['candidateSha256']==args.sha and old['referenceSha256']==REFERENCE_SHA
  rows=old['rows'];names=[n for n in names if not any(r['suite']==n for r in rows)]
 report(rows,reference,candidate,start)
 # Submit only the currently available lane(s), so a STOP_AFTER_CURRENT marker
 # can halt safely between native workers without silently launching queued jobs.
 stop=E/'STOP_AFTER_CURRENT';pending=list(names);running={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel)as pool:
  while pending or running:
   while pending and len(running)<args.parallel and not stop.exists():
    name=pending.pop(0);running[pool.submit(execute,name)]=name
   if not running:break
   done,_=concurrent.futures.wait(running,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in done:
    row=future.result();del running[future];rows.append(row);report(rows,reference,candidate,start)
    print(json.dumps({k:v for k,v in row.items()if k not in['command','errors']},ensure_ascii=False),flush=True)
 result=report(rows,reference,candidate,start);raise SystemExit(1 if result['newStrictFailures']else 2 if not result['allRequestedFreshSuitesExecuted']else 0)

if __name__=='__main__':main()
