const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12B.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ship-structural-fatigue';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP03 longitudinal strength, keel fatigue, cracks and secondary flooding', async ({ page }) => {
  test.setTimeout(120_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() =>
    Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
    window.__NAVAL_SIM_DIAG__?.runV48Wip03StructuralProbe &&
    window.__NAVAL_SIM_DIAG__?.v48Wip03StructuralReadPerformance,
  null, { timeout: 30_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    const probe = d.runV48Wip03StructuralProbe({
      hits: 2, label: 'Kh-32', xM: 12, zM: -3.5, side: 'STARBOARD'
    });
    const structure0 = d.v48Wip03StructuralState();
    const flood0 = d.damageFloodSnapshotV1();
    const visual0 = d.v48Wip03DamageVisualState();
    const authorityBefore = JSON.stringify({ structure: structure0, flood: flood0, visual: visual0 });
    for (let i = 0; i < 32; i++) window.get3DRenderState();
    const authorityAfter = JSON.stringify({
      structure: d.v48Wip03StructuralState(),
      flood: d.damageFloodSnapshotV1(),
      visual: d.v48Wip03DamageVisualState()
    });
    const performance = d.v48Wip03StructuralReadPerformance(20_000);
    d.stepTicks(59);
    const cadenceBefore = d.v48Wip03StructuralState().performance.loadEvaluations;
    d.stepTicks(1);
    const cadenceAtOneSecond = d.v48Wip03StructuralState().performance.loadEvaluations;
    d.stepTicks(180);
    const structure4s = d.v48Wip03StructuralState();
    const flood4s = d.damageFloodSnapshotV1();
    return {
      selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(),
      probe, structure0, flood0, visual0, performance,
      cadenceBefore, cadenceAtOneSecond, structure4s, flood4s,
      renderReadOnly: authorityBefore === authorityAfter
    };
  });

  const shell = result.flood0.openings.filter(o => o.kind === 'SHELL_ENTRY' || o.kind === 'SHELL_EXIT');
  const entryOpening = shell.find(o => o.kind === 'SHELL_ENTRY');
  const exitOpening = shell.find(o => o.kind === 'SHELL_EXIT');
  const sideCracks = result.flood0.openings.filter(o => o.kind === 'SIDE_STRENGTH_CRACK');
  const keelCracks = result.flood0.openings.filter(o => o.kind === 'KEEL_CRACK');
  const entryScar = result.visual0.scars.find(s => s.impactRole === 'ENTRY');
  const exitScar = result.visual0.scars.find(s => s.impactRole === 'EXIT');
  const areaMatches = scar => {
    const opening = result.flood0.openings.find(o => o.id === scar?.openingId);
    return !!opening && Math.abs(opening.areaM2 - scar.sourceAreaM2) < 1e-9;
  };
  const worst = result.structure0.zones.find(z => z.section === result.structure0.summary.worstSection);
  const checks = {
    pageLoad: !consoleErrors.length && !pageErrors.length,
    coreSelftests: result.selftestFailures.length === 0,
    impactEventCount: result.structure0.events.length === 2 && result.structure0.performance.impactEvaluations === 2,
    multiHitStrengthLoss: result.structure0.summary.longitudinalStrength01 < 0.2 && worst?.impactCount === 2 && worst.absorbedEnergyMJ > 10_000,
    sideCrackCreated: result.structure0.summary.sideCracks >= 1 && sideCracks.length >= 1 && sideCracks.every(o => o.areaM2 > 0),
    keelCrackCreated: result.structure0.summary.keelCracks >= 1 && keelCracks.length >= 1 && keelCracks.every(o => o.areaM2 > 0),
    secondStageFlooding: result.flood4s.summary.waterM3 > result.flood0.summary.waterM3 + 1 && result.flood4s.summary.wetCells >= 3 && result.flood4s.summary.netM3s > 0,
    oneHzCadence: result.cadenceBefore === 0 && result.cadenceAtOneSecond === 1 && result.structure4s.performance.loadEvaluations === 4,
    cachedReadPath: result.performance.impactEvaluations === 0 && result.performance.loadEvaluations === 0 && Number.isFinite(result.performance.totalMs),
    damageRenderContract: result.visual0.schema === 'AEGIS_SHIP_DAMAGE_VISUAL_V48_WIP03' && result.visual0.contract === 'PRESENTATION_ONLY_SOLVED_DAMAGE',
    entryExitRoles: !!entryScar && !!exitScar && entryScar.openingKind === 'SHELL_ENTRY' && exitScar.openingKind === 'SHELL_EXIT',
    separateSides: entryOpening?.y * exitOpening?.y < 0 && entryScar.p.y * exitScar.p.y < 0,
    areaPreserved: areaMatches(entryScar) && areaMatches(exitScar),
    renderReadOnly: result.renderReadOnly
  };

  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = {
    schema: 'AEGIS_SHIP_STRUCTURAL_FATIGUE_V48_WIP03_V1', simulator,
    simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),
    checks, consoleErrors, pageErrors, result
  };
  fs.writeFileSync(artifactDir + '/ship-structural-fatigue-results.json', JSON.stringify(artifact, null, 2) + '\n');
  await page.screenshot({ path: artifactDir + '/ship-structural-fatigue-page.png', fullPage: true });
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
