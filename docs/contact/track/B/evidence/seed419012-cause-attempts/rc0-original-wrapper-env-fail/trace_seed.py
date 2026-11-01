"""Seed419012 causal observation only. Default plan; --run needs root browser GO.

Runs ONE unchanged original D1 fixture on each pinned A/B product, with pass-through
watches around already-generated diagnostic records. Does not patch products,
expectations, RF/NIS/EKF, or caches. All raw differences remain unapproved.
"""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,os,sys,time,traceback

P=Path(__file__).resolve().parent;R=P.parents[3];A=P.parent/'A';F=R/'docs/contact/friendly/A'
REFERENCE=R/'Aegis_SIM_v48_WIP_TRACK_A.html';REFERENCE_SHA='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
CANDIDATE=R/'Aegis_SIM_v48_WIP_TRACK_B.html';CANDIDATE_SHA='0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6'
HELPER=P/'trace_seed_passive.js';ORIGINAL=R/'docs/ciws/dmg/A/diagnostic.js'
SEED=419012;CASE={'ship':'DDG_119_LATE_FLIGHT_IIA','bearing':90,'seed':SEED}
sha=lambda b:hashlib.sha256(b).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def file_receipt(path):
 h=hashlib.sha256()
 with path.open('rb')as source:
  for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
 return {'path':str(path.relative_to(R)),'sha256':h.hexdigest(),'bytes':path.stat().st_size}

def selected_row(path):
 if not path.exists():path=Path(str(path)+'.gz')
 with(gzip.open(path,'rt')if path.suffix=='.gz'else path.open())as source:
  for line in source:
   row=json.loads(line)
   if row['case']['seed']==SEED:return row,file_receipt(path)
 raise AssertionError('Missing fixed seed in OFF reference '+str(path))

def diff(a,b,path=''):
 if type(a)is not type(b):yield {'path':path,'before':a,'after':b};return
 if isinstance(a,dict):
  for key in sorted(set(a)|set(b)):
   if key not in a or key not in b:yield {'path':path+'/'+key,'beforePresent':key in a,'afterPresent':key in b,'before':a.get(key),'after':b.get(key)}
   else:yield from diff(a[key],b[key],path+'/'+key)
 elif isinstance(a,list):
  if len(a)!=len(b):yield {'path':path+'/~length','before':len(a),'after':len(b)}
  for i in range(min(len(a),len(b))):yield from diff(a[i],b[i],path+'/'+str(i))
 elif a!=b:yield {'path':path,'before':a,'after':b}

def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def gz(path,value):
 data=json.dumps(value,separators=(',',':')).encode();path.write_bytes(gzip.compress(data,6,mtime=0));return {'path':path.name,'rawSha256':sha(data),'gzipSha256':sha(path.read_bytes()),'rawBytes':len(data)}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true');parser.add_argument('--root-go',action='store_true');parser.add_argument('--out',type=Path,default=P/'evidence/seed419012-cause');args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 references={'baseline':selected_row(A/'evidence/candidate/friendly/ciws-d1.jsonl'),'active':selected_row(P/'evidence/runtime/active/friendly/ciws-d1.jsonl')}
 products=[('baseline',REFERENCE,REFERENCE_SHA),('active',CANDIDATE,CANDIDATE_SHA)]
 files=[file_receipt(path)for path in [Path(__file__),HELPER,ORIGINAL,F/'ciws.py',F/'harness.py',P/'regression_runner.py',A/'verify_runtime.py']]
 plan={'schema':'AEGIS_TRACK_B_SEED_CAUSE_PLAN_1','status':'RUN_REQUESTED'if args.run else'PLAN_ONLY_NO_BROWSER','seed':SEED,'case':CASE,'runs':2,'originalRunExpression':'c=>__CIWS_DMG_A__.run(c,true)','fixtureChanged':False,'expectationsChanged':False,'windowS':[29,30.65],'diagnosticByteBoundPerRun':8*1024*1024,'passThroughNativeEventWatchOnly':True,'nativeNisOrRfReevaluation':False,'cacheOrGeometryCapture':False,'products':[{'label':label,**file_receipt(file),'requiredSha256':pinned}for label,file,pinned in products],'referenceRows':{label:{'signatureSha256':row['signatureSha256'],'source':receipt}for label,(row,receipt)in references.items()},'files':files,'rootBrowserGoRequired':True,'automaticApproval':False,'releaseApproved':False}
 write(args.out/'PLAN.json',plan)
 if not args.run:print(json.dumps({'status':'READY_NOT_EXECUTED','plan':str(args.out/'PLAN.json'),'browserStarted':False}));return 0
 assert args.root_go,'Root browser GO required; default plan does not acquire any browser slot'
 for label,file,pinned in products:assert sha(file.read_bytes())==pinned,(label,'Frozen HTML changed')
 support=module('seed_trace_original_support',A/'verify_runtime.py');runtime=module('seed_trace_current_difference_support',P/'verify_runtime.py');slots=module('seed_trace_shared_browser_lease',P/'regression_runner.py');h=support.load_harness()
 from playwright.sync_api import sync_playwright
 rows=[];errors=[];started=time.perf_counter()
 with slots.heavy_browser_slot()as lease:
  for label,file,pinned in products:
   extra=ORIGINAL.read_text()+'\n'+support.PASSIVE_HELPER+'\n'+HELPER.read_text();raw=h.base.build(file=file.name,record=False,extra=extra);server,url=h.serve(raw)
   try:
    with sync_playwright()as pw:
     browser=h.launch(pw);page=h.load_fast_http(browser,url,own=CASE['ship'],errors=errors);page.set_default_timeout(600000)
     initial=page.evaluate('({a:__TRACK_A__.snapshot(),b:window.__TRACK_B__?__TRACK_B__.snapshot():null})')
     page.evaluate('()=>{__TRACK_A__.configure({enabled:true,capacity:4096});__TRACK_A__.clear();if(window.__TRACK_B__){__TRACK_B__.configure({enabled:true,capacity:4096});__TRACK_B__.clear();}}')
     ready=page.evaluate('__TRACK_B_SEED_TRACE__.start()');preflight=page.evaluate('__TRACK_B_SEED_TRACE__.info()');sources=preflight.pop('nativeSources');source_proof={name:sha(text.encode())if text is not None else None for name,text in sources.items()}
     result=page.evaluate('c=>__CIWS_DMG_A__.run(c,true)',CASE);signature=result.pop('equivalenceSignature');actual_signature=sha(signature.encode());trace_info=page.evaluate('__TRACK_B_SEED_TRACE__.stop()');trace=[]
     for start in range(0,trace_info['count'],120):trace.extend(page.evaluate('a=>__TRACK_B_SEED_TRACE__.read(a.start,a.count)',{'start':start,'count':120}))
     runtime.privacy(trace);trace_raw=gz(args.out/(label+'-diagnostics.json.gz'),{'schema':'AEGIS_TRACK_B_SEED_CAUSE_DIAGNOSTICS_1','classification':'OBSERVED_ESTIMATES_NOT_TRUTH','records':trace,'info':trace_info})
     before=page.evaluate('__TRACK_RUNTIME_A__.state()');one=page.evaluate('__TRACK_B_SEED_TRACE__.info()');read_one=page.evaluate('__TRACK_B_SEED_TRACE__.read(0,8)');two=page.evaluate('__TRACK_B_SEED_TRACE__.info()');read_two=page.evaluate('__TRACK_B_SEED_TRACE__.read(0,8)');after=page.evaluate('__TRACK_RUNTIME_A__.state()');env=page.evaluate('async()=>await __ENV_D__.status()')
     ref,receipt=references[label];actual={'case':{'seed':SEED},'signatureSha256':actual_signature,**result};raw_result=gz(args.out/(label+'-original-result-after-action.json.gz'),{'classification':'AFTER_ACTION_ORIGINAL_FIXTURE_OUTPUT_NOT_SENSOR_INPUT','row':actual})
     changed=0
     with gzip.open(args.out/(label+'-all-reference-differences.jsonl.gz'),'wt')as output:
      for value in diff(ref,actual):output.write(json.dumps(value,separators=(',',':'))+'\n');changed+=1
     checks={'exactOriginalOffSignature':actual_signature==ref['signatureSha256'],'traceNoFaults':not trace_info['faults'],'traceBelowTenMB':trace_raw['rawBytes']<10*1024*1024,'traceNotOverflowed':not trace_info['overflow'],'forbiddenDiagnosticFieldsAbsent':True,'queryGameAndPrivateStateUnchanged':before==after,'querySnapshotRepeatedExact':one==two and read_one==read_two,'envHashMatch':env['match']is True,'coreSelftestFailuresZero':not result['after']['core']}
     row={'label':label,'productSha256':pinned,'instrumentedHtmlSha256':sha(raw),'helperSha256':sha(HELPER.read_bytes()),'originalDiagnosticSha256':sha(ORIGINAL.read_bytes()),'referenceReceipt':receipt,'referenceSignatureSha256':ref['signatureSha256'],'instrumentedSignatureSha256':actual_signature,'checks':checks,'status':'PASS'if all(checks.values())else'FAIL','allRawDifferenceCount':changed,'allRawDifferenceStream':label+'-all-reference-differences.jsonl.gz','diagnostics':trace_raw,'originalAfterActionOutput':raw_result,'nativePassThroughSourcesSha256':source_proof,'ready':ready,'traceInfo':trace_info,'queryBeforeAfterSha256':[sha(before.encode()),sha(after.encode())],'env':env,'browserSlot':lease,'automaticApproval':False,'releaseApproved':False};rows.append(row);write(args.out/(label+'-receipt.json'),row)
     page.context.close();browser.close();print(json.dumps({'label':label,'status':row['status'],'signatureExact':checks['exactOriginalOffSignature'],'traceRows':len(trace),'traceBytes':trace_raw['rawBytes'],'allRawDifferences':changed,'elapsedS':time.perf_counter()-started}),flush=True)
   finally:server.shutdown()
 summary={'schema':'AEGIS_TRACK_B_SEED_CAUSE_EXECUTION_1','status':'PASSIVE_TRACE_EQUIVALENCE_PASS'if len(rows)==2 and all(x['status']=='PASS'for x in rows)and not errors else'INCOMPLETE_OR_FAILED_TRACE_PROOF','case':CASE,'products':rows,'browserErrors':errors,'wallS':time.perf_counter()-started,'causalAnalysisPending':True,'originalStrictD1DeltaApproved':False,'automaticApproval':False,'expectedValuesUpdated':False,'releaseApproved':False};write(args.out/'EXECUTION.json',summary);return 0 if summary['status']=='PASSIVE_TRACE_EQUIVALENCE_PASS'else 1

if __name__=='__main__':raise SystemExit(main())
