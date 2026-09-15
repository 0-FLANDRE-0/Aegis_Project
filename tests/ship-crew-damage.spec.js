const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP08.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ship-crew-damage';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP07 spatial crew routing, casualties and medical evacuation', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() =>
    Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
    window.__NAVAL_SIM_DIAG__?.runV48Wip07CrewDamageProbe &&
    window.__NAVAL_SIM_DIAG__?.v48Wip07CrewReadPerformance,
  null, { timeout: 30_000 });

  // Damage-control UI is materialized after the pre-sail overlay is dismissed.
  await page.locator('#wip125DepartBtn').click();
  await page.waitForFunction(() =>
    document.getElementById('damageControlPanelV1') &&
    document.getElementById('damageControlToggleV1') &&
    document.getElementById('external3DInteriorBtn'),
  null, { timeout: 10_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    const model = d.v48Wip07CrewDamageModel();
    const live = d.v48Wip07CrewState();
    const route = d.v48Wip07Route('l1.engine.aft', 's5.bridge.pilothouse', 'DAMAGE_CONTROL');
    const stretcherRoute = d.v48Wip07Route('s5.bridge.pilothouse', 'main.infirmary', 'STRETCHER');
    const probe = d.runV48Wip07CrewDamageProbe({ readCount: 20_000 });
    const authorityBefore = JSON.stringify({
      crew: d.v48Wip07CrewState(),
      topology: d.v48Wip06InteriorState(),
      flood: d.damageFloodSnapshotV1(),
      control: d.damageControlSnapshotV1()
    });
    const perfBefore = d.v48Wip07CrewReadPerformance(1);
    for (let i = 0; i < 64; i++) window.get3DRenderState();
    const perfAfter = d.v48Wip07CrewReadPerformance(20_000);
    const authorityAfter = JSON.stringify({
      crew: d.v48Wip07CrewState(),
      topology: d.v48Wip06InteriorState(),
      flood: d.damageFloodSnapshotV1(),
      control: d.damageControlSnapshotV1()
    });
    return {
      selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(),
      model, live, route, stretcherRoute, probe, perfBefore, perfAfter,
      renderReadOnly: authorityBefore === authorityAfter,
      ui: {
        damageControl: !!document.getElementById('damageControlPanelV1'),
        interiorButton: !!document.getElementById('external3DInteriorBtn')
      }
    };
  });

  const checks = {
    pageLoad: !consoleErrors.length && !pageErrors.length,
    coreSelftests: result.selftestFailures.length === 0,
    schema: result.model.schema === 'AEGIS_CREW_ROUTING_DAMAGE_V48_WIP07' &&
      result.live.contract === 'AUTHORITATIVE_SPATIAL_CREW_AND_CASUALTY_STATE',
    exactRoster: result.live.total === 310 && result.live.groups.length === 310 &&
      result.live.groups.every(g => g.spaceId && [g.position.x, g.position.y, g.position.z].every(Number.isFinite)),
    graphRouting: result.route?.spaces.length > 4 && result.route?.segments.length === result.route.spaces.length - 1,
    stretcherRouting: result.stretcherRoute?.spaces.length > 4 && result.probe.checks.stretcherRoute,
    automaticPolicy: result.model.policy.automaticDutyRouting &&
      result.model.policy.automaticDamageControlRouting &&
      result.model.policy.automaticMedicalEvacuation &&
      result.model.policy.individualDoorMicromanagement === false,
    boundedCadence: result.model.movementHz === 5 && result.model.physiologyHz === 1 &&
      result.model.routeInvalidationHz === 1 && result.probe.checks.fixedCadence,
    eventDrivenDamage: result.probe.checks.impactAccepted && result.probe.checks.eventOnce &&
      result.probe.performance.damageEvaluations === 1 && result.probe.performance.blastGraphEvaluations === 1,
    blastFragmentPenetrator: result.probe.checks.compartmentPropagation &&
      result.probe.checks.penetratorSpaces && result.probe.damage.sourceSpaceIds.includes('upper.cic.lower'),
    mixedCasualties: result.probe.totals.dead > 0 && result.probe.totals.injured > 0,
    medicalEvacuation: result.probe.checks.medicalRouting && result.probe.medical.routes > 0 &&
      result.probe.medical.routes <= result.model.stretcherTeams,
    cachedReadPath: result.probe.checks.cachedReads && result.perfAfter.snapshotRebuilds === 0 &&
      result.perfAfter.routeEvaluations === 0 && result.perfAfter.damageEvaluations === 0,
    presentationOnly: result.live.renderContract === 'PRESENTATION_ONLY_CREW_SNAPSHOT' &&
      result.probe.checks.renderReadOnly && result.renderReadOnly,
    uiPresent: result.ui.damageControl && result.ui.interiorButton
  };

  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = {
    schema: 'AEGIS_CREW_ROUTING_DAMAGE_V48_WIP07_BROWSER_V1',
    simulator,
    simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),
    checks, consoleErrors, pageErrors, result
  };
  fs.writeFileSync(`${artifactDir}/ship-crew-damage-results.json`, `${JSON.stringify(artifact, null, 2)}\n`);
  await page.screenshot({ path: `${artifactDir}/ship-crew-damage-page.png`, fullPage: true });
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
