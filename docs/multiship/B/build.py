#!/usr/bin/env python3
"""Deterministically repack main record 13 of the exact Multi Ship A release."""
import argparse,base64,gzip,hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE_SHA='704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685'
OLD='v48_WIP_MULTI_SHIP_A';NEW='v48_WIP_MULTI_SHIP_B';PATCHES=[]
def once(s,a,b,label):
    if s.count(a)!=1:raise AssertionError((label,s.count(a)))
    PATCHES.append(label);return s.replace(a,b,1)
def span(s,a,b,fn,label):
    start=s.index(a);end=s.index(b,start+len(a));PATCHES.append(label)
    return s[:start]+fn(s[start:end])+s[end:]
def build(s):
    s=once(s,'const MULTISHIP_MUTABLE_OWNERS_A=',(HERE/'runtime.js').read_text()+'\n'+(HERE/'state.js').read_text()+'\nconst MULTISHIP_MUTABLE_OWNERS_A=','physical fleet services')
    s=once(s,'boardSurvivor:()=>false,onReset:()=>{}','boardSurvivor:person=>r.rescue?.board?.(person.id)??false,onReset:()=>r.rescue?.reset?.()','owner evacuation callback')
    s=once(s,"const enemy=config.enemyProfileId?createPreparedShipRuntimeA(SHIP_PROFILE_REGISTRY[config.enemyProfileId],{entityId:'SHIP_SCENARIO_ENEMY_A',role:'ENEMY'}):null;","const enemy=config.enemyProfileId?preparePhysicalShipB(createPreparedShipRuntimeA(SHIP_PROFILE_REGISTRY[config.enemyProfileId],{entityId:'SHIP_SCENARIO_ENEMY_A',role:'ENEMY'})):null;",'detached physical preflight')
    s=once(s,'ENGAGEMENT_RUNTIME.ships.set(prepared.enemy.entityId,prepared.enemy);','ENGAGEMENT_RUNTIME.ships.set(prepared.enemy.entityId,prepared.enemy);activatePhysicalShipB(prepared.enemy);','departure activation')
    s=once(s,'ENGAGEMENT_RUNTIME.ships.delete(id);runtime.lifecycleState=', 'retirePhysicalShipB(runtime);ENGAGEMENT_RUNTIME.ships.delete(id);runtime.lifecycleState=','retire owner entities')
    s=s.replace("enemyExecution:'DEFERRED_STAGE_3_PLUS'","enemyExecution:'PHYSICAL_ACTIVE_COMBAT_DEFERRED'").replace('적함 준비','적함 배치').replace('적함 선택은 독립 상태를 준비합니다. 실제 해상 배치·항해·교전은 다음 단계에서 적용됩니다.','선택한 적함을 출항 시 바다에 배치합니다. 독립 항해·침수·피해를 적용하며, 탐지와 교전 AI는 이후 단계에서 추가됩니다.')
    s=s.replace("schema:'AEGIS_MULTI_SHIP_STAGE_2_A',registered:ENGAGEMENT_RUNTIME.ships.size,simulated:1","schema:'AEGIS_MULTI_SHIP_STAGE_3_B',registered:ENGAGEMENT_RUNTIME.ships.size,simulated:1+physicalShipsB().length").replace("'physicalEnemyDeployment','multiShipPhysicsTicks',",'')
    # Maximum speed belongs to the owner, including mixed-class pairs.
    s=once(s,'function c17ShaftStep(nav,h,offline,vCap=C17_MAX_KT,authority=1){','function c17ShaftStep(nav,h,offline,vCap=C17_MAX_KT,authority=1,maxAheadKt=C17_MAX_KT){','shaft owner ceiling')
    s=span(s,'function c17ShaftStep(', 'function ',lambda t:t.replace('C17_MAX_KT','maxAheadKt').replace('vCap=maxAheadKt','vCap=C17_MAX_KT').replace('maxAheadKt=maxAheadKt','maxAheadKt=C17_MAX_KT'),'shaft ceiling reads')
    s=span(s,'function createShipDynamicsV15(', 'let shipDynamicsV15=',lambda t:t.replace('const ownerNavigation=', 'const maxAheadKt=shipAheadLimitB(shipProfile);\n  const ownerNavigation=').replace('Math.min(C17_MAX_KT,','Math.min(maxAheadKt,').replace('resistance(C17_MAX_KT*','resistance(maxAheadKt*').replace('c17ShaftStep(nav,h,offline,vCap,authority)','c17ShaftStep(nav,h,offline,vCap,authority,maxAheadKt)'),'dynamics owner ceiling')
    s=once(s,'shipXM+=Math.cos(mid)*nextSpeed*dt;shipYM+=Math.sin(mid)*nextSpeed*dt;','if(options.position){const p=options.position();shipXM=p.x;shipYM=p.y;}else{shipXM+=Math.cos(mid)*nextSpeed*dt;shipYM+=Math.sin(mid)*nextSpeed*dt;}','wave owner inertial origin')
    s=once(s,'function shipEquipmentOfflineV1(){return floodAttitudePreviewV1.snapshot().equipmentOffline||!!shipCrewV21?.offline();}','function shipEquipmentOfflineV1(runtime=ACTIVE_SHIP_RUNTIME){return runtime===ACTIVE_SHIP_RUNTIME?floodAttitudePreviewV1.snapshot().equipmentOffline||!!shipCrewV21?.offline():runtime.survival.snapshot().equipmentOffline||runtime.crew.offline();}','owner equipment state')
    s=span(s,'  function computeShipStatus(', '  // Ship RCS model',lambda t:t.replace('function computeShipStatus(){','function computeShipStatus(runtime=ACTIVE_SHIP_RUNTIME){\n    const getShipSystemDamage=(id,aggregate)=>shipSystemDamageB(runtime,id,aggregate);').replace('function getShipDamageEffects(){','function getShipDamageEffects(runtime=ACTIVE_SHIP_RUNTIME){\n    const getShipSystemDamage=(id,aggregate)=>shipSystemDamageB(runtime,id,aggregate),shipCrewV21=runtime===ACTIVE_SHIP_RUNTIME?ACTIVE_SHIP_RUNTIME.crew:runtime.crew,damageControlV1=runtime===ACTIVE_SHIP_RUNTIME?ACTIVE_SHIP_RUNTIME.damage?.control:runtime.damage.control;').replace('getDamageFloodV1()','getDamageFloodV1(runtime)').replace('getShipLongitudinalStrengthV48Wip03()','getShipLongitudinalStrengthV48Wip03(runtime)').replace('shipEquipmentOfflineV1()','shipEquipmentOfflineV1(runtime)').replace('C17_MAX_KT * propulsionFac','(runtime===ACTIVE_SHIP_RUNTIME?C17_MAX_KT:shipAheadLimitB(resolveShipProfile(runtime.profileId))) * propulsionFac').replace('mastSupportLostV12()?0:',"(runtime===ACTIVE_SHIP_RUNTIME?mastSupportLostV12():shipSystemDamageB(runtime,'MAST')>=80)?0:"),'shared owner damage effects')
    s=span(s,'function updateShipMovement(', '// =====',lambda t:t.replace('function updateShipMovement(dt){','function updateShipMovement(dt,runtime=ACTIVE_SHIP_RUNTIME){').replace('const s = shipNav;','const s = runtime.navigation;').replace('getShipDamageEffects()','getShipDamageEffects(runtime)').replace('getShipDynamicsV15()','getShipDynamicsV15(runtime)').replace('shipEquipmentOfflineV1()','shipEquipmentOfflineV1(runtime)').replace('aircraft._heading =','if(runtime===ACTIVE_SHIP_RUNTIME)aircraft._heading =').replace('aircraft._speedMps =','if(runtime===ACTIVE_SHIP_RUNTIME)aircraft._speedMps =').replace('aircraft._vx =','if(runtime===ACTIVE_SHIP_RUNTIME)aircraft._vx =').replace('aircraft._vy =','if(runtime===ACTIVE_SHIP_RUNTIME)aircraft._vy =').replace('const ax = aircraft.x(), ay = aircraft.y();','const ax=s.positionWorld.x,ay=s.positionWorld.y;'),'shared owner navigation')
    s=once(s,'function shipTerrainCollisionAhead(dx,dy){','function shipTerrainCollisionAhead(dx,dy,runtime=ACTIVE_SHIP_RUNTIME){if(runtime!==ACTIVE_SHIP_RUNTIME)return shipTerrainContactB(runtime,dx,dy);','terrain owner input')
    s=span(s,'function shipTerrainCollisionAhead(', 'function ',lambda t:t.replace('const ax=aircraft.x(),ay=aircraft.y()', 'const ax=runtime.navigation.positionWorld.x,ay=runtime.navigation.positionWorld.y'),'terrain owner position')
    s=once(s,'function damageSupportPowerV30(generators){','function damageSupportPowerV30(generators,runtime=ACTIVE_SHIP_RUNTIME){','owner auxiliary power')
    s=span(s,'function damageSupportPowerV30(', 'function damageControlStepV1',lambda t:t.replace('getDamageFloodV1()','getDamageFloodV1(runtime)'),'owner pump feeds')
    s=span(s,'function damageControlStepV1(', '// Presentation-only adapter.',control,'shared owner damage-control cadence')
    s=span(s,'  function damageFloodPowerV1(', '  function damageFloodImpactV1',flood_tick,'shared owner flooding survival tick')
    s=span(s,'  function damageFloodImpactV1(', '  function damageFloodImpactV48Wip12C',impact,'shared owner physical impact')
    # A confirmed axial shell crossing can sit just outside bow/stern tolerance,
    # where halfBeam is zero. Keep the existing extent/finite gates and require
    # an actual inside/outside transition over 10 cm before accepting that tip.
    s=once(s,'&&geo.halfBeam(p.x,p.z)>0;}','&&(geo.halfBeam(p.x,p.z)>0||geo.contains(p.x-.05,p.y,p.z)!==geo.contains(p.x+.05,p.y,p.z));}','confirmed axial hull contact')
    s=once(s,'function createShipDamageVisualStateV1(flood,control,history,boxes){','function createShipDamageVisualStateV1(flood,control,history,boxes,options={}){','presentation owner event input')
    s=span(s,'function createShipDamageVisualStateV1(', 'function shipDamageVisualStateV1',lambda t:t.replace('(WIP12B_TERMINAL_EVENTS??[])','(options.terminalEvents??WIP12B_TERMINAL_EVENTS??[])'),'isolate residual scar events')
    s=once(s,'damageFloodTickV1(dt);\n', 'damageFloodTickV1(dt);if(physicalShipsB().length){SIM_SUBSYSTEM_PROFILER_V48_WIP11A.phase(_wip11aProfileTick,"naval_ship_damage");for(const r of physicalShipsB())damageFloodTickV1(dt,r);}\n','physical fleet tick')
    s=span(s,'function simulateFixedTick(', 'function ',lambda t:t.replace('advanceOwnshipWorldWip14A(dt);','advanceOwnshipWorldWip14A(dt);for(const r of physicalShipsB()){updateShipMovement(dt,r);advancePhysicalShipB(r,dt);}resolveNavalContactsB(dt);'),'physical fleet navigation')
    s=once(s,'const rows=ENGAGEMENT_RUNTIME.world.entities.lifeRafts;if(!rows.length)return;','const rows=ENGAGEMENT_RUNTIME.world.entities.lifeRafts.filter(q=>q.ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId);if(!rows.length)return;','CIC raft truth boundary')
    s=once(s,'function rescueLaunchPoseK(stationIndex,serial=0,nav=shipNav){\n  const deck=ACTIVE_SHIP_PROFILE.geometry.hardpoints.flightDeck,geo=shipGeometryLayout()', 'function rescueLaunchPoseK(stationIndex,serial=0,nav=shipNav,profile=ACTIVE_SHIP_PROFILE,geometry=shipGeometryLayout()){\n  const deck=profile.geometry.hardpoints.flightDeck,geo=geometry','owner rescue stations')
    s=once(s,'function rescueAvoidHullK(q){\n  const nav=ACTIVE_SHIP_RUNTIME.navigation,', 'function rescueAvoidHullK(q,runtime=ACTIVE_SHIP_RUNTIME){\n  const nav=runtime.navigation,','owner rescue hull')
    s=span(s,'function rescueAvoidHullK(', 'function shipRescueK',lambda t:t.replace('geo=shipGeometryLayout()','geo=runtime===ACTIVE_SHIP_RUNTIME?shipGeometryLayout():runtime.geometry.layout'),'owner rescue envelope')
    s=once(s,'const audit=resetScenarioWorldV48Wip11A(seed);','const audit=resetScenarioWorldV48Wip11A(seed);applyDeploymentA(prepareDeploymentA(deploymentConfigA()));','new sea owner redeployment')
    s=state_patches(s)
    s=renderer_patches(s)
    s=once(s,'ships:view.surfaceTargetVisuals.size+1,hostileMissiles:', 'ships:view.surfaceTargetVisuals.size+1+(view.navalShipPresentersB?.size??0),hostileMissiles:','profiler physical ship count')
    s=once(s,'multiShipSnapshotA:multiShipSnapshotA,','physicalFleetSnapshotB:fleetPhysicalSnapshotB, physicalShipProbeB:physicalProbeB, physicalShipCommandB:physicalShipCommandB, multiShipSnapshotA:multiShipSnapshotA,','physical diagnostics')
    return s
def control(t):
    t=t.replace('function damageControlStepV1(dt,power){','function damageControlStepV1(dt,power,runtime=ACTIVE_SHIP_RUNTIME){\n  const own=runtime===ACTIVE_SHIP_RUNTIME;let damageControlAccumulatorV1=own?ownerControlAccumulatorB():runtime.physicalAccumulators.damageControl,interiorTopologyAccumulatorV48Wip06=own?ownerInteriorAccumulatorB():runtime.physicalAccumulators.interior;')
    t=t.replace('floodAttitudePreviewV1.snapshot()','shipSurvivalB(runtime).snapshot()').replace('damageSupportPowerV30(power)','damageSupportPowerV30(power,runtime)').replace('shipNav.speed','runtime.navigation.speed').replace('shipEquipmentOfflineV1()','shipEquipmentOfflineV1(runtime)')
    for name in ['getShipCrewV21','getDamageControlV1','getDamageFloodV1','getShipInteriorTopologyV48Wip06','getShipMassLedgerV32']:t=t.replace(name+'()',name+'(runtime)')
    t=t.replace('vlsIncidentsStepV23(.1,power01,control,p);','if(own)vlsIncidentsStepV23(.1,power01,control,p);')
    t=t.replace("notify((c?.label??'구획')+' · '+e.text);","if(own)notify((c?.label??'구획')+' · '+e.text);else runtime.physicalEvents.push({...e,ownerEntityId:runtime.entityId});")
    return t.replace('\n}\n','\n  if(own)setOwnerControlAccumulatorsB(damageControlAccumulatorV1,interiorTopologyAccumulatorV48Wip06);else Object.assign(runtime.physicalAccumulators,{damageControl:damageControlAccumulatorV1,interior:interiorTopologyAccumulatorV48Wip06});\n}\n',1)
def flood_tick(t):
    t=t.replace('function damageFloodPowerV1(){','function damageFloodPowerV1(runtime=ACTIVE_SHIP_RUNTIME){').replace("getShipSystemDamage(id)","shipSystemDamageB(runtime,id)")
    t=t.replace('function damageFloodTickV1(dt){','function damageFloodTickV1(dt,runtime=ACTIVE_SHIP_RUNTIME){\n    const own=runtime===ACTIVE_SHIP_RUNTIME,survivalModel=shipSurvivalB(runtime),nav=runtime.navigation;')
    t=t.replace('shipGamePreviousPoseV1=floodAttitudePreviewV1.snapshot();shipGamePoseDtV1=dt;','if(own){shipGamePreviousPoseV1=survivalModel.snapshot();shipGamePoseDtV1=dt;}else {runtime.previousPose=survivalModel.snapshot();runtime.poseDtS=dt;}')
    t=t.replace('floodAttitudePreviewV1','survivalModel').replace('shipNav','nav').replace('syncShipMassLossV16()','shipMassLossB(runtime)').replace('damageControlStepV1(h,power)','damageControlStepV1(h,power,runtime)')
    for name in ['getDamageFloodV1','getWaveFloodEnvironmentV48Wip05','damageFloodPowerV1','getShipLongitudinalStrengthV48Wip03','getShipDynamicsV15','computeShipStatus','shipEquipmentOfflineV1']:t=t.replace(name+'()',name+'(runtime)')
    t=t.replace('shipHP=survival.irreversible?0:Math.max(0,100-computeShipStatus(runtime).overall);','const hp=survival.irreversible?0:Math.max(0,100-computeShipStatus(runtime).overall);if(own)shipHP=hp;else runtime.health.shipHP=hp;')
    t=t.replace("if(survival.state!==damageFloodTickV1.lastState)","if(own&&survival.state!==damageFloodTickV1.lastState)")
    t=t.replace('if(shipEquipmentOfflineV1(runtime)||shipCrewV21?.combatUnavailable())','if(own&&(shipEquipmentOfflineV1(runtime)||shipCrewV21?.combatUnavailable()))')
    t=t.replace('updateShipSurvivalBannerV1(survival);updateDamageControlPanelV1();','if(own){updateShipSurvivalBannerV1(survival);updateDamageControlPanelV1();}')
    return t
def impact(t):
    t=t.replace("!String(id).startsWith('dud:')","impactMeta?.ignitionAllowed??!String(id).startsWith('dud:')").replace('impactMeta=null){','impactMeta=null,runtime=ACTIVE_SHIP_RUNTIME){').replace('DF_TARGET_IDS[p.name]', '(runtime===ACTIVE_SHIP_RUNTIME?DF_TARGET_IDS:runtime.geometry.targetIds)[p.name]')
    for name in ['getDamageFloodV1','getDamageControlV1','getShipLongitudinalStrengthV48Wip03','getShipCrewV21']:t=t.replace(name+'()',name+'(runtime)')
    return t
def state_patches(s):
    s=once(s,'deployment:deploymentConfigA(),capabilities:', 'deployment:deploymentConfigA(),fleet:exportPhysicalFleetB(),capabilities:','fleet operational export')
    s=once(s,"'enemyShipExecutionAndTransientState',", "'nonplayerCombatTransientState','nonplayerDamageControlAndStructuralTimeline',",'save phase boundary')
    s=once(s,"Object.freeze({id:'deployment',validate:validateOperationalDeploymentA})", "Object.freeze({id:'deployment',validate:validateOperationalDeploymentA}),Object.freeze({id:'fleet',validate:validatePhysicalFleetB})",'fleet preflight codec')
    s=once(s,"'aviation','deployment'])", "'aviation','deployment','fleet'])",'codec inventory')
    s=once(s,'const harpoonMigrations=[];', "const harpoonMigrations=[];if(!Object.hasOwn(src,'fleet')){src.fleet={schema:MULTISHIP_PHYSICAL_SCHEMA_B,deploymentState:src.deployment?.enemyProfileId?'PENDING':'NONE',ships:[]};harpoonMigrations.push({id:'LEGACY_FLEET_B',policy:'FRESH_PHYSICAL_DEPLOYMENT_FROM_PREVIOUS_CONFIG'});}",'legacy fleet migration')
    s=once(s,'const preparedDeployment=prepareDeploymentA(src.deployment);','const preparedDeployment=prepareDeploymentA(src.deployment);restorePreparedPhysicalFleetB(preparedDeployment,src.fleet);','detached validated fleet restore')
    s=once(s,'crew.schema!==ACTIVE_SHIP_PROFILE.crew.modelId','crew.schema!==(ctx.profile??ACTIVE_SHIP_PROFILE).crew.modelId','owner crew schema preflight')
    s=span(s,'function createShipDynamicsV15(', 'let shipDynamicsV15=',lambda t:t.replace('navigation,attitude,hydro,load,setLoading:', 'navigation,attitude,restoreOperationalPose:pose=>{needsInitialEquilibrium=false;rollRate=trimRate=draftRate=0;hydroSample=hydro(pose);hydroAge=0;stabilityAge=V48_WIP04_STABILITY_MODEL.referenceRefreshS;Object.assign(diagnostic,{draftM:pose.draftM,rollRateRadS:0,trimRateRadS:0,draftRateMps:0});},hydro,load,setLoading:'),'restore owner pose with reset rates')
    s=span(s,'function createShipSurvivalV1(', '// Abstract 310-person',lambda t:t.replace('reset();return {config,reset,step,snapshot};',"function restorePhysical(src){pose={heelRad:src.heelRad,trimRad:src.trimRad,draftM:src.draftM};target={...src.target};state=src.state;timeS=src.timeS;phaseS=src.phaseS;capTimer=src.capTimer;sinkTimer=src.sinkTimer;side=Math.sign(pose.heelRad)||1;events=src.events.map(e=>({...e}));waterM3=src.waterM3;imbalance=src.imbalance;}\n  reset();return {config,reset,step,snapshot,restorePhysical};"),'survival canonical restore')
    return s
def renderer_patches(s):
    for name,args in [('createDamageSurfaceToolsV2','T'),('enhanceDamageSurfaceToolsV6','T,legacy'),('enhanceIntegratedRuptureV7','T,tools'),('c13EnhanceTools','T,tools')]:
        s=once(s,'function '+name+'('+args+'){','function '+name+'('+args+',options={}){\n const isBunker=options.profile?options.profile.id===\'CG_52_LATE_TICONDEROGA\':IS_BUNKER;','damage tools owner '+name)
        start=s.index('function '+name+'(');end=s.index('\nfunction ',start+10)
        block=s[start:end].replace('IS_BUNKER&&','isBunker&&')
        if name=='createDamageSurfaceToolsV2':block=block.replace('sampler,geometry})))','sampler,geometry},options),options),options)')
        s=s[:start]+block+s[end:]
    s=once(s,'function wip13c52InteriorSections(T){','function wip13c52InteriorSections(T,geometry=shipGeometryLayout()){','coarse DDG owner sections')
    s=span(s,'function wip13c52InteriorSections(', 'function createInteriorSectionsV9',lambda t:t.replace('const L=shipGeometryLayout()','const L=geometry'),'coarse source geometry')
    s=once(s,"if(root?.userData?.wip13c51)return wip13c52InteriorSections(T);","if(root?.userData?.wip13c51)return wip13c52InteriorSections(T,geometryForShipProfileA(SHIP_PROFILE_REGISTRY[root.userData.shipProfileId]).layout);",'owner coarse interior renderer')
    s=once(s,'function wip13c52InstallRenderer(v){\n const L=shipGeometryLayout()', 'function wip13c52InstallRenderer(v,profile=ACTIVE_SHIP_PROFILE){\n const L=profile.id===ACTIVE_SHIP_PROFILE.id?shipGeometryLayout():geometryForShipProfileA(profile).layout','DDG renderer owner geometry')
    s=span(s,'function wip13c52InstallRenderer(', '  function wip13c51InstallRenderer',lambda t:t.replace('shipAssetRegistration()', '(profile.id===\'DDG_119_LATE_FLIGHT_IIA\'?window.BurkeC5Registration:shipAssetRegistration())').replace('window.WIP13C5_2={','if(!v.ownerRuntime)window.WIP13C5_2={'),'DDG scanner registration')
    s=once(s,'function wip13c51InstallRenderer(view){\n    const R=shipAssetRegistration()', "function wip13c51InstallRenderer(view,profile=ACTIVE_SHIP_PROFILE){\n    const R=profile.id==='DDG_119_LATE_FLIGHT_IIA'?window.BurkeC5Registration:shipAssetRegistration()",'DDG renderer owner profile')
    s=span(s,'  function wip13c51InstallRenderer(', '  wip13c51InstallRenderer(WIP148_EXTERNAL_3D);',lambda t:t.replace('ACTIVE_SHIP_PROFILE','profile').replace('profile=profile','profile=ACTIVE_SHIP_PROFILE').replace('window.WIP13C5_1=API;','if(!view.ownerRuntime)window.WIP13C5_1=API;').replace('setTimeout(()=>wip13c51MakePanel(),0);','if(!view.ownerRuntime)setTimeout(()=>wip13c51MakePanel(),0);'),'reuse DDG builder without global diagnostic overwrite')
    s=once(s,'  wip13c51InstallRenderer(WIP148_EXTERNAL_3D);','  const MULTISHIP_RENDER_BASE_B={...WIP148_EXTERNAL_3D};\n  wip13c51InstallRenderer(WIP148_EXTERNAL_3D);','capture common owner presenter methods')
    s=once(s,'this.applyShipBodyFrame(st);this.scene.updateMatrixWorld(true);','this.applyShipBodyFrame(st);this.syncPhysicalFleetB?.(st);this.scene.updateMatrixWorld(true);','render fleet after common origin and budgets')
    s=once(s,'function harpoonDetachSourceCapsA(T,source,root,view){','function harpoonDetachSourceCapsA(T,source,root,view,profile=ACTIVE_SHIP_PROFILE){','owner Harpoon tube presentation')
    s=span(s,'function harpoonDetachSourceCapsA(', 'function ',lambda t:t.replace('const specs=ACTIVE_SHIP_PROFILE.weapons.harpoon.tubes','const specs=profile.weapons.harpoon.tubes'),'Harpoon source cap owner')
    s=once(s,'function installBunkerRenderer(view){\n  if(!IS_BUNKER)return;',"function installBunkerRenderer(view,profile=ACTIVE_SHIP_PROFILE){\n  if(profile.id!=='CG_52_LATE_TICONDEROGA')return;",'CG renderer owner profile')
    s=span(s,'function installBunkerRenderer(', 'installBunkerRenderer(WIP148_EXTERNAL_3D);',lambda t:t.replace('ACTIVE_SHIP_PROFILE','profile').replace('profile=profile','profile=ACTIVE_SHIP_PROFILE').replace('harpoonDetachSourceCapsA(T,o,root,this)', 'harpoonDetachSourceCapsA(T,o,root,this,profile)').replace('const frame=shipGameFrameV1()', 'const frame=view.ownerRuntime?shipBodyFrameB(view.ownerRuntime):shipGameFrameV1()'),'reuse exact CG builder and articulated parts')
    s=once(s,'installBunkerRenderer(WIP148_EXTERNAL_3D);','installBunkerRenderer(WIP148_EXTERNAL_3D);\n'+(HERE/'renderer.js').read_text(),'owner renderer fleet integration')
    return s
def main():
    p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('output',type=Path);a=p.parse_args();raw=a.baseline.read_bytes();assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    html=raw.decode();m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S);source=gzip.decompress(base64.b64decode(m[1])).decode();candidate=build(source).replace(OLD,NEW);gz=gzip.compress(candidate.encode(),mtime=0)
    html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):];row=re.search(r'const records=(\[.*?\]);',html,re.S);records=json.loads(row[1]);records[13].update(rawBytes=len(candidate.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(candidate.encode()).hexdigest());html=html[:row.start(1)]+json.dumps(records,separators=(',',':'))+html[row.end(1):];html=html.replace(OLD,NEW).replace("C55Packaging.build='V48_WIP_MULTI_SHIP_A'","C55Packaging.build='V48_WIP_MULTI_SHIP_B'")
    a.output.write_text(html);a.output.with_suffix('.main.js').write_text(candidate);manifest={'baselineSha256':BASE_SHA,'htmlSha256':hashlib.sha256(html.encode()).hexdigest(),'mainSha256':hashlib.sha256(candidate.encode()).hexdigest(),'changedPackedRecords':[13],'patches':PATCHES};a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))
if __name__=='__main__':main()
