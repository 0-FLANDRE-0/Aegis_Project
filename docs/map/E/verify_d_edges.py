"""Additional native-mount exclusion, UI geometry and route preservation tests."""
from pathlib import Path
import json,sys,time,hashlib,base64
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();E=H/'evidence/d-edges';E.mkdir(parents=True,exist_ok=True);checks={};records={};errors=[];start=time.perf_counter()
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def resetD(p,surface):
 p.evaluate('__MD_TEST__.reset()')
 if surface=='PIP':p.evaluate('__UI_A__.open("CIC");__PIP_A__.setDistance(40)')
 else:p.evaluate('__WIP148_3D_VIEW__.close()')
 p.wait_for_timeout(550)
def gun(p,mode='SINGLE'):
 p.locator('[data-weapon-b="MK45"]').click();p.locator('[data-gun-mode-d="'+mode+'"]').click()
def cap(p,n):
 c=p.context.new_cdp_session(p)
 try:(E/(n+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
 finally:c.detach()
fixture=(H/'test-helper.js').read_text()+'\n'+(H/'extension-fixture.js').read_text()
with sync_playwright()as pw:
 b=launch(pw,True)
 for w,h in [(1400,900),(832,384)]:
  for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
   p=load_fleet(b,instrument(raw,fixture),own=own,width=w,height=h,errors=errors);p.set_default_timeout(60000)
   for s in ['MAIN','PIP']:
    tag=f'{w}.{own[:2]}.{s}'
    if s=='PIP':p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=180000)
    resetD(p,s);p.locator('[data-weapon-b="MK45"]').click();p.wait_for_timeout(150);cap(p,tag+'-ammo-menu');g=p.locator('#mapSalvoB').bounding_box();ck(tag+'.gunMenuInside',g['x']>=0 and g['y']>=0 and g['x']+g['width']<=w+1 and g['y']+g['height']<=h+1);ck(tag+'.menuButtons28',p.locator('#mapSalvoB button').evaluate_all('bs=>bs.every(b=>b.getBoundingClientRect().height>=28)'));p.locator('[data-gun-mode-d="SINGLE"]').click();tid=p.evaluate('__MD_TEST__.surface({rangeKm:8,bearingDeg:30})');q=target(p,tid,s);ck(tag+'.targetChosen',q['target']is not None and q['target']['key']=='TRACK:'+str(tid));assert q['target']and q['target']['key']=='TRACK:'+str(tid)
    ck(tag+'.gunRingsNative',p.evaluate('__MD_TEST__.limits().gun.minM===800 && __MD_TEST__.limits().gun.maxM==='+('22000'if own.startswith('CG')else'24000')))
    # The deselection input revokes map-owned native continuous consent immediately.
    p.locator('[data-weapon-b="MK45"]').click();gun(p,'CONTINUOUS');target(p,tid,s);p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tickUntilGunShot(400)');snap(p);ck(tag+'.continuousActive',all(g['continuousFire']['active']for g in p.evaluate('__MAP_D__.snapshot().guns')));p.locator('[data-weapon-b="MK45"]').click();ck(tag+'.deselectStops',all(not g['continuousFire']['active']and g['commandTrackId']is None for g in p.evaluate('__MAP_D__.snapshot().guns')))
    if own.startswith('CG'):
     # These are real native obstruction/attitude gates; no mocked clearance result.
     for label,az,heel in [('함수만',0,0),('함미만',180,0),('2문',30,0),('사계 없음',270,25)]:
      resetD(p,s);gun(p);p.evaluate('d=>__MD_TEST__.heel(d)',heel);tid=p.evaluate('a=>__MD_TEST__.surface({rangeKm:8,bearingDeg:a})',az);q=target(p,tid,s);eligible=p.evaluate('id=>{const b=__MAP_B__.snapshot(),o=__MAP_A__.objects().find(o=>o.key==="TRACK:"+id);return __MAP_D__.calculate(b.selection,b.target,o).rows.filter(r=>r.eligible).map(r=>r.id)}',tid);ck(tag+'.'+label+'.nativeLabel',q['model']['mountLabel']==label)
      before=p.evaluate('__MD_TEST__.state().selectedGunId')
      if eligible:p.locator('#mapFireB').click();p.evaluate('__MD_TEST__.tickUntilGunShot(400)')
      else:ck(tag+'.noneDisabled',p.locator('#mapFireB').is_disabled())
      guns=p.evaluate('__MAP_D__.snapshot().guns');ck(tag+'.'+label+'.eligibleFired',all(g['shotsFired']==1 for g in guns if g['id']in eligible));ck(tag+'.'+label+'.excludedNoShots',all(g['shotsFired']==0 for g in guns if g['id']not in eligible));ck(tag+'.'+label+'.noSelectionChange',p.evaluate('__MD_TEST__.state().selectedGunId')==before);records[tag+'.'+label]={'initial':q,'guns':guns};cap(p,tag+'-'+label)
     resetD(p,s);p.locator('[data-weapon-b="HARPOON"]').click();cap(p,tag+'-salvo-menu');p.locator('[data-salvo-b="2"]').click();p.locator('#mapRouteChipButtonD').click();p.locator('#mapRouteBannerD').wait_for(state='visible');p.evaluate('__MD_TEST__.searchPoint(12000,0);__MD_TEST__.searchPoint(24000,0)');snap(p)
     ck(tag+'.hpRingNative',p.evaluate('__MD_TEST__.limits().harpoon.minKm===4 && __MD_TEST__.limits().harpoon.maxKm===140'))
     # Native route gate still protects an explicitly selected friendly/neutral contact.
     tid=p.evaluate('__MD_TEST__.surface({rangeKm:10,bearingDeg:90})');p.evaluate("id=>__MD_TEST__.observed(id,{_operatorIdentity:'NEUTRAL',identity:'NEUTRAL'})",tid);q=target(p,tid,s);ck(tag+'.protectedRouteBlocked',not q['model']['allowed']and q['model']['reason']=='PROTECTED_IDENTITY')
     ck(tag+'.controlRouteBlocked',p.evaluate('__MAP_A__.snapshot().currentTool')=='HARPOON_INS')
     geom=p.evaluate('''()=>{let z=__UI_A_SETTINGS__.scale;return Object.fromEntries(['mapRouteBannerD','mapRouteD','mapEngagementB'].map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect();return[id,{x:r.x,y:r.y,w:r.width,h:r.height,inside:r.x>=-1&&r.y>=-1&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1,hitH:r.height}]}))}''');ck(tag+'.routeBounds',all(v['inside']for v in geom.values()));ck(tag+'.routeButton28',geom['mapRouteD']['hitH']>=28);records[tag+'.routeGeometry']=geom;cap(p,tag+'-protected-route')
     # Cross-weapon pending menu confirmation retains the old choice.
     p.locator('[data-weapon-b="MK45"]').click();ck(tag+'.pendingKeepsWeapon',snap(p)['selection']['weapon']=='HARPOON');p.locator('[data-gun-mode-d="SINGLE"]').click();ck(tag+'.confirmationChangesWeapon',snap(p)['selection']['weapon']=='MK45')
   p.close()
 b.close()
ck('pageErrors0',not errors);out={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'elapsedS':time.perf_counter()-start};(E/'edges.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v]}));assert out['pass']
