"""Unmodified E bytes: real CIC mouse/touch input, immutable programs and launch/reset/save boundaries."""
import argparse,base64,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
ap=argparse.ArgumentParser();ap.add_argument('html');ap.add_argument('out');a=ap.parse_args();source=Path(a.html);body=source.read_bytes();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
checks={};details={};errors=[];console=[]
def check(k,v):checks[k]=bool(v)
def state(p):return p.evaluate('''()=>({draft:window.__HARPOON_DIAG_A__.routeDraft(),deck:window.__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot(),snapshot:window.__HARPOON_DIAG_A__.snapshot()})''')
with sync_playwright()as pw:
 b=launch(pw);p=load(b,body,errors=errors);p.on('console',lambda m:console.append(m.text)if m.type=='error'else None)
 p.evaluate('window.__HARPOON_DIAG_A__.forgetCombatTracksDiagnostic()');p.locator('#modeAimBtn').click()
 if p.locator('#armSubVlsBtn').is_visible():p.locator('#armSubVlsBtn').click()
 before=state(p);p.locator('#harpoonRouteE').click();p.mouse.click(450,260);p.mouse.click(550,330);after=state(p);details['actualTwoMapTaps']={'before':before,'after':after}
 check('actualButtonEntersDesignationAndTwoTapsAppendInOrder',after['draft']['editing']and len(after['draft']['pointsM'])==2 and after['draft']['pointsM'][0]!=after['draft']['pointsM'][1])
 check('designationLeavesLockCursorAndOwnshipNavigationUntouched',before['deck']['state']==after['deck']['state'])
 check('designationOnlyNeverFires',not after['snapshot']['missiles']and after['snapshot']['pending']is None)
 p.mouse.move(400,200);p.mouse.down();p.mouse.move(460,225,steps=5);p.mouse.up();p.mouse.wheel(0,-150);p.wait_for_timeout(100)
 check('dragAndWheelDoNotPlaceWaypoints',state(p)['draft']==after['draft'])
 cdp=p.context.new_cdp_session(p)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':400,'y':220,'id':1},{'x':520,'y':300,'id':2}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':380,'y':210,'id':1},{'x':540,'y':310,'id':2}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[{'x':380,'y':210,'id':1}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 check('actualTwoFingerPinchDoesNotPlaceWaypoints',state(p)['draft']==after['draft'])
 p.locator('#harpoonRouteE').click();cancel=state(p);p.mouse.click(540,350);resumed=state(p);details['cancelCursor']={'cancel':cancel,'resumed':resumed}
 check('cancelClearsMarkersAndExitsEditing',cancel['draft']=={'editing':False,'pointsM':[]}and p.locator('#harpoonRouteE').inner_text()=='웨이포인트 지정')
 check('normalAimTapMovesLockCursorAgain',resumed['deck']['state']['lockCursor']!=cancel['deck']['state']['lockCursor']and not resumed['draft']['pointsM'])
 p.locator('#harpoonRouteE').click();p.mouse.click(410,240);p.mouse.click(550,300);program=state(p);details['beforeFire']=program;details['beforeFireGate']=p.evaluate('window.__HARPOON_DIAG_A__.autoTube()');(out/'partial.json').write_text(json.dumps(details,ensure_ascii=False,indent=2));print(json.dumps({'beforeFire':details['beforeFireGate'],'checks':checks}),flush=True)
 assert details['beforeFireGate']['ok'],details['beforeFireGate']
 p.locator('#harpoonFireA').click();pending=state(p);p.locator('#harpoonRouteE').evaluate('(e)=>e.click()');blocked_edit=state(p)
 check('doorOpeningPinsTubeAndBlocksRouteEdits',pending['snapshot']['pending']is not None and blocked_edit['draft']==pending['draft']and p.locator('#harpoonRouteE').is_disabled())
 p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(12);window.__HARPOON_DIAG_A__.refreshUi()');first=state(p);details['firstRelease']={'program':program,'pending':pending,'released':first}
 check('successfulReleasePinsWholeProgram',first['snapshot']['missiles'][0]['route']['program']==pending['snapshot']['pending']['routeProgram'])
 check('successfulReleaseCopiesExactPointsAndClearsDraft',len(first['snapshot']['missiles'])==1 and first['snapshot']['missiles'][0]['route']['program']['pointsM']==program['draft']['pointsM']and first['draft']=={'editing':False,'pointsM':[]})
 check('firstMissileSeekerStillOffBeforeLastWaypoint',first['snapshot']['missiles'][0]['seeker']['mode']=='OFF')
 check('releasedRoundHasNoDatalinkOrTruthProgram',first['snapshot']['missiles'][0]['route']['program']['dataLink']is False and not first['snapshot']['missiles'][0]['memory']['truthUsed'])
 p.locator('#harpoonRouteE').click();p.mouse.click(400,400);p.mouse.click(550,460);second_draft=state(p)
 check('freshDraftDoesNotMutateAirborneProgram',second_draft['snapshot']['missiles'][0]['route']['program']==first['snapshot']['missiles'][0]['route']['program']and second_draft['draft']['pointsM']!=program['draft']['pointsM'])
 p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(92);window.__HARPOON_DIAG_A__.refreshUi()');p.locator('#harpoonFireA').click();p.evaluate('window.__HARPOON_DIAG_A__.fixedTicks(12);window.__HARPOON_DIAG_A__.refreshUi()');second=state(p);details['secondRelease']=second
 check('nextAutomaticTubeGetsIndependentRoute',len(second['snapshot']['missiles'])==2 and second['snapshot']['missiles'][0]['tubeId']!=second['snapshot']['missiles'][1]['tubeId']and second['snapshot']['missiles'][1]['route']['program']['pointsM']==second_draft['draft']['pointsM']and not second['draft']['pointsM'])
 check('shipPictureHasNoLaunchOnlyPositionOrRouteProgress',p.evaluate('window.__HARPOON_DIAG_A__.operatorPicture().launches.every(q=>q.trackId==null)'))
 # Declared API inputs only; no changes to guidance/seeker physics. Repeated click points
 # are covered above; these fixtures isolate budget, authority, cancellation and imports.
 gate_cases=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;h.reset(true);h.forgetCombatTracksDiagnostic();h.routeToggle();
  const close=h.routeAdd({x:10,y:0});h.routeAdd({x:90000,y:0});h.routeAdd({x:90000,y:60000});const over=h.autoTube(),overRequest=h.fire();
  h.reset(true);h.routeToggle();h.routeAdd({x:4000,y:0});const manual=h.autoTube(),automatic=h.autoTube(null,{automatic:true});
  const request=h.fire(),pinned=h.snapshot().pending;d.wip101SetModuleDamage('Mk 141('+request.tubeId.split('-')[1][0]+')',100);h.focusedTicks(12);
  const cancelled=h.snapshot(),retained=h.routeDraft();d.wip101SetModuleDamage('Mk 141(A)',0);d.wip101SetModuleDamage('Mk 141(B)',0);
  return {close,over,overRequest,manual,automatic,request,pinned,cancelled,retained};}''');details['gates']=gate_cases
 check('tooCloseAndRouteTotalBudgetRejected',gate_cases['close']['reason']=='WAYPOINT_TOO_CLOSE'and gate_cases['over']['reason']=='ROUTE_EXCEEDS_140KM_BUDGET'and not gate_cases['overRequest']['ok'])
 check('coordinateFireRequiresManualAuthority',gate_cases['manual']['ok']and gate_cases['automatic']['reason']=='MANUAL_SURFACE_AUTHORITY_REQUIRED')
 check('damageDuringDoorOpeningCancelsWithoutAmmoLossAndRetainsDraft',not gate_cases['cancelled']['missiles']and all(t['loaded']for t in gate_cases['cancelled']['inventory']['tubes'])and len(gate_cases['retained']['pointsM'])==1)
 saves=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__,saved=d.exportOperationalStateV48Wip11A();
  saved.profileRevision='BUNKERHILL_HARPOON_C_1';const imported=d.importOperationalStateV48Wip11B(saved);return {imported,draft:h.routeDraft(),snapshot:h.snapshot(),capabilities:saved.capabilities};}''');details['legacyCImport']=saves
 check('explicitLegacyCImportClearsTransientRoute',saves['draft']=={'editing':False,'pointsM':[]}and not saves['snapshot']['missiles']and saves['snapshot']['pending']is None)
 check('saveDeclaresRoutesTransient', 'harpoonPrelaunchRouteAndFlight'in saves['capabilities']['deferred'])
 protected=p.evaluate('''()=>{const d=window.__NAVAL_SIM_DIAG__,h=window.__HARPOON_DIAG_A__;d.setEmcon(false);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:0});
  const t=d.wip13b9StepSurfaceSensors(1200).audit.surfaceTracks.find(t=>t.confirmed);h.select(t.trackId);h.routeToggle();h.routeAdd({x:6000,y:0});const rows={};
  for(const id of ['FRIEND','NEUTRAL','UNKNOWN']){d.a3SetOperatorIdentity(t.trackId,id);rows[id]=h.fire();}h.reset(true);h.refreshUi();return rows;}''');details['protected']=protected
 check('selectedProtectedSurfaceTrackStillBlocksCoordinateRelease',all(not r['ok']for r in protected.values()))
 reset=state(p);check('resetRestoresInventoryAndClearsEditingAndFlight',reset['draft']=={'editing':False,'pointsM':[]}and not reset['snapshot']['missiles']and all(t['loaded']for t in reset['snapshot']['inventory']['tubes']))
 ddg=load(b,body,ship='DDG_119_LATE_FLIGHT_IIA',errors=errors)
 check('ddg119UnchangedNoHarpoonOrRouteControls',ddg.evaluate('''()=>{const h=window.__HARPOON_DIAG_A__;return document.getElementById('harpoonControlsA').hidden&&!h.routeToggle()&&!h.snapshot().inventory.tubes.length&&window.__CORE_SELFTEST_FAILURES__.length===0;}'''))
 check('cgCoreSelftestsPass',p.evaluate('window.__CORE_SELFTEST_FAILURES__')==[])
 b.close()
check('pageErrorsZero',not errors);check('consoleErrorsZero',not console)
report={'schema':'HARPOON_E_ROUTE_UI_VERIFICATION','source':source.name,'sha256':hashlib.sha256(body).hexdigest(),'fixtureBridge':False,'checks':checks,'details':details,'errors':errors,'console':console,'pass':all(checks.values())}
(out/'routes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'pass':report['pass'],'errors':errors,'console':console},ensure_ascii=False));raise SystemExit(0 if report['pass']else 1)
