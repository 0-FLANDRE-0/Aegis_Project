// Explicit manual commands only. Automatic CIWS selection is a later defense-AI step.
function ownerCloseInReleaseD(r,c,helpers){
  const mount=r.weapons.closeIn.find(m=>m.id===(c.mountId??m.id)&&m.type===(c.weapon==='RAM'?'RAM':'GUN'));
  if(!mount)return {ok:false,reason:'MOUNT_NOT_INSTALLED'};
  if(mount.ammo<=0)return {ok:false,reason:'NO_AMMO'};
  r.weapons.executionD.closeInPending={command:{...c},mountId:mount.id,expiresStep:simStepCounter+360};
  return {ok:true,queued:true,reason:'OWNER_MOUNT_CONSENT',mountId:mount.id};
}
function ownerCloseInTickD(r,dt,h){
  const e=r.weapons.executionD,p=e.closeInPending;if(!p)return;const c=p.command,mount=r.weapons.closeIn.find(m=>m.id===p.mountId),gate=ownerTrackGateD(r,c.trackId),health=ciwsB3PerformanceForDamage(mount,r.flooding.readDamage(mount.moduleName));
  if(!gate.ok||!health.operational||simStepCounter>=p.expiresStep||observerC(r).emcon||ownerDamageEffectsD(r).ciwsPowerFac<=.15||mount.ammo<=0){e.closeInPending=null;return;}
  const local=[...h.c55Bank(mount).files.values()].find(q=>q.cmsTrackId===c.trackId&&q.confirmed&&q.audit?.accepted&&!q.protectedIdentity&&q.st.valid&&q.st.localAgeS<CIWS_C55_POLICY.releaseFreshS);if(!local){e.closeInHoldD="LOCAL_MEASUREMENT_REQUIRED";return;}const st=local.st;
  const sol=c.weapon==='RAM'?h.ciwsInterceptSolution(mount,st,520):h.ciwsGunBallisticInterceptSolution(mount,st);if(!sol||st.rangeM/1000>mount.engageRangeKm||st.rangeM/1000<(mount.minEngageKm??.1)){e.closeInHoldD="ENGAGEMENT_RANGE";return;}
  let az=sol.azRad,el=sol.elRad;
  if(c.weapon==='RAM'){const body=h.shipGameAimBodyV1(az,el);el=h.shipGameAimWorldV1(body.az,Math.max(body.el,deg(RAM_BLK1A_6DOF_LITE.launchElevationFloorDeg))).el;}
  h.ciwsGameSlewV1(mount,az,dt,el);mount.turretEl=mount.turretEl??0;
  const targetBody=h.shipGameAimBodyV1(az,el),errEl=targetBody.el-mount.turretEl,rate=clamp(errEl*5,-health.maxElevationRateRadS,health.maxElevationRateRadS);mount.turretEl+=rate*dt;
  const actual=h.shipGameAimWorldV1(h.ciwsBodyYawV1(mount),mount.turretEl),err=Math.abs(angNorm(actual.az-az));
  if(!h.ciwsGameCanFireV1(mount,actual.az,actual.el)||err>deg(c.weapon==='RAM'?15:.08)||Math.abs(actual.el-el)>deg(c.weapon==='RAM'?15:.08)){e.closeInHoldD="MOUNT_NOT_ALIGNED";return;}
  if(c.weapon==='PHALANX'&&!h.phalanxFireControlGate(mount,st,sol,err,false).ready)return;
  if(c.weapon==='RAM'){
    if((mount.reloadTimer??0)>0)return;
    const o=h.wip199CiwsMuzzleStateM(mount,actual.az,actual.el,3.45,.45),speed=RAM_BLK1A_6DOF_LITE.launchKinematicSeedMps,ce=Math.cos(actual.el),m={id:++ENGAGEMENT_RUNTIME.world.navalWeaponSerialD,ownerEntityId:r.entityId,isRAM:true,x:metersToWorld(o.xM),y:metersToWorld(o.yM),z:o.zM,vx:mpsToWorldSpeed(o.vxMps+speed*ce*Math.cos(actual.az)),vy:mpsToWorldSpeed(o.vyMps+speed*ce*Math.sin(actual.az)),vz:o.vzMps+speed*Math.sin(actual.el),speedMps:speed,maxG:RAM_BLK1A_6DOF_LITE.optimalManeuverG,targetId:c.trackId,ownerTrackKeyD:ownerTrackKeyD(r.entityId,c.trackId),alive:true,life:0,maxLife:12,_seekerQuality:st.quality,_seekerCaptured:false,_seekerMode:'MEM',_launchRangeM:st.rangeM,_launchOffBore:err,_crossingAngle:0,_launchTrackSource:st.source,_launchPlatform:'SEARAM_TRAIN_ELEVATION_MOUNT',_launchAzimuthRad:actual.az,_launchElevationRad:actual.el};
    h.initializeRamSeeker(m,st);h.initializeRamSixDof(m);e.ram.push(m);mount.ammo--;mount.reloadTimer=health.reloadIntervalS;e.closeInPending=null;r.mass.markWeaponsDirty('SEARAM_FIRE');
  }else{
    const count=Math.min(mount.ammo,ciwsB3AdvanceGunAccumulator(mount,dt,health)),sigma=phalanxDispersionSigmaRad();
    for(let i=0;i<count;i++){const azShot=actual.az+observerNormalC(e.weaponRng)*sigma,elShot=actual.el+observerNormalC(e.weaponRng)*sigma,o=h.wip199CiwsMuzzleStateM(mount,azShot,elShot,3.02,.25),v=PHALANX_MK244_BALLISTICS.muzzleVelocityMps,ce=Math.cos(elShot);
      e.bullets.push({id:++ENGAGEMENT_RUNTIME.world.navalWeaponSerialD,ownerEntityId:r.entityId,mountId:mount.id,engagementTrackId:c.trackId,life:0,maxLife:Math.min(PHALANX_MK244_BALLISTICS.maxFlightTimeS,Math.max(.45,sol.tof*1.35)),x:metersToWorld(o.xM),y:metersToWorld(o.yM),z:o.zM,vx:mpsToWorldSpeed(o.vxMps+v*ce*Math.cos(azShot)),vy:mpsToWorldSpeed(o.vyMps+v*ce*Math.sin(azShot)),vz:o.vzMps+v*Math.sin(elShot)});mount.ammo--;}
    if(count>0){mount.firing=true;r.mass.markWeaponsDirty('PHALANX_FIRE');e.closeInPending=null;}
  }
}
function navalFlightObjectsD(){return [...enemyMissiles,...missiles.filter(m=>!m.dead),...ramMissiles.filter(m=>m.alive),...harpoonWorldA().filter(m=>m.alive),...physicalShipsB().flatMap(r=>[...(r.weapons.executionD?.sam??[]).filter(m=>!m.dead),...(r.weapons.executionD?.ram??[]).filter(m=>m.alive)])];}
function ownerRamRfD(rm,dt,h){
 const cfg=RAM_BLK1A_SEEKER_MODEL.rf;if(!h.sensorDwellDue('RAM_RF_D:'+rm.id,cfg.frameS,dt))return null;
 const bs=h.ramSeekerBoresight(rm,'RF'),pred=rm._ramRfTrack?.valid?rm._ramRfTrack:rm._ramMemTrack,rows=[];
 for(const m of navalFlightObjectsD()){
  // Physical emissions only. A Harpoon emits seeker RF only after activation.
  const emit=m.weaponKey==='HARPOON'?(m.seeker.active?1:0):ramEmitterStrength(m);if(!emit||m===rm||m.dead||m.alive===false)continue;
  const dx=worldToMeters(m.x-rm.x),dy=worldToMeters(m.y-rm.y),dz=(m.z??0)-rm.z,r=Math.max(1,Math.hypot(dx,dy,dz)),az=Math.atan2(dy,dx),el=Math.atan2(dz,Math.hypot(dx,dy));
  if(Math.hypot(angNorm(az-bs.az),el-bs.el)>deg(cfg.gimbalDeg)||terrainLineOfSightFactor(rm.x,rm.y,rm.z,m.x,m.y,m.z)<=0)continue;
  const snr=emit*(cfg.referenceRangeM/r)**2/(1+.75*Math.exp(-Math.abs(el)/deg(2))),pd=clamp(1-Math.exp(-.85*snr),.02,.995);if(h.simRandom()>pd)continue;
  const maz=az+h.gaussRand(0,deg(cfg.azSigmaDeg)/Math.sqrt(Math.max(.25,snr))),mel=el+h.gaussRand(0,deg(cfg.elSigmaDeg)/Math.sqrt(Math.max(.25,snr))),inn=Math.hypot(angNorm(maz-(pred?.azRad??bs.az)),mel-(pred?.elRad??bs.el)),gate=deg(pred?.valid?cfg.gateTrackDeg:cfg.gateAcquireDeg),cont=Math.exp(-.5*(inn/Math.max(deg(.25),gate))**2),signalScore=clamp(Math.log1p(snr)/Math.log(8),0,1);
  rows.push({azRad:maz,elRad:mel,snr,signal:snr,extentRad:deg(.08),quality:clamp(.35+.45*signalScore+.20*cont,0,1),score:.78*cont+.22*signalScore});
 }rows.sort((a,b)=>b.score-a.score);return rows[0]??null;
}
function stepOwnerPhalanxD(r,dt,applyHit){const e=r.weapons.executionD;
  for(const b of e.bullets){const prev={x:b.x,y:b.y,z:b.z},q=phalanxIntegratePointMass({x:worldToMeters(b.x),y:worldToMeters(b.y),z:b.z,vx:worldSpeedToMps(b.vx),vy:worldSpeedToMps(b.vy),vz:b.vz},dt);Object.assign(b,{x:metersToWorld(q.x),y:metersToWorld(q.y),z:q.z,vx:mpsToWorldSpeed(q.vx),vy:mpsToWorldSpeed(q.vy),vz:q.vz});b.life+=dt;
    for(const target of navalFlightObjectsD()){if(target.dead||target.alive===false||target.ownerEntityId===r.entityId)continue;const hit=ciwsBulletSweptHit(b,target,prev.x,prev.y,prev.z,dt);if(!hit.hit)continue;applyHit(target,hit.relSpeedMps,b.engagementTrackId,hit);b.life=b.maxLife;break;}
  }for(let i=e.bullets.length-1;i>=0;i--)if(e.bullets[i].life>=e.bullets[i].maxLife||e.bullets[i].z<0)e.bullets.splice(i,1);
}

// Physical fuze sensor geometry only, never an AI target association.
function navalFuzeTargetD(m,r){
 let best=null,range=2200;for(const q of navalFlightObjectsD()){
  if(q===m||q.ownerEntityId===r.entityId||q.alive===false||q.dead)continue;
  const d=Math.hypot(worldToMeters(q.x-m.x),worldToMeters(q.y-m.y),(q.z??0)-m.z);
  if(d<range){best=q;range=d;}
 }return best;
}

function navalIncomingOrdnanceD(r){if(!physicalShipsB().length)return enemyMissiles;return navalFlightObjectsD().filter(m=>m.ownerEntityId!==r.entityId);}
function navalCiwsSourcesD(r){
 const e=r===ACTIVE_SHIP_RUNTIME?{sam:missiles,ram:ramMissiles}:r.weapons.executionD,
   sources=navalFlightObjectsD().filter(m=>m.alive!==false&&!m.dead).map(m=>({e:m,key:'NAVAL_SENSOR:'+String(m.ownerEntityId??'SCENARIO')+':'+m.id,rcs:m.rcsM2??null,own:m.weaponKey!=='HARPOON'&&m.ownerEntityId===r.entityId}));
 // Own no-DL Harpoon identity can be protected only through measured CMS association.
 for(const m of [...e.sam,...e.ram])if(!m.dead&&m.alive!==false&&!sources.some(q=>q.e===m))sources.push({e:m,key:'OWN:'+r.entityId+':'+m.id,rcs:.04,own:true});
 for(const m of targetPool)if(m.alive!==false)sources.push({e:m,key:'AIR:'+m.id,rcs:null,own:false});return sources;
}
