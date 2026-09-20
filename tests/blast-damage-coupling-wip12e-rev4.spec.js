const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12E_REV4_BLAST_DAMAGE_COUPLING_FIX.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/compartment-blast-wip12e-rev4';

test.use({ viewport:{ width:1600, height:900 } });

async function loadSimulator(page) {
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481232; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() =>
    Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
    window.__NAVAL_SIM_DIAG__?.wip12eCompartmentBlastDiagnostics &&
    window.__NAVAL_SIM_DIAG__?.wip12eBlastBudgetProbe,
  null, { timeout:60_000 });
  return { consoleErrors, pageErrors };
}

test('v48 WIP12E REV4 boots with deterministic generic blast fixtures and bounded budgets', async ({ page }) => {
  test.setTimeout(180_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(async () => {
    const d = window.__NAVAL_SIM_DIAG__;
    return {
      title:document.title,
      bodyText:document.body?.innerText ?? '',
      selftests:window.__CORE_SELFTEST_FAILURES__.slice(),
      mode:d.wip12eBlastMode(),
      contract:d.wip12eCompartmentBlastContract(),
      coupling:d.wip12eRev4DamageCouplingContract(),
      core:d.wip12eCompartmentBlastDiagnostics(),
      fixtures:d.wip12eBlastFixtureDiagnostics(),
      authority:d.wip12eBlastAuthorityProbe(),
      idempotence:d.wip12eBlastIdempotenceProbe(),
      budget:d.wip12eBlastBudgetProbe(),
      performance:d.wip12eBlastPerformanceProbe(128)
    };
  });

  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    title:result.title === 'AEGIS v48 WIP12E REV4 — Blast Damage Coupling & Persistent Scars',
    nonBlank:result.bodyText.trim().length > 500,
    coreSelftests:result.selftests.length === 0,
    authorityDefault:result.mode === 'COMPARTMENT_BLAST_AUTHORITY' && result.contract.defaultMode === result.mode,
    rev4Coupling:result.coupling.schema === 'AEGIS_BLAST_DAMAGE_COUPLING_V48_WIP12E_REV4' && result.coupling.persistence.authoritativeScars === 'UNTIL_RESET',
    core:result.core.pass && Object.values(result.core.checks).every(Boolean),
    fixtures:result.fixtures.pass && Object.values(result.fixtures.checks).every(Boolean),
    authority:result.authority.pass && Object.values(result.authority.checks).every(Boolean),
    idempotence:result.idempotence.pass && Object.values(result.idempotence.checks).every(Boolean),
    hardBudget:result.budget.pass && Object.values(result.budget.checks).every(Boolean),
    capHit:result.budget.breach.caps.breaches === result.contract.limits.breaches && result.budget.portalEvents.caps.portalEvents === result.contract.limits.portalEvents,
    performance:result.performance.impactTimeOnly && !result.performance.backlogCreated && result.performance.averageMs < 50,
    rng:result.performance.rngUnchanged && result.core.checks.combatRngUnchanged && result.fixtures.checks.combatRngUnchanged
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));

  fs.mkdirSync(artifactDir, { recursive:true });
  await page.screenshot({ path:path.join(artifactDir, 'boot.png'), fullPage:true });
});

test('v48 WIP12E REV4 makes one shared Kh-32 blast trace authoritative while preserving WIP12D residual physics', async ({ page }) => {
  test.setTimeout(300_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d.wip12eSetBlastMode('COMPARTMENT_BLAST_AUTHORITY');
    const run = () => {
      const flight = d.runWip107AsmMemoryCase({ label:'Kh-32', rangeKm:100, maxTimeS:300, seed:481232 });
      const event = d.wip12bTerminalEvents().find(row => row.weaponKey === 'KH32');
      const residual = d.wip12dResidualEventDiagnostics(event?.impactEventId);
      const snapshot = d.snapshot();
      const hit = snapshot.shipLastHit;
      const trace = d.wip12eBlastTrace(event?.impactEventId);
      const crew = d.v48Wip07CrewState();
      const flood = d.damageFloodSnapshotV1();
      const control = d.damageControlSnapshotV1();
      const damageVisual = d.v48Wip03DamageVisualState();
      const modules = d.wip101ModuleDamageSnapshot();
      const render = window.get3DRenderState?.() ?? null;
      return {
        flight:{ label:flight.label, durationS:flight.durationS, targetAlive:flight.targetAlive, deathReason:flight.deathReason, shipHit:flight.shipHit },
        event,
        residual,
        hit,
        trace,
        crew:{ totals:{ fit:crew.fit, injured:crew.injured, dead:crew.dead }, damage:crew.damageEvents.find(row => row.id === event?.impactEventId) ?? null },
        fire:{ burning:control.summary.burning, cells:control.cells.filter(row => row.fire > .005).map(row => ({ id:row.id, fire:row.fire, temperatureC:row.temperatureC })) },
        flood:{ openings:flood.openings.map(row => ({ id:row.id, kind:row.kind, areaM2:row.areaM2, x:row.x, y:row.y, z:row.z })) },
        damageVisual:{ scars:damageVisual.scars.map(row => ({ id:row.id, openingId:row.openingId, openingKind:row.openingKind, impactRole:row.impactRole, holeAuthority:row.holeAuthority, sourceAreaM2:row.sourceAreaM2, damagedAreaM2:row.damagedAreaM2, tearLengthM:row.tearLengthM, tearWidthM:row.tearWidthM, footprintAspect:row.footprintAspect, radius:row.radius, hole:row.hole, p:row.p })) },
        modules,
        visual:(render?.visualEvents ?? []).filter(row => row.type === 'SHIP_WARHEAD_DETONATION').at(-1) ?? null
      };
    };
    const first = run();
    const second = run();
    const dudTraceCountBefore = d.wip12eBlastTraces().length;
    const dud = d.runWip113DudImpactProbe({ dud:true, rangeKm:2.4, altM:12, speedMps:280, seed:481233 });
    const dudTraceCount = d.wip12eBlastTraces().length;
    return { first, second, dud, dudTraceCountBefore, dudTraceCount, selftests:window.__CORE_SELFTEST_FAILURES__.slice() };
  });

  const first = result.first;
  const second = result.second;
  const trace = first.trace;
  const residual = first.residual;
  const blastOpenings = first.flood.openings.filter(row => String(row.kind).startsWith('BLAST_'));
  const traceBreaches = trace?.breaches ?? [];
  const entryBlowout = traceBreaches.find(row => row.kind === 'BLAST_ENTRY_BLOWOUT');
  const surfaceRuptures = traceBreaches.filter(row => row.kind === 'BLAST_SURFACE_RUPTURE');
  const internalTears = traceBreaches.filter(row => row.kind === 'BLAST_INTERNAL_TEAR');
  const fragmentBreaches = traceBreaches.filter(row => row.kind === 'BLAST_FRAGMENT_PERFORATION');
  const totalOpenAreaM2 = traceBreaches.filter(row => row.floodEligible).reduce((sum, row) => sum + Math.max(0, Number(row.holeAreaM2) || 0), 0);
  const totalDamagedFootprintM2 = traceBreaches.reduce((sum, row) => sum + Math.max(0, Number(row.damagedAreaM2 ?? row.holeAreaM2) || 0), 0);
  const entryScars = first.damageVisual.scars.filter(row => row.openingKind === 'BLAST_ENTRY_BLOWOUT');
  const fragmentScars = first.damageVisual.scars.filter(row => row.openingKind === 'BLAST_FRAGMENT_PERFORATION' || String(row.openingKind).startsWith('RESIDUAL_FRAGMENT'));
  const capKeys = Object.keys(first.trace.caps);
  const stable = value => JSON.stringify(value);
  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    coreSelftests:result.selftests.length === 0,
    liveHit:first.flight.label === 'Kh-32' && first.flight.shipHit && !first.flight.targetAlive && first.flight.deathReason === 'NORMAL_HIT',
    wip12dFlightGolden:Math.abs(first.flight.durationS - 92.78333333333333) < 1e-9 && first.hit.impactSpeed === 991,
    wip12dGeometryGolden:first.hit.impactPart === '전방연돌' && Math.abs(first.hit.penetration - 4.318827711120478) < 1e-9 && Math.abs(first.hit.physicalPenetrationM - 22.52876902577326) < 1e-9,
    oneAuthority:first.hit.blastAuthority === 'COMPARTMENT_BLAST_AUTHORITY' && first.event.applicationAuthority === 'WIP12E_BLAST_OBSERVED_ALREADY_APPLIED' && first.event.damageAppliedBy === 'WIP12E_COMPARTMENT_BLAST_AUTHORITY',
    traceContract:trace?.schema === 'AEGIS_BLAST_TRACE_V48_WIP12E' && trace.mode === 'COMPARTMENT_BLAST_AUTHORITY' && trace.damagePacket.schema === 'AEGIS_BLAST_DAMAGE_PACKET_V48_WIP12E',
    rev4Coupling:trace.damagePacket.couplingSchema === 'AEGIS_BLAST_DAMAGE_COUPLING_V48_WIP12E_REV4' && trace.damagePacket.damageEnvelope.coreRadiusM > 20 && trace.damagePacket.damageEnvelope.fringeRadiusM > trace.damagePacket.damageEnvelope.coreRadiusM,
    realDamageBreadth:trace.damagePacket.moduleDamage.length >= 30 && trace.damagePacket.compartmentDamage.length >= 25 && trace.damagePacket.moduleDamage.some(row => row.rangeBands.includes('FRINGE')) && trace.damagePacket.compartmentDamage.some(row => row.rangeBand === 'FRINGE'),
    realConsumerDamage:first.modules['제1보일러실'] >= 80 && first.modules['CDC(전투지휘실)'] >= 80 && first.modules['제1발전실'] >= 80,
    legacyComparison:first.hit.legacyBlastComparison.totalDamage === 191 && first.hit.legacyBlastComparison.damagedParts === 17 && Math.abs(first.hit.legacyBlastComparison.powerFractionSum - 1) < 1e-12,
    sharedCrewTrace:first.crew.damage?.usedSharedBlastTrace === true && first.crew.damage?.blastTraceHash === trace.physicsHash,
    separatedCrewChannels:first.crew.damage?.affectedSpaces?.every(row => Number.isFinite(row.positiveImpulseKPaMs) && Number.isFinite(row.dynamicPressureKPa) && Number.isFinite(row.fragmentExpected)) === true,
    energyClosed:Math.abs(trace.ledger.airClosureErrorJ) <= Math.max(1e-5, trace.ledger.airBlastEnergyJ * 1e-9) && Math.abs(trace.ledger.fragmentClosureErrorJ) <= Math.max(1e-5, trace.ledger.fragmentKineticJ * 1e-9) && Math.abs(trace.ledger.totalPartitionErrorJ) <= Math.max(1e-5, trace.ledger.chemicalEnergyJ * 1e-9),
    caps:capKeys.every(key => trace.caps[key] <= ({ cells:96, portalEvents:384, surfaceLoads:512, breaches:64, timeSlices:32, ventJets:32, ignitionCandidates:24, presentationKeyframes:256 })[key]),
    entryBackblast:entryBlowout?.outwardEjection === true && entryBlowout.replacesOpeningId && entryBlowout.holeAreaM2 > first.hit.entryOpeningAreaM2 && Math.hypot(entryBlowout.position.x-first.hit.impactPoint.x, entryBlowout.position.y-first.hit.impactPoint.y, entryBlowout.position.z-first.hit.impactPoint.z) < 1e-6,
    entryTearFootprint:entryBlowout?.damagedAreaM2 > entryBlowout?.holeAreaM2 && entryBlowout?.tearLengthM > entryBlowout?.tearWidthM && entryBlowout?.footprintAspect > 1,
    entryScarAtHit:entryScars.length === 1 && entryScars[0].hole && entryScars[0].holeAuthority === 'WIP12E_ENTRY_BACKBLAST' && Math.hypot(entryScars[0].p.x-first.hit.impactPoint.x, entryScars[0].p.y-first.hit.impactPoint.y, entryScars[0].p.z-first.hit.impactPoint.z) < 1e-6,
    continuousExteriorRupture:surfaceRuptures.length >= 4 && surfaceRuptures.every(row => row.source === 'DIRECT_BLAST_FOOTPRINT_SURFACE_INTERSECTION' && row.damagedAreaM2 >= row.holeAreaM2 && row.tearLengthM >= row.tearWidthM && row.pressureFootprintRadiusM > 0),
    continuousInternalRupture:internalTears.length >= 1 && internalTears.every(row => row.internal && row.floodEligible === false && row.damagedAreaM2 >= row.holeAreaM2 && row.tearLengthM >= row.tearWidthM),
    areaAccounting:totalDamagedFootprintM2 > totalOpenAreaM2 && totalDamagedFootprintM2 > 0 && totalOpenAreaM2 > 0,
    fragmentPerforations:fragmentBreaches.length > 0 && fragmentBreaches.every(row => row.exactArea && row.holeAreaM2 > 0) && fragmentScars.some(row => row.hole),
    distributedHotProductFire:first.hit.ignitionAudit?.hotGas?.appliedCount >= 5 && first.fire.burning >= 5 && trace.damagePacket.ignitionCandidates.filter(row => row.ignite).length >= 10,
    breachFloodOnce:new Set(blastOpenings.map(row => row.id)).size === blastOpenings.length && blastOpenings.filter(row => row.kind === 'BLAST_ENTRY_BLOWOUT').length <= 1,
    vfxPayload:first.visual?.blastTraceHash === trace.physicsHash && first.visual.visualFireballRadiusM > 0 && first.visual.shockwaveRadiusM > first.visual.visualFireballRadiusM,
    wip12dResidual:residual?.bodies?.length === 4 && residual.farHullExits.length === 2 && residual.residualSupplement.accepted && residual.residualSupplement.legacyBlastReplay === false,
    residualRng:residual?.ledger?.rngUnchanged !== false && trace.rngUnchanged,
    sameSeedExact:first.trace.physicsHash === second.trace.physicsHash && first.trace.determinismHash === second.trace.determinismHash && stable(first.residual) === stable(second.residual) && stable(first.crew.totals) === stable(second.crew.totals),
    dudZero:result.dud?.dud === true && result.dud?.hit?.dud === true && result.dud?.hit?.blastSourceCount === 0 && result.dudTraceCount === 0 && result.dudTraceCount <= result.dudTraceCountBefore
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('v48 WIP12E REV4 couples bridge blasts into SPY damage and keeps more than 96 scars in 2D', async ({ page }) => {
  test.setTimeout(300_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(async () => {
    const d = window.__NAVAL_SIM_DIAG__;
    d._resetShipTest();
    d.wip12eSetBlastMode('COMPARTMENT_BLAST_AUTHORITY');
    const detonation = { x:34, y:0, z:12 };
    const entry = { x:34, y:10, z:12 };
    const packet = index => ({
      schema:'AEGIS_DAMAGE_PACKET_V48_WIP12A',
      impactEventId:`WIP12E_REV4_BRIDGE_${index}`,
      sourceProjectileId:`GENERIC_EXPLOSIVE_${index}`,
      targetEntityId:'OWN_SHIP',
      projectile:{ caliberM:.92, speedMps:900, massKg:5800 },
      path:{ start:entry, stop:detonation },
      directPenetration:[],
      penetrationCorridors:[{ start:entry, stop:detonation, caliberM:.92, kineticBeforeJ:0, kineticAfterJ:0, entryOpeningAreaM2:0, exitOpeningAreaM2:0 }],
      breaches:[],
      blast:[{ position:detonation, explosiveMassKg:500, tntEquivalentKg:500, medium:'CLOSED' }],
      structuralImpulse:[],
      warheadFragments:[{ casingMassKg:250 }],
      thermalIncendiary:[]
    });
    const rows = [];
    let firstScarIds = [];
    for (let index=1; index<=3; index++) {
      const application = d.wip12aApplyDamagePacket(packet(index), { commit:true, emitVisualEvent:true });
      const trace = d.wip12eBlastTrace(`WIP12E_REV4_BRIDGE_${index}`);
      const visual = d.v48Wip03DamageVisualState();
      if (index === 1) firstScarIds = visual.scars.map(row => row.id);
      rows.push({ application, trace, status:d.wip12eRev4DamageCouplingStatus(), scars:visual.scars.map(row => row.id) });
    }
    const panel = document.getElementById('shipDetailPanel');
    if (panel) panel.style.display = 'block';
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const twoDBeforeAge = d.wip12eRev4TwoDScarAudit();
    const beforeAge = d.v48Wip03DamageVisualState();
    d.stepTicks(Math.ceil(130 / (1 / 60)));
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const afterAge = d.v48Wip03DamageVisualState();
    const twoDAfterAge = d.wip12eRev4TwoDScarAudit();
    return { rows, firstScarIds, beforeAge, afterAge, twoDBeforeAge, twoDAfterAge, selftests:window.__CORE_SELFTEST_FAILURES__.slice() };
  });

  const [one, two, three] = result.rows;
  const twoForwardDown = !two.status.spyOperational.F1 && !two.status.spyOperational.F2;
  const threeAllDown = Object.values(three.status.spyOperational).every(value => value === false);
  const firstPersistedAfterThree = result.firstScarIds.every(id => three.scars.includes(id));
  const firstPersistedAfterAge = result.firstScarIds.every(id => result.afterAge.scars.some(row => row.id === id));
  const traceBands = trace => ({
    core:trace.damagePacket.moduleDamage.some(row => row.rangeBands.includes('CORE')),
    fringe:trace.damagePacket.moduleDamage.some(row => row.rangeBands.includes('FRINGE')) || trace.damagePacket.compartmentDamage.some(row => row.rangeBand === 'FRINGE')
  });
  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    coreSelftests:result.selftests.length === 0,
    genericPacketPath:[one, two, three].every(row => row.application.accepted && row.application.reason === 'APPLIED' && 'vlsCellDamage' in row.application),
    noUnknownTargets:[one, two, three].every(row => row.status.damageIssues.length === 0),
    coreAndFringe:[one, two, three].every(row => { const bands=traceBands(row.trace); return bands.core && bands.fringe; }),
    detailedDamage:[one, two, three].every(row => row.trace.damagePacket.moduleDamage.length >= 12 && row.trace.damagePacket.compartmentDamage.length >= 12),
    oneHitSurvives:Object.values(one.status.spyOperational).every(Boolean),
    twoHitsDisableForward:twoForwardDown && two.status.spyOperational.F3 && two.status.spyOperational.F4,
    threeHitsDisableAll:threeAllDown,
    exceedsOldRollingCap:result.beforeAge.scars.length > 96,
    firstScarsPersist:firstPersistedAfterThree && firstPersistedAfterAge,
    simulationAgeDoesNotRepair:result.afterAge.scars.length >= result.beforeAge.scars.length,
    twoDUsesAllSolvedScars:result.twoDBeforeAge?.sourceScars === result.beforeAge.scars.length && result.twoDBeforeAge.topDrawn === result.beforeAge.scars.length && result.twoDBeforeAge.sideDrawn === result.beforeAge.scars.length,
    twoDPersistsAfterAge:result.twoDAfterAge?.sourceScars === result.afterAge.scars.length && result.twoDAfterAge.topDrawn === result.afterAge.scars.length && result.twoDAfterAge.sideDrawn === result.afterAge.scars.length
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));

  fs.mkdirSync(artifactDir, { recursive:true });
  await page.screenshot({ path:path.join(artifactDir, 'bridge-three-hit-persistent-2d.png'), fullPage:true });
});

test('v48 WIP12E REV4 renders solved Kh-32 tears in exterior and interior 3D views', async ({ page }) => {
  test.setTimeout(300_000);
  const localThree = process.env.THREE_JS_PATH ? path.resolve(process.env.THREE_JS_PATH) : null;
  if (localThree) {
    expect(fs.existsSync(localThree)).toBe(true);
    await page.route('**/three.min.js', route => route.fulfill({ path:localThree, contentType:'application/javascript' }));
  }
  const errors = await loadSimulator(page);
  await page.evaluate(() => { const overlay = document.getElementById('wip125LoadoutOverlay'); if (overlay) overlay.style.display = 'none'; });
  await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d.wip12eSetBlastMode('COMPARTMENT_BLAST_AUTHORITY');
    d.runWip107AsmMemoryCase({ label:'Kh-32', rangeKm:100, maxTimeS:300, seed:481232 });
  });
  await page.evaluate(() => window.__WIP148_3D_VIEW__.open());
  await page.waitForFunction(() => {
    const v = window.__WIP148_3D_VIEW__;
    return v?.ready && v?.shipRoot && v.compartmentBlastAuditV48Wip12E?.()?.traceCount >= 1;
  }, null, { timeout:180_000 });
  const initialBlast = await page.evaluate(() => window.__WIP148_3D_VIEW__.compartmentBlastAuditV48Wip12E());
  await page.evaluate(() => window.__WIP148_3D_VIEW__.toggleInteriorTopology());
  await page.waitForFunction(() => {
    const v = window.__WIP148_3D_VIEW__;
    const blast = v?.compartmentBlastAuditV48Wip12E?.();
    const damage = v?.damageAuditV48Wip03?.();
    const remoteCut = damage?.rows?.some(row => row.openingKind === 'BLAST_SURFACE_RUPTURE' && row.actualHole && row.attached);
    return v?.interiorTopologyVisible && blast?.internalTraceVisibleOnlyInInterior && blast?.persistentInternalTearVisuals >= 1 && blast?.persistentInternalTearsVisible && remoteCut && !damage?.detailPending;
  }, null, { timeout:120_000 });

  const result = await page.evaluate(() => {
    const v = window.__WIP148_3D_VIEW__;
    const d = window.__NAVAL_SIM_DIAG__;
    return {
      ready:v.ready,
      loadError:v._loadError,
      blast:v.compartmentBlastAuditV48Wip12E(),
      damage:v.damageAuditV48Wip03(),
      interior:v.interiorAuditV48Wip06(),
      residual:d.wip12dResidualOverpenetration3DAudit(),
      runtimeFault:window.__SIM_RUNTIME_FAULT__ ?? null
    };
  });
  const exteriorRows = result.damage.rows.filter(row => row.openingKind === 'BLAST_ENTRY_BLOWOUT' || row.openingKind === 'BLAST_SURFACE_RUPTURE');
  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    rendererReady:result.ready && !result.loadError && !result.runtimeFault,
    traceBound:result.blast.traceCount >= 1 && result.blast.eventCount >= 1 && result.blast.rendererReadsSolvedTrace && result.blast.traceCapsWithinContract,
    authoritativeScars:result.blast.authoritativeEntryBlowoutScars === 1 && result.blast.authoritativeRuptureScars >= 4 && result.blast.authoritativeFragmentPerforationScars >= 1 && result.blast.allEntryBlowoutsAuthoritative && result.blast.allRuptureScarsAuthoritative && result.blast.allFragmentPerforationsAuthoritative,
    actualExteriorCuts:exteriorRows.some(row => row.openingKind === 'BLAST_ENTRY_BLOWOUT' && row.actualHole && row.attached) && exteriorRows.some(row => row.openingKind === 'BLAST_SURFACE_RUPTURE' && row.actualHole && row.attached),
    transientInteriorTrace:initialBlast.interiorCellInstances > 0 && initialBlast.interiorPortalInstances > 0,
    interiorVisible:result.interior.visible && result.interior.buttonPressed && result.blast.internalTraceVisibleOnlyInInterior && result.blast.authoritativeInternalTearScars >= 1 && result.blast.allInternalTearsAuthoritative && result.blast.persistentInternalTearVisuals === result.blast.authoritativeInternalTearScars && result.blast.persistentInternalTearsVisible && result.blast.persistentInternalTearsMatchAuthority,
    residualPresentation:result.residual?.events >= 1 && result.residual?.terminal?.allShipLocalEventsRepresented
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));

  fs.mkdirSync(artifactDir, { recursive:true });
  await page.screenshot({ path:path.join(artifactDir, 'kh32-interior-tears.png'), fullPage:true });
});
