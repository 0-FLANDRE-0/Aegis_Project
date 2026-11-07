// EMITTER_A common runtime resolver. __MODE__ is replaced at build time.
const SHIP_EMITTER_MODE_A='__MODE__';
const SHIP_EMITTER_AUDIT_A={schema:'AEGIS_SHIP_EMITTER_SHADOW_A_1',mode:SHIP_EMITTER_MODE_A,comparisons:0,mismatches:0,
  perProfile:{},examples:[],rngConsumed:false,tacticalOutputUsed:SHIP_EMITTER_MODE_A==='ACTIVE'};
function shipEmitterRegistryA(r){return resolveShipProfile(r.profileId).equipment?.emitters??null;}
function shipEmitterRegistryValidateA(profile){
  const registry=profile.equipment?.emitters;if(!registry)return {ok:false,reason:'NO_REGISTRY'};
  const ids=new Set(),orders=new Set();
  for(const q of registry.entries){
    if(!q||typeof q.id!=='string'||ids.has(q.id)||!Number.isFinite(q.order)||orders.has(q.order)||!SHIP_EMITTER_CATEGORIES_A.includes(q.category))return {ok:false,reason:'ENTRY_SCHEMA'};
    ids.add(q.id);orders.add(q.order);
  }
  return {ok:true,reason:null,profileId:profile.id,registryId:registry.registryId,physicalEmission:registry.physicalEmission,entries:registry.entries.length};
}
function electronicShipPhysicalEmittersLegacyA(r){
  const out=[];
  if(sovNoEquipmentA(r))return out;const own=r===ACTIVE_SHIP_RUNTIME,o=observerC(r),silent=own?emconActive:o.emcon;
  if(!silent&&!shipEquipmentOfflineV1(r)){
    const p=resolveShipProfile(r.profileId),spy=o.normals.filter(q=>observerHealthC(r,q.moduleName)>.05);
    if(o.enabled.SPY&&spy.length)out.push({owner:r.entityId,point:observerMountC(r,spy[0].center),band:'S',frequencyMHz:Number.isFinite(p.sensors.spy1dv.frequencyMHz)?p.sensors.spy1dv.frequencyMHz:null,frequencyProvenance:Number.isFinite(p.sensors.spy1dv.frequencyMHz)?'EXISTING_EMITTER_PROFILE':'SIM_TUNED_BAND_CENTER',power:2500,family:'SHIP SEARCH RADAR',emitterClass:'SEARCH_RADAR',beamAz:null});
    for(const [key,hp]of [['SPQ','spq9b'],['NAV','bridgeMasterE']]){const spec=p.sensors[hp];if(o.enabled[key]&&observerHealthC(r,p.geometry.hardpoints[hp].name)>.05&&shipSystemDamageB(r,'MAST')<80)out.push({owner:r.entityId,point:observerMountC(r,p.geometry.hardpoints[hp]),band:key==='SPQ'?'IJ':electronicBandF(spec.band),frequencyMHz:Number.isFinite(spec.frequencyMHz)?spec.frequencyMHz:null,frequencyProvenance:Number.isFinite(spec.frequencyMHz)?'EXISTING_EMITTER_PROFILE':'SIM_TUNED_BAND_CENTER',power:key==='SPQ'?650:120,family:key==='SPQ'?'SURFACE SEARCH RADAR':'NAVIGATION RADAR',emitterClass:'SEARCH_RADAR',beamAz:r.navigation.heading+(own?(key==='SPQ'?spq9bRotorAngle:bridgeMasterERotorAngle):o.rotors[key]),beamwidthDeg:key==='SPQ'?.6:spec.horizontalBeamwidthDeg,beamwidthProvenance:key==='SPQ'?'SIM_TUNED_EXISTING_OBSERVATION_MODEL':String(spec.performanceBasis||spec.source||'EXISTING_EMITTER_PROFILE'),rpm:Number(spec.rpm??spec.nominalRpm),double:key==='SPQ'});}
  }
  const a=electronicAllocatorF(r),settings=electronicSettingsF(r),pods=electronicPodsF(r);
  if(a.resourceUsed>.001&&(settings.noiseRequested||settings.deceptionRequested)&&pods.length)out.push({owner:r.entityId,ship:r,point:observerMountC(r,pods[0].center),band:'IJ',power:2000*a.resourceUsed,family:'RF INTERFERENCE',emitterClass:'JAMMER',beamAz:settings.bearingRad});
  return out;
}
function electronicShipPhysicalEmittersDeclaredA(r){
  const out=[],registry=shipEmitterRegistryA(r);
  if(sovNoEquipmentA(r)||registry?.physicalEmission===false)return out;
  if(!registry)throw Error('SHIP_EMITTER_REGISTRY_REQUIRED:'+r.profileId);
  const own=r===ACTIVE_SHIP_RUNTIME,o=observerC(r),silent=own?emconActive:o.emcon,p=resolveShipProfile(r.profileId);
  if(!silent&&!shipEquipmentOfflineV1(r)){
    const spy=o.normals.filter(q=>observerHealthC(r,q.moduleName)>.05);
    for(const q of registry.entries){
      if(q.outputKind!=='RADAR'||!o.enabled[q.enabledKey])continue;
      const spec=p.sensors[q.sensorKey];
      if(q.mountKind==='FIRST_HEALTHY_SPY_FACE'){
        if(spy.length)out.push({owner:r.entityId,point:observerMountC(r,spy[0].center),band:q.band,frequencyMHz:Number.isFinite(spec.frequencyMHz)?spec.frequencyMHz:null,frequencyProvenance:Number.isFinite(spec.frequencyMHz)?'EXISTING_EMITTER_PROFILE':'SIM_TUNED_BAND_CENTER',power:q.power,family:q.family,emitterClass:q.emitterClass,beamAz:null});
        continue;
      }
      const hp=p.geometry.hardpoints[q.hardpointKey];
      if(observerHealthC(r,hp.name)>.05&&shipSystemDamageB(r,'MAST')<80)out.push({owner:r.entityId,point:observerMountC(r,hp),band:q.bandMode==='FIXED'?q.band:electronicBandF(spec.band),frequencyMHz:Number.isFinite(spec.frequencyMHz)?spec.frequencyMHz:null,frequencyProvenance:Number.isFinite(spec.frequencyMHz)?'EXISTING_EMITTER_PROFILE':'SIM_TUNED_BAND_CENTER',power:q.power,family:q.family,emitterClass:q.emitterClass,beamAz:r.navigation.heading+(own?(q.rotorKey==='SPQ'?spq9bRotorAngle:bridgeMasterERotorAngle):o.rotors[q.rotorKey]),beamwidthDeg:q.beamwidthDeg??spec[q.beamwidthField],beamwidthProvenance:q.beamwidthProvenance??String(spec.performanceBasis||spec.source||'EXISTING_EMITTER_PROFILE'),rpm:Number(spec[q.rpmField]),double:q.double});
    }
  }
  const a=electronicAllocatorF(r),settings=electronicSettingsF(r),pods=electronicPodsF(r),ecm=registry.entries.find(q=>q.outputKind==='ECM');
  if(ecm&&a.resourceUsed>.001&&(settings.noiseRequested||settings.deceptionRequested)&&pods.length)out.push({owner:r.entityId,ship:r,point:observerMountC(r,pods[0].center),band:ecm.band,power:ecm.powerPerResource*a.resourceUsed,family:ecm.family,emitterClass:ecm.emitterClass,beamAz:settings.bearingRad});
  return out;
}
function shipEmitterEqualA(a,b){
  if(Object.is(a,b))return true;if(!a||!b||typeof a!=='object'||typeof b!=='object')return false;
  const ak=Object.keys(a),bk=Object.keys(b);if(ak.length!==bk.length||ak.some((k,i)=>k!==bk[i]))return false;
  return ak.every(k=>shipEmitterEqualA(a[k],b[k]));
}
function shipEmitterComparableA(rows){return rows.map(row=>Object.fromEntries(Object.entries(row).map(([k,v])=>[k,k==='ship'?v?.entityId??null:v])));}
function shipEmitterShadowCompareA(r,legacy,declared){
  SHIP_EMITTER_AUDIT_A.comparisons++;const p=SHIP_EMITTER_AUDIT_A.perProfile[r.profileId]??={comparisons:0,mismatches:0};p.comparisons++;
  if(shipEmitterEqualA(legacy,declared))return;
  SHIP_EMITTER_AUDIT_A.mismatches++;p.mismatches++;
  if(SHIP_EMITTER_AUDIT_A.examples.length<32)SHIP_EMITTER_AUDIT_A.examples.push({profileId:r.profileId,entityId:r.entityId,legacy:shipEmitterComparableA(legacy),declared:shipEmitterComparableA(declared)});
}
function shipEmitterRuntimeSnapshotA(r){
  const o=observerC(r),settings=electronicSettingsF(r),a=electronicAllocatorF(r);
  return {schema:'AEGIS_SHIP_EMITTER_RUNTIME_A_1',entityId:r.entityId,profileId:r.profileId,registryId:shipEmitterRegistryA(r)?.registryId??null,
    stateOwners:{radar:'ShipRuntime.observerC',ecm:'ShipRuntime.ew'},enabled:{...o.enabled},emcon:r===ACTIVE_SHIP_RUNTIME?emconActive:o.emcon,
    rotors:{SPQ:r===ACTIVE_SHIP_RUNTIME?spq9bRotorAngle:o.rotors.SPQ,NAV:r===ACTIVE_SHIP_RUNTIME?bridgeMasterERotorAngle:o.rotors.NAV},
    ecm:{noiseRequested:settings.noiseRequested,deceptionRequested:settings.deceptionRequested,bearingRad:settings.bearingRad,resourceUsed:a.resourceUsed},
    duplicateMutableState:false};
}
function electronicPhysicalEmittersF(){
  const out=[];
  for(const r of electronicShipsF()){
    const legacy=electronicShipPhysicalEmittersLegacyA(r);
    if(SHIP_EMITTER_MODE_A==='SHADOW'){
      const declared=electronicShipPhysicalEmittersDeclaredA(r);shipEmitterShadowCompareA(r,legacy,declared);out.push(...legacy);
    }else out.push(...electronicShipPhysicalEmittersDeclaredA(r));
  }
  for(const t of targetPool)if(t.alive&&t.radarOn)out.push({point:{x:t.x,y:t.y,z:t.z??1000},band:'IJ',power:900,family:'AIR SEARCH RADAR',emitterClass:'SEARCH_RADAR',beamAz:null});
  for(const m of new Set([...enemyMissiles,...navalFlightObjectsD()])){
    const active=m.weaponKey==='HARPOON'?m.seeker?.active:m.seekerOn??(m.isARH&&m.seekerActive);
    if((m.alive===false||m.dead)||!active)continue;
    out.push({point:{x:m.x,y:m.y,z:m.z??5},band:'IJ',power:35,family:(m.seekerLocked||m.seeker?.mode==='TRACK')?'MISSILE SEEKER TRACK':'MISSILE SEEKER SEARCH',emitterClass:'ACTIVE_SEEKER',beamAz:m.heading??0,owner:m.ownerEntityId});
  }
  for(const q of nulkaEntities15B())if(q.alive&&q.payloadActive)out.push({point:{x:q.x,y:q.y,z:q.z},band:'IJ',power:200*(q.rfGain01??1),family:'RF INTERFERENCE',emitterClass:'JAMMER',beamAz:null,owner:q.ownerEntityId});
  return out;
}
function shipEmitterAuditSnapshotA(){return {schema:SHIP_EMITTER_AUDIT_A.schema,mode:SHIP_EMITTER_MODE_A,comparisons:SHIP_EMITTER_AUDIT_A.comparisons,mismatches:SHIP_EMITTER_AUDIT_A.mismatches,perProfile:structuredClone(SHIP_EMITTER_AUDIT_A.perProfile),examples:structuredClone(SHIP_EMITTER_AUDIT_A.examples),rngConsumed:false,tacticalOutputUsed:SHIP_EMITTER_MODE_A==='ACTIVE'};}
window.__SHIP_EMITTERS_A__=Object.freeze({schema:'AEGIS_SHIP_EMITTER_PUBLIC_A_1',mode:SHIP_EMITTER_MODE_A,categories:SHIP_EMITTER_CATEGORIES_A,
  compatibility:SHIP_EMITTER_COMPATIBILITY_A,definitions:id=>resolveShipProfile(id)?.equipment?.emitters??null,
  validate:id=>shipEmitterRegistryValidateA(resolveShipProfile(id)),runtime:id=>shipEmitterRuntimeSnapshotA(ENGAGEMENT_RUNTIME.ships.get(String(id))),
  audit:shipEmitterAuditSnapshotA,physical:()=>shipEmitterComparableA(electronicPhysicalEmittersF())});
