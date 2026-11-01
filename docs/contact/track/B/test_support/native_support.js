// TEST ONLY. Native anonymous ingress support, never an alternate association model.
// No invocation is automatic. Load into the existing actual-game test harness.
// Geometry here is supplied sensor evidence, not hidden world entity geometry.
const TRACK_B_PRIVATE_FIXTURE_OWNERS=[];
const TRACK_B_NATIVE_SUPPORT = Object.freeze({
  classification:'DIRECT_NATIVE_ANONYMOUS_INGRESS_NOT_NATURAL_RF',
  copy(value){return JSON.parse(JSON.stringify(value));},
  nowS(){return simStepCounter*SIM_FIXED_DT;},
  air({xM=4000,yM=0,zM=50,vxMps=0,vyMps=0,vzMps=0,receiver={xM:0,yM:0,zM:22,vxMps:0,vyMps:0,vzMps:0},measuredAtS=simStepCounter*SIM_FIXED_DT}={}){
    const dx=xM-receiver.xM,dy=yM-receiver.yM,dz=zM-receiver.zM,rangeM=Math.hypot(dx,dy,dz),losUx=dx/rangeM,losUy=dy/rangeM,losUz=dz/rangeM;
    return {x:metersToWorld(xM),y:metersToWorld(yM),z:zM,rangeM,azRad:Math.atan2(dy,dx),elRad:Math.atan2(dz,Math.hypot(dx,dy)),radialMps:(vxMps-receiver.vxMps)*losUx+(vyMps-receiver.vyMps)*losUy+(vzMps-receiver.vzMps)*losUz,
      radialVelSigmaMps:3,rangeSigmaM:15,azSigmaDeg:.1,elSigmaDeg:.1,losUx,losUy,losUz,sensorXWorld:metersToWorld(receiver.xM),sensorYWorld:metersToWorld(receiver.yM),sensorZM:receiver.zM,sensorVxMps:receiver.vxMps,sensorVyMps:receiver.vyMps,sensorVzMps:receiver.vzMps,quality:.8,source:'SPY1DV_SEARCH_VOLUME',measuredAtS,domainEvidence:{surface:.05,air:.9,missile:.05,background:0}};
  },
  surface(options={}){
    const p=this.air({...options,zM:8}),dx=worldToMeters(p.x-p.sensorXWorld),dy=worldToMeters(p.y-p.sensorYWorld);
    p.rangeM=Math.hypot(dx,dy);p.losUx=dx/p.rangeM;p.losUy=dy/p.rangeM;p.losUz=0;p.radialMps=((options.vxMps??0)-(options.receiver?.vxMps??0))*p.losUx+((options.vyMps??0)-(options.receiver?.vyMps??0))*p.losUy;
    p.source='SPQ9B_SURFACE_PRECISION';p.surfaceReferenceZM=8;p.domainEvidence={surface:.9,air:.05,missile:.05,background:0};delete p.elRad;delete p.elSigmaDeg;return p;
  },
  privateOwner(label){
    const owner=createPreparedShipRuntimeA(resolveShipProfile(ACTIVE_SHIP_RUNTIME.profileId),{entityId:'TRACK_B_FIXTURE_'+label,role:'ALLY',faction:'FRIENDLY'});
    preparePhysicalShipB(owner);prepareObserverC(owner);TRACK_B_PRIVATE_FIXTURE_OWNERS.push(owner);return owner;
  },
  resetPrivateOwnerEvidence(){TRACK_B_PRIVATE_FIXTURE_OWNERS.length=0;},
  afterActionPassiveState(){
    const privateOwners=TRACK_B_PRIVATE_FIXTURE_OWNERS.map(owner=>{const o=owner.combatSystem.observerC;return {id:owner.entityId,observer:o?{rng:this.copy(o.rng),tickCount:o.tickCount,lastTick:o.lastTick,serial:o.serial,stats:{...o.stats},tracks:this.snapshotStore(o.tracks),offboard:{accepted:o.offboard.accepted,rejected:o.offboard.rejected,queue:this.copy(o.offboard.queue),sources:[...o.offboard.sources.values()].map(x=>this.copy(x))}}:null,c55:owner.weapons.executionD?.context?.__trackBTestC55?.passiveState()??null};});
    return JSON.stringify({meaning:'AFTER_ACTION_TEST_ONLY_NO_GAME_CONSUMER',world:JSON.parse(__TRACK_RUNTIME_A__.state()),privateOwners});
  },
  snapshotFile(tr){return tr?{id:tr.trackId,source:tr.sensorSource,domain:tr.domain,classification:tr.classification,identity:tr.identity,authority:tr.engagementAuthority,hits:tr.sensorHits,confirmed:!!tr.confirmed,age:tr.sensorAge,x:Array.from(tr._kfX??[]),P:Array.from(tr._kfP??[]),lastMeasurementS:tr.lastMeasurementS??null}:null;},
  snapshotStore(store){return [...store.values()].map(tr=>this.snapshotFile(tr));},
  advanceTicks(count){if(!Number.isInteger(count)||count<0)throw Error('INVALID_TEST_TICKS');for(let i=0;i<count;i++)simulateFixedTick(SIM_FIXED_DT);},
  report({sourceId='H1',sequence=1,measuredAtS=simStepCounter*SIM_FIXED_DT,xM=4000,yM=0,zM=8,covarianceM2=[400,0,0,0,400,0,0,0,16]}={}){
    return {schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId,sequence,measuredAtS,positionM:{x:xM,y:yM,z:zM},covarianceM2:[...covarianceM2],domainEvidence:{surface:.95,air:.05,missile:0,background:0}};
  },
  assertNoTruthFields(payload){
    const forbidden=new Set(['truthRef','objectId','rfId','_truthObject','faction','owner','targetEntity','entityId']);
    const visit=x=>{if(!x||typeof x!=='object')return;for(const [key,value]of Object.entries(x)){if(forbidden.has(key))throw Error('TRUTH_FIELD_IN_ASSOCIATION_FIXTURE:'+key);visit(value);}};
    visit(payload);return true;
  }
});
