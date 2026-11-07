// EMITTER_A immutable ShipProfile equipment registration.
// Category describes installed equipment role; emitterClass remains an
// observation/output classification and is intentionally separate.
const SHIP_EMITTER_CATEGORIES_A=Object.freeze(['AIR_SEARCH','SURFACE_SEARCH','NAV','FIRE_CONTROL','ECM']);
const SHIP_EMITTER_COMPATIBILITY_A=Object.freeze({
  schema:'AEGIS_SHIP_EMITTER_COMPATIBILITY_A_1',
  units:'LEGACY_GAME_COMPATIBILITY_POWER__NOT_WATTS_OR_ERP',
  spyPower:2500,spqPower:650,navPower:120,ecmPowerPerResource:2000,
  provenance:'EXISTING_ELECTRONIC_PHYSICAL_EMITTERS_F_VALUES__NO_RETUNING'
});
function shipEmitterEquipmentRegistryA(profileId){
  const cg=profileId==='CG_52_LATE_TICONDEROGA';
  if(!cg&&profileId!=='DDG_119_LATE_FLIGHT_IIA')throw Error('SHIP_EMITTER_PROFILE_UNSUPPORTED:'+profileId);
  const entries=[
    {id:cg?'AN_SPY_1A_MODERNIZED':'AN_SPY_1DV',order:10,category:'AIR_SEARCH',outputKind:'RADAR',
      enabledKey:'SPY',sensorKey:'spy1dv',mountKind:'FIRST_HEALTHY_SPY_FACE',bandMode:'FIXED',band:'S',
      power:SHIP_EMITTER_COMPATIBILITY_A.spyPower,powerProvenance:'LEGACY_COMPATIBILITY_UNIT_2500',
      family:'SHIP SEARCH RADAR',emitterClass:'SEARCH_RADAR',beamMode:'OMNIDIRECTIONAL_NULL',
      provenance:'EXISTING_PROFILE_SENSOR_AND_OBSERVER_FACE_REGISTRATION'},
    {id:cg?'AN_SPQ_9':'AN_SPQ_9B',order:20,category:'SURFACE_SEARCH',outputKind:'RADAR',
      enabledKey:'SPQ',sensorKey:'spq9b',hardpointKey:'spq9b',mountKind:'PROFILE_HARDPOINT',bandMode:'FIXED',band:'IJ',
      power:SHIP_EMITTER_COMPATIBILITY_A.spqPower,powerProvenance:'LEGACY_COMPATIBILITY_UNIT_650',
      family:'SURFACE SEARCH RADAR',emitterClass:'SEARCH_RADAR',rotorKey:'SPQ',beamwidthDeg:.6,
      beamwidthProvenance:'SIM_TUNED_EXISTING_OBSERVATION_MODEL',rpmField:'rpm',double:true,
      provenance:cg?'CG52_EXISTING_SPQ9_PROFILE_AND_REGISTERED_HARDPOINT':'DDG119_EXISTING_SPQ9B_PROFILE_AND_REGISTERED_HARDPOINT'},
    {id:cg?'AN_SPS_73':'BRIDGEMASTER_E',order:30,category:'NAV',outputKind:'RADAR',
      enabledKey:'NAV',sensorKey:'bridgeMasterE',hardpointKey:'bridgeMasterE',mountKind:'PROFILE_HARDPOINT',bandMode:'SENSOR_PROFILE',
      power:SHIP_EMITTER_COMPATIBILITY_A.navPower,powerProvenance:'LEGACY_COMPATIBILITY_UNIT_120',
      family:'NAVIGATION RADAR',emitterClass:'SEARCH_RADAR',rotorKey:'NAV',beamwidthField:'horizontalBeamwidthDeg',
      beamwidthProvenanceMode:'SENSOR_PROFILE',rpmField:'nominalRpm',double:false,
      provenance:cg?'CG52_EXISTING_SPS73_PROFILE_AND_REGISTERED_HARDPOINT':'DDG119_EXISTING_BRIDGEMASTER_E_PROFILE_AND_REGISTERED_HARDPOINT'},
    {id:'AN_SLQ_32_EA',order:40,category:'ECM',outputKind:'ECM',mountKind:'FIRST_AVAILABLE_EW_POD',bandMode:'FIXED',band:'IJ',
      powerPerResource:SHIP_EMITTER_COMPATIBILITY_A.ecmPowerPerResource,powerProvenance:'LEGACY_COMPATIBILITY_UNIT_2000_X_RESOURCE_USED',
      family:'RF INTERFERENCE',emitterClass:'JAMMER',beamMode:'EW_OPERATOR_BEARING',
      provenance:cg?'CG52_REGISTERED_TWIN_SLQ32_PODS_SHARED_EXISTING_ALLOCATOR':'DDG119_LEGACY_RF_REFERENCE_SHARED_EXISTING_ALLOCATOR'}
  ];
  return {schema:'AEGIS_SHIP_EMITTER_EQUIPMENT_A_1',registryId:(cg?'CG52':'DDG119')+'_EMITTERS_A',profileId,
    physicalEmission:true,categories:SHIP_EMITTER_CATEGORIES_A,entries,
    mutableStateOwner:'ShipRuntime.observerC + ShipRuntime.ew; profile definitions are immutable',
    outputContract:'AEGIS_RECEIVER_EW_F_1_LEGACY_EXACT'};
}
function shipEmitterSovRegistryA(registration){
  const category=role=>role==='AIR_SEARCH'?'AIR_SEARCH':role==='ASM_TARGETING_RADAR'?'SURFACE_SEARCH':
    (String(role).includes('FIRE_CONTROL')||String(role).includes('ILLUMINATOR'))?'FIRE_CONTROL':'SURFACE_SEARCH';
  const entries=registration.sensors.map((q,i)=>({id:String(q.id).toUpperCase(),order:(i+1)*10,category:category(q.role),
    outputKind:'REGISTERED_INACTIVE',physicalEmission:false,installed:false,active:false,
    system:q.system,nato:q.nato??null,role:q.role,hardpointM:{x:q.simPosM[0],y:q.simPosM[1],z:q.simPosM[2]},
    confidence:q.confidence,provenance:q.basis??'MODEL_REGISTRATION'}));
  return {schema:'AEGIS_SHIP_EMITTER_EQUIPMENT_A_1',registryId:'SOV956_REGISTERED_INACTIVE_EMITTERS_A',profileId:'SOVREMENNY_956',
    physicalEmission:false,categories:SHIP_EMITTER_CATEGORIES_A,entries,
    mutableStateOwner:'NONE_NOT_INSTALLED',outputContract:'NO_PHYSICAL_EMISSION__NO_ESM_OUTPUT__NO_OWN_DETECTION',
    provenance:'SOV_A_EXISTING_MODEL_REGISTRATION_ONLY__UNVERIFIED_AND_INACTIVE'};
}
