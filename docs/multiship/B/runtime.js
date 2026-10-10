// Phase 3: authoritative physical ships. Observations and combat remain deferred.
const MULTISHIP_PHYSICAL_SCHEMA_B='AEGIS_NAVAL_PHYSICAL_FLEET_B_1';
const MULTISHIP_PHYSICAL_TUNING_B=Object.freeze({aheadM:450,starboardM:350,initialSpeedKt:8,contactRestitution:0,contactDamageBasis:'SIM_TUNED_CONTACT_ENERGY_NOT_WEAPON_BLAST'});
function shipAheadLimitB(p){return p.id==='DDG_119_LATE_FLIGHT_IIA'?31:p.navigation?.maxAheadKt??C17_MAX_KT;}
function shipSurvivalB(r=ACTIVE_SHIP_RUNTIME){return r===ACTIVE_SHIP_RUNTIME?floodAttitudePreviewV1:r.survival;}
function shipSystemDamageB(r,system,aggregate='MAX'){
  if(r===ACTIVE_SHIP_RUNTIME)return getShipSystemDamage(system,aggregate);
  const names=[...new Set(r.geometry.boxes.filter(b=>b.system===system).map(b=>b.name))],v=names.map(n=>r.flooding.readDamage(n));
  return !v.length?0:aggregate==='AVG'?v.reduce((a,b)=>a+b,0)/v.length:aggregate==='SUM'?v.reduce((a,b)=>a+b,0):Math.max(...v);
}
function shipMassLossB(r){
  if(r===ACTIVE_SHIP_RUNTIME)return syncShipMassLossV16();
  const mast=shipSystemDamageB(r,'MAST')>=80,key=r.hitHistory.length+':'+mast;
  if(r.massLossKey!==key){r.damage.massLoss.update(createShipDamageVisualStateV1({cells:[],openings:[]},{cells:[]},r.hitHistory,r.geometry.boxes,{terminalEvents:[]}).scars,mast);r.massLossKey=key;}
  return r.damage.massLoss.snapshot();
}
function shipBodyFrameB(r){return r===ACTIVE_SHIP_RUNTIME?shipGameFrameV1():createShipBodyFrameV1(r.survival.snapshot(),{x:worldToMeters(r.navigation.positionWorld.x),y:worldToMeters(r.navigation.positionWorld.y),z:OWN_ALT_M},r.navigation.heading);}
function preparePhysicalShipB(r){
  const p=resolveShipProfile(r.profileId);r.geometry=geometryForShipProfileA(p);r.hitHistory=[];r.physicalEvents=[];r.physicalAccumulators={damageControl:0,interior:0};r.modelRoots={world:null};
  r.survival=createShipSurvivalV1({config:p.damage.survival,dynamics:()=>r.dynamics,resetDynamics:()=>r.dynamics.reset()});
  const nav=r.navigation;nav.c17Ownship=true;nav.targetSpeedKt=MULTISHIP_PHYSICAL_TUNING_B.initialSpeedKt;nav.speed=nav.targetSpeedKt*.514444;nav.heading=shipNav.heading;nav.previousHeadingWorld=nav.heading;
  const c=Math.cos(nav.heading),s=Math.sin(nav.heading),origin=shipNav.positionWorld;
  // Deterministic open-water placement: no random samples or observer truth.
  let placed=false;for(let ring=0;ring<12&&!placed;ring++)for(const side of [1,-1]){
    const x=MULTISHIP_PHYSICAL_TUNING_B.aheadM+ring*200,y=side*(MULTISHIP_PHYSICAL_TUNING_B.starboardM+ring*200);
    Object.assign(nav.positionWorld,{x:origin.x+metersToWorld(x*c-y*s),y:origin.y+metersToWorld(x*s+y*c)});
    placed=!shipTerrainCollisionAhead(0,0,r);if(placed)break;
  }
  if(!placed)throw Error('NAVAL_DEPLOYMENT_NO_OPEN_WATER');
  nav.previousPositionWorld={...nav.positionWorld};nav.vx=mpsToWorldSpeed(nav.speed*c);nav.vy=mpsToWorldSpeed(nav.speed*s);
  r.environment.waveFlood=createWaveFloodEnvironmentV48Wip05({useCommonMaritime:true,position:()=>({x:worldToMeters(nav.positionWorld.x),y:worldToMeters(nav.positionWorld.y)})});
  // Detached preflight keeps raft entities private until activation.
  r.raftEntities=[];r.rescue=createShipRescueK({ownerEntityId:r.entityId,roster:p.crew.roster,entities:r.raftEntities,
    launchPose:(i,n)=>rescueLaunchPoseK(i,n,nav,p,r.geometry.layout),environment:maritimeEnvironmentSnapshotWip13A3,seaLevel:maritimeSeaLevelAtSimulationMetersWip13A3,avoidHull:q=>rescueAvoidHullK(q,r)});
  claimShipMutableRootA(r,'survival',r.survival);claimShipMutableRootA(r,'physicalAccumulators',r.physicalAccumulators);return r;
}
function activatePhysicalShipB(r){
  if(!r.survival)preparePhysicalShipB(r);r.executionState=r.lifecycleState='PHYSICAL_ACTIVE';
  const saved=r.rescue.snapshot(),p=resolveShipProfile(r.profileId);r.rescue=createShipRescueK({ownerEntityId:r.entityId,roster:p.crew.roster,entities:ENGAGEMENT_RUNTIME.world.entities.lifeRafts,launchPose:(i,n)=>rescueLaunchPoseK(i,n,r.navigation,p,r.geometry.layout),environment:maritimeEnvironmentSnapshotWip13A3,seaLevel:maritimeSeaLevelAtSimulationMetersWip13A3,avoidHull:q=>rescueAvoidHullK(q,r)});r.rescue.restore(saved);
  ENGAGEMENT_RUNTIME.world.entities.navalShips??=new Map();ENGAGEMENT_RUNTIME.world.entities.navalShips.set(r.entityId,r);
}
function retirePhysicalShipB(r){r.rescue?.reset?.();ENGAGEMENT_RUNTIME.world.entities.navalShips?.delete(r.entityId);r.executionState='DESTROYED';}
function physicalShipsB(){return [...ENGAGEMENT_RUNTIME.ships.values()].filter(r=>r!==ACTIVE_SHIP_RUNTIME&&r.executionState==='PHYSICAL_ACTIVE');}
function advancePhysicalShipB(r,dt){
  const n=r.navigation;n.previousPositionWorld={...n.positionWorld};n.worldPoseDtS=dt;
  const dx=n.vx*dt,dy=n.vy*dt,land=shipTerrainCollisionAhead(dx,dy,r);
  if(land){r.dynamics.haltHorizontalContact();n.vx=n.vy=n.targetSpeedKt=0;r.physicalEvents.push({kind:'TERRAIN_CONTACT',tick:simStepCounter,islandId:land.id});}
  else {n.positionWorld.x+=dx;n.positionWorld.y+=dy;}
  r.rescue.step(dt,r.crew.snapshot());r.clock.tick++;r.clock.timeS=r.clock.tick*SIM_FIXED_DT;
  if(r.physicalEvents.length>32)r.physicalEvents.splice(0,r.physicalEvents.length-32);
}
function physicalDamageImpactB(r,event){
  const {id,start,stop,parts=[],meta={}}=event;
  return damageFloodImpactV1(id,start,stop,parts,false,true,meta,r);
}
function fleetPhysicalSnapshotB(){return {schema:MULTISHIP_PHYSICAL_SCHEMA_B,simulated:1+physicalShipsB().length,
  worldUpdatesPerTick:1,phase:'PHYSICS_AND_PRESENTATION',ships:physicalShipsB().map(r=>({entityId:r.entityId,profileId:r.profileId,profileRevision:resolveShipProfile(r.profileId).revision,
    navigation:jsonSafeCloneV48Wip11A(r.navigation),clock:{...r.clock},health:{...r.health},survival:r.survival.snapshot(),flood:r.flooding.summary(),control:r.damage.control.snapshot().summary,
    crew:{total:r.crew.snapshot().total,fit:r.crew.snapshot().fit,injured:r.crew.snapshot().injured,dead:r.crew.snapshot().dead,evacuated:r.crew.snapshot().evacuated,mode:r.crew.snapshot().mode},mass:r.mass.snapshot(),dynamics:r.dynamics.snapshot(),wave:r.environment.waveFlood.snapshot(),rescue:r.rescue.snapshot(),events:[...r.physicalEvents]})),
  deferred:['perObserverMeasurements','bidirectionalWeaponRouting','receiverSpecificEW','enemyAI']};}
function physicalProbeB(entityId,options={}){
  const r=ENGAGEMENT_RUNTIME.ships.get(entityId);if(!r||r===ACTIVE_SHIP_RUNTIME||r.executionState!=='PHYSICAL_ACTIVE')throw Error('PHYSICAL_NONPLAYER_REQUIRED');
  const x=Number(options.xM??12),z=Number(options.zM??-3.5),b=r.geometry.halfBeam(x,z),side=options.side==='PORT'?-1:1;
  if(!(b>0))throw Error('PROBE_OUTSIDE_HULL');const start={x,y:side*b,z},stop={x,y:-side*(b+.5),z},box=r.geometry.boxes.find(q=>q.system==='HULL_SKIN'&&x>=q.oX-q.hL&&x<=q.oX+q.hL&&z>=q.zMin&&z<=q.zMax);
  const id=r.entityId+'.PROBE.'+r.hitHistory.length,parts=box?[{name:box.name,dmg:20}]:[];
  const accepted=physicalDamageImpactB(r,{id,start,stop,parts,meta:{ignitionAllowed:false,outerPerforated:true,throughHull:true,entryOpeningAreaM2:.06,exitOpeningAreaM2:.04,explosiveMassKg:0}});
  if(accepted){r.hitHistory.push({id,impactPoint:start,impactPart:box?.name,impactNormal:[0,side,0],outerPerforated:true,physicalPenetrationM:2,penetrationLine:{x0:x,y0:start.y,z0:z,x1:x,y1:stop.y,z1:z}});r.dynamics.impactImpulse({pointLocal:start,impulseLocal:{x:0,y:-side*80000,z:0},source:'CONTROLLED_PHYSICAL_PROBE'});}
  return {accepted,owner:r.entityId,flood:r.flooding.snapshot(),pose:r.survival.snapshot()};
}
window.__MULTISHIP_PHYSICS_B__=Object.freeze({snapshot:fleetPhysicalSnapshotB,probe:physicalProbeB});
