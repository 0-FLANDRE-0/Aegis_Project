// FRIENDLY_CONTACT_A: measurement capability, never entity/owner/class truth.
// The existing track hard lifetime bounds retained 3-D observation evidence.
function trackHasAirObservationFC(tr){
 return Number.isFinite(tr?._radar3dAirStepFC)&&(simStepCounter-tr._radar3dAirStepFC)*SIM_FIXED_DT<=TRACK_HARD_TTL;
}
function trackNoteAirObservationFC(tr){
 tr._radar3dAirStepFC=simStepCounter;tr._surface2DOnlyFC=false;
 // A subsequently accepted 3-D observation supersedes a 2-D height prior.
 tr._surfaceMotionPriorWip13B13=false;
}
