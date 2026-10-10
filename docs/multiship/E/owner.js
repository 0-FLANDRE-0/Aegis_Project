// LIVE_CANONICAL: these declarations are inserted inside the existing owner closure.
const ciwsBullets=owner.weapons.executionD.bullets,SIM_TEST_INTERCEPT_HISTORY=[],
  WIP122_SM2_HANDOFF_MEMORY=new Map(),hardKillDoctrineState={previousOrderKeys:[]},
  WIP119_VLS_WEAPON_REGISTRY=Object.freeze(Object.fromEntries(Object.entries(ownerVlsRegistryE()).map(([key,definition])=>[key,Object.freeze({...definition,fire:(options={})=>launch({weapon:key,trackId:selectedLockId,...options})})])));
let wip118ControlState={assessments:new Map(),accel:new Map(),recommendations:[],previousOrderKeys:[],schedulerFrameIndex:-1,revision:0,lastStep:-1,lastBuildMs:0,lastAssessmentMs:0,interceptHistoryCursor:0,interceptSeenKeys:new Set(),recentInterceptEvents:[],aliasLog:[]},
  wip119AutonomyState={responses:new Map(),pending:null,lastFrame:-1,lastOwnedLockId:null,lastAction:null,lastBuildMs:0,candidateRows:[],fireLog:[],operatorFireLog:[],totalAutoRounds:{SM2:0,SM2ER:0,SM6:0,ESSM:0}},
  wip124SemiLockState={trackId:null,sinceS:-Infinity,lastDisplay:null};
const defenseE=owner.weapons.executionD.defenseE={schema:'AEGIS_OWNER_DEFENSE_E_1',mode:'AUTO',control:wip118ControlState,autonomy:wip119AutonomyState,closeIn:new Map(),closeInLog:[],lastStep:-1,ticks:0};
owner.combatSystem.engagementControl.defenseE=defenseE;
function setRadarHalfAngle(){} // Foreign designation has no player UI side effect.
function updateModeButtonLabel(){}
function trackDisplayLabelById(id){return 'T'+String(id);}
function hardKillTrackThreatScore(id){
  const tr=tracks.get(Number(id));if(!tr)return null;
  const th=ownerThreatRowD(owner,tr),cue=trackKinematicThreatCue(tr),cpa=wip118PredictTrackCPA(tr,wip118TrackAcceleration(id));
  const urgency=clamp(1-th.tti/60,0,1),proximity=clamp(1-th.dKm/50,0,1),closure=clamp(cue.closureMps/550,0,1),confidence=clamp(tr.fireControlQuality??0,0,1);
  return {trackId:Number(id),threatScore:(15+40*urgency+20*proximity+15*closure+(cue.altM<30?20:5))*confidence,ttcS:th.tti,cpaM:cpa?.cpaM??null,source:'OWNER_MEASURED_KINEMATICS',truthUsed:false};
}
function defenseGateE(id,options={}){
  const tr=tracks.get(Number(id));if(!tr)return {ok:false,reason:'NO_TRACK'};
  if(!tr.confirmed||tr.sensorDetected===false||!Number.isFinite(tr.sensorAge)||tr.sensorAge>2||tr.memActive||tr.reacquiring)return {ok:false,reason:'FCS_TRACK_STALE'};
  if(shipEquipmentOfflineV1())return {ok:false,reason:'SHIP_EQUIPMENT_OFFLINE'};
  if(options.automatic){
    if(defenseE.mode!=='AUTO'||engagementControlMode!=='AUTO')return {ok:false,reason:'AUTO_OFF'};
    if(emconActive)return {ok:false,reason:'EMCON_BLOCK'};
    if(tr.domain==='SURFACE'||tr.classification==='SURFACE')return {ok:false,reason:'SURFACE_ROE_REQUIRED'};
  }else if(!['HOSTILE','TRAINING_TARGET'].includes(normalizeTrackOperatorIdentityA3(tr._operatorIdentity)))return {ok:false,reason:'IDENTITY_WITHHELD'};
  return {ok:true};
}
function defenseStepE(){
  if(defenseE.lastStep===simStepCounter)throw Error('DEFENSE_DOUBLE_TICK');defenseE.lastStep=simStepCounter;defenseE.ticks++;
  engagementControlMode=defenseE.mode==='AUTO'?'AUTO':'MANUAL';
  updateWip118EngagementControl();updateWip119EngagementAutomation();
  hardKillDoctrineState.previousOrderKeys=[...wip118ControlState.previousOrderKeys];
}
function defenseModeE(mode){
  if(!['AUTO','HOLD'].includes(mode))return {ok:false,reason:'INVALID_DEFENSE_MODE'};
  defenseE.mode=mode;engagementControlMode=mode==='AUTO'?'AUTO':'MANUAL';
  if(mode==='HOLD'){wip119CancelPending('AUTO_OFF');defenseE.closeIn.clear();}
  wip119AutonomyState.lastFrame=-1;refreshTrackOperationalStatesA3(engagementControlMode);return {ok:true,mode};
}
function defenseCloseInE(){
  if(defenseE.mode!=='AUTO'){defenseE.closeIn.clear();return;}
  const ranks=wip118ThreatRows().filter(th=>wip118ControlState.assessments.get(th.id)?.state==='THREAT'&&trackEngagementGateA3(th.id,{automatic:true,mode:'AUTO'}).ok);
  for(const mount of ciws){
    if(mount.ammo<=(mount.type==='RAM'?HARD_KILL_DOCTRINE.ramReserveRounds:0)){defenseE.closeIn.delete(mount.id);continue;}
    const bank=c55Bank(mount),rows=ranks.filter(th=>th.dKm<=mount.engageRangeKm&&th.dKm>=(mount.minEngageKm??.1)&&hardKillMountGeometry(mount,th.tr).ok&&[...bank.files.values()].some(q=>q.cmsTrackId===th.id&&q.confirmed&&q.audit?.accepted&&!q.protectedIdentity&&q.st.valid&&q.st.localAgeS<CIWS_C55_POLICY.releaseFreshS));
    const th=rows[0];if(!th){defenseE.closeIn.delete(mount.id);continue;}
    const pending=defenseE.closeIn.get(mount.id),counts=hardKillExistingEngagementCounts(th.id);
    if(mount.type==='RAM'&&counts.RAM>0){defenseE.closeIn.delete(mount.id);continue;}
    // Only a fresh CMS file plus the mount's independent measured file grants consent.
    defenseE.closeIn.set(mount.id,{command:{trackId:th.id,weapon:mount.type==='RAM'?'RAM':'PHALANX',mountId:mount.id,automatic:true,mode:'AUTO'},mountId:mount.id,expiresStep:simStepCounter+1,issuedStep:pending?.command.trackId===th.id?pending.issuedStep:simStepCounter});
    mount.trackingTrackId=th.id;mount.cuedTarget=th.id;
  }
}
function defenseSnapshotOwnerE(){return {mode:defenseE.mode,ticks:defenseE.ticks,control:wip118ControlSnapshot(),autonomy:wip119AutonomySnapshot(),closeIn:[...defenseE.closeIn].map(([mountId,p])=>({mountId,trackId:p.command.trackId,issuedStep:p.issuedStep})),closeInLog:defenseE.closeInLog.map(q=>({...q})),truthUsed:false};}
