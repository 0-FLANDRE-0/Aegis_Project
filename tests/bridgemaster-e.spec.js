const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12C.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/bridgemaster-e';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP08 BridgeMaster E authoritative sensor, mount and damage contract', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
    window.__NAVAL_SIM_DIAG__?.bridgeMasterEAudit &&
    window.__NAVAL_SIM_DIAG__?.bridgeMasterEInstallation, null, { timeout: 30_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__, before = JSON.stringify(d.bridgeMasterEAudit());
    const installation = d.bridgeMasterEInstallation(), audit = d.bridgeMasterEAudit();
    const render = window.get3DRenderState(), beam = render.radar.bridgeMasterEBeams[0];
    for (let i = 0; i < 64; i++) window.get3DRenderState();
    return {
      selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(), installation, audit,
      renderRevision: render.revision, shipProfile: render.shipProfile, beam, hardpoint: render.hardpoints.bridgeMasterE,
      renderReadOnly: before === JSON.stringify(d.bridgeMasterEAudit()),
      button: {
        exists: !!document.getElementById('external3DBridgeMasterEBtn'),
        text: document.getElementById('external3DBridgeMasterEBtn')?.textContent?.trim(),
        legacyExists: !!document.getElementById('external3DSps73Btn')
      }
    };
  });
  const source = fs.readFileSync(simulator, 'utf8');
  const i = result.installation;
  const same = (a, b) => Math.abs(Number(a) - Number(b)) < 1e-9;
  const checks = {
    pageLoad: !consoleErrors.length && !pageErrors.length,
    coreSelftests: result.selftestFailures.length === 0,
    noLegacySps73: !/SPS[-_ ]?73|AN\/SPS-73/i.test(source),
    identity: result.audit.schema === 'AEGIS_BRIDGEMASTER_E_AUDIT_V48_WIP08' && result.audit.name === 'BridgeMaster E',
    declaredAssumptions: i.performanceBasis === 'PUBLIC_BRIDGEMASTER_E_S_BAND_BASELINE__DDG119_EXACT_NAVAL_VARIANT_PUBLIC_UNKNOWN' &&
      i.navalVariantExactConfiguration === 'PUBLIC_UNKNOWN' && i.mountBasis === 'DDG119_PHOTO_DERIVED_UPPER_STARBOARD_YARDARM',
    mainMastYardarm: same(i.xM, 15.75) && same(i.yM, 5.15) && same(i.zM, 31.78),
    physicalDamageTarget: i.hitbox?.system === 'BRIDGEMASTER_E' && i.hitbox?.targetId === 'bridgemaster_e.01',
    sharedHardpoint: same(i.xM, result.hardpoint.xM) && same(i.yM, result.hardpoint.yM) && same(i.zM, result.hardpoint.zM) &&
      result.beam.sourceFrame === 'SHIP_BODY_X_BOW_Y_STARBOARD_Z_UP' &&
      same(i.xM, result.beam.sourceXM) && same(i.yM, result.beam.sourceYM) && same(i.zM, result.beam.sourceZM),
    publicSbandBaseline: result.audit.band === 'S' && result.audit.frequencyMHz === 3050 && result.audit.peakPowerW === 30000 &&
      i.antennaApertureFt === 12 && result.audit.beamAzDeg === 2 && result.audit.beamElDeg === 30 && result.audit.antennaGainDb === 26,
    scanModel: result.audit.rpm === 30 && result.audit.highSpeedRpm === 50 && Math.abs(result.audit.nominalRevisitS - 2) < 1e-12 && result.beam.sensor === 'BRIDGEMASTER_E',
    pulseModes: result.audit.pulseModes.SHORT.pulseWidthUs === 0.05 && result.audit.pulseModes.SHORT.prfHz === 1800 &&
      result.audit.pulseModes.MEDIUM.pulseWidthUs === 0.25 && result.audit.pulseModes.LONG.pulseWidthUs === 0.75 && result.audit.pulseModes.LONG.prfHz === 785,
    trackDisplaySeparation: result.audit.trackCapacity === 60 && Math.abs(result.audit.trackMinKm / 1.852 - 0.25) < 1e-9 &&
      Math.abs(result.audit.trackMaxKm / 1.852 - 40) < 1e-9 && Math.abs(result.audit.displayScaleMaxKm / 1.852 - 96) < 1e-9 &&
      same(result.beam.trackRangeM, result.audit.trackMaxKm * 1000) && same(result.beam.rangeM, result.audit.trackMaxKm * 1000) &&
      same(result.beam.displayScaleMaxM, result.audit.displayScaleMaxKm * 1000),
    publishedNearRange: result.audit.publishedMinimumRangeLessThanM === 35 && result.audit.workingMinimumRangeM < 35 &&
      result.audit.publishedRangeResolutionBetterThanM === 35 && result.audit.workingRangeResolutionM < 35,
    renderContract: result.renderRevision === 'V48_WIP11_MATERIAL_PROTECTION' && result.shipProfile?.id === 'DDG_119_LATE_FLIGHT_IIA' && result.shipProfile?.presentationOnly === true && result.shipProfile?.physicsFeedback === false && result.renderReadOnly,
    ui: result.button.exists && result.button.text === 'BridgeMaster E' && !result.button.legacyExists,
    physicalMeshDeclared: source.includes("name='BRIDGEMASTER_E_12FT_OPEN_ARRAY'") && source.includes("name='BRIDGEMASTER_E_AUTHORITATIVE_ROTOR'"),
    photoDerivedMastOutfit: source.includes("mastOutfit.name='DDG119_PHOTO_DERIVED_MAST_OUTFIT'") &&
      source.includes("mastWires.name='DDG119_MAST_WHIP_AND_CABLE_BATCH'") && source.includes('duplicateFunctionalRadar:false')
  };
  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = { schema: 'AEGIS_BRIDGEMASTER_E_BROWSER_V48_WIP08', simulator,
    simulatorSha256: crypto.createHash('sha256').update(source).digest('hex'), checks, consoleErrors, pageErrors, result };
  fs.writeFileSync(`${artifactDir}/bridgemaster-e-results.json`, `${JSON.stringify(artifact, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
