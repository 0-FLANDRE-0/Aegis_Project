// DIAGNOSTIC_ONLY: archived C10 real flight harness, injected into a VM at runtime; never packed into production.
window.__W14_TEST__={};
window.__C18_TEST__={surfaceCard(o={}){
 const tr=makeSurfaceMissileFixtureTrackWip13C4({bearingRad:deg(o.bearingDeg??90),identity:o.identity??'TRAINING_TARGET'});
 return lockedTrackCardLines(tr,tr.trackId,true);
},surfaceReasons(){const tr=makeSurfaceMissileFixtureTrackWip13C4({bearingRad:deg(90),identity:'TRAINING_TARGET'});return ['SM2','ESSM'].map(key=>surfaceMissileReleaseAssessmentWip13C4(tr,key,{mode:engagementControlMode}).reason);},surfaceCardPure(){
 const tr=makeSurfaceMissileFixtureTrackWip13C4({bearingRad:deg(90),identity:'TRAINING_TARGET'});
 const state=()=>JSON.stringify({rng:SIM_RNG_STATE,steps:simStepCounter,reservations:[...SPG62_RESERVATION_STATE],engagements:[...SPG62_ENGAGEMENT_STATE],servo:ACTIVE_SHIP_RUNTIME.combatSystem.fireControl.spg62Servo.mounts});
 const before=state();for(let i=0;i<8;i++)lockedTrackCardLines(tr,tr.trackId,true);return before===state();
}};
window.__W14_TEST__.fullFlight=function(o={}){
 _wip75ResetCase(o.seed??1350501);resetEngagementTransientV48Wip11A();resetOwnshipWorldWip14A(metersToWorld(o.xM??0),metersToWorld(o.yM??0));
 BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;engagementControlMode='MANUAL';emconActive=false;routePoints.length=0;navObjective.reached=true;
 surfaceContacts.length=0;SURFACE_TARGET_ENTITY_REGISTRY_V48_WIP13A.clear();
 shipNav.heading=deg(o.ownHeadingDeg??0);shipNav.previousHeadingWorld=shipNav.heading;shipNav.speed=(o.ownSpeedKt??25)*.514444;shipNav.targetSpeedKt=o.ownSpeedKt??25;shipNav.vx=mpsToWorldSpeed(shipNav.speed)*Math.cos(shipNav.heading);shipNav.vy=mpsToWorldSpeed(shipNav.speed)*Math.sin(shipNav.heading);shipNav.rudder=0;shipNav.targetRudder=0;shipNav.manualRudderV15=true;shipNav.manualSpeedV15=true;
 const bearing=deg(o.bearingDeg??90),target=spawnSurfaceTargetWip13A({entityId:'W14_LIVE_TARGET',x:aircraft.x()+Math.cos(bearing)*kmToWorld(8),y:aircraft.y()+Math.sin(bearing)*kmToWorld(8),heading:bearing+Math.PI/2,speedKt:15,mobilityMode:'FREE_RUNNING'});
 for(let i=0;i<1200;i++){simulateFixedTick(SIM_FIXED_DT);if(i%300===299)console.log('RADAR_WARMUP',i+1);}
 const tr=[...tracks.values()].filter(t=>surfaceTrackWip13C5(t)&&t.confirmed).sort((a,b)=>(b.trackQuality??0)-(a.trackQuality??0))[0];
 if(!tr)return {error:'NO_SENSOR_TRACK',fault:simRuntimeFault,lastError:lastErrorMsg};
 setTrackOperatorIdentityA3(tr.trackId,'TRAINING_TARGET');selectedLockId=tr.trackId;
 if(o.spgDisabled)for(const ill of SPG62_ILLUMINATORS)addModuleDmg(ill.moduleName,100);
 const weapon=o.weapon??'SM2',assessment=surfaceMissileReleaseAssessmentWip13C4(tr,weapon,{mode:'MANUAL'}),n=missiles.length,before=getVlsCounts();
 console.log('LAUNCH_START',weapon,'track',tr.trackId,'assessment',assessment.reason);
 (weapon==='ESSM'?spawnESSM:spawnMissile)({automatic:false});const m=missiles.length>n?missiles.at(-1):null;
 console.log('LAUNCH_DONE',weapon,'missile',m?.id??null);
 if(!m)return {error:'RELEASE_INHIBITED',assessment,before,after:getVlsCounts(),fault:simRuntimeFault,lastError:lastErrorMsg};
 let minRangeM=Infinity;const trace=[];for(let k=0;k<1800&&!m.dead;k++){if(k%20===0||k>=238&&k<=270)console.log('MISSILE_TICK_START',k);simulateFixedTick(SIM_FIXED_DT);if(k>=238&&k<=270)console.log('MISSILE_TICK_END',k);const rangeM=Math.hypot(worldToMeters(m.x-target.x),worldToMeters(m.y-target.y),m.z-8);minRangeM=Math.min(minRangeM,rangeM);if(k%60===0||m.dead)trace.push({t:m.life,x:worldToMeters(m.x),y:worldToMeters(m.y),z:m.z,source:m._v1GuidanceAuthority,heading:m.heading,pitch:m.pitch,ownship:{...shipNav.positionWorld},rangeM});if(k%300===299)console.log('MISSILE_FLIGHT',k+1,'rangeM',Math.round(rangeM),'mode',m._v1GuidanceAuthority,'servo',ACTIVE_SHIP_RUNTIME.combatSystem.fireControl.spg62Servo.mounts.map(q=>q.mode).join('/'));}
 return {schema:'AEGIS_WIP13C22_REAL_FIXED_LOOP_FLIGHT',options:o,assessment,before,after:getVlsCounts(),deathReason:m._deathReason??'TIMEOUT',lifeS:m.life,minRangeM,trace,damage:surfaceTargetSnapshotWip13A(target).damage,impact:m._surfaceImpact??null,terminalEvent:wip12bTerminalEventsSnapshot().find(e=>e.impactEventId===m._surfaceImpact?.eventId)??null,fault:simRuntimeFault,lastError:lastErrorMsg};
};
window.__W14_TEST__.drawCic=function(){drawRadar();updateHud();updateMissilePanel();drawAltitudeDisplay();drawShipDetail();return {fault:simRuntimeFault,error:lastErrorMsg,width:canvas.width,height:canvas.height,core:window.__CORE_SELFTEST_FAILURES__};};
