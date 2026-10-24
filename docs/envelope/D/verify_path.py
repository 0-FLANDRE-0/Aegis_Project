"""Native whole-game lexical functions versus detached ASM diagnostic capsule.

Disposable instrumented pages supply exactly the documented ideal boundaries.
No production game function body is changed. Private runs must not mutate the
live world, global RNG or tick. Includes a transverse ASM target.
"""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'diagnostic';E=H/'evidence'
sys.path[:0]=[str(R/'docs/pip/B'),str(R/'docs/helicopter/H')]
import browser_backend;browser_backend.install()
from browser import launch,load_fleet
deps=json.loads((D/'dependencies.json').read_text());used={r['name']for r in deps['rows']}
boundary={k:v for k,v in json.loads((D/'boundaries.json').read_text()).items()if k in used}
names=[k for k,v in boundary.items()if v['code'].startswith('function ')]
overrides=[k+'=('+boundary[k]['code']+');'for k in names]
private=(D/'private.js').read_text().split('return {runCase,profiles:')[0]
source=(D/'native-engine.js').read_text()+'\n'+(D/'private.js').read_text()
helper=(D/'native-asm-prefix.js').read_text()+'\n'+private+'\nwindow.__ENV_D_NATIVE__={runCase(c){const saved={'+','.join(names)+'};try{'+\
 '\n'.join(overrides)+"selectedLockId=1;emconActive=false;engagementControlMode='MANUAL';shipNav.positionWorld.x=0;shipNav.positionWorld.y=0;shipNav.vx=shipNav.vy=shipNav.speed=0;return runCase(c);}finally{"+';'.join(k+'=saved.'+k for k in names)+'}}};\n'
cases=[
 {'weapon':'SM2','rangeKm':20,'altM':30,'targetSpeedMps':-250},
 {'weapon':'SM2ER','rangeKm':100,'altM':5000,'targetSpeedMps':250},
 {'weapon':'SM6','rangeKm':60,'altM':5000,'crossSpeedMps':250},
 {'weapon':'ESSM','rangeKm':10,'altM':1000,'targetSpeedMps':250},
 {'weapon':'SM6','rangeKm':20,'altM':30,'targetSpeedMps':-250,'rngSeed':305419896,'navigationSeed':2654435769},
 {'weapon':'SM2','rangeKm':30,'altM':5000,'targetLabel':'Kh-32','crossSpeedMps':250},
]
state="()=>JSON.stringify({tick:__NAVAL_SIM_DIAG__.snapshot(),operation:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),world:__AEGIS_ENGAGEMENT_RUNTIME__.world,tracks:[...__AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.trackManager.tracks],rng:__HARPOON_DIAG_A__.snapshot().rng},(k,v)=>v instanceof Map?[...v]:v instanceof Set?[...v]:v)"
base=R/'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html'
if not base.exists():base=R/'archive/v48/WIP_KAPPA_PIP_LOS_A'/base.name
raw=base.read_bytes();errors=[];checks={};records=[];start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 data=json.loads((H/'inputs.json').read_text())
 p.evaluate('x=>window.__ENV_D_PRIVATE__=new Function("DATA","SETTINGS","PROFILE","PRIVATE_SHIP",x.source)(x.input.data,x.input.settings,{}, {entityId:"ENV_PRIVATE",navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}})',{'source':source,'input':data})
 detached=[]
 for i,c in enumerate(cases):
  before=p.evaluate(state);detached.append(p.evaluate('c=>__ENV_D_PRIVATE__.runCase(c)',c));checks[str(i)+'.worldRngTickUnchanged']=before==p.evaluate(state)
 p.close()
 h=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',h);s=gzip.decompress(base64.b64decode(m[1])).decode();s=s.replace('\n  completeShipStartup();','\n'+helper+'\n  completeShipStartup();',1);z=gzip.compress(s.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(rows,separators=(',',':'))+h[m.end(1):]
 p=load_fleet(b,h.encode(),own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 for i,(c,q)in enumerate(zip(cases,detached)):
  native=p.evaluate('c=>__ENV_D_NATIVE__.runCase(c)',c)
  keys=['timeS','xM','yM','altitudeM','speedMps','mach']
  errorsM={k:max((abs(a[k]-b[k])for a,b in zip(q['samples'],native['samples'])),default=0)for k in keys}
  checks[str(i)+'.sampleCounts']=len(q['samples'])==len(native['samples'])
  checks[str(i)+'.trajectoryExact']=not any(errorsM.values())
  checks[str(i)+'.nativeOutcomeExact']=all(q[k]==native[k]for k in ['reason','outcome','success','lethal','damage','missionKills','fuzeMissM','rng','pk'])
  records.append({'condition':c,'private':q,'native':native,'maxError':errorsM});print(i,c,native['reason'],errorsM,flush=True)
 p.close();b.close()
checks['pageErrors0']=not errors
(E/'path-details.json.gz').write_bytes(gzip.compress(json.dumps(records,separators=(',',':')).encode(),9,mtime=0))
out={'pass':all(checks.values()),'checks':checks,'conditions':[{'condition':r['condition'],'maxError':r['maxError'],'reason':r['native']['reason'],'samples':len(r['native']['samples'])}for r in records],'errors':errors,'elapsedS':time.perf_counter()-start,'method':__doc__}
(E/'path.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'failed':[k for k,v in checks.items()if not v]}));sys.exit(0 if out['pass']else 1)
