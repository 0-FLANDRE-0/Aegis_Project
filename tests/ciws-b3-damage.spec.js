const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP06.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ciws-b3-damage';
const results = {
  schema: 'AEGIS_CIWS_B3_CONTINUOUS_DAMAGE_V1',
  simulator,
  simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),
  seed: 3711201,
  checks: {},
  consoleErrors: [],
  pageErrors: []
};

test.use({ viewport: { width: 1600, height: 900 } });

test.afterEach(({}, testInfo) => {
  fs.mkdirSync(artifactDir, { recursive: true });
  results.completedAt = new Date().toISOString();
  results.testStatus = testInfo.status;
  results.pass = Object.values(results.checks).every(row => row.pass) &&
    !results.consoleErrors.length && !results.pageErrors.length;
  fs.writeFileSync(`${artifactDir}/ciws-b3-results.json`, `${JSON.stringify(results, null, 2)}\n`);
  const failures = Object.entries(results.checks)
    .filter(([, value]) => !value.pass)
    .map(([name, value]) => ({ name, value }));
  console.log('CIWS_B3_FAILED_CHECKS ' + JSON.stringify(failures));
});

test('CIWS Closure B3 continuous partial-damage performance', async ({ page }) => {
  test.setTimeout(150_000);
  page.on('console', msg => { if (msg.type() === 'error') results.consoleErrors.push(msg.text()); });
  page.on('pageerror', err => results.pageErrors.push(err.stack || String(err)));

  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() =>
    Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
    window.__NAVAL_SIM_DIAG__?.ciwsB3Damage &&
    window.__NAVAL_SIM_DIAG__?.ciwsB1Closure,
  null, { timeout: 30_000 });

  const startup = await page.evaluate(() => ({
    failures: window.__CORE_SELFTEST_FAILURES__.slice(),
    logs: window.__NAVAL_SIM_DIAG__.debugLogSnapshot()
  }));
  results.checks.pageLoadAndSelftest = {
    pass: !startup.failures.length &&
      startup.logs.some(x => String(x?.text ?? x).includes('CORE SELFTEST PASS')) &&
      !results.consoleErrors.length && !results.pageErrors.length,
    startup
  };

  const audit = await page.evaluate(() => window.__NAVAL_SIM_DIAG__.ciwsB3Damage.audit());
  const gun = audit.mounts.find(x => x.type === 'GUN').rows;
  const ram = audit.mounts.find(x => x.type === 'RAM').rows;
  const strictDown = (rows, key) => rows.slice(1).every((row, i) => row.performance[key] < rows[i].performance[key]);
  const strictUp = (rows, key) => rows.slice(1).every((row, i) => row.performance[key] > rows[i].performance[key]);

  results.checks.damageCurveEndpoints = {
    pass: audit.destroyThresholdPct === 80 &&
      gun[0].performance.health === 1 && ram[0].performance.health === 1 &&
      gun.at(-1).performance.health === 0 && ram.at(-1).performance.health === 0 &&
      audit.sensorModel?.searchRangeKm === 15 && audit.sensorModel?.trackRangeKm === 10 &&
      audit.sensorModel?.cueTrackRangeKm === 15 &&
      gun[0].performance.searchRangeKm === 15 && ram[0].performance.searchRangeKm === 15 &&
      gun[0].performance.trackRangeKm === 10 && ram[0].performance.trackRangeKm === 10 &&
      gun[0].performance.fireRateRps === 75 && ram[0].performance.reloadIntervalS === 2 &&
      !gun.at(-1).performance.operational && !ram.at(-1).performance.operational,
    audit
  };
  const commonSensorKeys = ['searchRangeKm', 'trackRangeKm', 'cueTrackRangeKm',
    'trackingSigmaFactor', 'dwellFactor', 'detectionProbabilityFactor'];
  results.checks.commonBlock1BSensorParity = {
    pass: gun.every((row, i) => commonSensorKeys.every(key =>
      Math.abs(row.performance[key] - ram[i].performance[key]) < 1e-12)),
    gun: gun.map(row => ({ damagePct: row.damagePct,
      sensor: Object.fromEntries(commonSensorKeys.map(key => [key, row.performance[key]])) })),
    ram: ram.map(row => ({ damagePct: row.damagePct,
      sensor: Object.fromEntries(commonSensorKeys.map(key => [key, row.performance[key]])) }))
  };
  results.checks.phalanxContinuousDegradation = {
    pass: strictDown(gun, 'searchRangeKm') && strictDown(gun, 'trackRangeKm') &&
      strictDown(gun, 'maxTurretRateRadS') && strictDown(gun, 'turretAccelRadS2') &&
      strictDown(gun, 'fireRateRps') && strictUp(gun, 'trackingSigmaFactor') &&
      gun[0].oneSecondRounds === 75 && gun[1].oneSecondRounds > gun[2].oneSecondRounds &&
      gun[2].oneSecondRounds > 0 && gun[3].oneSecondRounds === 0,
    rows: gun
  };
  results.checks.seaRamContinuousDegradation = {
    pass: strictDown(ram, 'searchRangeKm') && strictDown(ram, 'trackRangeKm') &&
      strictDown(ram, 'maxTurretRateRadS') && strictDown(ram, 'maxElevationRateRadS') &&
      strictUp(ram, 'trackingSigmaFactor') && strictUp(ram, 'reloadIntervalS'),
    rows: ram
  };

  const leaked = [];
  const banned = new Set(['enemyId', 'truthRef', 'trackingTarget', 'objectId']);
  const scan = (value, path = '$') => {
    if (!value || typeof value !== 'object') return;
    for (const [key, child] of Object.entries(value)) {
      if (banned.has(key)) leaked.push(`${path}.${key}`);
      scan(child, `${path}.${key}`);
    }
  };
  scan(audit);
  results.checks.diagnosticTruthBoundary = { pass: leaked.length === 0, leaked };

  const run = (method, ...args) =>
    page.evaluate(([method, args]) => window.__NAVAL_SIM_DIAG__.ciwsB1Closure[method](...args), [method, args]);

  await run('prepare', { mount: 'GUN', seed: results.seed, damage: 40, rangeKm: 2.4 });
  let damagedMeasurement = null;
  for (let i = 0; i < 120; i++) {
    damagedMeasurement = (await run('stepCiws', 0.1)).snapshot;
    if (damagedMeasurement.mounts[0].localTrack?.damageSigmaFactor > 1) break;
  }
  const dm = damagedMeasurement.mounts[0];
  results.checks.liveDamagedMeasurementPath = {
    pass: dm.performance.health > 0 && dm.performance.health < 1 &&
      dm.performance.searchRangeKm < 15 &&
      dm.localTrack?.damageSigmaFactor > 1 &&
      dm.localTrack?.damagePdFactor < 1 &&
      dm.localTrack?.effectiveRangeKm <= dm.performance.cueTrackRangeKm + 1e-9,
    snapshot: damagedMeasurement
  };

  let gunDamaged = damagedMeasurement;
  for (let i = 0; i < 120 && gunDamaged.mounts[0].spent === 0; i++)
    gunDamaged = (await run('stepCiws', 0.1)).snapshot;
  await run('prepare', { mount: 'RAM', seed: results.seed + 1, damage: 40, rangeKm: 6.0 });
  let ramDamaged = null;
  for (let i = 0; i < 160; i++) {
    ramDamaged = (await run('stepCiws', 0.1)).snapshot;
    if (ramDamaged.mounts[1].spent > 0) break;
  }
  results.checks.partialDamageStillOperates = {
    pass: gunDamaged.mounts[0].spent > 0 &&
      ramDamaged.mounts[1].spent > 0 && ramDamaged.ramLaunched > 0 &&
      ramDamaged.mounts[1].performance.reloadIntervalS > 2,
    gunDamaged,
    ramDamaged
  };

  await run('prepare', { mount: 'GUN', seed: results.seed + 2, damage: 80, rangeKm: 2.0 });
  const destroyed = (await run('stepCiws', 5)).snapshot;
  results.checks.destroyedMountHardStop = {
    pass: destroyed.mounts[0].spent === 0 &&
      destroyed.mounts[0].state === 'IDLE' &&
      !destroyed.mounts[0].performance.operational,
    destroyed
  };

  await run('prepare', { mount: 'GUN', seed: results.seed + 3, damage: 0, rangeKm: 12.0 });
  const healthyBoundary = (await run('stepCiws', 0.02)).snapshot;
  await run('prepare', { mount: 'GUN', seed: results.seed + 3, damage: 70, rangeKm: 12.0 });
  const severeBoundary = (await run('stepCiws', 0.02)).snapshot;
  results.checks.liveSearchRangeBoundary = {
    pass: healthyBoundary.mounts[0].state !== 'IDLE' &&
      severeBoundary.mounts[0].state === 'IDLE' &&
      severeBoundary.mounts[0].performance.cueTrackRangeKm < 12.0,
    healthyBoundary,
    severeBoundary
  };

  const speedRows = {};
  for (const scale of [1, 8, 16]) {
    await run('prepare', { mount: 'GUN', seed: results.seed + 4, damage: 40, rangeKm: 3.2 });
    const advanced = await run('advance', { timeScale: scale, simSeconds: 6, fps: 60 });
    speedRows[`x${scale}`] = advanced;
  }
  const digest = row => JSON.stringify({
    steps: row.steps,
    spent: row.snapshot.mounts.map(x => x.spent),
    states: row.snapshot.mounts.map(x => x.state),
    performance: row.snapshot.mounts.map(x => x.performance),
    rngState: row.snapshot.rngState,
    simStepCounter: row.snapshot.simStepCounter
  });
  results.checks.damagedFixedStepDeterminism = {
    pass: digest(speedRows.x1) === digest(speedRows.x8) &&
      digest(speedRows.x1) === digest(speedRows.x16),
    speedRows
  };

  expect(Object.entries(results.checks).filter(([, value]) => !value.pass)).toEqual([]);
  expect(results.consoleErrors).toEqual([]);
  expect(results.pageErrors).toEqual([]);
});
