"""Whole-world 120s combat hash: baseline / aligned / test-only eight-value restoration."""
import argparse,base64,gzip,hashlib,json,re,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(H));from build import EDITS
sys.path.insert(0,str(R/'docs/missile/termination/A'));from verify_live import instrument
from browser import launch,load_fleet
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
base=R/'archive/v48/WIP_ALL4_TERM/Aegis_SIM_v48_WIP_ALL4_TERM.html';current=a.candidate.read_bytes();h=current.decode();m=re.search(r'data-c55-index="13">(.*?)</script>',h,re.S);s=gzip.decompress(base64.b64decode(m[1])).decode()
for old,new in EDITS:assert s.count(new)==1;s=s.replace(new,old)
z=gzip.compress(s.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());restored=(h[:m.start(1)]+json.dumps(rs,separators=(',',':'))+h[m.end(1):]).encode()
STATE='''()=>{const d=__NAVAL_SIM_DIAG__,keys=['id','kind','type','label','weaponType','guidanceCore','ownerSide','alive','dead','x','y','z','vx','vy','vz','heading','speed','speedMps','pitch','roll','life','maxLife','boosterSeparated','fuel','age'];function physical(x){if(Array.isArray(x))return x.map(physical);if(!x||typeof x!=='object')return x;return Object.fromEntries(keys.filter(k=>k in x&&['number','string','boolean'].includes(typeof x[k])).map(k=>[k,x[k]]));}return JSON.stringify({timeS:d.observerSnapshotC().worldTimeS,ship:d.exportOperationalStateV48Wip11A().ship,dynamics:d.shipDynamics(),entities:Object.fromEntries(Object.entries(__AEGIS_ENGAGEMENT_RUNTIME__.world.entities).map(([k,v])=>[k,Array.isArray(v)?physical(v):Object.fromEntries(Object.entries(v).map(([name,data])=>[name,physical(data)]))])),rng:__HARPOON_DIAG_A__.snapshot().rng})}'''
rows=[];errors=[]
with sync_playwright()as pw:
 b=launch(pw)
 for name,raw in [('baseline',base.read_bytes()),('aligned',current),('restored8_test_only',restored)]:
  page=load_fleet(b,instrument(raw),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);c={'weapon':'SM6','rangeKm':100,'bearingDeg':45,'seed':12002,'enabled':True};page.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c);ticks=900;page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');launchResult=page.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
  while not launchResult.get('launched')and ticks<3600:
   page.evaluate('__NAVAL_SIM_DIAG__.stepTicks(300)');ticks+=300;launchResult=page.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c)
  assert launchResult.get('launched'),(name,launchResult)
  page.evaluate('n=>__NAVAL_SIM_DIAG__.stepTicks(n)',7200-ticks);state=page.evaluate(STATE);worldTimeS=page.evaluate('__NAVAL_SIM_DIAG__.observerSnapshotC().worldTimeS');core=page.evaluate('__CORE_SELFTEST_FAILURES__');after=page.evaluate('__TERM_LIVE_TEST__.afterAction()');page.close();(a.out/(name+'-truth.json')).write_text(state);row={'version':name,'htmlSha256':hashlib.sha256(raw).hexdigest(),'truthSha256':hashlib.sha256(state.encode()).hexdigest(),'bytes':len(state.encode()),'ticks':7200,'seconds':worldTimeS,'preLaunchTicks':ticks,'launch':launchResult,'afterAction':after,'core':core};rows.append(row);print(name,row['truthSha256'],after['missile']['reason'],flush=True)
 b.close()
checks={'all120Seconds':all(r['seconds']==120 for r in rows),'samePreLaunchTime':len({r['preLaunchTicks']for r in rows})==1,'restoringOnly8MatchesBaseline':rows[0]['truthSha256']==rows[2]['truthSha256'],'core0':all(not r['core']for r in rows),'pageErrors0':not errors};out={'pass':all(checks.values()),'checks':checks,'alignmentChangedCombatHash':rows[0]['truthSha256']!=rows[1]['truthSha256'],'records':rows,'errors':errors,'scope':'ownship physical state, inventory/dynamics, world-entity physical scalar fields, global RNG; excludes UI/presentation/performance caches','restorationOnlyInDisposableTestPage':True};(a.out/'causality120.json').write_text(json.dumps(out,indent=2));print(json.dumps({'pass':out['pass'],'checks':checks,'alignmentChangedCombatHash':out['alignmentChangedCombatHash']}));raise SystemExit(0 if out['pass']else 1)
