const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP07.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ship-stability-maneuver';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP04 upright GM0 and finite-angle GZ stay separated in manoeuvres', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));

  async function freshPage() {
    await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
    await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.v48Wip04StabilityState, null, { timeout: 30_000 });
  }

  await freshPage();
  const baseline = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d.stepTicks(2);
    return {
      selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(),
      model: d.v48Wip04StabilityModel(),
      state: d.v48Wip04StabilityState(),
      curve: d.v48Wip04StabilityCurve([0, 1, 5, 10, 14, 20, 30, 40, 50, 60])
    };
  });
  const loadingCase = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d.shipMassSetLoadFraction('ballast.fwd', 0);
    d.shipMassSetLoadFraction('ballast.aft', 0);
    d.stepTicks(240);
    const lowBallast = d.v48Wip04StabilityState();
    d.shipMassSetLoadFraction('ballast.fwd', 1);
    d.shipMassSetLoadFraction('ballast.aft', 1);
    d.stepTicks(240);
    return { lowBallast, restored: d.v48Wip04StabilityState() };
  });

  const cases = [];
  for (const speedKt of [15, 25, 30]) {
    for (const rudderDeg of [10, 20, 30]) {
      await freshPage();
      const result = await page.evaluate(({ speedKt, rudderDeg }) => {
        const d = window.__NAVAL_SIM_DIAG__;
        d.setShipMotionTest(speedKt, 0);
        d.setShipRudderTest(rudderDeg);
        const samples = [];
        for (let i = 0; i < 12; i++) {
          d.stepTicks(600);
          const q = d.shipDynamics();
          samples.push({
            timeS: (i + 1) * 5,
            heelDeg: q.pose.heelRad * 180 / Math.PI,
            gm0M: q.physics.gm0M,
            gzM: q.physics.rightingArmM,
            speedKt: q.speedMps / 0.514444,
            turnRadiusM: q.physics.turnRadiusM,
            draftM: q.pose.draftM,
            referenceDraftM: q.physics.stabilityReferenceDraftM
          });
        }
        return samples;
      }, { speedKt, rudderDeg });
      const steady = result.at(-1);
      cases.push({ speedKt, rudderDeg, samples: result, steady, diameterLengthRatio: 2 * steady.turnRadiusM / 155.3 });
    }
  }

  const allSamples = cases.flatMap(q => q.samples);
  const fullRudder = cases.filter(q => q.rudderDeg === 30);
  const hard30 = cases.find(q => q.speedKt === 30 && q.rudderDeg === 30);
  const gmValues = allSamples.map(q => q.gm0M);
  const curveVolumeErrorM3 = Math.max(...baseline.curve.points.map(q => Math.abs(q.displacementM3 - baseline.curve.points[0].displacementM3)));
  const oneDegree = baseline.curve.points.find(q => q.deg === 1);
  const checks = {
    pageLoad: !consoleErrors.length && !pageErrors.length,
    coreSelftests: baseline.selftestFailures.length === 0,
    stabilitySchema: baseline.model.schema === 'AEGIS_INTACT_STABILITY_V48_WIP04' && baseline.state.stabilitySchema === baseline.model.schema,
    calibratedUprightGM: Math.abs(baseline.state.gm0M - 1.5) < 0.0001 && baseline.state.gmM === baseline.state.gm0M,
    gmIndependentOfTurnHeel: Math.max(...gmValues) - Math.min(...gmValues) < 0.0001,
    gmRespondsToLoading: loadingCase.lowBallast.gm0M < baseline.state.gm0M - 0.08 && Math.abs(loadingCase.restored.gm0M - baseline.state.gm0M) < 0.0001,
    finiteAngleGZSeparated: Math.abs(hard30.steady.heelDeg) > 10 && Math.abs(hard30.steady.gzM) > 0.3 && Math.abs(hard30.steady.gzM / Math.sin(hard30.steady.heelDeg * Math.PI / 180) - hard30.steady.gm0M) > 0.1,
    hardTurnEnvelope: Math.abs(hard30.steady.heelDeg) >= 10 && Math.abs(hard30.steady.heelDeg) <= 20,
    turningScaleEnvelope: fullRudder.every(q => q.diameterLengthRatio >= 4.2 && q.diameterLengthRatio <= 5.5),
    constantDisplacementCurve: curveVolumeErrorM3 < 0.001,
    geometricSmallAngleSlope: Math.abs(oneDegree.geometricGZM / Math.sin(Math.PI / 180) - baseline.curve.gm0M) < 0.05,
    geometricCurveDiagnosticOnly: baseline.curve.authority === 'DIAGNOSTIC_ONLY_UNTIL_HULL_LINES_VALIDATED'
  };

  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = {
    schema: 'AEGIS_SHIP_STABILITY_MANOEUVRE_V48_WIP04_V1',
    simulator,
    simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),
    checks,
    consoleErrors,
    pageErrors,
    baseline,
    loadingCase,
    curveVolumeErrorM3,
    cases
  };
  fs.writeFileSync(`${artifactDir}/ship-stability-maneuver-results.json`, `${JSON.stringify(artifact, null, 2)}\n`);
  await page.screenshot({ path: `${artifactDir}/ship-stability-maneuver-page.png`, fullPage: true });
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
