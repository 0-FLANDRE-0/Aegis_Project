"""Remaining command, source and prelaunch-only mutation acceptance."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
from verify_map import FIXTURE,STATE
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v)
def close(p):p.evaluate("()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k)}");p.wait_for_timeout(300)
def obj(p,key):return next(o for o in p.evaluate('__MAP_A__.objects()')if o['key']==key)
def click(p,key):
 close(p);o=obj(p,key);q=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o);p.mouse.click(q['x'],q['y']);p.wait_for_timeout(50)
 if p.evaluate('__MAP_A__.snapshot().candidatesOpen'):p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click()
 return o
with sync_playwright()as pw:
 b=launch(pw);original=b.new_page
 def page(**kw):
  p=original(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('fixture'))");return p
 b.new_page=page;p=load_fleet(b,raw,width=1400,height=900,ally='DDG_119_LATE_FLIGHT_IIA',errors=errors);f=p.evaluate(FIXTURE);p.evaluate('__VIEWPORT_A__.setDistance(40)');p.evaluate('__NAVAL_SIM_DIAG__.setEmcon(false)');first=obj(p,'TRACK:'+str(f['id']));second=p.evaluate("__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:15,bearingDeg:45,altM:50,speedMps:0})");click(p,'TRACK:'+str(second));before=p.evaluate(STATE);p.locator('#mapPrecisionA').click();ck('G.coincidentExactId',p.evaluate('__EMCON_DESIGNATION_F2__.snapshot().selectedLockId')==second)
 p.evaluate('id=>__NAVAL_SIM_DIAG__.wip118DiagDropTrack(id)',second);click(p,'TRACK:'+str(f['id']));prior=p.evaluate(STATE);p.evaluate("document.getElementById('lockBtn').click()");ck('K.bridgeNativeManualLock',p.evaluate('__EMCON_DESIGNATION_F2__.snapshot().selectedLockId')==f['id']);ck('K.viewDidNotLockOther',prior['selectedLockId']==second)
 p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(180)');allies=[o for o in p.evaluate('__MAP_A__.objects()')if o['kind']=='ALLY'];ck('ally.receivedSelf',bool(allies));
 if allies:
  click(p,allies[0]['key']);ck('ally.controlDisabled',p.locator('#mapControlA').is_disabled()and'항로 명령 미지원'in p.locator('#uiWindowA-INFO').inner_text());ck('ally.noPrecisionOrID',not p.locator('#mapPrecisionA').count()and not p.locator('#mapIdentityA').count());p.screenshot(path=str(a.out/'info-ally.png'));close(p);o=obj(p,allies[0]['key']);q=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o);p.mouse.click(q['x'],q['y'],button='right')
  if p.evaluate('__MAP_A__.snapshot().candidatesOpen'):p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click()
  p.screenshot(path=str(a.out/'menu-ally.png'));p.keyboard.press('Escape')
 # A native own-weapon launch then immutable Harpoon INS/route, not synthetic BDA.
 p.evaluate("__HARPOON_DIAG_A__.forgetCombatTracksDiagnostic();__NAVAL_SIM_DIAG__.setEmcon(true);document.getElementById('modeAimBtn').click();__HARPOON_DIAG_A__.routeToggle();__HARPOON_DIAG_A__.routeAdd({x:4000,y:-2000});__HARPOON_DIAG_A__.routeAdd({x:10000,y:-4000});")
 request=p.evaluate('__HARPOON_DIAG_A__.fire()');ck('F.nativeRouteReleaseRequest',request['ok']);p.evaluate('__HARPOON_DIAG_A__.focusedTicks(30)');flight=p.evaluate('__HARPOON_DIAG_A__.snapshot().missiles');ck('F.actualMissile',len(flight)==1)
 if flight:
  memory={k:flight[0][k]for k in ['id','memory','ins','route']};records['flightBefore']=memory;p.evaluate('__HARPOON_DIAG_A__.routeToggle();__HARPOON_DIAG_A__.routeAdd({x:7000,y:-10000});__HARPOON_DIAG_A__.routeAdd({x:14000,y:-15000});');p.wait_for_timeout(300);n=p.evaluate('__HARPOON_DIAG_A__.routeDraft().pointsM.length');p.locator('#mapUndoA').click();ck('F.draftOnlyUndo',p.evaluate('__HARPOON_DIAG_A__.routeDraft().pointsM.length')==n-1);after=p.evaluate('__HARPOON_DIAG_A__.snapshot().missiles[0]');ck('F.frozenMemoryINSRouteUnchanged',memory=={k:after[k]for k in memory});records['flightAfter']={k:after[k]for k in memory}
  # Only launch receipt data, no live position, phase, seeker or derived flight fix.
  p.evaluate('id=>__MAP_A__.receipt(id)',flight[0]['id']);receipt=p.evaluate('__MAP_A__.snapshot()');ck('receipt.noPosition',not any(k in receipt['object']for k in ['x','y','z','positionM','ins','phase','seeker']));ck('receipt.releaseAndPlan',receipt['object']['releaseAtS']is not None and len(receipt['object']['route'])==2);ck('receipt.noDLMessage','데이터링크 없음'in p.locator('#uiWindowA-INFO').inner_text());p.screenshot(path=str(a.out/'info-harpoon-receipt.png'));records['receipt']=receipt
 p.evaluate('__HARPOON_DIAG_A__.routeToggle()');click(p,'OWN');p.locator('#mapControlA').click();close(p)
 # Multi-waypoint object hit and deletion support; arbitrary deletion remains disabled.
 p.evaluate("document.getElementById('modeNavBtn').click();document.getElementById('clearRouteBtn').click()");v=p.evaluate('AEGIS_VIEWPORT.twoD');p.mouse.click(v['cx']-180,v['cy']-130);p.mouse.click(v['cx']-100,v['cy']-180);wps=[o for o in p.evaluate('__MAP_A__.objects()')if o['kind']=='WP'];click(p,wps[0]['key']);ck('waypoint.nonLastDisabled',p.locator('#mapDeletePointA').is_disabled() and'마지막 점만 취소 가능'in p.locator('#uiWindowA-INFO').inner_text());n=len(p.evaluate(STATE)['ships']);click(p,wps[-1]['key']);p.locator('#mapDeletePointA').click();ck('waypoint.lastDeletesOne',len(p.evaluate(STATE)['ships'])==n-1)
 # Info source/provenance audit: getters on truth metadata and Helo RF internals.
 tid=p.evaluate('__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:15,bearingDeg:35,speedMps:0})');audit=p.evaluate("""tid=>{const r=__AEGIS_ACTIVE_SHIP_RUNTIME__,tr=r.combatSystem.trackManager.tracks.get(tid),h=__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.helicopters.values().next().value;let reads=0;const descriptors=['truthRef','associationDomain'].map(k=>[k,Object.getOwnPropertyDescriptor(tr,k)]);for(const[k]of descriptors)Object.defineProperty(tr,k,{configurable:true,get(){reads++;throw Error('TRUTH_READ')}});const hs=Object.getOwnPropertyDescriptor(h,'sensorsE');Object.defineProperty(h,'sensorsE',{configurable:true,get(){reads++;throw Error('PRIVATE_RF_READ')}});try{__MAP_A__.objects();__MAP_A__.snapshot();}finally{for(const[k,d]of descriptors){delete tr[k];if(d)Object.defineProperty(tr,k,d);}delete h.sensorsE;if(hs)Object.defineProperty(h,'sensorsE',hs);}return reads;}""",tid);ck('I.noTruthOrPrivateRFReads',audit==0)
 # Link-independent explicit ISAR targeting of a surface measurement, not map navigation.
 p.evaluate("()=>{const h=__HELO__.snapshot().aircraft[0],live=__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.helicopters.get(h.id);live.visible=true;live.onboard=false;live.state='TRANSIT';live.positionM={x:-8000,y:-8000,z:300};__HELO__.command(h.id,'SET_RADAR_MODE',{mode:'ISAR'});}");h=next(o for o in p.evaluate('__MAP_A__.objects()')if o['kind']=='HELO');click(p,h['key']);p.locator('#mapControlA').click();tr=p.evaluate('id=>{const t=__AEGIS_ACTIVE_SHIP_RUNTIME__.combatSystem.trackManager.tracks.get(id);t.classification="SURFACE";t.domain="SURFACE";return t.trackId}',tid);click(p,'TRACK:'+str(tid));ck('ISAR.buttonVisible',p.locator('#mapIsarA').count()==1);n=len(p.evaluate(STATE)['helo'][0]['route']);p.locator('#mapIsarA').click();ck('ISAR.doesNotAppendRoute',len(p.evaluate(STATE)['helo'][0]['route'])==n)
 # Docked info stays present when NONE clears a selection.
 p.locator('#uiWindowA-INFO').evaluate('e=>e.dataset.audit="docked"');p.evaluate('__UI_A__.dock("INFO","right")');p.locator('#mapReleaseControlA').count() # Track lookup has no control release; select controlled helo first.
 click(p,h['key']);p.locator('#mapReleaseControlA').click();close(p);p.evaluate('__UI_A__.open("INFO");__UI_A__.dock("INFO","right")');p.wait_for_timeout(350);v=p.evaluate('AEGIS_VIEWPORT.twoD');p.mouse.click(v['cx']-v['w']*.3,v['cy']+v['h']*.33);ck('info.dockedNoneStays',p.evaluate('__UI_A__.snapshot().windows.INFO.open')and p.evaluate('__MAP_A__.snapshot().lookupTarget')is None)
 ck('core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));p.close();b.close()
ck('pageErrors',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'additional.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
