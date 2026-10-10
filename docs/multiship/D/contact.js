// PHYSICAL ONLY. Geometry/target identity ends here; firing decisions do not call it.
function navalShipsD(){return physicalShipsB().length?[ACTIVE_SHIP_RUNTIME,...physicalShipsB()]:[];}
function navalGeometryD(r){return r===ACTIVE_SHIP_RUNTIME?geometryForShipProfileA(ACTIVE_SHIP_PROFILE):r.geometry;}
function navalFirstContactD(start,end,{sourceShipId=null,excludeShipId=null,launchCleared=true}={}){
  let best=null;for(const r of navalShipsD()){
    if(r.entityId===excludeShipId||!launchCleared&&r.entityId===sourceShipId||shipSurvivalB(r).snapshot().lost)continue;
    const n=r.navigation,g=navalGeometryD(r),length=g.bow-g.stern,dx=worldToMeters(end.x-n.positionWorld.x),dy=worldToMeters(end.y-n.positionWorld.y);
    if(Math.hypot(dx,dy)>length+Math.hypot(worldToMeters(end.x-start.x),worldToMeters(end.y-start.y)))continue;
    const f=shipBodyFrameB(r),pose=r===ACTIVE_SHIP_RUNTIME?(shipGamePreviousPoseV1??shipSurvivalB(r).snapshot()):(r.weapons.executionD?.previousPose??shipSurvivalB(r).snapshot()),
      previous=createShipBodyFrameV1(pose,{x:worldToMeters(n.previousPositionWorld.x),y:worldToMeters(n.previousPositionWorld.y),z:OWN_ALT_M},n.previousHeadingWorld),
      a=previous.pointToBody({x:worldToMeters(start.x),y:worldToMeters(start.y),z:start.z}),b=f.pointToBody({x:worldToMeters(end.x),y:worldToMeters(end.y),z:end.z}),L=g.layout,
      at=t=>({x:lerp(a.x,b.x,t),y:lerp(a.y,b.y,t),z:lerp(a.z,b.z,t)}),inside=p=>L.contains(p.x,p.y,p.z),steps=Math.min(4096,Math.max(1,Math.ceil(Math.hypot(b.x-a.x,b.y-a.y,b.z-a.z)/.15)));
    let t=null,last=inside(a);for(let i=1;i<=steps;i++){const u=i/steps,v=inside(at(u));if(!last&&v){let lo=(i-1)/steps,hi=u;for(let k=0;k<20;k++){const mid=(lo+hi)*.5;if(inside(at(mid)))hi=mid;else lo=mid;}t=hi;break;}last=v;}
    if(t===null)continue;const point=at(t),normal=L.normal(point),q={shipRuntimeD:r,entity:r,hit:{t,point,normal,crossingRole:'ENTRY'},trace:{coordinateSpace:'OWNER_LOCAL_METRES'}};
    if(!best||t<best.hit.t)best=q;
  }return best;
}
function harpoonTerminalSpecD(){return wip12aProjectileSpec({id:'RGM84D_BLOCK1C_CONTACT_A1',sourceClass:'PUBLIC_WARHEAD_FILL__SIM_TUNED_TERMINAL',caliberM:.343,lengthM:3.84,massKg:HARPOON_PROFILE_A.public.bodyMassKg,penetratorMassKg:123.5,noseShape:'MISSILE_OGIVE',hardness01:.82,shatterResistance01:.45,ductility01:.5,payloadType:'HE',explosiveMassKg:97.5,tntEquivalentFactor:HARPOON_PROFILE_A.sim.explosiveTntFactor,fuzeType:'LEGACY_IMPACT_DELAY',armMode:'IMPACT',minArmTimeS:HARPOON_PROFILE_A.sim.fuzeArmS,minArmDistanceM:HARPOON_PROFILE_A.sim.fuzeArmDistanceM,delayS:HARPOON_PROFILE_A.sim.fuzeDelayS,qualificationProfileId:'ANTI_SHIP_DELAY_8'});}
function ownerTerminalGeometryD(r,bundle){const g=bundle.geometry,owned=q=>q?{...q,...(q.surface?{surface:{...q.surface,id:r.entityId+':'+q.surface.id}}:{})}:q;return {...bundle,geometry:{...g,boundaries:g.boundaries.map(q=>({...q,id:r.entityId+':'+q.id})),eventProviders:g.eventProviders.map(p=>({...p,query:(...args)=>{const rows=p.query(...args);return Array.isArray(rows)?rows.map(owned):owned(rows);}}))}};}
function navalTerminalD(projectile,contact,{weaponKey,spec,armed=true,ageS=0,distanceM=0}={}){
  const r=contact.shipRuntimeD,g=navalGeometryD(r),own=r===ACTIVE_SHIP_RUNTIME,context=own?null:r.weapons.executionD.context,
    eventId='NAVAL_D:'+r.entityId+':'+String(projectile.ownerEntityId??ACTIVE_SHIP_RUNTIME.entityId)+':'+weaponKey+':'+projectile.id,
    seen=own?(r.damage.navalSeenImpactsD??=new Set()):r.weapons.executionD.seenImpacts;
  if(seen.has(eventId))return {accepted:false,duplicate:true,eventId};
  const point=contact.hit.point,p=shipBodyFrameB(r).pointToWorld(point),platform=ownerPointStateD(r,point),v=projectile.velocityMps??{x:worldSpeedToMps(projectile.vx??0),y:worldSpeedToMps(projectile.vy??0),z:projectile.vz??0},
    relative={x:v.x-platform.vxMps,y:v.y-platform.vyMps,z:v.z-platform.vzMps},body=shipBodyFrameB(r).vectorToBody(relative),speed=Math.max(.01,Math.hypot(body.x,body.y,body.z)),direction=wip12aUnit(body),start=wip12aPointAlong(point,direction,-.04),
    base=ownerTerminalGeometryD(r,own?wip12cShipMacroGeometry(start,direction):context.terminalGeometry(start,direction)),normal=wip12aVec(contact.hit.normal,wip12aScale(direction,-1)),
    entry=wip12aBoundarySurface(point.z<0?'SHELL_BOTTOM_BILGE':point.z<2?'SHELL_WATERLINE':point.z>14?'SUPERSTRUCTURE_UPPER':'SHELL_UPPER',{id:r.entityId+':ENTRY:'+eventId,targetId:'HULL_SKIN',point,normal,exterior:true,terminalExit:false,bounds:{min:{x:point.x-2,y:point.y-2,z:point.z-2},max:{x:point.x+2,y:point.y+2,z:point.z+2}}}),
    geometry={...base.geometry,boundaries:[entry,...base.geometry.boundaries]},state=wip12aMakeProjectileState(spec,{position:start,direction,bodyAxis:direction,speedMps:speed,massKg:projectile.massKg??spec.body.massKg,flightState:{launchCleared:armed,timeS:ageS,distanceM},fuze:{safetyArmed:armed,armed,functioning:armed,dud:!armed}}),
    terminal=wip12aTraceTerminalProjectile(spec,state,geometry,{impactEventId:eventId,sourceProjectileId:weaponKey+':'+projectile.id,targetEntityId:r.entityId,maxPathM:base.maxPathM});
  wip12cResolveTerminalCascade(terminal,spec,{geometryForBody:plan=>ownerTerminalGeometryD(r,own?wip12cShipMacroGeometry(plan.state.position,plan.state.direction,plan.index):context.terminalGeometry(plan.state.position,plan.state.direction,plan.index)),mergeDamage:true,enableReentry:false,applicationAuthority:'OWNER_PACKET_SINGLE_APPLICATION_D'});
  const applied=own?wip12aApplyDamagePacket(terminal.damagePacket,{commit:true,emitVisualEvent:false}):context.applyDamage(terminal.damagePacket,{commit:true,emitVisualEvent:false});
  if(applied.accepted){seen.add(eventId);while(seen.size>512)seen.delete(seen.values().next().value);const box=g.boxes.find(b=>Math.abs(point.x-b.oX)<=b.hL+.2&&Math.abs(point.y-(b.oY??0))<=b.hW+.2&&point.z>=b.zMin-.2&&point.z<=b.zMax+.2),part=box?.name??applied.parts.find(p=>g.boxes.some(b=>b.name===p.name))?.name;const hit={id:eventId,x:point.x,y:point.y,z:point.z,label:weaponKey,impactPoint:{...point},impactNormal:[normal.x,normal.y,normal.z],impactPart:part,part:part??'HULL',dmg:applied.parts.reduce((s,q)=>s+q.dmg,0),outerPerforated:terminal.boundaryResults[0]?.surfaceDamage?.perforated??false,blastParts:applied.parts,blastTraceSummary:applied.blastTrace,physicalPenetrationM:terminal.pathLengthM,penetrationLine:{x0:start.x,y0:start.y,z0:start.z,x1:terminal.finalState.position.x,y1:terminal.finalState.position.y,z1:terminal.finalState.position.z},time:performance.now()};
    const history=own?shipHitHistory:r.hitHistory;history.push(hit);if(history.length>64)history.splice(0,history.length-64);if(own)shipLastHit=hit;
    const impulse={x:relative.x*(projectile.massKg??spec.body.massKg),y:relative.y*(projectile.massKg??spec.body.massKg),z:relative.z*(projectile.massKg??spec.body.massKg)};
    getShipDynamicsV15(r).impactImpulse({pointLocal:point,impulseLocal:shipBodyFrameB(r).vectorToBody(impulse),source:weaponKey});
    const row={eventId,sourceShipId:projectile.ownerEntityId??ACTIVE_SHIP_RUNTIME.entityId,targetShipId:r.entityId,weaponKey,projectileId:projectile.id,step:simStepCounter,speedMps:speed,armed,terminationReason:terminal.terminationReason,accepted:true,explosiveMassKg:terminal.damagePacket.blast.reduce((s,q)=>s+q.explosiveMassKg,0)};
    if(!own){r.weapons.executionD.impacts.push(row);if(r.weapons.executionD.impacts.length>64)r.weapons.executionD.impacts.shift();}
    wip12bRecordTerminalEvent({impactEventId:eventId,weaponKey,sourceProjectileId:String(projectile.id),targetEntityId:r.entityId,coordinateSpace:'SHIP_LOCAL_METRES',referenceFrame:{type:'SHIP_LOCAL_METRES',targetEntityId:r.entityId},trace:terminal,damagePacket:terminal.damagePacket,effectResult:'HIT',fuzePath:armed?'CONTACT_DIRECT_ACTION':'DUD',applicationAuthority:'OWNER_PACKET_SINGLE_APPLICATION_D',damageAppliedBy:r.entityId,integrationMode:'LIVE_NAVAL_CONTACT_D'});
    wip173PushVisualEvent('SHIP_WARHEAD_DETONATION',{coordSpace:'WORLD',x:metersToWorld(p.x),y:metersToWorld(p.y),z:p.z,sourceId:projectile.id,targetEntityId:r.entityId,weaponType:weaponKey,explosiveMassKg:row.explosiveMassKg,impactSpeedMps:speed});
  }
  projectile.impact={eventId,targetEntityId:r.entityId,speedMps:speed,armed,accepted:applied.accepted};
  return {eventId,accepted:applied.accepted,duplicate:!applied.accepted,terminal};
}
function navalHarpoonContactD(m,contact){navalTerminalD(m,contact,{weaponKey:'HARPOON',spec:harpoonTerminalSpecD(),armed:m.fuzeArmed,ageS:m.ageS,distanceM:m.pathM});harpoonFinishA(m,'NAVAL_CONTACT');}
function navalGunContactD(p,contact){const q=navalTerminalD(p,contact,{weaponKey:'MK45',spec:WIP12A_DIAGNOSTIC_PROJECTILES[p.terminalProjectileSpecId],armed:true,ageS:p.ageS,distanceM:p.flightDistanceM}),h=q.terminal?.postExitHandoff;if(h){const f=shipBodyFrameB(contact.shipRuntimeD),at=f.pointToWorld(h.position),dir=f.vectorToWorld(h.direction),v=ownerPointStateD(contact.shipRuntimeD,h.position);p.positionM={...at};p.previousPositionM={...at};p.velocityMps={x:dir.x*h.speedMps+v.vxMps,y:dir.y*h.speedMps+v.vyMps,z:dir.z*h.speedMps+v.vzMps};p.massKg=h.massKg;p.postExit={targetEntityId:contact.shipRuntimeD.entityId,fuze:jsonSafeCloneV48Wip11A(h.fuze),liveFuze:!!h.liveFuze,remainingExplosiveKg:h.remainingExplosiveKg};p.alive=true;}else{p.alive=false;p.retiredReason='NAVAL_CONTACT';}return p.impact;}
function navalMissileContactD(m,prev){
  if(m._navalContactD||m.proxDetonated||m.contactDetonatedWip13C8||m.dead&&m._deathReason!=='SEA_IMPACT')return null;
  const key=m.isRAM?'RAM':m.isESSM?'ESSM':m.isSM6?'SM6':m.isSM2ER?'SM2ER':'SM2',entry=SURFACE_MISSILE_TERMINAL_ORDNANCE_WIP15C[key]??WIP12B_LIVE_ORDNANCE[key];if(!entry)return null;
  const contact=navalFirstContactD(prev,{x:m.x,y:m.y,z:m.z},{sourceShipId:m.ownerEntityId??ACTIVE_SHIP_RUNTIME.entityId,launchCleared:!m.vlsPhase&&(m.life??0)>2});if(!contact)return null;
  const seaT=prev.z>0&&m.z<0?prev.z/(prev.z-m.z):Infinity;if(contact.hit.t>seaT)return null;
  return navalMissileAtContactD(m,contact);
}
function navalMissileAtContactD(m,contact){
  const key=m.isRAM?'RAM':m.isESSM?'ESSM':m.isSM6?'SM6':m.isSM2ER?'SM2ER':'SM2',entry=SURFACE_MISSILE_TERMINAL_ORDNANCE_WIP15C[key]??WIP12B_LIVE_ORDNANCE[key];
  const q=navalTerminalD(m,contact,{weaponKey:key,spec:entry.spec,armed:!m.vlsPhase&&(m.life??0)>2,ageS:m.life,distanceM:Math.max(0,m.life*worldSpeedToMps(m.speed??mpsToWorldSpeed(m.speedMps??0)))});
  m._navalContactD=q.eventId;m.dead=true;if(m.isRAM)m.alive=false;m._deathReason='NAVAL_CONTACT';return q;
}
function navalContactFixtureD(r,o){
 const x=Number(o.xM??12),z=Number(o.zM??2),side=o.side==='PORT'?-1:1,g=navalGeometryD(r),half=g.halfBeam(x,z),f=shipBodyFrameB(r),a=f.pointToWorld({x,y:side*(half+25),z}),b=f.pointToWorld({x,y:-side*(half+25),z}),key=o.weapon??'HARPOON',spec=key==='HARPOON'?harpoonTerminalSpecD():WIP12B_LIVE_ORDNANCE[key]?.spec;
 if(!spec||half<=0)throw Error('CONTACT_FIXTURE_GEOMETRY');const dir=wip12aUnit(wip12aSub(b,a)),p={id:'DIAG_'+(++ENGAGEMENT_RUNTIME.world.navalWeaponSerialD),ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,velocityMps:{x:dir.x*600,y:dir.y*600,z:dir.z*600},massKg:spec.body.massKg};
 const c=navalFirstContactD({x:metersToWorld(a.x),y:metersToWorld(a.y),z:a.z},{x:metersToWorld(b.x),y:metersToWorld(b.y),z:b.z},{excludeShipId:ACTIVE_SHIP_RUNTIME.entityId});if(c?.shipRuntimeD!==r)return {ok:false,reason:'NO_CONTACT'};
 const q=navalTerminalD(p,c,{weaponKey:key,spec,armed:o.armed!==false,ageS:20,distanceM:12000}),again=navalTerminalD(p,c,{weaponKey:key,spec,armed:o.armed!==false,ageS:20,distanceM:12000});
 return {ok:q.accepted,duplicateRejected:again.duplicate,targetShipId:r.entityId,eventId:q.eventId,terminationReason:q.terminal?.terminationReason,impacts:r.weapons.executionD.impacts,terminal:q.terminal};
}
