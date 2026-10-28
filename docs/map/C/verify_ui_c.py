from pathlib import Path
import sys,json,hashlib,base64,math
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/new-ui';E.mkdir(parents=True,exist_ok=True);raw=(R/'Aegis_SIM_v48_WIP_MAP_C.html').read_bytes();checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def cap(p,name):
 c=p.context.new_cdp_session(p)
 try:(E/(name+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
 finally:c.detach()
def context(p,surface):
 reset(p)
 if surface=='PIP':p.evaluate('__UI_A__.open("CIC");__PIP_A__.setDistance(40)')
 else:p.evaluate('__WIP148_3D_VIEW__.close()')
 p.wait_for_timeout(550)
def select(p,w='SM2',n=1):
 e=p.locator('[data-weapon-b="'+w+'"]');e.wait_for(state='visible');p.wait_for_function('w=>!document.querySelector("[data-weapon-b="+w+"]").disabled',arg=w);r=e.bounding_box();p.mouse.click(r['x']+r['width']/2,r['y']+r['height']/2);e=p.locator('[data-salvo-b="'+str(n)+'"]');e.wait_for(state='visible');r=e.bounding_box();p.mouse.click(r['x']+r['width']/2,r['y']+r['height']/2);p.wait_for_timeout(120)
def tap_object(p,key,surface):
 p.wait_for_timeout(130);o=p.evaluate('key=>__MAP_A__.objects().find(o=>o.key===key)',key);v=p.evaluate('__PIP_A__.view()'if surface=='PIP'else'__VIEWPORT_A__.snapshot().twoD')if False else None
 pos=p.evaluate('a=>{const q=__MAP_C__.pointFor(a.o)??a.o;return a.surface==="PIP"?__PIP_A__.worldToScreen(q.x,q.y):__VIEWPORT_A__.worldToScreen(q.x,q.y)}',{'o':o,'surface':surface});p.mouse.click(pos['x'],pos['y']);p.wait_for_timeout(150);return snap(p),pos
with sync_playwright()as pw:
 b=launch(pw,True);native=b.new_page
 def make_page(**kw):
  p=native(**kw);p.add_init_script((H/'node-audit.js').read_text());return p
 b.new_page=make_page
 fixture=(H/'test-helper.js').read_text()+'\n'+(H/'motion-helper.js').read_text()
 for width,height in [(1400,900),(832,384)]:
  p=load_fleet(b,instrument(raw,fixture),width=width,height=height,errors=errors);p.set_default_timeout(60000)
  for surface in ['MAIN','PIP']:
   tag=str(width)+'.'+surface
   if surface=='PIP':p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000,polling=50)
   context(p,surface);before=p.evaluate('__MC_TEST__.barBoxes()');select(p,'SM6',2);p.wait_for_timeout(200);weap=p.evaluate('__MC_TEST__.barBoxes()');tid=p.evaluate('__MB_TEST__.add({rangeKm:10,altM:1000})');q,_=tap_object(p,'TRACK:'+str(tid),surface);after=p.evaluate('__MC_TEST__.barBoxes()')
   def boxdiff(a,b):return max(abs(a[k][v]-b[k][v])for k in a for v in ['x','y','width','height'])
   ck(tag+'.C4.reserveInvariant',boxdiff(before,weap)<.01 and boxdiff(before,after)<.01);records[tag+'.barInvariantPx']=max(boxdiff(before,weap),boxdiff(before,after))
   geom=p.evaluate('''()=>{const e=document.getElementById('mapFireB'),f=e.getBoundingClientRect(),em=document.getElementById('uiEmconChipA').getBoundingClientRect(),h=parseFloat(getComputedStyle(e,'::after').height)*__UI_A_SETTINGS__.scale;return{visibleH:f.height,hitH:h,hitW:f.width,gap:em.x-f.right,inBar:document.getElementById('uiStatusBarA').contains(e),notInTag:!document.getElementById('mapEngagementB').contains(e),overflow:document.documentElement.scrollWidth>innerWidth}}''')
   ck(tag+'.C4.hit40by72',geom['hitH']>=39.9 and geom['hitW']>=71.9);ck(tag+'.C4.emcon12',geom['gap']>=11.9);ck(tag+'.C4.fireMovedOnly',geom['inBar']and geom['notInTag']and not geom['overflow']);records[tag+'.fireGeometry']=geom
   ck(tag+'.C3.greenTwoRows',q['model']['allowed']and p.locator('.map-status-dot-c').first.get_attribute('data-tone')=='effective'and p.locator('#mapEngagementB .map-verdict-b').is_hidden());cap(p,tag+'-effective')
   ck(tag+'.C3.tag9px',p.locator('#mapEngagementB').evaluate('e=>getComputedStyle(e).fontSize')=='9px');g=p.locator('#mapEngagementB').bounding_box();v=p.evaluate('__PIP_A__.view().rect'if surface=='PIP'else'__VIEWPORT_A__.snapshot().viewport.twoD');ck(tag+'.C3.tagContained',g['x']>=v['x']-1 and g['y']>=v['y']-1 and g['x']+g['width']<=v['x']+v['w']+1 and g['y']+g['height']<=v['y']+v['h']+1)
   p.locator('#uiEmconChipA').click();p.wait_for_timeout(250);emcon=p.evaluate('__MC_TEST__.barBoxes()');snap(p);ck(tag+'.C4.blockedInvariant',boxdiff(before,emcon)<.01);ck(tag+'.C3.blockedReason',p.locator('#mapEngagementB .map-verdict-b').inner_text()==snap(p)['model']['reason']and p.locator('#mapEngagementB .map-status-dot-c').get_attribute('data-tone')=='blocked');p.locator('#uiEmconChipA').click();p.wait_for_timeout(200)
   # Centre jitter is critical when a mini tag is wider than half a small PiP.
   jitter=p.evaluate('''async s=>{const v=s==='PIP'?__PIP_A__.view().rect:__VIEWPORT_A__.snapshot().viewport.twoD;__MC_TEST__.anchorAt(s,v.cx+30);await new Promise(r=>requestAnimationFrame(r));const sides=[];for(let i=0;i<12;i++){__MC_TEST__.anchorAt(s,v.cx+(i%2?1:-1));await new Promise(r=>requestAnimationFrame(r));sides.push(__MAP_C__.snapshot().tag.side);}if(s==='PIP')__PIP_A__.setCenter({x:0,y:0});else __VIEWPORT_A__.setPan(0,0);return sides;}''',surface);ck(tag+'.C2.edgeJitter0',len(set(jitter))==1);records[tag+'.edgeSides']=jitter
   old=snap(p)['selection'];p.locator('#mapCancelB').click();ck(tag+'.C3.closeTargetOnly',snap(p)['selection']==old and snap(p)['target']is None)
   for name,weapon,rng,alt,spd,expect in [('maximum','SM6',296,1000,0,'최대 사거리 구간'),('deadzone','SM2',3,30,680,'사각지대'),('minimum','SM2',1,30,0,'최소 사거리 안쪽'),('outside','SM2',220,30,0,'사거리 밖')]:
    context(p,surface);select(p,weapon);p.evaluate('c=>{__VIEWPORT_A__.setDistance(c);__PIP_A__.setDistance(c)}',max(5,rng*1.5));tid=p.evaluate('o=>__MB_TEST__.add(o)',{'rangeKm':rng,'altM':alt,'speedMps':spd});q,_=tap_object(p,'TRACK:'+str(tid),surface);tone='blocked'if not q['model']['allowed']else'warning';ck(tag+'.C3.'+name,q['model']['verdict']==expect and p.locator('#mapEngagementB .map-status-dot-c').get_attribute('data-tone')==tone and p.locator('#mapFireSlotC .map-status-dot-c').get_attribute('data-tone')==tone);cap(p,tag+'-'+name)
   # Lost record remains at its last observed display position, grey framing, native red status.
   p.evaluate('id=>__MB_TEST__.lost(id)',tid);p.wait_for_function('()=>{__MAP_B__.refresh(true);return document.getElementById("mapEngagementB").dataset.lostC==="true"}');c0=p.evaluate('__MAP_C__.snapshot()');p.wait_for_timeout(200);c1=p.evaluate('__MAP_C__.snapshot()');ck(tag+'.C3.lostFrozen',c0['tag']['world']==c1['tag']['world']and p.locator('#mapEngagementB').get_attribute('data-lost-c')=='true'and p.locator('#mapEngagementB .map-verdict-b').inner_text()=='트랙 소실');cap(p,tag+'-lost')
   # Time controls are the same nodes and retained handlers.
   audit=p.evaluate('__C_NODE_AUDIT__()');ck(tag+'.C5.sameNineNodes',len(audit)==9 and all(r['same']and r['connected']for r in audit));records[tag+'.nodeAudit']=audit
   for n in [1,4,8,16,64]:
    p.locator('.time-btn[data-tw="'+str(n)+'"]').click();value=p.evaluate('__MC_TEST__.state().scale');ck(tag+'.C5.rate'+str(n),value==n);p.locator('#uiPauseA').click()
   s=p.evaluate('__MC_TEST__.state().step');p.wait_for_timeout(200);ck(tag+'.C5.pauseStopsTicks',p.evaluate('__MC_TEST__.state().step')==s)
   if surface=='PIP':
    # Move an actual floating window underneath the clock; the original time controls stay on top.
    p.evaluate('__UI_A__.open("NAV")');a=p.locator('#uiWindowA-NAV .ui-title-a').bounding_box();r=p.locator('#mapTimeBlockC').bounding_box();p.mouse.move(a['x']+15,a['y']+12);p.mouse.down();p.mouse.move(r['x']-70,r['y']+12,steps=5);p.mouse.up();p.wait_for_timeout(200);top=p.evaluate('''()=>{const r=document.getElementById('mapTimeBlockC').getBoundingClientRect(),e=document.elementFromPoint(r.x+15,r.y+15);return!!e?.closest('#mapTimeBlockC')}''');ck(tag+'.C5.clockAboveWindow',top)
    q=p.evaluate('''()=>{const t=document.getElementById('mapTimeBlockC').getBoundingClientRect(),ids=['external3DReadout','external3DNavalShipBtn'];return ids.map(id=>{const r=document.getElementById(id).getBoundingClientRect();return{id,overlap:Math.max(0,Math.min(t.right,r.right)-Math.max(t.left,r.left))*Math.max(0,Math.min(t.bottom,r.bottom)-Math.max(t.top,r.top)),rect:r.toJSON()}})}''');ck(tag+'.C5.no3DOverlap',all(r['overlap']==0 for r in q));records[tag+'.3DBoxes']=q;cap(p,tag+'-clock-layer');p.evaluate('__UI_A__.close("NAV")')
    a=p.locator('#uiWindowA-CIC .ui-title-a').bounding_box();r=p.locator('#mapTimeBlockC').bounding_box();p.mouse.move(a['x']+15,a['y']+12);p.mouse.down();p.mouse.move(r['x']-70,r['y']+12,steps=5);p.mouse.up();p.wait_for_timeout(160);ck(tag+'.C5.clockAboveDraggedPiP',p.evaluate('''()=>{const r=document.getElementById('mapTimeBlockC').getBoundingClientRect();return!!document.elementFromPoint(r.x+15,r.y+15)?.closest('#mapTimeBlockC')}'''));cap(p,tag+'-clock-over-pip');z=p.locator('#uiWindowA-CIC .ui-title-a').bounding_box();p.mouse.move(z['x']+15,z['y']+12);p.mouse.down();p.mouse.move(a['x']+15,a['y']+12,steps=5);p.mouse.up();p.wait_for_timeout(160)
   # Cluster selection: own ship, native launched missile, observed hostile in one visible location.
   context(p,surface);scene=p.evaluate('__MC_TEST__.overlap()');select(p,'SM6');p.wait_for_timeout(200);pos=p.evaluate('a=>a==="PIP"?__PIP_A__.worldToScreen(0,0):__VIEWPORT_A__.worldToScreen(0,0)',surface);hits=p.evaluate('a=>__MAP_A__.hitTest(a.x,a.y,a.surface)',{**pos,'surface':surface});ck(tag+'.C6.clusterExists',len(hits)>=3 and any(q['kind']=='MISSILE'for q in hits));p.mouse.click(pos['x'],pos['y']);p.wait_for_timeout(150);q=snap(p);ck(tag+'.C6.enemyFirstNoMenu',not p.evaluate('__MAP_A__.snapshot().candidatesOpen')and q['target']['key']=='TRACK:'+str(scene['id']));nativeState=p.evaluate('__MB_TEST__.state()');labels=[]
   for i in range(1,len(hits)):
    p.mouse.click(pos['x'],pos['y']);p.wait_for_timeout(120);labels.append(p.locator('#mapCycleHintC').inner_text())
   ck(tag+'.C6.cycleCount',all(str(i+2)+'/'+str(len(hits))in s for i,s in enumerate(labels)));ck(tag+'.C6.ownMissileLast',labels[-1].endswith('M'+str(scene['missileId'])));ck(tag+'.C6.noFireOrControl',p.evaluate('__MB_TEST__.state().missiles')==nativeState['missiles']and p.evaluate('__MAP_A__.snapshot().controlPlatform')is None);records[tag+'.cycle']=labels;cap(p,tag+'-cycle')
   # Existing long-press and right-click path still presents the full list and zoom action.
   p.mouse.click(pos['x'],pos['y'],button='right');p.wait_for_timeout(100);ck(tag+'.C6.rightList',p.evaluate('__MAP_A__.snapshot().candidatesOpen')and p.locator('#mapExpandPipA').count()==1);cap(p,tag+'-right-list');p.keyboard.press('Escape');p.mouse.move(pos['x'],pos['y']);p.mouse.down();p.wait_for_timeout(600);p.mouse.up();ck(tag+'.C6.longList',p.evaluate('__MAP_A__.snapshot().candidatesOpen'));p.keyboard.press('Escape')
   records[tag+'.status']=p.evaluate('__ENV_D__.status()');ck(tag+'.tableMatch',records[tag+'.status']['match']);ck(tag+'.core0',p.evaluate('__CORE_SELFTEST_FAILURES__.length===0'))
  p.close()
 b.close()
ck('pageErrors0',not errors);q={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(E/'ui-c.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v],'errors':errors}));raise SystemExit(0 if q['pass']else 1)
