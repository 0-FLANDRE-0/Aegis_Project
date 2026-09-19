const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12C.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/terminal-ballistics-wip12a';

test.use({ viewport:{ width:1600, height:900 } });

test('v48 WIP12A runs deterministic event-driven terminal-ballistics fixtures and damage contracts', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481200; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.wip12aTerminalDiagnostics, null, { timeout:45_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    const contract = d.wip12aTerminalBallisticsContract();
    const projectiles = d.wip12aDiagnosticProjectiles();
    const diagnostic = d.wip12aTerminalDiagnostics();
    const scaleRuns = {};
    for (const scale of [1, 8, 16]) {
      d.setTimeScale(scale);
      scaleRuns[scale] = d.wip12aRunFixture('TEST_127_SAP', { impactEventId:'WIP12A_TIMESCALE_EXACT' });
    }
    d.setTimeScale(64);
    const overload64x = d.wip12aPerformance(4096);
    d.setTimeScale(1);
    const idempotence = d.wip12aDamagePacketIdempotence();
    d._resetShipTest();
    const crewBefore = d.v48Wip07CrewState();
    const beforeConsumers = {
      openings:d.damageFloodSnapshotV1().openings.length,
      structure:d.v48Wip03StructuralState().performance.impactEvaluations,
      crew:{ fit:crewBefore.fit, injured:crewBefore.injured, dead:crewBefore.dead, damageEvents:crewBefore.damageEvents.length }
    };
    const consumerTrace = d.wip12aRunFixture('TEST_127_SAP', { impactEventId:'WIP12A_CONSUMER_CONNECTIONS' });
    const firstConsumerApply = d.wip12aApplyDamagePacket(consumerTrace.damagePacket, { commit:true });
    const crewAfter = d.v48Wip07CrewState();
    const afterConsumers = {
      openings:d.damageFloodSnapshotV1().openings.length,
      structure:d.v48Wip03StructuralState().performance.impactEvaluations,
      crew:{ fit:crewAfter.fit, injured:crewAfter.injured, dead:crewAfter.dead, damageEvents:crewAfter.damageEvents.length },
      modules:d.wip101ModuleDamageSnapshot()
    };
    const duplicateConsumerApply = d.wip12aApplyDamagePacket(consumerTrace.damagePacket, { commit:true });
    d._resetShipTest();
    return { contract, projectiles, diagnostic, scaleRuns, overload64x, idempotence, consumers:{before:beforeConsumers,after:afterConsumers,first:firstConsumerApply,duplicate:duplicateConsumerApply}, selftests:window.__CORE_SELFTEST_FAILURES__.slice(), debug:d.debugLogSnapshot() };
  });

  const ids = Object.keys(result.projectiles);
  const firstScale = JSON.stringify(result.scaleRuns[1]);
  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftests.length === 0 && result.debug.some(line => String(line?.text ?? line).includes('TERMINAL-BALLISTICS-V48-WIP12A SELFTEST PASS')),
    contract: result.contract.schema === 'AEGIS_TERMINAL_BALLISTICS_V48_WIP12A' && result.contract.coordinateSpace === 'SHIP_LOCAL_METRES' && result.contract.liveAsmMigration === false && result.contract.persistentDamagePatch === false,
    sixDiagnosticProjectiles: ids.length === 6 && ids.every(id => id.startsWith('TEST_') && result.projectiles[id].sourceClass === 'DIAGNOSTIC_SIM_TUNED'),
    diagnostic: result.diagnostic.pass && Object.values(result.diagnostic.checks).every(Boolean),
    everyFixtureBoundaryEnvelope: ids.every(id => result.diagnostic.boundaryEnvelopes[id].pass && Object.values(result.diagnostic.boundaryEnvelopes[id].checks).every(Boolean)),
    independentAxes: result.diagnostic.shatter.boundaryResults.some(row => row.traversalOutcome === 'PERFORATED' && row.projectileFailure === 'SHATTERED'),
    emptyAndFuzeTime: result.diagnostic.checks.emptyPreservesProjectile && result.diagnostic.checks.timeBasedFuzeInEmpty && result.diagnostic.checks.fuzeEventArbitration,
    eventDrivenDirectionRequery: result.diagnostic.eventRequery.pass && result.diagnostic.eventRequery.surfaceIds.join(',') === 'W12A_REQUERY_FIRST,W12A_REQUERIED_CONTACT',
    materialAndCrewSeparated: result.diagnostic.checks.materialVolumeRequiresExplicitMatter && result.diagnostic.checks.crewExposureZeroResistance,
    damageChannels: result.diagnostic.checks.fixtureDamageChannels && result.diagnostic.runs.TEST_30_HEI.damagePacket.thermalIncendiary.length === 1,
    aramidChannelsOnly: result.diagnostic.aramid.pass && result.diagnostic.aramid.checks.directWorkUnchanged && result.diagnostic.aramid.checks.fragmentReduced && result.diagnostic.aramid.checks.rearSpallReduced,
    unsupportedArmorRejected: result.diagnostic.unsupported.terminationReason === 'UNSUPPORTED_SOLVER',
    damagePacketIdempotence: result.idempotence.pass && Object.values(result.idempotence.checks).every(Boolean),
    existingConsumersConnected: result.consumers.first.accepted && !result.consumers.duplicate.accepted && result.consumers.after.openings > result.consumers.before.openings && result.consumers.after.structure === result.consumers.before.structure + 1 && result.consumers.after.crew.damageEvents === result.consumers.before.crew.damageEvents + 1 && result.consumers.after.modules['VLS(전)'] > 0 && result.consumers.first.parts.some(part => part.name === 'GEN_1' && part.dmg > 0),
    timeScaleExact: [8, 16].every(scale => JSON.stringify(result.scaleRuns[scale]) === firstScale),
    overload64xMeasured: result.overload64x.iterations === 4096 && result.overload64x.events > 0 && result.overload64x.queries > 0 && Number.isFinite(result.overload64x.totalMs) && Number.isFinite(result.overload64x.perImpactMs) && result.overload64x.perImpactMs < 10
  };

  fs.mkdirSync(artifactDir, { recursive:true });
  fs.writeFileSync(`${artifactDir}/terminal-ballistics-results.json`, `${JSON.stringify({ schema:'AEGIS_TERMINAL_BALLISTICS_BROWSER_V48_WIP12A', simulator, simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, result }, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('v48 WIP12A legacy ASM adapter remains exact and consumes no combat RNG', async ({ page }) => {
  test.setTimeout(120_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481201; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() => window.__NAVAL_SIM_DIAG__?.wip12aLegacyAsmCompat, null, { timeout:45_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__, events = [{distanceM:3,resistanceMJ:1.20},{distanceM:7,resistanceMJ:1.00},{distanceM:11,resistanceMJ:1.00}], reference = d.runWip100PenetrationDiagnostics();
    const cases = {
      kh32NormalM4:d.wip12aLegacyAsmCompat('Kh-32',{impactSpeedMps:1400,incidenceCos:1,initialResistance:.90,events}),
      kh35NormalSubsonic:d.wip12aLegacyAsmCompat('Kh-35U',{impactSpeedMps:280,incidenceCos:1,initialResistance:.90,events}),
      kh32Oblique60:d.wip12aLegacyAsmCompat('Kh-32',{impactSpeedMps:1400,incidenceCos:Math.cos(Math.PI/3),initialResistance:.90,events}),
      kh32Oblique80:d.wip12aLegacyAsmCompat('Kh-32',{impactSpeedMps:1400,incidenceCos:Math.cos(80*Math.PI/180),initialResistance:.90,events})
    };
    const stripped = Object.fromEntries(Object.entries(reference).map(([key,value]) => { const {label,impactSpeedMps,...penetration}=value; return [key,penetration]; }));
    return { reference:stripped, cases, terminalDiagnostic:d.wip12aTerminalDiagnostics().legacy, selftests:window.__CORE_SELFTEST_FAILURES__.slice() };
  });

  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftests.length === 0,
    allCasesExact: Object.keys(result.reference).every(key => JSON.stringify(result.reference[key]) === JSON.stringify(result.cases[key].penetration)),
    rngUnchanged: Object.values(result.cases).every(row => row.rngUnchanged && row.rngBefore === row.rngAfter),
    diagnosticParity: JSON.stringify(result.terminalDiagnostic.direct) === JSON.stringify(result.terminalDiagnostic.wrapped.penetration) && result.terminalDiagnostic.wrapped.rngUnchanged
  };

  fs.mkdirSync(artifactDir, { recursive:true });
  fs.writeFileSync(`${artifactDir}/legacy-asm-compat-results.json`, `${JSON.stringify({ schema:'AEGIS_LEGACY_ASM_COMPAT_BROWSER_V48_WIP12A', simulator, checks, consoleErrors, pageErrors, result }, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
