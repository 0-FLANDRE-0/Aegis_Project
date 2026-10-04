#!/usr/bin/env python3
"""Build the candidate from the exact reviewed startup HTML and local modules."""
from pathlib import Path
import sys, json, gzip, base64, re, hashlib, io, difflib
HERE=Path(__file__).resolve().parent
BASE_SHA='94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92'
sha=lambda b:hashlib.sha256(b).hexdigest()
def packed(b):return base64.b64encode(gzip.compress(b,compresslevel=9,mtime=0)).decode()
def build(src,out):
    raw=Path(src).read_bytes()
    if sha(raw)!=BASE_SHA:raise SystemExit('EXACT_STARTUP_BASELINE_REQUIRED')
    html=raw.decode();rec=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S)
    original=gzip.decompress(base64.b64decode(rec[1])).decode();s=original
    def replace(a,b,count=1):
        nonlocal s
        actual=s.count(a)
        if count is not None and actual!=count:raise RuntimeError(f'Patch context: expected {count}, got {actual}: {a[:100]}')
        s=s.replace(a,b)
    # Asset/profile consumers choose once; the DDG path keeps the original objects.
    replace('const SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8=', 'const BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8=')
    replace('const SRBOC_LAYOUT_WIP15A=','const DDG_SRBOC_LAYOUT_WIP15A=')
    replace('const NULKA_LAYOUT_15B=','const DDG_NULKA_LAYOUT_15B=')
    replace('p15.geometry.hardpoints.srboc=SRBOC_LAYOUT_WIP15A;','p15.geometry.hardpoints.srboc=DDG_SRBOC_LAYOUT_WIP15A;')
    replace('const extraRounds=SRBOC_LAYOUT_WIP15A.launchers.reduce','const extraRounds=DDG_SRBOC_LAYOUT_WIP15A.launchers.reduce')
    replace('p15.geometry.hardpoints.nulka=NULKA_LAYOUT_15B;','p15.geometry.hardpoints.nulka=DDG_NULKA_LAYOUT_15B;')
    prefix="""
async function readBunkerAsset(id,json=true){
 const node=document.getElementById(id);if(!node)throw Error('CG52_EMBEDDED_ASSET_MISSING:'+id);
 const bytes=Uint8Array.from(atob(node.textContent.trim()),c=>c.charCodeAt(0));
 const buf=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
 return json?JSON.parse(new TextDecoder().decode(buf)):buf;
}
const BUNKER_REGISTRATION=deepFreezeShipProfileV48Wip09(await readBunkerAsset('cg52-registration'));
const BUNKER_ENVELOPE=await readBunkerAsset('cg52-envelope');
window.BunkerEnvelopeSource=BUNKER_ENVELOPE.source;window.BunkerEnvelopeStats=BUNKER_ENVELOPE.stats;
/* CG52_ENVELOPE_ENGINE */
let SELECTED_SHIP_GEOMETRY=window.BurkeC52Layout;
let SELECTED_SHIP_REGISTRATION=window.BurkeC5Registration;
function shipGeometryLayout(){return SELECTED_SHIP_GEOMETRY;}
function shipAssetRegistration(){return SELECTED_SHIP_REGISTRATION;}
function shipCellRegistration(section,row,col){return shipAssetRegistration().cells[section]?.find(c=>c.row===row&&c.col===col)??null;}
"""
    geometry_record=re.search(r'<script type="application/octet-stream" data-c55-index="2">(.*?)</script>',html,re.S)
    engine='\n'.join(gzip.decompress(base64.b64decode(geometry_record[1])).decode().splitlines()[8:])
    engine=engine.replace('BurkeC52EnvelopeSource','BunkerEnvelopeSource').replace('BurkeC52EnvelopeStats','BunkerEnvelopeStats').replace('BurkeC52Layout','BunkerLayout')
    prefix=prefix.replace('/* CG52_ENVELOPE_ENGINE */',engine)
    # Route original runtime consumers through the selected offline geometry.
    s=s.replace('window.BurkeC52Layout','shipGeometryLayout()').replace('window.BurkeC5Registration','shipAssetRegistration()')
    replace('const BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8=',prefix+'\nconst BASE_SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8=')
    profile=(HERE/'bunker-profile.js').read_text()
    replace('const SHIP_PROFILE_REGISTRY=Object.freeze({[DDG_119_LATE_FLIGHT_IIA_PROFILE.id]:DDG_119_LATE_FLIGHT_IIA_PROFILE});',
      profile+"\nconst SHIP_PROFILE_REGISTRY=Object.freeze({[DDG_119_LATE_FLIGHT_IIA_PROFILE.id]:DDG_119_LATE_FLIGHT_IIA_PROFILE,[CG_52_LATE_TICONDEROGA_PROFILE.id]:CG_52_LATE_TICONDEROGA_PROFILE});")
    selection="""
const IS_BUNKER=ACTIVE_SHIP_PROFILE.id==='CG_52_LATE_TICONDEROGA';
let BUNKER_RENDER_META=null,BUNKER_RENDER_BUFFER=null,BUNKER_RENDER_COMPONENTS=null;
if(IS_BUNKER){
 SELECTED_SHIP_GEOMETRY=window.BunkerLayout;
 const R=BUNKER_REGISTRATION,arr=p=>[p.x,p.y,p.z];
 SELECTED_SHIP_REGISTRATION={...R,meshSource:R.basis,
   gun:{...R.guns.mk45.pivot,offsetX:R.guns.mk45.trunnionOffsetM.x,barrelM:R.guns.mk45.barrelM},
   ciws:{...R.ciws,seaRam:R.ciws.phalanxPort},
   sensor:{spq:arr(R.radars.find(q=>q.id==='SPQ9').center),nav:arr(R.radars.find(q=>q.id==='SPS73').center)}};
 BUNKER_RENDER_META=await readBunkerAsset('cg52-meta');BUNKER_RENDER_BUFFER=await readBunkerAsset('cg52-geo',false);BUNKER_RENDER_COMPONENTS=await readBunkerAsset('cg52-components');
}
const SRBOC_LAYOUT_WIP15A=ACTIVE_SHIP_PROFILE.geometry.hardpoints.srboc;
const NULKA_LAYOUT_15B=ACTIVE_SHIP_PROFILE.geometry.hardpoints.nulka;
"""
    replace('const ACTIVE_SHIP_PROFILE=await chooseShipBeforeInitialization();','const ACTIVE_SHIP_PROFILE=await chooseShipBeforeInitialization();\n'+selection)
    replace('inventory[section]=types.map((type,i)=>wip125MakeVlsCell(type,Math.floor(i/cfg.cols),i%cfg.cols));',
      "if(cfg.cellLayout&&(cfg.cellLayout.length!==cfg.cells||new Set(cfg.cellLayout.map(c=>c.row+':'+c.col)).size!==cfg.cells||cfg.cellLayout.some(c=>!Number.isInteger(c.row)||!Number.isInteger(c.col)||c.row<0||c.row>=cfg.rows||c.col<0||c.col>=cfg.cols)))throw Error('VLS_CELL_LAYOUT_INVALID:'+section);\n    inventory[section]=types.map((type,i)=>wip125MakeVlsCell(type,cfg.cellLayout?.[i]?.row??Math.floor(i/cfg.cols),cfg.cellLayout?.[i]?.col??i%cfg.cols));")
    replace('const C17_MAX_KT=31,','const C17_MAX_KT=IS_BUNKER?ACTIVE_SHIP_PROFILE.navigation.maxAheadKt:31,')
    replace("const xs=[geo.stern,-55.825,-38,-18,2,22,42,61,geo.bow],", "const xs=ACTIVE_SHIP_PROFILE.damage.flood.sectionDivisions??[geo.stern,-55.825,-38,-18,2,22,42,61,geo.bow],")
    # CG-specific sensor module tuning. All numerical performance assumptions are declared SIM_TUNED.
    replace('const SHIP_SENSOR_MODEL_REGISTRY_V48_WIP09=Object.freeze({DDG119_SENSOR_MODEL_V48_WIP09});',"""
const CG52_SENSOR_MODEL_LATE_V1=deepFreezeShipProfileV48Wip09({...DDG119_SENSOR_MODEL_V48_WIP09,
 spy1dv:{...DDG119_SENSOR_MODEL_V48_WIP09.spy1dv,searchRevisitAircraftS:1.0,trackRevisitAircraftS:.30,
   searchRevisitAsmS:.28,trackRevisitAsmS:.105,pdRevisitS:.055,schedulerGlobalBudgetMs:19,schedulerFaceBudgetMs:9.5,
   schedulerAntiStarvationReserveMs:4.8,rangeSigmaSearchM:52,rangeSigmaTrackM:17,
   azSigmaSearchDeg:.10,azSigmaTrackDeg:.032,surfaceTrackRevisitS:.42,surfaceRangeSigmaTrackM:19,
   surfaceAzSigmaTrackDeg:.045,horizonRetryS:.40},
 provenance:'CG52_MODERNIZED_SPY1A_SIM_TUNED__NOT_REAL_SENSOR_PERFORMANCE'});
const SHIP_SENSOR_MODEL_REGISTRY_V48_WIP09=Object.freeze({DDG119_SENSOR_MODEL_V48_WIP09,CG52_SENSOR_MODEL_LATE_V1});""")
    replace('if(targetAltM <= EXTREME_LOW_ALT_M) return 0.32;', 'if(targetAltM <= EXTREME_LOW_ALT_M) return ACTIVE_SHIP_PROFILE.sensors.spy1dv.seaClutterLowFactor??0.32;')
    replace('return lerp(0.32,1.0,Math.pow(t,0.72));','return lerp(ACTIVE_SHIP_PROFILE.sensors.spy1dv.seaClutterLowFactor??0.32,1.0,Math.pow(t,ACTIVE_SHIP_PROFILE.sensors.spy1dv.seaClutterExponent??0.72));')
    replace("bindShipRuntimeSubsystemV48Wip11A('sensors',{modelId:ACTIVE_SHIP_PROFILE.sensors.modelId,model:SENSOR_MODEL,runtime:null});",
      "bindShipRuntimeSubsystemV48Wip11A('sensors',{modelId:ACTIVE_SHIP_PROFILE.sensors.modelId,model:SENSOR_MODEL,runtime:null});if(IS_BUNKER)bunkerInitAuxNav();")
    replace('function resetBridgeMasterEState(){', 'function resetBridgeMasterEState(){if(IS_BUNKER)bunkerInitAuxNav();')
    replace('function updateBridgeMasterERadar(dt){', 'function updateBridgeMasterERadar(dt){\n    if(IS_BUNKER)bunkerUpdateAuxNav(dt);')
    # Actual sparse slots, shared by inventory, launch origin, damage and lid identity.
    replace('shipAssetRegistration().cells[section]?.[cell.row*8+cell.col]','shipCellRegistration(section,cell.row,cell.col)')
    replace('shipAssetRegistration().cells[sec][r*8+col]','shipCellRegistration(sec,r,col)')
    replace("moduleName:'AN/SPY-1D(V)(전좌)'","moduleName:IS_BUNKER?'AN/SPY-1A(전방)':'AN/SPY-1D(V)(전좌)'")
    replace("moduleName:'AN/SPY-1D(V)(전우)'","moduleName:IS_BUNKER?'AN/SPY-1A(우현)':'AN/SPY-1D(V)(전우)'")
    replace("moduleName:'AN/SPY-1D(V)(후우)'","moduleName:IS_BUNKER?'AN/SPY-1A(후방)':'AN/SPY-1D(V)(후우)'")
    replace("moduleName:'AN/SPY-1D(V)(후좌)'","moduleName:IS_BUNKER?'AN/SPY-1A(좌현)':'AN/SPY-1D(V)(후좌)'")
    replace('function spg62Quality(ill, targetBrgRel){','function spg62Quality(ill, targetBrgRel, targetAltM=ill.height, rangeKm=100){\n    if(IS_BUNKER)return bunkerSpgMask(ill,targetBrgRel,targetAltM,rangeKm).ok?spg62HardwareHealth01(ill):0;')
    replace('const maskQ = spg62Quality(ill, targetBrgRel);','const maskQ = spg62Quality(ill, targetBrgRel,tgtAlt,illHdist);')
    replace('function wip199SpgTerrainLosQ(ill,tgtX,tgtY,tgtAlt){','function wip199SpgTerrainLosQ(ill,tgtX,tgtY,tgtAlt){if(IS_BUNKER&&!bunkerSpgWorldMask(ill,tgtX,tgtY,tgtAlt))return 0;')
    replace('function wip199SpgTerrainLineFactor(ill,tgtX,tgtY,tgtAlt){','function wip199SpgTerrainLineFactor(ill,tgtX,tgtY,tgtAlt){if(IS_BUNKER&&!bunkerSpgWorldMask(ill,tgtX,tgtY,tgtAlt))return 0;')
    # Shared mount implementation accepts an installation-specific immutable view.
    replace('function wip13b1GunClearance(module,bodyAzRad,bodyElRad,distanceM=300){',
      'function wip13b1GunClearance(module,bodyAzRad,bodyElRad,distanceM=300){\n  if(IS_BUNKER&&module.installation)return bunkerGunClearance(module,bodyAzRad,bodyElRad,distanceM);')
    replace('const spec=SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8[installation.moduleId];if(!spec)',
      'const module=SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8[installation.moduleId],spec=IS_BUNKER&&module?deepFreezeShipProfileV48Wip09({...module,installation:{...installation},mount:{...module.mount,trunnionOffsetM:installation.trunnionOffsetM,exposedBarrelM:installation.exposedBarrelM,stowBodyAzRad:installation.neutralAzRad,trainMinRad:installation.neutralAzRad+module.mount.trainMinRad,trainMaxRad:installation.neutralAzRad+module.mount.trainMaxRad},damage:{...module.damage,moduleName:installation.moduleName}}):module;if(!spec)')
    replace('const body=shipGameAimBodyV1(solution.azimuthRad,solution.elevationRad);if(body.az<spec.mount.trainMinRad',
      'const body=shipGameAimBodyV1(solution.azimuthRad,solution.elevationRad);if(IS_BUNKER)body.az=bunkerGunAzimuth(spec,body.az);if(body.az<spec.mount.trainMinRad')
    replace("raw=typeof getShipSystemDamage==='function'?getShipSystemDamage(spec?.damage?.systemId??'MK45'):0;",
      "raw=spec?.damage?.moduleName?getModuleDmg(spec.damage.moduleName):typeof getShipSystemDamage==='function'?getShipSystemDamage(spec?.damage?.systemId??'MK45'):0;")
    replace('spec=ACTIVE_SHIP_RUNTIME.weapons.mainGun.spec;if(!tr)', 'spec=options.module??ACTIVE_SHIP_RUNTIME.weapons.mainGun.spec;if(!tr)')
    # Within each gun instance, release quality is assessed using that gun's profile.
    start=s.index('function createProfileGunModuleWip13B3(');end=s.index('const SHIP_GUN_BUILDER_REGISTRY_',start)
    part=s[start:end]
    part=part.replace("mode:options.mode??'MANUAL'","module:spec,mode:options.mode??'MANUAL'").replace("{mode:'MANUAL'}","{mode:'MANUAL',module:spec}")
    part=part.replace('state.solution.bodyAzRad=liveDemand.bodyAzRad;', 'if(IS_BUNKER)liveDemand.bodyAzRad=bunkerGunAzimuth(spec,liveDemand.bodyAzRad);state.solution.bodyAzRad=liveDemand.bodyAzRad;')
    part=part.replace('state.magazine[ammoId]--;state.shotsFired++;','state.magazine[ammoId]--;if(IS_BUNKER)shipMassMarkWeaponsV32(\'MAIN_GUN_FIRED\');state.shotsFired++;')
    part=part.replace('releaseGate:wip13b1SurfaceGunReleaseGate,','releaseGate:(id,solution,options={})=>wip13b1SurfaceGunReleaseGate(id,solution,{...options,module:spec}),')
    s=s[:start]+part+s[end:]
    bind='ACTIVE_SHIP_RUNTIME.weapons.mainGun=SHIP_GUN_BUILDER_REGISTRY_V48_WIP13B8[ACTIVE_SHIP_PROFILE.weapons.mainGun.builderId](ACTIVE_SHIP_PROFILE.weapons.mainGun,ACTIVE_SHIP_PROFILE);'
    replace(bind,bind+"""\nif(IS_BUNKER){
 ACTIVE_SHIP_RUNTIME.weapons.gunMounts=new Map(ACTIVE_SHIP_PROFILE.weapons.gunMounts.map(inst=>[inst.id,SHIP_GUN_BUILDER_REGISTRY_V48_WIP13B8[inst.builderId](inst,ACTIVE_SHIP_PROFILE)]));
 ACTIVE_SHIP_RUNTIME.weapons.selectedGunId=ACTIVE_SHIP_PROFILE.weapons.mainGun.id;
 ACTIVE_SHIP_RUNTIME.weapons.mainGun=ACTIVE_SHIP_RUNTIME.weapons.gunMounts.get(ACTIVE_SHIP_RUNTIME.weapons.selectedGunId);
}""")
    replace('function updateMainGunWip13B3(dt){const q=ACTIVE_SHIP_RUNTIME.weapons.mainGun?.step(dt);',
      'function updateMainGunWip13B3(dt){const q=IS_BUNKER?[...ACTIVE_SHIP_RUNTIME.weapons.gunMounts.values()].map(g=>g.step(dt)):ACTIVE_SHIP_RUNTIME.weapons.mainGun?.step(dt);')
    # Existing named geometry data has no operational RAM on CG-52.
    replace('const ciws = [','const ciws = IS_BUNKER?createBunkerCiwsRuntime({state:\'IDLE\',stateTimer:0,trackingTarget:null,trackQuality:0,tracking:false,firing:false,angle:0,trackAng:0,trackAngRate:0,turretRate:0,_shotAccumulator:0,burstTimer:0,trackToFireTime:.4,searchToTrackTime:.8,cueAge:0}):[')
    replace('ACTIVE_SHIP_PROFILE.weapons.closeIn.mounts.seaRam.engageRangeKm','ACTIVE_SHIP_PROFILE.weapons.closeIn.mounts.seaRam?.engageRangeKm??0')
    replace('function ciwsGameConstraintsV1(mount){', 'function ciwsGameConstraintsV1(mount){\n    if(IS_BUNKER){let q=CIWS_GAME_CONSTRAINT_CACHE_V1.get(mount);if(!q){q=bunkerCiwsConstraints(mount);CIWS_GAME_CONSTRAINT_CACHE_V1.set(mount,q);}return q;}')
    replace('function ciwsMountStateM(mount){return shipGamePointStateV1({x:mount.posOffsetM??0,y:0,z:mount.heightM??15});}',
      'function ciwsMountStateM(mount){return shipGamePointStateV1({x:mount.posOffsetM??0,y:mount.posOffsetYM??0,z:mount.heightM??15});}')
    replace('function wip199CiwsMuzzleStateM(mount,azRad,elRad,forwardM=0,verticalPivotOffsetM=0){',"""function wip199CiwsMuzzleStateM(mount,azRad,elRad,forwardM=0,verticalPivotOffsetM=0){
 if(IS_BUNKER){const m=BUNKER_REGISTRATION.ciws[mount.installation.hardpointId],body=shipGameAimBodyV1(azRad,elRad),
  d=forwardM?bunkerCiwsMuzzleOffset(m,body.az,body.el):{x:0,y:0,z:0};return shipGamePointStateV1({x:m.x+d.x,y:m.y+d.y,z:m.z+d.z});}
""")
    replace('ciws[1].ammo = ACTIVE_SHIP_PROFILE.weapons.closeIn.mounts.seaRam.ammo;',
      'ciws[1].ammo = IS_BUNKER?ciws[1].maxAmmo:ACTIVE_SHIP_PROFILE.weapons.closeIn.mounts.seaRam.ammo;')
    # Avoid construction of the legacy RAM branch's profile values on CG-52.
    replace('ACTIVE_SHIP_RUNTIME.weapons.mainGun?.reset();', 'ACTIVE_SHIP_RUNTIME.weapons.mainGun?.reset();if(IS_BUNKER)bunkerResetGunMounts();',count=None)
    replace('ACTIVE_SHIP_RUNTIME.weapons.mainGun.reset();', 'ACTIVE_SHIP_RUNTIME.weapons.mainGun.reset();if(IS_BUNKER)bunkerResetGunMounts();',count=None)
    replace("targetId:DF_TARGET_IDS[box.name]??null", "targetId:box.targetId??DF_TARGET_IDS[box.name]??null")
    replace("id=geo.targetIds[b.name];", "id=b.targetId??geo.targetIds[b.name];")
    replace("!box?.name||!DF_TARGET_IDS[box.name]", "!box?.name||(!box.targetId&&!DF_TARGET_IDS[box.name])")
    replace("targetId:DF_TARGET_IDS[box.name],system:String", "targetId:box.targetId??DF_TARGET_IDS[box.name],system:String")
    replace("const SPY1DV_FACE_MODULE = Object.freeze({F1:'AN/SPY-1D(V)(전좌)',F2:'AN/SPY-1D(V)(전우)',F3:'AN/SPY-1D(V)(후우)',F4:'AN/SPY-1D(V)(후좌)'});",
      "const SPY1DV_FACE_MODULE = Object.freeze(Object.fromEntries(Object.entries(WIP199_SPY_LAYOUT).map(([face,p])=>[face,p.moduleName])));")
    # This legacy fixture compares installed Phalanx and SeaRAM damage curves.
    # CG-52 has two Phalanx modules, so its analogous health tests are separate.
    replace("const b3=ciwsB3DamageAudit(),gunRows=b3.mounts.find(x=>x.type==='GUN')?.rows??[],ramRows=b3.mounts.find(x=>x.type==='RAM')?.rows??[];",
      "const b3=ciwsB3DamageAudit(),gunRows=b3.mounts.find(x=>x.type==='GUN')?.rows??[],ramRows=(IS_BUNKER?b3.mounts.filter(x=>x.type==='GUN')[1]:b3.mounts.find(x=>x.type==='RAM'))?.rows??[];")
    replace("if(!(monotonic(ramRows,'searchRangeKm')&&monotonic(ramRows,'maxTurretRateRadS')&&monotonic(ramRows,'trackingSigmaFactor',false)&&monotonic(ramRows,'reloadIntervalS',false)))",
      "if(!IS_BUNKER&&!(monotonic(ramRows,'searchRangeKm')&&monotonic(ramRows,'maxTurretRateRadS')&&monotonic(ramRows,'trackingSigmaFactor',false)&&monotonic(ramRows,'reloadIntervalS',false)))")
    # Representative old hull-compartment fixtures name DDG-specific plates.
    start=s.index('      const w101b=');end=s.index('      // WIP100 penetration physics contracts:',start)
    s=s[:start]+'      if(!IS_BUNKER){\n'+s[start:end]+'      }\n'+s[end:]
    replace("function buildShipHitBoxes(){const build=", "function buildShipHitBoxes(){if(IS_BUNKER)return buildBunkerHitboxes();const build=")
    # Generalized geometry filter remains shared by swept impacts and protection.
    replace("if(box?.geometryEnvelope==='C52_ARCHITECTURE'){", "if(box?.geometryEnvelope==='C52_ARCHITECTURE'||box?.geometryEnvelope==='CG52_ARCHITECTURE'){")
    replace("WIP06_FUNCTIONAL_INTERIOR_CLEAR_HANGARS_R3:createShipInteriorTopologyV48Wip06", "WIP06_FUNCTIONAL_INTERIOR_CLEAR_HANGARS_R3:createShipInteriorTopologyV48Wip06,CG52_FUNCTIONAL_INTERIOR_V1:createBunkerInterior")
    replace("DDG119_CREW_WIP07:createShipCrewV48Wip07", "DDG119_CREW_WIP07:createShipCrewV48Wip07,CG52_CREW_V1:createShipCrewV48Wip07")
    replace('function crewDutyPostsV48Wip07(){', 'function crewDutyPostsV48Wip07(){\n  if(IS_BUNKER)return bunkerCrewDutyPosts();')
    # Mass belongs to all live mounts, not the first GUN/RAM pair.
    mass_start=s.index("  const phalanx=ciws.find(q=>q.type==='GUN'),ram=ciws.find(q=>q.type==='RAM');",s.index('function shipMassWeaponNodesV32'))
    mass_end=s.index('  for(const l of mk36LauncherState)',mass_start)
    legacy=s[mass_start:mass_end]
    s=s[:mass_start]+"""  if(IS_BUNKER){
    for(const m of ciws)out.push(make('ciws.'+m.installationId+'.ammo','ORDNANCE_DYNAMIC',(m.ammo||0)*w.phalanxRoundKg,{x:m.posOffsetM,y:m.posOffsetYM,z:m.heightM},'SHARED_CARTRIDGE_MASS_CG52_POSITION'));
    for(const [id,g]of ACTIVE_SHIP_RUNTIME.weapons.gunMounts??[]){const q=g.snapshot(),h=ACTIVE_SHIP_PROFILE.geometry.hardpoints[g.installation.hardpointId];
      for(const [ammoId,n]of Object.entries(q.magazine))out.push(make('gun.'+id+'.'+ammoId,'ORDNANCE_DYNAMIC',n*g.spec.ammunition[ammoId].massKg,{x:h.x,y:h.y,z:h.z-3},'SIM_TUNED_ROUND_MASS_CG52_INDEPENDENT_MAGAZINE'));}
  }else{
"""+legacy+"  }\n"+s[mass_end:]
    # EW uses the physically visible outboard pod and the same single power pool.
    replace('const dxM=worldToMeters(em.x-aircraft.x()),dyM=worldToMeters(em.y-aircraft.y()),dzM=(em.z??0)-OWN_ALT_M;',
      'const emitter=IS_BUNKER?bunkerEwEmitter(em.x,em.y,em.z??0):null,dxM=IS_BUNKER?worldToMeters(em.x)-(emitter?.point.xM??worldToMeters(aircraft.x())):worldToMeters(em.x-aircraft.x()),dyM=IS_BUNKER?worldToMeters(em.y)-(emitter?.point.yM??worldToMeters(aircraft.y())):worldToMeters(em.y-aircraft.y()),dzM=(em.z??0)-(IS_BUNKER?(emitter?.point.zM??OWN_ALT_M):OWN_ALT_M);',count=2)
    replace("if(!noiseJamActive || eaShare<SLQ32_EA_ALLOC.minEffectiveShare)","if(!noiseJamActive || (IS_BUNKER&&!emitter) || eaShare<SLQ32_EA_ALLOC.minEffectiveShare)")
    replace("if(!deceptJamActive || eaShare<SLQ32_EA_ALLOC.minEffectiveShare)","if(!deceptJamActive || (IS_BUNKER&&!emitter) || eaShare<SLQ32_EA_ALLOC.minEffectiveShare)")
    replace('const effectiveErpW=NOISE_JAM.erpW*eaShare;','const effectiveErpW=NOISE_JAM.erpW*eaShare*(emitter?.health01??1);')
    replace('const effectiveReplayErpW=DECEPTION_JAM.replayErpW*eaShare;','const effectiveReplayErpW=DECEPTION_JAM.replayErpW*eaShare*(emitter?.health01??1);')
    # Auxiliary nav module names are selected with their installation.
    replace("getModuleDmg('BridgeMaster E')", "getModuleDmg(ACTIVE_SHIP_PROFILE.geometry.hardpoints.bridgeMasterE.name)",count=None)
    # Immutable generic interior hazard engine is shared, authored spaces are CG-52 specific.
    interior=(HERE/'bunker-interior.js').read_text()
    tail=original[original.index('  let evaluations=0,signature=null,cached=null;',original.index('function createShipInteriorTopologyV48Wip06')):original.index('\n}',original.index('  let evaluations=0,signature=null,cached=null;',original.index('function createShipInteriorTopologyV48Wip06')))]
    interior=interior.replace('/* BUNKER_SHARED_TOPOLOGY_ENGINE */',tail.replace('window.BurkeC52Layout','shipGeometryLayout()'))
    common=((HERE/'bunker-common.js').read_text()+'\n'+(HERE/'bunker-radars.js').read_text()).replace('.pointToLocal(','.pointToBody(')
    replace('mainGun:ACTIVE_SHIP_RUNTIME.weapons.mainGun.snapshot(),', 'mainGun:ACTIVE_SHIP_RUNTIME.weapons.mainGun.snapshot(),\n      ...(IS_BUNKER?{mountInventory:bunkerMountInventorySnapshot(),auxNav:bunkerAuxNavSnapshot()}:{}),')
    replace('const SRBOC_LAYOUT_WIP15A=ACTIVE_SHIP_PROFILE.geometry.hardpoints.srboc;',common+'\n'+interior+'\nconst SRBOC_LAYOUT_WIP15A=ACTIVE_SHIP_PROFILE.geometry.hardpoints.srboc;')
    replace('  completeShipStartup();','/* BUNKER_RENDERER_AND_AUDIT */\n  completeShipStartup();')
    if (HERE/'bunker-renderer.js').exists():s=s.replace('/* BUNKER_RENDERER_AND_AUDIT */',(HERE/'bunker-renderer.js').read_text())
    # Diagnostics appended only after the selected runtime has been constructed.
    if (HERE/'bunker-audit.js').exists():s=s.replace('  completeShipStartup();',(HERE/'bunker-audit.js').read_text()+'\n  completeShipStartup();')
    from refine_bunker import refine
    s=refine(s)
    from refine_bunker_e import refine_e
    s=refine_e(s)
    from refine_bunker_g import refine_g
    s=refine_g(s)
    from refine_bunker_i import refine_i
    s=refine_i(s)
    from refine_bunker_j import refine_j
    s=refine_j(s)
    (HERE/'candidate-main.js').write_text(s)
    (HERE/'main.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='STARTUP_A/main.js',tofile='BUNKERHILL_J/main.js')))
    html=html[:rec.start(1)]+packed(s.encode())+html[rec.end(1):]
    records=re.search(r'const records=(\[.*?\]);',html,re.S);a=json.loads(records[1]);gz=gzip.compress(s.encode(),9,mtime=0)
    a[13].update(rawBytes=len(s.encode()),gzipBytes=len(gz),sha256=sha(s.encode()))
    html=html[:records.start(1)]+json.dumps(a,separators=(',',':'))+html[records.end(1):]
    scripts=[]
    for ident,file in [('registration','registration.json'),('envelope','envelope.json'),('meta','asset-meta.json'),('components','asset-components.json'),('projection','projection.json')]:
        scripts.append(f'<script id="cg52-{ident}" type="application/octet-stream">'+packed((HERE/file).read_bytes())+'</script>')
    scripts.append('<script id="cg52-geo" type="application/octet-stream">'+base64.b64encode((HERE/'asset-geo.gz').read_bytes()).decode()+'</script>')
    html=html.replace('<script type="application/octet-stream" data-c55-index="0">','\n'.join(scripts)+'\n<script type="application/octet-stream" data-c55-index="0">',1)
    html=html.replace("window.C55Packaging.build='V48_WIP_STARTUP_A'","window.C55Packaging.build='V48_WIP_BUNKERHILL_J'")
    html=re.sub(r'<title>.*?</title>','<title>AEGIS v48 — DDG-119 / CG-52 Late-service Candidate</title>',html,count=1,flags=re.S)
    destination=Path(out)
    if destination.exists()and destination.read_bytes()!=html.encode():
        raise SystemExit('IMMUTABLE_VERSION_ALREADY_EXISTS_USE_NEW_WIP:'+str(destination))
    destination.write_text(html)
    print(json.dumps({'output':str(out),'bytes':len(html.encode()),'sha256':sha(html.encode()),'mainSha256':sha(s.encode())}))
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: build_bunker.py EXACT_STARTUP_A.html OUTPUT.html')
    build(*sys.argv[1:])
