"""Natural sensor/AUTO/terminal battle pilot and frozen cross-version runner.

Default dry-run; product changes never made. A nondecisive pilot is INCOMPLETE.
Each page has fresh normal inventory and one shared heavy-browser lease.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,importlib.util,json,os,sys,time,traceback

P=Path(__file__).resolve().parent;R=P.parents[3];HELPER=P/'battle.js'
sha=lambda b:hashlib.sha256(b).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def asm(bearing,rng):return {'label':'Kh-35U','bearingDeg':bearing,'rangeKm':rng,'altM':10,'speedMps':280}
CASES={
 'PILOT_SINGLE':{'id':'PILOT_SINGLE','ship':'DDG_119_LATE_FLIGHT_IIA','seed':419021,'maxSeconds':90,'asms':[asm(90,11)]},
 'DDG_CONVERGING_2':{'id':'DDG_CONVERGING_2','ship':'DDG_119_LATE_FLIGHT_IIA','seed':419022,'maxSeconds':90,'asms':[asm(87,11),asm(93,11.3)]},
 'CG_MULTIPLE_3':{'id':'CG_MULTIPLE_3','ship':'CG_52_LATE_TICONDEROGA','seed':419024,'maxSeconds':90,'asms':[asm(84,11),asm(90,11.3),asm(96,11.6)]},
 'DDG_CROSSING_2':{'id':'DDG_CROSSING_2','ship':'DDG_119_LATE_FLIGHT_IIA','seed':419022,'maxSeconds':90,'asms':[{**asm(89.5,11),'headingOffsetDeg':-5},{**asm(90.5,11.08),'headingOffsetDeg':5}]},
 'DDG_BEARING_CROSSING_2':{'id':'DDG_BEARING_CROSSING_2','ship':'DDG_119_LATE_FLIGHT_IIA','seed':419022,'maxSeconds':90,'afterActionSampleHz':10,'afterActionFocusS':5,'asms':[{**asm(89.9,11),'headingOffsetDeg':-5},{**asm(90.1,11.16),'headingOffsetDeg':5}]},
 'NATURAL_SATURATION_13':{'id':'NATURAL_SATURATION_13','ship':'DDG_119_LATE_FLIGHT_IIA','seed':419027,'maxSeconds':90,'asms':[asm(90,10.8+i*.08)for i in range(13)]}}
PINS=json.loads((P/'BASELINE_PINS.json').read_text())['files']
OLD={'track-a':'Aegis_SIM_v48_WIP_TRACK_A.html','old-shadow':'Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html','old-active':'Aegis_SIM_v48_WIP_TRACK_B.html'}

# Export-only lossless columnar encoding. Native sampler/flight code is unchanged.
# A dense 90s saturation page otherwise repeats >10MiB of JSON field names.
CAPTURE_EXPORT_JS='''async c=>{const r=__TRACK_STABLE_BATTLE__.run(c);r.passiveFinalState=__TRACK_RUNTIME_A__.state();
const original=JSON.stringify(r),strings=[],stringIds=new Map();
const columns=a=>[...new Set(a.flatMap(o=>Object.keys(o)))];
const intern=v=>{if(typeof v!=="string")return v;if(!stringIds.has(v)){stringIds.set(v,strings.length);strings.push(v);}return {$:stringIds.get(v)};};
const restore=v=>v&&typeof v==="object"&&!Array.isArray(v)&&Object.keys(v).length===1&&Object.hasOwn(v,"$")?strings[v.$]:v;
const encodeRows=(a,cols,map=(k,v)=>v)=>a.map(o=>{const keys=Object.keys(o);return [keys.map(k=>cols.indexOf(k)),...keys.map(k=>intern(map(k,o[k])))];});
const decodeRows=(a,cols,map=(k,v)=>v)=>a.map(row=>{const o={};row[0].forEach((i,j)=>o[cols[i]]=map(cols[i],restore(row[j+1])));return o;});
if(r.associationReturns.length){const a=r.associationReturns,cols=columns(a),pairCols=columns(a.flatMap(o=>o.actualSelectedPairs)),componentCols=columns(a.flatMap(o=>o.components));
const rows=encodeRows(a,cols,(k,v)=>k==="actualSelectedPairs"?encodeRows(v,pairCols):k==="components"?encodeRows(v,componentCols):v);
const roundTrip=decodeRows(rows,cols,(k,v)=>k==="actualSelectedPairs"?decodeRows(v,pairCols):k==="components"?decodeRows(v,componentCols):v);
if(JSON.stringify(a)!==JSON.stringify(roundTrip))throw Error("TRANSPORT_COLUMNAR_ROUND_TRIP_MISMATCH");
r.associationReturns={encoding:"LOSSLESS_ASSOCIATION_COLUMNAR_2",columns:cols,pairColumns:pairCols,componentColumns:componentCols,strings,rows};}
const line=r.observedPlotLineage,lineCols=columns(line),measurementCols=columns(line.map(o=>o.measurement)),observedCols=columns(line.map(o=>o.measurement.observed).filter(Boolean)),sigmaCols=columns(line.map(o=>o.measurement.providedSigmas).filter(Boolean)),models=[],modelIds=new Map();
const model=v=>{const key=JSON.stringify(v);if(!modelIds.has(key)){modelIds.set(key,models.length);models.push(v);}return modelIds.get(key);};
const encMeasurement=v=>encodeRows([v],measurementCols,(k,q)=>k==="observed"&&q?encodeRows([q],observedCols)[0]:k==="providedSigmas"&&q?encodeRows([q],sigmaCols)[0]:k==="model"?model(q):q)[0];
const decMeasurement=v=>decodeRows([v],measurementCols,(k,q)=>k==="observed"&&q?decodeRows([q],observedCols)[0]:k==="providedSigmas"&&q?decodeRows([q],sigmaCols)[0]:k==="model"?models[q]:q)[0];
const lineRows=encodeRows(line,lineCols,(k,v)=>k==="measurement"?encMeasurement(v):v);
const decodedLine=decodeRows(lineRows,lineCols,(k,v)=>k==="measurement"?decMeasurement(v):v);
if(JSON.stringify(line)!==JSON.stringify(decodedLine))throw Error("TRANSPORT_LINEAGE_ROUND_TRIP_MISMATCH");
const encodedLine={encoding:"LOSSLESS_LINEAGE_COLUMNAR_1",columns:lineCols,measurementColumns:measurementCols,observedColumns:observedCols,sigmaColumns:sigmaCols,models,strings,rows:lineRows};
r.observedPlotLineage=encodedLine;
const hex=async text=>Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text))),n=>n.toString(16).padStart(2,"0")).join("");
const encoded=r.associationReturns;if(encoded.encoding){r.associationReturns=decodeRows(encoded.rows,encoded.columns,(k,v)=>k==="actualSelectedPairs"?decodeRows(v,encoded.pairColumns):k==="components"?decodeRows(v,encoded.componentColumns):v);}
r.observedPlotLineage=decodedLine;
const decoded=JSON.stringify(r);if(original!==decoded)throw Error("TRANSPORT_COMPLETE_JSON_KEY_ORDER_MISMATCH");
r.associationReturns=encoded;r.observedPlotLineage=encodedLine;r.transportReceipt={encoding:"LOSSLESS_COLUMNAR_3",originalJsonBytes:new TextEncoder().encode(original).length,originalJsonSha256:await hex(original),decodedJsonSha256:await hex(decoded),jsonStringifyExact:original===decoded,nativeAssociationRecordCount:Array.isArray(encoded)?encoded.length:encoded.rows.length,lineageRecordCount:line.length,omittedRecords:0,omittedFields:0};
return JSON.stringify(r)}'''

def decode_capture(result):
 if result.get('captureTransport')=='LOSSLESS_GZIP_JSON_ENVELOPE_1':
  payload=gzip.decompress(base64.b64decode(result['jsonGzipBase64']))
  assert sha(payload)==result['semanticJsonSha256']and len(payload)==result['semanticJsonBytes']
  result=json.loads(payload)
 value=result.get('associationReturns')
 if isinstance(value,dict)and value.get('encoding')=='LOSSLESS_ASSOCIATION_COLUMNAR_2':
  def cell(v):return value['strings'][v['$']]if isinstance(v,dict)and list(v)==['$']else v
  def rows(a,cols,transform=lambda k,v:v):return [{cols[i]:transform(cols[i],cell(v))for i,v in zip(row[0],row[1:])}for row in a]
  result['associationReturns']=rows(value['rows'],value['columns'],lambda k,v:rows(v,value['pairColumns'])if k=='actualSelectedPairs'else rows(v,value['componentColumns'])if k=='components'else v)
 value=result.get('observedPlotLineage')
 if isinstance(value,dict)and value.get('encoding')=='LOSSLESS_LINEAGE_COLUMNAR_1':
  def cell(v):return value['strings'][v['$']]if isinstance(v,dict)and list(v)==['$']else v
  def rows(a,cols,transform=lambda k,v:v):return [{cols[i]:transform(cols[i],cell(v))for i,v in zip(row[0],row[1:])}for row in a]
  def measurement(v):return rows([v],value['measurementColumns'],lambda k,q:rows([q],value['observedColumns'])[0]if k=='observed'and q else rows([q],value['sigmaColumns'])[0]if k=='providedSigmas'and q else value['models'][q]if k=='model'else q)[0]
  result['observedPlotLineage']=rows(value['rows'],value['columns'],lambda k,v:measurement(v)if k=='measurement'else v)
 return result

def encode_storage(result):
 """Final storage only; preserve exact canonical semantic JSON bytes."""
 raw=json.dumps(result,separators=(',',':')).encode()
 if len(raw)<=10*1024*1024:return raw
 packed=base64.b64encode(gzip.compress(raw,6,mtime=0)).decode('ascii')
 envelope={'captureTransport':'LOSSLESS_GZIP_JSON_ENVELOPE_1','semanticJsonBytes':len(raw),'semanticJsonSha256':sha(raw),'jsonGzipBase64':packed,'roundTripByteExact':True,'omittedRecords':0,'omittedFields':0}
 restored=gzip.decompress(base64.b64decode(packed));assert restored==raw and json.loads(restored)==result
 return json.dumps(envelope,separators=(',',':')).encode()

def post_validation(result):
 final=result['final'];diag=result['diagnostics']
 return {'nativeCoreZero':final['core']==[],'nativeRuntimeFaultNull':final['runtimeFault']is None,'nativePresentationFaultNull':final['presentationFault']is None,'samplerFaultZero':result['faults']==[],'helperEventDropZero':result['counts']['eventsDropped']==0,'actualAssociationReturnDropZero':result['counts'].get('associationReturnsDropped',0)==0,'plotLineageCaptureDropZero':result['counts'].get('lineageRecordsDropped',0)==0,'nativeTraceAErrorZero':diag['a']['errors']==0,'nativeTraceBErrorZero':diag['b']is None or diag['b']['errors']==0,'noInterceptorRuntimeError':not any(x.get('deathReason')=='RUNTIME_ERROR'for x in final['interceptHistory'])}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true');ap.add_argument('--versions',nargs='+',default=['track-a'],choices=['track-a','old-shadow','old-active','candidate-shadow','candidate-active']);ap.add_argument('--cases',nargs='+',default=['PILOT_SINGLE'],choices=list(CASES));ap.add_argument('--candidate',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_A.html');ap.add_argument('--sha');ap.add_argument('--shadow',type=Path,default=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_A_SHADOW.html');ap.add_argument('--shadow-sha');ap.add_argument('--out',type=Path,default=P/'evidence/battle-pilot');a=ap.parse_args();a.out=a.out.resolve();assert a.out.is_relative_to(P/'evidence');a.out.mkdir(parents=True,exist_ok=True)
 products=[]
 for label in a.versions:
  if label in OLD:file=R/OLD[label];pinned=PINS[OLD[label]]
  else:file=a.shadow if label=='candidate-shadow'else a.candidate;pinned=a.shadow_sha if label=='candidate-shadow'else a.sha
  assert pinned and file.exists()and sha(file.read_bytes())==pinned,(label,'Frozen product SHA required');products.append((label,file,pinned))
 plan={'schema':'AEGIS_TRACK_B_STABILIZATION_BATTLE_PLAN_1','runRequested':a.run,'products':[{'version':l,'path':str(f),'sha256':p}for l,f,p in products],'cases':[CASES[n]for n in a.cases],'fixtureSha256':sha(HELPER.read_bytes()),'runnerSha256':sha(Path(__file__).read_bytes()),'productCodeChanged':False,'expectedValuesChanged':False,'initialTracksSeeded':False,'perLaneBrowsers':1,'overallHeavyBrowserLimit':2,'releaseApproved':False};(a.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
 if not a.run:print(json.dumps(plan,indent=2));return 0
 assert os.environ.get('B2_PHASE1_REGRESSION')!='1','Do not force gun AutoAA or old test settings in the new battle'
 sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import instrument,launch
 sys.path.insert(0,str(R/'docs/gun/B2/phase1b'));from fast_http import load_fast_http
 sys.path.insert(0,str(R/'docs/gun/B2/diagnostic'));from http_browser import serve
 from playwright.sync_api import sync_playwright
 slots=module('battle_shared_browser_slots',P.parent/'B/regression_runner.py');passive=module('battle_original_passive_state',P.parent/'A/verify_runtime.py').PASSIVE_HELPER;rows=[];errors=[];started=time.perf_counter();print(json.dumps({'pid':os.getpid(),'pages':len(products)*len(a.cases),'oneSharedBrowserLane':True}),flush=True)
 for label,file,pinned in products:
  body=instrument(file.read_bytes(),HELPER.read_text()+'\n'+passive);server,url=serve(body)
  try:
   for name in a.cases:
    case=CASES[name]
    with slots.heavy_browser_slot()as lease:
     with sync_playwright()as pw:
      browser=launch(pw);page=load_fast_http(browser,url,own=case['ship'],errors=errors);page.set_default_timeout(900000);at=time.perf_counter();result=json.loads(page.evaluate(CAPTURE_EXPORT_JS,case));state=result.pop('passiveFinalState');sources=result.pop('nativeSources');sourceHashes={k:sha(v.encode())if v else None for k,v in sources.items()};validation=post_validation(result);result['fixtureQualificationStatus']=result['status'];result['postValidation']=validation
      if not all(validation.values()):result['status']='INVALID_NATIVE_OR_DIAGNOSTIC_FAULT'
      raw=encode_storage(result);assert len(raw)<=10*1024*1024,('Capture exceeds 10MiB',len(raw));tag=label+'-'+name;(a.out/(tag+'.json.gz')).write_bytes(gzip.compress(raw,6,mtime=0));(a.out/(tag+'-PASSIVE.json.gz')).write_bytes(gzip.compress(state.encode(),6,mtime=0));row={'version':label,'case':name,'productSha256':pinned,'setupSha256':sha(json.dumps(case,sort_keys=True,separators=(',',':')).encode()),'fixtureSha256':plan['fixtureSha256'],'passiveHelperSha256':sha(passive.encode()),'passiveFinalStateSha256':sha(state.encode()),'nativeSourceHashes':sourceHashes,'qualification':result['qualification'],'postValidation':validation,'status':result['status'],'end':result['end'],'counts':result['counts'],'targets':result['targets'],'hp':result['final']['ship']['shipHP'],'inventory':result['final']['inventory'],'core':result['final']['core'],'faults':result['faults'],'recordBytes':len(raw),'wallS':time.perf_counter()-at,'lease':lease,'releaseApproved':False};rows.append(row);(a.out/(tag+'-SUMMARY.json')).write_text(json.dumps(row,indent=2)+'\n');page.context.close();browser.close();print(json.dumps({k:row[k]for k in ['version','case','status','end','postValidation','hp','wallS']}|{'launches':row['counts']['launches'],'intercepts':row['counts']['intercepts'],'componentMaximum':row['counts']['componentMaximum'],'componentsOver12':row['counts']['componentsOver12']},ensure_ascii=False),flush=True)
    assert sha(file.read_bytes())==pinned,'Product changed during battle'
    if result['status']!='QUALIFYING_COMPLETED_BATTLE'and name=='PILOT_SINGLE':break
  finally:server.shutdown()
 report={'schema':'AEGIS_TRACK_B_STABILIZATION_BATTLE_RESULTS_1','rows':rows,'errors':errors,'wallS':time.perf_counter()-started,'status':'QUALIFYING_PILOT'if rows and all(r['status']=='QUALIFYING_COMPLETED_BATTLE'for r in rows)and not errors else'INCOMPLETE_NOT_DECISIVE','expectedValuesChanged':False,'releaseApproved':False};(a.out/'SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'wallS':report['wallS'],'pages':len(rows)}));return 0 if report['status']=='QUALIFYING_PILOT'else 2

if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as error:
  error_dir=P/'evidence/battle-errors';error_dir.mkdir(parents=True,exist_ok=True)
  (error_dir/(str(time.time_ns())+'.json')).write_text(json.dumps({'status':'INCOMPLETE_EXECUTION_ERROR','argv':sys.argv,'error':str(error),'traceback':traceback.format_exc(),'fixtureSha256':sha(HELPER.read_bytes()),'productCodeChanged':False,'expectedValuesChanged':False,'releaseApproved':False},indent=2)+'\n')
  raise
