const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v37.1_WIP09.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ciws-b1-closure';
const results = { schema: 'AEGIS_CIWS_B1_CLOSURE_V2', simulator,
  simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),
  seed: 3710401, checks: {}, consoleErrors: [], pageErrors: [] };

test.use({ viewport: { width: 1600, height: 900 } });
const resetResults = () => {
  results.checks = {};
  results.consoleErrors = [];
  results.pageErrors = [];
  delete results.completedAt;
  delete results.pass;
};
test.afterEach(({}, testInfo) => {
  fs.mkdirSync(artifactDir, { recursive: true });
  results.completedAt = new Date().toISOString();
  results.pass = Object.values(results.checks).every(x => x.pass) && !results.consoleErrors.length && !results.pageErrors.length;
  const kind = testInfo.title.includes('browser matrix') ? 'matrix' : 'visual';
  fs.writeFileSync(`${artifactDir}/ciws-b1-${kind}-results.json`, `${JSON.stringify(results, null, 2)}\n`);
  const failures = Object.entries(results.checks).filter(([, value]) => !value.pass).map(([name, value]) => ({ name, value }));
  console.log('CIWS_B1_FAILED_CHECKS ' + JSON.stringify(failures));
});

test('CIWS Closure B1 browser matrix', async ({ page }) => {
  test.setTimeout(120_000);
  resetResults();
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
    const transitions = [];
    for (let i = 0; i < 120; i++) {
      const snapshot = (await run('stepCiws', 0.1)).snapshot;
      const previous = transitions.at(-1);
      if (!previous || previous.mounts.some((m, n) => m.state !== snapshot.mounts[n].state || m.spent !== snapshot.mounts[n].spent)) transitions.push(snapshot);
    }
    return { final: transitions.at(-1), transitions };
  };
  const gun = await engagement('GUN', results.seed);
  const ram = await engagement('RAM', results.seed + 1);
  results.checks.authorizedPhalanxEngagement = { pass: gun.final.mounts[0].spent > 0, result: gun };
  results.checks.authorizedSeaRamEngagement = { pass: ram.final.mounts[1].spent > 0 && ram.final.ramLaunched > 0, result: ram };

  const protectedRows = [];
  for (const condition of ['FRIEND', 'NEUTRAL', 'UNKNOWN', 'UNASSESSED', 'WITHHELD']) {
    const baseline = await run('prepare', { seed: results.seed + 10 + protectedRows.length, rangeKm: 2.0 });
    const configured = await run('setCondition', condition);
    const final = (await run('stepCiws', 5)).snapshot;
    protectedRows.push({ condition, baseline: { track: baseline.track, gate: baseline.gate }, configured: { track: configured.track, gate: configured.gate }, final: { track: final.track, gate: final.gate },
      automaticShots: final.mounts.reduce((sum, m) => sum + m.spent, 0) });
  }
  const conditionHeld = row => row.condition === 'UNASSESSED' ? (!row.final.track.confirmed && row.final.track.threatStatus === 'UNASSESSED') :
    row.condition === 'WITHHELD' ? row.final.track.engagementAuthority === 'WITHHELD' : row.final.track.identity === row.condition;
  results.checks.protectedTracksNoAutoFire = { pass: protectedRows.every(x => x.baseline.gate.ok && !x.configured.gate.ok && !x.final.gate.ok && conditionHeld(x) && x.automaticShots === 0), rows: protectedRows };

  await run('prepare', { mount: 'RAM', seed: results.seed + 30, rangeKm: 5.5 });
  results.checks.cueRequiresLocalDetection = { pass: await run('probeCueWithoutLocalDetection') };

  await run('prepare', { mount: 'GUN', seed: results.seed + 40, rangeKm: 2.4 });
  let acquired;
  for (let i = 0; i < 100; i++) { acquired = (await run('stepCiws', 0.1)).snapshot; if (acquired.mounts[0].spent > 0) break; }
  const misses = await run('recordSensorMisses', 2);
  const lost = misses[0], reacquiring = misses[1];
  const blocked = (await run('stepCiws', 1)).snapshot;
  const reacquisitionHits = await run('recordReacquisitionHits', 2);
  const restored = reacquisitionHits.at(-1);
  const reacquired = (await run('stepCiws', 5)).snapshot;
  const lostSpent = reacquiring.mounts[0].spent;
  results.checks.lossAndReacquisition = { pass: acquired.mounts[0].spent > 0 &&
    lost.track.trackLifecycle === 'COAST' && reacquiring.track.reacquiring &&
    reacquiring.mounts[0].state === 'IDLE' && !reacquiring.mounts[0].tracking &&
    blocked.mounts[0].spent === lostSpent && blocked.track.reacquiring &&
    !restored.track.reacquiring && restored.track.trackLifecycle === 'FIRM' &&
    reacquired.mounts[0].spent > lostSpent, result: { acquired, misses, blocked, reacquisitionHits, reacquired } };

  const gunDamaged = await engagement('GUN', results.seed + 50, 40);
  const ramDamaged = await engagement('RAM', results.seed + 51, 40);
  results.checks.healthyAndPartialDamage = { pass: gunDamaged.final.mounts[0].spent > 0 && ramDamaged.final.mounts[1].spent > 0, gunDamaged, ramDamaged };

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

  console.log('CIWS_B1_STARTUP_FAILURES ' + JSON.stringify(startup.failures));
  expect.soft(results.consoleErrors, 'JavaScript console errors').toEqual([]);
  expect.soft(results.pageErrors, 'uncaught page errors').toEqual([]);
  for (const [name, check] of Object.entries(results.checks)) expect.soft(check.pass, name).toBe(true);
});

test('CIWS and 3D evidence capture', async ({ page }) => {
  test.setTimeout(120_000);
  resetResults();
  page.on('console', msg => { if (msg.type() === 'error') results.consoleErrors.push(msg.text()); });
  page.on('pageerror', err => results.pageErrors.push(err.stack || String(err)));
  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'load' });
  await page.waitForFunction(() => window.__NAVAL_SIM_DIAG__?.ciwsB1Closure);
  const api = (method, ...args) => page.evaluate(([method, args]) => window.__NAVAL_SIM_DIAG__.ciwsB1Closure[method](...args), [method, args]);
  await api('prepare', { mount: 'GUN', seed: results.seed + 70, rangeKm: 2.0 });
  for (let i = 0; i < 100; i++) { const s = (await api('stepCiws', 0.1)).snapshot; if (s.mounts[0].spent > 0) break; }
  await page.locator('#wip125DepartBtn').click();
  await page.screenshot({ path: `${artifactDir}/ciws-engagement.png` });
  // Reload recreates the pre-sail overlay, so dismiss it before collecting 3D evidence.
  await page.reload({ waitUntil: 'load' });
  await page.waitForFunction(() => window.__NAVAL_SIM_DIAG__?.ciwsB1Closure);
  await page.locator('#wip125DepartBtn').click();
  await expect(page.locator('#wip125LoadoutOverlay')).toBeHidden({ timeout: 5_000 });
  results.checks.preSailOverlayHidden = { pass: true };
  const pause = await api('setPaused', true);
  results.checks.simulationPausedFor3D = { pass: pause.paused === true && pause.timeScale === 0, result: pause };
  const before3d = await api('snapshot');
  await page.evaluate(() => window.__WIP148_3D_VIEW__.open());
  await page.waitForFunction(() => window.__WIP148_3D_VIEW__?.ready === true, null, { timeout: 60_000 });
  const in3d = await api('snapshot');
  await page.locator('#external3DCanvas').screenshot({ path: `${artifactDir}/aegis-3d.png` });
  await page.evaluate(() => window.__WIP148_3D_VIEW__.close());
  const after3d = await api('snapshot');
  const digest = x => JSON.stringify({ track:x.track,mounts:x.mounts,ramLaunched:x.ramLaunched,bullets:x.bullets,rngState:x.rngState,simStepCounter:x.simStepCounter });
  const beforeDigest = digest(before3d), in3dDigest = digest(in3d), afterDigest = digest(after3d);
  results.checks.viewModeIsolation = { pass: beforeDigest === in3dDigest && in3dDigest === afterDigest,
    beforeDigest, in3dDigest, afterDigest };
  expect(results.checks.simulationPausedFor3D.pass).toBe(true);
  expect(results.checks.viewModeIsolation.pass).toBe(true);
});
