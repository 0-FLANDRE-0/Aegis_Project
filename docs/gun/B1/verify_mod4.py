"""Actual spawn origin versus generated mesh, with presentation-only closeup camera."""
from pathlib import Path
import sys,json,time,hashlib,base64
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'));from browser_tools import launch,load_fleet,instrument
raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();fixture='\n'.join(p.read_text()for p in [R/'docs/map/E/test-helper.js',R/'docs/map/D/extension-fixture.js',H/'test-fixture.js'])+'''
__GB_TEST__.actualMuzzles=()=>{const v=WIP148_EXTERNAL_3D,T=v.THREE;v.syncShipFittings(get3DRenderState());v.shipRoot.updateWorldMatrix(true,true);const frame=shipGameFrameV1(),rows=[];for(const[id,g]of gunB1OwnGuns()){const q=g.snapshot(),p=spawnMainGunProjectileWip13B3({module:g.spec,ammo:g.spec.ammunition.HE_127_SIM,ammoId:'HE_127_SIM',trackId:q.commandTrackId??-1,bodyAzRad:q.bodyAzRad,elevationRad:q.elevationRad,hardpoint:ACTIVE_SHIP_PROFILE.geometry.hardpoints[g.installation.hardpointId],solution:{timeOfFlightS:1}}),at=frame.pointToBody(p.positionM),visual=v._gunB1Visuals.get(g.installation.hardpointId),bore=visual.pitch.getObjectByName('MK45_MOD4_BORE'),m=v.shipRoot.worldToLocal(bore.getWorldPosition(new T.Vector3()));rows.push({id,angles:{az:q.bodyAzRad,el:q.elevationRad},spawnWorldM:{...p.positionM},spawnBodyM:at,meshBodyM:{x:m.x,y:m.z,z:m.y},errorM:Math.hypot(m.x-at.x,m.z-at.y,m.y-at.z)});p.alive=false;}resetMainGunProjectilesWip13B3();return rows;};
__GB_TEST__.gunFocus=key=>{const v=WIP148_EXTERNAL_3D;if(!v._b1DiagnosticCamera){const f=v.syncCamera;v.syncCamera=function(...args){const r=f.apply(this,args);if(this._b1DiagnosticFocus){const c=this._gunB1Visuals.get(this._b1DiagnosticFocus).holder.getObjectByName('MK45_MOD4_5IN_62').getWorldPosition(new this.THREE.Vector3());c.y+=3;this.camera.position.copy(c).add(new this.THREE.Vector3(11,8,12));this.camera.lookAt(c);}return r;};v._b1DiagnosticCamera=true;}v._b1DiagnosticFocus=key;};
'''
E=H/'evidence/mod4';E.mkdir(parents=True,exist_ok=True);errors=[];records={};checks={}
with sync_playwright()as pw:
 b=launch(pw,True)
 for w,h in [(1400,900),(832,384)]:
  p=load_fleet(b,instrument(raw,fixture),own='CG_52_LATE_TICONDEROGA',width=w,height=h,errors=errors);p.set_default_timeout(180000);p.evaluate('__GB_TEST__.reset();Object.keys(__UI_A__.snapshot().windows).forEach(k=>__UI_A__.close(k))');p.evaluate('async()=>{__WIP148_3D_VIEW__.c12ApplyPreset("LOW");await __WIP148_3D_VIEW__.open()}');p.wait_for_function('__WIP148_3D_VIEW__.ready',timeout=240000,polling=50)
  for bearing,alt in [(0,30),(90,500),(210,1000)]:
   id=p.evaluate('o=>__GB_TEST__.air(o)',{'bearingDeg':bearing,'altM':alt});p.evaluate('id=>__GB_TEST__.cue(id)',id);p.evaluate('__GB_TEST__.observeTick(300)');q=p.evaluate('__GB_TEST__.actualMuzzles()');key=f'{w}.{bearing}.{alt}';records[key]=q;checks[key]=all(r['errorM']<=.1 for r in q);print(key,q,flush=True)
  for key in ['mk45','mk45Aft']:
   p.evaluate('k=>__GB_TEST__.gunFocus(k)',key);p.wait_for_timeout(300);c=p.context.new_cdp_session(p)
   try:(E/(str(w)+'-'+key+'.png')).write_bytes(base64.b64decode(c.send('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})['data']))
   finally:c.detach()
  p.close()
 b.close()
out={'checks':checks,'records':records,'errors':errors,'pass':all(checks.values())and not errors,'htmlSha256':hashlib.sha256(raw).hexdigest(),'note':'Actual spawnMainGunProjectileWip13B3 compared in the common native body frame; bore decoration extends 6mm past physical muzzle. Closeup camera is test-only presentation, no simulation changes.'};(E/'results.json').write_text(json.dumps(out,indent=2)+'\n');raise SystemExit(not out['pass'])
