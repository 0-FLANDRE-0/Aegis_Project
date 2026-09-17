const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP11A.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ship-impact-penetration';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP02 impact energy, through-hull openings, flooding and impulse contract', async ({ page }) => {
  test.setTimeout(120_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.runV48Wip02ImpactProbe, null, { timeout: 30_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d._resetShipTest();
    d.setShipMotionTest(0, 0);
    const kh32a = d.runV48Wip02ImpactProbe('Kh-32');
    const kh32b = d.runV48Wip02ImpactProbe('Kh-32');
    const kh35 = d.runV48Wip02ImpactProbe('Kh-35U');
    const committed = d.runV48Wip02ImpactProbe('Kh-32', { commit: true, dud: true, zM: -1 });
    const before = d.damageFloodSnapshotV1();
    const eventStep = committed.committed.applied.step;
    d.stepTicks(240);
    const after = d.damageFloodSnapshotV1();
    const dynamics = d.shipDynamics();
    return {
      selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(),
      kh32a, kh32b, kh35, committed, eventStep,
      before: { openings: before.openings, summary: before.summary },
      after: { openings: after.openings, summary: after.summary },
      dynamics, lastImpulse: d.v48Wip02LastImpulse()
    };
  });

  const i32 = result.kh32a.impact, i35 = result.kh35.impact;
  const shellOpenings = result.before.openings.filter(opening => opening.kind === 'SHELL_ENTRY' || opening.kind === 'SHELL_EXIT');
  const entry = shellOpenings.find(opening => opening.kind === 'SHELL_ENTRY');
  const exit = shellOpenings.find(opening => opening.kind === 'SHELL_EXIT');
  const checks = {
    pageLoad: !consoleErrors.length && !pageErrors.length,
    coreSelftests: result.selftestFailures.length === 0,
    kineticIdentity: Math.abs(i32.rawKineticEnergyMJ - 5458.9136) < 1e-6 && Math.abs(i32.impactMomentumNs - 7_957_600) < 1e-6,
    kh32ThroughHull: i32.throughHull && i32.exitPointLocal.y < 0 && i32.exitEnergyMJ > 0 && i32.physicalPenetrationM >= i32.hullExitDistanceM,
    kh35StopsInside: !i35.throughHull && i35.openings.exitAreaM2 === 0 && i35.physicalPenetrationM < i35.hullExitDistanceM,
    deterministicGeometry: JSON.stringify(result.kh32a.impact) === JSON.stringify(result.kh32b.impact),
    entryExitOpenings: shellOpenings.length === 2 && entry.areaM2 > exit.areaM2 && exit.areaM2 > 0 && Math.abs(entry.areaM2 - result.committed.impact.openings.entryAreaM2) < 1e-9 && Math.abs(exit.areaM2 - result.committed.impact.openings.exitAreaM2) < 1e-9,
    belowWaterFlooding: result.after.summary.waterM3 > 1 && result.after.summary.wetCells >= 2 && result.after.summary.netM3s > 0,
    impulseApplied: result.committed.committed.applied.magnitudeNs > 0 && result.committed.committed.applied.delta.swayMps < 0 && Math.abs(result.committed.committed.applied.delta.rollRateRadS) > 0,
    eventOnlyImpulse: result.lastImpulse.step === result.eventStep && result.lastImpulse.magnitudeNs === result.committed.committed.applied.magnitudeNs && result.dynamics.physics.lastImpactImpulse.step === result.eventStep,
    dynamicMassCoupling: result.dynamics.physics.waterMassKg > 0 && result.dynamics.physics.massKg > result.dynamics.physics.loadedMassKg && Number.isFinite(result.dynamics.physics.gmM)
  };

  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = { schema: 'AEGIS_SHIP_IMPACT_V48_WIP02_V1', simulator, simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, result };
  fs.writeFileSync(`${artifactDir}/ship-impact-results.json`, `${JSON.stringify(artifact, null, 2)}\n`);
  await page.screenshot({ path: `${artifactDir}/ship-impact-page.png`, fullPage: true });
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
