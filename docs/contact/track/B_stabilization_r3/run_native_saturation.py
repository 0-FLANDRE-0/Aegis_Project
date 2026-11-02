"""Prepared native saturation boundary replay. No browser without --run."""
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
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_C.html');ap.add_argument('--sha',required=True);ap.add_argument('--shadow',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_C_SHADOW.html');ap.add_argument('--shadow-sha',required=True);ap.add_argument('--out',type=Path,default=P/'evidence/native-saturation');ap.add_argument('--run',action='store_true');args=ap.parse_args();r1_test_inputs=module('r2_frozen_native_inputs',P/'controller_pins.py').verify();args.candidate=args.candidate.resolve();args.shadow=args.shadow.resolve();args.out.mkdir(parents=True,exist_ok=True)
 base=R/'Aegis_SIM_v48_WIP_TRACK_B.html';base_sha=json.loads((P/'BASELINE_PINS.json').read_text())['files'][base.name];products=[('baseline',base,base_sha,'ORIGINAL_B_ACTIVE'),('shadow',args.shadow,args.shadow_sha,'SHADOW'),('active',args.candidate,args.sha,'ACTIVE')]
 for _,file,pin,_ in products:assert sha(file.read_bytes())==pin
 util=module('sat_native_original_unpacker',B/'build.py');source_locations=[]
 for label,file,pin,mode in products:
  main_source=util.unpack(file.read_bytes());entries=[]
  for name in ['observerAcceptPlotsC','trackSurfacePositionAssociationNisWip13B9','trackBSelectB','trackEkfUpdateSurfaceRadar2D']:
   a,b=util.scope_span(main_source,{'function':name});fragment=main_source[a:b];entries.append({'function':name,'startLine':main_source[:a].count('\n')+1,'scopedFragmentSha256':sha(fragment.encode()),'scopeMeaning':'Existing original packer function scope, including following non-function statements until next same-indent function.','gateLines':[line.strip()for line in fragment.splitlines()if 'gate' in line][:12]})
  source_locations.append({'product':label,'htmlSha256':pin,'packedMainIndex':13,'mainSha256':sha(main_source.encode()),'functions':entries})
 support=module('sat_native_original_a',A/'verify_runtime.py');slots=module('sat_native_original_slots',B/'regression_runner.py');helpers=[B/'test_support/native_support.js',P.parent/'B_stabilization/test_support/native_saturation.js'];source='\n'.join(p.read_text()for p in helpers)
 provenance={'schema':'AEGIS_TRACK_B_NATIVE_SATURATION_PROVENANCE_1','runnerSha256':sha(Path(__file__).read_bytes()),'moduleSha256':sha((P/'association.js').read_bytes()),'candidateSha256':args.sha,'shadowSha256':args.shadow_sha,'oldBReferenceSha256':base_sha,'actualSourceLocations':source_locations,'helpers':[{'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}for p in helpers],'combinedFixtureSha256':sha(source.encode()),'fixtureCases':['clear13','clear16','equal13'],'contexts':3,'maximumConcurrentBrowsers':1,'estimatedWallMinutes':1,'physicalRfGenerationEvidence':False,'existingCoefficientsOrExpectationsChanged':False}
 provenance['frozenR1NativeInputs']=r1_test_inputs;save(args.out/'PROVENANCE.json',provenance)
 if not args.run:print(json.dumps({'dryRun':True,'browserRuns':0,**provenance},indent=2));return 0
 from playwright.sync_api import sync_playwright
 h=support.load_harness();rows=[];errors=[];started=time.perf_counter()
 with slots.heavy_browser_slot()as lease:
  for label,file,pin,mode in products:
   raw=h.base.build(file=str(file.relative_to(R)),record=False,extra=source+'\n'+support.PASSIVE_HELPER);server,url=h.serve(raw)
   try:
    with sync_playwright()as pw:
     browser=h.launch(pw)
     try:
      page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=errors);page.set_default_timeout(600000);initial=page.evaluate('__TRACK_B__.snapshot()');assert initial['enabled']is False;assert initial.get('stabilizationMode','ORIGINAL_B_ACTIVE')==mode
      page.evaluate('__TRACK_B__.configure({enabled:true,capacity:4096});__TRACK_B__.clear()')
      result=page.evaluate('__TRACK_B_STABILIZATION_SATURATION__.run()');raw_proof=packed(args.out/(label+'-raw-before-aux.json.gz'),result);states={k:sha(v.encode())for k,v in result.pop('afterActionStateByFixture').items()};before=page.evaluate('__TRACK_B_STABILIZATION_SATURATION__.state()');one=page.evaluate('__TRACK_B__.snapshot()');two=page.evaluate('__TRACK_B__.snapshot()');env=page.evaluate('__ENV_D__.status()');after=page.evaluate('__TRACK_B_STABILIZATION_SATURATION__.state()')
      checks={'nativeFixtureAssertionsPass':result['pass']is True,'nativePreconditionsAndRuntimeErrorsZero':not result['errors'],'queryFullPrivateStatePure':before==after,'snapshotStable':one==two,'envStatusMatch':env['match']is True,'diagnosticErrorsZero':one['stats']['errors']==0,'coreSelftestsZero':not page.evaluate('__CORE_SELFTEST_FAILURES__')}
      row={'label':label,'mode':mode,'productSha256':pin,'rawResultBeforeAuxiliaryQueries':raw_proof,'nativeResult':result,'perFixtureFullPrivateStateSha256':states,'postFixtureFullPrivateStateSha256':sha(before.encode()),'checks':checks,'envStatus':env,'actualTrace':one,'lease':lease};rows.append(row);save(args.out/(label+'.json'),row);print(label,sum(result['checks'].values()),'/',len(result['checks']),'runtimeErrors',len(result['errors']),'controls',all(checks.values()),flush=True)
     finally:browser.close()
   finally:server.shutdown()
   assert sha(file.read_bytes())==pin
 baseline,shadow,active=rows;shadow_same=baseline['perFixtureFullPrivateStateSha256']==shadow['perFixtureFullPrivateStateSha256'];equal_same=baseline['perFixtureFullPrivateStateSha256']['equal13']==shadow['perFixtureFullPrivateStateSha256']['equal13']==active['perFixtureFullPrivateStateSha256']['equal13'];summary={'schema':'AEGIS_TRACK_B_NATIVE_SATURATION_RUN_1','status':'PASS'if all(all(r['checks'].values())for r in rows)and shadow_same and equal_same and not errors else'FAIL','allTasksComplete':True,'candidateSha256':args.sha,'shadowSha256':args.shadow_sha,'oldBReferenceSha256':base_sha,'moduleSha256':provenance['moduleSha256'],'shadowOriginalBFullPrivateStateExact':shadow_same,'equal13AllProductFullPrivateStateExact':equal_same,'rows':[{'label':r['label'],'passed':sum(r['nativeResult']['checks'].values()),'count':len(r['nativeResult']['checks']),'checks':r['checks'],'perFixtureCounts':{name:{'selected':len(v['coreCalls'][0]['selected']),'held':len(v['heldPlotIndices']),'corrections':len(v['corrections']),'births':v['statsAfter']['initiated']-v['statsBefore']['initiated']}for name,v in r['nativeResult']['records'].items()}}for r in rows],'browserErrors':errors,'wallS':time.perf_counter()-started,'naturalRfOrCombatEvidence':False,'existingCoefficientsOrExpectedValuesChanged':False,'releaseApproved':False,'performanceApproved':False};save(args.out/'SUMMARY.json',summary);print(json.dumps(summary,indent=2));return 0 if summary['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())
