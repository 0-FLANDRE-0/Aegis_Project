// GUN_B1: fictional game settings, NOT measured Mk187/MK419 performance.
// All new numeric settings below are SIM_TUNED (PREIMPLEMENTATION.md).
const GUN_B1_SPEC=deepFreezeShipProfileV48Wip09({
 provenance:'SIM_TUNED_GAME_ONLY',mffShareOfHe:.5,armDistanceM:430,proxRadiusM:25,etMarginS:.2,
 fragmentQueryRadiusM:120,clutterAltitudeScaleM:12,clutterHazardPerS:.004,clutterIncidenceFloor:.15,clutterSeedSalt:0x419b1001,
 maxMeasurementAgeS:3,readyAgeS:1.5,maxPositionSigmaM:150,readyPositionSigmaM:30,maxVelocitySigmaMps:30,readyVelocitySigmaMps:8,maxTofS:40,readyTofS:20,
 autoRangeM:9000,autoTtcHysteresisS:1,diagnosticLogLimit:256,
 fragments:{id:'127_HE_MFP_FICTIONAL_GAME',provenance:'SIM_TUNED_GAME_ONLY',explosiveMassKg:3.7,caseMassKg:9,gurneyDrivenMassKg:9,fragmentCount:1200,avgFragmentMassKg:.0075,gurneyMps:2200,effectiveFragmentFraction:1,annularBandHalfAngleDeg:55,coneHalfAngleDeg:55}
});
function gunB1Mod4Module(base,id=base.id){return {...base,id,
 sourceBasis:{...base.sourceBasis,cgMount:'USNI_2008_CRUISER_UPDATES__NAVY_MK45_FACT_FILE_CG52_MOD4',gunB1:'SIM_TUNED_GAME_ONLY'},
 ammunition:{...base.ammunition,MFF_127_SIM:{...base.ammunition.HE_127_SIM,id:'MFF_127_SIM',label:'127 HE-MFP',fuzeMode:'AIR',fuzeProfile:'MK419_GAME_AIR_B1',explosiveMassKg:GUN_B1_SPEC.fragments.explosiveMassKg,provenance:'SIM_TUNED_GAME_ONLY'}},
 magazine:{...base.magazine,initialRounds:{HE_127_SIM:180,SAP_127_SIM:240,MFF_127_SIM:180}}};}
