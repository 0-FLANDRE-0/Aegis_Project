"""Real ship-radar plots, launch association, EMCON, no-DL UI and lifecycle."""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parents[1]/'bunkerhill/K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args();source=Path(a.html);body=source.read_bytes();sha=hashlib.sha256(body).hexdigest();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);checks={};details={};errors=[]
def check(k,v):checks[k]=bool(v)
def setup(p):
 return p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:8});const t=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);d.a3SetOperatorIdentity(t.trackId,'TRAINING_TARGET');h.select(t.trackId);return t.trackId;}''')
with sync_playwright()as pw:
 b=launch(pw);p=load(b,body,errors=errors);tid=setup(p)
 p.locator('#modeAimBtn').click()
 if p.locator('#armSubVlsBtn').is_visible():p.locator('#armSubVlsBtn').click()
 p.evaluate('id=>window.__HARPOON_DIAG_A__.fire(id,\"MK141-A4\")',tid)
 p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(60)');initial=p.evaluate('window.__HARPOON_DIAG_A__.operatorPicture()');details['unobservedRelease']=initial
 check('noLaunchOnlyPositionOrTelemetry',initial['launches'][0]['positionM']is None and not initial['telemetryAvailable'])
 rows=[]
 for i in range(10):
  p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(60)')
  row=p.evaluate('''()=>{const h=window.__HARPOON_DIAG_A__,m=h.snapshot().missiles[0],st=window.get3DRenderState();return {ageS:m.ageS,truthPositionForDiagnosticOnly:m.positionM,picture:h.operatorPicture(),tracks:st.tacticalTracks.filter(t=>Math.hypot(t.worldXM-m.positionM.x,t.worldYM-m.positionM.y)<200)};}''');rows.append(row)
 details['sensorTrace']=rows;observed=[r for r in rows if r['picture']['launches'][0]['trackId']is not None];check('realRfEchoCreatesCorrelatedOwnRadarFile',len(observed)>=3)
 check('realOwnFileNeverHostile',all(t['identity']not in ['HOSTILE','ASSUMED_HOSTILE']for r in rows for t in r['tracks']))
 check('correlatedObservedFileIsFriend',all(any(t['identity']=='FRIEND'and t['ownLaunchId']==1 for t in r['tracks'])for r in observed))
 errorsM=[((r['picture']['launches'][0]['positionM']['x']-r['truthPositionForDiagnosticOnly']['x'])**2+(r['picture']['launches'][0]['positionM']['y']-r['truthPositionForDiagnosticOnly']['y'])**2)**.5 for r in observed];details['measuredErrorsM']=errorsM
 check('displayPositionIsMeasuredNotTruthExact',all(0<e<180 for e in errorsM))
 profile=p.evaluate('window.__HARPOON_DIAG_A__.profile()');check('profileHasNoDatalink',profile['dataLink']==False)
 p.evaluate('window.__HARPOON_DIAG_A__.refreshUi()');text=p.locator('#harpoonStatusA').inner_text();details['statusWithRadar']=text
 check('operatorStatusNoPrivateSeekerPhaseSpeed', 'NO DL'in text and 'RADAR'in text and not any(w in text for w in ['TRACK','TERMINAL_ARH','m/s','ACQUIRE']))
 # Actual canvas paint audit; no renderer/physics state is modified.
 p.evaluate('''()=>{window.__H_C_PAINT__=[];const c=document.getElementById('c').getContext('2d'),draw=c.fillText;c.fillText=function(text,...args){const a=window.__H_C_PAINT__;a.push({text:String(text),color:this.fillStyle});if(a.length>512)a.shift();return draw.call(this,text,...args);};}''')
 p.wait_for_function("window.__H_C_PAINT__.some(x=>x.text==='H1 RADAR')",timeout=15000)
 paint=p.evaluate("window.__H_C_PAINT__.filter(x=>x.text==='H1 RADAR')");details['actualCicPaint']=paint
 check('actualCicOwnLabelPaintsFriendlyCyan',paint and all(x['color'].startswith('rgba(90, 220, 245')or x['color'].startswith('#5adc')or x['color'].startswith('rgba(90,220,245')for x in paint))
 cdp=p.context.new_cdp_session(p);(out/'cic-own-radar.png').write_bytes(base64.b64decode(cdp.send('Page.captureScreenshot',{'format':'png','fromSurface':True})['data']))
 before=p.evaluate('window.__HARPOON_DIAG_A__.operatorPicture()');p.evaluate('window.__NAVAL_SIM_DIAG__.setEmcon(true)');p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(60)');coast=p.evaluate('window.__HARPOON_DIAG_A__.operatorPicture()');details['radarOffCoast']=coast
 check('radarOffUsesExplicitEstimate',coast['launches'][0]['source']=='ESTIMATE'and coast['launches'][0]['measurementAgeS']>.35)
 check('coastUncertaintyDoesNotShrink',coast['launches'][0]['positionSigmaM']>=before['launches'][0]['positionSigmaM'])
 p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(300)');blind=p.evaluate('window.__HARPOON_DIAG_A__.operatorPicture()');details['radarOffBlind']=blind
 check('expiredObservationsProvideNoFlightPosition',blind['launches'][0]['positionM']is None and blind['launches'][0]['trackId']is None)
 state=p.evaluate('window.__HARPOON_DIAG_A__.snapshot()');check('blindMissileKeepsIndependentInsArh',state['missiles'][0]['alive']and state['missiles'][0]['seeker']['mode']in ['TRACK','COAST'])
 p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(1500)');ended=p.evaluate('window.__HARPOON_DIAG_A__.snapshot()');p.evaluate('window.__HARPOON_DIAG_A__.refreshUi()');endedText=p.locator('#harpoonStatusA').inner_text();details['outcomeDiagnosticOnly']=ended['missiles'][0]['outcome'];details['statusAfterUnknownOutcome']=endedText
 check('unobservedImpactNotReportedAsTelemetry',ended['missiles'][0]['outcome']=='SURFACE_CONTACT'and 'H1'in endedText and '미관측'in endedText and '명중'not in endedText)
 saved=p.evaluate('window.__NAVAL_SIM_DIAG__.exportOperationalStateV48Wip11A()');oldB=p.evaluate("saved=>{const d=window.__NAVAL_SIM_DIAG__;saved.profileRevision='BUNKERHILL_HARPOON_B_1';return d.validateOperationalStateV48Wip11B(saved);}",saved);check('oldBInventorySaveExplicitlyAccepted',oldB['ok'])
 p.evaluate('saved=>window.__NAVAL_SIM_DIAG__.importOperationalStateV48Wip11B(saved)',saved);restored=p.evaluate('window.__HARPOON_DIAG_A__.operatorPicture()');check('operationalImportClearsCombatLaunchKnowledge',restored['launches']==[])
 p.close();p=load(b,body,errors=errors);tid=setup(p)
 p.evaluate('''id=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.setEmcon(true);h.fire(id,'MK141-A4');h.fixedTicks(900);}''',tid)
 noRadar=p.evaluate('''()=>{const h=window.__HARPOON_DIAG_A__,m=h.snapshot().missiles[0];return {m,picture:h.operatorPicture(),reflectors:window.__NAVAL_SIM_DIAG__.wip13a2PhysicalRfRegistryAudit('S').reflectors.filter(r=>r.id.startsWith('HARPOON:'))};}''');details['noRadarFlight']={'picture':noRadar['picture'],'ageS':noRadar['m']['ageS'],'seeker':noRadar['m']['seeker']['mode'],'reflectors':noRadar['reflectors']}
 check('noRadarProducesNoManufacturedOwnTrack',noRadar['picture']['launches'][0]['positionM']is None)
 check('noBlanketRfInvisibility',len(noRadar['reflectors'])==1 and noRadar['reflectors'][0]['rcsM2']>0)
 check('seekerStillOperatesWhenShipRadarOff',noRadar['m']['seeker']['mode']=='TRACK')
 check('coreSelfTestsZero',p.evaluate('window.__CORE_SELFTEST_FAILURES__')==[])
 p.close();p=load(b,body,errors=errors);p.locator('#modeAimBtn').click()
 route=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.setEmcon(false);d.setTerrainDiagBypass(true);h.forgetCombatTracksDiagnostic();h.routeToggle();h.routeAdd({x:4000,y:0});h.routeAdd({x:8000,y:0});
  const request=h.fire(),samples=[];for(let i=0;i<12;i++){h.fixedTicks(60);samples.push(h.operatorPicture());}return {request,samples,missile:h.snapshot().missiles[0]};}''');details['routeRadarAssociation']=route
 check('waypointLaunchCreatesOnlyMeasuredOwnRadarFile',route['request']['ok']and any(r['launches'][0]['trackId']is not None and r['launches'][0]['source']=='RADAR'for r in route['samples']))
 blindRoute=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.setEmcon(true);h.fixedTicks(360);return {picture:h.operatorPicture(),missile:h.snapshot().missiles[0]};}''');details['routeRadarOff']=blindRoute
 check('waypointMissileContinuesWithoutShipFlightPosition',blindRoute['picture']['launches'][0]['positionM']is None and blindRoute['missile']['alive']and blindRoute['missile']['route']['program']==route['missile']['route']['program'])
 b.close()
check('pageErrorsZero',not errors)
result={'schema':'HARPOON_E_SHIP_KNOWLEDGE_VERIFICATION','source':source.name,'sha256':sha,'checks':checks,'details':details,'errors':errors,'pass':all(checks.values())};(out/'knowledge.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':errors,'pass':result['pass']},ensure_ascii=False));raise SystemExit(0 if result['pass']else 1)
