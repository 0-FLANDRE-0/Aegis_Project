// LIVE_CANONICAL: selection is receiver-owned track intent, not RF authority.
// EMCON remains radar-only; communications and Harpoon release policy are unchanged.
function releaseManualSelectionOwnershipF2(){
  wip119AutonomyState.lastOwnedLockId=null;
  wip124SemiLockState={trackId:null,sinceS:-Infinity,lastDisplay:null};
}
function applyEmconDesignationF2(on){
  const previous=emconActive;emconActive=!!on;
  if(emconActive){radar.pdTracking=false;radar.mode='TWS';radar.trkBreakTimer=0;releaseManualSelectionOwnershipF2();}
  else if(previous){const tr=tracks.get(selectedLockId);radar.pdTracking=!!tr&&trackIsDisplayable(tr)&&isInRadarSector(tr.x,tr.y,tr.z);radar.mode=radar.pdTracking?'PD':'TWS';radar.trkBreakTimer=0;if(tr)radar.trkQuality=tr.trackQuality??1;}
  setRadarHalfAngle();updateModeButtonLabel();return emconActive;
}
// DIAGNOSTIC_ONLY detached reader. No alternate selection/release authority.
function emconDesignationSnapshotF2(){const tr=tracks.get(selectedLockId);return {schema:'AEGIS_EMCON_DESIGNATION_F2_0',emcon:emconActive,selectedLockId,mode:radar.mode,pdTracking:radar.pdTracking,displayable:!!tr&&trackIsDisplayable(tr),insideSpySector:!!tr&&isInRadarSector(tr.x,tr.y,tr.z),physicalSpyEmitters:electronicPhysicalEmittersF().filter(q=>q.owner===ACTIVE_SHIP_RUNTIME.entityId&&q.band==='S'&&q.emitterClass==='SEARCH_RADAR').length,label:document.getElementById('lockBtn')?.textContent??null};}
window.__EMCON_DESIGNATION_F2__=Object.freeze({snapshot:emconDesignationSnapshotF2});
