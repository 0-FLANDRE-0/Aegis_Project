// Automatic tube selection only. Manual surface-release authority remains mandatory.
// Candidates contain ship launcher geometry and observed track memory, never target truth.
function harpoonRankTubesD(gates){
  let best=null;
  for(const gate of gates){
    if(!gate.ok)continue;
    const aim=harpoonPredictionA(gate.memory,0,gate.muzzleM),
      turnRad=Math.abs(angNorm(Math.atan2(aim.y-gate.muzzleM.y,aim.x-gate.muzzleM.x)-Math.atan2(gate.axis.y,gate.axis.x)));
    // Profile order is the deterministic tie break; tube IDs and physical slots never move.
    if(Number.isFinite(turnRad)&&(!best||turnRad<best.turnRad-1e-9))best={gate,turnRad};
  }
  return best;
}
function harpoonAutoTubeGateD(trackId=selectedLockId,options={}){
  const r=harpoonRuntimeA(),bad=reason=>({ok:false,reason,tubeId:null,truthUsed:false,selectionMode:'AUTO'});
  // Once a door starts opening, pin that exact tube. Release rechecks it independently.
  if(r.pending)return {...bad('RELEASE_PENDING'),tubeId:r.pending.tubeId};
  if(!r.tubes.length)return bad('MK141_NOT_INSTALLED');
  const loaded=r.tubes.filter(t=>t.loaded);if(!loaded.length)return bad('TUBE_EMPTY');
  // Preview tube eligibility during cooldown; the final gate still enforces cooldown.
  // actualRelease bypasses only pending/cooldown, never identity, damage or geometry.
  const gates=loaded.map(t=>harpoonGateA(trackId,t.id,{...options,actualRelease:true})),best=harpoonRankTubesD(gates);
  if(!best)return bad(gates[0].reason);
  return {...harpoonGateA(trackId,best.gate.tubeId,options),tubeId:best.gate.tubeId,
    turnRad:best.turnRad,selectionMode:'AUTO'};
}
function harpoonTubeSelectionAuditD(){
  const gate=(id,heading,ok=true)=>({ok,tubeId:id,muzzleM:{x:0,y:0,z:20},axis:{x:Math.cos(heading),y:Math.sin(heading),z:.7},
    memory:{stateAgeS:0,positionM:{x:10000,y:0,z:0},velocityMps:{x:0,y:0,z:0}}}),
    rows=[gate('A1',Math.PI),gate('B1',0),gate('B2',0)],before=JSON.stringify(rows),
    preferred=harpoonRankTubesD(rows),fallback=harpoonRankTubesD([rows[0],{...rows[1],ok:false}]);
  const checks={leastObservedTurn:preferred.gate.tubeId==='B1'&&preferred.turnRad===0,
    stableTubeTieBreak:harpoonRankTubesD([rows[1],rows[2]]).gate.tubeId==='B1',
    blockedTubeSkipped:fallback.gate.tubeId==='A1',noEligibleTube:harpoonRankTubesD([{...rows[0],ok:false}])===null,
    emptyInstallation:harpoonRankTubesD([])===null,detachedInputUnchanged:before===JSON.stringify(rows)};
  return {schema:'HARPOON_D_SELECTION_AUDIT',checks,pass:Object.values(checks).every(Boolean)};
}
