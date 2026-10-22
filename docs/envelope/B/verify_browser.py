"""E2 live-world invariance and E3 native game-world vs detached capsule trace."""
import argparse,base64,gzip,hashlib,json,re,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
used={r['name']for r in json.loads((H/'dependencies.json').read_text())['rows']};boundary={k:v for k,v in json.loads((H/'boundaries.json').read_text()).items()if k in used};overrides=[]
for n,b in boundary.items():
 if b['code'].startswith('function '):overrides.append(n+'=('+b['code']+');')
fn_names=[n for n,v in boundary.items()if v['code'].startswith('function ')]
helper=(H/'private.js').read_text().split('return {runCase,profiles:')[0]+"\nwindow.__ENV_NATIVE_WORLD__={runCase(c){const saved={"+','.join(fn_names)+"};try{"+'\n'.join(overrides)+"selectedLockId=1;emconActive=false;engagementControlMode='MANUAL';shipNav.positionWorld.x=0;shipNav.positionWorld.y=0;shipNav.vx=shipNav.vy=shipNav.speed=0;return runCase(c);}finally{"+';'.join(n+'=saved.'+n for n in fn_names)+"}}};\n"

raw=a.html.read_bytes();html=raw.decode();m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);s=gzip.decompress(base64.b64decode(m[1])).decode();s=s.replace('\n  completeShipStartup();','\n'+helper+'\n  completeShipStartup();');instrumented=html[:m.start(1)]+base64.b64encode(gzip.compress(s.encode(),mtime=0)).decode()+html[m.end(1):]
# Loader integrity metadata must also describe the test-only instrumented world.
m=re.search(r'const records=(\[.*?\]);',instrumented,re.S);records=json.loads(m[1]);z=gzip.compress(s.encode(),mtime=0);records[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());instrumented=instrumented[:m.start(1)]+json.dumps(records,separators=(',',':'))+instrumented[m.end(1):]
checks={};errors=[];rows=[]
STATE="()=>JSON.stringify({tick:__NAVAL_SIM_DIAG__.snapshot(),operation:__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A(),mutation:__NAVAL_SIM_DIAG__.operationalImportMutationFingerprintV48Wip11B(),helicopters:__HELO__.snapshot(),world:__AEGIS_ENGAGEMENT_RUNTIME__.world,tracks:[...__AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.trackManager.tracks],links:__AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.weaponLinksB3},(k,v)=>v instanceof Map?[...v]:v instanceof Set?[...v]:v)"
with sync_playwright()as pw:
 b=launch(pw);p=load_fleet(b,raw,own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 capture=p.evaluate('__ENV_A__.capture()');(H/'inputs.json').write_text(json.dumps(capture,separators=(',',':')))
 before=p.evaluate(STATE);q=p.evaluate('__ENV_A__.case({weapon:"SM2",rangeKm:30,altM:5000})');after=p.evaluate(STATE);checks['E2.worldRngTickUnchanged']=before==after
 (a.out/'private-case.json').write_text(json.dumps(q,separators=(',',':')));p.close()
 p=load_fleet(b,instrumented.encode(),own='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 native=p.evaluate('__ENV_NATIVE_WORLD__.runCase({weapon:"SM2",rangeKm:30,altM:5000})');(a.out/'native-world-case.json').write_text(json.dumps(native,separators=(',',':')))
 keys=['timeS','xM','yM','altitudeM','speedMps','mach'];d={k:max(abs(x[k]-y[k])for x,y in zip(q['samples'],native['samples']))for k in keys};checks['E3.sameSampleCount']=len(q['samples'])==len(native['samples']);checks['E3.exactNativeTrajectory']=all(v==0 for v in d.values());checks['E3.sameNativeFuze']=q['success']==native['success']and q['reason']==native['reason']and q['fuzeMissM']==native['fuzeMissM'];rows={'maxError':d,'sampleCount':len(q['samples']),'worldHashBefore':hashlib.sha256(before.encode()).hexdigest(),'worldHashAfter':hashlib.sha256(after.encode()).hexdigest(),'privateSummary':{k:v for k,v in q.items()if k!='samples'},'nativeSummary':{k:v for k,v in native.items()if k!='samples'}};p.close();b.close()
checks['pageErrors']=not errors;result={'pass':all(checks.values()),'checks':checks,'records':rows,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'testOnlyInstrumentation':'native function bodies unchanged; ideal-support and stationary-platform boundaries replaced in a disposable real game page; its live world receives the native missile'};(a.out/'browser.json').write_text(json.dumps(result,indent=2));print(json.dumps({'pass':result['pass'],'checks':checks,'errors':errors,'maxError':rows['maxError']}));raise SystemExit(0 if result['pass']else 1)
