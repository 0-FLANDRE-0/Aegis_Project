"""Whole-game lexical native methods versus detached copied native methods."""
import json,gzip,hashlib,time
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_tools import H,R,launch,load_fleet,instrument
payload=json.loads(Path('/tmp/aegis-fuze-zem/e3-fixture.json').read_text());records=[];checks={};errors=[]
cases=[{'weapon':'SM2','rangeKm':30,'altM':5000,'targetSpeedMps':250},{'weapon':'SM2ER','rangeKm':30,'altM':30,'targetSpeedMps':680},{'weapon':'SM6','rangeKm':5,'altM':20000,'targetSpeedMps':0},{'weapon':'ESSM','rangeKm':15,'altM':5000,'crossSpeedMps':250}]
for c in cases:c.update(rngSeed=305419896,navigationSeed=2654435769,samples=True)
state="()=>JSON.stringify({tick:__NAVAL_SIM_DIAG__.snapshot(),rng:__HARPOON_DIAG_A__.snapshot().rng,operation:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),world:__AEGIS_ENGAGEMENT_RUNTIME__.world},(k,v)=>v instanceof Map?[...v]:v instanceof Set?[...v]:v)"
with sync_playwright()as pw:
 b=launch(pw)
 for variant in ['D','DZT']:
  raw=Path('/tmp/aegis-fuze-zem/builds/Aegis_SIM_v48_WIP_FUZE_ZEM_A_'+variant+'.html').read_bytes()
  p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors);assert not p.evaluate('__CORE_SELFTEST_FAILURES__')
  p.evaluate('x=>window.__FZ_PRIVATE_A__=new Function("DATA","SETTINGS","PROFILE","PRIVATE_SHIP",x.source)(x.input.data,x.input.settings,{}, {entityId:"ENV_PRIVATE",navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}})',{'source':payload['sources'][variant],'input':payload['input']})
  private=[]
  for i,c in enumerate(cases):
   before=p.evaluate(state);private.append(p.evaluate('c=>JSON.parse(JSON.stringify(__FZ_PRIVATE_A__.runCase(c)))',c));checks[variant+'.privateWorldRngUnchanged.'+str(i)]=before==p.evaluate(state)
  p.close();p=load_fleet(b,instrument(raw,payload['helper']),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000)
  for i,(c,a)in enumerate(zip(cases,private)):
   q=p.evaluate('c=>JSON.parse(JSON.stringify(__FZ_NATIVE_A__.runCase(c)))',c);keys=['timeS','xM','yM','altitudeM','speedMps'];dif={k:max((abs(x[k]-y[k])for x,y in zip(a['samples'],q['samples'])),default=0)for k in keys};checks[variant+'.samples.'+str(i)]=len(a['samples'])==len(q['samples']);checks[variant+'.trajectory.'+str(i)]=not any(dif.values());checks[variant+'.fuze.'+str(i)]=a['diagnostic']['fuze']==q['diagnostic']['fuze'];checks[variant+'.nativeOutcome.'+str(i)]=all(a[k]==q[k]for k in ['success','lethal','reason','rng','pk','damage','termFinal']);records.append({'variant':variant,'condition':c,'maxError':dif,'private':a,'native':q});print(variant,i,q['reason'],dif,flush=True)
  p.close()
 b.close()
checks['pageErrors0']=not errors;out={'pass':all(checks.values()),'checks':checks,'errors':errors,'conditions':[{'variant':r['variant'],'condition':r['condition'],'maxError':r['maxError'],'reason':r['native']['reason']}for r in records]};(H/'evidence/equivalence.json').write_text(json.dumps(out,indent=2)+'\n');(H/'results/equivalence-details.json.gz').write_bytes(gzip.compress(json.dumps(records,separators=(',',':')).encode(),9,mtime=0));print(json.dumps({'pass':out['pass'],'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if out['pass']else 1)
