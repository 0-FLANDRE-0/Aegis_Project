#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const { chromium } = require('playwright');

const [productPath, url, outputPath] = process.argv.slice(2);
if (!productPath || !url || !outputPath) {
  console.error('usage: baseline_oracle.cjs PRODUCT URL OUTPUT');
  process.exit(2);
}

const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const stableJson = value => JSON.stringify(value, (_key, item) => {
  if (item && typeof item === 'object' && !Array.isArray(item)) {
    return Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b)));
  }
  return item;
});

function compactControl(control) {
  return {
    revision: control.revision,
    step: control.step,
    recommendations: (control.recommendations || []).map(row => ({
      trackId: row.trackId,
      trackNumber: row.trackNumber ?? null,
      assessment: row.assessment,
      threatScore: row.threatScore,
      rangeKm: row.rangeKm,
      altM: row.altM,
      cpaM: row.cpaM,
      cpaTimeS: row.cpaTimeS,
      weapon: row.weapon,
      salvo: row.salvo,
      recommendedRounds: row.recommendedRounds ?? 0,
      salvoPolicy: row.salvoPolicy ?? null,
      firePlan: row.firePlan ? {
        status: row.firePlan.status,
        reason: row.firePlan.reason ?? null,
        fireDelayS: row.firePlan.fireDelayS ?? null,
        channelId: row.firePlan.channelId ?? null,
        requiresIlluminator: row.firePlan.requiresIlluminator ?? null,
      } : null,
    })),
  };
}

async function openOwner(browser, profileIndex) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error' && !/favicon\.ico|Failed to load resource.*404/i.test(msg.text())) {
      consoleErrors.push(msg.text());
    }
  });
  page.on('pageerror', error => pageErrors.push(String(error)));
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__AEGIS_SHIP_STARTUP__?.catalog?.().length >= 2, null, { timeout: 120000 });
  const profile = await page.evaluate(async index => {
    const catalog = window.__AEGIS_SHIP_STARTUP__.catalog();
    const own = catalog[index];
    const ally = catalog[index === 0 ? 1 : 0];
    window.__AEGIS_DEPLOYMENT_A__.setDraft({
      schema: 'AEGIS_DEPLOYMENT_MULTI_SHIP_F_1',
      targetShip: 'NONE',
      enemyProfileId: null,
      allyProfileId: ally.id,
      neutralProfileId: null,
      enemyAircraftEnabled: false,
      placementSeed: 1831565813,
      allyEmcon: false,
      enemyEmcon: false,
    });
    window.__AEGIS_SHIP_STARTUP__.select(own.id);
    await window.__AEGIS_STARTUP_PROMISE__;
    window.__NAVAL_SIM_DIAG__.setSeed(1831565813);
    window.__NAVAL_SIM_DIAG__.setBattlespaceSeed(1831565813);
    if (!window.__WIP125_DIAG__.confirmDeparture()) throw new Error('departure failed');
    return { own, ally, startup: window.__AEGIS_SHIP_STARTUP__.snapshot() };
  }, profileIndex);
  return { page, profile, consoleErrors, pageErrors };
}

async function ownerOracle(browser, profileIndex) {
  const { page, profile, consoleErrors, pageErrors } = await openOwner(browser, profileIndex);
  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    const ownId = window.__AEGIS_SHIP_STARTUP__.snapshot().entityId;
    const allyId = d.multiShipSnapshotA().ships.find(q => q.role === 'ALLY')?.entityId ?? null;
    d.setSeed(1831565813);
    const start = d.snapshot();
    const coreCallReturn = d.runCoreUnitSelfTests();
    const core = { callReturn: coreCallReturn, failures: [...(window.__CORE_SELFTEST_FAILURES__ || [])] };
    const isolation = d.multiShipIsolationAuditA();

    // 1. MANUAL/HOLD: the existing executor must not create a missile.
    const manualFixture = d.createTerminalAsmFixture({ label: 'Kh-35U', rangeKm: 15, altM: 15, speedMps: 260 });
    d.tacticalCommandH1(ownId, { enabled: true });
    d.wip119ResetAutonomy();
    d.wip119SetMode('MANUAL');
    const manualBefore = d.interceptorAudit().length;
    const manualState = d.wip119AutonomyTick(true);
    const manualAfter = d.interceptorAudit().length;
    const holdResult = allyId ? d.defenseCommandE(allyId, { mode: 'HOLD' }) : { ok: false, reason: 'NO_ALLY' };
    d.stepTicks(12);
    const holdDefense = d.defenseSnapshotE().ships.find(q => q.entityId === allyId) ?? null;

    // 2. Single threat / native salvo and mutation boundary.
    const singleFixture = d.createTerminalAsmFixture({ label: 'Kh-35U', rangeKm: 15, altM: 15, speedMps: 260 });
    d.wip118ResetControl();
    d.wip119ResetAutonomy();
    const singleControl = d.wip118ControlNow();
    const singleMutation = d.wip118MutationAudit();

    // 3. Multiple threats / priority order.
    const multiFixture = d.createSchedulerSaturationFixture({ count: 3, rangeKm: 24, altM: 25, speedMps: 310, relBearingDeg: 20, spreadDeg: 22 });
    d.wip118ResetControl();
    const multiControl = d.wip118ControlNow();

    // 4. H1 distribution with sufficient inventory, then below-reserve inventory.
    const inventoryFixture = d.createSchedulerSaturationFixture({ count: 4, rangeKm: 18, altM: 20, speedMps: 280, relBearingDeg: 15, spreadDeg: 18 });
    d.wip118ResetControl();
    const inventorySufficient = d.wip118ControlNow();
    const beforeReserve = d.wip119ReserveCheck('ESSM', 1);
    window.__WIP125_DIAG__.consume('ESSM', 1000);
    d.wip118ResetControl();
    const inventoryLow = d.wip118ControlNow();
    const afterReserve = d.wip119ReserveCheck('ESSM', 1);

    // 5. Re-engagement hysteresis and reserve brake.
    const reFixture = d.createTerminalAsmFixture({ label: 'Kh-35U', rangeKm: 14, altM: 15, speedMps: 260 });
    d.wip118ResetControl();
    d.wip119ResetAutonomy();
    const reBase = d.wip118ControlNow();
    const reWeapon = reBase.recommendations[0]?.weapon ?? 'ESSM';
    d.wip119PrimeResponse(reFixture.trackId, {
      autoEngagements: 1,
      autoEngagementsByLayer: { ESSM_BLK2_SIM: 1 },
      autoRounds: 2,
      lastAutoFireAgoS: 1,
      reengageThreatAgoS: 0.25,
      lastAssessment: 'THREAT',
      lastReengageRequired: true,
    });
    const reEvaluation = d.wip119EvaluateTrack(reFixture.trackId, true);
    const reLimit = d.wip123EngagementLimit(reFixture.trackId, reWeapon);

    // 6. LOST/coast and clean reacquisition boundary.
    const lostFixture = d.createTerminalAsmFixture({ label: 'Kh-35U', rangeKm: 16, altM: 15, speedMps: 260 });
    d.wip118ResetControl();
    const present = d.wip118ControlNow();
    d.wip118DiagDropTrack(lostFixture.trackId);
    d.wip118DiagAdvanceClock(0.4);
    const lost = d.wip118ControlNow();
    const reacquiredFixture = d.createTerminalAsmFixture({ label: 'Kh-35U', rangeKm: 16, altM: 15, speedMps: 260 });
    d.wip118ResetControl();
    const reacquired = d.wip118ControlNow();

    // 7. Cooperative assignment and local-FCS recheck.
    const networkFixture = d.createTerminalAsmFixture({ label: 'Kh-35U', rangeKm: 26, altM: 15, speedMps: 300 });
    d.stepTicks(180);
    const network = d.networkSnapshotG();
    const ownNetwork = network.ships.find(q => q.entityId === ownId);
    const allyNetwork = network.ships.find(q => q.entityId === allyId);
    const networkScene = {
      timeS: network.timeS,
      own: {
        peers: ownNetwork?.peers,
        leases: ownNetwork?.leases,
        stats: ownNetwork?.stats,
      },
      ally: {
        peers: allyNetwork?.peers,
        leases: allyNetwork?.leases,
        stats: allyNetwork?.stats,
      },
      ownGate: d.networkVlsGateProbeG(ownId, networkFixture.trackId, { automatic: true }),
      allyGate: allyId ? d.networkVlsGateProbeG(allyId, networkFixture.trackId, { automatic: true }) : null,
    };

    // 8/10. Immediate local defense and CMS/local-RF gates are existing self-tests.
    const localDefense = d.localDefenseSelfTestH4A();
    const ciws = d.ciwsAudit();
    const softKill = d.softKillDoctrineAudit();

    // 9. Damage / mission-unavailable contract, without changing a threshold.
    const moduleSnapshot = d.wip101ModuleDamageSnapshot();
    const damageCandidate = Object.keys(moduleSnapshot || {}).find(k => /CIC|CDC|VLS|SPY|SPG/i.test(k)) ?? Object.keys(moduleSnapshot || {})[0] ?? null;
    const damageBefore = d.equipmentOffline();
    const damageSet = damageCandidate ? d.wip101SetModuleDamage(damageCandidate, 100) : false;
    const spgBefore = d.wip116Spg62ReservationSnapshot();
    const spgDamageAttempts = [];
    for (let illId = 0; illId < 8; illId++) spgDamageAttempts.push({ illId, installed: !!d.wip116Spg62SetDamage(illId, 100) });
    const spgAfter = d.wip116Spg62ReservationSnapshot();
    const damageAfter = d.equipmentOffline();
    const damageControl = d.wip118ControlNow();

    // 11-13. H2/H3/H4 ownership and consent/command gates.
    const h1Own = d.tacticalCommandH1(ownId, { enabled: true });
    const h2Own = d.maneuverCommandH2(ownId, { enabled: true });
    const h2Ally = allyId ? d.maneuverCommandH2(allyId, { enabled: true }) : null;
    const h3Own = d.attackCommandH3(ownId, { enabled: true });
    const h3Ally = allyId ? d.attackCommandH3(allyId, { enabled: true }) : null;
    const h3Reject = d.attackCommandH3(ownId, { authorizeTrackId: 999999999, rounds: 1 });
    const h4Own = d.teamCommandH4(ownId, { enabled: true });
    const h4Ally = allyId ? d.teamCommandH4(allyId, { enabled: true }) : null;
    if (allyId) {
      d.teamCommandH4(ownId, { mission: 'ESCORT', formation: 'LINE_ASTERN', spacingM: 2000 });
      d.teamCommandH4(allyId, { mission: 'ESCORT', formation: 'LINE_ASTERN', spacingM: 2000 });
    }
    d.stepTicks(90);
    const hSnapshots = {
      h1: d.tacticalSnapshotH1(),
      h2: d.maneuverSnapshotH2(),
      h3: d.attackSnapshotH3(),
      h4: d.teamSnapshotH4(),
    };

    const save = JSON.stringify(d.exportOperationalStateV48Wip11A());
    const end = d.snapshot();
    // Diagnostic wall-clock duration only. It is not fixed-tick game state and the
    // baseline contract explicitly excludes diagnostic execution time.
    if (spgBefore?.meta) delete spgBefore.meta.lastPlanMs;
    if (spgAfter?.meta) delete spgAfter.meta.lastPlanMs;
    return {
      owner: { ownId, allyId, profileId: window.__AEGIS_SHIP_STARTUP__.snapshot().profileId },
      rng: { start: start.simRngState, end: end.simRngState },
      core,
      isolation,
      manualHold: {
        fixture: manualFixture,
        mode: manualState.mode,
        missileDelta: manualAfter - manualBefore,
        candidateRows: manualState.candidateRows,
        holdResult,
        allyModeAfter: holdDefense?.mode ?? null,
        allyFireLogCount: holdDefense?.autonomy?.fireLog?.length ?? null,
      },
      singleThreat: { fixture: singleFixture, control: singleControl, mutation: singleMutation },
      multipleThreats: { fixture: multiFixture, control: multiControl },
      inventoryDistribution: { fixture: inventoryFixture, sufficient: inventorySufficient, beforeReserve, low: inventoryLow, afterReserve },
      reengagement: { fixture: reFixture, base: reBase, evaluation: reEvaluation, limit: reLimit },
      lifecycle: { presentFixture: lostFixture, present, lost, reacquiredFixture, reacquired },
      network: networkScene,
      immediateDefense: { localDefense, ciws, softKill },
      damageUnavailable: { damageCandidate, damageBefore, damageSet, damageAfter, spgBefore, spgDamageAttempts, spgAfter, control: damageControl },
      hierarchy: { commands: { h1Own, h2Own, h2Ally, h3Own, h3Ally, h3Reject, h4Own, h4Ally }, snapshots: hSnapshots },
      save,
      finalState: {
        step: end.simStepCounter,
        rng: end.simRngState,
        shipHP: end.shipHP,
        hitCount: end.shipHitCount,
        missileCount: end.interceptorState.length,
      },
    };
  });

  const saveText = result.save;
  delete result.save;
  result.saveSnapshot = { bytes: Buffer.byteLength(saveText), sha256: sha256(saveText), schema: JSON.parse(saveText).schema };
  for (const key of ['singleThreat', 'multipleThreats']) result[key].control = compactControl(result[key].control);
  result.inventoryDistribution.sufficient = compactControl(result.inventoryDistribution.sufficient);
  result.inventoryDistribution.low = compactControl(result.inventoryDistribution.low);
  result.reengagement.base = compactControl(result.reengagement.base);
  result.lifecycle.present = compactControl(result.lifecycle.present);
  result.lifecycle.lost = compactControl(result.lifecycle.lost);
  result.lifecycle.reacquired = compactControl(result.lifecycle.reacquired);
  result.damageUnavailable.control = compactControl(result.damageUnavailable.control);
  result.browser = { consoleErrors, pageErrors };
  await page.close();
  return { profile, result };
}

(async () => {
  const product = fs.readFileSync(productPath);
  const executablePath = process.env.AEGIS_CHROMIUM_EXECUTABLE
    || (fs.existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined);
  const browser = await chromium.launch({
    headless: true,
    ...(executablePath ? { executablePath } : {}),
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  try {
    const owners = [];
    for (const index of [0, 1]) owners.push(await ownerOracle(browser, index));
    const payload = {
      schema: 'AEGIS_INTEGRATION_BASELINE_ORACLE_A_1',
      capturedFrom: {
        product: productPath.split('/').at(-1),
        bytes: product.length,
        sha256: sha256(product),
        browser: await browser.version(),
        playwright: require('playwright/package.json').version,
        fixedSeed: 1831565813,
      },
      semantics: {
        diagnosticTruthSetupOnly: true,
        liveDecisionInputsObservedOnly: true,
        excludedFromComparison: ['wallClock', 'diagnosticDuration', 'lastBuildMs', 'lastAssessmentMs', 'lastPlanMs'],
        scenarios: [
          'MANUAL_HOLD_ZERO_AUTO_FIRE', 'SINGLE_THREAT_NATIVE_SALVO', 'MULTI_THREAT_PRIORITY',
          'H1_INVENTORY_DISTRIBUTION', 'REENGAGEMENT_AND_RESERVE', 'LOST_COAST_REACQUIRE',
          'NETWORK_ASSIGNMENT_AND_LOCAL_FCS', 'EMERGENCY_LOCAL_DEFENSE', 'DAMAGE_MISSION_UNAVAILABLE',
          'CIWS_CMS_LOCAL_RF', 'H2_MANEUVER_OVERRIDE', 'H3_SURFACE_CONSENT', 'H4_TEAM_FORMATION',
          'DDG_CG_ACTIVE_FOREIGN_ROLE_PARITY',
        ],
      },
      owners,
    };
    payload.deterministicDigest = sha256(stableJson(payload.owners));
    fs.writeFileSync(outputPath, JSON.stringify(payload, null, 2) + '\n');
    console.log(JSON.stringify({ outputPath, owners: owners.length, deterministicDigest: payload.deterministicDigest }));
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error.stack || error);
  process.exit(1);
});
