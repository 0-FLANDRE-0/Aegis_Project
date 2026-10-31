"""Save compatibility, manual refusal, read-only popups and scaled geometry."""
from pathlib import Path
import sys,json,hashlib,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();fixture=(H/'test-helper.js').read_text()+'\n'+(R/'docs/map/D/extension-fixture.js').read_text()+'\n'+(H/'test_e_fixture.js').read_text()+'''\nwindow.__ME_TEST__.saveLoad=()=>{const d=__NAVAL_SIM_DIAG__,before=d.exportOperationalStateV48Wip11A(),valid=d.validateOperationalStateV48Wip11A(before).ok;d.importOperationalStateV48Wip11A(before);const after=d.exportOperationalStateV48Wip11A();return {valid,beforeFields:Object.keys(before.ship.ew).sort(),afterFields:Object.keys(after.ship.ew).sort(),saved:before.ship.ew,level:ownEcmLevelE(),serializedStage:/ownEcm|ecmAutoLevel|JAM/.test(JSON.stringify(before))};};'''
E=H/'evidence/e-policy';E.mkdir(parents=True,exist_ok=True);checks={};records={};errors=[];start=time.perf_counter()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
with sync_playwright()as pw:
 b=launch(pw)
 for w,h in [(1400,900),(832,384)]:
  for ship in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   p=load_fleet(b,instrument(raw,fixture),own=ship,width=w,height=h,errors=errors);p.set_default_timeout(60000);tag=f'{w}.{ship[:2]}';p.evaluate('__ME_TEST__.reset();__ME_TEST__.command("JAM")');q=p.evaluate('__ME_TEST__.saveLoad()');ck(tag+'.saveJAMinfersFULL',q['valid']and q['level']=='FULL');ck(tag+'.saveSchemaSame',q['beforeFields']==q['afterFields']==['auto','autoAim','bearingRad','deceptionRequested','emcon','noiseRequested']and not q['serializedStage']);records[tag+'.save']=q
   p.evaluate('__ME_TEST__.reset()');before=p.evaluate('__MB_TEST__.commandState()');p.locator('#uiEmconChipA').click();p.wait_for_timeout(400);p.locator('#uiEmconChipA').click();p.locator('[data-decoy-e="NULKA"]').click();p.wait_for_timeout(400);ck(tag+'.previewReadOnly',before==p.evaluate('__MB_TEST__.commandState()'));p.mouse.click(w/2,8)
   p.evaluate('__ME_TEST__.cue();__ME_TEST__.noStock("NULKA")');p.locator('[data-decoy-e="NULKA"]').click();ck(tag+'.nulkaNoStockNativeReason',p.locator('#mapDecoyFireE').is_disabled()and p.locator('.map-decoy-reason-e').inner_text()=='NO_READY_CANISTER');p.mouse.click(w/2,8);p.evaluate('__ME_TEST__.noStock("SRBOC")');p.locator('[data-decoy-e="SRBOC"]').click();ck(tag+'.srbocNoStockNativeReason',p.locator('#mapDecoyFireE').is_disabled()and'발사관 탄약 없음'in p.locator('.map-decoy-reason-e').inner_text());p.mouse.click(w/2,8)
   for scale in [85,100,130]:
    p.evaluate('s=>__UI_A__.setScale(s)',scale);p.wait_for_timeout(180);p.locator('#uiEmconChipA').click();p.wait_for_timeout(120);menu=p.locator('#mapEmconMenuE').bounding_box();p.locator('[data-decoy-e="NULKA"]').click();p.wait_for_timeout(120);decoy=p.locator('#mapDecoyMenuE').bounding_box();inside=lambda g:g['x']>=-1 and g['y']>=-1 and g['x']+g['width']<=w+1 and g['y']+g['height']<=h+1;ck(tag+'.scale'+str(scale)+'.inside',inside(menu)and inside(decoy));records[tag+'.scale'+str(scale)]={'menu':menu,'decoy':decoy,'fire':p.locator('#mapDecoyFireE').bounding_box()};p.mouse.click(w/2,8)
   p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start};(E/'policy.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));assert out['pass']
