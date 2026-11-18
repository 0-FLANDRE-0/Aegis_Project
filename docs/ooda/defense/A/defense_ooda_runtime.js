// DEFENSE_OODA_A — owner-local, observation-only advisory provider.
// Every profile coefficient is SIM_TUNED_GAMEPLAY_NOT_REAL_CIC_SPEC.
// This layer owns no ROE, FCS/SPG, network lease, reserve, EMCON, release,
// weapon execution, or fixed-tick C55 RAM/Phalanx authority.
const DEFENSE_OODA_IMPLEMENTATION_MODE_A='__DEFENSE_OODA_MODE__';
const DEFENSE_OODA_STATE_SCHEMA_A='AEGIS_DEFENSE_OODA_STATE_A1';
const DEFENSE_OODA_STATE_REVISION_A=1;
const DEFENSE_OODA_PHASES_A=Object.freeze(['OBSERVE','ORIENT','DECIDE','READY']);
const DEFENSE_OODA_PROVIDER_VALUES_A=Object.freeze(['LEGACY_H1','DEFENSE_OODA_A']);
const DEFENSE_OODA_SOURCE_A='SIM_TUNED_GAMEPLAY_NOT_REAL_CIC_SPEC';
const DEFENSE_OODA_PRIORITY_POLICY_A=Object.freeze({
  source:DEFENSE_OODA_SOURCE_A,
  cpaBandsM:Object.freeze([300,1000,3000]),
  freshnessBandsS:Object.freeze([.5,2,5]),
  covarianceBandsM:Object.freeze([100,500,1500]),
  scoreRadix:10,
  policy:'LEXICOGRAPHIC_OBSERVED_ONLY'
});
const OODA_SALVO_POLICY_A1=Object.freeze({
  source:DEFENSE_OODA_SOURCE_A,
  allowedWeapons:Object.freeze(['SM2','SM2ER','SM6','ESSM','RAM','PHALANX']),
  minimum:0,maximum:4,nativeUpperBound:true,
  policy:'NATIVE_H1_UPPER_BOUND_MINUS_OWNER_LOCAL_LIVE_ENGAGEMENTS_UNLESS_REENGAGE_REQUIRED'
});

function defenseOodaProfileA(r){
  const q=r&&resolveShipProfile(r.profileId)?.defenseOodaA;
  return q&&q.schema==='AEGIS_DEFENSE_OODA_PROFILE_A1'?q:null;
}
function defenseOodaCountersA(){return {queued:0,evaluated:0,preempted:0,deferred:0,fallback:0,rejected:0,overflow:0};}
function defenseOodaNewStateA(r,step=simStepCounter){
  const p=defenseOodaProfileA(r);if(!p)return null;
  return {schema:DEFENSE_OODA_STATE_SCHEMA_A,revision:DEFENSE_OODA_STATE_REVISION_A,ownerEntityId:r.entityId,profileId:r.profileId,
    phase:'OBSERVE',queueSequence:0,rows:[],lastServiceStep:step,lastAcceptedInputStep:-1,lastAcceptedInputRevision:-1,
    lastCommand:null,capacity:{value:0,slots:0,reason:'NOT_EVALUATED'},diagnostics:defenseOodaCountersA(),migration:'NONE'};
}
function defenseOodaEnsureStateA(r){
  if(!defenseOodaProfileA(r))return null;
  const q=r.combatSystem.defenseOodaA;
  if(q?.schema===DEFENSE_OODA_STATE_SCHEMA_A&&q.ownerEntityId===r.entityId&&q.profileId===r.profileId)return q;
  const state=defenseOodaNewStateA(r);r.combatSystem.defenseOodaA=state;return state;
}
function defenseOodaFinite01A(v){return Number.isFinite(v)&&v>=0&&v<=1?v:null;}
function defenseOodaCapacityA(input,profile){
  const ship=input?.ship,crew=ship?.crew,combat=defenseOodaFinite01A(crew?.departments?.COMBAT?.availability),operations=defenseOodaFinite01A(crew?.departments?.OPERATIONS?.availability),damage=defenseOodaFinite01A(ship?.damage?.combatEff);
  if(ship?.equipmentOffline===true||crew?.combatUnavailable===true||['MISSION_KILL','LOST','SUNK'].includes(ship?.missionState)||['LOST','SUNK'].includes(ship?.afloatState))return {value:0,slots:0,reason:'COMBAT_UNAVAILABLE'};
  if(combat===null||operations===null||damage===null)return {value:0,slots:0,reason:'CAPACITY_INPUT_INVALID'};
  const crewBottleneck=Math.min(combat,operations),operationalFactor=Math.min(crewBottleneck,damage),value=Math.max(0,Math.min(1,operationalFactor*profile.modernizationFactor));
  if(value<profile.minimumOperationalCapacity)return {value,slots:0,reason:'BELOW_MINIMUM_OPERATIONAL_CAPACITY',crewBottleneck,damageFactor:damage};
  return {value,slots:Math.max(1,Math.floor(profile.baseConcurrentEvaluations*value+1e-12)),reason:'AVAILABLE',crewBottleneck,damageFactor:damage};
}
function defenseOodaPhaseStepsA(profile,capacity,phase){
  const key=phase==='OBSERVE'?'baseObserveSteps':phase==='ORIENT'?'baseOrientSteps':'baseDecisionSteps';
  return Math.ceil(profile[key]/Math.max(profile.minimumOperationalCapacity,capacity));
}
function defenseOodaBandA(value,bands,missing=bands.length+1){if(!Number.isFinite(value))return missing;for(let i=0;i<bands.length;i++)if(value<=bands[i])return i;return bands.length;}
function defenseOodaCovarianceSigmaA(track){
  const p=track?.measurement?.covariance;if(!Array.isArray(p)||p.length!==36)return null;
  const d=[p[0],p[7],p[14]].filter(Number.isFinite);return d.length===3?Math.sqrt(Math.max(0,...d)):null;
}
function defenseOodaPriorityTupleA(track,profile,stateRow=null,currentStep=0){
  const id=Number(track?.trackId),a=track?.assessment??{},ident=track?.identification??{},life=track?.lifecycle??{},eng=track?.engagements??{},ageSteps=stateRow?Math.max(0,currentStep-stateRow.enqueuedStep):0,
    authority=(ident.engagementAuthority==='AUTO_AUTHORIZED'||ident.engagementAuthority==='AUTHORIZED')?0:(ident.threatStatus==='THREAT'||a.state==='THREAT')?1:2,
    tgo=defenseOodaBandA(a.closureTgoS,profile.urgentTgoBandsS),cpa=defenseOodaBandA(a.cpaM,DEFENSE_OODA_PRIORITY_POLICY_A.cpaBandsM),
    reengage=a.reengageRequired?0:1,live=Math.min(9,Math.max(0,Number(a.liveEngagement)||0)),inbound=Number.isFinite(a.closureTgoS)&&a.closureTgoS>=0?0:1,
    freshness=defenseOodaBandA(track?.measurement?.ageS,DEFENSE_OODA_PRIORITY_POLICY_A.freshnessBandsS),coast=life.coasting||life.memory?1:0,
    covariance=defenseOodaBandA(defenseOodaCovarianceSigmaA(track),DEFENSE_OODA_PRIORITY_POLICY_A.covarianceBandsM),engagements=Math.min(9,Object.values(eng).reduce((n,v)=>n+(Number(v)||0),0)),
    aging=Math.min(9,Math.floor(ageSteps/profile.agingStepInterval));
  return [authority,tgo,cpa,reengage,Math.max(0,live-aging),inbound,freshness,coast,covariance,engagements,Number.isInteger(id)?Math.max(0,id):2147483647];
}
function defenseOodaTupleCompareA(a,b){for(let i=0;i<Math.max(a.length,b.length);i++){const d=(a[i]??0)-(b[i]??0);if(d)return d;}return 0;}
function defenseOodaScoreA(tuple){
  // Mixed-radix finite encoding. Ordering is established by tuple comparison;
  // the score merely preserves it for the unchanged command schema.
  let code=0;for(let i=0;i<tuple.length-1;i++)code=code*10+Math.min(9,Math.max(0,tuple[i]));
  return 1e12-code-Math.min(999999,tuple.at(-1)??999999)/1e6;
}
function defenseOodaEligibleA(track){
  if(!track||!Number.isInteger(track.trackId))return false;
  const c=track.identification?.classification,s=track.assessment?.state??track.identification?.threatStatus;
  return c==='ASM'||c==='MISSILE'||s==='THREAT'||s==='LOST';
}
function defenseOodaPriorityRowsA(input,state,profile){
  const byState=new Map(state.rows.map(q=>[q.trackId,q]));
  return input.tracks.filter(defenseOodaEligibleA).map(track=>{const tuple=defenseOodaPriorityTupleA(track,profile,byState.get(track.trackId),input.step);return {track,tuple,score:defenseOodaScoreA(tuple)};}).sort((a,b)=>defenseOodaTupleCompareA(a.tuple,b.tuple));
}
function defenseOodaAdvanceRowA(row,delta,profile,capacity,step,state){
  let left=Math.max(0,delta);while(left>0&&row.phase!=='READY'){
    const used=Math.min(left,row.remainingSteps);row.remainingSteps-=used;left-=used;
    if(row.remainingSteps>0)break;
    const index=DEFENSE_OODA_PHASES_A.indexOf(row.phase);row.phase=DEFENSE_OODA_PHASES_A[index+1];
    if(row.phase==='READY'){row.readyStep=step-left;row.slot=null;state.diagnostics.evaluated++;break;}
    row.remainingSteps=defenseOodaPhaseStepsA(profile,capacity,row.phase);
  }
}
function defenseOodaEstimateReadyStepA(row,profile,capacity,step){
  if(row.phase==='READY')return step;let n=row.remainingSteps,index=DEFENSE_OODA_PHASES_A.indexOf(row.phase);
  for(let i=index+1;i<3;i++)n+=defenseOodaPhaseStepsA(profile,capacity,DEFENSE_OODA_PHASES_A[i]);return step+n;
}
function defenseOodaAssignSlotsA(state,priorityRows,profile,capacity,inputStep){
  const byPriority=new Map(priorityRows.map((q,i)=>[q.track.trackId,{...q,index:i}])),active=state.rows.filter(q=>q.phase!=='READY'&&q.slot!==null);
  for(const row of active)if(row.slot>=capacity.slots)row.slot=null;
  const occupied=new Set(state.rows.filter(q=>q.phase!=='READY'&&q.slot!==null).map(q=>q.slot));
  const waiting=state.rows.filter(q=>q.phase!=='READY'&&q.slot===null&&byPriority.has(q.trackId)).sort((a,b)=>defenseOodaTupleCompareA(byPriority.get(a.trackId).tuple,byPriority.get(b.trackId).tuple)||a.sequence-b.sequence);
  while(occupied.size<capacity.slots&&waiting.length){const row=waiting.shift();let slot=0;while(occupied.has(slot))slot++;row.slot=slot;occupied.add(slot);}
  if(!waiting.length||!capacity.slots)return;
  const urgent=waiting[0],urgentTuple=byPriority.get(urgent.trackId).tuple,candidates=state.rows.filter(q=>q.phase!=='READY'&&q.slot!==null&&byPriority.has(q.trackId)).sort((a,b)=>defenseOodaTupleCompareA(byPriority.get(b.trackId).tuple,byPriority.get(a.trackId).tuple)||b.sequence-a.sequence),victim=candidates[0];
  if(victim&&urgentTuple[1]<byPriority.get(victim.trackId).tuple[1]){urgent.slot=victim.slot;victim.slot=null;state.diagnostics.preempted++;}
}
function defenseOodaSyncQueueA(state,input,profile,capacity){
  const priority=defenseOodaPriorityRowsA(input,state,profile),current=new Set(priority.map(q=>q.track.trackId));
  state.rows=state.rows.filter(q=>current.has(q.trackId));const existing=new Set(state.rows.map(q=>q.trackId));
  for(const q of priority){if(existing.has(q.track.trackId))continue;if(state.rows.length>=profile.queueLimit){state.diagnostics.overflow++;continue;}
    state.rows.push({trackId:q.track.trackId,sequence:++state.queueSequence,phase:'OBSERVE',remainingSteps:defenseOodaPhaseStepsA(profile,Math.max(profile.minimumOperationalCapacity,capacity.value),'OBSERVE'),slot:null,enqueuedStep:input.step,startedStep:null,readyStep:null,lastSeenStep:input.step});state.diagnostics.queued++;existing.add(q.track.trackId);
  }
  for(const row of state.rows)if(current.has(row.trackId))row.lastSeenStep=input.step;
  return priority;
}
function defenseOodaDigestA(value){let h=2166136261,s=JSON.stringify(value);for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(16).padStart(8,'0');}
function defenseOodaBuildCommandA(r,input,state,profile,capacity,priorityRows){
  const hold=capacity.slots===0||input.mode==='MANUAL'||input.mode==='HOLD',current=new Map(input.tracks.map(q=>[q.trackId,q])),ready=priorityRows.filter(q=>state.rows.some(row=>row.trackId===q.track.trackId&&row.phase==='READY')&&current.has(q.track.trackId)),pending=state.rows.filter(q=>q.phase!=='READY'),defer=pending.length?Math.min(...pending.map(q=>defenseOodaEstimateReadyStepA(q,profile,Math.max(profile.minimumOperationalCapacity,capacity.value),input.step))):null;
  if(!ready.length&&!hold)state.diagnostics.deferred++;
  const command=deepFreezeShipProfileV48Wip09({schema:AEGIS_DEFENSE_DECISION_COMMAND_SCHEMA_A1,provider:'DEFENSE_OODA_A',ownerEntityId:r.entityId,inputStep:input.step,inputRevision:input.revision,trackOrder:hold?[]:ready.map(q=>q.track.trackId),priorities:priorityRows.map(q=>({trackId:q.track.trackId,score:q.score})),salvoOverrides:[],advisoryHold:hold||ready.length===0,deferUntilStep:hold?null:(ready.length?null:defer),reason:hold?capacity.reason==='AVAILABLE'?'MODE_HOLD':capacity.reason:ready.length?'OODA_READY':'OODA_DEFER'});
  state.phase=ready.length?'READY':pending.length?pending.slice().sort((a,b)=>a.sequence-b.sequence)[0].phase:'OBSERVE';state.lastCommand={step:input.step,revision:input.revision,reason:command.reason,digest:defenseOodaDigestA(command)};return command;
}
function defenseOodaCommandA(r,input){
  const profile=defenseOodaProfileA(r),state=defenseOodaEnsureStateA(r);if(!profile||!state)return null;
  const capacity=defenseOodaCapacityA(input,profile);state.capacity=capacity;
  if(input.step!==state.lastAcceptedInputStep||input.revision!==state.lastAcceptedInputRevision){
    const delta=Math.max(0,input.step-state.lastServiceStep);for(const row of state.rows)if(row.slot!==null&&row.phase!=='READY')defenseOodaAdvanceRowA(row,delta,profile,Math.max(profile.minimumOperationalCapacity,capacity.value),input.step,state);
    const priority=defenseOodaSyncQueueA(state,input,profile,capacity);defenseOodaAssignSlotsA(state,priority,profile,capacity,input.step);for(const row of state.rows)if(row.slot!==null&&row.startedStep===null)row.startedStep=input.step;
    state.lastServiceStep=input.step;state.lastAcceptedInputStep=input.step;state.lastAcceptedInputRevision=input.revision;
  }
  return defenseOodaBuildCommandA(r,input,state,profile,capacity,defenseOodaPriorityRowsA(input,state,profile));
}
function defenseOodaSalvoA(input,trackId,weapon,native){
  const track=input.tracks.find(q=>q.trackId===trackId),key=String(weapon).toLowerCase(),upper=Math.max(0,Math.min(4,Number(native?.salvo)||0));if(!track||!OODA_SALVO_POLICY_A1.allowedWeapons.includes(weapon))return {salvo:0,policy:'OODA_INVALID_TRACK_OR_WEAPON',canReengage:false};
  const live=Math.max(0,Number(track.engagements?.[key])||0),reengage=track.assessment?.reengageRequired===true,desired=reengage&&live===0?upper:Math.max(0,upper-live);
  return {...native,salvo:Math.min(upper,desired),policy:desired===upper?'OODA_NATIVE_BOUND':'OODA_OWNER_LOCAL_DISTRIBUTION'};
}
function defenseOodaSnapshotA(r){
  const s=r?.combatSystem?.defenseOodaA;if(!s)return null;return {schema:s.schema,revision:s.revision,ownerEntityId:s.ownerEntityId,profileId:s.profileId,phase:s.phase,capacity:{...s.capacity},queueLength:s.rows.length,usedSlots:s.rows.filter(q=>q.slot!==null).length,totalSlots:s.capacity.slots,nextReadyStep:s.rows.filter(q=>q.phase!=='READY').reduce((n,q)=>Math.min(n,defenseOodaEstimateReadyStepA(q,defenseOodaProfileA(r),Math.max(defenseOodaProfileA(r).minimumOperationalCapacity,s.capacity.value),simStepCounter)),Infinity),rows:s.rows.map(q=>({...q})),lastCommand:s.lastCommand?{...s.lastCommand}:null,diagnostics:{...s.diagnostics},migration:s.migration};
}

function defenseOodaCleanSaveA(profileId,ownerEntityId){return {schema:DEFENSE_OODA_STATE_SCHEMA_A,revision:DEFENSE_OODA_STATE_REVISION_A,ownerEntityId:String(ownerEntityId),profileId:String(profileId),phase:'OBSERVE',queueSequence:0,rows:[],lastAcceptedInputStep:-1,lastAcceptedInputRevision:-1,lastCommand:null,diagnostics:defenseOodaCountersA()};}
function defenseOodaExportStateA(r){
  const s=defenseOodaEnsureStateA(r);if(!s)return null;
  return {schema:s.schema,revision:s.revision,ownerEntityId:s.ownerEntityId,profileId:s.profileId,phase:s.phase,queueSequence:s.queueSequence,rows:s.rows.map(q=>({trackId:q.trackId,sequence:q.sequence,phase:q.phase,remainingSteps:q.remainingSteps,slot:q.slot})),lastAcceptedInputStep:s.lastAcceptedInputStep,lastAcceptedInputRevision:s.lastAcceptedInputRevision,lastCommand:s.lastCommand?{...s.lastCommand}:null,diagnostics:{...s.diagnostics}};
}
function defenseOodaValidateSaveA(profileId,ownerEntityId,q,errors=[],path='defenseOodaA'){
  const bad=code=>errors.push('DEFENSE_OODA_A_'+code+':'+path),p=SHIP_PROFILE_REGISTRY[profileId]?.defenseOodaA;if(!p){if(q!=null)bad('PROFILE_UNSUPPORTED');return errors;}
  if(!q||typeof q!=='object'||Array.isArray(q)){bad('OBJECT');return errors;}const keys=['schema','revision','ownerEntityId','profileId','phase','queueSequence','rows','lastAcceptedInputStep','lastAcceptedInputRevision','lastCommand','diagnostics'];if(Object.keys(q).sort().join('|')!==keys.sort().join('|'))bad('KEYS');
  if(q.schema!==DEFENSE_OODA_STATE_SCHEMA_A||q.revision!==DEFENSE_OODA_STATE_REVISION_A)bad('SCHEMA');if(q.ownerEntityId!==String(ownerEntityId)||q.profileId!==profileId)bad('OWNER_PROFILE');if(!DEFENSE_OODA_PHASES_A.includes(q.phase))bad('PHASE');if(!Number.isInteger(q.queueSequence)||q.queueSequence<0||q.queueSequence>1e9)bad('SEQUENCE');if(!Array.isArray(q.rows)||q.rows.length>p.queueLimit){bad('ROWS');return errors;}
  const ids=new Set(),seqs=new Set(),slots=new Set();for(const row of q.rows){if(!row||Object.keys(row).sort().join('|')!==['phase','remainingSteps','sequence','slot','trackId'].sort().join('|')){bad('ROW_KEYS');continue;}if(!Number.isInteger(row.trackId)||row.trackId<0||ids.has(row.trackId))bad('TRACK_ID');ids.add(row.trackId);if(!Number.isInteger(row.sequence)||row.sequence<1||row.sequence>q.queueSequence||seqs.has(row.sequence))bad('ROW_SEQUENCE');seqs.add(row.sequence);if(!DEFENSE_OODA_PHASES_A.includes(row.phase))bad('ROW_PHASE');if(!Number.isInteger(row.remainingSteps)||row.remainingSteps<0||row.remainingSteps>1e7||row.phase==='READY'&&row.remainingSteps!==0)bad('REMAINING');if(row.slot!==null&&(!Number.isInteger(row.slot)||row.slot<0||row.slot>=p.baseConcurrentEvaluations||slots.has(row.slot)))bad('SLOT');if(row.slot!==null)slots.add(row.slot);}
  for(const k of ['lastAcceptedInputStep','lastAcceptedInputRevision'])if(!Number.isInteger(q[k])||q[k]<-1||q[k]>1e12)bad(k.toUpperCase());if(q.lastCommand!==null&&(!q.lastCommand||Object.keys(q.lastCommand).sort().join('|')!==['digest','reason','revision','step'].sort().join('|')||!Number.isInteger(q.lastCommand.step)||!Number.isInteger(q.lastCommand.revision)||typeof q.lastCommand.reason!=='string'||typeof q.lastCommand.digest!=='string'))bad('LAST_COMMAND');
  const counterKeys=Object.keys(defenseOodaCountersA()).sort();if(!q.diagnostics||Object.keys(q.diagnostics).sort().join('|')!==counterKeys.join('|')||counterKeys.some(k=>!Number.isInteger(q.diagnostics[k])||q.diagnostics[k]<0||q.diagnostics[k]>1e9))bad('DIAGNOSTICS');return errors;
}
function defenseOodaRestoreStateA(r,q,step=simStepCounter){
  const errors=defenseOodaValidateSaveA(r.profileId,r.entityId,q,[]);if(errors.length)return {ok:false,errors};const next=defenseOodaNewStateA(r,step);Object.assign(next,{phase:q.phase,queueSequence:q.queueSequence,lastAcceptedInputStep:q.lastAcceptedInputStep,lastAcceptedInputRevision:q.lastAcceptedInputRevision,lastCommand:q.lastCommand?{...q.lastCommand}:null,diagnostics:{...q.diagnostics},migration:'RESTORED'});next.rows=q.rows.map(row=>({...row,enqueuedStep:step,startedStep:row.slot===null?null:step,readyStep:row.phase==='READY'?step:null,lastSeenStep:step}));r.combatSystem.defenseOodaA=next;return {ok:true};
}
function defenseOodaMigrateSaveA(src,migrations){
  if(src.ship&&!Object.hasOwn(src.ship,'defenseOodaA')){src.ship.defenseOodaA=defenseOodaCleanSaveA(src.profileId,src.shipId);migrations.push({id:'LEGACY_DEFENSE_OODA_A',policy:'FRESH_OWNER_LOCAL_STATE'});}
  for(const q of src.fleet?.ships??[])if(SHIP_PROFILE_REGISTRY[q.profileId]?.defenseOodaA&&!Object.hasOwn(q,'defenseOodaA')){q.defenseOodaA=defenseOodaCleanSaveA(q.profileId,q.entityId);migrations.push({id:'LEGACY_DEFENSE_OODA_A:'+q.entityId,policy:'FRESH_OWNER_LOCAL_STATE'});}
}
function defenseOodaContractSelfTestA(){
  const profile=SHIP_PROFILE_REGISTRY.DDG_119_LATE_FLIGHT_IIA?.defenseOodaA,cg=SHIP_PROFILE_REGISTRY.CG_52_LATE_TICONDEROGA?.defenseOodaA,base=defenseOodaCleanSaveA('DDG_119_LATE_FLIGHT_IIA','TEST_OWNER'),bad=JSON.parse(JSON.stringify(base));bad.rows=[{trackId:1,sequence:1,phase:'OBSERVE',remainingSteps:12,slot:0},{trackId:1,sequence:2,phase:'OBSERVE',remainingSteps:12,slot:1}];bad.queueSequence=2;const errors=defenseOodaValidateSaveA('DDG_119_LATE_FLIGHT_IIA','TEST_OWNER',bad,[]),checks={profiles:!!profile&&!!cg,source:profile?.source===DEFENSE_OODA_SOURCE_A&&cg?.source===DEFENSE_OODA_SOURCE_A,saveValid:defenseOodaValidateSaveA('DDG_119_LATE_FLIGHT_IIA','TEST_OWNER',base,[]).length===0,duplicateRejected:errors.some(q=>q.includes('TRACK_ID')),providerValues:DEFENSE_OODA_PROVIDER_VALUES_A.join('|')==='LEGACY_H1|DEFENSE_OODA_A',noRng:/Math\.random|observerRandom|SIM_RNG/.test(defenseOodaCommandA.toString())===false};return {schema:'AEGIS_DEFENSE_OODA_CONTRACT_TEST_A1',checks,pass:Object.values(checks).every(Boolean)};
}
