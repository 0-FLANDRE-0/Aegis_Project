"""Plan/preflight by default. --run --root-go permits ONE A/DDG historical raid pilot.

Original files/products are read-only. The old paired120 helper is reused in a
test copy with one read-only checkpoint accessor. No browser without both flags.
"""
from pathlib import Path
import argparse,ast,base64,difflib,gzip,hashlib,importlib.util,json,os,re,subprocess,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3];B=P.parent/'B';REV='5718f2d25f2e069f9ebd7948360fcf468bcdbb0b'
A=R/'Aegis_SIM_v48_WIP_TRACK_A.html';A_SHA='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a';SHIP='DDG_119_LATE_FLIGHT_IIA'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git_bytes(p):return subprocess.check_output(['git','show',REV+':'+str(p)],cwd=R)
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def write(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def prepare():
 source_path='docs/multiship/H4/regression_baseline.py';source=git_bytes(source_path)
 values=[n.value for n in ast.walk(ast.parse(source))if isinstance(n,ast.Constant)and isinstance(n.value,str)and n.value.startswith('scenario=>')];assert len(values)==1
 original=values[0];needle='dynamics:d.shipDynamics(),rng:';assert original.count(needle)==1
 effective=original.replace(needle,'dynamics:d.shipDynamics(),observers:d.observerSnapshotC(),offboard:d.offboardSnapshotC(),rng:',1)
 assert sha(effective.encode())=='3b54ea341abd67143df73dbc91aff1cd154d9f16a4958a6a9e5630b778b32d04'
 assert effective.count('raid:1920')==1 and effective.count('d.runFramesToTicks(60,scale,ticks)')==1
 pilot=effective.replace('raid:1920','raid:36000',1).replace('d.runFramesToTicks(60,scale,ticks)','window.__ORIGINAL_RAID_PILOT__.runFramesToTicks(60,scale,ticks,fixture)',1)
 helper_path='docs/contact/track/B/paired_cause_120.js';helper_raw=git_bytes(helper_path);assert sha(helper_raw)=='057c658dc4c7df790f5cddfefd09881ca678720c416e8d4220615b0919f2d069'
 helper=helper_raw.decode();anchor='  stop(){armed=false;return '
 assert helper.count(anchor)==1
 helper_copy=helper.replace(anchor,'  checkpoint(step){return rows.find(r=>r.step===step)??null;},\n'+anchor,1)
 old_raw=git_bytes('docs/contact/track/B/evidence/paired-cause-120/baseline-'+SHIP+'.json.gz');old=json.loads(gzip.decompress(old_raw))
 checkpoints={str(t):next(r for r in old['rows']if r['step']==t)for t in [1920,7200]}
 assert old['step']==7200 and not old['faults']
 archive_receipt=json.loads(git_bytes('docs/contact/track/B/evidence/paired-cause-120/baseline-'+SHIP+'-SUMMARY.json'))
 assert all(archive_receipt['checkpoint32Checks'].values()) and archive_receipt['all32ChecksExact']
 assert archive_receipt['sourceProofHashes']['baseSource']=='a4360bd84ee5401aedfca45439dd0ff78a266101948433a006906b5eb72ad5b1'
 support_pins={p:sha(git_bytes(p))for p in ['docs/contact/track/B/paired_cause.py','docs/bunkerhill/K/browser_i.py','docs/gun/B2/phase1b/test_support/sitecustomize.py']}
 for p,pinned in support_pins.items():assert sha((R/p).read_bytes())==pinned,('SUPPORT_FILE_CHANGED',p)
 assert sha(A.read_bytes())==A_SHA,'TRACK_A_PRODUCT_PIN_MISMATCH'
 own_js=(P/'original_raid_pilot.js').read_bytes();combined=helper_copy+'\n'+own_js.decode()
 metadata={'schema':'AEGIS_ORIGINAL_RAID_PILOT_PLAN_1','status':'PREPARED_NOT_EXECUTED','revision':REV,'productSha256':A_SHA,'ship':SHIP,'runs':1,'seed':0x6d2b79f5,'fps':60,'timeScale':8,'horizonS':600,'maximumNativeTicks':36001,'extra600sTickPolicy':'EXACTLY_ONE_NATIVE_STEP_AFTER_36000_ONLY; MAX_LIFE_IS_NOT_KILL','earlyStop':'INITIAL_8_NATIVE_TERMINAL_OR_NATIVE_OWN_SHIP_LOST_THEN_5S; OBSERVED_AT_NATIVE_FRAME_BOUNDARIES','rawCheckpointSteps':[1920,7200],'rawCheckpointMatchRequired':True,'checkpointMismatchAction':'BLOCKED_STOP_BEFORE_LONG_HORIZON','originalFile':source_path,'originalFileSha256':sha(source),'originalExpressionSha256':sha(original.encode()),'pairedEffectiveExpressionSha256':sha(effective.encode()),'pilotExpressionSha256':sha(pilot.encode()),'historicalRawArchiveSha256':sha(old_raw),'oldHelperSha256':sha(helper_raw),'testCopyCheckpointAccessorHelperSha256':sha(helper_copy.encode()),'newHelperSha256':sha(own_js),'combinedHelperSha256':sha(combined.encode()),'runnerSha256':sha(Path(__file__).read_bytes()),'supportPins':support_pins,'newTestNotOldRegression':True,'releaseApproved':False,'estimatedWallS':344.362,'estimateLimits':'120s four-page historical wall275.490 /4 *5; background accumulation can increase cost; provisional 5-10 minutes; no automatic B/CG follow-up'}
 metadata['historical32BridgeChecks']=archive_receipt['checkpoint32Checks']
 metadata['rawCheckpointExpectedJsonSha256']={t:sha(json.dumps(row,sort_keys=True,separators=(',',':')).encode())for t,row in checkpoints.items()}
 return metadata,effective,pilot,helper,helper_copy,combined,checkpoints
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true');parser.add_argument('--root-go',action='store_true');parser.add_argument('--out',type=Path,default=P/'evidence/original-raid-pilot');a=parser.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 try:plan,effective,pilot,helper,helper_copy,combined,checkpoints=prepare()
 except Exception as e:write(a.out/'PLAN.json',{'status':'BLOCKED_PREFLIGHT','error':str(e),'browserRuns':0});raise
 write(a.out/'PLAN.json',plan);(a.out/'expression.diff').write_text(''.join(difflib.unified_diff(effective.splitlines(True),pilot.splitlines(True),fromfile='historical-effective-expression',tofile='pilot-expression')));(a.out/'helper-accessor.diff').write_text(''.join(difflib.unified_diff(helper.splitlines(True),helper_copy.splitlines(True),fromfile='original-paired120-helper',tofile='test-copy-checkpoint-accessor')))
 if not(a.run and a.root_go):print(json.dumps({**plan,'browserRuns':0}));return 0
 assert os.environ.get('B2_PHASE1_REGRESSION')=='1','BLOCKED: use original B2 regression support environment'
 site=sys.modules.get('sitecustomize');assert site and Path(site.__file__).resolve()==(R/'docs/gun/B2/phase1b/test_support/sitecustomize.py').resolve(),'BLOCKED: original sitecustomize is not installed'
 base=module('original_raid_pilot_support',B/'paired_cause.py')
 class InlineHelper:
  def read_text(self):return combined
 base.HELPER=InlineHelper();body,instrumentation=base.instrument(A.read_bytes())
 assert instrumentation['sourceSha256']=='8d2de4f64cb18e3248156e36fa454daee91b5603e03fee5a8f7bd372e0d5780e'
 assert instrumentation['nativeFixedTickBodyUnchanged'] and instrumentation['existingNativeWrapperUnchanged']
 sys.path.insert(0,str(R/'docs/bunkerhill/K'));from browser_i import launch,load
 from playwright.sync_api import sync_playwright
 slots=module('original_raid_pilot_slots',B/'regression_runner.py');errors=[];started=time.perf_counter();browser=None;page=None;captured=None;result=None;ready=None
 print(json.dumps({'status':'WAITING_SHARED_BROWSER_LEASE','pid':os.getpid(),'runs':1,'maxSeconds':600,'extraLifetimeTick':True}),flush=True)
 with slots.heavy_browser_slot()as lease:
  print(json.dumps({'status':'LEASE_ACQUIRED','pid':os.getpid(),'lease':lease}),flush=True)
  with sync_playwright()as pw:
   try:
    browser=launch(pw);page=load(browser,body,ship=SHIP,errors=errors);page.set_default_timeout(1800000)
    ready=page.evaluate('(checkpoints)=>__ORIGINAL_RAID_PILOT__.start({checkpoints})',checkpoints);proof=page.evaluate('__ORIGINAL_RAID_PILOT__.proof()');base_proof=page.evaluate('__TRACK_B_PAIRED_CAUSE_120__.proof()');proof_hash={k:sha(v.encode())if v else None for k,v in proof.items()}
    assert proof_hash['pipeline']==instrumentation['nativePipelineWrapperSha256']
    assert sha(base_proof['baseSource'].encode())==instrumentation['nativeFixedTickSha256']
    result=page.evaluate(pilot,'raid');captured=page.evaluate('__ORIGINAL_RAID_PILOT__.stop()');env=page.evaluate('async()=>await __ENV_D__.status()')
    raw=json.dumps(captured,separators=(',',':')).encode();assert len(raw)<=10*1024*1024,('PASSIVE_RECORD_BUDGET_EXCEEDED',len(raw))
    (a.out/'track-a-DDG-original-raid.json.gz').write_bytes(gzip.compress(raw,6,mtime=0));write(a.out/'original-expression-result.json',result);write(a.out/'env-status.json',env)
    checkpoint_exact={str(t):next((r['fullRawExact']for r in captured['checkpoints']if r['step']==t),False)for t in [1920,7200]}
    status='BLOCKED_SOURCE_OR_CHECKPOINT'if captured['gateFailure']or not all(checkpoint_exact.values())or env.get('match')is not True else'OBSERVED_FOR_REVIEW_NOT_APPROVED'
    summary={'schema':'AEGIS_ORIGINAL_RAID_PILOT_RESULT_1','status':status,'plan':plan,'ready':ready,'instrumentation':instrumentation,'nativeSourceHashes':proof_hash,'rawCheckpointExact':checkpoint_exact,'originalRun':result['run'],'endStep':captured['step'],'initial':captured['initial'],'laterSpawnCount':len(captured['later']),'initialNativeTerminal':sum(t['alive']is False and t['nativeRetirement']is not None for t in captured['initial']),'gateFailure':captured['gateFailure'],'faults':captured['faults']+captured['base']['faults'],'errors':errors,'restoredNativeRefs':captured['restoredNativeRefs'],'envStatus':env,'lease':lease,'recordBytes':len(raw),'wallS':time.perf_counter()-started,'releaseApproved':False,'expectedValuesChanged':False,'limitation':'ONE A/DDG pilot; B/DDG and A/B CG comparison still required; native MAX_LIFE/TIMEOUT is not kill'}
    write(a.out/'SUMMARY.json',summary);print(json.dumps({'status':status,'wallS':summary['wallS'],'rawCheckpointExact':checkpoint_exact,'end':result['run'],'initialNativeTerminal':summary['initialNativeTerminal'],'releaseApproved':False}),flush=True)
    assert not errors and not summary['faults'] and all(captured['restoredNativeRefs'].values())
    assert status!='BLOCKED_SOURCE_OR_CHECKPOINT',summary['gateFailure']
   except Exception as e:
    if page and ready and captured is None:
     try:
      captured=page.evaluate('__ORIGINAL_RAID_PILOT__.stop()');raw=json.dumps(captured,separators=(',',':')).encode();(a.out/'partial-attempt-record.json.gz').write_bytes(gzip.compress(raw,6,mtime=0))
     except Exception as capture_error:write(a.out/'PARTIAL_CAPTURE_ERROR.json',{'error':str(capture_error)})
    write(a.out/'ATTEMPT_ERROR.json',{'error':str(e),'errors':errors,'wallS':time.perf_counter()-started,'productChanged':sha(A.read_bytes())!=A_SHA,'browserRuns':1,'approval':False});raise
   finally:
    if page:
     try:page.context.close()
     except Exception:pass
    if browser:
     try:browser.close()
     except Exception:pass
 assert sha(A.read_bytes())==A_SHA
 return 0
if __name__=='__main__':raise SystemExit(main())
