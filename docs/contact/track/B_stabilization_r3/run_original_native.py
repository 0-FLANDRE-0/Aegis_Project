"""Replay ALL immutable original-B native fixtures on final stable products.

Default is preparation only. --run is required and must receive frozen SHAs.
Each product/trace configuration receives separate fresh native and cohort page
contexts. This avoids comparing a cohort with a different native-test prelude.
The original cohort helper itself forces diagnostics ON; never call that an
OFF cohort test. No original helper, assertion or expected value is rewritten.
"""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,inspect,json,time
P=Path(__file__).resolve().parent;R=P.parents[3];B=P.parent/'B';A=P.parent/'A'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
PASSIVE_ACCESSOR='window.__TRACK_B_ORIGINAL_NATIVE_PASSIVE__=()=>TRACK_B_NATIVE_SUPPORT.afterActionPassiveState();'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')
def packed(path,value):
 raw=json.dumps(value,separators=(',',':')).encode();path.write_bytes(gzip.compress(raw,6,mtime=0));return {'path':path.name,'rawSha256':sha(raw),'gzipSha256':sha(path.read_bytes())}
def differences(a,b):
 absent=object();rows=[]
 def walk(x,y,at=''):
  if x is absent or y is absent:rows.append({'path':at,'beforePresent':x is not absent,'afterPresent':y is not absent,'before':None if x is absent else x,'after':None if y is absent else y})
  elif type(x)is not type(y):rows.append({'path':at,'before':x,'after':y,'typeChanged':True})
  elif isinstance(x,dict):
   for key in sorted(set(x)|set(y)):walk(x.get(key,absent),y.get(key,absent),at+'/'+str(key).replace('~','~0').replace('/','~1'))
  elif isinstance(x,list):
   for i in range(max(len(x),len(y))):walk(x[i]if i<len(x)else absent,y[i]if i<len(y)else absent,at+'/'+str(i))
  elif x!=y:rows.append({'path':at,'before':x,'after':y})
 walk(a,b);return rows

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_C.html');ap.add_argument('--sha',required=True);ap.add_argument('--shadow',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_C_SHADOW.html');ap.add_argument('--shadow-sha',required=True);ap.add_argument('--out',type=Path,default=P/'evidence/original-native-full');ap.add_argument('--run',action='store_true');args=ap.parse_args();r1_test_inputs=module('r2_frozen_native_inputs',P/'controller_pins.py').verify();args.candidate=args.candidate.resolve();args.shadow=args.shadow.resolve();args.out.mkdir(parents=True,exist_ok=True)
 pins=json.loads((P/'BASELINE_PINS.json').read_text());base_sha=pins['files']['Aegis_SIM_v48_WIP_TRACK_B.html'];manifest={}
 for line in(B/'CHECKSUMS.sha256').read_text().splitlines():
  if line.strip():digest,name=line.split(None,1);manifest[name.strip()]=digest
 paths=[B/'run_native.py',B/'run_cohort_supplement.py',B/'test_support/native_support.js',B/'test_support/native_c55.js',B/'test_support/native_integration.js',B/'test_support/cohort_supplement.js',B/'evidence/native-integration/active-off.json',B/'evidence/native-integration/active-on.json',B/'evidence/cohort-supplement/active.json']
 original_source_rows=[]
 for file in paths:
  name=str(file.relative_to(B));expected=manifest[name];actual=sha(file.read_bytes());assert actual==expected,('Original B source/evidence changed',name);original_source_rows.append({'path':str(file.relative_to(R)),'sha256':actual,'publishedManifestSha256':expected,'exact':True})
 for file,pin in [(args.candidate,args.sha),(args.shadow,args.shadow_sha)]:assert sha(file.read_bytes())==pin,('Frozen final product changed',file)
 original_runner=module('stable_full_unmodified_b_run_native',B/'run_native.py');cohort_runner=module('stable_full_unmodified_b_run_cohort',B/'run_cohort_supplement.py');support=module('stable_full_original_a_support',A/'verify_runtime.py');slots=module('stable_full_original_b_slots',B/'regression_runner.py')
 native_helpers=[B/'test_support/native_support.js',B/'test_support/native_c55.js',B/'test_support/native_integration.js'];cohort_helpers=[B/'test_support/native_support.js',B/'test_support/cohort_supplement.js'];native_source='\n'.join(p.read_text()for p in native_helpers);cohort_source='\n'.join(p.read_text()for p in cohort_helpers)
 refs={'native-off':json.loads((B/'evidence/native-integration/active-off.json').read_text()),'native-on':json.loads((B/'evidence/native-integration/active-on.json').read_text()),'cohort':json.loads((B/'evidence/cohort-supplement/active.json').read_text())}
 assert refs['native-off']['productSha256']==refs['native-on']['productSha256']==refs['cohort']['productSha256']==base_sha
 assert refs['native-off']['fixtureSourceSha256']==refs['native-on']['fixtureSourceSha256']==sha(native_source.encode())
 products=[('shadow-off','SHADOW',False,args.shadow,args.shadow_sha),('shadow-on','SHADOW',True,args.shadow,args.shadow_sha),('active-off','ACTIVE',False,args.candidate,args.sha),('active-on','ACTIVE',True,args.candidate,args.sha)]
 provenance={'schema':'AEGIS_TRACK_B_STABLE_ORIGINAL_NATIVE_PROVENANCE_1','runnerSha256':sha(Path(__file__).read_bytes()),'candidateSha256':args.sha,'shadowSha256':args.shadow_sha,'oldBReferenceSha256':base_sha,'originalBSourceAndEvidence':original_source_rows,'nativeHelperCombinedSha256':sha(native_source.encode()),'cohortHelperCombinedSha256':sha(cohort_source.encode()),'nativeHelpers':[str(x.relative_to(R))for x in native_helpers],'cohortHelpers':[str(x.relative_to(R))for x in cohort_helpers],'oldNativeRunnerImportedByteUnchanged':True,'oldCohortRunnerImportedByteUnchanged':True,'oldC55AccessorFunctionSha256':sha(inspect.getsource(original_runner.c55_access_test_copy).encode()),'additionalReadOnlyPassiveAccessorSha256':sha(PASSIVE_ACCESSOR.encode()),'originalMainInvoked':False,'controllerAdaptation':'New controller uses original helper bytes and imported original C55 test-accessor function. It checks actual B mode ACTIVE plus stabilizationMode rather than the old runner main-only SHADOW guard. No game assertion or expected value changed.','nativeScope':'All23 original groups:84 checks diagnosticOFF;90 checks diagnosticON.','cohortScope':'Original14 checks; helper itself always enablesdiagnostics, so every cohort page is explicitly ON regardless of variant label.','freshContexts':8,'maxConcurrentBrowsers':1,'estimatedWallMinutes':2,'existingExpectationsChanged':False,'countsNotAddedToDomain420':True,'naturalRfOrCombatEvidence':False,'releaseApproved':False}
 provenance['frozenR1NativeInputs']=r1_test_inputs;save(args.out/'PROVENANCE.json',provenance)
 if not args.run:print(json.dumps({'dryRun':True,'browserRuns':0,**provenance},indent=2));return 0
 h=support.load_harness();rows=[];browser_errors=[];started=time.perf_counter()
 from playwright.sync_api import sync_playwright
 with slots.heavy_browser_slot()as lease:
  for label,mode,trace,file,pin in products:
   assert sha(file.read_bytes())==pin
   row={'label':label,'mode':mode,'requestedNativeTrace':trace,'product':file.name,'productSha256':pin,'lease':lease,'suites':{}}
   with sync_playwright()as pw:
    browser=h.launch(pw)
    try:
     for suite,helper in [('native',native_source),('cohort',cohort_source)]:
      raw=h.base.build(file=str(file.relative_to(R)),record=False,extra=helper+'\n'+support.PASSIVE_HELPER+'\n'+PASSIVE_ACCESSOR)
      if suite=='native':raw=original_runner.c55_access_test_copy(raw)
      server,url=h.serve(raw)
      try:
       page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=browser_errors);page.set_default_timeout(600000);initial=page.evaluate('({a:__TRACK_A__.snapshot(),b:__TRACK_B__.snapshot()})');assert initial['a']['enabled']is False and initial['b']['enabled']is False;assert initial['b']['mode']=='ACTIVE'and initial['b']['stabilizationMode']==mode
       if suite=='native':
        page.evaluate('on=>{__TRACK_B__.configure({enabled:on,capacity:4096});__TRACK_B__.clear()}',trace)
        result=page.evaluate('__TRACK_B_NATIVE_INTEGRATION__.run()');ref=refs['native-on'if trace else'native-off'];expected_count=90 if trace else 84
       else:
        # Exact original helper enables both diagnostics inside reset().
        result=page.evaluate('__TRACK_B_COHORT_SUPPLEMENT__.run()');ref=refs['cohort'];expected_count=14
       raw_result=packed(args.out/(label+'-'+suite+'-raw-before-aux.json.gz'),result)
       states={name:sha(value.encode())for name,value in result.pop('afterActionStateByFixture').items()}
       full_before=page.evaluate('__TRACK_B_ORIGINAL_NATIVE_PASSIVE__()');world_before=page.evaluate('__TRACK_RUNTIME_A__.state()');one=page.evaluate('({a:__TRACK_A__.snapshot(),b:__TRACK_B__.snapshot()})');two=page.evaluate('({a:__TRACK_A__.snapshot(),b:__TRACK_B__.snapshot()})');env=page.evaluate('__ENV_D__.status()');full_after=page.evaluate('__TRACK_B_ORIGINAL_NATIVE_PASSIVE__()')
       ref_states=ref['perFixturePassiveFullStateSha256'if suite=='native'else'perFixturePassiveStateSha256'];delta=differences(ref['nativeResult'],result);state_delta=differences(ref_states,states)
       delta_proof=packed(args.out/(label+'-'+suite+'-old-B-full-raw-deltas.json.gz'),{'nativeResult':delta,'perFixtureFullStateHashes':state_delta,'noDifferingFieldIgnored':True})
       checks={'allOriginalChecksExecuted':len(result['checks'])==expected_count,'allOriginalAssertionsPass':result['pass']is True,'originalErrorsZero':not result['errors'],'actualNativeResultExactPublishedB':not delta,'perFixtureFullStateExactPublishedB':not state_delta,'fullPrivateStateQueryPure':full_before==full_after,'snapshotsStable':one==two,'envStatusMatch':env['match']is True,'coreSelftestZero':not page.evaluate('__CORE_SELFTEST_FAILURES__')}
       if suite=='native':checks['postWorldStateExactPublishedB']=sha(world_before.encode())==ref['postFixtureStateSha256']
       else:checks['helperActuallyEnabledDiagnostics']=one['a']['enabled']is True and one['b']['enabled']is True
       result_row={'suite':suite,'expectedOriginalAssertions':expected_count,'passedOriginalAssertions':sum(result['checks'].values()),'requestedNativeTrace':trace,'actualCohortDiagnosticPolicy':'FORCED_ON_BY_UNMODIFIED_ORIGINAL_HELPER'if suite=='cohort'else None,'initialDiagnosticDefaults':initial,'actualPostDiagnosticEnabled':{'a':one['a']['enabled'],'b':one['b']['enabled']},'rawResultBeforeAuxiliaryQueries':raw_result,'nativeResult':result,'perFixtureFullStateSha256':states,'postFullPrivateStateSha256':sha(full_before.encode()),'postWorldStateSha256':sha(world_before.encode()),'rawDeltaCount':len(delta),'stateHashDeltaCount':len(state_delta),'rawDeltaProof':delta_proof,'checks':checks,'envStatus':env,'testCopySha256':sha(raw),'diagnostics':one}
       row['suites'][suite]=result_row;save(args.out/(label+'-'+suite+'.json'),result_row);page.context.close();print(label,suite,sum(result['checks'].values()),'/',expected_count,'oldRawDelta',len(delta),'stateDelta',len(state_delta),'controls',all(checks.values()),flush=True)
      finally:server.shutdown()
    finally:browser.close()
   rows.append(row);save(args.out/(label+'.json'),row);assert sha(file.read_bytes())==pin
 trace_pairs=[]
 for mode in ['SHADOW','ACTIVE']:
  off,on=[r for r in rows if r['mode']==mode];proof={'mode':mode}
  for suite in ['native','cohort']:
   x,y=off['suites'][suite],on['suites'][suite]
   # Native result has ON-only C55 assertions and A diagnostics, so compare the
   # immutable gameplay records plus all full-state hashes; preserve full raw.
   proof[suite]={'nativeRecordsExact':x['nativeResult']['records']==y['nativeResult']['records'],'allPerFixturePrivateStateExact':x['perFixtureFullStateSha256']==y['perFixtureFullStateSha256'],'postFullPrivateStateExact':x['postFullPrivateStateSha256']==y['postFullPrivateStateSha256'],'postWorldStateExact':x['postWorldStateSha256']==y['postWorldStateSha256'],'cohortBothActuallyOn':suite=='cohort'}
  trace_pairs.append(proof)
 passed=all(all(s['checks'].values())for r in rows for s in r['suites'].values())and not browser_errors and all(all(v for k,v in p[suite].items()if k!='cohortBothActuallyOn')for p in trace_pairs for suite in ['native','cohort'])
 value={'schema':'AEGIS_TRACK_B_STABLE_ORIGINAL_NATIVE_RUN_1','status':'PASS'if passed else'FAIL','allTasksComplete':True,'candidateSha256':args.sha,'shadowSha256':args.shadow_sha,'oldBReferenceSha256':base_sha,'contextsExecuted':sum(len(r['suites'])for r in rows),'expectedContexts':8,'originalNative':{'groups':23,'offCount':84,'onCount':90},'cohort':{'count':14,'actualDiagnosticPolicy':'FORCED_ON_BY_ORIGINAL_HELPER_ALL4_CONTEXTS'},'sourceProvenance':'PROVENANCE.json','traceOffOn':trace_pairs,'rows':[{'label':r['label'],'suites':{name:{'passed':s['passedOriginalAssertions'],'expected':s['expectedOriginalAssertions'],'checks':s['checks'],'rawDeltaCount':s['rawDeltaCount'],'stateHashDeltaCount':s['stateHashDeltaCount']}for name,s in r['suites'].items()}}for r in rows],'browserErrors':browser_errors,'wallS':time.perf_counter()-started,'existingAssertionsOrExpectationsChanged':False,'allDifferingRawFieldsRetained':True,'naturalRfOrCombatEvidence':False,'releaseApproved':False,'performanceApproved':False}
 save(args.out/'SUMMARY.json',value);print(json.dumps(value,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
