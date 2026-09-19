const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12D.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/residual-overpenetration-wip12d';

test.use({ viewport:{ width:1600, height:900 } });

test('v48 WIP12D gives Kh-32 bounded reentry, real residual breaches, and a conserved teardrop blast', async ({ page }) => {
  test.setTimeout(300_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481232; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.wip12dResidualOverpenetrationDiagnostics, null, { timeout:60_000 });

  await page.evaluate(() => { document.getElementById('shipDetailPanel').style.display='block'; });
  await page.waitForTimeout(100);
  const funnelIndicatorPixels = await page.evaluate(() => {
    const cv=document.getElementById('shipDetailCanvas'),ctx=cv.getContext('2d'),P=window.__AEGIS_ACTIVE_SHIP_PROFILE__.geometry.funnels,W=cv.width,H=cv.height,sc=1.8,tcx=W/2,tcy=H*.48*.5,sideY=H*.48+4,sideH=H-H*.48-16,scy=sideY+sideH,ssc=sideH/70;
    const sample=(id,x,y)=>({id,x,y,rgba:[...ctx.getImageData(Math.round(x),Math.round(y),1,1).data]}),tx=x=>tcx-x*sc,section=(F,z)=>{const t=(z-F.shellBottomZM)/(F.topZM-F.shellBottomZM);return {aft:F.xAftM+(F.roofAftXM-F.xAftM)*t,fwd:F.xFwdM+(F.roofFwdXM-F.xFwdM)*t};},z=12,fs=section(P.forward,z),as=section(P.aft,z);
    return [
      sample('TOP_FWD_AFT_EXTENSION',tx(P.forward.xAftM+.35),tcy),
      sample('TOP_AFT_AFT_EXTENSION',tx(P.aft.xAftM+.20),tcy),
      sample('TOP_AFT_FWD_EXTENSION',tx(P.aft.xFwdM-.25),tcy),
      sample('SIDE_FWD_AFT_EXTENSION',tx(fs.aft+.35),scy-z*ssc),
      sample('SIDE_AFT_AFT_EXTENSION',tx(as.aft+.20),scy-z*ssc),
      sample('SIDE_AFT_FWD_EXTENSION',tx(as.fwd-.25),scy-z*ssc)
    ];
  });
  await page.evaluate(() => { document.getElementById('shipDetailPanel').style.display='none'; });

  const result = await page.evaluate(() => {
    const d=window.__NAVAL_SIM_DIAG__,contract=d.wip12dResidualOverpenetrationContract(),diagnostic=d.wip12dResidualOverpenetrationDiagnostics(),funnelGeometry=d.wip12bFunnelGeometryAudit();
    const run=()=>{
      const flight=d.runWip107AsmMemoryCase({label:'Kh-32',rangeKm:100,maxTimeS:300,seed:481232}),event=d.wip12bTerminalEvents().find(q=>q.weaponKey==='KH32'),residual=d.wip12dResidualEventDiagnostics(event?.impactEventId),hit=d.snapshot().shipLastHit,flood=d.damageFloodSnapshotV1();
      return {flight:{label:flight.label,durationS:flight.durationS,targetAlive:flight.targetAlive,deathReason:flight.deathReason,shipHit:flight.shipHit},hit:hit?{impactSpeed:hit.impactSpeed,impactKineticEnergyMJ:hit.impactKineticEnergyMJ,penetration:hit.penetration,physicalPenetrationM:hit.physicalPenetrationM,preDetonationResidualEnergyMJ:hit.preDetonationResidualEnergyMJ,dmg:hit.dmg,part:hit.part,impactPart:hit.impactPart,blastSources:hit.blastSources.map(q=>({...q})),blastParts:hit.blastParts.map(q=>({name:q.name,dmg:q.dmg,dist:q.dist,pathCrossed:q.pathCrossed,side:q.side,deck:q.deck,system:q.system}))}:null,event:event?{impactEventId:event.impactEventId,weaponKey:event.weaponKey,fuzePath:event.fuzePath,effectResult:event.effectResult,applicationAuthority:event.applicationAuthority,damageAppliedBy:event.damageAppliedBy,damageSummary:event.damageSummary,cascadeSummary:event.cascadeSummary,visual:event.visual}:null,residual,flood:{summary:flood.summary,openings:flood.openings.map(q=>({id:q.id,x:q.x,y:q.y,z:q.z,areaM2:q.areaM2,seaWet01:q.seaWet01,kind:q.kind})),events:flood.events}};
    };
    const first=run(),second=run(),stable=q=>({flight:q.flight,hit:q.hit,event:{weaponKey:q.event.weaponKey,fuzePath:q.event.fuzePath,effectResult:q.event.effectResult,applicationAuthority:q.event.applicationAuthority,damageAppliedBy:q.event.damageAppliedBy,damageSummary:q.event.damageSummary,cascadeSummary:q.event.cascadeSummary},residual:q.residual});
    const deterministic=JSON.stringify(stable(first))===JSON.stringify(stable(second));
    const dud=d.runWip113DudImpactProbe({dud:true,rangeKm:2.4,altM:12,speedMps:280,seed:481233}),dudEvent=d.wip12bTerminalEvents()[0]??null,performance=d.wip12cShipTraversalPerformance(256),supplementProbe=d.wip12dResidualSupplementProbe(),shipReentryProbe=d.wip12dShipReentryProbe();
    return {contract,diagnostic,funnelGeometry,first,secondDeterministic:deterministic,dud,dudEvent,performance,supplementProbe,shipReentryProbe,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const q=result.first,residual=q.residual,ledger=residual.ledger,bodies=residual.bodies,allBoundaries=bodies.flatMap(body=>body.boundaries),exitIds=new Set(residual.farHullExits.map(exit=>exit.bodyId)),sourcePower=q.hit.blastSources.reduce((s,x)=>s+x.powerFraction,0),residualFloodEvent=q.flood.events.find(e=>e.id.endsWith(':RESIDUAL_SUPPLEMENT')),residualOpenings=residual.residualSupplement.additionalShellOpenings;
  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftests.length === 0,
    diagnostic: result.diagnostic.pass && Object.values(result.diagnostic.checks).every(Boolean),
    funnelGeometryR2: result.funnelGeometry.pass && result.funnelGeometry.revision === 'V48_WIP12D_FUNNEL_EXTENSION_R2' && result.funnelGeometry.forward.xAftM === 3.5 && result.funnelGeometry.forward.xFwdM === 17.1 && result.funnelGeometry.aft.xAftM === -18.15 && result.funnelGeometry.aft.xFwdM === -4.55,
    spgClearanceAndCalculatedMask: result.funnelGeometry.checks.spgMountAndSupportCoupled && result.funnelGeometry.checks.spgPlanClearance && result.funnelGeometry.checks.spgLoftClearance && result.funnelGeometry.checks.spgTangentMasksCalculated && result.funnelGeometry.aftHighPlanClearanceM >= .35 && result.funnelGeometry.aftHighLoftClearanceM >= 1 && result.funnelGeometry.spgBlindHalfDeg.join(',') === '41,49,54' && result.funnelGeometry.spgFunnelTangentCeilDeg.join(',') === '0,49,20',
    twoDIndicatorUpdated: funnelIndicatorPixels.length === 6 && funnelIndicatorPixels.every(sample=>sample.rgba[0]>=105&&sample.rgba[1]>=115&&sample.rgba[2]>=120&&sample.rgba[3]>=245),
    realKh32Hit: q.flight.label === 'Kh-32' && q.flight.shipHit && !q.flight.targetAlive && q.flight.deathReason === 'NORMAL_HIT' && Math.abs(q.flight.durationS-92.78333333333333) < 1e-9,
    intendedFunnelHitboxDelta: q.hit.dmg === 191 && q.hit.part === '제1보일러실' && q.hit.impactPart === '전방연돌' && Math.abs(q.hit.impactKineticEnergyMJ-2849.804054661079) < 1e-9 && Math.abs(q.hit.penetration-4.318827711120478) < 1e-9 && Math.abs(q.hit.physicalPenetrationM-22.52876902577326) < 1e-9,
    conservedTeardropBlast: q.hit.blastSources.length === 3 && Math.abs(sourcePower-1) < 1e-12 && q.hit.blastSources[0].u === 0 && q.hit.blastSources[1].u > .5 && q.hit.blastSources[2].u === 1 && q.hit.blastParts.reduce((s,x)=>s+x.dmg,0) === q.hit.dmg && q.event.visual.blastEnvelope.nodes.length === q.hit.blastSources.length && q.event.visual.blastEnvelope.shape === 'SPEED_WEIGHTED_TEARDROP_MULTI_LOBE',
    spatialBlastGolden: q.hit.blastParts.length === 17 && q.hit.blastParts[0].name === '제1보일러실' && q.hit.blastParts[0].dmg === 47 && q.hit.blastParts[1].name === '제1발전실' && q.hit.blastParts[1].dmg === 43,
    legacyPrimaryPlusResidualSupplement: q.event.applicationAuthority === 'OBSERVED_ALREADY_APPLIED' && q.event.damageAppliedBy === 'LEGACY_ASM_DAMAGE_PATH' && q.event.cascadeSummary.authority === 'LEGACY_PREACCOUNTED_OBSERVATION_ONLY' && q.event.cascadeSummary.mergeDamage === false && residual.residualSupplement.accepted && residual.residualSupplement.legacyBlastReplay === false,
    physicalMotionRecovered: q.hit.preDetonationResidualEnergyMJ > 0 && ledger.parentKineticJ > 1e9 && ledger.preDetonationSpeedMps > 700 && ledger.preDetonationSpeedMps < q.event.damageSummary.speedBeforeMps && ledger.preDetonationRetainedEnergyRatio01 > .75 && ledger.preDetonationRetainedEnergyRatio01 < .9,
    boundedMacroBodies: bodies.length === result.contract.motion.maxBodies && bodies.every(body=>body.massKg >= 20 && body.massKg <= 40 && body.initialSpeedMps > 1000 && body.queryCount <= result.contract.performance.maxEventsPerBody),
    mixedPhysicalOutcomes: bodies.some(body=>body.terminationReason === 'PROJECTILE_SHATTERED') && bodies.some(body=>body.terminationReason === 'TARGET_EXIT') && residual.farHullExits.length === 2,
    shatterCanContinue: ledger.shatterContinuations > 0 && bodies.some(body=>body.shatterContinuations > 0 && body.terminationReason === 'TARGET_EXIT') && allBoundaries.some(row=>row.traversalOutcome === 'PERFORATED' && row.projectileFailure === 'SHATTERED'),
    plateAndVolumeStateMonotonic: allBoundaries.every(row=>row.speedAfterMps <= row.speedBeforeMps+1e-9 && row.massAfterKg <= row.massBeforeKg+1e-9 && row.coherentMassAfterKg <= row.coherentMassBeforeKg+1e-9 && row.kineticAfterJ <= row.kineticBeforeJ+1e-6),
    massLedgerClosed: Math.abs(ledger.massClosureErrorKg) < 1e-9 && Math.abs(ledger.parentNonExplosiveMassKg-ledger.macroMassKg-ledger.statisticalFragmentMassKg) < 1e-9,
    energyLedgerBounded: Math.abs(ledger.macroInitialKineticJ-ledger.inheritedTranslationJ-ledger.chemicalEnergyCoupledJ) < 1e-6 && ledger.macroInitialKineticJ <= ledger.parentKineticJ+ledger.chemicalEnergyCoupledJ+1e-6 && ledger.energyClosureSlackJ >= 0,
    validFarHullResiduals: residual.farHullExits.every(exit=>exit.residualMassKg >= result.contract.shatterContinuation.minResidualMassKg && exit.residualCoherentMassKg >= result.contract.shatterContinuation.minCoherentMassKg && exit.residualSpeedMps >= result.contract.shatterContinuation.minResidualSpeedMps && exit.residualKineticJ >= result.contract.shatterContinuation.minResidualEnergyJ && exit.holeAreaM2 > 0 && exitIds.has(exit.bodyId)),
    boundedReentryContract: result.diagnostic.checks.boundedReentryQuery && result.diagnostic.checks.reentryUsesMaterialSolver && result.diagnostic.checks.reexitCanPerforateOrStop && result.shipReentryProbe.pass && result.shipReentryProbe.checks.orderedExitReentryExit && result.shipReentryProbe.checks.everyPerforationHasHole && result.shipReentryProbe.checks.materialRecomputed && residual.reentries.length <= result.contract.reentry.maxReentriesPerBody*result.contract.motion.maxBodies && bodies.every(body=>body.outsideQueryCount <= result.contract.reentry.maxSamplesPerLeg*Math.max(1,result.contract.reentry.maxReentriesPerBody)),
    everyHullCrossingMakesRealHole: residual.shellCrossings.length === 2 && residualOpenings.length === residual.shellCrossings.length && residualFloodEvent?.contacts >= residual.shellCrossings.length && residualOpenings.every(h=>q.flood.openings.some(o=>Math.hypot(o.x-h.position.x,o.y-h.position.y,o.z-h.position.z)<2.1&&o.areaM2+1e-9>=h.holeAreaM2)),
    submergedResidualHolesCanFlood: q.flood.openings.filter(o=>residualOpenings.some(h=>Math.hypot(o.x-h.position.x,o.y-h.position.y,o.z-h.position.z)<2.1)).some(o=>o.seaWet01>0) && result.supplementProbe.pass && result.supplementProbe.checks.submergedOpeningFloods,
    supplementIdempotentAndNoGenericFire: result.supplementProbe.checks.duplicateRejected && result.supplementProbe.checks.noBlastReplay && result.supplementProbe.checks.noGenericFire && residual.residualSupplement.ignitionAudit.ignitionCount === 0,
    precomputedWaterPaths: residual.postExitPaths.length === residual.farHullExits.length && residual.seaEntries.length === residual.farHullExits.length && residual.postExitPaths.every(path=>path.presentationOnly && path.points.length <= result.contract.postExit.samples) && residual.seaEntries.some(entry=>entry.kind === 'SEA_ENTRY') && residual.seaEntries.some(entry=>entry.kind === 'SUBMERGED_WATER_ENTRY'),
    noRenderDamagePhysics: result.contract.postExit.damageFeedback === false && result.contract.postExit.renderFramePhysics === false && result.contract.scope.duplicateLegacyDamageApplication === false && result.contract.scope.residualMechanicalAndBreachSupplement === true,
    combatRngUnchanged: q.event.cascadeSummary.rngUnchanged && result.diagnostic.checks.combatRngUnchanged,
    sameSeedExact: result.secondDeterministic,
    dudStillNoCascade: result.dud.outcome === 'DUD_PENETRATION' && result.dudEvent.fuzePath === 'DUD' && result.dudEvent.cascadeSummary.macroBodies === 0 && result.dudEvent.cascadeSummary.farHullExits === 0,
    impactTimePerformance: result.performance.iterations === 256 && result.performance.perImpactMs < 10 && result.performance.renderFrameQueries === 0 && result.performance.rngUnchanged,
    scopeHeld: result.contract.exclusions.includes('LEGACY_ASM_DAMAGE_RETUNE') && result.contract.exclusions.includes('LEGACY_ASM_BLAST_REPLAY') && result.contract.exclusions.includes('UNBOUNDED_FRAGMENT_ENTITIES') && result.contract.exclusions.includes('PERSISTENT_DAMAGE_PATCH')
  };

  fs.mkdirSync(artifactDir, { recursive:true });
  fs.writeFileSync(`${artifactDir}/residual-overpenetration-results.json`, `${JSON.stringify({ schema:'AEGIS_RESIDUAL_OVERPENETRATION_BROWSER_V48_WIP12D', simulator, simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, funnelIndicatorPixels, result }, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('v48 WIP12D shows depth-independent Kh-32 residual paths only in focused interior mode and batches hazards', async ({ page }) => {
  test.setTimeout(600_000);
  const consoleErrors = [], pageErrors = [], localThree = process.env.THREE_LOCAL_FILE || process.env.THREE_JS_LOCAL;
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  if (localThree) {
    await page.route('**/__wip12d_three.min.js', route => route.fulfill({ status:200, contentType:'application/javascript', body:fs.readFileSync(localThree) }));
    await page.addInitScript(() => { window.__NAVAL_THREE_URL__ = '/__wip12d_three.min.js'; window.__NAVAL_SIM_SEED__ = 481232; });
  } else {
    await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481232; });
  }
  await page.goto(`http://127.0.0.1:4173/${simulator}?view3d=1`, { waitUntil:'load' });
  await page.waitForFunction(() => window.__WIP148_3D_VIEW__?.ready === true || !!window.__WIP148_3D_VIEW__?._loadError, null, { timeout:120_000 });
  const ready = await page.evaluate(() => ({ ready:window.__WIP148_3D_VIEW__.ready, loadError:window.__WIP148_3D_VIEW__._loadError }));
  expect(ready).toEqual({ ready:true, loadError:null });
  if (await page.locator('#wip125DepartBtn').isVisible()) await page.locator('#wip125DepartBtn').click();

  const result = await page.evaluate(() => {
    const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__;v.active=false;d.runWip107AsmMemoryCase({label:'Kh-32',rangeKm:100,maxTimeS:300,seed:481232});const hazard=d.wip12bInteriorHazardPresentationProbe({flood01:.58,fire01:.42,smoke01:.68}),base=performance.now();
    v.active=true;for(let i=0;i<180;i++)v.render(base+i*16.667);v.active=false;const exterior=v.residualOverpenetrationAuditV48Wip12D();
    if(!v.interiorTopologyVisible)v.toggleInteriorTopology();v.orbit.yaw=Math.PI/2;v.orbit.pitch=.17;v.orbit.distance=72;v.orbit.targetY=4.5;v.active=true;for(let i=180;i<212;i++)v.render(base+i*16.667);v.active=false;const focused=v.residualOverpenetrationAuditV48Wip12D(),focusedStats={calls:v.renderer.info.render.calls,triangles:v.renderer.info.render.triangles},summary=document.getElementById('external3DTerminalSummary')?.textContent??'',focusButton={pressed:document.getElementById('external3DInteriorFocusBtn')?.getAttribute('aria-pressed'),text:document.getElementById('external3DInteriorFocusBtn')?.textContent};
    v.toggleInteriorImpactFocusV48Wip12D();v.active=true;for(let i=212;i<216;i++)v.render(base+i*16.667);v.active=false;const full=v.residualOverpenetrationAuditV48Wip12D(),fullStats={calls:v.renderer.info.render.calls,triangles:v.renderer.info.render.triangles};
    v.toggleInteriorImpactFocusV48Wip12D();v.active=true;for(let i=216;i<220;i++)v.render(base+i*16.667);const canvasDataUrl=v.canvas.toDataURL('image/png');v.active=false;const restored=v.residualOverpenetrationAuditV48Wip12D(),funnel3D=v.funnelGeometry3DAuditV48Wip12B(),event=d.wip12bTerminalEvents().find(q=>q.weaponKey==='KH32');
    return {hazard:{spaceId:hazard.spaceId,row:hazard.state.hazards.find(h=>h.spaceId===hazard.spaceId)},event,exterior,focused,full,restored,funnel3D,focusedStats,fullStats,summary,focusButton,canvasDataUrl,selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const event=result.event,checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftests.length === 0,
    wip12dEvent: event.cascadeSummary.schema === 'AEGIS_TERMINAL_EFFECT_CASCADE_V48_WIP12D' && event.cascadeSummary.macroBodies === 4 && event.cascadeSummary.farHullExits === 2 && event.cascadeSummary.residualSupplement.accepted,
    funnelAndSpg3DProfileDriven: result.funnel3D.pass && result.funnel3D.revision === 'V48_WIP12D_FUNNEL_EXTENSION_R2' && result.funnel3D.rows.FWD.matched && result.funnel3D.rows.AFT.matched && result.funnel3D.checks.spgMountsProfileDriven && result.funnel3D.checks.aftHighSpgMoved && result.funnel3D.checks.aftHighPedestalMoved && result.funnel3D.spgMounts.find(q=>q.id===1)?.xM === -20,
    hiddenOutsideInterior: result.exterior.terminal.hiddenOutsideInterior && !result.exterior.terminal.visible && result.exterior.interior.detailedHiddenOutsideInterior && !result.exterior.focusActive,
    visibleOnlyInInterior: result.focused.terminal.visibleInInterior && result.focused.terminal.visibilityMatchesInterior && result.focused.interior.detailedTopologyVisible && result.focused.interior.coarseHiddenInInteriorMode,
    macroPathsVisible: result.focused.terminal.macroPathVisuals === event.cascadeSummary.macroBodies && result.focused.terminal.macroBodyVisuals === event.cascadeSummary.macroBodies && result.focused.terminal.farHullExitVisuals === event.cascadeSummary.farHullExits,
    exitAndWaterPresentation: result.focused.postExitRepresented && result.focused.seaEntriesRepresented && result.focused.terminal.postExitPathVisuals >= 1 && result.focused.terminal.seaEntryVisuals === event.cascadeSummary.seaEntries,
    teardropBlastPresentation: event.visual.blastEnvelope.nodes.length === 3 && result.focused.blastEnvelopesRepresented && result.focused.terminal.blastEnvelopeVisuals === 1 && result.focused.reentriesRepresented,
    readableDepthIndependentPaths: result.focused.depthIndependent && result.focused.terminal.depthIndependentMacroPaths === result.focused.terminal.macroPathVisuals+result.focused.terminal.postExitPathVisuals,
    impactFocusActive: result.focused.focusButtonPresent && result.focused.focusEnabled && result.focused.focusActive && result.focused.focusClippingPlanes === 6 && result.focused.focusedMaterials > 0 && result.focused.focusCulledObjects > 1000,
    fullInteriorFallback: !result.full.focusEnabled && !result.full.focusActive && result.full.focusClippingPlanes === 0 && result.full.focusedMaterials === 0 && result.full.interior.detailedTopologyVisible,
    focusRestored: result.restored.focusEnabled && result.restored.focusActive && result.restored.focusClippingPlanes === 6,
    statusExplainsResult: result.focused.summaryVisible && result.summary.includes('KH32') && result.summary.includes('잔존체 4') && result.summary.includes('반대편 이탈 2') && result.summary.includes('실제 외피 구멍 2') && result.summary.includes('진단 시각화') && result.focusButton.pressed === 'true' && result.focusButton.text === '피격 중심',
    hazardsBatched: result.hazard.row.flood01 === .58 && result.hazard.row.fire01 === .42 && result.hazard.row.smoke01 === .68 && result.focused.hazardsBatched && result.focused.interior.hazardBatchCount > 0 && result.focused.interior.hazardBatchCount <= 3 && result.focused.interior.hazardFragmentCount > result.focused.interior.hazardBatchCount,
    boundedDrawables: result.focusedStats.calls > 0 && result.focusedStats.calls < 300 && result.focusedStats.calls < result.fullStats.calls*.25 && result.focusedStats.triangles > 0,
    visualLayerPresentationOnly: result.focused.presentationOnly && !result.focused.physicsFeedback && event.cascadeSummary.mergeDamage === false && event.cascadeSummary.residualSupplement.accepted
  };

  fs.mkdirSync(artifactDir, { recursive:true });
  const { canvasDataUrl, ...resultWithoutImage } = result;
  fs.writeFileSync(`${artifactDir}/residual-overpenetration-3d-results.json`, `${JSON.stringify({ schema:'AEGIS_RESIDUAL_OVERPENETRATION_3D_BROWSER_V48_WIP12D', simulator, simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, ready, result:resultWithoutImage }, null, 2)}\n`);
  const prefix='data:image/png;base64,';
  expect(canvasDataUrl.startsWith(prefix)).toBe(true);
  fs.writeFileSync(`${artifactDir}/residual-overpenetration-3d.png`, Buffer.from(canvasDataUrl.slice(prefix.length), 'base64'));
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
