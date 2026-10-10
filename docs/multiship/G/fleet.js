// LIVE_CANONICAL owner-addressed operator ports. Selection is UI routing only;
// player role, profiles, physical clocks and native sensor/weapon contexts stay put.
function fleetMembersG(){return [ACTIVE_SHIP_RUNTIME,...physicalShipsB()].filter(r=>r===ACTIVE_SHIP_RUNTIME||r.role==='ALLY'&&r.faction==='FRIENDLY'&&r.executionState==='PHYSICAL_ACTIVE');}
function fleetOperatorG(){
  const s=ENGAGEMENT_RUNTIME.fleetOperatorG??={selectedShipId:ACTIVE_SHIP_RUNTIME.entityId};
  if(!fleetMembersG().some(r=>r.entityId===s.selectedShipId))s.selectedShipId=ACTIVE_SHIP_RUNTIME.entityId;
  return s;
}
function fleetOwnerG(id=fleetOperatorG().selectedShipId){return fleetMembersG().find(r=>r.entityId===id)??null;}
function fleetOwnerOperatorG(r){
  if(!r.combatSystem.operatorG){r.combatSystem.operatorG={trackId:null,lastResult:'',revision:0};claimShipMutableRootA(r,'fleetOperatorG',r.combatSystem.operatorG);}
  return r.combatSystem.operatorG;
}
function fleetResetG(){
  ENGAGEMENT_RUNTIME.fleetOperatorG={selectedShipId:ACTIVE_SHIP_RUNTIME.entityId};
  for(const r of fleetMembersG())r.combatSystem.operatorG=null;
}
function fleetSelectG(id){
  const r=fleetOwnerG(id);if(!r)return {ok:false,reason:'FRIENDLY_OWNER_REQUIRED'};
  fleetOperatorG().selectedShipId=r.entityId;networkUpdateUiG();fleetUpdateUiG(true);return {ok:true,selectedShipId:r.entityId};
}
function fleetModeG(r){return r===ACTIVE_SHIP_RUNTIME?engagementControlMode:(r.weapons.executionD.context.defenseSnapshot().mode==='AUTO'?'AUTO':'MANUAL');}
function fleetGunsG(r){return r.weapons.gunMounts?[...r.weapons.gunMounts]:r.weapons.mainGun?[['PRIMARY',r.weapons.mainGun]]:[];}
function fleetTrackGateG(r,id){
  const tr=observerC(r).tracks.get(id);if(!tr)return {ok:false,reason:'현지 추적 없음'};
  if(networkProtectionG(r,tr)||['FRIEND','NEUTRAL'].includes(tr.identity))return {ok:false,reason:'보호 식별 — 발사 보류'};
  if(!tr.confirmed||tr.sensorDetected===false||networkLocalAgeG(tr)>2||tr.memActive||tr.reacquiring)return {ok:false,reason:'현지 추적 불충분 / 오래된 관측'};
  if(!['HOSTILE','TRAINING_TARGET'].includes(normalizeTrackOperatorIdentityA3(tr._operatorIdentity??tr.identity)))return {ok:false,reason:'적성 / 훈련 표적 식별 필요'};
  return {ok:true,tr};
}
function fleetCommandG(id,c){
  const r=fleetOwnerG(id),bad=reason=>({ok:false,reason});
  if(!r)return bad('FRIENDLY_OWNER_REQUIRED');
  if(!c||typeof c!=='object'||Array.isArray(c)||typeof c.action!=='string')return bad('COMMAND_FIELDS');
  const fields={NAV:['action','speedKt','rudderDeg'],MODE:['action','mode'],TRACK:['action','trackId'],IDENTITY:['action','trackId','identity'],FIRE:['action','trackId','weapon','mountId'],EMCON:['action','enabled']};
  if(!fields[c.action]||Object.keys(c).some(k=>!fields[c.action].includes(k)))return bad('COMMAND_FIELDS');
  if(c.action==='NAV'&&(!Number.isFinite(c.speedKt)||c.speedKt< -15||c.speedKt>shipAheadLimitB(resolveShipProfile(r.profileId))||!Number.isFinite(c.rudderDeg)||Math.abs(c.rudderDeg)>35))return bad('NAV_LIMIT');
  if(c.action==='MODE'&&!['MANUAL','AUTO'].includes(c.mode)||c.action==='EMCON'&&typeof c.enabled!=='boolean')return bad('COMMAND_FIELDS');
  if(['TRACK','IDENTITY','FIRE'].includes(c.action)&&(!Number.isInteger(c.trackId)||!observerC(r).tracks.has(c.trackId)))return bad('LOCAL_TRACK_ADDRESS_REQUIRED');
  if(c.action==='IDENTITY'&&!['UNKNOWN','HOSTILE','FRIEND','NEUTRAL','TRAINING_TARGET'].includes(c.identity))return bad('IDENTITY_FIELDS');
  if(c.action==='FIRE'&&(!['SM2','SM2ER','SM6','ESSM','HARPOON','GUN'].includes(c.weapon)||c.mountId!=null&&typeof c.mountId!=='string'))return bad('WEAPON_FIELDS');
  if(shipSurvivalB(r).snapshot().lost||shipEquipmentOfflineV1(r))return bad('SHIP_EQUIPMENT_OFFLINE');
  const op=fleetOwnerOperatorG(r);let result;
  if(c.action==='NAV'){
    const order=c17OrderForKt(c.speedKt),speed=Math.min(shipAheadLimitB(resolveShipProfile(r.profileId)),C17_TELEGRAPH[order+3].kt);
    if(r===ACTIVE_SHIP_RUNTIME){clearRoute();shipNav.targetSpeedKt=speed;shipNav.targetRudder=c.rudderDeg;result={ok:true};}
    else result=physicalShipCommandB(id,{targetSpeedKt:speed,targetRudder:c.rudderDeg});
    if(result.ok){r.navigation.manualSpeedV15=true;r.navigation.manualRudderV15=true;r.navigation.telegraph=order;}
  }else if(c.action==='MODE')result=r===ACTIVE_SHIP_RUNTIME?{ok:true,mode:setEngagementControlMode(c.mode)}:defenseCommandE(id,{mode:c.mode==='AUTO'?'AUTO':'HOLD'});
  else if(c.action==='EMCON'){
    // Individual radar operation exits the shared policy. Followers receive that
    // change through the normal delayed radio; no remote sensor mutation here.
    networkIndividualCommandG();networkOverrideRadarG(r);result=electronicCommandF(id,{emcon:c.enabled});
  }else if(c.action==='TRACK'){op.trackId=c.trackId;result={ok:true};}
  else if(c.action==='IDENTITY'){
    if(['HOSTILE','TRAINING_TARGET'].includes(c.identity)&&networkProtectionG(r,observerC(r).tracks.get(c.trackId)))result=bad('NETWORK_PROTECTED_IDENTITY');
    else result=r===ACTIVE_SHIP_RUNTIME?setTrackOperatorIdentityA3(c.trackId,c.identity):r.weapons.executionD.context.operatorIdentity(c.trackId,c.identity);
  }else {
    const mountId=c.mountId==='PRIMARY'?r.weapons.selectedGunId:c.mountId;
    if(fleetModeG(r)!=='MANUAL')result=bad('수동 모드에서 발사하세요');
    else {const gate=fleetTrackGateG(r,c.trackId);
      if(!gate.ok)result=gate;
      else if(r!==ACTIVE_SHIP_RUNTIME)result=weaponCommandD(id,{weapon:c.weapon,trackId:c.trackId,observerShipId:id,mode:'MANUAL',automatic:false,...(mountId?{mountId}:{})});
      else if(c.weapon==='GUN'){
        const gun=fleetGunsG(r).find(([id])=>id===(mountId??r.weapons.selectedGunId??'PRIMARY'))?.[1],authority=trackEngagementGateA3(c.trackId,{mode:'MANUAL'});
        if(!authority.ok)result=authority;else if(!gun)result=bad('MOUNT_NOT_INSTALLED');else {const q=gun.command(c.trackId,gun.snapshot().loadedAmmoId);result=q.ok?gun.requestFire(c.trackId,{mode:'MANUAL'}):q;}
      }else if(c.weapon==='HARPOON')result=harpoonRequestFireA(c.trackId);
      else {wip119SetOwnedLock(c.trackId);const before=missiles.length,q=wip119WeaponDescriptor(c.weapon).fire({automatic:false,mode:'MANUAL'});result={ok:missiles.length>before,reason:missiles.length>before?null:q?.reason??r.weapons.vlsReleaseB2?.lastReject?.reason??'발사 조건 불충족'};}
    }
  }
  op.revision++;op.lastResult=result.ok?(c.action==='FIRE'?'발사 명령 접수':'명령 적용'):(result.reason??'명령 거부');fleetUpdateUiG(true);return result;
}
function fleetSnapshotG(){
  return {selectedShipId:fleetOperatorG().selectedShipId,ships:fleetMembersG().map(r=>{
    const op=fleetOwnerOperatorG(r),nav=r.navigation,own=r===ACTIVE_SHIP_RUNTIME,cell=r.weapons.vls,
      count=type=>[...cell.fwd,...cell.aft].filter(c=>!c.destroyed&&c.type===type).reduce((n,c)=>n+(type==='ESSM4'?Math.max(0,c.essmCount??0):1),0);
    return {entityId:r.entityId,label:(own?'자함':'아군함')+' · '+(r.profileId.startsWith('CG')?'CG-52 Bunker Hill':'DDG-119 Delbert D. Black'),
      speedKt:nav.targetSpeedKt,rudderDeg:nav.targetRudder,currentSpeedKt:worldSpeedToMps(Math.hypot(nav.vx,nav.vy))/.514444,headingDeg:(nav.heading*180/Math.PI+450)%360,mode:fleetModeG(r),emcon:own?emconActive:observerC(r).emcon,
      selectedTrackId:op.trackId,lastResult:op.lastResult,inventory:{SM2:count('SM2'),SM2ER:count('SM2ER'),SM6:count('SM6'),ESSM:count('ESSM4'),HARPOON:r.weapons.harpoon?.tubes?.filter(t=>t.loaded).length??0},
      guns:fleetGunsG(r).map(([id])=>({id:id??'PRIMARY',label:id==='mk45a'?'후미 함포':'선수 함포'})),
      tracks:[...observerC(r).tracks.values()].filter(tr=>tr.confirmed&&networkLocalAgeG(tr)<=12).slice(0,96).map(tr=>({id:tr.trackId,classification:tr.classification,identity:tr.identity,ageS:networkLocalAgeG(tr),rangeKm:Math.hypot(worldToMeters(tr.x-nav.positionWorld.x),worldToMeters(tr.y-nav.positionWorld.y))/1000}))};
  })};
}
function fleetViewG(){
  const r=fleetOwnerG(),v=window.__WIP148_3D_VIEW__;if(!r||!v)return;
  v.focusPhysicalShipB(r===ACTIVE_SHIP_RUNTIME?null:r.entityId);v.open();
}
