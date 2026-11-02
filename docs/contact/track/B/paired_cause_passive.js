// TEST COPY ONLY / AFTER_ACTION_TRUTH_TEST_ONLY.
// Numeric cache scalars, native updated-track kf6/NIS, and launch events only.
// No producer, NIS calculation, filter, bank getter, snapshot or rebuild call.
(() => {
  if(window.__TRACK_B_PAIRED_CAUSE__)throw Error('PAIRED_CAUSE_INSTALLED_TWICE');
  const rows=[],faults=[],seenSam=new Set(),seenRam=new Set(),seenTrackUpdates=new Map();
  let armed=false,ordinal=0,traceSerial=0,nativeFixedTick=null;
  const own=(o,k)=>o==null?undefined:Object.getOwnPropertyDescriptor(o,k)?.value;
  const scalar=v=>v==null||['number','string','boolean'].includes(typeof v);
  function pick(o,keys){const out={};for(const k of keys){const v=own(o,k);if(v!==undefined&&scalar(v))out[k]=v;}return out;}
  const navKeys=['x','y','heading','speed','targetSpeedKt','swayMps','turnRate','rudder','targetRudder','thrustN','accelerationMps2','telegraph','shaftRpm','propPitch'];
  function newMissiles(a,seen){const out=[];for(const m of a){if(seen.has(m.id))continue;seen.add(m.id);out.push(pick(m,['id','weaponType','type','label','assignedTargetId','targetTrackId','trackId','life','z','x','y','_launchStep','_launchTimeS']));}return out;}
  function trackUpdates(bank,ownerId){
    const out=[];
    for(const t of bank.values()){
      const id=t.trackId??t.id,key=String(ownerId)+':'+id;
      const signature=[t._lastMeasurementStep,t._kfNis,t._kfRejectedNis,t.sensorHits,t.sensorSource].join('|');
      if(seenTrackUpdates.get(key)===signature)continue;seenTrackUpdates.set(key,signature);
      const r={observer:ownerId,...pick(t,['trackId','trackNumber','_lastMeasurementStep','_kfNis','_kfRejectedNis','sensorHits','sensorSource','confirmed','identity','classification'])};
      if(t._kfX)r.kf6=Array.from(t._kfX);out.push(r);
    }
    return out;
  }
  function capture(phase){
    if(!armed)return;
    try{
      const phys=shipDynamicsV15?.__pairedCauseRead?.()??null,mass=shipMassLedgerV32?.__pairedCauseRead?.()??null,survival=floodAttitudePreviewV1.__pairedCauseRead();
      const b=typeof TRACK_B_DIAG==='undefined'?null:TRACK_B_DIAG;
      // Actual native records only. Keep batch summaries and decisions that
      // differ/hold/reject; no reconstructed NIS, producer or assignment call.
      const trace=b?.enabled?b.records.filter(x=>x.serial>traceSerial&&(x.decision==='BATCH'||x.decision==='HOLD'||x.decision==='SANITY_REJECT'||x.nativeTrackId!==x.proposedTrackId)).map(x=>({...x})):[];
      if(b)traceSerial=b.serial;
      const observers=[];
      for(const r of ENGAGEMENT_RUNTIME.ships.values()){
        const o=r.combatSystem.observerC,e=r.weapons.executionD;
        observers.push({ship:r.entityId,weaponRng:e?.weaponRng?pick(e.weaponRng,['state','spare','rng','seed']):null,observer:o?{ticks:o.tickCount,lastTick:o.lastTick,cycles:o.cycles,rng:pick(o.rng,Object.keys(o.rng)),rotors:pick(o.rotors,['SPQ','NAV']),trackCount:o.tracks.size,updates:trackUpdates(o.tracks,r.entityId)}:null});
      }
      const vls={};for(const [section,cells]of Object.entries(vlsCells)){vls[section]={};for(const c of cells){const k=c.destroyed?'DESTROYED':c.type;vls[section][k]=(vls[section][k]??0)+(k==='ESSM4'?c.essmCount:1);}}
      rows.push({tag:'AFTER_ACTION_TRUTH_TEST_ONLY',phase,ordinal:ordinal++,step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT,
        rng:{global:SIM_RNG_STATE,visual:VIS_RNG_STATE,battlespace:BATTLESPACE_RNG_STATE,bme:BRIDGEMASTER_E_RNG_STATE,chaff:AIR_CHAFF_RNG_STATE,spySurface:SPY_SURFACE_RNG_STATE_WIP13B9,spySpare:SPY_SURFACE_RNG_SPARE_WIP13B9,spqSurface:SPQ9B_SURFACE_RNG_STATE_WIP13B1,rf:pick(SHIPBOARD_RADAR_RF_RNG_WIP13B13,Object.keys(SHIPBOARD_RADAR_RF_RNG_WIP13B13))},
        own:{shipHP,navigation:pick(shipNav,navKeys),physics:phys,mass,survival},
        inventory:{vls,ciws:ciws.map(m=>pick(m,['id','type','ammo','state','trackingTrackId','_gunAimRngState','_gunShotRngState']))},
        tracks:{count:tracks.size,updates:trackUpdates(tracks,'PLAYER')},
        c55:Array.from(CIWS_C55.banks,([id,q])=>({id,files:q.files.size,...pick(q,['rng','winner','status','reason'])})),
        missiles:{samCount:missiles.length,ramCount:ramMissiles.length,hostileCount:enemyMissiles.length,newSam:newMissiles(missiles,seenSam),newRam:newMissiles(ramMissiles,seenRam)},
        observers,association:{available:!!b,enabled:b?.enabled??false,serial:b?.serial??0,dropped:b?.dropped??0,records:trace}});
    }catch(e){faults.push({step:simStepCounter,message:String(e?.stack??e)});armed=false;}
  }
  window.__TRACK_B_PAIRED_CAUSE__=Object.freeze({
    start(){if(armed||rows.length||nativeFixedTick)throw Error('PAIRED_CAUSE_ALREADY_STARTED');nativeFixedTick=simulateFixedTick;simulateFixedTick=function(...args){const value=nativeFixedTick.apply(this,args);capture('AFTER_FIXED_TICK');return value;};armed=true;capture('PRE_FIXTURE');return {ready:true,step:simStepCounter,fixedDt:SIM_FIXED_DT,tag:'PASSIVE_TEST_COPY'};},
    stop(){armed=false;return {rows:rows.length,faults};},
    info(){return {schema:'AEGIS_TRACK_B_PAIRED_CAUSE_TIMELINE_2',classification:'AFTER_ACTION_TRUTH_TEST_ONLY_NOT_SENSOR_INPUT',count:rows.length,faults,nativeFixedTickSource:String(nativeFixedTick),nativeBaseFixedTickSource:String(window.__TRACK_B_PAIRED_CAUSE_BASE_FN__)};},
    read(start,count){return rows.slice(start,start+count);}
  });
})();
