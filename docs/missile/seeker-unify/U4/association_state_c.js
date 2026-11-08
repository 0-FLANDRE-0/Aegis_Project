// SEEKER_UNIFY_U4 Commit C — common anonymous association and state engine.
//
// Weapon front ends retain physical truth, their existing RNG handles and
// weapon-specific scoring/gates.  Only anonymous numeric scores and each
// missile's local state cross this boundary.  The audit object below is
// diagnostic telemetry, never a tactical state owner.
const SEEKER_U4_COMMON_MODE_C='__MODE__';
const SEEKER_U4_COMMON_PROFILES_C=Object.freeze({
  ASM:Object.freeze({association:'ANONYMOUS_MAX_SCORE',state:'ASM_HOJ_ACQUIRE_HOOK',hooks:Object.freeze(['HOJ','RF_EKF','INS'])}),
  HARPOON:Object.freeze({association:'ANONYMOUS_MIN_SCORE',state:'HARPOON_ROUTE_INS_HOOK',hooks:Object.freeze(['ROUTE_PLAN_PRIOR','INS_MEMORY','RF_TRACK'])}),
  SARH:Object.freeze({association:'ANONYMOUS_MAX_SCORE',state:'COMMON_RF_STATE',hooks:Object.freeze(['ILLUMINATION','BISTATIC_LOS'])}),
  ARH:Object.freeze({association:'ANONYMOUS_MAX_SCORE',state:'COMMON_RF_STATE',hooks:Object.freeze(['SARH_ARH_SOURCE_ARBITER'])}),
  RAM:Object.freeze({association:'ANONYMOUS_ANGULAR_GATE',state:'COMMON_ANGULAR_STATE',hooks:Object.freeze(['MEM','PASSIVE_RF','PASSIVE_IR'])})
});
const SEEKER_U4_COMMON_AUDIT_C={associationCalls:0,stateCalls:0,policyCalls:0,associationComparisons:0,associationMismatches:0,
  stateComparisons:0,stateMismatches:0,invalidScores:0,truthFieldViolations:0,rngConsumed:0,
  families:{ASM:0,HARPOON:0,SARH:0,ARH:0,RAM:0},events:{VALID_MEASUREMENT:0,HIT_ACCUMULATION:0,MISS_COAST:0,REACQUIRE:0,
    GIMBAL_LOS_ILLUMINATION_SIGNAL_LOSS:0,TIMEOUT_LOST_OFF:0,DESTROY_RETIRE:0}};
function seekerU4FamilyC(family){const f=String(family??'').toUpperCase();if(!SEEKER_U4_COMMON_PROFILES_C[f])throw new Error('SEEKER_U4_C_UNKNOWN_FAMILY:'+f);return f;}
function seekerU4FiniteScoreC(value){const n=Number(value);if(!Number.isFinite(n)){SEEKER_U4_COMMON_AUDIT_C.invalidScores++;return null;}return n;}
function seekerU4LegacyScoreIndexC(scores,direction){
  if(!scores.length)return -1;
  const rows=scores.map((score,index)=>({score:Number(score),index}));
  rows.sort(direction==='MIN'?(a,b)=>a.score-b.score:(a,b)=>b.score-a.score);
  return rows[0].index;
}
function seekerU4CommonScoreIndexC(scores,direction){
  if(!scores.length)return -1;let best=0,bestScore=seekerU4FiniteScoreC(scores[0]);
  for(let i=1;i<scores.length;i++){
    const q=seekerU4FiniteScoreC(scores[i]);
    // All existing weapon scores are finite.  Preserve first-in stable tie
    // ownership; an invalid score remains ordered as the legacy stable sort.
    if(q==null||bestScore==null)continue;
    if((direction==='MIN'&&q<bestScore)||(direction!=='MIN'&&q>bestScore)){best=i;bestScore=q;}
  }
  return best;
}
function seekerU4SelectIndexC(family,scores,direction){
  const f=seekerU4FamilyC(family),dir=direction==='MIN'?'MIN':'MAX',anonymous=Array.from(scores??[],Number);
  SEEKER_U4_COMMON_AUDIT_C.associationCalls++;SEEKER_U4_COMMON_AUDIT_C.associationComparisons++;SEEKER_U4_COMMON_AUDIT_C.families[f]++;
  const legacy=seekerU4LegacyScoreIndexC(anonymous,dir),common=seekerU4CommonScoreIndexC(anonymous,dir);
  if(legacy!==common)SEEKER_U4_COMMON_AUDIT_C.associationMismatches++;
  return SEEKER_U4_COMMON_MODE_C==='ACTIVE'?common:legacy;
}
function seekerU4StateSnapshotC(state){
  const s=state&&typeof state==='object'?state:{};
  const keys=['mode','state','valid','trackValid','acquireHits','acquireStrongHits','reacquireHits','lockCount','missAgeS','missedS','lastHitAgeS','measAgeS','quality','confidence','trackStableAgeS'];
  const out={};for(const key of keys){const value=s[key];if(value==null||typeof value==='string'||typeof value==='boolean'||Number.isFinite(Number(value)))out[key]=value??null;}
  return out;
}
function seekerU4StateEqualC(a,b){return JSON.stringify(seekerU4StateSnapshotC(a))===JSON.stringify(seekerU4StateSnapshotC(b));}
function seekerU4RecordTransitionC(family,before,after,event={}){
  const f=seekerU4FamilyC(family),bm=String(before?.mode??before?.state??''),am=String(after?.mode??after?.state??'');
  SEEKER_U4_COMMON_AUDIT_C.stateCalls++;SEEKER_U4_COMMON_AUDIT_C.families[f]++;
  if(event.accepted)SEEKER_U4_COMMON_AUDIT_C.events.VALID_MEASUREMENT++;
  if((after?.acquireHits??0)>(before?.acquireHits??0)||(after?.reacquireHits??0)>(before?.reacquireHits??0)||(after?.lockCount??0)>(before?.lockCount??0))SEEKER_U4_COMMON_AUDIT_C.events.HIT_ACCUMULATION++;
  if(am==='COAST'&&bm!=='COAST')SEEKER_U4_COMMON_AUDIT_C.events.MISS_COAST++;
  if((am==='REACQUIRE'&&bm!=='REACQUIRE')||(am==='TRACK'&&(bm==='COAST'||bm==='REACQUIRE')))SEEKER_U4_COMMON_AUDIT_C.events.REACQUIRE++;
  if(event.signalAvailable===false||event.illuminationAvailable===false||event.gimbalAvailable===false||event.losAvailable===false)SEEKER_U4_COMMON_AUDIT_C.events.GIMBAL_LOS_ILLUMINATION_SIGNAL_LOSS++;
  if(['LOST','OFF','SEARCH'].includes(am)&&['TRACK','COAST','REACQUIRE','ACQUIRE'].includes(bm))SEEKER_U4_COMMON_AUDIT_C.events.TIMEOUT_LOST_OFF++;
  if(event.retired||event.destroyed)SEEKER_U4_COMMON_AUDIT_C.events.DESTROY_RETIRE++;
}
function seekerU4RunPolicyC(family,stateProvider,policy,event={}){
  const f=seekerU4FamilyC(family),before=seekerU4StateSnapshotC(stateProvider?.());
  SEEKER_U4_COMMON_AUDIT_C.policyCalls++;const result=policy();const after=seekerU4StateSnapshotC(stateProvider?.());
  seekerU4RecordTransitionC(f,before,after,event);return result;
}
function seekerU4SarhStateC(s,accepted,period,hasIll,p){
  const before=seekerU4StateSnapshotC(s);
  if(accepted){
    s.missAgeS=0;s.lastHitAgeS=0;
    if(s.mode==='SEARCH'||s.mode==='LOST'){s.mode='ACQUIRE';s.acquireHits=1;s.reacquireHits=0;s.trackStableAgeS=0;}
    else if(s.mode==='ACQUIRE'){s.acquireHits=(s.acquireHits??0)+1;if(s.acquireHits>=p.acquireHits){s.mode='TRACK';s.acquireHits=0;s.reacquireHits=0;s.trackStableAgeS=0;}}
    else if(s.mode==='COAST'||s.mode==='REACQUIRE'){s.mode='REACQUIRE';s.reacquireHits=(s.reacquireHits??0)+1;if(s.reacquireHits>=p.reacquireHits){s.mode='TRACK';s.reacquireHits=0;s.trackStableAgeS=0;}}
    else s.mode='TRACK';
  }else{
    s.lastHitAgeS+=period;s.missAgeS+=period;if(s.mode==='ACQUIRE')s.acquireHits=0;if(s.mode==='REACQUIRE')s.reacquireHits=0;
    if(!hasIll&&(s.mode==='SEARCH'||s.mode==='ACQUIRE')){s.mode='SEARCH';s.acquireHits=0;}
    else if(s.mode==='ACQUIRE'&&s.missAgeS>.45){s.mode='SEARCH';s.acquireHits=0;s._kfX=null;s._kfP=null;s.trackValid=false;}
    else if(s.mode==='TRACK'&&s.missAgeS>p.coastAfterS){s.mode='COAST';s.trackStableAgeS=0;}
    else if(s.mode==='COAST'){
      if(!hasIll&&s.missAgeS>p.lostAfterS){s.mode='LOST';s.acquireHits=0;s.reacquireHits=0;s._kfX=null;s._kfP=null;s.trackValid=false;s.trackStableAgeS=0;}
      else if(hasIll&&s.missAgeS>p.reacquireAfterS){s.mode='REACQUIRE';s.reacquireHits=0;}
    }else if(s.mode==='REACQUIRE'&&s.missAgeS>p.lostAfterS){s.mode='LOST';s.acquireHits=0;s.reacquireHits=0;s._kfX=null;s._kfP=null;s.trackValid=false;s.trackStableAgeS=0;}
  }
  seekerU4RecordTransitionC('SARH',before,s,{accepted,illuminationAvailable:hasIll,signalAvailable:hasIll});return s;
}
function seekerU4ArhStateC(s,accepted,period,active,p){
  const before=seekerU4StateSnapshotC(s);
  if(!active){s.mode='OFF';s.acquireHits=0;s.reacquireHits=0;s.missAgeS=999;s.trackValid=false;s._kfX=null;s._kfP=null;}
  else if(accepted){s.missAgeS=0;s.lastHitAgeS=0;if(s.mode==='OFF'||s.mode==='SEARCH'||s.mode==='LOST'){s.mode='ACQUIRE';s.acquireHits=1;}
    else if(s.mode==='ACQUIRE'){s.acquireHits++;if(s.acquireHits>=p.acquireHits){s.mode='TRACK';s.acquireHits=0;}}
    else if(s.mode==='COAST'||s.mode==='REACQUIRE'){s.mode='REACQUIRE';s.reacquireHits++;if(s.reacquireHits>=p.reacquireHits){s.mode='TRACK';s.reacquireHits=0;}}
    else s.mode='TRACK';
  }else{s.lastHitAgeS+=period;s.missAgeS+=period;if(s.mode==='OFF')s.mode='SEARCH';else if(s.mode==='ACQUIRE'&&s.missAgeS>.34){s.mode='SEARCH';s.acquireHits=0;s._kfX=null;s._kfP=null;s.trackValid=false;}
    else if(s.mode==='TRACK'&&s.missAgeS>p.coastAfterS)s.mode='COAST';else if(s.mode==='COAST'&&s.missAgeS>p.reacquireAfterS)s.mode='REACQUIRE';
    else if(s.mode==='REACQUIRE'&&s.missAgeS>p.lostAfterS){s.mode='LOST';s.acquireHits=0;s.reacquireHits=0;s._kfX=null;s._kfP=null;s.trackValid=false;}}
  seekerU4RecordTransitionC('ARH',before,s,{accepted,signalAvailable:active});return s;
}
function seekerU4RamStateC(tr,meas,dt,cfg){
  const before=seekerU4StateSnapshotC(tr);ramPredictAngularTrack(tr,dt);
  if(!meas){tr.quality=Math.max(0,(tr.quality??0)-.55*dt);if(tr.measAgeS>(cfg.coastS??.3)){tr.valid=false;tr.state='SEARCH';}else if(tr.valid)tr.state='COAST';seekerU4RecordTransitionC('RAM',before,tr,{accepted:false,signalAvailable:false});return tr;}
  const ia=angNorm(meas.azRad-tr.azRad),ie=meas.elRad-tr.elRad,gate=deg(tr.valid?(cfg.gateTrackDeg??3):(cfg.gateAcquireDeg??8));
  if(tr.valid&&Math.hypot(ia,ie)>gate){tr.quality=Math.max(0,tr.quality-.10);tr.state='COAST';seekerU4RecordTransitionC('RAM',before,tr,{accepted:false,gimbalAvailable:false});return tr;}
  const md=Math.max(.015,Math.min(.15,tr.measAgeS<900?tr.measAgeS:(cfg.frameS??.03)));
  if(!tr.valid){tr.azRad=meas.azRad;tr.elRad=meas.elRad;tr.azRate=meas.azRateSeed??0;tr.elRate=meas.elRateSeed??0;tr.valid=true;}
  else{const a=cfg.alpha??.72,b=cfg.beta??.20;tr.azRad=angNorm(tr.azRad+a*ia);tr.elRad=clamp(tr.elRad+a*ie,deg(-89),deg(89));tr.azRate+=b*ia/md;tr.elRate+=b*ie/md;}
  tr.ageS=0;tr.measAgeS=0;tr.quality=clamp(tr.quality+.12+.25*(meas.quality??.5),0,1);tr.lastSignal=meas.signal??0;tr.lastExtentRad=meas.extentRad??0;tr.lastSnr=meas.snr??0;
  tr.lastCompositeCount=meas.compositeCount??1;tr.lastElementIndex=meas.elementIndex??null;tr.lastScanPhaseRad=meas.scanPhaseRad??tr.lastScanPhaseRad??null;tr.lastInnovationDeg=rad2deg(Math.hypot(ia,ie));tr.state=tr.quality>(cfg.acquireQ??.45)?'TRACK':'ACQUIRE';
  seekerU4RecordTransitionC('RAM',before,tr,{accepted:true,signalAvailable:true});return tr;
}
function seekerU4ShadowStateC(family,real,shadow,legacyResult,event={}){
  SEEKER_U4_COMMON_AUDIT_C.stateComparisons++;if(!seekerU4StateEqualC(real,shadow))SEEKER_U4_COMMON_AUDIT_C.stateMismatches++;
  return legacyResult;
}
function seekerU4SyntheticMatrixC(){
  const assoc={max:seekerU4CommonScoreIndexC([1,5,5,2],'MAX')===1,min:seekerU4CommonScoreIndexC([3,-1,-1,4],'MIN')===1,empty:seekerU4CommonScoreIndexC([],'MAX')===-1};
  const sp={acquireHits:2,reacquireHits:2,coastAfterS:.2,reacquireAfterS:.4,lostAfterS:.8},sarh={mode:'SEARCH',acquireHits:0,reacquireHits:0,missAgeS:999,lastHitAgeS:999,trackStableAgeS:0,trackValid:true,_kfX:{},_kfP:{}};
  seekerU4SarhStateC(sarh,true,.1,true,sp);seekerU4SarhStateC(sarh,true,.1,true,sp);const sarhTrack=sarh.mode==='TRACK';seekerU4SarhStateC(sarh,false,.3,true,sp);const sarhCoast=sarh.mode==='COAST';seekerU4SarhStateC(sarh,false,.2,true,sp);const sarhReacquire=sarh.mode==='REACQUIRE';seekerU4SarhStateC(sarh,true,.1,true,sp);seekerU4SarhStateC(sarh,true,.1,true,sp);const sarhReacquired=sarh.mode==='TRACK';seekerU4SarhStateC(sarh,false,.3,true,sp);seekerU4SarhStateC(sarh,false,.6,false,sp);const sarhLost=sarh.mode==='LOST';
  const ap={acquireHits:2,reacquireHits:2,coastAfterS:.2,reacquireAfterS:.4,lostAfterS:.8},arh={mode:'SEARCH',acquireHits:0,reacquireHits:0,missAgeS:999,lastHitAgeS:999,trackValid:true,_kfX:{},_kfP:{}};seekerU4ArhStateC(arh,false,.1,false,ap);const arhOff=arh.mode==='OFF'&&!arh.trackValid;
  const cfg={coastS:.3,gateTrackDeg:3,gateAcquireDeg:8,frameS:.03,alpha:.72,beta:.2,acquireQ:.45},r1={valid:false,azRad:0,elRad:0,azRate:0,elRate:0,quality:0,ageS:999,measAgeS:999,state:'SEARCH'},r2={...r1};
  seekerU4RamStateC(r1,{azRad:.01,elRad:.01,quality:1},.02,cfg);const independent=r1!==r2&&!r2.valid&&r1.valid;
  const retired={mode:'TRACK'};seekerU4RunPolicyC('ASM',()=>retired,()=>{retired.mode='OFF';},{destroyed:true});
  return Object.freeze({schema:'AEGIS_SEEKER_UNIFY_U4_C_MATRIX_1',assoc,sarhTrack,sarhCoast,sarhReacquire,sarhReacquired,sarhLost,arhOff,independent,
    pass:Object.values(assoc).every(Boolean)&&sarhTrack&&sarhCoast&&sarhReacquire&&sarhReacquired&&sarhLost&&arhOff&&independent});
}
function seekerU4ContractAuditC(){
  const source=[seekerU4SelectIndexC,seekerU4RunPolicyC,seekerU4SarhStateC,seekerU4ArhStateC,seekerU4RamStateC].map(String).join('\n'),
    forbidden=/(entityId|targetId|profileId|faction|hostile|truthObject|truthRef|physicalId)/;
  return Object.freeze({schema:'AEGIS_SEEKER_UNIFY_U4_C_CONTRACT_AUDIT_1',anonymousDecisionSource:!forbidden.test(source),rngCalls:/\b(simRandom|randn|Math\.random)\s*\(/.test(source),
    saveSchemaChanged:false,mutableTacticalSingleton:false,perWeaponStateArgument:true,pass:!forbidden.test(source)&&!/\b(simRandom|randn|Math\.random)\s*\(/.test(source)});
}
function seekerU4SnapshotC(){return Object.freeze({schema:'AEGIS_SEEKER_UNIFY_U4_C_SNAPSHOT_1',mode:SEEKER_U4_COMMON_MODE_C,profiles:SEEKER_U4_COMMON_PROFILES_C,
  audit:JSON.parse(JSON.stringify(SEEKER_U4_COMMON_AUDIT_C)),rngConsumedByCommonLayer:false,truthOutput:false,mutableTacticalSingleton:false,saveSchemaChanged:false});}
window.__SEEKER_U4_C__=Object.freeze({schema:'AEGIS_SEEKER_UNIFY_U4_C_1',mode:SEEKER_U4_COMMON_MODE_C,profiles:SEEKER_U4_COMMON_PROFILES_C,
  snapshot:seekerU4SnapshotC,syntheticMatrix:seekerU4SyntheticMatrixC,contractAudit:seekerU4ContractAuditC,
  selectIndex:(family,scores,direction)=>seekerU4SelectIndexC(family,scores,direction),stateSnapshot:seekerU4StateSnapshotC});
