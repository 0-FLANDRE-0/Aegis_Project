// Diagnostic-only resolver call counter. Never shipped in the product.
function emitterAResolverCallProbeA(allyProfileId=null){
  if(allyProfileId){
    const config={...MULTISHIP_DEPLOYMENT_STATE_A.draft,targetShip:'NONE',enemyAircraftEnabled:false,
      allyProfileId,enemyProfileId:null,neutralProfileId:null,allyEmcon:false,enemyEmcon:false};
    applyDeploymentA(prepareDeploymentA(config));
  }
  emconActive=false;
  const ships=electronicShipsF();
  for(const r of ships){const o=observerC(r);Object.assign(o.enabled,{SPY:true,SPQ:true,NAV:true});o.emcon=false;}
  const originalLegacy=electronicShipPhysicalEmittersLegacyA;
  const originalDeclared=electronicShipPhysicalEmittersDeclaredA;
  let legacyCalls=0,declaredCalls=0;
  electronicShipPhysicalEmittersLegacyA=function(r){legacyCalls++;return originalLegacy(r);};
  electronicShipPhysicalEmittersDeclaredA=function(r){declaredCalls++;return originalDeclared(r);};
  try{
    const rngBefore=ships.map(r=>({id:r.entityId,rng:{...prepareElectronicF(r).rng}}));
    const output=electronicPhysicalEmittersF().map(emitterABaselineSerializeA);
    const rngAfter=ships.map(r=>({id:r.entityId,rng:{...prepareElectronicF(r).rng}}));
    return {schema:'AEGIS_EMITTER_A_RESOLVER_CALL_PROBE_1',mode:SHIP_EMITTER_MODE_A,
      shipCount:ships.length,legacyCalls,declaredCalls,rngBefore,rngAfter,
      rngExact:JSON.stringify(rngBefore)===JSON.stringify(rngAfter),output};
  }finally{
    electronicShipPhysicalEmittersLegacyA=originalLegacy;
    electronicShipPhysicalEmittersDeclaredA=originalDeclared;
  }
}
window.__EMITTER_A_CLOSURE_DIAG__=Object.freeze({resolverCalls:emitterAResolverCallProbeA});
