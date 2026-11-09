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
  function anonymousAssociation(event){
    if(!event?.selected)return null;
    return {
      source:'ASM_SEEKER_ASSOCIATION_EVENT',step:event.step,timeS:event.timeS,mode:event.mode??null,
      family:event.family??null,selectedCandidateKind:event.selected?._debugKind??event.family??null,
      selectedKinds:members(event.selected),candidateKinds:eventKinds(event),candidateCount:(event.candidates??[]).length,
    };
  }
  function decoyEvidence(kind,deployment,raw,events,targetHit,terminalCategory,egressQualified){
    const associationEvents=events.filter(event=>event.kind==='ASSOCIATION'&&event.selected);
    const rawSeen=raw.some(row=>row.kinds.some(q=>upper(q.kind).includes(kind)));
    const candidateEvents=events.filter(event=>event.kind==='ASSOCIATION'&&(event.candidates??[]).some(q=>members(q).some(v=>v.includes(kind))));
    const selectedEvents=associationEvents.filter(event=>members(event.selected).some(v=>v.includes(kind)));
    const firstSelected=selectedEvents[0]??null,lastSelected=selectedEvents.at(-1)??null,firstRecovered=firstSelected?associationEvents.find(event=>event.step>firstSelected.step&&members(event.selected).some(isShipKind))??null:null,lastSelectionRecovery=lastSelected?associationEvents.find(event=>event.step>lastSelected.step&&members(event.selected).some(isShipKind))??null:null;
    const lastValid=associationEvents.at(-1)??null,lastKinds=lastValid?members(lastValid.selected):[],lastDecoyOnly=!!lastValid&&lastKinds.some(v=>v.includes(kind))&&!lastKinds.some(isShipKind);
    const terminalMiss=['KINEMATIC_MISS','SEA_IMPACT','SEEKER_ASSOCIATION_DROP','SEEKER_GATE_REJECT','SEEKER_SEARCH_ACQUIRE_LOOP','SEEKER_COAST_TIMEOUT','SEEKER_NO_VALID_MEASUREMENT'].includes(terminalCategory)||egressQualified;
    let stage='SELECTED_OUTCOME_UNRESOLVED',unresolvedReason=null,causalEvidence=null;
    if(!deployment?.attempted)stage='NOT_DEPLOYED';
    else if(!deployment.ok){stage='NOT_DEPLOYED';unresolvedReason=deployment.reason??'DEPLOYMENT_FAILED';}
    else if(!deployment.seekerOnAtDeployment){stage='DEPLOYED_OUTSIDE_WINDOW';unresolvedReason='SEEKER_NOT_ACTIVE_AT_DEPLOYMENT';}
    else if(!rawSeen){stage='DEPLOYED_NOT_OBSERVABLE';unresolvedReason='NO_PHYSICAL_RETURN_OBSERVED';}
    else if(!candidateEvents.length){stage='OBSERVABLE_GATE_REJECTED';unresolvedReason='NO_ASSOCIATION_CANDIDATE_CONSTRUCTED';}
    else if(!firstSelected){stage='CANDIDATE_NOT_SELECTED';unresolvedReason='CANDIDATE_NEVER_SELECTED';}
    else if(targetHit&&lastSelectionRecovery){stage='SELECTED_THEN_RECOVERED_TARGET';causalEvidence='VALID_SHIP_ASSOCIATION_AFTER_LAST_DECOY_SELECTION';}
    else if(targetHit){stage='SELECTED_TARGET_HIT_RECOVERY_UNPROVEN';unresolvedReason='TARGET_HIT_WITHOUT_SHIP_ASSOCIATION_AFTER_LAST_DECOY_SELECTION';}
    else if(terminalMiss&&lastDecoyOnly){stage='SEDUCED';causalEvidence='LAST_VALID_ASSOCIATION_REMAINED_DECOY_ONLY_AT_TERMINAL_OUTCOME';}
    else if(lastSelectionRecovery){stage='SELECTED_THEN_RECOVERED_TARGET';causalEvidence='VALID_SHIP_ASSOCIATION_AFTER_LAST_DECOY_SELECTION';}
    else if(firstRecovered){stage='SELECTED_OUTCOME_UNRESOLVED';unresolvedReason='EARLY_SHIP_RECOVERY_FOLLOWED_BY_LATER_DECOY_RESELECTION_WITHOUT_FINAL_CAUSAL_PROOF';}
    else if(terminalMiss)unresolvedReason='TERMINAL_MISS_WITHOUT_PERSISTENT_DECOY_ONLY_ASSOCIATION';
    else unresolvedReason='SELECTED_WITHOUT_RECOVERY_OR_TERMINAL_CAUSAL_EVIDENCE';
    return {
      requested:!!deployment?.attempted,deployed:!!deployment?.ok,deploymentTimeS:deployment?.timeS??null,deployedCount:Number(deployment?.count)||0,
      physicallyObserved:rawSeen,candidateConstructed:candidateEvents.length>0,selected:selectedEvents.length>0,
      firstSelectedStep:firstSelected?.step??null,firstSelectedTimeS:firstSelected?.timeS??null,
      lastSelectedStep:lastSelected?.step??null,lastSelectedTimeS:lastSelected?.timeS??null,
      recoveredShipAfterSelection:!!firstRecovered,firstRecoveredShipStep:firstRecovered?.step??null,firstRecoveredShipTimeS:firstRecovered?.timeS??null,
      recoveredShipAfterLastSelection:!!lastSelectionRecovery,firstShipAfterLastSelectionStep:lastSelectionRecovery?.step??null,firstShipAfterLastSelectionTimeS:lastSelectionRecovery?.timeS??null,
      anonymousCandidateKind:firstSelected?.selected?._debugKind??firstSelected?.family??null,
      associationEvidence:{firstSelected:anonymousAssociation(firstSelected),lastSelected:anonymousAssociation(lastSelected),firstRecoveredShip:anonymousAssociation(firstRecovered),firstShipAfterLastSelection:anonymousAssociation(lastSelectionRecovery),lastValidSelection:anonymousAssociation(lastValid),selectionMaintainedAsDecoyOnly:lastDecoyOnly},
      terminalTargetHit:!!targetHit,terminalCategoryAtEvaluation:terminalCategory,causalEvidence,stage,unresolvedReason,
    };
  }
  function defenseSnapshot(em){
    const defense=ACTIVE_SHIP_RUNTIME?.weapons?.executionD?.defenseE;
    const autonomy=typeof wip119AutonomySnapshot==='function'?wip119AutonomySnapshot():null;
    const guns=[];for(const [id,mount] of ACTIVE_SHIP_RUNTIME?.weapons?.gunMounts??[]){const q=mount.snapshot();guns.push({id,shotsFired:Number(q.shotsFired)||0,lastFire:q.lastFire?{...q.lastFire}:null});}
    return {captured:!!defense,autoFireLog:autonomy?.fireLog?.map(q=>({...q}))??null,closeInLog:defense?.closeInLog?.map(q=>({...q}))??null,guns,phalanxHits:Number(em?._phalanxHitCount)||0};
  }
  function defenseEvidence(options,before,after,retirement,em,decoys,emission){
    const afterAuto=after.autoFireLog??[],beforeAuto=before.autoFireLog??[],afterClose=after.closeInLog??[],beforeClose=before.closeInLog??[];
    const autoEvents=afterAuto.slice(beforeAuto.length),closeEvents=afterClose.slice(beforeClose.length),ciwsEvents=closeEvents.filter(q=>/PHALANX|CIWS|20MM/i.test(String(q.weapon??q.mountId??''))),otherClose=closeEvents.filter(q=>!ciwsEvents.includes(q));
    const beforeGun=new Map(before.guns.map(q=>[q.id,q])),gunEvents=after.guns.map(q=>({id:q.id,shots:Math.max(0,q.shotsFired-(beforeGun.get(q.id)?.shotsFired??0)),lastFire:q.lastFire})).filter(q=>q.shots>0);
    const retirementText=upper([retirement?.cause,retirement?.weaponLabel,retirement?.result].filter(Boolean).join(' ')),ciwsKill=/PHALANX|CIWS|20MM/.test(retirementText)&&/KILL|STRUCT_FAIL|INTERCEPT/.test(retirementText),hardKill=/INTERCEPT|SAM|RAM|ESSM|SM-?2|SM-?6|5IN|MFF/.test(retirementText)&&!ciwsKill;
    const hardShots=autoEvents.length+otherClose.reduce((n,q)=>n+Math.max(1,Number(q.rounds)||0),0)+gunEvents.reduce((n,q)=>n+q.shots,0),ciwsShots=ciwsEvents.reduce((n,q)=>n+Math.max(1,Number(q.rounds)||0),0),phalanxHitDelta=Math.max(0,(Number(em?._phalanxHitCount)||0)-before.phalanxHits);
    const hardSources=[autoEvents.length&&'WIP119_AUTO_FIRE_LOG',otherClose.length&&'DEFENSE_E_CLOSE_IN_LOG',gunEvents.length&&'GUN_MOUNT_SHOTS_FIRED',hardKill&&'ASM_RETIREMENT_EVENT'].filter(Boolean),ciwsSources=[ciwsEvents.length&&'DEFENSE_E_CLOSE_IN_LOG',phalanxHitDelta>0&&'PHALANX_PHYSICAL_HIT_COUNTER',ciwsKill&&'ASM_RETIREMENT_EVENT'].filter(Boolean);
    // A terminal retirement record is itself an actual engagement/kill event.
    // In the absence of that event, lack of a complete close-in snapshot is
    // reported as unknown rather than disguised as a negative observation.
    const hardEngaged=!options.hardKill?false:(hardKill?true:(before.captured&&after.captured?hardShots>0:(hardShots>0?true:null))),ciwsEngaged=!options.hardKill?false:(ciwsKill?true:(before.captured&&after.captured?(ciwsShots>0||phalanxHitDelta>0):((ciwsShots>0||phalanxHitDelta>0)?true:null)));
    return {
      hardKill:{enabled:!!options.hardKill,engaged:hardEngaged,shotsOrEvents:hardShots+(hardKill&&hardShots===0?1:0),hit:hardKill?true:(hardEngaged===false?false:null),kill:!!hardKill,evidenceSource:hardSources,unverifiedReason:hardEngaged===null?'DEFENSE_EVENT_SNAPSHOT_UNAVAILABLE':(hardEngaged&&!hardKill?'NONTERMINAL_HIT_EVENT_NOT_EXPOSED':null),events:{autoFire:autoEvents,closeIn:otherClose,guns:gunEvents,retirement:hardKill?retirement:null}},
      ciws:{enabled:!!options.hardKill,engaged:ciwsEngaged,shotsOrEvents:ciwsShots,hit:phalanxHitDelta>0||ciwsKill?true:(ciwsEngaged===false?false:null),kill:!!ciwsKill,evidenceSource:ciwsSources,unverifiedReason:ciwsEngaged===null?'DEFENSE_EVENT_SNAPSHOT_UNAVAILABLE':null,events:{closeIn:ciwsEvents,physicalHits:phalanxHitDelta,retirement:ciwsKill?retirement:null}},
      softKill:{
        chaff:{requested:decoys.CHAFF.requested,deployed:decoys.CHAFF.deployed,observed:decoys.CHAFF.physicallyObserved,selected:decoys.CHAFF.selected},
        nulka:{requested:decoys.NULKA.requested,deployed:decoys.NULKA.deployed,observed:decoys.NULKA.physicallyObserved,selected:decoys.NULKA.selected},
        ecm:{requested:!!options.ecm,effective:emission.maxAllocatorResource>0||emission.maxEcmEmitters>0||emission.maxJammerCouplingW>0,evidenceSource:['SLQ32_ALLOCATOR','EMCON_EQUIPMENT_DECISION','SEEKER_RECEIVER_COUPLING']},
      },
    };
  }
  function newEmissionTelemetry(){return {samples:0,maxAllocatorResource:0,maxRadarEmitters:0,maxEcmEmitters:0,maxJammerCouplingW:0,maxHojDirectJOverN:0,jammerSampleSeen:false,hojActiveSeen:false,finalAllocator:null,finalEmitters:[]};}
  function allocatorEvidenceView(q){return {policy:q.policy,reason:q.reason,primaryKey:q.primaryKey,emitterMode:q.emitterMode,noiseRequested:q.noiseRequested,deceptionRequested:q.deceptionRequested,noiseShare:q.noiseShare,deceptionShare:q.deceptionShare,targetNoiseShare:q.targetNoiseShare,targetDeceptionShare:q.targetDeceptionShare,resourceUsed:q.resourceUsed,schedulerFrameS:q.schedulerFrameS};}
  function observeEmissionTelemetry(em,telemetry){
    return safe(()=>{
      const allocator=slq32EaAuditSnapshot(),snapshot=window.__EMCON_B__.snapshot(ACTIVE_SHIP_RUNTIME.entityId),equipment=snapshot?.equipment??[],p=ASM_SEEKER_PROFILES[em.label]??ASM_SEEKER_PROFILES['Kh-35U'],noise=electronicJammerSampleF(ACTIVE_SHIP_RUNTIME,em,p,'NOISE'),deception=electronicJammerSampleF(ACTIVE_SHIP_RUNTIME,em,p,'DECEPTION'),hoj=electronicHojF(em,em.seeker,p),coupling=(noise?.rawW??0)+(deception?.rawW??0),radarCount=equipment.filter(q=>q.definition.outputKind==='RADAR'&&q.decision.emissionActive).length,ecmCount=equipment.filter(q=>q.definition.outputKind==='ECM'&&q.decision.emissionActive&&allocator.resourceUsed>.001).length;
      telemetry.samples++;telemetry.maxAllocatorResource=Math.max(telemetry.maxAllocatorResource,Number(allocator.resourceUsed)||0);telemetry.maxRadarEmitters=Math.max(telemetry.maxRadarEmitters,radarCount);telemetry.maxEcmEmitters=Math.max(telemetry.maxEcmEmitters,ecmCount);telemetry.maxJammerCouplingW=Math.max(telemetry.maxJammerCouplingW,coupling);telemetry.maxHojDirectJOverN=Math.max(telemetry.maxHojDirectJOverN,Number(hoj?.directJOverN)||0);telemetry.jammerSampleSeen||=!!noise||!!deception;telemetry.hojActiveSeen||=!!hoj?.active;telemetry.finalAllocator=allocatorEvidenceView(allocator);telemetry.finalEmitters=equipment.filter(q=>q.decision.emissionActive).map(q=>({equipmentId:q.definition.id,category:q.definition.category,outputKind:q.definition.outputKind}));
    });
  }
  function emconEvidence(mode,authorityPath,actions,telemetry){
    const snapshot=window.__EMCON_B__.snapshot(ACTIVE_SHIP_RUNTIME.entityId),allocator=slq32EaAuditSnapshot();
    return {mode,authorityPath,actions,ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,legacyRadarMaster:!!emconActive,allRadiationSilent:!!snapshot?.state?.allRadiationSilent,
      ecmRequestPreserved:!!allocator.noiseRequested&&!!allocator.deceptionRequested,equipment:(snapshot?.equipment??[]).map(q=>({equipmentId:q.definition.id,category:q.definition.category,allowed:!!q.decision.allowed,emissionActive:!!q.decision.emissionActive,reason:q.decision.reason??null})),
      effective:{allocatorResourceMax:telemetry.maxAllocatorResource,radarEmitterCountMax:telemetry.maxRadarEmitters,ecmEmitterCountMax:telemetry.maxEcmEmitters,jammerCouplingRawWMax:telemetry.maxJammerCouplingW,hojDirectJOverNMax:telemetry.maxHojDirectJOverN,jammerSampleSeen:telemetry.jammerSampleSeen,hojActiveSeen:telemetry.hojActiveSeen,finalAllocator:allocatorEvidenceView(allocator),finalEmitters:telemetry.finalEmitters},
      truthUsed:false,rngConsumed:false};
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
    const seed=(Number(options.seed)>>>0)||0x5ec10a,label=String(options.label??'Kh-35U'),rangeKm=Number(options.rangeKm??18),speedMps=Number(options.speedMps??300),maxTimeS=Number(options.maxTimeS??90),timeScale=Math.max(1,Math.round(Number(options.timeScale??1))),hardKill=!!options.hardKill,chaff=!!options.chaff,nulka=!!options.nulka,ecm=!!options.ecm,legacyRadarMaster=!!options.legacyRadarMaster||!!options.emcon,allRadiationSilent=!!options.allRadiationSilent;
    _wip75ResetCase(seed);worldTimeScale=0;simAccumulator=0;DIAG_SUPPRESS_PATROLS=true;BATTLESPACE_DIAG_BYPASS=true;
    const fixture=window.__NAVAL_SIM_DIAG__.createTerminalAsmFixture({label,rangeKm,speedMps,bearingDeg:Number(options.bearingDeg??0),altM:Number(options.altM??15)}),em=enemyMissiles.find(q=>q.id===fixture.enemyId);
    if(!em)throw new Error('SEEKER_CLOSE_FIXTURE_MISSING');
    const track=tracks.get(fixture.trackId);if(track){track.identity='HOSTILE';track._operatorIdentity='HOSTILE';track.threatStatus='THREAT';track.classification='ASM';track.confirmed=true;track.sensorDetected=true;track.sensorAge=0;}
    softKillAutoDoctrine=false;noiseJamActive=false;deceptJamActive=false;jammerAutoTrack=false;emconActive=legacyRadarMaster;
    const authorityActions=[];let emconMode=legacyRadarMaster?'RADAR_MASTER_SILENT_ECM_ON':'NORMAL';
    if(allRadiationSilent){
      emconMode='ALL_RADIATION_SILENT';
      const ecmCommand=ownEcmCommandE('FULL');authorityActions.push({action:'ECM_FULL_REQUEST',path:'ownEcmCommandE/UI_AUTHORITY',result:ecmCommand});
      const uiOwner=window.__EMCON_B_UI__.owner(),globalCommand=window.__EMCON_B_UI__.allRadiation();authorityActions.push({action:'ALL_RADIATION_SILENT_ON',path:'__EMCON_B_UI__.allRadiation -> emconGlobalCommandB',uiOwner,result:globalCommand});
    }else if(ecm){
      // Historical bounded scene: the legacy radar master is silent while the
      // ECM technique flags remain independently requested.  It is not the
      // EMCON_B all-radiation-silent authority path.
      noiseJamActive=true;deceptJamActive=true;jammerAutoTrack=true;authorityActions.push({action:'LEGACY_RADAR_MASTER_PLUS_DIRECT_ECM_FLAGS',path:'DIAGNOSTIC_LEGACY_SCENE',result:{ok:true}});
    }
    if(typeof wip119SetMode==='function')wip119SetMode(hardKill?'AUTO':'MANUAL');
    const hitStart=shipHitHistory.length,rngStart=SIM_RNG_STATE>>>0,launchTimeS=simStepCounter*SIM_FIXED_DT;
    const defenseBefore=defenseSnapshot(em),emissionTelemetry=newEmissionTelemetry();
    resetCapture(em.id);window.__ASM_SEEKER_A_DIAG__.beginBattle([em.id]);
    updateSoftKillThreatManager(SIM_FIXED_DT);
    if(nulka){window.__NAVAL_SIM_DIAG__.injectActiveSeekerEsmForTracks('TRACK',.98);updateSoftKillThreatManager(SIM_FIXED_DT);}
    const threat=softKillPrimaryThreat(),deployments={
      CHAFF:{attempted:chaff,ok:false,count:0,reason:chaff?'NO_THREAT_OR_LAUNCH_FAILED':'NOT_REQUESTED',timeS:simStepCounter*SIM_FIXED_DT,seekerOnAtDeployment:!!em.seekerOn},
      NULKA:{attempted:nulka,ok:false,count:0,reason:nulka?'NO_THREAT_OR_LAUNCH_FAILED':'NOT_REQUESTED',timeS:simStepCounter*SIM_FIXED_DT,seekerOnAtDeployment:!!em.seekerOn},
    };
    if(chaff){const fired=deployOwnChaffForThreat(threat,{automatic:false});Object.assign(deployments.CHAFF,{ok:fired>0,count:fired,reason:fired>0?null:'LAUNCH_FAILED'});}
    if(nulka){const fired=nulkaFire15B(threat,{automatic:false,quiet:true});Object.assign(deployments.NULKA,{ok:!!fired?.ok,count:fired?.ok?1:0,reason:fired?.ok?null:(fired?.reason??'LAUNCH_FAILED'),id:fired?.id??null});}
    if(ecm||allRadiationSilent){updateSoftKillThreatManager(SIM_FIXED_DT);updateJammerBearing(SIM_FIXED_DT);updateSlq32EaAllocator(SIM_FIXED_DT);}observeEmissionTelemetry(em,emissionTelemetry);
    let closestApproachM=rangeToOwnM(em),outwardTicks=0,ticks=0,frames=0,egressQualified=false;
    const maxTicks=Math.ceil(maxTimeS/SIM_FIXED_DT);
    while(ticks<maxTicks&&em.alive){
      frames++;
      for(let batch=0;batch<timeScale&&ticks<maxTicks&&em.alive;batch++){
        const before=rangeToOwnM(em);
        if(hardKill){simulateFixedTick(SIM_FIXED_DT);}else{
          if(ecm||allRadiationSilent){updateSoftKillThreatManager(SIM_FIXED_DT);updateJammerBearing(SIM_FIXED_DT);updateSlq32EaAllocator(SIM_FIXED_DT);observeEmissionTelemetry(em,emissionTelemetry);}
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
    const decoyEvidenceRows={CHAFF:decoyEvidence('CHAFF',deployments.CHAFF,C.raw,events,targetHit,category,egressQualified),NULKA:decoyEvidence('NULKA',deployments.NULKA,C.raw,events,targetHit,category,egressQualified)},decoyStages={CHAFF:decoyEvidenceRows.CHAFF.stage,NULKA:decoyEvidenceRows.NULKA.stage};
    if(Object.values(decoyStages).includes('SEDUCED')&&!['DEFENSE_INTERCEPT','CIWS_KILL','TARGET_HIT'].includes(category))category='DECOY_SEDUCTION';
    const validEvents=selectedEvents,transitions=states.filter(q=>q.before!==q.after).map(q=>({step:q.step,timeS:q.timeS,from:q.before,to:q.after,trackValid:q.trackValid,guidanceSource:q.guidanceSource})),dwell=events.filter(q=>q.kind==='DWELL_RESULT');
    const retirement=em._wip11cRetirementQueued?{cause:em._wip11cRetirementQueued.cause??null,weaponLabel:em._wip11cRetirementQueued.weaponLabel??null,result:em._wip11cRetirementQueued.result??null,step:em._wip11cRetirementQueued.step??null}:null;
    observeEmissionTelemetry(em,emissionTelemetry);const defenseAfter=defenseSnapshot(em),defense=defenseEvidence({hardKill,ecm},defenseBefore,defenseAfter,retirement,em,decoyEvidenceRows,emissionTelemetry),emconRow=emconEvidence(emconMode,authorityActions.map(q=>q.path).join(' + ')||'NONE',authorityActions,emissionTelemetry);
    const softEffective=defense.softKill.chaff.deployed||defense.softKill.nulka.deployed||defense.softKill.ecm.effective;
    const result={schema:'AEGIS_SEEKER_CLOSE_A_SHOT_2',ship:ACTIVE_SHIP_RUNTIME.profileId,condition:String(options.condition??'UNNAMED'),weapon:label,profile:em.seeker?.profileId??null,seed,launchTimeS,terminalTimeS:simStepCounter*SIM_FIXED_DT,terminalCategory:category,nativeCause:em._deathReason??em._wip113Outcome??em.retiredReason??retirement?.cause??null,retirement,aliveAtEnd:!!em.alive,egressQualified,terminalQualified:!em.alive||egressQualified,firstValidObservationS:validEvents[0]?.timeS??null,lastValidObservationS:validEvents.at(-1)?.timeS??null,stateTransitions:transitions,transitionCounts:countBy(transitions,'to'),searchAcquireReturns:transitions.filter(q=>q.from==='ACQUIRE'&&q.to==='SEARCH').length,gateRejectReasons:countBy(dwell.filter(q=>!q.accepted),'rejectReason'),validCandidateCounts:{max:Math.max(0,...dwell.map(q=>Number(q.validated)||0)),selectedEvents:validEvents.length},selectedCandidateKinds:selectedKinds,guidanceAvailable:states.some(q=>q.trackValid||q.guidanceSource==='RF_EKF'),decoyDeployments:deployments,decoyEvidence:decoyEvidenceRows,decoyStages,rawDecoyKinds:[...new Set(C.raw.flatMap(row=>row.kinds.map(q=>upper(q.kind))).filter(isDecoyKind))],defenseEvidence:defense,hardKillIntervention:defense.hardKill.engaged,ciwsIntervention:defense.ciws.engaged,softKillIntervention:softEffective,closestApproachM,seaImpact:category==='SEA_IMPACT',targetHit,combatRngStart:rngStart,combatRngEnd:SIM_RNG_STATE>>>0,ticks,frames,timeScale,emcon:legacyRadarMaster||allRadiationSilent,emconMode,emconEvidence:emconRow,ecm,hardKill,chaff,nulka,diagnosticFaults:[...C.faults,...(battle.faults??[])],afterActionTruthOnly:true,tacticalConsumerReads:0};
    return result;
  }

  function runHarpoonSupport(seed=0x5ec300){
    window.__ASM_SEEKER_A_DIAG__.configure({enabled:true});
    const physical=window.__ASM_SEEKER_A_DIAG__.runHarpoonPhysical({seed,targetMode:'OWN_PLUS_TARGET'}),core=window.__HARPOON_DIAG_A__.coreAudit(),seeker=window.__HARPOON_DIAG_A__.seekerAudit(),selection=window.__HARPOON_DIAG_A__.selectionAudit();
    return {schema:'AEGIS_SEEKER_CLOSE_A_HARPOON_SUPPORT_1',ship:ACTIVE_SHIP_RUNTIME.profileId,seed,physical,core,seeker,selection,terminalShot:false,reason:'BOUNDED_SENSOR_PATH_SUPPORT_NOT_TERMINAL_CLASSIFICATION'};
  }
  function contractAudit(){
    const common=window.__SEEKER_U4_C__.contractAudit(),snapshot=window.__SEEKER_U4_C__.snapshot(),source=[runCase,terminalCategory,decoyEvidence,defenseEvidence,emconEvidence].map(String).join('\n');
    return {schema:'AEGIS_SEEKER_CLOSE_A_DIAGNOSTIC_CONTRACT_2',afterActionOnly:true,tacticalConsumerReads:0,classifierTruthFeedback:/selectedLockId\s*=|seekerTgt[XY]\s*=|insTgt[XY]\s*=/.test(source),commonAnonymous:common.anonymousDecisionSource,commonRngCalls:common.rngCalls,commonSaveSchemaChanged:common.saveSchemaChanged,commonRngConsumed:snapshot.rngConsumedByCommonLayer,pass:common.pass&&!snapshot.rngConsumedByCommonLayer&&!snapshot.saveSchemaChanged};
  }
  window.__SEEKER_CLOSE_A_DIAG__=Object.freeze({schema:'AEGIS_SEEKER_CLOSE_A_DIAGNOSTIC_2',runCase,runHarpoonSupport,contractAudit,snapshot:()=>({active:C.active,missileId:C.missileId,rawRows:C.raw.length,faults:[...C.faults]})});
})();
