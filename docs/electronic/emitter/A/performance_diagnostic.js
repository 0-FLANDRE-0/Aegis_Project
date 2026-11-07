// Diagnostic-only microbenchmark of the existing physical emitter query.
function emitterAPerformanceProbeA(iterations=50000){
  iterations=Math.max(1000,Math.min(200000,Math.trunc(iterations)));
  const o=observerC(ACTIVE_SHIP_RUNTIME),saved={emconActive,enabled:{...o.enabled},noiseJamActive,deceptJamActive};
  try{
    emconActive=false;Object.assign(o.enabled,{SPY:true,SPQ:true,NAV:true});noiseJamActive=false;deceptJamActive=false;
    for(let i=0;i<500;i++)electronicPhysicalEmittersF();
    const rngBefore=electronicShipsF().map(r=>({id:r.entityId,rng:{...prepareElectronicF(r).rng}}));
    const started=performance.now();let rows=null;
    for(let i=0;i<iterations;i++)rows=electronicPhysicalEmittersF();
    const elapsedMs=performance.now()-started;
    const rngAfter=electronicShipsF().map(r=>({id:r.entityId,rng:{...prepareElectronicF(r).rng}}));
    return {schema:'AEGIS_EMITTER_A_PERFORMANCE_PROBE_1',iterations,elapsedMs,nsPerCall:elapsedMs*1e6/iterations,
      outputRows:rows.map(emitterABaselineSerializeA),rngUnchanged:JSON.stringify(rngBefore)===JSON.stringify(rngAfter)};
  }finally{emconActive=saved.emconActive;Object.assign(o.enabled,saved.enabled);noiseJamActive=saved.noiseJamActive;deceptJamActive=saved.deceptJamActive;}
}
window.__EMITTER_A_PERF__=Object.freeze({run:emitterAPerformanceProbeA});
