const path = require('node:path');

let playwrightTest;
try {
  playwrightTest = require('@playwright/test');
} catch {
  playwrightTest = require('playwright/test');
}
const { test, expect } = playwrightTest;

const simulator = path.resolve(process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12F.html'));
const simulatorUrl = process.env.SIM_URL || `file://${simulator}`;
const launchOptions = process.env.WIP12F_CHROMIUM_PATH
  ? { executablePath:process.env.WIP12F_CHROMIUM_PATH }
  : undefined;

test.use({ viewport:{ width:1600, height:900 }, launchOptions });

async function loadSimulator(page) {
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481232; });
  await page.goto(simulatorUrl, { waitUntil:'load', timeout:120_000 });
  await page.waitForFunction(() =>
    Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
    window.__NAVAL_SIM_DIAG__?.wip12fTerminalHardeningDiagnostics,
  null, { timeout:60_000 });
  return { consoleErrors, pageErrors };
}

test('WIP12F closes terminal-ballistics invariants without regressing WIP12A-E', async ({ page }) => {
  test.setTimeout(180_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    const names = [
      'wip12aTerminalDiagnostics',
      'wip12aDamagePacketIdempotence',
      'wip12bTerminalDiagnostics',
      'wip12cInternalEffectsDiagnostics',
      'wip12dResidualOverpenetrationDiagnostics',
      'wip12eCompartmentBlastDiagnostics',
      'wip12eBlastFixtureDiagnostics',
      'wip12eBlastAuthorityProbe',
      'wip12eBlastIdempotenceProbe',
      'wip12eBlastBudgetProbe',
      'wip12eRev5NavalArmorFuzeDiagnostics'
    ];
    const rngBefore = d.snapshot().rngState;
    const first = d.wip12fTerminalHardeningDiagnostics();
    const second = d.wip12fTerminalHardeningDiagnostics();
    return {
      title:document.title,
      bodyText:document.body?.innerText ?? '',
      selftests:window.__CORE_SELFTEST_FAILURES__.slice(),
      contract:d.wip12fTerminalHardeningContract(),
      first,
      deterministic:JSON.stringify(first) === JSON.stringify(second),
      inherited:Object.fromEntries(names.map(name => [name, d[name]() ])),
      rngBefore,
      rngAfter:d.snapshot().rngState
    };
  });

  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    title:result.title === 'AEGIS v48 WIP12F — Terminal Ballistics Closure',
    nonBlank:result.bodyText.trim().length > 500,
    selftests:result.selftests.length === 0,
    contract:result.contract.schema === 'AEGIS_TERMINAL_HARDENING_V48_WIP12F' && result.contract.boundaryDamage.partialTraversalCreatesOpening === false,
    hardening:result.first.pass && Object.values(result.first.checks).every(Boolean),
    deterministic:result.deterministic,
    inherited:Object.values(result.inherited).every(row => row.pass === true),
    partialNoOpening:result.first.partial.outcome === 'PARTIAL' && result.first.partial.holeAreaM2 === 0 && result.first.partial.breaches === 0,
    spallAttenuates:result.first.spall.armor[0].attenuation01 > result.first.spall.armor[1].attenuation01 && result.first.spall.armor[1].attenuation01 > result.first.spall.armor[2].attenuation01,
    directAndContact:result.first.checks.directActionInitiatesBeforeBodyFracture && result.first.checks.contactTimerStartsAtBoundary,
    postExit:result.first.postExit.schema === 'AEGIS_POST_EXIT_PROJECTILE_HANDOFF_V48_WIP12F' && result.first.postExit.liveFuze,
    persistentPatch:result.first.persistence.secondResistanceJ < result.first.persistence.firstResistanceJ && result.first.persistence.snapshot.count === 1,
    rng:result.rngBefore === result.rngAfter && result.first.checks.combatRngUnchanged
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('WIP12F live Kh-32 and Kh-35U deliver blast, spall, crew, fire, and armor persistence once', async ({ page }) => {
  test.setTimeout(300_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d.wip12eSetBlastMode('COMPARTMENT_BLAST_AUTHORITY');
    const run = (label, weaponKey, seed, maxTimeS) => {
      const flight = d.runWip107AsmMemoryCase({ label, rangeKm:100, maxTimeS, seed });
      const event = d.wip12bTerminalEvents().find(row => row.weaponKey === weaponKey);
      const trace = d.wip12eBlastTrace(event?.impactEventId);
      const hit = d.snapshot().shipLastHit;
      const crew = d.v48Wip07CrewState().damageEvents.find(row => row.id === event?.impactEventId);
      const status = d.wip12eRev5DamageCouplingStatus();
      const render = window.get3DRenderState?.();
      return {
        flight:{ durationS:flight.durationS, shipHit:flight.shipHit, deathReason:flight.deathReason },
        event,
        trace,
        hit,
        crew,
        patch:d.wip12fArmorPatches(),
        render:{ revision:render?.terminalEffectsRevision, armorPatches:render?.armorDamagePatches?.count },
        burning:d.damageControlSnapshotV1().summary.burning,
        damagedModules:Object.values(d.wip101ModuleDamageSnapshot()).filter(value => value > 0).length,
        status
      };
    };
    return {
      kh32:run('Kh-32', 'KH32', 481232, 300),
      kh35:run('Kh-35U', 'KH35U', 481235, 600),
      selftests:window.__CORE_SELFTEST_FAILURES__.slice()
    };
  });

  const energyClosed = trace => Math.abs(trace.ledger.closureErrorJ) <= Math.max(1e-5, trace.ledger.chemicalEnergyJ * 1e-9);
  const valid = row => row.flight.shipHit && row.flight.deathReason === 'NORMAL_HIT' &&
    row.event.applicationAuthority === 'WIP12E_BLAST_OBSERVED_ALREADY_APPLIED' &&
    row.event.damageAppliedBy === 'WIP12E_COMPARTMENT_BLAST_AUTHORITY' &&
    row.trace.mode === 'COMPARTMENT_BLAST_AUTHORITY' && row.trace.damagePacket.moduleDamage.length >= 20 &&
    row.trace.damagePacket.compartmentDamage.length >= 12 && row.trace.damagePacket.ignitionCandidates.some(q => q.ignite) &&
    row.crew.kineticSpallSourceCount === 1 && row.crew.kineticSpallEnergyJ > 0 && row.crew.usedSharedBlastTrace &&
    row.hit.armorPatchAudit.committed === 1 && row.hit.kineticSpallSources.length === 1 &&
    row.patch.count === 1 && row.damagedModules >= 20 && row.burning >= 1 &&
    row.render.revision === 'V48_WIP12F_TERMINAL_HARDENING' && row.render.armorPatches === 1 &&
    row.trace.rngUnchanged && energyClosed(row.trace) && row.status.damageIssues.length === 0;

  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    selftests:result.selftests.length === 0,
    kh32:valid(result.kh32),
    kh35:valid(result.kh35),
    kh32Golden:Math.abs(result.kh32.flight.durationS - 92.78333333333333) < 1e-9,
    kh35Golden:Math.abs(result.kh35.flight.durationS - 345.81666666666666) < 1e-9,
    bothWeapons:[result.kh32, result.kh35].map(row => row.event.weaponKey).join(',') === 'KH32,KH35U'
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('WIP12F DUD impact keeps kinetic damage and a persistent scar without inventing a blast', async ({ page }) => {
  test.setTimeout(180_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    d._resetShipTest();
    const before = {
      scars:d.v48Wip03DamageVisualState().scars.length,
      patches:d.wip12fArmorPatches().count,
      blastTraces:d.wip12eBlastTraces().length
    };
    const probe = d.runWip113DudImpactProbe({ dud:true, rangeKm:2.4, altM:12, speedMps:280, seed:481233 });
    const hit = d.snapshot().shipLastHit;
    const crew = d.v48Wip07CrewState().damageEvents.at(-1);
    return {
      before,
      probe,
      hit,
      crew,
      after:{
        scars:d.v48Wip03DamageVisualState().scars.length,
        patches:d.wip12fArmorPatches().count,
        blastTraces:d.wip12eBlastTraces().length
      },
      selftests:window.__CORE_SELFTEST_FAILURES__.slice()
    };
  });

  const checks = {
    pageLoad:errors.consoleErrors.length === 0 && errors.pageErrors.length === 0,
    selftests:result.selftests.length === 0,
    dud:result.probe.dud === true && result.hit.dud === true,
    noBlast:result.after.blastTraces === result.before.blastTraces && result.hit.blastSources.length === 0,
    kineticSpall:result.hit.kineticSpallSources.length === 1 && result.crew.kineticSpallSourceCount === 1,
    persistentScar:result.after.scars > result.before.scars,
    persistentArmorPatch:result.hit.armorPatchAudit.committed === 1 && result.after.patches > result.before.patches
  };
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('WIP12F cumulative bridge blasts disable SPY while every 2D scar remains persistent', async ({ page }) => {
  test.setTimeout(300_000);
  const errors = await loadSimulator(page);
  const result = await page.evaluate(async () => {
    const d = window.__NAVAL_SIM_DIAG__;
    d._resetShipTest();
    d.wip12eSetBlastMode('COMPARTMENT_BLAST_AUTHORITY');
    const detonation = { x:34, y:0, z:12 };
    const entry = { x:34, y:10, z:12 };
    const packet = index => ({
      schema:'AEGIS_DAMAGE_PACKET_V48_WIP12A',
      impactEventId:`WIP12F_BRIDGE_${index}`,
      sourceProjectileId:`GENERIC_EXPLOSIVE_${index}`,
      targetEntityId:'OWN_SHIP',
      projectile:{ caliberM:.92, speedMps:900, massKg:5800 },
      path:{ start:entry, stop:detonation },
      directPenetration:[], penetrationCorridors:[{ start:entry, stop:detonation, caliberM:.92, kineticBeforeJ:0, kineticAfterJ:0, entryOpeningAreaM2:0, exitOpeningAreaM2:0 }],
      plugAndSpall:[], breaches:[], structuralImpulse:[], crewExposure:[], armorDamagePatches:[], diagnosticPatches:[],
      blast:[{ position:detonation, explosiveMassKg:500, tntEquivalentKg:500, medium:'CLOSED' }],
      warheadFragments:[{ casingMassKg:250 }], thermalIncendiary:[]
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
