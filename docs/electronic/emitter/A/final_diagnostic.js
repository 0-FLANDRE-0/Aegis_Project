// Diagnostic-only final contract/edge probe. Never shipped in the product.
function emitterAFinalContractA(){
  const profiles=['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA','SOVREMENNY_956'].map(id=>{
    const p=resolveShipProfile(id),r=p.equipment.emitters,ids=r.entries.map(q=>q.id),orders=r.entries.map(q=>q.order);
    const refs=r.entries.map(q=>({id:q.id,sensorOk:!q.sensorKey||!!p.sensors[q.sensorKey],
      hardpointOk:!q.hardpointKey||!!p.geometry.hardpoints[q.hardpointKey],
      enabledKeyOk:!q.enabledKey||['SPY','SPQ','NAV'].includes(q.enabledKey),
      mountKindOk:['FIRST_HEALTHY_SPY_FACE','PROFILE_HARDPOINT','FIRST_AVAILABLE_EW_POD'].includes(q.mountKind)||q.outputKind==='REGISTERED_INACTIVE',
      damageDependencyPolicy:q.outputKind==='REGISTERED_INACTIVE'?'NOT_INSTALLED':q.mountKind==='FIRST_HEALTHY_SPY_FACE'?'SHIP_EQUIPMENT_AND_OBSERVER_FACE_HEALTH':q.mountKind==='PROFILE_HARDPOINT'?'SHIP_EQUIPMENT_HARDPOINT_HEALTH_AND_MAST_LT_80':'AVAILABLE_EW_POD_REQUEST_AND_RESOURCE'}));
    return {id,registryId:r.registryId,frozen:Object.isFrozen(r)&&Object.isFrozen(r.entries)&&r.entries.every(Object.isFrozen),
      uniqueIds:new Set(ids).size===ids.length,uniqueOrders:new Set(orders).size===orders.length,refs};
  });
  return {schema:'AEGIS_EMITTER_A_FINAL_CONTRACT_1',profiles,categories:[...SHIP_EMITTER_CATEGORIES_A],
    receiverKeys:['bearing','bearingSigmaDeg','strength','quality','band','type','emitterClass','measuredAtS'],
    protectedConsumerContracts:{receiver:String(electronicReceiverPlotsF),hoj:String(electronicHojF),radarInterference:String(electronicRadarInterferenceF)}};
}
function emitterACoreSelftestA(){
  const profileIds=['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA','SOVREMENNY_956'];
  const audit=shipEmitterAuditSnapshotA();
  const checks={
    packagingReady:window.C55Packaging?.ready===true&&!window.C55Packaging?.error,
    runtimeFaultAbsent:window.__WIP125_DIAG__?.wip150RuntimeFault?.()===null,
    presentationFaultAbsent:window.__WIP125_DIAG__?.wip150PresentationFault?.()===null,
    registriesValid:profileIds.every(id=>shipEmitterRegistryValidateA(resolveShipProfile(id)).ok),
    activeAuthority:SHIP_EMITTER_MODE_A==='ACTIVE'&&audit.tacticalOutputUsed===true,
    activeComparatorIdle:audit.comparisons===0&&audit.mismatches===0,
  };
  return {schema:'AEGIS_EMITTER_A_CORE_SELFTEST_1',checks,passed:Object.values(checks).filter(Boolean).length,
    total:Object.keys(checks).length,pass:Object.values(checks).every(Boolean)};
}
function emitterAFinalEdgeA(){
  const config={...MULTISHIP_DEPLOYMENT_STATE_A.draft,targetShip:'NONE',enemyAircraftEnabled:false,
    allyProfileId:'DDG_119_LATE_FLIGHT_IIA',enemyProfileId:null,neutralProfileId:null,allyEmcon:false,enemyEmcon:false};
  applyDeploymentA(prepareDeploymentA(config));const own=ACTIVE_SHIP_RUNTIME,ally=physicalShipsB().find(r=>r.role==='ALLY');
  emconActive=false;const ownObserver=observerC(own),allyObserver=observerC(ally);Object.assign(ownObserver.enabled,{SPY:true,SPQ:true,NAV:true});
  Object.assign(allyObserver.enabled,{SPY:true,SPQ:true,NAV:true});allyObserver.emcon=false;
  const ownBefore={enabled:{...ownObserver.enabled},emcon:emconActive,rotors:{...ownObserver.rotors}};
  const command=observerCommandC(ally.entityId,{emcon:true,SPY:false,SPQ:false,NAV:false});
  const ownAfter={enabled:{...ownObserver.enabled},emcon:emconActive,rotors:{...ownObserver.rotors}},allyAfter={enabled:{...allyObserver.enabled},emcon:allyObserver.emcon};
  noiseJamActive=true;deceptJamActive=false;jammerBearing=.25;Object.assign(slq32EaState,{noiseShare:1,deceptionShare:0,resourceUsed:1,policy:'NOISE'});
  const maxJammer=electronicPhysicalEmittersF().filter(q=>q.owner===own.entityId&&q.emitterClass==='JAMMER').map(emitterABaselineSerializeA);
  noiseJamActive=false;Object.assign(slq32EaState,{noiseShare:0,deceptionShare:0,resourceUsed:0,policy:'OFF'});
  spq9bRotorAngle=TAU+.001;bridgeMasterERotorAngle=-TAU-.002;
  const wrap=electronicPhysicalEmittersF().filter(q=>q.owner===own.entityId&&q.emitterClass==='SEARCH_RADAR').map(emitterABaselineSerializeA);
  allyObserver.emcon=false;Object.assign(allyObserver.enabled,{SPY:true,SPQ:true,NAV:true});
  const emitters=electronicPhysicalEmittersF(),e=prepareElectronicF(own);e.rng.state=0x5a17c0de;e.rng.spare=null;
  const plots=electronicReceiverPlotsF(own,emitters),plotKeys=plots.map(q=>Object.keys(q)),forbidden=['owner','ship','entityId','objectId','truthRef','profileId','damage'];
  return {schema:'AEGIS_EMITTER_A_FINAL_EDGE_1',command,ownBefore,ownAfter,allyAfter,maxJammer,wrap,
    anonymousPlots:{count:plots.length,keys:plotKeys,forbiddenPresent:plots.some(q=>forbidden.some(k=>Object.hasOwn(q,k)))}};
}
window.__EMITTER_A_FINAL_DIAG__=Object.freeze({coreSelftest:emitterACoreSelftestA,contract:emitterAFinalContractA,edge:emitterAFinalEdgeA,sovSnapshot:sovSnapshotA});
