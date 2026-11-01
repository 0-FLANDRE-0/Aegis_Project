// TEST ONLY: ideal received track, constant-velocity Kh-35U, actual release/spawn,
// native projectile updater, physical fuze, fragment field and damage path.
window.__B2_RANGE_PROBE__=({seed,rangeKm,bearing=0,surface=false,interceptRange=false})=>{
 __GB_TEST__.reset(seed);const dyn=getShipDynamicsV15();dyn.haltHorizontalContact();Object.assign(shipNav,{vx:0,vy:0,speedMps:0,surgeMps:0,swayMps:0});
 const scene=_wip75CreateTarget({rangeKm,bearingDeg:bearing,altM:10,speedMps:surface?10:280}),em=scene.em;em.label='Kh-35U';em.type='SUBSONIC';wip112EnsureTargetState(em);
 const id=scene.trackId,tr=scene.tr;tr.classification='ASM';tr.domain='AIR';tr.isASM=true;tr._operatorIdentity=tr.identity='HOSTILE';tr.confirmed=true;
 // This explicit ideal observation is the harness input, not a production truth correction.
 const sync=()=>{tr.x=em.x;tr.y=em.y;tr.z=em.z;tr.vx=em.vx;tr.vy=em.vy;tr.vz=em.vz;tr.sensorAge=0;tr._lastMeasurementStep=simStepCounter;tr._kfX=new Float64Array([worldToMeters(tr.x),worldToMeters(tr.y),tr.z,worldSpeedToMps(tr.vx),worldSpeedToMps(tr.vy),tr.vz]);tr._kfP=new Float64Array(36);};sync();
 let chosen=null,reason=null;for(const [mount,g]of gunB1OwnGuns()){g.selectAmmo('MFF_127_SIM');const q=g.command(id,'MFF_127_SIM');if(q.ok||interceptRange){chosen={mount,g};break;}reason=q.reason;}
 if(!chosen)return {seed,rangeKm,bearing,pk:0,reason:'NO_NATIVE_SOLUTION:'+reason};const {mount,g}=chosen;
 let firingRangeKm=rangeKm,plannedInterceptM=null;
 if(interceptRange){
  const original={x:aircraft.x(),y:aircraft.y()},direction=deg(bearing),hp=ACTIVE_SHIP_PROFILE.geometry.hardpoints[g.installation.hardpointId],center=shipGamePointStateV1(hp),atDistance=km=>{em.x=original.x+Math.cos(direction)*kmToWorld(km);em.y=original.y+Math.sin(direction)*kmToWorld(km);sync();const az=g.snapshot().bodyAzRad,off=g.spec.mount.trunnionOffsetM,origin=shipGamePointStateV1({x:hp.x+off.x*Math.cos(az)-off.y*Math.sin(az),y:hp.y+off.x*Math.sin(az)+off.y*Math.cos(az),z:hp.z+off.z}),q=g.solveState({xM:worldToMeters(tr.x),yM:worldToMeters(tr.y),zM:tr.z,vxMps:worldSpeedToMps(tr.vx),vyMps:worldSpeedToMps(tr.vy),vzMps:tr.vz},'MFF_127_SIM',{originM:{x:origin.xM,y:origin.yM,z:origin.zM},platformVelocityMps:{x:origin.vxMps,y:origin.vyMps,z:origin.vzMps},environment:maritimeEnvironmentSnapshotWip13A3()});return {q,d:q.ok?Math.hypot(q.predictedAimPointM.x-center.xM,q.predictedAimPointM.y-center.yM):null};};
  let lo=rangeKm,hi=Math.min(23.8,rangeKm*2+1),upper=atDistance(hi);if(!upper.q.ok||upper.d<rangeKm*1000)return {seed,rangeKm,bearing,pk:0,reason:'INTERCEPT_BIN_UNREACHABLE',solver:upper.q};
  for(let i=0;i<20;i++){const mid=(lo+hi)/2,r=atDistance(mid);if(!r.q.ok)return {seed,rangeKm,bearing,pk:0,reason:'INTERCEPT_BIN_SOLVE_FAILED'};if(r.d<rangeKm*1000)lo=mid;else hi=mid;}
  firingRangeKm=(lo+hi)/2;const r=atDistance(firingRangeKm);plannedInterceptM=r.d;const finalCommand=g.command(id,'MFF_127_SIM');if(!finalCommand.ok)return {seed,rangeKm,bearing,mount,firingRangeKm,plannedInterceptM,pk:0,reason:'NATIVE_FINAL_RELEASE_WITHHELD:'+finalCommand.reason,finalCommand};
 }
 let release;
 for(let i=0;i<900;i++){sync();g.step(SIM_FIXED_DT);simStepCounter++;sync();release=g.requestFire(id,{mode:'MANUAL',ammoId:'MFF_127_SIM',allowQueue:false});if(release.projectileId)break;}
 if(!release?.projectileId)return {seed,rangeKm,bearing,mount,pk:0,reason:'NO_RELEASE:'+release?.reason};
 const p=mainGunProjectilesWip13B3.find(p=>p.id===release.projectileId),origin={...p.positionM},age=g.snapshot().solution.ageS;let minimumM=Infinity;
 for(let i=0;i<7200&&p.alive;i++){minimumM=Math.min(minimumM,Math.hypot(p.positionM.x-worldToMeters(em.x),p.positionM.y-worldToMeters(em.y),p.positionM.z-em.z));updateMainGunProjectilesWip13B3(SIM_FIXED_DT);em.x+=em.vx*SIM_FIXED_DT;em.y+=em.vy*SIM_FIXED_DT;em.z+=em.vz*SIM_FIXED_DT;simStepCounter++;}
 const burst=gunB1Log.find(x=>x.kind==='AIRBURST'&&x.projectileId===p.id),result=burst?.results.find(x=>x.kind==='ASM'&&x.id===em.id),distanceKm=burst?Math.hypot(burst.positionM.x-origin.x,burst.positionM.y-origin.y)/1000:null;
 return {seed,rangeKm,bearing,mount,firingRangeKm,plannedInterceptM,release,solutionAgeS:age,pk:result?.pk??0,outcome:result?.result??null,reason:p.retiredReason,burstRangeKm:distanceKm,burstAgeS:burst?.ageS??null,minimumM,fragment:result??null,dispersion:p._gunB2Dispersion,core:window.__CORE_SELFTEST_FAILURES__};
};
