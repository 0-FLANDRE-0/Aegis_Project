"""MAP_A acceptance: native artifact + diagnostic fixtures, real client pointer events.
No gameplay functions replaced. Truth access only in test fixtures/audits/hash.
"""
import argparse,hashlib,importlib.util,json,math,random,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
STATE="""()=>{const r=__AEGIS_ACTIVE_SHIP_RUNTIME__,w=__AEGIS_ENGAGEMENT_RUNTIME__,e=__EMCON_DESIGNATION_F2__.snapshot();return {selectedLockId:e.selectedLockId,mode:e.mode,pdTracking:e.pdTracking,emcon:e.emcon,ships:__NAVAL_SIM_DIAG__.wip13cControlDeckSnapshot().state.routePoints,harpoon:__HARPOON_DIAG_A__.routeDraft(),fired:[w.world.entities.ordnance.length,w.world.entities.ramOrdnance.length,w.world.entities.antiShipOrdnance.length],helo:__HELO__.snapshot().aircraft.map(h=>({id:h.id,route:h.route,radarMode:h.radarMode,state:h.state}))};}"""
FIXTURE="""()=>{const d=__NAVAL_SIM_DIAG__;d.setTerrainDiagBypass(true);d.setEmcon(true);document.getElementById('clearRouteBtn').click();const id=d.wip114DiagAddTrack({rangeKm:15,bearingDeg:45,altM:50,speedMps:0});const esm=d.injectActiveSeekerEsmBearing({bearingDeg:165});return {id,esm};}"""
def main():
 ap=argparse.ArgumentParser();ap.add_argument('html',type=Path);ap.add_argument('out',type=Path);ap.add_argument('--part',choices=['input','invariance','legacy','3d'],required=True);ap.add_argument('--baseline',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True);raw=a.html.read_bytes();checks={};records={};errors=[];assertions=[]
 def ck(k,v):checks[k]=bool(v)
 def snap(p):return p.evaluate('__MAP_A__.snapshot()')
 def all_objects(p):return p.evaluate('__MAP_A__.objects()')
 def xy(p,o):return p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o)
 def close(p):p.evaluate("()=>{for(const id of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(id)}");p.wait_for_timeout(250)
 def settle(p,w,h):
  p.set_viewport_size({'width':w,'height':h});p.wait_for_function('([w,h])=>Math.abs(AEGIS_VIEWPORT.raw.w-w)<.1&&Math.abs(AEGIS_VIEWPORT.raw.h-h)<.1',arg=[w,h],polling=50);p.wait_for_timeout(350)
 def click_obj(p,key):
  close(p);o=next(x for x in all_objects(p)if x['key']==key);q=xy(p,o);p.mouse.click(q['x'],q['y']);p.wait_for_timeout(90)
  if snap(p)['candidatesOpen']:p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click()
  return o
 def sea(p):
  close(p);v=p.evaluate('AEGIS_VIEWPORT.twoD');spots=[{'x':v['x']+v['w']*.28,'y':v['y']+v['h']*.35},{'x':v['x']+v['w']*.7,'y':v['y']+v['h']*.72},{'x':v['x']+v['w']*.17,'y':v['y']+v['h']*.7}]
  return next(q for q in spots if not p.evaluate('p=>__MAP_A__.hitTest(p.x,p.y)',q))
 def capture(p,name):p.evaluate('__VIEWPORT_A__.draw()');p.screenshot(path=str(a.out/name))
 with sync_playwright()as pw:
  b=launch(pw,a.part=='3d');native=b.new_page
  def page(**kw):
   kw.update(device_scale_factor=2.8125,has_touch=True);p=native(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('geometry fixture'))");return p
  b.new_page=page
  if a.part=='input':
   for w,h in [(1400,900),(832,384),(384,832)]:
    tag=str(w);print('size',w,h,flush=True);p=load_fleet(b,raw,width=w,height=h,ally='DDG_119_LATE_FLIGHT_IIA',errors=errors);fixture=p.evaluate(FIXTURE);p.evaluate('__VIEWPORT_A__.setDistance(40)');close(p);p.wait_for_timeout(320);track=next(o for o in all_objects(p)if o['kind']=='TRACK');q=xy(p,track);before=p.evaluate(STATE)
    # Short-tap boundaries are CSS px independent of DPR/symbol scale.
    p.mouse.click(q['x']+19,q['y']);ck(tag+'.C.19px',snap(p)['lookupTarget']==track['key']);close(p);pt={'x':q['x']+21,'y':q['y']};p.mouse.click(pt['x'],pt['y']);ck(tag+'.C.21pxNone',snap(p)['lookupTarget']is None);ck(tag+'.D.noneHasNoCommand',p.evaluate(STATE)==before)
    p.mouse.move(q['x'],q['y']);p.mouse.down();p.mouse.move(q['x']+15,q['y'],steps=4);p.mouse.up();ck(tag+'.B.drag15NoSelection',snap(p)['lookupTarget']is None);ck(tag+'.B.dragNoRoute',p.evaluate(STATE)==before);p.evaluate('__VIEWPORT_A__.setPan(0,0)');p.wait_for_timeout(100);q=xy(p,track)
    p.mouse.move(q['x']-21,q['y']);p.mouse.down();p.mouse.move(q['x']-14,q['y'],steps=3);p.mouse.up();ck(tag+'.B.emptyToObjectNoAction',snap(p)['lookupTarget']is None)
    p.locator('#c').dispatch_event('pointerdown',{'pointerId':21,'pointerType':'touch','isPrimary':True,'button':0,'clientX':q['x'],'clientY':q['y']});p.locator('#c').dispatch_event('pointerdown',{'pointerId':22,'pointerType':'touch','isPrimary':False,'button':0,'clientX':q['x']+50,'clientY':q['y']});p.locator('#c').dispatch_event('pointerup',{'pointerId':22,'pointerType':'touch','isPrimary':False,'button':0,'clientX':q['x']+50,'clientY':q['y']});p.locator('#c').dispatch_event('pointerup',{'pointerId':21,'pointerType':'touch','isPrimary':True,'button':0,'clientX':q['x'],'clientY':q['y']});ck(tag+'.B.twoPointersNoSelection',snap(p)['lookupTarget']is None);p.mouse.click(q['x'],q['y']);ck(tag+'.B.postPinch300ms',snap(p)['lookupTarget']is None);p.wait_for_timeout(320)
    # Overlap uses a candidate list, never a command or silent best choice.
    id2=p.evaluate("()=>__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:15,bearingDeg:45,altM:50,speedMps:0})");close(p);p.mouse.click(q['x'],q['y']);ck(tag+'.C.overlapList',snap(p)['candidatesOpen']and len(snap(p)['candidateLabels'])==2);ck(tag+'.C.listNoCommand',p.evaluate(STATE)==before);p.locator('#mapCandidatesA button').first.click();ck(tag+'.C.chooseOpensInfo',snap(p)['lookupTarget']==track['key']);p.evaluate('id=>__NAVAL_SIM_DIAG__.wip118DiagDropTrack(id)',id2)
    # Control is explicit. Object taps retain it; empty sea appends exactly once.
    click_obj(p,'OWN');ck(tag+'.D.shipTapDoesNotControl',snap(p)['controlPlatform']is None);p.locator('#mapControlA').click();ck(tag+'.D.explicitControl',snap(p)['controlPlatform']=='OWN');pt=sea(p);n=len(p.evaluate(STATE)['ships']);p.mouse.click(pt['x'],pt['y']);ck(tag+'.D.oneWaypoint',len(p.evaluate(STATE)['ships'])==n+1);saved=snap(p)['lookupTarget'];click_obj(p,track['key']);ck(tag+'.D.objectNoWaypoint',len(p.evaluate(STATE)['ships'])==n+1 and snap(p)['lookupTarget']==track['key']);p.locator('#mapUndoA').click();ck(tag+'.D.undoOne',len(p.evaluate(STATE)['ships'])==n)
    # Menus: right click / hold / pen. No command merely by opening.
    close(p);pt=sea(p);state=p.evaluate(STATE);p.mouse.click(pt['x'],pt['y'],button='right');ck(tag+'.J.rightClick',snap(p)['menuOpen']);r=p.locator('#mapContextMenuA').bounding_box();v=p.evaluate('AEGIS_VIEWPORT.twoD');ck(tag+'.J.menuContained',r['x']>=v['x'] and r['y']>=v['y'] and r['x']+r['width']<=v['x']+v['w']+.2 and r['y']+r['height']<=v['y']+v['h']+.2);p.keyboard.press('Escape');p.mouse.move(pt['x'],pt['y']);p.mouse.down();p.wait_for_timeout(590);ck(tag+'.J.longPress550',snap(p)['menuOpen']);p.mouse.up();ck(tag+'.J.releaseNoTap',p.evaluate(STATE)==state);p.keyboard.press('Escape')
    p.mouse.move(pt['x'],pt['y']);p.mouse.down();p.mouse.move(pt['x']+11,pt['y'],steps=3);p.wait_for_timeout(580);p.mouse.up();ck(tag+'.J.move11Cancels',not snap(p)['menuOpen']);ck(tag+'.J.move11Pans',p.evaluate('__VIEWPORT_A__.snapshot().twoD.pan.x')!=0);p.evaluate('__VIEWPORT_A__.setPan(0,0)');p.wait_for_timeout(100)
    p.locator('#c').dispatch_event('pointerdown',{'pointerId':99,'pointerType':'pen','isPrimary':True,'button':2,'buttons':2,'clientX':pt['x'],'clientY':pt['y']});ck(tag+'.J.penButton',snap(p)['menuOpen']);p.locator('#c').dispatch_event('pointerup',{'pointerId':99,'pointerType':'pen','button':2,'clientX':pt['x'],'clientY':pt['y']});ck(tag+'.J.penNoCommand',p.evaluate(STATE)==state);capture(p,'menu-sea-'+tag+'.png');p.keyboard.press('Escape');p.wait_for_timeout(360)
    if w!=1400:p.close();continue
    # H: identity only, persistent display number. Save reset is the retained policy.
    click_obj(p,track['key']);identity_before=p.evaluate('__NAVAL_SIM_DIAG__.trackContracts()');p.locator('#mapIdentityA').click();p.locator('#mapIdentityA-TRAINING_TARGET').click();tr=next(o for o in all_objects(p)if o['key']==track['key']);ck('H.identityChanged',tr['identity']=='TRAINING_TARGET');ck('H.numberStable',tr['label']==track['label']);records['H.savedTrackPolicy']='저장 시 트랙·식별 초기화(기존 정책)';capture(p,'info-radar.png')
    # Exact precision id + legacy cursor bridge, no implicit precision on show.
    p.evaluate('__NAVAL_SIM_DIAG__.setEmcon(false)');click_obj(p,track['key']);state=p.evaluate(STATE);ck('K.bridgeOnlyNoLock',state['selectedLockId']==before['selectedLockId'] and state['mode']==before['mode']and state['pdTracking']==before['pdTracking']);p.locator('#mapPrecisionA').click();ck('G.exactTrack',p.evaluate('__EMCON_DESIGNATION_F2__.snapshot().selectedLockId')==track['id']);p.evaluate('__NAVAL_SIM_DIAG__.setEmcon(true)');click_obj(p,track['key']);n=snap(p)['counts']['precision'];ck('G.emconDisabled',p.locator('#mapPrecisionA').is_disabled() and 'EMCON'in p.locator('#uiWindowA-INFO').inner_text());p.locator('#mapPrecisionA').evaluate('e=>e.click()');ck('G.emconInvocation0',snap(p)['counts']['precision']==n);capture(p,'info-emcon.png')
    # ESM-only has no made-up position/range, including its public snapshot.
    esm=next(o for o in all_objects(p)if o['kind']=='ESM');p.evaluate('id=>__NAVAL_SIM_DIAG__.wip118DiagDropTrack(id)',track['id']);close(p);own=p.evaluate('__VIEWPORT_A__.snapshot().twoD.ownship');end=p.evaluate('([o,s])=>({x:s.x+Math.cos(o.bearingRad)*180,y:s.y+Math.sin(o.bearingRad)*180})',[esm,own]);p.mouse.click(end['x'],end['y']);ck('I.esmSelected',snap(p)['lookupTarget']==esm['key']);o=snap(p)['object'];ck('I.esmNoPosition',not any(k in o for k in ['x','y','z','rangeKm','positionM']));ck('I.esmUnknownRange','거리: 알 수 없음'in p.locator('#uiWindowA-INFO').inner_text());ck('G.esmDisabled',p.locator('#mapPrecisionA').is_disabled());capture(p,'info-esm-only.png');close(p)
    # Source audit: prohibit all unobserved enemy truth paths synchronously.
    audit=p.evaluate("""()=>{const w=__AEGIS_ENGAGEMENT_RUNTIME__.world.entities,before=w.hostileMissiles;let reads=0;Object.defineProperty(w,'hostileMissiles',{configurable:true,get(){reads++;throw Error('TRUTH_ACCESS')}});try{__MAP_A__.objects();__MAP_A__.snapshot();}finally{Object.defineProperty(w,'hostileMissiles',{configurable:true,writable:true,value:before});}return reads;}""");ck('I.enemyTruthAccess0',audit==0)
    # Own helicopter telemetry can receive route commands even with AIR closed.
    hkey=p.evaluate("""()=>{const h=__HELO__.snapshot().aircraft[0],live=__AEGIS_ENGAGEMENT_RUNTIME__.world.entities.helicopters.get(h.id);Object.assign(live,{visible:true,onboard:false,state:'TRANSIT',positionM:{x:8000,y:-3000,z:50}});return 'HELO:'+h.id;}""");click_obj(p,hkey);rn=len(p.evaluate(STATE)['helo'][0]['route']);ck('E.tapNoControl',snap(p)['controlPlatform']=='OWN');p.locator('#mapControlA').click();capture(p,'info-helicopter.png');pt=sea(p);n=snap(p)['counts']['helo'];p.mouse.click(pt['x'],pt['y']);ck('E.appendOnce',snap(p)['counts']['helo']==n+1 and len(p.evaluate(STATE)['helo'][0]['route'])==rn+1);p.locator('#mapUndoA').click();ck('E.undo',len(p.evaluate(STATE)['helo'][0]['route'])==rn)
    # F: Harpoon plan takes precedence over control; selecting objects preserves it.
    p.evaluate("()=>{document.getElementById('modeAimBtn').click();__HARPOON_DIAG_A__.routeToggle();}");pt=sea(p);p.mouse.click(pt['x'],pt['y']);ck('F.oneRoutePoint',len(p.evaluate(STATE)['harpoon']['pointsM'])==1);click_obj(p,'OWN');ck('F.controlDisabled',p.locator('#mapControlA').is_disabled() and '하푼 계획 작성 중'in p.locator('#uiWindowA-INFO').inner_text());n=len(p.evaluate(STATE)['harpoon']['pointsM']);p.mouse.click(*[p.locator('#mapUndoA').bounding_box()[k]+5 for k in ['x','y']]);ck('F.undoPlanOnly',len(p.evaluate(STATE)['harpoon']['pointsM'])==n-1);p.evaluate('__HARPOON_DIAG_A__.routeToggle()')
    # Losing a selected track leaves the window and marks its actions unavailable.
    tid=p.evaluate("__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:14,bearingDeg:50,speedMps:0})");click_obj(p,'TRACK:'+str(tid));p.evaluate('id=>__NAVAL_SIM_DIAG__.wip118DiagDropTrack(id)',tid);p.wait_for_timeout(350);ck('lost.windowRemains',p.locator('#uiWindowA-INFO').is_visible() and '트랙 소실'in p.locator('#uiWindowA-INFO').inner_text() and p.locator('#mapPrecisionA').is_disabled())
    controlled=snap(p)['controlPlatform'];p.keyboard.press('Escape');ck('ESC.retainsControl',snap(p)['controlPlatform']==controlled)
    # Actual received Hawklink report and allied SELF network record.
    rid=p.evaluate("""()=>{const d=__NAVAL_SIM_DIAG__,r=__AEGIS_ACTIVE_SHIP_RUNTIME__;d.offboardDiagnosticC(r.entityId,{link:{sourceId:'H1',connected:true,latencyS:0}});for(let i=0;i<3;i++){d.offboardDiagnosticC(r.entityId,{report:{schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'H1',sequence:700+i,measuredAtS:d.observerSnapshotC().worldTimeS,positionM:{x:-10000,y:-15000,z:8},covarianceM2:[400,0,0,0,400,0,0,0,16],domainEvidence:{surface:.98,air:.02,missile:.01,background:.01}}});d.stepTicks(1);}return d.observerFacadeC(r.entityId).tracks.find(t=>t.source==='OFFBOARD_C')?.trackId;}""");ck('link.nativeTrack',rid is not None)
    if rid is not None:click_obj(p,'TRACK:'+str(rid));capture(p,'info-link.png');ck('I.linkProvidedOnly','H1'in p.locator('#uiWindowA-INFO').inner_text())
    # Pure tape arithmetic: visible ticks cross north continuously.
    tape=p.evaluate("()=>{const a=__MAP_A__.tapeModel(359,359,300),b=__MAP_A__.tapeModel(1,359,300);return {a,b}}")
    tickA=next(t for t in tape['a']['ticks']if t['degrees']==0);tickB=next(t for t in tape['b']['ticks']if t['degrees']==0);jump=abs((tickB['x']-tickA['x'])-(-2*300/60));ck('M.northContinuous',jump<1e-8);ck('M.labels30',all(not t['label']or int(t['label'])%30==0 for t in tape['a']['ticks']));ck('M.headingError',abs(tape['b']['markerPx']/(300/60)+2)<=1);records['tape']={'northJumpResidualPx':jump,'headingErrorDeg':abs(tape['b']['markerPx']/(300/60)+2)}
    records['state']=snap(p);ck('core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));p.close()
  elif a.part=='invariance':
   sp=importlib.util.spec_from_file_location('inv',R/'docs/viewport/A/verify_invariance.py');inv=importlib.util.module_from_spec(sp);sp.loader.exec_module(inv);hashes=[]
   for mutate in [False,True]:
    p=load_fleet(b,raw,own='CG_52_LATE_TICONDEROGA',ally='DDG_119_LATE_FLIGHT_IIA',enemy='SOVREMENNY_956',width=1400,height=900,errors=errors);p.evaluate("()=>{__NAVAL_SIM_DIAG__.setTerrainDiagBypass(true);__NAVAL_SIM_DIAG__.setEmcon(false);__AEGIS_WIP14A14_ENGAGEMENT_UI__.selectionProbe(35);document.getElementById('external3DAutoLockBtn').click();document.getElementById('external3DFireBtn').click();}");p.evaluate(inv.SETUP);p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(180)');close(p);before=p.evaluate(STATE)
    if mutate:
     kinds=p.evaluate("""()=>{const c=document.getElementById('c'),dispatch=(type,o)=>c.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,isPrimary:true,pointerId:1,pointerType:'mouse',button:0,...o})),m=__MAP_A__,seen=new Set();for(let i=0;i<200;i++){const objects=m.objects().filter(o=>Number.isFinite(o.x)||o.kind==='ESM'),o=objects[i%objects.length],own=__VIEWPORT_A__.snapshot().twoD.ownship,p=o.kind==='ESM'?{x:own.x+Math.cos(o.bearingRad)*150,y:own.y+Math.sin(o.bearingRad)*150}:__VIEWPORT_A__.worldToScreen(o.x,o.y);if(i%3===0){c.dispatchEvent(new MouseEvent('contextmenu',{clientX:p.x,clientY:p.y,bubbles:true,cancelable:true}));}else{dispatch('pointerdown',{clientX:p.x,clientY:p.y});dispatch('pointerup',{clientX:p.x,clientY:p.y});}const button=[...document.querySelectorAll('#mapCandidatesA button')].find(b=>b.textContent===o.kind+' · '+o.label);if(button&&!button.closest('[hidden]'))button.click();const q=m.snapshot();if(q.object)seen.add(q.object.kind);document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));}return [...seen];}""")
     records['randomKinds']=kinds;ck('A.allRequestedKinds',all(k in kinds for k in ['OWN','HELO','ALLY','TRACK','ESM','MISSILE']))
     ck('A.200NoCommand',before==p.evaluate(STATE))
    for i in range(24):p.evaluate('__NAVAL_SIM_DIAG__.stepTicks(300)');p.evaluate('__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)')
    state=p.evaluate(inv.STATE);encoded=json.dumps(state,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();hashes.append({'input200':mutate,'hash':hashlib.sha256(encoded).hexdigest(),'bytes':len(encoded),'ticks':7200});(a.out/('state-input.json'if mutate else'state-control.json')).write_bytes(encoded);p.close()
   ck('A.120sHashSame',hashes[0]['hash']==hashes[1]['hash']);records['hashes']=hashes
  elif a.part=='legacy':
   assert a.baseline;rows=[]
   for path in [a.baseline,a.html]:
    p=load_fleet(b,path.read_bytes(),width=1400,height=900,errors=errors);p.evaluate("window.__MAP_A__?.setMode(false)");p.evaluate(FIXTURE);close(p);p.evaluate('__VIEWPORT_A__.setDistance(40)');states=[]
    for tab,mode in [('NAV','modeNavBtn'),('ARM','modeAimBtn'),('AIR',None),('ARM','harpoonRouteE')]:
     p.evaluate('t=>__NAVAL_SIM_DIAG__.wip13cSetControlDeckTab(t)',tab)
     if mode:p.evaluate('id=>document.getElementById(id)?.click()',mode)
     close(p);v=p.evaluate('AEGIS_VIEWPORT.twoD');p.mouse.click(v['cx']-v['w']*.2,v['cy']-v['h']*.12);states.append(p.evaluate(STATE))
    f=p.evaluate("__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:12,bearingDeg:0,speedMps:0})")
    for emcon in [True,False]:
     p.evaluate('v=>__NAVAL_SIM_DIAG__.setEmcon(v)',emcon);states.append(p.evaluate('id=>__NAVAL_SIM_DIAG__.lockTrackViaCursor(id)',f));p.evaluate("document.getElementById('lockBtn').click()");states.append(p.evaluate('__EMCON_DESIGNATION_F2__.snapshot()'));p.evaluate("document.getElementById('external3DAutoLockBtn').click()");states.append(p.evaluate('__EMCON_DESIGNATION_F2__.snapshot()'))
    rows.append(states);p.close()
   ck('N.legacyFourBranches',rows[0][:4]==rows[1][:4]);ck('N.noArgumentPrecisionAndEmcon',rows[0][4:]==rows[1][4:]);records['paired']=rows
  else:
   p=load_fleet(b,raw,width=832,height=384,errors=errors);p.evaluate(FIXTURE);close(p);click_obj(p,'OWN');p.locator('#mapControlA').click();state=snap(p);p.evaluate('__WIP148_3D_VIEW__.c12ApplyPreset("LOW")');before=p.evaluate(STATE);p.locator('#mapViewA').click();p.wait_for_function('__WIP148_3D_VIEW__.active');p.wait_for_timeout(400);ck('A.3DViewNoCommand',before==p.evaluate(STATE));ck('L.3DSelectionPreserved',snap(p)['lookupTarget']==state['lookupTarget']and snap(p)['controlPlatform']==state['controlPlatform']);p.evaluate('__WIP148_3D_VIEW__.active=false');p.wait_for_timeout(120)
   tape=p.evaluate('''()=>{const v=__WIP148_3D_VIEW__,e=document.getElementById('uiBearingTapeA'),rows=[];for(const bearing of [359,1]){const a=bearing*Math.PI/180,p=v.camera.position.clone();v.camera.lookAt(p.x+Math.sin(a),p.y,p.z-Math.cos(a));v.camera.updateMatrixWorld(true);const d=new v.THREE.Vector3();v.camera.getWorldDirection(d);const actual=(Math.atan2(d.x,-d.z)*180/Math.PI+360)%360;e.hidden=false;__MAP_A__.updateTape(e,actual,359);const tick=e.querySelector('[data-degrees="0"]'),marker=e.querySelector('.map-tape-heading-a');rows.push({actual,width:e.clientWidth-16,zeroX:new DOMMatrix(getComputedStyle(tick).transform).m41,markerX:new DOMMatrix(getComputedStyle(marker).transform).m41,labels:[...e.querySelectorAll('.map-tape-label-a')].map(l=>l.textContent).filter(Boolean)});}return rows;}''')
   residual=abs(tape[1]['zeroX']-tape[0]['zeroX']+2*tape[0]['width']/60);ck('M.actualCameraNorthContinuity',residual<.01);ck('M.actualHeadingError',abs(tape[1]['markerX']/(tape[1]['width']/60)+2)<=1);ck('M.domLabels30',all(int(t)%30==0 for row in tape for t in row['labels']));records['cameraTape']=tape
   r=p.locator('#uiWindowA-INFO .ui-title-a').bounding_box();p.mouse.move(r['x']+20,r['y']+12);p.mouse.down();p.mouse.move(r['x']+40,r['y']+35,steps=4);p.mouse.up();ck('L.infoDrag',snap(p)['lookupTarget']==state['lookupTarget']and snap(p)['controlPlatform']==state['controlPlatform'])
   for scale in [85,130,100]:
    p.evaluate('n=>__UI_A__.setScale(n)',scale);settle(p,384,832);ck('L.resizeScale'+str(scale),snap(p)['lookupTarget']==state['lookupTarget']and snap(p)['controlPlatform']==state['controlPlatform'])
   p.evaluate('__WIP148_3D_VIEW__.close()');ck('L.to2D',snap(p)['lookupTarget']==state['lookupTarget']);records['state']=snap(p);p.close()
  b.close()
 ck('pageErrors',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(a.out/(a.part+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
if __name__=='__main__':main()
