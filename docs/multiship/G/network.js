// LIVE_CANONICAL: receiver-owned cooperative picture, independent of FCS filters.
// These game link parameters are SIM-TUNE; this is not a Link 16 or CEC model.
const NETWORK_POLICY_G=Object.freeze({schema:'AEGIS_FRIENDLY_NETWORK_G_1',packet:'AEGIS_LINK_PACKET_G_1',periodTicks:30,latencyTicks:18,
  freshS:2,coastS:12,leaseS:1.8,groupLeaseS:2,waitS:1.2,emergencyS:8,maxFiles:96,maxReports:32,maxQueue:16,maxLogs:128,maxRangeM:150000});
function networkNowG(){return simStepCounter*SIM_FIXED_DT;}
function networkMemberG(r){return !!r&&r.faction==='FRIENDLY'&&(r===ACTIVE_SHIP_RUNTIME||r.role==='ALLY')&&r.executionState!=='STATE_BOUND_INACTIVE';}
function networkMembersG(){return [ACTIVE_SHIP_RUNTIME,...physicalShipsB()].filter(networkMemberG);}
function networkDefaultsG(r){const enabled=r===ACTIVE_SHIP_RUNTIME||r.faction==='FRIENDLY'&&['ALLY','PLAYER'].includes(r.role);return {schema:NETWORK_POLICY_G.schema,enabled,shareTracks:enabled,cooperativeDefense:enabled,groupEmcon:'INDIVIDUAL'};}
function prepareNetworkG(r){
  if(r.combatSystem.networkG)return r.combatSystem.networkG;
  const settings=r.restoredNetworkG??networkDefaultsG(r);delete r.restoredNetworkG;
  const n={settings:{...settings},files:new Map(),peers:new Map(),queue:[],serial:1,sequence:0,lastTick:-1,ticks:0,lastSendStep:-1,
    leases:new Map(),waitSince:new Map(),groupBase:null,groupLease:null,groupRevision:0,logs:[],stats:{sent:0,received:0,rejected:0,associated:0,created:0,expired:0,withheld:0}};
  r.combatSystem.networkG=n;claimShipMutableRootA(r,'networkG',n);return n;
}
function networkLogG(n,kind,detail={}){n.logs.push({step:simStepCounter,kind,...detail});if(n.logs.length>NETWORK_POLICY_G.maxLogs)n.logs.shift();}
function networkSpdG(a,size=6){
  if(!Array.isArray(a)||a.length!==size*size||!a.every(Number.isFinite))return null;
  const L=new Array(size*size).fill(0);
  for(let i=0;i<size;i++)for(let j=0;j<=i;j++){
    if(Math.abs(a[i*size+j]-a[j*size+i])>1e-6*Math.max(1,Math.abs(a[i*size+j]),Math.abs(a[j*size+i])))return null;
    let q=a[i*size+j];for(let k=0;k<j;k++)q-=L[i*size+k]*L[j*size+k];
    if(i===j){if(!(q>1e-10)||q>1e12)return null;L[i*size+j]=Math.sqrt(q);}else L[i*size+j]=q/L[j*size+j];
  }
  const inv=new Array(size*size).fill(0);
  for(let col=0;col<size;col++){
    const y=new Array(size).fill(0),x=new Array(size).fill(0);
    for(let i=0;i<size;i++){let q=i===col?1:0;for(let k=0;k<i;k++)q-=L[i*size+k]*y[k];y[i]=q/L[i*size+i];}
    for(let i=size-1;i>=0;i--){let q=y[i];for(let k=i+1;k<size;k++)q-=L[k*size+i]*x[k];x[i]=q/L[i*size+i];}
    for(let i=0;i<size;i++)inv[i*size+col]=x[i];
  }
  return inv;
}
function networkCovarianceG(tr){
  if(!tr?._kfP||tr._kfP.length!==36)return null;const P=Array.from(tr._kfP);
  for(let i=0;i<6;i++)for(let j=0;j<i;j++)P[i*6+j]=P[j*6+i]=(P[i*6+j]+P[j*6+i])*.5;
  for(let i=0;i<6;i++)P[i*6+i]+=i<3?.01:.0001;
  return networkSpdG(P)?P:null;
}
function networkEstimateG(x,P,fromS,now,domain){
  const age=Math.max(0,now-fromS),out=x.slice(),F=new Array(36).fill(0),FP=new Array(36).fill(0),C=new Array(36).fill(0);
  for(let i=0;i<6;i++)F[i*6+i]=1;for(let i=0;i<3;i++){F[i*6+i+3]=age;out[i]+=out[i+3]*age;}
  for(let i=0;i<6;i++)for(let j=0;j<6;j++)for(let k=0;k<6;k++)FP[i*6+j]+=F[i*6+k]*P[k*6+j];
  for(let i=0;i<6;i++)for(let j=0;j<6;j++)for(let k=0;k<6;k++)C[i*6+j]+=FP[i*6+k]*F[j*6+k];
  const a=domain==='SURFACE'?1.2:12;for(let i=0;i<3;i++){C[i*6+i]+=.01+a*a*age**4/4;C[(i+3)*6+i+3]+=.0001+a*a*age*age;}
  return {x:out,P:C};
}
function networkNisG(a,b){
  const inv=networkSpdG(a.P.map((q,i)=>q+b.P[i]));if(!inv)return Infinity;
  const delta=a.x.map((q,i)=>q-b.x[i]);let nis=0;for(let i=0;i<6;i++)for(let j=0;j<6;j++)nis+=delta[i]*inv[i*6+j]*delta[j];
  // A broad covariance cannot merge different contacts at arbitrary distance/speed.
  if(Math.hypot(...delta.slice(0,3))>Math.min(2500,5*Math.sqrt(a.P[0]+a.P[7]+a.P[14]+b.P[0]+b.P[7]+b.P[14]))||Math.hypot(...delta.slice(3))>Math.min(180,5*Math.sqrt(a.P[21]+a.P[28]+a.P[35]+b.P[21]+b.P[28]+b.P[35])))return Infinity;
  return nis;
}
function networkIntersectionG(a,b){
  const A=networkSpdG(a.P),B=networkSpdG(b.P);if(!A||!B)return null;
  // Fixed covariance intersection is conservative for unknown cross correlation.
  // Identical/repeated estimates cannot halve P as independent Kalman fixes would.
  const C=networkSpdG(A.map((q,i)=>(q+B[i])*.5));if(!C)return null;
  const rhs=new Array(6).fill(0),x=new Array(6).fill(0);
  for(let i=0;i<6;i++)for(let j=0;j<6;j++)rhs[i]+=.5*(A[i*6+j]*a.x[j]+B[i*6+j]*b.x[j]);
  for(let i=0;i<6;i++)for(let j=0;j<6;j++)x[i]+=C[i*6+j]*rhs[j];return {x,P:C};
}
function networkLocalAgeG(tr){
  if(!tr||tr.sensorDetected===false||tr.sensorSource==='OFFBOARD_C')return Infinity;
  const stamp=tr.networkLocalAtS_G??tr.observationReportsC?.localAtS??(Number.isFinite(tr._lastMeasurementStep)?tr._lastMeasurementStep*SIM_FIXED_DT:null);
  return stamp==null?Infinity:Math.max(0,networkNowG()-stamp);
}
function networkLocalEstimateG(tr){const P=networkCovarianceG(tr);return P&&tr._kfX?.length===6?{x:Array.from(tr._kfX),P}:null;}
function networkNoteLocalG(r,tr,source){if(source!=='OFFBOARD_C'&&tr)tr.networkLocalAtS_G=networkNowG();}
function networkPeerG(n,id){let p=n.peers.get(id);if(!p){p={entityId:id,lastSequence:-1,lastReceivedS:-Infinity,connected:false,reason:'NO_HEARTBEAT',shared:0};n.peers.set(id,p);}return p;}
function networkLinkPathG(a,b){
  // Transport/availability boundary may read the participating radios' own state.
  // No target entity, target identity, or target coordinate enters this boundary.
  if(!networkMemberG(a)||!networkMemberG(b)||a===b)return {ok:false,reason:'NOT_ALLIED'};
  if(!prepareNetworkG(a).settings.enabled||!prepareNetworkG(b).settings.enabled)return {ok:false,reason:'RADIO_OFF'};
  for(const r of [a,b])if(shipSurvivalB(r).snapshot().equipmentOffline||r.crew.offline()||shipSystemDamageB(r,'CDC')>=80||shipSystemDamageB(r,'MAST')>=85)return {ok:false,reason:'RADIO_UNAVAILABLE'};
  // Existing navigation radar height is a documented link reference, not a new antenna registration.
  const mount=r=>observerMountC(r,resolveShipProfile(r.profileId).geometry.hardpoints.bridgeMasterE),x=mount(a),y=mount(b),rangeM=Math.hypot(worldToMeters(x.x-y.x),worldToMeters(x.y-y.y));
  const horizonM=4120*(Math.sqrt(Math.max(0,x.z))+Math.sqrt(Math.max(0,y.z)));
  if(rangeM>Math.min(NETWORK_POLICY_G.maxRangeM,horizonM))return {ok:false,reason:'RADIO_HORIZON'};
  if(terrainAwareRadarLOS(x.x,x.y,x.z,y.x,y.y,y.z)<=.05)return {ok:false,reason:'RADIO_MASKED'};
  return {ok:true,reason:null};
}
function networkStrictKeysG(q,keys){return !!q&&typeof q==='object'&&!Array.isArray(q)&&Object.keys(q).sort().join(',')===keys.slice().sort().join(',');}
function networkValidateReportG(q,now){
  if(!networkStrictKeysG(q,['fileId','kind','measuredAtS','stateAtS','stateM','covariance','domain','classification','identity','assessment','bid']))return false;
  if(!Number.isInteger(q.fileId)||q.fileId<0||q.fileId>1e9||!['SELF','TRACK'].includes(q.kind)||q.kind==='SELF'&&q.fileId!==0||q.kind==='TRACK'&&q.fileId===0)return false;
  if(![q.measuredAtS,q.stateAtS].every(v=>Number.isFinite(v)&&v>=0)||q.measuredAtS>q.stateAtS+1e-8||q.stateAtS>now+1e-8||now-q.measuredAtS>NETWORK_POLICY_G.coastS||now-q.stateAtS>NETWORK_POLICY_G.coastS)return false;
  if(!Array.isArray(q.stateM)||q.stateM.length!==6||!q.stateM.every((v,i)=>Number.isFinite(v)&&Math.abs(v)<(i<3?2e7:5000))||!networkSpdG(q.covariance))return false;
  if(!['AIR','SURFACE'].includes(q.domain)||!['AIR','ASM','SURFACE'].includes(q.classification)||!['UNKNOWN','FRIEND','NEUTRAL','HOSTILE','ASSUMED_HOSTILE','TRAINING_TARGET'].includes(q.identity)||!['UNASSESSED','MONITOR','THREAT','HARMLESS','KILL_ASSESSMENT','DESTROYED','LOST'].includes(q.assessment))return false;
  if(q.kind==='SELF'&&(q.identity!=='FRIEND'||q.domain!=='SURFACE'||q.classification!=='SURFACE'))return false;
  const b=q.bid;if(!networkStrictKeysG(b,['eligible','cost','weapon','inFlight'])||typeof b.eligible!=='boolean'||!Number.isFinite(b.cost)||b.cost<0||b.cost>1e6||!Number.isInteger(b.inFlight)||b.inFlight<0||b.inFlight>256||![null,'SM2','SM2ER','SM6','ESSM'].includes(b.weapon)||b.eligible&&!b.weapon)return false;
  return true;
}
function networkReceiveG(receiver,senderId,packet){
  if(!receiver?.combatSystem)return {ok:false,reason:'RECEIVER_REQUIRED'};
  const n=prepareNetworkG(receiver),now=networkNowG(),sender=ENGAGEMENT_RUNTIME.ships.get(senderId),bad=reason=>{n.stats.rejected++;return {ok:false,reason};};
  if(!networkMemberG(receiver)||!networkMemberG(sender)||sender===receiver||sender.faction!==receiver.faction)return bad('AUTHENTICATED_ALLY_REQUIRED');
  if(!networkLinkPathG(receiver,sender).ok)return bad('LINK_UNAVAILABLE');
  if(!networkStrictKeysG(packet,['schema','sequence','sentAtS','cooperative','reports','group','grants'])||packet.schema!==NETWORK_POLICY_G.packet||!Number.isInteger(packet.sequence)||packet.sequence<0||!Number.isFinite(packet.sentAtS)||packet.sentAtS>now+1e-8||now-packet.sentAtS>NETWORK_POLICY_G.freshS||typeof packet.cooperative!=='boolean')return bad('PACKET_SCHEMA_TIME_OR_TRUTH');
  if(packet.sequence<=(n.peers.get(senderId)?.lastSequence??-1))return bad('PACKET_REPLAY');
  if(!Array.isArray(packet.reports)||packet.reports.length>NETWORK_POLICY_G.maxReports+1||!packet.reports.every(q=>networkValidateReportG(q,now))||new Set(packet.reports.map(q=>q.fileId)).size!==packet.reports.length)return bad('ANONYMOUS_TRACK_REPORT_REQUIRED');
  if(!networkValidateControlG(packet.group,packet.grants,sender,receiver,now))return bad('CONTROL_SCHEMA');
  // All validation precedes any heartbeat, picture or command update.
  const peer=networkPeerG(n,senderId);peer.lastSequence=packet.sequence;peer.lastReceivedS=now;peer.connected=true;peer.reason=null;peer.cooperative=packet.cooperative;n.stats.received++;
  for(const report of packet.reports)if(report.kind==='SELF'||n.settings.shareTracks)networkAcceptReportG(receiver,senderId,report);
  networkAcceptControlG(receiver,senderId,packet.group,packet.grants);return {ok:true};
}
function networkFileEstimateG(file,now=networkNowG()){
  let out=null;for(const q of [...file.sources.values()].sort((a,b)=>a.senderId.localeCompare(b.senderId)||a.fileId-b.fileId)){
    if(now-q.measuredAtS>NETWORK_POLICY_G.coastS)continue;const e=networkEstimateG(q.stateM,q.covariance,q.stateAtS,now,q.domain);out=out?networkIntersectionG(out,e):e;
  }return out;
}
function networkAcceptReportG(r,senderId,report){
  const n=prepareNetworkG(r),key=JSON.stringify([senderId,report.fileId]),now=networkNowG();let file=[...n.files.values()].find(f=>f.sources.has(key));
  if(file?.sources.get(key).measuredAtS>=report.measuredAtS){
    // New delivery sequence is not a new measurement; status may change, but P/time/hits may not.
    const q=file.sources.get(key);q.bid={...report.bid};q.assessment=report.assessment;q.identity=report.identity;return;
  }
  const estimate=networkEstimateG(report.stateM,report.covariance,report.stateAtS,now,report.domain);
  if(file){const prior=networkFileEstimateG(file,now);if(file.domain!==report.domain||!prior||networkNisG(prior,estimate)>36){file.sources.delete(key);file=null;}}
  if(!file){
    const candidates=[];for(const f of n.files.values())if(f.domain===report.domain&&!f.sources.has(key)&&![...f.sources.values()].some(q=>q.senderId===senderId)){const e=networkFileEstimateG(f,now),nis=e?networkNisG(e,estimate):Infinity;if(nis<=36)candidates.push({f,nis});}
    candidates.sort((a,b)=>a.nis-b.nis||a.f.serial-b.f.serial);if(candidates.length===1||candidates.length>1&&candidates[1].nis-candidates[0].nis>4)file=candidates[0].f;
  }
  if(!file){if(n.files.size>=NETWORK_POLICY_G.maxFiles)return;const serial=n.serial++;file={id:'N'+serial,serial,domain:report.domain,sources:new Map(),localTrackId:null,hits:0};n.files.set(serial,file);n.stats.created++;}
  file.sources.set(key,{...jsonSafeCloneV48Wip11A(report),senderId});file.hits++;
}
function networkReconcileG(r){
  const n=prepareNetworkG(r),now=networkNowG(),local=observerC(r).tracks,pairs=[];
  const candidates=[...local.entries()].filter(([id,tr])=>tr.confirmed&&networkLocalAgeG(tr)<=NETWORK_POLICY_G.freshS&&trackIsDisplayable(tr)).slice(0,128);
  for(const [serial,file]of n.files){
    for(const [key,q]of file.sources)if(now-q.measuredAtS>NETWORK_POLICY_G.coastS)file.sources.delete(key);
    if(!file.sources.size){n.files.delete(serial);n.stats.expired++;continue;}file.localTrackId=null;file.fused=null;
    const estimate=networkFileEstimateG(file,now);if(!estimate)continue;
    for(const [id,tr]of candidates){if(tr.domain!==file.domain)continue;const e=networkLocalEstimateG(tr),nis=e?networkNisG(e,estimate):Infinity;if(nis<=36)pairs.push({file,id,tr,e,estimate,nis});}
  }
  pairs.sort((a,b)=>a.nis-b.nis||a.id-b.id||a.file.serial-b.file.serial);const used=new Set(),ambiguous=new Set();
  const bestByFile=new Map();for(const p of pairs){const best=bestByFile.get(p.file.serial);if(!best)bestByFile.set(p.file.serial,p);else if(best.id!==p.id&&p.nis-best.nis<4)ambiguous.add(p.file.serial);}
  for(const p of pairs){if(ambiguous.has(p.file.serial)||p.file.localTrackId!=null||used.has(p.id))continue;p.file.localTrackId=p.id;p.file.fused=networkIntersectionG(p.e,p.estimate);p.file.fusedAtS=now;used.add(p.id);n.stats.associated++;}
  for(const [id,lease]of n.leases)if(lease.untilS<now||!local.has(id))n.leases.delete(id);
  for(const id of n.waitSince.keys())if(!local.has(id))n.waitSince.delete(id);
}
function networkProtectionG(r,tr){
  if(!networkMemberG(r)||!tr||!r.combatSystem.networkG)return null;
  const now=networkNowG();for(const file of r.combatSystem.networkG.files.values())if(file.localTrackId===tr.trackId){
    const q=[...file.sources.values()].find(q=>now-q.measuredAtS<=NETWORK_POLICY_G.freshS&&['FRIEND','NEUTRAL'].includes(q.identity));if(q)return q.identity;
  }return null;
}
function networkPresentationTrackG(tr){
  const n=ACTIVE_SHIP_RUNTIME.combatSystem.networkG;if(!n)return tr;const file=[...n.files.values()].find(f=>f.localTrackId===tr.trackId);
  if(!file?.fused||networkLocalAgeG(tr)>NETWORK_POLICY_G.freshS||['KILL_ASSESSMENT','DESTROYED'].includes(tr.threatStatus))return tr;
  const e=networkEstimateG(file.fused.x,file.fused.P,file.fusedAtS,networkNowG(),tr.domain),q={...tr,x:metersToWorld(e.x[0]),y:metersToWorld(e.x[1]),z:e.x[2],vx:mpsToWorldSpeed(e.x[3]),vy:mpsToWorldSpeed(e.x[4]),vz:e.x[5],_kfP:Float64Array.from(e.P),_kfX:Float64Array.from(e.x),covarianceEllipse:null};
  const protection=networkProtectionG(ACTIVE_SHIP_RUNTIME,tr);if(protection)q.identity=protection;return q;
}
function networkPictureG(r){
  const n=prepareNetworkG(r),now=networkNowG();return [...n.files.values()].map(file=>{
    const e=networkFileEstimateG(file,now),sources=[...file.sources.values()],age=now-Math.max(...sources.map(q=>q.measuredAtS)),protectedSource=sources.find(q=>['FRIEND','NEUTRAL'].includes(q.identity));
    return {id:file.id,localTrackId:file.localTrackId,domain:file.domain,classification:sources.find(q=>q.classification==='ASM')?.classification??sources[0]?.classification,identity:protectedSource?.identity??'UNKNOWN',
      ageS:age,coasting:age>NETWORK_POLICY_G.freshS,positionM:e?{x:e.x[0],y:e.x[1],z:e.x[2]}:null,velocityMps:e?{x:e.x[3],y:e.x[4],z:e.x[5]}:null,covariance:e?.P??null,
      fusedPositionM:file.fused?{x:file.fused.x[0],y:file.fused.x[1],z:file.fused.x[2]}:null,sources:sources.map(q=>({senderId:q.senderId,fileId:q.fileId,measurementAgeS:now-q.measuredAtS,kind:q.kind,assessment:q.assessment,bid:{...q.bid}})),fcsSource:'LOCAL_ONLY',automaticRelease:false};
  });
}
function networkBuildReportsG(r){
  const n=prepareNetworkG(r),now=networkNowG(),pos=r.navigation.positionWorld,zero={eligible:false,cost:1e6,weapon:null,inFlight:0},P=new Array(36).fill(0);for(let i=0;i<6;i++)P[i*6+i]=i<3?100:1;
  const reports=[{fileId:0,kind:'SELF',measuredAtS:now,stateAtS:now,stateM:[worldToMeters(pos.x),worldToMeters(pos.y),8,worldSpeedToMps(r.navigation.vx),worldSpeedToMps(r.navigation.vy),0],covariance:P,domain:'SURFACE',classification:'SURFACE',identity:'FRIEND',assessment:'MONITOR',bid:zero}];
  if(!n.settings.shareTracks)return reports;
  const candidates=[...observerC(r).tracks.values()].filter(tr=>tr.confirmed&&networkLocalAgeG(tr)<=NETWORK_POLICY_G.freshS&&networkLocalEstimateG(tr));
  candidates.sort((a,b)=>(b.classification==='ASM')-(a.classification==='ASM')||networkLocalAgeG(a)-networkLocalAgeG(b)||a.trackId-b.trackId);
  for(const tr of candidates.slice(0,NETWORK_POLICY_G.maxReports)){
    const e=networkLocalEstimateG(tr),identity=['FRIEND','NEUTRAL','HOSTILE','ASSUMED_HOSTILE','TRAINING_TARGET'].includes(tr.identity)?tr.identity:'UNKNOWN',assessment=['THREAT','HARMLESS','KILL_ASSESSMENT','DESTROYED','LOST','MONITOR'].includes(tr.threatStatus)?tr.threatStatus:'UNASSESSED';
    reports.push({fileId:tr.trackId,kind:'TRACK',measuredAtS:now-networkLocalAgeG(tr),stateAtS:now,stateM:e.x,covariance:e.P,domain:tr.domain==='SURFACE'?'SURFACE':'AIR',classification:['AIR','ASM','SURFACE'].includes(tr.classification)?tr.classification:'AIR',identity,assessment,bid:networkBidG(r,tr)});
  }return reports;
}
function resetNetworkFleetG(){
  for(const r of [ACTIVE_SHIP_RUNTIME,...physicalShipsB()]){const old=r.combatSystem.networkG,settings=old?.settings?{...old.settings}:null;if(old)networkRestoreIndividualG(r);r.combatSystem.networkG=null;if(settings)r.restoredNetworkG=settings;prepareNetworkG(r);}
}
function retireNetworkG(r){const n=r.combatSystem.networkG;if(n){networkRestoreIndividualG(r);n.queue.length=0;n.leases.clear();n.files.clear();n.peers.clear();}r.combatSystem.networkG=null;}
function networkFixedStepG(dt){
  const members=networkMembersG(),now=networkNowG();
  for(const r of members){
    const n=prepareNetworkG(r);if(n.lastTick===simStepCounter)throw Error('NETWORK_DOUBLE_TICK');n.lastTick=simStepCounter;n.ticks++;
    for(const peer of n.peers.values())if(now-peer.lastReceivedS>NETWORK_POLICY_G.freshS){peer.connected=false;peer.reason='HEARTBEAT_EXPIRED';}
    const due=n.queue.filter(q=>q.availableStep<=simStepCounter);n.queue=n.queue.filter(q=>q.availableStep>simStepCounter);
    for(const q of due)networkReceiveG(r,q.senderId,q.packet);networkGroupStepG(r);if(due.length||simStepCounter%12===0)networkReconcileG(r);
  }
  if(simStepCounter%12===0)networkCoordinateG(ACTIVE_SHIP_RUNTIME);
  for(const sender of members){
    const n=prepareNetworkG(sender);if(simStepCounter%NETWORK_POLICY_G.periodTicks!==0||n.lastSendStep===simStepCounter||!n.settings.enabled)continue;n.lastSendStep=simStepCounter;
    const reports=networkBuildReportsG(sender),sequence=++n.sequence;
    for(const receiver of members){if(sender===receiver)continue;const path=networkLinkPathG(sender,receiver),peer=networkPeerG(n,receiver.entityId);if(!path.ok){peer.connected=false;peer.reason=path.reason;continue;}
      const to=prepareNetworkG(receiver);if(to.queue.length>=NETWORK_POLICY_G.maxQueue){n.stats.rejected++;continue;}
      const packet={schema:NETWORK_POLICY_G.packet,sequence,sentAtS:now,cooperative:n.settings.cooperativeDefense&&n.settings.shareTracks,reports,group:networkGroupPacketG(sender,receiver),grants:networkGrantPacketsG(sender,receiver)};
      to.queue.push({senderId:sender.entityId,availableStep:simStepCounter+NETWORK_POLICY_G.latencyTicks,packet:jsonSafeCloneV48Wip11A(packet)});n.stats.sent++;
    }
  }
}
function networkSnapshotG(){return {schema:NETWORK_POLICY_G.schema,timeS:networkNowG(),policy:{...NETWORK_POLICY_G},ships:networkMembersG().map(r=>{const n=prepareNetworkG(r);return {entityId:r.entityId,settings:{...n.settings},ticks:n.ticks,sequence:n.sequence,queued:n.queue.length,peers:[...n.peers.values()].map(q=>({...q,lastReceivedS:Number.isFinite(q.lastReceivedS)?q.lastReceivedS:null})),picture:networkPictureG(r),leases:[...n.leases].map(([trackId,q])=>({trackId,...jsonSafeCloneV48Wip11A(q)})),group:{baseEmcon:n.groupBase,lease:n.groupLease?{...n.groupLease}:null},stats:{...n.stats},logs:n.logs.map(q=>({...q}))};}),ordnanceDatalink:false,remoteFireControl:false};}
