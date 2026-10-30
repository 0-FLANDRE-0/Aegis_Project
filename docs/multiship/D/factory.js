// LIVE_CANONICAL, nonplayer only. These are lexical owner bindings, never a
// temporary assignment to ACTIVE_SHIP_* or the player's compatibility aliases.
function createWeaponContextD(owner){
  const ACTIVE_SHIP_RUNTIME=owner,ACTIVE_SHIP_PROFILE=owner.context.profile,
    IS_BUNKER=ACTIVE_SHIP_PROFILE.id==='CG_52_LATE_TICONDEROGA',shipNav=owner.navigation,
    aircraft={x:()=>shipNav.positionWorld.x,y:()=>shipNav.positionWorld.y},
    tracks=owner.combatSystem.trackManager.tracks,ciws=owner.weapons.closeIn,
    missiles=owner.weapons.executionD.sam,ramMissiles=owner.weapons.executionD.ram,
    mainGunProjectilesWip13B3=owner.weapons.executionD.shells,
    mainGunImpactLogWip13B3=owner.weapons.executionD.shellImpacts,
    vlsCells=owner.weapons.vls,floodAttitudePreviewV1=owner.survival,
    DF_TARGET_IDS=owner.geometry.targetIds,WIP199_HULL_STATIONS=ACTIVE_SHIP_PROFILE.geometry.hullStations,
    WIP173_SHIP_BOW_X_M=owner.geometry.bow,WIP173_SHIP_STERN_X_M=owner.geometry.stern,
    shipHitHistory=owner.hitHistory,WIP101_SYSTEM_MEMBER_CACHE=new Map(),WIP12C_SHIP_GEOMETRY_CACHE={value:null,builds:0};
  const CIWS_GAME_CONSTRAINT_CACHE_V1=new WeakMap(),BRIDGEMASTER_E_INSTALLATION={...ACTIVE_SHIP_PROFILE.sensors.bridgeMasterE,xM:ACTIVE_SHIP_PROFILE.geometry.hardpoints.bridgeMasterE.x,yM:ACTIVE_SHIP_PROFILE.geometry.hardpoints.bridgeMasterE.y,zM:ACTIVE_SHIP_PROFILE.geometry.hardpoints.bridgeMasterE.z},
    selectedMslType='ARH',wip118ControlState={assessments:new Map(),accel:new Map(),recentInterceptEvents:[],interceptSeenKeys:new Set()},
    enemyMissiles=new Proxy([],{get(_target,key){const rows=navalFlightObjectsD().filter(m=>m.ownerEntityId!==owner.entityId),value=rows[key];return typeof value==='function'?value.bind(rows):value;}});
  let WIP12E_TOPOLOGY_CACHE=null,selectedLockId=null,emconActive=false,
    engagementControlMode='MANUAL',missileSerial=1,mainGunProjectileSerialWip13B3=1,
    wip125VlsConsumeTieFlip=0,shipLastHit=null;
  const SPG62_ILLUMINATORS=ACTIVE_SHIP_PROFILE.geometry.hardpoints.spg62.map(q=>({
    id:q.id,oX:q.oX,oY:q.oY,height:q.heightM,label:q.label,mountRole:q.mountRole,moduleName:q.moduleName,
    hitboxHalfLengthM:1.45,hitboxHalfWidthM:1.45,hitboxHalfHeightM:1.35,
    preferredBrg:deg(q.blindCenterDeg===180?0:180),sectorHalf:deg(q.sectorHalfDeg),blindCenter:deg(q.blindCenterDeg),blindHalf:deg(q.blindHalfDeg)}));
  const SPG62_ENGAGEMENT_STATE=owner.combatSystem.fireControl.illuminatorAssignments,
    SPG62_RESERVATION_STATE=owner.combatSystem.fireControl.reservations,
    SPG62_RESERVATIONS=new Map(),SPG62_RESERVATION_META={lastPlanStep:-1,hardwareSig:'',engagementSig:'',revision:0},
    SPY1DV_FACE_KEYS=observerC(owner).normals.map(q=>q.id),
    SPY1DV_FACE_CENTER_REL=Object.fromEntries(observerC(owner).normals.map(q=>[q.id,q.bearingRad])),
    SPY1DV_FACE_MODULE=Object.fromEntries(observerC(owner).normals.map(q=>[q.id,q.moduleName])),
    WIP199_SPY_LAYOUT=Object.fromEntries(observerC(owner).normals.map(q=>[q.id,{center:{...q.center},bearingRad:q.bearingRad,moduleName:q.moduleName}])),
    WIP118_SHIP_ENVELOPE_RADIUS_M=Math.max(Math.abs(owner.geometry.bow),Math.abs(owner.geometry.stern));
  const SHIP_EXTERNAL_GEOMETRY=owner.geometry.boxes,SENSOR_MODEL=resolveSensorSuite(ACTIVE_SHIP_PROFILE.sensors.modelId),SPY1DV_SEARCH_MAX_RANGE_KM=ACTIVE_SHIP_PROFILE.sensors.spy1dv.searchMaxRangeKm,SPQ9B_SEARCH_MAX_RANGE_KM=ACTIVE_SHIP_PROFILE.sensors.spq9b.searchMaxRangeKm,
    WIP199_FINAL_LAYOUT={...ACTIVE_SHIP_PROFILE.geometry,...ACTIVE_SHIP_PROFILE.geometry.hardpoints,vls:{fwd:ACTIVE_SHIP_PROFILE.geometry.hardpoints.vlsForward,aft:ACTIVE_SHIP_PROFILE.geometry.hardpoints.vlsAft},ciws:{phalanx:ACTIVE_SHIP_PROFILE.geometry.hardpoints.phalanx,searam:ACTIVE_SHIP_PROFILE.geometry.hardpoints.seaRam}},_losState=new Map(),spyScheduler={faces:Object.fromEntries(observerC(owner).normals.map(q=>[q.id,{load01:0}]))};
  const CIWS_C55={banks:new Map(),serial:0,clockS:0,disabled:null,uiAgeS:0,stats:{attempted:0,accepted:0,created:0,expired:0,cueOnly:0},lastStep:-1},CIWS_C55_SENSOR_LINKS=new WeakMap(),SIM_SEED_BASE=rfSeedWip13A2('CIWS_D:'+BATTLESPACE.seed+':'+owner.entityId);
  const radar={mode:'TWS',pdTracking:false},lockCursor={x:0,y:0};
  function shipEquipmentOfflineV1(){return owner.survival.snapshot().equipmentOffline||owner.crew.offline();}
  function getShipDamageEffects(){return ownerDamageEffectsD(owner);}
  function getModuleDmg(name){return owner.flooding.readDamage(name);}
  function getShipSystemDamage(id,aggregate){return shipSystemDamageB(owner,id,aggregate);}
  function buildShipHitBoxes(){return owner.geometry.boxes;}
  function getDamageFloodV1(){return owner.flooding;}
  function getDamageControlV1(){return owner.damage.control;}
  function getShipInteriorTopologyV48Wip06(){return owner.interior;}
  function getShipCrewV21(){return owner.crew;}
  function getShipMassLedgerV32(){return owner.mass;}
  function getShipLongitudinalStrengthV48Wip03(){return owner.damage.strength;}
  function shipGeometryLayout(){return owner.geometry.layout;}
  function shipAssetRegistration(){return IS_BUNKER?BUNKER_REGISTRATION:window.BurkeC5Registration;}
  function shipCellRegistration(section,row,col){return shipAssetRegistration().cells[section]?.find(c=>c.row===row&&c.col===col)??null;}
  function shipHullContainsPoint(x,y,z){return owner.geometry.contains(x,y,z);}
  function wip199HullHalfBeamAt(x,z){return owner.geometry.halfBeam(x,z);}
  function wip199BowMaxXAtZ(z){return owner.geometry.bowAtZ(z);}
  function wip199HullInterpolatedSection(x){return owner.geometry.section(x);}
  function shipMassMarkWeaponsV32(reason){owner.mass.markWeaponsDirty(reason);}
  function shipGameFrameV1(){return shipBodyFrameB(owner);}
  function shipGamePointStateV1(p){return ownerPointStateD(owner,p);}
  function wip199ShipLocalWorldPoint(x,y,z){const q=shipGameFrameV1().pointToWorld({x,y,z});return {x:metersToWorld(q.x),y:metersToWorld(q.y),z:q.z};}
  function wip148VlsCellLocal(meta){return ownerVlsLocalD(owner,meta);}
  function mastSupportLostV12(){return getShipSystemDamage('MAST')>=80;}
  function spq9bTrackFresh(tr){return !emconActive&&getModuleDmg(ACTIVE_SHIP_PROFILE.geometry.hardpoints.spq9b.name)<80&&Math.min(...Object.entries(tr?.contributorsC??{}).filter(([k])=>k.startsWith('SPQ9B')).map(([,v])=>simStepCounter*SIM_FIXED_DT-v.measuredAtS),Infinity)<SPQ9B_TRACK_FRESH_S;}
  function isAegisAvailable(x,y){const az=Math.atan2(y-aircraft.y(),x-aircraft.x()),faces=observerC(owner).normals;return !emconActive&&faces.some(q=>observerHealthC(owner,q.moduleName)>.05&&Math.abs(angNorm(az-shipNav.heading-q.bearingRad))<=Math.max(Math.abs(q.lower),Math.abs(q.upper))+deg(8));}

  function trackEngagementGateA3(id,options={}){return ownerTrackGateD(owner,id,options);}
  function updateTrackOperationalStateA3(tr){return tr;}
  function wip121TargetSupportBlocked(id){return owner.weapons.executionD.blockedTracks.has(Number(id));}
  function vlsReleaseB2SupportPreflight(weapon){
    const d=wip119WeaponDescriptor(weapon),tr=tracks.get(selectedLockId);if(!d?.requiresIlluminator||!tr||surfaceTrackWip13C5(tr))return {ok:true,reservation:null};
    const th=ownerThreatRowD(owner,tr),pt={launchDelayS:0,interceptS:hardKillKinematicInterceptEstimate(th,d.profile).interceptS,futureThreat:th},q=wip118ReservationAtNezPoint(th,weapon,pt,{provisionalReservations:[]});
    return q.ok?{ok:true,reservation:q.reservation}:{ok:false,reason:'NO_CHANNEL'};
  }
  function wip119ReserveAvailable(){return {ok:false,reason:'SHADOW_AI_ONLY'};}
  function truthObjectForTrackV27(){return null;} // Never resolve another observer's numeric ID.
  function wip11cRememberEngagementTrack(){return null;}
  function retireTruthAssociationV27(){return false;}
  function wip11cQueueAsmRetirement(target,reason){target._deathReason=reason;target.dead=true;}
  function trackIdForTruthV27(){return null;}
  function trackDisplayLabelOr(id,fallback){return fallback??'TRACK';}
  function _wip106LogRamTerminal(){}
  function wip173RecordInterceptBurst(m,weapon,target,result){
    const e=owner.weapons.executionD,id=m.assignedTargetId??m.targetId;
    e.shadow.logs.push({step:simStepCounter,weaponReport:{trackKey:ownerTrackKeyD(owner.entityId,id),evidence:'FUZE_DETONATION',result:'UNCONFIRMED',truthUsed:false}});
    while(e.shadow.logs.length>NAVAL_WEAPONS_POLICY_D.maxLogs)e.shadow.logs.shift();
    wip173PushVisualEvent('INTERCEPT_BURST',{x:m.x,y:m.y,z:m.z,sourceId:m.id,weaponType:weapon,explosiveMassKg:wip173InterceptorExplosiveKg(weapon)});
  }
  function toggleEmcon(){observerC(owner).emcon=!observerC(owner).emcon;emconActive=observerC(owner).emcon;}
  function harpoonRuntimeA(){return owner.weapons.harpoon;}
  function harpoonTubeSpecA(id){return ACTIVE_SHIP_PROFILE.weapons.harpoon?.tubes.find(t=>t.id===id)??null;}
  function notify(message){owner.weapons.executionD.lastMessage=String(message);}
  function wip173PushVisualEvent(type,opt={}){if(opt.coordSpace==='SHIP_LOCAL'){const p=shipGameFrameV1().pointToWorld({x:opt.x,y:opt.y,z:opt.z});return worldVisualPublishD(type,{...opt,coordSpace:'WORLD',x:metersToWorld(p.x),y:metersToWorld(p.y),z:p.z,targetEntityId:owner.entityId});}return worldVisualPublishD(type,opt);}
  function debugLog(){} // Foreign telemetry cannot become player knowledge.
  function simRandom(){return observerRandomC(owner.weapons.executionD.weaponRng);}
  function rand(a,b){return a+(b-a)*simRandom();}
  function gaussRand(mean=0,sigma=1){return mean+observerNormalC(owner.weapons.executionD.weaponRng)*sigma;}
  function sensorDwellDue(key,period,dt){const q=owner.weapons.executionD.dwell,t=(q.get(key)??0)+dt;if(t+1e-9>=period){q.set(key,t%period);return true;}q.set(key,t);return false;}
  function ramRfMeasurement(rm,dt){return ownerRamRfD(rm,dt,{ramSeekerBoresight,simRandom,gaussRand,sensorDwellDue});}
  function bunkerSpgWorldMask(ill,x,y,z){const f=shipGameFrameV1(),p=f.pointToBody({x:worldToMeters(x),y:worldToMeters(y),z});return !bunkerRaySource({x:ill.oX,y:ill.oY,z:ill.height},wip12aUnit(wip12aSub(p,{x:ill.oX,y:ill.oY,z:ill.height})),Math.min(300,Math.hypot(p.x-ill.oX,p.y-ill.oY,p.z-ill.height)),'SPG62:'+ill.id);}
  function hardKillExistingEngagementCounts(id){const rows=missiles.filter(m=>!m.dead&&m.assignedTargetId===id);return {SM2:rows.filter(m=>!m.isESSM&&!m.isSM2ER&&!m.isSM6).length,SM2ER:rows.filter(m=>m.isSM2ER).length,SM6:rows.filter(m=>m.isSM6).length,ESSM:rows.filter(m=>m.isESSM).length,RAM:ramMissiles.filter(m=>m.alive&&m.targetId===id).length,PHALANX:ciws.filter(m=>m.firing&&m.trackingTrackId===id).length};}
  function wip118TrackAcceleration(){return {x:0,y:0,z:0};}
  // Shared world RF/terminal physics is deliberately outside this owner closure.
  // @GENERATED_OWNER_FUNCTIONS_D@
  // @GENERATED_RAM_FUZE_D@
  function sync(){emconActive=observerC(owner).emcon;aircraft._vx=shipNav.vx;aircraft._vy=shipNav.vy;}
  function launch(command){
    sync();selectedLockId=Number(command.trackId);engagementControlMode=command.mode??'MANUAL';
    const before=missiles.length,result=command.weapon==='HARPOON'?harpoonRequestFireA(selectedLockId):vlsReleaseB2Request(command.weapon,command,()=>command.weapon==='ESSM'?vlsReleaseEssmB1(command):vlsReleaseStandardB1({...command,weaponType:command.weapon}));
    for(const m of missiles.slice(before)){m.ownerEntityId=owner.entityId;m.ownerTrackKeyD=ownerTrackKeyD(owner.entityId,m.assignedTargetId);m.id=++ENGAGEMENT_RUNTIME.world.navalWeaponSerialD;m.rcsM2=.06;m._weaponLinkB3=null;weaponLinkB3Init(m);}
    return result?.ok!=null?result:{ok:missiles.length>before,projectileId:result?.id??null,reason:missiles.length>before?null:owner.weapons.executionD.lastMessage};
  }
  function step(dt){
    sync();allocateDatalinks();spg62MaybeReplanReservations();spg62ServoStep(dt);allocateSARH();
    for(const gun of owner.weapons.gunMounts.values())gun.step(dt);
    c55StepSensors(dt);
    for(const mount of ciws){mount.reloadTimer=Math.max(0,(mount.reloadTimer??0)-dt);mount.firing=false;}
    ownerCloseInTickD(owner,dt,{c55Bank,phalanxFireControlGate,ciwsTrackStateForTargetB1,ciwsGunBallisticInterceptSolution,ciwsInterceptSolution,ciwsGameCanFireV1,ciwsGameSlewV1,ciwsBodyYawV1,shipGameAimBodyV1,shipGameAimWorldV1,wip199CiwsMuzzleStateM,initializeRamSeeker,initializeRamSixDof});
    updateMainGunProjectilesWip13B3(dt);
    const h=harpoonRuntimeA();h.releaseCooldownS=Math.max(0,h.releaseCooldownS-dt);
    for(const tube of h.tubes)tube.capOpen01=clamp(tube.capOpen01+(!tube.loaded||h.pending?.tubeId===tube.id?1:-1)*dt/HARPOON_PROFILE_A.sim.releaseDoorDelayS,0,1);
    if(h.pending){h.pending.remainingS-=dt;if(h.pending.remainingS<=1e-9){const p=h.pending;h.pending=null;harpoonReleaseA(p);}}
    for(const m of missiles){if(m.dead)continue;const prev={x:m.x,y:m.y,z:m.z};updateMissile(m,dt);navalMissileContactD(m,prev);}
    for(const m of ramMissiles){if(!m.alive)continue;const prev={x:m.x,y:m.y,z:m.z};m.life+=dt;const gd=updateRamMeasurementSeeker(m,dt);updateRamSixDof(m,dt,gd.aYawReq,gd.aPitReq);navalMissileContactD(m,prev);if(m.alive)ramFuzeD(m,prev,dt);if(m.life>m.maxLife||m.z<0)m.alive=false;}
    stepOwnerPhalanxD(owner,dt,applyPhalanxProjectileHit);
    owner.weapons.executionD.ticks++;
  }
  return {launch,step,vlsIncidents:vlsIncidentsStepV23,createGun:createProfileGunModuleWip13B3,
    terminalGeometry:wip12cShipMacroGeometry,blast:wip12eSolveCompartmentBlast,
    applyDamage:wip12aApplyDamagePacket,damage:damageFloodImpactV48Wip12E,spall:wip12fKineticSpallParts,
    plan:(th,a,ctx)=>{sync();const recs=[];for(const weapon of wip14a14ExpandStandardOrder(['SM2','ESSM','RAM','PHALANX'],th)){const inventory=wip14a14DecisionInventory(getVlsCounts()),res=wip118BasicResource(weapon,inventory,th);if(!res.ok){recs.push({weapon,reason:res.reason});continue;}const p=wip118FindNezPlan(th,weapon,a,ctx);recs.push({weapon,plan:p,salvo:p.status==='READY'?wip118SalvoPolicy(th,weapon,a,p):null});}return recs;},
    cpa:tr=>wip118PredictTrackCPA(tr),closeIn:(c)=>ownerCloseInReleaseD(owner,c,{ciwsTrackStateForTargetB1,ciwsGunBallisticInterceptSolution,ciwsInterceptSolution,ciwsGameCanFireV1,ciwsGameSlewV1,shipGameAimBodyV1,shipGameAimWorldV1,wip199CiwsMuzzleStateM}),
    nativeCiws:()=>ciws.map(m=>{const b=c55Bank(m);return {id:m.id,type:m.type,files:b.files.size,status:b.status,reason:b.reason,measured:[...b.files.values()].map(q=>({localId:q.id,cmsTrackId:q.cmsTrackId,confirmed:q.confirmed,protectedIdentity:q.protectedIdentity,audit:q.audit?{accepted:q.audit.accepted,reason:q.audit.reason}:null,ageS:q.st.localAgeS,hits:q.st.localHits,rangeM:q.st.rangeM}))};}),
    reservations:()=>({live:[...SPG62_ENGAGEMENT_STATE],planned:[...SPG62_RESERVATION_STATE],queues:[...SPG62_RESERVATIONS]})};
}
