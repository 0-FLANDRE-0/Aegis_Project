const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12A.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/asm-wreckage-wip11c';

test.use({ viewport:{ width:1600, height:900 } });

test('v48 WIP11C retires the threat but keeps deterministic damage-linked wreckage through water entry', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481130; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.wip11cWreckageDiagnostic, null, { timeout:45_000 });

  const result = await page.evaluate(() => {
    const d=window.__NAVAL_SIM_DIAG__;
    const diagnostic=d.wip11cWreckageDiagnostic(), ownership=d.runtimeOwnershipAuditV48Wip11A();

    d.wip11cResetWreckage();
    const live=d.createTerminalAsmFixture({ seed:481131, label:'Kh-35U', rangeKm:2.4, bearingDeg:0, altM:32, speedMps:280 });
    const liveBefore=d.lifecycleStateV48Wip11A(), kill=d.wip11cDiagnosticKillLiveAsm(live.trackId,{damage:{fuel:78,engine:72,guidance:86,fins:62}}), liveAfter=d.lifecycleStateV48Wip11A();
    const postKill=d.wip11cWreckageSnapshot(), renderPostKill=window.get3DRenderState();

    const startMain=postKill.wreckage.find(w=>w.pieceType==='MAIN');
    const fall=d.wip11cAdvanceWreckage(.5), fallingMain=fall.snapshot.wreckage.find(w=>w.id===startMain?.id);

    d.wip11cResetWreckage();
    const low=d.wip11cCreateWreckageFixture({ id:-11021, altM:14, speedMps:280, flightPathDeg:-8, structDmg:95, damage:{fuel:80,engine:75,guidance:88,fins:65} });
    const water=d.wip11cAdvanceWreckage(6).snapshot;

    d._resetShipTest();
    const collisionFixture=d.wip11cCreateWreckageFixture({ id:-11025, rangeKm:.15, headingDeg:180, altM:5, speedMps:300, flightPathDeg:0, structDmg:95, damage:{fuel:20} });
    const collisionAdvance=d.wip11cAdvanceWreckage(1).snapshot, collisionShip=d.snapshot(), collisionEvents=window.get3DRenderState().visualEvents.map(e=>e.type);

    d.wip11cResetWreckage();
    d.wip11cCreateWreckageFixture({ id:-11031, altM:120, speedMps:300, flightPathDeg:-2, damage:{fuel:40} });
    const valid=d.exportOperationalStateV48Wip11A(), invalid=structuredClone(valid);invalid.profileRevision += '_REJECT';
    const fingerprintBefore=d.operationalImportMutationFingerprintV48Wip11B();let rejected=false;
    try{d.importOperationalStateV48Wip11B(invalid);}catch(_err){rejected=true;}
    const fingerprintAfter=d.operationalImportMutationFingerprintV48Wip11B();
    const reset=d.resetEngagementTransientV48Wip11A(), final=d.wip11cWreckageSnapshot();
    return {diagnostic,ownership,live:{fixture:live,before:liveBefore,kill,after:liveAfter,postKill,renderPostKill:{featureRevision:renderPostKill.featureRevision,wreckage:renderPostKill.asmWreckage}},fall:{startMain,fallingMain},low,water,collision:{fixture:collisionFixture,advance:collisionAdvance,ship:collisionShip,events:collisionEvents},zeroMutation:{rejected,before:fingerprintBefore,after:fingerprintAfter},reset,final,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const waterIds=new Set(result.water.waterSurfaceEvents.map(e=>e.wreckId));
  const checks = {
    pageLoad: consoleErrors.length===0 && pageErrors.length===0,
    coreSelftests: result.selftests.length===0,
    diagnostic: result.diagnostic.pass && Object.values(result.diagnostic.checks).every(Boolean),
    ownership: result.ownership.pass && result.ownership.checks.worldWreckage && result.ownership.checks.truthSeparated,
    liveThreatRetired: result.live.kill.ok && result.live.kill.result==='KILL' && result.live.kill.after.hostileMissiles===result.live.kill.before.hostileMissiles-1 && result.live.kill.after.truthResolved===false,
    physicalWreckCreated: result.live.kill.created.length>=3 && result.live.postKill.wreckage.length===result.live.kill.created.length && result.live.postKill.wreckage.every(w=>w.sourceAsmId===result.live.fixture.enemyId),
    componentDamageVisible: result.live.postKill.wreckage.some(w=>w.pieceType==='MAIN'&&w.burning&&w.systemDamage.fuel===78&&w.systemDamage.engine===72),
    renderReadsPhysics: result.live.renderPostKill.featureRevision==='V48_WIP11C_ASM_WRECKAGE_WATER_SURFACE' && result.live.renderPostKill.wreckage.length===result.live.postKill.wreckage.length,
    ballisticFall: result.fall.startMain && result.fall.fallingMain && result.fall.fallingMain.z<result.fall.startMain.z && result.fall.fallingMain.vzMps<result.fall.startMain.vzMps,
    waterRetirementExact: result.water.wreckage.length===0 && result.water.waterSurfaceEvents.length===result.low.pieces.length && waterIds.size===result.low.pieces.length,
    waterEnergyAndAngle: result.water.waterSurfaceEvents.every(e=>e.kind==='WATER_ENTRY'&&e.surfaceEnergyMJ>0&&e.entryAngleDeg>=0&&e.entryAngleDeg<=90),
    residualShipImpact: result.collision.advance.wreckage.length===0 && result.collision.advance.waterSurfaceEvents.length===0 && result.collision.ship.shipHitCount>=1 && result.collision.ship.shipLastOutcome?.wip11cWreck===true && result.collision.events.includes('SHIP_WRECK_IMPACT'),
    rejectedImportZeroMutation: result.zeroMutation.rejected && JSON.stringify(result.zeroMutation.before)===JSON.stringify(result.zeroMutation.after),
    resetClearsTransient: result.reset.entityCounts.asmWreckage===0 && result.reset.entityCounts.waterSurfaceEvents===0 && result.final.wreckage.length===0 && result.final.waterSurfaceEvents.length===0,
  };
  fs.mkdirSync(artifactDir,{recursive:true});
  fs.writeFileSync(`${artifactDir}/asm-wreckage-results.json`,`${JSON.stringify({schema:'AEGIS_ASM_WRECKAGE_BROWSER_V48_WIP11C',simulator,simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),checks,consoleErrors,pageErrors,result},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C BDA withholds AUTO fire during coast and reopens only on a coherent return', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors=[],pageErrors=[];
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  await page.addInitScript(()=>{window.__NAVAL_SIM_SEED__=481131;});
  await page.goto(`http://127.0.0.1:4173/${simulator}`,{waitUntil:'load'});
  await page.waitForFunction(()=>Array.isArray(window.__CORE_SELFTEST_FAILURES__)&&window.__NAVAL_SIM_DIAG__?.wip121RecordFriendlyInterceptEvent,null,{timeout:45_000});

  const result=await page.evaluate(()=>{
    const d=window.__NAVAL_SIM_DIAG__;d.resetEngagementTransientV48Wip11A();
    const fixture=d.createTerminalAsmFixture({seed:481131,label:'Kh-35U',rangeKm:12,bearingDeg:0,altM:18,speedMps:300});
    d.wip118ResetControl();d.wip119ResetAutonomy();d.wip118DiagSetObservedTrack(fixture.trackId,{rangeKm:12,bearingDeg:0,headingDeg:180,altM:18,speedMps:300});
    const initialAssessment=d.wip118KillAssessmentNow().find(a=>a.trackId===fixture.trackId),mode=d.wip119SetMode('AUTO');
    const supportBefore=d.wip121PrimeDiagnosticTargetSupport(fixture.trackId,0),kill=d.wip11cDiagnosticKillLiveAsm(fixture.trackId,{damage:{fuel:70,engine:65,guidance:80,fins:55}}),immediateControl=d.wip118ControlSnapshot(),immediateTrack=d.a3TrackStates().find(t=>t.id===fixture.trackId),supportAfter=d.wip121TargetSupportSnapshot(fixture.trackId);
    const ordnanceBeforeAuto=d.lifecycleStateV48Wip11A().entityCounts.ordnance,autoDuringBda=d.wip119AutonomyTick(),ordnanceAfterAuto=d.lifecycleStateV48Wip11A().entityCounts.ordnance;
    d.wip118DiagAdvanceClock(.20);const shortAssessment=d.wip118KillAssessmentNow().find(a=>a.trackId===fixture.trackId);
    d.wip118DiagAdvanceClock(.20);const confirmedAssessment=d.wip118KillAssessmentNow().find(a=>a.trackId===fixture.trackId),confirmedTrack=d.a3TrackStates().find(t=>t.id===fixture.trackId);
    d.wip118DiagAdvanceClock(1.30);d.wip118KillAssessmentNow();const retiredPresentation=d.wip121BdaTrackPresentation(fixture.trackId),retiredSupport=d.wip121TargetSupportSnapshot(fixture.trackId);
    d.wip118DiagAdvanceClock(.10);d.wip118DiagSetObservedTrack(fixture.trackId,{rangeKm:11.9,bearingDeg:0,headingDeg:180,altM:18,speedMps:300});const returnAssessment=d.wip118KillAssessmentNow().find(a=>a.trackId===fixture.trackId),returnTrack=d.a3TrackStates().find(t=>t.id===fixture.trackId),returnPresentation=d.wip121BdaTrackPresentation(fixture.trackId);
    return {fixture,initialAssessment,mode,supportBefore,kill,immediateControl,immediateTrack,supportAfter,ordnanceBeforeAuto,ordnanceAfterAuto,autoDuringBda,shortAssessment,confirmedAssessment,confirmedTrack,retiredPresentation,retiredSupport,returnAssessment,returnTrack,returnPresentation,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const immediate=result.immediateControl.assessments.find(a=>a.trackId===result.fixture.trackId),checks={
    pageLoad:consoleErrors.length===0&&pageErrors.length===0,
    coreSelftests:result.selftests.length===0,
    initialThreat:result.initialAssessment?.state==='THREAT'&&result.mode==='AUTO',
    breakupReport:result.kill.ok&&immediate?.killPlausibility?.reason==='FRIENDLY_DIRECT_BREAKUP'&&immediate?.bdaEvent?.evidence==='DIRECT_BREAKUP',
    immediateCeaseFire:immediate?.state==='KILL_ASSESSMENT'&&result.immediateTrack?.threatStatus==='KILL_ASSESSMENT'&&result.immediateTrack?.engagementAuthority==='WITHHELD',
    directBreakupReleasesSpg:!!result.supportBefore?.liveIlluminator&&!result.supportAfter?.liveIlluminator&&!result.supportAfter?.reservation&&result.supportAfter?.blocked===true&&result.supportAfter?.missiles?.every(m=>!m.dlAlive&&!m.sarhAlive&&!m.illuminatorGuided&&m.illuminatorId==null),
    autoLaunchSuppressed:result.ordnanceAfterAuto===result.ordnanceBeforeAuto&&result.autoDuringBda.fireLog.length===0,
    shortWindowHeld:result.shortAssessment?.state==='KILL_ASSESSMENT',
    noReturnConfirmed:result.confirmedAssessment?.state==='DESTROYED'&&result.confirmedTrack?.threatStatus==='DESTROYED'&&result.confirmedTrack?.engagementAuthority==='WITHHELD',
    ghostMemRetired:result.retiredPresentation?.kind==='KILL'&&result.retiredPresentation?.hidden===true&&result.retiredPresentation?.confirmedAgeS>=1.25&&result.retiredSupport?.blocked===true,
    coherentReturnReopens:result.returnAssessment?.state==='THREAT'&&result.returnAssessment?.bdaResolvedByReturnStep!=null&&result.returnTrack?.threatStatus==='THREAT'&&result.returnTrack?.engagementAuthority==='AUTO_AUTHORIZED'&&result.returnPresentation?.kind==='LIVE'&&result.returnPresentation?.hidden===false
  };
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/bda-results.json`,`${JSON.stringify({schema:'AEGIS_WIP11C_BDA_BROWSER',simulator,checks,consoleErrors,pageErrors,result},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C correlates a pre-effect duplicate MEM file to breakup BDA without blocking a later coherent return', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors=[],pageErrors=[];
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  await page.addInitScript(()=>{window.__NAVAL_SIM_SEED__=481132;});
  await page.goto(`http://127.0.0.1:4173/${simulator}`,{waitUntil:'load'});
  await page.waitForFunction(()=>window.__NAVAL_SIM_DIAG__?.wip121CloneCoastTrackForTest,null,{timeout:45_000});

  const result=await page.evaluate(()=>{
    const d=window.__NAVAL_SIM_DIAG__;d.resetEngagementTransientV48Wip11A();
    const fixture=d.createTerminalAsmFixture({seed:481132,label:'Kh-35U',rangeKm:12,bearingDeg:0,altM:18,speedMps:300});
    d.wip118ResetControl();d.wip118KillAssessmentNow();
    const alias=d.wip121CloneCoastTrackForTest(fixture.trackId,{dxM:52,dyM:-31,dvxMps:7,dvyMps:-4}),kill=d.wip11cDiagnosticKillLiveAsm(fixture.trackId,{damage:{fuel:70,engine:65,guidance:80,fins:55}}),immediate=d.wip118ControlSnapshot();
    d.wip118DiagAdvanceClock(.40);d.wip118KillAssessmentNow();const confirmed=d.wip118ControlSnapshot(),aliasPresentation=d.wip121BdaTrackPresentation(alias.trackId);
    d.wip118DiagAdvanceClock(1.30);d.wip118KillAssessmentNow();const hidden=d.wip121BdaTrackPresentation(alias.trackId);
    d.wip118DiagAdvanceClock(.10);d.wip118DiagSetObservedTrack(alias.trackId,{rangeKm:11.5,bearingDeg:.1,headingDeg:180,altM:18,speedMps:300});d.wip118KillAssessmentNow();const reopened=d.wip118ControlSnapshot(),reopenedPresentation=d.wip121BdaTrackPresentation(alias.trackId);
    return {fixture,alias,kill,immediate,confirmed,aliasPresentation,hidden,reopened,reopenedPresentation,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });
  const immediateOrigin=result.immediate.assessments.find(a=>a.trackId===result.fixture.trackId),immediateAlias=result.immediate.assessments.find(a=>a.trackId===result.alias.trackId),confirmedAlias=result.confirmed.assessments.find(a=>a.trackId===result.alias.trackId),reopenedAlias=result.reopened.assessments.find(a=>a.trackId===result.alias.trackId),originEvent=result.immediate.recentInterceptEvents.find(e=>e.trackId===result.fixture.trackId),aliasEvent=result.immediate.recentInterceptEvents.find(e=>e.trackId===result.alias.trackId),checks={
    pageLoad:consoleErrors.length===0&&pageErrors.length===0,
    coreSelftests:result.selftests.length===0,
    breakupRecorded:result.kill.ok&&immediateOrigin?.state==='KILL_ASSESSMENT'&&originEvent?.terminalReport?.schema==='AEGIS_TERMINAL_EFFECT_REPORT_V48_WIP11C',
    duplicateMemCorrelated:immediateAlias?.state==='KILL_ASSESSMENT'&&aliasEvent?.source==='TERMINAL_EFFECT_TRACK_CORRELATION'&&aliasEvent?.correlatedFromTrackId===result.fixture.trackId&&originEvent?.correlatedTrackIds?.includes(result.alias.trackId),
    duplicateConfirmed:confirmedAlias?.state==='DESTROYED'&&result.aliasPresentation?.kind==='KILL',
    duplicateHidden:result.hidden?.hidden===true,
    coherentReturnReopens:reopenedAlias?.state==='THREAT'&&reopenedAlias?.bdaResolvedByReturnStep!=null&&result.reopenedPresentation?.kind==='LIVE'&&result.reopenedPresentation?.hidden===false
  };
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/bda-alias-correlation-results.json`,`${JSON.stringify({schema:'AEGIS_WIP11C_BDA_ALIAS_CORRELATION_BROWSER',simulator,checks,consoleErrors,pageErrors,result},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C moves weapon and SPG ownership when a replacement track appears on the first LOST frame', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors=[],pageErrors=[];
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`,{waitUntil:'load'});
  await page.waitForFunction(()=>window.__NAVAL_SIM_DIAG__?.wip121CloneCoastTrackForTest,null,{timeout:45_000});
  const result=await page.evaluate(()=>{
    const d=window.__NAVAL_SIM_DIAG__;d.resetEngagementTransientV48Wip11A();const fixture=d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:14,bearingDeg:0,altM:18,speedMps:300});
    d.wip118ResetControl();d.wip118KillAssessmentNow();const supportBefore=d.wip121PrimeDiagnosticTargetSupport(fixture.trackId,0),replacement=d.wip121CloneCoastTrackForTest(fixture.trackId,{dxM:35,dyM:20,dvxMps:4,dvyMps:2});
    d.wip118DiagDropTrack(fixture.trackId);d.wip118KillAssessmentNow();const control=d.wip118ControlSnapshot(),oldSupport=d.wip121TargetSupportSnapshot(fixture.trackId),newSupport=d.wip121TargetSupportSnapshot(replacement.trackId);
    return {fixture,replacement,supportBefore,control,oldSupport,newSupport,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });
  const alias=result.control.aliasLog.find(q=>q.oldId===result.fixture.trackId&&q.newId===result.replacement.trackId),oldAssessment=result.control.assessments.find(q=>q.trackId===result.fixture.trackId),newAssessment=result.control.assessments.find(q=>q.trackId===result.replacement.trackId),checks={
    pageLoad:consoleErrors.length===0&&pageErrors.length===0,
    coreSelftests:result.selftests.length===0,
    firstLostFrameAliased:alias?.phase==='POST_LOSS_SAME_FRAME'&&!oldAssessment&&newAssessment?.state==='THREAT'&&newAssessment?.reacquiredFromTrackId===result.fixture.trackId,
    spgOwnershipMoved:!!result.supportBefore?.liveIlluminator&&!result.oldSupport?.liveIlluminator&&!result.oldSupport?.reservation&&!!result.newSupport?.liveIlluminator&&!!result.newSupport?.reservation,
    interceptorAssignmentMoved:result.oldSupport?.missiles?.length===0&&result.newSupport?.missiles?.length===1&&result.newSupport.missiles[0].dlAlive===true
  };
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/bda-first-lost-alias-results.json`,`${JSON.stringify({schema:'AEGIS_WIP11C_FIRST_LOST_ALIAS_BROWSER',simulator,checks,consoleErrors,pageErrors,result},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C carries an anonymous SPY track id through a real ESSM kill and retires its MEM/SPG presentation', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors=[],pageErrors=[];
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  await page.addInitScript(()=>{window.__NAVAL_SIM_SEED__=991212;});
  await page.goto(`http://127.0.0.1:4173/${simulator}`,{waitUntil:'load'});
  await page.waitForFunction(()=>Array.isArray(window.__CORE_SELFTEST_FAILURES__)&&window.__NAVAL_SIM_DIAG__?.createUndetectedAsmFixture,null,{timeout:45_000});

  const result=await page.evaluate(()=>{
    const d=window.__NAVAL_SIM_DIAG__;
    d.createUndetectedAsmFixture({rangeKm:18,bearingDeg:0,altM:35,speedMps:240,label:'Kh-35U'});d.setEmcon(false);d.wip118ResetControl();
    let track=null,detectTicks=0;
    for(;detectTicks<1200;detectTicks++){
      d.stepTicks(1);track=d.sensorAudit().tracks.find(q=>q.associationDomain==null&&q.confirmed&&q.fcReady);if(track)break;
    }
    if(!track)return {error:'ANONYMOUS_TRACK_NOT_ACQUIRED',detectTicks,sensor:d.sensorAudit()};
    d.designateTrack(track.id);const fired=[d.fireESSM(),d.fireESSM()];let deathTick=null,atDeath=null;
    for(let i=0;i<3600;i++){
      d.stepTicks(1);if(i%12===0)d.wip118ControlNow();const truth=d.trackingTruthAudit().asm[0];
      if(!truth?.alive&&deathTick==null){deathTick=i;atDeath={assessment:d.wip118ControlSnapshot().assessments.find(q=>q.trackId===track.id),support:d.wip121TargetSupportSnapshot(track.id),sensor:d.sensorAudit().tracks.find(q=>q.id===track.id)};}
      if(deathTick!=null&&i>deathTick+180)break;
    }
    d.wip118ControlNow();const control=d.wip118ControlSnapshot(),sensor=d.sensorAudit();
    return {track,detectTicks,fired,deathTick,atDeath,final:{assessment:control.assessments.find(q=>q.trackId===track.id),events:control.recentInterceptEvents.filter(q=>q.trackId===track.id),support:d.wip121TargetSupportSnapshot(track.id),presentation:d.wip121BdaTrackPresentation(track.id),sensorTrack:sensor.tracks.find(q=>q.id===track.id),displayable:sensor.displayable,history:d.wip75PipAudit().history},selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const direct=result.final?.events?.find(e=>e.evidence==='DIRECT_BREAKUP'),checks={
    pageLoad:consoleErrors.length===0&&pageErrors.length===0,
    coreSelftests:result.selftests?.length===0,
    anonymousOperationalTrack:!result.error&&result.track?.associationDomain==null&&result.track?.confirmed===true&&result.detectTicks<1200,
    realEssmKill:result.fired?.every(Number.isFinite)&&result.deathTick!=null&&result.final?.history?.some(e=>e.targetId===result.track.id&&e.deathReason==='PROX_DETONATION_KILL'),
    directBreakupUsesAssignedTrack:direct?.trackId===result.track.id&&['INTERCEPTOR_TERMINAL_REPORT','WIP11C_ASM_RETIREMENT'].includes(direct?.source)&&direct?.relatedKeys?.some(k=>String(k).startsWith('INTERCEPT_BURST:ESSM:')),
    immediateSpgRelease:result.atDeath?.assessment?.state==='KILL_ASSESSMENT'&&result.atDeath?.assessment?.bdaEvent?.evidence==='DIRECT_BREAKUP'&&result.atDeath?.support?.blocked===true&&!result.atDeath?.support?.liveIlluminator&&!result.atDeath?.support?.reservation&&result.atDeath?.support?.missiles?.every(m=>!m.dlAlive&&!m.sarhAlive&&!m.illuminatorGuided&&m.illuminatorId==null),
    fuzeEchoDoesNotDowngradeEvidence:result.final?.assessment?.bdaEvent?.evidence==='DIRECT_BREAKUP'&&result.final?.events?.filter(e=>e.trackId===result.track.id).length===1,
    ghostMemHidden:result.final?.assessment?.state==='DESTROYED'&&result.final?.presentation?.kind==='KILL'&&result.final?.presentation?.hidden===true&&result.final?.sensorTrack?.threatStatus==='DESTROYED'&&result.final?.displayable?.asm===0,
    noLingeringSpg:result.final?.support?.blocked===true&&!result.final?.support?.liveIlluminator&&!result.final?.support?.reservation
  };
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/anonymous-track-bda-results.json`,`${JSON.stringify({schema:'AEGIS_WIP11C_ANONYMOUS_TRACK_BDA_BROWSER',simulator,checks,consoleErrors,pageErrors,result},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C promotes a preceding fuze echo to the real anonymous Kh-32 ESSM breakup epoch', async ({ page }) => {
  test.setTimeout(240_000);
  const consoleErrors=[],pageErrors=[];
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  await page.addInitScript(()=>{window.__NAVAL_SIM_SEED__=112000;});
  await page.goto(`http://127.0.0.1:4173/${simulator}`,{waitUntil:'load'});
  await page.waitForFunction(()=>Array.isArray(window.__CORE_SELFTEST_FAILURES__)&&window.__NAVAL_SIM_DIAG__?.createUndetectedAsmFixture,null,{timeout:45_000});

  const result=await page.evaluate(()=>{
    const d=window.__NAVAL_SIM_DIAG__;d.resetTestClock();d._resetShipTest();d.resetEngagementTransientV48Wip11A();d.setSeed(112000);
    const fixtureId=d.createUndetectedAsmFixture({label:'Kh-32',rangeKm:20,bearingDeg:0,altM:1000,speedMps:900}),fixture=d.trackingTruthAudit().asm.find(q=>q.id===fixtureId)??{id:fixtureId,label:'Kh-32'};d.setEmcon(false);d.wip118ResetControl();d.wip119ResetAutonomy();
    let track=null,detectTicks=0;
    for(;detectTicks<1200;detectTicks++){d.stepTicks(1);track=d.sensorAudit().tracks.find(q=>q.associationDomain==null&&q.confirmed&&q.fcReady&&(q.isASM||q.classification==='ASM'));if(track)break;}
    if(!track)return {error:'ANONYMOUS_KH32_NOT_ACQUIRED',fixture,detectTicks,sensor:d.sensorAudit(),selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
    d.designateTrack(track.id);const fired=[d.fireESSM(),d.fireESSM(),d.fireESSM(),d.fireESSM()].filter(Number.isFinite);let syntheticFuze=null,preBreakupTrack=null,kill=null,killTick=null;
    for(let i=0;i<1800;i++){
      d.stepTicks(1);
      // Reproduce the real race: cleanup telemetry from a preceding ESSM burst is pending while
      // the next real ESSM physically destroys the target six fixed ticks later.
      if(i===785){preBreakupTrack=d.sensorAudit().tracks.find(q=>q.id===track.id)??null;syntheticFuze=d.wip121RecordFriendlyInterceptEvent(track.id,{key:'KH32_STALE_FUZE_ECHO',weapon:'ESSM',evidence:'FUZE_DETONATION',burstMissM:45,deathReason:'PROX_DETONATION_MISS',source:'INTERCEPTOR_TELEMETRY'});}
      if(i%12===0)d.wip118ControlNow();const history=d.wip75PipAudit().history.filter(q=>fired.includes(q.id));kill=history.find(q=>q.deathReason==='PROX_DETONATION_KILL')??null;
      if(kill){killTick=i;break;}if(history.length===fired.length)break;
    }
    if(!kill)return {error:'REAL_ESSM_KILL_NOT_OBSERVED',fixture,track,detectTicks,fired,syntheticFuze,preBreakupTrack,history:d.wip75PipAudit().history,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
    d.wip119SetMode('AUTO');const autoAtKill=d.wip119AutonomyTick(),atKillSensor=d.sensorAudit(),atKillControl=d.wip118ControlSnapshot(),atKill={sim:d.snapshot(),sensorTrack:atKillSensor.tracks.find(q=>q.id===track.id)??null,displayable:atKillSensor.displayable,assessment:atKillControl.assessments.find(q=>q.trackId===track.id)??null,events:atKillControl.recentInterceptEvents.filter(q=>q.trackId===track.id),support:d.wip121TargetSupportSnapshot(track.id),presentation:d.wip121BdaTrackPresentation(track.id),history:d.wip75PipAudit().history.filter(q=>fired.includes(q.id)),wreckage:d.wip11cWreckageSnapshot()};
    const postKillAutoFire=[];
    for(let i=0;i<360;i++){d.stepTicks(1);if(i%12===0){const auto=d.wip119AutonomyTick();for(const row of auto.fireLog)if(!postKillAutoFire.some(q=>q.t===row.t&&q.trackId===row.trackId&&q.weapon===row.weapon&&q.round===row.round))postKillAutoFire.push(row);}}
    d.wip118ControlNow();const control=d.wip118ControlSnapshot(),sensor=d.sensorAudit(),wreckage=d.wip11cWreckageSnapshot(),liveGhosts=sensor.tracks.filter(q=>q.classification==='ASM'&&d.wip121BdaTrackPresentation(q.id)?.hidden!==true);
    return {fixture,track,detectTicks,fired,syntheticFuze,preBreakupTrack,kill,killTick,autoAtKill,atKill,postKillAutoFire,final:{sensorTrack:sensor.tracks.find(q=>q.id===track.id)??null,displayable:sensor.displayable,assessment:control.assessments.find(q=>q.trackId===track.id)??null,events:control.recentInterceptEvents.filter(q=>q.trackId===track.id),aliasLog:control.aliasLog,support:d.wip121TargetSupportSnapshot(track.id),presentation:d.wip121BdaTrackPresentation(track.id),history:d.wip75PipAudit().history.filter(q=>fired.includes(q.id)),wreckage,liveGhosts},selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const promoted=result.atKill?.assessment?.bdaEvent,checks={
    pageLoad:consoleErrors.length===0&&pageErrors.length===0,
    coreSelftests:result.selftests?.length===0,
    anonymousKh32Track:!result.error&&result.fixture?.label==='Kh-32'&&result.track?.associationDomain==null&&result.track?.trackUid&&result.track?.classification==='ASM'&&result.detectTicks<1200,
    realEssmPhysicalKill:result.fired?.length===4&&result.kill?.isESSM===true&&result.kill?.targetId===result.track?.id&&result.kill?.deathReason==='PROX_DETONATION_KILL'&&result.atKill?.wreckage?.wreckage?.some(w=>w.sourceLabel==='Kh-32'),
    staleFuzeRebasedToBreakup:result.syntheticFuze?.evidence==='FUZE_DETONATION'&&promoted?.key==='KH32_STALE_FUZE_ECHO'&&promoted?.evidence==='DIRECT_BREAKUP'&&promoted?.effectStep>result.syntheticFuze.effectStep&&promoted?.effectStep===promoted?.terminalReport?.step&&promoted?.deathReason===result.kill?.deathReason&&Math.abs(promoted?.burstMissM-result.kill?.burstMissM)<1e-9&&promoted?.resolvedByReturnStep==null,
    sameTickPlotNotFalseReturn:result.atKill?.sensorTrack?.lastMeasurementStep<=promoted?.effectStep&&result.atKill?.assessment?.state==='KILL_ASSESSMENT'&&result.atKill?.assessment?.bdaResolvedByReturnStep==null,
    sameTickAutoCease:result.autoAtKill?.fireLog?.length===0&&result.postKillAutoFire?.length===0,
    immediateSpgDlSarhRelease:result.atKill?.support?.blocked===true&&!result.atKill?.support?.liveIlluminator&&!result.atKill?.support?.reservation&&result.atKill?.support?.missiles?.every(m=>!m.dlAlive&&!m.sarhAlive&&!m.illuminatorGuided&&m.illuminatorId==null),
    briefBdaThenHiddenKill:result.atKill?.presentation?.kind==='BDA'&&result.atKill?.presentation?.hidden===false&&result.final?.assessment?.state==='DESTROYED'&&result.final?.presentation?.kind==='KILL'&&result.final?.presentation?.hidden===true,
    noLiveAsmGhost:result.final?.sensorTrack?.threatStatus==='DESTROYED'&&result.final?.displayable?.asm===0&&result.final?.liveGhosts?.length===0,
    wreckageIndependent:result.final?.wreckage?.wreckage?.length+result.final?.wreckage?.waterSurfaceEvents?.length>0&&result.final?.wreckage?.waterSurfaceEvents?.every(e=>e.sourceType==='ASM_WRECK')
  };
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/kh32-essm-ghost-retirement-results.json`,`${JSON.stringify({schema:'AEGIS_WIP11C_KH32_ESSM_GHOST_RETIREMENT_BROWSER',simulator,checks,consoleErrors,pageErrors,result},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C preserves the commanded SM-2 launch azimuth through the physical Mk41 in-cell phase', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors=[],pageErrors=[];
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  await page.addInitScript(()=>{window.__NAVAL_SIM_SEED__=932008;});
  await page.goto(`http://127.0.0.1:4173/${simulator}`,{waitUntil:'load'});
  await page.waitForFunction(()=>window.__NAVAL_SIM_DIAG__?.sm2LaunchAudit&&Array.isArray(window.__CORE_SELFTEST_FAILURES__),null,{timeout:45_000});
  const result=await page.evaluate(()=>{
    const d=window.__NAVAL_SIM_DIAG__,deltaDeg=(a,b)=>Math.abs((((Number(a)-Number(b))+540)%360)-180),rows=[];
    for(const bearingDeg of [-135,-45,45,135]){
      const fixture=d.createTerminalAsmFixture({label:'Kh-32',rangeKm:90,bearingDeg,altM:24000,speedMps:1200}),missileId=d.fireSM2();
      const initial=d.sm2LaunchAudit().find(q=>q.id===missileId)??null;d.stepTicks(1);
      const inCell=d.sm2LaunchAudit().find(q=>q.id===missileId)??null;d.stepTicks(119);
      const settled=d.sm2LaunchAudit().find(q=>q.id===missileId)??null;
      rows.push({bearingDeg,fixture,missileId,initial,inCell,settled,errorDeg:{initialBodyToCommand:initial?deltaDeg(initial.bodyHeadingDeg,bearingDeg):null,inCellBodyToCommand:inCell?deltaDeg(inCell.bodyHeadingDeg,bearingDeg):null,inCellBodyToStoredAzimuth:inCell?deltaDeg(inCell.bodyHeadingDeg,inCell.launchAzimuthDeg):null,settledBodyToDesired:settled?deltaDeg(settled.bodyHeadingDeg,settled.desiredBearingDeg):null}});
    }
    return {rows,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });
  const checks={
    pageLoad:consoleErrors.length===0&&pageErrors.length===0,
    coreSelftests:result.selftests.length===0,
    allFourBearingsLaunched:result.rows.length===4&&result.rows.every(r=>Number.isFinite(r.missileId)&&r.initial&&r.inCell&&r.settled),
    commandStoredExactly:result.rows.every(r=>r.initial?.launchAzimuthDeg!=null&&r.errorDeg.initialBodyToCommand<.1&&r.errorDeg.inCellBodyToStoredAzimuth<1e-8),
    noDeckNormalReversal:result.rows.every(r=>r.errorDeg.inCellBodyToCommand<.1),
    earlyGuidanceFacesTarget:result.rows.every(r=>r.errorDeg.settledBodyToDesired<3)
  };
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/sm2-launch-azimuth-results.json`,`${JSON.stringify({schema:'AEGIS_SM2_VLS_LAUNCH_AZIMUTH_V48_WIP11C',simulator,checks,consoleErrors,pageErrors,result},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C retires a missed Kh-32 sea-impact coast instead of carrying an ASM MEM threat through the ship', async ({ page }) => {
  test.setTimeout(300_000);
  const consoleErrors=[],pageErrors=[];
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  await page.addInitScript(()=>{window.__NAVAL_SIM_SEED__=932008;});
  await page.goto(`http://127.0.0.1:4173/${simulator}`,{waitUntil:'load'});
  await page.waitForFunction(()=>window.__NAVAL_SIM_DIAG__?.createUndetectedAsmFixture&&window.__NAVAL_SIM_DIAG__?.wip119AutonomyTick,null,{timeout:45_000});
  const result=await page.evaluate(()=>{
    const d=window.__NAVAL_SIM_DIAG__;d.setSeed(932008);d.createUndetectedAsmFixture({rangeKm:90,bearingDeg:-45,altM:24000,speedMps:1200,label:'Kh-32'});d.setEmcon(false);d.wip118ResetControl();d.wip119ResetAutonomy();
    let track=null,detectTicks=0;
    for(;detectTicks<1800;detectTicks++){d.stepTicks(1);track=d.sensorAudit().tracks.find(q=>q.associationDomain==null&&q.confirmed&&q.fcReady&&(q.isASM||q.classification==='ASM'));if(track)break;}
    if(!track)return {error:'ANONYMOUS_KH32_NOT_ACQUIRED',detectTicks,sensor:d.sensorAudit(),selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
    d.wip119SetMode('AUTO');const fireLog=[];let firstSm2Launch=null,truthRemovedTick=null,atTruthRemoval=null,seaImpactTick=null,atSeaImpact=null;
    for(let i=0;i<6000;i++){
      d.stepTicks(1);
      if(i%12===0){const auto=d.wip119AutonomyTick();for(const row of auto.fireLog){if(!fireLog.some(q=>q.t===row.t&&q.trackId===row.trackId&&q.weapon===row.weapon&&q.round===row.round))fireLog.push(row);if(!firstSm2Launch&&row.weapon==='SM2')firstSm2Launch=d.sm2LaunchAudit().at(-1)??null;}}
      const truth=d.trackingTruthAudit().asm[0]??null,sensor=d.sensorAudit(),sensorTrack=sensor.tracks.find(q=>q.id===track.id)??null;
      if(!truth&&truthRemovedTick==null){truthRemovedTick=i;atTruthRemoval={sensorTrack,displayable:sensor.displayable,presentation:d.wip121BdaTrackPresentation(track.id),support:d.wip121TargetSupportSnapshot(track.id)};}
      if(sensorTrack?.observedSeaImpact&&seaImpactTick==null){seaImpactTick=i;atSeaImpact={sensorTrack,displayable:sensor.displayable,presentation:d.wip121BdaTrackPresentation(track.id),support:d.wip121TargetSupportSnapshot(track.id)};}
      if(seaImpactTick!=null&&i>seaImpactTick+30)break;
    }
    d.wip119AutonomyTick();d.wip118ControlNow();const control=d.wip118ControlSnapshot(),sensor=d.sensorAudit(),history=d.wip75PipAudit().history;
    return {track,detectTicks,fireLog,firstSm2Launch,truthRemovedTick,atTruthRemoval,seaImpactTick,atSeaImpact,final:{sensorTrack:sensor.tracks.find(q=>q.id===track.id)??null,displayable:sensor.displayable,assessment:control.assessments.find(q=>q.trackId===track.id)??null,events:control.recentInterceptEvents.filter(q=>q.trackId===track.id),support:d.wip121TargetSupportSnapshot(track.id),presentation:d.wip121BdaTrackPresentation(track.id),history},selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });
  const final=result.final??{},checks={
    pageLoad:consoleErrors.length===0&&pageErrors.length===0,
    coreSelftests:result.selftests?.length===0,
    anonymousKh32Acquired:!result.error&&result.track?.associationDomain==null&&result.track?.classification==='ASM'&&result.detectTicks<1800,
    autoEngagementOccurred:result.fireLog?.some(q=>q.weapon==='SM2')&&result.firstSm2Launch?.targetId===result.track?.id,
    kh32PhysicalFlightEnded:result.truthRemovedTick!=null,
    liveCoastExistedAtRemoval:!!result.atTruthRemoval?.sensorTrack&&!result.atTruthRemoval.sensorTrack.observedSeaImpact&&result.atTruthRemoval.presentation?.hidden===false,
    observedSeaImpactPrompt:result.seaImpactTick!=null&&result.seaImpactTick>=result.truthRemovedTick&&result.seaImpactTick-result.truthRemovedTick<=180&&result.atSeaImpact?.sensorTrack?.observedSeaImpact?.predictedShipClearanceM>0,
    notInventedAsFriendlyKill:final.events?.length===0&&!final.history?.some(e=>e.targetId===result.track?.id&&e.deathReason==='PROX_DETONATION_KILL')&&final.presentation?.kind==='SEA_IMPACT'&&final.assessment?.state==='HARMLESS',
    ghostAsmHidden:final.sensorTrack?.observedSeaImpact!=null&&final.sensorTrack?.threatStatus==='HARMLESS'&&final.presentation?.hidden===true&&final.displayable?.asm===0,
    spgAndAutoSupportReleased:final.support?.blocked===true&&!final.support?.liveIlluminator&&!final.support?.reservation&&final.assessment?.liveEngagement===0&&final.assessment?.reengageRequired===false
  };
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/kh32-sea-impact-track-retirement.json`,`${JSON.stringify({schema:'AEGIS_KH32_OBSERVED_SEA_IMPACT_TRACK_RETIREMENT_V48_WIP11C',simulator,checks,consoleErrors,pageErrors,result},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C renders physical wreck meshes plus water column, rings, and foam', async ({ page }) => {
  test.setTimeout(240_000);
  const consoleErrors=[],pageErrors=[],localThree=process.env.THREE_LOCAL_FILE||process.env.THREE_JS_LOCAL;
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  if(localThree){
    await page.route('**/__wip11c_three.min.js',route=>route.fulfill({status:200,contentType:'application/javascript',body:fs.readFileSync(localThree)}));
    await page.addInitScript(()=>{window.__NAVAL_THREE_URL__='/__wip11c_three.min.js';});
  }
  await page.goto(`http://127.0.0.1:4173/${simulator}?view3d=1`,{waitUntil:'load'});
  await page.waitForFunction(()=>window.__WIP148_3D_VIEW__?.ready===true||!!window.__WIP148_3D_VIEW__?._loadError,null,{timeout:120_000});
  const ready=await page.evaluate(()=>({ready:window.__WIP148_3D_VIEW__.ready,loadError:window.__WIP148_3D_VIEW__._loadError}));
  expect(ready).toEqual({ready:true,loadError:null});
  const smokePresentationProbe=await page.evaluate(()=>{const v=window.__WIP148_3D_VIEW__,T=window.THREE,removeTagged=tag=>{for(let i=v.smokeParticles.length-1;i>=0;i--){const p=v.smokeParticles[i];if(!p[tag])continue;v.fxLayer?.remove(p.sprite);p.sprite?.material?.dispose?.();v.smokeParticles.splice(i,1);}};
    const asm={id:-11992,label:'Kh-32',lengthM:11.65,diameterM:.92,xM:180,zM:0,pitchRad:0,headingRad:0,thrustN:290000,motorActive:true};v.syncEnemyAsmVisuals({enemyAsms:[{...asm,yM:4000}]},1/60);const lowAsmSmoke=v.smokeParticles.filter(q=>q.asmSmoke).length;v.syncEnemyAsmVisuals({enemyAsms:[{...asm,yM:9000}]},1/60);const highAsmSmoke=v.smokeParticles.filter(q=>q.asmSmoke).length;v.syncEnemyAsmVisuals({enemyAsms:[]},1/60);removeTagged('asmSmoke');
    const s={kind:'SM2',id:-11993,lengthM:4.72,diameterM:.343,xM:0,yM:20,zM:0,headingRad:0,pitchRad:0,lifeS:1},profile=v.smokeVisualProfile(s,1),pose={x:0,y:20,z:0,dir:new T.Vector3(1,0,0)};for(let i=0;i<12;i++)v.emitSmoke(s,profile,1,0,{...pose,x:i*profile.spacingM,dir:pose.dir});const created=v.smokeParticles.filter(q=>q.interceptorTrail);for(const p of created)p.age=p.life*.35;v.updateSmoke(profile.life*.02,{ship:{speedMps:0}});const aged=v.smokeParticles.filter(q=>q.interceptorTrail),result={lowAsmSmoke,highAsmSmoke,created:created.length,agedSurvivors:aged.length,allAgedEvaluated:aged.every(q=>q.agedTrailEvaluated),minOpacityFactor:Math.min(...aged.map(q=>q.sprite.material.opacity/q.opacity0)),minScaleRatio:Math.min(...aged.map(q=>q.sprite.scale.x/q.base))};removeTagged('interceptorTrail');return result;});
  await page.evaluate(()=>{const d=window.__NAVAL_SIM_DIAG__;d.wip11cResetWreckage();d.wip11cCreateWreckageFixture({id:-11991,altM:18,speedMps:280,flightPathDeg:-8,damage:{fuel:80,engine:80,guidance:90}});});
  await page.waitForFunction(()=>window.__WIP148_3D_VIEW__.wreckVisuals.size>=3,null,{timeout:15_000});
  await page.waitForFunction(()=>window.__WIP148_3D_VIEW__.smokeParticles.some(q=>q.wreckSmoke)&&window.__WIP148_3D_VIEW__.smokeParticles.some(q=>q.wreckSmoke&&q.burstV4),null,{timeout:15_000});
  const wreck=await page.evaluate(()=>{const v=window.__WIP148_3D_VIEW__,fires=[...v.wreckVisuals.values()].map(q=>q.mesh.userData.wip11cFire).filter(q=>q?.visible);return {physics:window.get3DRenderState().asmWreckage.length,meshes:v.wreckVisuals.size,burning:fires.length,layeredFire:fires.filter(q=>q.children.length>=3).length,darkSmoke:v.smokeParticles.filter(q=>q.wreckSmoke&&!q.burstV4).length,flamePuffs:v.smokeParticles.filter(q=>q.wreckSmoke&&q.burstV4).length,smokeAudit:v.wip11cInterceptorSmokeAudit(),asmSmokeAudit:v.wip11cAsmSmokeAltitudeAudit()};});
  await page.evaluate(()=>window.__NAVAL_SIM_DIAG__.wip11cAdvanceWreckage(6));
  await page.waitForFunction(()=>window.__WIP148_3D_VIEW__.eventParticles.some(q=>q.kind==='WATER_COLUMN')&&window.__WIP148_3D_VIEW__.eventParticles.some(q=>q.kind==='WATER_RING')&&window.__WIP148_3D_VIEW__.eventParticles.some(q=>q.kind==='WATER_FOAM'),null,{timeout:15_000});
  const water=await page.evaluate(()=>({wreckMeshes:window.__WIP148_3D_VIEW__.wreckVisuals.size,kinds:[...new Set(window.__WIP148_3D_VIEW__.eventParticles.map(q=>q.kind).filter(k=>String(k).startsWith('WATER')))],eventSeen:window.__WIP148_3D_VIEW__.eventSeen.size,selftests:window.__CORE_SELFTEST_FAILURES__.slice()}));
  const checks={pageLoad:consoleErrors.length===0&&pageErrors.length===0,physicalMeshes:wreck.physics>=3&&wreck.meshes===wreck.physics,burningComponentVisual:wreck.burning>=1&&wreck.layeredFire===wreck.burning,visibleBurningTrail:wreck.darkSmoke>0&&wreck.flamePuffs>0,interceptorSmokeExtendedLife:wreck.smokeAudit.pass&&wreck.smokeAudit.rows.every(q=>q.lifetimeRatio===8),interceptorSmokeSparseLongTrail:wreck.smokeAudit.contract.samplingSpacingMultiplier===3.5&&wreck.smokeAudit.rows.every(q=>q.agedSpacingRatio===5.25)&&wreck.smokeAudit.averagePopulationFactor<1.85&&wreck.smokeAudit.checks.oldSmokeVisible&&wreck.smokeAudit.checks.agedExpansionGrows,agedSmokeDynamic:smokePresentationProbe.created===12&&smokePresentationProbe.agedSurvivors===8&&smokePresentationProbe.allAgedEvaluated&&smokePresentationProbe.minOpacityFactor>.65&&smokePresentationProbe.minScaleRatio>2,interceptorSmokeBounded:wreck.smokeAudit.contract.maxInterceptorParticles===9000&&wreck.smokeAudit.contract.maxGlobalSmokeParticles===12000&&wreck.smokeAudit.checks.singlePassUnderCap&&wreck.smokeAudit.checks.globalReserve,asmSmokeAltitudeGate:wreck.asmSmokeAudit.pass&&wreck.asmSmokeAudit.contract.hiddenAtOrBelowM===5000&&wreck.asmSmokeAudit.contract.fullDensityAtOrAboveM===8000&&smokePresentationProbe.lowAsmSmoke===0&&smokePresentationProbe.highAsmSmoke>0,retiredMeshes:water.wreckMeshes===0,waterColumn:water.kinds.includes('WATER_COLUMN')&&water.kinds.includes('WATER'),expandingRings:water.kinds.includes('WATER_RING'),lingeringFoam:water.kinds.includes('WATER_FOAM'),selftests:water.selftests.length===0};
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/asm-wreckage-3d-results.json`,`${JSON.stringify({schema:'AEGIS_ASM_WRECKAGE_3D_BROWSER_V48_WIP11C',simulator,checks,consoleErrors,pageErrors,ready,smokePresentationProbe,wreck,water},null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C preserves WIP11B same-seed outcomes outside the bounded Mk41 launch-azimuth correction', async ({ page }) => {
  test.setTimeout(240_000);
  const consoleErrors=[],pageErrors=[];
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  const run=async file=>{
    await page.goto(`http://127.0.0.1:4173/${file}`,{waitUntil:'load'});
    await page.waitForFunction(()=>window.__NAVAL_SIM_DIAG__?.runWip87PkAudit&&Array.isArray(window.__CORE_SELFTEST_FAILURES__),null,{timeout:45_000});
    return page.evaluate(()=>{const d=window.__NAVAL_SIM_DIAG__,audit=d.runWip87PkAudit({distancesKm:[100],seedBase:750000}),curves={essm:d.runWip88PkCurveDiagnostics({weaponType:'ESSM',targetLabel:'Kh-35U',missileSpeedMps:900,targetSpeedMps:280,distancesM:[2,5,10,15,20,30,40],anglesDeg:[0,45,90,135,180],angleTestMissM:15}),ram:d.runWip88PkCurveDiagnostics({weaponType:'RAM',targetLabel:'Kh-35U',missileSpeedMps:700,targetSpeedMps:280,distancesM:[2,5,10,15,20,30,40],anglesDeg:[0,45,90,135,180],angleTestMissM:15})};return {audit,curves,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};});
  };
  const baseline=await run('archive/v48/WIP11B/Aegis_SIM_v48_WIP11B.html'),candidate=await run(simulator),baselineJson=JSON.stringify(baseline.audit),candidateJson=JSON.stringify(candidate.audit),baselineCurveJson=JSON.stringify(baseline.curves),candidateCurveJson=JSON.stringify(candidate.curves);
  const numericDiffs=[];const compare=(a,b,path='root')=>{if(typeof a==='number'&&typeof b==='number'){const delta=Math.abs(a-b),limit=1e-8*Math.max(1,Math.abs(a),Math.abs(b));if(!(Number.isFinite(a)&&Number.isFinite(b)&&delta<=limit))numericDiffs.push({path,baseline:a,candidate:b,delta,limit});return;}if(Array.isArray(a)||Array.isArray(b)){if(!Array.isArray(a)||!Array.isArray(b)||a.length!==b.length){numericDiffs.push({path,baseline:a,candidate:b,reason:'ARRAY_SHAPE'});return;}for(let i=0;i<a.length;i++)compare(a[i],b[i],`${path}[${i}]`);return;}if(a&&b&&typeof a==='object'&&typeof b==='object'){const ak=Object.keys(a),bk=Object.keys(b);if(JSON.stringify(ak)!==JSON.stringify(bk)){numericDiffs.push({path,baseline:ak,candidate:bk,reason:'OBJECT_KEYS'});return;}for(const k of ak)compare(a[k],b[k],`${path}.${k}`);return;}if(a!==b)numericDiffs.push({path,baseline:a,candidate:b,reason:'VALUE'});};compare(baseline.audit,candidate.audit);
  const outcomeSignature=a=>a.rows.map(r=>({rangeKm:r.rangeKm,speedMps:r.speedMps,bearingDeg:r.bearingDeg,seed:r.seed,prox:r.prox,deathReason:r.deathReason,result:r.trace?.applyInterceptResult,targetAliveAfter:r.trace?.targetAliveAfter,rngStateBeforeApply:r.trace?.rngStateBeforeApply,rngStateAfterApply:r.trace?.rngStateAfterApply}));
  const baselineOutcome=outcomeSignature(baseline.audit),candidateOutcome=outcomeSignature(candidate.audit),checks={pageLoad:consoleErrors.length===0&&pageErrors.length===0,selftests:baseline.selftests.length===0&&candidate.selftests.length===0,sameSeedOutcomesExact:JSON.stringify(baselineOutcome)===JSON.stringify(candidateOutcome),sameSeedAuditNumericallyEquivalent:numericDiffs.length===0,pkCurvesExact:baselineCurveJson===candidateCurveJson,cases:baseline.audit.rows.length===12&&candidate.audit.rows.length===12};
  const evidence={schema:'AEGIS_WIP11B_WIP11C_GUIDANCE_INTERCEPT_BOUNDED_PARITY',baseline:'archive/v48/WIP11B/Aegis_SIM_v48_WIP11B.html',candidate:simulator,checks,parityTolerance:'absolute delta <= 1e-8 * max(1, |a|, |b|); discrete outcomes/RNG states exact',rawJsonExact:baselineJson===candidateJson,numericDiffs,baselineSha256:crypto.createHash('sha256').update(baselineJson).digest('hex'),candidateSha256:crypto.createHash('sha256').update(candidateJson).digest('hex'),baselineCurveSha256:crypto.createHash('sha256').update(baselineCurveJson).digest('hex'),candidateCurveSha256:crypto.createHash('sha256').update(candidateCurveJson).digest('hex'),summary:candidate.audit.summary,selftestFailures:{baseline:baseline.selftests,candidate:candidate.selftests},consoleErrors,pageErrors};
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/guidance-intercept-parity.json`,`${JSON.stringify(evidence,null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});

test('v48 WIP11C bounds the sparse long-lived smoke trail at the 9k and 12k WebGL ceilings', async ({ page }) => {
  test.setTimeout(300_000);
  const consoleErrors=[],pageErrors=[],localThree=process.env.THREE_LOCAL_FILE||process.env.THREE_JS_LOCAL;
  page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
  page.on('pageerror',error=>pageErrors.push(error.stack||String(error)));
  if(localThree){await page.route('**/__wip11c_three.min.js',route=>route.fulfill({status:200,contentType:'application/javascript',body:fs.readFileSync(localThree)}));await page.addInitScript(()=>{window.__NAVAL_THREE_URL__='/__wip11c_three.min.js';});}
  await page.goto(`http://127.0.0.1:4173/${simulator}?view3d=1`,{waitUntil:'load'});
  await page.waitForFunction(()=>window.__WIP148_3D_VIEW__?.ready===true||!!window.__WIP148_3D_VIEW__?._loadError,null,{timeout:120_000});
  const result=await page.evaluate(async()=>{
    const v=window.__WIP148_3D_VIEW__,T=window.THREE;if(!v?.ready)throw new Error(v?._loadError||'3D_NOT_READY');v.active=false;await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    const group=new T.Group();group.position.set(0,18,0);v.scene.add(group);const materials=[];
    const addTo=count=>{while(group.children.length<count){const i=group.children.length,mat=new T.SpriteMaterial({color:i<9000?0xdededa:0x777777,transparent:true,opacity:.18,depthWrite:false}),sp=new T.Sprite(mat);sp.position.set(((i%61)-30)*.025,((Math.floor(i/61)%41)-20)*.025,(i%7)*.002);sp.scale.setScalar(.8);group.add(sp);materials.push(mat);}};
    const measure=count=>{addTo(count);for(let i=0;i<2;i++)v.renderer.render(v.scene,v.camera);const samples=[];let calls=0;for(let i=0;i<5;i++){const t0=performance.now();v.renderer.render(v.scene,v.camera);samples.push(performance.now()-t0);calls=v.renderer.info.render.calls;}const sorted=samples.slice().sort((a,b)=>a-b);return {visibleSmokeSprites:count,meanFrameMs:samples.reduce((a,b)=>a+b,0)/samples.length,p50FrameMs:sorted[Math.floor(sorted.length*.5)],p95FrameMs:sorted[Math.min(sorted.length-1,Math.floor(sorted.length*.95))],drawCalls:calls};};
    const rows=[measure(0),measure(9000),measure(12000)],audit=v.wip11cInterceptorSmokeAudit();v.scene.remove(group);for(const mat of materials)mat.dispose();return {contract:audit.contract,averagePopulationFactor:audit.averagePopulationFactor,rows};
  });
  const [base,interceptor,global]=result.rows,checks={pageLoad:consoleErrors.length===0&&pageErrors.length===0,contractLongSparse:result.contract.lifetimeMultiplier===8&&result.contract.samplingSpacingMultiplier===3.5&&result.averagePopulationFactor<1.85,capsExact:result.contract.maxInterceptorParticles===9000&&result.contract.maxGlobalSmokeParticles===12000,interceptorDrawBound:interceptor.drawCalls-base.drawCalls>=8900&&interceptor.drawCalls-base.drawCalls<=9100,globalDrawBound:global.drawCalls-interceptor.drawCalls>=2900&&global.drawCalls-interceptor.drawCalls<=3100,finiteMeasurements:result.rows.every(r=>Number.isFinite(r.meanFrameMs)&&r.meanFrameMs>=0)};
  const evidence={schema:'AEGIS_INTERCEPTOR_SMOKE_WEBGL_BENCHMARK_V48_WIP11C',simulator,environment:'Playwright Chromium headless software render; every synthetic sprite visible',warning:'Absolute FPS is hardware-dependent; use deltas and draw-call counts.',contract:result.contract,averagePopulationFactor:result.averagePopulationFactor,rows:result.rows,delta0To9000:{meanFrameMs:interceptor.meanFrameMs-base.meanFrameMs,drawCalls:interceptor.drawCalls-base.drawCalls},delta9000To12000:{meanFrameMs:global.meanFrameMs-interceptor.meanFrameMs,drawCalls:global.drawCalls-interceptor.drawCalls},checks,consoleErrors,pageErrors};
  fs.mkdirSync(artifactDir,{recursive:true});fs.writeFileSync(`${artifactDir}/smoke-budget-benchmark.json`,`${JSON.stringify(evidence,null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key=>[key,true])));
});
