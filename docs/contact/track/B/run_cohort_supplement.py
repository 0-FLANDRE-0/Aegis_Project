"""Supplemental actual native cohort defect reproductions, three pinned products.

No production function or old fixture/expectation is replaced. Baseline contract
failures are observations; fixture-precondition/runtime failures are separate.
Default uses the existing two-browser flock. An explicitly borrowed stopped
runtime-controller lease is allowed only after /proc verification and receipt.
"""
from pathlib import Path
from contextlib import contextmanager
import argparse,hashlib,importlib.util,json,os,time

P=Path(__file__).resolve().parent;R=P.parents[3]
BASE=R/'Aegis_SIM_v48_WIP_TRACK_A.html'
BASE_SHA='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
sha=lambda value:hashlib.sha256(value).hexdigest()

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def proc_record(pid):
 raw=Path(f'/proc/{pid}/stat').read_text();tail=raw[raw.rfind(')')+2:].split()
 return {'pid':pid,'name':raw[raw.find('(')+1:raw.rfind(')')],'state':tail[0],'ppid':int(tail[1])}

def inherited_lease_receipt(pid):
 parent=proc_record(pid);cmd=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
 if parent['state']not in ['T','t']or not any(x.endswith(b'/docs/contact/track/B/verify_runtime.py')or x==b'docs/contact/track/B/verify_runtime.py'for x in cmd):raise RuntimeError('INHERITED_LEASE_PRECONDITION: parent must be stopped known B verify_runtime.py controller')
 processes={}
 for entry in Path('/proc').iterdir():
  if not entry.name.isdigit():continue
  try:record=proc_record(int(entry.name))
  except(FileNotFoundError,ProcessLookupError,PermissionError):continue
  processes[record['pid']]=record
 descendants=[];front=[pid]
 while front:
  owner=front.pop()
  for record in processes.values():
   if record['ppid']==owner:descendants.append(record);front.append(record['pid'])
 if any(record['state']!='Z'for record in descendants):raise RuntimeError('INHERITED_LEASE_PRECONDITION: runtime descendants must all be finished zombies; no live browser/worker may share this reserved lane')
 locks=Path('/proc/locks').read_text().splitlines();owned=[]
 for slot in range(2):
  path=Path(f'/dev/shm/aegis-track-b-browser-{slot}.lock')
  if not path.exists():continue
  inode=str(path.stat().st_ino)
  if any('FLOCK'in row and len(row.split())>5 and row.split()[4]==str(pid)and row.split()[5].split(':')[-1]==inode for row in locks):owned.append(slot)
 if len(owned)!=1:raise RuntimeError('INHERITED_LEASE_PRECONDITION: stopped controller must hold exactly one existing shared browser FLOCK')
 return {'scope':'EXPLICIT_STOPPED_CONTROLLER_RESERVED_LANE','parent':parent,'parentCommandVerified':'docs/contact/track/B/verify_runtime.py','descendants':descendants,'allDescendantsZombie':True,'heldSharedSlot':owned[0],'flockOwnershipVerified':True,'newFlockAcquired':False,'receiptEpochS':time.time()}

@contextmanager
def browser_slot(slots,pid):
 if pid is None:
  with slots.heavy_browser_slot()as receipt:yield receipt
 else:
  receipt=inherited_lease_receipt(pid)
  try:yield receipt
  finally:inherited_lease_receipt(pid) # Parent must stay stopped until all browsers close.

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B.html');ap.add_argument('--candidate-sha',required=True)
 ap.add_argument('--shadow',type=Path,required=True);ap.add_argument('--shadow-sha',required=True)
 ap.add_argument('--out',type=Path,default=P/'evidence/cohort-supplement')
 ap.add_argument('--inherited-lease-parent','--lease-held-by-controller',type=int,dest='lease_parent')
 args=ap.parse_args();args.candidate=args.candidate.resolve();args.shadow=args.shadow.resolve();args.out.mkdir(parents=True,exist_ok=True)
 products=[('baseline',BASE,BASE_SHA),('shadow',args.shadow,args.shadow_sha),('active',args.candidate,args.candidate_sha)]
 for label,path,pinned in products:assert sha(path.read_bytes())==pinned,(label,'pinned product SHA mismatch')
 old_helper=P/'test_support/native_integration.js';old_helper_sha=sha(old_helper.read_bytes())
 helper_paths=[P/'test_support/native_support.js',P/'test_support/cohort_supplement.js'];helpers='\n'.join(path.read_text()for path in helper_paths)
 a=module('cohort_existing_track_a_harness',P.parent/'A/verify_runtime.py');slots=module('cohort_existing_shared_slots',P/'regression_runner.py');h=a.load_harness()
 from playwright.sync_api import sync_playwright
 start=time.perf_counter();rows=[];errors=[]
 provenance={'schema':'AEGIS_TRACK_B_COHORT_SUPPLEMENT_PROVENANCE_1','runnerSha256':sha(Path(__file__).read_bytes()),'helpers':[{'path':str(path.relative_to(R)),'sha256':sha(path.read_bytes())}for path in helper_paths],'oldNativeIntegrationHelper':{'path':str(old_helper.relative_to(R)),'sha256':old_helper_sha,'loaded':False,'edited':False},'products':[{'label':label,'path':str(path.relative_to(R)),'sha256':pinned}for label,path,pinned in products],'harnessPath':str((P.parent/'A/verify_runtime.py').relative_to(R)),'harnessSha256':sha((P.parent/'A/verify_runtime.py').read_bytes()),'classification':'DIRECT_NATIVE_ANONYMOUS_INGRESS_NOT_NATURAL_RF','existingAssertionsChanged':False,'inheritedLeaseParent':args.lease_parent,'releaseApproved':False}
 (args.out/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
 for label,path,pinned in products:
  with browser_slot(slots,args.lease_parent)as receipt:
   raw=h.base.build(file=str(path.relative_to(R)),record=False,extra=helpers+'\n'+a.PASSIVE_HELPER);server,url=h.serve(raw);browser=None
   try:
    with sync_playwright()as pw:
     browser=h.launch(pw);page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=errors);page.set_default_timeout(600000)
     initial=page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})')
     assert not initial['a']['enabled']and(initial['b']is None or not initial['b']['enabled']),'Diagnostic default not OFF'
     if label!='baseline':assert initial['b']['mode']==('SHADOW'if label=='shadow'else'ACTIVE'),'Incorrect frozen product mode'
     result=page.evaluate('__TRACK_B_COHORT_SUPPLEMENT__.run()')
     # Persist actual outcomes before ANY subsequent query can fail. This raw
     # result retains fixture errors and after-action state, without reexecution.
     (args.out/(label+'-native-result.json')).write_text(json.dumps({'label':label,'productSha256':pinned,'testCopySha256':sha(raw),'helpers':provenance['helpers'],'nativeResult':result},separators=(',',':'))+'\n')
     state_hashes={name:sha(value.encode())for name,value in result.pop('afterActionStateByFixture').items()}
     before=page.evaluate('__TRACK_B_COHORT_SUPPLEMENT__.state()');one=page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})');two=page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})');after=page.evaluate('__TRACK_B_COHORT_SUPPLEMENT__.state()')
     env=page.evaluate('__ENV_D__.status()')
     row={'label':label,'productSha256':pinned,'testCopySha256':sha(raw),'helpers':provenance['helpers'],'classification':provenance['classification'],'nativeResult':result,'perFixturePassiveStateSha256':state_hashes,'queryStateUnchanged':before==after,'querySnapshotExact':one==two,'envMatch':env['match']is True,'diagnostics':one,'initialDiagnosticDefaults':initial,'leaseReceipt':receipt,'policyAssertionFailures':[name for name,value in result['checks'].items()if not value and not name.endswith('.completed')],'fixturePreconditionOrRuntimeFailures':[name for name,value in result['checks'].items()if not value and name.endswith('.completed')]}
     rows.append(row);(args.out/(label+'.json')).write_text(json.dumps(row,separators=(',',':'))+'\n')
     page.context.close();browser.close();browser=None
     print(label,'checks',sum(result['checks'].values()),'/',len(result['checks']),'precondition/runtime errors',len(result['errors']),'wall',round(time.perf_counter()-start,2),flush=True)
   finally:
    if browser is not None:
     try:browser.close()
     except Exception:pass
    server.shutdown()
  assert sha(path.read_bytes())==pinned,'Pinned product changed during execution'
 assert sha(old_helper.read_bytes())==old_helper_sha,'Existing native integration helper changed'
 base,shadow,active=rows;record_exact=base['nativeResult']['records']==shadow['nativeResult']['records'];state_exact=base['perFixturePassiveStateSha256']==shadow['perFixturePassiveStateSha256'];precondition_errors=[{'label':row['label'],'errors':row['nativeResult']['errors']}for row in rows if row['nativeResult']['errors']]
 legacy={name:base['nativeResult']['records'].get(name,{}).get('legacyDefectObserved')is True for name in ['npcActualGreedyTrap','hawklinkActualSequentialFalseReplay']}
 protections=all(row['queryStateUnchanged']and row['querySnapshotExact']and row['envMatch']for row in rows)
 passed=not errors and not precondition_errors and all(legacy.values())and record_exact and state_exact and active['nativeResult']['pass']and protections
 summary={'schema':'AEGIS_TRACK_B_COHORT_SUPPLEMENT_RUN_1','status':'PASS'if passed else'INCOMPLETE_FIXTURE'if precondition_errors else'FAIL','candidateSha256':args.candidate_sha,'shadowSha256':args.shadow_sha,'baselineSha256':BASE_SHA,'baselineDefectsActuallyReproduced':legacy,'shadowActualNativeRecordsExact':record_exact,'shadowPrivateGameRngStateExact':state_exact,'activeChecks':{'count':len(active['nativeResult']['checks']),'passed':sum(active['nativeResult']['checks'].values())},'fixturePreconditionOrRuntimeErrors':precondition_errors,'browserErrors':errors,'queryAndProtectedFunctionChecksPass':protections,'rows':[{'label':row['label'],'productSha256':row['productSha256'],'fixturePreconditionOrRuntimeFailures':row['fixturePreconditionOrRuntimeFailures'],'policyAssertionFailures':row['policyAssertionFailures']}for row in rows],'classification':provenance['classification'],'naturalRfOrWeaponEvidence':False,'existingAssertionsChanged':False,'oldNativeIntegrationHelperUnchanged':True,'countsNotAddedToExistingDomain420':True,'wallS':time.perf_counter()-start,'releaseApproved':False}
 (args.out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));return 0 if passed else 1

if __name__=='__main__':raise SystemExit(main())
