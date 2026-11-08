function electronicShipPhysicalEmittersDeclaredA(r){
  const out=[],registry=shipEmitterRegistryA(r);
  if(sovNoEquipmentA(r)||registry?.physicalEmission===false){emconShadowResolveB(r,out);return out;}
  if(!registry)throw Error('SHIP_EMITTER_REGISTRY_REQUIRED:'+r.profileId);
  const own=r===ACTIVE_SHIP_RUNTIME,o=observerC(r),p=resolveShipProfile(r.profileId),spy=o.normals.filter(q=>observerHealthC(r,q.moduleName)>.05);
  for(const q of registry.entries){
    if(q.outputKind!=='RADAR'||!emconEquipmentDecisionB(r,q.id).allowed)continue;
    const spec=p.sensors[q.sensorKey];
    if(q.mountKind==='FIRST_HEALTHY_ARRAY_FACE'){
      if(spy.length)out.push({owner:r.entityId,point:observerMountC(r,spy[0].center),band:q.band,frequencyMHz:Number.isFinite(spec.frequencyMHz)?spec.frequencyMHz:null,frequencyProvenance:Number.isFinite(spec.frequencyMHz)?'EXISTING_EMITTER_PROFILE':'SIM_TUNED_BAND_CENTER',power:q.power,family:q.family,emitterClass:q.emitterClass,beamAz:null});
      continue;
    }
    const hp=p.geometry.hardpoints[q.hardpointKey];
    if(observerHealthC(r,hp.name)>.05&&shipSystemDamageB(r,'MAST')<80)out.push({owner:r.entityId,point:observerMountC(r,hp),band:q.bandMode==='FIXED'?q.band:electronicBandF(spec.band),frequencyMHz:Number.isFinite(spec.frequencyMHz)?spec.frequencyMHz:null,frequencyProvenance:Number.isFinite(spec.frequencyMHz)?'EXISTING_EMITTER_PROFILE':'SIM_TUNED_BAND_CENTER',power:q.power,family:q.family,emitterClass:q.emitterClass,beamAz:r.navigation.heading+(own?(q.rotorKey==='SPQ'?spq9bRotorAngle:bridgeMasterERotorAngle):o.rotors[q.rotorKey]),beamwidthDeg:q.beamwidthDeg??spec[q.beamwidthField],beamwidthProvenance:q.beamwidthProvenance??String(spec.performanceBasis||spec.source||'EXISTING_EMITTER_PROFILE'),rpm:Number(spec[q.rpmField]),double:q.double});
  }
  const a=electronicAllocatorF(r),settings=electronicSettingsF(r),pods=electronicPodsF(r),ecm=registry.entries.find(q=>q.outputKind==='ECM');
  if(ecm&&emconEquipmentDecisionB(r,ecm.id).emissionActive&&pods.length)out.push({owner:r.entityId,ship:r,point:observerMountC(r,pods[0].center),band:ecm.band,power:ecm.powerPerResource*a.resourceUsed,family:ecm.family,emitterClass:ecm.emitterClass,beamAz:settings.bearingRad});
  emconShadowResolveB(r,out);return out;
}
