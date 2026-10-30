from pathlib import Path
import sys,json,hashlib,base64
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/rules';E.mkdir(parents=True,exist_ok=True);checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def cap(p,name):p.screenshot(path=str(E/(name+'.png')))
def close(p,surface):
 p.evaluate('s=>{for(const id of Object.keys(__UI_A__.snapshot().windows))if(id!=="CIC"||s!=="PIP")__UI_A__.close(id);document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));}',surface);p.wait_for_timeout(200)
def xy(p,o,s):return p.evaluate('a=>a.s==="PIP"?__PIP_A__.worldToScreen(a.o.x,a.o.y):__VIEWPORT_A__.worldToScreen(a.o.x,a.o.y)',{'s':s,'o':o})
def click(p,key,s):
 close(p,s);o=p.evaluate('k=>__MAP_A__.objects().find(o=>o.key===k)',key);pos=xy(p,o,s);p.mouse.click(pos['x'],pos['y']);p.wait_for_timeout(150);return o
with sync_playwright()as pw:
 b=launch(pw,True)
 for w,h in [(1400,900),(832,384)]:
  raw=(R/'Aegis_SIM_v48_WIP_MAP_C.html').read_bytes();p=load_fleet(b,instrument(raw,(H/'test-helper.js').read_text()+'\n'+(H/'motion-helper.js').read_text()),width=w,height=h,errors=errors);p.set_default_timeout(60000)
  for surface in ['MAIN','PIP']:
   if surface=='PIP':p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000)
   reset(p)
   if surface=='PIP':p.evaluate('__UI_A__.open("CIC");__PIP_A__.setDistance(15)')
   else:p.evaluate('__WIP148_3D_VIEW__.close()')
   p.evaluate('__VIEWPORT_A__.setDistance(15)');tag=f'{w}.{surface}';key=p.evaluate('__MC_TEST__.ally()');old=p.evaluate('__MAP_A__.snapshot().controlPlatform');click(p,key,surface);ck(tag+'.allyInfoOnly',p.evaluate('__MAP_A__.snapshot().lookupTarget')==key and p.evaluate('__MAP_A__.snapshot().controlPlatform')==old);ck(tag+'.allyControlDisabled',p.locator('#mapControlA').is_disabled()and'항로 명령 미지원'in p.locator('#uiWindowA-INFO').inner_text());cap(p,tag+'-ally')
   click(p,'OWN',surface);old=p.evaluate('__MAP_A__.snapshot().controlPlatform');ck(tag+'.ownTapNoControl',p.evaluate('__MAP_A__.snapshot().controlPlatform')==old)
   if old!='OWN':p.locator('#mapControlA').click()
   ck(tag+'.explicitControl',p.evaluate('__MAP_A__.snapshot().controlPlatform')=='OWN');close(p,surface);v=p.evaluate('__PIP_A__.view().rect'if surface=='PIP'else'__VIEWPORT_A__.snapshot().viewport.twoD');spots=[{'x':v['x']+v['w']*.2,'y':v['y']+v['h']*.2},{'x':v['x']+v['w']*.8,'y':v['y']+v['h']*.2}];pos=next(o for o in spots if not p.evaluate('a=>__MAP_A__.hitTest(a.p.x,a.p.y,a.s)',{'p':o,'s':surface}));n=p.evaluate('__MC_TEST__.state().waypoints');p.mouse.click(pos['x'],pos['y']);ck(tag+'.seaOneWaypoint',p.evaluate('__MC_TEST__.state().waypoints')==n+1);p.locator('#mapUndoA').click();ck(tag+'.undoOne',p.evaluate('__MC_TEST__.state().waypoints')==n)
   click(p,'OWN',surface);p.evaluate('document.getElementById("modeAimBtn").click();__HARPOON_DIAG_A__.routeToggle()');p.wait_for_function('()=>document.getElementById("mapControlA").disabled&&document.getElementById("uiWindowA-INFO").innerText.includes("하푼 계획 작성 중")');p.evaluate('__MAP_A__.snapshot()');ck(tag+'.planBlocksControl',p.locator('#mapControlA').is_disabled()and'하푼 계획 작성 중'in p.locator('#uiWindowA-INFO').inner_text());p.evaluate('__HARPOON_DIAG_A__.routeToggle()');close(p,surface)
   # Location-free bearing is still unjudgeable and never produces a hidden coordinate.
   select(p,'SM6');key=p.evaluate('__MB_TEST__.esm()');p.wait_for_timeout(200);own=xy(p,{'x':0,'y':0},surface);pos={'x':own['x']+34,'y':own['y']+34};p.mouse.click(pos['x'],pos['y']);p.wait_for_timeout(200);q=snap(p);ck(tag+'.esmUnknown',q['target']is not None and q['target']['key']==key and q['model']['verdict']=='판정 불가'and q['model']['reason']=='위치 정보 없음'and not q['model']['allowed']);ck(tag+'.esmRedReason',p.locator('#mapEngagementB .map-status-dot-c').get_attribute('data-tone')=='blocked'and p.locator('#mapEngagementB .map-verdict-b').inner_text()=='위치 정보 없음');cap(p,tag+'-esm')
   p.locator('#mapCancelB').click();p.wait_for_timeout(180);view=p.evaluate('__PIP_A__.view()'if surface=='PIP'else'()=>({target:"MAIN",rect:__VIEWPORT_A__.snapshot().viewport.twoD,center:{x:0,y:0},km:15})');view['km']=15;labels=p.evaluate('v=>__MC_TEST__.ringLabels(v)',view);clock=p.locator('#mapTimeBlockC').bounding_box();arrow=[a for a in labels if a['text'].startswith('→')];overlaps=[max(0,min(a['x']+a['w'],clock['x']+clock['width'])-max(a['x'],clock['x']))*max(0,min(a['y']+a['h'],clock['y']+clock['height'])-max(a['y'],clock['y']))for a in arrow];ck(tag+'.C1.arrowClockOverlap0',bool(arrow)and all(a<.01 for a in overlaps));ck(tag+'.C1.arrow9',all(abs(a['fontPx']-9)<1e-6 for a in arrow));records[tag+'.labels']={'labels':labels,'clock':clock,'overlapArea':overlaps};cap(p,tag+'-initial-rings')
  p.close()
 b.close()
ck('pageErrors0',not errors);q={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'rules.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if q['pass']else 1)
