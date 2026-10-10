// Stage 5A/5B: explicit owner execution, shared physical world, bounded shadow AI.
const NAVAL_WEAPONS_POLICY_D=Object.freeze({schema:'AEGIS_OWNER_WEAPONS_D_1',shadowPeriodTicks:12,maxLogs:64,maxRounds:256,maxShells:128,activeAI:false,automaticForeignRelease:false});
const ownerDamageEffectsD=getShipDamageEffects,worldVisualPublishD=wip173PushVisualEvent;
function ownerTrackKeyD(shipId,trackId){return JSON.stringify([String(shipId),Number(trackId)]);}
function ownerPointStateD(r,p){
  if(r===ACTIVE_SHIP_RUNTIME)return shipGamePointStateV1(p);
  const n=r.navigation,pose=r.survival.snapshot(),dt=n.worldPoseDtS||SIM_FIXED_DT,f=shipBodyFrameB(r),q=f.pointToWorld(p),
    prev=createShipBodyFrameV1(r.weapons.executionD?.previousPose??pose,{x:worldToMeters(n.previousPositionWorld.x),y:worldToMeters(n.previousPositionWorld.y),z:OWN_ALT_M},n.previousHeadingWorld).pointToWorld(p);
  return {xM:q.x,yM:q.y,zM:q.z,vxMps:(q.x-prev.x)/dt,vyMps:(q.y-prev.y)/dt,vzMps:(q.z-prev.z)/dt};
}
function ownerVlsLocalD(r,meta){
  const reg=r.profileId==='CG_52_LATE_TICONDEROGA'?BUNKER_REGISTRATION:window.BurkeC5Registration,
    c=reg.cells[meta.section]?.find(c=>c.row===meta.row&&c.col===meta.col);
  if(!c)throw Error('OWNER_VLS_UNINSTALLED_SLOT');let x=c.x,y=c.y;
  if(meta.weaponType==='ESSM'){const o=[[-.22,-.22],[.22,-.22],[-.22,.22],[.22,.22]][clamp(Math.floor(meta.quadIndex??0),0,3)];x+=o[0]*.649;y+=o[1]*.649;}
  return {xM:x,zM:y,deckM:c.z};
}
function ownerTrackGateD(r,id,options={}){
  const tr=r.combatSystem.trackManager.tracks.get(Number(id)),identity=normalizeTrackOperatorIdentityA3(tr?._operatorIdentity??tr?.identity),bad=reason=>({ok:false,reason});
  if(!tr)return bad('NO_TRACK');if(!tr.confirmed||tr.sensorDetected===false||tr.sensorAge>2)return bad('FCS_TRACK_STALE');
  if(options.automatic||options.mode==='AUTO'||options.mode==='SEMIAUTO')return bad('SHADOW_AI_ONLY');
  if(!['HOSTILE','TRAINING_TARGET'].includes(identity))return bad('IDENTITY_WITHHELD');
  if(shipEquipmentOfflineV1(r))return bad('SHIP_EQUIPMENT_OFFLINE');return {ok:true,identity,truthUsed:false};
}
function prepareWeaponsD(r){
  const saved=r.restoredWeaponInventoryD??(r.weapons.executionD?exportWeaponInventoryD(r):null);delete r.restoredWeaponInventoryD;
  ENGAGEMENT_RUNTIME.world.navalWeaponSerialD??=1000000;
  const e={schema:NAVAL_WEAPONS_POLICY_D.schema,sam:[],ram:[],shells:[],bullets:[],shellImpacts:[],blockedTracks:new Set(),ticks:0,previousPose:r.survival.snapshot(),lastMessage:null,weaponRng:{state:rfSeedWip13A2('WEAPONS_D:'+BATTLESPACE.seed+':'+r.entityId),spare:null},dwell:new Map(),shadow:{frame:-1,logs:[],assessments:new Map(),releaseCount:0},impacts:[],seenImpacts:new Set()};
  r.weapons.executionD=e;(ENGAGEMENT_RUNTIME.world.entities.navalOrdnanceD??=new Map()).set(r.entityId,{sam:e.sam,ram:e.ram,shells:e.shells,bullets:e.bullets});r.combatSystem.fireControl.execution='OWNER_EXECUTION_D';
  r.combatSystem.fireControl.spg62Servo={mounts:r.context.profile.geometry.hardpoints.spg62.map(q=>({illId:q.id,azRad:0,elRad:0,azRateRadS:0,elRateRadS:0,targetTrackId:null,aligned:false,settleS:0,emitting:false,mode:'HOLD'}))};
  r.weapons.vlsReleaseB2={profileId:VLS_RELEASE_B2_PROFILE.id,intervalS:VLS_RELEASE_B2_PROFILE.defaultIntervalS,nextStep:0,lastStep:null,busy:false,releaseCount:0,history:[],lastReject:null};
  const context=createWeaponContextD(r);e.context=context;
  r.weapons.gunMounts=new Map((r.context.profile.weapons.gunMounts??[r.context.profile.weapons.mainGun]).map(inst=>[inst.id,context.createGun(inst,r.context.profile,{health:spec=>Math.max(0,1-r.flooding.readDamage(spec.damage.moduleName)/100)})]));
  r.weapons.mainGun=r.weapons.gunMounts.get(r.weapons.selectedGunId);r.combatSystem.engagementControl.execution='SHADOW_DECISIONS_D';
  restoreWeaponInventoryD(r,saved);claimShipMutableRootA(r,'weaponExecutionD',e);return e;
}
function retireWeaponsD(r){ENGAGEMENT_RUNTIME.world.entities.navalOrdnanceD?.delete(r.entityId);if(r.weapons.executionD){r.weapons.executionD.sam.length=0;r.weapons.executionD.ram.length=0;r.weapons.executionD.shells.length=0;r.weapons.executionD.bullets.length=0;r.weapons.executionD=null;}for(const m of harpoonWorldA())if(m.ownerEntityId===r.entityId)m.alive=false;r.weapons.harpoon.pending=null;}
function resetWeaponsD(){
  for(const r of physicalShipsB())prepareWeaponsD(r);
  ENGAGEMENT_RUNTIME.world.navalWeaponSerialD=1000000;
}
function ownerThreatRowD(r,tr){
  const n=r.navigation,x=worldToMeters(tr.x-n.positionWorld.x),y=worldToMeters(tr.y-n.positionWorld.y),z=(tr.z??0)-OWN_ALT_M,
    vx=worldSpeedToMps((tr.vx??0)-n.vx),vy=worldSpeedToMps((tr.vy??0)-n.vy),vz=tr.vz??0,rangeM=Math.hypot(x,y,z),closure=rangeM>0?-(x*vx+y*vy+z*vz)/rangeM:0;
  return {id:tr.trackId,tr,type:tr.classification==='ASM'?'ASM':'AIR',tag:(tr.z??0)<100?'ASM-SK':'ASM-SS',dKm:rangeM/1000,alt:tr.z??0,vr:closure*3.6,tti:rangeM/Math.max(20,closure),threatScore:clamp(closure/500+5000/Math.max(100,rangeM),0,1)};
}
function shadowDecisionsD(r){
  const e=r.weapons.executionD,s=e.shadow,frame=Math.floor(simStepCounter/NAVAL_WEAPONS_POLICY_D.shadowPeriodTicks);if(s.frame===frame)return;s.frame=frame;
  const rows=[];for(const tr of r.combatSystem.trackManager.tracks.values()){
    if(!tr.confirmed)continue;const key=ownerTrackKeyD(r.entityId,tr.trackId),identity=normalizeTrackOperatorIdentityA3(tr._operatorIdentity??tr.identity),th=ownerThreatRowD(r,tr),cpa=e.context.cpa(tr),gate=ownerTrackGateD(r,tr.trackId),
      a={state:tr.sensorAge>4?'LOST':cpa?.resolved&&cpa.cpaM>Math.max(Math.abs(r.geometry.bow),Math.abs(r.geometry.stern))+WIP118_KILL_ASSESSMENT_POLICY.harmlessMarginM?'HARMLESS':'THREAT',cpaM:cpa?.cpaM??null,cpaTimeS:cpa?.tCpaS??null,closureTgoS:cpa?.linearTgoRawS??null,accel:{x:0,y:0,z:0}};
    s.assessments.set(key,a);
    const reason=tr.domain==='SURFACE'?'SURFACE_ROE_REQUIRED':!gate.ok?gate.reason:a.state!=='THREAT'?a.state:'SHADOW_ONLY',plans=gate.ok&&tr.domain!=='SURFACE'&&a.state==='THREAT'?e.context.plan(th,a,{provisionalReservations:[]}):[];
    rows.push({observerShipId:r.entityId,trackId:tr.trackId,trackKey:key,classification:tr.classification,identity,observationAgeS:tr.sensorAge,assessment:a,plans,action:'WITHHOLD',reason,truthUsed:false,executed:false});
  }
  s.logs.push({step:simStepCounter,rows});if(s.logs.length>NAVAL_WEAPONS_POLICY_D.maxLogs)s.logs.shift();
  for(const key of s.assessments.keys())if(!r.combatSystem.trackManager.tracks.has(JSON.parse(key)[1]))s.assessments.delete(key);
}
function stepWeaponsD(dt){
  for(const r of physicalShipsB()){const e=r.weapons.executionD??prepareWeaponsD(r);e.context.step(dt);shadowDecisionsD(r);e.previousPose=r.survival.snapshot();
    for(const key of ['sam','ram']){const rows=e[key];while(rows.length>NAVAL_WEAPONS_POLICY_D.maxRounds){const i=rows.findIndex(m=>m.dead||m.alive===false);if(i<0)break;rows.splice(i,1);}}
  }
}
function weaponCommandD(shipId,command={}){
  const r=ENGAGEMENT_RUNTIME.ships.get(String(shipId));if(!r||r===ACTIVE_SHIP_RUNTIME||r.executionState!=='PHYSICAL_ACTIVE')return {ok:false,reason:'PHYSICAL_NONPLAYER_REQUIRED'};
  if(Object.keys(command).some(k=>!['weapon','trackId','observerShipId','mountId','ammoId','mode','automatic'].includes(k))||command.observerShipId!==r.entityId||!Number.isInteger(command.trackId))return {ok:false,reason:'OWNER_TRACK_ADDRESS_REQUIRED'};
  if(command.automatic||command.mode&&command.mode!=='MANUAL')return {ok:false,reason:'SHADOW_AI_ONLY'};
  const e=r.weapons.executionD??prepareWeaponsD(r),gate=ownerTrackGateD(r,command.trackId,command);if(!gate.ok)return gate;
  if([...e.sam,...e.ram].filter(m=>!m.dead&&m.alive!==false).length>=NAVAL_WEAPONS_POLICY_D.maxRounds)return {ok:false,reason:'ORDNANCE_LIMIT'};
  if(command.weapon==='GUN'){const g=r.weapons.gunMounts.get(command.mountId??r.weapons.selectedGunId);if(!g)return {ok:false,reason:'MOUNT_NOT_INSTALLED'};const q=g.command(command.trackId,command.ammoId??g.snapshot().loadedAmmoId);return q.ok?g.requestFire(command.trackId,{mode:'MANUAL',ammoId:command.ammoId}):q;}
  if(['RAM','PHALANX'].includes(command.weapon))return e.context.closeIn(command);
  if(!['SM2','SM2ER','SM6','ESSM','HARPOON'].includes(command.weapon))return {ok:false,reason:'WEAPON_NOT_INSTALLED'};
  return e.context.launch(command);
}
function weaponsSnapshotD(){return {schema:NAVAL_WEAPONS_POLICY_D.schema,activeAI:false,ships:physicalShipsB().map(r=>{const e=r.weapons.executionD;return {entityId:r.entityId,profileId:r.profileId,ticks:e?.ticks??0,vls:jsonSafeCloneV48Wip11A(r.weapons.vls),release:jsonSafeCloneV48Wip11A(r.weapons.vlsReleaseB2),harpoon:harpoonCopyA(r.weapons.harpoon),guns:[...r.weapons.gunMounts].map(([id,g])=>({id,...g.snapshot()})),closeIn:r.weapons.closeIn.map(m=>({id:m.id,type:m.type,ammo:m.ammo,azRad:m._bodyYawV1??0,elRad:m.turretEl??0})),sam:(e?.sam??[]).map(m=>({id:m.id,ownerEntityId:m.ownerEntityId,trackKey:m.ownerTrackKeyD,profileId:m._v1Profile?.id,lifeS:m.life,x:m.x,y:m.y,z:m.z,dead:m.dead,deathReason:m._deathReason,dlAlive:m.dlAlive,sarhAlive:m.sarhAlive,link:weaponLinkB3Snapshot(m)})),ram:(e?.ram??[]).map(m=>({id:m.id,ownerEntityId:m.ownerEntityId,lifeS:m.life,x:m.x,y:m.y,z:m.z,alive:m.alive})),closeInHold:e?.closeInHoldD??null,nativeCiws:e?.context.nativeCiws(),reservations:e?.context.reservations(),shadow:jsonSafeCloneV48Wip11A(e?.shadow.logs??[]),impacts:jsonSafeCloneV48Wip11A(e?.impacts??[])};})};}
function navalOrdnanceReflectorsD(){return physicalShipsB().flatMap(r=>[...(r.weapons.executionD?.sam??[]),...(r.weapons.executionD?.ram??[])].filter(m=>!m.dead&&m.alive!==false).map(m=>({rfId:'NAVAL_ORDNANCE:'+r.entityId+':'+m.id,x:m.x,y:m.y,z:m.z,vx:m.vx,vy:m.vy,vz:m.vz,rcsM2:.06,extentRangeM:2,extentCrossM:.4,extentVerticalM:.3,dopplerSpreadMps:1,_sourceSeed:rfSeedWip13A2('NAVAL_ORDNANCE:'+m.id),_truthObject:m,_physicsKind:'RF_ORDNANCE'})));}
// DIAGNOSTIC_ONLY. Explicit measured-state fixtures/identity commands cannot query
// a target by physical ID. Natural acquisition is verified separately.
function weaponFixtureD(shipId,options={}){
 const r=ENGAGEMENT_RUNTIME.ships.get(shipId);if(!r||r===ACTIVE_SHIP_RUNTIME||r.executionState!=='PHYSICAL_ACTIVE')throw Error('FIXTURE_NONPLAYER_REQUIRED');
 if(options.action==='identity'){const tr=r.combatSystem.trackManager.tracks.get(options.trackId);if(!tr)return {ok:false,reason:'NO_TRACK'};tr._operatorIdentity=normalizeTrackOperatorIdentityA3(options.identity);tr.identity=tr._operatorIdentity;return {ok:true};}
 if(options.action==='track'){
  const id=Number(options.trackId),pos=options.positionM,vel=options.velocityMps??{x:0,y:0,z:0};if(!Number.isInteger(id)||!pos||![pos.x,pos.y,pos.z,vel.x,vel.y,vel.z].every(Number.isFinite))throw Error('FIXTURE_MEASURED_STATE_REQUIRED');
  const P=new Float64Array(36);for(const i of [0,7,14])P[i]=(options.sigmaM??8)**2;for(const i of [21,28,35])P[i]=.3**2;
  const tr={trackId:id,trackNumber:id,x:metersToWorld(pos.x),y:metersToWorld(pos.y),z:pos.z,vx:mpsToWorldSpeed(vel.x),vy:mpsToWorldSpeed(vel.y),vz:vel.z,_kfX:Float64Array.from([pos.x,pos.y,pos.z,vel.x,vel.y,vel.z]),_kfP:P,classification:options.domain==='SURFACE'?'SURFACE':'ASM',domain:options.domain??'AIR',confirmed:true,sensorDetected:true,sensorAge:0,sensorHits:12,ttl:18,lastIndependentHitS:simStepCounter*SIM_FIXED_DT,_lastMeasurementStep:simStepCounter,sensorSource:'SPY1DV_TRACK_REVISIT',trackQuality:.95,fireControlQuality:.95,kinematicQuality:.95,classificationConfidence:.98,identity:'UNKNOWN',_operatorIdentity:'UNKNOWN',engagementAuthority:'WITHHELD',truthUsed:false};
  r.combatSystem.trackManager.tracks.set(id,tr);observerC(r).serial=Math.max(observerC(r).serial,id+1);return {ok:true,trackKey:ownerTrackKeyD(shipId,id)};
 }
 if(options.action==='contact')return navalContactFixtureD(r,options);
 return {ok:false,reason:'FIXTURE_ACTION_REQUIRED'};
}
