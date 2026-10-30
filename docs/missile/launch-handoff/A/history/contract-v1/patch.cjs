// LAUNCH_HANDOFF_A. SIM_TUNED readiness contract, frozen before candidate flights.
// Reuse profile tolerances/speed/clearance, never increase control authority.
const HELPER=`function samLaunchHandoffGateA(m,cfg,cor,own,altM){
    // SI: own velocity m/s, angles rad, altitude m. Air Standard only.
    // 'Forward' is along the intended 3-D launch corridor, not the sea plane.
    const v=own?.velMps,u={x:Math.cos(cor.desiredPitch)*Math.cos(cor.bearing),y:Math.cos(cor.desiredPitch)*Math.sin(cor.bearing),z:Math.sin(cor.desiredPitch)};
    const finite=!!v&&[v.x,v.y,v.z,altM,m.heading,m.pitch,cor.desiredPitch,cor.bearing,cfg.pitchTol,cfg.headingTol,cfg.minForwardMps,cfg.exitAltM,cfg.pitMinS].every(Number.isFinite);
    const speed3DMps=finite?Math.hypot(v.x,v.y,v.z):0,horizontalMps=finite?Math.hypot(v.x,v.y):0;
    const alongCorridorMps=finite?v.x*u.x+v.y*u.y+v.z*u.z:0;
    const corridorErrorRad=finite&&speed3DMps>1e-9?Math.acos(clamp(alongCorridorMps/speed3DMps,-1,1)):Math.PI;
    const body={x:Math.cos(m.pitch??0)*Math.cos(m.heading??0),y:Math.cos(m.pitch??0)*Math.sin(m.heading??0),z:Math.sin(m.pitch??0)};
    const incidenceRad=finite&&speed3DMps>1e-9?Math.acos(clamp((body.x*v.x+body.y*v.y+body.z*v.z)/speed3DMps,-1,1)):Math.PI;
    // Preserve the physical incidence bound from the existing dynamics sample.
    // Before a valid sample, use the existing smaller alignment tolerance.
    const incidenceLimitRad=Number.isFinite(m.aoaMaxDyn)&&m.aoaMaxDyn>0?m.aoaMaxDyn:Math.min(cfg.pitchTol,cfg.headingTol);
    const attitudeReady=finite&&Math.abs(angNorm(cor.bearing-m.heading))<=cfg.headingTol&&Math.abs(cor.desiredPitch-m.pitch)<=cfg.pitchTol;
    const corridorAligned=finite&&corridorErrorRad<=cfg.pitchTol;
    const incidenceReady=finite&&incidenceRad<=incidenceLimitRad;
    const speedReady=finite&&alongCorridorMps>=cfg.minForwardMps&&alongCorridorMps>0;
    const clearanceReady=finite&&altM>=cfg.exitAltM,minTimeDone=(m.pitchoverTimer??0)>=cfg.pitMinS;
    const velocityReady=corridorAligned&&incidenceReady&&speedReady;
    const blocked=[];if(!finite)blocked.push('NONFINITE');if(!attitudeReady)blocked.push('BODY_ATTITUDE');if(!corridorAligned)blocked.push('CORRIDOR_ALIGNMENT');if(!incidenceReady)blocked.push('EXCESS_INCIDENCE');if(!speedReady)blocked.push('ALONG_CORRIDOR_SPEED');if(!clearanceReady)blocked.push('CLEARANCE');if(!minTimeDone)blocked.push('MINIMUM_SETTLING_TIME');
    return {contract:'AIR_STANDARD_3D_CORRIDOR_A',atS:m.life??0,ready:attitudeReady&&velocityReady&&clearanceReady&&minTimeDone,attitudeReady,velocityReady,clearanceReady,minTimeDone,corridorAligned,incidenceReady,speedReady,alongCorridorMps,speed3DMps,horizontalMps,corridorErrorRad,incidenceRad,incidenceLimitRad,desiredPitchRad:cor.desiredPitch,velocityPitchRad:finite?Math.atan2(v.z,horizontalMps):null,deadlineExceeded:(m.pitchoverTimer??0)>=cfg.pitMaxS,blocked};
  }`;
function patch(symbols){const before=symbols.get('updateMissileBodyB3').code;let after=before;after=after.replace('inside the launch corridor. SM-2 keeps its proven WIP56 gate unchanged.','inside the launch corridor. LAUNCH_HANDOFF_A extends relative corridor readiness to air Standard; surface/ESSM remain separate.');
 const old='const pitchEnvelopeReady=isESSM?vectorAligned:Math.abs(m.velPitch??0)<=cfg.maxVelExit;\n      const velocityReady=forwardMps>=cfg.minForwardMps&&vectorAligned&&surfaceVectorAligned&&pitchEnvelopeReady;';
 const replacement=`// LAUNCH_HANDOFF_A: air Standard uses the intended 3-D corridor.
      // ESSM and surface mode retain their existing vector/clearance contract.
      const airStandard=m.guidanceCore==='v1'&&!isESSM&&!surfaceMissileRuntimeWip13C6(m)&&['SM2MR_BLKIIIA_SIM','SM2ER_BLKIV_SIM','SM6_BLKIA_SIM'].includes(m._v1Profile?.id);
      const airHandoff=airStandard?samLaunchHandoffGateA(m,cfg,cor,_b1Own,mslAlt):null;
      if(airHandoff)m._launchHandoffA=airHandoff;
      const pitchEnvelopeReady=isESSM?vectorAligned:airHandoff?airHandoff.corridorAligned:Math.abs(m.velPitch??0)<=cfg.maxVelExit;
      const velocityReady=airHandoff?airHandoff.velocityReady:forwardMps>=cfg.minForwardMps&&vectorAligned&&surfaceVectorAligned&&pitchEnvelopeReady;`;
 if(after.split(old).length!==2)throw Error('LAUNCH_GATE_NOT_UNIQUE');after=after.replace(old,replacement);
 const oldGate='m._pitchoverGate={attitudeReady,velocityReady,vectorAligned:vectorAligned&&surfaceVectorAligned,velPitchErr,velHdgErr,clearanceReady,minTimeDone,deadlineExceeded,hdgErr,pitchErr,forwardMps};';
 after=after.replace(oldGate,'m._pitchoverGate={attitudeReady,velocityReady,vectorAligned:airHandoff?airHandoff.corridorAligned:vectorAligned&&surfaceVectorAligned,velPitchErr,velHdgErr,clearanceReady,minTimeDone,deadlineExceeded,hdgErr,pitchErr,forwardMps,pitchEnvelopeReady,airHandoff};');
 if(after===before||!after.includes('pitchEnvelopeReady,airHandoff'))throw Error('NO_HANDOFF_PATCH');return{functions:{updateMissileBodyB3:{before,after,line:symbols.get('updateMissileBodyB3').line}},additions:[HELPER]};}
module.exports={patch,HELPER};
