from pathlib import Path
import sys,json,time,hashlib,base64
from playwright.sync_api import sync_playwright,Locator
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();fixture='\n'.join(p.read_text()for p in [R/'docs/map/E/test-helper.js',R/'docs/map/D/extension-fixture.js',H/'test-fixture.js'])+'''
__GB_TEST__.muzzleAudit=()=>{const view=WIP148_EXTERNAL_3D,T=view.THREE;view.syncShipFittings(get3DRenderState());view.shipRoot.updateWorldMatrix(true,true);return gunB1OwnGuns().map(([id,g])=>{const v=view._gunB1Visuals.get(g.installation.hardpointId),b=v.pitch.getObjectByName('MK45_MOD4_BORE'),p=view.shipRoot.worldToLocal(b.getWorldPosition(new T.Vector3())),q=g.snapshot(),hp=ACTIVE_SHIP_PROFILE.geometry.hardpoints[g.installation.hardpointId],off=g.spec.mount.trunnionOffsetM,az=q.bodyAzRad,el=q.elevationRad,l=g.spec.mount.exposedBarrelM,expected={x:hp.x+off.x*Math.cos(az)-off.y*Math.sin(az)+Math.cos(az)*Math.cos(el)*l,y:hp.y+off.x*Math.sin(az)+off.y*Math.cos(az)+Math.sin(az)*Math.cos(el)*l,z:hp.z+off.z+Math.sin(el)*l};return {id,expected,actual:{x:p.x,y:p.z,z:p.y},errorM:Math.hypot(p.x-expected.x,p.z-expected.y,p.y-expected.z),faceted:!!v.holder.getObjectByName('MK45_MOD4_FACETED_HOUSING'),sourceHidden:view._bunkerAsset.nodes.get(BUNKER_REGISTRATION.guns[g.installation.hardpointId].yawNode).obj.visible===false};});};
__GB_TEST__.patchAir=(id,o)=>Object.assign(tracks.get(id),o);
__GB_TEST__.uiTick=n=>{for(let i=0;i<n;i++){for(const tr of tracks.values()){tr._lastMeasurementStep=simStepCounter;tr.sensorAge=0;}simulateFixedTick(SIM_FIXED_DT);}return __GB_TEST__.guns();};
'''
# Buttons invoke their original DOM click listeners after independent bounds checks;
# map selection below uses real pointer input. Avoid WebGL actionability RAF stalls.
Locator.click=lambda self,*a,**kw:self.evaluate('e=>e.click()')
E=H/'evidence/ui';E.mkdir(parents=True,exist_ok=True);errors=[];records={};checks={};start=time.perf_counter()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def cap(p,n):
 c=p.context.new_cdp_session(p)
 try:(E/(n+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
 finally:c.detach()
def boxes(p):return p.evaluate('''()=>Object.fromEntries(['uiShipA','uiInventoryA','mapFireSlotC','uiEmconChipA','uiModeChipA','uiWindowListButtonA','uiWindowAddButtonA'].map(id=>[id,document.getElementById(id).getBoundingClientRect().toJSON()]))''')
def select(p,ammo='MFF_127_SIM',mode='SINGLE'):
 if p.evaluate('__MAP_B__.snapshot().selection?.weapon==="MK45"'):p.locator('[data-weapon-b=MK45]').click()
 p.locator('[data-weapon-b=MK45]').click();p.locator('[data-ammo-d="'+ammo+'"]').click();p.locator('[data-gun-mode-d="'+mode+'"]').click()
def choose(p,tid,surface):
 p.evaluate('__VIEWPORT_A__.setDistance(15);__PIP_A__.setDistance(10)');o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',tid);pt=p.evaluate('a=>a.s==="PIP"?__PIP_A__.worldToScreen(a.o.x,a.o.y):__VIEWPORT_A__.worldToScreen(a.o.x,a.o.y)',{'o':o,'s':surface});p.mouse.click(pt['x'],pt['y']);p.wait_for_timeout(100)
 if p.evaluate('__MAP_A__.snapshot().candidatesOpen'):p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click()
 p.evaluate('__MAP_B__.refresh(true)');return p.evaluate('__MAP_B__.snapshot()')
with sync_playwright()as pw:
 b=launch(pw,True)
 for w,h in [(1400,900),(832,384)]:
  for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   p=load_fleet(b,instrument(raw,fixture),own=ship,width=w,height=h,errors=errors);p.set_default_timeout(180000)
   for surf in ['MAIN','PIP']:
    tag=f'{w}.{ship[:2]}.{surf}';p.evaluate('__GB_TEST__.reset();Object.keys(__UI_A__.snapshot().windows).forEach(id=>__UI_A__.close(id));document.getElementById("uiStatusBarA").click()')
    if surf=='PIP':p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open();__UI_A__.open("CIC")}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=240000,polling=50);p.wait_for_timeout(350)
    else:p.evaluate('__WIP148_3D_VIEW__.close()')
    before=boxes(p);p.locator('[data-weapon-b=MK45]').click();p.wait_for_timeout(100);menu=p.locator('#mapSalvoB').bounding_box();ck(tag+'.G8.menuInside',menu['x']>=0 and menu['y']>=0 and menu['x']+menu['width']<=w+1 and menu['y']+menu['height']<=h+1);ck(tag+'.G5.ammo3',p.locator('[data-ammo-d]').count()==3);p.locator('[data-gun-auto-b1]').click();p.wait_for_timeout(100);after=boxes(p);err=max(abs(before[k][v]-after[k][v])for k in before for v in ['x','y','width','height']);ck(tag+'.G8.bar0px',err<.01);cap(p,tag+'-menu');p.locator('[data-gun-auto-b1]').click();p.locator('[data-ammo-d=MFF_127_SIM]').click();p.locator('[data-gun-mode-d=SINGLE]').click();tid=p.evaluate('__GB_TEST__.air({rangeKm:5,bearingDeg:90,altM:500})');q=choose(p,tid,surf);ck(tag+'.G5.airGreen',q['model']['allowed']and q['model']['tone']=='effective');cap(p,tag+'-air-ready')
    p.evaluate('id=>__GB_TEST__.patchAir(id,{_lastMeasurementStep:-120})',tid);q=choose(p,tid,surf);ck(tag+'.G5.airOrange',q['model']['allowed']and q['model']['tone']=='warning');cap(p,tag+'-air-degraded');p.evaluate('id=>__GB_TEST__.patchAir(id,{_lastMeasurementStep:-240})',tid);q=choose(p,tid,surf);ck(tag+'.G5.airBlocked',not q['model']['allowed']);cap(p,tag+'-air-blocked');p.evaluate('id=>__GB_TEST__.patchAir(id,{_lastMeasurementStep:0})',tid);select(p,'HE_127_SIM');q=choose(p,tid,surf);ck(tag+'.G5.nonMffWarning',q['model']['allowed']and'대공탄 아님'in p.locator('#mapEngagementB').inner_text());cap(p,tag+'-nonMff-warning');select(p,'MFF_127_SIM');q=choose(p,tid,surf);p.locator('#mapFireB').click();p.evaluate('__GB_TEST__.uiTick(360)');q=p.evaluate('__GB_TEST__.guns()');ck(tag+'.G5.singleNative',sum(g['q']['shotsFired']for g in q)>=1);records[tag+'.shots']=q
    if ship.startswith('CG')and surf=='PIP':
     q=p.evaluate('__GB_TEST__.muzzleAudit()');ck(tag+'.G1.muzzle',all(x['errorM']<=.1 and x['faceted']and x['sourceHidden']for x in q));records[tag+'.muzzle']=q;cap(p,tag+'-mod4-ship')
    ck(tag+'.core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));records[tag+'.barDeltaPx']=err
   if w==1400 and ship.startswith('DD'):
    status=p.evaluate('__ENV_D__.status()');records['ENV_D.status']=status;ck('ENV_D.statusMatches120',status['match']and status['rows']==120)
   p.close()
 b.close()
ck('pageErrors0',not errors);out={'checks':checks,'records':records,'errors':errors,'pass':all(checks.values()),'elapsedS':time.perf_counter()-start,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'pass':out['pass'],'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(not out['pass'])
