// SEEKER_UNIFY_B test-only U0 probes. Debug identity is copied only into
// after-action evidence and is never consumed by tactical code.
(() => {
  function reset(seed,emcon){
    _wip75ResetCase(seed);worldTimeScale=0;simAccumulator=0;BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;
    enemyMissiles.length=0;missiles.length=0;ramMissiles.length=0;targetPool.length=0;tracks.clear();resetSurfaceContacts();ownChaffs.length=0;
    applyDeploymentA(prepareDeploymentA({schema:DEPLOYMENT_POLICY_F.schema,targetShip:'NONE',enemyProfileId:null,allyProfileId:null,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:seed>>>0,allyEmcon:true,enemyEmcon:true}));
    emconActive=!!emcon;resetShipboardRadarRfRngWip13B13();
  }
  function cueState(em){
    const s=em.seeker,q=em._targetCueU0;
    return {basket:s?.lastCueBasketU0?{...s.lastCueBasketU0}:null,legacyPass:s?.cueLegacyPassCountU0??null,expandedPass:s?.cueExpandedPassCountU0??null,expandedOnly:s?.cueExpandedOnlyCountU0??null,
      passive:q?{attempts:q.passiveCorrectionAttempts,updates:q.passiveBearingClockUpdates,lastResidualRad:q.lastPassiveBearingResidualRad??null,lastConverged:q.lastPassiveBearingConverged??null,rangeRefTimeS:q.rangeRefTimeS,bearingRefTimeS:q.bearingRefTimeS,source:q.source}:null};
  }
  function runCueCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||729300,label=String(opts.label??'Kh-35U'),rangeKm=Number(opts.rangeKm??100),speedKt=Number(opts.speedKt??30),turnDeg=Number(opts.turnDeg??0),emcon=!!opts.emcon;reset(seed,emcon);
    const ax=aircraft.x(),ay=aircraft.y(),speed=speedKt*.514444,launchX=ax-kmToWorld(rangeKm),launchY=ay,initialCourse=0,turnAtS=Math.max(4,rangeKm*1000/(label==='Kh-32'?1200:280)/3);
    shipNav.heading=initialCourse;shipNav.speed=speed;shipNav.vx=mpsToWorldSpeed(speed);shipNav.vy=0;
    spawnEnemyMissile({id:730000+seed,x:launchX,y:launchY,z:label==='Kh-32'?10000:200,heading:0,vx:mpsToWorldSpeed(label==='Kh-32'?1200:280),vy:0,vz:0,asmType:label,lastKnownShipX:ax,lastKnownShipY:ay});
    const em=enemyMissiles.at(-1);let everAcquire=false,everTrack=false,firstAcquireS=null,firstTrackS=null,firstAcquireBasket=null,firstTrackBasket=null,firstAccepted=null,closestM=Infinity,passedForS=0,endedBy='TIMEOUT',ticks=0;
    const maxTicks=Math.ceil(Math.min(610,rangeKm*1000/(label==='Kh-32'?650:180)+180)/SIM_FIXED_DT),hitCount0=shipHitHistory.length;
    for(;ticks<maxTicks&&em.alive;ticks++){
      if(ticks*SIM_FIXED_DT>=turnAtS&&turnDeg!==0){const c=deg(turnDeg);shipNav.heading=c;shipNav.vx=mpsToWorldSpeed(Math.cos(c)*speed);shipNav.vy=mpsToWorldSpeed(Math.sin(c)*speed);}
      shipNav.previousPositionWorld={...shipNav.positionWorld};shipNav.positionWorld.x+=shipNav.vx*SIM_FIXED_DT;shipNav.positionWorld.y+=shipNav.vy*SIM_FIXED_DT;
      updateEnemyMissile(em,SIM_FIXED_DT);simStepCounter++;
      const d=Math.hypot(worldToMeters(em.x-aircraft.x()),worldToMeters(em.y-aircraft.y()),(em.z??0)-8);if(d<closestM){closestM=d;passedForS=0;}else if(d>closestM+200)passedForS+=SIM_FIXED_DT;
      const s=em.seeker,mode=s?.mode;if(!firstAccepted&&(s?.acceptedDiscreteCount??0)+(s?.acceptedSeaOnlyCount??0)>0)firstAccepted={timeS:ticks*SIM_FIXED_DT,kind:s.lastAssocDebugKind??null,id:s.lastAssocDebugId??null,evidence:s.lastAcceptedEvidence??null};
      if(mode==='ACQUIRE'&&!everAcquire){everAcquire=true;firstAcquireS=ticks*SIM_FIXED_DT;firstAcquireBasket=cueState(em);}
      if(mode==='TRACK'&&!everTrack){everTrack=true;firstTrackS=ticks*SIM_FIXED_DT;firstTrackBasket=cueState(em);}
      if(passedForS>8){endedBy='PASSED_TARGET';break;}
    }
    if(shipHitHistory.length>hitCount0)endedBy='GAME_SHIP_HIT';else if(!em.alive)endedBy=em._outcome??em._deathReason??'GAME_TERMINATED';
    return {setup:{seed,label,rangeKm,speedKt,turnDeg,turnAtS,emcon},result:{everAcquire,everTrack,firstAcquireS,firstTrackS,firstAcquireBasket,firstTrackBasket,firstAccepted,finalCue:cueState(em),finalMode:em.seeker?.mode??null,closestM,endedBy,alive:!!em.alive,flightTimeS:ticks*SIM_FIXED_DT,shipHit:shipHitHistory.length>hitCount0,rejectReason:em.seeker?.lastRejectReasonWip13C8??null}};
  }
  function cueContract(){
    return {available:typeof ASM_CUE_BASKET_U0!=='undefined',profile:typeof ASM_CUE_BASKET_U0==='undefined'?null:{...ASM_CUE_BASKET_U0},targetCue:typeof asmTargetCueU0==='undefined'?null:asmTargetCueU0.toString(),basket:typeof asmCueBasketU0==='undefined'?null:asmCueBasketU0.toString(),passive:asmApplyPassiveBearingB2.toString(),association:asmSeekerAssociateMeasurements.toString()};
  }
  window.__SEEKER_UNIFY_B_DIAG__=Object.freeze({runCueCase,cueContract});
})();
