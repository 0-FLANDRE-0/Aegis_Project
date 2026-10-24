"""Final HTML read-only table/status and 120s simulation invariance checks."""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence'
sys.path[:0]=[str(R/'docs/pip/B'),str(R/'docs/helicopter/H')]
import browser_backend;browser_backend.install()
from browser import launch,load_fleet
sys.path.insert(0,str(R/'docs/missile/termination/A'));from verify_live import instrument
STATE='''()=>{const d=__NAVAL_SIM_DIAG__,keys=['id','kind','type','label','weaponType','guidanceCore','ownerSide','alive','dead','x','y','z','vx','vy','vz','heading','speed','speedMps','pitch','roll','life','maxLife','boosterSeparated','fuel','age'];function physical(x){if(Array.isArray(x))return x.map(physical);if(!x||typeof x!=='object')return x;return Object.fromEntries(keys.filter(k=>k in x&&['number','string','boolean'].includes(typeof x[k])).map(k=>[k,x[k]]));}return JSON.stringify({timeS:d.observerSnapshotC().worldTimeS,ship:d.exportOperationalStateV48Wip11A().ship,dynamics:d.shipDynamics(),entities:Object.fromEntries(Object.entries(__AEGIS_ENGAGEMENT_RUNTIME__.world.entities).map(([k,v])=>[k,Array.isArray(v)?physical(v):Object.fromEntries(Object.entries(v).map(([name,data])=>[name,physical(data)]))])),rng:__HARPOON_DIAG_A__.snapshot().rng})}'''
raw=(R/'Aegis_SIM_v48_WIP_ENV_D.html').read_bytes();beforeFile=R/'Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html'
if not beforeFile.exists():beforeFile=R/'archive/v48/WIP_KAPPA_PIP_LOS_A'/beforeFile.name
baseline=beforeFile.read_bytes();checks={};errors=[];records=[]
def unpack(raw):return gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)</script>',raw)[1])).decode()
old=unpack(baseline);new=unpack(raw);block=(H/'data-block.js').read_text()
checks['preexistingMainJsByteIdentical']=new.replace('\n'+block,'',1)==old
checks['oneDataBlock']=new.count('// ENV_D_DATA_BEGIN')==1 and new.count('// ENV_D_DATA_END')==1
assets=lambda b:[hashlib.sha256(base64.b64decode(s)).hexdigest()for s in re.findall(rb'data-c55-index="\d+">([^<]+)</script>',b)]
checks['other13AssetsByteIdentical']=assets(raw)[:13]==assets(baseline)[:13]
world=json.loads((E/'reg-k/world120.json').read_text());expected={r['mode']:r['truthSha256']for r in world['records']if r['version']=='current'}
with sync_playwright()as pw:
 b=launch(pw)
 for mode in ['idle','combat']:
  p=load_fleet(b,instrument(raw)if mode=='combat'else raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
  if mode=='idle':
   stateBefore=p.evaluate(STATE);status=p.evaluate('__ENV_D__.status()')
   checks['statusMatches']=status['match']and not status['recalculationRequired']and not status['changedNativeFunctions']and status['rows']==120
   checks['statusWorldRngTickUnchanged']=stateBefore==p.evaluate(STATE)
   checks['tableDetached']=p.evaluate('()=>{const a=__ENV_D__.table(),b=__ENV_D__.table();a.rows[0].maxRangeKm=-100;return __ENV_D__.table().rows[0].maxRangeKm===b.rows[0].maxRangeKm;}')
   checks['captureDetached']=p.evaluate('()=>{const a=__ENV_D__.capture(),b=__ENV_D__.capture();a.seeds[0].rngSeed=1;a.models.SAM_LOFT_B4_PROFILES={};return JSON.stringify(__ENV_D__.capture())===JSON.stringify(b);}')
   (E/'status.json').write_text(json.dumps(status,indent=2)+'\n')
   p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(7200)')
  else:
   c={'weapon':'SM6','rangeKm':100,'bearingDeg':45,'seed':12002,'enabled':True}
   p.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c);p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');launch=p.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c);checks['combatNativeRelease']=bool(launch.get('launched'));p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(6300)')
  state=p.evaluate(STATE);sha=hashlib.sha256(state.encode()).hexdigest();checks[mode+'120UnchangedFromKappa']=sha==expected[mode]
  checks[mode+'.core0']=p.evaluate('__CORE_SELFTEST_FAILURES__.length===0');records.append({'mode':mode,'truthSha256':sha,'baselineTruthSha256':expected[mode]});p.close()
 # The table describes missiles, not the selected Aegis hull. Switching to
 # CG-52 must not invalidate it through selected ship geometry/runtime state.
 p=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',errors=errors)
 cgBefore=p.evaluate(STATE);cgStatus=p.evaluate('__ENV_D__.status()')
 checks['cgStatusMatches']=cgStatus['match'] and cgStatus['rows']==120 and not cgStatus['changedNativeFunctions']
 checks['cgStatusReadOnly']=cgBefore==p.evaluate(STATE)
 records.append({'mode':'cg-status','status':cgStatus});p.close()
 b.close()
checks['pageErrors0']=not errors
result={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'method':__doc__};(E/'delivery-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'failed':[k for k,v in checks.items()if not v]}));sys.exit(0 if result['pass']else 1)
