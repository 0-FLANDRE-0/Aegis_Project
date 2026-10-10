// LIVE_CANONICAL. Physical emitters stop at anonymous receiver measurements.
// Powers, sensitivity, bandwidth and ECCM factors are game SIM-TUNE values.
const ELECTRONIC_POLICY_F=Object.freeze({schema:'AEGIS_RECEIVER_EW_F_1',revisitS:.2,holdS:12,maxContacts:96,esmReferenceNoiseW:2e-12,radarNoiseW:2e-11,radarRejectionDb:24});
function electronicShipsF(){return [ACTIVE_SHIP_RUNTIME,...physicalShipsB()];}
function prepareElectronicF(r){
  const own=r===ACTIVE_SHIP_RUNTIME,previous=r.ew.executionF;
  if(previous)return previous;
  const e={schema:ELECTRONIC_POLICY_F.schema,contacts:own?esmContacts:r.ew.contacts,serial:1,rng:{state:rfSeedWip13A2('EW_F:'+BATTLESPACE_SEED+':'+r.entityId),spare:null},ageS:0,lastTick:-1,ticks:0,
    noiseRequested:!own,deceptionRequested:!own,auto:!own,autoAim:true,bearing:r.navigation.heading,receiver:{lastAtS:null,noiseRatio:0},history:[]};
  r.ew.executionF=e;r.ew.execution='OWNER_RECEIVER_EW_F';
  if(!own){observerC(r).emcon=r.initialEmconF??false;e.context=createElectronicContextF(r,e,MK36_SRBOC);if(r.restoredElectronicF)electronicCommandF(r.entityId,r.restoredElectronicF);}
  claimShipMutableRootA(r,'electronicF',e);return e;
}
function resetElectronicFleetF(){
  for(const r of electronicShipsF()){const old=r.ew.executionF,command=old?electronicSettingsF(r):null;r.ew.contacts.clear();r.ew.executionF=null;prepareElectronicF(r);if(command)electronicCommandF(r.entityId,command);}
}
function electronicSettingsF(r){
  const own=r===ACTIVE_SHIP_RUNTIME,e=prepareElectronicF(r);
  return {emcon:own?emconActive:observerC(r).emcon,noiseRequested:own?noiseJamActive:e.noiseRequested,deceptionRequested:own?deceptJamActive:e.deceptionRequested,auto:own?softKillAutoDoctrine:e.auto,autoAim:own?jammerAutoTrack:e.autoAim,bearingRad:own?jammerBearing:e.bearing};
}
function electronicCommandF(id,command){
  const r=ENGAGEMENT_RUNTIME.ships.get(id);if(!r||!command||typeof command!=='object'||Array.isArray(command))return {ok:false,reason:'EW_OWNER_OR_COMMAND'};
  const keys=['emcon','noiseRequested','deceptionRequested','auto','autoAim','bearingRad'];
  if(Object.keys(command).some(k=>!keys.includes(k))||keys.slice(0,5).some(k=>k in command&&typeof command[k]!=='boolean')||'bearingRad'in command&&(!Number.isFinite(command.bearingRad)||Math.abs(command.bearingRad)>TAU))return {ok:false,reason:'EW_COMMAND_FIELDS'};
  const e=prepareElectronicF(r),own=r===ACTIVE_SHIP_RUNTIME;
  if('emcon'in command){if(own){if(emconActive!==command.emcon)toggleEmcon();}else observerC(r).emcon=command.emcon;}
  if(own){if('noiseRequested'in command)noiseJamActive=command.noiseRequested;if('deceptionRequested'in command)deceptJamActive=command.deceptionRequested;if('auto'in command)setSoftKillAutoDoctrine(command.auto);if('autoAim'in command)jammerAutoTrack=command.autoAim;if('bearingRad'in command)jammerBearing=command.bearingRad;updateSlq32EaButtonLabels();}
  else {for(const k of keys.slice(1,5))if(k in command)e[k]=command[k];if('bearingRad'in command)e.bearing=command.bearingRad;}
  return {ok:true};
}
function electronicAllocatorF(r){return r===ACTIVE_SHIP_RUNTIME?slq32EaState:r.ew.slq32Allocator;}
function electronicPodsF(r){
  const p=resolveShipProfile(r.profileId);if(p.equipment?.ew?.pods)return p.equipment.ew.pods;
  const boxes=r===ACTIVE_SHIP_RUNTIME?SHIP_EXTERNAL_GEOMETRY:r.geometry.boxes;
  const registered=boxes.filter(q=>q.name.includes('SLQ-32')).map(q=>({id:q.name,name:q.name,center:{x:q.oX,y:q.oY,z:(q.zMin+q.zMax)*.5},beamCenterRad:q.oY<0?-Math.PI/2:Math.PI/2,beamHalfRad:deg(105)}));
  // DDG has no separate antenna damage registration. Retain the original
  // RF reference point and power/CDC availability, not an invented mount.
  return registered.length?registered:[{id:'DDG_LEGACY_EW_REFERENCE',name:null,basis:'LEGACY_DDG_RF_REFERENCE_NOT_ANTENNA_REGISTRATION',center:{x:0,y:0,z:OWN_ALT_M},beamCenterRad:0,beamHalfRad:Math.PI}];
}
function electronicPodF(r,rx){
  if(shipEquipmentOfflineV1(r))return null;
  const p=resolveShipProfile(r.profileId),frame=shipBodyFrameB(r),target=frame.pointToBody({x:worldToMeters(rx.x),y:worldToMeters(rx.y),z:rx.z??5});
  const pods=electronicPodsF(r);
  let best=null;
  for(const pod of pods){const d=wip12aSub(target,pod.center),range=Math.hypot(d.x,d.y,d.z),az=Math.atan2(d.y,d.x),el=Math.atan2(d.z,Math.hypot(d.x,d.y)),health=pod.name?observerHealthC(r,pod.name):clamp(1-shipSystemDamageB(r,'CDC')/100,0,1)*clamp(((1-shipSystemDamageB(r,'GEN_1')/100)+(1-shipSystemDamageB(r,'GEN_2')/100))*.5+(1-shipSystemDamageB(r,'GEN_3')/100)*.3,0,1);
    if(health<=.01||Math.abs(angNorm(az-(pod.beamCenterRad??0)))>(pod.beamHalfRad??Math.PI)||observerMaskC(r,pod.center,Math.atan2(rx.y-r.navigation.positionWorld.y,rx.x-r.navigation.positionWorld.x),el))continue;
    const q={point:observerMountC(r,pod.center),health};if(!best||health>best.health)best=q;
  }return best;
}
function electronicBandF(tag){const t=String(tag??'').toUpperCase();return t.includes('X')||t.includes('I')||t.includes('J')?'IJ':t.includes('S')?'S':t;}
function electronicBeamF(r,rx,cfg){
  const settings=electronicSettingsF(r),az=Math.atan2(rx.y-r.navigation.positionWorld.y,rx.x-r.navigation.positionWorld.x),off=Math.abs(angNorm(az-settings.bearingRad)),half=deg(cfg.beamHalfWidthDeg??60);
  return Math.max(cfg.sidelobeFloorLinear??.012,off<half?Math.pow(Math.max(0,Math.cos(off/half*Math.PI/2)),cfg.beamCosineExponent??1.7):0);
}
function electronicJammerSampleF(r,rx,p,kind){
  const cfg=kind==='NOISE'?NOISE_JAM:DECEPTION_JAM,settings=electronicSettingsF(r),allocation=electronicAllocatorF(r),share=kind==='NOISE'?allocation.noiseShare:allocation.deceptionShare,requested=kind==='NOISE'?settings.noiseRequested:settings.deceptionRequested;
  if(!requested||!(share>SLQ32_EA_ALLOC.minEffectiveShare))return null;
  const pod=electronicPodF(r,rx);if(!pod)return null;
  const band=electronicBandF(p.rfBandTag),match=band==='IJ'?1:0;if(!match)return null;
  const dx=worldToMeters(pod.point.x-rx.x),dy=worldToMeters(pod.point.y-rx.y),dz=pod.point.z-(rx.z??5),rangeM=Math.max(100,Math.hypot(dx,dy,dz)),los=terrainAwareRadarLOS(rx.x,rx.y,rx.z??5,pod.point.x,pod.point.y,pod.point.z);if(los<=.005)return null;
  const gain=electronicBeamF(r,rx,cfg),coupling=cfg.txPathEfficiency*cfg.polarizationCoupling*gain*match*clamp(p[kind==='NOISE'?'noiseJamBandCoupling':'deceptionJamBandCoupling']??1,0,1),power=(kind==='NOISE'?cfg.erpW:cfg.replayErpW)*share*pod.health,
    rawW=power*coupling*Math.max(1e-5,p.receiveApertureM2??.006)/(4*Math.PI*rangeM*rangeM)*los*maritimeRfWeatherPathFactorWip13A3('IJ',rangeM/1000),leak=Math.pow(10,-Math.max(0,p[kind==='NOISE'?'noiseJamRejectionDb':'deceptionJamRejectionDb']??0)/10);
  return {rawW,receivedW:rawW*leak,rangeKm:rangeM/1000,beamGain:gain,bandCoupling:coupling,eccmLeak:leak,share,power,worldAz:Math.atan2(dy,dx),worldEl:Math.atan2(dz,Math.hypot(dx,dy)),los};
}
function electronicJammerAtReceiverF(rx,p,kind){
  const noiseW=asmReceiverNoisePowerW(p);let power=0,raw=0,best=null;
  for(const r of electronicShipsF()){if(r.entityId===rx.receiverShipId)continue;const q=electronicJammerSampleF(r,rx,p,kind);if(!q)continue;
    if(Number.isFinite(p.receiverBeamAz)){const off=Math.abs(angNorm(q.worldAz-p.receiverBeamAz)),half=Math.max(deg(.1),p.receiverBeamHalfAz??deg(2)),gain=Math.max(.005,Math.exp(-2.7726*(off/half)**2));q.rawW*=gain;q.receivedW*=gain;}
    power+=q.receivedW;raw+=q.rawW;if(!best||q.receivedW>best.receivedW)best=q;}
  if(kind==='NOISE')return {active:power>0,noiseW,jammerRxW:power,jammerRxRawW:raw,jOverN:power/Math.max(1e-30,noiseW),rangeKm:best?.rangeKm??null,beamGain:best?.beamGain??0,bandCoupling:best?.bandCoupling??0,eccmLeak:best?.eccmLeak??0,eaShare:best?.share??0,effectiveErpW:best?.power??0};
  return {active:power>0,noiseW,replayRxW:best?.receivedW??0,replayRxRawW:best?.rawW??0,replaySnr:(best?.receivedW??0)/Math.max(1e-30,noiseW),rangeKm:best?.rangeKm??null,beamGain:best?.beamGain??0,bandCoupling:best?.bandCoupling??0,eccmLeak:best?.eccmLeak??0,eaShare:best?.share??0,effectiveReplayErpW:best?.power??0};
}
function electronicHojF(em,s,p){
  const noiseW=asmReceiverNoisePowerW(p);let best={active:false,noiseW,directJOverN:0,rxGain:0,worldAz:null,worldEl:null,noiseRawW:0,deceptionRawW:0,losQ:0};
  if(!p.hojEnabled||!em.seekerOn)return best;
  for(const r of electronicShipsF()){
    const n=electronicJammerSampleF(r,em,p,'NOISE'),d=electronicJammerSampleF(r,em,p,'DECEPTION'),q=n??d;if(!q)continue;
    const az=Math.abs(angNorm(q.worldAz-em.heading-s.gimbalAz)),el=Math.abs(angNorm(q.worldEl-(em.flight?.bodyPitch??0)-s.gimbalEl)),ha=deg(p.hojReceiveHalfAzDeg??8),he=deg(p.hojReceiveHalfElDeg??6.5),gain=Math.max(p.hojRxSidelobeFloor??.02,(az<ha?Math.cos(az/ha*Math.PI/2)**2:0)*(el<he?Math.cos(el/he*Math.PI/2)**2:0)),signal=((n?.rawW??0)+(d?.rawW??0))*gain/noiseW;
    if(signal>best.directJOverN)best={active:true,noiseW,directJOverN:signal,rxGain:gain,worldAz:q.worldAz,worldEl:q.worldEl,noiseRawW:n?.rawW??0,deceptionRawW:d?.rawW??0,losQ:q.los};
  }return best;
}
function electronicRadarInterferenceF(opts){
  if(!physicalShipsB().length)return {noise:0,replay:0};
  const rx={...opts.receiver,receiverShipId:opts.observerShipId??ACTIVE_SHIP_RUNTIME.entityId},p={rfBandTag:opts.band,receiveApertureM2:.008,receiverNoiseBandwidthHz:12e6,receiverNoiseFigureDb:6,noiseJamRejectionDb:ELECTRONIC_POLICY_F.radarRejectionDb,deceptionJamRejectionDb:ELECTRONIC_POLICY_F.radarRejectionDb,receiverBeamAz:opts.beamAz,receiverBeamHalfAz:opts.beamHalfAzRad};
  const n=electronicJammerAtReceiverF(rx,p,'NOISE'),d=electronicJammerAtReceiverF(rx,p,'DECEPTION');
  const result={noise:(n.jammerRxW??0)/ELECTRONIC_POLICY_F.radarNoiseW,replay:(d.replayRxW??0)/ELECTRONIC_POLICY_F.radarNoiseW},owner=ENGAGEMENT_RUNTIME.ships.get(rx.receiverShipId);
  if(owner){const e=prepareElectronicF(owner);e.receiver.noiseRatio=result.noise;e.receiver.lastInterferenceAtS=simStepCounter*SIM_FIXED_DT;}return result;
}
function electronicPhysicalEmittersF(){
  const out=[];
  for(const r of electronicShipsF()){
    const own=r===ACTIVE_SHIP_RUNTIME,o=observerC(r),silent=own?emconActive:o.emcon;
    if(!silent&&!shipEquipmentOfflineV1(r)){
      const p=resolveShipProfile(r.profileId),spy=o.normals.filter(q=>observerHealthC(r,q.moduleName)>.05);
      if(o.enabled.SPY&&spy.length)out.push({owner:r.entityId,point:observerMountC(r,spy[0].center),band:'S',power:2500,family:'SHIP SEARCH RADAR',emitterClass:'SEARCH_RADAR',beamAz:null});
      for(const [key,hp]of [['SPQ','spq9b'],['NAV','bridgeMasterE']])if(o.enabled[key]&&observerHealthC(r,p.geometry.hardpoints[hp].name)>.05&&shipSystemDamageB(r,'MAST')<80)out.push({owner:r.entityId,point:observerMountC(r,p.geometry.hardpoints[hp]),band:key==='SPQ'?'IJ':electronicBandF(p.sensors.bridgeMasterE.band),power:key==='SPQ'?650:120,family:key==='SPQ'?'SURFACE SEARCH RADAR':'NAVIGATION RADAR',emitterClass:'SEARCH_RADAR',beamAz:r.navigation.heading+(own?(key==='SPQ'?spq9bRotorAngle:bridgeMasterERotorAngle):o.rotors[key]),double:key==='SPQ'});
    }
    const a=electronicAllocatorF(r),settings=electronicSettingsF(r),pods=electronicPodsF(r);
    if(a.resourceUsed>.001&&(settings.noiseRequested||settings.deceptionRequested)&&pods.length)out.push({owner:r.entityId,ship:r,point:observerMountC(r,pods[0].center),band:'IJ',power:2000*a.resourceUsed,family:'RF INTERFERENCE',emitterClass:'JAMMER',beamAz:settings.bearingRad});
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
function electronicReceiverPlotsF(r,emitters){
  // PHYSICAL/SENSOR boundary: owner IDs are used only to suppress self-coupling.
  const e=prepareElectronicF(r);if(shipEquipmentOfflineV1(r))return [];
  const plots=[];
  for(const source of emitters){
    if(source.owner===r.entityId)continue;
    const receiverPod=electronicPodF(r,source.point);if(!receiverPod)continue;const rx=receiverPod.point,health=receiverPod.health,transmitterPod=source.ship?electronicPodF(source.ship,rx):null;if(source.ship&&!transmitterPod)continue;
    const point=transmitterPod?.point??source.point,dx=worldToMeters(point.x-rx.x),dy=worldToMeters(point.y-rx.y),dz=point.z-rx.z,range=Math.max(100,Math.hypot(dx,dy,dz)),los=terrainAwareRadarLOS(rx.x,rx.y,rx.z,point.x,point.y,point.z);if(los<=.005)continue;
    const az=Math.atan2(dy,dx),toward=angNorm(az+Math.PI),off=source.beamAz==null?0:Math.abs(angNorm(toward-source.beamAz)),gain=source.beamAz==null?1:source.emitterClass==='ACTIVE_SEEKER'?Math.max(.005,Math.exp(-((off/deg(25))**2))):source.double?Math.max(.015,Math.exp(-((Math.min(off,Math.abs(Math.PI-off))/deg(35))**2))):Math.max(.015,Math.exp(-((off/deg(35))**2)));
    const power=source.power*gain*(transmitterPod?.health??1)*.008*los*health*maritimeRfWeatherPathFactorWip13A3(source.band,range/1000)/(4*Math.PI*range*range),snr=power/ELECTRONIC_POLICY_F.esmReferenceNoiseW,pd=snr/(snr+1);if(observerRandomC(e.rng)>pd)continue;
    const quality=clamp(pd*health,.01,1),sigma=lerp(6,.6,quality),bearing=angNorm(az+observerNormalC(e.rng)*deg(sigma));
    plots.push({bearing,bearingSigmaDeg:sigma,strength:quality,quality,band:source.band,type:source.family,emitterClass:source.emitterClass,measuredAtS:simStepCounter*SIM_FIXED_DT});
  }return plots;
}
function electronicAcceptPlotsF(r,plots){
  const allowed=['bearing','bearingSigmaDeg','strength','quality','band','type','emitterClass','measuredAtS'];
  if(!r||!Array.isArray(plots)||plots.length>96||plots.some(q=>!q||Object.keys(q).some(k=>!allowed.includes(k))||!['bearing','bearingSigmaDeg','strength','quality','measuredAtS'].every(k=>Number.isFinite(q[k]))||Math.abs(q.bearing)>TAU||q.bearingSigmaDeg<=0||q.bearingSigmaDeg>180||q.strength<0||q.strength>1||q.quality<0||q.quality>1||q.measuredAtS<0||q.measuredAtS>simStepCounter*SIM_FIXED_DT+.001||!['S','IJ','X'].includes(q.band)||typeof q.type!=='string'||q.type.length>80||!['SEARCH_RADAR','ACTIVE_SEEKER','JAMMER'].includes(q.emitterClass)))return {ok:false,reason:'ANONYMOUS_EW_PLOT_REQUIRED'};
  const e=prepareElectronicF(r),used=new Set();
  for(const q of plots){
    let found=null,best=Infinity;
    for(const [id,c]of e.contacts){if(used.has(id)||c.band!==q.band||c.emitterClass!==q.emitterClass||q.emitterClass!=='ACTIVE_SEEKER'&&c.type!==q.type)continue;const err=Math.abs(angNorm(q.bearing-c.bearing)),gate=deg(Math.max(2,3*Math.hypot(q.bearingSigmaDeg,c.bearingSigmaDeg??6)));if(err<gate&&err<best){best=err;found=id;}}
    if(found==null){if(e.contacts.size>=ELECTRONIC_POLICY_F.maxContacts)continue;found=600000000+e.serial++;e.contacts.set(found,{contactId:found,...q,age:0,hits:1,rangeKm:null,identity:'UNKNOWN',threatLevel:q.emitterClass==='ACTIVE_SEEKER'?'HIGH':'LOW',source:'PASSIVE_RF_F'});}
    else {const c=e.contacts.get(found);c.bearing=angNorm(c.bearing+angNorm(q.bearing-c.bearing)*.45);Object.assign(c,{bearingSigmaDeg:q.bearingSigmaDeg,strength:q.strength,quality:q.quality,type:q.type,measuredAtS:q.measuredAtS,age:0,hits:(c.hits??0)+1});}
    delete e.contacts.get(found).truthRef;used.add(found);
  }return {ok:true};
}
function stepElectronicReceiversF(dt){
  const emitters=electronicPhysicalEmittersF();
  for(const r of electronicShipsF()){
    const e=prepareElectronicF(r);if(e.lastTick===simStepCounter)throw Error('EW_DOUBLE_TICK_F');e.lastTick=simStepCounter;e.ticks++;
    for(const [id,c]of e.contacts){c.age+=dt;if(c.age>ELECTRONIC_POLICY_F.holdS)e.contacts.delete(id);}
    e.ageS+=dt;if(e.ageS+1e-9<ELECTRONIC_POLICY_F.revisitS)continue;e.ageS%=ELECTRONIC_POLICY_F.revisitS;
    electronicAcceptPlotsF(r,electronicReceiverPlotsF(r,emitters));e.receiver.lastAtS=simStepCounter*SIM_FIXED_DT;
  }
}
function stepElectronicOwnersF(dt){for(const r of physicalShipsB())prepareElectronicF(r).context.step(dt);stepFriendlyIffF(dt);}
function friendlyIffPlotsF(r){
  // Authenticated transponder replies are measured at the receiver. No world
  // coordinates or entity keys enter the track classifier.
  if(r===ACTIVE_SHIP_RUNTIME?emconActive:observerC(r).emcon)return [];
  const rx=observerMountC(r,resolveShipProfile(r.profileId).geometry.hardpoints.bridgeMasterE),e=prepareElectronicF(r),out=[];
  for(const q of electronicShipsF())if(q!==r&&q.faction===r.faction&&!shipEquipmentOfflineV1(q)){
    const tx=observerMountC(q,{x:0,y:0,z:20}),dx=worldToMeters(tx.x-rx.x),dy=worldToMeters(tx.y-rx.y),range=Math.hypot(dx,dy),los=terrainAwareRadarLOS(rx.x,rx.y,rx.z,tx.x,tx.y,tx.z);if(range>40000||los<.05)continue;
    out.push({bearing:angNorm(Math.atan2(dy,dx)+observerNormalC(e.rng)*deg(.25)),rangeM:range+observerNormalC(e.rng)*35,rangeSigmaM:35,bearingSigmaDeg:.25,authenticatedFriendly:true,measuredAtS:simStepCounter*SIM_FIXED_DT});
  }return out;
}
function stepFriendlyIffF(dt){
  if(simStepCounter%30!==0)return;
  for(const r of electronicShipsF()){
    const o=observerC(r),rx=r.navigation.positionWorld,used=new Set();
    for(const reply of friendlyIffPlotsF(r)){
      let pick=null,best=Infinity;
      for(const [id,tr]of o.tracks){if(tr.domain!=='SURFACE'||used.has(id)||tr.sensorAge>2)continue;const dx=worldToMeters(tr.x-rx.x),dy=worldToMeters(tr.y-rx.y),range=Math.hypot(dx,dy),sigma=trackCovarianceMetrics(tr).posSigmaM??100,dr=Math.abs(range-reply.rangeM),da=Math.abs(angNorm(Math.atan2(dy,dx)-reply.bearing)),rg=Math.max(120,3*Math.hypot(sigma,reply.rangeSigmaM)),ag=deg(Math.max(1,rad2deg(Math.atan2(3*sigma,Math.max(100,range)))));if(dr>rg||da>ag)continue;const score=dr/rg+da/ag;if(score<best){best=score;pick={id,tr};}}
      if(pick){pick.tr.iffF={authenticatedFriendly:true,measuredAtS:reply.measuredAtS};pick.tr._operatorIdentity='FRIEND';pick.tr.identity='FRIEND';pick.tr.engagementAuthority='WITHHELD';used.add(pick.id);}
    }
  }
}
function electronicSnapshotF(){return {schema:ELECTRONIC_POLICY_F.schema,ships:electronicShipsF().map(r=>{const e=prepareElectronicF(r);return {entityId:r.entityId,role:r.role,faction:r.faction,settings:electronicSettingsF(r),allocator:{...electronicAllocatorF(r)},ticks:e.ticks,rng:{...e.rng},contacts:[...e.contacts.values()].map(c=>({...c})),receiver:{...e.receiver},logistics:e.context?.logistics()??{srboc:skLogisticsSnapshot15B('SRBOC'),nulka:skLogisticsSnapshot15B('NULKA')},responses:e.context?.snapshot()??softKillDoctrineAuditSnapshot()};}),deferred:['friendlyNetwork','offensiveAndManeuverAI','cooperativeEngagement'],truthUsedByController:false};}
function electronicReleaseF(id,kind){const r=ENGAGEMENT_RUNTIME.ships.get(id);if(!r||r===ACTIVE_SHIP_RUNTIME||!['SRBOC','NULKA'].includes(kind))return {ok:false,reason:'EW_RELEASE_OWNER_OR_KIND'};return prepareElectronicF(r).context.release(kind);}
function electronicCicTextF(){const e=prepareElectronicF(ACTIVE_SHIP_RUNTIME),fresh=[...e.contacts.values()].filter(c=>c.source==='PASSIVE_RF_F'),n=fresh.filter(c=>c.emitterClass==='JAMMER').length;return 'ESM '+fresh.length+' · RF 간섭 '+n+' · 방위 관측 / 거리 미확정';}
