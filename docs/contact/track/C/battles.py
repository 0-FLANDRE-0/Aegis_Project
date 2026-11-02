"""Exact native terminal battles and isolated AFTER_ACTION lineage. Max2 browsers."""
from pathlib import Path
import argparse,concurrent.futures,gzip,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/battles'
sys.path.insert(0,str(P))
from instrument import physical_probe,battle_helper
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def save(path,q):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
def selected_out(job_id):
 root=E/'runs'/job_id;pin=root/'SELECTED_ATTEMPT.json';attempt=json.loads(pin.read_text())['attempt']if pin.exists()else'attempt1';assert attempt.startswith('attempt')and attempt[7:].isdigit();return root/attempt
def products():
 active=json.loads((P/'BUILD.json').read_text());shadow=json.loads((P/'BUILD_SHADOW.json').read_text())
 return {'R4':{'file':'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html','sha256':active['baselineHtmlSha256']},'C':{'file':active['html'],'sha256':active['htmlSha256']},'C_SHADOW':{'file':shadow['html'],'sha256':shadow['htmlSha256']}}
def specs():
 source=json.loads((P.with_name('B_statistics_r4')/'JOBS.json').read_text());out=[]
 for q in source:
  if q['product']!='R4':continue
  for prod in ['R4','C']:out.append({'id':q['scenario']+'-'+str(q['seed'])+'-'+prod,'scenario':q['scenario'],'seed':q['seed'],'product':prod,'case':q['case']})
 return out
def prepare():
 E.mkdir(parents=True,exist_ok=True);helper=P/'test_support/battle.js';helper.parent.mkdir(exist_ok=True);s=battle_helper()
 freeze=E/'FROZEN.json'
 if freeze.exists():assert helper.read_text()==s;data=json.loads(freeze.read_text());assert data['products']==products();return data
 helper.write_text(s);data={'schema':'AEGIS_TRACK_C_FROZEN_NATIVE_BATTLES_1','products':products(),'helperSha256':sha(helper),'afterActionSha256':sha(P/'after_action.js'),'instrumentSha256':sha(P/'instrument.py'),'originalRunnerSha256':sha(P.with_name('B_stabilization')/'battle.py'),'planSha256':sha(P/'PLAN.json'),'jobs':specs(),'firstRealBattleNotYetExecuted':True}
 save(freeze,data);return data
def worker(job_path):
 frozen=json.loads((E/'FROZEN.json').read_text());job=json.loads(Path(job_path).read_text());product=frozen['products'][job['product']]
 assert sha(R/product['file'])==product['sha256'];assert sha(P/'test_support/battle.js')==frozen['helperSha256'];assert sha(P/'instrument.py')==frozen['instrumentSha256'];assert sha(P/'after_action.js')==frozen['afterActionSha256']
 os.environ.pop('B2_PHASE1_REGRESSION',None)
 sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));import browser_tools
 original=browser_tools.instrument
 def observed(raw,helper):
  hooked,receipt=physical_probe(raw);save(Path(job['out'])/'PHYSICAL_PROBE.json',receipt);return original(hooked,helper)
 browser_tools.instrument=observed
 b=mod('frozen_native_battle_runner_c',P.with_name('B_stabilization')/'battle.py');b.P=P;b.HELPER=P/'test_support/battle.js';b.CASES={job['case']['id']:job['case']}
 if job.get('noiseOriginProbe'):
  b.HELPER=P/'test_support/noise_origin_battle.js';assert sha(b.HELPER)==job['noiseHelperSha256']
 sys.path.insert(0,str(R/'docs/gun/B2/phase1b'))
 from export_transport import install
 install(b,Path(job['out']),save)
 sys.argv=[str(P/'battles.py'),'--run','--versions','candidate-active','--cases',job['case']['id'],'--candidate',str(R/product['file']),'--sha',product['sha256'],'--out',job['out']]
 return b.main()
def load(out):
 out=Path(out).resolve();job=json.loads((out/'JOB.json').read_text());tag='candidate-active-'+job['case']['id']
 b=mod('original_capture_decoder_c',P.with_name('B_stabilization')/'battle.py');r=b.decode_capture(json.loads(gzip.decompress((out/(tag+'.json.gz')).read_bytes())))
 if r.get('trackCLineage',{}).get('schema')=='AEGIS_TRACK_C_LINEAGE_EXTERNAL_GZIP_1':
  ref=r['trackCLineage'];assert ref['path']=='TRACK_C_LINEAGE.json.gz'and ref['omittedRecords']==ref['omittedFields']==0 and ref['gzipRoundTripExact'];path=out/ref['path'];assert sha(path)==ref['compressedSha256'];raw=gzip.decompress(path.read_bytes());assert len(raw)==ref['jsonBytes']and hashlib.sha256(raw).hexdigest()==ref['jsonSha256'];r['trackCLineage']=json.loads(raw)
 checks=b.post_validation(r);assert all(checks.values()),checks
 assert r['end']['reason']=='ALL_INITIAL_NATIVE_TERMINAL_OR_EGRESS_PLUS_5S'and all(t['statisticalResolved']for t in r['targets'])
 assert not json.loads((out/'SUMMARY.json').read_text())['errors']
 summary=json.loads((out/(tag+'-SUMMARY.json')).read_text());frozen=json.loads((E/'FROZEN.json').read_text())
 assert summary['productSha256']==frozen['products'][job['product']]['sha256']
 assert summary['fixtureSha256']==frozen['helperSha256']
 assert summary['setupSha256']==hashlib.sha256(json.dumps(job['case'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert r['case']==job['case'] and r['startsWithZeroTracks'] and r['mode']=='AUTO'
 aa=r['trackCLineage'];assert not aa['faults']and aa['dropped']==0
 if aa.get('candidateTrace'):assert aa['candidateTrace']['errors']==aa['candidateTrace']['dropped']==0
 kinds={};kills={'INTERCEPT_KILL','INTERCEPT_STRUCTURAL_FAILURE','PHALANX_KILL','DELAYED_STRUCTURAL_FAILURE','WARHEAD_AIRBURST'};hits={'NORMAL_HIT','DUD_PENETRATION','DAMAGED_HIT','DEGRADED_HIT','WARHEAD_DUD_HIT'}
 outcomes=[]
 for t in r['targets']:
  cause=t['retirement'].get('cause')or t.get('_deathReason')or t.get('_wip113Outcome')or t.get('retiredReason')
  k='EGRESS'if t['alive']else'KILL'if cause in kills else'LEAKER'if cause in hits else'OTHER'
  if k=='EGRESS':assert t['statisticalEgress']['qualified']
  if k=='OTHER':assert cause and ('SEA'in cause or'WATER'in cause or cause in ['GUIDANCE_CONTROL_LOSS_MISS','FUEL_EXHAUSTED','LIFETIME_EXCEEDED','LIFE_EXPIRED','TERRAIN_IMPACT','GROUND_IMPACT','SELF_DESTRUCT']),('NATIVE_OUTCOME_NEEDS_SOURCE_CLASSIFICATION',job['id'],cause)
  outcomes.append({'initialId':t['id'],'category':k,'nativeCause':cause,'egress':t['statisticalEgress']})
  kinds[k]=kinds.get(k,0)+1
 events=[e for e in r['events']if e['kind']=='NATIVE_SHIP_HIT_RECORD'];damaging=[e for e in events if(e['hit'].get('dmg')or 0)>0 and not e['hit'].get('miss')]
 metric={'id':job['id'],'scenario':job['scenario'],'seed':job['seed'],'product':job['product'],'status':'VALID','kills':kinds.get('KILL',0),'leakers':kinds.get('LEAKER',0),'egress':kinds.get('EGRESS',0),'other':kinds.get('OTHER',0),'damagingHitRounds':len(damaging),'wreckDamagingCallbacks':sum(bool(e['hit'].get('wip11cWreck'))for e in damaging),'floodM3':sum(c['waterM3']for c in r['final']['ship']['damage']['flooding']['cells']),'hpReferenceOnly':r['final']['ship']['shipHP'],'end':r['end'],'initialCount':len(r['targets']),'rawSha256':sha(out/(tag+'.json.gz')),'rawPath':str((out/(tag+'.json.gz')).relative_to(P)),'nativeChecks':checks,'lineageRecords':len(aa['records']),'unlinkedRfRecords':sum(q['lineageStatus']=='UNLINKED'for q in aa['records']),'ambiguousExactFingerprints':sum(q['lineageStatus']=='AMBIGUOUS_EXACT_FINGERPRINT'for q in aa['records'])}
 metric.update(initialOutcomes=outcomes,productSha256=summary['productSha256'],fixtureSha256=summary['fixtureSha256'],noGameObjectsRetiredByTest=r['statisticalEndpoint']['gameObjectsRetiredByTest']==0)
 assert metric['noGameObjectsRetiredByTest'];save(out/'METRICS.json',metric);return r,metric
def execute(job,deadline):
 root=E/'runs'/job['id'];out=selected_out(job['id'])
 if job.get('retryInfrastructure'):
  previous=out;old=json.loads((previous/'EXECUTION.json').read_text());assert old['status']=='INCOMPLETE';log=(previous/'worker.log').read_text();assert'Target crashed'in log or'Capture exceeds 10MiB'in log or(job['id'].startswith('CONTROL-TRANSPORT-')and"No module named 'fast_http'"in log),'RETRY_ONLY_RECORDED_INFRASTRUCTURE_FAILURE';out=root/('attempt'+str(max(int(p.name[7:])for p in root.glob('attempt*'))+1));assert not out.exists()
 else:assert not(out/'EXECUTION.json').exists(),'PRESERVE_EXECUTED_TRIAL_USE_RESUME_OR_FRESH_EVIDENCE_DIRECTORY'
 out.mkdir(parents=True,exist_ok=True);job={**job,'out':str(out)};save(out/'JOB.json',job)
 while int(Path('/sys/fs/cgroup/memory.max').read_text())-int(Path('/sys/fs/cgroup/memory.current').read_text())<2*1024**3 and time.monotonic()<deadline:time.sleep(1)
 if time.monotonic()>=deadline:
  receipt={'id':job['id'],'status':'NOT_EXECUTED_BUDGET','reason':'Four-hour total wall cap; no new worker/browser launched.','wallS':0};save(out/'EXECUTION.json',receipt);return receipt
 at=time.monotonic();cmd=[sys.executable,'-u',str(Path(__file__).resolve()),'--worker',str(out/'JOB.json')]
 with(out/'worker.log').open('w')as log:
  p=subprocess.Popen(cmd,cwd=R,env={**os.environ,'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:code=p.wait(timeout=max(1,min(900,deadline-time.monotonic())))
  except subprocess.TimeoutExpired:
   import signal;os.killpg(p.pid,signal.SIGTERM);code=124
 receipt={'id':job['id'],'exitCode':code,'wallS':time.monotonic()-at,'command':cmd}
 try:
  assert code==0,code;r,m=load(out);receipt.update(status='VALID',metrics=m)
 except Exception as ex:receipt.update(status='INCOMPLETE',error=str(ex),traceback=traceback.format_exc())
 save(out/'EXECUTION.json',receipt)
 if receipt['status']=='VALID':save(root/'SELECTED_ATTEMPT.json',{'attempt':out.name,'reason':'Only complete native outcome-independent capture selected; prior infrastructure attempts remain intact.','rawSha256':receipt['metrics']['rawSha256']})
 return receipt
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--worker');ap.add_argument('--run',action='store_true');ap.add_argument('--controls',action='store_true');ap.add_argument('--transport-controls',action='store_true');ap.add_argument('--only',nargs='+');ap.add_argument('--retry-incomplete',action='store_true');ap.add_argument('--resume',action='store_true');a=ap.parse_args()
 if a.worker:return worker(a.worker)
 frozen=prepare();deadline=json.loads((P/'evidence/BUDGET.json').read_text())['deadlineMonotonic'];jobs=frozen['jobs']
 if a.transport_controls:
  jobs=[{**next(q for q in jobs if q['scenario']=='S6'and q['seed']==419027 and q['product']==prod),'id':'CONTROL-TRANSPORT-'+prod}for prod in ['R4','C']];parallel=1
 elif a.controls:
  q=next(x for x in jobs if x['scenario']=='S6'and x['seed']==419027 and x['product']=='C')
  r4=next(x for x in jobs if x['scenario']=='S6'and x['seed']==419027 and x['product']=='R4')
  jobs=[r4,{**q,'id':'CONTROL-S6-419027-C_SHADOW','product':'C_SHADOW'},{**q,'id':'CONTROL-S6-419027-C_OFF','case':{**q['case'],'lineageOn':False}},q]
  # Controls are sequential: isolate capture ON/OFF and prevent extra lane pressure.
  parallel=1
 else:parallel=2
 if a.only:jobs=[q for q in jobs if q['id']in a.only];assert len(jobs)==len(a.only)
 if not a.run:print(json.dumps({'jobs':len(jobs),'products':frozen['products']}));return
 rows=[];todo=[]
 for job in jobs:
  path=selected_out(job['id'])/'EXECUTION.json'
  if a.resume and path.exists():
   old=json.loads(path.read_text())
   if a.retry_incomplete and old['status']=='INCOMPLETE':todo.append({**job,'retryInfrastructure':True})
   else:rows.append(old)
  else:todo.append(job)
 with concurrent.futures.ThreadPoolExecutor(max_workers=parallel)as pool:
  futures={pool.submit(execute,j,deadline):j for j in todo}
  for f in concurrent.futures.as_completed(futures):
   row=f.result();rows.append(row);save(E/('TRANSPORT_CONTROLS_PROGRESS.json'if a.transport_controls else'CONTROLS_PROGRESS.json'if a.controls else'PROGRESS.json'),{'completed':len(rows),'planned':len(jobs),'rows':rows,'remainingWallS':deadline-time.monotonic()})
   print(json.dumps({'id':row['id'],'status':row['status'],'wallS':row['wallS'],'error':row.get('error')}),flush=True)
if __name__=='__main__':main()
