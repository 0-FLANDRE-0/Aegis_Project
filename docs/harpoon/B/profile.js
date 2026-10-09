// RGM-84D Block 1C. Public dimensions/architecture, explicit SIM-TUNED flight/RF.
const HARPOON_LAUNCH_REGISTRATION_A=deepFreezeShipProfileV48Wip09(await readBunkerAsset('harpoon-launch-registration'));
const HARPOON_MODEL_META_A=deepFreezeShipProfileV48Wip09(await readBunkerAsset('harpoon-model-meta'));
const HARPOON_MODEL_BUFFER_A=await readBunkerAsset('harpoon-model-geo',false);
const HARPOON_PROFILE_A=deepFreezeShipProfileV48Wip09({
  id:'RGM84D_BLOCK1C_B1',revision:'HARPOON_B1',family:'RGM-84D Harpoon Block 1C',
  architecture:'PRELAUNCH_TRACK_MEMORY_INS_RADAR_ALTIMETER_THEN_INDEPENDENT_ACTIVE_RF',
  dataLink:false,illuminatorRequired:false,automaticRelease:false,
  public:{lengthM:4.63,bodyLengthM:3.84,diameterM:.343,wingSpanM:.914,launchMassKg:690,
    bodyMassKg:540,nominalMach:.85,rangeKm:124,rangeSecondaryKm:140,warheadAssemblyKg:221,
    explosiveMassKg:97.5,jetMaxThrustN:3000,boosterThrustN:53000,boosterBurnS:2.9},
  sim:{minLaunchRangeKm:4,maxLaunchRangeKm:124,maxTrackAgeS:10,acquisitionBasketM:4000,
    cruiseSpeedMps:289,cruiseHeightM:15,terminalHeightM:5,boostPropellantKg:90,boosterDryKg:60,
    boosterBurnS:3.2,boosterAverageThrustN:48000,
    fuelKg:110,fuelFlowKgS:.245,wingDeployS:.42,tailDeployS:.35,releaseDoorDelayS:.18,
    releaseIntervalS:1.5,referenceCd:.48,wingAreaM2:.32,maxCl:1.6,maxNormalG:4,
    dragAreaM2:.0924,maxLifeS:600,navDriftMps:.08,altimeterErrorM:.12,
    seekerActivationRangeM:14000,seekerPeriodS:.1,seekerGimbalRad:Math.PI/4,
    seekerBeamHalfRad:8*Math.PI/180,seekerRangeM:18000,seekerReferenceRangeM:12000,
    seekerReferenceRcsM2:100,seekerReferenceSnr:12,seekerMinSnr:3,
    seekerRangeSigmaM:8,seekerAzSigmaRad:.035*Math.PI/180,seekerCoastS:4,
    seekerSearchBasketM:4000,seekerTrackGateM:350,fuzeArmS:5,fuzeArmDistanceM:800,
    fuzeDelayS:.015,explosiveTntFactor:1.1},
  evidence:{public:'PUBLIC_SECONDARY_DIMENSIONS_ARCHITECTURE_AND_COMPONENT_DATA',
    range:'CSIS_BLOCK_IC_124KM__DESIGNATION_SYSTEMS_RGM_D_APPROX_140KM_DIFFERENT_ESTIMATES',
    unknown:'RETIREMENT_DATE_CG52_LOADED_BLOCK_NOT_VERIFIED__USER_SELECTED_RGM84D',
    booster:'PUBLIC_REFERENCE_53KN_2P9S__USER_TUNED_3P2S_AT_48KN_MEAN_PRESERVES_TOTAL_IMPULSE',
    smoke:'USER_ASSUMED_HIGH_SMOKE_SOLID_PROPELLANT__VISUAL_ONLY',
    sim:'ALL_SEEKER_NUMBERS_AERO_AUTOPILOT_FUEL_ALLOCATION_NAV_ERRORS_ALTITUDES_AND_FUZE_NUMBERS_SIM_TUNED',
    sources:['https://www.designation-systems.net/dusrm/m-84.html','https://missilethreat.csis.org/missile/harpoon/',
      'https://man.fas.org/dod-101/sys/smart/agm-84.htm','https://www.seaforces.org/usnships/cg/CG-52-USS-Bunker-Hill.htm']}
});
function harpoonInstallationA(){
  const counter={A:0,B:0};return {moduleId:HARPOON_PROFILE_A.id,launcherType:'MK141',
    registrationSchema:HARPOON_LAUNCH_REGISTRATION_A.schema,
    tubes:HARPOON_LAUNCH_REGISTRATION_A.tubeRows.map(r=>({...r,id:'MK141-'+r.bank+(++counter[r.bank]),
      moduleName:'Mk 141('+r.bank+')',massCenterM:{x:(r.muzzle.x+r.rear.x)/2,y:(r.muzzle.y+r.rear.y)/2,z:(r.muzzle.z+r.rear.z)/2}}))};
}
