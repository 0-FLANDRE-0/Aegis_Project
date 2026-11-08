// EMCON_B PR74 correction 3 — immutable profile-to-equipment bindings.
// consumerId is a ship-class-neutral capability requested by sensor code.
// equipmentId remains the exact physical registration owned by ShipProfile.
const EMCON_B_CONSUMER_SPEC=Object.freeze({
  AIR_SEARCH_VOLUME:Object.freeze({category:'AIR_SEARCH',outputKind:'RADAR'}),
  SURFACE_SEARCH_SCAN:Object.freeze({category:'SURFACE_SEARCH',outputKind:'RADAR'}),
  NAVIGATION_SCAN:Object.freeze({category:'NAV',outputKind:'RADAR'})
});
const EMCON_B_CONSUMER_IDS=Object.freeze(Object.keys(EMCON_B_CONSUMER_SPEC));
function emconConsumerBindingsForProfileB(profileId){
  const rows=profileId==='DDG_119_LATE_FLIGHT_IIA'?[
    {consumerId:'AIR_SEARCH_VOLUME',equipmentId:'AN_SPY_1DV'},
    {consumerId:'SURFACE_SEARCH_SCAN',equipmentId:'AN_SPQ_9B'},
    {consumerId:'NAVIGATION_SCAN',equipmentId:'BRIDGEMASTER_E'}
  ]:profileId==='CG_52_LATE_TICONDEROGA'?[
    {consumerId:'AIR_SEARCH_VOLUME',equipmentId:'AN_SPY_1A_MODERNIZED'},
    {consumerId:'SURFACE_SEARCH_SCAN',equipmentId:'AN_SPQ_9'},
    {consumerId:'NAVIGATION_SCAN',equipmentId:'AN_SPS_73'}
  ]:profileId==='SOVREMENNY_956'?[]:null;
  if(rows===null)throw Error('EMCON_CONSUMER_PROFILE_UNSUPPORTED:'+profileId);
  return Object.freeze(rows.map(q=>Object.freeze({...q})));
}
