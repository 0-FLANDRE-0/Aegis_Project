// LIVE_CANONICAL owner commands. Prediction is SIM-TUNE scoring, never physics.
const MANEUVER_POLICY_H2=Object.freeze({schema:'AEGIS_MANEUVER_UTILITY_H2_1',periodTicks:12,minHoldS:3,switchMargin:.04,quietS:4,maxThreats:8,maxTraffic:16,maxLog:64,horizonS:30});
const MANEUVER_NAV_KEYS_H2=Object.freeze(['targetSpeedKt','targetRudder','manualSpeedV15','manualRudderV15','telegraph','_c17Kt','_c17Tg']);
function prepareManeuverH2(r){
  if(r.combatSystem.maneuverH2)return r.combatSystem.maneuverH2;
  const settings=r.restoredManeuverH2??{schema:MANEUVER_POLICY_H2.schema,enabled:r!==ACTIVE_SHIP_RUNTIME,manualNav:false};delete r.restoredManeuverH2;
  const s={settings:{...settings},lastStep:-1,evaluations:0,selected:'KEEP',sinceS:0,lastDangerS:-1e6,baseline:null,candidates:[],summary:null,command:null,log:[]};
  r.combatSystem.maneuverH2=s;claimShipMutableRootA(r,'maneuverH2',s);return s;
}
function maneuverSettingsH2(r){return {...prepareManeuverH2(r).settings};}
function maneuverActiveH2(r){const s=prepareManeuverH2(r);return s.settings.enabled&&!s.settings.manualNav&&tacticalActiveH1(r);}
function maneuverOwnsH2(r){return !!r.combatSystem.maneuverH2?.baseline;}
function maneuverYieldH2(r){
  const s=r.combatSystem.maneuverH2;if(!s)return;
  if(s.baseline)for(const k of MANEUVER_NAV_KEYS_H2){if(Object.hasOwn(s.baseline.order,k))r.navigation[k]=s.baseline.order[k];else delete r.navigation[k];}
  s.baseline=null;s.command=null;s.selected='KEEP';
}
function maneuverNoteOperatorH2(r){const s=prepareManeuverH2(r);maneuverYieldH2(r);s.settings.manualNav=true;s.lastStep=-1;}
function maneuverCommandH2(id,c){
  const r=fleetOwnerG(id);if(!r)return {ok:false,reason:'FRIENDLY_OWNER_REQUIRED'};
  if(!c||typeof c!=='object'||Array.isArray(c)||Object.keys(c).length!==1||!('enabled'in c||'resume'in c)||'enabled'in c&&typeof c.enabled!=='boolean'||'resume'in c&&c.resume!==true)return {ok:false,reason:'MANEUVER_COMMAND_FIELDS'};
  const s=prepareManeuverH2(r);maneuverYieldH2(r);
  if('enabled'in c)s.settings.enabled=c.enabled;
  else {s.settings.enabled=true;s.settings.manualNav=false;tacticalCommandH1(id,{enabled:true});}
  s.lastStep=-1;fleetUpdateUiG(true);return {ok:true,settings:{...s.settings}};
}
function maneuverExportNavigationH2(r){const n=jsonSafeCloneV48Wip11A(r.navigation),s=r.combatSystem.maneuverH2;if(s?.baseline)for(const k of MANEUVER_NAV_KEYS_H2){if(Object.hasOwn(s.baseline.order,k))n[k]=s.baseline.order[k];else delete n[k];}return n;}
function resetManeuverFleetH2(){for(const r of [ACTIVE_SHIP_RUNTIME,...physicalShipsB()]){const s=r.combatSystem.maneuverH2;if(s&&!r.restoredManeuverH2)r.restoredManeuverH2={...s.settings};r.combatSystem.maneuverH2=null;prepareManeuverH2(r);}}
function validateManeuverSettingsH2(q,errors){if(!networkStrictKeysG(q,['schema','enabled','manualNav'])||q.schema!==MANEUVER_POLICY_H2.schema||typeof q.enabled!=='boolean'||typeof q.manualNav!=='boolean')errors.push('MANEUVER_H2_SETTINGS');}
function validateManeuverNavigationH2(n,errors){
  if(!n||typeof n!=='object')return;
  if('telegraph'in n&&(!Number.isInteger(n.telegraph)||n.telegraph< -3||n.telegraph>5))errors.push('MANEUVER_H2_TELEGRAPH');
  if('_c17Kt'in n&&(!Number.isFinite(n._c17Kt)||n._c17Kt< -15||n._c17Kt>35))errors.push('MANEUVER_H2_SPEED_ORDER');
  if('_c17Tg'in n&&typeof n._c17Tg!=='boolean')errors.push('MANEUVER_H2_TELEGRAPH_MODE');
}
function migrateManeuverSaveH2(src,migrations){
  if(src.fleet&&!['AEGIS_NAVAL_PHYSICAL_FLEET_H1_1','AEGIS_NAVAL_PHYSICAL_FLEET_G_1','AEGIS_NAVAL_PHYSICAL_FLEET_F_1','AEGIS_NAVAL_PHYSICAL_FLEET_B_1'].includes(src.fleet.schema))return;
  if(src.ship&&!Object.hasOwn(src.ship,'maneuver'))src.ship.maneuver={schema:MANEUVER_POLICY_H2.schema,enabled:false,manualNav:!!(src.ship.navigation?.manualSpeedV15||src.ship.navigation?.manualRudderV15)};
  for(const q of src.fleet?.ships??[])if(!Object.hasOwn(q,'maneuver'))q.maneuver={schema:MANEUVER_POLICY_H2.schema,enabled:true,manualNav:!!(q.ship?.navigation?.manualSpeedV15||q.ship?.navigation?.manualRudderV15)};
  migrations.push({id:'LEGACY_MANEUVER_H2',policy:'SETTINGS_ONLY_NO_HEADING_GOAL_OR_COMMAND_OWNERSHIP'});
}
function maneuverObservedH2(r){
  const rows=[];for(const q of r.combatSystem.tacticalH1?.priorities??[]){
    if(rows.length>=MANEUVER_POLICY_H2.maxThreats)break;const tr=observerC(r).tracks.get(q.trackId);
    if(!tr?.confirmed||tr.sensorDetected===false||networkLocalAgeG(tr)>2||tr.memActive||tr.reacquiring||tr.domain==='SURFACE'||tr.classification==='SURFACE'||['FRIEND','NEUTRAL','UNKNOWN','TRAINING_TARGET'].includes(tr.identity)||tr.engagementAuthority!=='AUTO_AUTHORIZED'||networkProtectionG(r,tr))continue;
    const e=networkLocalEstimateG(tr);if(!e)continue;const n=r.navigation,rx=e.x[0]-worldToMeters(n.positionWorld.x),ry=e.x[1]-worldToMeters(n.positionWorld.y),vx=e.x[3]-worldSpeedToMps(n.vx??0),vy=e.x[4]-worldSpeedToMps(n.vy??0),vv=vx*vx+vy*vy,t=vv>1?- (rx*vx+ry*vy)/vv:0,cpa=Math.hypot(rx+vx*Math.max(0,t),ry+vy*Math.max(0,t));
    if(t<=0||t>120||cpa>1500)continue;
    rows.push({trackId:q.trackId,weight:Math.max(.1,q.score),ttiS:q.ttiS,cpaS:t,cpaM:cpa,positionM:{x:e.x[0],y:e.x[1],z:e.x[2]},velocityMps:{x:e.x[3],y:e.x[4],z:e.x[5]}});
  }return rows;
}
function maneuverTrafficH2(r){
  const rows=[];for(const tr of observerC(r).tracks.values()){
    if(rows.length>=MANEUVER_POLICY_H2.maxTraffic)break;if(!tr.confirmed||tr.domain!=='SURFACE'||networkLocalAgeG(tr)>2||tr.memActive||tr.reacquiring)continue;const e=networkLocalEstimateG(tr);if(e)rows.push({x:e.x[0],y:e.x[1],vx:e.x[3],vy:e.x[4],source:'LOCAL_SURFACE'});
  }
  if(networkMemberG(r))for(const q of networkPictureG(r)){
    if(rows.length>=MANEUVER_POLICY_H2.maxTraffic)break;if(q.domain!=='SURFACE'||q.coasting||q.ageS>2||!q.sources.some(s=>s.kind==='SELF')||!q.positionM||!q.velocityMps)continue;rows.push({x:q.positionM.x,y:q.positionM.y,vx:q.velocityMps.x,vy:q.velocityMps.y,source:'RECEIVED_NAVIGATION'});
  }return rows;
}
function maneuverPredictH2(r,goal,speedKt,horizon,damage){
  const n=r.navigation,poses=[],origin={x:worldToMeters(n.positionWorld.x),y:worldToMeters(n.positionWorld.y)},initialSpeed=Math.max(0,n.speed),targetSpeed=Math.max(0,speedKt)*.514444,turnCap=deg(.9)*clamp(initialSpeed/10,.1,1.5)*Math.max(0,damage.turnFac??0),actuation=Math.min(10,Math.abs(clamp(angNorm(goal-n.heading)*180/Math.PI*1.6,-30,30)-n.rudder)/Math.max(.3,3*(damage.rudderRateFac??0)));
  let x=origin.x,y=origin.y,heading=n.heading,v=initialSpeed;const dt=horizon/6;
  for(let i=1;i<=6;i++){const timeS=i*dt,turnTime=Math.max(0,timeS-actuation),next=n.heading+clamp(angNorm(goal-n.heading),-turnCap*turnTime,turnCap*turnTime),accel=(targetSpeed<v?.06:.08)*Math.max(0,damage.accelFac??0),newSpeed=v+clamp(targetSpeed-v,-accel*dt,accel*dt),mid=heading+angNorm(next-heading)*.5;x+=Math.cos(mid)*(v+newSpeed)*.5*dt;y+=Math.sin(mid)*(v+newSpeed)*.5*dt;heading=angNorm(next);v=newSpeed;poses.push({x,y,heading,speedMps:v,timeS});}
  return {origin,poses,final:poses.at(-1),horizonS:horizon};
}
function maneuverPathGuardH2(r,prediction,traffic){
  const profile=resolveShipProfile(r.profileId),radius=Math.max(Math.abs(profile.geometry.bowXM),Math.abs(profile.geometry.sternXM))+15;
  for(const p of prediction.poses){
    if(!BATTLESPACE_DIAG_BYPASS)for(const island of terrainIslands){const x=metersToWorld(p.x),y=metersToWorld(p.y),pad=metersToWorld(radius);if(Math.hypot(x-island.cx,y-island.cy)>island.boundRadiusWorld+pad)continue;if(pointInTerrainPolygon(x,y,island.points)||distanceToTerrainEdge(x,y,island)<pad)return {ok:false,reason:'CHART_TERRAIN',atS:p.timeS};}
    for(const q of traffic){const initial=Math.hypot(prediction.origin.x-q.x,prediction.origin.y-q.y),separation=Math.hypot(p.x-q.x-q.vx*p.timeS,p.y-q.y-q.vy*p.timeS);if(separation<radius+100&&separation<initial-2)return {ok:false,reason:'MEASURED_TRAFFIC',atS:p.timeS};}
  }return {ok:true,reason:null};
}
function maneuverCoverageNativeH2(r,observation,pose,ports){
  const frame=createShipBodyFrameV1(shipSurvivalB(r).snapshot(),{x:pose.x,y:pose.y,z:OWN_ALT_M},pose.heading),p=frame.pointToBody(observation),range=Math.max(1,Math.hypot(p.x,p.y)),az=Math.atan2(p.y,p.x),spg=[],closeIn=[];
  for(const ill of ports.illuminators){const quality=ports.spg62Quality(ill,az,observation.z,range/1000);spg.push({id:ill.id,quality,open:quality>=.05});}
  for(const mount of ports.closeIn){const origin={x:mount.posOffsetM??0,y:mount.posOffsetYM??0,z:mount.heightM??15},dx=p.x-origin.x,dy=p.y-origin.y,dz=p.z-origin.z,dir=ports.ciwsGameConstraintsV1(mount).direction(Math.atan2(dy,dx),Math.atan2(dz,Math.hypot(dx,dy)),Math.min(300,Math.hypot(dx,dy,dz))),healthy=observerHealthC(r,mount.moduleName)>.15&&mount.ammo>0;closeIn.push({id:mount.id,open:healthy&&dir.ok});}
  return {spg,closeIn,spgFraction:spg.filter(q=>q.open).length/Math.max(1,spg.length),closeInFraction:closeIn.filter(q=>q.open).length/Math.max(1,closeIn.length),rangeM:range,bearingRelRad:az};
}
function maneuverCoverageH2(r,observation,pose){return r===ACTIVE_SHIP_RUNTIME?maneuverCoverageNativeH2(r,observation,pose,{illuminators:SPG62_ILLUMINATORS,closeIn:ciws,spg62Quality,ciwsGameConstraintsV1}):r.weapons.executionD.context.maneuverCoverageH2(observation,pose);}
function maneuverSpeedH2(r,requested,damage){const max=Math.min(shipAheadLimitB(resolveShipProfile(r.profileId)),Math.max(0,damage.maxSpeedKt??0)),options=C17_TELEGRAPH.filter(q=>q.kt>=0&&q.kt<=max+.001);return (options.filter(q=>q.kt<=Math.max(0,requested)+.001).at(-1)??options[0]).kt;}
function maneuverMissionHeadingH2(r,s){if(r===ACTIVE_SHIP_RUNTIME&&routePoints.length&&activeWpIdx<routePoints.length){const wp=routePoints[activeWpIdx],n=r.navigation;return Math.atan2(wp.y-n.positionWorld.y,wp.x-n.positionWorld.x);}return s.baseline?.headingRad??r.navigation.heading;}
function maneuverPlanH2(r,rows,damage,s){
  const n=r.navigation,horizon=Math.min(MANEUVER_POLICY_H2.horizonS,Math.max(4,Math.min(...rows.map(q=>q.ttiS))*.5)),anchor=maneuverMissionHeadingH2(r,s),requested=s.baseline?.order.targetSpeedKt??n.targetSpeedKt,normal=maneuverSpeedH2(r,Math.max(14,requested),damage),traffic=maneuverTrafficH2(r),specs=[['KEEP',0,maneuverSpeedH2(r,requested,damage)],['PORT30',-30,normal],['STARBOARD30',30,normal],['PORT60',-60,normal],['STARBOARD60',60,normal],['FAST',0,maneuverSpeedH2(r,28,damage)],['SLOW',0,maneuverSpeedH2(r,8,damage)],['STOP',0,0]],candidates=[];
  for(const [id,offset,speedKt] of specs){
    const headingRad=angNorm(anchor+deg(offset)),prediction=maneuverPredictH2(r,headingRad,speedKt,horizon,damage),guard=maneuverPathGuardH2(r,prediction,traffic);let weight=0,coverage=0,spacing=0,aspect=0,supportRisk=0,supportCount=0;const opportunities=[];
    for(const q of rows){const target={x:q.positionM.x+q.velocityMps.x*horizon,y:q.positionM.y+q.velocityMps.y*horizon,z:Math.max(0,q.positionM.z+q.velocityMps.z*horizon)},m=prediction.final,c=maneuverCoverageH2(r,target,m),current=maneuverCoverageH2(r,target,{x:m.x,y:m.y,heading:n.heading}),near=clamp(1-c.rangeM/15000,0,1);weight+=q.weight;coverage+=q.weight*(c.spgFraction*(1-.6*near)+c.closeInFraction*.6*near);aspect+=q.weight*Math.abs(Math.cos(c.bearingRelRad));
      const rx=target.x-m.x,ry=target.y-m.y,vx=q.velocityMps.x-Math.cos(m.heading)*m.speedMps,vy=q.velocityMps.y-Math.sin(m.heading)*m.speedMps,vv=vx*vx+vy*vy,t=vv>1?Math.max(0,-(rx*vx+ry*vy)/vv):0,cpa=Math.hypot(rx+vx*t,ry+vy*t);spacing+=q.weight*clamp(cpa/700,0,1);
      const assigned=r.combatSystem.fireControl.illuminatorAssignments.get(q.trackId);if(assigned?.illId!=null&&current.spg.find(v=>v.id===assigned.illId)?.open){supportCount++;if(!c.spg.find(v=>v.id===assigned.illId)?.open)supportRisk++;}
      opportunities.push({trackId:q.trackId,spgOpen:c.spg.filter(q=>q.open).map(q=>q.id),closeInOpen:c.closeIn.filter(q=>q.open).map(q=>q.id),cpaM:cpa});
    }
    const turnCost=Math.abs(angNorm(headingRad-n.heading))/Math.PI,speedCost=Math.abs(speedKt-requested)/31,score=guard.ok?.55*coverage/Math.max(.1,weight)+.2*spacing/Math.max(.1,weight)+.1*aspect/Math.max(.1,weight)-.12*turnCost-.08*speedCost-.45*supportRisk/Math.max(1,supportCount)+(id==='KEEP'?.02:0):-1;
    candidates.push({id,headingRad,speedKt,score,guard,coverage:coverage/Math.max(.1,weight),supportRisk,supportCount,predictedHeadingRad:prediction.final.heading,predictedSpeedMps:prediction.final.speedMps,horizonS:horizon,opportunities});
  }candidates.sort((a,b)=>b.score-a.score||specs.findIndex(q=>q[0]===a.id)-specs.findIndex(q=>q[0]===b.id));return candidates;
}
function maneuverChooseH2(s,now,candidates,emergency){const best=candidates[0],current=candidates.find(q=>q.id===s.selected);if(s.baseline&&s.command===null)return best;if(!current||!current.guard.ok||emergency||now-s.sinceS>=MANEUVER_POLICY_H2.minHoldS&&best.score>current.score+MANEUVER_POLICY_H2.switchMargin)return best;return current;}
function maneuverApplyH2(r,choice,damage){
  if(!maneuverActiveH2(r)||shipEquipmentOfflineV1(r))return;
  const n=r.navigation,limit=30*Math.max(.1,damage.steerFac??0),rudder=clamp(angNorm(choice.headingRad-n.heading)*180/Math.PI*1.6-n.turnRate*90,-limit,limit),command={targetSpeedKt:choice.speedKt,targetRudder:rudder};
  if(r!==ACTIVE_SHIP_RUNTIME){const q=physicalShipCommandB(r.entityId,command,'TACTICAL_H2');if(!q.ok)return;}else Object.assign(n,command);
  n.manualSpeedV15=true;n.manualRudderV15=true;n.telegraph=c17OrderForKt(choice.speedKt);n._c17Kt=choice.speedKt;prepareManeuverH2(r).command={headingRad:choice.headingRad,speedKt:choice.speedKt,rudderDeg:rudder};
}
function maneuverEvaluateH2(r){
  const s=prepareManeuverH2(r);if(s.lastStep===simStepCounter)return;s.lastStep=simStepCounter;s.evaluations++;const now=networkNowG(),damage=getShipDamageEffects(r);
  if(!maneuverActiveH2(r)||shipEquipmentOfflineV1(r)){maneuverYieldH2(r);s.summary={reason:s.settings.manualNav?'MANUAL_NAV':shipEquipmentOfflineV1(r)?'OFFLINE':'INACTIVE',localThreats:0};s.candidates=[];return;}
  const rows=maneuverObservedH2(r);s.summary={reason:'MONITOR',localThreats:rows.length,steering:damage.steerFac,propulsion:damage.accelFac};
  if(!rows.length){
    if(!s.baseline)return;if(now-s.lastDangerS<MANEUVER_POLICY_H2.quietS)return;
    const heading=maneuverMissionHeadingH2(r,s),speed=maneuverSpeedH2(r,s.baseline.order.targetSpeedKt,damage);if(Math.abs(angNorm(heading-r.navigation.heading))<deg(2)){maneuverYieldH2(r);s.candidates=[];s.summary.reason='BASELINE_RESTORED';return;}
    const prediction=maneuverPredictH2(r,heading,speed,30,damage),guard=maneuverPathGuardH2(r,prediction,maneuverTrafficH2(r));s.selected=guard.ok?'RECOVER':'SAFETY_HOLD';s.summary.reason=s.selected;
    maneuverApplyH2(r,{headingRad:guard.ok?heading:r.navigation.heading,speedKt:guard.ok?speed:0},damage);return;
  }
  s.lastDangerS=now;if(!s.baseline){const order={};for(const k of MANEUVER_NAV_KEYS_H2)if(Object.hasOwn(r.navigation,k))order[k]=r.navigation[k];s.baseline={order,headingRad:r.navigation.heading};s.sinceS=now;}
  const candidates=maneuverPlanH2(r,rows,damage,s);s.candidates=candidates;let choice=maneuverChooseH2(s,now,candidates,Math.min(...rows.map(q=>q.ttiS))<=12);
  if(!choice.guard.ok)choice={id:'SAFETY_HOLD',headingRad:r.navigation.heading,speedKt:0,score:-1};
  if(choice.id!==s.selected){s.log.push({step:simStepCounter,from:s.selected,to:choice.id,score:choice.score});if(s.log.length>MANEUVER_POLICY_H2.maxLog)s.log.shift();s.sinceS=now;}
  s.selected=choice.id;s.summary.reason=choice.id;s.summary.earliestTtiS=Math.min(...rows.map(q=>q.ttiS));maneuverApplyH2(r,choice,damage);
}
function stepManeuverFleetH2(){if(simStepCounter%MANEUVER_POLICY_H2.periodTicks!==0)return;for(const r of [ACTIVE_SHIP_RUNTIME,...physicalShipsB()])maneuverEvaluateH2(r);}
function maneuverSnapshotH2(){return {schema:MANEUVER_POLICY_H2.schema,truthUsed:false,remoteFireControl:false,ships:[ACTIVE_SHIP_RUNTIME,...physicalShipsB()].map(r=>{const s=prepareManeuverH2(r);return {entityId:r.entityId,settings:{...s.settings},active:maneuverActiveH2(r),owned:!!s.baseline,selected:s.selected,sinceS:s.sinceS,lastStep:s.lastStep,evaluations:s.evaluations,summary:s.summary?{...s.summary}:null,command:s.command?{...s.command}:null,candidates:jsonSafeCloneV48Wip11A(s.candidates),log:s.log.map(q=>({...q}))};})};}
function maneuverSelfTestH2(){const s={selected:'KEEP',sinceS:0},rows=[{id:'PORT30',score:.8,guard:{ok:true}},{id:'KEEP',score:.5,guard:{ok:true}}],checks={hold:maneuverChooseH2(s,1,rows,false).id==='KEEP',normal:maneuverChooseH2(s,3,rows,false).id==='PORT30',emergency:maneuverChooseH2(s,.1,rows,true).id==='PORT30',blocked:maneuverChooseH2(s,.1,[rows[0],{...rows[1],guard:{ok:false}}],false).id==='PORT30',margin:maneuverChooseH2(s,4,[{...rows[0],score:.53},rows[1]],false).id==='KEEP'};return {checks,pass:Object.values(checks).every(Boolean)};}
