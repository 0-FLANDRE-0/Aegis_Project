"""Native PIP_B UI acceptance; canvas/client geometry is measured, not inferred."""
import argparse,base64,hashlib,json,math,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'docs/helicopter/H'));from browser import launch,load_fleet
p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);productRaw=a.html.read_bytes();raw=productRaw;sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import instrument;raw=instrument(raw,'window.__UI88_EXACT_LOCK__=id=>mapPrecisionCommandA(mapTrackReadA(id,tracks.get(id)));');checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v)
def capture(p,name):
 s=p.context.new_cdp_session(p)
 try:(a.out/name).write_bytes(base64.b64decode(s.send('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']))
 finally:s.detach()
def close(p):p.evaluate("()=>{for(const k of Object.keys(__UI_A__.snapshot().windows))__UI_A__.close(k);document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))}")
with sync_playwright()as pw:
 b=launch(pw);native=b.new_page
 def page(**kw):
  kw.update(device_scale_factor=2.8125,has_touch=True);p=native(**kw);p.add_init_script("Element.prototype.requestFullscreen=()=>Promise.reject(Error('geometry fixture'))");return p
 b.new_page=page
 for w,h in [(1400,900),(832,384),(384,832)]:
  p=load_fleet(b,raw,errors=errors,width=w,height=h);close(p);p.evaluate('__WIP148_3D_VIEW__.active=true;__UI_A__.open("CIC")');p.wait_for_timeout(500)
  for scale in [85,100,130]:
   tag=f'{w}.{scale}';p.evaluate('s=>__UI_A__.setScale(s)',scale);p.wait_for_timeout(250)
   q=p.evaluate('''()=>{const w=document.getElementById('uiWindowA-CIC'),t=w.querySelector('.ui-title-a'),c=document.getElementById('external3DMiniCicCanvas'),r=e=>e.getBoundingClientRect().toJSON(),z=__UI_A_SETTINGS__.scale;return {win:r(w),title:r(t),canvas:r(c),clientHeight:w.clientHeight*z,clientWidth:w.clientWidth*z,buttons:[...w.querySelectorAll('.ui-body-a button')].filter(e=>e.getBoundingClientRect().height>0).length,titleButtons:[...t.querySelectorAll('button')].map(e=>e.textContent),font:getComputedStyle(t.querySelector('.ui-window-name-a')).fontSize}}''')
   ck(tag+'.P1.fullClientArea',abs(q['canvas']['height']-(q['clientHeight']-q['title']['height']))<=1 and abs(q['canvas']['width']-q['clientWidth'])<=1);ck(tag+'.P1.buttons0',q['buttons']==0);ck(tag+'.P1.titleActions',q['titleButtons']==['≡','□','×']);ck(tag+'.P3.titleFont11',q['font']=='11px');records[tag]=q
  p.evaluate('__UI_A__.setScale(100);__PIP_A__.setCenter({x:50,y:70})');p.wait_for_timeout(250);p.locator('#uiWindowA-CIC button[title="창 메뉴"]').click();p.locator('#pipCenterA').click();ck(f'{w}.P1.titleCenter',p.evaluate('__PIP_A__.snapshot().follow'));p.locator('#uiWindowA-CIC button[title="창 메뉴"]').click();p.locator('#pipSwapA').click();ck(f'{w}.P1.titleSwap',not p.evaluate('__WIP148_3D_VIEW__.active'))
  p.evaluate('__WIP148_3D_VIEW__.active=true;__UI_A__.open("CIC");__PIP_A__.setDistance(40)');p.wait_for_timeout(200);v=p.evaluate('__PIP_A__.view().rect');x=v['x']+v['w']*.8;y=v['y']+v['h']*.2;p.mouse.click(x,y,button='right');ck(f'{w}.P1.contextActions',p.locator('#pipContextCenterB').count()==1 and p.locator('#pipContextSwapB').count()==1);p.locator('#pipContextCenterB').click();ck(f'{w}.P1.contextCenter',p.evaluate('__PIP_A__.snapshot().follow'));p.mouse.click(x,y,button='right');p.locator('#pipContextSwapB').click();ck(f'{w}.P1.contextSwap',not p.evaluate('__WIP148_3D_VIEW__.active'))
  close(p);p.evaluate('__UI_A__.open("DEBUG")');ck(f'{w}.P4.defaultOff',not p.locator('#sensorBeams2DB').is_checked());p.evaluate('__PIP_A__.prepare();__VIEWPORT_A__.draw();__PIP_A__.paint()');ck(f'{w}.P4.defaultDraw0',p.evaluate('__PIP_B__.snapshot().stats.beamGroups===0'));p.locator('#sensorBeams2DB').check();before=p.evaluate('__PIP_B__.snapshot().stats.beamGroups');p.evaluate('__VIEWPORT_A__.draw();__PIP_A__.paint()');ck(f'{w}.P4.enabledDraws',p.evaluate('__PIP_B__.snapshot().stats.beamGroups')>before);p.locator('#sensorBeams2DB').uncheck();close(p)
  # Actual native manual lock, with no alternate setter for selectedLockId.
  p.evaluate('()=>{__WIP148_3D_VIEW__.active=false;if(__UI_A__.snapshot().modeMenu.emcon)document.getElementById("emconBtn").click()}')
  p.wait_for_timeout(350)
  tid=p.evaluate('__NAVAL_SIM_DIAG__.wip114DiagAddTrack({rangeKm:10,bearingDeg:0,altM:1000,speedMps:0})');p.wait_for_timeout(100);o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',tid);point=p.evaluate('o=>__VIEWPORT_A__.worldToScreen(o.x,o.y)',o);p.mouse.click(point['x'],point['y']);p.evaluate('id=>__UI88_EXACT_LOCK__(id)',tid);p.wait_for_timeout(300);ck(f'{w}.P2.autoOpen',p.evaluate('__PIP_B__.snapshot().open&&__PIP_B__.snapshot().lastLock!==null'))
  text=p.locator('#lockedTargetTextB').inner_text();ck(f'{w}.P2.originalFields',text.startswith('T')and'POSσ'in text and'ALT'in text)
  # No canvas fillText receives an original card row in either renderer.
  canvas=p.evaluate(r'''()=>{const rows=document.getElementById('lockedTargetTextB').textContent.split('\n'),old=CanvasRenderingContext2D.prototype.fillText;let n=0;CanvasRenderingContext2D.prototype.fillText=function(t,...args){if(rows.includes(String(t)))n++;return old.call(this,t,...args)};try{__VIEWPORT_A__.draw();__PIP_A__.renderView(__PIP_A__.view());return n;}finally{CanvasRenderingContext2D.prototype.fillText=old;}}''');ck(f'{w}.P2.canvasCards0',canvas==0)
  close(p);p.evaluate('__WIP148_3D_VIEW__.active=true;__UI_A__.open("CIC");__UI_A__.open("LOCKED")');p.wait_for_timeout(1300);n=p.evaluate('__PIP_B__.snapshot().stats.lockedRefreshes');p.wait_for_timeout(2000);hz=(p.evaluate('__PIP_B__.snapshot().stats.lockedRefreshes')-n)/2;ck(f'{w}.P2.independentHz',5<=hz<=10);records[f'{w}.lockedHz']=hz
  p.locator('#uiWindowA-LOCKED button[title="닫기"]').click();p.wait_for_timeout(400);ck(f'{w}.P2.closeSuppression',not p.evaluate('__PIP_B__.snapshot().open'));p.evaluate('__AEGIS_WIP14A14_ENGAGEMENT_UI__.clearLock("PIP_B_FIXTURE")');p.wait_for_timeout(180);ck(f'{w}.P2.unlockText',p.locator('#lockedTargetTextB').inner_text()=='락 없음');p.evaluate('id=>__UI88_EXACT_LOCK__(id)',tid);p.wait_for_timeout(180);ck(f'{w}.P2.relockReopens',p.evaluate('__PIP_B__.snapshot().open'))
  p.evaluate('__UI_A__.open("INFO")');p.wait_for_timeout(150);font=p.locator('.map-info-a').evaluate('e=>({font:getComputedStyle(e).fontSize,line:getComputedStyle(e).lineHeight,width:document.getElementById("uiWindowA-INFO").getBoundingClientRect().width})');ck(f'{w}.P3.info11',font['font']=='11px'and abs(float(font['line'].removesuffix('px'))-14.3)<.1);records[f'{w}.info']=font
  capture(p,f'dense-locked-{w}.png');ck(f'{w}.core',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'));p.close()
 b.close()
ck('pageErrors',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(productRaw).hexdigest()};(a.out/'ui.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
