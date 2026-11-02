function spyFalsePlotV31(task){
    const mp=spyTaskMeasurementParams(task,null),maxRange=Math.max(SENSOR_MODEL.spy1dv.falsePlotMinRangeM+1,Number(task.gateRangeM)||worldToMeters(task.rangeWorld)||SPY1DV_SEARCH_MAX_RANGE_KM*1000);
    const minRange=Math.min(maxRange*0.55,SENSOR_MODEL.spy1dv.falsePlotMinRangeM),u=simRandom();
    // sqrt distribution is uniform in illuminated ground area rather than over-populating the ship.
    const rangeM=minRange+(maxRange-minRange)*Math.sqrt(u),az=task.azWorld+(simRandom()*2-1)*task.azHalfRad,el=task.elRad+(simRandom()*2-1)*task.elHalfRad;
    const hM=rangeM*Math.cos(el),ax=aircraft.x(),ay=aircraft.y(),losUx=Math.cos(el)*Math.cos(az),losUy=Math.cos(el)*Math.sin(az),losUz=Math.sin(el);
    return {x:ax+metersToWorld(hM*Math.cos(az)),y:ay+metersToWorld(hM*Math.sin(az)),z:OWN_ALT_M+rangeM*Math.sin(el),rangeM,azRad:az,elRad:el,
      radialMps:(simRandom()*2-1)*95,radialVelSigmaMps:mp.rvSigma*1.35,losUx,losUy,losUz,quality:clamp(mp.q*0.42,0.08,0.45),
      rangeSigmaM:mp.rangeSigma*1.35,azSigmaDeg:mp.azSigma*1.25,elSigmaDeg:mp.elSigma*1.35,source:'SPY1DV_'+task.type};
  }

  function spyCollectAnonymousPlotsV31(task){
    if(task.type.startsWith('SURFACE_'))return {plots:[],attempted:0};
    const plots=[];let attempted=0;
    for(const t of targetPool){if(!t.alive||!spyTruthInsideBeam(task,t))continue;attempted++;const p=spySynthesizeAnonymousTruthPlotV31(task,t,false);if(p){plots.push(p);spyScheduler.anonymousStats.truthPlots++;}}
    for(const em of enemyMissiles){if(!em.alive||!spyTruthInsideBeam(task,em))continue;attempted++;const p=spySynthesizeAnonymousTruthPlotV31(task,em,true);if(p){plots.push(p);spyScheduler.anonymousStats.truthPlots++;}}
    const focused=!task.type.startsWith('SEARCH_'),baseP=focused?SENSOR_MODEL.spy1dv.falsePlotProbabilityFocused:SENSOR_MODEL.spy1dv.falsePlotProbabilitySearch;
    const pFalse=clamp(baseP*(task.type==='SEARCH_HORIZON'?SENSOR_MODEL.spy1dv.falsePlotHorizonMultiplier:1),0,0.25);
    let falseCount=simRandom()<pFalse?1:0;
    if(falseCount>0&&simRandom()<pFalse*0.08)falseCount++;
    if(spyScheduler.forcedFalsePlots>0){const forced=Math.min(SENSOR_MODEL.spy1dv.falsePlotMaxPerDwell,spyScheduler.forcedFalsePlots);falseCount=Math.max(falseCount,forced);spyScheduler.forcedFalsePlots-=forced;}
    falseCount=Math.min(SENSOR_MODEL.spy1dv.falsePlotMaxPerDwell,falseCount);
    for(let i=0;i<falseCount;i++){plots.push(spyFalsePlotV31(task));spyScheduler.anonymousStats.falsePlots++;}
    return {plots,attempted:attempted+falseCount};
  }

  function spyCollectUnifiedEchoPlotsWip13B13(task){
    const mount=spySurfaceOriginWip13B9(task),mp=spyTaskMeasurementParams(task,null),gateRangeM=Math.max(500,Number(task.gateRangeM)||worldToMeters(task.rangeWorld)||SPY1DV_SEARCH_MAX_RANGE_KM*1000),focused=!task.type.startsWith('SEARCH_'),dwell=shipboardRadarEchoFieldWip13B13({
      radarId:'SPY1DV',band:'S',receiver:{x:mount.x,y:mount.y,z:mount.z,vxMps:mount.sensorVxMps,vyMps:mount.sensorVyMps,vzMps:0},beamAz:task.azWorld,beamEl:task.elRad,beamHalfAzRad:task.azHalfRad,beamHalfElRad:task.elHalfRad,maxRangeKm:Math.min(SPY1DV_SEARCH_MAX_RANGE_KM,gateRangeM*1.04/1000),minRangeM:120,focusRangeM:focused?gateRangeM:null,rangeResolutionM:Math.max(20,mp.rangeSigma*1.8),seaAzimuthCells:3,seaRangeCells:focused?5:6,maxDistributedEchoes:0,health:spyFaceHealth01(task.face)*spyFaceSteerGain(task.face,task.azWorld)*(task.snrBoost??1),snrReferenceRangeKm:SPY1DV_SNR_REF_RANGE_KM,snrReferenceRcsM2:1,clutterLeak01:.00012,receiverNoiseNorm:.035,pdHalfSnr:1,rangeSigmaM:mp.rangeSigma,azSigmaDeg:mp.azSigma,elSigmaDeg:mp.elSigma,dopplerSigmaMps:mp.rvSigma,losMarginM:1.4,includeSea:true
    }),airPlots=[],surfacePlots=[];let backgroundRejected=0,ambiguous=0;
    for(const echo of dwell.echoes){
      const evidence=shipboardRadarDomainEvidenceWip13B13(echo,{elevationObservable:true});if(evidence.candidateDomain==='BACKGROUND'){backgroundRejected++;continue;}
      const preferSurface=shipboardRadarSurfaceDiscreteEvidenceWip13B13(evidence);
      if(preferSurface){
        if(task.type==='SEARCH_HORIZON'||task.type==='SEARCH_VOLUME'||task.type.startsWith('SURFACE_')){const source=task.type.startsWith('SURFACE_')?'SPY1DV_'+task.type:'SPY1DV_SURFACE_SEARCH';surfacePlots.push(spySurfaceAnonymousPlotContractWip13B9(shipboardRadarEchoToSurfacePlotWip13B13(echo,evidence,source,BRIDGEMASTER_E_TRACK_REFERENCE_Z_M)));}
        else ambiguous++;
      }else if(evidence.candidateDomain==='AIR'&&!task.type.startsWith('SURFACE_'))airPlots.push(shipboardRadarEchoToAirPlotWip13B13(echo,evidence,'SPY1DV_'+task.type));else ambiguous++;
    }
    // Receiver/processing false alarms remain possible in addition to resolved physical clutter.
    // They are anonymous measurement-space plots and carry no forced domain.
    // The legacy probability represented both receiver false alarms and unresolved environmental
    // clutter.  Sea/terrain energy is now explicit in the common CFAR scene, so retain only the
    // small residual electronics/processing false-alarm component here to avoid double counting.
    const baseP=focused?SENSOR_MODEL.spy1dv.falsePlotProbabilityFocused:SENSOR_MODEL.spy1dv.falsePlotProbabilitySearch,pFalse=clamp(baseP*(task.type==='SEARCH_HORIZON'?SENSOR_MODEL.spy1dv.falsePlotHorizonMultiplier:1)*.0025,0,.01);let falseCount=shipboardRadarRandomWip13B13('SPY1DV')<pFalse?1:0;
    if(spyScheduler.forcedFalsePlots>0){const forced=Math.min(SENSOR_MODEL.spy1dv.falsePlotMaxPerDwell,spyScheduler.forcedFalsePlots);falseCount=Math.max(falseCount,forced);spyScheduler.forcedFalsePlots-=forced;}
    falseCount=Math.min(SENSOR_MODEL.spy1dv.falsePlotMaxPerDwell,falseCount);for(let i=0;i<falseCount;i++){airPlots.push(spyFalsePlotV31(task));spyScheduler.anonymousStats.falsePlots++;}
    spyScheduler.anonymousStats.truthPlots+=airPlots.length+surfacePlots.length-falseCount;
    return {schema:'AEGIS_SPY1DV_UNIFIED_DWELL_V48_WIP13B13',dwell,airPlots,surfacePlots,attempted:dwell.candidateCount+falseCount,backgroundRejected,ambiguous,falseCount};
  }

  function spyAssociationGateV31(task){
    return task.type==='PRECISION_REACQUIRE'?TRACK_FILTER_MODEL.nisGatePrecisionReacquire:(task.type==='TRACK_REACQUIRE'?TRACK_FILTER_MODEL.nisGateReacquire:(task.type.startsWith('SEARCH_')||task.type==='TRACK_CONFIRM'?TRACK_FILTER_MODEL.nisGateSearch:TRACK_FILTER_MODEL.nisGateNormal));
  }

  function spyBestPlotForTrackV31(trackId,plots,usedPlots,task){
    // A scheduler cycle may contain several physically separate dwells.  A track that was
    // measured by an earlier dwell is still a legal candidate here; one-to-one use is enforced
    // inside each dwell by usedPlots/usedTracks, not across the whole 25 ms scheduler cycle.
    const tr=tracks.get(trackId);if(!tr)return null;
    let best=null;for(let i=0;i<plots.length;i++){if(usedPlots.has(i))continue;const nis=trackRadarAssociationNisV31(tr,plots[i]),trackAGate=spyAssociationGateV31(task);if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{...trackATraceContextA('AIR_RADAR',plots[i].source,ACTIVE_SHIP_RUNTIME.entityId),route:'SPY_FOCUSED',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId,nis,gate:trackAGate,decision:nis<=trackAGate?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});if(nis<=trackAGate&&(!best||nis<best.nis))best={index:i,nis};}
    if(TRACK_A_DIAG.enabled)trackATraceEventA('ASSIGNMENT',best?plots[best.index]:{}, {...trackATraceContextA('AIR_RADAR','SPY1DV',ACTIVE_SHIP_RUNTIME.entityId),route:'SPY_FOCUSED',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId,decision:best?'ASSIGN':'NO_ASSIGNMENT',nis:best?.nis,reason:'NATIVE_FOCUSED_WINNER'});
    return best;
  }

  function spyGlobalAssignmentsV36(plots,usedPlots,usedTracks,task){
    // Batch, one-to-one minimum-total-NIS association for one physical dwell.  The extractor has
    // already emitted one plot per resolved echo, so an unassigned search plot is a legitimate
    // tentative-track candidate -- never evidence that it is a duplicate merely because another
    // formation member lies inside a broad covariance envelope.
    const plotIndices=[];for(let i=0;i<plots.length;i++)if(!usedPlots.has(i))plotIndices.push(i);
    const trackEntries=[...tracks].filter(([id,tr])=>!usedTracks.has(id)&&tr&&tr.sensorDetected!==false).sort((a,b)=>a[0]-b[0]);
    const assigned=new Map();if(!plotIndices.length||!trackEntries.length)return assigned;
    const gate=spyAssociationGateV31(task),dummyCost=gate+0.5,blockedCost=1e6;
    const costs=plotIndices.map(i=>[
      ...trackEntries.map(([,tr])=>{if(!trackMayAcceptAirPlotCrossDomainWip13B14(tr,plots[i])){if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{...trackATraceContextA('AIR_RADAR',plots[i].source,ACTIVE_SHIP_RUNTIME.entityId),route:'SPY_BATCH',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId:tr.trackId,decision:'REJECT',reason:'NATIVE_CROSS_DOMAIN_PARTITION',gate});return blockedCost;}const nis=trackRadarAssociationNisV31(tr,plots[i]),cross=trackSurfaceBackedWip13B14(tr);if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',plots[i],{...trackATraceContextA('AIR_RADAR',plots[i].source,ACTIVE_SHIP_RUNTIME.entityId),route:'SPY_BATCH',appliedModel:'AIR_POLAR_DOPPLER',appliedDimension:4,appliedFields:['rangeM','azRad','elRad','radialMps'],gateUnits:'NIS',trackId:tr.trackId,nis,gate:Math.min(gate,cross?WIP13B14_CROSS_DOMAIN_ASSOCIATION_CONTRACT.airToSurfaceNisGate:gate),decision:nis<=Math.min(gate,cross?WIP13B14_CROSS_DOMAIN_ASSOCIATION_CONTRACT.airToSurfaceNisGate:gate)?'ELIGIBLE':'REJECT',reason:'NATIVE_NIS'});return nis<=Math.min(gate,cross?WIP13B14_CROSS_DOMAIN_ASSOCIATION_CONTRACT.airToSurfaceNisGate:gate)?nis:blockedCost;}),
      ...new Array(plotIndices.length).fill(dummyCost)
    ]);
    // Preserve the actual native Hungarian result for SHADOW or an enabled
    // comparison trace. Default ACTIVE does not duplicate this pure solve.
    // Native NIS and cross-domain gates were evaluated exactly once above.
    const cols=(TRACK_B_IMPLEMENTATION_MODE!=='ACTIVE'||TRACK_B_DIAG.enabled)?bridgeMasterEMinCostAssignmentV35(costs):[],legacyPairs=[],trackBPairs=[];
    for(let row=0;row<cols.length;row++){
      const col=cols[row];if(col<0||col>=trackEntries.length||costs[row][col]>gate)continue;
      legacyPairs.push({i:plotIndices[row],id:trackEntries[col][0],nis:costs[row][col]});
    }
    for(let row=0;row<plotIndices.length;row++)for(let col=0;col<trackEntries.length;col++){
      const nis=costs[row][col];if(!(nis<=gate))continue;
      const [id,tr]=trackEntries[col],i=plotIndices[row];trackBPairs.push({i,id,nis,sanity:trackBGeometryB(tr,plots[i],'AIR'),evidence:trackBEvidenceStableB(tr,plots[i],'AIR',simStepCounter*SIM_FIXED_DT)});
    }
    const trackBSelection=trackBSelectB({plotCount:plots.length,pairs:trackBPairs,legacyPairs,gate,route:'OWN_SPY_GLOBAL',observerShip:ACTIVE_SHIP_RUNTIME.entityId,timeS:simStepCounter*SIM_FIXED_DT,tick:simStepCounter});
    for(const q of trackBSelection.pairs)assigned.set(q.i,{trackId:q.id,nis:q.nis});
    assigned.trackBHeldPlots=trackBSelection.heldPlots;
    return assigned;
  }

  function spyFinalizeAcceptedTrackV31(tr,task){
    const revisit=task.expectedRevisitS??spyDesiredRevisitS(tr,task.type);
    // A coherent associated return contradicts the prior no-return sea-impact inference.
    wip11cClearObservedSeaImpactTrack(tr);
    tr._spyExpectedRevisitS=revisit;tr._spyDwellFailed=false;tr._spyLastTaskType=task.type;tr._spyLastFace=task.face;
    // Association metadata ownership: a coherent anonymous return for a
    // firm neighbouring file must not inherit the scheduled file's reacquire
    // state. Actual RF task/source, EKF correction and existing reacquisition
    // recovery remain unchanged. Frozen B / SHADOW retain their exact path.
    const foreignFirmReturn=TRACK_B_IMPLEMENTATION_MODE==='ACTIVE'&&TRACK_B_STABILIZATION_MODE==='ACTIVE'&&task.trackId!=null&&task.trackId!==tr.trackId&&!tr.reacquiring&&(task.type==='TRACK_REACQUIRE'||task.type==='PRECISION_REACQUIRE');
    if((task.type==='TRACK_REACQUIRE'||task.type==='PRECISION_REACQUIRE')&&!foreignFirmReturn){
      tr._spyReacquireHits=(tr._spyReacquireHits??0)+1;
      tr.reacquiring=tr._spyReacquireHits<2;
      if(tr.reacquiring){
        tr._spyConsecutiveDwellMisses=Math.max(SENSOR_MODEL.spy1dv.reacquireAfterMisses??2,tr._spyConsecutiveDwellMisses??0);
        tr._memReason='REACQUIRE';tr.trackLifecycle='REACQUIRE';
        trackRefreshDerivedQuality(tr);
      } else {
        tr._spyConsecutiveDwellMisses=0;tr._spyLastMissReason=null;tr._spyReacquireHits=0;tr.reacquiring=false;tr._memReason=null;tr.trackLifecycle='FIRM';
        trackRefreshDerivedQuality(tr);
      }
    } else {
      tr._spyConsecutiveDwellMisses=0;tr._spyLastMissReason=null;tr._spyReacquireHits=0;
      tr.reacquiring=false;tr.memActive=false;tr._memReason=null;tr.trackLifecycle=tr.confirmed?'FIRM':'TENTATIVE';
      trackRefreshDerivedQuality(tr);
    }
    if(task.type==='PRECISION_LOCK'||task.type==='PRECISION_REACQUIRE') tr.confirmed=true;
    if(task.type==='SPG_HANDOFF') tr._spyHandoffFreshS=0;
    spyScheduler.measuredThisCycle.add(tr.trackId);
    return tr;
  }

  function spyFinalizeAcceptedSurfaceTrackWip13B9(tr,task,plot){
    // WIP13C6-1: an accepted surface return, including missile-support and
    // precision-lock dwells, owns the common file's observation freshness too.
    tr._spyDwellFailed=false;tr._spyConsecutiveDwellMisses=0;tr._spyLastMissReason=null;tr._spyReacquireHits=0;
    tr.memActive=false;tr.reacquiring=false;tr.memLostOutOfSector=false;tr._memReason=null;
    tr._spySurfaceFreshS=0;tr._spySurfaceMisses=0;tr._spySurfaceReacquiring=false;tr._spySurfaceLastTask=task.type;tr._spySurfaceLastFace=task.face;
    tr._spyExpectedRevisitS=surfaceTrackExpectedRevisitSWip13B9(tr);tr.trackLifecycle=tr.confirmed?'FIRM':'TENTATIVE';tr.ttl=Math.max(tr.ttl??0,SENSOR_MODEL.bridgeMasterE.coastDropS);fuseSurfaceTrackExtentWip13B8(tr,plot);trackRefreshDerivedQuality(tr);spyScheduler.measuredThisCycle.add(tr.trackId);return tr;
  }
  function spyExecuteSurfacePlotsWip13B9(task,collected){
    const plots=collected.plots,focused=task.type.startsWith('SURFACE_')||(task.trackId!=null&&trackSurfaceBackedWip13B14(tracks.get(task.trackId))),usedPlots=new Set(),usedTracks=new Set(),gate=SENSOR_MODEL.spy1dv.surfaceNisGate;let hits=0;
    const accept=(trackId,plot,index,nis=null)=>{const existing=trackId==null?null:tracks.get(trackId),cross=!!existing&&!trackSurfaceBackedWip13B14(existing),tr=updateSensorTrackMeasurement(trackId,plot,{source:plot.source,domainEvidence:plot.domainEvidence,revisitS:spyDesiredRevisitS(existing,task.type),taskType:task.type});if(!tr)return null;if(cross){WIP13B14_CROSS_DOMAIN_ASSOC_STATS.surfacePlotToAirTrack++;WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastTrackId=tr.trackId;WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastRoute='SURFACE';WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastNis=Number.isFinite(nis)?nis:null;}usedPlots.add(index);usedTracks.add(tr.trackId);spyFinalizeAcceptedSurfaceTrackWip13B9(tr,task,plot);hits++;if(trackId==null)spyScheduler.anonymousStats.surfaceNewTracks++;else spyScheduler.anonymousStats.surfaceAssociated++;return tr;};
    if(focused&&task.trackId!=null){
      const scheduled=tracks.get(task.trackId);let best=null;if(scheduled)for(let i=0;i<plots.length;i++){const nis=trackSurfacePositionAssociationNisWip13B9(scheduled,plots[i]);if(nis<=gate&&(!best||nis<best.nis))best={index:i,nis};}
      if(best)accept(task.trackId,plots[best.index],best.index,best.nis);else if(scheduled){scheduled._spySurfaceMisses=(scheduled._spySurfaceMisses??0)+1;scheduled._spySurfaceReacquiring=scheduled._spySurfaceMisses>=(SENSOR_MODEL.spy1dv.reacquireAfterMisses??2);}
    }
    const plotIndices=[];for(let i=0;i<plots.length;i++)if(!usedPlots.has(i))plotIndices.push(i);
    const assignments=surfaceAssignmentsPreferEstablishedWip13B14(plots,trackSurfacePositionAssociationNisWip13B9,gate,usedTracks,plotIndices);
    for(const i of plotIndices){if(assignments.trackBHeldPlots?.has(i)){spyScheduler.anonymousStats.surfaceRejected++;continue;}const match=assignments.get(i),trackId=match?.trackId??null;if(trackId==null&&focused){spyScheduler.anonymousStats.surfaceRejected++;continue;}if(!accept(trackId,plots[i],i,match?.nis??null))spyScheduler.anonymousStats.surfaceRejected++;}
    spyScheduler.anonymousStats.surfacePlots+=plots.length;return {hits,attempted:collected.attempted,acceptedTrackIds:[...usedTracks]};
  }

  function executeSpyTask(task){
    const unified=spyCollectUnifiedEchoPlotsWip13B13(task),surfaceResult=spyExecuteSurfacePlotsWip13B9(task,{plots:unified.surfacePlots,attempted:unified.dwell.candidateCount,clutter:{unified:true}});
    let hits=surfaceResult.hits;const collected={plots:unified.airPlots,attempted:unified.dwell.candidateCount+unified.falseCount},plots=collected.plots,usedPlots=new Set(),usedTracks=new Set(surfaceResult.acceptedTrackIds??[]);
    // WIP13C6-1: one accepted track update per physical dwell across both extractors.
    // A focused dwell first offers every anonymous plot to the scheduled track. The selection
    // is strictly minimum NIS inside the gate; no truth lookup can rescue a failed association.
    if(!task.type.startsWith('SEARCH_')&&!task.type.startsWith('SURFACE_')&&task.trackId!=null&&!trackSurfaceBackedWip13B14(tracks.get(task.trackId))&&!usedTracks.has(task.trackId)){
      const match=spyBestPlotForTrackV31(task.trackId,plots,usedPlots,task),existing=tracks.get(task.trackId);
      if(match){
        const cross=trackSurfaceBackedWip13B14(existing)&&shipboardRadarLowSlowSurfaceEchoWip13B14(plots[match.index]);
        const tr=updateSensorTrackMeasurement(task.trackId,plots[match.index],{source:'SPY1DV_'+task.type,domainEvidence:plots[match.index].domainEvidence,revisitS:task.expectedRevisitS,taskType:task.type,reacquire:(task.type==='TRACK_REACQUIRE'||task.type==='PRECISION_REACQUIRE')});
        if(tr){if(cross){WIP13B14_CROSS_DOMAIN_ASSOC_STATS.airPlotToSurfaceTrack++;WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastTrackId=tr.trackId;WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastRoute='AIR';WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastNis=match.nis;}usedPlots.add(match.index);usedTracks.add(task.trackId);spyFinalizeAcceptedTrackV31(tr,task);spyScheduler.anonymousStats.associatedPlots++;hits++;}
      }
      if(existing&&!usedTracks.has(task.trackId))markSpyDwellMiss(existing,task,plots.length?'NO_ASSOCIATED_PLOT':'NO_PLOT');
    }
    // Associate the complete remainder as one batch.  Greedy plot order and scheduler-cycle-wide
    // duplicate suppression previously collapsed 0.8--3 km formations into one track at long
    // range.  Each track may be used once per dwell; a later physical dwell may update it again.
    const assignments=spyGlobalAssignmentsV36(plots,usedPlots,usedTracks,task);
    for(let i=0;i<plots.length;i++){
      if(usedPlots.has(i))continue;
      if(assignments.trackBHeldPlots?.has(i)){spyScheduler.anonymousStats.rejectedPlots++;continue;}
      const assoc=assignments.get(i),id=assoc?.trackId??null;
      // Focused illumination may update a second file inside the pencil beam, but it is not an
      // initiation search. An unassociated focused return is discarded instead of cloning the
      // scheduled target into a chain of duplicate tentative tracks.
      if(id==null&&!task.type.startsWith('SEARCH_')){spyScheduler.anonymousStats.rejectedPlots++;continue;}
      const existing=id==null?null:tracks.get(id),cross=!!existing&&trackSurfaceBackedWip13B14(existing)&&shipboardRadarLowSlowSurfaceEchoWip13B14(plots[i]);
      const tr=updateSensorTrackMeasurement(id,plots[i],{source:'SPY1DV_'+task.type,domainEvidence:plots[i].domainEvidence,revisitS:task.expectedRevisitS,taskType:task.type});
      if(!tr){spyScheduler.anonymousStats.rejectedPlots++;continue;}
      if(cross){WIP13B14_CROSS_DOMAIN_ASSOC_STATS.airPlotToSurfaceTrack++;WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastTrackId=tr.trackId;WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastRoute='AIR';WIP13B14_CROSS_DOMAIN_ASSOC_STATS.lastNis=assoc?.nis??null;}
      usedPlots.add(i);usedTracks.add(tr.trackId);spyFinalizeAcceptedTrackV31(tr,task);hits++;
      if(id==null)spyScheduler.anonymousStats.newTracks++;else spyScheduler.anonymousStats.associatedPlots++;
    }
    const fs=spyScheduler.faces[task.face];
    if(fs){
      fs.lastDwellAgeS=0;fs.lastTask=task.type;fs.taskCounts[task.type]=(fs.taskCounts[task.type]||0)+1;
      if(task.searchCursor==='horizon'){fs.horizonCursor+=task.cursorAdvance??1;fs.lastHorizonAgeS=0;}
      if(task.searchCursor==='volume'){fs.volumeCursor+=task.cursorAdvance??1;fs.lastVolumeAgeS=0;}
    }
    const attempted=unified.attempted;recordSpyBeam(task,{hits,attempted,ok:hits>0});
    return {hits,attempted,ok:hits>0};
  }

  function recordSpyBeam(task,res){
    const hold=SENSOR_MODEL.spy1dv.schedulerHistoryHoldS;
    const long=task.type==='PRECISION_LOCK'||task.type==='PRECISION_REACQUIRE'||task.type==='SPG_HANDOFF'||task.type==='MISSILE_SUPPORT'||task.type==='HIGH_THREAT';
    const entry={
      type:task.type,code:SPY1DV_TASK_CODE[task.type]??'?',face:task.face,azWorld:task.azWorld,elRad:task.elRad,
      azHalfRad:task.azHalfRad,elHalfRad:task.elHalfRad,rangeWorld:task.rangeWorld,trackId:task.trackId??null,
      priority:task.priority,costMs:task.costMs,ageS:0,holdS:long?hold:hold*0.58,hits:res.hits,attempted:res.attempted,ok:res.ok
    };
    spyScheduler.beamHistory.push(entry);
    if(spyScheduler.beamHistory.length>SENSOR_MODEL.spy1dv.schedulerMaxHistory) spyScheduler.beamHistory.splice(0,spyScheduler.beamHistory.length-SENSOR_MODEL.spy1dv.schedulerMaxHistory);
    spyScheduler.latestTasks.push({...entry});
    if(spyScheduler.latestTasks.length>64) spyScheduler.latestTasks.splice(0,spyScheduler.latestTasks.length-64);
  }

  function ageSpySchedulerVisuals(dt){
    spyScheduler.simTimeS+=dt;
    for(const f of SPY1DV_FACE_KEYS){
      const fs=spyScheduler.faces[f]; if(!fs) continue;
      fs.lastDwellAgeS+=dt;fs.lastHorizonAgeS+=dt;fs.lastVolumeAgeS+=dt;
    }
    for(const b of spyScheduler.beamHistory) b.ageS+=dt;
    spyScheduler.beamHistory=spyScheduler.beamHistory.filter(b=>b.ageS<=(b.holdS??0.5));
    for(const b of spyScheduler.latestTasks) b.ageS=(b.ageS??0)+dt;
    spyScheduler.latestTasks=spyScheduler.latestTasks.filter(b=>(b.ageS??0)<1.25);
  }

  function spyTaskDeadlineRatio(task){
    const age=Number(task?.serviceAgeS), deadline=Number(task?.serviceDeadlineS);
    if(!(age>=0)||!(deadline>0)) return 0;
    return age/deadline;
  }

  function spyTaskIsMustService(task){
    return spyTaskDeadlineRatio(task)>=1.0;
  }

  function spyMustServiceRank(task){
    const ratio=spyTaskDeadlineRatio(task);
    // Search receives a small tie-break advantage once actually overdue; track urgency still grows
    // without bound with deadline ratio, so severely stale tracks naturally rise above search.
    const classBias=task?.type==='SEARCH_HORIZON'?0.20:(task?.type==='SEARCH_VOLUME'?0.08:0);
    return ratio+classBias;
  }

  function runSpySchedulerCycle(){
    spyScheduler.cycleCounter++;
    spyScheduler.measuredThisCycle.clear();
    for(const face of SPY1DV_FACE_KEYS){
      const fs=spyScheduler.faces[face];
      fs.usedMs=0;fs.candidateCount=0;fs.executedCount=0;fs.droppedCount=0;fs.taskCounts={};
    }
    let tasks=buildSpySchedulerTasks();
    spyScheduler.candidates=tasks.length;
    for(const task of tasks){const fs=spyScheduler.faces[task.face];if(fs)fs.candidateCount++;}

    const globalBudget=SENSOR_MODEL.spy1dv.schedulerGlobalBudgetMs*clamp(getShipDamageEffects().cdcFac,0.35,1);
    const maxDwells=SENSOR_MODEL.spy1dv.schedulerMaxDwells;
    const reserveBudget=Math.min(globalBudget,Math.max(0,SENSOR_MODEL.spy1dv.schedulerAntiStarvationReserveMs??0));
    let used=0,executed=0,dropped=0,priorityUsed=0,searchUsed=0,priorityDropped=0;
    let mustUsed=0,mustExecuted=0,mustDeferred=0;
    const executedSeq=new Set();

    const tryExecute=(task,limitMs,markMust=false)=>{
      const fs=spyScheduler.faces[task.face]; if(!fs) return false;
      const faceCap=spyFaceCapacityMs(task.face)*(task.priority>=100?1.30:1.0);
      const fitsGlobal=(used+task.costMs<=globalBudget+1e-9);
      const fitsPass=(used+task.costMs<=limitMs+1e-9);
      const fitsFace=(fs.usedMs+task.costMs<=faceCap+1e-9);
      if(executed>=maxDwells||!fitsGlobal||!fitsPass||!fitsFace) return false;
      executeSpyTask(task);used+=task.costMs;fs.usedMs+=task.costMs;fs.executedCount++;executed++;executedSeq.add(task.seq);
      if(task.type.startsWith('SEARCH_')) searchUsed+=task.costMs; else priorityUsed+=task.costMs;
      if(markMust){mustUsed+=task.costMs;mustExecuted++;}
      return true;
    };

    // Pass 1 — bounded anti-starvation reserve. Only tasks that actually crossed a hard service
    // deadline enter this pass. Unused reserve is immediately returned to the normal greedy pass.
    // This protects minimum situational awareness without pretending the radar gained extra RF time.
    const mustTasks=tasks.filter(spyTaskIsMustService).sort((a,b)=>
      spyMustServiceRank(b)-spyMustServiceRank(a) || b.priority-a.priority || a.seq-b.seq);
    for(const task of mustTasks){
      if(!tryExecute(task,reserveBudget,true)) mustDeferred++;
    }

    // Pass 2 — original priority-greedy policy over the FULL remaining global budget. Deferred
    // deadline tasks stay in the queue and may still run here; they are not silently discarded.
    tasks.sort((a,b)=>b.priority-a.priority||spyTaskDeadlineRatio(b)-spyTaskDeadlineRatio(a)||a.seq-b.seq);
    for(const task of tasks){
      if(executedSeq.has(task.seq)) continue;
      const fs=spyScheduler.faces[task.face]; if(!fs){dropped++;continue;}
      if(!tryExecute(task,globalBudget,false)){
        fs.droppedCount++;dropped++;
        if(!task.type.startsWith('SEARCH_')) priorityDropped++;
      }
    }
    spyScheduler.globalUsedMs=used;spyScheduler.priorityUsedMs=priorityUsed;spyScheduler.searchUsedMs=searchUsed;spyScheduler.priorityDropped=priorityDropped;spyScheduler.executed=executed;spyScheduler.dropped=dropped;
    spyScheduler.mustServiceUsedMs=mustUsed;spyScheduler.mustServiceExecuted=mustExecuted;spyScheduler.mustServiceDeferred=mustDeferred;
    spyScheduler.overdueCandidates=mustTasks.length;
    spyScheduler.globalLoad01=lerp(spyScheduler.globalLoad01,clamp(used/Math.max(0.1,globalBudget),0,1),0.30);
    const pPressure=clamp(priorityUsed/Math.max(0.1,globalBudget*0.60)+priorityDropped*0.14,0,1);
    spyScheduler.priorityLoad01=lerp(spyScheduler.priorityLoad01,pPressure,0.35);
    for(const face of SPY1DV_FACE_KEYS){
      const fs=spyScheduler.faces[face],cap=Math.max(0.1,spyFaceCapacityMs(face));
      fs.load01=lerp(fs.load01,clamp(fs.usedMs/cap,0,1),0.35);
    }
  }

  function updateSpyScheduler(dt){
    ageSpySchedulerVisuals(dt);
    if(emconActive) return;
    spyScheduler.accumulatorS+=dt;
    const cycle=Math.max(0.010,SENSOR_MODEL.spy1dv.schedulerCycleS);
    let guard=0;
    while(spyScheduler.accumulatorS+1e-9>=cycle&&guard++<4){
      spyScheduler.accumulatorS=Math.max(0,spyScheduler.accumulatorS-cycle);
      runSpySchedulerCycle();
    }
  }

  function spySchedulerSnapshot(){
    return {
      cycle:spyScheduler.cycleCounter,load:spyScheduler.globalLoad01,usedMs:spyScheduler.globalUsedMs,
      associationMode:'BATCH_ONE_TO_ONE_V36',
      // Scheduler beam-time occupancy only. This is NOT RF transmitter duty cycle.
      // Actual RF duty factor depends on waveform pulse width, PRF/pulse count,
      // transmitter sharing, etc. and is intentionally not modeled here.
      beamOccupancy01:clamp(spyScheduler.globalUsedMs/Math.max(1,SENSOR_MODEL.spy1dv.schedulerCycleS*1000),0,1),
      priorityLoad:spyScheduler.priorityLoad01,priorityUsedMs:spyScheduler.priorityUsedMs,searchUsedMs:spyScheduler.searchUsedMs,priorityDropped:spyScheduler.priorityDropped,
      candidates:spyScheduler.candidates,executed:spyScheduler.executed,dropped:spyScheduler.dropped,
      mustServiceUsedMs:spyScheduler.mustServiceUsedMs,mustServiceExecuted:spyScheduler.mustServiceExecuted,mustServiceDeferred:spyScheduler.mustServiceDeferred,overdueCandidates:spyScheduler.overdueCandidates,
      anonymousPlots:{...spyScheduler.anonymousStats},forcedFalsePlots:spyScheduler.forcedFalsePlots,
      faces:Object.fromEntries(SPY1DV_FACE_KEYS.map(f=>{const fs=spyScheduler.faces[f];return [f,{alive:spyFaceHealth01(f)>0,health:spyFaceHealth01(f),load:fs.load01,usedMs:fs.usedMs,candidates:fs.candidateCount,executed:fs.executedCount,dropped:fs.droppedCount,lastTask:fs.lastTask,taskCounts:{...fs.taskCounts},hCursor:fs.horizonCursor,vCursor:fs.volumeCursor}]})),
      recent:spyScheduler.latestTasks.slice().sort((a,b)=>(a.ageS??0)-(b.ageS??0)||(b.priority??0)-(a.priority??0)).slice(0,8).map(b=>({type:b.type,face:b.face,trackId:b.trackId,ok:b.ok,hits:b.hits,priority:b.priority,costMs:b.costMs,elDeg:b.elRad*180/Math.PI,ageS:b.ageS}))
    };
  }

  function trackLifecycleState(tr){
    if(!tr)return 'DROP';
    if(tr.memActive)return 'MEMORY';
    if(tr.reacquiring)return 'REACQUIRE';
    if(!tr.confirmed)return 'TENTATIVE';
    const expected=Math.max(0.05,tr._spyExpectedRevisitS??0.30);
    if((tr.sensorAge??0)>expected*1.65)return 'COAST';
    return 'FIRM';
  }

  // ===== WIP11C OBSERVED ASM SEA-IMPACT COAST =====
  // This is an epistemic track-manager rule, not a truth shortcut.  An airborne missile file is
  // retired from the tactical display only after its EKF state reaches the sea with a decisive
  // downward rate and SPY receives no coherent return for a bounded confirmation interval.
  // Any subsequently associated plot cancels the inference and reopens the ordinary track path.
  const WIP11C_OBSERVED_SEA_IMPACT_TRACK_POLICY=Object.freeze({
    maxEstimatedAltitudeM:8,
    minDescentMps:45,
    maxPredictedImpactTimeS:.35,
    minNoPlotAgeS:.25,
    confirmS:.30,
    shipClearanceMarginM:25
  });
  function wip11cClearObservedSeaImpactTrack(tr){
    if(!tr)return false;const was=!!tr._wip11cObservedSeaImpact;
    tr._wip11cSeaImpactCandidateS=0;tr._wip11cObservedSeaImpact=null;
    if(was)wip121RestoreTargetSupportEligibility(tr.trackId);
    return was;
  }
  function wip11cUpdateObservedSeaImpactTrack(tr,dt){
    if(!tr||tr.domain==='SURFACE'||tr.classification==='SURFACE')return false;
    const missileLike=tr.classification==='ASM'||tr.isASM||trackKinematicThreatCue(tr).missileLike;
    if(!missileLike){wip11cClearObservedSeaImpactTrack(tr);return false;}
    trackEkfInit(tr);const x=tr._kfX,P=WIP11C_OBSERVED_SEA_IMPACT_TRACK_POLICY,altM=Number(x?.[2]),vzMps=Number(x?.[5]);
    const descending=Number.isFinite(vzMps)&&vzMps<=-P.minDescentMps;
    const impactTimeS=descending?Math.max(0,altM)/Math.max(P.minDescentMps,-vzMps):Infinity;
    const approachesSea=Number.isFinite(altM)&&impactTimeS<=P.maxPredictedImpactTimeS;
    const impactXM=Number(x?.[0])+Number(x?.[3])*impactTimeS,impactYM=Number(x?.[1])+Number(x?.[4])*impactTimeS;
    const shipXM=worldToMeters(aircraft.x()),shipYM=worldToMeters(aircraft.y()),shipClearanceM=Math.hypot(impactXM-shipXM,impactYM-shipYM);
    // Never retire a steep-diving coast while its predicted water crossing is still inside the ship.
    // If it misses and passes through the envelope, the coast becomes eligible immediately afterward.
    const clearsShip=Number.isFinite(shipClearanceM)&&shipClearanceM>WIP118_SHIP_ENVELOPE_RADIUS_M+P.shipClearanceMarginM;
    const noPlot=!tr.lastUpdateSeen&&(tr.memActive||tr.reacquiring||(tr._spyConsecutiveDwellMisses??0)>=(SENSOR_MODEL.spy1dv.reacquireAfterMisses??2)||(tr.sensorAge??0)>=P.minNoPlotAgeS);
    if(!(descending&&approachesSea&&clearsShip&&noPlot)){tr._wip11cSeaImpactCandidateS=0;return !!tr._wip11cObservedSeaImpact;}
    tr._wip11cSeaImpactCandidateS=(tr._wip11cSeaImpactCandidateS??0)+Math.max(0,Number(dt)||0);
    if(!tr._wip11cObservedSeaImpact&&altM<=P.maxEstimatedAltitudeM&&tr._wip11cSeaImpactCandidateS+1e-9>=P.confirmS){
      tr._wip11cObservedSeaImpact={step:simStepCounter,estimatedAltitudeM:altM,verticalRateMps:vzMps,predictedImpactTimeS:impactTimeS,predictedShipClearanceM:shipClearanceM,noPlotAgeS:tr.sensorAge??0,confirmationS:tr._wip11cSeaImpactCandidateS};
      wip121ReleaseTargetFireControlSupport(tr.trackId,'OBSERVED_SEA_IMPACT');
    }
    return !!tr._wip11cObservedSeaImpact;
  }

  function trackDisplayLabelById(id){
    if(id==null) return 'NO-TRK';
    const tr=tracks.get(id);
    if(!tr) return 'TRK?';
    const cls=tr.classification==='ASM'?'ASM':(tr.classification==='AIR'?'AIR':(tr.classification==='SURFACE'?'SUR':'UNK'));
    return `${cls} T${tr.trackNumber??'?'}`;
  }

  // WIP115 presentation adapter only. The canonical track label function above is intentionally
  // unchanged. If no player-side track exists, show only the caller-provided observed class fallback;
  // never recover a truth model name from enemyMissiles[].label / aircraft.acType.
  function trackDisplayLabelOr(id,fallback='UNK'){
    const shown=trackDisplayLabelById(id);
    return (shown==='TRK?'||shown==='NO-TRK')?fallback:shown;
  }

  function trackIsDisplayable(tr){
    if(!tr||tr.sensorDetected===false)return false;
    // WIP11C BDA presentation: a retired ASM track may remain internally available for
    // anonymous-search reassociation, but it must not coast across the PPI as a live threat
    // after own-force kill confirmation.  Wreckage is a separate world/render collection.
    if(wip121BdaTrackPresentation(tr).hidden)return false;
    const u=trackCovarianceMetrics(tr);
    return (tr.trackQuality??0)>0.05 && u.posSigmaM<TRACK_FILTER_MODEL.maxPosSigmaM;
  }
  function trackIsFireControlQuality(tr){
    if(tr) trackRefreshDerivedQuality(tr);
    if(wip121TargetSupportBlocked(tr?.trackId,tr))return false;
    if(!trackIsDisplayable(tr)||tr.confirmed!==true||tr.memActive||tr.reacquiring)return false;
    const src=tr.sensorSource??'',u=trackCovarianceMetrics(tr);
    const primary=src.startsWith('SPY1DV')||src==='DATALINK'||src==='TEST';
    const spq9b=src.startsWith('SPQ9B');
    if(!primary&&!spq9b)return false;
    if(spq9b){
      // AN/SPQ-9B may support a coarse engagement/cueing track, but only after
      // repeated mechanical sweeps have driven covariance well below ordinary search quality.
      return (tr.fireControlQuality??0)>0.52 && u.posSigmaM<1200 && u.altSigmaM<1400 && u.velSigmaMps<190;
    }
    return (tr.fireControlQuality??0)>0.34 && u.posSigmaM<TRACK_FILTER_MODEL.fcPosSigmaM && u.altSigmaM<TRACK_FILTER_MODEL.fcAltSigmaM && u.velSigmaMps<TRACK_FILTER_MODEL.fcVelSigmaMps;
  }

  function detectedTrackCounts(){
    let air=0, asm=0, surface=0, unk=0;
    for(const [,tr] of tracks){
      if(!trackIsDisplayable(tr)) continue;
      if(tr.classification==='ASM') asm++;
      else if(tr.classification==='AIR') air++;
      else if(tr.classification==='SURFACE') surface++;
      else unk++;
    }
    return { air, asm, surface, unk, total:air+asm+surface+unk };
  }

  function accumulateTrackDomainEvidenceWip13B13(tr,evidence){
    if(!tr||!evidence||typeof evidence!=='object')return null;
    const q=clamp(Number(evidence.quality)||.25,.05,1),gain=tr._domainEvidenceSamplesWip13B13?clamp(.16+.30*q,.16,.46):1,blend=(key,value,fallback=.12)=>{const v=clamp(Number(value)||0,0,1),old=Number.isFinite(tr[key])?tr[key]:fallback;tr[key]=lerp(old,v,gain);return tr[key];};
    const surface=blend('_domainEvidenceSurfaceWip13B13',evidence.surface),air=blend('_domainEvidenceAirWip13B13',evidence.air),missile=blend('_domainEvidenceMissileWip13B13',evidence.missile),background=blend('_domainEvidenceBackgroundWip13B13',evidence.background,0);
    tr._domainEvidenceSamplesWip13B13=(tr._domainEvidenceSamplesWip13B13??0)+1;tr._lastDomainEvidenceWip13B13={surface,air,missile,background,quality:q,candidateDomain:evidence.candidateDomain??'AMBIGUOUS'};
    return tr._lastDomainEvidenceWip13B13;
  }
  function updateTrackClassification(tr,meta={}){
    if(!tr)return;if(tr.classification==null)tr.classification='UNKNOWN';
    const src=tr.sensorSource??'',domainEvidence=accumulateTrackDomainEvidenceWip13B13(tr,meta.domainEvidence);
    if(src==='VISUAL'){
      tr.classification=meta.isASM?'ASM':'AIR';tr.classificationConfidence=0.92;
      tr._classEvidenceAsm=meta.isASM?0.95:0.03;tr._classEvidenceAir=meta.isASM?0.03:0.95;return;
    }
    if(src==='TEST'){
      tr.classification=(meta.isASM||tr.isASM)?'ASM':'AIR';tr.classificationConfidence=1.0;
      tr._classEvidenceAsm=tr.classification==='ASM'?1:0;tr._classEvidenceAir=tr.classification==='AIR'?1:0;return;
    }
    if(domainEvidence){
      const s=domainEvidence.surface,a=domainEvidence.air,m=domainEvidence.missile,b=domainEvidence.background,bestAir=Math.max(a,m),samples=tr._domainEvidenceSamplesWip13B13??0,wasSurface=trackSurfaceBackedWip13B14(tr),wasAir=tr.domain==='AIR'&&(tr.classification==='AIR'||tr.classification==='ASM'),lowSlowSurfaceEcho=shipboardRadarLowSlowSurfaceEchoWip13B14({domainEvidence:meta.domainEvidence});
      if(s>.50&&s>bestAir+.055&&b<s){
        tr._domainSwitchAirStreakWip13B14=0;
        if(wasAir&&tr.confirmed&&(tr.sensorHits??0)>=4){
          tr._domainSwitchSurfaceStreakWip13B14=(tr._domainSwitchSurfaceStreakWip13B14??0)+1;
          if(tr._domainSwitchSurfaceStreakWip13B14<3){tr.classificationConfidence=clamp((tr.classificationConfidence??.55)*.94,.20,.95);return;}
        }
        tr._domainSwitchSurfaceStreakWip13B14=0;
        tr.domain='SURFACE';tr.classification='SURFACE';tr.classificationConfidence=clamp(.38+(s-bestAir)*.78+.055*Math.min(5,tr._domainEvidenceSamplesWip13B13??1),.44,.97);return;
      }
      if(bestAir>.48&&bestAir>s+.035&&b<bestAir){
        tr._domainSwitchSurfaceStreakWip13B14=0;
        if(wasSurface&&samples>=3){
          // A single low-altitude/low-Doppler classifier excursion must not fork an established
          // ship file into a second AIR plot.  A real domain change requires repeated decisive
          // measurement evidence; no truth label or reflector identity participates here.
          if(lowSlowSurfaceEcho){tr._domainSwitchAirStreakWip13B14=0;tr.domain='SURFACE';tr.classification='SURFACE';tr.classificationConfidence=clamp((tr.classificationConfidence??.60)*.97,.38,.97);return;}
          tr._domainSwitchAirStreakWip13B14=(tr._domainSwitchAirStreakWip13B14??0)+1;
          if(tr._domainSwitchAirStreakWip13B14<3){tr.domain='SURFACE';tr.classification='SURFACE';tr.classificationConfidence=clamp((tr.classificationConfidence??.60)*.90,.30,.94);return;}
        }
        tr._domainSwitchAirStreakWip13B14=0;
        tr.domain='AIR';if(tr.classification==='SURFACE')tr.classification='UNKNOWN';
        // A strong compact/high-Doppler RF signature can accelerate, but never replace, the
        // existing kinematic ASM classifier below.
        tr._classEvidenceAsm=lerp(tr._classEvidenceAsm??.15,m,m>.65?.34:.18);tr._classEvidenceAir=lerp(tr._classEvidenceAir??.15,a,.20);
      }else if((tr._domainEvidenceSamplesWip13B13??0)<2){tr.domain='UNKNOWN';tr.classification='UNKNOWN';tr.classificationConfidence=clamp(Math.max(s,bestAir)*.52,.05,.52);}
    }
    if(!tr.confirmed||(tr.sensorHits??0)<2)return;
    const speedMps=Math.hypot(worldSpeedToMps(tr.vx??0),worldSpeedToMps(tr.vy??0),tr.vz??0),altM=tr.z??0,closure=Math.max(0,spyTrackClosureMps(tr));
    let asm=0.05,air=0.05;
    if(speedMps>600)asm+=0.55;else if(speedMps>350)asm+=0.20;
    if(altM<100&&speedMps>180)asm+=0.46;else if(altM<500&&speedMps>180)asm+=0.30;
    if(closure>150)asm+=0.15;if(closure>450)asm+=0.10;
    if(speedMps>=80&&speedMps<=430)air+=0.28;
    if(altM>500)air+=0.24;if(altM>3000)air+=0.10;
    if((tr.sensorHits??0)>=4)air+=0.10;
    if(domainEvidence){asm+=.32*domainEvidence.missile;air+=.20*domainEvidence.air;}
    const q=clamp(tr.kinematicQuality??tr.trackQuality??0.5,0.1,1),gain=clamp(0.14+0.20*q,0.14,0.34);
    tr._classEvidenceAsm=lerp(tr._classEvidenceAsm??0.15,clamp(asm,0,1),gain);
    tr._classEvidenceAir=lerp(tr._classEvidenceAir??0.15,clamp(air,0,1),gain);
    const a=tr._classEvidenceAsm,b=tr._classEvidenceAir;
    if(a>0.58&&a>b+0.10){tr.classification='ASM';tr.classificationConfidence=clamp((a-b)*1.7+0.45,0,0.98);}
    else if(b>0.52&&b>a+0.08){tr.classification='AIR';tr.classificationConfidence=clamp((b-a)*1.6+0.40,0,0.96);}
    else {tr.classification='UNKNOWN';tr.classificationConfidence=clamp(Math.max(a,b)*0.75,0.05,0.70);}
  }

  function _sensorMeasurementFromTruth(obj, opts={}){
    const ax = aircraft.x(), ay = aircraft.y();
    const dxM = worldToMeters(obj.x - ax);
    const dyM = worldToMeters(obj.y - ay);
    const dzM = (obj.z ?? 0) - OWN_ALT_M;
    const trueRangeM = Math.max(1, Math.hypot(dxM,dyM,dzM));
    const trueAz = Math.atan2(dyM, dxM);
    const trueEl = Math.atan2(dzM, Math.max(1, Math.hypot(dxM,dyM)));
    const q = clamp(opts.quality ?? 0.5, 0.05, 1);
    const qScale = 1 / Math.sqrt(q);
    const rangeSigmaM = Math.max(1, (opts.rangeSigmaM ?? 40) * qScale);
    const azSigma = deg((opts.azSigmaDeg ?? 0.08) * qScale);
    const elSigma = deg((opts.elSigmaDeg ?? 0.10) * qScale);
    const rM = Math.max(1, trueRangeM + randn()*rangeSigmaM);
    const az = trueAz + randn()*azSigma;
    const el = trueEl + randn()*elSigma;
    const hM = rM * Math.cos(el);
    const mx = ax + metersToWorld(hM * Math.cos(az));
    const my = ay + metersToWorld(hM * Math.sin(az));
    // Keep the raw elevation solution signed. Near the radar horizon an unbiased noisy
    // measurement can fall slightly below sea level; clipping every sample to 0 m creates a
    // positive/negative derivative bias in the track filter. The TRACK state itself is clamped.
    const mz = OWN_ALT_M + rM * Math.sin(el);

    const losUx = dxM/trueRangeM, losUy = dyM/trueRangeM, losUz = dzM/trueRangeM;
    const objVx = worldSpeedToMps(obj.vx ?? 0), objVy = worldSpeedToMps(obj.vy ?? 0), objVz = obj.vz ?? 0;
    const ownVx = worldSpeedToMps(aircraft._vx ?? 0), ownVy = worldSpeedToMps(aircraft._vy ?? 0);
    const radialTrue = (objVx-ownVx)*losUx + (objVy-ownVy)*losUy + objVz*losUz;
    const radialMps = radialTrue + randn() * (opts.radialVelSigmaMps ?? 6) * qScale;
    return { x:mx, y:my, z:mz, rangeM:rM, azRad:az, elRad:el, radialMps, radialVelSigmaMps:(opts.radialVelSigmaMps ?? 6)*qScale, losUx, losUy, losUz, quality:q, rangeSigmaM, azSigmaDeg:azSigma*180/Math.PI, elSigmaDeg:elSigma*180/Math.PI, source:opts.source ?? 'SENSOR' };
  }

  function _opticalMeasurementFromTruth(obj, quality=0.5){
    const ax=aircraft.x(), ay=aircraft.y();
    const dKm=Math.max(0.05, worldToKm(dist(ax,ay,obj.x,obj.y))),horizontalM=dKm*1000;
    const trueBrg=Math.atan2(obj.y-ay,obj.x-ax),trueEl=Math.atan2((obj.z??0)-OWN_ALT_M,Math.max(1,horizontalM));
    const qScale=1/Math.sqrt(Math.max(0.1,quality));
    const azSigmaDeg=SENSOR_MODEL.visual.bearingSigmaDeg*qScale,elSigmaDeg=SENSOR_MODEL.visual.elevationSigmaDeg*qScale;
    const brg=trueBrg + randn()*deg(azSigmaDeg),el=trueEl+randn()*deg(elSigmaDeg);
    const rangeKm=Math.max(0.02, dKm * (1 + randn()*SENSOR_MODEL.visual.rangeFracSigma));
    const rangeM=rangeKm*1000,rangeSigmaM=rangeM*SENSOR_MODEL.visual.rangeFracSigma;
    const hM=rangeM*Math.cos(el),ur=[Math.cos(el)*Math.cos(brg),Math.cos(el)*Math.sin(brg),Math.sin(el)],uaz=[-Math.sin(brg),Math.cos(brg),0],uel=[-Math.sin(el)*Math.cos(brg),-Math.sin(el)*Math.sin(brg),Math.cos(el)];
    const sig=[Math.max(25,rangeSigmaM),Math.max(25,rangeM*deg(azSigmaDeg)),Math.max(30,rangeM*deg(elSigmaDeg))],basis=[ur,uaz,uel],R=new Array(9).fill(0);
    for(let k=0;k<3;k++)for(let r=0;r<3;r++)for(let c=0;c<3;c++)R[_mIdx(r,c,3)]+=basis[k][r]*basis[k][c]*sig[k]*sig[k];
    return {
      x:ax+metersToWorld(hM*Math.cos(brg)), y:ay+metersToWorld(hM*Math.sin(brg)), z:OWN_ALT_M+rangeM*Math.sin(el),
      rangeM,azRad:brg,elRad:el,radialMps:0,radialVelSigmaMps:SENSOR_MODEL.visual.radialVelSigmaMps,
      losUx:ur[0],losUy:ur[1],losUz:ur[2],quality:clamp(quality,0.1,0.8),rangeSigmaM,
      altitudeSigmaM:sig[2],azSigmaDeg,elevationSigmaDeg:elSigmaDeg,elSigmaDeg,cartesianCovarianceM2:R,source:'VISUAL'
    };
  }

  // WIP33: visual detections are anonymous measurement plots. Truth objects are consumed only
  // above while synthesizing optics; association below sees covariance and measured class only.
  const VISUAL_ASSOC_STATS_V33={plots:0,associated:0,newTracks:0,rejected:0,lastNis:null,lastTrackId:null};
  function visualTrackAssociationV33(meas,meta={}){
    let best=null;
    for(const [id,tr] of tracks){
      if(!tr||tr.truthEnded||tr.domain==='SURFACE'||tr.classification==='SURFACE')continue;
      const conf=clamp(Number(tr.classificationConfidence)||0,0,1);
      if(meta.isASM===true&&tr.classification==='AIR'&&conf>0.85)continue;
      if(meta.isASM!==true&&tr.classification==='ASM'&&conf>0.85)continue;
      const nis=trackCartesianAssociationNisV33(tr,meas);
      if(nis<=SENSOR_MODEL.visual.associationNisGate&&(!best||nis<best.nis))best={trackId:id,nis};
    }
    return best;
  }
  function acceptVisualAnonymousPlotV33(meas,meta={}){
    VISUAL_ASSOC_STATS_V33.plots++;
    const match=visualTrackAssociationV33(meas,meta),tr=updateSensorTrackMeasurement(match?.trackId??null,meas,{source:'VISUAL',revisitS:SENSOR_MODEL.visual.revisitS,isASM:meta.isASM===true});
    if(!tr){VISUAL_ASSOC_STATS_V33.rejected++;return null;}
    if(match)VISUAL_ASSOC_STATS_V33.associated++;else VISUAL_ASSOC_STATS_V33.newTracks++;
    VISUAL_ASSOC_STATS_V33.lastNis=match?.nis??null;VISUAL_ASSOC_STATS_V33.lastTrackId=tr.trackId;return {tr,match};
  }

  function surfaceSensorFamilyWip13B9(source=''){
    if(String(source).startsWith('SPY1DV_SURFACE'))return 'SPY1DV';
    if(String(source).startsWith('SPQ9B_SURFACE'))return 'SPQ9B';
    if(String(source).startsWith('BRIDGEMASTER_E'))return 'BRIDGEMASTER_E';
    return null;
  }
  function recordSurfaceSensorContributorWip13B9(tr,source,meas){
    const family=surfaceSensorFamilyWip13B9(source);if(!tr||!family)return null;
    const all=tr._surfaceSensorContributorsWip13B9||(tr._surfaceSensorContributorsWip13B9={});
    const prev=all[family]||{updates:0};
    all[family]={source:String(source),lastStep:simStepCounter,updates:prev.updates+1,
      rangeSigmaM:Number(meas?.rangeSigmaM)||null,azSigmaDeg:Number(meas?.azSigmaDeg)||null,
      radialVelSigmaMps:Number.isFinite(meas?.radialVelSigmaMps)?Number(meas.radialVelSigmaMps):null};
    return all[family];
  }
  function surfaceSensorContributorSnapshotWip13B9(tr){
    const out={},fixedDtS=1/60;
    for(const [family,row] of Object.entries(tr?._surfaceSensorContributorsWip13B9||{}))out[family]={...row,ageS:Math.max(0,(simStepCounter-row.lastStep)*fixedDtS)};
    return out;
  }
// FRIENDLY_CONTACT_A: measurement capability, never entity/owner/class truth.
// The existing track hard lifetime bounds retained 3-D observation evidence.
