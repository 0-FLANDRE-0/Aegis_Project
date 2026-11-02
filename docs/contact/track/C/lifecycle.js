// TRACK-C: diagnostic compatibility views only. No track/RF/weapon writes.
const TRACK_C_IMPLEMENTATION_MODE='ACTIVE';
const TRACK_C_DIAG={enabled:false,capacity:2048,serial:0,dropped:0,errors:0,records:[],previous:new Map()}; // SIM_TUNED diagnostic capacity only.
function trackCFiniteC(v){return typeof v==='number'&&Number.isFinite(v)?v:null;}
function trackCTimeC(){return simStepCounter*SIM_FIXED_DT;}
function trackCEvidenceViewC(tr,now=trackCTimeC()){
  const iff=tr?.iffF,air=iff?.source==='AIR_IFF_E',operatorAt=Number.isFinite(tr?._operatorIdentitySetAtStep)?tr._operatorIdentitySetAtStep*SIM_FIXED_DT:null,
    own=tr?._harpoonOwnC,ownAt=Number.isFinite(own?.lastStep)?own.lastStep*SIM_FIXED_DT:null,ownAge=ownAt===null?null:Math.max(0,now-ownAt),
    ownReason=String(tr?._a3AuthorityReason??''),ownResolved=ownReason.includes('OWN_LAUNCH')||ownReason==='POSSIBLE_OWN_LAUNCH';
  return {
    classification:{value:tr?.classification??null,source:'MEASUREMENT_CLASSIFIER',confirmed:!!tr?.confirmed,grantsAuthority:false},
    identity:{value:tr?.identity??'UNKNOWN',source:ownResolved?'OWN_LAUNCH_RADAR_CORRELATION':heloFriendlyIffEvidenceE(tr)?'AUTHENTICATED_IFF':tr?._operatorIdentity?'OPERATOR_OR_LEGACY_SURFACE_IFF':tr?.identity==='ASSUMED_HOSTILE'?'EXISTING_KINEMATIC_POLICY':'EXISTING_RESOLVED_IDENTITY_SOURCE_NOT_STORED'},
    operator:{value:tr?._operatorIdentity??null,setAtS:operatorAt,expiresAtS:null,policy:'EXISTING_PERSISTENT_ANNOTATION_NO_NEW_EXPIRY'},
    iff:iff?{authenticatedFriendly:iff.authenticatedFriendly===true,source:iff.source??'LEGACY_SURFACE_IFF',measuredAtS:trackCFiniteC(iff.measuredAtS),expiresAtS:air?trackCFiniteC(iff.expiresAtS):null,valid:air?Number.isFinite(iff.expiresAtS)&&iff.expiresAtS>now:iff.authenticatedFriendly===true,policy:air?'EXISTING_AIR_IFF_HOLD':'EXISTING_SURFACE_IFF_NO_EXPIRY'}:null,
    ownFireEvidence:own?{source:'STORED_FIRST_PARTY_LAUNCH_RADAR_CORRELATION',confirmed:!!own.confirmed,launchId:own.launchId??null,lastMeasuredAtS:ownAt,ageS:ownAge,visibleCoastS:HARPOON_CORRELATION_G.visibleCoastS,revalidationLimitS:HARPOON_CORRELATION_G.reacquireS,evidence:own.evidence??null,policy:'READ_STORED_EVIDENCE_ONLY; DO_NOT_CALL_MUTATING_CORRELATOR'}:null,
    threatStatus:tr?.threatStatus??null,engagementAuthority:tr?.engagementAuthority??null,
    authorityReason:tr?._a3AuthorityReason??null,
    aliasPolicy:'NO_CLASSIFICATION_IDENTITY_OPERATOR_IFF_AUTHORITY_COPY',
    distinction:'classification != identity != authority; nonresponse is not hostile evidence'
  };
}
function trackCLifecycleViewC(tr,ownerEntityId,now=trackCTimeC()){
  const measuredAtS=Number.isFinite(tr?._lastMeasurementStep)?tr._lastMeasurementStep*SIM_FIXED_DT:trackCFiniteC(tr?.lastMeasurementS),
    airAtS=Number.isFinite(tr?._radar3dAirStepFC)?tr._radar3dAirStepFC*SIM_FIXED_DT:null,
    contributors=Object.fromEntries(Object.entries(tr?.contributorsC??{}).map(([k,v])=>[k,{measuredAtS:trackCFiniteC(v?.measuredAtS),receivedAtS:null,quality:trackCFiniteC(v?.quality),receivedTimePolicy:'NOT_STORED_ON_LEGACY_CONTRIBUTOR'}]));
  const reports=tr?.observationReportsC;
  for(const [sourceId,q]of Object.entries(reports?.remote??{}))contributors['OFFBOARD:'+sourceId]={measuredAtS:trackCFiniteC(q.measuredAtS),receivedAtS:trackCFiniteC(q.receivedAtS),sequence:q.sequence??null,policy:'RECEIPT_OR_REPLAY_DOES_NOT_PROVE_INDEPENDENT_FIX'};
  return {schema:'AEGIS_TRACK_C_LIFECYCLE_VIEW_1',ownerEntityId,trackId:tr?.trackId??null,trackUid:tr?.trackUid??null,
    timeS:now,filterEpochS:trackCFiniteC(tr?._kfTimeS),nativeLifecycle:tr?.trackLifecycle??null,
    confirmation:tr?.confirmed?'FIRM':'TENTATIVE',sensorSource:tr?.sensorSource??null,
    sensorAgeS:trackCFiniteC(tr?.sensorAge),ttlS:trackCFiniteC(tr?.ttl),memory:!!tr?.memActive,reacquiring:!!tr?.reacquiring,
    lastAcceptedMeasurementAtS:measuredAtS,lastIndependentFixAtS:trackCFiniteC(tr?.lastIndependentHitS),
    independentFixPolicy:ownerEntityId===ACTIVE_SHIP_RUNTIME.entityId?'LEGACY_OWN_ACCEPTED_PLOT_COUNT; packet/ISAR not inferred':'LEGACY_OBSERVER_CONFIRMATION_SPACING',
    hits:trackCFiniteC(tr?.sensorHits),contributors,
    air3d:{lastObservedAtS:airAtS,ageS:airAtS===null?null:Math.max(0,now-airAtS),valid:trackHasAirObservationFC(tr),maxAgeS:TRACK_HARD_TTL},
    surfacePrior:{only2D:!!tr?._surface2DOnlyFC,motionPrior:!!tr?._surfaceMotionPriorWip13B13,measuredElevation:false,referenceRole:'MODEL_PRIOR_NOT_HEIGHT_OBSERVATION'},
    evidence:trackCEvidenceViewC(tr,now),readOnly:true};
}
function trackCLocalViewC(rec,ownerEntityId,mountId){
  return {schema:'AEGIS_TRACK_C_LOCAL_RF_VIEW_1',ownerEntityId,mountId,fileId:rec?.id??null,
    confirmation:rec?.confirmed?'FIRM':'TENTATIVE',firstSeenS:trackCFiniteC(rec?.firstSeenS),
    localAgeS:trackCFiniteC(rec?.st?.localAgeS),localHits:trackCFiniteC(rec?.st?.localHits),
    ownFireEvidence:{value:!!rec?.ownFireEvidence,source:'ACTUAL_OWN_LAUNCH_RF_PARTITION',expires:'NATIVE_FILE_RETIREMENT',inheritedFromProximity:false},
    protectedIdentity:{value:rec?.protectedIdentity??null,cmsTrackId:rec?.protectedCmsId??null,source:rec?.ownFireEvidence?'ACTUAL_OWN_LAUNCH_RF_PARTITION':'EXISTING_GEOMETRIC_CMS_VETO',confirmedAtS:null,policy:'LEGACY_LATCH; NO_NEW_EXPIRY_OR_IFF_POLICY'},
    cmsTrackId:rec?.cmsTrackId??null,cmsIdentity:rec?.cmsIdentity??null,readOnly:true};
}
function trackCSnapshotC(){
  const owners=[ACTIVE_SHIP_RUNTIME,...physicalShipsB()],now=trackCTimeC();
  return {schema:'AEGIS_TRACK_C_DIAGNOSTICS_1',mode:TRACK_C_IMPLEMENTATION_MODE,timeS:now,truthUsed:false,
    ownerTracks:owners.map(r=>({ownerEntityId:r.entityId,tracks:[...(r.combatSystem.observerC?.tracks??r.combatSystem.trackManager?.tracks??new Map())].map(([,tr])=>trackCLifecycleViewC(tr,r.entityId,now))})),
    ownLocalFiles:[...CIWS_C55.banks].flatMap(([mountId,b])=>[...b.files.values()].map(rec=>trackCLocalViewC(rec,ACTIVE_SHIP_RUNTIME.entityId,mountId))),
    routes:{SPQ_AIR:TRACK_C_IMPLEMENTATION_MODE,C55_OWN:TRACK_C_IMPLEMENTATION_MODE,C55_NPC:TRACK_C_IMPLEMENTATION_MODE,c55Reason:'EXISTING_DISTANCE_ELIGIBILITY; NIS_FROM_EXISTING_AXIS_KF_P_PLUS_NATIVE_MEASUREMENT_R'},
    trace:{enabled:TRACK_C_DIAG.enabled,recorded:TRACK_C_DIAG.serial,dropped:TRACK_C_DIAG.dropped,errors:TRACK_C_DIAG.errors,records:TRACK_C_DIAG.records.map(r=>({...r}))}};
}
function trackCSampleC(){
  if(!TRACK_C_DIAG.enabled)return;
  try{
    const snapshot=trackCSnapshotC(),current=new Map();
    for(const owner of snapshot.ownerTracks)for(const q of owner.tracks){
      const key=JSON.stringify([owner.ownerEntityId,q.trackId]),old=TRACK_C_DIAG.previous.get(key);
      current.set(key,q);
      const changed=!old||['nativeLifecycle','confirmation','hits','lastAcceptedMeasurementAtS','reacquiring','memory'].some(k=>old[k]!==q[k])||JSON.stringify(old.evidence)!==JSON.stringify(q.evidence);
      if(changed)trackCRecordC({event:old?'OBSERVED_STATE_CHANGE':'FILE_APPEARED',...q});
    }
    for(const[key,old]of TRACK_C_DIAG.previous)if(!current.has(key))trackCRecordC({event:'FILE_DROPPED',ownerEntityId:old.ownerEntityId,trackId:old.trackId,timeS:snapshot.timeS,lastAcceptedMeasurementAtS:old.lastAcceptedMeasurementAtS,priorState:old.nativeLifecycle});
    TRACK_C_DIAG.previous=current;
  }catch(_){TRACK_C_DIAG.errors++;}
}
function trackCRecordC(record){
  if(!TRACK_C_DIAG.enabled)return;
  TRACK_C_DIAG.records.push({...record,serial:++TRACK_C_DIAG.serial});
  if(TRACK_C_DIAG.records.length>TRACK_C_DIAG.capacity){TRACK_C_DIAG.records.shift();TRACK_C_DIAG.dropped++;}
}
function trackCAliasUniqueC(candidates){return candidates.length===1?candidates[0]:null;}
function trackCAliasDecisionC(candidates,newId,tr,store,extractState){
  const reject=reason=>({ok:false,reason});
  if(['FRIEND','NEUTRAL','TRAINING_TARGET'].includes(tr?.identity)||['FRIEND','NEUTRAL','TRAINING_TARGET'].includes(tr?._operatorIdentity)||heloFriendlyIffEvidenceE(tr))return reject('NEW_FILE_PROTECTED');
  if(!tr?.confirmed||tr.sensorDetected===false||tr.memActive||tr.reacquiring)return reject('NEW_FILE_NOT_FIRM_OBSERVATION');
  const pick=trackCAliasUniqueC(candidates);if(!pick)return reject(candidates.length?'AMBIGUOUS_LOST_PREDECESSOR':'NO_LOST_PREDECESSOR');
  for(const[id,other]of store){
    if(id===newId||id===pick.oldId||!other?.confirmed||other.sensorDetected===false||other.memActive||other.reacquiring)continue;
    const si=extractState(other),ps=pick.coast;if(!si||!ps)continue;
    if(Math.hypot(si.x-ps.x,si.y-ps.y,si.z-ps.z)<=pick.posGate&&Math.hypot(si.vx-ps.vx,si.vy-ps.vy,si.vz-ps.vz)<=pick.velGate)return reject('AMBIGUOUS_LIVE_SUCCESSOR');
  }
  return {ok:true,reason:'UNIQUE_EXISTING_COAST_GATES',pick};
}
function trackCC55AssignmentsC(plots,files,cfg){
  const pairs=[],fileRows=[...files.values()],invalid=[];
  for(let i=0;i<plots.length;i++){
    const p=plots[i],m=p.measurement;
    for(const rec of fileRows){
      if(!!rec.ownFireEvidence!==!!p.knownOwnLaunch)continue;
      const s=rec.st,distanceM=Math.hypot(s.rxM-m.rxM,s.ryM-m.ryM,s.rzM-m.rzM),
        gateM=CIWS_C55_POLICY.associationBaseM+m.rangeM*deg(cfg.searchAzSigmaDeg)*3+(s.localHits<5?2200:350)*Math.min(.35,s.localAgeS);
      if(!(distanceM<gateM))continue;
      // Identical innovation denominator and R floor to native c55UpdateFile.
      // Native axis filters already assume independent x/y/z; no P/R/gain writes.
      const R=m.positionVarianceM2??[36,100,100],P=s._c55P,axis=['rxM','ryM','rzM'];let nis=0,logDetS=0,valid=true;
      for(let k=0;k<3;k++){
        const variance=P?.[k]?.[0],noise=Math.max(.5,R[k]),S=variance+noise,innovation=m[axis[k]]-s[axis[k]];
        if(![variance,noise,S,innovation].every(Number.isFinite)||variance<0||!(S>0)){valid=false;break;}
        nis+=innovation*innovation/S;logDetS+=Math.log(S);
      }
      if(!valid||!Number.isFinite(nis)||nis<0){invalid.push({i,id:rec.id});continue;}
      pairs.push({i,id:rec.id,nis,evidence:{valid:true,dimensions:3,epochS:trackCTimeC(),logDetS}});
    }
  }
  const maxCost=pairs.reduce((n,p)=>Math.max(n,p.nis),TRACK_B_POLICY.ambiguityDeltaNis);
  // 1e6 is the unchanged shared solver's blocked-cell sentinel, not a new RF gate.
  if(invalid.length||maxCost>=1e6-.5)return {pairs:[],heldPlots:new Set(plots.map((_,i)=>i)),heldTracks:new Set(fileRows.map(r=>r.id)),reason:invalid.length?'INVALID_NATIVE_C55_COVARIANCE':'SHARED_SOLVER_NUMERIC_DOMAIN',components:[],rejected:[],ambiguous:true};
  // The pre-existing distance gate decides edge eligibility. Dynamic gate only
  // admits every finite native-eligible cost to the existing generic solver;
  // it introduces no extra NIS rejection threshold or physical coefficient.
  return trackBSolveB({plotCount:plots.length,pairs,gate:maxCost,ambiguityDeltaCost:TRACK_B_POLICY.ambiguityDeltaNis},bridgeMasterEMinCostAssignmentV35);
}
function trackCSpqAssignmentsC(observations){
  const pairs=[];
  for(let i=0;i<observations.length;i++){
    const plot=observations[i].plot;
    for(const[id,tr]of tracks){
      if(!tr||tr.sensorDetected===false||!trackMayAcceptAirPlotCrossDomainWip13B14(tr,plot))continue;
      const nis=trackRadarAssociationNisV31(tr,plot),cross=trackSurfaceBackedWip13B14(tr),gate=Math.min(TRACK_FILTER_MODEL.nisGateSearch,cross?WIP13B14_CROSS_DOMAIN_ASSOCIATION_CONTRACT.airToSurfaceNisGate:TRACK_FILTER_MODEL.nisGateSearch);
      if(nis<=gate)pairs.push({i,id,nis,sanity:trackBGeometryB(tr,plot,'AIR'),evidence:trackBEvidenceStableB(tr,plot,'AIR',trackCTimeC())});
    }
  }
  return trackBSolveB({plotCount:observations.length,pairs,gate:TRACK_FILTER_MODEL.nisGateSearch,ambiguityDeltaCost:TRACK_B_POLICY.ambiguityDeltaNis},bridgeMasterEMinCostAssignmentV35);
}
window.__TRACK_C__=Object.freeze({schema:'AEGIS_TRACK_C_DIAGNOSTICS_1',mode:TRACK_C_IMPLEMENTATION_MODE,
  snapshot:trackCSnapshotC,view:trackCLifecycleViewC,evidence:trackCEvidenceViewC,localView:trackCLocalViewC,
  sample:trackCSampleC,uniqueAlias:trackCAliasUniqueC,aliasDecision:trackCAliasDecisionC,spqAssignments:trackCSpqAssignmentsC,c55Assignments:trackCC55AssignmentsC,
  configure(options={}){if(typeof options.enabled==='boolean')TRACK_C_DIAG.enabled=options.enabled;if(Number.isFinite(options.capacity))TRACK_C_DIAG.capacity=Math.max(16,Math.min(32768,Math.floor(options.capacity)));return {enabled:TRACK_C_DIAG.enabled,capacity:TRACK_C_DIAG.capacity};},
  clear(){TRACK_C_DIAG.records.length=0;TRACK_C_DIAG.previous.clear();TRACK_C_DIAG.serial=TRACK_C_DIAG.dropped=TRACK_C_DIAG.errors=0;}
});
