"""Frozen actual native fixture replay: old B ACTIVE vs stabilization SHADOW/ACTIVE.

Raw candidate policy failures are retained. SHADOW is accepted only as a
behavior-preserving diagnostic proposal; this does not approve live policy.
"""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,time
P=Path(__file__).resolve().parent;R=P.parents[3];B=P.parent/'B';A=P.parent/'A'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')
def packed(path,value):
 raw=json.dumps(value,separators=(',',':')).encode();path.write_bytes(gzip.compress(raw,6,mtime=0));return {'path':path.name,'rawSha256':sha(raw),'gzipSha256':sha(path.read_bytes())}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--sha',required=True);ap.add_argument('--mode',choices=['SHADOW','ACTIVE'],required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.candidate=args.candidate.resolve();args.out.mkdir(parents=True,exist_ok=True)
 pins=json.loads((P/'BASELINE_PINS.json').read_text());base=R/'Aegis_SIM_v48_WIP_TRACK_B.html';base_sha=pins['files'][base.name];assert sha(base.read_bytes())==base_sha;assert sha(args.candidate.read_bytes())==args.sha
 helpers=[B/'test_support/native_support.js',B/'test_support/native_integration.js',P/'test_support/native_policy.js',P/'test_support/native_metadata.js'];helper_source='\n'.join(p.read_text()for p in helpers)
 support=module('stable_native_original_a',A/'verify_runtime.py');slots=module('stable_native_shared_slots',B/'regression_runner.py');h=support.load_harness()
 old_selected=['ownExactAmbiguity','ownDopplerCrossing','spqSurfaceAmbiguityNoBirth','airThenSurfacePrior','hawklinkNativeTimeAndDelayContract']
 products=[('baseline',False,base,base_sha),('candidate-off',False,args.candidate,args.sha),('candidate-on',True,args.candidate,args.sha)];rows=[];errors=[];started=time.perf_counter()
 provenance={'schema':'AEGIS_TRACK_B_STABLE_NATIVE_PROVENANCE_1','runnerSha256':sha(Path(__file__).read_bytes()),'helpers':[{'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}for p in helpers],'combinedFixtureSourceSha256':sha(helper_source.encode()),'candidateSha256':args.sha,'baselineSha256':base_sha,'candidateMode':args.mode,'actualOldFixtureSelection':old_selected,'originalBAssertionsAndHelpersChanged':False,'naturalRfOrWeaponEvidence':False}
 save(args.out/'PROVENANCE.json',provenance)
 from playwright.sync_api import sync_playwright
 with slots.heavy_browser_slot()as lease:
  for label,enabled,file,pin in products:
   assert sha(file.read_bytes())==pin
   raw=h.base.build(file=str(file.relative_to(R)),record=False,extra=helper_source+'\n'+support.PASSIVE_HELPER);server,url=h.serve(raw)
   try:
    with sync_playwright()as pw:
     browser=h.launch(pw)
     try:
      page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=errors);page.set_default_timeout(600000)
      initial=page.evaluate('__TRACK_B__.snapshot()');assert initial['enabled']is False,'Diagnostics must default OFF';assert initial['mode']=='ACTIVE','Original B ACTIVE contract must remain live'
      if label!='baseline':assert initial['stabilizationMode']==args.mode,'Wrong stabilization build mode'
      page.evaluate('on=>{__TRACK_A__.configure({enabled:on,capacity:4096});__TRACK_A__.clear();__TRACK_B__.configure({enabled:on,capacity:4096});__TRACK_B__.clear()}',enabled)
      old=page.evaluate('selected=>__TRACK_B_NATIVE_INTEGRATION__.run(selected)',old_selected)
      old_raw=packed(args.out/(label+'-old-native-raw-before-aux.json.gz'),old)
      new=page.evaluate('__TRACK_B_STABILIZATION_NATIVE__.run()')
      new_raw=packed(args.out/(label+'-new-native-raw-before-aux.json.gz'),new)
      metadata=page.evaluate('__TRACK_B_STABILIZATION_METADATA__.run()')
      metadata_raw=packed(args.out/(label+'-metadata-native-raw-before-aux.json.gz'),metadata)
      old_states={k:sha(v.encode())for k,v in old.pop('afterActionStateByFixture').items()};new_states={k:sha(v.encode())for k,v in new.pop('afterActionStateByFixture').items()}
      before=page.evaluate('__TRACK_B_STABILIZATION_NATIVE__.state()');first=page.evaluate('__TRACK_B__.snapshot()');second=page.evaluate('__TRACK_B__.snapshot()');env=page.evaluate('__ENV_D__.status()');after=page.evaluate('__TRACK_B_STABILIZATION_NATIVE__.state()')
      old_mode=first.get('stabilizationMode');page.evaluate("__TRACK_B__.configure({mode:'SHADOW',stabilizationMode:'ACTIVE',active:false})");control=page.evaluate('__TRACK_B__.snapshot()')
      row={'label':label,'trace':enabled,'candidateMode':args.mode,'product':file.name,'productSha256':pin,'fixtureSourceSha256':provenance['combinedFixtureSourceSha256'],'oldRaw':old_raw,'newRaw':new_raw,'oldNative':old,'newNative':new,'metadataNative':metadata,'metadataRaw':metadata_raw,'oldPerFixtureFullPassiveSha256':old_states,'newPerFixtureFullPassiveSha256':new_states,'queryStateSha256':sha(before.encode()),'checks':{'diagnosticQueryPure':before==after,'snapshotStable':first==second,'buildModeCannotBeChangedByConfigure':control.get('stabilizationMode')==old_mode and control['mode']==first['mode'],'envStatusMatch':env['match']is True,'oldNativeAssertionsPass':old['pass']is True,'runtimePreconditionErrorsZero':not old['errors']and not new['errors']and not metadata['errors'],'coreSelftestsZero':not page.evaluate('__CORE_SELFTEST_FAILURES__')},'initialDiagnosticDefaults':initial,'envStatus':env,'traceB':first,'lease':lease}
      rows.append(row);save(args.out/(label+'.json'),row);print(label,'old',sum(old['checks'].values()),'/',len(old['checks']),'new',sum(new['checks'].values()),'/',len(new['checks']),'fixtureErrors',len(new['errors']),flush=True)
     finally:browser.close()
   finally:server.shutdown()
   assert sha(file.read_bytes())==pin
 baseline,off,on=rows;new_native_exact=off['newNative']['records']==on['newNative']['records'];trace_pairs={'oldNativeRecordsExact':off['oldNative']['records']==on['oldNative']['records'],'newNativeRecordsExact':new_native_exact,'oldPerFixtureFullPassiveStateExact':off['oldPerFixtureFullPassiveSha256']==on['oldPerFixtureFullPassiveSha256'],'newPerFixtureFullPassiveStateExact':off['newPerFixtureFullPassiveSha256']==on['newPerFixtureFullPassiveSha256'],'postAllFixturesFullPassiveStateExact':off['queryStateSha256']==on['queryStateSha256']}
 shadow_control={'oldNativeRecordsExact':baseline['oldNative']['records']==off['oldNative']['records']==on['oldNative']['records'],'oldPerFixtureFullPassiveStateExact':baseline['oldPerFixtureFullPassiveSha256']==off['oldPerFixtureFullPassiveSha256']==on['oldPerFixtureFullPassiveSha256'],'newPerFixtureFullPassiveStateExact':baseline['newPerFixtureFullPassiveSha256']==off['newPerFixtureFullPassiveSha256']==on['newPerFixtureFullPassiveSha256'],'postAllFixturesFullPassiveStateExact':baseline['queryStateSha256']==off['queryStateSha256']==on['queryStateSha256']}
 trace_by=on['newNative']['traceByFixture'];positive_names=['covarianceAgreesWithNativeWinner','npcCovarianceEvidenceAndOwnerIsolation'];proposal={name:[r for r in trace_by.get(name,[])if r.get('decision')=='COMPONENT'and r.get('evidenceResolved')is True]for name in positive_names}
 checks={'allThreePagesComplete':len(rows)==3,'allQueryApiEnvOriginalNativeChecksPass':all(all(r['checks'].values())for r in rows),'traceOffOnExact':all(trace_pairs.values()),'browserErrorsZero':not errors,'actualNativeMetadataContractsPass':off['metadataNative']['pass']is True and on['metadataNative']['pass']is True,'actualNativeMetadataOffOnExact':off['metadataNative']==on['metadataNative']}
 if args.mode=='SHADOW':checks.update({'shadowActualNativeStateExactFrozenB':all(shadow_control.values()),'bothPositiveProposalsActuallyTraced':all(proposal.values())})
 else:
  checks['newActualNativeAssertionsPass']=off['newNative']['pass']is True and on['newNative']['pass']is True
 value={'schema':'AEGIS_TRACK_B_STABLE_NATIVE_RUN_1','status':'PASS'if all(checks.values())else'FAIL','allTasksComplete':True,'candidateSha256':args.sha,'candidateMode':args.mode,'baselineSha256':base_sha,'classification':'DIRECT_NATIVE_ANONYMOUS_INGRESS_NOT_NATURAL_RF','checks':checks,'shadowBehaviorControl':shadow_control,'traceOffOn':trace_pairs,'actualPositiveProposalRecords':proposal,'rawNewPolicyFailuresRetained':{r['label']:[k for k,v in r['newNative']['checks'].items()if not v]for r in rows},'browserErrors':errors,'wallS':time.perf_counter()-started,'performanceApproved':False,'releaseApproved':False}
 save(args.out/'SUMMARY.json',value);print(json.dumps(value,indent=2));return 0 if value['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())
