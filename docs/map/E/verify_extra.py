"""Explicit precision, UI-only state, native multi-round variants and actual WebGL PiP."""
from pathlib import Path
import sys,json,hashlib,base64
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/extra';E.mkdir(parents=True,exist_ok=True);raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
with sync_playwright()as pw:
 b=launch(pw,True)
 for width,height in [(1400,900),(832,384)]:
  tag=str(width);p=load_fleet(b,instrument(raw,(H/'test-helper.js').read_text()),width=width,height=height,errors=errors);p.set_default_timeout(15000);reset(p);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');target(p,tid);p.locator('#mapPrecisionA').click();ck(tag+'.explicitPrecisionExactId',p.evaluate('__MB_TEST__.state().lock')==tid);p.evaluate('__UI_A__.close("INFO")')
  # Warm native chart caches, then exercise browsing/selection without a simulation tick.
  reset(p);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');p.wait_for_timeout(350)
  result=p.evaluate('''id=>{const before=__MB_TEST__.commandState();for(let i=0;i<200;i++){const w=i%2?'SM2':'ESSM';document.querySelector('[data-weapon-b="'+w+'"]').click();const n=document.querySelector('#mapSalvoB button');if(n&&!n.disabled)n.click();const o=__MAP_A__.objects().find(o=>o.id===id&&o.kind==='TRACK');__MAP_B__.pickObject(o,i%2?'PIP':'MAIN');__MAP_B__.refresh(true);document.getElementById('mapCancelB').click();document.getElementById('uiStatusBarA').click();}return{actions:200,exact:before===__MB_TEST__.commandState()};}''',tid);records[tag+'.200']=result;ck(tag+'.200NoCommandNoTrackRngMutation',result['exact'])
  for w in ['SM2','SM2ER','ESSM']:
   reset(p);select(p,w,2);p.evaluate('__VIEWPORT_A__.setDistance(70)');tid=p.evaluate('c=>__MB_TEST__.add(c)',{'rangeKm':42 if w=='ESSM'else 10,'altM':1000});q=target(p,tid);p.locator('#mapFireB').click();p.evaluate('__MB_TEST__.tick(49)');s=p.evaluate('__MB_TEST__.state()');ck(tag+'.native2.'+w,len(s['log']['history'])==2 and all(q['weapon']==w for q in s['log']['history']));records[tag+'.native2.'+w]=s['log']
  reset(p);select(p,'SM6',1);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open();__UI_A__.open("CIC");__PIP_A__.setDistance(40)}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000,polling=50);p.wait_for_timeout(450);q=target(p,tid,'PIP');old=p.evaluate('__WIP148_3D_VIEW__.renderer.info.render.frame');p.wait_for_function('n=>__WIP148_3D_VIEW__.renderer.info.render.frame>n',arg=old,timeout=30000,polling=50);ck(tag+'.actualWebGLPiP',q['target']['surface']=='PIP'and q['model']['allowed']);
  c=p.context.new_cdp_session(p)
  try:(E/(tag+'-webgl-pip.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
  finally:c.detach()
  p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'extra.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
