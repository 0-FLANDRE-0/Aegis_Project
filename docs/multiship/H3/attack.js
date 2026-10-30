// LIVE_CANONICAL. Owner-local, measured surface attack utility. All constants SIM-TUNE.
// The capability below authorizes only native Harpoon release; it is never a DL.
const ATTACK_POLICY_H3=Object.freeze({schema:'AEGIS_SURFACE_ATTACK_H3_1',periodTicks:12,freshS:2,consentS:120,enemyCycleS:90,reserve:2,maxTracks:16,maxProtected:64,maxLog:64,maxFiles:96,maxTurnRad:2*Math.PI/3,corridorM:250,protectedMarginM:500});
function attackDefaultsH3(r){return {schema:ATTACK_POLICY_H3.schema,enabled:r.role==='ENEMY'};}
function prepareAttackH3(r){
  if(r.combatSystem.attackH3)return r.combatSystem.attackH3;
  const settings=r.restoredAttackH3??attackDefaultsH3(r);delete r.restoredAttackH3;
  const s={settings:{...settings},consents:new Map(),releaseToken:null,lastStep:-1,evaluations:0,plans:[],selectedTrackId:null,status:'WAIT',reason:'ATTACK_CONSENT_REQUIRED',lastReleaseS:-1e6,enemyRemaining:2,log:[]};
  r.combatSystem.attackH3=s;claimShipMutableRootA(r,'attackH3',s);return s;
}
function attackSettingsH3(r){return {...prepareAttackH3(r).settings};}
function attackActiveH3(r){return prepareAttackH3(r).settings.enabled&&tacticalActiveH1(r)&&!shipEquipmentOfflineV1(r);}
function attackLogH3(r,action,reason,trackId=null,extra={}){const s=prepareAttackH3(r);s.log.push({step:simStepCounter,action,reason,trackId,...extra});if(s.log.length>ATTACK_POLICY_H3.maxLog)s.log.shift();}
function attackCancelH3(r,reason='ATTACK_CANCELLED',revoke=false){
  const s=r.combatSystem.attackH3;if(!s)return;
  const h=r.weapons.harpoon;if(h?.pending?.attackH3){h.pending=null;h.lastResult='CANCELLED:'+reason;attackLogH3(r,'CANCEL',reason,s.selectedTrackId);}
  s.releaseToken=null;s.selectedTrackId=null;s.status='WAIT';s.reason=reason;if(revoke)s.consents.clear();
}
function resetAttackFleetH3(){for(const r of [ACTIVE_SHIP_RUNTIME,...physicalShipsB()]){const s=r.combatSystem.attackH3;if(s&&!r.restoredAttackH3)r.restoredAttackH3={...s.settings};attackCancelH3(r,'LIFECYCLE',true);r.combatSystem.attackH3=null;prepareAttackH3(r);}}
function validateAttackSettingsH3(q,errors){if(!networkStrictKeysG(q,['schema','enabled'])||q.schema!==ATTACK_POLICY_H3.schema||typeof q.enabled!=='boolean')errors.push('ATTACK_H3_SETTINGS');}
function migrateAttackSaveH3(src,migrations){
  if(src.fleet&&!['AEGIS_NAVAL_PHYSICAL_FLEET_H2_1','AEGIS_NAVAL_PHYSICAL_FLEET_H1_1','AEGIS_NAVAL_PHYSICAL_FLEET_G_1','AEGIS_NAVAL_PHYSICAL_FLEET_F_1','AEGIS_NAVAL_PHYSICAL_FLEET_B_1'].includes(src.fleet.schema))return;
  // Legacy saves must not silently acquire a new surface attack permission.
  if(src.ship&&!Object.hasOwn(src.ship,'attack'))src.ship.attack={schema:ATTACK_POLICY_H3.schema,enabled:false};
  for(const q of src.fleet?.ships??[])if(!Object.hasOwn(q,'attack'))q.attack={schema:ATTACK_POLICY_H3.schema,enabled:false};
  migrations.push({id:'LEGACY_SURFACE_ATTACK_H3',policy:'OFF_NO_CONSENT_PLANS_OR_FLIGHT_KNOWLEDGE'});
}
function attackObservationGateH3(r,tr){
  const bad=reason=>({ok:false,reason,truthUsed:false});if(!tr)return bad('NO_LOCAL_SURFACE_TRACK');
  if(tr.domain!=='SURFACE'&&tr.classification!=='SURFACE')return bad('NOT_SURFACE_TRACK');
  if(!tr.confirmed||tr.sensorDetected===false||tr.memActive||tr.reacquiring||networkLocalAgeG(tr)>ATTACK_POLICY_H3.freshS||networkLocalAgeG(tr)<0)return bad('LOCAL_SURFACE_TRACK_STALE');
  if(['FRIEND','NEUTRAL'].includes(tr.identity)||['FRIEND','NEUTRAL'].includes(tr._operatorIdentity)||tr.iffF?.authenticatedFriendly||networkProtectionG(r,tr))return bad('PROTECTED_IDENTITY');
  if(normalizeTrackOperatorIdentityA3(tr._operatorIdentity??tr.identity)!=='HOSTILE')return bad('HOSTILE_SURFACE_IDENTIFICATION_REQUIRED');
  const e=networkLocalEstimateG(tr);if(!e)return bad('INVALID_LOCAL_ESTIMATE');return {ok:true,estimate:e,truthUsed:false};
}
function attackCommandH3(id,c){
  const r=fleetOwnerG(id),bad=reason=>({ok:false,reason});if(!r)return bad('FRIENDLY_OWNER_REQUIRED');
  const toggle=networkStrictKeysG(c,['enabled'])&&typeof c.enabled==='boolean',grant=networkStrictKeysG(c,['authorizeTrackId','rounds'])&&Number.isInteger(c.authorizeTrackId)&&[1,2].includes(c.rounds),revoke=networkStrictKeysG(c,['revoke'])&&c.revoke===true;
  if(!toggle&&!grant&&!revoke)return bad('ATTACK_COMMAND_FIELDS');
  if(grant){const tr=observerC(r).tracks.get(c.authorizeTrackId),g=attackObservationGateH3(r,tr);if(!g.ok)return g;if(!(r.weapons.harpoon?.tubes?.length))return bad('MK141_NOT_INSTALLED');
    const s=prepareAttackH3(r);attackCancelH3(r,'NEW_ATTACK_CONSENT',true);s.consents.set(tr.trackId,{track:tr,remaining:c.rounds,untilS:networkNowG()+ATTACK_POLICY_H3.consentS});attackLogH3(r,'CONSENT','OPERATOR_AUTHORIZED',tr.trackId,{rounds:c.rounds});
  }else {const s=prepareAttackH3(r);attackCancelH3(r,toggle?'ATTACK_SWITCH_CHANGED':'CONSENT_REVOKED',true);if(toggle)s.settings.enabled=c.enabled;}
  fleetUpdateUiG(true);return {ok:true,settings:attackSettingsH3(r)};
}
function attackConsentH3(r,tr){
  const s=prepareAttackH3(r),now=networkNowG();
  if(r.role==='ENEMY')return s.enemyRemaining>0?{remaining:s.enemyRemaining,untilS:now+1,track:tr,mission:true}:null;
  const c=s.consents.get(tr.trackId);return c?.track===tr&&c.remaining>0&&c.untilS>=now?c:null;
}
function attackAuthorityH3(r,tr,token){
  const s=prepareAttackH3(r),bad=reason=>({ok:false,reason});
  if(!token||token!==s.releaseToken||token.track!==tr||token.ownerId!==r.entityId)return bad('ATTACK_CAPABILITY_REQUIRED');
  if(!attackActiveH3(r))return bad('ATTACK_AUTO_INACTIVE');
  if(observerC(r).tracks.size>ATTACK_POLICY_H3.maxFiles)return bad('LOCAL_PICTURE_CAPACITY');
  const g=attackObservationGateH3(r,tr);if(!g.ok)return g;if(!attackConsentH3(r,tr))return bad('ATTACK_CONSENT_EXPIRED');
  if(r.combatSystem.tacticalH1?.summary?.emergency)return bad('AIR_DEFENSE_PRIORITY');
  const h=r.weapons.harpoon;if(h.routeDraft?.editing||h.routeDraft?.pointsM?.length)return bad('MANUAL_HARPOON_ROUTE_PRIORITY');
  if(h.tubes.filter(t=>t.loaded).length<=ATTACK_POLICY_H3.reserve)return bad('HARPOON_AI_RESERVE');
  return {ok:true,mode:'SURFACE_ATTACK_H3',identity:'HOSTILE',truthUsed:false};
}
function attackNativePreviewH3(r,id,token){return r===ACTIVE_SHIP_RUNTIME?harpoonAutoTubeGateD(id,{attackH3:token}):r.weapons.executionD.context.attackPreviewH3(id,token);}
function attackProtectedH3(r){
  const rows=[],now=networkNowG();let overflow=false;
  const add=q=>{if(rows.length>=ATTACK_POLICY_H3.maxProtected)overflow=true;else rows.push(q);};
  for(const tr of observerC(r).tracks.values()){
    if(tr.domain!=='SURFACE'&&tr.classification!=='SURFACE')continue;
    if(!['FRIEND','NEUTRAL'].includes(tr.identity)&&!['FRIEND','NEUTRAL'].includes(tr._operatorIdentity)&&!tr.iffF?.authenticatedFriendly&&!networkProtectionG(r,tr))continue;
    const e=networkLocalEstimateG(tr);if(!e)return {rows,blocked:'PROTECTED_ESTIMATE_INVALID'};
    const age=networkLocalAgeG(tr);if(age>12||age<0)return {rows,blocked:'PROTECTED_PICTURE_STALE'};
    add({x:e.x[0],y:e.x[1],vx:e.x[3],vy:e.x[4],P:e.P,ageS:age,source:'LOCAL_PROTECTED'});
  }
  if(networkMemberG(r))for(const q of networkPictureG(r)){
    if(q.domain!=='SURFACE'||!['FRIEND','NEUTRAL'].includes(q.identity)||!q.positionM||!q.velocityMps)continue;
    if(q.ageS>12||q.ageS<0)return {rows,blocked:'PROTECTED_PICTURE_STALE'};
    add({x:q.positionM.x,y:q.positionM.y,vx:q.velocityMps.x,vy:q.velocityMps.y,P:q.covariance??null,ageS:q.ageS,source:'RECEIVED_PROTECTED'});
  }
  return {rows,blocked:overflow?'PROTECTED_PICTURE_CAPACITY':null};
}
function attackChartGuardH3(start,end){
  if(BATTLESPACE_DIAG_BYPASS)return {ok:true};
  // Exact 2D chart edge crossings, plus conservative 100 m coastal clearance.
  const a={x:metersToWorld(start.x),y:metersToWorld(start.y)},b={x:metersToWorld(end.x),y:metersToWorld(end.y)},pad=metersToWorld(100),dist=(p,u,v)=>{const x=v.x-u.x,y=v.y-u.y,t=clamp(((p.x-u.x)*x+(p.y-u.y)*y)/Math.max(1e-12,x*x+y*y),0,1);return Math.hypot(p.x-u.x-t*x,p.y-u.y-t*y);},cross=(u,v,p)=>(v.x-u.x)*(p.y-u.y)-(v.y-u.y)*(p.x-u.x);
  for(const island of terrainIslands){
    if(dist({x:island.cx,y:island.cy},a,b)>island.boundRadiusWorld+pad)continue;
    if(pointInTerrainPolygon(a.x,a.y,island.points)||pointInTerrainPolygon(b.x,b.y,island.points))return {ok:false,reason:'CHART_ROUTE_BLOCKED'};
    for(let i=0;i<island.points.length;i++){const u=island.points[i],v=island.points[(i+1)%island.points.length];if(cross(a,b,u)*cross(a,b,v)<=0&&cross(u,v,a)*cross(u,v,b)<=0||Math.min(dist(a,u,v),dist(b,u,v),dist(u,a,b),dist(v,a,b))<pad)return {ok:false,reason:'CHART_ROUTE_BLOCKED'};}
  }return {ok:true};
}
function attackLauncherMaskH3(r,spec){
  if(r.profileId!=='CG_52_LATE_TICONDEROGA')return {ok:false,reason:'MK141_MASK_NOT_REGISTERED'};
  const a=spec.axis,o={x:spec.muzzle.x+a.x*.7,y:spec.muzzle.y+a.y*.7,z:spec.muzzle.z+a.z*.7},hit=bunkerRaySource(o,a,24,null,.15);
  return hit?{ok:false,reason:'MK141_DEPARTURE_MASK',occluder:hit.name??hit.node??'REGISTERED_GEOMETRY'}:{ok:true};
}
function attackPathGuardH3(r,gate){
  const spec=resolveShipProfile(r.profileId).weapons.harpoon?.tubes.find(q=>q.id===gate.tubeId);if(!spec)return {ok:false,reason:'MK141_NOT_INSTALLED'};
  const mask=attackLauncherMaskH3(r,spec);if(!mask.ok)return mask;
  const p=gate.memory.positionM,v=gate.memory.velocityMps,start=gate.muzzleM;let t=Math.hypot(p.x-start.x,p.y-start.y)/HARPOON_PROFILE_A.sim.cruiseSpeedMps;
  for(let i=0;i<4;i++)t=Math.hypot(p.x+v.x*t-start.x,p.y+v.y*t-start.y)/HARPOON_PROFILE_A.sim.cruiseSpeedMps;
  const end={x:p.x+v.x*t,y:p.y+v.y*t},turn=Math.abs(angNorm(Math.atan2(end.y-start.y,end.x-start.x)-Math.atan2(gate.axis.y,gate.axis.x))),length=Math.hypot(end.x-start.x,end.y-start.y)+2000*turn/Math.PI;
  if(turn>ATTACK_POLICY_H3.maxTurnRad)return {ok:false,reason:'MK141_TURN_LIMIT'};
  if(length>HARPOON_PROFILE_A.sim.maxLaunchRangeKm*1000)return {ok:false,reason:'ATTACK_ROUTE_RANGE_BUDGET'};
  const chart=attackChartGuardH3(start,end);if(!chart.ok)return chart;
  const protectedPicture=attackProtectedH3(r);if(protectedPicture.blocked)return {ok:false,reason:protectedPicture.blocked};
  for(const q of protectedPicture.rows){
    const dx=end.x-start.x,dy=end.y-start.y,rx=q.x-start.x,ry=q.y-start.y,ux=dx-q.vx*t,uy=dy-q.vy*t,f=clamp((rx*ux+ry*uy)/Math.max(1,ux*ux+uy*uy),0,1),cpa=Math.hypot(rx-ux*f,ry-uy*f),terminal=Math.hypot(q.x+q.vx*t-end.x,q.y+q.vy*t-end.y),P=q.P;
    const sigma=2*Math.sqrt(Math.max(P?.[0]??2500,P?.[7]??2500,0)+t*t*Math.max(P?.[21]??1,P?.[28]??1,0))+.5*.04*t*t;
    if(cpa<ATTACK_POLICY_H3.corridorM+sigma||terminal<HARPOON_PROFILE_A.sim.seekerSearchBasketM+ATTACK_POLICY_H3.protectedMarginM+sigma)return {ok:false,reason:'PROTECTED_ATTACK_CORRIDOR_OR_SEARCH'};
  }
  return {ok:true,routeLengthM:length,flightTimeEstimateS:t,turnRad:turn,searchCenterM:end,protectedContacts:protectedPicture.rows.length};
}
function attackFinalGuardH3(r,tr,token,gate){const a=attackAuthorityH3(r,tr,token);return a.ok?attackPathGuardH3(r,gate):a;}
function attackCommitH3(r,token,gate,serial){
  const s=prepareAttackH3(r),c=attackConsentH3(r,token.track);if(c){if(c.mission)s.enemyRemaining--;else {c.remaining--;if(c.remaining===0)s.consents.delete(token.track.trackId);}}
  s.lastReleaseS=networkNowG();s.releaseToken=null;s.status='RELEASED';s.reason='NO_DL_NO_FLIGHT_TELEMETRY';attackLogH3(r,'RELEASE','NATIVE_HARPOON',gate.trackId,{tubeId:gate.tubeId,serial});
}
function attackEvaluateH3(r){
  const s=prepareAttackH3(r);if(s.lastStep===simStepCounter)return;s.lastStep=simStepCounter;s.evaluations++;
  const now=networkNowG();for(const [id,c]of s.consents)if(c.untilS<now||c.track!==observerC(r).tracks.get(id))s.consents.delete(id);
  if(r.role==='ENEMY'&&s.enemyRemaining===0&&now-s.lastReleaseS>=ATTACK_POLICY_H3.enemyCycleS)s.enemyRemaining=2;
  if(!attackActiveH3(r)){attackCancelH3(r,'ATTACK_AUTO_INACTIVE');s.plans=[];return;}
  if(r.combatSystem.tacticalH1?.summary?.emergency){attackCancelH3(r,'AIR_DEFENSE_PRIORITY');s.plans=[];return;}
  const h=r.weapons.harpoon;if(h.pending){if(h.pending.attackH3){const tr=observerC(r).tracks.get(h.pending.trackId),g=attackAuthorityH3(r,tr,h.pending.attackH3);if(!g.ok)attackCancelH3(r,g.reason);else {s.status='PREPARING';s.reason='RELEASE_RECHECK_PENDING';}}else {s.status='WAIT';s.reason='MANUAL_HARPOON_PENDING';}return;}
  if(observerC(r).tracks.size>ATTACK_POLICY_H3.maxFiles){attackCancelH3(r,'LOCAL_PICTURE_CAPACITY');s.plans=[];return;}
  const rows=[];for(const tr of observerC(r).tracks.values()){const g=attackObservationGateH3(r,tr);if(!g.ok||!attackConsentH3(r,tr))continue;const e=g.estimate,n=r.navigation,range=Math.hypot(e.x[0]-worldToMeters(n.positionWorld.x),e.x[1]-worldToMeters(n.positionWorld.y)),score=.6*clamp(tr.fireControlQuality??tr.trackQuality??0,0,1)+.4*clamp(1-range/140000,0,1);rows.push({tr,score});}
  rows.sort((a,b)=>b.score-a.score||a.tr.trackId-b.tr.trackId);s.plans=[];
  for(const q of rows.slice(0,ATTACK_POLICY_H3.maxTracks)){
    const token={ownerId:r.entityId,trackId:q.tr.trackId};Object.defineProperty(token,'track',{value:q.tr});s.releaseToken=token;const gate=attackNativePreviewH3(r,q.tr.trackId,token),path=gate.ok?attackPathGuardH3(r,gate):gate;
    s.plans.push({trackId:q.tr.trackId,score:q.score,ready:gate.ok&&path.ok,reason:path.reason??null,tubeId:gate.tubeId??null,rangeKm:gate.rangeKm??null,predictionSigmaM:gate.predictionSigmaM??null,...(path.ok?{routeLengthM:path.routeLengthM,flightTimeEstimateS:path.flightTimeEstimateS}:{}),truthUsed:false});
    if(!gate.ok||!path.ok){s.releaseToken=null;continue;}
    s.selectedTrackId=q.tr.trackId;const result=r===ACTIVE_SHIP_RUNTIME?harpoonRequestFireA(q.tr.trackId,null,{attackH3:token}):r.weapons.executionD.context.attackRequestH3(q.tr.trackId,token);
    if(result.ok){s.status='PREPARING';s.reason='RELEASE_RECHECK_PENDING';attackLogH3(r,'PREPARE','CONSENT_AND_PLAN_PASSED',q.tr.trackId,{tubeId:result.tubeId});return;}
    s.releaseToken=null;s.plans.at(-1).ready=false;s.plans.at(-1).reason=result.reason;
  }
  s.releaseToken=null;s.selectedTrackId=null;s.status='WAIT';s.reason=s.plans[0]?.reason??(r.role==='ENEMY'&&s.enemyRemaining===0?'ENEMY_SALVO_REASSESS_TIMER':'ATTACK_CONSENT_OR_HOSTILE_TRACK_REQUIRED');
}
function stepAttackFleetH3(){if(simStepCounter%ATTACK_POLICY_H3.periodTicks===0)for(const r of [ACTIVE_SHIP_RUNTIME,...physicalShipsB()])attackEvaluateH3(r);}
function attackSnapshotH3(){return {schema:ATTACK_POLICY_H3.schema,truthUsed:false,remoteFireControl:false,dataLink:false,ships:[ACTIVE_SHIP_RUNTIME,...physicalShipsB()].map(r=>{const s=prepareAttackH3(r);return {entityId:r.entityId,settings:{...s.settings},active:attackActiveH3(r),status:s.status,reason:s.reason,lastStep:s.lastStep,evaluations:s.evaluations,selectedTrackId:s.selectedTrackId,consents:[...s.consents].map(([trackId,c])=>({trackId,remaining:c.remaining,expiresInS:Math.max(0,c.untilS-networkNowG())})),plans:s.plans.map(q=>({...q})),log:s.log.map(q=>({...q}))};})};}
