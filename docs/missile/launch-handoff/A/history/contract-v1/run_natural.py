"""Unforced native onboard RF/EKF, controlled constant ASM target and ship cue."""
from pathlib import Path
import sys,json,gzip,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument,fixture
files={'DZT':R/'Aegis_SIM_v48_WIP_FUZE_ZEM_A.html','HANDOFF':Path(json.loads((H/'build.json').read_text())['file'])};cases=json.loads((R/'docs/missile/fuze-zem/A/natural-cases.json').read_text());rows=[];errors=[];start=time.perf_counter()
extra=r'''
const lhNativeDyn=updateSamSixDofLiteDynamics;
updateSamSixDofLiteDynamics=function(m,dt,y,p,env){const result=lhNativeDyn(m,dt,y,p,env);const key=[m.vlsPhase,m.pitchoverPhase,m._v1GuidancePhase,m._v1GuidanceAuthority,m.dead].join('/');if(m._lhNativeLast!==key){m._lhNativeLast=key;(m._lhNativeTrace??=[]).push(JSON.parse(JSON.stringify({lifeS:m.life,vls:m.vlsPhase,pitchover:m.pitchoverPhase,handoffAt:m._pitchoverCompleteAt??null,gate:m._pitchoverGate??null,owner:m._v1LaunchControlAuthority?'LAUNCH':m._wip79KappaActive?'KAPPA':m._v1TerminalActive?'TERMINAL':'GUIDANCE_OR_FALLBACK',guidance:m._v1GuidancePhase,source:m._v1GuidanceAuthority,actualG:m.sam6dofActualNormalG,deliveredG:m.sam6dofDeliveredG,limitedCommandG:m._v1GAchieved,feedback:m._samFinAccelLoopActive,bridgeToDynamics:{yaw:y,pitch:p}})));}return result;};
'''
helper=fixture();helper=helper.replace('return {diagnostic:diagCaseA,','return {handoffAtS:m._pitchoverCompleteAt??null,handoffTrace:m._lhNativeTrace??[],diagnostic:diagCaseA,',1)+extra
with sync_playwright()as pw:
 b=launch(pw)
 for variant,file in files.items():
  p=load_fleet(b,instrument(file.read_bytes(),helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000)
  for c in cases:
   q=p.evaluate('c=>__TERM_LIVE_TEST__.run(c)',c);rows.append({'variant':variant,'condition':c,'result':q});print(variant,c['caseId'],q.get('reason'),q.get('success'),q.get('closestM'),q.get('handoffAtS'),flush=True);(H/'results/natural.json.gz').write_bytes(gzip.compress(json.dumps({'rows':rows,'errors':errors,'elapsedS':time.perf_counter()-start},separators=(',',':')).encode(),9,mtime=0))
  p.close()
 b.close()
print(json.dumps({'flights':len(rows),'pageErrors':errors}));raise SystemExit(0 if not errors else 1)
