const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v37.1_WIP11.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ciws-b2-maneuver';
const results = {
  schema: 'AEGIS_CIWS_B2_MANEUVER_V1',
  simulator,
  simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),
  checks: {},
  consoleErrors: [],
  pageErrors: []
};

test.use({ viewport: { width: 1600, height: 900 } });

test.afterEach(({}, testInfo) => {
  fs.mkdirSync(artifactDir, { recursive: true });
  results.completedAt = new Date().toISOString();
  results.pass = Object.values(results.checks).every(row => row.pass) && !results.consoleErrors.length && !results.pageErrors.length;
  results.testStatus = testInfo.status;
  fs.writeFileSync(`${artifactDir}/ciws-b2-results.json`, `${JSON.stringify(results, null, 2)}\n`);
  const failures = Object.entries(results.checks).filter(([, value]) => !value.pass).map(([name, value]) => ({ name, value }));
  console.log('CIWS_B2_FAILED_CHECKS ' + JSON.stringify(failures));
});

test('CIWS Closure B2 acceleration and maneuver prediction', async ({ page }) => {
  test.setTimeout(120_000);
  page.on('console', msg => { if (msg.type() === 'error') results.consoleErrors.push(msg.text()); });
  page.on('pageerror', err => results.pageErrors.push(err.stack || String(err)));

  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.ciwsB2Maneuver && window.__NAVAL_SIM_DIAG__?.ciwsB1Closure, null, { timeout: 30_000 });

  const startup = await page.evaluate(() => ({
    failures: window.__CORE_SELFTEST_FAILURES__.slice(),
    logs: window.__NAVAL_SIM_DIAG__.debugLogSnapshot()
  }));
  results.checks.pageLoad = { pass: !results.consoleErrors.length && !results.pageErrors.length };
  results.checks.selftests = {
    pass: !startup.failures.length && startup.logs.some(x => String(x?.text ?? x).includes('CORE SELFTEST PASS')),
    failures: startup.failures
  };

  const audits = await page.evaluate(() => [1, 8, 16].map(timeScale => ({
    timeScale,
    audit: window.__NAVAL_SIM_DIAG__.ciwsB2Maneuver.audit({ timeScale })
  })));
  const reference = JSON.stringify(audits[0].audit);
  results.checks.fixedStepDeterminism = {
    pass: audits.every(row => JSON.stringify(row.audit) === reference),
    audits
  };

  const audit = audits[0].audit;
  results.checks.straightTrackNoiseGuard = {
    pass: audit.straight.accelMps2 < 3 && !audit.straight.maneuvering,
    result: audit.straight
  };
  results.checks.maneuverEstimate = {
    pass: audit.maneuver.estimatedAyMps2 > 12 && audit.maneuver.accelMps2 <= 90.01 &&
      audit.maneuver.jerkMps3 <= 450.01 && audit.maneuver.maneuvering,
    result: audit.maneuver
  };
  results.checks.predictionHookup = {
    pass: audit.prediction.enabled && audit.prediction.horizonS > 0 && audit.prediction.horizonS <= 3.2 &&
      audit.prediction.interceptShiftM > 1,
    result: audit.prediction
  };
  results.checks.boundedCoastAndRange = {
    pass: audit.coast.bounded && audit.coast.afterAccelMps2 < audit.coast.beforeAccelMps2 &&
      !audit.rangeGate.enabled && audit.rangeGate.horizonS === 0 && audit.rangeGate.rangeM > audit.rangeGate.limitM,
    coast: audit.coast,
    rangeGate: audit.rangeGate
  };

  const banned = new Set(['enemyId', 'truthRef', 'trackingTarget', 'objectId']);
  const leaked = [];
  const scan = (value, path = '$') => {
    if (!value || typeof value !== 'object') return;
    for (const [key, child] of Object.entries(value)) {
      if (banned.has(key)) leaked.push(`${path}.${key}`);
      scan(child, `${path}.${key}`);
    }
  };
  scan(audit);
  results.checks.diagnosticBoundary = { pass: leaked.length === 0, leaked };

  const liveSensor = await page.evaluate(() => window.__NAVAL_SIM_DIAG__.ciwsB2Maneuver.liveSensorAudit());
  results.checks.liveLocalRfNoiseGuard = {
    pass: liveSensor.straight.valid && liveSensor.straight.localHits >= 16 &&
      liveSensor.straight.accelMps2 < 12 && !liveSensor.straight.maneuvering &&
      liveSensor.straight.lastSource === 'LOCAL_RF',
    result: liveSensor.straight
  };
  results.checks.liveLocalRfManeuver = {
    pass: liveSensor.maneuver.valid && liveSensor.maneuver.localHits >= 16 &&
      liveSensor.maneuver.estimatedAyMps2 > 8 && liveSensor.maneuver.accelMps2 <= 90.01 &&
      liveSensor.maneuver.maneuvering && liveSensor.maneuver.lastSource === 'LOCAL_RF',
    result: liveSensor.maneuver
  };

  expect(Object.entries(results.checks).filter(([, value]) => !value.pass)).toEqual([]);
  expect(results.consoleErrors).toEqual([]);
  expect(results.pageErrors).toEqual([]);
});
