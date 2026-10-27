function surfaceMissileReleaseAssessmentWip13C4(tr,weapon,options={}){
  const policy=surfaceMissileWeaponPolicyWip13C4(weapon),key=policy?.weaponKey??surfaceMissileVariantKeyWip15C(weapon),mode=String(options.mode??(typeof engagementControlMode==='string'?engagementControlMode:'MANUAL')).toUpperCase(),identity=normalizeTrackOperatorIdentityA3(tr?._operatorIdentity),authority=surfaceMissileIdentityPolicyWip13C4(identity,mode,options.automatic===true),base={schema:'AEGIS_SURFACE_MISSILE_RELEASE_CANDIDATE_V48_WIP13C4',weaponKey:key,mode,identity,liveLaunchEnabled:false,truthUsed:false};
  if(!policy)return {...base,ok:false,reason:'UNSUPPORTED_WEAPON'};if(!tr)return {...base,ok:false,reason:'NO_TRACK'};if(!authority.ok)return {...base,ok:false,reason:authority.reason,authority};
  const fcs=surfaceMissileFireControlQualityWip13C4(tr,key);if(!fcs.firePermitted)return {...base,ok:false,reason:fcs.reason??'FIRE_CONTROL_TRACK_QUALITY_INSUFFICIENT',authority,fireControl:fcs};
  const platform=options.platformSnapshot??surfaceMissilePlatformSnapshotWip13C4(key);if(!platform.ok)return {...base,ok:false,reason:platform.reason,authority,fireControl:fcs,platform};
  const capability=policy.requiresSpg62?surfaceMissileSpgFeasibilityWip13C4(tr,fcs,{emconActive:platform.emconActive}):surfaceMissileArhHandoffFeasibilityWip15C(tr,fcs);if(!capability.feasible)return {...base,ok:false,reason:capability.reason,authority,fireControl:fcs,platform,capability};
  return {...base,ok:true,reason:null,status:'RELEASE_CANDIDATE_ONLY',engagementMode:policy.mode,authority,fireControl:fcs,platform,capability};
}
function surfaceMissileFireControlQualityWip13C4(tr,weapon){
  const policy=surfaceMissileWeaponPolicyWip13C4(weapon),cfg=SURFACE_MISSILE_ENGAGEMENT_PROFILE_V48_WIP13C4.fireControl,bad=(reason,extra={})=>({schema:'AEGIS_SURFACE_MISSILE_FCS_V48_WIP13C4',weaponKey:policy?.weaponKey??surfaceMissileVariantKeyWip15C(weapon),status:'SURFACE_MISSILE_FCS_INSUFFICIENT',quality01:0,firePermitted:false,reason,truthUsed:false,...extra});
  if(!policy)return bad('UNSUPPORTED_WEAPON');const ready=surfaceMissileTrackReadinessWip13C4(tr,policy);if(!ready.ok)return bad(ready.reason,{trackReadiness:ready});
  const P=tr._kfP,rangeM=ready.rangeKm*1000,terminalRangeM=policy.terminalSupportRangeKm*1000,horizonS=clamp(Math.max(0,rangeM-terminalRangeM)/Math.max(1,policy.nominalMidcourseSpeedMps),policy.minPredictionHorizonS,policy.maxPredictionHorizonS),t2=horizonS*horizonS;
  const cxx=Math.max(1e-6,P[0]+horizonS*(P[3]+P[18])+t2*P[21]),cyy=Math.max(1e-6,P[7]+horizonS*(P[10]+P[25])+t2*P[28]),cxy=P[1]+horizonS*(P[4]+P[19])+t2*P[22],czz=Math.max(1e-6,P[14]+horizonS*(P[17]+P[32])+t2*P[35]),az=Math.atan2(tr.y-aircraft.y(),tr.x-aircraft.x()),along={x:Math.cos(az),y:Math.sin(az)},cross={x:-Math.sin(az),y:Math.cos(az)},projected=u=>Math.max(1e-6,u.x*u.x*cxx+2*u.x*u.y*cxy+u.y*u.y*cyy);
  const contributors=ready.contributors,fresh=cfg.contributorFreshS,order=['SPQ9B','SPY1DV','BRIDGEMASTER_E'],bestContributor=order.find(k=>(contributors[k]?.ageS??Infinity)<=Number(fresh[k]))??'COAST',bestAgeS=bestContributor==='COAST'?ready.measurementAgeS:Number(contributors[bestContributor]?.ageS??ready.measurementAgeS),floor=cfg.systematicFloor[bestContributor],maneuverProbability=clamp(Math.max(Number(tr._surfaceManeuverProbabilityWip13B10)||0,Number(tr._maneuverProbability)||0),0,1),freshLimit=bestContributor==='COAST'?0:Number(fresh[bestContributor]),coastAgeS=Math.max(0,ready.measurementAgeS-freshLimit),maneuverSigmaMps2=clamp(lerp(cfg.maneuverSigmaBaseMps2,cfg.maneuverSigmaMaxMps2,maneuverProbability)+coastAgeS*cfg.coastGrowthMps2PerS,cfg.maneuverSigmaBaseMps2,cfg.maneuverSigmaMaxMps2+cfg.maxMeasurementAgeS*cfg.coastGrowthMps2PerS),maneuverPositionSigmaM=.5*maneuverSigmaMps2*t2;
  const sigmaCrossM=Math.sqrt(projected(cross)+floor.positionCrossM**2+(horizonS*floor.velocityCrossMps)**2+maneuverPositionSigmaM**2),sigmaAlongM=Math.sqrt(projected(along)+floor.positionAlongM**2+(horizonS*floor.velocityAlongMps)**2+maneuverPositionSigmaM**2),sigmaVerticalM=Math.sqrt(czz+cfg.verticalSystematicFloorM**2),horizontal2SigmaM=2*Math.max(sigmaCrossM,sigmaAlongM),vertical2SigmaM=2*sigmaVerticalM,uncertaintyRatio=Math.max(horizontal2SigmaM/policy.acquisitionBasketRadiusM,vertical2SigmaM/policy.verticalBasketHalfM),basketMargin=1/Math.max(1e-9,uncertaintyRatio),familyConfidence={SPQ9B:1,SPY1DV:.88,BRIDGEMASTER_E:.72,COAST:.34}[bestContributor],freshnessConfidence=Math.exp(-bestAgeS/Math.max(.5,Number(fresh[bestContributor]??cfg.maxMeasurementAgeS))),quality01=clamp(Math.exp(-.48*uncertaintyRatio*uncertaintyRatio)*(.80+.20*familyConfidence*freshnessConfidence),0,1),status=uncertaintyRatio<=cfg.readyUncertaintyRatioMax?'SURFACE_MISSILE_FCS_READY':(uncertaintyRatio<=cfg.degradedUncertaintyRatioMax?'SURFACE_MISSILE_FCS_DEGRADED':'SURFACE_MISSILE_FCS_INSUFFICIENT'),firePermitted=status!=='SURFACE_MISSILE_FCS_INSUFFICIENT'&&quality01>=cfg.minFireQuality01;
  const state=tr._kfX&&tr._kfX.length===6?tr._kfX:[worldToMeters(tr.x),worldToMeters(tr.y),Number(tr.z)||0,worldSpeedToMps(tr.vx??0),worldSpeedToMps(tr.vy??0),Number(tr.vz)||0],observedExtent=surfaceTrackExtentSnapshotWip13B8(tr),aimHeightM=clamp(Number(observedExtent?.verticalHalfExtentM)*.42||6,3.5,12),handoffState={xM:state[0]+state[3]*horizonS,yM:state[1]+state[4]*horizonS,zM:Math.max(0,aimHeightM+state[5]*Math.min(horizonS,3)),vxMps:state[3],vyMps:state[4],vzMps:state[5]};
  return {schema:'AEGIS_SURFACE_MISSILE_FCS_V48_WIP13C4',weaponKey:policy.weaponKey,mode:policy.mode,status,quality01,firePermitted,reason:firePermitted?null:'FIRE_CONTROL_TRACK_QUALITY_INSUFFICIENT',rangeKm:ready.rangeKm,measurementAgeS:ready.measurementAgeS,predictionHorizonS:horizonS,bestContributor,contributorAgesS:Object.fromEntries(Object.entries(contributors).map(([k,v])=>[k,v.ageS])),sensorConfidence01:familyConfidence*freshnessConfidence,maneuverProbability,maneuverSigmaMps2,predictedHandoffSigmaM:{cross:sigmaCrossM,along:sigmaAlongM,vertical:sigmaVerticalM},acquisitionBasketM:{horizontalRadius:policy.acquisitionBasketRadiusM,verticalHalf:policy.verticalBasketHalfM},acquisitionBasketMargin:basketMargin,uncertaintyRatio,handoffState,aimHeightPolicy:'ANONYMOUS_OBSERVED_VERTICAL_EXTENT_OR_CONSERVATIVE_WATERLINE_OFFSET',truthUsed:false};
}
function surfaceMissileTrackReadinessWip13C4(tr,weaponPolicy){
  const bad=(reason,extra={})=>({ok:false,reason,truthUsed:false,...extra});if(!tr)return bad('NO_TRACK');
  if(!(tr.domain==='SURFACE'||tr.classification==='SURFACE'))return bad('NOT_SURFACE_TRACK');
  if(tr.confirmed!==true||tr.sensorDetected===false||tr.memActive||tr.reacquiring||trackLifecycleState(tr)==='DROP')return bad('SURFACE_TRACK_NOT_CONFIRMED');
  if(!tr._kfP||tr._kfP.length!==36||![tr.x,tr.y].every(Number.isFinite))return bad('SURFACE_TRACK_STATE_UNAVAILABLE');
  if(tr.trackId!=null&&tracks.get(tr.trackId)===tr&&wip121TargetSupportBlocked(tr.trackId,tr))return bad('TRACK_SUPPORT_BLOCKED');
  const contributors=surfaceSensorContributorSnapshotWip13B9(tr),ages=Object.values(contributors).map(q=>Number(q.ageS)).filter(Number.isFinite),measurementAgeS=weaponPolicy?.includeOffboardAgeF1&&tr.observationReportsC?Math.min(...ages,Math.max(0,Number(tr.sensorAge)||0)):(ages.length?Math.min(...ages):Math.max(0,Number(tr.sensorAge)||0)),limitS=SURFACE_MISSILE_ENGAGEMENT_PROFILE_V48_WIP13C4.fireControl.maxMeasurementAgeS;
  if(measurementAgeS>limitS)return bad('SURFACE_TRACK_COAST_EXPIRED',{measurementAgeS,limitS});
  const rangeKm=horizDistKm(aircraft.x(),aircraft.y(),tr.x,tr.y),minRangeKm=Number(weaponPolicy?.minRangeKm)||0,maxRangeKm=Number(weaponPolicy?.maxRangeKm)||Infinity;
  if(rangeKm<minRangeKm||rangeKm>maxRangeKm)return bad('SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE',{rangeKm,minRangeKm,maxRangeKm});
  return {ok:true,reason:null,measurementAgeS,rangeKm,contributors,truthUsed:false};
}
function surfaceMissilePlatformSnapshotWip13C4(weapon){
  const policy=surfaceMissileWeaponPolicyWip13C4(weapon),key=policy?.weaponKey??surfaceMissileVariantKeyWip15C(weapon),counts=getVlsCounts(),inventory=({SM2:counts.sm2Ready,SM2ER:counts.sm2erReady,SM6:counts.sm6Ready,ESSM:counts.essmReady}[key]??0),damage=getShipDamageEffects(),meta=policy?wip148PeekVlsLaunchMeta(key):null,frame=shipGameFrameV1(),local=meta?wip148VlsCellLocal(meta):null,launchPoint=local?frame.pointToWorld({x:local.xM,y:local.zM,z:local.deckM}):null,launchAxis=frame.vectorToWorld({x:0,y:0,z:1}),offline=shipEquipmentOfflineV1(),emcon=!!emconActive;
  let reason=null;if(!policy)reason='UNSUPPORTED_WEAPON';else if(offline)reason='SHIP_EQUIPMENT_OFFLINE';else if(!damage.vlsAvailable)reason='VLS_UNAVAILABLE';else if(damage.combatEff<.15)reason='COMBAT_SYSTEM_DAMAGE';else if(inventory<=0||!meta)reason='NO_READY_VLS_ROUND';else if(!launchPoint||launchPoint.z<=.1||launchAxis.z<=0)reason='VLS_LAUNCH_GEOMETRY_UNSAFE';else if(emcon&&policy.emconPolicy==='BLOCK_FIRE')reason='EMCON_BLOCKS_SURFACE_FIRE';
  return {schema:'AEGIS_SURFACE_MISSILE_PLATFORM_PREFLIGHT_V48_WIP13C4',weaponKey:key,ok:reason==null,reason,inventory,combatEff:damage.combatEff,vlsAvailable:!!damage.vlsAvailable,equipmentOffline:offline,emconActive:emcon,launchSection:meta?.section??null,truthUsed:false};
}
function networkMemberG(r){return !!r&&r.faction==='FRIENDLY'&&(r===ACTIVE_SHIP_RUNTIME||r.role==='ALLY')&&r.executionState!=='STATE_BOUND_INACTIVE';}
function networkProtectionG(r,tr){
  if(!networkMemberG(r)||!tr||!r.combatSystem.networkG)return null;
  const now=networkNowG();for(const file of r.combatSystem.networkG.files.values())if(file.localTrackId===tr.trackId){
    const q=[...file.sources.values()].find(q=>now-q.measuredAtS<=NETWORK_POLICY_G.freshS&&['FRIEND','NEUTRAL'].includes(q.identity));if(q)return q.identity;
  }return null;
}
function networkVlsGateG(r,trackId,options={}){
  if(!networkMemberG(r))return {ok:true};const n=prepareNetworkG(r),tr=observerC(r).tracks.get(Number(trackId)),now=networkNowG();
  if(tr&&networkProtectionG(r,tr))return {ok:false,reason:'NETWORK_PROTECTED_IDENTITY'};
  // Manual consent is not reassigned by the network. Native identity gates still apply.
  if(!options.automatic||!n.settings.enabled||!n.settings.shareTracks||!n.settings.cooperativeDefense)return {ok:true};
  if(!tr||networkLocalAgeG(tr)>NETWORK_POLICY_G.freshS)return {ok:false,reason:'LOCAL_FCS_REQUIRED'};
  const peers=networkConnectedPeersG(r).filter(p=>p.cooperative);if(!peers.length)return {ok:true,reason:'INDIVIDUAL_DEFENSE'};
  const th=ownerThreatRowD(r,tr);if(th.vr>0&&th.tti<=NETWORK_POLICY_G.emergencyS)return {ok:true,reason:'EMERGENCY_SELF_DEFENSE'};
  const lease=n.leases.get(tr.trackId);
  if(lease&&lease.untilS>=now){
    if(lease.primary===r.entityId)return {ok:true,reason:'ASSIGNED_PRIMARY'};
    const p=n.peers.get(lease.primary);if(p?.connected&&now-p.lastReceivedS<=NETWORK_POLICY_G.freshS){n.stats.withheld++;return {ok:false,reason:'NETWORK_ASSIGNED_PEER'};}
    return {ok:true,reason:'PEER_LINK_LOST'};
  }
  const since=n.waitSince.get(tr.trackId)??now;n.waitSince.set(tr.trackId,since);
  if(now-since<NETWORK_POLICY_G.waitS){n.stats.withheld++;return {ok:false,reason:'NETWORK_COORDINATION_PENDING'};}
  return {ok:true,reason:'NO_LEASE_LOCAL_DEFENSE'};
}
function updateTrackOperationalStateA3(tr,opts={}){
    if(!tr)return null;
    const prev=`${tr.identity??''}|${tr.threatStatus??''}|${tr.engagementAuthority??''}`;
    const cue=trackKinematicThreatCue(tr),classConf=clamp(Number(tr.classificationConfidence)||0,0,1),hits=Math.max(0,Number(tr.sensorHits)||0);
    const ownLaunch=harpoonTrackIdentityC(tr,ACTIVE_SHIP_RUNTIME);
    const operatorIdentity=ownLaunch?ownLaunch.identity:(heloFriendlyIffEvidenceE(tr)?'FRIEND':normalizeTrackOperatorIdentityA3(tr._operatorIdentity));
    const hostileIntent=tr.confirmed===true&&tr.classification==='ASM'&&classConf>=.58&&hits>=2&&cue.missileLike&&cue.highThreat;
    tr.identity=operatorIdentity!=='UNKNOWN'?operatorIdentity:(!ownLaunch&&hostileIntent?TRACK_A3_IDENTITY.ASSUMED_HOSTILE:TRACK_A3_IDENTITY.UNKNOWN);

    const assessment=opts.assessment??null;
    if(assessment?.state&&Object.prototype.hasOwnProperty.call(TRACK_A3_THREAT,String(assessment.state)))tr.threatStatus=String(assessment.state);
    else if(!tr.confirmed)tr.threatStatus=TRACK_A3_THREAT.UNASSESSED;
    else if(cue.highThreat)tr.threatStatus=TRACK_A3_THREAT.THREAT;
    else tr.threatStatus=TRACK_A3_THREAT.MONITOR;

    const mode=String(opts.mode??'MANUAL').toUpperCase(),explicitFcs=opts.fireControlReady;
    const fcs=explicitFcs==null?trackIsFireControlQuality(tr):!!explicitFcs;
    const protectedIdentity=!!networkProtectionG(ACTIVE_SHIP_RUNTIME,tr)||!!ownLaunch||tr.identity===TRACK_A3_IDENTITY.FRIEND||tr.identity===TRACK_A3_IDENTITY.NEUTRAL;
    const killAssessment=tr.threatStatus===TRACK_A3_THREAT.KILL_ASSESSMENT;
    const terminal=tr.threatStatus===TRACK_A3_THREAT.HARMLESS||tr.threatStatus===TRACK_A3_THREAT.DESTROYED;
    const liveTrack=tr.confirmed===true&&!tr.memActive&&!tr.reacquiring&&fcs;
    if(protectedIdentity||killAssessment||terminal||!liveTrack){tr.engagementAuthority=TRACK_A3_AUTHORITY.WITHHELD;tr._a3AuthorityReason=protectedIdentity?(ownLaunch?.reason??'PROTECTED_IDENTITY'):(killAssessment?'KILL_ASSESSMENT':(terminal?'NON_THREAT':'TRACK_NOT_READY'));}
    else if(mode==='AUTO'){
      const hostile=tr.identity===TRACK_A3_IDENTITY.HOSTILE||tr.identity===TRACK_A3_IDENTITY.ASSUMED_HOSTILE;
      if(hostile&&tr.threatStatus===TRACK_A3_THREAT.THREAT){tr.engagementAuthority=TRACK_A3_AUTHORITY.AUTO_AUTHORIZED;tr._a3AuthorityReason=tr.identity==='HOSTILE'?'OPERATOR_HOSTILE':'HOSTILE_INTENT';}
      else {tr.engagementAuthority=TRACK_A3_AUTHORITY.WITHHELD;tr._a3AuthorityReason=tr.identity==='UNKNOWN'?'IDENTITY_UNKNOWN':'THREAT_NOT_CONFIRMED';}
    }else if(mode==='SEMIAUTO'){tr.engagementAuthority=TRACK_A3_AUTHORITY.OPERATOR_RELEASE;tr._a3AuthorityReason='OPERATOR_RELEASE_REQUIRED';}
    else {tr.engagementAuthority=TRACK_A3_AUTHORITY.MANUAL_ONLY;tr._a3AuthorityReason='MANUAL_TRIGGER_REQUIRED';}
    const next=`${tr.identity}|${tr.threatStatus}|${tr.engagementAuthority}`;
    if(next!==prev){tr._a3StateRevision=(tr._a3StateRevision??0)+1;tr._a3StateChangedStep=typeof simStepCounter==='number'?simStepCounter:0;}
    return tr;
  }
function trackEngagementGateA3(trackId,opts={}){
    const networkTr=tracks.get(Number(trackId));if(networkTr&&networkProtectionG(ACTIVE_SHIP_RUNTIME,networkTr))return {ok:false,reason:'NETWORK_PROTECTED_IDENTITY'};
    const tr=tracks.get(Number(trackId));if(!tr)return {ok:false,reason:'NO_TRACK'};
    const mode=String(opts.mode??(typeof engagementControlMode==='string'?engagementControlMode:'MANUAL')).toUpperCase();
    updateTrackOperationalStateA3(tr,{mode,assessment:typeof wip118ControlState==='object'?wip118ControlState?.assessments?.get(Number(trackId)):null});
    if(opts.automatic===true){
      if(mode!=='AUTO')return {ok:false,reason:'MODE'};
      if(tr.identity==='UNKNOWN')return {ok:false,reason:'IDENTITY_UNKNOWN'};
      if(tr.threatStatus==='UNASSESSED')return {ok:false,reason:'UNASSESSED'};
      if(tr.engagementAuthority!=='AUTO_AUTHORIZED')return {ok:false,reason:'AUTHORITY_WITHHELD'};
      return {ok:true,reason:null,tr};
    }
    if(tr.identity==='FRIEND'||tr.identity==='NEUTRAL')return {ok:false,reason:'PROTECTED_IDENTITY'};
    if(!trackIsFireControlQuality(tr))return {ok:false,reason:'FCS_QUALITY'};
    return {ok:true,reason:null,tr};
  }
function classifyThreats(){
    const ax=aircraft.x(),ay=aircraft.y(),threats=[];
    for(const [id,tr] of tracks){
      if(!trackIsDisplayable(tr)) continue;
      const assessmentState=wip118ControlState?.assessments?.get(id)?.state??tr.threatStatus;
      if(assessmentState==='KILL_ASSESSMENT'||assessmentState==='DESTROYED'||assessmentState==='HARMLESS')continue;
      if(tr.memActive&&(tr.trackQuality??1)<0.2) continue;
      const dKm=worldToKm(dist(ax,ay,tr.x,tr.y)),alt=tr.z??0;
      const vr=closingSpeedKmh3(ax,ay,0,0,OWN_ALT_M,0,tr.x,tr.y,tr.vx,tr.vy,alt,tr.vz??0);
      const closureMps=Math.max(0,vr/3.6),tti=(dKm*1000)/Math.max(20,closureMps);
      const cue=trackKinematicThreatCue(tr),hasMissile=missiles.some(m=>!m.dead&&m.assignedTargetId===id);
      let type=tr.classification==='ASM'?'ASM':(tr.classification==='AIR'?'AIR':'UNKNOWN');
      let score=0,tag='UNK';
      if(type==='ASM'||cue.highThreat){
        score+=type==='ASM'?15:7;
        score+=clamp(1-tti/60,0,1)*40;
        score+=clamp(1-dKm/50,0,1)*20;
        score+=clamp(vr/2000,0,1)*15;
        score+=(alt<30?20:(alt<200?12:5));
        tag=type==='ASM'?(alt<30?'ASM-SK':(cue.speedMps>600?'ASM-SS':'ASM')):'MSL?';
      }else{
        const approaching=vr>50;
        if(approaching)score+=clamp(1-tti/120,0,1)*35;
        score+=clamp(1-dKm/80,0,1)*20;
        score+=clamp(vr/1500,0,1)*20;
        score+=(alt<500?15:(alt<2000?8:0));
        if(!approaching)score-=30;
        tag=type==='AIR'?(!approaching?'RET':(tti<30?'CLOSE':(vr>800?'FAST':(alt<500?'SKIM':'TRK')))):'UNK';
      }
      // Existing interceptor assignment reduces urgency, but never changes classification or truth state.
      if(hasMissile)score-=type==='ASM'||cue.highThreat?35:40;
      score*=lerp(0.72,1.0,clamp(tr.fireControlQuality??tr.trackQuality??0,0,1));
      threats.push({id,type,dKm,vr,alt,tti,score,tag,hasMissile,tr});
    }
    threats.sort((a,b)=>b.score-a.score);
    return threats;
  }
function vlsReleaseB2Snapshot(includeHistory=false){
    const s=ACTIVE_SHIP_RUNTIME.weapons.vlsReleaseB2;
    const step=simStepCounter,intervalS=s?.intervalS??VLS_RELEASE_B2_PROFILE.defaultIntervalS,nextStep=s?.nextStep??0;
    return {profileId:VLS_RELEASE_B2_PROFILE.id,step,intervalS,nextStep,remainingS:nextStep>step?(nextStep-step)*SIM_FIXED_DT:0,
      ready:!(s?.busy)&&step>=nextStep,lastStep:s?.lastStep??null,releaseCount:s?.releaseCount??0,
      history:includeHistory&&s?s.history.map(r=>({...r})):[],lastReject:s?.lastReject?{...s.lastReject}:null};
  }
function vlsReleaseB2CycleFeedback(manual=true){
    const q=vlsReleaseB2Snapshot();if(q.ready)return null;
    if(manual)notify(`VLS_CYCLE · ${q.remainingS.toFixed(2)} s — 발사 보류`);
    return {ok:false,reason:'VLS_CYCLE',remainingS:q.remainingS,nextStep:q.nextStep};
  }
function vlsReleaseB2SupportPreflight(weapon){
    const d=wip119WeaponDescriptor(weapon),tr=selectedLockId==null?null:tracks.get(selectedLockId);
    if(!d?.requiresIlluminator||!tr||surfaceTrackWip13C5(tr))return {ok:true,reservation:null};
    // Existing track-only planner, recomputed at actual release (not an old approval timestamp).
    const th=classifyThreats().find(t=>t.id===selectedLockId);
    if(!th)return {ok:false,reason:'FCS_QUALITY'};
    const pt={launchDelayS:0,interceptS:hardKillKinematicInterceptEstimate(th,d.profile).interceptS,futureThreat:th};
    const q=wip118ReservationAtNezPoint(th,weapon,pt,{provisionalReservations:[]});
    const ill=q.ok?SPG62_ILLUMINATORS.find(i=>i.id===q.illId):null;
    if(!q.ok||!ill||!spg62Operational(ill))return {ok:false,reason:'NO_CHANNEL'};
    return {ok:true,reservation:q.reservation?{...q.reservation}:null};
  }
function shipGameVlsReadyV1(type){
    if(shipEquipmentOfflineV1()){notify('발사 차단 · 함선 장비 정지');return false;}
    const meta=wip148PeekVlsLaunchMeta(type);if(!meta){notify('VLS 발사 차단 · 사용 가능한 셀 없음');return false;}const p=wip148VlsCellLocal(meta),f=shipGameFrameV1();
    if(f.pointToWorld({x:p.xM,y:p.zM,z:p.deckM}).z<=.1||f.vectorToWorld({x:0,y:0,z:1}).z<=0){notify('VLS 발사 차단 · 발사구 수몰 또는 뒤집힘');return false;}return true;
  }
function surfaceMissileReleaseGateWip13C4(trackId,weapon,options={}){return surfaceMissileReleaseAssessmentWip13C4(tracks.get(Number(trackId))??null,weapon,options);}
function surfaceSm2LiveReleaseGateWip13C5(trackId,options={}){
  const key=surfaceMissileVariantKeyWip15C(options.weaponKey??'SM2'),tr=tracks.get(Number(trackId))??null,base=surfaceMissileReleaseAssessmentWip13C4(tr,key,{...options,mode:String(options.mode??(typeof engagementControlMode==='string'?engagementControlMode:'MANUAL')).toUpperCase()});
  if(!base.ok)return {...base,schema:'AEGIS_LIVE_SURFACE_STANDARD_RELEASE_V48_WIP15C',weaponKey:key,liveLaunchEnabled:true,status:'RELEASE_INHIBITED'};
  return {...base,schema:'AEGIS_LIVE_SURFACE_STANDARD_RELEASE_V48_WIP15C',weaponKey:key,liveLaunchEnabled:true,status:'RELEASE_AUTHORIZED',engagementMode:base.engagementMode,truthUsed:false};
}
function surfaceEssmLiveReleaseGateWip13C6(trackId,options={}){
  const key=surfaceMissileVariantKeyWip15C(options.weaponKey??'ESSM'),base=surfaceMissileReleaseGateWip13C4(trackId,key,options);
  return {...base,schema:'AEGIS_LIVE_SURFACE_ARH_RELEASE_V48_WIP15C',weaponKey:key,liveLaunchEnabled:true,status:base.ok?'RELEASE_AUTHORIZED':'RELEASE_INHIBITED'};
}
function vlsReleaseStandardB1(opts={}){
    const ng=networkVlsGateG(ACTIVE_SHIP_RUNTIME,selectedLockId,opts);if(!ng.ok)return;
    const _requestedWeapon=String(opts.weaponType??'SM2').toUpperCase();
    const _weaponType=_requestedWeapon==='SM6'?'SM6':(_requestedWeapon==='SM2ER'?'SM2ER':'SM2');
    const _isSm2Er=_weaponType==='SM2ER',_isSm6=_weaponType==='SM6';
    const _profileId=_isSm6?'SM6_BLKIA_SIM':(_isSm2Er?'SM2ER_BLKIV_SIM':'SM2MR_BLKIIIA_SIM');
    const _weaponLabel=_isSm6?'SM-6 Block IA':(_isSm2Er?'SM-2ER Block IV':'SM-2MR Block IIIA');
    if(!shipGameVlsReadyV1(_weaponType))return;
    // VLS damage check
    const _vlsDmg = getShipDamageEffects();
    if(!_vlsDmg.vlsAvailable){
      notify('⚠ VLS 발사 불가 — 전력/발사관 피해!');
      return;
    }
    if(_vlsDmg.combatEff < 0.15){
      notify('⚠ 전투체계 심각 손상 — 사격통제 불가!');
      return;
    }

    // WIP13C5: surface release is a separate manual authority path. It must pass the
    // anonymous surface FCQ and reserve a usable SPG-62 window before a round is consumed.
    const _selectedPreflightTrack=selectedLockId!=null?tracks.get(selectedLockId):null;
    const _surfaceStandardSelected=surfaceTrackWip13C5(_selectedPreflightTrack);
    let _surfaceStandardRelease=null;
    if(_surfaceStandardSelected){
      _surfaceStandardRelease=_isSm6
        ?surfaceEssmLiveReleaseGateWip13C6(selectedLockId,{weaponKey:'SM6',mode:typeof engagementControlMode==='string'?engagementControlMode:'MANUAL',automatic:opts.automatic===true})
        :surfaceSm2LiveReleaseGateWip13C5(selectedLockId,{weaponKey:_weaponType,mode:typeof engagementControlMode==='string'?engagementControlMode:'MANUAL',automatic:opts.automatic===true});
      if(!_surfaceStandardRelease.ok){notify(`⚠ ${_weaponLabel} 대수상 발사 차단 — ${_surfaceStandardRelease.reason}`);return;}
    }

    // REPAIR-2 §5: SM-2 EMCON 정책 — SARH terminal은 함 조명 필수.
    // SM2_EMCON_POLICY: 'BLOCK_FIRE' | 'AUTO_RADIATE' (v1 profile 섹션에 선언)
    if(typeof emconActive !== 'undefined' && emconActive){
      if(SM2_EMCON_POLICY === 'BLOCK_FIRE'){
        notify('⚠ EMCON ON — SM-2 발사 차단 (SARH 조명 불가)');
        return;
      } else {
        toggleEmcon();  // AUTO_RADIATE: 발사 전 자동 방사
        notify('📡 SM-2 AUTO_RADIATE: EMCON 자동 해제');
      }
    }

  const ax = aircraft.x(), ay = aircraft.y();
  // SAM: aim toward locked target or cursor direction
  let initHeading;
  if(selectedLockId != null){
    const tr = tracks.get(selectedLockId);
    if(!_surfaceStandardRelease){
      if(!trackIsFireControlQuality(tr)){ notify('⚠ 사격통제 품질 트랙 없음'); return; }
      const a3Gate=trackEngagementGateA3(selectedLockId,{automatic:opts.automatic===true});
      if(!a3Gate.ok){notify(`⚠ SM-2 교전 차단 — ${trackA3ReasonKo(a3Gate.reason)}`);return;}
    }
    initHeading = Math.atan2(tr.y - ay, tr.x - ax);
  } else {
    initHeading = Math.atan2(lockCursor.y - ay, lockCursor.x - ax);
  }
  // WIP155: exact vertical launcher-relative launch + full ship inertial-velocity inheritance.
  // No target-directed horizontal seed is injected at spawn; pitchover belongs to the launch controller.

return {ok:true};
}
function vlsReleaseEssmB1(opts={}){
    const ng=networkVlsGateG(ACTIVE_SHIP_RUNTIME,selectedLockId,opts);if(!ng.ok)return;
    if(!shipGameVlsReadyV1('ESSM'))return;
    // VLS damage check
    const _vlsDmgE = getShipDamageEffects();
    if(!_vlsDmgE.vlsAvailable){
      notify('⚠ VLS 발사 불가 — 전력/발사관 피해!');
      return;
    }
    if(_vlsDmgE.combatEff < 0.15){
      notify('⚠ 전투체계 심각 손상 — 사격통제 불가!');
      return;
    }
    // WIP111 ESSM EMCON doctrine: Block 2 ARH terminal autonomy does not create an EMCON fire-control track.
    // Until an ESM/external-DL fire-control-quality track path exists, ESSM launch doctrine remains BLOCK_FIRE.
    if(emconActive && ESSM_EMCON_POLICY === 'BLOCK_FIRE'){ notify('EMCON 중 — 발사 불가'); return; }
    if(selectedLockId == null){ notify('락온 없음'); return; }

    const ax = aircraft.x(), ay = aircraft.y();
    const tr = tracks.get(selectedLockId);
    const surfaceSelected=surfaceTrackWip13C5(tr);
    const surfaceRelease=surfaceSelected?surfaceEssmLiveReleaseGateWip13C6(selectedLockId,{mode:engagementControlMode,automatic:opts.automatic===true}):null;
    if(surfaceRelease){
      if(!surfaceRelease.ok){notify(`⚠ ESSM 대수상 발사 차단 — ${surfaceRelease.reason}`);return;}
    }else{
      if(!trackIsFireControlQuality(tr)){notify('⚠ ESSM 사격통제 품질 트랙 없음');return;}
      const a3Gate=trackEngagementGateA3(selectedLockId,{automatic:opts.automatic===true});
      if(!a3Gate.ok){notify(`⚠ ESSM 교전 차단 — ${trackA3ReasonKo(a3Gate.reason)}`);return;}
    }


return {ok:true};
}
function vlsReleaseB2Request(weapon,opts,release){
    const s=ACTIVE_SHIP_RUNTIME.weapons.vlsReleaseB2;
    if(!s)throw new Error('VLS_RELEASE_STATE_UNINITIALIZED');
    const ng=networkVlsGateG(ACTIVE_SHIP_RUNTIME,selectedLockId,opts);if(!ng.ok){s.lastReject={reason:ng.reason,step:simStepCounter,weapon};return null;}
    const cycle=vlsReleaseB2CycleFeedback(!opts.automatic);
    if(cycle){s.lastReject={reason:cycle.reason,step:simStepCounter,weapon};return null;}
    // No asynchronous wait: request and commit happen in this tick. Original release path rechecks
    // FCQ/identity/EMCON/port/damage/cell and surface-SPG gates immediately before actual cell consumption.
    if(opts.automatic||opts.mode==='SEMIAUTO'){
      const reserve=wip119ReserveAvailable(weapon,1);
      if(!reserve.ok){s.lastReject={reason:'RESERVE',step:simStepCounter,weapon};return null;}
    }
    const support=vlsReleaseB2SupportPreflight(weapon);
    if(!support.ok){s.lastReject={reason:support.reason,step:simStepCounter,weapon};if(!opts.automatic)notify(`VLS 발사 보류 · ${support.reason}`);return null;}

return release();
}