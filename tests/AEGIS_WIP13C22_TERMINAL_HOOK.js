// DIAGNOSTIC_ONLY: injected by the terminal regression runner, never packed in gameplay.
window.__C22_TEST__={surfaceTerminal(o={}){
  _wip75ResetCase(1350501);resetEngagementTransientV48Wip11A();
  surfaceContacts.length=0;SURFACE_TARGET_ENTITY_REGISTRY_V48_WIP13A.clear();WIP12B_TERMINAL_EVENTS.length=0;
  const weapon=o.weapon==='ESSM'?'ESSM':'SM2',tdd=weapon==='ESSM'?ESSM_BLOCK2_TDD_SIM:SM2MR_BLOCK_IIIA_MK45_MOD9_TDD_SIM,missileProfile=SAM_MISSILE_PROFILES[weapon==='ESSM'?'ESSM_BLK2_SIM':'SM2MR_BLKIIIA_SIM'],initialTddRadius=tdd.detectionRadiusM;
  if(o.fuzeRangeOverrideM!=null)tdd.detectionRadiusM=Number(o.fuzeRangeOverrideM);
  const target=spawnSurfaceTargetWip13A({entityId:'C22_TERMINAL_TARGET',x:aircraft.x()+kmToWorld(1),y:aircraft.y(),heading:0,speedKt:0,mobilityMode:'DEAD_IN_WATER'}),profile=surfaceTargetProfileWip13A(target.profileId),beam=profile.geometry.beamM;
  let startLocal,endLocal;
  if(o.case==='SEA_FIRST'){
    const seaLocalZ=surfaceTargetWorldSimToLocalWip13A(target,{x:target.x,y:target.y,z:0}).z;
    startLocal={x:0,y:beam+35,z:seaLocalZ+1};endLocal={x:0,y:beam+29,z:seaLocalZ-1};
  }
  else if(o.case==='MISS'){startLocal={x:0,y:beam+190,z:6};endLocal={x:0,y:beam+120,z:6};}
  else if(o.case==='NEAR_MISS'){startLocal={x:profile.geometry.lengthM*.5+4,y:beam+100,z:6};endLocal={x:startLocal.x,y:-beam-10,z:6};}
  else if(o.case==='APPROACH_CONTACT'){
    const radius=missileProfile.lethalRadiusM,exterior=surfaceMissileClosestExteriorWip13C22(profile,{x:0,y:beam,z:6}).point;
    startLocal={x:0,y:exterior.y+radius+1,z:6};endLocal={x:0,y:exterior.y+radius-1,z:6};
  }
  else{startLocal={x:0,y:beam+20,z:6};endLocal={x:0,y:-beam-10,z:6};}
  const start=surfaceTargetLocalToWorldSimWip13A(target,startLocal),end=surfaceTargetLocalToWorldSimWip13A(target,endLocal),delta={x:worldToMeters(end.x-start.x),y:worldToMeters(end.y-start.y),z:end.z-start.z},norm=Math.hypot(delta.x,delta.y,delta.z)||1;
  const m={id:o.case==='CONTACT'?313502:313501,isESSM:weapon==='ESSM',_v1Profile:missileProfile,guidanceCore:'v1',heading:Math.atan2(delta.y,delta.x),pitch:Math.asin(delta.z/norm),x:end.x,y:end.y,z:end.z,vx:mpsToWorldSpeed(780*delta.x/norm),vy:mpsToWorldSpeed(780*delta.y/norm),vz:780*delta.z/norm,speed:mpsToWorldSpeed(780),life:12,massKg:weapon==='ESSM'?280:708,vlsPhase:false,dead:false,proxDetonated:false};
  m[weapon==='ESSM'?'_surfaceArh':'_surfaceSarh']={schema:'C22_DIAGNOSTIC_SURFACE_RUNTIME',trackId:313500,aimHeightM:6,truthUsed:false};
  const binding=surfaceMissileFuzeEnvelopeWip13C22(m);let result=null;
  if(o.case==='NEAR_MISS'){
    const ticks=Math.ceil(norm/(780*SIM_FIXED_DT));
    for(let i=0;i<ticks&&!m.dead;i++){
      const a=i/ticks,b=(i+1)/ticks,stepStart={x:lerp(start.x,end.x,a),y:lerp(start.y,end.y,a),z:lerp(start.z,end.z,a)};
      m.x=lerp(start.x,end.x,b);m.y=lerp(start.y,end.y,b);m.z=lerp(start.z,end.z,b);
      result=surfaceMissileSweptContactWip13C5(m,stepStart);simStepCounter++;
    }
  }else result=surfaceMissileSweptContactWip13C5(m,start);
  const snapshot=surfaceTargetSnapshotWip13A(target),event=wip12bTerminalEventsSnapshot().find(e=>e.impactEventId===m._surfaceImpact?.eventId)??null;
  surfaceMissileSweptContactWip13C5(m,start);
  tdd.detectionRadiusM=initialTddRadius;
  return {weapon,case:o.case??'CONTACT',deathReason:m._deathReason??null,dead:m.dead,proxDetonated:m.proxDetonated,impact:result??null,impactCount:snapshot.damage.impacts.length,hitCount:snapshot.damage.impacts.filter(q=>q.hit).length,damageRevision:snapshot.damage.revision,revisionAfterDuplicate:target.targetRuntime.damage.revision,scars:snapshot.damage.scars.length,breaches:snapshot.damage.breaches.length,impactExplosiveKg:snapshot.damage.impacts[0]?.explosiveMassKg??0,terminal:event?{fuzePath:event.fuzePath,integrationMode:event.integrationMode,damageSummary:event.damageSummary}:null,targetAlive:target.alive,z:m.z,nearestAtEndM:surfaceMissileClosestExteriorWip13C22(profile,endLocal).distanceM,fuzeBinding:{source:tdd.id,sensingM:binding.detectionRadiusM,activationM:binding.actuationRadiusM,armingKm:binding.armingRangeKm,delayS:binding.processingDelayS},sensorAcquired:!!m._surfaceFuzeSenseWip13C22,airFuzeArmed:!!m.proxArmed};
},supportLifecycle(){
  _wip75ResetCase(1350501);resetEngagementTransientV48Wip11A();
  const oldId=313900,newId=313901,tr=makeSurfaceMissileFixtureTrackWip13C4({trackId:oldId,identity:'TRAINING_TARGET'});
  tracks.set(oldId,tr);
  const primed=wip121PrimeDiagnosticTargetSupport(oldId,0),mount=spg62ServoMount(0);
  mount.targetTrackId=oldId;mount.mode='ILLUMINATING';mount.emitting=true;
  wip121TransferEngagementMemory(oldId,newId);
  tracks.delete(oldId);tr.trackId=newId;tracks.set(newId,tr);
  const transferred={oldReservation:SPG62_RESERVATION_STATE.has(oldId),newReservation:SPG62_RESERVATION_STATE.has(newId),oldOwner:SPG62_ENGAGEMENT_STATE.has(oldId),newOwner:SPG62_ENGAGEMENT_STATE.has(newId),mountTargetId:mount.targetTrackId,missileTargetId:missiles.at(-1)?.assignedTargetId};
  wip118ControlState.assessments.set(newId,{state:'KILL_ASSESSMENT',bdaEvent:{evidence:'DIRECT_BREAKUP'}});
  const bdaBlocked=wip121TargetSupportBlocked(newId,tr),released=wip121ReleaseTargetFireControlSupport(newId,'DIRECT_BREAKUP'),after=wip121TargetSupportSnapshot(newId);
  return {primed:!!primed,transferred,bdaBlocked,released:{released:released.released,missiles:released.missiles,rowsRemoved:released.rowsRemoved},after:{owner:!!after.liveIlluminator,reservation:!!after.reservation,missiles:after.missiles,mountMode:mount.mode,mountEmitting:mount.emitting,mountTargetId:mount.targetTrackId}};
}};
