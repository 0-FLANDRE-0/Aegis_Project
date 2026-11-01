"""Execute anonymous fixtures through actual baseline/shadow/active game functions.

No sensor, NIS, assignment, EKF, or damage function is replaced. This runner is
not natural RF evidence. New B assertions may fail on A; those observations do
not change any existing regression expectation.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,importlib.util,json,re,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3]
sha=lambda value:hashlib.sha256(value).hexdigest()
BASE=R/'Aegis_SIM_v48_WIP_TRACK_A.html'
BASE_SHA='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'

def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def c55_access_test_copy(raw):
 """Same accessor insertion in all three TEST copies; no association replacement."""
 text=raw.decode();packed=re.search(r'data-c55-index="13">([^<]+)</script>',text);source=gzip.decompress(base64.b64decode(packed[1])).decode()
 anchor='return {localDefenseGuardProbeH4A,';assert source.count(anchor)==1,'NPC C55 test accessor anchor not unique'
 extra="return {__trackBTestC55:{mounts:()=>ciws,bank:c55Bank,sweep:(m,b,dt)=>{sync();return c55SensorSweep(m,b,dt);},associateCms:c55AssociateCms,passiveState:()=>({clockS:CIWS_C55.clockS,serial:CIWS_C55.serial,stats:{...CIWS_C55.stats},banks:[...CIWS_C55.banks].map(([id,b])=>({id,rng:b.rng,winner:b.winner,status:b.status,reason:b.reason}))}),swapMeasurement(fn){const original=ciwsLocalMeasurement;ciwsLocalMeasurement=fn;return()=>{ciwsLocalMeasurement=original;};}},localDefenseGuardProbeH4A,"
 source=source.replace(anchor,extra,1);encoded=base64.b64encode(gzip.compress(source.encode(),9,mtime=0)).decode();text=text[:packed.start(1)]+encoded+text[packed.end(1):]
 metadata=re.search(r'const records=(\[.*?\]);',text,re.S);records=json.loads(metadata[1]);records[13].update(rawBytes=len(source.encode()),gzipBytes=len(base64.b64decode(encoded)),sha256=sha(source.encode()))
 return(text[:metadata.start(1)]+json.dumps(records,separators=(',',':'))+text[metadata.end(1):]).encode()

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B.html');parser.add_argument('--candidate-sha',required=True)
 parser.add_argument('--shadow',type=Path,required=True);parser.add_argument('--shadow-sha',required=True)
 parser.add_argument('--out',type=Path,default=P/'evidence/native-integration');parser.add_argument('--only',default=None)
 args=parser.parse_args();args.candidate=args.candidate.resolve();args.shadow=args.shadow.resolve();args.out.mkdir(parents=True,exist_ok=True)
 products=[('baseline',False,BASE,BASE_SHA),('shadow',False,args.shadow,args.shadow_sha),('shadow',True,args.shadow,args.shadow_sha),('active',False,args.candidate,args.candidate_sha),('active',True,args.candidate,args.candidate_sha)]
 for label,trace,file,pinned in products:assert sha(file.read_bytes())==pinned,(label,'HTML SHA mismatch')
 helpers=[P/'test_support/native_support.js',P/'test_support/native_c55.js',P/'test_support/native_integration.js'];helper_source='\n'.join(path.read_text()for path in helpers)
 a=load_module('track_b_reused_runtime_support',P.parent/'A/verify_runtime.py')
 slots=load_module('track_b_shared_browser_slots',P/'regression_runner.py')
 h=a.load_harness();rows=[];browser_errors=[];start=time.perf_counter()
 from playwright.sync_api import sync_playwright
 for label,trace,file,pinned in products:
  with slots.heavy_browser_slot()as slot:
   # The existing test harness adds access/recording helpers; record=False.
   # The actual packed product functions remain the source of all decisions.
   raw=c55_access_test_copy(h.base.build(file=str(file.relative_to(R)),record=False,extra=helper_source+'\n'+a.PASSIVE_HELPER))
   server,url=h.serve(raw)
   try:
    with sync_playwright()as pw:
     browser=h.launch(pw);page=h.load_fast_http(browser,url,own='CG_52_LATE_TICONDEROGA',errors=browser_errors);page.set_default_timeout(600000)
     initial=page.evaluate('({b:window.__TRACK_B__?__TRACK_B__.snapshot():null,a:__TRACK_A__.snapshot(),env:__ENV_D__.status()})')
     if label!='baseline':
      assert initial['b']is not None and initial['b']['enabled']is False,'B diagnostics must default OFF'
      assert initial['b']['mode']==('SHADOW'if label=='shadow'else'ACTIVE'),'Wrong build-time mode'
      page.evaluate('enabled=>{__TRACK_B__.configure({enabled,capacity:4096});__TRACK_B__.clear()}',trace)
     selected=args.only.split(',')if args.only else None
     result=page.evaluate('selected=>__TRACK_B_NATIVE_INTEGRATION__.run(selected)',selected)
     per_fixture_state={name:sha(value.encode())for name,value in result.pop('afterActionStateByFixture').items()}
     state_before=page.evaluate('__TRACK_RUNTIME_A__.state()');snap1=page.evaluate('window.__TRACK_B__?__TRACK_B__.snapshot():null');snap2=page.evaluate('window.__TRACK_B__?__TRACK_B__.snapshot():null');state_after=page.evaluate('__TRACK_RUNTIME_A__.state()');env=page.evaluate('__ENV_D__.status()')
     assert state_before==state_after,'Diagnostic query changed native game/private RNG state'
     assert snap1==snap2,'Repeated diagnostic snapshot changed output'
     assert env['match']is True,'Protected ENV profile/function hashes no longer match'
     failed_checks=[name for name,value in result['checks'].items()if not value]
     row={'label':label,'trace':trace,'product':str(file.relative_to(R)),'productSha256':pinned,'fixtureSourceSha256':sha(helper_source.encode()),'helpers':[{'path':str(path.relative_to(R)),'sha256':sha(path.read_bytes())}for path in helpers],'classification':'DIRECT_NATIVE_ANONYMOUS_INGRESS_NOT_NATURAL_RF','naturalRfOrWeaponEvidence':False,'initialDiagnosticDefaults':initial,'nativeResult':result,'policyAssertionFailures':[name for name in failed_checks if not name.endswith('.completed')],'fixturePreconditionOrRuntimeFailures':[name for name in failed_checks if name.endswith('.completed')],'traceB':snap1,'queryGameStateUnchanged':True,'querySnapshotStable':True,'perFixturePassiveFullStateSha256':per_fixture_state,'postFixtureStateSha256':sha(state_before.encode()),'envMatch':env['match'],'browserSlot':slot}
     rows.append(row);(args.out/(label+('-on'if trace else'-off')+'.json')).write_text(json.dumps(row,separators=(',',':'))+'\n')
     if trace or label=='baseline':(args.out/(label+'.json')).write_text(json.dumps(row,separators=(',',':'))+'\n')
     page.context.close();browser.close();print(label,'trace',trace,sum(result['checks'].values()),'/',len(result['checks']),'errors',len(result['errors']),'failed',failed_checks,round(time.perf_counter()-start,2),flush=True)
   finally:server.shutdown()
  assert sha(file.read_bytes())==pinned,'Product changed during fixture execution'
 # Baseline result is an observation, not a retroactively edited B expectation.
 active=rows[-1]['nativeResult'];a_records=rows[0]['nativeResult']['records'];s_records=rows[1]['nativeResult']['records']
 shadow_equal=a_records==s_records==rows[2]['nativeResult']['records']
 trace_pairs=[]
 for label in ['shadow','active']:
  off,on=[row for row in rows if row['label']==label]
  trace_pairs.append({'label':label,'nativeFixtureRecordsExact':off['nativeResult']['records']==on['nativeResult']['records'],'perFixtureGameAndPrivateRngSha256Exact':off['perFixturePassiveFullStateSha256']==on['perFixturePassiveFullStateSha256'],'differingPassiveStateFixtures':[name for name,value in off['perFixturePassiveFullStateSha256'].items()if value!=on['perFixturePassiveFullStateSha256'].get(name)],'postAllFixturesStateExact':off['postFixtureStateSha256']==on['postFixtureStateSha256'],'fixtureCount':len(off['perFixturePassiveFullStateSha256'])})
 trace_exact=all(row['nativeFixtureRecordsExact']and row['perFixtureGameAndPrivateRngSha256Exact']and row['postAllFixturesStateExact']for row in trace_pairs)
 changed=[{'check':key,'baseline':rows[0]['nativeResult']['checks'].get(key),'shadow':rows[1]['nativeResult']['checks'].get(key),'active':value}for key,value in active['checks'].items()if value!=rows[0]['nativeResult']['checks'].get(key)]
 summary={'schema':'AEGIS_TRACK_B_NATIVE_INTEGRATION_RUN_1','status':'PASS'if active['pass']and rows[-2]['nativeResult']['pass']and shadow_equal and trace_exact and not browser_errors else'FAIL','candidateSha256':args.candidate_sha,'shadowSha256':args.shadow_sha,'baselineSha256':BASE_SHA,'classification':'DIRECT_NATIVE_ANONYMOUS_INGRESS_NOT_NATURAL_RF','naturalRfOrWeaponEvidence':False,'existingExpectationsChanged':False,'countsNotAddedToExistingDomain420':True,'activeChecks':{'count':len(active['checks']),'passed':sum(active['checks'].values()),'errors':active['errors']},'shadowOriginalNativeRecordsExact':shadow_equal,'traceOnOff':trace_pairs,'changedContractAssertions':changed,'browserErrors':browser_errors,'records':[{'label':r['label'],'trace':r['trace'],'productSha256':r['productSha256'],'fixtureSourceSha256':r['fixtureSourceSha256'],'postFixtureStateSha256':r['postFixtureStateSha256']}for r in rows],'wallS':time.perf_counter()-start,'releaseApproved':False}
 (args.out/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));return 0 if summary['status']=='PASS'else 1

if __name__=='__main__':raise SystemExit(main())
