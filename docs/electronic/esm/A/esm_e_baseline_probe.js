// TEST_ONLY probe shared by EMCON_B baseline and ESM_A Commit-E candidate.
// It deliberately avoids all ESM_A symbols so the SOV snapshot is comparable.
function esmESovBaselineProbeA(){
  const profile=resolveShipProfile('SOVREMENNY_956'),id='ESM_E_SOV_PROBE',runtime=preparePhysicalShipB(createPreparedShipRuntimeA(profile,{entityId:id,role:'NEUTRAL'}));
  ENGAGEMENT_RUNTIME.ships.set(id,runtime);activatePhysicalShipB(runtime);prepareElectronicF(runtime);
  try{
    const hardpoints=Object.fromEntries(Object.entries(profile.geometry?.hardpoints??{}).filter(([key,value])=>/(band|mineral|mr184|moskit)/i.test(key+' '+(value?.name??''))).map(([key,value])=>[key,JSON.parse(JSON.stringify(value))]));
    return {profileId:profile.id,capabilities:JSON.parse(JSON.stringify(profile.capabilities)),equipment:JSON.parse(JSON.stringify(profile.equipment??null)),sensors:JSON.parse(JSON.stringify(profile.sensors??null)),weapons:JSON.parse(JSON.stringify(profile.weapons??null)),hardpoints,sovNoEquipment:sovNoEquipmentA(runtime),physicalEmitters:JSON.parse(JSON.stringify(electronicShipPhysicalEmittersDeclaredA(runtime))),contactCount:prepareElectronicF(runtime).contacts.size};
  }finally{retirePhysicalShipB(runtime);ENGAGEMENT_RUNTIME.ships.delete(id);}
}
window.__ESM_A_E_BASELINE__=Object.freeze({sov:esmESovBaselineProbeA});
