// TEST_ONLY: PR74 correction-3 ship-class-neutral consumer binding probes.
// Injected only into the disposable diagnostic HTML.
function emconCorr3TraceB(r){
  const calls=[],original=emconConsumerAllowsB;
  try{
    emconConsumerAllowsB=(owner,consumerId)=>{calls.push({ownerEntityId:owner?.entityId??null,consumerId});return original(owner,consumerId);};
    const sensors=emconCorr2SensorPassB(r);friendlyIffPlotsF(r);heloMeasureIffRepliesE(r);return {calls,sensors};
  }finally{emconConsumerAllowsB=original;}
}
function emconCorr3CurrentB(id){
  const r=ENGAGEMENT_RUNTIME.ships.get(String(id));if(!r)throw Error('EMCON_CORR3_OWNER');
  emconCommandB(r.entityId,{reset:true},'DIAGNOSTIC');networkSetRadarG(r,false);
  const registry=shipEmitterRegistryA(r),bindings=EMCON_B_CONSUMER_IDS.map(consumerId=>{const q=emconResolveConsumerBindingB(r,consumerId),{entry,...view}=q;return view;});
  return {schema:'AEGIS_EMCON_B_CORRECTION_3_CURRENT_1',ownerEntityId:r.entityId,profileId:r.profileId,registryId:registry.registryId,validation:emconConsumerBindingsValidateB(r),bindings,trace:emconCorr3TraceB(r)};
}
function emconCorr3VirtualFixtureB(){
  const base=ACTIVE_SHIP_RUNTIME,baseProfile=resolveShipProfile(base.profileId),mount={...baseProfile.geometry.hardpoints.bridgeMasterE,name:baseProfile.geometry.hardpoints.bridgeMasterE.name};
  const sensor={...baseProfile.sensors.bridgeMasterE,band:'X',frequencyMHz:9400,nominalRpm:24,horizontalBeamwidthDeg:1.5,verticalBeamwidthDeg:12};
  const entry=(id,order,category,key,system)=>({id,order,category,outputKind:'RADAR',enabledKey:key,sensorKey:key,hardpointKey:key,mountKind:'PROFILE_HARDPOINT',bandMode:'SENSOR_PROFILE',band:'X',power:100,powerProvenance:'DIAGNOSTIC_ONLY',family:system.toUpperCase(),emitterClass:'SEARCH_RADAR',rotorKey:key,beamwidthField:'horizontalBeamwidthDeg',rpmField:'nominalRpm',double:false,system,provenance:'DIAGNOSTIC_ONLY_NON_VENDOR_PROFILE'});
  const entries=[
    entry('VOLUME_ARRAY_ALPHA',10,'AIR_SEARCH','VOLUME_ARRAY','Volume Array Alpha'),
    entry('VOLUME_ARRAY_DECOY',11,'AIR_SEARCH','VOLUME_DECOY','Volume Array Decoy'),
    entry('SURFACE_SCANNER_BETA',20,'SURFACE_SEARCH','SURFACE_SCANNER','Surface Scanner Beta'),
    entry('NAV_SCANNER_GAMMA',30,'NAV','NAV_SCANNER','Navigation Scanner Gamma')
  ];
  const bindings=[
    {consumerId:'AIR_SEARCH_VOLUME',equipmentId:'VOLUME_ARRAY_ALPHA'},
    {consumerId:'SURFACE_SEARCH_SCAN',equipmentId:'SURFACE_SCANNER_BETA'},
    {consumerId:'NAVIGATION_SCAN',equipmentId:'NAV_SCANNER_GAMMA'}
  ];
  const registry={schema:'AEGIS_SHIP_EMITTER_EQUIPMENT_A_1',registryId:'VIRTUAL_NON_VENDOR_EMITTERS_C3',profileId:'VIRTUAL_NON_VENDOR_C3',physicalEmission:true,categories:SHIP_EMITTER_CATEGORIES_A,consumerBindings:bindings,entries,mutableStateOwner:'DIAGNOSTIC_ONLY',outputContract:'AEGIS_RECEIVER_EW_F_1_LEGACY_EXACT'};
  const profile=Object.freeze({id:'VIRTUAL_NON_VENDOR_C3',geometry:{hardpoints:{VOLUME_ARRAY:mount,VOLUME_DECOY:mount,SURFACE_SCANNER:mount,NAV_SCANNER:mount}},sensors:{VOLUME_ARRAY:sensor,VOLUME_DECOY:sensor,SURFACE_SCANNER:sensor,NAV_SCANNER:sensor},equipment:{emitters:registry,ew:{pods:[]}}});
  const o=observerC(base),observer={...o,profile,enabled:{...o.enabled,VOLUME_ARRAY:true,VOLUME_DECOY:true,SURFACE_SCANNER:true,NAV_SCANNER:true},rotors:{...o.rotors,VOLUME_ARRAY:0,VOLUME_DECOY:0,SURFACE_SCANNER:0,NAV_SCANNER:0}};
  const runtime={...base,entityId:'DIAG_VIRTUAL_NON_VENDOR_C3',profileId:profile.id,role:'ALLY',faction:'FRIENDLY',navigation:{...base.navigation,positionWorld:{...base.navigation.positionWorld}},geometry:base.geometry??geometryForShipProfileA(baseProfile),hitHistory:[],
    survival:{snapshot:()=>({equipmentOffline:false,heelRad:0,trimRad:0,heaveM:0})},crew:{offline:()=>false},flooding:{readDamage:()=>0},
    combatSystem:{...base.combatSystem,observerC:observer,emconB:null},ew:{...base.ew,executionF:{...prepareElectronicF(base)},slq32Allocator:{...slq32EaState}}};
  return {profile,runtime,registry,bindings};
}
function emconCorr3WithVirtualB(run){
  const fixture=emconCorr3VirtualFixtureB(),originalResolve=resolveShipProfile,originalMembers=fleetMembersG,originalOwner=fleetOwnerG,originalSelect=fleetSelectG;
  try{
    resolveShipProfile=id=>String(id)===fixture.profile.id?fixture.profile:originalResolve(id);
    fixture.runtime.combatSystem.emconB=emconDefaultStateB(fixture.runtime);
    fleetMembersG=()=>[fixture.runtime];fleetOwnerG=()=>fixture.runtime;fleetSelectG=()=>true;
    return run(fixture);
  }finally{resolveShipProfile=originalResolve;fleetMembersG=originalMembers;fleetOwnerG=originalOwner;fleetSelectG=originalSelect;}
}
function emconCorr3VirtualB(){return emconCorr3WithVirtualB(({profile,runtime:r,registry,bindings})=>{
  const defaultRows=electronicShipPhysicalEmittersDeclaredA(r),validation=emconConsumerBindingsValidateB(r),resolved=EMCON_B_CONSUMER_IDS.map(id=>{const q=emconResolveConsumerBindingB(r,id),{entry,...view}=q;return view;});
  const ui=emconCreatePolicyUiB();document.body.append(ui.root);ui.refresh();const uiText=ui.root.textContent,uiSnapshot=ui.snapshot();ui.root.remove();
  const originalState=structuredClone(r.combatSystem.emconB);r.combatSystem.emconB={...structuredClone(originalState),allRadiationSilent:true,allRadiationRestoreMasterSilent:false,revision:originalState.revision+1};const hardRows=electronicShipPhysicalEmittersDeclaredA(r);
  r.combatSystem.emconB=emconBreakoutStateB(r,{equipmentId:'SURFACE_SCANNER_BETA'});const breakoutRows=electronicShipPhysicalEmittersDeclaredA(r),breakoutDecisions=registry.entries.map(q=>emconEquipmentDecisionB(r,q.id));
  r.combatSystem.emconB=structuredClone(originalState);r.combatSystem.emconB.equipmentOverride.VOLUME_ARRAY_ALPHA='FORCE_SILENT';const categoryAllows=emconCategoryAllowsB(r,'AIR_SEARCH'),consumerDecision=emconConsumerDecisionB(r,'AIR_SEARCH_VOLUME'),bypassRows=electronicShipPhysicalEmittersDeclaredA(r);
  const failure=(name,rows,consumerId)=>{const saved=profile.equipment.emitters.consumerBindings;profile.equipment.emitters.consumerBindings=rows;const q=emconResolveConsumerBindingB(r,consumerId),before=JSON.stringify(r.combatSystem.emconB);let restoreError=null;try{emconRestoreStateB(r,structuredClone(r.combatSystem.emconB));}catch(err){restoreError=String(err.message);}const after=JSON.stringify(r.combatSystem.emconB);profile.equipment.emitters.consumerBindings=saved;const {entry,...view}=q;return {name,decision:view,restoreError,zeroMutation:before===after};};
  // The fixture is intentionally mutable only inside this diagnostic so malformed
  // profile bindings can be tested without touching the frozen product profiles.
  const failures=[
    failure('MISSING',bindings.filter(q=>q.consumerId!=='NAVIGATION_SCAN'),'NAVIGATION_SCAN'),
    failure('AMBIGUOUS',[...bindings,{consumerId:'AIR_SEARCH_VOLUME',equipmentId:'VOLUME_ARRAY_DECOY'}],'AIR_SEARCH_VOLUME'),
    failure('NONEXISTENT',bindings.map(q=>q.consumerId==='SURFACE_SEARCH_SCAN'?{...q,equipmentId:'NO_SUCH_EQUIPMENT'}:q),'SURFACE_SEARCH_SCAN')
  ];
  r.combatSystem.emconB=originalState;
  return {schema:'AEGIS_EMCON_B_CORRECTION_3_VIRTUAL_1',profileId:profile.id,registryId:registry.registryId,profileRegistrationText:JSON.stringify({id:profile.id,emitters:registry}),validation,resolved,ui:{text:uiText,snapshot:uiSnapshot},defaultRows,hardRows,breakout:{rows:breakoutRows,decisions:breakoutDecisions},sameCategoryIsolation:{categoryAllows,consumerDecision,rows:bypassRows},failures};
});}
window.__EMCON_B_CORRECTION_3__=Object.freeze({current:emconCorr3CurrentB,virtual:emconCorr3VirtualB});
