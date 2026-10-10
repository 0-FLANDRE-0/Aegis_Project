// LIVE_CANONICAL. Deterministic, owner-local utility decisions over observations.
// Weights/timers are SIM-TUNE. Native ROE, FCS, reserves and release remain final.
const TACTICAL_POLICY_H1=Object.freeze({schema:'AEGIS_UTILITY_TACTICAL_H1_1',minHoldS:2,switchMargin:.08,emergencyS:12,freshS:2,maxTracks:96,maxLog:64});
function tacticalDefaultsH1(r){return {schema:TACTICAL_POLICY_H1.schema,enabled:r!==ACTIVE_SHIP_RUNTIME,manualRadar:false,manualEw:false};}
function prepareTacticalH1(r){
  if(r.combatSystem.tacticalH1)return r.combatSystem.tacticalH1;
  const settings=r.restoredTacticalH1??tacticalDefaultsH1(r);delete r.restoredTacticalH1;
  const s={settings:{...settings},posture:'WATCH',sinceS:0,lastStep:-1,evaluations:0,scores:[],priorities:[],summary:null,lastDangerS:-1e6,radarBase:null,ewBase:null,log:[]};
  r.combatSystem.tacticalH1=s;claimShipMutableRootA(r,'tacticalH1',s);return s;
}
function tacticalSettingsH1(r){return {...prepareTacticalH1(r).settings};}
function tacticalModeH1(r){return r===ACTIVE_SHIP_RUNTIME?engagementControlMode:r.weapons.executionD?.defenseE.mode==='AUTO'?'AUTO':'MANUAL';}
function tacticalActiveH1(r){return prepareTacticalH1(r).settings.enabled&&tacticalModeH1(r)==='AUTO';}
function tacticalNoteOperatorH1(r,channels){
  const s=r?.combatSystem?.tacticalH1;if(!s)return;
  if(channels.includes('radar')){s.settings.manualRadar=true;s.radarBase=null;}
  if(channels.includes('ew')){s.settings.manualEw=true;s.ewBase=null;}
}
function tacticalGroupAuthorityH1(r){
  const n=r.combatSystem.networkG;if(!n)return false;
  return r===ACTIVE_SHIP_RUNTIME?n.settings.groupEmcon!=='INDIVIDUAL':!!n.groupLease&&n.groupLease.mode!=='INDIVIDUAL'&&n.groupLease.untilS>=networkNowG();
}
function tacticalYieldRadarH1(r){
  const s=r.combatSystem.tacticalH1;if(!s||s.radarBase===null)return;
  if(!s.settings.manualRadar&&!tacticalGroupAuthorityH1(r))networkSetRadarG(r,s.radarBase);s.radarBase=null;
}
function tacticalRestoreH1(r){
  const s=r.combatSystem.tacticalH1;if(!s)return;
  if(s.radarBase!==null&&!s.settings.manualRadar&&!tacticalGroupAuthorityH1(r))networkSetRadarG(r,s.radarBase);
  if(s.ewBase!==null&&!s.settings.manualEw)electronicCommandF(r.entityId,s.ewBase,'TACTICAL_H1');
  s.radarBase=null;s.ewBase=null;
}
function tacticalCommandH1(id,c){
  const r=fleetOwnerG(id);if(!r)return {ok:false,reason:'FRIENDLY_OWNER_REQUIRED'};
  if(!c||typeof c!=='object'||Array.isArray(c)||Object.keys(c).length!==1||!('enabled'in c||'resume'in c)||'enabled'in c&&typeof c.enabled!=='boolean'||'resume'in c&&c.resume!==true)return {ok:false,reason:'TACTICAL_COMMAND_FIELDS'};
  const s=prepareTacticalH1(r);tacticalRestoreH1(r);
  if('enabled'in c)s.settings.enabled=c.enabled;
  else {s.settings.enabled=true;s.settings.manualRadar=false;s.settings.manualEw=false;}
  s.lastStep=-1;fleetUpdateUiG(true);return {ok:true,settings:{...s.settings}};
}
function tacticalExportElectronicH1(r){
  const q=electronicSettingsF(r),s=r.combatSystem.tacticalH1;
  if(s?.radarBase!==null&&s?.radarBase!==undefined&&!s.settings.manualRadar)q.emcon=s.radarBase;
  if(s?.ewBase&&!s.settings.manualEw)Object.assign(q,s.ewBase);return q;
}
function resetTacticalFleetH1(){
  for(const r of [ACTIVE_SHIP_RUNTIME,...physicalShipsB()]){const s=r.combatSystem.tacticalH1,settings=s?{...s.settings}:null;r.combatSystem.tacticalH1=null;if(settings&&!r.restoredTacticalH1)r.restoredTacticalH1=settings;prepareTacticalH1(r);}
}
function validateTacticalSettingsH1(q,errors){
  if(!networkStrictKeysG(q,['schema','enabled','manualRadar','manualEw'])||q.schema!==TACTICAL_POLICY_H1.schema||['enabled','manualRadar','manualEw'].some(k=>typeof q[k]!=='boolean'))errors.push('TACTICAL_H1_SETTINGS');
}
function migrateTacticalSaveH1(src,migrations){
  if(src.fleet&&!['AEGIS_NAVAL_PHYSICAL_FLEET_G_1','AEGIS_NAVAL_PHYSICAL_FLEET_F_1','AEGIS_NAVAL_PHYSICAL_FLEET_B_1'].includes(src.fleet.schema))return;
  if(src.ship&&!Object.hasOwn(src.ship,'tactical'))src.ship.tactical={schema:TACTICAL_POLICY_H1.schema,enabled:false,manualRadar:false,manualEw:false};
  for(const q of src.fleet?.ships??[])if(!Object.hasOwn(q,'tactical'))q.tactical={schema:TACTICAL_POLICY_H1.schema,enabled:true,manualRadar:false,manualEw:false};
  migrations.push({id:'LEGACY_UTILITY_TACTICAL_H1',policy:'SETTINGS_ONLY_NO_DECISIONS_OR_TARGET_MEMORY'});
}
function tacticalChooseH1(current,sinceS,now,scores,emergency=false,offline=false){
  const best=scores[0],previous=scores.find(q=>q.posture===current);
  return best.posture!==current&&(offline||emergency||now-sinceS>=TACTICAL_POLICY_H1.minHoldS&&best.score>(previous?.score??0)+TACTICAL_POLICY_H1.switchMargin)?best.posture:current;
}
function tacticalSelfTestH1(){
  const scores=[{posture:'DEFEND',score:.9},{posture:'WATCH',score:.4}],checks={
    hold:tacticalChooseH1('WATCH',0,1,scores)==='WATCH',normal:tacticalChooseH1('WATCH',0,2,scores)==='DEFEND',
    margin:tacticalChooseH1('WATCH',0,3,[{posture:'DEFEND',score:.45},{posture:'WATCH',score:.4}])==='WATCH',
    emergency:tacticalChooseH1('WATCH',0,.1,scores,true)==='DEFEND',offline:tacticalChooseH1('WATCH',0,.1,[{posture:'DEGRADED',score:1.5},{posture:'WATCH',score:.4}],false,true)==='DEGRADED',
    recovery:tacticalChooseH1('DEFEND',0,3,[{posture:'WATCH',score:.6},{posture:'DEFEND',score:.1}])==='WATCH'};
  return {checks,pass:Object.values(checks).every(Boolean)};
}
function tacticalEvaluateH1(r,control,inventory,damage){
  const s=prepareTacticalH1(r);if(s.lastStep===simStepCounter)return s;s.lastStep=simStepCounter;s.evaluations++;
  const now=networkNowG(),rows=[],nav=r.navigation;
  for(const tr of observerC(r).tracks.values()){
    if(rows.length>=TACTICAL_POLICY_H1.maxTracks)break;
    const a=control.assessments.get(tr.trackId);
    if(a?.state!=='THREAT'||!tr.confirmed||tr.sensorDetected===false||networkLocalAgeG(tr)>TACTICAL_POLICY_H1.freshS||tr.memActive||tr.reacquiring||tr.domain==='SURFACE'||tr.classification==='SURFACE'||['FRIEND','NEUTRAL','UNKNOWN','TRAINING_TARGET'].includes(tr.identity)||tr.engagementAuthority!=='AUTO_AUTHORIZED'||networkProtectionG(r,tr))continue;
    const e=networkLocalEstimateG(tr);if(!e)continue;
    const dx=e.x[0]-worldToMeters(nav.positionWorld.x),dy=e.x[1]-worldToMeters(nav.positionWorld.y),range=Math.max(1,Math.hypot(dx,dy)),vx=e.x[3]-worldSpeedToMps(nav.vx??0),vy=e.x[4]-worldSpeedToMps(nav.vy??0),closure=-(dx*vx+dy*vy)/range;
    const tti=closure>20?range/closure:1e6,urgency=clamp(1-tti/80,0,1),quality=clamp(tr.fireControlQuality??tr.trackQuality??0,0,1),unserved=(a.liveEngagement??0)===0;
    const score=clamp(.56*urgency+.18*clamp(closure/800,0,1)+.16*quality+.1*(unserved?1:0),0,1);
    rows.push({trackId:tr.trackId,score,ttiS:tti,closureMps:closure,speedMps:Math.hypot(e.x[3],e.x[4],e.x[5]),rangeKm:range/1000,bearingRad:Math.atan2(dy,dx),unserved,quality});
  }
  rows.sort((a,b)=>b.score-a.score||a.trackId-b.trackId);
  const mounts=resolveShipProfile(r.profileId).geometry.hardpoints.spg62,availableChannels=mounts.filter(q=>observerHealthC(r,q.moduleName)>.15).length,supportLoad=clamp(r.combatSystem.fireControl.illuminatorAssignments.size/Math.max(1,availableChannels),0,1);
  const esm=[...prepareElectronicF(r).contacts.values()].filter(q=>q.emitterClass==='ACTIVE_SEEKER'&&now-q.measuredAtS>=0&&now-q.measuredAtS<=2&&q.quality>=.25).length,
    remote=networkMemberG(r)?networkPictureG(r).filter(q=>q.localTrackId===null&&!q.coasting&&q.domain==='AIR'&&!['FRIEND','NEUTRAL'].includes(q.identity)&&q.sources.some(source=>source.assessment==='THREAT')).length:0,
    earliest=rows.length?Math.min(...rows.map(q=>q.ttiS)):1e6,urgency=rows.length?Math.max(...rows.map(q=>clamp(1-q.ttiS/80,0,1))):esm>0 ? .65 : remote>0 ? .45 : 0,
    unserved=rows.filter(q=>q.unserved).length,ammo=Object.values(inventory).reduce((n,q)=>n+Math.max(0,Number(q)||0),0),pressure=clamp(unserved/4+.15*supportLoad,0,1),scarcity=clamp(1-ammo/Math.max(8,2*unserved),0,1),degradation=clamp(Math.max(1-(damage.combatEff??0),1-(damage.radarPowerFac??0),.7*(1-availableChannels/Math.max(1,mounts.length))),0,1),offline=shipEquipmentOfflineV1(r),emergency=earliest<=TACTICAL_POLICY_H1.emergencyS;
  const scores=[{posture:'WATCH',score:rows.length||esm||remote ? .1 : .55},
    {posture:'CONSERVE',score:.12+.55*scarcity+.12*pressure},
    {posture:'DEFEND',score:rows.length||esm||remote ? .22+.63*urgency+.18*pressure : 0},
    {posture:'SATURATED',score:rows.length>=3?.4+.32*pressure+.25*urgency:0},
    {posture:'DEGRADED',score:offline?1.5:degradation>.45?.35+.5*degradation+.15*urgency:0}];
  scores.sort((a,b)=>b.score-a.score||a.posture.localeCompare(b.posture));const best=scores[0];
  if(tacticalChooseH1(s.posture,s.sinceS,now,scores,emergency,offline)!==s.posture){
    s.log.push({step:simStepCounter,from:s.posture,to:best.posture,score:best.score});if(s.log.length>TACTICAL_POLICY_H1.maxLog)s.log.shift();s.posture=best.posture;s.sinceS=now;
  }
  s.priorities=rows;s.scores=scores;s.summary={localThreats:rows.length,unserved,passiveSeekerAlerts:esm,sharedAlerts:remote,earliestTtiS:rows.length?earliest:null,availableRounds:ammo,inventory:{...inventory},supportChannels:mounts.length,availableChannels,activeIlluminations:r.combatSystem.fireControl.illuminatorAssignments.size,combatEfficiency:damage.combatEff??0,radarPower:damage.radarPowerFac??0,ciwsPower:damage.ciwsPowerFac??0,steering:damage.steerFac??0,emergency,offline};
  if(!tacticalActiveH1(r)||offline){tacticalRestoreH1(r);return s;}
  // Passive/shared alerts change readiness only; they never supply a fire-control file.
  const danger=rows.length>0||esm>0||remote>0;if(danger)s.lastDangerS=now;const quiet=!danger&&now-s.lastDangerS>=TACTICAL_POLICY_H1.minHoldS;
  if(!s.settings.manualRadar&&!tacticalGroupAuthorityH1(r)){
    if(danger){if(s.radarBase===null)s.radarBase=electronicSettingsF(r).emcon;networkSetRadarG(r,false);}
    else if(s.radarBase!==null&&quiet){networkSetRadarG(r,s.radarBase);s.radarBase=null;}
  }
  if(!s.settings.manualEw){
    const current=electronicSettingsF(r);
    if(danger){if(s.ewBase===null)s.ewBase={auto:current.auto,autoAim:current.autoAim,noiseRequested:current.noiseRequested,deceptionRequested:current.deceptionRequested};
      if(!current.auto||!current.autoAim||!current.noiseRequested||!current.deceptionRequested)electronicCommandF(r.entityId,{auto:true,autoAim:true,noiseRequested:true,deceptionRequested:true},'TACTICAL_H1');
    }else if(s.ewBase!==null&&quiet){electronicCommandF(r.entityId,s.ewBase,'TACTICAL_H1');s.ewBase=null;}
  }
  return s;
}
function tacticalPriorityH1(r,id){return r.combatSystem.tacticalH1?.priorities.find(q=>q.trackId===id)?.score??0;}
function tacticalOrderH1(r,rows){return tacticalActiveH1(r)?[...rows].sort((a,b)=>tacticalPriorityH1(r,b.id)-tacticalPriorityH1(r,a.id)||(b.threatScore??0)-(a.threatScore??0)||a.id-b.id):rows;}
function tacticalRecommendationOrderH1(r,a,b){return tacticalActiveH1(r)?tacticalPriorityH1(r,b.trackId)-tacticalPriorityH1(r,a.trackId):0;}
function tacticalSalvoH1(r,th,weapon,native){
  if(!tacticalActiveH1(r)||!['SM2','SM2ER','SM6','ESSM'].includes(weapon)||native.salvo<2)return native;
  const s=prepareTacticalH1(r),q=s.priorities.find(q=>q.trackId===th.id),summary=s.summary;
  if(!q||!summary||q.ttiS<=25||q.speedMps>=600)return native;
  const pool=summary.inventory[weapon.toLowerCase()]??0;
  if(summary.localThreats>=3&&pool<2*summary.localThreats)return {...native,salvo:1,policy:'UTILITY_SPREAD_DEFENSE_H1',canReengage:false};
  return native;
}
function tacticalSnapshotH1(){return {schema:TACTICAL_POLICY_H1.schema,truthUsed:false,remoteFireControl:false,ships:[ACTIVE_SHIP_RUNTIME,...physicalShipsB()].map(r=>{
  const s=prepareTacticalH1(r);return {entityId:r.entityId,settings:{...s.settings},active:tacticalActiveH1(r),posture:s.posture,sinceS:s.sinceS,lastStep:s.lastStep,evaluations:s.evaluations,scores:s.scores.map(q=>({...q})),priorities:s.priorities.map(q=>({...q})),summary:s.summary?{...s.summary,inventory:{...s.summary.inventory}}:null,radarOwned:s.radarBase!==null,ewOwned:s.ewBase!==null,groupRadarPriority:tacticalGroupAuthorityH1(r),log:s.log.map(q=>({...q}))};
})};}
