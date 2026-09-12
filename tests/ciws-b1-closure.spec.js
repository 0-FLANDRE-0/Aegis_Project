const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v37.1_WIP04.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ciws-b1-closure';
const results = { schema: 'AEGIS_CIWS_B1_CLOSURE_V2', simulator,
  simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),
  seed: 3710401, checks: {}, consoleErrors: [], pageErrors: [] };

test.use({ viewport: { width: 1600, height: 900 } });
test.afterAll(() => {
  fs.mkdirSync(artifactDir, { recursive: true });
  results.completedAt = new Date().toISOString();
  results.pass = Object.values(results.checks).every(x => x.pass) && !results.consoleErrors.length && !results.pageErrors.length;
  fs.writeFileSync(`${artifactDir}/ciws-b1-results.json`, `${JSON.stringify(results, null, 2)}\n`);
});

test('CIWS Closure B1 browser matrix', async ({ page }) => {
  page.on('console', msg => { if (msg.type() === 'error') results.consoleErrors.push(msg.text()); });
  page.on('pageerror', err => results.pageErrors.push(err.stack || String(err)));
  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.ciwsB1Closure, null, { timeout: 30_000 });

  const startup = await page.evaluate(() => ({ failures: window.__CORE_SELFTEST_FAILURES__.slice(), logs: window.__NAVAL_SIM_DIAG__.debugLogSnapshot() }));
  results.checks.pageLoad = { pass: !results.consoleErrors.length && !results.pageErrors.length };
  results.checks.selftestFailuresEmpty = { pass: !startup.failures.length, failures: startup.failures };
  results.checks.coreSelftestPass = { pass: startup.logs.some(x => String(x?.text ?? x).includes('CORE SELFTEST PASS')) };

  const run = (method, ...args) => page.evaluate(([method, args]) => window.__NAVAL_SIM_DIAG__.ciwsB1Closure[method](...args), [method, args]);
  const engagement = async (mount, seed, damage = 0) => {
    await run('prepare', { mount, seed, damage, rangeKm: mount === 'GUN' ? 2.4 : 6.0 });
    return (await run('advance', { timeScale: 1, simSeconds: 12, fps: 60 })).snapshot;
  };
  const gun = await engagement('GUN', results.seed);
  const ram = await engagement('RAM', results.seed + 1);
  results.checks.authorizedPhalanxEngagement = { pass: gun.mounts[0].spent > 0, result: gun };
  results.checks.authorizedSeaRamEngagement = { pass: ram.mounts[1].spent > 0 && ram.ramLaunched > 0, result: ram };

  const protectedRows = [];
  for (const condition of ['FRIEND', 'NEUTRAL', 'UNKNOWN', 'UNASSESSED', 'WITHHELD']) {
    const baseline = await run('prepare', { seed: results.seed + 10 + protectedRows.length, rangeKm: 2.0 });
    const configured = await run('setCondition', condition);
    const final = (await run('advance', { timeScale: 1, simSeconds: 5, fps: 60 })).snapshot;
    protectedRows.push({ condition, baseline: { track: baseline.track, gate: baseline.gate }, configured: configured.track, gate: final.gate,
      automaticShots: final.mounts.reduce((sum, m) => sum + m.spent, 0) });
  }
  results.checks.protectedTracksNoAutoFire = { pass: protectedRows.every(x => x.baseline.gate.ok && x.automaticShots === 0 && !x.gate.ok), rows: protectedRows };

  await run('prepare', { mount: 'RAM', seed: results.seed + 30, rangeKm: 5.5 });
  results.checks.cueRequiresLocalDetection = { pass: await run('probeCueWithoutLocalDetection') };

  await run('prepare', { mount: 'GUN', seed: results.seed + 40, rangeKm: 2.4 });
  const acquired = (await run('advance', { timeScale: 1, simSeconds: 4, fps: 60 })).snapshot;
  await run('setLifecycle', 'LOST');
  const lost = (await run('advance', { timeScale: 1, simSeconds: 1, fps: 60 })).snapshot;
  await run('setLifecycle', 'REACQUIRING');
  const reacquiring = (await run('advance', { timeScale: 1, simSeconds: 1, fps: 60 })).snapshot;
  await run('setLifecycle', 'PRESENT');
  const reacquired = (await run('advance', { timeScale: 1, simSeconds: 5, fps: 60 })).snapshot;
  const lostSpent = lost.mounts[0].spent;
  results.checks.lossAndReacquisition = { pass: acquired.mounts[0].spent > 0 &&
    lost.mounts[0].state === 'IDLE' && !lost.mounts[0].tracking &&
    reacquiring.mounts[0].spent === lostSpent && reacquiring.mounts[0].state === 'IDLE' &&
    reacquired.mounts[0].spent > lostSpent, result: { acquired, lost, reacquiring, reacquired } };

  const gunDamaged = await engagement('GUN', results.seed + 50, 40);
  const ramDamaged = await engagement('RAM', results.seed + 51, 40);
  results.checks.healthyAndPartialDamage = { pass: gunDamaged.mounts[0].spent > 0 && ramDamaged.mounts[1].spent > 0, gunDamaged, ramDamaged };

  const speedRows = {};
  for (const scale of [1, 8, 16]) {
    await run('prepare', { mount: 'GUN', seed: results.seed + 60, rangeKm: 4.0 });
    const advanced = await run('advance', { timeScale: scale, simSeconds: 6, fps: 60 });
    speedRows[`x${scale}`] = { simSeconds: advanced.simSeconds, steps: advanced.steps, snapshot: advanced.snapshot };
  }
  const digest = row => JSON.stringify({ simSeconds: row.simSeconds, steps: row.steps,
    spent: row.snapshot.mounts.map(x => x.spent), states: row.snapshot.mounts.map(x => x.state),
    rngState: row.snapshot.rngState, simStepCounter: row.snapshot.simStepCounter });
  results.checks.timeScaleDeterminism = { pass: digest(speedRows.x1) === digest(speedRows.x8) && digest(speedRows.x1) === digest(speedRows.x16), result: speedRows };

  await run('prepare', { mount: 'GUN', seed: results.seed + 70, rangeKm: 2.0 });
  await run('advance', { timeScale: 1, simSeconds: 4, fps: 60 });
  await page.screenshot({ path: `${artifactDir}/ciws-engagement.png`, fullPage: true });
  const before3d = await run('snapshot');
  await page.evaluate(() => window.__WIP148_3D_VIEW__.open());
  await page.waitForFunction(() => window.__WIP148_3D_VIEW__?.ready === true, null, { timeout: 30_000 });
  const in3d = await run('snapshot');
  await page.screenshot({ path: `${artifactDir}/aegis-3d.png`, fullPage: true });
  await page.evaluate(() => window.__WIP148_3D_VIEW__.close());
  const after3d = await run('snapshot');
  const combatDigest = x => JSON.stringify({ track: x.track, mounts: x.mounts, ramLaunched: x.ramLaunched, bullets: x.bullets, rngState: x.rngState, simStepCounter: x.simStepCounter });
  results.checks.viewModeIsolation = { pass: combatDigest(before3d) === combatDigest(in3d) && combatDigest(in3d) === combatDigest(after3d) };

  expect(results.consoleErrors, 'JavaScript console errors').toEqual([]);
  expect(results.pageErrors, 'uncaught page errors').toEqual([]);
  for (const [name, check] of Object.entries(results.checks)) expect(check.pass, name).toBe(true);
});
