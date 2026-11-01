// TEST COPY ONLY / AFTER_ACTION_TRUTH_TEST_ONLY.
// No producer, NIS, filter, bank getter, mass rebuild or gameplay command here.
// The three __pairedCauseRead methods expose already-computed closure caches.
(() => {
  if(window.__TRACK_B_PAIRED_CAUSE__)throw Error('PAIRED_CAUSE_INSTALLED_TWICE');
  const rows=[],faults=[];let armed=false,ordinal=0,traceSerial=0;
  const own=(o,k)=>o==null?undefined:Object.getOwnPropertyDescriptor(o,k)?.value;
  function tree(o,depth=0){
    if(o===undefined)return null;
    if(o===null||['string','number','boolean'].includes(typeof o))return o;
    if(ArrayBuffer.isView(o))return Array.from(o);
    if(depth>5)return null;
    if(Array.isArray(o))return o.map(v=>tree(v,depth+1));
    // Existing plain data only. Getters and functions are never executed.
    if(typeof o==='object')return Object.fromEntries(Object.keys(o).filter(k=>Object.getOwnPropertyDescriptor(o,k)?.value!==undefined&&typeof own(o,k)!=='function').map(k=>[k,tree(own(o,k),depth+1)]));
    return null;
  }
  function pick(o,keys){return Object.fromEntries(keys.filter(k=>own(o,k)!==undefined).map(k=>[k,tree(own(o,k))]));}
  const trackKeys=['trackId','trackNumber','x','y','z','vx','vy','vz','_kfX','_kfP','_kfNis','_kfRejectedNis','_lastMeasurementStep','lastMeasurementS','lastUpdateSeen','sensorAge','sensorHits','sensorDetected','sensorSource','contributorsC','measurementSigmaM','confirmed','identity','classification','domain','ttl','memActive'];
  const missileKeys=['id','label','type','weaponType','alive','dead','x','y','z','vx','vy','vz','age','ageS','life','maxLife','phase','state','targetId','trackId','targetTrackId','_deathReason','launchTime','launchTimeS','launchStep','launchedAtS','_launchStep','_launchTimeS','_rngState','rngState','rng','seed','navigationSeed','guidanceCore','nav','ins','seeker'];
  function missilesState(a){return Array.from(a??[],m=>{
    const x=pick(m,missileKeys);
    for(const k of Object.keys(m))if(/rng|seed|launch|born|last.*fire|fire.*step/i.test(k)&&!Object.prototype.hasOwnProperty.call(x,k))x[k]=tree(own(m,k));
    return x;
  });}
  function localBanks(){return Array.from(CIWS_C55.banks,([id,b])=>({id,...pick(b,['rng','clockS','winner','status','reason','serial','searchPhase','mode','lastTick']),files:Array.from(b.files??[],([key,value])=>({key,value:tree(value)}))}));}
  function capture(phase){
    if(!armed)return;
    try{
      const phys=shipDynamicsV15?.__pairedCauseRead?.(),mass=shipMassLedgerV32?.__pairedCauseRead?.(),survival=floodAttitudePreviewV1.__pairedCauseRead();
      const b=typeof TRACK_B_DIAG==='undefined'?null:TRACK_B_DIAG;
      const trace=b?.enabled?b.records.filter(x=>x.serial>traceSerial).map(x=>({...x})):[];
      if(b)traceSerial=b.serial;
      rows.push({tag:'AFTER_ACTION_TRUTH_TEST_ONLY',phase,ordinal:ordinal++,step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT,
        rng:{global:SIM_RNG_STATE,visual:VIS_RNG_STATE,battlespace:BATTLESPACE_RNG_STATE,bme:BRIDGEMASTER_E_RNG_STATE,chaff:AIR_CHAFF_RNG_STATE,spySurface:SPY_SURFACE_RNG_STATE_WIP13B9,spySpare:SPY_SURFACE_RNG_SPARE_WIP13B9,spqSurface:SPQ9B_SURFACE_RNG_STATE_WIP13B1,rf:tree(SHIPBOARD_RADAR_RF_RNG_WIP13B13)},
        own:{shipHP,navigation:tree(shipNav),physics:phys?tree(phys.diagnostic):null,loading:phys?tree(phys.loading):null,stability:phys?pick(phys,['hydroAge','stabilityAge','stabilityReference']):null,survival:tree(survival),mass:mass?{...pick(mass,['dirty','revision','rebuilds','cacheHits','dirtyMarks','lastDirtyReason']),cache:mass.cache?{...pick(mass.cache,['revision','massKg','cgM','categoryMassKg','variableLoadKg','nodeCount']),nodes:mass.cache.nodes.map(n=>pick(n,['id','category','massKg','x','y','z']))}:null}:null},
        inventory:{vls:tree(vlsCells),ciws:ciws.map(m=>pick(m,['id','type','ammo','state','trackingTrackId','_gunAimRngState','_gunShotRngState']))},
        tracks:Array.from(tracks.values(),t=>pick(t,trackKeys)),c55:localBanks(),
        missiles:{sam:missilesState(missiles),ram:missilesState(ramMissiles),hostile:missilesState(enemyMissiles)},
        observers:Array.from(ENGAGEMENT_RUNTIME.ships.values(),r=>{const o=r.combatSystem.observerC,e=r.weapons.executionD;return {ship:r.entityId,navigation:tree(r.navigation),weaponRng:e?tree(e.weaponRng):null,observer:o?{rng:tree(o.rng),ticks:o.tickCount,lastTick:o.lastTick,cycles:o.cycles,rotors:tree(o.rotors),stats:tree(o.stats),tracks:Array.from(o.tracks.values(),t=>pick(t,trackKeys))}:null};}),
        association:{available:!!b,enabled:b?.enabled??false,serial:b?.serial??0,dropped:b?.dropped??0,records:trace}});
    }catch(e){faults.push({step:simStepCounter,message:String(e?.stack??e)});armed=false;}
  }
  const nativeFixedTick=simulateFixedTick;
  simulateFixedTick=function(...args){const value=nativeFixedTick.apply(this,args);capture('AFTER_FIXED_TICK');return value;};
  window.__TRACK_B_PAIRED_CAUSE__=Object.freeze({
    start(){if(armed||rows.length)throw Error('PAIRED_CAUSE_ALREADY_STARTED');armed=true;capture('PRE_FIXTURE');return {ready:true,step:simStepCounter,fixedDt:SIM_FIXED_DT,tag:'PASSIVE_TEST_COPY'};},
    stop(){armed=false;return {rows:rows.length,faults:tree(faults)};},
    read(){return {schema:'AEGIS_TRACK_B_PAIRED_CAUSE_TIMELINE_1',classification:'AFTER_ACTION_TRUTH_TEST_ONLY_NOT_SENSOR_INPUT',rows,faults,nativeFixedTickSource:String(nativeFixedTick)};}
  });
})();
