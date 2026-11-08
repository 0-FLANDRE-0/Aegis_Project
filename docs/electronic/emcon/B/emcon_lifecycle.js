// EMCON_B Commit E — operational snapshot, lifecycle, and network-overlay helpers.
// Group leases remain transient. Only each owner's individual detail policy is authoritative.
function emconCloneStateB(state){return structuredClone(state);}
function emconExportStateB(r){return emconCloneStateB(emconStateViewB(r));}
function emconRestoreStateB(r,state){
  const candidate=state?.schema===EMCON_B_PREVIOUS_SCHEMA?migrateEmconStateV1B(r,state):state;
  const validation=validateEmconStateB(r,candidate);
  if(!validation.ok)throw Error('EMCON_B_RESTORE_INVALID:'+validation.errors.join(','));
  const restored=emconCloneStateB(candidate);r.combatSystem.emconB=restored;delete r.restoredEmconB;claimShipMutableRootA(r,'emconB',restored);return restored;
}
function emconResetRuntimeB(r){
  if(!r?.combatSystem)return null;
  delete r.restoredEmconB;const fresh=emconDefaultStateB(r);r.combatSystem.emconB=fresh;claimShipMutableRootA(r,'emconB',fresh);
  return fresh;
}
function emconRetireRuntimeB(r){
  if(!r)return;
  delete r.restoredEmconB;if(r.combatSystem)r.combatSystem.emconB=null;
}
function emconLegacyDefaultForProfileB(profileId){return emconDefaultStateB({profileId});}
function migrateEmconSaveB(src,migrations){
  const defaults=[],v1=[];
  function migrate(owner,profileId,ownerId){
    if(!owner||!Object.hasOwn(owner,'emconB')){if(owner){owner.emconB=emconLegacyDefaultForProfileB(profileId);defaults.push(ownerId);}return;}
    if(owner.emconB?.schema!==EMCON_B_PREVIOUS_SCHEMA)return;
    const check=validateEmconDetailB({profileId},owner.emconB,EMCON_B_PREVIOUS_SCHEMA);
    if(!check.ok)return;
    owner.emconB=migrateEmconStateV1B({profileId},owner.emconB);v1.push(ownerId);
  }
  migrate(src.ship,src.profileId,src.shipId??'PLAYER');
  for(const q of src.fleet?.ships??[])migrate(q,q?.profileId,q?.entityId);
  if(defaults.length)migrations.push({id:'LEGACY_EMCON_B_DEFAULTS_V2',policy:'PROFILE_DEFAULT_RADIATE_AND_INHERIT; ALL_RADIATION_SILENT_FALSE; MASTER_EMCON_PRESERVED',owners:defaults});
  if(v1.length)migrations.push({id:'EMCON_B_V1_TO_V2',policy:'DETAIL_EXACT; ALL_RADIATION_SILENT_FALSE; MASTER_EMCON_PRESERVED',owners:v1});
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
  const row={ownerEntityId:r.entityId,profileId:r.profileId,revision:r.combatSystem.emconB?.revision??0,networkMode:mode,disposition,command:structuredClone(command)};
  EMCON_B_AUDIT.operatorDispositions.push(row);if(EMCON_B_AUDIT.operatorDispositions.length>64)EMCON_B_AUDIT.operatorDispositions.shift();return row;
}
function emconLifecycleSnapshotB(){return [...ENGAGEMENT_RUNTIME.ships.values()].map(r=>({ownerEntityId:r.entityId,profileId:r.profileId,lifecycleState:r.lifecycleState,state:emconExportStateB(r),networkMode:emconNetworkModeB(r)}));}
