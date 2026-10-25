"""Live lexical game functions vs private copies, both selected by product HTML."""
from pathlib import Path
import sys,json,gzip,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
payload=json.loads(Path('/tmp/aegis-launch-handoff-a/e3-fixture.json').read_text());start=time.perf_counter();checks={};errors=[];rows=[];ledger=[]
files={'DZT':R/'Aegis_SIM_v48_WIP_FUZE_ZEM_A.html','HANDOFF':Path(json.loads((H/'build.json').read_text())['file'])}
cases=[{'weapon':'SM2ER','rangeKm':5,'altM':20000,'targetSpeedMps':0},{'weapon':'SM6','rangeKm':5,'altM':20000,'targetSpeedMps':0},{'weapon':'SM2','rangeKm':30,'altM':5000,'targetSpeedMps':250},{'weapon':'ESSM','rangeKm':15,'altM':5000,'crossSpeedMps':250},{'weapon':'SM6','rangeKm':320,'altM':15000,'targetSpeedMps':0}]
for i,c in enumerate(cases):c.update(rngSeed=305419896 if i%2 else 1831565813,navigationSeed=2654435769 if i%2 else 2047861954,samples=True,trace=True)
state="()=>JSON.stringify({tick:__NAVAL_SIM_DIAG__.snapshot(),rng:__HARPOON_DIAG_A__.snapshot().rng,operation:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),world:__AEGIS_ENGAGEMENT_RUNTIME__.world},(k,v)=>v instanceof Map?[...v]:v instanceof Set?[...v]:v)"
with sync_playwright()as pw:
 b=launch(pw)
 for variant,file in files.items():
  raw=file.read_bytes();assert hashlib.sha256(raw).hexdigest()==payload['products'][variant]['htmlSha256']
  p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000);p.evaluate('q=>window.__LH_PRIVATE__=new Function("DATA","SETTINGS","PROFILE","PRIVATE_SHIP",q.source)(q.input.data,q.input.settings,{}, {entityId:"ENV_PRIVATE",navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}})',{'source':payload['sources'][variant],'input':payload['input']});private=[]
  for i,c in enumerate(cases):
   before=p.evaluate(state);private.append(p.evaluate('c=>JSON.parse(JSON.stringify(__LH_PRIVATE__.runCase(c)))',c));checks[f'{variant}.privateIsolation.{i}']=before==p.evaluate(state)
  p.close();p=load_fleet(b,instrument(raw,payload['helpers'][variant]),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000);texts=p.evaluate('__LH_NATIVE_FUNCTION_TEXT__');hashes={n:hashlib.sha256(s.encode()).hexdigest()for n,s in texts.items()};checks[variant+'.everyNativeFunctionExact']=hashes==payload['functionHashes'][variant];ledger.append({'variant':variant,'htmlSha256':hashlib.sha256(raw).hexdigest(),'functions':len(hashes),'mismatches':[n for n,h in hashes.items()if payload['functionHashes'][variant].get(n)!=h]})
  for i,(c,a)in enumerate(zip(cases,private)):
   q=p.evaluate('c=>JSON.parse(JSON.stringify(__LH_NATIVE_A__.runCase(c)))',c);keys=['timeS','xM','yM','altitudeM','speedMps'];dif={k:max((abs(x[k]-y[k])for x,y in zip(a['samples'],q['samples'])),default=0)for k in keys};checks[f'{variant}.sampleCount.{i}']=len(a['samples'])==len(q['samples']);checks[f'{variant}.trajectory.{i}']=not any(dif.values());checks[f'{variant}.telemetry.{i}']=a['telemetry']==q['telemetry'];checks[f'{variant}.outcome.{i}']=all(a[k]==q[k]for k in ['success','lethal','reason','rng','pk','damage','fuzeState']);rows.append({'variant':variant,'condition':c,'maxError':dif,'private':a,'native':q});print(variant,i,q['reason'],q['closestM'],dif,flush=True)
  p.close()
 b.close()
checks['pageErrors0']=not errors;o={'pass':all(checks.values()),'checks':checks,'ledger':ledger,'errors':errors,'elapsedS':time.perf_counter()-start,'products':payload['products'],'conditions':[{'variant':r['variant'],'condition':r['condition'],'maxError':r['maxError'],'reason':r['native']['reason']}for r in rows]};(H/'evidence/equivalence.json').write_text(json.dumps(o,indent=2)+'\n');(H/'results/equivalence-details.json.gz').write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),9,mtime=0));print(json.dumps({'pass':o['pass'],'failed':[k for k,v in checks.items()if not v],'ledger':ledger}));raise SystemExit(0 if o['pass']else 1)
