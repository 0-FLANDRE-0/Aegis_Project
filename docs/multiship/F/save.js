function exportSoftKillOwnerF(r){
  const store=key=>{const runtime=r.weapons[key],layout=resolveShipProfile(r.profileId).geometry.hardpoints[key];return {layoutRevision:layout.revision,logistics:{reserveRounds:runtime.logistics.reserveRounds,expendedRounds:runtime.logistics.expendedRounds,reloadSeconds:runtime.logistics.reloadSeconds},launchers:runtime.launchers.map(l=>({id:l.id,label:l.label,enabled:l.enabled,health01:l.health01,nextTube:l.nextTube,rounds:l.rounds,tubes:l.tubes.map(t=>({...t})),reload:{state:l.reload.state,allocatedRounds:l.reload.allocatedRounds,totalTicks:l.reload.totalTicks,remainingTicks:l.reload.remainingTicks,pauseReason:l.reload.pauseReason}}))};};
  return {mk36:jsonSafeCloneV48Wip11A(r.weapons.srboc.launchers),softKill15B:{schema:'AEGIS_SOFTKILL_SNAPSHOT_15B',srboc:store('srboc'),nulka:store('nulka')}};
}
function validateSoftKillOwnerF(r,inventory,errors){
  // Detached profile-only validation: no operational state is reset or bound.
  const context={weapons:r.weapons},p=resolveShipProfile(r.profileId);
  const skLayout15B=k=>p.geometry.hardpoints[k==='SRBOC'?'srboc':'nulka'],skSpec15B=k=>p.weapons.softKill15B[k==='SRBOC'?'srboc':'nulka'];
  // @ORIGINAL_SOFTKILL_VALIDATOR_F@
  skValidate15B(inventory,errors);
}
function restoreSoftKillOwnerF(r,inventory){
  if(!inventory?.softKill15B)return;
  for(const key of ['srboc','nulka']){const rec=inventory.softKill15B[key],runtime=r.weapons[key];Object.assign(runtime.logistics,rec.logistics,{lastUpdateStep:simStepCounter});
    rec.launchers.forEach((q,i)=>{const l=runtime.launchers[i];l.enabled=q.enabled;l.health01=q.health01;l.nextTube=q.nextTube;q.tubes.forEach((t,j)=>Object.assign(l.tubes[j],t));l.reload={...q.reload,startedStep:simStepCounter};});}
  r.mass.markWeaponsDirty('OWNER_SOFTKILL_RESTORE_F');
}
function validateElectronicSettingsF(settings,errors){
  const keys=['emcon','noiseRequested','deceptionRequested','auto','autoAim','bearingRad'];
  if(!settings||typeof settings!=='object'||Array.isArray(settings)||Object.keys(settings).length!==keys.length||Object.keys(settings).some(k=>!keys.includes(k))||keys.slice(0,5).some(k=>typeof settings[k]!=='boolean')||!Number.isFinite(settings.bearingRad)||Math.abs(settings.bearingRad)>TAU)errors.push('EW_SETTINGS_F');
}
function retireElectronicF(r){
  r.ew.executionF?.contacts.clear();
  for(const rows of [ownChaffCartridges,ownChaffs,nulkaEntities15B()])for(let i=rows.length-1;i>=0;i--)if(rows[i].ownerEntityId===r.entityId)rows.splice(i,1);
  r.ew.executionF=null;
}
