from pathlib import Path
import sys,json,hashlib,base64
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/warnings';E.mkdir(parents=True,exist_ok=True);raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();checks={};records=[];errors=[]
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def capture(p,name):
 c=p.context.new_cdp_session(p)
 try:(E/(name+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
 finally:c.detach()
with sync_playwright()as pw:
 b=launch(pw)
 for w,h in [(1400,900),(832,384)]:
  p=load_fleet(b,instrument(raw,(H/'test-helper.js').read_text()+'\n'+(H/'warning-helper.js').read_text()),width=w,height=h,errors=errors);p.set_default_timeout(180000)
  for name,weapon,rng,alt,spd in [('deadzone','SM2',3,30,680),('maximum','SM6',296,1000,0),('below-effective','SM2',1,30,0)]:
   tag=str(w)+'.'+name;reset(p);select(p,weapon);p.evaluate('k=>__VIEWPORT_A__.setDistance(k)',max(4,rng*1.5));tid=p.evaluate('c=>__MB_TEST__.realWarning(c)',{'rangeKm':rng,'altM':alt,'speedMps':spd});q=target(p,tid);text=p.locator('.map-verdict-b').inner_text();tone=p.locator('.map-verdict-b').get_attribute('data-tone');ck(tag+'.warningEnabled',q['model']['allowed']and not p.locator('#mapFireB').is_disabled());ck(tag+'.orange',tone=='warning'and'명중 확률 낮음'in text);capture(p,str(w)+'-'+name+'-enabled');before=p.evaluate('__MB_TEST__.state()');p.locator('#mapFireB').click();after=p.evaluate('__MB_TEST__.state()');ck(tag+'.nativeShot',after['missiles']==before['missiles']+1 and len(after['log']['history'])==1 and after['log']['history'][0]['weapon']==weapon);flight=p.evaluate('__MB_TEST__.runWarningFlight()')if w==1400 and '--release-only' not in sys.argv else None;records.append({'size':[w,h],'scenario':name,'condition':{'weapon':weapon,'rangeKm':rng,'altM':alt,'targetSpeedMps':spd},'before':q,'label':text,'tone':tone,'release':after['log']['history'],'flight':flight})
  reset(p);select(p,'SM2');p.evaluate('__VIEWPORT_A__.setDistance(.1)');tid=p.evaluate('__MB_TEST__.surfaceNear()');q=target(p,tid);ck(str(w)+'.nativePhysicalMinStillBlocked',not q['model']['allowed']and'SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE'in q['model']['reason']and p.locator('.map-verdict-b').get_attribute('data-tone')=='blocked');capture(p,str(w)+'-native-min-blocked');records.append({'scenario':'native-surface-minimum','size':[w,h],'ui':q})
  reset(p);select(p,'SM6');tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');q=target(p,tid);ck(str(w)+'.effectiveGreen',q['model']['allowed']and p.locator('.map-verdict-b').get_attribute('data-tone')=='effective');capture(p,str(w)+'-effective-green');p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'warnings.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
