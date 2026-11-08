// EMCON_B Commit E — operational snapshot, lifecycle, and network-overlay helpers.
// Group leases remain transient. Only each owner's individual detail policy is authoritative.
function emconCloneStateB(state){return structuredClone(state);}
function emconExportStateB(r){return emconCloneStateB(emconStateViewB(r));}
function emconRestoreStateB(r,state){
  const validation=validateEmconStateB(r,state);
  if(!validation.ok)throw Error('EMCON_B_RESTORE_INVALID:'+validation.errors.join(','));
  const restored=emconCloneStateB(state);r.combatSystem.emconB=restored;delete r.restoredEmconB;claimShipMutableRootA(r,'emconB',restored);return restored;
}
function emconResetRuntimeB(r){
  if(!r?.combatSystem)return null;
  delete r.restoredEmconB;const fresh=emconDefaultStateB(r);r.combatSystem.emconB=fresh;claimShipMutableRootA(r,'emconB',fresh);
  if(typeof EMCON_B_ALL_RADIATION_MEMORY!=='undefined')EMCON_B_ALL_RADIATION_MEMORY.delete(r.entityId);return fresh;
}
function emconRetireRuntimeB(r){
  if(!r)return;
  if(typeof EMCON_B_ALL_RADIATION_MEMORY!=='undefined')EMCON_B_ALL_RADIATION_MEMORY.delete(r.entityId);
  delete r.restoredEmconB;if(r.combatSystem)r.combatSystem.emconB=null;
}
function emconLegacyDefaultForProfileB(profileId){return emconDefaultStateB({profileId});}
function migrateEmconSaveB(src,migrations){
  const changed=[];
  if(src.ship&&!Object.hasOwn(src.ship,'emconB')){src.ship.emconB=emconLegacyDefaultForProfileB(src.profileId);changed.push(src.shipId??'PLAYER');}
  for(const q of src.fleet?.ships??[])if(q&&!Object.hasOwn(q,'emconB')){q.emconB=emconLegacyDefaultForProfileB(q.profileId);changed.push(q.entityId);}
  if(changed.length)migrations.push({id:'LEGACY_EMCON_B_DEFAULTS',policy:'PROFILE_DEFAULT_RADIATE_AND_INHERIT; MASTER_EMCON_PRESERVED',owners:changed});
}
function validateEmconSaveB(profileId,state,errors,path){
  let validation;
  try{validation=validateEmconStateB({profileId},state);}catch(_err){errors.push('EMCON_B_INTERNAL:'+path);return;}
  for(const code of validation.errors)errors.push('EMCON_B_'+code+':'+path);
}
function emconNetworkModeB(r){
  const n=r?.combatSystem?.networkG,now=(typeof simStepCounter==='number'?simStepCounter:0)*SIM_FIXED_DT;
  if(!n)return 'INDIVIDUAL';
  if(r===ACTIVE_SHIP_RUNTIME&&n.groupBase!==null&&n.groupBase!==undefined)return n.settings?.groupEmcon??'INDIVIDUAL';
  if(r!==ACTIVE_SHIP_RUNTIME&&n.groupLease&&n.groupLease.untilS>=now)return n.groupLease.mode??'INDIVIDUAL';
  return 'INDIVIDUAL';
}
function emconRecordOperatorDispositionB(r,command){
  const mode=emconNetworkModeB(r),disposition=mode==='INDIVIDUAL'?'INDIVIDUAL_POLICY_UPDATE':'MANUAL_DETAIL_UNDER_GROUP_OVERLAY';
  const row={ownerEntityId:r.entityId,profileId:r.profileId,revision:r.combatSystem.emconB?.revision??0,networkMode:mode,disposition,command:Object.hasOwn(command,'category')?{category:command.category,policy:command.policy}:Object.hasOwn(command,'equipmentId')?{equipmentId:command.equipmentId,override:command.override}:{reset:true}};
  EMCON_B_AUDIT.operatorDispositions.push(row);if(EMCON_B_AUDIT.operatorDispositions.length>64)EMCON_B_AUDIT.operatorDispositions.shift();return row;
}
function emconLifecycleSnapshotB(){return [...ENGAGEMENT_RUNTIME.ships.values()].map(r=>({ownerEntityId:r.entityId,profileId:r.profileId,lifecycleState:r.lifecycleState,state:emconExportStateB(r),networkMode:emconNetworkModeB(r)}));}
