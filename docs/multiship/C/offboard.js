// Prepared measurement port for future airborne observers. This does not create
// a helicopter, datalink to ordnance, perfect OTH contacts, or remote fire control.
function configureOffboardSourceC(r,config){
  if(!config||typeof config.sourceId!=='string'||!config.sourceId.match(/^[A-Z0-9_-]{1,40}$/)||typeof config.connected!=='boolean'||!Number.isFinite(config.latencyS)||config.latencyS<0||config.latencyS>10)return {ok:false,reason:'INVALID_LINK'};
  const o=observerC(r),old=o.offboard.sources.get(config.sourceId);if(!old&&o.offboard.sources.size>=8)return {ok:false,reason:'LINK_CAPACITY'};
  o.offboard.sources.set(config.sourceId,{sourceId:config.sourceId,connected:config.connected,latencyS:config.latencyS,lastSequence:old?.lastSequence??-1,lastReportS:old?.lastReportS??null});
  if(!config.connected)o.offboard.queue=o.offboard.queue.filter(q=>q.sourceId!==config.sourceId);
  return {ok:true};
}
function ingestOffboardReportC(r,report){
  const o=observerC(r),now=simStepCounter*SIM_FIXED_DT,bad=reason=>({ok:false,reason});
  if(!report||report.schema!=='AEGIS_OFFBOARD_PLOT_C_1'||Object.keys(report).some(k=>!['schema','sourceId','sequence','measuredAtS','positionM','covarianceM2','domainEvidence'].includes(k)))return bad('REPORT_SCHEMA_OR_TRUTH_FIELDS');
  const link=o.offboard.sources.get(report.sourceId);if(!link?.connected)return bad('LINK_UNAVAILABLE');
  if(!Number.isInteger(report.sequence)||report.sequence<=link.lastSequence||!Number.isFinite(report.measuredAtS)||report.measuredAtS>now+1e-9||now-report.measuredAtS>OBSERVER_POLICY_C.externalMaxAgeS)return bad('REPORT_TIME_OR_REPLAY');
  const pos=report.positionM,C=report.covarianceM2;
  if(!pos||Object.keys(pos).sort().join(',')!=='x,y,z'||!Object.values(pos).every(q=>Number.isFinite(q)&&Math.abs(q)<2e7)||!Array.isArray(C)||C.length!==9||!C.every(Number.isFinite)||[0,4,8].some(i=>C[i]<1||C[i]>1e10)||Math.abs(C[1]-C[3])+Math.abs(C[2]-C[6])+Math.abs(C[5]-C[7])>1e-8)return bad('REPORT_COVARIANCE');
  // Sylvester criterion: symmetric positive definite, with actual uncertainty.
  const determinant=C[0]*(C[4]*C[8]-C[5]*C[7])-C[1]*(C[3]*C[8]-C[5]*C[6])+C[2]*(C[3]*C[7]-C[4]*C[6]);
  if(C[0]*C[4]-C[1]*C[3]<=0||determinant<=0)return bad('REPORT_COVARIANCE');
  const e=report.domainEvidence;if(!e||Object.keys(e).sort().join(',')!=='air,background,missile,surface'||!Object.values(e).every(v=>Number.isFinite(v)&&v>=0&&v<=1))return bad('REPORT_EVIDENCE');
  if(o.offboard.queue.length>=64)return bad('REPORT_QUEUE_FULL');
  const clean=jsonSafeCloneV48Wip11A(report);o.offboard.queue.push({...clean,availableAtS:now+link.latencyS});link.lastSequence=report.sequence;return {ok:true};
}
function offboardPlotC(report,now){
  const age=now-report.measuredAtS,C=report.covarianceM2.slice(),surface=report.domainEvidence.surface>.55&&report.domainEvidence.surface>report.domainEvidence.air;
  // Stale positions have no measured transverse velocity. Inflate covariance
  // instead of pretending reception time or target truth supplies a new fix.
  const speedPrior=surface?12:180;C[0]+=age*age*speedPrior*speedPrior;C[4]+=age*age*speedPrior*speedPrior;C[8]+=age*age*(surface?1.2:120)**2;
  return {x:metersToWorld(report.positionM.x),y:metersToWorld(report.positionM.y),z:report.positionM.z,sensorVxMps:0,sensorVyMps:0,rangeSigmaM:Math.sqrt(Math.max(C[0],C[4])),altitudeSigmaM:Math.sqrt(C[8]),quality:Math.exp(-age/8)*.7,source:'OFFBOARD_C',cartesianCovarianceM2:C,domainEvidence:report.domainEvidence,_reportedSurface:surface};
}
function acceptOffboardC(r,report){
  const o=observerC(r),now=simStepCounter*SIM_FIXED_DT,meas=offboardPlotC(report,now),age=now-report.measuredAtS;
  let match=null;for(const [id,tr]of o.tracks){const nis=trackCartesianAssociationNisV33(tr,meas);if(nis<=25&&(!match||nis<match.nis))match={id,nis};}
  const existing=match?o.tracks.get(match.id):null,priorLocalS=existing?.observationReportsC?.localAtS??(existing&&existing.sensorSource!=='OFFBOARD_C'?(existing._lastMeasurementStep??simStepCounter)*SIM_FIXED_DT:null);
  // A new packet sequence may contain a repeated/older fix. It cannot provide
  // another independent confirmation or overwrite a newer fix on this file.
  if(existing?.observationReportsC?.remote[report.sourceId]?.measuredAtS>=report.measuredAtS)return false;
  let tr;
  if(r===ACTIVE_SHIP_RUNTIME)tr=updateSensorTrackMeasurement(match?.id??null,meas,{source:meas.source,domainEvidence:meas.domainEvidence});
  else{
    if(match){tr=o.tracks.get(match.id);if(!trackEkfUpdateCartesianPosition(tr,meas))return false;}
    else{if(o.tracks.size>=OBSERVER_POLICY_C.maxTracks)return false;tr=observerNewTrackC(o,{...meas,radialMps:0,losUx:1,losUy:0},meas._reportedSurface);o.tracks.set(tr.trackId,tr);}
    observerClassifyC(tr,meas);tr.sensorSource='OFFBOARD_C';tr.sensorAge=age;tr.sensorHits++;tr.confirmed=tr.sensorHits>=3;tr.sensorDetected=true;trackRefreshDerivedQuality(tr);
  }
  if(!tr)return false;
  if(!existing&&meas._reportedSurface){tr._kfP[21]=tr._kfP[28]=144;tr._kfP[35]=1.44;tr._surfaceMotionPriorWip13B13=true;}
  tr.observationReportsC??={localAtS:priorLocalS,remote:{}};
  tr.observationReportsC.remote[report.sourceId]={measuredAtS:report.measuredAtS,receivedAtS:now,sequence:report.sequence};
  // Do not age a newer local observation backwards, or freshen a stale remote one.
  const local=tr.observationReportsC.localAtS;tr.sensorAge=Math.min(local==null?Infinity:now-local,age);tr._lastMeasurementStep=Math.floor((now-tr.sensorAge)/SIM_FIXED_DT);
  tr.memActive=tr.sensorAge>OBSERVER_POLICY_C.coastS;tr.trackLifecycle=tr.memActive?'MEMORY':tr.confirmed?'FIRM':'TENTATIVE';
  tr.ttl=Math.max(0,OBSERVER_POLICY_C.dropS-tr.sensorAge);trackRefreshDerivedQuality(tr);o.offboard.accepted++;o.offboard.sources.get(report.sourceId).lastReportS=report.measuredAtS;return true;
}
function drainOffboardC(r){
  const o=observerC(r),now=simStepCounter*SIM_FIXED_DT,pending=[];
  for(const q of o.offboard.queue){if(!o.offboard.sources.get(q.sourceId)?.connected)continue;if(q.availableAtS>now){pending.push(q);continue;}if(now-q.measuredAtS>OBSERVER_POLICY_C.externalMaxAgeS||!acceptOffboardC(r,q))o.offboard.rejected++;}
  o.offboard.queue=pending;
}
function observationReportViewC(tr,r=ACTIVE_SHIP_RUNTIME){
  if(!tr?.observationReportsC)return null;const now=simStepCounter*SIM_FIXED_DT,o=observerC(r);
  return {localAgeS:tr.observationReportsC.localAtS==null?null:now-tr.observationReportsC.localAtS,
    remote:Object.entries(tr.observationReportsC.remote).map(([sourceId,q])=>({sourceId,measurementAgeS:now-q.measuredAtS,deliveryDelayS:q.receivedAtS-q.measuredAtS,connected:!!o.offboard.sources.get(sourceId)?.connected}))};
}
function offboardSnapshotC(r){const q=observerC(r).offboard;return {schema:'AEGIS_OFFBOARD_PORT_C_1',sources:[...q.sources.values()].map(v=>({...v})),queued:q.queue.length,accepted:q.accepted,rejected:q.rejected,helicopterImplemented:false,ordnanceDatalink:false};}
function offboardDiagnosticC(id,cmd){const r=ENGAGEMENT_RUNTIME.ships.get(id);if(!r)return {ok:false,reason:'OBSERVER_NOT_FOUND'};if(cmd?.link)return configureOffboardSourceC(r,cmd.link);if(cmd?.report)return ingestOffboardReportC(r,cmd.report);return {ok:false,reason:'INVALID_DIAGNOSTIC'};}
function observationReportLabelC(tr){
  const q=observationReportViewC(tr);if(!q?.remote.length)return '';const latest=q.remote.slice().sort((a,b)=>a.measurementAgeS-b.measurementAgeS)[0];
  return ' EXT '+latest.sourceId+' '+latest.measurementAgeS.toFixed(1)+'s '+(latest.connected?'LINK':'LINK LOST');
}
function offboardFixtureC(){
  const p=resolveShipProfile(ACTIVE_SHIP_RUNTIME.profileId),r=createPreparedShipRuntimeA(p,{entityId:'DIAG_OFFBOARD_C'});preparePhysicalShipB(r);prepareObserverC(r);
  const checks={},now=simStepCounter*SIM_FIXED_DT,report={schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'HELI_TEST',sequence:1,measuredAtS:now,positionM:{x:120000,y:50000,z:8},covarianceM2:[40000,0,0,0,40000,0,0,0,400],domainEvidence:{surface:.9,air:.1,missile:.1,background:.1}};
  checks.disconnectedBlocked=!ingestOffboardReportC(r,report).ok;checks.linkSetup=configureOffboardSourceC(r,{sourceId:'HELI_TEST',connected:true,latencyS:.5}).ok;
  checks.validAccepted=ingestOffboardReportC(r,report).ok;drainOffboardC(r);checks.deliveryDelayed=observerC(r).tracks.size===0;
  checks.replayBlocked=!ingestOffboardReportC(r,report).ok;checks.truthBlocked=!ingestOffboardReportC(r,{...report,sequence:2,objectId:'SECRET'}).ok;
  checks.futureBlocked=!ingestOffboardReportC(r,{...report,sequence:2,measuredAtS:now+1}).ok;
  checks.invalidCovarianceBlocked=!ingestOffboardReportC(r,{...report,sequence:2,covarianceM2:[1,2,0,2,1,0,0,0,1]}).ok;
  configureOffboardSourceC(r,{sourceId:'HELI_TEST',connected:false,latencyS:.5});checks.lossClearsPending=observerC(r).offboard.queue.length===0;
  configureOffboardSourceC(r,{sourceId:'HELI_TEST',connected:true,latencyS:0});ingestOffboardReportC(r,{...report,sequence:2});drainOffboardC(r);
  ingestOffboardReportC(r,{...report,sequence:3});drainOffboardC(r);checks.repeatedFixNotNewConfirmation=observerC(r).offboard.accepted===1&&observerC(r).offboard.rejected===1&&[...observerC(r).tracks.values()][0].sensorHits===1;
  checks.noMissileLink=offboardSnapshotC(r).ordnanceDatalink===false;checks.noTruthFacade=!JSON.stringify(observerFacadeC(r)).match(/truthRef|objectId|physicalWorld/);
  return {checks,pass:Object.values(checks).every(Boolean)};
}
