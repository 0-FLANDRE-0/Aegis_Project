"""MAP_E E1-E7, actual UI dispatch on both ships / surfaces / target sizes.
No inherited legacy test adapter is installed in this new acceptance suite.
"""
from pathlib import Path
import os
import sys,json,hashlib,time,base64
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();E=H/'evidence/e-new';E.mkdir(parents=True,exist_ok=True);checks={};records={};errors=[];start=time.perf_counter()
fixture=(H/'test-helper.js').read_text()+'\n'+(R/'docs/map/D/extension-fixture.js').read_text()+'\n'+(H/'test_e_fixture.js').read_text()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def cap(p,n):
 s=p.context.new_cdp_session(p)
 try:(E/(n+'.png')).write_bytes(base64.b64decode(s.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
 finally:s.detach()
def reset(p,s):
 p.evaluate('__ME_TEST__.reset()')
 if s=='PIP':p.evaluate('__UI_A__.open("CIC");__PIP_A__.setDistance(40)')
 else:p.evaluate('__WIP148_3D_VIEW__.close()')
 p.wait_for_timeout(400)
def boxes(p):return p.evaluate('''()=>Object.fromEntries(['uiShipA','uiInventoryA','mapFireSlotC','uiEmconChipA','uiModeChipA','uiWindowListButtonA','uiWindowAddButtonA'].map(id=>[id,document.getElementById(id).getBoundingClientRect().toJSON()]))''')
def delta(a,b):return max(abs(a[k][v]-b[k][v])for k in a for v in ['x','y','width','height'])
def select(p,w='SM6'):
 p.locator('[data-weapon-b="'+w+'"]').click();p.locator('[data-salvo-b="1"]').click()
def target(p,tid,s):
 o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',tid);p.evaluate('a=>__MAP_B__.pickObject(a.o,a.s)',{'o':o,'s':s});p.evaluate('__MAP_B__.refresh(true)');return p.evaluate('__MAP_B__.snapshot()')
def own(p):return p.evaluate('__MAP_E__.snapshot()')
with sync_playwright()as pw:
 b=launch(pw,True)
 # Same observed multi-threat history against baseline D and current E.
 for ship in ([]if os.environ.get('MAP_E_UI_ONLY')else['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']):
  base=load_fleet(b,instrument((R/'Aegis_SIM_v48_WIP_MAP_D.html').read_bytes(),fixture),own=ship,errors=errors);base.set_default_timeout(120000);old=base.evaluate('__ME_TEST__.ecmRun("FULL")');base.close()
  p=load_fleet(b,instrument(raw,fixture),own=ship,errors=errors);p.set_default_timeout(120000);results={k:p.evaluate('k=>__ME_TEST__.ecmRun(k)',k)for k in ['OFF','JAM','FULL']};(E/(ship+'-ecm.json')).write_text(json.dumps({'baseline':old,'current':results},indent=2));ck(ship+'.E3.FULL.exactNativeHistory',old==results['FULL']);ck(ship+'.E3.FULL.expends',len(old['chaff'])>0 and len(old['nulka'])>0);ck(ship+'.E3.JAM.noExpendables',not results['JAM']['chaff']and not results['JAM']['nulka']);ck(ship+'.E3.JAM.EA',any(q['resourceUsed']>.1 for q in results['JAM']['ea']));ck(ship+'.E3.OFF.noEAorExpendables',not results['OFF']['chaff']and not results['OFF']['nulka']and all(q['resourceUsed']==0 for q in results['OFF']['ea']));records[ship+'.E3']={'baseline':old,'current':results};p.close()
 for width,height in ([]if os.environ.get('MAP_E_NATIVE_ONLY')else[(1400,900),(832,384)]):
  for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   p=load_fleet(b,instrument(raw,fixture),own=ship,ally='DDG_119_LATE_FLIGHT_IIA'if ship.startswith('CG')else'CG_52_LATE_TICONDEROGA',width=width,height=height,errors=errors);p.set_default_timeout(60000)
   for s in ['MAIN','PIP']:
    tag=f'{width}.{ship[:2]}.{s}'
    if s=='PIP':p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000,polling=50)
    reset(p,s)
    ck(tag+'.E1.noARM',p.locator('#modeAimBtn,#autoEngBtn,#cg52GunSelect,#uiWindowA-ARM,.control-deck-page[data-page="ARM"]').count()==0)
    ck(tag+'.E1.debugRetained',p.evaluate('''()=>['scenarioModeBtn','newSeaBtn','resetBtn','debugSpawnKh35Btn','debugSpawnKh32Btn','debugToggle'].every(id=>document.getElementById('uiWindowA-DEBUG').contains(document.getElementById(id)))'''))
    ck(tag+'.E1.nodeIntegrity',p.evaluate('__UI_A__.snapshot().originalNodesConnected&&__UI_A__.snapshot().duplicateIds.length===0'))
    p.locator('#uiWindowAddButtonA').click();p.locator('#armsBtn').click();ck(tag+'.E1.armsOpens',p.locator('#armsPanel').is_visible());p.locator('#armsPanelClose').click();p.evaluate('document.getElementById("uiWindowAddA").hidden=true')
    before=boxes(p);npc=p.evaluate('__ME_TEST__.npc()');p.locator('#uiEmconChipA').click();p.locator('#mapEcmJAME').click();ck(tag+'.E2.JAM',own(p)['level']=='JAM'and own(p)['noiseRequested']and own(p)['deceptionRequested']);p.locator('#mapAllRadiationE').click();ck(tag+'.E2.allOff',not own(p)['radarOn']and own(p)['level']=='OFF');p.locator('#mapAllRadiationE').click();ck(tag+'.E2.restoresJAM',own(p)['radarOn']and own(p)['level']=='JAM');ecm=own(p);p.locator('#mapRadarE').click();ck(tag+'.E2.radarOnly',own(p)['radarOn']!=ecm['radarOn']and own(p)['level']=='JAM');p.locator('#mapEcmFULLE').click();p.locator('#mapAllRadiationE').click();p.locator('#mapAllRadiationE').click();ck(tag+'.E2.restoresFULL',own(p)['level']=='FULL'and own(p)['radarOn']);p.locator('#mapEcmOFFE').click();p.wait_for_timeout(200);d=delta(before,boxes(p));ck(tag+'.E2.boxes0px',d<.01);records[tag+'.barErrorPx']=d;ck(tag+'.E3.NPCunchanged',p.evaluate('__ME_TEST__.npc()')==npc);cap(p,tag+'-emcon-menu');p.mouse.click(width/2,8);ck(tag+'.E2.outsideCloses',not own(p)['menuOpen']);p.locator('#uiEmconChipA').click();p.locator('#uiEmconChipA').click();ck(tag+'.E2.repeatCloses',not own(p)['menuOpen'])
    p.evaluate('__ME_TEST__.command("JAM")');ck(tag+'.E3.legacyInfersFULL',p.evaluate('__ME_TEST__.nativeResetStage()')=='FULL');p.evaluate('__ME_TEST__.command("OFF")')
    # Manual commands preserve the current SAM selection / target and use native effects.
    select(p);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');target(p,tid,s);selection=p.evaluate('({selection:__MAP_B__.snapshot().selection,target:__MAP_B__.snapshot().target})');p.locator('[data-decoy-e="SRBOC"]').click();n0=p.evaluate('__ME_TEST__.own().srboc.expendedRounds');p.locator('#mapDecoyFireE').click();n1=p.evaluate('__ME_TEST__.own().srboc.expendedRounds');ck(tag+'.E4.SRBOCnative',n1-n0==2 and own(p)['lastResult']['ok']);ck(tag+'.E4.selectionUnchanged',selection==p.evaluate('({selection:__MAP_B__.snapshot().selection,target:__MAP_B__.snapshot().target})'));ck(tag+'.E4.cooldownReason',p.locator('#mapDecoyFireE').is_disabled()and'Mk 36 SRBOC 대기'in p.locator('.map-decoy-reason-e').inner_text());cap(p,tag+'-srboc-rejected');p.mouse.click(width/2,8)
    p.locator('[data-decoy-e="NULKA"]').click();ck(tag+'.E4.NulkaNativeNoCue',p.locator('#mapDecoyFireE').is_disabled()and'NO_VALID_ASM_BEARING'in p.locator('.map-decoy-reason-e').inner_text());p.mouse.click(width/2,8);p.evaluate('__ME_TEST__.cue()');p.locator('[data-decoy-e="NULKA"]').click();n0=p.evaluate('__ME_TEST__.own().nulka.expendedRounds');p.locator('#mapDecoyFireE').click();n1=p.evaluate('__ME_TEST__.own().nulka.expendedRounds');ck(tag+'.E4.NulkaNative',n1-n0==1 and own(p)['lastResult']['ok']);ck(tag+'.E4.NulkaSelectionUnchanged',selection==p.evaluate('({selection:__MAP_B__.snapshot().selection,target:__MAP_B__.snapshot().target})'));cap(p,tag+'-nulka')
    # Every ECM stage leaves native manual SRBOC/Nulka authority available.
    manual={}
    for level in ['OFF','JAM','FULL']:
     reset(p,s);p.evaluate('k=>__ME_TEST__.command(k)',level);p.evaluate('__ME_TEST__.cue()');p.locator('[data-decoy-e="SRBOC"]').click();p.locator('#mapDecoyFireE').click();a=own(p)['lastResult'];p.locator('[data-decoy-e="NULKA"]').click();p.locator('#mapDecoyFireE').click();bb=own(p)['lastResult'];manual[level]={'srboc':a,'nulka':bb};ck(tag+'.E4.manual.'+level,a['ok']and bb['ok'])
    records[tag+'.manual']=manual
    # New map paths are operator MANUAL irrespective of AAW mode.
    if ship.startswith('CG'):
     for mode in ['MANUAL','SEMIAUTO','AUTO']:
      reset(p,s);p.evaluate('m=>__MD_TEST__.mode(m)',mode);select(p,'HARPOON');tid=p.evaluate('__MD_TEST__.surface({rangeKm:10,bearingDeg:90})');q=target(p,tid,s);ck(tag+'.E5.preview.'+mode,q['model']['allowed']);p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tick(120)');r=p.evaluate('__MAP_D__.snapshot()');ck(tag+'.E5.release.'+mode,r['metrics']['hpReleased']>=1 and any(x['action']=='HARPOON_REQUEST'and x['ok']for x in r['log'][-8:]));records[tag+'.harpoon.'+mode]=r
     reset(p,s);select(p,'HARPOON');tid=p.evaluate('__MD_TEST__.surface({rangeKm:10,bearingDeg:90})');p.evaluate('id=>__MD_TEST__.observed(id,{_operatorIdentity:"NEUTRAL",identity:"NEUTRAL"})',tid);q=target(p,tid,s);ck(tag+'.E5.protection',not q['model']['allowed']and q['model']['reason']=='PROTECTED_IDENTITY')
     reset(p,s);select(p,'HARPOON');state=p.evaluate('__ME_TEST__.routeInput()');p.locator('#mapRouteChipButtonD').click();after=p.evaluate('__ME_TEST__.routeInput()');ck(tag+'.E6.noWindowAutoOpen',state['open']==after['open']and state['tab']==after['tab']and state['mode']==after['mode']);ck(tag+'.E6.HARPOON_INS',p.evaluate('__MAP_A__.snapshot().currentTool')=='HARPOON_INS');p.wait_for_timeout(150);pos=p.evaluate('s=>{const v=s==="PIP"?__PIP_A__.view().rect:__VIEWPORT_A__.snapshot().viewport.twoD;for(const fx of [.2,.35,.6,.8])for(const fy of [.35,.6,.8]){const x=v.x+v.w*fx,y=v.y+v.h*fy;if(__MAP_A__.hitTest(x,y,s).length===0)return{x,y};}}',s);p.mouse.click(pos['x'],pos['y']);p.wait_for_timeout(160);a=p.evaluate('__ME_TEST__.routeInput()');ck(tag+'.E6.onlyRoutePoint',a['points']==state['points']+1 and a['wp']==state['wp']);p.locator('#mapRouteChipButtonD').click();ck(tag+'.E6.exitNoWindowAutoOpen',p.evaluate('__ME_TEST__.routeInput().open')==state['open']);cap(p,tag+'-route')
    reset(p,s);p.locator('#uiEmconChipA').click();geo=p.locator('#mapEmconMenuE').bounding_box();ck(tag+'.E7.popoverInside',geo['x']>=0 and geo['y']>=0 and geo['x']+geo['width']<=width+1 and geo['y']+geo['height']<=height+1);ck(tag+'.E7.buttons28',p.locator('#mapEmconMenuE button').evaluate_all('es=>es.every(e=>e.getBoundingClientRect().height>=28&&e.getBoundingClientRect().width>=28)'));p.locator('[data-decoy-e="SRBOC"]').click();geo=p.locator('#mapDecoyMenuE').bounding_box();ck(tag+'.E7.decoyInside',geo['x']>=0 and geo['y']>=0 and geo['x']+geo['width']<=width+1 and geo['y']+geo['height']<=height+1);ck(tag+'.E7.fire40',p.locator('#mapDecoyFireE').bounding_box()['height']>=40);cap(p,tag+'-manual-popup');p.mouse.click(width/2,8);ck(tag+'.E4.outsideCloses',not own(p)['decoyOpen']);ck(tag+'.core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'))
   p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start};(E/('native-results.json'if os.environ.get('MAP_E_NATIVE_ONLY')else'results.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
