"""REG_K paired idle/combat whole-world 120s; no counterfactual tuning."""
from pathlib import Path
import hashlib,json,sys,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence/reg-k'
sys.path.insert(0,str(R/'docs/missile/termination/A'))
from verify_live import instrument
from browser import launch,load_fleet
FILES={'recovery':R/'archive/v48/WIP_RANGE_RECOVERY_A/Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html',
 'current':R/'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html'}
if not FILES['current'].exists():FILES['current']=R/'archive/v48/WIP_KAPPA_PIP_LOS_A'/FILES['current'].name
STATE='''()=>{const d=__NAVAL_SIM_DIAG__,keys=['id','kind','type','label','weaponType','guidanceCore','ownerSide','alive','dead','x','y','z','vx','vy','vz','heading','speed','speedMps','pitch','roll','life','maxLife','boosterSeparated','fuel','age'];function physical(x){if(Array.isArray(x))return x.map(physical);if(!x||typeof x!=='object')return x;return Object.fromEntries(keys.filter(k=>k in x&&['number','string','boolean'].includes(typeof x[k])).map(k=>[k,x[k]]));}return JSON.stringify({timeS:d.observerSnapshotC().worldTimeS,ship:d.exportOperationalStateV48Wip11A().ship,dynamics:d.shipDynamics(),entities:Object.fromEntries(Object.entries(__AEGIS_ENGAGEMENT_RUNTIME__.world.entities).map(([k,v])=>[k,Array.isArray(v)?physical(v):Object.fromEntries(Object.entries(v).map(([name,data])=>[name,physical(data)]))])),rng:__HARPOON_DIAG_A__.snapshot().rng})}'''
rows=[];errors=[];checks={};start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for mode in ['idle','combat']:
  for tag,file in FILES.items():
   raw=file.read_bytes();p=load_fleet(b,instrument(raw)if mode=='combat'else raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
   launchResult=None;ticks=0
   if mode=='combat':
    c={'weapon':'SM6','rangeKm':100,'bearingDeg':45,'seed':12002,'enabled':True}
    p.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c)
    p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');ticks=900
    launchResult=p.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
    while not launchResult.get('launched')and ticks<3600:
     p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(300)');ticks+=300
     launchResult=p.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
    if not launchResult.get('launched'):raise RuntimeError((tag,launchResult))
   p.evaluate('n=>__NAVAL_SIM_DIAG__.stepTicks(n)',7200-ticks)
   state=p.evaluate(STATE);core=p.evaluate('__CORE_SELFTEST_FAILURES__')
   after=p.evaluate('__TERM_LIVE_TEST__.afterAction()')if mode=='combat'else None
   (E/(tag+'-'+mode+'120-truth.json')).write_text(state)
   q={'version':tag,'mode':mode,'htmlSha256':hashlib.sha256(raw).hexdigest(),'truthSha256':hashlib.sha256(state.encode()).hexdigest(),'bytes':len(state.encode()),'ticks':7200,'preLaunchTicks':ticks,'launch':launchResult,'afterAction':after,'core':core}
   rows.append(q);p.close();print(tag,mode,q['truthSha256'],after,flush=True)
 b.close()
checks['idleSameTruthHash']=rows[0]['truthSha256']==rows[1]['truthSha256']
checks['core0']=all(not r['core']for r in rows);checks['pageErrors0']=not errors
out={'pass':all(checks.values()),'checks':checks,'records':rows,'errors':errors,'elapsedS':time.perf_counter()-start,'combatHashChanged':rows[2]['truthSha256']!=rows[3]['truthSha256'],'scope':'native complete fixed tick; physical world/inventory/RNG; excludes UI/performance; target AI retained'}
(E/'world120.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':checks,'combatHashChanged':out['combatHashChanged']}));sys.exit(0 if out['pass']else 1)
