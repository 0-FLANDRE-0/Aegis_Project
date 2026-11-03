// SEEKER_UNIFY_A test-only probes. Debug identities are copied only to
// after-action rows; no tactical consumer receives them.
(() => {
  const PROFILE={DDG:'DDG_119_LATE_FLIGHT_IIA',CG:'CG_52_LATE_TICONDEROGA',SOV:'SOVREMENNY_956'};
  const hasBasis=()=>typeof SURFACE_SHIP_RCS_BASIS_UNIFY_A!=='undefined';
  function reset(seed){
    _wip75ResetCase(seed);worldTimeScale=0;simAccumulator=0;BATTLESPACE_DIAG_BYPASS=true;DIAG_SUPPRESS_PATROLS=true;
    enemyMissiles.length=0;missiles.length=0;ramMissiles.length=0;targetPool.length=0;tracks.clear();resetSurfaceContacts();ownChaffs.length=0;
    applyDeploymentA(prepareDeploymentA({schema:DEPLOYMENT_POLICY_F.schema,targetShip:'NONE',enemyProfileId:null,allyProfileId:null,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:seed>>>0,allyEmcon:true,enemyEmcon:true}));
    emconActive=false;resetShipboardRadarRfRngWip13B13();
  }
  function setupTarget(kind,seed,x,y,speedKt=0){
    const v=speedKt*.514444;
    if(kind==='HULK'){
      const t=spawnSurfaceTargetWip13A({entityId:'SEEKER_UNIFY_HULK_'+seed,x,y,heading:0,speedKt,mobilityMode:'DEAD_IN_WATER'});t.vx=mpsToWorldSpeed(v);t.vy=0;
      return {obj:t,id:'SFC:'+t.id,profileId:'EMPTY_CONTAINER_TEST_HULK_V1',heightM:t.radarHeightM??12,move:dt=>{t.x+=t.vx*dt;}};
    }
    const p=prepareDeploymentA({schema:DEPLOYMENT_POLICY_F.schema,targetShip:'NONE',enemyProfileId:PROFILE[kind],allyProfileId:null,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:seed>>>0,allyEmcon:true,enemyEmcon:true});
    applyDeploymentA(p);const r=p.enemy,n=r.navigation;n.positionWorld.x=x;n.positionWorld.y=y;n.previousPositionWorld={x,y};n.heading=0;n.previousHeadingWorld=0;n.speed=v;n.targetSpeedKt=speedKt;n.vx=mpsToWorldSpeed(v);n.vy=0;
    return {obj:r,id:'NAVAL:'+r.entityId,profileId:r.profileId,heightM:resolveShipProfile(r.profileId).geometry.referenceHeightM??30,move:dt=>{n.positionWorld.x+=n.vx*dt;}};
  }
  function setupMissile(seed,x,y,z,cueX,cueY,label='Kh-35U'){
    const speed=label==='Kh-32'?1200:280;
    spawnEnemyMissile({id:930000+seed,x,y,z,heading:0,vx:mpsToWorldSpeed(speed),vy:0,vz:0,asmType:label,lastKnownShipX:cueX,lastKnownShipY:cueY});
    const em=enemyMissiles.at(-1);em.insTgtX=cueX;em.insTgtY=cueY;em.seekerOn=true;em.phase=label==='Kh-32'?'DIVE':'SEEKERON';em.separateTimer=99;em.separateDuration=0;em.heading=0;
    em.flight.bodyYaw=em.flight.flightPathYaw=em.flight.cmdFlightPathYaw=0;em.flight.bodyPitch=em.flight.flightPath=em.flight.cmdFlightPath=0;em.z=z;em.vx=mpsToWorldSpeed(speed);em.vy=0;em.vz=0;em.speedMps=speed;
    missileNavB2Init(em,true);const s=asmEnsureSeeker(em);s.mode='SEARCH';s.gimbalAz=0;s.gimbalEl=Math.atan2((ASM_SEEKER_PROFILES[label].aimHeightM??5)-z,Math.max(1,worldToMeters(cueX-x)));return em;
  }
  function addChaff(seed,x,y,z){
    const base=150,id='SEEKER_UNIFY_CHAFF_'+seed;ownChaffs.push({ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,id,kind:'MK214_CHAFF',x,y,z,life:1,maxLife:15,baseRcsM2:base,rcsM2:base,bloom:1,radiusM:18,verticalThicknessM:12,vx:0,vy:0,vz:0,settleMps:1,dopplerSpreadMps:5.5,strength:1,rfBandTag:'I/J',source:'SEEKER_UNIFY_TEST'});return 'CHAFF:OWN:'+id;
  }
  const hasId=(q,id)=>String(q?._debugId??q?._debugSourceId??'').includes(id)||Array.isArray(q?._debugMembers)&&q._debugMembers.some(v=>String(v).includes(id));
  function echoSnapshot(em,targetId){
    const s=asmEnsureSeeker(em),p=ASM_SEEKER_PROFILES[em.label],rng=SIM_RNG_STATE>>>0,raw=asmSeekerVisibleRfReturns(em,s,p),echoes=asmSeekerCompositeReturns(em,s,p,raw),cueRange=Math.hypot(worldToMeters(em.insTgtX-em.x),worldToMeters(em.insTgtY-em.y)),naval=String(targetId).startsWith('NAVAL:');
    const targetRaw=raw.find(q=>hasId(q,targetId))??(naval?raw.filter(q=>q._debugId==null).sort((a,b)=>Math.abs(a._g.rangeM-cueRange)-Math.abs(b._g.rangeM-cueRange))[0]:null)??null;
    const targetEcho=echoes.find(q=>hasId(q,targetId))??(naval?echoes.filter(q=>q._debugMembers?.some(v=>v==null)).sort((a,b)=>Math.abs((a._g??asmSeekerReturnGeometry(em,a)).rangeM-cueRange)-Math.abs((b._g??asmSeekerReturnGeometry(em,b)).rangeM-cueRange))[0]:null)??null;
    const best=targetEcho??echoes.slice().sort((a,b)=>(b.rcs??0)-(a.rcs??0))[0]??null;let meas=null;if(best)for(let i=0;i<12&&!meas;i++)meas=asmSeekerEchoMeasurement(em,s,p,best);SIM_RNG_STATE=rng;
    const ev=meas?.targetEvidenceFeatures??null;return {rawCount:raw.length,echoCount:echoes.length,targetRaw:targetRaw&&{kind:targetRaw._debugKind,id:targetRaw._debugId,rcs:targetRaw.rcs},targetEcho:best&&{kind:best._debugKind,id:best._debugId,members:best._debugMembers,rcs:best.rcs,rangeM:(best._g??asmSeekerReturnGeometry(em,best)).rangeM,rangeExtentM:best.extentRangeM,crossExtentM:best.extentCrossM,verticalExtentM:best.extentVerticalM},measurement:meas&&{snr:meas.snr,pd:meas.pd,score:ev?.score??null,pass:ev?arhRfCandidateAcceptedWip13B12('SEARCH',ev.score):false,features:ev}};
  }
  function runRangeCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||629300,kind=String(opts.kind??'DDG'),rangeKm=Number(opts.rangeKm??45),altM=Number(opts.altM??200),speedKt=Number(opts.speedKt??0),control=String(opts.control??'TARGET');reset(seed);
    const mx=aircraft.x()+kmToWorld(160),my=aircraft.y()+kmToWorld(160),tx=mx+kmToWorld(rangeKm),ty=my;let t=null,targetId='NO_TARGET';
    if(control==='TARGET'){t=setupTarget(kind,seed,tx,ty,speedKt);targetId=t.id;}else if(control==='CHAFF')targetId=addChaff(seed,tx,ty,Math.max(8,altM===15?12:30));
    const em=setupMissile(seed,mx,my,altM,tx,ty,'Kh-35U'),snap=echoSnapshot(em,targetId);let everAcquire=false,everTrack=false,firstAcquireS=null,firstTrackS=null;
    for(let i=0;i<Math.ceil(12/SIM_FIXED_DT);i++){t?.move(SIM_FIXED_DT);updateAsmSeeker(em,SIM_FIXED_DT);simStepCounter++;if(em.seeker.mode==='ACQUIRE'&&!everAcquire){everAcquire=true;firstAcquireS=i*SIM_FIXED_DT;}if(em.seeker.mode==='TRACK'&&!everTrack){everTrack=true;firstTrackS=i*SIM_FIXED_DT;}}
    return {setup:{seed,kind,control,rangeKm,altM,speedKt,targetId},snapshot:snap,result:{everAcquire,everTrack,firstAcquireS,firstTrackS,finalMode:em.seeker.mode,rejectReason:em.seeker.lastRejectReasonWip13C8,lowEvidenceRejectTotal:em.seeker.lowEvidenceRejectTotal??0}};
  }
  function runSamArhCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||829300,path=String(opts.path??'ESSM_BLOCK2_AIR'),targetKind=String(opts.targetKind??'AIRCRAFT'),rangeKm=Number(opts.rangeKm??20),isSM6=path.startsWith('SM6'),surfaceMode=path.endsWith('SURFACE');reset(seed);
    const mx=aircraft.x()+kmToWorld(160),my=aircraft.y()+kmToWorld(160),mz=Number(opts.missileAltM??200),tx=mx+kmToWorld(rangeKm),ty=my,tz=targetKind==='AIRCRAFT'?5000:targetKind==='ASM'?30:12;let targetId='';
    if(targetKind==='AIRCRAFT'){const q={id:880000+seed,alive:true,x:tx,y:ty,z:tz,vx:mpsToWorldSpeed(-250),vy:0,vz:0,lengthM:16,widthM:10,rcsM2:5,heading:Math.PI,speedMps:250};targetPool.push(q);targetId='AIR:'+q.id;}
    else if(targetKind==='ASM'){const q={id:890000+seed,alive:true,label:'Kh-35U',x:tx,y:ty,z:tz,vx:mpsToWorldSpeed(-280),vy:0,vz:0,heading:Math.PI,flight:{bodyYaw:Math.PI,bodyPitch:0}};enemyMissiles.push(q);targetId='ASM:'+q.id;}
    else if(targetKind==='CHAFF')targetId=addChaff(seed,tx,ty,30);
    else if(surfaceMode&&targetKind==='SURFACE'){const q=spawnSurfaceTargetWip13A({entityId:'SEEKER_UNIFY_SM6_SURFACE_'+seed,x:tx,y:ty,heading:0,speedKt:0,mobilityMode:'DEAD_IN_WATER'});targetId='SFC:'+q.id;}
    const m={id:870000+seed,x:mx,y:my,z:mz,vx:mpsToWorldSpeed(900),vy:0,vz:0,heading:0,velPitch:Math.atan2(tz-mz,Math.max(1,rangeKm*1000)),seekerAngle:0,seekerEl:Math.atan2(tz-mz,Math.max(1,rangeKm*1000)),essmActiveSeeker:true,isSM6,_v1ArhState:'SEARCH',_v1Profile:{seekerType:'DUAL_MODE_ARH_SARH'},_v1Mem:{posM:{x:worldToMeters(tx),y:worldToMeters(ty),z:tz},velMps:{x:0,y:0,z:0}},_surfaceArh:surfaceMode};
    const pool=buildEssmArhEchoPool(m),target=pool.find(q=>String(q._debugSourceId??'').includes(targetId))??null,background=pool.filter(q=>q._debugSourceKind==='SEA_CLUTTER'),chosen=target??background.slice().sort((a,b)=>(b.snr??0)-(a.snr??0))[0]??null;
    return {setup:{seed,path,targetKind,rangeKm,targetId},poolCount:pool.length,backgroundCount:background.length,target:chosen&&{id:chosen._debugSourceId,kind:chosen._debugSourceKind,snr:chosen.snr,pd:clamp(1-Math.exp(-chosen.snr*getSamArhProfile(m).searchDwellGain),.001,.999),score:chosen.targetEvidence,pass:arhRfCandidateAcceptedWip13B12('SEARCH',chosen.targetEvidence)}};
  }
  function runCueCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||729300,label=String(opts.label??'Kh-35U'),rangeKm=Number(opts.rangeKm??100),speedKt=Number(opts.speedKt??30),turnDeg=Number(opts.turnDeg??0);reset(seed);
    const ax=aircraft.x(),ay=aircraft.y(),speed=speedKt*.514444,launchX=ax-kmToWorld(rangeKm),launchY=ay,initialCourse=0,turnAtS=Math.max(4,rangeKm*1000/(label==='Kh-32'?1200:280)/3);
    shipNav.heading=initialCourse;shipNav.speed=speed;shipNav.vx=mpsToWorldSpeed(speed);shipNav.vy=0;
    spawnEnemyMissile({id:730000+seed,x:launchX,y:launchY,z:label==='Kh-32'?10000:200,heading:0,vx:mpsToWorldSpeed(label==='Kh-32'?1200:280),vy:0,vz:0,asmType:label,lastKnownShipX:ax,lastKnownShipY:ay});
    const em=enemyMissiles.at(-1);let everAcquire=false,everTrack=false,firstAcquireS=null,firstTrackS=null,closestM=Infinity,passedForS=0,endedBy='TIMEOUT',ticks=0;
    const maxTicks=Math.ceil(Math.min(610,rangeKm*1000/(label==='Kh-32'?650:180)+180)/SIM_FIXED_DT),hitCount0=shipHitHistory.length;
    for(;ticks<maxTicks&&em.alive;ticks++){
      if(ticks*SIM_FIXED_DT>=turnAtS&&turnDeg!==0){const c=deg(turnDeg);shipNav.heading=c;shipNav.vx=mpsToWorldSpeed(Math.cos(c)*speed);shipNav.vy=mpsToWorldSpeed(Math.sin(c)*speed);}
      shipNav.previousPositionWorld={...shipNav.positionWorld};shipNav.positionWorld.x+=shipNav.vx*SIM_FIXED_DT;shipNav.positionWorld.y+=shipNav.vy*SIM_FIXED_DT;
      updateEnemyMissile(em,SIM_FIXED_DT);simStepCounter++;
      const d=Math.hypot(worldToMeters(em.x-aircraft.x()),worldToMeters(em.y-aircraft.y()),(em.z??0)-8);if(d<closestM){closestM=d;passedForS=0;}else if(d>closestM+200)passedForS+=SIM_FIXED_DT;
      const mode=em.seeker?.mode;if(mode==='ACQUIRE'&&!everAcquire){everAcquire=true;firstAcquireS=ticks*SIM_FIXED_DT;}if(mode==='TRACK'&&!everTrack){everTrack=true;firstTrackS=ticks*SIM_FIXED_DT;}
      if(passedForS>8){endedBy='PASSED_TARGET';break;}
    }
    if(shipHitHistory.length>hitCount0)endedBy='GAME_SHIP_HIT';else if(!em.alive)endedBy=em._outcome??em._deathReason??'GAME_TERMINATED';
    return {setup:{seed,label,rangeKm,speedKt,turnDeg,turnAtS},result:{everAcquire,everTrack,firstAcquireS,firstTrackS,finalMode:em.seeker?.mode??null,closestM,endedBy,alive:!!em.alive,flightTimeS:ticks*SIM_FIXED_DT,shipHit:shipHitHistory.length>hitCount0,rejectReason:em.seeker?.lastRejectReasonWip13C8??null}};
  }
  function runRadarCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||929300,kind=String(opts.kind??'DDG'),rangeKm=Number(opts.rangeKm??30),radar=String(opts.radar??'SPY1DV');reset(seed);
    const rxX=aircraft.x()+kmToWorld(160),rxY=aircraft.y()+kmToWorld(160),target=setupTarget(kind,seed,rxX+kmToWorld(rangeKm),rxY,0),profile=resolveShipProfile(target.profileId),targetHeightM=profile?.geometry?.referenceHeightM??target.heightM??target.obj?.radarHeightM??30;
    const spec=radar==='SPY1DV'?{band:'S',heightM:20,maxKm:300,halfAz:2,halfEl:5,refKm:55,refRcs:50,noise:.035,clutter:.015}:radar==='SPQ9B'?{band:'X',heightM:18,maxKm:80,halfAz:2.1,halfEl:8,refKm:32,refRcs:20,noise:.04,clutter:.012}:{band:'X',heightM:15,maxKm:44.4,halfAz:1.2,halfEl:12,refKm:SENSOR_MODEL.bridgeMasterE.snrRefRangeKm,refRcs:SENSOR_MODEL.bridgeMasterE.snrRefRcsM2,noise:.045,clutter:.001};
    const dwell=shipboardRadarEchoFieldWip13B13({radarId:radar,band:spec.band,receiver:{x:rxX,y:rxY,z:spec.heightM,vxMps:0,vyMps:0,vzMps:0},beamAz:0,beamEl:Math.atan2(targetHeightM-spec.heightM,rangeKm*1000),beamHalfAzRad:deg(spec.halfAz),beamHalfElRad:deg(spec.halfEl),maxRangeKm:spec.maxKm,minRangeM:80,rangeResolutionM:40,focusRangeM:rangeKm*1000,seaAzimuthCells:3,seaRangeCells:7,maxDistributedEchoes:0,snrReferenceRangeKm:spec.refKm,snrReferenceRcsM2:spec.refRcs,clutterLeak01:spec.clutter,receiverNoiseNorm:spec.noise,pdHalfSnr:1,rangeSigmaM:25,azSigmaDeg:.1,elSigmaDeg:.2,dopplerSigmaMps:3,includeSea:true});
    const echo=dwell.echoes.find(q=>String(q._debugSourceId??'').includes(target.id))??null,evidence=echo?shipboardRadarDomainEvidenceWip13B13(echo,{elevationObservable:radar!=='BRIDGEMASTER_E',surfaceBiased:radar!=='SPY1DV'}):null;
    return {setup:{seed,kind,rangeKm,radar},horizonKm:radarHorizonKm(spec.heightM,targetHeightM),targetHeightM,candidateCount:dwell.candidateCount,detected:!!echo,trackEligible:!!evidence&&shipboardRadarSurfaceDiscreteEvidenceWip13B14(evidence),echo:echo&&{snr:echo.snr,pd:echo.pd,rcsM2:echo.apparentRcsM2,rangeM:echo.rangeM,evidence}};
  }
  function runManagedRadarCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||929300,kind=String(opts.kind??'DDG'),rangeKm=Number(opts.rangeKm??30),radar=String(opts.radar??'SPY1DV');reset(seed);tracks.clear();resetSpySchedulerState();
    const ax=aircraft.x(),ay=aircraft.y(),target=setupTarget(kind,seed,ax+kmToWorld(rangeKm),ay,0),worldBearing=0,profile=resolveShipProfile(target.profileId),targetHeightM=profile?.geometry?.referenceHeightM??target.heightM??target.obj?.radarHeightM??30;let plots=0,background=0;
    if(radar==='SPY1DV'){
      const face=spyBestFaceForAngle(worldBearing),mount=spySurfaceOriginWip13B9({face}),elevation=Math.atan2(targetHeightM-mount.z,rangeKm*1000),task={...spyTaskBase('SEARCH_HORIZON'),type:'SEARCH_HORIZON',face,azWorld:worldBearing,elRad:elevation,azHalfRad:deg(2.2),elHalfRad:deg(1.5),rangeWorld:kmToWorld(Math.max(50,rangeKm+5)),gateRangeM:Math.max(50000,(rangeKm+5)*1000),snrBoost:1,expectedRevisitS:.2};
      for(let i=0;i<12;i++){const q=spyCollectUnifiedEchoPlotsWip13B13(task);plots+=q.surfacePlots.length;background+=q.backgroundRejected;spyExecuteSurfacePlotsWip13B9(task,{plots:q.surfacePlots,attempted:q.dwell.candidateCount,clutter:{unified:true}});simStepCounter++;}
    }else if(radar==='SPQ9B'){
      const rel=angNorm(worldBearing-shipNav.heading);for(let i=0;i<8;i++){spq9bPrevRotorAngle=angNorm(rel-deg(1.8));spq9bRotorAngle=angNorm(rel+deg(1.8));const q=spq9bCollectUnifiedEchoPlotsWip13B13();plots+=q.surface.length;background+=q.backgroundRejected;spq9bAcceptSurfacePlotsWip13B1(q.surface);simStepCounter++;}
    }else{
      const rel=angNorm(worldBearing-shipNav.heading);for(let i=0;i<8;i++){bridgeMasterEPrevRotorAngle=angNorm(rel-deg(1.8));bridgeMasterERotorAngle=angNorm(rel+deg(1.8));const q=bridgeMasterECollectUnifiedEchoPlotsWip13B13();plots+=q.observations.length;background+=q.backgroundRejected;bridgeMasterEAcceptAnonymousPlotsV35(q.observations);simStepCounter++;}
    }
    const family=radar==='SPY1DV'?'SPY1DV':radar,rows=bridgeMasterESurfaceTrackEntriesV35().filter(([,tr])=>trackIsDisplayable(tr)).map(([id,tr])=>({id,confirmed:!!tr.confirmed,classification:tr.classification,domain:tr.domain,contributors:surfaceSensorContributorSnapshotWip13B9(tr),truthRefExposed:tr.truthRef!=null||tr.associationDomain!=null})),created=rows.some(q=>Object.keys(q.contributors).some(k=>k.startsWith(family)));
    const sensorHeightM=radar==='SPY1DV'?20:(radar==='SPQ9B'?SPQ9B_HEIGHT_M:BRIDGEMASTER_E_HEIGHT_M);
    return {setup:{seed,kind,rangeKm,radar},horizonKm:radarHorizonKm(sensorHeightM,targetHeightM),plots,background,trackCreated:created,confirmedSurface:rows.some(q=>q.confirmed&&q.classification==='SURFACE'),tracks:rows};
  }
  function runNpcRadarCase(opts={}){
    const seed=(Number(opts.seed)>>>0)||939300,observerKind=String(opts.observerKind??'DDG'),rangeKm=Number(opts.rangeKm??30);reset(seed);tracks.clear();
    const ax=aircraft.x(),ay=aircraft.y(),placed=setupTarget(observerKind,seed,ax+kmToWorld(rangeKm),ay,0),r=placed.obj,o=observerC(r);o.emcon=false;o.enabled.SPY=true;o.enabled.SPQ=true;o.enabled.NAV=true;
    const limit=Math.ceil(30/SIM_FIXED_DT);let firstConfirmedS=null;
    for(let i=0;i<limit;i++){stepObserversC(SIM_FIXED_DT);simStepCounter++;if(firstConfirmedS==null&&[...o.tracks.values()].some(q=>q.confirmed&&q.classification==='SURFACE'))firstConfirmedS=i*SIM_FIXED_DT;}
    const rows=[...o.tracks.values()].filter(q=>q.sensorDetected).map(q=>({confirmed:!!q.confirmed,classification:q.classification,domain:q.domain,source:q.sensorSource,contributors:Object.keys(q.contributorsC??{}),truthRefExposed:q.truthRef!=null||q.associationDomain!=null})),targetHeightM=ACTIVE_SHIP_PROFILE.geometry.referenceHeightM??30,observerHeightM=o.normals[0]?.center?.z??20;
    return {setup:{seed,targetProfile:ACTIVE_SHIP_PROFILE.id,observerKind,rangeKm},horizonKm:radarHorizonKm(observerHeightM,targetHeightM),firstConfirmedS,trackCreated:rows.some(q=>q.confirmed&&q.classification==='SURFACE'),rows,stats:{...o.stats}};
  }
  function rcsAudit(){
    const bands=['S','X','IJ'],angles=[['BOW',0],['BEAM',90],['STERN',180],['TOP',90]],own={};
    for(const band of bands)own[band]=Object.fromEntries(angles.map(([name,a],i)=>{const r=10000,az=shipNav.heading+deg(a),z=i===3?10000:20,q=computeShipRCS(aircraft.x()+metersToWorld(r*Math.cos(az)),aircraft.y()+metersToWorld(r*Math.sin(az)),z,band);return [name,{totalRcsM2:q.totalRCS,band:q.band??'LEGACY_SINGLE_VALUE',sectionScale:q.sectionScale??1,reference:q.rcsReference??null}];}));
    const hulk=surfaceTargetProfileWip13A('EMPTY_CONTAINER_TEST_HULK_V1');
    return {schema:'AEGIS_SEEKER_UNIFY_A_RCS_AUDIT_1',basis:hasBasis()?SURFACE_SHIP_RCS_BASIS_UNIFY_A:null,activeProfile:ACTIVE_SHIP_PROFILE.id,sectionBeamLegacyM2:typeof SHIP_RCS_SECTION_BEAM_REFERENCE_UNIFY_A==='undefined'?shipRcsSections.reduce((s,q)=>s+q.rcsBase*q.beam,0):SHIP_RCS_SECTION_BEAM_REFERENCE_UNIFY_A,own,hulk:hulk&&{id:hulk.id,lengthM:hulk.geometry.lengthM,beamM:hulk.geometry.beamM,rcsM2:hulk.signature.rcsM2},genericContacts:{SMALL:{bow:7,beam:38,stern:12},MEDIUM:{bow:28,beam:180,stern:48},LARGE:{bow:110,beam:780,stern:190},source:'SIM_TUNED surfaceRcsM2; no class/displacement metadata'},consumers:{registry:physicalRfReflectorRegistryWip13A2.toString(),shipboard:shipboardRadarEchoFieldWip13B13.toString(),asm:asmSeekerShipRfReturn.toString(),sam:buildEssmArhEchoPool.toString()}};
  }
  function sourceAudit(){return {wip22:{visible:asmSeekerVisibleRfReturns.toString(),composite:asmSeekerCompositeReturns.toString(),measurement:asmSeekerEchoMeasurement.toString(),state:updateAsmSeeker.toString()},harpoon:harpoonSeekerA.toString(),sam:{arh:buildEssmArhEchoPool.toString(),sarh:_v1UpdateSarhMeasurementCore.toString(),core:_v1UpdateArhMeasurementCore.toString()},ram:{rf:ramRfMeasurement.toString(),authority:ramUpdateSeekerAuthority.toString()}};}
  window.__SEEKER_UNIFY_A_DIAG__=Object.freeze({rcsAudit,runRangeCase,runSamArhCase,runCueCase,runRadarCase,runManagedRadarCase,runNpcRadarCase,sourceAudit});
})();
