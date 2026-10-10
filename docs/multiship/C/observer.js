// LIVE_CANONICAL: explicit observer state; never swap ACTIVE_SHIP_* or legacy aliases.
// Player keeps the mature legacy scheduler/TrackStore. Foreign ships use the same
// RF extractor and EKF primitives with explicit receiver origins and owned buffers.
const OBSERVER_POLICY_C=Object.freeze({schema:'AEGIS_SHIP_OBSERVER_C_1',maxTracks:256,maxPlots:96,history:64,coastS:4,dropS:18,confirmationSpacingS:.15,externalMaxAgeS:15});
function observerRandomC(q){let x=q.state>>>0;x^=x<<13;x^=x>>>17;x^=x<<5;q.state=x>>>0;return (q.state+.5)/4294967296;}
function observerNormalC(q){if(q.spare!=null){const n=q.spare;q.spare=null;return n;}const u=Math.max(1e-12,observerRandomC(q)),v=observerRandomC(q),a=Math.sqrt(-2*Math.log(u));q.spare=a*Math.sin(TAU*v);return a*Math.cos(TAU*v);}
function prepareObserverC(r){
  const p=resolveShipProfile(r.profileId),own=r===ACTIVE_SHIP_RUNTIME,registration=p.id==='CG_52_LATE_TICONDEROGA'?BUNKER_REGISTRATION:window.BurkeC5Registration;
  const normals=Object.entries(registration.spy).map(([id,q])=>({id,center:{x:q.center[0],y:q.center[1],z:q.center[2]},bearingRad:Math.atan2(q.normal[1],q.normal[0]),
    moduleName:(own?WIP199_SPY_LAYOUT[id]?.moduleName:null)??(p.id==='CG_52_LATE_TICONDEROGA'?{'F1':'AN/SPY-1A(전방)','F2':'AN/SPY-1A(우현)','F3':'AN/SPY-1A(후방)','F4':'AN/SPY-1A(좌현)'}[id]:{'F1':'AN/SPY-1D(V)(전좌)','F2':'AN/SPY-1D(V)(전우)','F3':'AN/SPY-1D(V)(후우)','F4':'AN/SPY-1D(V)(후좌)'}[id]),hCursor:0,vCursor:0,hAge:0,vAge:0,usedMs:0}));
  const ordered=normals.slice().sort((a,b)=>a.bearingRad-b.bearingRad);
  ordered.forEach((q,i)=>{q.lower=-spyPositiveArcRadV32(ordered[(i+3)%4].bearingRad,q.bearingRad)*.5;q.upper=spyPositiveArcRadV32(q.bearingRad,ordered[(i+1)%4].bearingRad)*.5;});
  const o={schema:OBSERVER_POLICY_C.schema,ownerEntityId:r.entityId,profile:p,model:resolveSensorSuite(p.sensors.modelId),normals,
    tracks:own?tracks:r.combatSystem.trackManager.tracks,rng:Object.fromEntries(['SPY','SPQ','NAV'].map(k=>[k,{state:rfSeedWip13A2('OBSERVER_C:'+BATTLESPACE_SEED+':'+r.entityId+':'+k),spare:null}])),
    enabled:{SPY:true,SPQ:true,NAV:true},emcon:false,rotors:{SPQ:0,NAV:0},accumulator:0,cycles:0,serial:1,tickCount:0,lastTick:-1,
    history:[],stats:{plots:0,associated:0,initiated:0,rejected:0,background:0,dropped:0,executed:0,usedMs:0},offboard:{sources:new Map(),queue:[],accepted:0,rejected:0}};
  r.combatSystem.observerC=o;
  claimShipMutableRootA(r,'observerC',o);
  if(!own){r.combatSystem.sensors.execution='OBSERVER_ACTIVE_C';r.combatSystem.trackManager.execution='OBSERVER_ACTIVE_C';}
  return o;
}
function observerC(r){return r.combatSystem.observerC??prepareObserverC(r);}
function resetObserversC(){
  if(!ACTIVE_SHIP_RUNTIME.combatSystem.trackManager)return;
  prepareObserverC(ACTIVE_SHIP_RUNTIME);
  for(const r of physicalShipsB()){r.combatSystem.trackManager.tracks.clear();prepareObserverC(r);}
}
function retireObserverC(r){const o=r.combatSystem.observerC;if(o){if(r!==ACTIVE_SHIP_RUNTIME)o.tracks.clear();o.offboard.queue.length=0;o.offboard.sources.clear();o.history.length=0;}r.combatSystem.observerC=null;}
function observerClassifyC(tr,meas){
  const e=meas.domainEvidence??{},prev=tr.domainEvidenceC??{surface:0,air:0,missile:0,weight:0},w=clamp(meas.quality??.5,.05,1),a=.35;
  tr.domainEvidenceC={surface:lerp(prev.surface,e.surface??0,a),air:lerp(prev.air,e.air??0,a),missile:lerp(prev.missile,e.missile??0,a),weight:prev.weight+w};
  const q=tr.domainEvidenceC,speed=Math.hypot(tr._kfX[3],tr._kfX[4]);
  tr.domain=q.surface>q.air&&q.surface>q.missile*.8?'SURFACE':'AIR';
  tr.classification=tr.domain==='SURFACE'?'SURFACE':(q.missile>.22&&speed>170?'ASM':'AIR');
  // Observed category never grants hostile identity or release authority.
  tr.identity=tr._operatorIdentity??'UNKNOWN';tr.threatStatus=tr.sensorAge>OBSERVER_POLICY_C.coastS?'LOST':'MONITOR';tr.engagementAuthority='WITHHELD';
}
function observerNewTrackC(o,meas,surface){
  const id=o.serial++,tr={trackId:id,trackUid:'OBS-'+id,trackNumber:id,x:meas.x,y:meas.y,z:meas.z,
    vx:mpsToWorldSpeed((meas.sensorVxMps??0)+(meas.radialMps??0)*(meas.losUx??0)),vy:mpsToWorldSpeed((meas.sensorVyMps??0)+(meas.radialMps??0)*(meas.losUy??0)),vz:(meas.radialMps??0)*(meas.losUz??0),
    domain:surface?'SURFACE':'AIR',classification:surface?'SURFACE':'AIR',identity:'UNKNOWN',threatStatus:'UNASSESSED',engagementAuthority:'WITHHELD',sensorAge:0,sensorHits:0,confirmed:false,sensorDetected:true,memActive:false,ttl:OBSERVER_POLICY_C.dropS,lastIndependentHitS:-Infinity};
  trackEkfInit(tr,meas);
  if(surface){tr._kfP[21]=tr._kfP[28]=o.model.bridgeMasterE.surfaceVelSigmaInitMps**2;trackApplySurfaceDomainConstraint(tr,8);}
  return tr;
}
function observerAcceptPlotsC(r,plots,{initiate=true,initiationLimit=OBSERVER_POLICY_C.maxTracks,initiationFamily=null}={}){
  const o=observerC(r),now=simStepCounter*SIM_FIXED_DT,usedTracks=new Set(),usedPlots=new Set(),pairs=[];
  o.stats.plots+=plots.length;plots=plots.slice(0,OBSERVER_POLICY_C.maxPlots);
  const surface=m=>!!m.surfaceReferenceZM;
  // Association knows only covariance, measured geometry, and domain evidence.
  for(let i=0;i<plots.length;i++)for(const [id,tr] of o.tracks){
    if(surface(plots[i])!==(tr.domain==='SURFACE'))continue;
    const nis=surface(plots[i])?trackSurfacePositionAssociationNisWip13B9(tr,plots[i]):trackRadarAssociationNisV31(tr,plots[i]);
    if(nis<=64)pairs.push({i,id,nis});
  }
  pairs.sort((a,b)=>a.nis-b.nis||a.i-b.i||a.id-b.id);
  const apply=(id,meas,created)=>{
    const tr=created?observerNewTrackC(o,meas,surface(meas)):o.tracks.get(id);
    const ok=created||(surface(meas)?trackEkfUpdateSurfaceRadar2D(tr,meas,{nisGate:64}):trackEkfUpdateRadar(tr,meas,{nisGate:64}));if(!ok){o.stats.rejected++;return null;}
    if(created)o.tracks.set(tr.trackId,tr);
    if(now-tr.lastIndependentHitS>=OBSERVER_POLICY_C.confirmationSpacingS){tr.sensorHits++;tr.lastIndependentHitS=now;}
    tr.confirmed=tr.confirmed||tr.sensorHits>=3;tr.sensorAge=0;tr.memActive=false;tr.trackLifecycle=tr.confirmed?'FIRM':'TENTATIVE';tr.sensorSource=meas.source;tr.sensorDetected=true;tr.ttl=OBSERVER_POLICY_C.dropS;
    tr._lastMeasurementStep=simStepCounter;tr.lastMeasurementS=now;tr._lastDetQuality=meas.quality;tr._spyExpectedRevisitS=surface(meas)?o.model.spy1dv.surfaceTrackRevisitS:o.model.spy1dv.trackRevisitAircraftS;
    observerClassifyC(tr,meas);trackRefreshDerivedQuality(tr);if(surface(meas))fuseSurfaceTrackExtentWip13B8(tr,meas);
    tr.contributorsC??={};tr.contributorsC[meas.source]={measuredAtS:now,quality:meas.quality};
    if(created)o.stats.initiated++;else o.stats.associated++;return tr;
  };
  for(const q of pairs){if(usedTracks.has(q.id)||usedPlots.has(q.i))continue;if(apply(q.id,plots[q.i],false)){usedTracks.add(q.id);usedPlots.add(q.i);}}
  for(let i=0;i<plots.length;i++)if(!usedPlots.has(i)){const familyCount=initiationFamily?[...o.tracks.values()].filter(q=>Object.keys(q.contributorsC??{}).some(k=>k.startsWith(initiationFamily))).length:o.tracks.size;
    if(initiate&&o.tracks.size<OBSERVER_POLICY_C.maxTracks&&familyCount<initiationLimit)apply(null,plots[i],true);else o.stats.rejected++;}
}
function observerExtractC(r,opts,{surfaceOnly=false,elevationObservable=true,source,center,exclude=null}={}){
  const o=observerC(r),dwell=shipboardRadarEchoFieldWip13B13({...opts,observerShipId:r.entityId}),plots=[];
  for(const echo of dwell.echoes){
    if(center&&observerMaskC(r,center,echo.azRad,elevationObservable?echo.elRad:0,exclude))continue;
    const evidence=shipboardRadarDomainEvidenceWip13B13(echo,{elevationObservable,surfaceBiased:surfaceOnly});
    if(evidence.candidateDomain==='BACKGROUND'){o.stats.background++;continue;}
    let plot;
    if(shipboardRadarSurfaceDiscreteEvidenceWip13B13(evidence))plot=shipboardRadarEchoToSurfacePlotWip13B13(echo,evidence,source+'_SURFACE',8);
    else if(!surfaceOnly&&evidence.candidateDomain==='AIR')plot={...shipboardRadarEchoToAirPlotWip13B13(echo,evidence,source+'_AIR'),sensorXWorld:opts.receiver.x,sensorYWorld:opts.receiver.y,sensorZM:opts.receiver.z,sensorVxMps:opts.receiver.vxMps,sensorVyMps:opts.receiver.vyMps,sensorVzMps:0};
    else {o.stats.rejected++;continue;}
    plots.push(plot);
  }
  o.history.push({timeS:simStepCounter*SIM_FIXED_DT,source,plots:plots.length,scene:dwell.sceneCount,candidates:dwell.candidateCount,background:dwell.distributedCandidateCount});
  if(o.history.length>OBSERVER_POLICY_C.history)o.history.shift();return plots;
}
function observerSearchTaskC(r,q,horizon){
  const o=observerC(r),m=o.model.spy1dv,width=q.upper-q.lower,step=deg(horizon?m.horizonAzStepDeg:m.searchAzStepDeg),count=Math.ceil(width/step),bars=m.searchBars,cursor=horizon?q.hCursor:q.vCursor,
    index=cursor%count,bar=bars[Math.floor(cursor/count)%bars.length],rel=q.lower+(index+.5)*width/count;
  return {face:q,type:horizon?'SEARCH_HORIZON':'SEARCH_VOLUME',search:true,horizon,az:angNorm(r.navigation.heading+q.bearingRad+rel),el:deg(horizon?m.horizonElDeg:bar.elDeg),halfAz:width/count*.5,halfEl:deg(horizon?m.horizonElHalfDeg:bar.halfDeg),rangeM:o.profile.sensors.spy1dv.searchMaxRangeKm*1000,priority:horizon?44:31,cost:m.taskCostMs[horizon?'SEARCH_HORIZON':'SEARCH_VOLUME']};
}
function observerSpyCycleC(r){
  const o=observerC(r),m=o.model.spy1dv,tasks=[];o.cycles++;o.stats.usedMs=0;o.normals.forEach(q=>q.usedMs=0);
  for(const q of o.normals){q.hAge+=m.schedulerCycleS;q.vAge+=m.schedulerCycleS;
    const horizon=q.hAge/(m.searchHorizonHardDeadlineS??.125)>=q.vAge/(m.searchVolumeHardDeadlineS??.3);tasks.push(observerSearchTaskC(r,q,horizon));}
  for(const [id,tr]of o.tracks){
    if(tr.sensorAge<(tr.domain==='SURFACE'?m.surfaceTrackRevisitS:m.trackRevisitAircraftS)&&tr.confirmed)continue;
    const dx=worldToMeters(tr.x-r.navigation.positionWorld.x),dy=worldToMeters(tr.y-r.navigation.positionWorld.y),az=Math.atan2(dy,dx),rangeM=Math.hypot(dx,dy),q=o.normals.slice().sort((a,b)=>Math.abs(angNorm(az-r.navigation.heading-a.bearingRad))-Math.abs(angNorm(az-r.navigation.heading-b.bearingRad)))[0];
    const u=trackCovarianceMetrics(tr),reacquire=tr.sensorAge>OBSERVER_POLICY_C.coastS,type=reacquire?'TRACK_REACQUIRE':tr.confirmed?'TRACK_REVISIT':'TRACK_CONFIRM';
    tasks.push({face:q,type,trackId:id,search:false,az,el:Math.atan2((tr.z??8)-q.center.z,Math.max(1,rangeM)),halfAz:deg(Math.min(reacquire?8.5:3.2,Math.max(m.taskBeamAzHalfDeg[type],rad2deg(Math.atan2(u.posSigmaM*2.35,rangeM))))),halfEl:deg(m.taskBeamElHalfDeg[type]),rangeM:Math.min(o.profile.sensors.spy1dv.searchMaxRangeKm*1000,rangeM+u.posSigmaM*3+100),priority:64+Math.min(45,tr.sensorAge*30),cost:m.taskCostMs[type]});
  }
  // Deadline reserve prevents revisit load from erasing the independent search raster.
  const overdue=t=>t.search?(t.horizon?t.face.hAge/(m.searchHorizonHardDeadlineS??.125):t.face.vAge/(m.searchVolumeHardDeadlineS??.3)):0;
  tasks.sort((a,b)=>(overdue(b)>=1?1:0)-(overdue(a)>=1?1:0)||b.priority-a.priority||overdue(b)-overdue(a));
  let dwells=0;for(const t of tasks){
    const health=observerHealthC(r,t.face.moduleName),capacity=m.schedulerFaceBudgetMs*health,relative=angNorm(t.az-r.navigation.heading-t.face.bearingRad),limit=Math.max(deg(45+m.faceOverlapDeg),Math.abs(t.face.lower),Math.abs(t.face.upper));
    if(!o.enabled.SPY||o.emcon||health<=.05||Math.abs(relative)>limit||dwells>=m.schedulerMaxDwells||o.stats.usedMs+t.cost>m.schedulerGlobalBudgetMs||t.face.usedMs+t.cost>capacity){o.stats.dropped++;continue;}
    const receiver=observerMountC(r,t.face.center),focused=!t.search,snrBoost=m.taskSnrBoost[t.type]??1,steer=Math.pow(Math.max(.02,Math.cos(relative)),1.7);
    if(observerMaskC(r,t.face.center,t.az,t.el))continue;
    const plots=observerExtractC(r,{radarId:'SPY1DV',band:'S',receiver,beamAz:t.az,beamEl:t.el,beamHalfAzRad:t.halfAz,beamHalfElRad:t.halfEl,maxRangeKm:t.rangeM/1000,minRangeM:120,focusRangeM:focused?t.rangeM:null,rangeResolutionM:Math.max(20,m.rangeSigmaSearchM*1.8),seaAzimuthCells:3,seaRangeCells:6,maxDistributedEchoes:0,health:health*steer,snrReferenceRangeKm:o.profile.sensors.spy1dv.snrReferenceRangeKm*Math.pow(snrBoost,.25),snrReferenceRcsM2:1,clutterLeak01:.00012,receiverNoiseNorm:.035,pdHalfSnr:1,rangeSigmaM:focused?m.rangeSigmaTrackM:m.rangeSigmaSearchM,azSigmaDeg:focused?m.azSigmaTrackDeg:m.azSigmaSearchDeg,elSigmaDeg:focused?m.elSigmaTrackDeg:m.elSigmaSearchDeg,dopplerSigmaMps:focused?m.radialVelSigmaTrackMps:m.radialVelSigmaSearchMps,rngState:o.rng.SPY}, {source:'SPY1DV_'+t.type,center:t.face.center});
    observerAcceptPlotsC(r,plots,{initiate:t.search});t.face.usedMs+=t.cost;o.stats.usedMs+=t.cost;o.stats.executed++;dwells++;
    if(t.search){if(t.horizon){t.face.hCursor++;t.face.hAge=0;}else{t.face.vCursor++;t.face.vAge=0;}}
  }
}
function observerAuxStepC(r,dt,key){
  const o=observerC(r),p=o.profile,m=o.model,spq=key==='SPQ',cg=p.id==='CG_52_LATE_TICONDEROGA',spec=spq?p.sensors.spq9b:p.sensors.bridgeMasterE,hp=p.geometry.hardpoints[spq?'spq9b':'bridgeMasterE'],health=observerHealthC(r,hp.name)*(shipSystemDamageB(r,'MAST')>=80?0:1);
  if(!o.enabled[key]||o.emcon||health<=.08)return;
  const old=o.rotors[key],advance=(spq?spec.rpm:spec.nominalRpm)/60*TAU*dt;o.rotors[key]=angNorm(old+advance);
  const panels=spq?(spec.panelOffsetsRad??[0,Math.PI]):[0],receiver=observerMountC(r,hp),maxRange=spq?spec.searchMaxRangeKm:spec.trackMaxNmi*1.852;
  for(const offset of panels){const az=angNorm(r.navigation.heading+old+offset+advance*.5),halfAz=advance*.5+deg(spq?.6:spec.horizontalBeamwidthDeg*.5),elevationObservable=spq&&!cg,el=spq&&!cg?deg(-.6):0,halfEl=deg(spq?(cg?10:1.45):spec.verticalBeamwidthDeg*.5),exclude=spq&&cg?'ANTENNA:SPQ9':null;
    if(observerMaskC(r,hp,az,el,exclude))continue;
    let plots=observerExtractC(r,{radarId:spq?'SPQ9B':'BRIDGEMASTER_E',band:spq?'X':spec.band,receiver,beamAz:az,beamEl:el,beamHalfAzRad:halfAz,beamHalfElRad:halfEl,maxRangeKm:maxRange,minRangeM:spq?(spec.minimumRangeM??250):spec.trackMinNmi*1852,rangeResolutionM:spq?25:spec.workingRangeResolutionM,seaAzimuthCells:3,seaRangeCells:6,maxDistributedEchoes:0,health,snrReferenceRangeKm:spq?spec.snrReferenceRangeKm:m.bridgeMasterE.snrRefRangeKm,snrReferenceRcsM2:spq?1:m.bridgeMasterE.snrRefRcsM2,clutterLeak01:spq?(cg?.00025:.00001):.00012,receiverNoiseNorm:.035,pdHalfSnr:1,rangeSigmaM:spq?(cg?13:10):m.bridgeMasterE.rangeSigmaFloorM,azSigmaDeg:spq?(cg?.085:.045):m.bridgeMasterE.azSigmaFloorDeg,elSigmaDeg:elevationObservable?.18:10,dopplerSigmaMps:spq?(cg?3:1.5):6,rngState:o.rng[key]}, {source:spq?'SPQ9B':'BRIDGEMASTER_E',surfaceOnly:!elevationObservable,elevationObservable,center:hp,exclude});
    if(!spq)plots=plots.filter(q=>Math.abs(q.radialMps??0)<=spec.maxTrackRelativeSpeedKt*.514444+2*(q.radialVelSigmaMps??6)).map(q=>{const out={...q};delete out.radialMps;delete out.radialVelSigmaMps;return out;});
    if(spq&&!cg)plots=plots.filter(q=>{const elq=Math.atan2((q.z??8)-receiver.z,Math.max(1,q.rangeM)),h=Math.exp(-2.7726*(elq/deg(.5))**2),down=Math.exp(-2.7726*((elq-deg(-1.2))/deg(.5))**2);return observerRandomC(o.rng.SPQ)<Math.max(h,down);});
    observerAcceptPlotsC(r,plots,spq?{}:{initiationLimit:spec.maxRadarTracks,initiationFamily:'BRIDGEMASTER_E'});
  }
}
function stepObserversC(dt){
  const own=observerC(ACTIVE_SHIP_RUNTIME);drainOffboardC(ACTIVE_SHIP_RUNTIME);own.tickCount++;own.lastTick=simStepCounter;
  for(const r of physicalShipsB()){
    const o=observerC(r);if(o.lastTick===simStepCounter)throw Error('OBSERVER_DOUBLE_TICK');o.lastTick=simStepCounter;o.tickCount++;
    for(const [id,tr]of o.tracks){tr.sensorAge+=dt;tr.ttl-=dt;tr.memActive=tr.sensorAge>OBSERVER_POLICY_C.coastS;tr.trackLifecycle=tr.memActive?'MEMORY':tr.sensorAge>.65?'COAST':tr.confirmed?'FIRM':'TENTATIVE';trackEkfPredict(tr,dt,{memory:tr.memActive});if(tr.ttl<=0||trackCovarianceMetrics(tr).posSigmaM>TRACK_FILTER_MODEL.dropPosSigmaM)o.tracks.delete(id);}
    o.accumulator+=dt;while(o.accumulator+1e-9>=o.model.spy1dv.schedulerCycleS){o.accumulator-=o.model.spy1dv.schedulerCycleS;observerSpyCycleC(r);}
    observerAuxStepC(r,dt,'SPQ');observerAuxStepC(r,dt,'NAV');drainOffboardC(r);
  }
}
function observerTrackViewC(tr,r){return {trackId:tr.trackId,trackNumber:tr.trackNumber,positionM:{x:worldToMeters(tr.x),y:worldToMeters(tr.y),z:tr.z},velocityMps:{x:worldSpeedToMps(tr.vx),y:worldSpeedToMps(tr.vy),z:tr.vz},covariance:Array.from(tr._kfP??[]),classification:tr.classification,identity:tr.identity,threatStatus:tr.threatStatus,engagementAuthority:tr.engagementAuthority,confirmed:!!tr.confirmed,sensorAgeS:tr.sensorAge,source:tr.sensorSource,lifecycle:tr.trackLifecycle,contributors:jsonSafeCloneV48Wip11A(tr.contributorsC??{}),offboard:observationReportViewC(tr,r)};}
function observerFacadeC(r){if(!r)return null;const o=observerC(r);return Object.freeze({ownerEntityId:r.entityId,profileId:r.profileId,timeS:simStepCounter*SIM_FIXED_DT,tracks:Object.freeze([...o.tracks.values()].filter(tr=>tr.sensorDetected).map(tr=>Object.freeze(observerTrackViewC(tr,r)))),offboard:offboardSnapshotC(r)});}
function observerSnapshotC(){return {schema:OBSERVER_POLICY_C.schema,worldTimeS:simStepCounter*SIM_FIXED_DT,ships:[ACTIVE_SHIP_RUNTIME,...physicalShipsB()].map(r=>{const o=observerC(r);return {...observerFacadeC(r),legacyPlayerScheduler:r===ACTIVE_SHIP_RUNTIME,legacyPlayerAudit:r===ACTIVE_SHIP_RUNTIME?spySchedulerSnapshot():null,tickCount:o.tickCount,cycles:o.cycles,rotors:{...o.rotors},enabled:{...o.enabled},emcon:r===ACTIVE_SHIP_RUNTIME?emconActive:o.emcon,rng:jsonSafeCloneV48Wip11A(o.rng),stats:{...o.stats},history:o.history.map(q=>({...q})),faces:o.normals.map(q=>({id:q.id,moduleName:q.moduleName,bearingRad:q.bearingRad,center:{...q.center},hCursor:q.hCursor,vCursor:q.vCursor,usedMs:q.usedMs}))};}),deferred:['bidirectionalWeaponRouting','receiverSpecificEW','enemyAI','helicopterFlightAndSensors']};}
function observerCommandC(id,cmd){
  const r=ENGAGEMENT_RUNTIME.ships.get(id);if(!r||r===ACTIVE_SHIP_RUNTIME)return {ok:false,reason:'NONPLAYER_DIAGNOSTIC_ONLY'};
  if(!cmd||Object.keys(cmd).some(k=>!['emcon','SPY','SPQ','NAV'].includes(k))||Object.values(cmd).some(v=>typeof v!=='boolean'))return {ok:false,reason:'INVALID_OBSERVER_COMMAND'};
  const o=observerC(r);for(const [k,v]of Object.entries(cmd))if(k==='emcon')o.emcon=v;else o.enabled[k]=v;return {ok:true};
}
function observerRenderStateC(r){const o=observerC(r);return {emconActive:o.emcon,mastLostV12:shipSystemDamageB(r,'MAST')>=80,spq9bLostV12:!o.enabled.SPQ,bridgeMasterELostV48Wip08:!o.enabled.NAV,spq9bAngleRad:o.rotors.SPQ,bridgeMasterEAngleRad:o.rotors.NAV,spq9bBeams:[],bridgeMasterEBeams:[],spyBeams:[]};}
function observerAuxPresentationC(r){const o=observerC(r);return (o.profile.equipment?.secondaryRadars??[]).map(q=>({id:q.id,angleRad:q.id==='SPQ9'?o.rotors.SPQ:o.rotors.NAV,origin:q.center,rotorPivot:q.rotorPivot}));}
function observerFixtureC(){
  const p=resolveShipProfile(ACTIVE_SHIP_RUNTIME.profileId),r=createPreparedShipRuntimeA(p,{entityId:'DIAG_OBSERVER_C'});preparePhysicalShipB(r);const o=prepareObserverC(r),checks={};
  const now=simStepCounter*SIM_FIXED_DT,rx=observerMountC(r,o.normals[0].center),meas={x:rx.x+metersToWorld(3000),y:rx.y,z:8,rangeM:3000,azRad:0,radialMps:0,radialVelSigmaMps:3,losUx:1,losUy:0,losUz:0,sensorXWorld:rx.x,sensorYWorld:rx.y,sensorVxMps:0,sensorVyMps:0,rangeSigmaM:20,azSigmaDeg:.1,quality:.8,source:'SPY1DV_SURFACE_SEARCH',surfaceReferenceZM:8,domainEvidence:{surface:.8,air:.1,missile:.1}};
  observerAcceptPlotsC(r,[meas]);checks.anonymousInitiation=o.tracks.size===1&&[...o.tracks.values()][0].identity==='UNKNOWN';
  observerAcceptPlotsC(r,[meas]);checks.sameTickNotConfirmation=![...o.tracks.values()][0].confirmed;
  checks.detachedNoLegacyWrites=!tracks.has(1)&&o.tracks!==tracks;checks.noTruthFields=!JSON.stringify(observerFacadeC(r)).match(/truthRef|objectId|_truthObject|physicalWorld/);
  checks.coverage360=Math.abs(o.normals.reduce((n,q)=>n+q.upper-q.lower,0)-TAU)<1e-9;checks.ownerClock=observerFacadeC(r).timeS===now;
  return {checks,pass:Object.values(checks).every(Boolean)};
}
window.__MULTISHIP_OBSERVERS_C__=Object.freeze({snapshot:observerSnapshotC,facade:id=>observerFacadeC(ENGAGEMENT_RUNTIME.ships.get(id)),fixture:observerFixtureC});
