// Commit-D diagnostic-only SOV deployment probe. Never shipped in the product.
function emitterASovDeploymentSceneA(role){
  const config={...MULTISHIP_DEPLOYMENT_STATE_A.draft,targetShip:'NONE',enemyAircraftEnabled:false,
    allyProfileId:null,enemyProfileId:role==='ENEMY'?'SOVREMENNY_956':null,
    neutralProfileId:role==='NEUTRAL'?'SOVREMENNY_956':null,allyEmcon:false,enemyEmcon:false};
  applyDeploymentA(prepareDeploymentA(config));emconActive=false;
  const ships=electronicShipsF(),sov=ships.find(r=>r.profileId==='SOVREMENNY_956');
  if(!sov)throw Error('EMITTER_A_SOV_DEPLOYMENT_MISSING:'+role);
  for(const r of ships){
    const o=observerC(r);Object.assign(o.enabled,{SPY:true,SPQ:true,NAV:true});o.emcon=false;
    const e=prepareElectronicF(r);Object.assign(e,{noiseRequested:false,deceptionRequested:false});
    Object.assign(electronicAllocatorF(r),{noiseShare:0,deceptionShare:0,resourceUsed:0});
  }
  const rngBefore=ships.map(r=>({id:r.entityId,rng:{...prepareElectronicF(r).rng}}));
  const emitters=electronicPhysicalEmittersF();
  const rngAfter=ships.map(r=>({id:r.entityId,rng:{...prepareElectronicF(r).rng}}));
  const receiverRows=ships.map(r=>{const e=prepareElectronicF(r);e.rng.state=0x5a17c0de;e.rng.spare=null;
    const before={...e.rng},plots=electronicReceiverPlotsF(r,emitters),after={...e.rng};
    return {receiver:r.entityId,profileId:r.profileId,before,after,plots};});
  const observer=observerC(sov),attack=attackSnapshotH3().ships.find(q=>q.entityId===sov.entityId);
  return {schema:'AEGIS_EMITTER_A_SOV_SCENE_1',role,config,
    owners:ships.map(r=>({entityId:r.entityId,profileId:r.profileId,role:r.role})),sovEntityId:sov.entityId,
    sovCapabilities:resolveShipProfile('SOVREMENNY_956').capabilities,
    sovObserver:{enabled:{...observer.enabled},normals:observer.normals.length,tracks:observer.tracks.size,history:observer.history.length},
    sovAttack:attack,emitters:emitters.map(emitterABaselineSerializeA),
    sovEmitterCount:emitters.filter(q=>q.owner===sov.entityId).length,
    sovReceiver:receiverRows.find(q=>q.receiver===sov.entityId),receiverRows,rngBefore,rngAfter};
}
window.__EMITTER_A_D_DIAG__=Object.freeze({sovScene:emitterASovDeploymentSceneA});
