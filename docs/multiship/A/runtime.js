// Canonical per-ship state. Legacy execution remains attached to the player.
const MULTISHIP_MUTABLE_OWNERS_A=new WeakMap();
function claimShipMutableRootA(runtime,kind,value){
  const pending=[value],seen=new Set();
  while(pending.length){const q=pending.pop();if(!q||typeof q!=='object'||Object.isFrozen(q)||seen.has(q))continue;seen.add(q);
    const owner=MULTISHIP_MUTABLE_OWNERS_A.get(q);if(owner&&owner!==runtime)throw Error('SHIP_MUTABLE_STATE_ALREADY_OWNED:'+kind);
    // Map/Set containers are owned; their observations can reference shared physical fixtures.
    if(!(q instanceof Map)&&!(q instanceof Set))pending.push(...Object.values(q));
  }
  for(const q of seen)MULTISHIP_MUTABLE_OWNERS_A.set(q,runtime);
}
function attachShipContextA(runtime,role){
  if(role==='PLAYER'&&runtime!==ACTIVE_SHIP_RUNTIME)throw Error('ACTIVE_PLAYER_CONTEXT_RESERVED');
  const profile=resolveShipProfile(runtime.profileId);
  runtime.role=role;runtime.executionState=role==='PLAYER'?'PLAYER_LEGACY_BOUND':'STATE_BOUND_INACTIVE';
  runtime.clock=role==='PLAYER'?Object.freeze({get tick(){return simStepCounter;},get timeS(){return simStepCounter*SIM_FIXED_DT;}}):runtime.clock??{tick:0,timeS:0};
  if(role==='PLAYER')runtime.health={get shipHP(){return shipHP;}};
  runtime.context=Object.freeze({schema:'AEGIS_SHIP_CONTEXT_MULTI_SHIP_A_1',entityId:runtime.entityId,
    get profile(){return profile;},get navigation(){return runtime.navigation;},
    get sensors(){return runtime.combatSystem.sensors;},get observations(){return runtime.combatSystem.trackManager;},
    get weapons(){return runtime.weapons;},get ew(){return runtime.ew;},get damage(){return runtime.damage;},get health(){return runtime.health;},
    get environment(){return runtime.environment;},get interior(){return runtime.interior;},get crew(){return runtime.crew;},get rescue(){return runtime.rescue;},
    get mass(){return runtime.mass;},get dynamics(){return runtime.dynamics;},
    // Shared physical-world service, never copied into observer/AI state.
    get physicalWorld(){return ENGAGEMENT_RUNTIME.world;},get terrain(){return ENGAGEMENT_RUNTIME.terrain;},
    get tick(){return role==='PLAYER'?simStepCounter:runtime.clock.tick;},
    command(){return {ok:false,reason:'MULTI_SHIP_COMMAND_ROUTING_DEFERRED'};}
  });
  for(const kind of ['navigation','weapons','ew','damage','environment','interior','crew','rescue','mass','dynamics','clock','aviation','health'])claimShipMutableRootA(runtime,kind,runtime[kind]);
  for(const kind of ['sensors','trackManager','fireControl','engagementControl'])claimShipMutableRootA(runtime,kind,runtime.combatSystem[kind]);
  return runtime;
}
function geometryForShipProfileA(profile){
  const layout=profile.id==='CG_52_LATE_TICONDEROGA'?window.BunkerLayout:window.BurkeC52Layout;
  const registration=MULTISHIP_DAMAGE_REGISTRATION_A.profiles[profile.id];
  if(!layout||registration?.profileRevision!==profile.revision)throw Error('SHIP_GEOMETRY_REGISTRATION_REVISION');
  return {layout,boxes:registration.hitboxes,stations:profile.geometry.hullStations,stern:profile.geometry.sternXM,bow:profile.geometry.bowXM,
    targetIds:Object.fromEntries(registration.hitboxes.map(b=>[b.name,b.targetId])),section:x=>layout.hullSection(x),halfBeam:(x,z)=>layout.halfBeam(x,z),
    bowAtZ:z=>layout.bowAtZ(z),contains:(x,y,z)=>layout.contains(x,y,z,'HULL',.015)};
}
function guardedPreparedGunA(runtime,installation){
  const profile=resolveShipProfile(runtime.profileId),module=createProfileGunModuleWip13B3(installation,profile,{health:spec=>Math.max(0,1-runtime.flooding.readDamage(spec.damage.moduleName)/100)});
  const denied=()=>({ok:false,reason:'MULTI_SHIP_EXECUTION_DEFERRED'});
  // These operations depend on legacy player FCS and cannot be called by an enemy yet.
  return {...module,solveTrack:denied,solveState:denied,releaseGate:denied,command:denied,requestFire:denied,startContinuousFire:denied,step:denied};
}
function profileWeaponMassNodesA(runtime,make){
  const p=resolveShipProfile(runtime.profileId),w=p.mass.weapons,out=[],cg=p.id==='CG_52_LATE_TICONDEROGA',registration=cg?BUNKER_REGISTRATION:window.BurkeC5Registration;
  for(const section of ['fwd','aft'])for(const c of runtime.weapons.vls[section]){
    if(c.destroyed||c.type==='EMPTY')continue;
    const q=registration.cells[section].find(q=>q.row===c.row&&q.col===c.col);
    if(!q)throw Error('SHIP_VLS_MASS_REGISTRATION:'+section+':'+c.row+':'+c.col);
    const key={SM2:'sm2',SM2ER:'sm2er',SM6:'sm6',ESSM4:'essm'}[c.type],depth={SM2:2.36,SM2ER:3.28,SM6:3.28,ESSM4:1.83}[c.type];
    const offset=c.type==='ESSM4'?-.22*.649:0;
    out.push(make(`vls.${section}.${c.row}.${c.col}.${key}`,'ORDNANCE_DYNAMIC',w[key+'Kg']*(c.type==='ESSM4'?c.essmCount:1),{x:q.x+offset,y:q.y+offset,z:q.z-depth},'PROFILE_REGISTERED_CELL_POSITION'));
  }
  for(const m of runtime.weapons.closeIn)out.push(make('ciws.'+(m.installationId??(m.type==='RAM'?'searam':'phalanx'))+'.ammo','ORDNANCE_DYNAMIC',m.ammo*(m.type==='RAM'?w.ramKg:w.phalanxRoundKg),{x:m.posOffsetM,y:m.posOffsetYM??0,z:m.heightM},'PROFILE_REGISTERED_CLOSE_IN_POSITION'));
  if(cg)for(const [id,g]of runtime.weapons.gunMounts){const q=g.snapshot(),h=p.geometry.hardpoints[g.installation.hardpointId];for(const [ammo,n]of Object.entries(q.magazine))out.push(make('gun.'+id+'.'+ammo,'ORDNANCE_DYNAMIC',n*g.spec.ammunition[ammo].massKg,{x:h.x,y:h.y,z:h.z-3},'PROFILE_GUN_MAGAZINE'));}
  for(const l of runtime.weapons.srboc.launchers){const h=p.geometry.hardpoints.srboc.launchers.find(q=>q.id===l.id);for(let j=0;j<l.tubes.length;j++)if(l.tubes[j].loaded)out.push(make(`mk36.${l.id}.${l.tubes[j].id}`,'ORDNANCE_DYNAMIC',w.mk214Kg,mk36AddLocalWip15A(h.mount,h.tubes[j].massOffsetM),'PROFILE_REGISTERED_TUBE_POSITION'));}
  for(const t of runtime.weapons.harpoon.tubes)if(t.loaded)out.push(make('harpoon.'+t.id,'ORDNANCE_DYNAMIC',HARPOON_PROFILE_A.public.launchMassKg,p.weapons.harpoon.tubes.find(q=>q.id===t.id).massCenterM,'PROFILE_HARPOON_POSITION'));
  for(const key of ['srboc','nulka']){const r=runtime.weapons[key],spec=p.weapons.softKill15B[key],mass=key==='srboc'?w.mk214Kg:spec.roundMassKg,allocated=r.launchers.reduce((n,l)=>n+(l.reload?.allocatedRounds??0),0);
    out.push(make(key+'.reserve','ORDNANCE_DYNAMIC',(r.logistics.reserveRounds+allocated)*mass,spec.reservePositionM,'PROFILE_RESERVED_ROUNDS'));
    if(key==='nulka')for(let i=0;i<r.launchers.length;i++)for(let j=0;j<r.launchers[i].tubes.length;j++)if(r.launchers[i].tubes[j].loaded){const h=p.geometry.hardpoints.nulka.launchers[i];out.push(make(`nulka.${r.launchers[i].id}.T${j+1}`,'ORDNANCE_DYNAMIC',mass,mk36AddLocalWip15A(h.mount,h.tubes[j].massOffsetM),'PROFILE_REGISTERED_TUBE_POSITION'));}
  }
  return out;
}
function createPreparedShipRuntimeA(profile,options={}){
  if(!profile||!Object.isFrozen(profile))throw Error('IMMUTABLE_SHIP_PROFILE_REQUIRED');
  if(!['ENEMY','UNASSIGNED'].includes(options.role??'UNASSIGNED'))throw Error('PREPARED_SHIP_ROLE_INVALID');
  const r=createShipRuntime(profile,options),geo=geometryForShipProfileA(profile);r.navigation.c17Ownship=false;
  r.health={shipHP:100};r.clock={tick:0,timeS:0};
  r.combatSystem.sensors={model:resolveSensorSuite(profile.sensors.modelId),runtime:{radar:createShipRadarStateA(),spyScheduler:createShipSpySchedulerStateA(),spq9b:{model:resolveSensorSuite(profile.sensors.modelId).spq9b},bridgeMasterE:{model:resolveSensorSuite(profile.sensors.modelId).bridgeMasterE}},execution:'DEFERRED_STAGE_4'};
  r.combatSystem.trackManager={schema:'AEGIS_TRACK_MANAGER_BINDING_V48_WIP11A',tracks:new Map(),dwellTimers:new Map(),execution:'DEFERRED_STAGE_4'};
  Object.assign(r.combatSystem.fireControl,{illuminatorAssignments:new Map(),reservations:new Map(),illuminators:profile.geometry.hardpoints.spg62,execution:'DEFERRED_STAGE_5'});
  r.combatSystem.engagementControl={assessment:{},autonomy:{enabled:false},mode:'MANUAL',execution:'DEFERRED_STAGE_7'};
  r.ew={contacts:new Map(),slq32Allocator:createShipEaAllocatorStateA(),softKillDoctrine:createShipSoftKillDoctrineStateA(),mk36:r.weapons.srboc,nulka:r.weapons.nulka,execution:'DEFERRED_STAGE_6'};
  r.weapons.vls=createProfileVlsInventory(profile);r.weapons.closeIn=createProfileCloseInRuntimeA(profile,r.navigation);
  r.flooding=createDamageFloodModel(geo,{profile});
  r.damage={flood:r.flooding,control:createDamageControlV1(r.flooding,geo.boxes,{...DAMAGE_CONTROL_FEATURES_V1,profile,crewRouting:true,halfBeam:geo.halfBeam}),strength:createShipLongitudinalStrengthV48Wip03(r.flooding,{geometry:geo}),massLoss:createShipMassLossV16(geo,geo.boxes,{lightshipKg:profile.mass.lightshipKg})};
  r.interior=profile.id==='CG_52_LATE_TICONDEROGA'?createBunkerInterior(r.flooding,geo.layout):createShipInteriorTopologyV48Wip06(r.flooding,{profile,geometry:geo.layout,publishDiagnostics:false});
  r.crew=createShipCrewV48Wip07(r.interior,crewDutyPostsV48Wip07(profile),{profile,boardSurvivor:()=>false,onReset:()=>{}});
  const installations=profile.weapons.gunMounts??[profile.weapons.mainGun];
  r.weapons.gunMounts=new Map(installations.map(inst=>[inst.id,guardedPreparedGunA(r,inst)]));r.weapons.selectedGunId=profile.weapons.mainGun.id;r.weapons.mainGun=r.weapons.gunMounts.get(r.weapons.selectedGunId);
  r.weapons.magazines={mk41:r.weapons.vls,mk36:r.weapons.srboc.launchers,nulka:r.weapons.nulka.launchers};
  r.mass=createShipMassLedgerV32(r.flooding.cells,{massProfile:profile.mass,weaponNodes:make=>profileWeaponMassNodesA(r,make)});r.mass.syncCrew(r.crew.snapshot().groups,0,true);
  r.dynamics=createShipDynamicsV15(geo,{profile,massLedger:()=>r.mass,navigation:()=>r.navigation,clock:()=>r.clock.tick});
  r.environment={waveFlood:createWaveFloodEnvironmentV48Wip05({useCommonMaritime:true})};
  r.aviation.facilities={hangar:profile.geometry.aft.hangar,flightDeck:profile.geometry.hardpoints.flightDeck};
  // Raft controllers join the shared world only when physical ships are activated.
  r.rescue={schema:'AEGIS_PREPARED_RESCUE_MULTI_SHIP_A',roster:profile.crew.roster,capacityPersons:SHIP_RESCUE_MK7_K.capacityPersons,execution:'DEFERRED_STAGE_3',snapshot:()=>({ownerEntityId:r.entityId,rafts:[],execution:'DEFERRED_STAGE_3'})};
  for(const k of Object.keys(r.subsystems))r.subsystems[k]=k==='sensors'?r.combatSystem.sensors:r[k];
  r.lifecycleState='STATE_BOUND_INACTIVE';return attachShipContextA(r,options.role??'UNASSIGNED');
}
function multiShipSnapshotA(){
  return {schema:'AEGIS_MULTI_SHIP_STAGE_2_A',registered:ENGAGEMENT_RUNTIME.ships.size,simulated:1,sharedWorldUpdatesPerTick:1,activePlayerShipId:ENGAGEMENT_RUNTIME.activePlayerShipId,
    deployment:deploymentSnapshotA(),ships:[...ENGAGEMENT_RUNTIME.ships.values()].map(r=>({entityId:r.entityId,profileId:r.profileId,role:r.role,execution:r.executionState,lifecycle:r.lifecycleState??'OWNERSHIP_BOUND',bound:{context:!!r.context,sensors:!!r.combatSystem.sensors,tracks:!!r.combatSystem.trackManager,weapons:!!r.weapons.mainGun,ew:!!r.ew,damage:!!r.damage,environment:!!r.environment,interior:!!r.interior,crew:!!r.crew,mass:!!r.mass,dynamics:!!r.dynamics},vlsCells:Object.values(r.weapons.vls??{}).reduce((n,q)=>n+q.length,0),crew:r.crew?.snapshot().summary?.roster??resolveShipProfile(r.profileId).crew.roster,closeInTypes:r.weapons.closeIn?.map(q=>q.type),harpoonTubes:r.weapons.harpoon.tubes.length})),
    deferred:['physicalEnemyDeployment','multiShipPhysicsTicks','perObserverMeasurements','bidirectionalWeaponRouting','receiverSpecificEW','enemyAI']};
}
function multiShipIsolationAuditA(){
  const before=operationalImportMutationFingerprintV48Wip11B(),rng=SIM_RNG_STATE>>>0,checks={},rows=[];
  for(const profile of Object.values(SHIP_PROFILE_REGISTRY)){
    const a=createPreparedShipRuntimeA(profile,{entityId:'DIAG_MULTI_A_'+profile.id}),b=createPreparedShipRuntimeA(profile,{entityId:'DIAG_MULTI_B_'+profile.id});
    const pristine=JSON.stringify({mass:b.mass.snapshot({detail:true}),crew:b.crew.snapshot(),flood:b.flooding.snapshot(),guns:[...b.weapons.gunMounts.values()].map(g=>g.snapshot())});
    a.navigation.positionWorld.x=123;a.weapons.vls.fwd[0].destroyed=true;a.weapons.closeIn[0].ammo=0;a.weapons.srboc.launchers[0].tubes[0].loaded=false;a.weapons.nulka.logistics.reserveRounds=0;
    a.combatSystem.trackManager.tracks.set(42,{id:42});a.combatSystem.trackManager.dwellTimers.set('test',2);a.ew.contacts.set(77,{bearing:1});a.ew.slq32Allocator.resourceUsed=1;a.combatSystem.fireControl.spg62Servo.mounts[0].azRad=1;
    const label=[...a.flooding.targets.values()][0].label;a.flooding.setDamage(label,60);a.flooding.setWater(a.flooding.cells[0].id,5);a.mass.setLoadMassKg(a.mass.loadIds()[0],0);a.crew.abandon('DIAG_ISOLATION');a.damage.control.ignite(a.flooding.cells[0].id,.8,'EXPLOSIVE_DIAGNOSTIC');a.dynamics.haltHorizontalContact();
    const after=JSON.stringify({mass:b.mass.snapshot({detail:true}),crew:b.crew.snapshot(),flood:b.flooding.snapshot(),guns:[...b.weapons.gunMounts.values()].map(g=>g.snapshot())});
    // Ignore diagnostic-only cache-hit counters; physical state must be identical.
    const physical=q=>{const t=JSON.parse(q);delete t.mass.performance;delete t.crew.performance;return t;};
    const id=profile.id;checks[id+'.independentModels']=JSON.stringify(physical(pristine))===JSON.stringify(physical(after));
    checks[id+'.independentBuffers']=b.combatSystem.trackManager.tracks.size===0&&b.combatSystem.trackManager.dwellTimers.size===0&&b.ew.contacts.size===0&&b.ew.slq32Allocator.resourceUsed===0&&b.combatSystem.fireControl.spg62Servo.mounts[0].azRad===0;
    checks[id+'.independentInventory']=!b.weapons.vls.fwd[0].destroyed&&b.weapons.closeIn[0].ammo>0&&b.weapons.srboc.launchers[0].tubes[0].loaded&&b.weapons.nulka.logistics.reserveRounds>0;
    checks[id+'.sharedImmutableProfile']=a.context.profile===b.context.profile&&Object.isFrozen(a.context.profile)&&a.context.physicalWorld===ENGAGEMENT_RUNTIME.world;
    checks[id+'.contextLive']=a.context.navigation.positionWorld.x===123&&a.context.damage.flood.readDamage(label)===60;
    checks[id+'.crewAndControlIndependent']=a.crew.snapshot().mode!==b.crew.snapshot().mode&&b.damage.control.snapshot().cells.every(c=>c.fire===0);
    checks[id+'.coreAccessorOwner']=getDamageFloodV1(a)===a.flooding&&getDamageControlV1(a)===a.damage.control&&getShipCrewV21(a)===a.crew&&getShipDynamicsV15(a)===a.dynamics&&getShipInteriorTopologyV48Wip06(a)===a.interior&&getShipMassLedgerV32(a)===a.mass&&getWaveFloodEnvironmentV48Wip05(a)===a.environment.waveFlood;
    checks[id+'.gunRoutingBlocked']=a.weapons.mainGun.requestFire(1).reason==='MULTI_SHIP_EXECUTION_DEFERRED'&&a.weapons.mainGun.command(1).reason==='MULTI_SHIP_EXECUTION_DEFERRED'&&a.weapons.mainGun.step(1/60).reason==='MULTI_SHIP_EXECUTION_DEFERRED';
    let rejected=false;try{bindShipRuntimeSubsystemV48Wip11A('mass',a.mass,b);}catch(e){rejected=String(e.message).startsWith('SHIP_MUTABLE_STATE_ALREADY_OWNED');}checks[id+'.crossBindingRejected']=rejected;
    rows.push({profileId:id,vlsCells:Object.values(b.weapons.vls).reduce((n,q)=>n+q.length,0),crew:b.crew.snapshot().groups.length,interior:b.interior.audit(),massKg:b.mass.snapshot().massKg});
  }
  checks.playerUnchanged=JSON.stringify(before)===JSON.stringify(operationalImportMutationFingerprintV48Wip11B());checks.combatRngUnchanged=rng===(SIM_RNG_STATE>>>0);checks.playerAliasesPinned=shipNav===ACTIVE_SHIP_RUNTIME.navigation&&tracks===ACTIVE_SHIP_RUNTIME.combatSystem.trackManager.tracks;
  return {schema:'AEGIS_MULTI_SHIP_ISOLATION_A',pass:Object.values(checks).every(Boolean),checks,rows};
}
