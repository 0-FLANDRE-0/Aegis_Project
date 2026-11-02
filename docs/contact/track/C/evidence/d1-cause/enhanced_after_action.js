// TEST BUILD ONLY. Physical labels never enter a plot, KF, identity or command.
(() => {
 const state={active:false,record:true,serial:0,rfSerial:0,labels:new Map(),aliases:new Map(),objects:new WeakMap(),sourceObjects:new Map(),fileLabels:new Map(),measurements:new WeakMap(),fingerprints:new Map(),records:[],candidateRecords:[],lifecycle:[],lastFiles:new Map(),seeker:new Map(),faults:[],dropped:0};
 const stamp=()=>({step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT});
 const scalar=(o,keys)=>Object.fromEntries(keys.filter(k=>o?.[k]!==undefined).map(k=>[k,o[k]]));
 function safe(fn){try{return fn();}catch(e){state.faults.push({...stamp(),error:String(e?.stack??e)});}}
 function label(object,key,kind){
  let uid=object&&typeof object==='object'?state.objects.get(object):null;uid??=state.aliases.get(String(key));
  if(!uid){uid='P'+(++state.serial);state.labels.set(uid,{uid,kind,keys:[],firstSeenS:simStepCounter*SIM_FIXED_DT});}
  const row=state.labels.get(uid);if(kind!=='C55_PHYSICAL_SOURCE')row.kind=kind;
  if(key!=null){const k=String(key);state.aliases.set(k,uid);if(!row.keys.includes(k))row.keys.push(k);}
  if(object&&typeof object==='object'){state.objects.set(object,uid);state.sourceObjects.set(uid,object);}return uid;
 }
 function radar(source){const s=String(source??'');return s.startsWith('SPY1DV')?'SPY1DV':s.startsWith('SPQ')?'SPQ9B':s.startsWith('BRIDGEMASTER')?'BRIDGEMASTER_E':s;}
 function keys(p,owner,source){
  const values=[p?.rangeM,p?.azRad,p?.elRad,p?.radialMps],prefix=JSON.stringify([simStepCounter,owner,radar(source)]);
  return [[0,1,2,3],[0,1,3],[0,1]].filter(ix=>ix.every(i=>Number.isFinite(values[i]))).map(ix=>prefix+':'+JSON.stringify(ix.map(i=>values[i])));
 }
 function emit(q){if(state.records.length<1000000)state.records.push(q);else state.dropped++;} // SIM_TUNED test storage only.
 const api={begin(options={}){state.active=true;state.record=options.record!==false;state.serial=state.rfSerial=state.dropped=0;state.labels.clear();state.aliases.clear();state.objects=new WeakMap();state.sourceObjects.clear();state.fileLabels.clear();state.measurements=new WeakMap();state.fingerprints.clear();state.records.length=state.candidateRecords.length=state.lifecycle.length=state.faults.length=0;state.lastFiles.clear();state.seeker.clear();if(window.__TRACK_C__){window.__TRACK_C__.configure({enabled:state.record,capacity:32768});window.__TRACK_C__.clear();}},
  rf(echo,ref,owner,source){if(!state.active||!state.record)return;safe(()=>{
   const uid=label(ref?._truthObject,ref?.rfId,ref?._physicsKind),id=++state.rfSerial;
   const link={measurementUid:'RF'+id,physicalUid:uid,ownerEntityId:owner,radarId:source,...stamp()};state.measurements.set(echo,link);emit({...link,store:'RF_FRONTEND',type:'RF_ECHO',decision:'SYNTHESIZED_MEASUREMENT',trackId:null,fields:scalar(echo,['rangeM','azRad','elRad','radialMps'])});
   for(const key of keys(echo,owner,source)){let a=state.fingerprints.get(key);if(!a){a=[];state.fingerprints.set(key,a);}a.push(link);}
  });},
  local(meas,src,owner,mount){if(!state.active||!state.record||!meas?.accepted)return;safe(()=>{const uid=label(src.e,src.key,'C55_PHYSICAL_SOURCE');const link={measurementUid:'LOCAL'+(++state.rfSerial),physicalUid:uid,ownerEntityId:owner,mountId:mount,...stamp()};state.measurements.set(meas,link);emit({...link,store:'C55:'+mount,type:'LOCAL_MEASURED',decision:'RF_DETECTED_BEFORE_ASSOCIATION',trackId:null,fields:scalar(meas,['rangeM','azRad','elRad','rxM','ryM','rzM','positionVarianceM2'])});});},
  sample(initial=[],egress=null){if(!state.active||!state.record)return;safe(()=>{
   // Drain diagnostic DTOs only; no live consumer reads this ring. This avoids
   // truncating long battles while preserving every actual proposal record.
   if(typeof TRACK_C_DIAG!=='undefined'&&TRACK_C_DIAG.records.length)state.candidateRecords.push(...TRACK_C_DIAG.records.splice(0));
   const live=new Map(),owners=[ACTIVE_SHIP_RUNTIME,...physicalShipsB()];
   for(const r of owners){const store=r.combatSystem.observerC?.tracks??r.combatSystem.trackManager?.tracks;if(!store)continue;
    for(const[id,tr]of store){const key=JSON.stringify([r.entityId,'CANONICAL',id]),value={ownerEntityId:r.entityId,store:'CANONICAL',trackId:id,...stamp(),lifecycle:tr.trackLifecycle??null,confirmed:!!tr.confirmed,memory:!!tr.memActive,reacquiring:!!tr.reacquiring,hits:tr.sensorHits,lastMeasurementStep:tr._lastMeasurementStep,ttl:tr.ttl};live.set(key,value);const old=state.lastFiles.get(key);if(!old||old.lifecycle!==value.lifecycle||old.confirmed!==value.confirmed||old.memory!==value.memory||old.reacquiring!==value.reacquiring)state.lifecycle.push({event:old?'STATE':'APPEAR',...value});}
   }
   for(const[key,old]of state.lastFiles)if(!live.has(key)){state.lifecycle.push({event:'DROP',...old,...stamp()});state.fileLabels.delete(key);}state.lastFiles=live;
   for(const t of initial){let row=state.seeker.get(t.id);if(!row){row={id:t.id,accepted:[],states:[],qualifiedEgress:null};state.seeker.set(t.id,row);}
    const s=t.seeker??{},q={...stamp(),mode:s.mode??t._seekerState??null,trackValid:!!s.trackValid,guidance:s.lastGuidanceSource??null,blind:!!t._blindTerminal,seekerOn:!!t.seekerOn,alive:t.alive!==false};
    if(!row.states.length||['mode','trackValid','guidance','blind','alive'].some(k=>q[k]!==row.states.at(-1)[k]))row.states.push(q);
    if(egress?.get(t.id)?.qualified&&!row.qualifiedEgress)row.qualifiedEgress={...q,rangeM:egress.get(t.id).previousRangeM,outwardS:egress.get(t.id).outwardS,lastAccepted:row.accepted.at(-1)??null};
   }
   // Only current-tick fingerprints can be consumed. Bound memory independently of gameplay.
   if(simStepCounter%60===0)for(const[k,links]of state.fingerprints)if(links[0]?.step<simStepCounter-1)state.fingerprints.delete(k);
  });},
  finish(){state.active=false;const candidateTrace=window.__TRACK_C__?.snapshot().trace??null;if(candidateTrace)candidateTrace.records=[...state.candidateRecords,...candidateTrace.records];window.__TRACK_C__?.configure({enabled:false});return {schema:'AEGIS_TRACK_C_AFTER_ACTION_LINEAGE_1',tag:'AFTER_ACTION_TRUTH_TEST_ONLY',labels:[...state.labels.values()],records:state.records,lifecycle:state.lifecycle,seeker:[...state.seeker.values()],candidateTrace,faults:state.faults,dropped:state.dropped,physicalLabelsWrittenToGameObjects:0,physicalLabelsReadByTacticalConsumers:0};}
 };
 window.__TRACK_C_AA_INTERNAL__=api;
 const trace=trackATraceEventA;
 trackATraceEventA=function(type,payload,context={}){
  const result=trace.apply(this,arguments);
  if(state.active&&state.record&&(type==='UPDATE'||type==='ASSIGNMENT'||(type==='RECEIVED'&&context.kind==='CIWS_LOCAL_RF')))safe(()=>{
   const owner=context.observerShip??ACTIVE_SHIP_RUNTIME.entityId;let link=state.measurements.get(payload),ambiguous=false;
   if(!link){for(const key of keys(payload,owner,context.sourceSensor??payload?.source)){const rows=state.fingerprints.get(key)??[];if(rows.length===1){link=rows[0];break;}if(rows.length>1){ambiguous=true;break;}}}
   if(!link&&!context.kind?.includes('RADAR')&&context.kind!=='CIWS_LOCAL_RF')return;
   const p=payload??{},before=context.before,after=context.after,store=context.kind==='CIWS_LOCAL_RF'?'C55:'+context.mountId:'CANONICAL',fileKey=JSON.stringify([owner,store,context.trackId]),priorPhysicalUid=state.fileLabels.get(fileKey)??null,priorObject=state.sourceObjects.get(priorPhysicalUid),priorPhysicalAlive=priorObject?priorObject.alive!==false&&!priorObject.dead:null;
   emit({...stamp(),ownerEntityId:owner,store,route:context.route,type,decision:context.decision,trackId:context.trackId,knownOwnLaunch:context.knownOwnLaunch??null,priorPhysicalUid,priorPhysicalAlive,
    measurementUid:link?.measurementUid??null,physicalUid:link?.physicalUid??null,lineageStatus:link?'EXACT_RF_OBJECT_OR_EXACT_MEASURED_POLAR_CLONE':ambiguous?'AMBIGUOUS_EXACT_FINGERPRINT':'UNLINKED',
    measuredAtS:context.measuredAtS??p.measuredAtS??null,receivedAtS:context.receivedAtS??p.receivedAtS??null,source:context.sourceSensor??p.source??null,
    fields:scalar(p,['rangeM','azRad','elRad','radialMps']),filterEpochStep:simStepCounter,
    before:before?{...scalar(before,['confirmed','memActive','reacquiring','trackLifecycle','sensorHits','sensorAge','identity','classification','engagementAuthority','ownFireEvidence','protectedIdentity']),stateM:before.stateM??null}:null,
    after:after?{...scalar(after,['confirmed','memActive','reacquiring','trackLifecycle','sensorHits','sensorAge','identity','classification','engagementAuthority','ownFireEvidence','protectedIdentity']),stateM:after.stateM??null}:null,
    independentHit:context.independentHit??null,nativeHitIncrement:context.nativeHitIncrement??null});
   if(link&&['ACCEPT','CREATE','ASSOCIATE_WITHOUT_HIT'].includes(context.decision))state.fileLabels.set(fileKey,link.physicalUid);
  });return result;
 };
 const update=asmSeekerEkfUpdate;
 asmSeekerEkfUpdate=function(s,measurement,em){const result=update.apply(this,arguments);if(state.active&&state.record&&result)safe(()=>{let row=state.seeker.get(em.id);if(!row){row={id:em.id,accepted:[],states:[],qualifiedEgress:null};state.seeker.set(em.id,row);}const members=measurement?._debugMembers??[measurement?._debugKind].filter(Boolean),entry={...stamp(),members:[...members],debugId:measurement?._debugId??null,mode:s.mode??null,snr:measurement?.snr??null};const old=row.accepted.at(-1);if(!old||JSON.stringify(old.members)!==JSON.stringify(entry.members)||old.debugId!==entry.debugId)row.accepted.push(entry);});return result;};
})();
