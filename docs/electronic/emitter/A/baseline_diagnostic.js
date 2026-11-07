// EMITTER_A Commit A — diagnostic-only readout of the frozen predecessor.
// Injected into a disposable HTML copy; never shipped in the product.
function emitterABaselineSerializeA(row){
  const out={};
  for(const key of Object.keys(row)){
    if(key==='ship')out.shipEntityId=row.ship?.entityId??null;
    else if(key==='point')out.point={x:row.point.x,y:row.point.y,z:row.point.z};
    else out[key]=row[key];
  }
  return {keys:Object.keys(row),value:out};
}
function emitterABaselineOwnRowsA(){
  return electronicPhysicalEmittersF().filter(q=>q.owner===ACTIVE_SHIP_RUNTIME.entityId).map(emitterABaselineSerializeA);
}
function emitterABaselineMatrixA(){
  const o=observerC(ACTIVE_SHIP_RUNTIME),saved={
    enabled:{...o.enabled},emconActive,spq9bRotorAngle,bridgeMasterERotorAngle,
    noiseJamActive,deceptJamActive,jammerBearing,
    allocator:{...slq32EaState}
  };
  const legacyHealth=observerHealthC,legacyDamage=shipSystemDamageB;
  const run=(id,apply)=>{emconActive=false;apply();return {id,rows:emitterABaselineOwnRowsA()};};
  const reset=()=>{
    Object.assign(o.enabled,saved.enabled);emconActive=saved.emconActive;
    spq9bRotorAngle=saved.spq9bRotorAngle;bridgeMasterERotorAngle=saved.bridgeMasterERotorAngle;
    noiseJamActive=saved.noiseJamActive;deceptJamActive=saved.deceptJamActive;
    jammerBearing=saved.jammerBearing;Object.assign(slq32EaState,saved.allocator);
    observerHealthC=legacyHealth;shipSystemDamageB=legacyDamage;
  };
  const cases=[];
  try{
    reset();cases.push(run('ALL_RADARS',()=>{}));
    reset();cases.push(run('ALL_RADARS_OFF',()=>{o.enabled.SPY=o.enabled.SPQ=o.enabled.NAV=false;}));
    reset();cases.push(run('SPY_ONLY',()=>{o.enabled.SPY=true;o.enabled.SPQ=o.enabled.NAV=false;}));
    reset();cases.push(run('SPQ_ONLY',()=>{o.enabled.SPQ=true;o.enabled.SPY=o.enabled.NAV=false;}));
    reset();cases.push(run('NAV_ONLY',()=>{o.enabled.NAV=true;o.enabled.SPY=o.enabled.SPQ=false;}));
    reset();cases.push(run('SPY_OFF',()=>{o.enabled.SPY=false;}));
    reset();cases.push(run('SPQ_OFF',()=>{o.enabled.SPQ=false;}));
    reset();cases.push(run('NAV_OFF',()=>{o.enabled.NAV=false;}));
    reset();cases.push(run('EMCON',()=>{emconActive=true;}));
    reset();cases.push(run('ROTATED',()=>{spq9bRotorAngle=.731;bridgeMasterERotorAngle=-1.217;}));
    reset();cases.push(run('MAST_DAMAGE_79_999',()=>{shipSystemDamageB=(r,name)=>name==='MAST'?79.999:legacyDamage(r,name);}));
    reset();cases.push(run('MAST_DAMAGE_80',()=>{shipSystemDamageB=(r,name)=>name==='MAST'?80:legacyDamage(r,name);}));
    reset();cases.push(run('HARDPOINT_HEALTH_0_050001',()=>{observerHealthC=(r,name)=>(name===ACTIVE_SHIP_PROFILE.geometry.hardpoints.spq9b.name ? 0.050001 : legacyHealth(r,name));}));
    reset();cases.push(run('HARDPOINT_HEALTH_0_05',()=>{observerHealthC=(r,name)=>(name===ACTIVE_SHIP_PROFILE.geometry.hardpoints.spq9b.name ? 0.05 : legacyHealth(r,name));}));
    reset();cases.push(run('ECM_NOISE',()=>{
      noiseJamActive=true;deceptJamActive=false;jammerBearing=.417;
      Object.assign(slq32EaState,{noiseShare:.625,deceptionShare:0,resourceUsed:.625,policy:'NOISE'});
    }));
    reset();cases.push(run('ECM_DECEPTION',()=>{
      noiseJamActive=false;deceptJamActive=true;jammerBearing:-.823;
      Object.assign(slq32EaState,{noiseShare:0,deceptionShare:.375,resourceUsed:.375,policy:'DECEPTION'});
    }));
  } finally {observerHealthC=legacyHealth;shipSystemDamageB=legacyDamage;reset();}
  return {schema:'AEGIS_EMITTER_A_BASELINE_MATRIX_1',profileId:ACTIVE_SHIP_PROFILE.id,entityId:ACTIVE_SHIP_RUNTIME.entityId,cases};
}
function emitterABaselineFleetSceneA(config={}){
  const base={...MULTISHIP_DEPLOYMENT_STATE_A.draft,targetShip:'NONE',enemyAircraftEnabled:false,
    allyProfileId:config.allyProfileId??null,enemyProfileId:config.enemyProfileId??null,neutralProfileId:null,
    allyEmcon:false,enemyEmcon:false};
  applyDeploymentA(prepareDeploymentA(base));
  emconActive=false;
  for(const r of electronicShipsF()){
    const o=observerC(r);Object.assign(o.enabled,{SPY:true,SPQ:true,NAV:true});o.emcon=false;
    const e=prepareElectronicF(r);Object.assign(e,{noiseRequested:false,deceptionRequested:false});
    Object.assign(electronicAllocatorF(r),{noiseShare:0,deceptionShare:0,resourceUsed:0});
  }
  const rngBefore=electronicShipsF().map(r=>({id:r.entityId,rng:{...prepareElectronicF(r).rng}}));
  const emitters=electronicPhysicalEmittersF(),rngAfterPhysical=electronicShipsF().map(r=>({id:r.entityId,rng:{...prepareElectronicF(r).rng}}));
  const receiverRows=[];
  for(const r of electronicShipsF()){
    const e=prepareElectronicF(r);e.rng.state=0x5a17c0de;e.rng.spare=null;
    const before={...e.rng},plots=electronicReceiverPlotsF(r,emitters),after={...e.rng};
    receiverRows.push({receiver:r.entityId,before,after,plots});
  }
  return {schema:'AEGIS_EMITTER_A_BASELINE_FLEET_SCENE_1',activeProfileId:ACTIVE_SHIP_PROFILE.id,config:base,
    owners:electronicShipsF().map(r=>({entityId:r.entityId,profileId:r.profileId,role:r.role})),
    emitters:emitters.map(emitterABaselineSerializeA),rngBefore,rngAfterPhysical,receiverRows};
}
function emitterABaselineProfileAuditA(){
  const sov=SHIP_PROFILE_REGISTRY.SOVREMENNY_956;
  return {
    schema:'AEGIS_EMITTER_A_BASELINE_PROFILE_AUDIT_1',
    activeProfileId:ACTIVE_SHIP_PROFILE.id,
    electronicPolicy:ELECTRONIC_POLICY_F,
    sov:{capabilities:sov.capabilities,equipment:sov.equipment,sensors:sov.sensors,
      physicalEmitterCount:electronicPhysicalEmittersF().filter(q=>q.owner==='DIAG_SOV_EMITTER_A').length},
    contracts:{
      emitterFunction:String(electronicPhysicalEmittersF),
      receiverFunction:String(electronicReceiverPlotsF),
      ownerOrder:electronicShipsF().map(q=>q.entityId),
      observerStateKeys:Object.keys(observerC(ACTIVE_SHIP_RUNTIME)),
      ewStateKeys:Object.keys(prepareElectronicF(ACTIVE_SHIP_RUNTIME))
    }
  };
}
window.__EMITTER_A_BASELINE__=Object.freeze({matrix:emitterABaselineMatrixA,fleetScene:emitterABaselineFleetSceneA,profileAudit:emitterABaselineProfileAuditA});

