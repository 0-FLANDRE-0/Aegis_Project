"""Live lexical game functions vs private copies, both selected by product HTML."""
from pathlib import Path
import sys,json,gzip,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
payload=json.loads(Path('/tmp/aegis-launch-handoff-a/e3-fixture.json').read_text());start=time.perf_counter();checks={};errors=[];rows=[];ledger=[]
files={'DZT':(R/'archive/v48/WIP_FUZE_ZEM_A/Aegis_SIM_v48_WIP_FUZE_ZEM_A.html'),'HANDOFF':Path(json.loads((H/'build.json').read_text())['file'])}
cases=[{'weapon':'SM2ER','rangeKm':5,'altM':20000,'targetSpeedMps':0},{'weapon':'SM6','rangeKm':5,'altM':20000,'targetSpeedMps':0},{'weapon':'SM2','rangeKm':30,'altM':5000,'targetSpeedMps':250},{'weapon':'ESSM','rangeKm':15,'altM':5000,'crossSpeedMps':250},{'weapon':'SM6','rangeKm':320,'altM':15000,'targetSpeedMps':0}]
for i,c in enumerate(cases):c.update(rngSeed=305419896 if i%2 else 1831565813,navigationSeed=2654435769 if i%2 else 2047861954,samples=True,trace=True)
state="()=>JSON.stringify({tick:__NAVAL_SIM_DIAG__.snapshot(),rng:__HARPOON_DIAG_A__.snapshot().rng,operation:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),world:__AEGIS_ENGAGEMENT_RUNTIME__.world},(k,v)=>v instanceof Map?[...v]:v instanceof Set?[...v]:v)"
with sync_playwright()as pw:
 b=launch(pw)
 for variant,file in files.items():
  raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==payload['products'][variant]['htmlSha256']
  p=load_fleet(b,instrument(raw,payload['helpers'][variant]),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000)
  texts=p.evaluate('__LH_NATIVE_FUNCTION_TEXT__');hashes={n:hashlib.sha256(s.encode()).hexdigest()for n,s in texts.items()};checks[variant+'.everyNativeFunctionExact']=hashes==payload['functionHashes'][variant];ledger.append({'variant':variant,'htmlSha256':hashlib.sha256(raw).hexdigest(),'functions':len(hashes),'mismatches':[n for n,h in hashes.items()if payload['functionHashes'][variant].get(n)!=h]})
  p.evaluate('q=>window.__LH_PRIVATE__=new Function("DATA","SETTINGS","PROFILE","PRIVATE_SHIP",q.source)(q.input.data,q.input.settings,{}, {entityId:"ENV_PRIVATE",navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}})',{'source':payload['sources'][variant],'input':payload['input']})
  import gc
  detailDir=H/'final-results/equivalence';detailDir.mkdir(parents=True,exist_ok=True)
  for i,c in enumerate(cases):
   c['trace']=False
   before=p.evaluate(state);a=p.evaluate('c=>JSON.parse(JSON.stringify(__LH_PRIVATE__.runCase(c)))',c);checks[f'{variant}.privateIsolation.{i}']=before==p.evaluate(state)
   q=p.evaluate('c=>JSON.parse(JSON.stringify(__LH_NATIVE_A__.runCase(c)))',c);keys=['timeS','xM','yM','altitudeM','speedMps'];dif={k:max((abs(x[k]-y[k])for x,y in zip(a['samples'],q['samples'])),default=0)for k in keys};checks[f'{variant}.sampleCount.{i}']=len(a['samples'])==len(q['samples']);checks[f'{variant}.trajectory.{i}']=not any(dif.values());checks[f'{variant}.telemetry.{i}']=a['telemetry']==q['telemetry'];checks[f'{variant}.outcome.{i}']=all(a[k]==q[k]for k in ['success','lethal','reason','rng','pk','damage','fuzeState']);checks[f'{variant}.wholeReturn.{i}']=a==q
   ah=hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest();qh=hashlib.sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
   detail={'variant':variant,'condition':c,'native':q,'privateSha256':ah,'nativeSha256':qh,'wholeReturnEqual':a==q}
   if a!=q:detail['private']=a
   (detailDir/(variant+'-'+str(i)+'.json.gz')).write_bytes(gzip.compress(json.dumps(detail,separators=(',',':')).encode(),9,mtime=0))
   rows.append({'variant':variant,'condition':c,'maxError':dif,'reason':q['reason'],'privateSha256':ah,'nativeSha256':qh});print(variant,i,q['reason'],q['closestM'],dif,a==q,flush=True)
   del a,q,detail;gc.collect();cdp=p.context.new_cdp_session(p);cdp.send('HeapProfiler.collectGarbage');cdp.detach()
  p.close()
 b.close()
checks['pageErrors0']=not errors;o={'pass':all(checks.values()),'checks':checks,'ledger':ledger,'errors':errors,'elapsedS':time.perf_counter()-start,'products':payload['products'],'conditions':rows,'memoryPolicy':'One pair at a time. Native full result retained once when entire private result equals it, with both canonical hashes. No aggregation of large duplicate telemetry.'};(H/'final-evidence/equivalence.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps({'pass':o['pass'],'failed':[k for k,v in checks.items()if not v],'ledger':ledger}));raise SystemExit(0 if o['pass']else 1)
