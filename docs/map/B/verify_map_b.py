from pathlib import Path
import sys,json,hashlib,base64,time,math
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet,instrument
E=H/'evidence/map-b';E.mkdir(parents=True,exist_ok=True);raw=(R/'Aegis_SIM_v48_WIP_MAP_B.html').read_bytes();checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def snap(p):p.evaluate('__MAP_B__.refresh(true)');return p.evaluate('__MAP_B__.snapshot()')
def screenshot(p,name):
 c=p.context.new_cdp_session(p)
 try:(E/(name+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
 finally:c.detach()
def reset(p):p.evaluate('__MB_TEST__.reset()');p.wait_for_timeout(320)
def select(p,w='SM2',n=1):p.locator('[data-weapon-b="'+w+'"]').click();p.locator('[data-salvo-b="'+str(n)+'"]').click();p.wait_for_timeout(80)
def target(p,id,surface='MAIN'):
 p.wait_for_timeout(130);o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',id);pt=p.evaluate('(a)=>a.surface==="PIP"?__PIP_A__.worldToScreen(a.o.x,a.o.y):__VIEWPORT_A__.worldToScreen(a.o.x,a.o.y)',{'o':o,'surface':surface});p.mouse.click(pt['x'],pt['y']);p.wait_for_timeout(160);
 if p.evaluate('__MAP_A__.snapshot().candidatesOpen'):
  p.locator('#mapCandidatesA button').filter(has_text=o['label']).first.click();p.wait_for_timeout(100)
 return snap(p)
with sync_playwright()as pw:
 b=launch(pw)
 for width,height in [(1400,900),(832,384)]:
  p=load_fleet(b,instrument(raw,(H/'test-helper.js').read_text()),width=width,height=height,errors=errors);p.set_default_timeout(12000);tag=str(width)
  reset(p);p.locator('[data-weapon-b="SM2"]').click();ck(tag+'.M1.pendingOnly',snap(p)['selection']is None);screenshot(p,tag+'-salvo');p.locator('[data-salvo-b="2"]').click();ck(tag+'.M1.commit',snap(p)['selection']=={'weapon':'SM2','count':2});p.locator('[data-weapon-b="ESSM"]').click();ck(tag+'.M1.keepUntilCount',snap(p)['selection']['weapon']=='SM2');p.locator('[data-salvo-b="3"]').click();ck(tag+'.M1.change',snap(p)['selection']=={'weapon':'ESSM','count':3});p.locator('#uiPauseA').click();ck(tag+'.M1.otherButton',snap(p)['selection']['weapon']=='ESSM');p.locator('[data-weapon-b="ESSM"]').click();ck(tag+'.M1.repeatClear',snap(p)['selection']is None);select(p);p.evaluate('document.getElementById("uiStatusBarA").click()');ck(tag+'.M1.blankClear',snap(p)['selection']is None)
  reset(p);select(p);screenshot(p,tag+'-initial-rings');ck(tag+'.M2.initial',snap(p)['model']['initial']);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');before=p.evaluate('__MB_TEST__.state()');q=target(p,tid);after=p.evaluate('__MB_TEST__.state()');ck(tag+'.M2.targetSingle',q['target']is not None and not q['model']['initial']);ck(tag+'.M7.selectionNoCommand',before==after);ck(tag+'.M7.nativePreviewReadOnly',p.evaluate('id=>__MB_TEST__.previewAudit(id,"SM2").exact',tid));screenshot(p,tag+'-effective');ck(tag+'.M3.effective',q['model']['verdict']=='유효'and q['model']['allowed']);p.locator('#mapCancelB').click();ck(tag+'.M2.cancel',snap(p)['model']['initial']and snap(p)['selection']is not None)
  # No weapon: passive INFO leaves lockCursor unchanged; precision remains explicit.
  p.evaluate('document.getElementById("uiStatusBarA").click()');s=p.evaluate('__MB_TEST__.state()');target(p,tid);ck(tag+'.M7.noLegacyBridge',s==p.evaluate('__MB_TEST__.state()')and p.evaluate('__MAP_A__.snapshot().lookupTarget')=='TRACK:'+str(tid))
  p.evaluate('__UI_A__.close("INFO")');select(p);target(p,tid);p.locator('[data-weapon-b="ESSM"]').click();p.locator('[data-salvo-b="1"]').click();ck(tag+'.M1.weaponChangeKeepsTarget',snap(p)['target']['key']=='TRACK:'+str(tid))
  # Six table-based verdicts, using only synthetic observed-track reports.
  for name,rng,alt,spd in [('maximum',200,30,0),('minimum',1,30,0),('outside',220,30,0),('deadzone',3,30,680)]:
   reset(p);select(p);p.evaluate('k=>__VIEWPORT_A__.setDistance(k)',max(5,rng*1.5));tid=p.evaluate('c=>__MB_TEST__.add(c)',{'rangeKm':rng,'altM':alt,'speedMps':spd});q=target(p,tid);records[tag+'.'+name]=q;expect={'maximum':'최대 사거리 구간','minimum':'최소 사거리 안쪽','outside':'사거리 밖','deadzone':'사각지대'}[name];ck(tag+'.M3.'+name,q['model']['verdict']==expect);screenshot(p,tag+'-'+name)
  reset(p);select(p);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');p.evaluate('id=>__MB_TEST__.patch(id,{z:null})',tid);q=target(p,tid);ck(tag+'.M4.altUnknown',q['model']['altitudeUnknown']);screenshot(p,tag+'-alt-unknown');p.evaluate('id=>__MB_TEST__.lost(id)',tid);p.wait_for_timeout(200);q=snap(p);ck(tag+'.M4.lost',q['model']['reason']=='트랙 소실'and not q['model']['allowed']);screenshot(p,tag+'-lost')
  reset(p);select(p);p.evaluate('__MB_TEST__.esm()');p.wait_for_timeout(150);# choose an outer section of the observed bearing ray
  v=p.evaluate('__VIEWPORT_A__.snapshot().viewport.twoD');own=p.evaluate('__VIEWPORT_A__.worldToScreen(0,0)');# use public observed hit test to find a bearing-only section
  hit=p.evaluate('()=>{const v=AEGIS_VIEWPORT.twoD;for(let y=v.y+50;y<v.y+v.h-5;y+=8)for(let x=v.x+50;x<v.x+v.w-5;x+=8){const h=__MAP_A__.hitTest(x,y);if(h.length===1&&h[0].kind==="ESM")return{x,y};}return null;}') if False else p.evaluate('()=>{const v=__VIEWPORT_A__.snapshot().viewport.twoD;for(let y=v.y+50;y<v.y+v.h-5;y+=8)for(let x=v.x+50;x<v.x+v.w-5;x+=8){const h=__MAP_A__.hitTest(x,y);if(h.length===1&&h[0].kind==="ESM")return{x,y};}return null;}')
  p.mouse.click(hit['x'],hit['y']);q=snap(p);ck(tag+'.M3.undetermined',q['model']['verdict']=='판정 불가');ck(tag+'.M4.esm',q['model']['reason']=='위치 정보 없음'and not q['model']['allowed']);screenshot(p,tag+'-esm')
  # Real native VLS 1/2/3/4, fixed-tick cadence. Keep synthetic observations fresh.
  for n in [1,2,3,4]:
   reset(p);select(p,'SM6',n);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');target(p,tid);p.locator('#mapFireB').click();tickdiag=p.evaluate('n=>__MB_TEST__.tick(n)',int((n-1)*48+1));print('tickdiag',tickdiag,flush=True);q=snap(p);s=p.evaluate('__MB_TEST__.state()');log=s['log']['history'];ck(tag+'.M5.salvo'+str(n),len(log)==n and all(r['weapon']=='SM6'and r['mode']=='MANUAL'for r in log));ck(tag+'.M5.cadence'+str(n),all(log[i]['step']-log[i-1]['step']>=48 for i in range(1,len(log))));ck(tag+'.M5.keep'+str(n),q['selection']=={'weapon':'SM6','count':n}and q['target']is not None);records[tag+'.salvo'+str(n)]={'log':log,'ui':q};print(json.dumps({'salvo':n,'ui':q}),flush=True)
  reset(p);p.evaluate('__MB_TEST__.stock("SM6",1)');p.wait_for_timeout(350);p.locator('[data-weapon-b="SM6"]').click();ck(tag+'.M5.shortage',all(p.locator('[data-salvo-b="'+str(n)+'"]').is_disabled()for n in [2,3,4]));p.evaluate('document.getElementById("uiStatusBarA").click();__MB_TEST__.stock("SM6",0)');p.wait_for_timeout(400);ck(tag+'.M5.zero',p.locator('[data-weapon-b="SM6"]').is_disabled())
  reset(p);select(p);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');p.evaluate('id=>__MB_TEST__.evidence(id,"FRIEND")',tid);q=target(p,tid);ck(tag+'.M5.protected',not q['model']['allowed']and bool(q['model']['reason']));screenshot(p,tag+'-disabled')
  # PiP uses its own observed hit positions and the same selected weapon/target.
  reset(p);select(p,'SM6',1);tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');p.evaluate('__WIP148_3D_VIEW__.active=true;__UI_A__.open("CIC");__PIP_A__.setDistance(40)');p.wait_for_timeout(350);q=target(p,tid,'PIP');ck(tag+'.M6.pipTarget',q['target']['surface']=='PIP'and q['model']['allowed']);p.locator('#mapFireB').click();ck(tag+'.M6.pipFire',len(p.evaluate('__MB_TEST__.state().log.history'))==1);screenshot(p,tag+'-pip')
  g=p.locator('#mapEngagementB').bounding_box();f=p.locator('#mapFireB').bounding_box();c=p.locator('#mapCancelB').bounding_box();records[tag+'.geometry']={'pane':g,'fire':f,'cancel':c};ck(tag+'.M9.fire40gap8',f['height']>=40 and c['x']-(f['x']+f['width'])>=8-.1);ck(tag+'.M9.paneInside',g['x']>=0 and g['y']>=0 and g['x']+g['width']<=width+1 and g['y']+g['height']<=height+1);ck(tag+'.removedWidget',p.locator('#wip14a14QuickEngage3D').count()==0);ck(tag+'.nodeIntegrity',p.evaluate('__UI_A__.snapshot().originalNodesConnected&&__UI_A__.snapshot().duplicateIds.length===0'));records[tag+'.status']=p.evaluate('__ENV_D__.status()');ck(tag+'.envelopeMatch',records[tag+'.status']['match']);p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'map-b.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if out['pass']else 1)
