"""Native measurement/source examples and target-specific menus; no command on open."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v)
def close(p):p.evaluate("()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k);document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))}");p.wait_for_timeout(220)
def pick(p,o,right=False):
 close(p)
 if o['kind']=='ESM':
  own=p.evaluate('__VIEWPORT_A__.snapshot().twoD.ownship');q={'x':own['x']+math.cos(o['bearingRad'])*180,'y':own['y']+math.sin(o['bearingRad'])*180}
 else:q=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o)
 p.mouse.click(q['x'],q['y'],button='right'if right else'left');p.wait_for_timeout(60)
 if p.evaluate('__MAP_A__.snapshot().candidatesOpen'):p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click()
 return q
import math
with sync_playwright()as pw:
 b=launch(pw);old=b.new_page
 def page(**kw):
  p=old(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('fixture'))");return p
 b.new_page=page;p=load_fleet(b,raw,width=1400,height=900,ally='DDG_119_LATE_FLIGHT_IIA',errors=errors);p.evaluate("()=>{const d=__NAVAL_SIM_DIAG__;d.setTerrainDiagBypass(true);d.setEmcon(false);document.getElementById('clearRouteBtn').click();__VIEWPORT_A__.setDistance(40);d.createWip13aSurfaceTargetFixture({rangeKm:8,bearingDeg:0,headingDeg:90,speedKt:0});d.wip13b9StepSurfaceSensors(1200);}");objects=p.evaluate('__MAP_A__.objects()');track=next(o for o in objects if o['kind']=='TRACK'and o['classification']=='SURFACE');pick(p,track);ck('example.nativeRadarSources',any('SPY'in q['name']or'SPQ'in q['name']or'BRIDGEMASTER'in q['name']for q in track['local']));p.screenshot(path=str(a.out/'info-radar-native.png'));records['radar']=p.evaluate('__MAP_A__.snapshot()');pick(p,track,True);p.screenshot(path=str(a.out/'menu-track.png'))
 p.evaluate('__NAVAL_SIM_DIAG__.setEmcon(true)');pick(p,track);p.screenshot(path=str(a.out/'info-emcon-native.png'));ck('example.emconActiveBlocked',p.locator('#mapPrecisionA').is_disabled());close(p)
 p.evaluate("()=>{const h=__HELO__.snapshot().aircraft[0],q=__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.helicopters.get(h.id);q.onboard=false;q.visible=true;q.state='ARRIVED_HOVER';q.positionM={x:0,y:-3000,z:150};q.holdPointM={x:0,y:-3000,z:150};q.targetAltitudeM=150;}");p.evaluate("()=>{const d=__NAVAL_SIM_DIAG__,r=__AEGIS_ACTIVE_SHIP_RUNTIME__;d.offboardDiagnosticC(r.entityId,{link:{sourceId:'H1',connected:true,latencyS:0}});for(let i=1;i<=3;i++){d.offboardDiagnosticC(r.entityId,{report:{schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'H1',sequence:900+i,measuredAtS:d.observerSnapshotC().worldTimeS,positionM:{x:-12000,y:-14000,z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:.01,background:.01}}});d.stepTicks(1);}d.stepTicks(180);}");objects=p.evaluate('__MAP_A__.objects()');linked=next(o for o in objects if o['kind']=='TRACK'and o['remote']);pick(p,linked);p.screenshot(path=str(a.out/'info-link-native.png'));records['link']=p.evaluate('__MAP_A__.snapshot()');ck('example.linkH1','H1'in p.locator('#uiWindowA-INFO').inner_text())
 objects=p.evaluate('__MAP_A__.objects()');esm=next(o for o in objects if o['kind']=='ESM');pick(p,esm);p.screenshot(path=str(a.out/'info-esm-native.png'));records['esm']=p.evaluate('__MAP_A__.snapshot()');pick(p,esm,True);p.screenshot(path=str(a.out/'menu-esm.png'))
 ally=next(o for o in objects if o['kind']=='ALLY');pick(p,ally);p.screenshot(path=str(a.out/'info-ally-native.png'));pick(p,ally,True);p.screenshot(path=str(a.out/'menu-ally.png'))
 p.evaluate("()=>{const h=__HELO__.snapshot().aircraft[0],q=__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.helicopters.get(h.id);q.visible=true;q.onboard=false;q.state='TRANSIT';q.positionM={x:5000,y:-7000,z:50};}");helo=next(o for o in p.evaluate('__MAP_A__.objects()')if o['kind']=='HELO');pick(p,helo);p.screenshot(path=str(a.out/'info-helicopter-native.png'));pick(p,helo,True);p.screenshot(path=str(a.out/'menu-helicopter.png'))
 # The pen barrel may arrive as a chorded pointermove rather than a second down.
 close(p);v=p.evaluate('AEGIS_VIEWPORT.twoD');q={'x':v['cx']-v['w']*.25,'y':v['cy']+v['h']*.25};before=p.evaluate('__MAP_A__.snapshot().counts');p.locator('#c').dispatch_event('pointermove',{'pointerId':50,'pointerType':'pen','button':-1,'buttons':2,'isPrimary':True,'clientX':q['x'],'clientY':q['y']});ck('pen.chordedMoveMenu',p.evaluate('__MAP_A__.snapshot().menuOpen||__MAP_A__.snapshot().candidatesOpen'));ck('pen.noCommands',before==p.evaluate('__MAP_A__.snapshot().counts'));p.keyboard.press('Escape')
 # Native fire supplies the own MSL STATUS data; no fabricated missile position.
 p.evaluate("()=>{const d=__NAVAL_SIM_DIAG__;d.setEmcon(false);__AEGIS_WIP14A14_ENGAGEMENT_UI__.selectionProbe(35);document.getElementById('external3DAutoLockBtn').click();document.getElementById('external3DFireBtn').click();d.stepTicks(1);}");msl=next(o for o in p.evaluate('__MAP_A__.objects()')if o['kind']=='MISSILE');pick(p,msl);ck('missile.statusFields',all(k in p.evaluate('__MAP_A__.snapshot().object')for k in ['phase','remainingS','targetTrackId']));p.screenshot(path=str(a.out/'info-own-missile.png'));pick(p,msl,True);p.screenshot(path=str(a.out/'menu-own-missile.png'))
 ck('core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));p.close();b.close()
ck('pageErrors',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/'examples.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
