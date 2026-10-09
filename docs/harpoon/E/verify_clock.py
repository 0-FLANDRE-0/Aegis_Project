"""Automatic selection and release through the full accumulator at 1/8/16/64x."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[1]/'bunkerhill/K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args()
source=Path(a.html);body=source.read_bytes();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];cases=[]
with sync_playwright()as pw:
 b=launch(pw)
 for scale in [1,8,16,64]:
  p=load(b,body,errors=errors)
  p.locator('#modeAimBtn').click()
  if p.locator('#armSubVlsBtn').is_visible():p.locator('#armSubVlsBtn').click()
  case=p.evaluate('''scale=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;
   d.setTerrainDiagBypass(true);h.forgetCombatTracksDiagnostic();h.routeToggle();h.routeAdd({x:4000,y:0});h.routeAdd({x:8000,y:0});
   const gate=h.autoTube(),request=h.fire();d.setTimeScale(scale);const run=d.runFramesToTicks(60,scale,3072),state=h.snapshot();
   d.ciwsB1Closure.setPaused(true);return {scale,gate,request,run,missiles:state.missiles,inventory:state.inventory,worldRng:state.rng,core:window.__CORE_SELFTEST_FAILURES__};}''',scale)
  cases.append(case);p.close();print(json.dumps({'scale':scale,'tube':case['request']['tubeId']}),flush=True)
 b.close()
signature=lambda c:json.dumps({k:c[k]for k in ['missiles','inventory','worldRng']},sort_keys=True)
checks={'eachScalePassesFinalWaypointAndStartsSearch':all(c['missiles'][0]['route']['completed']and c['missiles'][0]['seeker']['active']for c in cases),'fullAccumulatorAutoSelectionReleaseExactAt1_8_16_64':all(signature(c)==signature(cases[0])for c in cases),
 'allScalesReleaseExactlyOneChosenTube':all(c['request']['ok']and len(c['missiles'])==1 and c['missiles'][0]['tubeId']==c['gate']['tubeId']for c in cases),
 'allScalesCoreAndPageErrorsZero':all(c['core']==[]for c in cases)and not errors}
report={'schema':'HARPOON_E_CLOCK_VERIFICATION','source':source.name,'sha256':hashlib.sha256(body).hexdigest(),'seed':'0x6d2b79f5','ticksPerCase':3072,'checks':checks,'details':cases,'errors':errors,'pass':all(checks.values())}
(out/'clock.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'checks':checks,'pass':report['pass']}));raise SystemExit(0 if report['pass']else 1)
