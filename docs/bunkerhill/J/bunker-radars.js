// The historical suffix is explicitly unresolved; this runtime implements the
// user's AN/SPQ-9 non-B configuration, rather than claiming a verified refit.
function bunkerRadarMask(id,worldAzRad,worldElRad=0){
  const r=BUNKER_REGISTRATION.radars.find(r=>r.id===id),f=shipGameFrameV1(),d=f.vectorToBody({
    x:Math.cos(worldElRad)*Math.cos(worldAzRad),y:Math.cos(worldElRad)*Math.sin(worldAzRad),z:Math.sin(worldElRad)});
  return bunkerRaySource(r.center,d,300,id==='SPQ9'?'ANTENNA:SPQ9':null);
}
function bunkerSpq9CollectPlots(){
  const h=spq9bHealth01(),p=ACTIVE_SHIP_PROFILE.sensors.spq9b,r=BUNKER_REGISTRATION.radars.find(r=>r.id==='SPQ9'),
    src=wip199ShipLocalWorldPoint(r.center.x,r.center.y,r.center.z),
    empty={schema:'AEGIS_CG52_SPQ9_2D_SWEEP_V1',dwells:[],air:[],surface:[],backgroundRejected:0,ambiguousRejected:0,
      elevationObservable:false,specializedBLookback:false,antennaLayoutBasis:p.antennaLayoutBasis};
  const receiver={x:src.x,y:src.y,z:src.z,vxMps:worldSpeedToMps(shipNav.vx),vyMps:worldSpeedToMps(shipNav.vy),vzMps:0},
    dwells=[],surface=[];let backgroundRejected=0,ambiguousRejected=0;
  for(let panel=0;panel<p.panelOffsetsRad.length;panel++){
    const beam=rotatingSweepBeamWorldWip13B13(spq9bPrevRotorAngle,spq9bRotorAngle,p.panelOffsetsRad[panel],deg(.6));
    if(beam.sweepRad<=1e-12||bunkerRadarMask('SPQ9',beam.azWorld))continue;
    const dwell=shipboardRadarEchoFieldWip13B13({radarId:'SPQ9B',band:'X',receiver,beamAz:beam.azWorld,beamEl:0,
      beamHalfAzRad:beam.azHalfRad,beamHalfElRad:deg(10),maxRangeKm:p.searchMaxRangeKm,minRangeM:p.minimumRangeM,
      // Distributed sea/terrain cells remain in the receiver's local clutter
      // power and CFAR noise floor. They are background energy, not resolved
      // point detections to promote into the surface track manager. Match the
      // shared SPY and navigation receiver policy, including rough seas.
      rangeResolutionM:25,seaAzimuthCells:3,seaRangeCells:6,maxDistributedEchoes:0,health:h,
      snrReferenceRangeKm:p.snrReferenceRangeKm,snrReferenceRcsM2:1,clutterLeak01:.00025,receiverNoiseNorm:.04,
      pdHalfSnr:1.1,rangeSigmaM:13,azSigmaDeg:.085,elSigmaDeg:10,dopplerSigmaMps:3,losMarginM:1.2,includeSea:true});
    dwells.push(dwell);
  for(const echo of dwell.echoes){
    if(bunkerRadarMask('SPQ9',echo.azRad,echo.elRad))continue;
    const evidence=shipboardRadarDomainEvidenceWip13B13(echo,{elevationObservable:false,surfaceBiased:true});
    if(evidence.candidateDomain==='BACKGROUND'){backgroundRejected++;continue;}
    if(!shipboardRadarSurfaceDiscreteEvidenceWip13B13(evidence)){ambiguousRejected++;continue;}
    const plot=shipboardRadarEchoToSurfacePlotWip13B13(echo,evidence,'SPQ9B_SURFACE_PRECISION',BRIDGEMASTER_E_TRACK_REFERENCE_Z_M);
    surface.push({plot,panel,pd:echo.pd,snr:echo.snr,rcs:echo.apparentRcsM2,
      vertical:{combinedQ:1,selectedLobe:'TWO_DIMENSIONAL_SURFACE',elevationObservable:false}});
  }
  }
  return {...empty,dwells,surface,backgroundRejected,ambiguousRejected,masked:dwells.length===0};
}
function bunkerRadarAudit(){
  const rows=bunkerAuxNavSnapshot(),spy=ACTIVE_SHIP_PROFILE.sensors.spy1dv,
    checks={twoRegisteredRadars:rows.length===2&&rows.map(r=>r.id).join(',')==='SPQ9,SPS73',
      spqOnMarkedMast:BUNKER_REGISTRATION.radars.find(r=>r.id==='SPQ9').component===120,
      spsOnMarkedMast:BUNKER_REGISTRATION.radars.find(r=>r.id==='SPS73').component===122,
      noYardarmScanners:BUNKER_REGISTRATION.radars.every(r=>![56,57,87,88].includes(r.component)),
      noDomeScanner:BUNKER_REGISTRATION.radars.every(r=>r.component!==744),
      nonBProfile:ACTIVE_SHIP_PROFILE.sensors.spq9b.moduleId==='SPQ9_CG52_V1'&&ACTIVE_SHIP_PROFILE.sensors.spq9b.processor==='CG52_SPQ9_2D',
      dualFaces:SPQ9B_PANEL_COUNT===2&&ACTIVE_SHIP_PROFILE.sensors.spq9b.panelOffsetsRad[1]===Math.PI,
      explicitLayoutSimTune:ACTIVE_SHIP_PROFILE.sensors.spq9b.antennaLayoutBasis.includes('SIM_TUNED'),
      publicSpqRange:Math.abs(SPQ9B_SEARCH_MAX_RANGE_KM_BASE-20*1.852)<1e-8,
      spsProfile:BRIDGEMASTER_E_INSTALLATION.moduleId==='SPS73_CG52_V1'&&BRIDGEMASTER_E_INSTALLATION.band==='X',
      immutableModules:Object.isFrozen(SHIP_EQUIPMENT_PROFILE_REGISTRY.SPQ9_CG52_V1)&&Object.isFrozen(SHIP_EQUIPMENT_PROFILE_REGISTRY.SPS73_CG52_V1),
      explicitSimTune:SHIP_EQUIPMENT_PROFILE_REGISTRY.SPS73_CG52_V1.provenance.includes('SIM_TUNED'),
      ownFrame:rows.every(q=>Number.isFinite(q.origin.x)&&Number.isFinite(q.rotorPivot.z)),
      noInventedNavScanners:ACTIVE_SHIP_RUNTIME.combatSystem.sensors.auxNav.length===0};
  return {schema:'AEGIS_CG52_FRONT_MAST_RADAR_AUDIT_V1',checks,radars:rows,pass:Object.values(checks).every(Boolean)};
}
function bunkerAuxRadarBeamStates(){
  const rows=bunkerAuxNavSnapshot(),f=shipGameFrameV1(),out={spq9b:[],bridgeMasterE:[]};
  for(const r of rows){
    const spq=r.id==='SPQ9',offsets=spq?ACTIVE_SHIP_PROFILE.sensors.spq9b.panelOffsetsRad:[0];
    for(let panel=0;panel<offsets.length;panel++){
    const az=shipNav.heading+r.angleRad+offsets[panel],range=(spq?SPQ9B_SEARCH_MAX_RANGE_KM:BRIDGEMASTER_E_TRACK_MAX_KM)*1000,
      origin=shipGameRenderPointV1(r.origin.x,r.origin.y,r.origin.z),mask=bunkerRadarMask(r.id,az),
      q={id:r.id+':'+panel+':2D',sensor:r.id,label:spq?'AN/SPQ-9':'AN/SPS-73',channel:'TWO_DIMENSIONAL_SURFACE',
        role:spq?'SURFACE_SEARCH_AND_GUN_FIRE_CONTROL':'NAVIGATION_AND_SURFACE_SEARCH',panel,panels:offsets.length,...origin,
        sourceFrame:'SHIP_BODY_X_BOW_Y_STARBOARD_Z_UP',sourceXM:r.origin.x,sourceYM:r.origin.y,sourceZM:r.origin.z,
        azRelRad:angNorm(az),azWorldRad:angNorm(az),panelOffsetRad:offsets[panel],elRad:0,fovAzFullDeg:spq?1.2:BRIDGEMASTER_E_BEAM_AZ_FULL_DEG,fovElFullDeg:20,
        rangeM:mask?Math.min(range,mask.distanceM):range,displayRangeCapM:range,rpm:30,health01:r.health01,
        emitting:!emconActive&&r.health01>.08&&!mask,masked:!!mask,obstruction:mask?.name??null,
        nominalRevisitS:60/(30*offsets.length),elevationObservable:false,modelBasis:spq?'USER_REQUESTED_DUAL_FACE_SIM_TUNED':'SIM_TUNED_2D_SCAN',presentationOnly:true,physicsFeedback:false};
    out[spq?'spq9b':'bridgeMasterE'].push(q);
    }
  }
  return out;
}
function bunkerAuxRadarPresentationAudit(beams=bunkerAuxRadarBeamStates()){
  const rows=[...(beams.spq9b??[]),...(beams.bridgeMasterE??[])],checks={
    dualSpqSingleSps:beams.spq9b?.length===2&&beams.bridgeMasterE?.length===1,
    antipodalFaces:beams.spq9b?.length===2&&Math.abs(Math.abs(angNorm(beams.spq9b[0].azWorldRad-beams.spq9b[1].azWorldRad))-Math.PI)<1e-8,
    equipmentNames:rows.map(r=>r.sensor).join(',')==='SPQ9,SPQ9,SPS73',
    twoDimensional:rows.every(r=>r.panels===(r.sensor==='SPQ9'?2:1)&&r.channel==='TWO_DIMENSIONAL_SURFACE'&&r.elevationObservable===false),
    selectedBeamGeometry:rows.every(r=>r.fovAzFullDeg===1.2&&r.fovElFullDeg===20),
    sourceOrigins:rows.every(q=>{const r=BUNKER_REGISTRATION.radars.find(r=>r.id===q.sensor);
      if(!r)return false;const p=shipGameRenderPointV1(r.center.x,r.center.y,r.center.z);
      return Math.hypot(q.xM-p.xM,q.yM-p.yM,q.zM-p.zM)<1e-8&&
        Math.hypot(q.sourceXM-r.center.x,q.sourceYM-r.center.y,q.sourceZM-r.center.z)<1e-8;}),
    maskedRanges:rows.every(q=>{const max=(q.sensor==='SPQ9'?SPQ9B_SEARCH_MAX_RANGE_KM:BRIDGEMASTER_E_TRACK_MAX_KM)*1000;
      return q.rangeM>0&&q.rangeM<=max&&q.displayRangeCapM===max&&(!q.masked||!q.emitting);}),
    readOnly:rows.every(q=>q.presentationOnly===true&&q.physicsFeedback===false)};
  return {schema:'AEGIS_CG52_2D_RADAR_PRESENTATION_AUDIT_V1',checks,pass:Object.values(checks).every(Boolean)};
}
