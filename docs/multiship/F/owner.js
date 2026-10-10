// These lexical bindings reuse the existing soft-kill kernel without switching
// the player profile, compatibility globals or sensor buffers.
function createElectronicContextF(owner,e,sharedMk36){
  const ACTIVE_SHIP_RUNTIME=owner,ACTIVE_SHIP_PROFILE=resolveShipProfile(owner.profileId),shipNav=owner.navigation,
    aircraft={x:()=>shipNav.positionWorld.x,y:()=>shipNav.positionWorld.y},tracks=observerC(owner).tracks,esmContacts=e.contacts,
    MK36_RUNTIME_WIP15A=owner.weapons.srboc,mk36LauncherState=owner.weapons.srboc.launchers,
    MK36_SRBOC={...sharedMk36,launcherCount:ACTIVE_SHIP_PROFILE.geometry.hardpoints.srboc.launchers.length},
    wip118ControlState=owner.weapons.executionD.defenseE.control;
  let slq32EaState=owner.ew.slq32Allocator,softKillDoctrineState=owner.ew.softKillDoctrine,
    softKillThreatState={threats:[],primary:null,revision:0,lastStep:-1},noiseJamActive=e.noiseRequested,deceptJamActive=e.deceptionRequested,
    softKillAutoDoctrine=e.auto,jammerAutoTrack=e.autoAim,jammerBearing=e.bearing,mk36LastCue=null;
  function notify(message){e.lastMessage=String(message);}
  function updateMk36ButtonLabel(){}
  function updateNulkaUi15B(){}
  function updateSlq32EaButtonLabels(){}
  function shipEquipmentOfflineV1(){return owner.survival.snapshot().equipmentOffline||owner.crew.offline();}
  function getModuleDmg(name){return owner.flooding.readDamage(name);}
  function shipMassMarkWeaponsV32(reason){owner.mass.markWeaponsDirty(reason);}
  function shipGameFrameV1(){return shipBodyFrameB(owner);}
  function shipGamePointStateV1(point){return ownerPointStateD(owner,point);}
  function shipGameAnglesV1(v){return {az:Math.atan2(v.y,v.x),el:Math.atan2(v.z,Math.hypot(v.x,v.y))};}
  function simRandom(){return observerRandomC(e.rng);}
  function rand(a,b){return a+(b-a)*simRandom();}
  function trackIsDisplayable(tr){return !!tr&&tr.confirmed&&tr.sensorDetected!==false&&tr.sensorAge<=2&&!tr.memActive;}
  function trackKinematicThreatCue(tr){const q=ownerThreatRowD(owner,tr);return {missileLike:tr.classification==='ASM',closureMps:q.vr/3.6,altM:tr.z??0};}
  // @ORIGINAL_EW_FUNCTIONS_F@
  function sync(){noiseJamActive=e.noiseRequested;deceptJamActive=e.deceptionRequested;softKillAutoDoctrine=e.auto;jammerAutoTrack=e.autoAim;jammerBearing=e.bearing;}
  function step(dt){
    sync();MK36_RUNTIME_WIP15A.cooldownS=Math.max(0,MK36_RUNTIME_WIP15A.cooldownS-dt);owner.weapons.nulka.cooldownS=Math.max(0,owner.weapons.nulka.cooldownS-dt);
    skUpdateReload15B('SRBOC');skUpdateReload15B('NULKA');updateSoftKillThreatManager(dt);updateSoftKillDoctrine(dt);updateJammerBearing(dt);updateSlq32EaAllocator(dt);
    e.bearing=jammerBearing;owner.ew.slq32Allocator=slq32EaState;owner.ew.softKillDoctrine=softKillDoctrineState;
  }
  return {step,release:kind=>{sync();updateSoftKillThreatManager(SIM_FIXED_DT);return kind==='NULKA'?nulkaFire15B(softKillPrimaryThreat(),{quiet:true}):{ok:deployOwnChaffForThreat(softKillPrimaryThreat())>0};},
    bloom:cart=>bloomMk214Cloud(cart),snapshot:()=>jsonSafeCloneV48Wip11A({primary:softKillThreatState.primary,threats:softKillThreatState.threats,...softKillDoctrineAuditSnapshot()}),
    logistics:()=>({srboc:skLogisticsSnapshot15B('SRBOC'),nulka:skLogisticsSnapshot15B('NULKA')}),inventory:()=>({mk36:jsonSafeCloneV48Wip11A(mk36LauncherState),softKill15B:skExport15B()}),validateInventory:skValidate15B,restoreInventory:skRestore15B};
}
