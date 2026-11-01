"""Read-only assembly of actual TRACK-B runtime evidence; no result approvals."""
from pathlib import Path
import ast,hashlib,json

P=Path(__file__).resolve().parent;E=P/'evidence/runtime';sha=lambda raw:hashlib.sha256(raw).hexdigest()
read=lambda path:json.loads(path.read_text())
BASE='e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a'
ACTIVE='0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6'
SHADOW='e9af30d8d71209f9eb45d72de58ca509efd261d7126d89ab626e2873d182995d'
TASKS={'d1','repro','trace','auto-iff','idle','clocks','performance','allocation'}

def fn_source(source,name):
 tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name==name);return ast.get_source_segment(source,node)

def main():
 execution=read(E/'execution.json');rows=execution['rows'];required={(product,task)for product in ['baseline','shadow','active']for task in TASKS};actual={(r['product'],r['task'])for r in rows}
 assert execution['candidateSha256']==ACTIVE and execution['shadowSha256']==SHADOW
 assert len(actual)==len(rows),'Duplicate runtime execution rows'
 if actual!=required:
  print(json.dumps({'status':'INCOMPLETE','completed':len(rows),'missing':sorted(required-actual)}));return 2
 assert execution['allRequestedTasksExecuted']is True
 products={};receipts=[]
 for product,pinned in [('baseline',BASE),('shadow',SHADOW),('active',ACTIVE)]:
  out=E/product;d1=read(out/'d1-comparison.json');repro=read(out/'reproduction-off.json');trace=read(out/'trace-on.json');auto=read(out/'auto-iff-comparison.json');idle=read(out/'idle-comparison.json');clock=read(out/'harpoon-clock/ui-clock.json');perf=read(out/'performance.json');allocation=read(out/'allocation-and-owners.json')
  assert d1['productSha256']==pinned and repro['productSha256']==pinned and trace['productSha256']==pinned
  original_clock=clock['checks'];record=lambda r:{'name':r['name'],'checks':r['checks'],'status':r['status'],'stateSha256':r['stateSha256'],'birthMaxFinal':[r['nativeBirths'],r['maxFiles'],r['finalFiles']],'fullStateDifferenceCount':r['fullStateDifferenceCount'],'fullStateEvidence':r['fullStateEvidence'],'differences':r['differences'],'diagnostic':r['diagnostic']}
  performance_records=[{k:r.get(k)for k in ['trace','repetition','steps','meanTickMs','medianTickMs','p95TickMs','allCosts','liveHeapDeltaBytes','heapMetric','checks','stateSha256','fullState']}for r in perf['records']]
  allocation_records=[{k:r.get(k)for k in ['trace','repetition','steps','sampledAllocation','kernelInclusiveCounters','nestedCostWarning','checks','stateSha256','fullState']}for r in allocation['records']]
  products[product]={'sha256':pinned,'d1':{'status':d1['status'],'checks':d1['checks'],'cases':len(d1['rows']),'sameOriginalSignatures':sum(r['sameSignature']for r in d1['rows']),'differentSeeds':[r['seed']for r in d1['rows']if not r['sameSignature']],'path':str(out/'d1-comparison.json')},'reproOff':{'status':repro['status'],'records':[record(r)for r in repro['records']],'errors':repro['errors']},'traceOn':{'status':trace['status'],'records':[record(r)for r in trace['records']],'419025':{'status':trace['ciws419025']['status'],'checks':trace['ciws419025']['checks'],'releaseApproved':False},'errors':trace['errors']},'autoIff':{'status':auto['status'],'checks':auto['checks']},'idle120':{'status':idle['status'],'checks':idle['checks']},'clocks':{'assertions':len(original_clock),'passed':sum(original_clock.values()),'scales':[1,8,16,64],'path':str(out/'harpoon-clock/ui-clock.json')},'performance':{'status':perf['status'],'checks':perf['checks'],'records':performance_records,'versusFreshTrackA':perf.get('versusFreshTrackA',[]),'limitations':perf['limitations'],'approval':False},'allocationAndOwners':{'status':allocation['status'],'checks':allocation['checks'],'records':allocation_records,'versusFreshTrackA':allocation.get('versusFreshTrackA',[]),'limitations':allocation['limitations'],'approval':False}}
 for row in rows:
  receipt=row.get('workerReceipt')
  if receipt:
   assert receipt['completed']is True and receipt['exitCode']==row['exitCode']and receipt['controllerUnchangedDuringWorker']is True
   assert receipt['sourceProvenance']['status']=='PASS'
   receipts.append({'product':row['product'],'task':row['task'],'loadedControllerSha256':receipt['loadedControllerSha256'],'completed':True,'exitCode':receipt['exitCode'],'recoveredFromWorkerReceipt':row.get('recoveredFromWorkerReceipt',False)})
  else:
   assert row['product']=='baseline'and row['task']=='d1','Unproven missing worker receipt'
   old=P/'evidence/runtime/attempts/async-env-guard-a151/verify_runtime-a151.py';before=old.read_text();after=(P/'verify_runtime.py').read_text()
   assert sha(old.read_bytes())=='a151ee2ad2e85291e0c1cef2d832f823ec34d985f1932ca54ac6a4f0c04b7f75'
   assert fn_source(before,'original_script')==fn_source(after,'original_script')
   receipts.append({'product':'baseline','task':'d1','receiptNotAvailableInOriginalTool':True,'sourceProvenFromArchivedExactTool':str(old),'oldControllerSha256':sha(old.read_bytes()),'originalScriptFunctionByteIdentical':True,'functionSha256':sha(fn_source(before,'original_script').encode()),'actualOriginalExecutionAndComparisonRetained':True})
 semantic=read(E/'active/d1-semantic/SUMMARY.json');assert semantic['cases']==30 and semantic['status']=='COMPLETE_OBSERVATION'
 failures=[{'product':r['product'],'task':r['task'],'status':r['status'],'exitCode':r['exitCode'],'deltaApproved':False}for r in rows if r['status']!='PASS']
 value={'schema':'AEGIS_TRACK_B_RUNTIME_SUMMARY_1','candidateSha256':ACTIVE,'shadowSha256':SHADOW,'baselineSha256':BASE,'status':'FAIL'if failures else'PASS','completionStatus':'COMPLETE','allTasksComplete':True,'executedJobs':len(rows),'strictPassJobs':len(rows)-len(failures),'strictFailuresRetained':failures,'automaticApproval':False,'releaseApproved':False,'existing419025AndPairedDeltasNotApproved':True,'originalExpectedValuesAndAssertionsUnchanged':True,'countsNotAddedToExistingDomain420':True,'executionPath':str(E/'execution.json'),'toolEpochs':receipts,'products':products,'activeD1AfterAction':{'classification':'AFTER_ACTION_ONLY_NOT_GAME_INPUT','path':str(E/'active/d1-semantic/SUMMARY.json'),'originalStrictStatus':products['active']['d1']['status'],'cases':semantic['cases'],'sameOriginalSignatureCount':semantic['sameOriginalSignatureCount'],'differentSignatureSeeds':semantic['differentSignatureSeeds'],'selectedGameplayEqualCount':sum(r['selectedGameplaySummaryEqual']for r in semantic['rows']),'selectedGameplaySummaryNotPassCriterion':True,'outcomeWorseningIndicators':semantic['outcomeWorseningIndicators'],'allRawRowsAndTimestampKeyedEventDifferencesRetained':True,'approval':False},'performanceInterpretation':'All samples/outliers retained. Shared-host concurrent workloads and changed order prevent a reliable speedup/production-overhead conclusion. Live heap deltas are not allocation counts; sampled allocation is statistical. No performance approval.','historicalFixtureFailures':[str(E/'attempts/async-env-guard-a151/ATTEMPT.json')],'completedPassRecovery':[str(E/'attempts/scheduling-shadow-d1-receipt/RECOVERY.json')]}
 value['allocationMetricClarification']='B starts CDP HeapProfiler sampling with interval32768 and default GC collection flags: these are statistical retained sampled allocations, not total allocation churn/rate. Do not compare directly to prior A sampling that included GC-collected objects. All three fresh B variants use the same sampling options.'
 value['candidateKernelCoverage']='Two-owner fixture measures existing surface and surface-position kernels21 calls each; inclusive nesting is not additive. AIR/Cartesian calls are0 in that sampled workload; it is not universal worst-case candidate-cost coverage.'
 (E/'RUNTIME_SUMMARY.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value[k]for k in ['status','completionStatus','executedJobs','strictPassJobs','strictFailuresRetained','automaticApproval']},indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
