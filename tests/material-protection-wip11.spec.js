const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12D.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/material-protection-wip11';

test('v48 WIP11 derives mass and penetration from one material/thickness ledger', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.materialProtectionAuditV48Wip11, null, { timeout: 45_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    const auditA = d.materialProtectionAuditV48Wip11(), auditB = d.materialProtectionAuditV48Wip11();
    const ref = d.materialPlateProbeV48Wip11({ diameterM:.42, boundaryIds:['SHELL_UPPER','SHELL_BOTTOM_BILGE','FLIGHT_DECK','CIC_LOCAL','MAGAZINE_LOCAL','WATERTIGHT_DOOR'] });
    const shell127 = d.materialPlateProbeV48Wip11({ diameterM:.127, boundaryIds:['SHELL_UPPER','MAGAZINE_LOCAL'] });
    const openDoor = d.materialBoundaryMetricsV48Wip11('WATERTIGHT_DOOR',{ diameterM:.42, open:true });
    const fragmentProbe = d.aramidFragmentProbeV48Wip11();
    const upper = d.materialPenetrationProbeV48Wip11({ system:'HULL_SKIN', deck:'ABOVE_WL', label:'Kh-35U', impactSpeedMps:280 });
    const lower = d.materialPenetrationProbeV48Wip11({ system:'HULL_SKIN', deck:'BELOW_WL', label:'Kh-35U', impactSpeedMps:280 });
    return { auditA, auditB, ref, shell127, openDoor, fragmentProbe, upper, lower, profile:d.shipProfileV48Wip11(), selftestFailures:window.__CORE_SELFTEST_FAILURES__.slice() };
  });
  const rows = Object.fromEntries(result.ref.rows.map(row => [row.id, row]));
  const rows127 = Object.fromEntries(result.shell127.rows.map(row => [row.id, row]));
  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftestFailures.length === 0,
    auditPass: result.auditA.pass && Object.values(result.auditA.checks).every(Boolean),
    deterministicAudit: JSON.stringify(result.auditA) === JSON.stringify(result.auditB),
    activeContract: result.profile.protection.status === 'ACTIVE_PHYSICS_COUPLED' && result.profile.protection.physicsCoupled === true,
    underwaterStronger: rows.SHELL_BOTTOM_BILGE.directResistanceMJ > rows.SHELL_UPPER.directResistanceMJ && result.lower.box.referenceResistanceMJ > result.upper.box.referenceResistanceMJ,
    referenceResistance: rows.SHELL_UPPER.directResistanceMJ > .90 && rows.SHELL_UPPER.directResistanceMJ < .94 && rows.FLIGHT_DECK.directResistanceMJ > .48 && rows.FLIGHT_DECK.directResistanceMJ < .51,
    projectileAreaScaling: rows127.SHELL_UPPER.directResistanceMJ < rows.SHELL_UPPER.directResistanceMJ && rows127.MAGAZINE_LOCAL.directResistanceMJ < rows.MAGAZINE_LOCAL.directResistanceMJ,
    aramidSeparated: rows.CIC_LOCAL.layers.find(q=>q.materialId==='ARAMID_SPLINTER').directResistanceMJ === 0 && rows.MAGAZINE_LOCAL.layers.find(q=>q.materialId==='ARAMID_SPLINTER').directResistanceMJ === 0 && rows.MAGAZINE_LOCAL.fragmentTransmission01 < 1 && rows.MAGAZINE_LOCAL.rearSpallTransmission01 < 1,
    aramidLiveFragmentPath: result.fragmentProbe.pass && Object.values(result.fragmentProbe.checks).every(Boolean) && result.auditA.checks.fragmentPropagationCoupled,
    openDoorZero: rows.WATERTIGHT_DOOR.directResistanceMJ > 0 && result.openDoor.directResistanceMJ === 0 && result.openDoor.fragmentTransmission01 === 1,
    livePenetrationCoupled: result.upper.solved.barrierTrace[0].model === 'MATERIAL_THICKNESS' && result.lower.solved.barrierTrace[0].model === 'MATERIAL_THICKNESS',
    massClosure: result.auditA.massLedger.structuralMaterialMassKg > 0 && result.auditA.massLedger.residualOutfitMassKg > 0 && Math.abs(result.auditA.massLedger.lightshipClosureKg - result.profile.mass.lightshipKg) < 1e-6,
  };
  fs.mkdirSync(artifactDir, { recursive:true });
  fs.writeFileSync(`${artifactDir}/material-protection-results.json`, `${JSON.stringify({ schema:'AEGIS_MATERIAL_PROTECTION_BROWSER_V48_WIP11', simulator, simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'), checks, consoleErrors, pageErrors, result }, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
