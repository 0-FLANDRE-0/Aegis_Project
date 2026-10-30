// Cooperative SAM allocation is advisory scheduling with expiring consent.
// Native owner ROE/FCS/ammunition/SPG checks remain authoritative at release.
function networkBidDataG(r,tr,control,mode,rounds){
  const n=prepareNetworkG(r),zero={eligible:false,cost:1e6,weapon:null,inFlight:0},active=rounds.filter(m=>!m.dead&&m.alive!==false&&(m.assignedTargetId??m.targetId)===tr.trackId).length;
  const safe=tr.confirmed&&networkLocalAgeG(tr)<=NETWORK_POLICY_G.freshS&&!tr.memActive&&!tr.reacquiring&&tr.domain!=='SURFACE'&&!['FRIEND','NEUTRAL','UNKNOWN','TRAINING_TARGET'].includes(tr.identity)&&!networkProtectionG(r,tr)&&tr.engagementAuthority==='AUTO_AUTHORIZED';
  if(!n.settings.enabled||!n.settings.shareTracks||!n.settings.cooperativeDefense||mode!=='AUTO'||!safe)return {...zero,inFlight:active};
  const row=(control.recommendations??[]).find(q=>q.trackId===tr.trackId&&['SM2','SM2ER','SM6','ESSM'].includes(q.weapon)&&q.firePlan?.status==='READY'&&q.recommendedRounds>0),assessment=control.assessments.get(tr.trackId);
  if(!row||assessment?.state!=='THREAT')return {...zero,inFlight:active};
  const cost=Math.max(0,Math.min(1e6,(Number(row.firePlan?.fireDelayS)||0)+ownerThreatRowD(r,tr).dKm*.1+(Number(row.recommendedRounds)||1)));
  return {eligible:true,cost,weapon:row.weapon,inFlight:active};
}
function networkBidG(r,tr){
  if(r===ACTIVE_SHIP_RUNTIME)return networkBidDataG(r,tr,wip118ControlState,engagementControlMode,missiles);
  return r.weapons.executionD?.context.networkBid?.(tr.trackId)??{eligible:false,cost:1e6,weapon:null,inFlight:0};
}
function networkConnectedPeersG(r){const n=prepareNetworkG(r),now=networkNowG();return [...n.peers.values()].filter(p=>p.connected&&now-p.lastReceivedS<=NETWORK_POLICY_G.freshS);}
function networkCoordinateG(leader){
  if(!networkMemberG(leader)||leader!==ACTIVE_SHIP_RUNTIME)return;const n=prepareNetworkG(leader),now=networkNowG();
  if(!n.settings.enabled||!n.settings.shareTracks||!n.settings.cooperativeDefense){n.outboundGrants=[];return;}
  const peers=networkConnectedPeersG(leader).filter(p=>p.cooperative),peerIds=new Set(peers.map(p=>p.entityId)),grants=[];
  if(!peerIds.size){n.outboundGrants=[];return;}
  // Receiver picture is correlated from measured kinematics; never common truth IDs.
  for(const file of n.files.values()){
    if(file.domain==='SURFACE')continue;const sources=[...file.sources.values()].filter(q=>q.kind==='TRACK'&&peerIds.has(q.senderId)&&now-q.measuredAtS<=NETWORK_POLICY_G.freshS),local=file.localTrackId==null?null:observerC(leader).tracks.get(file.localTrackId),bids=[];
    if(sources.some(q=>['FRIEND','NEUTRAL'].includes(q.identity)))continue;
    if(local){const bid=networkBidG(leader,local);if(bid.eligible||bid.inFlight)bids.push({entityId:leader.entityId,fileId:local.trackId,...bid});}
    for(const q of sources)if(q.bid.eligible||q.bid.inFlight)bids.push({entityId:q.senderId,fileId:q.fileId,...q.bid});
    if(!bids.length)continue;bids.sort((a,b)=>(b.inFlight>0)-(a.inFlight>0)||a.cost-b.cost||a.entityId.localeCompare(b.entityId));
    const prior=n.leaderChoices?.get(file.serial),sticky=prior&&prior.untilS>=now&&bids.find(q=>q.entityId===prior.primary&&(q.eligible||q.inFlight));
    const primary=(sticky??bids[0]).entityId,estimate=networkFileEstimateG(file,now);if(!estimate)continue;
    const decision={primary,untilS:now+NETWORK_POLICY_G.leaseS,stateAtS:now,stateM:estimate.x,covariance:estimate.P,domain:file.domain};
    n.leaderChoices??=new Map();n.leaderChoices.set(file.serial,decision);
    if(local)n.leases.set(local.trackId,{...decision,issuer:leader.entityId});
    for(const q of sources)grants.push({recipient:q.senderId,fileId:q.fileId,...decision});
  }
  if(n.leaderChoices)for(const [id,q]of n.leaderChoices)if(q.untilS<now||!n.files.has(id))n.leaderChoices.delete(id);
  n.outboundGrants=grants.slice(0,NETWORK_POLICY_G.maxReports);
}
function networkGrantPacketsG(sender,receiver){return sender===ACTIVE_SHIP_RUNTIME?(prepareNetworkG(sender).outboundGrants??[]).filter(q=>q.recipient===receiver.entityId).map(({recipient,...q})=>q):[];}
function networkValidateControlG(group,grants,sender,receiver,now){
  if(!Array.isArray(grants)||grants.length>NETWORK_POLICY_G.maxReports)return false;
  if(sender!==ACTIVE_SHIP_RUNTIME&&(group!==null||grants.length))return false;
  if(group!==null&&(!networkStrictKeysG(group,['mode','revision','untilS'])||!['INDIVIDUAL','ACTIVE','SILENT','PLAYER_SEARCH','ALLY_SEARCH'].includes(group.mode)||!Number.isInteger(group.revision)||group.revision<0||!Number.isFinite(group.untilS)||group.untilS<now||group.untilS>now+NETWORK_POLICY_G.groupLeaseS))return false;
  for(const q of grants){
    if(!networkStrictKeysG(q,['fileId','primary','untilS','stateAtS','stateM','covariance','domain'])||!Number.isInteger(q.fileId)||q.fileId<=0||!networkMemberG(ENGAGEMENT_RUNTIME.ships.get(q.primary))||!Number.isFinite(q.untilS)||q.untilS<now||q.untilS>now+NETWORK_POLICY_G.leaseS||!Number.isFinite(q.stateAtS)||q.stateAtS>now||now-q.stateAtS>NETWORK_POLICY_G.freshS||q.domain!=='AIR'||!Array.isArray(q.stateM)||q.stateM.length!==6||!q.stateM.every(Number.isFinite)||!networkSpdG(q.covariance))return false;
  }return true;
}
function networkAcceptControlG(r,senderId,group,grants){
  const n=prepareNetworkG(r),now=networkNowG();
  if(group&&r!==ACTIVE_SHIP_RUNTIME&&(!n.groupLease||group.revision>=n.groupLease.revision)){if(n.groupBase===null)n.groupBase=observerC(r).emcon;n.groupLease={...group};}
  for(const grant of grants){
    if(!n.settings.cooperativeDefense||!n.settings.shareTracks)continue;const tr=observerC(r).tracks.get(grant.fileId),e=tr?networkLocalEstimateG(tr):null,g=networkEstimateG(grant.stateM,grant.covariance,grant.stateAtS,now,grant.domain);
    if(tr&&networkLocalAgeG(tr)<=NETWORK_POLICY_G.freshS&&e&&tr.domain===grant.domain&&networkNisG(e,g)<=36)n.leases.set(tr.trackId,{...jsonSafeCloneV48Wip11A(grant),issuer:senderId});
  }
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
function networkGroupPacketG(sender,receiver){
  if(sender!==ACTIVE_SHIP_RUNTIME)return null;const n=prepareNetworkG(sender);return {mode:n.settings.groupEmcon,revision:n.groupRevision,untilS:networkNowG()+NETWORK_POLICY_G.groupLeaseS};
}
function networkSetRadarG(r,value){
  if(r===ACTIVE_SHIP_RUNTIME){if(emconActive!==value){emconActive=value;const btn=document.getElementById('emconBtn');if(btn){btn.textContent=value?'EMCON ON':'EMCON OFF';btn.style.color=value?'rgba(100,255,100,.9)':'rgba(255,100,100,.9)';}}}
  else observerC(r).emcon=value;
}
function networkRestoreIndividualG(r){const n=r.combatSystem.networkG;if(!n)return;if(n.groupBase!==null)networkSetRadarG(r,n.groupBase);n.groupBase=null;n.groupLease=null;}
function networkGroupStepG(r){
  const n=prepareNetworkG(r),now=networkNowG();let mode='INDIVIDUAL';
  if(r===ACTIVE_SHIP_RUNTIME){
    const connected=n.settings.enabled&&networkConnectedPeersG(r).length>0;mode=connected?n.settings.groupEmcon:'INDIVIDUAL';
    if(mode!=='INDIVIDUAL'&&n.groupBase===null)n.groupBase=emconActive;
  }else if(n.settings.enabled&&n.groupLease&&n.groupLease.untilS>=now&&networkConnectedPeersG(r).some(q=>q.entityId===ACTIVE_SHIP_RUNTIME.entityId))mode=n.groupLease.mode;
  if(mode==='INDIVIDUAL'){networkRestoreIndividualG(r);return;}
  const silent=mode==='SILENT'||mode==='PLAYER_SEARCH'&&r!==ACTIVE_SHIP_RUNTIME||mode==='ALLY_SEARCH'&&r===ACTIVE_SHIP_RUNTIME;
  networkSetRadarG(r,silent);
}
function networkIndividualCommandG(){
  const r=ACTIVE_SHIP_RUNTIME,n=r?.combatSystem?.networkG;if(!n)return;
  networkRestoreIndividualG(r);n.settings.groupEmcon='INDIVIDUAL';n.groupRevision++;networkUpdateUiG();
}
function networkOverrideRadarG(r){
  const n=r?.combatSystem?.networkG;if(!n)return;const current=r===ACTIVE_SHIP_RUNTIME?emconActive:observerC(r).emcon;
  networkRestoreIndividualG(r);if(r===ACTIVE_SHIP_RUNTIME){n.settings.groupEmcon='INDIVIDUAL';n.groupRevision++;}networkSetRadarG(r,current);networkUpdateUiG();
}
function networkSettingsG(r){return {...prepareNetworkG(r).settings};}
function networkExportElectronicG(r){const q=electronicSettingsF(r),n=r.combatSystem.networkG;if(n?.groupBase!==null&&n?.groupBase!==undefined)q.emcon=n.groupBase;return q;}
function networkCommandG(id,command){
  const r=ENGAGEMENT_RUNTIME.ships.get(id);if(!networkMemberG(r))return {ok:false,reason:'AUTHENTICATED_ALLY_REQUIRED'};
  if(!command||typeof command!=='object'||Array.isArray(command)||Object.keys(command).some(k=>!['enabled','shareTracks','cooperativeDefense','groupEmcon'].includes(k))||['enabled','shareTracks','cooperativeDefense'].some(k=>k in command&&typeof command[k]!=='boolean')||'groupEmcon'in command&&(!['INDIVIDUAL','ACTIVE','SILENT','PLAYER_SEARCH','ALLY_SEARCH'].includes(command.groupEmcon)||r!==ACTIVE_SHIP_RUNTIME))return {ok:false,reason:'NETWORK_COMMAND_FIELDS'};
  const n=prepareNetworkG(r);if('groupEmcon'in command&&command.groupEmcon!==n.settings.groupEmcon){networkRestoreIndividualG(r);n.groupRevision++;}
  Object.assign(n.settings,command);
  if(!n.settings.enabled){n.queue.length=0;n.leases.clear();for(const p of n.peers.values()){p.connected=false;p.reason='RADIO_OFF';}networkRestoreIndividualG(r);}
  if(!n.settings.cooperativeDefense)n.leases.clear();networkUpdateUiG();return {ok:true,settings:{...n.settings}};
}
function validateNetworkSettingsG(q,errors,role='PLAYER'){
  if(!networkStrictKeysG(q,['schema','enabled','shareTracks','cooperativeDefense','groupEmcon'])||q.schema!==NETWORK_POLICY_G.schema||['enabled','shareTracks','cooperativeDefense'].some(k=>typeof q[k]!=='boolean')||!['INDIVIDUAL','ACTIVE','SILENT','PLAYER_SEARCH','ALLY_SEARCH'].includes(q.groupEmcon)||role!=='PLAYER'&&q.groupEmcon!=='INDIVIDUAL'||role==='ENEMY'&&(q.enabled||q.shareTracks||q.cooperativeDefense))errors.push('NETWORK_G_SETTINGS');
}
function migrateNetworkSaveG(src,migrations){
  if(src.fleet&&!['AEGIS_NAVAL_PHYSICAL_FLEET_F_1','AEGIS_NAVAL_PHYSICAL_FLEET_B_1'].includes(src.fleet.schema))return;
  if(src.ship&&!Object.hasOwn(src.ship,'network'))src.ship.network={schema:NETWORK_POLICY_G.schema,enabled:true,shareTracks:true,cooperativeDefense:true,groupEmcon:'INDIVIDUAL'};
  for(const q of src.fleet?.ships??[])if(!Object.hasOwn(q,'network'))q.network={schema:NETWORK_POLICY_G.schema,enabled:q.role==='ALLY',shareTracks:q.role==='ALLY',cooperativeDefense:q.role==='ALLY',groupEmcon:'INDIVIDUAL'};
  migrations.push({id:'LEGACY_FRIENDLY_NETWORK_G',policy:'LOCAL_ONLY_OLD_STATE_WITH_FRESH_NETWORK_SETTINGS_NO_REPORTS_OR_LEASES'});
}
function networkTransferAliasG(r,oldId,newId){
  const n=r.combatSystem.networkG;if(!n)return;const old=observerC(r).tracks.get(oldId),next=observerC(r).tracks.get(newId),a=old&&networkLocalEstimateG(old),b=next&&networkLocalEstimateG(next);if(!a||!b||networkNisG(a,b)>36)return;
  const lease=n.leases.get(oldId);if(lease){n.leases.delete(oldId);n.leases.set(newId,lease);}if(n.waitSince.has(oldId)){n.waitSince.set(newId,n.waitSince.get(oldId));n.waitSince.delete(oldId);}
  for(const f of n.files.values())if(f.localTrackId===oldId)f.localTrackId=newId;
}
