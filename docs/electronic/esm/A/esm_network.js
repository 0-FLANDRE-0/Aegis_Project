// ESM_A Commit C — anonymous raw ESM transport. It is deliberately separate
// from NETWORK_G SELF/TRACK reports and never writes observerC tracks.
const ESM_A_NETWORK_SCHEMA='AEGIS_ESM_RAW_NETWORK_A_1';
const ESM_A_NETWORK_KEYS=Object.freeze(['schema','sequence','sentAtS','measurements']);
function esmNetworkPacketValidA(packet,sender,now){
  if(!esmKeysExactA(packet,ESM_A_NETWORK_KEYS)||packet.schema!==ESM_A_NETWORK_SCHEMA||!Number.isInteger(packet.sequence)||packet.sequence<1||!Number.isFinite(packet.sentAtS)||packet.sentAtS<0||packet.sentAtS>now+1e-8||now-packet.sentAtS>NETWORK_POLICY_G.coastS||!Array.isArray(packet.measurements)||packet.measurements.length>NETWORK_POLICY_G.maxReports)return {ok:false,reason:'ESM_RAW_PACKET'};
  const expectedReceiver=esmReceiverProfileA(sender)?.receiverId??null;if(!expectedReceiver)return {ok:false,reason:'RECEIVER_UNAVAILABLE'};
  const ids=new Set();for(const q of packet.measurements){const v=esmValidateRawA(q,now,sender.entityId,expectedReceiver);if(!v.ok)return {ok:false,reason:v.reason};if(ids.has(q.observationId))return {ok:false,reason:'ESM_RAW_DUPLICATE_IN_PACKET'};ids.add(q.observationId);}return {ok:true};
}
function esmNetworkReceiveA(receiver,senderId,packet){
  const sender=ENGAGEMENT_RUNTIME.ships.get(String(senderId)),state=prepareEsmA(receiver),now=networkNowG(),bad=reason=>{state.stats.rejected++;ESM_A_AUDIT.networkRejected++;return {ok:false,reason};};
  if(!networkMemberG(receiver)||!networkMemberG(sender)||sender===receiver||sender.faction!==receiver.faction)return bad('AUTHENTICATED_ALLY_REQUIRED');
  if(!networkLinkPathG(receiver,sender).ok)return bad('LINK_UNAVAILABLE');const valid=esmNetworkPacketValidA(packet,sender,now);if(!valid.ok)return bad(valid.reason);
  state.networkPeerSequence??=new Map();const previous=state.networkPeerSequence.get(sender.entityId)??0;if(packet.sequence<=previous)return bad('PACKET_REPLAY');
  // Packet and every raw DTO are fully validated before any sequence/contact mutation.
  state.networkPeerSequence.set(sender.entityId,packet.sequence);const accepted=esmAcceptRawA(receiver,packet.measurements,'NETWORK');if(!accepted.ok)return bad(accepted.reason);ESM_A_AUDIT.networkAccepted+=accepted.accepted;return {ok:true,accepted:accepted.accepted};
}
function esmNetworkReportRowsA(sender){
  const state=prepareEsmA(sender);state.networkSentIds??=new Map();const now=networkNowG();for(const [id,t]of state.networkSentIds)if(now-t>ELECTRONIC_POLICY_F.holdS)state.networkSentIds.delete(id);
  const rows=[];for(const q of state.outbox){if(state.networkSentIds.has(q.observationId)||now-q.measuredAtS>NETWORK_POLICY_G.coastS)continue;rows.push(q);if(rows.length>=NETWORK_POLICY_G.maxReports)break;}return rows;
}
function esmNetworkFixedStepA(_dt){
  const members=networkMembersG(),now=networkNowG();
  for(const receiver of members){const state=prepareEsmA(receiver),due=state.networkQueue.filter(q=>q.availableStep<=simStepCounter);state.networkQueue=state.networkQueue.filter(q=>q.availableStep>simStepCounter);for(const q of due)esmNetworkReceiveA(receiver,q.senderId,q.packet);}
  if(simStepCounter%NETWORK_POLICY_G.periodTicks!==0)return;
  for(const sender of members){const n=prepareNetworkG(sender),state=prepareEsmA(sender);if(!n.settings.enabled||state.lastNetworkSendStep===simStepCounter)continue;const rows=esmNetworkReportRowsA(sender);if(!rows.length)continue;state.lastNetworkSendStep=simStepCounter;const packet={schema:ESM_A_NETWORK_SCHEMA,sequence:++state.networkSequence,sentAtS:now,measurements:rows.map(esmJsonA)};
    for(const receiver of members){if(receiver===sender)continue;const path=networkLinkPathG(sender,receiver);if(!path.ok)continue;const target=prepareEsmA(receiver);if(target.networkQueue.length>=NETWORK_POLICY_G.maxQueue){target.stats.rejected++;continue;}target.networkQueue.push({senderId:sender.entityId,availableStep:simStepCounter+NETWORK_POLICY_G.latencyTicks,packet:esmJsonA(packet)});}
    state.networkSentIds??=new Map();for(const q of rows)state.networkSentIds.set(q.observationId,q.measuredAtS);
  }
}
function esmNetworkSnapshotA(r){const s=prepareEsmA(r);return {schema:ESM_A_NETWORK_SCHEMA,ownerEntityId:r.entityId,sequence:s.networkSequence,queue:s.networkQueue.length,peerSequences:[...(s.networkPeerSequence??new Map())],sentObservationIds:[...(s.networkSentIds??new Map()).keys()],observerTracksWritten:0,automaticAuthority:false};}
