const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP07.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ship-wave-flooding';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP05 deterministic wave phase drives local shell-opening flooding', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.runV48Wip05WaveFloodProbe, null, { timeout: 30_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    const common = { tpS: 8, directionDeg: 90, seed: 4805, durationS: 16, sampleEveryS: .25, speedKt: 15, headingDeg: 0, xM: 12, zM: 1.30, areaM2: .24 };
    const calm = d.runV48Wip05WaveFloodProbe({ ...common, hsM: 0 });
    const waveA = d.runV48Wip05WaveFloodProbe({ ...common, hsM: 2 });
    const waveB = d.runV48Wip05WaveFloodProbe({ ...common, hsM: 2 });
    const outflow = d.runV48Wip05WaveFloodProbe({ ...common, hsM: 0, durationS: 3, initialFill01: .8 });
    const authorityBefore = JSON.stringify({ wave: d.v48Wip05WaveFloodState(true), flood: d.damageFloodSnapshotV1(), dynamics: d.shipDynamics() });
    for (let i = 0; i < 64; i++) window.get3DRenderState();
    const authorityAfter = JSON.stringify({ wave: d.v48Wip05WaveFloodState(true), flood: d.damageFloodSnapshotV1(), dynamics: d.shipDynamics() });
    const performance = d.v48Wip05WaveReadPerformance(20_000);
    return { selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(), model: d.v48Wip05WaveFloodModel(), calm, waveA, waveB, outflow, performance, renderReadOnly: authorityBefore === authorityAfter, ui: { preset: !!document.getElementById('dfWavePreset'), direction: !!document.getElementById('dfWaveDirection'), state: !!document.getElementById('dfWaveState') } };
  });

  const waveRows = result.waveA.samples.flatMap(s => s.openings);
  const oppositeSidePhaseDifference = result.waveA.samples.some(s => s.openings.length === 2 && Math.abs(s.openings[0].seaLevelM - s.openings[1].seaLevelM) > .03);
  const checks = {
    pageLoad: !consoleErrors.length && !pageErrors.length,
    coreSelftests: result.selftestFailures.length === 0,
    schema: result.model.schema === 'AEGIS_WAVE_FLOODING_V48_WIP05' && result.waveA.wave.contract === 'DETERMINISTIC_LOCAL_SEA_BOUNDARY',
    calmBackwardCompatible: result.calm.summary.waterM3 < 1e-9 && result.calm.summary.seaInM3 < 1e-9 && result.calm.samples.every(s => s.openings.every(o => o.seaLevelM === 0 && o.seaWet01 === 0)),
    crestTroughRange: result.waveA.summary.minSeaLevelM < -.15 && result.waveA.summary.maxSeaLevelM > .15,
    wetDryTransition: result.waveA.summary.minWet01 < .05 && result.waveA.summary.maxWet01 > .95,
    phaseModulatedIngress: result.waveA.summary.maxFlowIntoM3s > .05 && result.waveA.summary.waterM3 > 1 && new Set(waveRows.map(o => Math.round(o.flowIntoM3s * 100))).size > 4,
    oppositeSidesSampleLocalSea: oppositeSidePhaseDifference,
    bidirectionalBoundary: result.outflow.summary.seaOutM3 > .01 && result.outflow.summary.minFlowIntoM3s < -.01,
    massStabilityFeedback: Number.isFinite(result.waveA.summary.gm0M) && result.waveA.summary.draftM > 0 && result.waveA.summary.waterM3 > result.calm.summary.waterM3,
    deterministicSeed: JSON.stringify(result.waveA.samples) === JSON.stringify(result.waveB.samples) && JSON.stringify(result.waveA.summary) === JSON.stringify(result.waveB.summary),
    conservativeLedger: [result.calm, result.waveA, result.waveB, result.outflow].every(q => Math.abs(q.summary.balanceErrorM3) < 1e-6),
    cachedReadPath: result.performance.evaluations === 0 && Number.isFinite(result.performance.totalMs),
    renderReadOnly: result.renderReadOnly,
    uiControls: result.ui.preset && result.ui.direction && result.ui.state
  };

  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = { schema: 'AEGIS_SHIP_WAVE_FLOODING_V48_WIP05_V1', simulator, simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, result };
  fs.writeFileSync(`${artifactDir}/ship-wave-flooding-results.json`, `${JSON.stringify(artifact, null, 2)}\n`);
  await page.screenshot({ path: `${artifactDir}/ship-wave-flooding-page.png`, fullPage: true });
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
