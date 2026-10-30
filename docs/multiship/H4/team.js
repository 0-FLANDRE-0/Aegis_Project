// LIVE_CANONICAL. Received navigation, local observations and launch receipts only.
// Formation/leases/ROE thresholds are SIM-TUNE, not real naval doctrine.
const TEAM_POLICY_H4=Object.freeze({schema:'AEGIS_TEAM_TACTICS_H4_1',packet:'AEGIS_TEAM_PACKET_H4_1',periodTicks:12,sendTicks:30,latencyTicks:18,freshS:2,leaseS:1.8,waitS:2.4,salvoHoldS:90,maxFiles:96,maxBids:16,maxQueue:16,maxReceipts:8,maxLog:64,intentHoldS:30});
function teamDefaultsH4(r){return {schema:TEAM_POLICY_H4.schema,enabled:false,mission:'ESCORT',formation:'LINE_ASTERN',spacingM:2000,surfaceRoe:r.role==='ENEMY'?'SELF_DEFENSE':'IDENTIFIED_ONLY'};}
function prepareTeamH4(r){
  if(r.combatSystem.teamH4)return r.combatSystem.teamH4;
  const settings=r.restoredTeamH4??teamDefaultsH4(r);delete r.restoredTeamH4;
  const s={settings:{...settings},queue:[],peers:new Map(),linkSeenH4:false,sequence:0,lastSendStep:-1,lastStep:-1,evaluations:0,role:'INDEPENDENT',reason:'TEAM_OFF',formation:null,leases:new Map(),choices:new Map(),outbound:[],wait:new Map(),receipts:[],receivedReceiptsH4:new Map(),receiptSerial:0,intents:new Map(),origins:new Map(),log:[]};
  r.combatSystem.teamH4=s;claimShipMutableRootA(r,'teamH4',s);return s;
}
function teamSettingsH4(r){return {...prepareTeamH4(r).settings};}
function teamLogH4(r,action,reason,extra={}){const s=prepareTeamH4(r);s.log.push({step:simStepCounter,action,reason,...extra});if(s.log.length>TEAM_POLICY_H4.maxLog)s.log.shift();}
function teamYieldNavigationH4(r){const m=r.combatSystem.maneuverH2;if(m?.commandSourceH4==='FORMATION')maneuverYieldH2(r);const s=r.combatSystem.teamH4;if(s)s.formation=null;}
function teamClearH4(r,reason){const s=r.combatSystem.teamH4;if(!s)return;teamYieldNavigationH4(r);s.queue.length=0;s.peers.clear();s.linkSeenH4=false;s.leases.clear();s.choices.clear();s.wait.clear();s.outbound=[];s.formation=null;s.reason=reason;}
function resetTeamFleetH4(){for(const r of [ACTIVE_SHIP_RUNTIME,...physicalShipsB()]){const old=r.combatSystem.teamH4;if(old&&!r.restoredTeamH4)r.restoredTeamH4={...old.settings};teamClearH4(r,'LIFECYCLE');r.combatSystem.teamH4=null;prepareTeamH4(r);}}
function retireTeamH4(r){teamClearH4(r,'OWNER_RETIRED');r.combatSystem.teamH4=null;}
function validateTeamSettingsH4(q,errors){if(!networkStrictKeysG(q,['schema','enabled','mission','formation','spacingM','surfaceRoe'])||q.schema!==TEAM_POLICY_H4.schema||typeof q.enabled!=='boolean'||!['ESCORT','SURFACE_ACTION'].includes(q.mission)||!['LINE_ASTERN','PORT_SCREEN','STARBOARD_SCREEN'].includes(q.formation)||![1000,2000,4000].includes(q.spacingM)||!['IDENTIFIED_ONLY','SELF_DEFENSE'].includes(q.surfaceRoe))errors.push('TEAM_H4_SETTINGS');}
function migrateTeamSaveH4(src,migrations){
  if(src.fleet&&!['AEGIS_NAVAL_PHYSICAL_FLEET_H3_1','AEGIS_NAVAL_PHYSICAL_FLEET_H2_1','AEGIS_NAVAL_PHYSICAL_FLEET_H1_1','AEGIS_NAVAL_PHYSICAL_FLEET_G_1','AEGIS_NAVAL_PHYSICAL_FLEET_F_1','AEGIS_NAVAL_PHYSICAL_FLEET_B_1'].includes(src.fleet.schema))return;
  const legacy={...teamDefaultsH4(ACTIVE_SHIP_RUNTIME),enabled:false,surfaceRoe:'IDENTIFIED_ONLY'};
  if(src.ship&&!Object.hasOwn(src.ship,'team'))src.ship.team={...legacy};
  for(const q of src.fleet?.ships??[])if(!Object.hasOwn(q,'team'))q.team={...legacy};
  migrations.push({id:'LEGACY_TEAM_H4',policy:'OFF_IDENTIFIED_ONLY_NO_COMMAND_LEASES_OR_INTENT'});
}
function teamCommandH4(id,c){
  const r=fleetOwnerG(id),bad=reason=>({ok:false,reason});if(!r)return bad('FRIENDLY_OWNER_REQUIRED');
  const toggle=networkStrictKeysG(c,['enabled'])&&typeof c.enabled==='boolean',mission=networkStrictKeysG(c,['mission','formation','spacingM'])&&['ESCORT','SURFACE_ACTION'].includes(c.mission)&&['LINE_ASTERN','PORT_SCREEN','STARBOARD_SCREEN'].includes(c.formation)&&[1000,2000,4000].includes(c.spacingM),roe=networkStrictKeysG(c,['surfaceRoe'])&&['IDENTIFIED_ONLY','SELF_DEFENSE'].includes(c.surfaceRoe);
  if(!toggle&&!mission&&!roe)return bad('TEAM_COMMAND_FIELDS');
  const s=prepareTeamH4(r);teamClearH4(r,'OPERATOR_TEAM_CHANGED');Object.assign(s.settings,c);if(roe){s.intents.clear();s.origins.clear();}
  attackCancelH3(r,'TEAM_COMMAND_CHANGED');teamLogH4(r,'COMMAND','OPERATOR_TEAM_CHANGED');fleetUpdateUiG(true);return {ok:true,settings:{...s.settings}};
}
function teamActiveH4(r){return networkMemberG(r)&&prepareTeamH4(r).settings.enabled&&prepareNetworkG(r).settings.enabled&&!shipEquipmentOfflineV1(r);}
function teamFreshPeerH4(r,id){const q=prepareTeamH4(r).peers.get(id);return q&&networkNowG()-q.receivedAtS<=TEAM_POLICY_H4.freshS&&networkNowG()-q.sentAtS<=TEAM_POLICY_H4.freshS?q:null;}
function teamStateValidH4(q,now,maxAge=TEAM_POLICY_H4.freshS){return networkStrictKeysG(q,['stateAtS','stateM','covariance'])&&Number.isFinite(q.stateAtS)&&q.stateAtS>=0&&q.stateAtS<=now+1e-8&&now-q.stateAtS<=maxAge&&Array.isArray(q.stateM)&&q.stateM.length===6&&q.stateM.every((v,i)=>Number.isFinite(v)&&Math.abs(v)<(i<3?2e7:5000))&&!!networkSpdG(q.covariance);}
function teamProtectedH4(r,tr){return ['FRIEND','NEUTRAL','TRAINING_TARGET'].includes(tr.identity)||['FRIEND','NEUTRAL','TRAINING_TARGET'].includes(tr._operatorIdentity)||tr.iffF?.authenticatedFriendly||!!networkProtectionG(r,tr);}
function teamSurfaceEstimateH4(r,tr){if(!tr?.confirmed||tr.domain!=='SURFACE'||tr.sensorDetected===false||tr.memActive||tr.reacquiring||networkLocalAgeG(tr)>2||teamProtectedH4(r,tr))return null;const e=networkLocalEstimateG(tr);return e&&e.x.every(Number.isFinite)?e:null;}
function teamIntentIdentityH4(r,tr){
  if(prepareTeamH4(r).settings.surfaceRoe!=='SELF_DEFENSE'||!teamSurfaceEstimateH4(r,tr))return null;
  const q=prepareTeamH4(r).intents.get(tr.trackId);return q?.track===tr&&q.untilS>=networkNowG()?'HOSTILE':null;
}
function teamObserveIntentH4(r){
  const s=prepareTeamH4(r),now=networkNowG(),tracks=observerC(r).tracks;
  for(const [id,q]of s.intents){const weapon=tracks.get(q.weaponTrackId);if(q.untilS<now||q.track!==tracks.get(id)||!teamSurfaceEstimateH4(r,q.track)||weapon&&(weapon!==q.weaponTrack||teamProtectedH4(r,weapon)))s.intents.delete(id);}
  for(const [id,q]of s.origins)if(q.untilS<now||q.track!==tracks.get(id))s.origins.delete(id);
  if(s.settings.surfaceRoe!=='SELF_DEFENSE'||tracks.size>TEAM_POLICY_H4.maxFiles||shipEquipmentOfflineV1(r))return;
  const surfaces=[...tracks.values()].map(tr=>({tr,e:teamSurfaceEstimateH4(r,tr)})).filter(q=>q.e).slice(0,TEAM_POLICY_H4.maxBids);
  for(const tr of tracks.values()){
    if(!tr.confirmed||tr.classification!=='ASM'||tr.classificationConfidence<.7||tr.sensorDetected===false||tr.memActive||tr.reacquiring||networkLocalAgeG(tr)>1||teamProtectedH4(r,tr)||!['HOSTILE','ASSUMED_HOSTILE'].includes(tr.identity)||tr.engagementAuthority!=='AUTO_AUTHORIZED')continue;
    const e=networkLocalEstimateG(tr);if(!e||e.x[2]>400||e.x[2]<0)continue;
    const n=r.navigation,dx=e.x[0]-worldToMeters(n.positionWorld.x),dy=e.x[1]-worldToMeters(n.positionWorld.y),vx=e.x[3]-worldSpeedToMps(n.vx??0),vy=e.x[4]-worldSpeedToMps(n.vy??0),vv=vx*vx+vy*vy,t=vv>1?-(dx*vx+dy*vy)/vv:0;
    if(Math.hypot(e.x[3],e.x[4])<150||t<0||t>120||Math.hypot(dx+vx*t,dy+vy*t)>800)continue;
    let record=s.origins.get(tr.trackId);
    if(!record){
      const candidates=[];for(const q of surfaces){const ax=e.x[0]-q.e.x[0],ay=e.x[1]-q.e.x[1],ux=e.x[3]-q.e.x[3],uy=e.x[4]-q.e.x[4],uv=ux*ux+uy*uy,back=uv>1?(ax*ux+ay*uy)/uv:-1,miss=Math.hypot(ax-ux*back,ay-uy*back),sigma=2*Math.sqrt(e.P[0]+e.P[7]+q.e.P[0]+q.e.P[7]+back*back*(e.P[21]+e.P[28]+q.e.P[21]+q.e.P[28]));if(back>=0&&back<=6&&miss<=180&&sigma<=300)candidates.push(q);}
      if(candidates.length!==1)continue;record={track:tr,surface:candidates[0].tr,firstAtS:now,measurementAtS:now-networkLocalAgeG(tr),hits:1,untilS:now+4};s.origins.set(tr.trackId,record);
    }else if(record.track!==tr||record.surface!==tracks.get(record.surface.trackId)||!teamSurfaceEstimateH4(r,record.surface)){s.origins.delete(tr.trackId);continue;}
    const stamp=now-networkLocalAgeG(tr);if(stamp>record.measurementAtS+1e-6){record.hits++;record.measurementAtS=stamp;}
    if(record.hits>=3&&now-record.firstAtS>=.8){const old=s.intents.get(record.surface.trackId);s.intents.set(record.surface.trackId,{track:record.surface,untilS:now+TEAM_POLICY_H4.intentHoldS,weaponTrackId:tr.trackId,weaponTrack:tr,evidence:'LOCAL_WEAPON_ORIGIN_AND_INBOUND',firstAtS:record.firstAtS});if(!old)teamLogH4(r,'INTENT','OBSERVED_SELF_DEFENSE_ORIGIN',{trackId:record.surface.trackId,weaponTrackId:tr.trackId});}
  }
}
function teamBuildBidsH4(r){
  const rows=[],now=networkNowG();if(!teamActiveH4(r)||!prepareNetworkG(r).settings.shareTracks||prepareTeamH4(r).settings.mission!=='SURFACE_ACTION'||observerC(r).tracks.size>TEAM_POLICY_H4.maxFiles)return rows;
  for(const tr of observerC(r).tracks.values()){
    if(rows.length>=TEAM_POLICY_H4.maxBids)break;const g=attackObservationGateH3(r,tr),c=g.ok?attackConsentH3(r,tr):null;if(!c)continue;
    const e=g.estimate,n=r.navigation,rangeM=Math.hypot(e.x[0]-worldToMeters(n.positionWorld.x),e.x[1]-worldToMeters(n.positionWorld.y)),h=r.weapons.harpoon,coarse=attackActiveH3(r)&&!r.combatSystem.tacticalH1?.summary?.emergency&&!!h?.tubes?.length&&h.tubes.filter(q=>q.loaded).length>ATTACK_POLICY_H3.reserve&&!h.routeDraft?.editing&&!h.routeDraft?.pointsM?.length&&rangeM>=4000&&rangeM<=140000,preview=coarse?teamNativeBidH4(r,tr):{ok:false},eligible=coarse&&preview.ok;
    rows.push({fileId:tr.trackId,stateAtS:now,stateM:e.x,covariance:e.P,remaining:Math.min(2,c.remaining),consentUntilS:c.untilS,eligible,cost:rangeM/1000+20*(1-clamp(tr.fireControlQuality??tr.trackQuality??0,0,1))});
  }return rows;
}
function teamNativeBidH4(r,tr){
  // Synchronous preview only: save/restore the exact canonical capability in finally.
  // No request/release port is called here. Manual pending preparation is not borrowed.
  const a=prepareAttackH3(r),s=prepareTeamH4(r),h=r.weapons.harpoon;if(h.pending)return {ok:!!h.pending.attackH3&&h.pending.trackId===tr.trackId};
  const prior=a.releaseToken,token={ownerId:r.entityId,trackId:tr.trackId};Object.defineProperty(token,'track',{value:tr});a.releaseToken=token;s.previewingH4=true;
  try{const q=attackNativePreviewH3(r,tr.trackId,token);return q.ok||q.reason==='LAUNCHER_COOLDOWN'?{ok:true}:q;}finally{s.previewingH4=false;a.releaseToken=prior;}
}
function teamOwnNavigationReportH4(r,q){
  // An authenticated FRIEND relay can be the observer's own radar return.
  // Exclude only a tight 2-sigma ellipse inside our known central hull footprint.
  // Nearby vessels, neutral contacts, stale or broad reports remain protected.
  if(q.identity!=='FRIEND'||q.ageS>2||q.localTrackId!==null||!q.positionM||!q.velocityMps||!q.covariance||!q.sources?.length||q.sources.some(s=>s.kind!=='TRACK'))return false;
  const n=r.navigation,dx=q.positionM.x-worldToMeters(n.positionWorld.x),dy=q.positionM.y-worldToMeters(n.positionWorld.y),c=Math.cos(n.heading),s=Math.sin(n.heading),x=dx*c+dy*s,y=-dx*s+dy*c,P=q.covariance,px=c*c*P[0]+2*c*s*P[1]+s*s*P[7],py=s*s*P[0]-2*c*s*P[1]+c*c*P[7],beam=Math.max(...resolveShipProfile(r.profileId).geometry.hullStations.map(v=>v[1]));
  return Math.abs(x)+2*Math.sqrt(Math.max(0,px))<30&&Math.abs(y)+2*Math.sqrt(Math.max(0,py))<beam*.95&&Math.hypot(q.velocityMps.x-worldSpeedToMps(n.vx??0),q.velocityMps.y-worldSpeedToMps(n.vy??0))<5;
}
function teamMatchLocalH4(r,state){const now=networkNowG(),e=networkEstimateG(state.stateM,state.covariance,state.stateAtS,now,'SURFACE'),rows=[];for(const tr of observerC(r).tracks.values()){const q=teamSurfaceEstimateH4(r,tr);if(q){const nis=networkNisG(q,e);if(nis<=16)rows.push({tr,nis});}}rows.sort((a,b)=>a.nis-b.nis||a.tr.trackId-b.tr.trackId);return rows.length===1||rows.length>1&&rows[1].nis-rows[0].nis>4?rows[0].tr:null;}
function teamValidatePacketH4(sender,receiver,p){
  const now=networkNowG();if(!teamActiveH4(receiver)||!networkMemberG(sender)||!networkLinkPathG(sender,receiver).ok||!networkStrictKeysG(p,['schema','sequence','sentAtS','mission','navigation','bids','receipts','grants'])||p.schema!==TEAM_POLICY_H4.packet||!Number.isInteger(p.sequence)||p.sequence<1||!Number.isFinite(p.sentAtS)||p.sentAtS>now||now-p.sentAtS>2||!['ESCORT','SURFACE_ACTION'].includes(p.mission))return false;
  if(!networkStrictKeysG(p.navigation,['stateAtS','stateM','covariance','headingRad'])||!Number.isFinite(p.navigation.headingRad)||Math.abs(p.navigation.headingRad)>Math.PI+1e-8||!teamStateValidH4(({stateAtS:p.navigation.stateAtS,stateM:p.navigation.stateM,covariance:p.navigation.covariance}),now))return false;
  if(!Array.isArray(p.bids)||p.bids.length>16||!Array.isArray(p.receipts)||p.receipts.length>8||!Array.isArray(p.grants)||p.grants.length>16||new Set(p.bids.map(q=>q?.fileId)).size!==p.bids.length||new Set(p.receipts.map(q=>q?.serial)).size!==p.receipts.length)return false;
  const state=q=>({stateAtS:q.stateAtS,stateM:q.stateM,covariance:q.covariance});
  for(const q of p.bids)if(!networkStrictKeysG(q,['fileId','stateAtS','stateM','covariance','remaining','consentUntilS','eligible','cost'])||!Number.isInteger(q.fileId)||q.fileId<=0||!teamStateValidH4(state(q),now)||![1,2].includes(q.remaining)||!Number.isFinite(q.consentUntilS)||q.consentUntilS<now||q.consentUntilS>now+120||typeof q.eligible!=='boolean'||!Number.isFinite(q.cost)||q.cost<0||q.cost>1e6)return false;
  for(const q of p.receipts)if(!networkStrictKeysG(q,['serial','releasedAtS','stateAtS','stateM','covariance'])||!Number.isInteger(q.serial)||q.serial<1||!Number.isFinite(q.releasedAtS)||q.releasedAtS>now||q.releasedAtS<0||now-q.releasedAtS>90||!teamStateValidH4(state(q),now,90)||q.stateAtS!==q.releasedAtS)return false;
  if(sender!==ACTIVE_SHIP_RUNTIME&&p.grants.length)return false;
  for(const q of p.grants)if(!networkStrictKeysG(q,['fileId','primary','untilS','quota','stateAtS','stateM','covariance'])||!Number.isInteger(q.fileId)||q.fileId<=0||![ACTIVE_SHIP_RUNTIME.entityId,receiver.entityId].includes(q.primary)||!Number.isFinite(q.untilS)||q.untilS<now||q.untilS>now+TEAM_POLICY_H4.leaseS||!Number.isInteger(q.quota)||q.quota<0||q.quota>2||!teamStateValidH4(state(q),now))return false;
  return true;
}
function teamReceiveH4(r,sender,p){
  if(!teamValidatePacketH4(sender,r,p))return {ok:false,reason:'TEAM_PACKET_INVALID'};
  const s=prepareTeamH4(r),prior=s.peers.get(sender.entityId);if(prior&&p.sequence<=prior.sequence)return {ok:false,reason:'TEAM_PACKET_REPLAY'};
  const q={...jsonSafeCloneV48Wip11A(p),receivedAtS:networkNowG(),senderId:sender.entityId};if(!prepareNetworkG(r).settings.shareTracks){q.bids=[];q.receipts=[];q.grants=[];}s.peers.set(sender.entityId,q);s.linkSeenH4=true;
  for(const receipt of q.receipts){const key=JSON.stringify([sender.entityId,receipt.serial]);if(!s.receivedReceiptsH4.has(key)&&s.receivedReceiptsH4.size<16)s.receivedReceiptsH4.set(key,{...jsonSafeCloneV48Wip11A(receipt),senderId:sender.entityId});}
  for(const grant of q.grants){const tr=observerC(r).tracks.get(grant.fileId);if(tr&&teamMatchLocalH4(r,grant)===tr)s.leases.set(tr.trackId,{...jsonSafeCloneV48Wip11A(grant),track:tr,issuer:sender.entityId});}
  return {ok:true};
}
function teamReceiptCountH4(r,state){const now=networkNowG(),s=prepareTeamH4(r),e=networkEstimateG(state.stateM,state.covariance,state.stateAtS,now,'SURFACE'),rows=[...s.receipts,...s.receivedReceiptsH4.values()];return rows.filter(q=>now-q.releasedAtS<=90&&networkNisG(e,networkEstimateG(q.stateM,q.covariance,q.stateAtS,now,'SURFACE'))<=16).length;}
function teamCoordinateH4(r){
  const s=prepareTeamH4(r);s.outbound=[];if(r!==ACTIVE_SHIP_RUNTIME||!teamActiveH4(r)||!prepareNetworkG(r).settings.shareTracks||s.settings.mission!=='SURFACE_ACTION')return;
  const now=networkNowG(),peer=[...s.peers.keys()].map(id=>teamFreshPeerH4(r,id)).find(q=>q?.mission==='SURFACE_ACTION');if(!peer)return;
  const local=teamBuildBidsH4(r),used=new Set();
  for(const bid of peer.bids){
    const tr=teamMatchLocalH4(r,bid),own=tr&&local.find(q=>q.fileId===tr.trackId),p=networkEstimateG(bid.stateM,bid.covariance,bid.stateAtS,now,'SURFACE');if(used.has(tr?.trackId))continue;if(tr)used.add(tr.trackId);
    const key=JSON.stringify([peer.senderId,bid.fileId]),choices=[...(own?.eligible?[{id:r.entityId,cost:own.cost}]:[]),...(bid.eligible?[{id:peer.senderId,cost:bid.cost}]:[])].sort((a,b)=>a.cost-b.cost||a.id.localeCompare(b.id)),old=s.choices.get(key);if(!choices.length)continue;
    let primary=choices[0].id,handoffUntilS=old?.handoffUntilS??0;
    if(old&&choices.some(q=>q.id===old.primary)&&now-old.sinceS<4)primary=old.primary;
    if(old&&old.primary!==primary)handoffUntilS=now+TEAM_POLICY_H4.leaseS;
    const quota=handoffUntilS>now?0:Math.max(0,2-teamReceiptCountH4(r,bid,peer)),choice={primary,sinceS:old?.primary===primary?old.sinceS:now,handoffUntilS,untilS:now+TEAM_POLICY_H4.leaseS};s.choices.set(key,choice);
    const g={primary,untilS:choice.untilS,quota,stateAtS:now,stateM:p.x,covariance:p.P};
    if(tr)s.leases.set(tr.trackId,{...g,fileId:tr.trackId,track:tr,issuer:r.entityId});s.outbound.push({recipient:peer.senderId,fileId:bid.fileId,...g});
  }
  for(const [key,q]of s.choices)if(q.untilS<now)s.choices.delete(key);
}
function teamAttackGateH4(r,tr){
  const s=prepareTeamH4(r),now=networkNowG();if(s.previewingH4===true||!teamActiveH4(r)||!prepareNetworkG(r).settings.shareTracks||s.settings.mission!=='SURFACE_ACTION')return {ok:true};
  const local=networkLocalEstimateG(tr);if(local&&teamReceiptCountH4(r,{stateAtS:now,stateM:local.x,covariance:local.P})>=2)return {ok:false,reason:'TEAM_SALVO_HOLD_NO_BDA'};
  const fresh=[...s.peers.keys()].map(id=>teamFreshPeerH4(r,id)).filter(Boolean),peer=fresh.find(q=>q.mission==='SURFACE_ACTION');if(!peer){if(s.linkSeenH4||fresh.length||networkMembersG().length<2)return {ok:true,reason:'INDIVIDUAL_LINK_FALLBACK'};if(!s.wait.has(tr.trackId))s.wait.set(tr.trackId,now);return now-s.wait.get(tr.trackId)>=TEAM_POLICY_H4.waitS?{ok:true,reason:'INDIVIDUAL_LINK_FALLBACK'}:{ok:false,reason:'TEAM_LINK_WARMUP'};}
  const lease=s.leases.get(tr.trackId);if(lease?.track===tr&&lease.untilS>=now&&teamMatchLocalH4(r,lease)===tr){s.wait.delete(tr.trackId);if(lease.quota===0)return {ok:false,reason:'TEAM_SALVO_HOLD_NO_BDA'};if(lease.primary!==r.entityId)return {ok:false,reason:'TEAM_OTHER_SHIP_ASSIGNED'};return teamReceiptCountH4(r,lease,peer)>=2?{ok:false,reason:'TEAM_SALVO_HOLD_NO_BDA'}:{ok:true};}
  if(!s.wait.has(tr.trackId))s.wait.set(tr.trackId,now);return now-s.wait.get(tr.trackId)>=TEAM_POLICY_H4.waitS?{ok:true,reason:'INDIVIDUAL_ASSIGNMENT_FALLBACK'}:{ok:false,reason:'TEAM_ASSIGNMENT_WAIT'};
}
function teamCommitReceiptH4(r,tr){const s=prepareTeamH4(r),e=networkLocalEstimateG(tr);if(!e)return;s.receipts.push({serial:++s.receiptSerial,releasedAtS:networkNowG(),stateAtS:networkNowG(),stateM:e.x,covariance:e.P});if(s.receipts.length>8)s.receipts.shift();teamLogH4(r,'RELEASE_RECEIPT','NO_DL_NO_BDA',{trackId:tr.trackId});}
function teamFormationH4(r){
  const s=prepareTeamH4(r);s.formation=null;if(!teamActiveH4(r)){s.role='INDEPENDENT';s.reason='TEAM_OFF_OR_LINK_OFF';return null;}if(r===ACTIVE_SHIP_RUNTIME){s.role='LEADER';s.reason='LEAD_OWN_NAVIGATION';return null;}
  const peer=teamFreshPeerH4(r,ACTIVE_SHIP_RUNTIME.entityId);if(!peer){s.role='INDEPENDENT';s.reason='LEADER_REPORT_LOST';return null;}
  const now=networkNowG(),p=networkEstimateG(peer.navigation.stateM,peer.navigation.covariance,peer.navigation.stateAtS,now,'SURFACE'),n=r.navigation,heading=peer.navigation.headingRad,spacing=s.settings.spacingM,side=s.settings.formation==='PORT_SCREEN'?-1:s.settings.formation==='STARBOARD_SCREEN'?1:0,a=side?-.3*spacing:-spacing,b=side*spacing,slot={x:p.x[0]+a*Math.cos(heading)-b*Math.sin(heading),y:p.x[1]+a*Math.sin(heading)+b*Math.cos(heading)},origin={x:worldToMeters(n.positionWorld.x),y:worldToMeters(n.positionWorld.y)},dx=slot.x-origin.x,dy=slot.y-origin.y,along=dx*Math.cos(heading)+dy*Math.sin(heading),error=Math.hypot(dx,dy),speedMps=Math.hypot(p.x[3],p.x[4]),goal=error<100?heading:Math.atan2(dy+p.x[4]*10,dx+p.x[3]*10),damage=getShipDamageEffects(r),speedKt=maneuverSpeedH2(r,clamp(speedMps/.514444+clamp(along/180,-8,8),error>300?6:0,28),damage),traffic=maneuverTrafficH2(r),candidates=[];
  const ownPeerTraffic={x:p.x[0],y:p.x[1],vx:p.x[3],vy:p.x[4],source:'H4_RECEIVED_SELF'};traffic.push(ownPeerTraffic);
  for(const [id,offset,kt]of [['STATION',0,speedKt],['PORT_BYPASS',-30,speedKt],['STARBOARD_BYPASS',30,speedKt],['HOLD',0,0]]){
    const headingRad=id==='HOLD'?n.heading:angNorm(goal+deg(offset)),prediction=maneuverPredictH2(r,headingRad,kt,30,damage);let guard=maneuverPathGuardH2(r,prediction,traffic),last=prediction.origin;
    if(guard.ok)for(const point of prediction.poses){const chart=attackChartGuardH3(last,point);if(!chart.ok){guard=chart;break;}last=point;}
    const future={x:slot.x+p.x[3]*30,y:slot.y+p.x[4]*30},score=guard.ok?-Math.hypot(prediction.final.x-future.x,prediction.final.y-future.y)/Math.max(1000,spacing)-.1*Math.abs(angNorm(headingRad-n.heading))-(id==='HOLD'?.3:0):-1e6;
    candidates.push({id,headingRad,speedKt:kt,score,guard});
  }
  candidates.sort((a,b)=>b.score-a.score);let choice=candidates[0];if(!choice.guard.ok)choice={id:'SAFETY_HOLD',headingRad:n.heading,speedKt:0,guard:choice.guard};
  s.role=side?'SCREEN':'ESCORT';s.reason=choice.id;s.formation={slotM:slot,errorM:error,leaderAgeS:now-peer.navigation.stateAtS,formation:s.settings.formation,spacingM:spacing,choice:{...choice},candidates};return choice;
}
function teamFixedStepH4(){
  const all=[ACTIVE_SHIP_RUNTIME,...physicalShipsB()],members=all.filter(networkMemberG),now=networkNowG();
  for(const r of all){const s=prepareTeamH4(r);s.receipts=s.receipts.filter(q=>now-q.releasedAtS<=90);for(const [key,q]of s.receivedReceiptsH4)if(now-q.releasedAtS>90)s.receivedReceiptsH4.delete(key);const due=s.queue.filter(q=>q.availableStep<=simStepCounter);s.queue=s.queue.filter(q=>q.availableStep>simStepCounter);for(const q of due){const sender=members.find(v=>v.entityId===q.senderId);if(sender)teamReceiveH4(r,sender,q.packet);}for(const [id,q]of s.peers)if(now-q.receivedAtS>2)s.peers.delete(id);for(const [id,q]of s.leases)if(q.untilS<now||observerC(r).tracks.get(id)!==q.track)s.leases.delete(id);for(const id of s.wait.keys())if(!observerC(r).tracks.has(id))s.wait.delete(id);
    if(simStepCounter%12===0&&s.lastStep!==simStepCounter){s.lastStep=simStepCounter;s.evaluations++;if(r===ACTIVE_SHIP_RUNTIME){s.role=teamActiveH4(r)?'LEADER':'INDEPENDENT';s.reason=teamActiveH4(r)?'LEAD_OWN_NAVIGATION':'TEAM_OFF_OR_LINK_OFF';}else if(!maneuverActiveH2(r)){s.formation=null;s.role='INDEPENDENT';s.reason='MANUAL_NAV';}teamObserveIntentH4(r);teamCoordinateH4(r);}}
  if(simStepCounter%30!==0)return;
  for(const sender of members){const s=prepareTeamH4(sender);if(!teamActiveH4(sender)||s.lastSendStep===simStepCounter)continue;s.lastSendStep=simStepCounter;
    const n=sender.navigation,P=new Array(36).fill(0);for(let i=0;i<6;i++)P[i*6+i]=i<3?100:1;
    const navigation={stateAtS:now,stateM:[worldToMeters(n.positionWorld.x),worldToMeters(n.positionWorld.y),8,worldSpeedToMps(n.vx??0),worldSpeedToMps(n.vy??0),0],covariance:P,headingRad:angNorm(n.heading)},bids=teamBuildBidsH4(sender),sequence=++s.sequence;
    for(const receiver of members){if(sender===receiver||!teamActiveH4(receiver)||!networkLinkPathG(sender,receiver).ok)continue;const target=prepareTeamH4(receiver);if(target.queue.length>=16)continue;
      const sharing=prepareNetworkG(sender).settings.shareTracks,packet={schema:TEAM_POLICY_H4.packet,sequence,sentAtS:now,mission:s.settings.mission,navigation,bids,receipts:sharing?s.receipts:[],grants:sharing?s.outbound.filter(q=>q.recipient===receiver.entityId).map(({recipient,...q})=>q):[]};
      target.queue.push({senderId:sender.entityId,availableStep:simStepCounter+18,packet:jsonSafeCloneV48Wip11A(packet)});
    }
  }
}
function teamSnapshotH4(){return {schema:TEAM_POLICY_H4.schema,truthUsed:false,remoteFireControl:false,ordnanceDatalink:false,policy:{...TEAM_POLICY_H4},ships:[ACTIVE_SHIP_RUNTIME,...physicalShipsB()].map(r=>{const s=prepareTeamH4(r);return {entityId:r.entityId,settings:{...s.settings},active:teamActiveH4(r),role:s.role,reason:s.reason,evaluations:s.evaluations,queued:s.queue.length,peers:[...s.peers.values()].map(q=>({senderId:q.senderId,ageS:networkNowG()-q.sentAtS,mission:q.mission,bids:q.bids.length,receipts:q.receipts.length})),formation:jsonSafeCloneV48Wip11A(s.formation),leases:[...s.leases].map(([trackId,{track,...q}])=>({trackId,...jsonSafeCloneV48Wip11A(q)})),receipts:s.receipts.map(q=>({serial:q.serial,releasedAtS:q.releasedAtS})),intents:[...s.intents].map(([trackId,q])=>({trackId,weaponTrackId:q.weaponTrackId,evidence:q.evidence,untilS:q.untilS})),log:s.log.map(q=>({...q}))};})};}
function teamSelfTestH4(){const P=new Array(36).fill(0);for(let i=0;i<6;i++)P[i*6+i]=1;const state={stateAtS:1,stateM:[100,200,8,0,0,0],covariance:P},q={schema:TEAM_POLICY_H4.schema,enabled:false,mission:'ESCORT',formation:'LINE_ASTERN',spacingM:2000,surfaceRoe:'IDENTIFIED_ONLY'},errors=[];validateTeamSettingsH4(q,errors);const invalid=[];validateTeamSettingsH4({...q,spacingM:0},invalid);const checks={freshState:teamStateValidH4(state,2),staleStateDenied:!teamStateValidH4(state,4),futureStateDenied:!teamStateValidH4(state,0),unexpectedFieldDenied:!teamStateValidH4({...state,foreignState:'NO'},2),nonFiniteDenied:!teamStateValidH4({...state,stateM:[NaN,0,0,0,0,0]},2),badCovarianceDenied:!teamStateValidH4({...state,covariance:new Array(36).fill(0)},2),strictSettings:errors.length===0,invalidSpacingDenied:invalid.length===1};return {checks,pass:Object.values(checks).every(Boolean)};}
