const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12C.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/internal-terminal-effects-wip12c';

test.use({ viewport:{ width:1600, height:900 } });

test('v48 WIP12C resolves deterministic internal cascades and applies one combined packet', async ({ page }) => {
  test.setTimeout(240_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481230; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.wip12cInternalEffectsDiagnostics, null, { timeout:60_000 });

  const result = await page.evaluate(() => {
    const d=window.__NAVAL_SIM_DIAG__,contract=d.wip12cInternalEffectsContract(),diagnostic=d.wip12cInternalEffectsDiagnostics();
    const fixture=d.wip12cRunFixture({impactEventId:'WIP12C_BROWSER_COMMIT'}),macroSummary=fixture.cascade.macroBodies.map(q=>({bodyId:q.bodyId,massKg:q.massKg,initialSpeedMps:q.initialSpeedMps,terminationReason:q.terminationReason,farHullExit:q.farHullExit}));
    const shipProbe=d.wip12cShipTraversalProbe({impactEventId:'WIP12C_BROWSER_SHIP'}),alternateProbe=d.wip12cShipTraversalProbe({impactEventId:'WIP12C_BROWSER_SHIP_ALT',direction:{x:.32,y:.947,z:-.04}}),stoppedProbe=d.wip12cShipTraversalProbe({impactEventId:'WIP12C_BROWSER_SHIP_STOP',speedMps:80}),performance=d.wip12cShipTraversalPerformance(512),ignition=d.wip12cIgnitionPolicyDiagnostics();
    d._resetShipTest();const before={flood:d.damageFloodSnapshotV1(),crew:d.v48Wip07CrewState(),control:d.damageControlSnapshotV1()},first=d.wip12aApplyDamagePacket(fixture.damagePacket,{commit:true,defaultTargetId:'Mk45'}),middle={flood:d.damageFloodSnapshotV1(),crew:d.v48Wip07CrewState(),control:d.damageControlSnapshotV1()},second=d.wip12aApplyDamagePacket(fixture.damagePacket,{commit:true,defaultTargetId:'Mk45'}),after={flood:d.damageFloodSnapshotV1(),crew:d.v48Wip07CrewState(),control:d.damageControlSnapshotV1()};
    d._resetShipTest();const inertBefore=d.damageControlSnapshotV1(),inertApply=d.wip12aApplyDamagePacket(stoppedProbe.trace.damagePacket,{commit:true,defaultTargetId:'Mk45'}),inertAfter=d.damageControlSnapshotV1();
    const mechanicalIgnition=d.wip12cMechanicalIgnitionApplicationProbe();
    d._resetShipTest();d.wip12bResetTerminalEvents();const liveNormal=d.runWip113DudImpactProbe({dud:false,rangeKm:2.4,altM:12,speedMps:280}),normalEvent=d.wip12bTerminalEvents()[0];d._resetShipTest();d.wip12bResetTerminalEvents();const liveDud=d.runWip113DudImpactProbe({dud:true,rangeKm:2.4,altM:12,speedMps:280}),dudEvent=d.wip12bTerminalEvents()[0];
    const slimProbe=q=>({terminationReason:q.trace.terminationReason,queryCount:q.trace.queryCount,boundaryMaterials:q.boundaryMaterials,farHullBreaches:q.farHullBreaches,geometryDiagnostics:q.geometryDiagnostics});
    d._resetShipTest();return {contract,diagnostic,fixture:{terminationReason:fixture.trace.terminationReason,rootCorridors:fixture.damagePacket.penetrationCorridors.filter(q=>!q.secondaryBodyId).length,secondaryCorridors:fixture.damagePacket.penetrationCorridors.filter(q=>q.secondaryBodyId).length,breaches:fixture.damagePacket.breaches.length,macroSummary,cascade:{authority:fixture.cascade.authority,mergeDamage:fixture.cascade.mergeDamage,farHullExits:fixture.cascade.farHullExits.length,ledger:fixture.cascade.ledger,rngUnchanged:fixture.cascade.rngUnchanged}},shipTraversal:{primary:slimProbe(shipProbe),alternate:slimProbe(alternateProbe),stopped:slimProbe(stoppedProbe),performance},ignition,mechanicalIgnition,application:{first,second,before:{floodEvents:before.flood.events.length,crewEvents:before.crew.damageEvents.length},middle:{floodEvents:middle.flood.events.length,floodIssues:middle.flood.issues,crewEvent:middle.crew.damageEvents.at(-1),injured:middle.crew.injured,dead:middle.crew.dead,burning:middle.control.summary.burning},after:{floodEvents:after.flood.events.length,crewEvents:after.crew.damageEvents.length},inert:{apply:inertApply,burningBefore:inertBefore.summary.burning,burningAfter:inertAfter.summary.burning}},legacy:{liveNormal,normalEvent,liveDud,dudEvent},selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const ledger=result.fixture.cascade.ledger,primaryFar=result.shipTraversal.primary.boundaryMaterials.find(q=>q.surfaceId.includes('FAR_HULL')),alternateFar=result.shipTraversal.alternate.boundaryMaterials.find(q=>q.surfaceId.includes('FAR_HULL'));
  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftests.length === 0,
    diagnostic: result.diagnostic.pass && Object.values(result.diagnostic.checks).every(Boolean),
    boundedDeterministicCascade: result.fixture.macroSummary.length >= 1 && result.fixture.macroSummary.length <= result.contract.cascade.maxBodies && result.fixture.cascade.rngUnchanged,
    commonTraversalChildren: result.fixture.macroSummary.every(q => q.terminationReason && q.massKg > 0 && q.initialSpeedMps > 0),
    farHullExit: result.fixture.cascade.farHullExits >= 1 && result.fixture.macroSummary.some(q => q.farHullExit?.holeAreaM2 > 0),
    massClosed: Math.abs(ledger.massClosureErrorKg) < 1e-9 && Math.abs(ledger.parentNonExplosiveMassKg-ledger.macroMassKg-ledger.statisticalFragmentMassKg) < 1e-9,
    energyBounded: ledger.macroInitialKineticJ <= ledger.parentKineticJ+ledger.chemicalEnergyCoupledJ+1e-6 && ledger.energyClosureSlackJ >= -1e-6,
    combinedPacket: result.fixture.rootCorridors === 1 && result.fixture.secondaryCorridors === result.fixture.macroSummary.length && result.fixture.breaches >= result.fixture.cascade.farHullExits,
    appliedExactlyOnce: result.application.first.accepted && !result.application.second.accepted && result.application.second.reason === 'DUPLICATE_IMPACT_EVENT' && result.application.middle.floodEvents === 1 && result.application.after.floodEvents === 1 && result.application.after.crewEvents === 1,
    consumersReceiveCascade: result.application.middle.crewEvent.penetrationLineCount === 1+result.fixture.macroSummary.length && result.application.middle.crewEvent.penetratedSpaceIds.length >= 1 && result.application.middle.burning >= 1 && result.application.first.ignitionAudit.appliedCount >= 1,
    dynamicMaterialTraversal: result.shipTraversal.primary.terminationReason === 'TARGET_EXIT' && result.shipTraversal.primary.boundaryMaterials.some(q=>q.materialProfileId === 'WATERTIGHT_MACHINERY') && primaryFar?.materialProfileId === 'SHELL_WATERLINE',
    localHullNormalAndRequery: primaryFar?.obliquityDeg > .5 && alternateFar && Math.hypot(primaryFar.position.x-alternateFar.position.x,primaryFar.position.y-alternateFar.position.y,primaryFar.position.z-alternateFar.position.z) > .25,
    internalStructureCanStop: result.shipTraversal.stopped.terminationReason === 'PROJECTILE_STOPPED' && result.shipTraversal.stopped.farHullBreaches.length === 0,
    boundedImpactTimePerformance: result.shipTraversal.primary.geometryDiagnostics.impactTimeOnly && result.shipTraversal.primary.geometryDiagnostics.renderFrameQueries === 0 && result.shipTraversal.primary.geometryDiagnostics.candidateReduction01 > .3 && result.shipTraversal.primary.queryCount <= result.contract.geometry.maxEventsPerBody,
    traversalBenchmark: result.shipTraversal.performance.iterations === 512 && result.shipTraversal.performance.perImpactMs < 10 && result.shipTraversal.performance.maxQueries <= result.contract.geometry.maxEventsPerBody && result.shipTraversal.performance.candidateReduction01 > .3 && result.shipTraversal.performance.renderFrameQueries === 0 && result.shipTraversal.performance.rngUnchanged,
    volumeResistanceAndNoSpeedCreation: result.diagnostic.checks.materialVolumeConsumesEnergy && result.diagnostic.checks.speedNeverIncreases && result.diagnostic.shipTraversal.volumeResults.every(q=>q.speedAfterMps < q.speedBeforeMps),
    inertImpactAlmostNeverFire: result.application.inert.apply.accepted && result.application.inert.burningBefore === 0 && result.application.inert.burningAfter === 0 && result.application.inert.apply.ignitionAudit.ignitionCount === 0,
    rareDeterministicVulnerableIgnition: result.ignition.pass && result.ignition.sample.fires > 0 && result.ignition.sample.rate01 <= result.contract.ignition.maxProbability01.FUEL_LUBE + .003 && result.ignition.checks.structuralImpulseCannotIgnite && result.ignition.checks.inertCannotIgnite && result.ignition.checks.deterministicMechanical,
    rareMechanicalApplication: result.mechanicalIgnition.pass && result.mechanicalIgnition.checks.accepted && result.mechanicalIgnition.checks.mechanicalApplied && result.mechanicalIgnition.checks.burningStarted && result.mechanicalIgnition.checks.rngUnchanged,
    registeredFixtureTargets: result.application.middle.floodIssues.length === 0,
    legacyNormalObservedOnly: result.legacy.liveNormal.outcome === 'NORMAL_HIT' && result.legacy.normalEvent.applicationAuthority === 'OBSERVED_ALREADY_APPLIED' && result.legacy.normalEvent.damageAppliedBy === 'LEGACY_ASM_DAMAGE_PATH' && result.legacy.normalEvent.cascadeSummary.authority === 'LEGACY_PREACCOUNTED_OBSERVATION_ONLY' && !result.legacy.normalEvent.cascadeSummary.mergeDamage && result.legacy.normalEvent.cascadeSummary.rngUnchanged,
    legacyDudNoCascade: result.legacy.liveDud.outcome === 'DUD_PENETRATION' && result.legacy.dudEvent.fuzePath === 'DUD' && result.legacy.dudEvent.cascadeSummary.macroBodies === 0 && result.legacy.dudEvent.cascadeSummary.farHullExits === 0,
    scopeHeld: result.contract.exclusions.includes('GUN_LAUNCH') && result.contract.exclusions.includes('SURFACE_FIRE_CONTROL') && result.contract.persistence.damagePatchLedger === false && result.contract.persistence.operationalSnapshot === false
  };

  fs.mkdirSync(artifactDir, { recursive:true });
  fs.writeFileSync(`${artifactDir}/internal-terminal-effects-results.json`, `${JSON.stringify({ schema:'AEGIS_INTERNAL_TERMINAL_EFFECTS_BROWSER_V48_WIP12C', simulator, simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, result }, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('v48 WIP12C separates exterior breach compartments from explicit detailed interior inspection', async ({ page }) => {
  test.setTimeout(600_000);
  const consoleErrors = [], pageErrors = [], localThree = process.env.THREE_LOCAL_FILE || process.env.THREE_JS_LOCAL;
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  if (localThree) {
    await page.route('**/__wip12c_three.min.js', route => route.fulfill({ status:200, contentType:'application/javascript', body:fs.readFileSync(localThree) }));
    await page.addInitScript(() => { window.__NAVAL_THREE_URL__ = '/__wip12c_three.min.js'; });
  }
  await page.goto(`http://127.0.0.1:4173/${simulator}?view3d=1`, { waitUntil:'load' });
  await page.waitForFunction(() => window.__WIP148_3D_VIEW__?.ready === true || !!window.__WIP148_3D_VIEW__?._loadError, null, { timeout:120_000 });
  const ready = await page.evaluate(() => ({ ready:window.__WIP148_3D_VIEW__.ready, loadError:window.__WIP148_3D_VIEW__._loadError }));
  expect(ready).toEqual({ ready:true, loadError:null });
  if (await page.locator('#wip125DepartBtn').isVisible()) await page.locator('#wip125DepartBtn').click();

  const result = await page.evaluate(() => {
    const d=window.__NAVAL_SIM_DIAG__,v=window.__WIP148_3D_VIEW__;v.active=false;d.wip12bResetTerminalEvents();d.runWip113DudImpactProbe({dud:false,rangeKm:2.4,altM:12,speedMps:280});const hazard=d.wip12bInteriorHazardPresentationProbe({flood01:.58,fire01:.42,smoke01:.68});
    v.active=true;const base=performance.now();for(let i=0;i<180;i++)v.render(base+i*16.667);v.active=false;const exterior=v.internalEffectsAuditV48Wip12C(),coarse=v.shipRoot?.getObjectByName('COMPARTMENT_INTERIOR_V8'),renderState=window.get3DRenderState();
    if(!v.interiorTopologyVisible)v.toggleInteriorTopology();v.active=true;for(let i=180;i<196;i++)v.render(base+i*16.667);v.active=false;const interior=v.internalEffectsAuditV48Wip12C(),topology=v.interiorAuditV48Wip06();
    return {hazard:{spaceId:hazard.spaceId,row:hazard.state.hazards.find(h=>h.spaceId===hazard.spaceId)},exterior,interior,topology,coarse:{present:!!coarse,visibleOutside:!!exterior.interior.coarseCompartmentProxyVisible,visibleInside:!!interior.interior.coarseCompartmentProxyVisible},renderState:{holes:renderState.shipDamageVisual.scars.filter(s=>s.hole&&s.sealed<=.9).length,events:renderState.terminalImpacts},selftests:window.__CORE_SELFTEST_FAILURES__.slice()};
  });

  const event=result.renderState.events[0],checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftests.length === 0,
    openDamageExists: result.renderState.holes >= 1,
    coarseExteriorView: result.coarse.present && result.coarse.visibleOutside && result.exterior.interior.coarseVisibleThroughOpenDamage && result.exterior.interior.detailedHiddenOutsideInterior,
    detailedNotLeakingOutside: !result.exterior.interior.detailedTopologyVisible && !result.exterior.terminal.visible,
    explicitInteriorSplit: result.interior.interior.interiorMode && result.interior.interior.detailedTopologyVisible && result.interior.interior.coarseHiddenInInteriorMode && !result.coarse.visibleInside,
    detailedHazardsAndCrewMode: result.hazard.row.flood01 === .58 && result.hazard.row.fire01 === .42 && result.hazard.row.smoke01 === .68 && result.interior.interior.activeDetailedHazards >= 1 && result.interior.interior.renderedHazardVolumes >= 3,
    terminalInteriorOnly: result.exterior.terminal.hiddenOutsideInterior && result.interior.terminal.visibleInInterior && result.interior.terminal.visibilityMatchesInterior,
    macroVisuals: event.cascadeSummary.macroBodies >= 1 && result.interior.expectedMacroPaths === event.cascadeSummary.macroBodies && result.interior.terminal.macroPathVisuals === event.cascadeSummary.macroBodies && result.interior.terminal.macroBodyVisuals === event.cascadeSummary.macroBodies && result.interior.macroPathsRepresented,
    exitVisuals: result.interior.expectedExits === event.cascadeSummary.farHullExits && result.interior.terminal.farHullExitVisuals === event.cascadeSummary.farHullExits && result.interior.farHullExitsRepresented,
    topologyContained: result.topology.allSpacesRepresented && result.topology.allInteriorContained && result.topology.outsideInteriorVertices === 0,
    exteriorTransparent: result.interior.interior.exteriorTransparentInInteriorMode && result.topology.exteriorTransparent,
    presentationOnly: result.exterior.presentationOnly && !result.exterior.physicsFeedback && result.interior.presentationOnly && !result.interior.physicsFeedback && result.interior.presentationSplit
  };

  fs.mkdirSync(artifactDir, { recursive:true });
  fs.writeFileSync(`${artifactDir}/internal-terminal-effects-3d-results.json`, `${JSON.stringify({ schema:'AEGIS_INTERNAL_TERMINAL_EFFECTS_3D_BROWSER_V48_WIP12C', simulator, simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, ready, result }, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
  await page.screenshot({ path:`${artifactDir}/internal-terminal-effects-3d.png`, animations:'disabled', timeout:60_000 });
});
