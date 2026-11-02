"""Exact provenance of no-reflector native processing false alarms.

Additional causal replays only; never replace a statistical trial or label a
measurement using range/nearest truth. The original generator is called once.
"""
from pathlib import Path
import concurrent.futures,gzip,hashlib,json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3]
sys.path.insert(0,str(P));import battles
PREFIX=r'''
const trackCNoiseOrigins=[];
const trackCNativeFalsePlot=spyFalsePlotV31;
spyFalsePlotV31=function(task){const p=trackCNativeFalsePlot.apply(this,arguments);trackCNoiseOrigins.push({step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT,origin:'NATIVE_RECEIVER_PROCESSING_FALSE_ALARM_NO_REFLECTOR',source:p.source,fields:{rangeM:p.rangeM,azRad:p.azRad,elRad:p.elRad,radialMps:p.radialMps}});return p;};
'''
def save(path,q):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
def prepare():
 root=P/'evidence/noise-origin';root.mkdir(parents=True,exist_ok=True);source=(P/'test_support/battle.js').read_text();needle='return {trackCLineage,schema:';assert source.count(needle)==1;helper=PREFIX+source.replace(needle,'return {noiseOriginBirths:trackCNoiseOrigins,trackCLineage,schema:',1);path=P/'test_support/noise_origin_battle.js'
 if path.exists():assert path.read_text()==helper
 else:path.write_text(helper)
 table=json.loads((P/'LINEAGE_RESULTS.json').read_text());normal={q['id']:q for q in battles.specs()};jobs=[]
 for row in table['rows']:
  if not row['counts'].get('UNLINKED'):continue
  q=normal[row['id']];orig=battles.selected_out(q['id']);analysis=json.loads(gzip.decompress((orig/'LINEAGE_ANALYSIS.json.gz').read_bytes()));expected=[q for q in analysis['events']if q['event']=='UNRESOLVED_RF_LINEAGE'];jobs.append({**q,'normalId':q['id'],'id':'NOISE-'+q['id'],'noiseOriginProbe':True,'noiseHelperSha256':battles.sha(path),'expected':expected,'out':str(root/'runs'/q['id'])})
 save(root/'PLAN.json',{'caseCount':len(jobs),'expectedMeasurements':sum(len(q['expected'])for q in jobs),'helperSha256':battles.sha(path),'originalHelperSha256':battles.sha(P/'test_support/battle.js'),'generatorOriginalSourceSha256':'derived from unchanged product source; source audit saved separately','callsOriginalGeneratorExactlyOnce':True,'writesIntoPlot':0,'physicsOrRngChanged':False,'statisticalDatasetReplaced':False,'jobs':jobs});return jobs
def run(job):
 out=Path(job['out']);out.mkdir(parents=True,exist_ok=True);assert not(out/'RESULTS.json').exists();save(out/'JOB.json',job);at=time.monotonic();cmd=[sys.executable,'-u',str(P/'battles.py'),'--worker',str(out/'JOB.json')]
 with(out/'worker.log').open('w')as f:q=subprocess.run(cmd,cwd=R,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/dev/shm'},stdout=f,stderr=subprocess.STDOUT,timeout=600)
 assert q.returncode==0,(job['id'],(out/'worker.log').read_text()[-1200:]);decoder=battles.mod('noise_decoder',P.with_name('B_stabilization')/'battle.py');tag='candidate-active-'+job['case']['id'];r=decoder.decode_capture(json.loads(gzip.decompress((out/(tag+'.json.gz')).read_bytes())));ref=r['trackCLineage'];assert ref['schema']=='AEGIS_TRACK_C_LINEAGE_EXTERNAL_GZIP_1';packed=(out/ref['path']).read_bytes();assert hashlib.sha256(packed).hexdigest()==ref['compressedSha256'];aa=gzip.decompress(packed);assert len(aa)==ref['jsonBytes']and hashlib.sha256(aa).hexdigest()==ref['jsonSha256'];r['trackCLineage']=json.loads(aa)
 original,metric=battles.load(battles.selected_out(job['normalId']));summary=json.loads((out/(tag+'-SUMMARY.json')).read_text());assert summary['fixtureSha256']==job['noiseHelperSha256'];assert summary['productSha256']==metric['productSha256'];assert r['case']==original['case'];checks={'nativeChecks':all(decoder.post_validation(r).values()),'entireNativeFinalExact':r['final']==original['final'],'entireExistingLineageExact':r['trackCLineage']==original['trackCLineage'],'passiveRngAndStateExact':json.loads(gzip.decompress((out/(tag+'-PASSIVE.json.gz')).read_bytes()))==json.loads(gzip.decompress(next(battles.selected_out(job['normalId']).glob('*-PASSIVE.json.gz')).read_bytes()))};matches=[]
 for event in job['expected']:
  match=[v for v in r['noiseOriginBirths']if v['step']==event['step']and v['source']==event['source']and v['fields']==event['fields']];matches.append({'event':event,'generatorMatches':match,'exactOriginProven':len(match)==1})
 checks['allMissingOriginsExactlyNativeNoise']=all(v['exactOriginProven']for v in matches);result={'status':'PASS'if all(checks.values())else'FAIL','id':job['normalId'],'checks':checks,'matches':matches,'allGeneratorBirths':r['noiseOriginBirths'],'wallS':time.monotonic()-at,'rawSha256':battles.sha(out/(tag+'.json.gz'))};save(out/'RESULTS.json',result);print(json.dumps({'id':job['normalId'],'status':result['status'],'checks':checks}),flush=True);return result
def main():
 jobs=prepare();rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  for future in concurrent.futures.as_completed([pool.submit(run,q)for q in jobs]):rows.append(future.result());save(P/'evidence/noise-origin/PROGRESS.json',{'completed':len(rows),'planned':len(jobs),'rows':rows})
 q={'status':'PASS'if len(rows)==len(jobs)and all(r['status']=='PASS'for r in rows)else'FAIL','rows':rows,'measurementsResolved':sum(len(r['matches'])for r in rows),'noPhysicalIdInvented':True,'allStatisticalResultsAndGameInputsUnchanged':True};save(P/'evidence/noise-origin/RESULTS.json',q);return 0 if q['status']=='PASS'else 1
if __name__=='__main__':raise SystemExit(main())
