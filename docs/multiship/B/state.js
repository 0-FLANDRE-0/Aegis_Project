// Canonical operational restore; combat, fire timelines, fatigue and body rates
// reset, matching the existing player operational-save contract.
function ownerControlAccumulatorB(){return damageControlAccumulatorV1;}
function ownerInteriorAccumulatorB(){return interiorTopologyAccumulatorV48Wip06;}
function setOwnerControlAccumulatorsB(dc,interior){damageControlAccumulatorV1=dc;interiorTopologyAccumulatorV48Wip06=interior;}
function physicalShipCommandB(entityId,command){
  const r=ENGAGEMENT_RUNTIME.ships.get(entityId),p=r&&resolveShipProfile(r.profileId);
  if(!r||r===ACTIVE_SHIP_RUNTIME||r.executionState!=='PHYSICAL_ACTIVE')return {ok:false,reason:'PHYSICAL_NONPLAYER_REQUIRED'};
  if(!command||Object.keys(command).some(k=>!['targetSpeedKt','targetRudder','abandon'].includes(k)))return {ok:false,reason:'PHYSICAL_COMMAND_FIELDS'};
  if(command.targetSpeedKt!=null&&(!Number.isFinite(command.targetSpeedKt)||command.targetSpeedKt< -15||command.targetSpeedKt>shipAheadLimitB(p)))return {ok:false,reason:'PHYSICAL_COMMAND_SPEED'};
  if(command.targetRudder!=null&&(!Number.isFinite(command.targetRudder)||Math.abs(command.targetRudder)>35))return {ok:false,reason:'PHYSICAL_COMMAND_RUDDER'};
  if(command.abandon!=null&&typeof command.abandon!=='boolean')return {ok:false,reason:'PHYSICAL_COMMAND_ABANDON'};
  if(command.targetSpeedKt!=null)r.navigation.targetSpeedKt=command.targetSpeedKt;
  if(command.targetRudder!=null)r.navigation.targetRudder=command.targetRudder;
  if(command.abandon)r.crew.abandon('PHYSICAL_DIAGNOSTIC');return {ok:true};
}
function exportPhysicalFleetB(){const ships=physicalShipsB();return {schema:MULTISHIP_PHYSICAL_SCHEMA_B,deploymentState:ships.length?'ACTIVE':deploymentConfigA().enemyProfileId?'PENDING':'NONE',ships:ships.map(r=>{
  const mass=r.mass.snapshot({detail:true}),flood=r.flooding;
  return {entityId:r.entityId,profileId:r.profileId,profileRevision:resolveShipProfile(r.profileId).revision,clock:{...r.clock},survival:r.survival.snapshot(),
    ship:{navigation:jsonSafeCloneV48Wip11A(r.navigation),shipHP:r.health.shipHP,
      liquidLoads:Object.fromEntries(mass.nodes.filter(n=>n.category==='LIQUID_LOAD').map(n=>[n.id,n.massKg])),
      damage:{moduleDamage:Object.fromEntries(flood.damageKeys().map(n=>[n,flood.readDamage(n)])),flooding:jsonSafeCloneV48Wip11A(flood.snapshot())},crew:r.crew.snapshot(),rescue:r.rescue.snapshot()}};
})};}
function physicalValidationContextB(r){const p=resolveShipProfile(r.profileId),f=r.flooding,c=r.crew.snapshot();return {profile:p,flood:f,liquidIds:new Set(r.mass.loadIds()),
  damageLabels:new Set([...f.targets.values()].map(q=>q.label)),floodCells:new Map(f.cells.map(q=>[q.id,q])),doorIds:new Set(f.connections.map(q=>q.id)),pumpIds:new Set(f.pumps.map(q=>q.id)),
  crewExpectedCount:p.crew.roster,crewGroups:new Map(c.groups.map(q=>[Number(q.id),q])),crewSpaceIds:new Set(r.interior.snapshot().spaces.map(q=>q.id))};}
function validatePhysicalFleetB(src,_ctx,errors){
  const fleet=src.fleet,err=x=>errors.push('FLEET_'+x);
  if(!fleet||fleet.schema!==MULTISHIP_PHYSICAL_SCHEMA_B||!['NONE','PENDING','ACTIVE'].includes(fleet.deploymentState)||!Array.isArray(fleet.ships)||fleet.ships.length>1){err('SCHEMA');return;}
  if(fleet.deploymentState==='ACTIVE'&&fleet.ships.length!==1){err('MISSING_SHIP');return;}
  if(fleet.deploymentState!=='ACTIVE'&&fleet.ships.length){err('INACTIVE_SHIP');return;}
  if((fleet.deploymentState==='NONE')!==!src.deployment?.enemyProfileId){err('DEPLOYMENT_STATE');return;}
  if(fleet.ships.length&&!src.deployment?.enemyProfileId){err('DEPLOYMENT');return;}
  for(const q of fleet.ships){
    if(!q||q.entityId!=='SHIP_SCENARIO_ENEMY_A'||q.profileId!==src.deployment?.enemyProfileId||q.profileRevision!==SHIP_PROFILE_REGISTRY[q.profileId]?.revision){err('OWNER_PROFILE');continue;}
    const r=createPreparedShipRuntimeA(SHIP_PROFILE_REGISTRY[q.profileId],{entityId:q.entityId,role:'ENEMY'}),ctx=physicalValidationContextB(r),envelope={shipId:q.entityId,ship:q.ship};
    for(const validate of [validateOperationalNavigationV48Wip11B,validateOperationalLoadsV48Wip11B,validateOperationalDamageFloodingV48Wip11B,validateOperationalCrewV48Wip11B,validateOperationalRescueK])validate(envelope,ctx,errors);
    const n=q.ship?.navigation;if(n){if(n.trail?.length>r.navigation.maxTrail)err('TRAIL_BOUND');
      const numeric=['heading','speed','targetSpeedKt','rudder','targetRudder','turnRate','vx','vy','swayMps','thrustN','accelerationMps2','shaftRpm','propPitch','shaftRpmCap','_trailTimer','telegraph'];
      for(const k of numeric)if(k in n&&(!Number.isFinite(n[k])||Math.abs(n[k])>1e12))err('NAV_'+k);
      if(Math.abs(n.targetSpeedKt)>shipAheadLimitB(r.context.profile)||Math.abs(n.rudder)>35||Math.abs(n.targetRudder)>35||typeof n.c17Ownship!=='boolean')err('NAV_RANGE');
    }
    const p=q.survival;
    if(!p||!['NORMAL','DAMAGED','FLOODING','CRITICAL','CAPSIZING','CAPSIZED','SINKING','LOST'].includes(p.state)||!Array.isArray(p.events)||p.events.length>32){err('SURVIVAL');continue;}
    for(const k of ['timeS','phaseS','capTimer','sinkTimer','waterM3','imbalance'])if(!Number.isFinite(p[k])||p[k]<0)err('SURVIVAL_'+k);
    for(const k of ['heelRad','trimRad','draftM'])if(!Number.isFinite(p[k])||!Number.isFinite(p.target?.[k])||Math.abs(p[k])>r.context.profile.damage.survival.lostDraftM+2||Math.abs(p.target?.[k])>r.context.profile.damage.survival.lostDraftM+2)err('POSE_'+k);
    if(!q.clock||!Number.isInteger(q.clock.tick)||q.clock.tick<0||!Number.isFinite(q.clock.timeS)||Math.abs(q.clock.timeS-q.clock.tick*SIM_FIXED_DT)>1e-7)err('CLOCK');
  }
}
function restorePreparedPhysicalFleetB(prepared,fleet){
  const r=prepared.enemy,q=fleet.ships[0];if(!r||!q)return;const src=q.ship;
  // Copy declared navigation values only: a save cannot attach foreign state.
  for(const k of ['positionWorld','previousPositionWorld','trail'])r.navigation[k]=jsonSafeCloneV48Wip11A(src.navigation[k]);
  for(const k of ['previousHeadingWorld','worldPoseDtS','heading','speed','targetSpeedKt','rudder','targetRudder','turnRate','vx','vy','manualSpeedV15','manualRudderV15','manualSpeed','manualRudder','c17Ownship','swayMps','thrustN','accelerationMps2','shaftRpm','propPitch','shaftRpmCap','telegraph','_trailTimer'])if(k in src.navigation)r.navigation[k]=src.navigation[k];
  r.clock={...q.clock};r.health.shipHP=src.shipHP;const f=r.flooding,fs=src.damage.flooding;
  for(const [name,d]of Object.entries(src.damage.moduleDamage))f.setDamage(name,d);
  for(const o of fs.openings){f.addOpening({id:o.id,a:o.a,b:o.b,x:o.x,y:o.y,z:o.z,normal:o.normal,kind:o.kind,impactRole:o.impactRole,damage:o.work,areaM2:o.areaM2,perforated:o.areaM2>0});if(o.seal01)f.seal(o.id,o.seal01);}
  for(const c of fs.cells)f.setWater(c.id,c.waterM3);for(const d of fs.doors)f.setDoor(d.id,d.open);for(const p of fs.pumps)f.setPump(p.id,p.enabled);
  r.survival.restorePhysical(q.survival);f.setAttitude(q.survival);r.crew.restoreOperational(src.crew);r.rescue.restore(src.rescue);
  for(const [id,kg]of Object.entries(src.liquidLoads))r.mass.setLoadMassKg(id,kg);r.mass.syncCrew(r.crew.snapshot().groups,0,true);r.dynamics.setLoading({...f.summary(),...shipMassLossB(r)});r.dynamics.restoreOperationalPose(q.survival);
}
function navalFootprintB(r){const p=resolveShipProfile(r.profileId),n=r.navigation,c=Math.cos(n.heading),s=Math.sin(n.heading),rows=p.geometry.hullStations;
  const points=[...rows.map(q=>[q[0],q[1]]),...rows.toReversed().map(q=>[q[0],-q[1]])];return points.map(([x,y])=>({x:worldToMeters(n.positionWorld.x)+x*c-y*s,y:worldToMeters(n.positionWorld.y)+x*s+y*c}));}
function navalOverlapB(a,b){let best=null;for(const points of [a,b])for(let i=0;i<points.length;i++){
  const p=points[i],q=points[(i+1)%points.length],len=Math.hypot(q.x-p.x,q.y-p.y);if(len<1e-8)continue;const nx=-(q.y-p.y)/len,ny=(q.x-p.x)/len;
  const av=a.map(p=>p.x*nx+p.y*ny),bv=b.map(p=>p.x*nx+p.y*ny),overlap=Math.min(Math.max(...av),Math.max(...bv))-Math.max(Math.min(...av),Math.min(...bv));
  if(overlap<=0)return null;if(!best||overlap<best.overlap)best={nx,ny,overlap};
}return best;}
function resolveNavalContactsB(dt){
  const foreign=physicalShipsB();if(!foreign.length)return;const all=[ACTIVE_SHIP_RUNTIME,...foreign];
  for(let i=0;i<all.length;i++)for(let j=i+1;j<all.length;j++){
    const a=all[i],b=all[j],an=a.navigation,bn=b.navigation,dx=worldToMeters(bn.positionWorld.x-an.positionWorld.x),dy=worldToMeters(bn.positionWorld.y-an.positionWorld.y);
    if(Math.hypot(dx,dy)>220||shipSurvivalB(a).snapshot().lost||shipSurvivalB(b).snapshot().lost)continue;
    const hit=navalOverlapB(navalFootprintB(a),navalFootprintB(b));if(!hit)continue;let {nx,ny}=hit;if(nx*dx+ny*dy<0){nx=-nx;ny=-ny;}
    const ma=getShipMassLedgerV32(a).snapshot().massKg,mb=getShipMassLedgerV32(b).snapshot().massKg,reduced=ma*mb/(ma+mb),closing=Math.max(0,worldToMeters((an.vx-bn.vx)*nx+(an.vy-bn.vy)*ny)),impulse=reduced*closing;
    for(const [r,sign,m]of [[a,-1,ma],[b,1,mb]]){
      const n=r.navigation,c=Math.cos(n.heading),s=Math.sin(n.heading),push=(hit.overlap+.01)*(r===a?mb:ma)/(ma+mb);
      n.positionWorld.x+=metersToWorld(sign*nx*push);n.positionWorld.y+=metersToWorld(sign*ny*push);
      getShipDynamicsV15(r).impactImpulse({pointLocal:{x:0,y:0,z:0},impulseLocal:{x:sign*impulse*(nx*c+ny*s),y:sign*impulse*(-nx*s+ny*c),z:0},source:'NAVAL_HULL_CONTACT'});
      n.vx+=mpsToWorldSpeed(sign*impulse*nx/m);n.vy+=mpsToWorldSpeed(sign*impulse*ny/m);
      const event={kind:'NAVAL_HULL_CONTACT',tick:simStepCounter,otherShipId:r===a?b.entityId:a.entityId,closingMps:closing,energyJ:.5*reduced*closing*closing};
      if(r!==ACTIVE_SHIP_RUNTIME)r.physicalEvents.push(event);
      // Damage uses the same flooding/control/crew impact entry point, with
      // deliberately conservative, declared collision tuning; no explosive blast.
      if(event.energyJ>5e5){const geo=r===ACTIVE_SHIP_RUNTIME?geometryForShipProfileA(ACTIVE_SHIP_PROFILE):r.geometry,ux=-sign*(nx*c+ny*s),uy=-sign*(-nx*s+ny*c);let lo=0,hi=geo.bow-geo.stern;
        for(let k=0;k<24;k++){const mid=(lo+hi)/2;if(geo.contains(ux*mid,uy*mid,0))lo=mid;else hi=mid;}
        const point={x:ux*lo,y:uy*lo,z:0},inside={x:ux*Math.max(0,lo-.5),y:uy*Math.max(0,lo-.5),z:0},box=geo.boxes.find(q=>q.system==='HULL_SKIN'&&Math.abs(point.x-q.oX)<=q.hL+.1&&Math.abs(point.y-(q.oY||0))<=q.hW+.1);
        if(r!==ACTIVE_SHIP_RUNTIME)Object.assign(event,{pointLocal:point,stopLocal:inside,halfBeam:geo.halfBeam(point.x,point.z),contains:geo.contains(point.x,point.y,point.z)});
        damageFloodImpactV1('CONTACT:'+simStepCounter+':'+r.entityId,point,inside,box?[{name:box.name,dmg:Math.min(20,event.energyJ/2e6)}]:[],false,true,{ignitionAllowed:false,outerPerforated:true,entryOpeningAreaM2:Math.min(.06,event.energyJ/1e9),exitOpeningAreaM2:0},r);
      }
    }
  }
}

function shipTerrainContactB(r,dx,dy){
  if(BATTLESPACE_DIAG_BYPASS||!terrainIslands.length)return null;const points=navalFootprintB(r).map(p=>({x:metersToWorld(p.x)+dx,y:metersToWorld(p.y)+dy})),n=r.navigation,cx=n.positionWorld.x+dx,cy=n.positionWorld.y+dy,rad=metersToWorld((r.geometry.bow-r.geometry.stern)*.6);
  for(const island of terrainIslands){if(Math.hypot(cx-island.cx,cy-island.cy)>island.boundRadiusWorld+rad)continue;if(pointInTerrainPolygon(cx,cy,island.points)||points.some(p=>pointInTerrainPolygon(p.x,p.y,island.points)||distanceToTerrainEdge(p.x,p.y,island)<metersToWorld(.5))||island.points.some(p=>pointInTerrainPolygon(p.x,p.y,points)))return island;}return null;
}
