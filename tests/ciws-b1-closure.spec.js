const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v37.1_WIP03.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ciws-b1-closure';
const results = {
  schema: 'AEGIS_CIWS_B1_CLOSURE_V1',
  simulator,
  simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),
  seed: 3710301,
  checks: {},
  consoleErrors: [],
  pageErrors: [],
};

test.use({ viewport: { width: 1600, height: 900 } });

test.afterAll(() => {
  fs.mkdirSync(artifactDir, { recursive: true });
  results.completedAt = new Date().toISOString();
  results.pass = Object.values(results.checks).every(check => check.pass) &&
    results.consoleErrors.length === 0 && results.pageErrors.length === 0;
  fs.writeFileSync(`${artifactDir}/ciws-b1-results.json`, `${JSON.stringify(results, null, 2)}\n`);
});

test('CIWS Closure B1 browser matrix', async ({ page }) => {
  page.on('console', message => {
    if (message.type() === 'error') results.consoleErrors.push(message.text());
  });
  page.on('pageerror', error => results.pageErrors.push(error.stack || String(error)));

  await page.goto('http://127.0.0.1:4173/', { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__), null, { timeout: 30_000 });

  const startup = await page.evaluate(() => ({
    failures: window.__CORE_SELFTEST_FAILURES__.slice(),
    logs: window.__NAVAL_SIM_DIAG__.debugLogSnapshot(),
  }));
  const corePass = startup.logs.some(row => String(row?.text ?? row).includes('CORE SELFTEST PASS'));
  results.checks.pageLoad = { pass: results.consoleErrors.length === 0 && results.pageErrors.length === 0 };
  results.checks.selftestFailuresEmpty = { pass: startup.failures.length === 0, failures: startup.failures };
  results.checks.coreSelftestPass = { pass: corePass };

  const matrix = await page.evaluate(async seed => {
    const resetMounts = () => {
      for (const mount of ciws) {
        Object.assign(mount, { state: 'IDLE', stateTimer: 0, tracking: false, trackingTarget: null,
          trackingTrackId: null, cuedTarget: null, cueAge: 999, firing: false, trackQuality: 0,
          reloadTimer: 0, _shotAccumulator: 0 });
        delete mount._localTrack;
      }
      ciwsLocalDetectB1._contacts?.clear?.();
    };
    const prepare = (caseSeed, rangeKm, damage = 0) => {
      _wip75ResetCase(caseSeed); resetMounts(); setEngagementControlMode('AUTO');
      ciws[0].ammo = ciws[0].maxAmmo; ciws[1].ammo = ciws[1].maxAmmo;
      shipModules.Phalanx = damage; shipModules.SeaRAM = damage;
      const fixture = _wip75CreateTarget({ rangeKm, bearingDeg: 0, speedMps: 300, altM: 15, vzMps: 0 });
      updateTrackOperationalStateA3(fixture.tr, { mode: 'AUTO', assessment: { state: 'THREAT' }, fireControlReady: true });
      return fixture;
    };
    const step = (fixture, ticks, group = 1) => {
      for (let outer = 0; outer < ticks; outer += group) {
        for (let inner = 0; inner < Math.min(group, ticks - outer); inner++) {
          if (fixture.em.alive) {
            fixture.em.x += fixture.em.vx * SIM_FIXED_DT;
            fixture.em.y += fixture.em.vy * SIM_FIXED_DT;
            fixture.em.z += fixture.em.vz * SIM_FIXED_DT;
            const tr = _wip75SyncTrack(fixture.em);
            updateTrackOperationalStateA3(tr, { mode: 'AUTO', assessment: { state: 'THREAT' }, fireControlReady: true });
          }
          updateCIWS(SIM_FIXED_DT); simStepCounter++;
        }
      }
    };
    const engagement = (kind, caseSeed, damage = 0) => {
      const fixture = prepare(caseSeed, kind === 'GUN' ? 2.4 : 6.0, damage);
      if (kind === 'GUN') ciws[1].ammo = 0; else ciws[0].ammo = 0;
      const before = { gun: ciws[0].ammo, ram: ciws[1].ammo };
      step(fixture, 20 * 60);
      return { kind, damage, before, after: { gun: ciws[0].ammo, ram: ciws[1].ammo },
        ramLaunched: ramMissiles.length, bullets: ciwsBullets.length,
        states: ciws.map(m => ({ type: m.type, state: m.state, source: m._ciwsTrackSource, trackingTrackId: m.trackingTrackId })) };
    };

    const gunHealthy = engagement('GUN', seed);
    const ramHealthy = engagement('RAM', seed + 1);
    const gunDamaged = engagement('GUN', seed + 2, 40);
    const ramDamaged = engagement('RAM', seed + 3, 40);

    const protectedRows = [];
    for (const state of ['FRIEND', 'NEUTRAL', 'UNKNOWN', 'UNASSESSED', 'WITHHELD']) {
      const fixture = prepare(seed + 100 + protectedRows.length, 2.0);
      ciws[0].ammo = 200; ciws[1].ammo = 2;
      Object.assign(fixture.tr, {
        identity: state === 'FRIEND' || state === 'NEUTRAL' ? state : 'UNKNOWN',
        threatStatus: state === 'UNASSESSED' ? 'UNASSESSED' : 'THREAT',
        engagementAuthority: state === 'WITHHELD' ? 'WITHHELD' : 'WITHHELD',
      });
      const before = [ciws[0].ammo, ciws[1].ammo];
      for (let i = 0; i < 240; i++) { updateCIWS(SIM_FIXED_DT); simStepCounter++; }
      protectedRows.push({ state, automaticShots: before[0] - ciws[0].ammo + before[1] - ciws[1].ammo });
    }

    const cueFixture = prepare(seed + 200, 5.5);
    const originalLocalDetect = ciwsLocalDetectB1;
    ciwsLocalDetectB1 = () => false;
    const cueNoLocal = ciwsResolveLocalContactB1(ciws[1], cueFixture.trackId, SIM_FIXED_DT, true);
    ciwsLocalDetectB1 = originalLocalDetect;

    const lifecycle = prepare(seed + 300, 2.5);
    const present = ciwsObservedThreatsB1(ciws[0]).some(x => x.trackId === lifecycle.trackId);
    lifecycle.tr.sensorDetected = false;
    const lost = !ciwsObservedThreatsB1(ciws[0]).some(x => x.trackId === lifecycle.trackId);
    lifecycle.tr.sensorDetected = true; lifecycle.tr.reacquiring = true;
    const reacquiringBlocked = !ciwsObservedThreatsB1(ciws[0]).some(x => x.trackId === lifecycle.trackId);
    lifecycle.tr.reacquiring = false;
    const reacquired = ciwsObservedThreatsB1(ciws[0]).some(x => x.trackId === lifecycle.trackId);

    const speedCase = group => {
      const fixture = prepare(seed + 400, 4.0); ciws[1].ammo = 0;
      step(fixture, 360, group);
      return { gunAmmo: ciws[0].ammo, ramAmmo: ciws[1].ammo, targetAlive: fixture.em.alive,
        targetX: fixture.em.x, states: ciws.map(m => m.state), rng: SIM_RNG_STATE };
    };
    const speed = { x1: speedCase(1), x8: speedCase(8), x16: speedCase(16) };

    const toggleFixture = prepare(seed + 500, 4.0);
    const digest = () => JSON.stringify({ enemies: enemyMissiles.map(e => [e.id, e.alive, e.x, e.y, e.z]),
      tracks: [...tracks].map(([id, tr]) => [id, tr.x, tr.y, tr.identity, tr.engagementAuthority]),
      ammo: ciws.map(m => m.ammo), steps: simStepCounter });
    const beforeToggle = digest();
    WIP148_EXTERNAL_3D.open(); await new Promise(resolve => setTimeout(resolve, 1500));
    const in3d = digest(); WIP148_EXTERNAL_3D.close(); const afterToggle = digest();

    return { gunHealthy, ramHealthy, gunDamaged, ramDamaged, protectedRows,
      cueNoLocal: cueNoLocal === null,
      lifecycle: { present, lost, reacquiringBlocked, reacquired }, speed,
      viewToggle: { unchanged: beforeToggle === in3d && in3d === afterToggle },
      screenshotReady: { targetId: toggleFixture.trackId } };
  }, results.seed);

  const gunFired = row => row.after.gun < row.before.gun;
  const ramFired = row => row.after.ram < row.before.ram && row.ramLaunched > 0;
  results.checks.authorizedPhalanxEngagement = { pass: gunFired(matrix.gunHealthy), result: matrix.gunHealthy };
  results.checks.authorizedSeaRamEngagement = { pass: ramFired(matrix.ramHealthy), result: matrix.ramHealthy };
  results.checks.protectedTracksNoAutoFire = { pass: matrix.protectedRows.every(x => x.automaticShots === 0), rows: matrix.protectedRows };
  results.checks.cueRequiresLocalDetection = { pass: matrix.cueNoLocal };
  results.checks.lossAndReacquisition = { pass: matrix.lifecycle.present && matrix.lifecycle.lost && matrix.lifecycle.reacquiringBlocked && matrix.lifecycle.reacquired, result: matrix.lifecycle };
  results.checks.healthyAndPartialDamage = { pass: gunFired(matrix.gunDamaged) && ramFired(matrix.ramDamaged), gun: matrix.gunDamaged, ram: matrix.ramDamaged };
  results.checks.timeScaleDeterminism = { pass: JSON.stringify(matrix.speed.x1) === JSON.stringify(matrix.speed.x8) && JSON.stringify(matrix.speed.x1) === JSON.stringify(matrix.speed.x16), result: matrix.speed };
  results.checks.viewModeIsolation = { pass: matrix.viewToggle.unchanged, result: matrix.viewToggle };

  await page.evaluate(seed => {
    _wip75ResetCase(seed); setEngagementControlMode('AUTO');
    for (const mount of ciws) Object.assign(mount, { state: 'IDLE', stateTimer: 0, trackingTarget: null,
      trackingTrackId: null, cuedTarget: null, firing: false, reloadTimer: 0, _shotAccumulator: 0 });
    ciws[0].ammo = ciws[0].maxAmmo; ciws[1].ammo = 0;
    const fixture = _wip75CreateTarget({ rangeKm: 2.0, bearingDeg: 0, speedMps: 250, altM: 15 });
    updateTrackOperationalStateA3(fixture.tr, { mode: 'AUTO', assessment: { state: 'THREAT' }, fireControlReady: true });
    const initialAmmo = ciws[0].ammo;
    for (let i = 0; i < 1200 && ciws[0].ammo === initialAmmo; i++) {
      fixture.em.x += fixture.em.vx * SIM_FIXED_DT; fixture.em.y += fixture.em.vy * SIM_FIXED_DT;
      const tr = _wip75SyncTrack(fixture.em);
      updateTrackOperationalStateA3(tr, { mode: 'AUTO', assessment: { state: 'THREAT' }, fireControlReady: true });
      updateCIWS(SIM_FIXED_DT); simStepCounter++;
    }
  }, results.seed + 600);
  await page.screenshot({ path: `${artifactDir}/ciws-engagement.png`, fullPage: true });
  await page.evaluate(() => WIP148_EXTERNAL_3D.open());
  await page.waitForFunction(() => window.__WIP148_3D_VIEW__?.ready === true, null, { timeout: 30_000 });
  await page.screenshot({ path: `${artifactDir}/aegis-3d.png`, fullPage: true });

  expect(results.consoleErrors, 'JavaScript console errors').toEqual([]);
  expect(results.pageErrors, 'uncaught page errors').toEqual([]);
  for (const [name, check] of Object.entries(results.checks)) expect(check.pass, name).toBe(true);
});
