"""Pinned HELI_F2 -> SOV_A. Existing combat/aircraft kernels retained."""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,re
HERE=Path(__file__).resolve().parent
BASE_SHA='100b12c24355666627c76f7e79c88b98a1a7a963e9bb777ea8f9f7e9c908bb94'
def decoded(s):return gzip.decompress(base64.b64decode(re.search(r'data-c55-index="13">(.*?)</script>',s,re.S)[1])).decode()
def patch(s):
 def edit(a,b,n=1):
  nonlocal s
  assert s.count(a)==n,(a[:110],s.count(a),n);s=s.replace(a,b)
 def first(fn,body):
  nonlocal s
  p=re.search(r'function '+fn+r'\([^\n]*?\)\{',s);assert p,fn;s=s[:p.end()]+body+s[p.end():]
 # Static assets decoded once. Geometry buffers are consumed only by rendering.
 prefix="\nconst SOV_REG_A=deepFreezeShipProfileV48Wip09(await readBunkerAsset('sov-registration-a'));\nconst SOV_META_A=deepFreezeShipProfileV48Wip09(await readBunkerAsset('sov-meta-a'));\nconst SOV_TEXTURES_A=deepFreezeShipProfileV48Wip09(await readBunkerAsset('sov-textures-a'));\nconst SOV_BUFFER_A=await readBunkerAsset('sov-geometry-a',false);\n"
 start=s.index('(function(G){\'use strict\';\nconst source=G.BunkerEnvelopeSource');end=s.index('})(globalThis);',s.index('(function(G){\'use strict\';\nconst source=G.BunkerEnvelopeSource'))+len('})(globalThis);')
 layout=s[start:end].replace('const source=G.BunkerEnvelopeSource,stats=G.BunkerEnvelopeStats;',"const source={basis:'MODEL_REGISTRATION_OFFLINE_V9_1',groups:SOV_REG_A.groups},stats={bounds:{bow:78.25,stern:-78.25},waterline:SOV_REG_A.waterline,stations:SOV_REG_A.stations};").replace('G.BunkerLayout=','G.SovLayoutA=').replace("schema:'BURKE_C52_STATIC_SECTION_LAYOUT'","schema:'SOV_STATIC_SECTION_LAYOUT_A'")
 engine=(HERE/'shared-interior-baseline.js').read_text()
 assert engine in s
 engine=engine.replace('createBunkerInterior','createSovInteriorA').replace('bunkerInteriorAuthored','sovInteriorAuthoredA').replace('CG52','SOV').replace('independentCG52Layout','independentSovLayout').replace('5.2','3.2')
 layout=layout.replace("function sections(x,kind='all'){\n return groups.filter(g=>kind==='all'||g.name.startsWith(kind))", "const sovGroupsByXA=new Map();for(const g of groups)for(let k=Math.floor(g.xmin-1e-5);k<=Math.floor(g.xmax+1e-5);k++){if(!sovGroupsByXA.has(k))sovGroupsByXA.set(k,[]);sovGroupsByXA.get(k).push(g); }\nfunction sections(x,kind='all'){\n return (sovGroupsByXA.get(Math.floor(x))??[]).filter(g=>kind==='all'||g.name.startsWith(kind))")
 modules=prefix+layout+'\n'+engine+'\n'+(HERE/'profile.js').read_text()+'\n'+(HERE/'interior.js').read_text()+'\n'+(HERE/'render.js').read_text()+'\n'+(HERE/'diagnostic.js').read_text()
 edit('const SHIP_PROFILE_REGISTRY=Object.freeze({',modules+'\nconst globalBoundarySurfaceSovA=wip12aBoundarySurface;\nconst SOVREMENNY_956_PROFILE=makeSovProfileA();\nconst SHIP_PROFILE_REGISTRY=Object.freeze({[SOVREMENNY_956_PROFILE.id]:SOVREMENNY_956_PROFILE,')
 edit('Object.values(SHIP_PROFILE_REGISTRY).map(p=>Object.freeze({','Object.values(SHIP_PROFILE_REGISTRY).filter(p=>!p.capabilities?.npcOnly).map(p=>Object.freeze({')
 edit("const p=SHIP_PROFILE_REGISTRY[profileId];\n  if(!Object.isFrozen(p)","const p=SHIP_PROFILE_REGISTRY[profileId];if(p.capabilities?.npcOnly)return false;\n  if(!Object.isFrozen(p)")
 edit('function createWeaponContextD(owner){','function createWeaponContextD(owner){const wip12aBoundarySurface=sovHullA(owner)?sovBoundarySurfaceA:globalBoundarySurfaceSovA,wip12eSurfaceProfile=sovHullA(owner)?sovBoundarySurfaceA:sovLegacySurfaceProfileA;')
 first('createPlayerShipSession',"if(sovHullA(profile))throw Error('NPC_ONLY_PROFILE');")
 first('createShipRuntime',"if(sovHullA(profile)&&!['ENEMY','NEUTRAL','UNASSIGNED'].includes(options.role??'UNASSIGNED'))throw Error('NPC_ONLY_PROFILE');")
 edit("entry=wip12aBoundarySurface(point.z<0?","entry=(sovHullA(r)?sovBoundarySurfaceA:wip12aBoundarySurface)(point.z<0?")
 first('geometryForShipProfileA',"if(sovHullA(profile))return sovGeometryA(profile);")
 first('createProfileVlsInventory',"if(sovHullA(profile))return {fwd:[],aft:[]};")
 first('createProfileCloseInRuntimeA',"if(sovHullA(profile))return [];")
 edit('createShipMassLossV16(geo,geo.boxes,{lightshipKg:profile.mass.lightshipKg})',"createShipMassLossV16(geo,geo.boxes,{lightshipKg:profile.mass.lightshipKg,...(sovHullA(profile)?{mastParcel:{x:2.522,y:0,z:25.47,massKg:9000},arealDensity:id=>(id.includes('SHELL')?12:4)*7.85}:{})})")
 first('profileWeaponMassNodesA',"if(sovHullA(runtime))return [];")
 edit("['ALLY','ENEMY','UNASSIGNED'].includes(options.role??'UNASSIGNED')","['ALLY','ENEMY','NEUTRAL','UNASSIGNED'].includes(options.role??'UNASSIGNED')")
 edit("role==='ENEMY'?'HOSTILE':'UNASSIGNED'","role==='ENEMY'?'HOSTILE':role==='NEUTRAL'?'NEUTRAL':'UNASSIGNED'")
 edit("r.interior=profile.id==='CG_52_LATE_TICONDEROGA'?", "r.interior=sovHullA(profile)?createSovInteriorA(r.flooding,geo.layout):profile.id==='CG_52_LATE_TICONDEROGA'?")
 edit('r.weapons.selectedGunId=profile.weapons.mainGun.id;r.weapons.mainGun=r.weapons.gunMounts.get(r.weapons.selectedGunId);','r.weapons.selectedGunId=sovHullA(profile)?null:profile.weapons.mainGun.id;r.weapons.mainGun=sovHullA(profile)?sovDisabledGunA():r.weapons.gunMounts.get(r.weapons.selectedGunId);')
 edit('createShipCrewV48Wip07(r.interior,crewDutyPostsV48Wip07(profile),','createShipCrewV48Wip07(r.interior,sovHullA(profile)?sovCrewPostsA(r.interior):crewDutyPostsV48Wip07(profile),')
 first('crewDutyPostsV48Wip07',"if(sovHullA(profile))return sovCrewPostsA();")
 edit("if(l.schema!=='AEGIS_NULKA_LAYOUT_WIP15B'||l.launchers.length!==4)","if(l.schema!=='AEGIS_NULKA_LAYOUT_WIP15B'||(!sovHullA(profile)&&l.launchers.length!==4))")
 edit("function resolveSensorSuite(id){return SHIP_SENSOR_MODEL_REGISTRY_V48_WIP09[String(id)]??null;}","function resolveSensorSuite(id){return id==='SOV_NO_SENSORS_A'?sovDisabledSensorTemplateA():SHIP_SENSOR_MODEL_REGISTRY_V48_WIP09[String(id)]??null;}")
 # Compatibility computational template is never installed or executed as a sensor.
 edit("registration=p.id==='CG_52_LATE_TICONDEROGA'?BUNKER_REGISTRATION:window.BurkeC5Registration;","registration=sovHullA(p)?{spy:{}}:p.id==='CG_52_LATE_TICONDEROGA'?BUNKER_REGISTRATION:window.BurkeC5Registration;")
 edit('enabled:{SPY:true,SPQ:true,NAV:true},emcon:false,rotors:', 'enabled:{SPY:!sovHullA(r),SPQ:!sovHullA(r),NAV:!sovHullA(r)},emcon:sovHullA(r),rotors:')
 edit('for(const r of physicalShipsB()){\n    const o=observerC(r);if(o.lastTick', 'for(const r of physicalShipsB()){\n    if(sovNoEquipmentA(r))continue;const o=observerC(r);if(o.lastTick')
 edit("for(const r of electronicShipsF()){\n    const own=r===ACTIVE_SHIP_RUNTIME,o=observerC(r)","for(const r of electronicShipsF()){\n    if(sovNoEquipmentA(r))continue;const own=r===ACTIVE_SHIP_RUNTIME,o=observerC(r)")
 edit('for(const r of electronicShipsF()){\n    const e=prepareElectronicF(r);if(e.lastTick', 'for(const r of electronicShipsF()){\n    if(sovNoEquipmentA(r))continue;const e=prepareElectronicF(r);if(e.lastTick')
 first('friendlyIffPlotsF',"if(sovNoEquipmentA(r))return [];")
 edit('for(const r of physicalShipsB())prepareElectronicF(r).context.step(dt);','for(const r of physicalShipsB())if(!sovNoEquipmentA(r))prepareElectronicF(r).context.step(dt);')
 edit('noiseRequested:!own,deceptionRequested:!own,auto:!own,autoAim:true','noiseRequested:!own&&!sovHullA(r),deceptionRequested:!own&&!sovHullA(r),auto:!own&&!sovHullA(r),autoAim:!sovHullA(r)')
 edit('observerC(r).emcon=r.initialEmconF??false;', 'observerC(r).emcon=sovHullA(r)?true:r.initialEmconF??false;')
 edit('applyDamage:wip12aApplyDamagePacket,damage:damageFloodImpactV48Wip12E', 'applyDamage:(packet,opts)=>wip12aApplyDamagePacket(sovHullA(owner)?sovRouteDamagePacketA(owner,packet):packet,opts),damage:damageFloodImpactV48Wip12E')
 # Double gate public commands and internal execution. Common damage context stays.
 for fn,arg,ret in [('electronicCommandF','id',"{ok:false,reason:'NO_EW_INSTALLED'}"),('electronicReleaseF','id',"{ok:false,reason:'NO_EW_INSTALLED'}"),('observerCommandC','id',"{ok:false,reason:'NO_SENSORS_INSTALLED'}"),('weaponCommandD','shipId',"{ok:false,reason:'NO_WEAPONS_INSTALLED'}"),('defenseCommandE','shipId',"{ok:false,reason:'NO_WEAPONS_INSTALLED'}")]:first(fn,"if(sovHullA(ENGAGEMENT_RUNTIME.ships.get(String("+arg+"))))return "+ret+';')
 edit('r.weapons.mainGun=r.weapons.gunMounts.get(r.weapons.selectedGunId);r.combatSystem.engagementControl.execution=', 'r.weapons.mainGun=sovHullA(r)?sovDisabledGunA():r.weapons.gunMounts.get(r.weapons.selectedGunId);if(sovHullA(r)){e.defenseE.mode=\'HOLD\';e.context=sovDisabledCombatA(context);r.combatSystem.engagementControl.mode=\'MANUAL\';}r.combatSystem.engagementControl.execution=')
 edit('for(const r of physicalShipsB()){const e=r.weapons.executionD??prepareWeaponsD(r);e.context.step(dt);','for(const r of physicalShipsB()){if(sovNoEquipmentA(r))continue;const e=r.weapons.executionD??prepareWeaponsD(r);e.context.step(dt);')
 first('attackDefaultsH3',"if(sovHullA(r))return {schema:ATTACK_POLICY_H3.schema,enabled:false};")
 first('tacticalActiveH1',"if(sovNoEquipmentA(r))return false;")
 edit('enabled:r!==ACTIVE_SHIP_RUNTIME,manualRadar:false','enabled:r!==ACTIVE_SHIP_RUNTIME&&!sovHullA(r),manualRadar:false')
 for fn in ['tacticalCommandH1','maneuverCommandH2','attackCommandH3','teamCommandH4','networkCommandG']:
  first(fn,"if(sovHullA(ENGAGEMENT_RUNTIME.ships.get(String(id))))return {ok:false,reason:'SOV_NAV_ONLY'};")
 edit('r.weapons.selectedGunId=q.selectedGunId;r.weapons.mainGun=r.weapons.gunMounts.get(q.selectedGunId);','r.weapons.selectedGunId=q.selectedGunId;r.weapons.mainGun=sovHullA(r)?sovDisabledGunA():r.weapons.gunMounts.get(q.selectedGunId);')
 edit("if(!r.weapons.gunMounts.has(q.selectedGunId)||!Array.isArray(q.guns)","if((sovHullA(r)?q.selectedGunId!==null:!r.weapons.gunMounts.has(q.selectedGunId))||!Array.isArray(q.guns)")
 # Keep legacy diagnostic combat fixture on its supported weapon-equipped profiles.
 edit('for(const profile of Object.values(SHIP_PROFILE_REGISTRY)){','for(const profile of Object.values(SHIP_PROFILE_REGISTRY).filter(p=>!p.capabilities?.npcOnly)){')
 # Fixed-pitch shaft spool feeds existing shared force integrator. SIM_TUNED 24 s.
 first('c17ShaftStep',"if(nav.sovSteamA){const target=Math.max(-5,Math.min(vCap,nav.targetSpeedKt||0)),cmd=offline?0:Math.sign(target)*C17_MAX_RPM*Math.abs(target)/32;nav._c17Tg=false;nav.shaftRpm=(nav.shaftRpm||0)+(cmd-(nav.shaftRpm||0))*(-Math.expm1(-h/24));nav.shaftRpmCap=C17_MAX_RPM*Math.min(1,vCap/32);nav.propPitch=1;return;}")
 edit('const nav=r.navigation;nav.c17Ownship=true;','const nav=r.navigation;if(sovHullA(r))nav.sovSteamA=true;nav.c17Ownship=!sovHullA(r);')
 edit("let placed=r.role==='ENEMY';","let placed=['ENEMY','NEUTRAL'].includes(r.role);")
 # Use shaft speed as the fixed-pitch force demand; no controllable-pitch artifact.
 edit('if(nav._c17Tg&&Number.isFinite(nav.telegraph)){','if(nav.sovSteamA){const rn=(nav.shaftRpm||0)/C17_MAX_RPM;demand=clamp(resistance(maxAheadKt*.514444)*rn*Math.abs(rn),-limit*.55,limit);}\n      else if(nav._c17Tg&&Number.isFinite(nav.telegraph)){')
 edit('function getShipDamageEffects(runtime=ACTIVE_SHIP_RUNTIME){','function getShipDamageEffects(runtime=ACTIVE_SHIP_RUNTIME){if(sovHullA(runtime))return sovDamageEffectsA(runtime);')
 edit('loading=load(summary);const mass=loading.massKg,cg=loading.cg;', 'loading=load(summary);const mass=loading.massKg,cg=loading.cg,waveForce=sovHullA(shipProfile)?sovWaveForcingA(ownerNavigation(),cfg):null;')
 edit('rollRate+=(-buoyancy*transverse+rollMoment-rollDamp*rollRate)', 'rollRate+=(-buoyancy*transverse+rollMoment+(waveForce?weight*gm0*waveForce.rollSlope:0)-rollDamp*rollRate)')
 edit('trimRate+=(-buoyancy*longitudinal-pitchDamp*trimRate)', 'trimRate+=(-buoyancy*longitudinal+(waveForce?rho*g*b.iyM4*waveForce.pitchSlope:0)-pitchDamp*trimRate)')
 edit('draftRate+=(weight-buoyancy-heaveDamp*draftRate)', 'draftRate+=(weight-buoyancy-(waveForce?rho*g*b.waterplaneM2*waveForce.heightM:0)-heaveDamp*draftRate)')
 edit('for(const t of v._bunkerAsset?.ownedTextures??[])t.dispose();', 'for(const t of v._bunkerAsset?.ownedTextures??[])t.dispose();for(const t of v._sovAssetA?.ownedTextures??[])t.dispose();')
 edit('z:Math.max(.8,12-r.survival.snapshot().draftM)', 'z:Math.max(.8,(sovHullA(p)?p.geometry.referenceHeightM:12)-r.survival.snapshot().draftM)')
 first('navalRcsC',"if(sovHullA(ref._truthObject)){const r=ref._truthObject,a=((Math.atan2(y-r.navigation.positionWorld.y,x-r.navigation.positionWorld.x)-r.navigation.heading)*180/Math.PI%360+360)%360,rows=SOV_REG_A.projectedAreaLut,i=Math.floor(a/15),q=rows[i],next=rows[(i+1)%rows.length],area=q[1]+(next[1]-q[1])*(a%15)/15;return Math.max(1,area*resolveShipProfile(r.profileId).signature.areaToRcsScale*({S:1,X:.82,IJ:.68}[rfBandKeyWip13A2(band)]??1));}")
 # UI membership is not network/team membership; only SOV scenario NAV is authorized.
 edit("r=>r===ACTIVE_SHIP_RUNTIME||r.role==='ALLY'&&r.faction==='FRIENDLY'&&r.executionState==='PHYSICAL_ACTIVE'","r=>r===ACTIVE_SHIP_RUNTIME||(r.role==='ALLY'&&r.faction==='FRIENDLY'||sovHullA(r))&&r.executionState==='PHYSICAL_ACTIVE'")
 first('fleetCommandG',"const sov=ENGAGEMENT_RUNTIME.ships.get(id);if(sovHullA(sov))return sovFleetNavA(sov,c);")
 edit("label:(own?'자함':'아군함')+' · '+(r.profileId.startsWith('CG')?", "label:sovHullA(r)?(r.role==='NEUTRAL'?'중립':'적')+' · 소브레멘니급 (NAV 전용)':(own?'자함':'아군함')+' · '+(r.profileId.startsWith('CG')?")
 edit('tacticalUpdateUiH1();\n}\nfunction networkUpdateUiG()', 'tacticalUpdateUiH1();sovFleetUiA();\n}\nfunction networkUpdateUiG()')
 edit("fleetMembersG().length<2?'아군함 없음'","networkMembersG().length<2?'아군함 없음'")
 # Scene owner adapter. Shared damage/crew/body/wake code continues unchanged.
 edit("if(p.id==='CG_52_LATE_TICONDEROGA')installBunkerRenderer(v,p);", "if(sovHullA(p))installSovRendererA(v,p);else if(p.id==='CG_52_LATE_TICONDEROGA')installBunkerRenderer(v,p);")
 edit("if(p.id!=='CG_52_LATE_TICONDEROGA')v.contractAudit=", "if(!sovHullA(p)&&p.id!=='CG_52_LATE_TICONDEROGA')v.contractAudit=")
 # Preserve SOV paint parameters through the existing cooperative cuts/deformation.
 edit("const isBunker=options.profile?options.profile.id==='CG_52_LATE_TICONDEROGA':IS_BUNKER;", "const isBunker=options.profile?(options.profile.id==='CG_52_LATE_TICONDEROGA'||sovHullA(options.profile)):IS_BUNKER;",4)
 edit("...(isBunker&&a.color&&b.color?{color:a.color.clone().lerp(b.color,t)}:{})", "...(isBunker&&a.color&&b.color?{color:a.color.clone().lerp(b.color,t)}:{}),...(a.sovPaint&&b.sovPaint?{sovPaint:a.sovPaint.clone().lerp(b.sovPaint,t)}:{})")
 edit("...(isBunker&&v.color?{color:v.color.clone()}:{})", "...(isBunker&&v.color?{color:v.color.clone()}:{}),...(v.sovPaint?{sovPaint:v.sovPaint.clone()}:{})",4)
 edit("uv:uv?new T.Vector2().fromBufferAttribute(uv,k):new T.Vector2()", "uv:uv?new T.Vector2().fromBufferAttribute(uv,k):new T.Vector2(),...(geo.attributes.sovPaint?{sovPaint:new T.Vector3().fromBufferAttribute(geo.attributes.sovPaint,k)}:{})",2)
 edit("const ps=new Float32Array(maxVertices*3),ns=", "const sovPaint=rows.some(r=>r.v.some(v=>v.sovPaint))?new Float32Array(maxVertices*3):null;const ps=new Float32Array(maxVertices*3),ns=")
 edit("uv[k*2+1]=v.uv.y;if(colors)", "uv[k*2+1]=v.uv.y;if(sovPaint){sovPaint[k*3]=v.sovPaint?.x??0;sovPaint[k*3+1]=v.sovPaint?.y??0;sovPaint[k*3+2]=v.sovPaint?.z??0;}if(colors)")
 edit("g.groups=groups;if(colors)", "g.groups=groups;if(sovPaint)g.setAttribute('sovPaint',new T.BufferAttribute(sovPaint.subarray(0,count*3),3));if(colors)")
 # Neutral optional extension retains exact old F_1 normalized shape when absent.
 edit("enemyId:'SHIP_SCENARIO_ENEMY_A',enemyMinM", "enemyId:'SHIP_SCENARIO_ENEMY_A',neutralId:'SHIP_SCENARIO_NEUTRAL_SOV_A',enemyMinM")
 edit('return {schema:DEPLOYMENT_POLICY_F.schema,targetShip:input.targetShip,enemyProfileId:input.enemyProfileId,','return {...(input.neutralProfileId!=null?{neutralProfileId:input.neutralProfileId}:{}),schema:DEPLOYMENT_POLICY_F.schema,targetShip:input.targetShip,enemyProfileId:input.enemyProfileId,')
 edit("const allowed=legacy?['schema','targetShip','enemyProfileId','enemyAircraftEnabled']:['schema','targetShip','enemyProfileId','allyProfileId','enemyAircraftEnabled','placementSeed','allyEmcon','enemyEmcon'];", "if(sovHullA(q.allyProfileId))errors.push('DEPLOYMENT_SOV_ENEMY_OR_NEUTRAL_ONLY');if(input.neutralProfileId!=null&&input.neutralProfileId!=='SOVREMENNY_956')errors.push('DEPLOYMENT_NEUTRAL_PROFILE');const allowed=legacy?['schema','targetShip','enemyProfileId','enemyAircraftEnabled']:['schema','targetShip','enemyProfileId','allyProfileId','neutralProfileId','enemyAircraftEnabled','placementSeed','allyEmcon','enemyEmcon'];")
 edit("for(const [key,role,id]of [['ally','ALLY',DEPLOYMENT_POLICY_F.allyId],['enemy','ENEMY',DEPLOYMENT_POLICY_F.enemyId]])", "for(const [key,role,id]of [['ally','ALLY',DEPLOYMENT_POLICY_F.allyId],['enemy','ENEMY',DEPLOYMENT_POLICY_F.enemyId],['neutral','NEUTRAL',DEPLOYMENT_POLICY_F.neutralId]])")
 edit('[DEPLOYMENT_POLICY_F.allyId,DEPLOYMENT_POLICY_F.enemyId]', '[DEPLOYMENT_POLICY_F.allyId,DEPLOYMENT_POLICY_F.enemyId,DEPLOYMENT_POLICY_F.neutralId]')
 edit('[prepared.ally,prepared.enemy].filter(Boolean)','[prepared.ally,prepared.enemy,prepared.neutral].filter(Boolean)',2)
 # New UI controls are appended through existing deployment authoring adapter.
 edit('parent.insertBefore(root,before);syncDeploymentUiA();','sovDeploymentUiA(root);parent.insertBefore(root,before);syncDeploymentUiA();')
 edit("const q=MULTISHIP_DEPLOYMENT_STATE_A.draft;\n  for", "const q=MULTISHIP_DEPLOYMENT_STATE_A.draft;for(const n of document.querySelectorAll('[data-neutral-choice]'))n.value=q.neutralProfileId??'NONE';\n  for")
 edit('fleet.ships.length>2','fleet.ships.length>3')
 edit('[src.deployment?.allyProfileId,src.deployment?.enemyProfileId]','[src.deployment?.allyProfileId,src.deployment?.enemyProfileId,src.deployment?.neutralProfileId]')
 edit('src.deployment?.enemyProfileId||src.deployment?.allyProfileId','src.deployment?.enemyProfileId||src.deployment?.allyProfileId||src.deployment?.neutralProfileId',2)
 edit("q?.entityId===DEPLOYMENT_POLICY_F.enemyId?'ENEMY':null,expected=role==='ALLY'?src.deployment?.allyProfileId:src.deployment?.enemyProfileId;", "q?.entityId===DEPLOYMENT_POLICY_F.enemyId?'ENEMY':q?.entityId===DEPLOYMENT_POLICY_F.neutralId?'NEUTRAL':null,expected=role==='ALLY'?src.deployment?.allyProfileId:role==='NEUTRAL'?src.deployment?.neutralProfileId:src.deployment?.enemyProfileId;")
 edit("role==='ALLY'?'FRIENDLY':'HOSTILE'", "role==='ALLY'?'FRIENDLY':role==='NEUTRAL'?'NEUTRAL':'HOSTILE'")
 edit('deploymentConfigA().enemyProfileId||deploymentConfigA().allyProfileId','deploymentConfigA().enemyProfileId||deploymentConfigA().allyProfileId||deploymentConfigA().neutralProfileId')
 edit("'telegraph','_trailTimer']", "'telegraph','_trailTimer','sovSteamA']")
 edit('velocityMps:{x:dir.x*600,y:dir.y*600,z:dir.z*600}', 'velocityMps:{x:dir.x*(sovHullA(r)?HARPOON_PROFILE_A.sim.cruiseSpeedMps:600),y:dir.y*(sovHullA(r)?HARPOON_PROFILE_A.sim.cruiseSpeedMps:600),z:dir.z*(sovHullA(r)?HARPOON_PROFILE_A.sim.cruiseSpeedMps:600)}')
 # SOV physical casualty continuation, with full preflight before mutation.
 edit('snapshot,controlWater,setWater,setDoor,setPump,seal,damageKeys:',"snapshot,controlWater,setWater,setDoor,setPump,seal,exportSovState(){return {timeS:state.timeS,stabilityV11:{...state.stabilityV11},ledger:{...state.ledger},last:{...state.last},seen:[...state.seen].slice(-128)};},restoreSovState(q){if(!sovHullA(options.profile))throw Error('SOV_RESTORE_OWNER');state.timeS=q.timeS;state.stabilityV11={...q.stabilityV11};state.ledger={...q.ledger};state.last={...q.last};state.seen=new Set(q.seen);},damageKeys:")
 edit('crew:r.crew.snapshot(),rescue:r.rescue.snapshot()}};', 'crew:sovHullA(r)?sovExportCrewA(r):r.crew.snapshot(),rescue:r.rescue.snapshot()}};')
 # SOV mid-casualty extension is preflighted before any live mutation.
 edit('flooding:jsonSafeCloneV48Wip11A(flood.snapshot())},crew:', 'flooding:jsonSafeCloneV48Wip11A(flood.snapshot()),...(sovHullA(r)?sovExportDamageA(r):{})},crew:')
 edit('validateWeaponInventoryD(r,q.ship?.inventory,errors);','sovValidateDamageA(r,q.ship?.damage,errors);validateWeaponInventoryD(r,q.ship?.inventory,errors);')
 edit('r.survival.restorePhysical(q.survival);f.setAttitude(q.survival);', 'if(sovHullA(r)){r.hitHistory.push(...jsonSafeCloneV48Wip11A(src.damage.surfaceHistorySovA));r.damage.control.restoreSovOperational(src.damage.controlSovA);f.restoreSovState(src.damage.floodContinuationSovA);}r.survival.restorePhysical(q.survival);f.setAttitude(q.survival);')
 edit('reset();return {cfg,reset,impact,ignite,setVent,assign,setAutomation,tick,snapshot,drainEvents,evaluateWork};',"reset();return {cfg,reset,impact,ignite,setVent,assign,setAutomation,tick,snapshot,drainEvents,evaluateWork,restoreSovOperational(q){if(!sovHullA(options.profile))throw Error('SOV_RESTORE_OWNER');timeS=q.timeS;for(const row of q.cells)Object.assign(cells[row.id],row);}};")
 # New ISAR library entry is offline information; measurement/classifier unchanged.
 lib=json.loads((HERE/'library.json').read_text())['entries']
 a=s.index('const ISAR_LIBRARY_F2=Object.freeze(');b=s.index('.map(e=>Object.freeze({...e,heightsM:Object.freeze(e.heightsM)})));',a)
 s=s[:a]+'const ISAR_LIBRARY_F2=Object.freeze('+json.dumps(lib,ensure_ascii=False,separators=(',',':'))+s[b:]
 edit("meanQuality:quality/n,majorConfusion:","meanQuality:quality/n,confusions,majorConfusion:")
 edit("return ['AN/APS-153 ISAR 판별표", "return ['Burke IIA↔Sovremenny 혼동: '+JSON.stringify(sovIsarConfusionA(d)),'AN/APS-153 ISAR 판별표")
 return s

def build(raw):
 assert hashlib.sha256(raw).hexdigest()==BASE_SHA;html=raw.decode();main=patch(decoded(html)).replace('v48_WIP_HELI_F2','v48_WIP_SOV_A');z=gzip.compress(main.encode(),9,mtime=0)
 m=re.search(r'data-c55-index="13">(.*?)</script>',html,re.S);html=html[:m.start(1)]+base64.b64encode(z).decode()+html[m.end(1):]
 m=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(main.encode()),gzipBytes=len(z),sha256=hashlib.sha256(main.encode()).hexdigest());html=html[:m.start(1)]+json.dumps(records,separators=(',',':'))+html[m.end(1):]
 assets=[]
 for id,file in [('sov-registration-a','registration.json'),('sov-meta-a','meta.json.gz'),('sov-textures-a','textures.json.gz'),('sov-geometry-a','geometry.bin.gz')]:
  b=(HERE/file).read_bytes();b=b if file.endswith('.gz')else gzip.compress(b,9,mtime=0);assets.append('<script id="'+id+'" type="application/octet-stream">'+base64.b64encode(b).decode()+'</script>')
 html=html.replace('</head>','\n'.join(assets)+'\n</head>').replace('v48_WIP_HELI_F2','v48_WIP_SOV_A').replace('V48_WIP_HELI_F2','V48_WIP_SOV_A')
 return html,main
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();h,m=build(a.baseline.read_bytes());a.output.write_text(h);a.output.with_suffix('.main.js').write_text(m);print(json.dumps({'bytes':len(h.encode()),'addedBytes':len(h.encode())-a.baseline.stat().st_size,'sha256':hashlib.sha256(h.encode()).hexdigest()}))
