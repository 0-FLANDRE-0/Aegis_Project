function harpoonRfObservationsA(m,beamAz,beamEl){
  const cfg=HARPOON_PROFILE_A.sim,rx={x:m.x,y:m.y,z:m.z},hint=harpoonPredictionA(m.memory,m.ageS,m.navPositionM),focus=Math.hypot(hint.x-m.navPositionM.x,hint.y-m.navPositionM.y),
    field={receiver:rx,band:'IJ',beamAz,beamEl,beamHalfAzRad:cfg.seekerBeamHalfRad,beamHalfElRad:cfg.seekerBeamHalfElRad,
      maxRangeKm:cfg.seekerRangeM/1000,minRangeM:100,focusRangeM:focus,rangeResolutionM:35,azimuthCells:3,rangeCells:6},out=[];
  for(const q of physicalRfReflectorRegistryWip13A3({band:'IJ',excludeObject:m,seaField:field})){
    const dx=worldToMeters(q.x-m.x),dy=worldToMeters(q.y-m.y),dz=(q.z??0)-m.z,range=Math.hypot(dx,dy,dz),az=Math.atan2(dy,dx),el=Math.atan2(dz,Math.hypot(dx,dy)),off=angNorm(az-beamAz),bodyAz=angNorm(az-m.yawRad),bodyEl=el-m.pitchRad;
    if(range<25||range>cfg.seekerRangeM||Math.abs(off)>cfg.seekerBeamHalfRad||Math.abs(el-beamEl)>cfg.seekerBeamHalfElRad||Math.abs(bodyAz)>cfg.seekerGimbalRad||Math.abs(bodyEl)>cfg.seekerElGimbalRad)continue;
    const los=terrainAwareRadarLOS(m.x,m.y,m.z,q.x,q.y,q.z??0,1.4);if(los<=.01)continue;
    const rcs=rfReflectorRcsM2Wip13A2(q,'IJ',m.x,m.y,m.z),gain=Math.exp(-2.7726*(off/cfg.seekerBeamHalfRad)**2),
      weather=maritimeRfWeatherPathFactorWip13A3('IJ',range*.002),commonSnr=seekerSynthesizeMonostaticPowerU2('HARPOON',{referenceSnr:cfg.seekerReferenceSnr,rcsM2:rcs,referenceRcsM2:cfg.seekerReferenceRcsM2,referenceRangeM:cfg.seekerReferenceRangeM,rangeM:range,txRxGain:gain,losQ:los,pathQ:weather});
    let snr=commonSnr;
    if(SEEKER_U3_HARPOON_RF_MODE_A==='SHADOW'){
      const legacySnr=cfg.seekerReferenceSnr*(rcs/cfg.seekerReferenceRcsM2)*(cfg.seekerReferenceRangeM/range)**4*gain*los*weather;
      seekerU3HarpoonCompareNumberA('power',legacySnr,commonSnr);snr=legacySnr;
    }
    if(snr<cfg.seekerMinSnr||harpoonRandomA(m)>clamp(1-Math.exp(-snr/7),.05,.997))continue;
    const rvx=worldSpeedToMps(q.vx??0)-m.velocityMps.x,rvy=worldSpeedToMps(q.vy??0)-m.velocityMps.y,rvz=(q.vz??0)-m.velocityMps.z,
      radial=(rvx*dx+rvy*dy+rvz*dz)/range,noise=Math.sqrt(12/Math.max(3,snr));
    out.push({rangeM:Math.max(1,range+harpoonNoiseA(m)*cfg.seekerRangeSigmaM*noise),
      bearingRad:angNorm(bodyAz+harpoonNoiseA(m)*cfg.seekerAzSigmaRad*noise),elevationRad:bodyEl+harpoonNoiseA(m)*.002*noise,
      radialMps:radial+harpoonNoiseA(m)*.6*noise,verticalExtentM:Math.max(0,(q.extentVerticalM??0)+harpoonNoiseA(m)*.35),
      rangeExtentM:Math.max(0,(q.extentRangeM??0)+harpoonNoiseA(m)*2),dopplerSpreadMps:q.dopplerSpreadMps??0,snr,noiseScale:noise});
  }
  const common=seekerResolveCellsU2('HARPOON',this,[out.slice(),96]);
  if(SEEKER_U3_HARPOON_RF_MODE_A==='SHADOW'){
    const legacy=out.slice().sort((a,b)=>b.snr-a.snr).slice(0,96);seekerU3HarpoonCompareCellsA(legacy,common);return legacy;
  }
  return common;
}
