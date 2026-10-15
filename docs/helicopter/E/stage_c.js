// Hawklink transport reads only its own radios and anonymous radar measurements.
// All newly introduced settings are simulation tuning, not Hawklink specifications.
const HELO_HAWKLINK_SPEC_E=Object.freeze({
  maxRangeM:Object.freeze({value:160000,source:'SIM_TUNED',reference:'Bounded mother-helicopter line-of-sight link envelope'}),
  latencyS:Object.freeze({value:.4,source:'SIM_TUNED',reference:'Existing offboard port transport latency'}),
  recentWindowS:Object.freeze({value:10,source:'SIM_TUNED',reference:'AIR recent transmitted plot counter window'}),
  selfGateSigma:Object.freeze({value:3,source:'SIM_TUNED',reference:'Own-navigation hull blanking uncertainty margin'}),
  selfMaxPadM:Object.freeze({value:75,source:'SIM_TUNED',reference:'Cap own-hull blanking expansion for uncertain radar plots'}),
  motherCdcDamageLimitPct:Object.freeze({value:80,source:'SIM_TUNED',reference:'Existing fleet radio combat-center availability threshold'}),
  motherMastDamageLimitPct:Object.freeze({value:85,source:'SIM_TUNED',reference:'Existing fleet radio mast availability threshold'})
});
function heloHawklinkExistingE(h){return ENGAGEMENT_RUNTIME.ships.get(h.ownerEntityId)?.aviation.heloSensorsE?.get(h.id)?.link??null;}
function heloHawklinkStateE(h){
  const s=heloSensorStateE(h);return s.link??(s.link={connected:false,reason:'ONBOARD',rangeM:0,horizonM:0,motherHeightM:0,sequence:0,attemptedTotal:0,transmittedTotal:0,rejectedTotal:0,selfRejectedTotal:0,lastTransmitS:null,lastTransitionS:null,recentTransmitS:[]});
}
function heloHawklinkPathE(h){
  const r=ENGAGEMENT_RUNTIME.ships.get(h.ownerEntityId),empty={connected:false,rangeM:0,horizonM:0,motherHeightM:0};
  if(!r||h.state==='LOST')return {...empty,reason:'MOTHER_UNAVAILABLE'};
  const point=observerMountC(r,resolveShipProfile(r.profileId).geometry.hardpoints.bridgeMasterE),rangeM=Math.hypot(h.positionM.x-worldToMeters(point.x),h.positionM.y-worldToMeters(point.y)),horizonM=radarHorizonKm(h.positionM.z,point.z)*1000,base={rangeM,horizonM,motherHeightM:point.z};
  if(h.onboard)return {...base,connected:false,reason:'ONBOARD'};
  if(shipEquipmentOfflineV1(r)||shipSystemDamageB(r,'CDC')>=HELO_HAWKLINK_SPEC_E.motherCdcDamageLimitPct.value||shipSystemDamageB(r,'MAST')>=HELO_HAWKLINK_SPEC_E.motherMastDamageLimitPct.value)return {...base,connected:false,reason:'MOTHER_UNAVAILABLE'};
  // EMCON currently suppresses ship radar only. Hawklink remains available, like Link 16.
  // A future communications EMCON policy must govern both links explicitly.
  if(rangeM>HELO_HAWKLINK_SPEC_E.maxRangeM.value)return {...base,connected:false,reason:'RANGE'};
  if(rangeM>horizonM)return {...base,connected:false,reason:'LOS'};
  return {...base,connected:true,reason:'CONNECTED'};
}
function heloHawklinkBeforeObserversE(dt){
  if(!heloSupportedA())return;const now=simStepCounter*SIM_FIXED_DT;
  for(const h of heloWorldA().values()){
    const r=ENGAGEMENT_RUNTIME.ships.get(h.ownerEntityId);if(!r)continue;
    const s=heloHawklinkStateE(h),path=heloHawklinkPathE(h),changed=s.connected!==path.connected||s.reason!==path.reason;
    Object.assign(s,path);s.recentTransmitS=s.recentTransmitS.filter(t=>now-t<=HELO_HAWKLINK_SPEC_E.recentWindowS.value);
    configureOffboardSourceC(r,{sourceId:'H'+(h.slot+1),connected:s.connected,latencyS:HELO_HAWKLINK_SPEC_E.latencyS.value});
    if(changed){s.lastTransitionS=now;debugLog(`HELO H${h.slot+1} HAWKLINK ${s.connected?'CONNECTED':'DISCONNECTED'} ${s.reason}`);}
  }
}
function heloHawklinkSelfContactE(r,plot){
  const n=r.navigation,C=plot.covarianceM2,p=plot.positionM,c=Math.cos(n.heading),s=Math.sin(n.heading),dx=p.x-worldToMeters(n.positionWorld.x),dy=p.y-worldToMeters(n.positionWorld.y),x=c*dx+s*dy,y=-s*dx+c*dy;
  const stations=resolveShipProfile(r.profileId).geometry.hullStations,minX=Math.min(...stations.map(v=>v[0])),maxX=Math.max(...stations.map(v=>v[0])),halfBeam=Math.max(...stations.map(v=>Math.abs(v[1]))),K=HELO_HAWKLINK_SPEC_E;
  const varX=c*c*C[0]+2*c*s*C[1]+s*s*C[4],varY=s*s*C[0]-2*c*s*C[1]+c*c*C[4],padX=Math.min(K.selfMaxPadM.value,K.selfGateSigma.value*Math.sqrt(Math.max(0,varX))),padY=Math.min(K.selfMaxPadM.value,K.selfGateSigma.value*Math.sqrt(Math.max(0,varY)));
  // The receiver blanks its measured own-hull footprint and bounded uncertainty.
  // Nearby unresolved contacts in the same small footprint are also blanked;
  // no target identity or physical-object reference is used to distinguish them.
  return x>=minX-padX&&x<=maxX+padX&&Math.abs(y)<=halfBeam+padY;
}
function heloPublishRadarPlotsE(h,plots){
  const r=ENGAGEMENT_RUNTIME.ships.get(h.ownerEntityId);if(!r)return;
  const s=heloHawklinkStateE(h),now=simStepCounter*SIM_FIXED_DT;
  for(const plot of plots){
    s.attemptedTotal++;const sequence=++s.sequence;
    if(!s.connected)continue; // No buffering or retransmission across a link outage.
    if(heloHawklinkSelfContactE(r,plot)){s.selfRejectedTotal++;continue;}
    const report={schema:'AEGIS_OFFBOARD_PLOT_C_1',sourceId:'H'+(h.slot+1),sequence,measuredAtS:plot.measuredAtS,positionM:{...plot.positionM},covarianceM2:[...plot.covarianceM2],domainEvidence:{...plot.domainEvidence}};
    const q=ingestOffboardReportC(r,report);
    if(q.ok){s.transmittedTotal++;s.lastTransmitS=now;s.recentTransmitS.push(now);}else s.rejectedTotal++;
  }
}
function heloHawklinkResetE(r){
  const q=r?.combatSystem.observerC?.offboard;if(!q)return;
  const ids=new Set(['H1','H2']);for(const id of ids)q.sources.delete(id);
  q.queue=q.queue.filter(v=>!ids.has(v.sourceId));
}
function heloHawklinkSummaryE(h){
  const s=heloHawklinkExistingE(h),now=simStepCounter*SIM_FIXED_DT;
  if(!s)return {connected:false,reason:h.onboard?'ONBOARD':'NOT_EVALUATED',rangeM:0,horizonM:0,motherHeightM:0,sequence:0,attemptedTotal:0,transmittedTotal:0,rejectedTotal:0,selfRejectedTotal:0,lastTransmitS:null,lastTransitionS:null,recentPlotCount:0};
  return {connected:s.connected,reason:s.reason,rangeM:s.rangeM,horizonM:s.horizonM,motherHeightM:s.motherHeightM,sequence:s.sequence,attemptedTotal:s.attemptedTotal,transmittedTotal:s.transmittedTotal,rejectedTotal:s.rejectedTotal,selfRejectedTotal:s.selfRejectedTotal,lastTransmitS:s.lastTransmitS,lastTransitionS:s.lastTransitionS,recentPlotCount:s.recentTransmitS.reduce((n,t)=>n+(now-t<=HELO_HAWKLINK_SPEC_E.recentWindowS.value),0)};
}

function heloHawklinkSnapshotE(h){return {link:heloHawklinkSummaryE(h)};}

function heloHarpoonLocalObservationE(tr,maxAgeS){
  const reports=tr?.observationReportsC;
  // Native tracks retain their existing release rules. An external contributor
  // cannot freshen the separate timestamp of a genuine local observation.
  if(!reports)return tr?.sensorSource!=='OFFBOARD_C';
  const stamp=reports.localAtS,now=simStepCounter*SIM_FIXED_DT;
  return Number.isFinite(stamp)&&stamp<=now&&now-stamp<=maxAgeS;
}
