// IMU/altimeter simulation is a physical sensor boundary, not ship telemetry.
// The inertial solution integrates measured delta-v/gyro increments; no position reset,
// GPS, target truth, ship tracks or post-launch uplink exists in this navigation path.
function harpoonInsInitC(pos,vel,axis,serial){
  const cfg=HARPOON_PROFILE_A.sim,a=serial*2.7;
  return {velocityMps:{x:vel.x+Math.cos(a)*cfg.navDriftMps,y:vel.y+Math.sin(a)*cfg.navDriftMps,z:vel.z},
    yawRad:Math.atan2(axis.y,axis.x),pitchRad:Math.atan2(axis.z,Math.hypot(axis.x,axis.y)),
    accelBiasMps2:{x:Math.cos(a+.7)*cfg.navAccelBiasMps2,y:Math.sin(a+.7)*cfg.navAccelBiasMps2,z:0},
    gyroBiasRadS:Math.sin(a)*cfg.navGyroBiasRadS,samples:0,source:'INTEGRATED_IMU_NO_DL'};
}
function harpoonImuSampleC(m,before,dt){
  const n=m.ins,cfg=HARPOON_PROFILE_A.sim;
  // Ideal delta-v from physical motion, then sensor bias and orientation error.
  // This is the only physical-state adapter for the inertial navigator.
  const dx=m.velocityMps.x-before.velocityMps.x,dy=m.velocityMps.y-before.velocityMps.y,
    error=angNorm(n.yawRad-before.yawRad),c=Math.cos(error),s=Math.sin(error);
  n.velocityMps.x+=dx*c-dy*s+n.accelBiasMps2.x*dt;
  n.velocityMps.y+=dx*s+dy*c+n.accelBiasMps2.y*dt;
  n.velocityMps.z+=m.velocityMps.z-before.velocityMps.z+n.accelBiasMps2.z*dt;
  n.yawRad=angNorm(n.yawRad+angNorm(m.yawRad-before.yawRad)+n.gyroBiasRadS*dt);
  n.pitchRad=clamp(n.pitchRad+m.pitchRad-before.pitchRad,-Math.PI/2,Math.PI/2);
  for(const k of ['x','y','z'])m.navPositionM[k]+=n.velocityMps[k]*dt;
  m.radarAltitudeM=m.positionM.z-maritimeSeaLevelAtSimulationMetersWip13A3(m.positionM.x,m.positionM.y)+Math.sin(m.ageS*.7+m.id)*cfg.altimeterErrorM;
  n.samples++;
}

function harpoonMemoryElapsedC(memory,flightAgeS){
  // Current ship EKF is already propagated to the release epoch. Measurement
  // age affects readiness/uncertainty, never another propagation of that mean.
  // A detached dated-observation fixture may explicitly carry its state age.
  return flightAgeS+(Number.isFinite(memory.stateAgeS)?Math.max(0,memory.stateAgeS):Math.max(0,Number(memory.observationAgeS)||0));
}
