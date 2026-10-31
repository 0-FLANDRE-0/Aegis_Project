from pathlib import Path
import json,re,gzip,base64,hashlib,difflib
H=Path(__file__).resolve().parent;R=H.parents[2];sha=lambda x:hashlib.sha256(x).hexdigest()
raw=(R/'Aegis_SIM_v48_WIP_MAP_E.html').read_bytes();assert sha(raw)=='f825ccffbdf617f9f1154f131db484ac6682e91fceedcb9e33e2686f5255514b'
html=raw.decode();packed=re.search(r'data-c55-index="13">([^<]+)</script>',html);base=gzip.decompress(base64.b64decode(packed[1])).decode();main=base;changes=[]
symbols=json.loads((H/'base-functions.json').read_text())
def change(a,b):
 global main
 assert main.count(a)==1,(main.count(a),a[:160]);main=main.replace(a,b);changes.append({'anchor':a[:100],'beforeSha256':sha(a.encode()),'afterSha256':sha(b.encode())})
def fn(name,transform):
 global main
 q=symbols[name];a=q['code'];b=transform(a);assert a!=b,name
 ordinal=q['ordinal'];matches=list(re.finditer(re.escape(a),main));assert len(matches)==base.count(a),(name,len(matches));m=matches[ordinal];main=main[:m.start()]+b+main[m.end():];changes.append({'symbol':name,'ordinal':ordinal,'beforeSha256':sha(a.encode()),'afterSha256':sha(b.encode())})
# Constants precede profile evaluation. The original Mod2 and BASE objects stay exact.
change('const BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8=',(H/'spec.js').read_text()+'\nconst BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8=')
a='const SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8=deepFreezeShipProfileV48Wip09({\n  ...BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8,'
b=a+"\n  MK45_MOD4_MK160_SURFACE_V1:gunB1Mod4Module(BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8.MK45_MOD4_MK160_SURFACE_V1),\n  MK45_MOD4_CG52_MK160_V1:gunB1Mod4Module(BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8.MK45_MOD4_MK160_SURFACE_V1,'MK45_MOD4_CG52_MK160_V1'),"
change(a,b)
change("moduleId:'MK45_MOD2_MK160_SURFACE_V1',hardpointId,neutralAzRad:g.neutralAzRad,geometryMask:true,\n    moduleName:hp[hardpointId].name,trunnionOffsetM:g.trunnionOffsetM,exposedBarrelM:g.barrelM,sourceNode:g.yawNode", "moduleId:'MK45_MOD4_CG52_MK160_V1',hardpointId,neutralAzRad:g.neutralAzRad,geometryMask:true,\n    moduleName:hp[hardpointId].name,trunnionOffsetM:{x:.91,y:0,z:2.87},exposedBarrelM:6.206,sourceNode:g.yawNode")
# CG base datum is the old yaw platform; Mod4's .91m offset is referenced to
# an elevated DDG hardpoint. 2.87m = authored DDG Mod4 trunnionZM-baseDeckZM.
for a,b in [('함수 Mk 45 Mod 2','함수 Mk 45 Mod 4'),('함미 Mk 45 Mod 2','함미 Mk 45 Mod 4')]:change(a,b)
fragment=symbols['_wip88FragmentationPk']['code'].replace('function _wip88FragmentationPk(','function gunB1FragmentationPk(',1).replace('const w=INTERCEPT_FRAGMENT_WARHEADS[weaponType],','const w=GUN_B1_SPEC.fragments,',1)
change('const SHIP_GUN_BUILDER_REGISTRY_V48_WIP13B8=', '\n'.join((H/n).read_text()for n in ['air.js','auto.js','fuze.js'])+'\n// Private copy: original SAM function and registry remain byte exact.\n'+fragment+'\nconst SHIP_GUN_BUILDER_REGISTRY_V48_WIP13B8=')
def gun(s):
 s=s.replace("  function stopContinuousFire(reason=", "  function solveAirTrack(trackId,ammoId='MFF_127_SIM',options={}){return gunB1SolveAirTrack(spec,hp,state,profile,trackId,ammoId,options);}\n  function solveCommandTrack(id,ammo,options={}){return gunB1IsAir(tracks.get(Number(id)))?solveAirTrack(id,ammo,options):solveTrack(id,ammo,options);}\n  function stopContinuousFire(reason=",1)
 s=s.replace('solution=solveTrack(state.commandTrackId,','solution=solveCommandTrack(state.commandTrackId,').replace('const solution=solveTrack(id,round,options);','const solution=solveCommandTrack(id,round,options);')
 s=s.replace('wip13b1SurfaceGunReleaseGate(', 'gunB1ReleaseGate(')
 s=s.replace("policy=tr?wip13b1SurfaceReleasePolicy(identity,'MANUAL',spec):", "policy=tr?(gunB1IsAir(tr)?gunB1AirPolicy(tr):wip13b1SurfaceReleasePolicy(identity,'MANUAL',spec)):")
 s=s.replace('qualityTrack&&state.solution?.ok?wip13b10SurfaceFireControlQuality(qualityTrack,state.solution,spec):', 'qualityTrack&&state.solution?.ok?(state.solution.airDomain?gunB1AirQuality(qualityTrack,state.solution):wip13b10SurfaceFireControlQuality(qualityTrack,state.solution,spec)):')
 s=s.replace('solution:state.solution?{ok:', 'solution:state.solution?{...(state.solution.airDomain?{airDomain:true,targetAltitudeM:state.solution.targetAltitudeM,azimuthRad:state.solution.azimuthRad,elevationRad:state.solution.elevationRad,verticalSlopeMPerRad:state.solution.verticalSlopeMPerRad}:{}),ok:')
 s=s.replace('return {spec,installation:{...installation},solveTrack,', 'return {spec,installation:{...installation},solveTrack,solveAirTrack,')
 return s
fn('createProfileGunModuleWip13B3',gun)
fn('updateMainGunWip13B3',lambda s:s.replace('const q=', 'gunB1AutoTick();const q=',1))
fn('spawnMainGunProjectileWip13B3',lambda s:s.replace('  mainGunProjectilesWip13B3.push(projectile);',"  if(projectile.ammoId==='MFF_127_SIM')gunB1ArmShell(projectile);\n  mainGunProjectilesWip13B3.push(projectile);"))
def projectiles(s):
 s=s.replace('    p.previousPositionM=prev;p.ageS+=dt;p.flightDistanceM+=distanceM;', "    const mffEvent=p.mffB1?gunB1ShellEvent(p,prev,next,dt):null;\n    if(mffEvent&&[targetT,terrainT,seaT,fuzeT].every(t=>t==null||mffEvent.t<t)){p.previousPositionM=prev;p.positionM={x:lerp(prev.x,next.x,mffEvent.t),y:lerp(prev.y,next.y,mffEvent.t),z:lerp(prev.z,next.z,mffEvent.t)};p.ageS+=dt*mffEvent.t;p.flightDistanceM+=distanceM*mffEvent.t;gunB1Detonate(p,mffEvent,dt);continue;}\n    p.previousPositionM=prev;p.ageS+=dt;p.flightDistanceM+=distanceM;")
 return s
fn('updateMainGunProjectilesWip13B3',projectiles)
fn('prepareOperationalStateV48Wip11B',lambda s:s.replace('const harpoonMigrations=[];', 'const harpoonMigrations=[];gunB1MigrateSave(src,harpoonMigrations);',1))
fn('applyPreparedOperationalStateV48Wip11B',lambda s:s.replace('  const preparedDeployment=', '  gunB1ResetAuto();const preparedDeployment=',1))
# Return module gate dispatch only changes the gun's air path.
# Shared Mod4 generator with caller-supplied geometry datum, no renderer feedback.
change('buildMk45(parent,mats){\n      const T=this.THREE,M=WIP199_FINAL_LAYOUT.mk45,', 'buildMk45(parent,mats,layout=WIP199_FINAL_LAYOUT.mk45){\n      const T=this.THREE,M=layout,')
a="    this.mk45TraverseGroup=parts.get('mk45f_yaw');this.mk45ElevationGroup=parts.get('mk45f_pitch');"
b="""    // GUN_B1: reuse the existing DDG Mod4 generator, hide authored round turrets.
    this._gunB1Visuals=new Map();
    const paint=color=>new T.MeshStandardMaterial({color,roughness:.86,metalness:.02}),gm={weapon:paint(0x969fa3),weaponLight:paint(0xa3adae),structure3:paint(0x869095),dark:paint(0x424b50),darkVent:paint(0x20282c)};
    for(const inst of profile.weapons.gunMounts){const hp=profile.geometry.hardpoints[inst.hardpointId],spec=SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8[inst.moduleId],off=inst.trunnionOffsetM;
      const old=parts.get(R.guns[inst.hardpointId].yawNode);if(old)old.visible=false;
      const holder=new T.Group();holder.name='GUN_B1_'+inst.id;root.add(holder);
      this.buildMk45(holder,gm,{...WIP199_FINAL_LAYOUT.mk45,xM:hp.x,yM:hp.y,baseDeckZM:hp.z,trunnionXM:hp.x+off.x,trunnionZM:hp.z+off.z,exposedBarrelM:inst.exposedBarrelM});
      const yaw=this.mk45TraverseGroup,pitch=this.mk45ElevationGroup;yaw.rotation.y=-inst.neutralAzRad;
      this._gunB1Visuals.set(inst.hardpointId,{holder,yaw,pitch});parts.set(R.guns[inst.hardpointId].yawNode,yaw);
    }
    this.mk45TraverseGroup=this._gunB1Visuals.get('mk45').yaw;this.mk45ElevationGroup=this._gunB1Visuals.get('mk45').pitch;"""
change(a,b)
a="    for(const q of st.mountInventory?.guns??[]){const g=BUNKER_REGISTRATION.guns[q.hardpointId];\n      rotate(g.yawNode,-(q.bodyAzRad-g.neutralAzRad));rotate(g.pitchNode,q.elevationRad-g.restElevationRad);}"
b="    for(const q of st.mountInventory?.guns??[]){const g=this._gunB1Visuals?.get(q.hardpointId);if(g){g.yaw.rotation.y=-q.bodyAzRad;g.pitch.rotation.z=q.elevationRad;}}"
change(a,b)
# MAP_D UI: extend original command adapter; keep public APIs and 2-mount rule.
change("ammoNames={HE_127_SIM:'HE',SAP_127_SIM:'SAP'}", "ammoNames={HE_127_SIM:'HE',SAP_127_SIM:'SAP',MFF_127_SIM:'MFF'}")
change('function cue(o){\n  clearOwned', 'function cue(o,ammoId=null){\n  clearOwned')
change('if(!isSurface(tr))return;\n  for(const{id:key,g}of guns()){const a=g.snapshot().loadedAmmoId,', 'if(!isSurface(tr)&&!gunB1IsAir(tr))return;\n  for(const{id:key,g}of guns()){const a=ammoId??g.snapshot().loadedAmmoId,')
change("if(s?.weapon==='MK45')cue(o);", "if(s?.weapon==='MK45')cue(o,s.ammoId);")
change("if(!isSurface(tr))return bad('NOT_SURFACE_TRACK');", "if(!isSurface(tr)&&!gunB1IsAir(tr))return bad('NOT_SURFACE_TRACK');")
# Pure preview if autonomous mount temporarily owns a different track. No commands from render.
change('const q=g.snapshot(),sol=q.solution,desired=sol?.ok?', "const live=g.snapshot(),ammoId=selection()?.ammoId??live.loadedAmmoId,preview=live.commandTrackId!==id?(gunB1IsAir(tr)?g.solveAirTrack(id,ammoId):g.solveTrack(id,ammoId)):null,q=preview?{...live,commandTrackId:preview.ok?id:null,loadedAmmoId:ammoId,solution:preview}:live,sol=q.solution,desired=sol?.ok?")
change("return {ok:allowed,allowed,tone,reason,verdict:allowed?(tone==='effective'?'사통 준비':'사통 저하'):'사격 제한',rows,mountLabel:", "return {air:gunB1IsAir(tr),nonMff:gunB1IsAir(tr)&&rows.some(r=>r.eligible&&r.q.loadedAmmoId!=='MFF_127_SIM'),ok:allowed,allowed,tone,reason,verdict:allowed?(tone==='effective'?'사통 준비':'사통 저하'):'사격 제한',rows,mountLabel:")
change("createdStep:simStepCounter});note('GUN_QUEUE'", "createdStep:simStepCounter,ammoId:s.ammoId});note('GUN_QUEUE'")
change("for(const{id,g}of guns()){const q=g.snapshot();let result;if(op.action==='STOP')", "for(const{id,g}of guns()){let q=g.snapshot();if(op.action==='FIRE'){gunB1ManualIntent(g);q=g.snapshot();const ammoId=op.ammoId??q.loadedAmmoId;if(q.loadedAmmoId!==ammoId){const f=g.selectAmmo(ammoId);if(!f.ok){note('GUN_WITHHELD',f.reason,{mount:id});continue;}}if(q.commandTrackId!==op.trackId||q.loadedAmmoId!==ammoId)g.command(op.trackId,ammoId);q=g.snapshot();}let result;if(op.action==='STOP')")
# Show autonomous stop/feed/manual-priority reason through the existing menu.
change("e.append(r);dom.menuReason=r;", "e.append(r);dom.menuReason=r;r.textContent=gunB1AutoReasonText();")
change("e.title='Mk45'+(s?.weapon==='MK45'?' · '+(s.fireMode==='CONTINUOUS'?'연속':'단발'):' · 탄종/사격 방식');", "e.title='Mk45'+(s?.weapon==='MK45'?' · '+(s.fireMode==='CONTINUOUS'?'연속':'단발'):' · 탄종/사격 방식')+' · 자동 대공 '+(gunB1AutoState().enabled?'ON':'OFF')+' '+gunB1AutoReasonText();if(dom.menuReason&&menuWeapon==='MK45'&&dom.chooser&&!dom.chooser.hidden&&gunB1AutoReasonText())dom.menuReason.textContent=gunB1AutoReasonText();")
# New menu action does not commit/deselect the pending weapon choice.
change("for(const[mode,label]of [['SINGLE','단발'],['CONTINUOUS','연속']])", "add('자동 대공 '+(gunB1AutoState().enabled?'ON':'OFF'),{gunAutoB1:'toggle'},()=>{const on=gunB1SetAuto(!gunB1AutoState().enabled);e.querySelector('[data-gun-auto-b1]').textContent='자동 대공 '+(on?'ON':'OFF');highlight(selection());});\n   for(const[mode,label]of [['SINGLE','단발'],['CONTINUOUS','연속']])")
change("e.querySelector('span').textContent='5in';e.title=", "e.querySelector('span').textContent='5in';e.dataset.autoAirB1=gunB1AutoState().enabled?'on':'off';e.title=")
change("ui.verdict.textContent=textReason(m.reason)||m.verdict;ui.verdict.dataset.tone=tone;ui.verdict.hidden=tone==='effective';", "if(s.weapon==='MK45'&&m.air)ui.summary.textContent+=' · '+(Number.isFinite(m.d.tr?.z)?Math.round(m.d.tr.z)+'m':'고도 미상');ui.verdict.textContent=textReason(m.reason)||(m.nonMff?'대공탄 아님':m.verdict);ui.verdict.dataset.tone=m.nonMff&&m.allowed?'warning':tone;ui.verdict.hidden=tone==='effective'&&!m.nonMff;")
a="  if(s.weapon==='HARPOON'&&harpoonRuntimeA().routeDraft.pointsM.length){"
b="""  if(s.weapon==='MK45'){const radius=kmToWorld(GUN_B1_SPEC.autoRangeM/1000);context.setLineDash([2/z,5/z]);context.beginPath();context.arc(ownship.x,ownship.y,radius,0,Math.PI*2);context.stroke();const c=worldToScreen(ownship.x,ownship.y,view),r=view.rect,label='대공 자동 9km (SIM)';{const fits=radius*z<Math.min(c.x-r.x,r.x+r.w-c.x,c.y-r.y,r.y+r.h-c.y),p=screenToWorld(r.x+r.w-8,window.__MAP_C__.labelBase(view)+24,view);context.textAlign='right';context.fillText((fits?'':'→ ')+label,p.x,p.y);context.textAlign='left';}}
"""+a
change(a,b)
change("const native=simulateFixedTick;simulateFixedTick=function(dt){step();", "const b1css=document.createElement('style');b1css.textContent='[data-weapon-b=MK45]{position:relative}[data-auto-air-b1=on]::after{content:\"A\";position:absolute;right:1px;top:0;font:7px/1 monospace;color:#72e2bb;pointer-events:none}';document.head.append(b1css);\n  const native=simulateFixedTick;simulateFixedTick=function(dt){step();")
# Additional reasons are presentation only.
change("const textReason=code=>reasonNames[code]??String(code??'');", "const textReason=code=>({AIR_TRACK_NOT_CONFIRMED:'공중 트랙 미확정',AIR_TRACK_COAST_EXPIRED:'공중 관측 노후',AIR_TRACK_3D_STATE_REQUIRED:'3D 관측 정보 부족',AIR_PREDICTION_TOO_LONG:'공중 예측 시간 초과',NOT_AIR_TRACK:'공중 트랙 필요',BELOW_MIN_RANGE:'최소 사거리 안쪽',ABOVE_MAX_RANGE:'최대 사거리 밖'}[code]??reasonNames[code]??String(code??''));")
# Small public port: no hidden targets in snapshot.
change('// MAP_E_UI_BEGIN',"window.__GUN_B1__=Object.freeze({spec:GUN_B1_SPEC,setAuto:gunB1SetAuto,snapshot:gunB1AutoSnapshot});\n// MAP_E_UI_BEGIN")
# Existing detached legacy labels still name the loaded round correctly.
def labels(s):
 s=s.replace("q.loadedAmmoId==='SAP_127_SIM'?", "q.loadedAmmoId==='MFF_127_SIM'?`127 HE-MFP · ${q.magazine.MFF_127_SIM}`:q.loadedAmmoId==='SAP_127_SIM'?")
 anchor="    const fcq=q.solution?.fireControlTrackQuality,"
 air="""    if(q.solution?.airDomain){const fcq=q.solution.fireControlTrackQuality;if(cue){cue.textContent='MK45 AIR '+q.status;cue.title='관측 공중 트랙 사격해';}if(fire){fire.textContent=q.pendingSingleFire.active?'MK45 HOLD':'MK45 AIR FIRE';fire.disabled=!q.solution.ok||!fcq?.firePermitted||q.cycleRemainingS>0;fire.title=fcq?.status??q.solution.reason??'';}if(continuous){continuous.textContent=q.continuousFire.active?'CONT STOP':'MK45 AIR CONT';continuous.disabled=!q.continuousFire.active&&!fcq?.firePermitted;}wip13cUpdateMissileControlLabels();return;}
"""
 return s.replace(anchor,air+anchor)
fn('wip13b5UpdateGunButtonLabels',labels)
from handoff_patch import apply as apply_handoff
main,handoff_changes=apply_handoff(main);changes.extend(handoff_changes)
# Authoritative envelope and historical diagnostics must not change.
assert re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',main)[0]==re.search(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END',base)[0]
gz=gzip.compress(main.encode(),9,mtime=0);html=html[:packed.start(1)]+base64.b64encode(gz).decode()+html[packed.end(1):];m=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(main.encode()),gzipBytes=len(gz),sha256=sha(main.encode()));html=html[:m.start(1)]+json.dumps(rs,separators=(',',':'))+html[m.end(1):]
out=R/'Aegis_SIM_v48_WIP_GUN_B1.html';temporary=out.with_suffix('.html.building');temporary.write_text(html);temporary.replace(out);(Path('/tmp/aegis-gun-b1')).mkdir(parents=True,exist_ok=True);Path('/tmp/aegis-gun-b1/current.js').write_text(main)
record={'baseCommit':'5542aa005479713a5a8959143157fdf4ba07447e','baseHtmlSha256':sha(raw),'output':out.name,'sha256':sha(out.read_bytes()),'mainSha256':sha(main.encode()),'bytes':out.stat().st_size,'envelopeBlockByteExact':True,'changes':changes};(H/'build.json').write_text(json.dumps(record,indent=2)+'\n')
clean=lambda s:re.sub(r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END','// ENV_D byte identical',s)
(H/'GUN_B1.diff').write_text(''.join(difflib.unified_diff(clean(base).splitlines(True),clean(main).splitlines(True),fromfile='MAP_E/main.js',tofile='GUN_B1/main.js')));print(json.dumps({k:v for k,v in record.items()if k!='changes'}))
