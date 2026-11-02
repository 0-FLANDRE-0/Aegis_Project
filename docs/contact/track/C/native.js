// DIRECT_NATIVE_ANONYMOUS_FIXTURE. Synthetic observations, no physical truth hint.
window.__TRACK_C_NATIVE__={run(){
  const checks={},detail={},now=simStepCounter*SIM_FIXED_DT,owner=ACTIVE_SHIP_RUNTIME.entityId;
  const state=()=>__TRACK_RUNTIME_A__.state(),before=state();
  for(let i=0;i<20;i++)__TRACK_C__.snapshot();
  checks.snapshotReadOnly=before===state();
  __TRACK_C__.configure({enabled:true,capacity:32768});__TRACK_C__.sample();__TRACK_C__.sample();
  checks.sampleReadOnly=before===state();
  const base={trackId:901,confirmed:true,sensorDetected:true,sensorAge:.2,sensorHits:4,ttl:12,trackLifecycle:'FIRM',classification:'AIR',identity:'UNKNOWN',engagementAuthority:'WITHHELD',_lastMeasurementStep:simStepCounter,_radar3dAirStepFC:simStepCounter};
  const view=__TRACK_C__.view(base,owner);
  checks.nativeLifecycleNotReinterpreted=view.nativeLifecycle==='FIRM'&&view.confirmation==='FIRM';
  checks.air3dObservedWindow=view.air3d.valid&&view.air3d.maxAgeS===TRACK_HARD_TTL;
  const stale={...base,_radar3dAirStepFC:simStepCounter-Math.ceil(TRACK_HARD_TTL/SIM_FIXED_DT)-1,_surface2DOnlyFC:true,_surfaceMotionPriorWip13B13:true};
  const prior=__TRACK_C__.view(stale,owner);
  checks.priorIsNotAltitudeObservation=!prior.air3d.valid&&!prior.surfacePrior.measuredElevation&&prior.surfacePrior.only2D;
  checks.missingReceiptNotFabricated=__TRACK_C__.view({...base,contributorsC:{SPQ:{measuredAtS:now}}},owner).contributors.SPQ.receivedAtS===null;
  const manual={...base,_operatorIdentity:'FRIEND',_operatorIdentitySetAtStep:0,identity:'FRIEND'};
  const ev=__TRACK_C__.evidence(manual);
  checks.manualIdentityPersistsInView=ev.operator.value==='FRIEND'&&ev.operator.expiresAtS===null;
  const receipt={...base,identity:'FRIEND',_a3AuthorityReason:'OWN_LAUNCH_RADAR_CORRELATION',_harpoonOwnC:{confirmed:true,launchId:7,lastStep:simStepCounter,evidence:'LAUNCH_CORRELATED_ANONYMOUS_RADAR'}};
  const receiptBefore=JSON.stringify(receipt),receiptView=__TRACK_C__.evidence(receipt);
  checks.ownLaunchSourceSeparated=receiptView.identity.source==='OWN_LAUNCH_RADAR_CORRELATION'&&receiptView.ownFireEvidence.launchId===7;
  checks.storedReceiptReadOnly=receiptBefore===JSON.stringify(receipt)&&receiptView.ownFireEvidence.lastMeasuredAtS===now;
  checks.noReplyNotHostile=__TRACK_C__.evidence({...base,iffF:null}).identity.value==='UNKNOWN';
  const airborne={...base,iffF:{source:'AIR_IFF_E',authenticatedFriendly:true,measuredAtS:now,expiresAtS:now+1}};
  checks.airIffActiveAndExpired=__TRACK_C__.evidence(airborne,now).iff.valid&&!__TRACK_C__.evidence(airborne,now+2).iff.valid;
  const surface={...base,iffF:{authenticatedFriendly:true,measuredAtS:0}};
  checks.surfaceIffExistingPolicyDocumented=__TRACK_C__.evidence(surface,now+999).iff.policy==='EXISTING_SURFACE_IFF_NO_EXPIRY';
  const record={id:-1,confirmed:true,ownFireEvidence:true,protectedIdentity:'FRIEND',st:{localHits:4,localAgeS:0}};
  const local=__TRACK_C__.localView(record,owner,'fixture');
  checks.ownFireSourceAndLifetime=local.ownFireEvidence.source==='ACTUAL_OWN_LAUNCH_RF_PARTITION'&&local.ownFireEvidence.expires==='NATIVE_FILE_RETIREMENT'&&!local.ownFireEvidence.inheritedFromProximity;
  checks.c55ModeDeclaredAccurately=__TRACK_C__.snapshot().routes.C55_OWN===__TRACK_C__.mode&&__TRACK_C__.snapshot().routes.C55_NPC===__TRACK_C__.mode;
  const cfg=CIWS_LOCAL_TRACK_MODEL.GUN,localFile=(id,x=0)=>({id,ownFireEvidence:false,st:{rxM:x,ryM:0,rzM:0,localHits:10,localAgeS:0,_c55P:[[4,0,100],[4,0,100],[4,0,100]]}}),
    localMeas=(x=3,y=4)=>({measurement:{rxM:x,ryM:y,rzM:0,rangeM:100,positionVarianceM2:[5,5,5]},knownOwnLaunch:false}),f=localFile(-55),bank=new Map([[f.id,f]]),priorLocal=JSON.stringify(f),pm=localMeas(),one=__TRACK_C__.c55Assignments([pm],bank,cfg);
  checks.c55UsesNativeInnovationDenominator=one.pairs.length===1&&Math.abs(one.pairs[0].nis-25/9)<1e-12;
  checks.c55AssociationCannotUpdateFilter=priorLocal===JSON.stringify(f);
  checks.c55OwnFirePartitionPreserved=__TRACK_C__.c55Assignments([{...pm,knownOwnLaunch:true}],bank,cfg).pairs.length===0;
  const doubleBank=new Map([[-55,localFile(-55)],[-56,localFile(-56,100)]]),two=__TRACK_C__.c55Assignments([localMeas(1,0),localMeas(99,0)],doubleBank,cfg);
  checks.c55SeparatedObservedFilesOneToOne=two.pairs.length===2&&new Set(two.pairs.map(p=>p.id)).size===2&&two.heldPlots.size===0;
  const tieLocal=__TRACK_C__.c55Assignments([pm],new Map([[-55,localFile(-55)],[-56,localFile(-56)]]),cfg);
  checks.c55ExactTieUsesSharedHold=tieLocal.pairs.length===0&&tieLocal.heldPlots.has(0)&&tieLocal.heldTracks.size===2;
  const broken=localFile(-55);delete broken.st._c55P;const invalidLocal=__TRACK_C__.c55Assignments([pm],new Map([[-55,broken]]),cfg);
  checks.c55MissingNativeCovarianceNeverInvented=invalidLocal.pairs.length===0&&invalidLocal.heldPlots.has(0)&&invalidLocal.reason==='INVALID_NATIVE_C55_COVARIANCE';
  let localPoison=0;Object.defineProperty(pm.measurement,'truthRef',{get(){localPoison++;throw Error('C55_TRUTH_READ');}});__TRACK_C__.c55Assignments([pm],bank,cfg);checks.c55TruthPoisonReadsZero=localPoison===0;
  // Run actual alias gate on competing observed coast hypotheses and protected files.
  const coast={x:0,y:0,z:100,vx:-250,vy:0,vz:0},candidate={oldId:100,newId:901,posGate:600,velGate:120,coast};
  const extract=q=>q.fixtureState??coast;
  checks.uniqueCoastAccepted=__TRACK_C__.aliasDecision([candidate],901,base,new Map([[901,base]]),extract).ok;
  checks.twoLostFilesNeverInherit=!__TRACK_C__.aliasDecision([candidate,{...candidate,oldId:101}],901,base,new Map(),extract).ok;
  checks.twoLiveSuccessorsNeverInherit=!__TRACK_C__.aliasDecision([candidate],901,base,new Map([[902,{...base,trackId:902}]]),extract).ok;
  checks.friendNeverInheritsHostileFcs=!__TRACK_C__.aliasDecision([candidate],901,manual,new Map(),extract).ok;
  checks.neutralNeverInheritsHostileFcs=!__TRACK_C__.aliasDecision([candidate],901,{...base,identity:'NEUTRAL'},new Map(),extract).ok;
  checks.memoryNeverInherits=!__TRACK_C__.aliasDecision([candidate],901,{...base,memActive:true},new Map(),extract).ok;
  checks.reacquiringNeverInherits=!__TRACK_C__.aliasDecision([candidate],901,{...base,reacquiring:true},new Map(),extract).ok;
  checks.tentativeNeverInherits=!__TRACK_C__.aliasDecision([candidate],901,{...base,confirmed:false},new Map(),extract).ok;
  // Only the native EKF initializer/corrector makes these tracks; geometry is a supplied observation.
  const saved=[...tracks];tracks.clear();
  function plot(yM){const xM=5000,z=100,rx=aircraft.x(),ry=aircraft.y(),rangeM=Math.hypot(xM,yM,z),azRad=Math.atan2(yM,xM),elRad=Math.atan2(z,Math.hypot(xM,yM)),ce=Math.cos(elRad);return {x:rx+metersToWorld(xM),y:ry+metersToWorld(yM),z,rangeM,azRad,elRad,radialMps:-250,radialVelSigmaMps:2,rangeSigmaM:10,azSigmaDeg:.05,elSigmaDeg:.1,quality:.9,sensorXWorld:rx,sensorYWorld:ry,sensorZM:0,sensorVxMps:0,sensorVyMps:0,sensorVzMps:0,losUx:ce*Math.cos(azRad),losUy:ce*Math.sin(azRad),losUz:Math.sin(elRad),source:'SPQ9B_AIR',domainEvidence:{air:.9,missile:.1,surface:0}};}
  function file(p){let tr=updateSensorTrackMeasurement(null,p,{source:'SPY1DV_SEARCH_HORIZON',taskType:'SEARCH_HORIZON'});if(tr)for(let j=0;j<4;j++)updateSensorTrackMeasurement(tr.trackId,p,{source:'SPY1DV_SEARCH_HORIZON',taskType:'SEARCH_HORIZON'});return tr;}
  const p1=plot(-200),p2=plot(200),t1=file(p1),t2=file(p2);
  checks.nativeFixturesCreated=!!t1&&!!t2&&t1.confirmed&&t2.confirmed;
  if(t1&&t2){
    const input=[{plot:p1,pd:.9,panel:0},{plot:p2,pd:.9,panel:0}],selection=__TRACK_C__.spqAssignments(input);
    detail.separated=selection.pairs.map(p=>({i:p.i,id:p.id,nis:p.nis}));
    checks.separateObjectsOneToOne=selection.pairs.length===2&&new Set(selection.pairs.map(p=>p.id)).size===2&&selection.heldPlots.size===0;
    const hits=[t1.sensorHits,t2.sensorHits],n=tracks.size;spq9bAcceptAnonymousPlotsV34(input);
    checks.spyPreferredNoIndependentHit=t1.sensorHits===hits[0]&&t2.sensorHits===hits[1]&&tracks.size===n;
  }
  tracks.clear();const equal=plot(0),a=file(equal),b=file(equal);
  const tie=__TRACK_C__.spqAssignments([{plot:equal,pd:.9,panel:0}]);
  detail.tie={heldPlots:[...tie.heldPlots],heldTracks:[...tie.heldTracks]};
  checks.exactTieConservativeHold=tie.pairs.length===0&&tie.heldPlots.has(0)&&tie.heldTracks.size===2;
  const n=tracks.size,accepted=spq9bAcceptAnonymousPlotsV34([{plot:equal,pd:.9,panel:0}]);
  checks.activeHoldDoesNotInitiate=__TRACK_C__.mode==='SHADOW'?accepted===1:accepted===0&&tracks.size===n;
  // Truth poison is never an input to the observational solver.
  let poisonReads=0;Object.defineProperty(equal,'truthRef',{get(){poisonReads++;throw Error('TRUTH_READ');}});
  __TRACK_C__.spqAssignments([{plot:equal,pd:.9,panel:0}]);checks.truthPoisonReadsZero=poisonReads===0;
  // Actual native alias integration: ambiguous predecessors cannot transfer BDA/FCS.
  tracks.clear();const aliasTrack=file(plot(0)),control=wip118ControlState,
    oldAssessments=[...control.assessments],oldAccel=[...control.accel],oldAliasLog=control.aliasLog.slice(),
    oldReservation=[...SPG62_RESERVATION_STATE],oldPlanStep=SPG62_RESERVATION_META.lastPlanStep;
  control.assessments.clear();control.accel.clear();control.aliasLog.length=0;
  const oldId=-90101,otherOldId=-90102,si=wip118TrackStateSI(aliasTrack),
    lost=()=>({state:'LOST',lostAgeS:0,everEngaged:true,bdaEvent:{evidence:'FUZE_DETONATION',fixture:true},lastObservation:{si:{...si},cov:{posSigmaM:30,altSigmaM:30,velSigmaMps:10},classification:'ASM',trackNumber:oldId,trackMetadata:{identity:'HOSTILE'}}});
  control.assessments.set(oldId,lost());control.assessments.set(otherOldId,lost());
  SPG62_RESERVATION_STATE.set(oldId,{targetId:oldId,fixture:true});
  let inherited=wip121TryAliasReacquire(aliasTrack.trackId,aliasTrack);
  checks.nativeAmbiguousAliasModeContract=__TRACK_C__.mode==='SHADOW'?!!inherited:inherited===null&&!control.assessments.has(aliasTrack.trackId)&&SPG62_RESERVATION_STATE.get(oldId)?.targetId===oldId;
  if(__TRACK_C__.mode==='ACTIVE'){
    control.assessments.delete(otherOldId);const originalIdentity=aliasTrack.identity,originalAuthority=aliasTrack.engagementAuthority;
    inherited=wip121TryAliasReacquire(aliasTrack.trackId,aliasTrack);
    checks.nativeUniqueAliasFcsTransfer=!!inherited&&SPG62_RESERVATION_STATE.get(aliasTrack.trackId)?.targetId===aliasTrack.trackId;
    checks.nativeAliasNoIdentityAuthorityCopy=aliasTrack.identity===originalIdentity&&aliasTrack.engagementAuthority===originalAuthority;
    control.assessments.clear();control.assessments.set(oldId,lost());SPG62_RESERVATION_STATE.set(oldId,{targetId:oldId,fixture:true});aliasTrack._operatorIdentity='FRIEND';aliasTrack.identity='FRIEND';
    inherited=wip121TryAliasReacquire(aliasTrack.trackId,aliasTrack);
    checks.nativeProtectedAliasNoFcsTransfer=inherited===null&&control.assessments.has(oldId)&&!control.assessments.has(aliasTrack.trackId);
  }
  control.assessments.clear();for(const[k,v]of oldAssessments)control.assessments.set(k,v);control.accel.clear();for(const[k,v]of oldAccel)control.accel.set(k,v);control.aliasLog.length=0;control.aliasLog.push(...oldAliasLog);
  SPG62_RESERVATION_STATE.clear();for(const[k,v]of oldReservation)SPG62_RESERVATION_STATE.set(k,v);SPG62_RESERVATION_META.lastPlanStep=oldPlanStep;
  tracks.clear();for(const[id,tr]of saved)tracks.set(id,tr);
  const native=__CORE_SELFTEST_FAILURES__;
  checks.nativeCoreZero=native.length===0;
  return {schema:'AEGIS_TRACK_C_NATIVE_CONTRACT_1',mode:__TRACK_C__.mode,checks,detail,core:native,pass:Object.values(checks).every(Boolean)};
}};
