const { test, expect } = require('@playwright/test');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP12E_REV5_NAVAL_ARMOR_FUZE_COUPLING.html';

test.use({ viewport:{ width:1600, height:900 } });

async function loadSimulator(page) {
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481232; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() =>
    Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
    window.__NAVAL_SIM_DIAG__?.wip12eRev5NavalArmorFuzeDiagnostics,
  null, { timeout:60_000 });
  return { consoleErrors, pageErrors };
}

test('WIP12E REV5 qualifies both ASMs and separates thin-skin blowout from thick-armor shock', async ({ page }) => {
  test.setTimeout(180_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    return {
      title:document.title,
      selftests:window.__CORE_SELFTEST_FAILURES__.slice(),
      armor:d.wip12eRev5NavalArmorFuzeDiagnostics(),
      core:d.wip12eCompartmentBlastDiagnostics(),
      fixtures:d.wip12eBlastFixtureDiagnostics(),
      budget:d.wip12eBlastBudgetProbe(),
      ordnance:d.wip12bLiveOrdnance()
    };
  });

  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    title:result.title === 'AEGIS v48 WIP12E REV5 — Naval Armor & Fuze Coupling',
    selftests:result.selftests.length === 0,
    armor:result.armor.pass && Object.values(result.armor.checks).every(Boolean),
    thresholds:result.armor.checks.threshold8 && result.armor.checks.threshold12 && result.armor.checks.threshold20 && result.armor.checks.grazingCannotSelfQualify,
    liveASMs:result.armor.liveProfiles.KH32 === 'ANTI_SHIP_DELAY_8' && result.armor.liveProfiles.KH35U === 'ANTI_SHIP_DELAY_8',
    thinBlowout:result.armor.external.thinCoupling.mode === 'EXTERNAL_BLAST_BLOWOUT' && result.armor.external.thinCoupling.externalBlowout.failed && result.armor.external.thin.externalBlowouts === 1,
    thickHold:result.armor.external.thickCoupling.mode === 'NON_PERFORATING_EXTERNAL_DETONATION' && !result.armor.external.thickCoupling.externalBlowout.failed && result.armor.external.thick.breaches === 0,
    energyClosed:result.armor.checks.externalBlowoutEnergyClosed,
    generic:result.armor.checks.genericCarrierContract,
    inheritedBlast:result.core.pass && result.fixtures.pass && result.budget.pass
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('WIP12E REV5 live Kh-32 and Kh-35U share the generic blast consumer without crashing', async ({ page }) => {
  test.setTimeout(300_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d.wip12eSetBlastMode('COMPARTMENT_BLAST_AUTHORITY');
    const run = (label, weaponKey, seed, maxTimeS) => {
      const flight = d.runWip107AsmMemoryCase({ label, rangeKm:100, maxTimeS, seed });
      const event = d.wip12bTerminalEvents().find(row => row.weaponKey === weaponKey);
      const trace = d.wip12eBlastTrace(event?.impactEventId);
      return {
        flight:{ durationS:flight.durationS, shipHit:flight.shipHit, deathReason:flight.deathReason },
        event,
        trace,
        status:d.wip12eRev5DamageCouplingStatus(),
        hit:d.snapshot().shipLastHit
      };
    };
    return {
      kh32:run('Kh-32', 'KH32', 481232, 300),
      kh35:run('Kh-35U', 'KH35U', 481235, 600),
      selftests:window.__CORE_SELFTEST_FAILURES__.slice()
    };
  });

  const closed = trace => Math.abs(trace.ledger.airClosureErrorJ) <= Math.max(1e-5, trace.ledger.airBlastEnergyJ * 1e-9);
  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    selftests:result.selftests.length === 0,
    kh32Hit:result.kh32.flight.shipHit && result.kh32.flight.deathReason === 'NORMAL_HIT' && Math.abs(result.kh32.flight.durationS - 92.78333333333333) < 1e-9,
    kh32ThroughEntry:result.kh32.trace.boundaryCoupling.mode === 'EXTERNAL_DETONATION_THROUGH_ENTRY' && result.kh32.trace.breaches.some(row => row.kind === 'BLAST_ENTRY_BLOWOUT'),
    kh32DamageAndFire:result.kh32.trace.damagePacket.moduleDamage.length >= 30 && result.kh32.trace.damagePacket.compartmentDamage.length >= 12 && result.kh32.trace.damagePacket.ignitionCandidates.filter(row => row.ignite).length >= 5,
    kh35Hit:result.kh35.flight.shipHit && result.kh35.flight.deathReason === 'NORMAL_HIT' && result.kh35.event.weaponKey === 'KH35U',
    kh35Damage:result.kh35.trace.damagePacket.moduleDamage.length >= 20 && result.kh35.trace.damagePacket.compartmentDamage.length >= 12,
    authority:[result.kh32, result.kh35].every(row => row.trace.mode === 'COMPARTMENT_BLAST_AUTHORITY' && row.hit.blastAuthority === 'COMPARTMENT_BLAST_AUTHORITY'),
    energy:[result.kh32.trace, result.kh35.trace].every(closed),
    rng:[result.kh32.trace, result.kh35.trace].every(trace => trace.rngUnchanged),
    consumers:[result.kh32.status, result.kh35.status].every(status => status.damageIssues.length === 0)
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('WIP12E REV5 cumulative bridge damage disables SPY and keeps every 2D scar', async ({ page }) => {
  test.setTimeout(300_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(async () => {
    const d = window.__NAVAL_SIM_DIAG__;
    d._resetShipTest();
    d.wip12eSetBlastMode('COMPARTMENT_BLAST_AUTHORITY');
    const detonation = { x:34, y:0, z:12 };
    const entry = { x:34, y:10, z:12 };
    const packet = index => ({
      schema:'AEGIS_DAMAGE_PACKET_V48_WIP12A', impactEventId:`WIP12E_REV5_BRIDGE_${index}`,
      sourceProjectileId:`GENERIC_EXPLOSIVE_${index}`, targetEntityId:'OWN_SHIP',
      projectile:{ caliberM:.92, speedMps:900, massKg:5800 }, path:{ start:entry, stop:detonation },
      directPenetration:[], penetrationCorridors:[{ start:entry, stop:detonation, caliberM:.92, kineticBeforeJ:0, kineticAfterJ:0, entryOpeningAreaM2:0, exitOpeningAreaM2:0 }],
      breaches:[], blast:[{ position:detonation, explosiveMassKg:500, tntEquivalentKg:500, medium:'CLOSED' }],
      structuralImpulse:[], warheadFragments:[{ casingMassKg:250 }], thermalIncendiary:[]
    });
    const rows = [];
    let firstScarIds = [];
    for (let index=1; index<=3; index++) {
      const application = d.wip12aApplyDamagePacket(packet(index), { commit:true, emitVisualEvent:true });
      const visual = d.v48Wip03DamageVisualState();
      if (index === 1) firstScarIds = visual.scars.map(row => row.id);
      rows.push({ application, status:d.wip12eRev5DamageCouplingStatus(), scars:visual.scars.map(row => row.id) });
    }
    const panel = document.getElementById('shipDetailPanel');
    if (panel) panel.style.display = 'block';
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const before = d.v48Wip03DamageVisualState();
    const twoDBefore = d.wip12eRev5TwoDScarAudit();
    d.stepTicks(Math.ceil(130 / (1 / 60)));
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    const after = d.v48Wip03DamageVisualState();
    const twoDAfter = d.wip12eRev5TwoDScarAudit();
    return { rows, firstScarIds, before, after, twoDBefore, twoDAfter, selftests:window.__CORE_SELFTEST_FAILURES__.slice() };
  });

  const [one, two, three] = result.rows;
  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    selftests:result.selftests.length === 0,
    applied:[one, two, three].every(row => row.application.accepted && row.application.reason === 'APPLIED'),
    oneHitSurvives:Object.values(one.status.spyOperational).every(Boolean),
    twoHitsDisableForward:!two.status.spyOperational.F1 && !two.status.spyOperational.F2 && two.status.spyOperational.F3 && two.status.spyOperational.F4,
    threeHitsDisableAll:Object.values(three.status.spyOperational).every(value => value === false),
    exceedsOldCap:result.before.scars.length > 96,
    persists:result.firstScarIds.every(id => three.scars.includes(id)) && result.firstScarIds.every(id => result.after.scars.some(row => row.id === id)),
    noAgeRepair:result.after.scars.length >= result.before.scars.length,
    twoDParity:result.twoDBefore.sourceScars === result.before.scars.length && result.twoDBefore.topDrawn === result.before.scars.length && result.twoDBefore.sideDrawn === result.before.scars.length,
    twoDAfter:result.twoDAfter.sourceScars === result.after.scars.length && result.twoDAfter.topDrawn === result.after.scars.length && result.twoDAfter.sideDrawn === result.after.scars.length
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});
