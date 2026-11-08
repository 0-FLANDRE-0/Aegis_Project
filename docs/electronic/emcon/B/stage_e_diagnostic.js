// TEST_ONLY: Commit-E deterministic network/lifecycle probes. Never packed into the product.
function emconEDiagnosticPairB(){
  const active=ACTIVE_SHIP_RUNTIME,ally=physicalShipsB().find(r=>r.role==='ALLY'&&r.faction==='FRIENDLY');
  if(!ally)throw Error('EMCON_B_E_ALLY_REQUIRED');return {active,ally};
}
function emconEConnectB(a,b){
  const now=networkNowG(),na=prepareNetworkG(a),nb=prepareNetworkG(b),pa=networkPeerG(na,b.entityId),pb=networkPeerG(nb,a.entityId);
  Object.assign(pa,{connected:true,lastReceivedS:now,reason:'DIAGNOSTIC_LINK'});Object.assign(pb,{connected:true,lastReceivedS:now,reason:'DIAGNOSTIC_LINK'});na.settings.enabled=nb.settings.enabled=true;
}
function emconEGroupB(mode,activeMaster=false,allyMaster=false){
  if(!['ACTIVE','SILENT','PLAYER_SEARCH','ALLY_SEARCH'].includes(mode))throw Error('EMCON_B_E_GROUP_MODE');
  const {active,ally}=emconEDiagnosticPairB();networkRestoreIndividualG(active);networkRestoreIndividualG(ally);networkSetRadarG(active,activeMaster);networkSetRadarG(ally,allyMaster);emconEConnectB(active,ally);
  const now=networkNowG(),an=prepareNetworkG(active),bn=prepareNetworkG(ally);an.settings.groupEmcon=mode;an.groupRevision++;bn.groupBase=allyMaster;bn.groupLease={mode,revision:an.groupRevision,untilS:now+NETWORK_POLICY_G.groupLeaseS};
  networkGroupStepG(active);networkGroupStepG(ally);return emconEGroupSnapshotB();
}
function emconEIndividualB(){
  const {active,ally}=emconEDiagnosticPairB(),an=prepareNetworkG(active),bn=prepareNetworkG(ally),now=networkNowG();an.settings.groupEmcon='INDIVIDUAL';an.groupRevision++;bn.groupLease={mode:'INDIVIDUAL',revision:an.groupRevision,untilS:now+NETWORK_POLICY_G.groupLeaseS};networkGroupStepG(active);networkGroupStepG(ally);return emconEGroupSnapshotB();
}
function emconEExpireFollowerLeaseB(){const {ally}=emconEDiagnosticPairB(),n=prepareNetworkG(ally);if(n.groupLease)n.groupLease.untilS=networkNowG()-1;networkGroupStepG(ally);return emconEGroupSnapshotB();}
function emconEGroupSnapshotB(){
  const {active,ally}=emconEDiagnosticPairB(),row=r=>({entityId:r.entityId,masterSilent:emconMasterSilentB(r),networkMode:emconNetworkModeB(r),state:emconExportStateB(r),network:networkSnapshotG().ships.find(q=>q.entityId===r.entityId)});
  return {active:row(active),ally:row(ally),communicationPolicy:'SEPARATE_UNCHANGED'};
}
function emconETacticalPulseB(){
  const r=ACTIVE_SHIP_RUNTIME,before=emconExportStateB(r),counts=getVlsCounts(),inventory=wip14a14DecisionInventory(counts);tacticalEvaluateH1(r,wip118ControlState,inventory,getShipDamageEffects());return {before,after:emconExportStateB(r),masterSilent:emconMasterSilentB(r)};
}
function emconEResetDetailsB(){resetElectronicFleetF();return emconLifecycleSnapshotB();}
function emconEDestroyB(id){return destroyShipRuntime(id);}
window.__EMCON_B_E_DIAG__=Object.freeze({group:emconEGroupB,individual:emconEIndividualB,expireFollower:emconEExpireFollowerLeaseB,snapshot:emconEGroupSnapshotB,tactical:emconETacticalPulseB,reset:emconEResetDetailsB,destroy:emconEDestroyB});
