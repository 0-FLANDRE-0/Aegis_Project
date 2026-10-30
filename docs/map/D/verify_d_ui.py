from pathlib import Path
import sys,json,hashlib,base64,time,math
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/d-ui';E.mkdir(parents=True,exist_ok=True);raw=(R/'Aegis_SIM_v48_WIP_MAP_D.html').read_bytes();checks={};records={};errors=[];start=time.perf_counter()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def cap(p,name):
 c=p.context.new_cdp_session(p)
 try:(E/(name+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
 finally:c.detach()
def resetD(p,surface):
 p.evaluate('__MD_TEST__.reset()')
 if surface=='PIP':p.evaluate('__UI_A__.open("CIC");__PIP_A__.setDistance(40)')
 else:p.evaluate('__WIP148_3D_VIEW__.close()')
 p.wait_for_timeout(420)
def selectD(p,weapon,n=1,mode='SINGLE',ammo='HE_127_SIM'):
 if snap(p)['selection']and snap(p)['selection']['weapon']==weapon:p.locator('[data-weapon-b="'+weapon+'"]').click()
 if weapon=='HARPOON':select(p,weapon,n)
 else:
  p.locator('[data-weapon-b="MK45"]').click();p.locator('[data-ammo-d="'+ammo+'"]').click();p.locator('[data-gun-mode-d="'+mode+'"]').click();p.wait_for_timeout(120)
def surface(p,opts={}):return p.evaluate('o=>__MD_TEST__.surface(o)',opts)
def boxes(p):return p.evaluate('''()=>Object.fromEntries(['uiShipA','uiInventoryA','mapFireSlotC','uiEmconChipA','uiModeChipA','uiWindowListButtonA','uiWindowAddButtonA'].map(id=>[id,document.getElementById(id).getBoundingClientRect().toJSON()]))''')
def diff(a,b):return max(abs(a[k][v]-b[k][v])for k in a for v in ['x','y','width','height'])
def clickWorld(p,surface,xM,yM):
 a=p.evaluate('a=>a.s==="PIP"?__PIP_A__.worldToScreen(a.x,a.y):__VIEWPORT_A__.worldToScreen(a.x,a.y)',{'s':surface,'x':xM*.0038,'y':yM*.0038}) if False else p.evaluate('a=>__MD_TEST__.screen(a.s,a.x,a.y)',{'s':surface,'x':xM,'y':yM});assert p.evaluate('a=>document.elementFromPoint(a.x,a.y)?.tagName==="CANVAS"',a),'fixture point covered by UI';p.mouse.click(a['x'],a['y']);p.wait_for_timeout(120)
fixture=(H/'test-helper.js').read_text()+'\n'+(H/'extension-fixture.js').read_text()
with sync_playwright()as pw:
 b=launch(pw,True)
 for w,h in [(1400,900),(832,384)]:
  for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   p=load_fleet(b,instrument(raw,fixture),own=own,width=w,height=h,errors=errors);p.set_default_timeout(60000)
   for s in ['MAIN','PIP']:
    tag=f'{w}.{own[:2]}.{s}';print('context',tag,flush=True)
    if s=='PIP':p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000)
    resetD(p,s);a=boxes(p);ck(tag+'.D1.onlyInstalled',p.locator('[data-weapon-b="HARPOON"]').count()==(1 if own.startswith('CG')else 0));ck(tag+'.D1.otherInventoryNotSelectable',p.locator('[data-weapon-b]').count()==(6 if own.startswith('CG')else 5))
    selectD(p,'MK45');after=boxes(p);tid=surface(p,{'rangeKm':8,'bearingDeg':90});q=target(p,tid,s);ck(tag+'.D1.boxInvariant',diff(a,after)<.01 and diff(a,boxes(p))<.01);records[tag+'.boxes']={'maxDeltaPx':max(diff(a,after),diff(a,boxes(p))),'before':a,'after':boxes(p)}
    ck(tag+'.D4.cueAll',all(g['commandTrackId']==tid for g in p.evaluate('__MAP_D__.snapshot().guns')));ck(tag+'.D4.readyGreen',q['model']['allowed']and q['model']['tone']=='effective');cap(p,tag+'-gun-ready')
    # FCQ is computed by the unchanged native method from changed observed covariance.
    p.evaluate('id=>__MD_TEST__.quality(id,25,.9)',tid);q=snap(p);ck(tag+'.D4.degradedOrange',q['model']['allowed']and q['model']['tone']=='warning');cap(p,tag+'-gun-degraded');p.evaluate('id=>__MD_TEST__.quality(id,70,2)',tid);q=snap(p);ck(tag+'.D4.insufficientRed',not q['model']['allowed']and q['model']['tone']=='blocked');cap(p,tag+'-gun-blocked');p.evaluate('id=>__MD_TEST__.quality(id,4,.18)',tid);snap(p)
    # Hold and second trigger cancel use requestFire on the next fixed tick.
    p.locator('#mapFireB').click();ck(tag+'.D4.noRenderShot',all(g['shotsFired']==0 for g in p.evaluate('__MAP_D__.snapshot().guns')));p.evaluate('__MD_TEST__.tick(1)');q=snap(p);ck(tag+'.D4.nativeHold',all(g['pendingSingleFire']['active']for g in p.evaluate('__MAP_D__.snapshot().guns'))and'정렬 대기'in p.locator('#mapFireB').inner_text());cap(p,tag+'-gun-hold');p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tick(1)');snap(p);ck(tag+'.D4.holdCancel',all(not g['pendingSingleFire']['active']and g['shotsFired']==0 for g in p.evaluate('__MAP_D__.snapshot().guns')))
    p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tickUntilGunShot(400)');snap(p);shot=p.evaluate('__MAP_D__.snapshot().guns');ck(tag+'.D4.singleShot',all(g['shotsFired']==1 for g in shot));records[tag+'.single']=shot
    p.evaluate('__MD_TEST__.tick(200)');selectD(p,'MK45',mode='CONTINUOUS');target(p,tid,s);p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tick(20)');snap(p);ck(tag+'.D4.contStarts',all(g['continuousFire']['active']for g in p.evaluate('__MAP_D__.snapshot().guns')));shots=p.evaluate('__MAP_D__.snapshot().guns');cap(p,tag+'-gun-cont');p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tick(1)');snap(p);stopped=p.evaluate('__MAP_D__.snapshot().guns');ck(tag+'.D4.contStopsNoExtra',all(not g['continuousFire']['active']for g in stopped)and[g['shotsFired']for g in shots]==[g['shotsFired']for g in stopped])
    # Feed rejection remains native; switching after the cycle succeeds.
    p.locator('[data-weapon-b="MK45"]').click();p.locator('[data-weapon-b="MK45"]').click();p.locator('[data-ammo-d="SAP_127_SIM"]').click();reason=p.locator('.map-menu-reason-d').inner_text();ck(tag+'.D4.feedReject',reason=='급탄 중');p.evaluate('__MD_TEST__.tick(240)');p.locator('[data-ammo-d="SAP_127_SIM"]').click();ck(tag+'.D4.ammoNative',all(g['loadedAmmoId']=='SAP_127_SIM'for g in p.evaluate('__MAP_D__.snapshot().guns')));p.locator('[data-gun-mode-d="CONTINUOUS"]').click();target(p,tid,s);p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tick(1)');snap(p);p.locator('#mapCancelB').click();ck(tag+'.D4.targetCancelStops',all(not g['continuousFire']['active']and g['commandTrackId']is None for g in p.evaluate('__MAP_D__.snapshot().guns')))
    # Native range values and input isolation, including unavailable air targets.
    p.locator('[data-weapon-b="MK45"]').click();selectD(p,'MK45');air=p.evaluate('__MB_TEST__.add({rangeKm:10,bearingDeg:30})');q=target(p,air,s);ck(tag+'.D4.airBlocked',q['model']['reason']=='NOT_SURFACE_TRACK'and not q['model']['allowed']);cap(p,tag+'-gun-air');records[tag+'.gunRangeKm']=p.evaluate('__MAP_D__.snapshot().guns.map(g=>g.moduleId)')
    if own.startswith('CG'):
     resetD(p,s);a=boxes(p);selectD(p,'HARPOON',2);tid=surface(p,{'rangeKm':10,'bearingDeg':90});q=target(p,tid,s);ck(tag+'.D2.hpGreen',q['model']['allowed']and q['model']['tone']=='effective');ck(tag+'.D1.hpBoxes',diff(a,boxes(p))<.01);cap(p,tag+'-harpoon-ready');p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tickUntilHarpoon(2,240)');snap(p);ck(tag+'.D2.hpTwo',len(p.evaluate('__MD_TEST__.state().harpoon.launches'))==2)
     # Menus disable unavailable salvo counts, keep an existing choice pending.
     resetD(p,s);p.evaluate('__MD_TEST__.tubeStock(2)');p.wait_for_timeout(300);p.locator('[data-weapon-b="HARPOON"]').click();ck(tag+'.D1.stockDisables',p.locator('[data-salvo-b="3"]').is_disabled()and p.locator('[data-salvo-b="4"]').is_disabled());p.locator('[data-salvo-b="2"]').click();p.locator('#mapRouteChipButtonD').click();p.locator('#mapRouteBannerD').wait_for(state='visible');ck(tag+'.D3.banner',p.locator('#mapRouteBannerD').is_visible());p.evaluate('__VIEWPORT_A__.setDistance(3);__PIP_A__.setDistance(3)');p.wait_for_timeout(250);n=p.evaluate('__MD_TEST__.state().waypoints.length');clickWorld(p,s,2500,0);ck(tag+'.D3.emptyAddsRoute',len(p.evaluate('__MAP_D__.snapshot().route.pointsM'))==1 and p.evaluate('__MD_TEST__.state().waypoints.length')==n);clickWorld(p,s,2500,1000);ck(tag+'.D3.spacing',len(p.evaluate('__MAP_D__.snapshot().route.pointsM'))==1);clickWorld(p,s,-2500,0);ck(tag+'.D3.secondRoute',len(p.evaluate('__MAP_D__.snapshot().route.pointsM'))==2)
     for i in range(6):p.evaluate('i=>__MD_TEST__.searchPoint(-5000-i*2500,0)',i)
     limit=p.evaluate('__MD_TEST__.searchPoint(-22000,0)');ck(tag+'.D3.max8',len(p.evaluate('__MAP_D__.snapshot().route.pointsM'))==8 and limit['reason']=='WAYPOINT_LIMIT');cap(p,tag+'-route8');p.locator('#mapRouteChipButtonD').click();ck(tag+'.D3.exitClears',not p.evaluate('__MAP_D__.snapshot().route.editing')and len(p.evaluate('__MAP_D__.snapshot().route.pointsM'))==0)
     p.locator('#mapRouteChipButtonD').click();p.evaluate('__MD_TEST__.searchPoint(12000,0);__MD_TEST__.searchPoint(24000,0)');snap(p);p.evaluate('__VIEWPORT_A__.setDistance(40);__PIP_A__.setDistance(40)');cap(p,tag+'-route-plan');p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tickUntilHarpoon(2,240)');snap(p);launch=p.evaluate('__MD_TEST__.state().harpoon.launches');ck(tag+'.D3.frozenN',len(launch)==2 and launch[0]['routeProgram']==launch[1]['routeProgram']);ck(tag+'.D3.searchSame',all(l['memory']['positionM']==l['routeProgram']['searchCenterM']for l in launch));ck(tag+'.D3.nativeDraftCleared',not p.evaluate('__MAP_D__.snapshot().route.pointsM'));records[tag+'.routeLaunches']=launch
    geometry=p.evaluate('''()=>{const f=document.getElementById('mapFireB'),r=f.getBoundingClientRect(),h=parseFloat(getComputedStyle(f,'::after').height)*__UI_A_SETTINGS__.scale;return{hitHeight:h,width:r.width,overflow:document.documentElement.scrollWidth>innerWidth}}''');ck(tag+'.D6.fireHit',geometry['hitHeight']>=40 and geometry['width']>=72 and not geometry['overflow']);records[tag+'.geometry']=geometry
    ck(tag+'.nativeCore',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));ck(tag+'.tableMatch',p.evaluate('async()=> (await __ENV_D__.status()).match'));cap(p,tag+'-final')
   p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start};(E/'ui.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
