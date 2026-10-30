"""Reproduce the two 300-shot release regressions without changing original inputs.
Uses original AIR target/native RF fixture, not the ideal ASM capsule.
Read-only telemetry is detached; no extra random draws or guidance overrides.
"""
from pathlib import Path
import json,gzip,sys,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
old=R/'Aegis_SIM_v48_WIP_FUZE_ZEM_A.html'
if not old.exists():old=R/'archive/v48/WIP_FUZE_ZEM_A'/old.name
files={'DZT':old,'HANDOFF':Path(json.loads((H/'build.json').read_text())['file'])}
helper=(R/'docs/missile/termination/A/live-fixture.js').read_text()+r'''
const lhReleaseDynA=updateSamSixDofLiteDynamics,lhReleaseUpdateA=updateMissile;
const lhReleaseRowsA=[];
updateSamSixDofLiteDynamics=function(m,dt,y,p,env){m._releaseInputA={yaw:y,pitch:p};return lhReleaseDynA(m,dt,y,p,env);};
updateMissile=function(m,dt){const q=lhReleaseUpdateA(m,dt);if(m===TERM_LIVE_LAST_MISSILE_A&&(m.life<8||m.life>160||simStepCounter%6===0)){const rf=m._arhRfSeeker;lhReleaseRowsA.push(JSON.parse(JSON.stringify({lifeS:m.life,positionM:[worldToMeters(m.x),worldToMeters(m.y),m.z],velocityMps:[worldSpeedToMps(m.vx),worldSpeedToMps(m.vy),m.vz],pitchover:!!m.pitchoverPhase,handoffAtS:m._pitchoverCompleteAt??null,gate:m._launchHandoffA??null,phase:m._v1GuidancePhase,owner:m._v1LaunchControlAuthority?'LAUNCH':m._wip79KappaActive?'KAPPA':m._v1TerminalActive?'TERMINAL':'OTHER',source:m._v1TargetState?.source,rf:{mode:rf?.mode,valid:rf?.trackValid,hitAgeS:rf?.lastHitAgeS},finalInput:m._releaseInputA,rawG:m._v1GCommand,limitedG:m._v1GAchieved,actualG:m.sam6dofActualNormalG,deliveredG:m.sam6dofDeliveredG,fuze:{detected:m._fuzeStage2Detected,prox:m.proxDetonated,burstMissM:m._fuzeBurstMissM,burstOffsetS:m._fuzeBurstOffsetS,processingDelayS:m._fuzeSignalLastA?.processingDelayS},closestRecordedM:m._everClosest==null?null:m._everClosest*1000,term:m._gameFlightTerm,dead:m.dead,reason:m._deathReason})));}return q;};
window.__LH_RELEASE_PROBE__={clear:()=>lhReleaseRowsA.length=0,read:()=>lhReleaseRowsA};
'''
original=json.loads((R/'docs/missile/termination/A/cases/normal.json').read_text())
cases=[original[152],original[153]];rows=[];errors=[];started=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for variant,file in files.items():
  reference=json.loads((R/'docs/missile/fuze-zem/A/evidence/release-DZT/normals.json' if variant=='DZT' else H/'final-evidence/release-HANDOFF/normals.json').read_text())['results']
  p=load_fleet(b,instrument(file.read_bytes(),helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000)
  for i,c in enumerate(cases):
   p.evaluate('__LH_RELEASE_PROBE__.clear()');r=p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',c);trace=p.evaluate('__LH_RELEASE_PROBE__.read()')
   exact=r==reference[152+i];assert exact,(variant,i,'observer changed original result')
   rows.append({'variant':variant,'condition':c,'result':r,'trace':trace,'observerPreservesEntireOriginalReturn':exact});print(variant,c['enabled'],r['success'],r['closestM'],flush=True)
  p.close()
 b.close()
o={'records':rows,'errors':errors,'elapsedS':time.perf_counter()-started,'method':__doc__,'selectedHtmlSha256':{v:hashlib.sha256(f.read_bytes()).hexdigest()for v,f in files.items()}}
(H/'final-results/release-regression.json.gz').write_bytes(gzip.compress(json.dumps(o,separators=(',',':')).encode(),9,mtime=0))
raise SystemExit(0 if not errors else 1)
