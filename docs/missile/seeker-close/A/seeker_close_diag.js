// SEEKER_CLOSE_A TEST-ONLY after-action instrumentation.
//
// This module is injected only into a separate diagnostic build.  Physical
// labels and target coordinates are read only after a fixture has terminated;
// no value produced here is consumed by seeker, guidance, ROE or weapon code.
(() => {
  const C={active:false,missileId:null,raw:[],faults:[],maxRows:24000};
  const stamp=()=>({step:simStepCounter,timeS:simStepCounter*SIM_FIXED_DT});
  const safe=(fn)=>{try{return fn();}catch(error){C.faults.push({...stamp(),error:String(error?.stack??error)});return null;}};
  const upper=value=>String(value??'').toUpperCase();
  const members=value=>[...new Set((value?._debugMembers??[value?._debugKind]).filter(Boolean).map(upper))];
  const isDecoyKind=value=>['CHAFF','NULKA'].some(kind=>upper(value).includes(kind));
  const isShipKind=value=>upper(value).includes('SHIP');
  const rangeToOwnM=em=>Math.hypot(worldToMeters(em.x-aircraft.x()),worldToMeters(em.y-aircraft.y()),(em.z??0)-OWN_ALT_M);

  // Observe the real physical-return call exactly once.  The wrapper neither
  // calls a second producer nor consumes RNG.
  const originalVisible=asmSeekerVisibleRfReturns;
  asmSeekerVisibleRfReturns=function(em,s,p){
    const result=originalVisible.apply(this,arguments);
    if(C.active&&em?.id===C.missileId&&C.raw.length<C.maxRows)safe(()=>{
      const row={...stamp(),mode:s?.mode??null,kinds:result.map(q=>({kind:q._debugKind??null,id:q._debugId??null,rangeM:asmSeekerReturnGeometry(em,q).rangeM}))};
      const prior=C.raw.at(-1);const signature=JSON.stringify(row.kinds.map(q=>[q.kind,q.id]));
      if(!prior||prior.signature!==signature||simStepCounter%15===0)C.raw.push({...row,signature});
    });
    return result;
  };

  function resetCapture(id){C.active=true;C.missileId=id;C.raw.length=0;C.faults.length=0;}
  function stopCapture(){C.active=false;C.missileId=null;}
  function countBy(rows,key){const out={};for(const row of rows){const value=String(row[key]??'UNSPECIFIED');out[value]=(out[value]??0)+1;}return out;}
  function eventKinds(event){
    const values=[];
    if(event?.selected)values.push(...members(event.selected));
    for(const candidate of event?.candidates??[])values.push(...members(candidate));
    return [...new Set(values)];
  }
  function decoyStage(kind,deployment,raw,events,targetHit,terminalCategory){
    if(!deployment?.attempted)return 'NOT_DEPLOYED';
    if(!deployment.ok)return 'NOT_DEPLOYED';
    if(!deployment.seekerOnAtDeployment)return 'DEPLOYED_OUTSIDE_WINDOW';
    const rawSeen=raw.some(row=>row.kinds.some(q=>upper(q.kind).includes(kind)));
    const candidateEvents=events.filter(event=>event.kind==='ASSOCIATION'&&(event.candidates??[]).some(q=>members(q).some(v=>v.includes(kind))));
    const selectedEvents=events.filter(event=>event.kind==='ASSOCIATION'&&event.selected&&members(event.selected).some(v=>v.includes(kind)));
    if(!rawSeen)return 'DEPLOYED_NOT_OBSERVABLE';
    if(!candidateEvents.length)return 'OBSERVABLE_GATE_REJECTED';
    if(!selectedEvents.length)return 'CANDIDATE_NOT_SELECTED';
    const selectedStep=selectedEvents[0].step;
    const recovered=events.some(event=>event.kind==='ASSOCIATION'&&event.step>selectedStep&&event.selected&&members(event.selected).some(isShipKind));
    if(targetHit||recovered)return 'SELECTED_THEN_RECOVERED_TARGET';
    if(['KINEMATIC_MISS','SEA_IMPACT','SEEKER_ASSOCIATION_DROP','SEEKER_GATE_REJECT','SEEKER_SEARCH_ACQUIRE_LOOP','SEEKER_COAST_TIMEOUT','SEEKER_NO_VALID_MEASUREMENT'].includes(terminalCategory))return 'SEDUCED';
    return 'CANDIDATE_NOT_SELECTED';
  }
  function terminalCategory(em,events,raw,hits,closestApproachM,decoySelected,egressQualified){
    const cause=upper(em?._deathReason??em?._wip113Outcome??em?.retiredReason??em?._wip11cRetirementQueued?.cause??'');
    if(/PHALANX|CIWS/.test(cause))return 'CIWS_KILL';
    if(/INTERCEPT|SAM_KILL|RAM|ESSM|SM-2|SM2/.test(cause))return 'DEFENSE_INTERCEPT';
    const targetHit=hits.some(hit=>!hit.miss&&(hit.label===em.label||!hit.label));
    if(targetHit||/NORMAL_HIT|DUD_PENETRATION|SHIP_IMPACT/.test(cause))return 'TARGET_HIT';
    if(/SEA_IMPACT|TERRAIN_IMPACT|GROUND_IMPACT|WATER/.test(cause))return 'SEA_IMPACT';
    if(/GUIDANCE_CONTROL_LOSS/.test(cause))return 'GUIDANCE_CONTROL_LOSS';
    if(/TARGET_REMOVED|TARGET_INVALID/.test(cause))return 'TARGET_REMOVED_OR_INVALID';
    const states=(window.__ASM_SEEKER_A_DIAG__.finishBattle().states??[]).filter(q=>q.missileId===em.id);
    // finishBattle is read-only and can be called again by the caller.  No
    // diagnostic value is fed to a tactical path.
    const transitions=states.filter(q=>q.before!==q.after);
    const selected=events.filter(q=>q.kind==='ASSOCIATION'&&q.selected);
    const everTrack=states.some(q=>q.after==='TRACK'||q.trackValid);
    const searchAcquireReturns=transitions.filter(q=>q.before==='ACQUIRE'&&q.after==='SEARCH').length;
    const sameValidCandidateLoop=searchAcquireReturns>=2&&selected.length>=2&&new Set(selected.map(q=>q.selected?._debugId??q.selected?._debugKind)).size===1;
    if(decoySelected&&egressQualified)return 'KINEMATIC_MISS';
    if(sameValidCandidateLoop)return 'SEEKER_SEARCH_ACQUIRE_LOOP';
    const coastTimedOut=transitions.some(q=>q.before==='COAST'&&['SEARCH','LOST','OFF'].includes(q.after))&&!transitions.some(q=>q.before==='REACQUIRE'&&q.after==='TRACK');
    if(coastTimedOut)return 'SEEKER_COAST_TIMEOUT';
    const dwell=events.filter(q=>q.kind==='DWELL_RESULT'),last=dwell.at(-1);
    if(everTrack&&!selected.length)return 'SEEKER_ASSOCIATION_DROP';
    if(last&&!last.accepted&&(last.raw>0||last.echoes>0||last.candidates>0))return 'SEEKER_GATE_REJECT';
    if(!selected.length)return 'SEEKER_NO_VALID_MEASUREMENT';
    if(hits.some(hit=>hit.miss)||egressQualified||(!em.alive&&closestApproachM>100))return 'KINEMATIC_MISS';
    return 'UNCLASSIFIED';
  }

  function runCase(options={}){
    const seed=(Number(options.seed)>>>0)||0x5ec10a,label=String(options.label??'Kh-35U'),rangeKm=Number(options.rangeKm??18),speedMps=Number(options.speedMps??300),maxTimeS=Number(options.maxTimeS??90),timeScale=Math.max(1,Math.round(Number(options.timeScale??1))),hardKill=!!options.hardKill,chaff=!!options.chaff,nulka=!!options.nulka,ecm=!!options.ecm,emcon=!!options.emcon;
    _wip75ResetCase(seed);worldTimeScale=0;simAccumulator=0;DIAG_SUPPRESS_PATROLS=true;BATTLESPACE_DIAG_BYPASS=true;
    const fixture=window.__NAVAL_SIM_DIAG__.createTerminalAsmFixture({label,rangeKm,speedMps,bearingDeg:Number(options.bearingDeg??0),altM:Number(options.altM??15)}),em=enemyMissiles.find(q=>q.id===fixture.enemyId);
    if(!em)throw new Error('SEEKER_CLOSE_FIXTURE_MISSING');
    const track=tracks.get(fixture.trackId);if(track){track.identity='HOSTILE';track._operatorIdentity='HOSTILE';track.threatStatus='THREAT';track.classification='ASM';track.confirmed=true;track.sensorDetected=true;track.sensorAge=0;}
    softKillAutoDoctrine=false;noiseJamActive=false;deceptJamActive=false;jammerAutoTrack=false;emconActive=emcon;
    if(typeof wip119SetMode==='function')wip119SetMode(hardKill?'AUTO':'MANUAL');
    const hitStart=shipHitHistory.length,rngStart=SIM_RNG_STATE>>>0,launchTimeS=simStepCounter*SIM_FIXED_DT;
    resetCapture(em.id);window.__ASM_SEEKER_A_DIAG__.beginBattle([em.id]);
    updateSoftKillThreatManager(SIM_FIXED_DT);
    if(nulka){window.__NAVAL_SIM_DIAG__.injectActiveSeekerEsmForTracks('TRACK',.98);updateSoftKillThreatManager(SIM_FIXED_DT);}
    const threat=softKillPrimaryThreat(),deployments={
      CHAFF:{attempted:chaff,ok:false,count:0,reason:chaff?'NO_THREAT_OR_LAUNCH_FAILED':'NOT_REQUESTED',timeS:simStepCounter*SIM_FIXED_DT,seekerOnAtDeployment:!!em.seekerOn},
      NULKA:{attempted:nulka,ok:false,count:0,reason:nulka?'NO_THREAT_OR_LAUNCH_FAILED':'NOT_REQUESTED',timeS:simStepCounter*SIM_FIXED_DT,seekerOnAtDeployment:!!em.seekerOn},
    };
    if(chaff){const fired=deployOwnChaffForThreat(threat,{automatic:false});Object.assign(deployments.CHAFF,{ok:fired>0,count:fired,reason:fired>0?null:'LAUNCH_FAILED'});}
    if(nulka){const fired=nulkaFire15B(threat,{automatic:false,quiet:true});Object.assign(deployments.NULKA,{ok:!!fired?.ok,count:fired?.ok?1:0,reason:fired?.ok?null:(fired?.reason??'LAUNCH_FAILED'),id:fired?.id??null});}
    if(ecm){noiseJamActive=true;deceptJamActive=true;jammerAutoTrack=true;}
    let closestApproachM=rangeToOwnM(em),outwardTicks=0,ticks=0,frames=0,egressQualified=false;
    const maxTicks=Math.ceil(maxTimeS/SIM_FIXED_DT);
    while(ticks<maxTicks&&em.alive){
      frames++;
      for(let batch=0;batch<timeScale&&ticks<maxTicks&&em.alive;batch++){
        const before=rangeToOwnM(em);
        if(hardKill){simulateFixedTick(SIM_FIXED_DT);}else{
          if(ecm){updateSoftKillThreatManager(SIM_FIXED_DT);updateJammerBearing(SIM_FIXED_DT);updateSlq32EaAllocator(SIM_FIXED_DT);}
          updateOwnChaff(SIM_FIXED_DT);updateEnemyMissile(em,SIM_FIXED_DT);simStepCounter++;
        }
        const after=rangeToOwnM(em);closestApproachM=Math.min(closestApproachM,after);outwardTicks=after>before?outwardTicks+1:0;ticks++;
        if(after>30000&&outwardTicks>=Math.ceil(10/SIM_FIXED_DT)){egressQualified=true;break;}
      }
      if(rangeToOwnM(em)>30000&&outwardTicks>=Math.ceil(10/SIM_FIXED_DT)){egressQualified=true;break;}
    }
    const battle=window.__ASM_SEEKER_A_DIAG__.finishBattle();stopCapture();
    const events=(battle.events??[]).filter(q=>q.missileId===em.id),states=(battle.states??[]).filter(q=>q.missileId===em.id),hits=shipHitHistory.slice(hitStart),selectedEvents=events.filter(q=>q.kind==='ASSOCIATION'&&q.selected),selectedKinds=[...new Set(selectedEvents.flatMap(event=>members(event.selected)))],decoySelected=selectedKinds.some(isDecoyKind);
    let category=terminalCategory(em,events,C.raw,hits,closestApproachM,decoySelected,egressQualified);
    const targetHit=hits.some(hit=>!hit.miss&&(hit.label===label||!hit.label));
    const decoyStages={CHAFF:decoyStage('CHAFF',deployments.CHAFF,C.raw,events,targetHit,category),NULKA:decoyStage('NULKA',deployments.NULKA,C.raw,events,targetHit,category)};
    if(Object.values(decoyStages).includes('SEDUCED')&&!['DEFENSE_INTERCEPT','CIWS_KILL','TARGET_HIT'].includes(category))category='DECOY_SEDUCTION';
    const validEvents=selectedEvents,transitions=states.filter(q=>q.before!==q.after).map(q=>({step:q.step,timeS:q.timeS,from:q.before,to:q.after,trackValid:q.trackValid,guidanceSource:q.guidanceSource})),dwell=events.filter(q=>q.kind==='DWELL_RESULT');
    const retirement=em._wip11cRetirementQueued?{cause:em._wip11cRetirementQueued.cause??null,weaponLabel:em._wip11cRetirementQueued.weaponLabel??null,result:em._wip11cRetirementQueued.result??null,step:em._wip11cRetirementQueued.step??null}:null;
    const result={schema:'AEGIS_SEEKER_CLOSE_A_SHOT_1',ship:ACTIVE_SHIP_RUNTIME.profileId,condition:String(options.condition??'UNNAMED'),weapon:label,profile:em.seeker?.profileId??null,seed,launchTimeS,terminalTimeS:simStepCounter*SIM_FIXED_DT,terminalCategory:category,nativeCause:em._deathReason??em._wip113Outcome??em.retiredReason??retirement?.cause??null,retirement,aliveAtEnd:!!em.alive,egressQualified,terminalQualified:!em.alive||egressQualified,firstValidObservationS:validEvents[0]?.timeS??null,lastValidObservationS:validEvents.at(-1)?.timeS??null,stateTransitions:transitions,transitionCounts:countBy(transitions,'to'),searchAcquireReturns:transitions.filter(q=>q.from==='ACQUIRE'&&q.to==='SEARCH').length,gateRejectReasons:countBy(dwell.filter(q=>!q.accepted),'rejectReason'),validCandidateCounts:{max:Math.max(0,...dwell.map(q=>Number(q.validated)||0)),selectedEvents:validEvents.length},selectedCandidateKinds:selectedKinds,guidanceAvailable:states.some(q=>q.trackValid||q.guidanceSource==='RF_EKF'),decoyDeployments:deployments,decoyStages,rawDecoyKinds:[...new Set(C.raw.flatMap(row=>row.kinds.map(q=>upper(q.kind))).filter(isDecoyKind))],hardKillIntervention:category==='DEFENSE_INTERCEPT',ciwsIntervention:category==='CIWS_KILL',softKillIntervention:chaff||nulka||ecm,closestApproachM,seaImpact:category==='SEA_IMPACT',targetHit,combatRngStart:rngStart,combatRngEnd:SIM_RNG_STATE>>>0,ticks,frames,timeScale,emcon,ecm,hardKill,chaff,nulka,diagnosticFaults:[...C.faults,...(battle.faults??[])],afterActionTruthOnly:true,tacticalConsumerReads:0};
    return result;
  }

  function runHarpoonSupport(seed=0x5ec300){
    window.__ASM_SEEKER_A_DIAG__.configure({enabled:true});
    const physical=window.__ASM_SEEKER_A_DIAG__.runHarpoonPhysical({seed,targetMode:'OWN_PLUS_TARGET'}),core=window.__HARPOON_DIAG_A__.coreAudit(),seeker=window.__HARPOON_DIAG_A__.seekerAudit(),selection=window.__HARPOON_DIAG_A__.selectionAudit();
    return {schema:'AEGIS_SEEKER_CLOSE_A_HARPOON_SUPPORT_1',ship:ACTIVE_SHIP_RUNTIME.profileId,seed,physical,core,seeker,selection,terminalShot:false,reason:'BOUNDED_SENSOR_PATH_SUPPORT_NOT_TERMINAL_CLASSIFICATION'};
  }
  function contractAudit(){
    const common=window.__SEEKER_U4_C__.contractAudit(),snapshot=window.__SEEKER_U4_C__.snapshot(),source=[runCase,terminalCategory,decoyStage].map(String).join('\n');
    return {schema:'AEGIS_SEEKER_CLOSE_A_DIAGNOSTIC_CONTRACT_1',afterActionOnly:true,tacticalConsumerReads:0,classifierTruthFeedback:/selectedLockId\s*=|seekerTgt[XY]\s*=|insTgt[XY]\s*=/.test(source),commonAnonymous:common.anonymousDecisionSource,commonRngCalls:common.rngCalls,commonSaveSchemaChanged:common.saveSchemaChanged,commonRngConsumed:snapshot.rngConsumedByCommonLayer,pass:common.pass&&!snapshot.rngConsumedByCommonLayer&&!snapshot.saveSchemaChanged};
  }
  window.__SEEKER_CLOSE_A_DIAG__=Object.freeze({schema:'AEGIS_SEEKER_CLOSE_A_DIAGNOSTIC_1',runCase,runHarpoonSupport,contractAudit,snapshot:()=>({active:C.active,missileId:C.missileId,rawRows:C.raw.length,faults:[...C.faults]})});
})();
