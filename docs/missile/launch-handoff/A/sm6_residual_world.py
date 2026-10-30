"""After-action-only SM-6 telemetry in the complete world; no model change."""
from pathlib import Path
import sys,json,gzip,time,hashlib
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[3];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=Path(json.loads((H/'build.json').read_text())['file']).read_bytes()
helper=(R/'docs/missile/termination/A/live-fixture.js').read_text()+r'''
const LH_RESIDUAL={ticks:[]};
const lrPn=computeTruePN3D,lrApn=computeAPNCorrectionV1,lrZem=computeZEMCorrectionV1,lrBridge=applyGuidanceKernelV1ToLegacyRates,lrBody=updateSamSixDofLiteDynamics,lrUpdate=updateMissile;
computeTruePN3D=function(m,...a){const q=lrPn(m,...a);m._lrPn={...q};return q;};
computeAPNCorrectionV1=function(m,...a){const q=lrApn(m,...a);m._lrApn={...q};return q;};
computeZEMCorrectionV1=function(m,...a){const q=lrZem(m,...a);m._lrZem={...q};return q;};
applyGuidanceKernelV1ToLegacyRates=function(m,y,p,dt){const q=lrBridge(m,y,p,dt);m._lrBridge={input:{yaw:y,pitch:p},output:{...q}};return q;};
updateSamSixDofLiteDynamics=function(m,dt,y,p,env){m._lrDynamicsInput={yaw:y,pitch:p};return lrBody(m,dt,y,p,env);};
updateMissile=function(m,dt){const q=lrUpdate(m,dt);if(m===TERM_LIVE_LAST_MISSILE_A){const t=targetPool[0],o=samNavB1OwnState(m),obs=m._v1TargetState,rf=s=>s?{mode:s.mode,valid:s.trackValid,hitAge:s.lastHitAgeS,confidence:s.confidence,estimate:s._kfX?[...s._kfX]:null}:null;LH_RESIDUAL.ticks.push(JSON.parse(JSON.stringify({timeS:m.life,positionM:[worldToMeters(m.x),worldToMeters(m.y),m.z],velocityMps:[worldSpeedToMps(m.vx),worldSpeedToMps(m.vy),m.vz],ownNav:o,phase:m._v1GuidancePhase,authority:m._v1GuidanceAuthority,launch:{vls:m.vlsPhase,pitchover:m.pitchoverPhase,handoffAt:m._pitchoverCompleteAt,gate:m._launchHandoffA,launchAuthority:m._v1LaunchControlAuthority,overlap:m._v1AllowLaunchGuidanceOverlap,blend:m._v1LaunchGuidanceBlend01},observation:obs?{source:obs.source,valid:obs.isValid,confidence:obs.confidence,posM:obs.posM,velMps:obs.velMps}:null,rf:{active:m.essmActiveSeeker,arh:rf(m._arhRfSeeker),sarh:rf(m._sarhRfSeeker),dlAlive:m.dlAlive,sarhAlive:m.sarhAlive},control:{pn:m._lrPn,apn:m._lrApn,zem:m._lrZem,bridge:m._lrBridge,final:m._lrDynamicsInput,rawG:m._v1GCommand,limitedG:m._v1GAchieved,availableG:m.availableG,actualNormalG:m.sam6dofActualNormalG,deliveredG:m.sam6dofDeliveredG,normalVector:m._samPrevNormalAccWorld,controlVector:m._v1ControlCommandVec,feedback:m._samFinAccelLoopActive},predictedCPA:m._v1PredCPA,predictedCpaTime:m._v1PredCPATime,fuze:{armed:m.proxArmed,detected:m._fuzeStage2Detected,signal:m._fuzeSignalLastA,burstMissM:m._fuzeBurstMissM,fragmentArrivalMissM:m._fuzeFragmentArrivalMissM,fragmentTimeS:m._fuzeFragmentFlightTimeS,burstOffsetS:m._fuzeBurstOffsetS,prox:m.proxDetonated},termination:m._gameFlightTerm,dead:m.dead,reason:m._deathReason,closestRecordedM:m._everClosest==null?null:m._everClosest*1000,AFTER_ACTION_TRUTH:t?{positionM:[worldToMeters(t.x),worldToMeters(t.y),t.z],velocityMps:[worldSpeedToMps(t.vx),worldSpeedToMps(t.vy),t.vz],alive:t.alive}:null})));}return q;};
window.__LH_RESIDUAL__={read:()=>LH_RESIDUAL.ticks};
''';rows=[];errors=[];start=time.perf_counter()
with sync_playwright()as pw:
 b=launch(pw)
 for enabled in [False,True]:
  p=load_fleet(b,instrument(raw,helper),own='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.set_default_timeout(240000);c={'weapon':'SM6','rangeKm':30,'bearingDeg':45,'enabled':enabled};p.evaluate('c=>__TERM_LIVE_TEST__.prepareObserved(c)',c);p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(900)');release=p.evaluate('c=>__TERM_LIVE_TEST__.launchObserved(c)',c);assert release.get('launched'),release
  for i in range(250):
   p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(120)');q=p.evaluate('__TERM_LIVE_TEST__.observe()')
   if q['dead']:break
  final=p.evaluate('__TERM_LIVE_TEST__.afterAction()');trace=p.evaluate('__LH_RESIDUAL__.read()');rows.append({'enabled':enabled,'release':release,'final':final,'trace':trace});p.close();print(enabled,final['missile']['reason'],final['missile']['lifeS'],len(trace),flush=True)
 b.close()
o={'htmlSha256':hashlib.sha256(raw).hexdigest(),'method':__doc__,'records':rows,'errors':errors,'elapsedS':time.perf_counter()-start};(H/'final-results/sm6-residual-world.json.gz').write_bytes(gzip.compress(json.dumps(o,separators=(',',':')).encode(),9,mtime=0));print(json.dumps({'errors':errors}));raise SystemExit(0 if not errors else 1)
