const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP10.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ship-interior-topology';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP06 detailed ship interior topology and assisted automation contract', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.runV48Wip06InteriorProbe, null, { timeout: 30_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__, probe = d.runV48Wip06InteriorProbe(), state = d.v48Wip06InteriorState(), before = JSON.stringify({ flood: d.damageFloodSnapshotV1(), control: d.damageControlSnapshotV1?.() ?? null, topology: state });
    for (let i = 0; i < 64; i++) window.get3DRenderState();
    const after = JSON.stringify({ flood: d.damageFloodSnapshotV1(), control: d.damageControlSnapshotV1?.() ?? null, topology: d.v48Wip06InteriorState() });
    return {
      selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(), model: d.v48Wip06InteriorModel(), probe,
      state, audit: d.v48Wip06InteriorAudit(), liveDamageControl: d.damageControlSnapshotV1(), performance: d.v48Wip06InteriorReadPerformance(20_000),
      renderReadOnly: before === after,
      renderStateContract: window.get3DRenderState().shipInteriorTopology?.renderContract,
      ui: { button: !!document.getElementById('external3DInteriorBtn'), pressed: document.getElementById('external3DInteriorBtn')?.getAttribute('aria-pressed') }
    };
  });

  const checks = {
    pageLoad: !consoleErrors.length && !pageErrors.length,
    coreSelftests: result.selftestFailures.length === 0,
    schema: result.model.schema === 'AEGIS_SHIP_INTERIOR_TOPOLOGY_V48_WIP06' && result.state.contract === 'AUTHORITATIVE_SPATIAL_TOPOLOGY',
    detailedSpaces: result.audit.spaceCount >= 125 && result.audit.spaceCount <= 160 && result.audit.spaceCount === result.audit.macroSpaceCount && result.audit.deckCount === 11 && result.audit.upperStructureSpaces >= 75,
    functionalUpperworks: result.audit.bridgeSpaces >= 12 && result.audit.spySpaces >= 12,
    verticalShellFill: result.audit.upperStructureDecks >= 7 && result.audit.bridgeDecks >= 5 && result.audit.hangarDecks >= 2 && result.audit.exhaustTrunks >= 12 && result.audit.mastTrunks >= 3,
    equipmentNodes: result.audit.equipmentCount >= 70 && result.audit.spaceCount + result.audit.equipmentCount >= 200 && result.audit.uniqueEquipmentIds && result.audit.equipmentSpacesValid,
    validTopology: result.audit.uniqueSpaceIds && result.audit.uniquePortalIds && result.audit.endpointsValid,
    connectedRouteableSpaces: result.audit.routeable === result.audit.reached && result.audit.unreachable.length === 0,
    physicalConnectorTypes: result.audit.watertightDoors > 0 && result.audit.fireDoors > 0 && result.audit.stairs >= 10 && result.audit.ladders >= 4 && result.audit.accessHatches === 8,
    parentFloodOwnership: result.state.spaces.every(s => typeof s.parentFloodCellId === 'string' && s.parentFloodCellId.startsWith('flood.')),
    assistedAutomation: result.model.automation.mode === 'AUTO_ASSISTED' && result.model.automation.perDoorMicromanagement === false && result.model.automation.playerControl === 'ZONE_PRIORITY_AND_OVERRIDE',
    oneHzCadence: result.model.updatePolicy.cadenceHz === 1 && result.model.updatePolicy.floodParentCells === 24 && result.model.updatePolicy.renderFrameRecompute === false,
    liveAutomationDefault: result.liveDamageControl.automation.mode === 'AUTO',
    automaticIsolation: result.probe.checks.automaticIsolation && result.probe.emergency.automaticActions.some(q => q.reason === 'AUTO_FLOOD_ISOLATION') && result.probe.emergency.automaticActions.some(q => q.reason === 'AUTO_FIRE_SMOKE_ISOLATION'),
    deterministicFixture: result.probe.checks.deterministic,
    cachedReadPath: result.performance.evaluations === 0 && Number.isFinite(result.performance.totalMs),
    renderReadOnly: result.renderReadOnly && result.renderStateContract === 'PRESENTATION_ONLY_TOPOLOGY_SNAPSHOT',
    interiorButton: result.ui.button && result.ui.pressed === 'false'
  };

  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = { schema: 'AEGIS_SHIP_INTERIOR_TOPOLOGY_V48_WIP06_V1', simulator, simulatorSha256: crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, result };
  fs.writeFileSync(`${artifactDir}/ship-interior-topology-results.json`, `${JSON.stringify(artifact, null, 2)}\n`);
  await page.screenshot({ path: `${artifactDir}/ship-interior-topology-page.png`, fullPage: true });
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
