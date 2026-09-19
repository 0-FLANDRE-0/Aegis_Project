const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12E.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/compartment-blast-wip12e';

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

test('v48 WIP12E boots with deterministic generic blast fixtures and bounded budgets', async ({ page }) => {
  test.setTimeout(180_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    return {
      title:document.title,
      bodyText:document.body?.innerText ?? '',
      selftests:window.__CORE_SELFTEST_FAILURES__.slice(),
      mode:d.wip12eBlastMode(),
      contract:d.wip12eCompartmentBlastContract(),
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
    title:result.title === 'AEGIS v48 WIP12E — Generic Compartment Blast Authority',
    nonBlank:result.bodyText.trim().length > 500,
    coreSelftests:result.selftests.length === 0,
    authorityDefault:result.mode === 'COMPARTMENT_BLAST_AUTHORITY' && result.contract.defaultMode === result.mode,
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

test('v48 WIP12E makes one shared Kh-32 blast trace authoritative while preserving WIP12D residual physics', async ({ page }) => {
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
      const render = window.get3DRenderState?.() ?? null;
      return {
        flight:{ label:flight.label, durationS:flight.durationS, targetAlive:flight.targetAlive, deathReason:flight.deathReason, shipHit:flight.shipHit },
        event,
        residual,
        hit,
        trace,
        crew:{ totals:{ fit:crew.fit, injured:crew.injured, dead:crew.dead }, damage:crew.damageEvents.at(-1) ?? null },
        flood:{ openings:flood.openings.map(row => ({ id:row.id, kind:row.kind, areaM2:row.areaM2, x:row.x, y:row.y, z:row.z })) },
        visual:(render?.visualEvents ?? []).filter(row => row.type === 'SHIP_WARHEAD_DETONATION').at(-1) ?? null
      };
    };
    const first = run();
    const second = run();
    const dud = d.runWip113DudImpactProbe({ dud:true, rangeKm:2.4, altM:12, speedMps:280, seed:481233 });
    const dudTraceCount = d.wip12eBlastTraces().length;
    return { first, second, dud, dudTraceCount, selftests:window.__CORE_SELFTEST_FAILURES__.slice() };
  });

  const first = result.first;
  const second = result.second;
  const trace = first.trace;
  const residual = first.residual;
  const ruptureOpenings = first.flood.openings.filter(row => row.kind === 'BLAST_SURFACE_RUPTURE');
  const traceBreaches = trace?.breaches ?? [];
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
    legacyComparison:first.hit.legacyBlastComparison.totalDamage === 191 && first.hit.legacyBlastComparison.damagedParts === 17 && Math.abs(first.hit.legacyBlastComparison.powerFractionSum - 1) < 1e-12,
    sharedCrewTrace:first.crew.damage?.usedSharedBlastTrace === true && first.crew.damage?.blastTraceHash === trace.physicsHash,
    separatedCrewChannels:first.crew.damage?.affectedSpaces?.every(row => Number.isFinite(row.positiveImpulseKPaMs) && Number.isFinite(row.dynamicPressureKPa) && Number.isFinite(row.fragmentExpected)) === true,
    energyClosed:Math.abs(trace.ledger.airClosureErrorJ) <= Math.max(1e-5, trace.ledger.airBlastEnergyJ * 1e-9) && Math.abs(trace.ledger.totalPartitionErrorJ) <= Math.max(1e-5, trace.ledger.chemicalEnergyJ * 1e-9),
    caps:capKeys.every(key => trace.caps[key] <= ({ cells:96, portalEvents:384, surfaceLoads:512, breaches:64, timeSlices:32, ventJets:32, presentationKeyframes:256 })[key]),
    breachFloodOnce:traceBreaches.length > 0 && ruptureOpenings.length === traceBreaches.filter(row => row.floodEligible).length && new Set(ruptureOpenings.map(row => row.id)).size === ruptureOpenings.length,
    vfxPayload:first.visual?.blastTraceHash === trace.physicsHash && first.visual.visualFireballRadiusM > 0 && first.visual.shockwaveRadiusM > first.visual.visualFireballRadiusM,
    wip12dResidual:residual?.bodies?.length === 4 && residual.farHullExits.length === 2 && residual.residualSupplement.accepted && residual.residualSupplement.legacyBlastReplay === false,
    residualRng:residual?.ledger?.rngUnchanged !== false && trace.rngUnchanged,
    sameSeedExact:first.trace.physicsHash === second.trace.physicsHash && first.trace.determinismHash === second.trace.determinismHash && stable(first.residual) === stable(second.residual) && stable(first.crew.totals) === stable(second.crew.totals),
    dudZero:result.dud?.cascade?.macroBodies?.length === 0 && result.dud?.cascade?.farHullExits?.length === 0 && result.dudTraceCount === 0
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
