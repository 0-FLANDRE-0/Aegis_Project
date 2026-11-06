// RGM-84D HOJ is not confirmed by the public material used in this project.
// Capability provenance is ASSUMED_THREAT. Numerical behavior reuses the
// existing Kh-35U game abstraction without claiming real Harpoon performance.
const HARPOON_HOJ_C_PROFILE=Object.freeze({...ASM_SEEKER_PROFILES['Kh-35U'],id:'RGM84D_TERMINAL_HOJ_GAME_ABSTRACTION',
  capabilityProvenance:ASM_CUE_FEATURE_PROVENANCE_A.ASSUMED_THREAT,parameterProvenance:'SIM_TUNED_REUSE_EXISTING_GAME_ABSTRACTION'});
function harpoonHojEnabledC(){return asmCueFeatureEnabledA('RGM-84D','terminalHoj');}
function harpoonHojEmitterSignalC(m,s,p){
  const receiver={x:m.x,y:m.y,z:m.z,seekerOn:s.active,heading:m.yawRad,flight:{bodyPitch:m.pitchRad}},view={gimbalAz:s.azRelRad,gimbalEl:s.elRelRad};
  return asmHojEmitterSignal(receiver,view,p);
}
function harpoonUpdateHojC(m,dt){
  const s=m.seeker,p=HARPOON_HOJ_C_PROFILE;
  return seekerUpdateHojTrackU3(m,s,p,dt,{ensure:seekerEnsureHojStateU3,enabled:()=>s.active&&harpoonHojEnabledC(),
    signal:()=>harpoonHojEmitterSignalC(m,s,p),uniform:()=>harpoonRandomA(m),normal:()=>harpoonNoiseA(m)});
}
function harpoonHojGuidanceActiveC(m){
  const s=m.seeker,h=seekerEnsureHojStateU3(s);if(!harpoonHojEnabledC()||!h.valid||(h.mode!=='TRACK'&&h.mode!=='COAST'))return false;
  const rfFirm=!!(s.lock&&s.mode==='TRACK'&&s.missedS<Math.max(.05,HARPOON_PROFILE_A.sim.seekerCoastS*.65));return !rfFirm;
}
function harpoonHojSnapshotC(m){const h=seekerEnsureHojStateU3(m.seeker);return {enabled:harpoonHojEnabledC(),provenance:HARPOON_HOJ_C_PROFILE.capabilityProvenance,mode:h.mode,valid:h.valid,guidanceActive:harpoonHojGuidanceActiveC(m),everTracked:h.everTracked,everGuidance:h.everGuidance,lastDirectJOverN:h.lastDirectJOverN,rng:m.rng>>>0};}
