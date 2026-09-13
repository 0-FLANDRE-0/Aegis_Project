const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP05.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ship-mass-ledger';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP01 compartment mass ledger, dynamic GM and cache contract', async ({ page }) => {
  test.setTimeout(120_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.shipMassLedger, null, { timeout: 30_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d._resetShipTest();
    const full = d.shipMassLedger();
    const perf = d.shipMassPerformance(20_000);
    const lightshipNodes = full.nodes.filter(node => node.category === 'LIGHTSHIP');

    const lowFwd = d.shipMassSetLoadFraction('ballast.fwd', 0).snapshot;
    const lowBoth = d.shipMassSetLoadFraction('ballast.aft', 0).snapshot;
    const cachedA = d.shipMassLedger(), cachedB = d.shipMassLedger();
    d.stepTicks(240);
    const lightDynamics = d.shipDynamics();

    d.shipMassSetLoadFraction('ballast.fwd', 1);
    const restored = d.shipMassSetLoadFraction('ballast.aft', 1).snapshot;
    d.wip114DiagSetVls(71, 96);
    const oneSm2Expended = d.shipMassLedger();
    d.wip114DiagReset();
    const final = d.shipMassLedger();
    return {
      selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(),
      full: { massKg: full.massKg, cgM: full.cgM, categories: full.categoryMassKg, nodeCount: full.nodeCount, performance: full.performance },
      lightship: { count: lightshipNodes.length, compartmentIds: lightshipNodes.map(node => node.compartmentId), massKg: lightshipNodes.reduce((sum, node) => sum + node.massKg, 0) },
      perf, lowFwd, lowBoth, cacheRebuilds: [cachedA.performance.rebuilds, cachedB.performance.rebuilds], lightDynamics,
      restored: { massKg: restored.massKg, cgM: restored.cgM }, oneSm2Expended: { massKg: oneSm2Expended.massKg }, final: { massKg: final.massKg }
    };
  });

  const checks = {
    pageLoad: !consoleErrors.length && !pageErrors.length,
    coreSelftests: result.selftestFailures.length === 0,
    fullLoadClosure: Math.abs(result.full.massKg - 9652445.6336) < 0.001,
    calibratedStart: Math.abs(result.full.cgM.z - 4.388257) < 0.0001,
    ordnanceClosure: Math.abs((result.full.categories.ORDNANCE_FIXED + result.full.categories.ORDNANCE_DYNAMIC) - 116100) < 0.001,
    compartments: result.lightship.count === 24 && new Set(result.lightship.compartmentIds).size === 24 && Math.abs(result.lightship.massKg - 7085245.6336) < 0.001,
    cacheHotPath: result.perf.rebuilds === 0 && result.perf.cacheHits >= 20000 && result.cacheRebuilds[0] === result.cacheRebuilds[1],
    ballastMassAndKg: Math.abs(result.full.massKg - result.lowFwd.massKg - 110000) < 0.001 && Math.abs(result.full.massKg - result.lowBoth.massKg - 220000) < 0.001 && result.lowBoth.cgM.z > result.full.cgM.z,
    dynamicDisplacement: Math.abs(result.lightDynamics.physics.loadedMassKg - result.lowBoth.massKg) < 0.001 && Math.abs(result.lightDynamics.pose.draftM - result.lightDynamics.physics.initialDraftM) < 0.01 && Number.isFinite(result.lightDynamics.physics.gmM),
    restoration: Math.abs(result.restored.massKg - result.full.massKg) < 0.001,
    weaponEvent: Math.abs(result.full.massKg - result.oneSm2Expended.massKg - 708) < 0.001 && Math.abs(result.final.massKg - result.full.massKg) < 0.001
  };

  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = { schema: 'AEGIS_SHIP_MASS_LEDGER_V48_WIP01_V1', simulator, simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, result };
  fs.writeFileSync(`${artifactDir}/ship-mass-ledger-results.json`, `${JSON.stringify(artifact, null, 2)}\n`);
  await page.screenshot({ path: `${artifactDir}/ship-mass-ledger-page.png`, fullPage: true });
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
