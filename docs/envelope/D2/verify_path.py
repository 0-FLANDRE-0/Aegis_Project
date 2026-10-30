from pathlib import Path
import gzip,hashlib,json,sys,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
p=json.loads((H/'path-fixture.json').read_text());checks={};errors=[];rows=[];start=time.perf_counter()
cases=[{'weapon':'SM2','rangeKm':20,'altM':30,'targetSpeedMps':-250},{'weapon':'SM2ER','rangeKm':100,'altM':5000,'targetSpeedMps':250},{'weapon':'SM6','rangeKm':60,'altM':5000,'crossSpeedMps':250},{'weapon':'ESSM','rangeKm':10,'altM':1000,'targetSpeedMps':250},{'weapon':'SM6','rangeKm':20,'altM':30,'targetSpeedMps':-250,'rngSeed':305419896,'navigationSeed':2654435769},{'weapon':'SM2','rangeKm':30,'altM':5000,'targetLabel':'Kh-32','crossSpeedMps':250}]
state="()=>JSON.stringify({tick:__NAVAL_SIM_DIAG__.snapshot(),rng:__HARPOON_DIAG_A__.snapshot().rng,operation:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),world:__AEGIS_ENGAGEMENT_RUNTIME__.world},(k,v)=>v instanceof Map?[...v]:v instanceof Set?[...v]:v)"
with sync_playwright()as pw:
 b=launch(pw);page=load_fleet(b,instrument(Path(p['product']['file']).read_bytes(),p['helper']),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);page.set_default_timeout(240000)
 checks['nativeFunctionHashesExact']={k:hashlib.sha256(v.encode()).hexdigest()for k,v in page.evaluate('__ENV_D2_TEXT__').items()}==p['functionHashes']
 page.evaluate('q=>window.__ENV_D2_PRIVATE__=new Function("DATA","SETTINGS","PROFILE","PRIVATE_SHIP",q.source)(q.input.data,q.input.settings,{}, {entityId:"ENV_PRIVATE",navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}})',p)
 for i,c in enumerate(cases):
  before=page.evaluate(state);a=page.evaluate('c=>__ENV_D2_PRIVATE__.runCase(c)',c);checks[f'isolated.{i}']=before==page.evaluate(state);q=page.evaluate('c=>__ENV_D2_NATIVE__.runCase(c)',c)
  dif={k:max((abs(x[k]-y[k])for x,y in zip(a['samples'],q['samples'])),default=0)for k in ['timeS','xM','yM','altitudeM','speedMps']};checks[f'exact.{i}']=a==q
  rows.append({'condition':c,'private':a,'native':q,'maxError':dif});print(i,q['reason'],dif,a==q,flush=True)
  page.evaluate('()=>{}');cdp=page.context.new_cdp_session(page);cdp.send('HeapProfiler.collectGarbage');cdp.detach()
 page.close();b.close()
checks['pageErrors0']=not errors
(H/'evidence/path-details.json.gz').write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),9,mtime=0))
out={'pass':all(checks.values()),'checks':checks,'conditions':[{'condition':r['condition'],'maxError':r['maxError'],'reason':r['native']['reason']}for r in rows],'errors':errors,'elapsedS':time.perf_counter()-start};(H/'evidence/path.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));raise SystemExit(0 if out['pass']else 1)
