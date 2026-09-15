const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP09.html';
const baselineSimulator = process.env.BASELINE_SIM_FILE || 'Aegis_SIM_v48_WIP08.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/ship-profile';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP09 immutable DDG-119 profile drives isolated runtime and renderer', async ({ page }) => {
  test.setTimeout(180_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil: 'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
    window.__NAVAL_SIM_DIAG__?.shipProfileAuditV48Wip09 && window.get3DRenderState, null, { timeout: 30_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__, profileBefore = JSON.stringify(d.shipProfileV48Wip09());
    const exposed = window.__AEGIS_ACTIVE_SHIP_PROFILE__;
    try { exposed.geometry.bowXM = 999; exposed.geometry.hullStations[0][0] = 999; } catch {}
    const auditA = d.shipProfileAuditV48Wip09(), auditB = d.shipProfileAuditV48Wip09();
    const profile = d.shipProfileV48Wip09(), runtime = d.shipRuntimeBindingsV48Wip09(), render = window.get3DRenderState();
    return { profileBefore, profileAfter: JSON.stringify(profile), auditA, auditB, profile, runtime,
      render: { revision: render.revision, shipProfile: render.shipProfile, hardpoints: render.hardpoints, vls: { forwardCells: render.vls.forwardCells, aftCells: render.vls.aftCells } },
      selftestFailures: window.__CORE_SELFTEST_FAILURES__.slice(), exposedFrozen: Object.isFrozen(exposed) && Object.isFrozen(exposed.geometry) && Object.isFrozen(exposed.geometry.hullStations[0]) };
  });

  const source = fs.readFileSync(simulator, 'utf8');
  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftestFailures.length === 0,
    auditPass: result.auditA.pass === true && Object.values(result.auditA.checks).every(Boolean),
    deterministicAudit: JSON.stringify(result.auditA) === JSON.stringify(result.auditB),
    immutable: result.exposedFrozen && result.profileBefore === result.profileAfter && result.profile.geometry.bowXM === 82,
    identity: result.profile.id === 'DDG_119_LATE_FLIGHT_IIA' && result.profile.identity.hullNumber === 'DDG-119',
    isolatedRuntime: result.runtime.profileId === result.profile.id && result.runtime.navigationIsMutable === true && result.auditA.checks.runtimeSeparated === true,
    modelBindings: Object.values(result.auditA.registries).every(Boolean) && Object.values(result.auditA.consumerParity).every(Boolean),
    topologyCrew: result.auditA.counts.spaces === 138 && result.auditA.counts.portals === 160 && result.auditA.counts.equipment === 70 && result.auditA.counts.crew === 310,
    loadout: result.auditA.counts.vlsForward === 32 && result.auditA.counts.vlsAft === 64 && result.render.vls.forwardCells === 32 && result.render.vls.aftCells === 64,
    protectionDeferred: result.profile.protection.status === 'SCHEMA_ONLY_DEFERRED_TO_WIP10' && result.profile.protection.physicsCoupled === false,
    rendererProfileBound: result.render.revision === 'V48_WIP09_SHIP_PROFILE' && result.render.shipProfile.id === result.profile.id && result.render.shipProfile.presentationOnly === true && result.render.shipProfile.physicsFeedback === false,
    bridgeMasterParity: result.render.hardpoints.bridgeMasterE.xM === 15.75 && result.render.hardpoints.bridgeMasterE.yM === 5.15 && result.render.hardpoints.bridgeMasterE.zM === 31.78,
    baselineDeclared: result.profile.parity.baselineSha256 === 'fe537db57d08f7c87120ed80a6118acd7c83389e75169e3fde9d404834f67eb8' && result.profile.parity.expectedBehavior === 'NO_GAMEPLAY_CHANGE',
  };
  fs.mkdirSync(artifactDir, { recursive: true });
  const artifact = { schema: 'AEGIS_SHIP_PROFILE_BROWSER_V48_WIP09', simulator,
    simulatorSha256: crypto.createHash('sha256').update(source).digest('hex'), checks, consoleErrors, pageErrors, result };
  fs.writeFileSync(`${artifactDir}/ship-profile-results.json`, `${JSON.stringify(artifact, null, 2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key, true])));
});

test('v48 WIP09 preserves deterministic WIP08 ship behavior', async ({ page }) => {
  test.setTimeout(300_000);
  const capture = async file => {
    await page.goto(`http://127.0.0.1:4173/${file}`, { waitUntil: 'load' });
    await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) &&
      window.__NAVAL_SIM_DIAG__?.runV48Wip02ImpactProbe && window.get3DRenderState, null, { timeout: 30_000 });
    return page.evaluate(() => {
      const d = window.__NAVAL_SIM_DIAG__;
      d.setSeed(4809001);
      const impact32 = d.runV48Wip02ImpactProbe('Kh-32'), impact35 = d.runV48Wip02ImpactProbe('Kh-35U');
      const wave = d.runV48Wip05WaveFloodProbe({ hsM: 2, tpS: 8, directionDeg: 90, seed: 4805, durationS: 3, sampleEveryS: .5, speedKt: 15, headingDeg: 90, xM: 12, zM: -1, areaM2: .08 });
      const interior = d.runV48Wip06InteriorProbe(), crew = d.runV48Wip07CrewDamageProbe({ readCount: 0 });
      const mass = d.shipMassLedger(), render = window.get3DRenderState(), bridge = d.bridgeMasterEAudit();
      const impact = q => ({ rawKineticEnergyMJ:q.impact.rawKineticEnergyMJ,impactMomentumNs:q.impact.impactMomentumNs,throughHull:q.impact.throughHull,physicalPenetrationM:q.impact.physicalPenetrationM,hullExitDistanceM:q.impact.hullExitDistanceM,exitEnergyMJ:q.impact.exitEnergyMJ,openings:q.impact.openings,rigidBodyDelta:q.rigidBodyDelta });
      return {
        selftestFailures:window.__CORE_SELFTEST_FAILURES__.slice(),
        impact32:impact(impact32),impact35:impact(impact35),
        wave:{input:wave.input,summary:wave.summary,samples:wave.samples},
        interior:{checks:interior.checks,summary:interior.base.summary,audit:interior.base.audit,locatedSpace:interior.locatedSpace},
        crew:{checks:crew.checks,base:crew.base,route:{spaces:crew.route.spaces,distanceM:crew.route.distanceM,etaS:crew.route.etaS},stretcherRoute:{spaces:crew.stretcherRoute.spaces,distanceM:crew.stretcherRoute.distanceM,etaS:crew.stretcherRoute.etaS},damage:crew.damage,totals:crew.totals,medical:crew.medical},
        mass:{schema:mass.schema,massKg:mass.massKg,cgM:mass.cgM,lightshipMassKg:mass.lightshipMassKg,variableLoadKg:mass.variableLoadKg,categoryMassKg:mass.categoryMassKg,nodeCount:mass.nodeCount},
        render:{hardpoints:render.hardpoints,vls:{forwardCells:render.vls.forwardCells,aftCells:render.vls.aftCells,counts:render.vls.counts},interior:{schema:render.shipInteriorTopology.schema,summary:render.shipInteriorTopology.summary},crew:{schema:render.shipCrewSpatial.schema,total:render.shipCrewSpatial.total,fit:render.shipCrewSpatial.fit}},
        bridge:{band:bridge.band,frequencyMHz:bridge.frequencyMHz,rpm:bridge.rpm,nominalRevisitS:bridge.nominalRevisitS,peakPowerW:bridge.peakPowerW,pulseModes:bridge.pulseModes,trackMinKm:bridge.trackMinKm,trackMaxKm:bridge.trackMaxKm,displayScaleMaxKm:bridge.displayScaleMaxKm,heightM:bridge.heightM}
      };
    });
  };
  const baseline = await capture(baselineSimulator), current = await capture(simulator);
  const checks = { baselineSelftests: baseline.selftestFailures.length === 0, currentSelftests: current.selftestFailures.length === 0, exactBehaviorParity: JSON.stringify(current) === JSON.stringify(baseline) };
  fs.mkdirSync(artifactDir, { recursive: true });
  fs.writeFileSync(`${artifactDir}/wip08-wip09-parity.json`, `${JSON.stringify({ schema:'AEGIS_SHIP_PROFILE_PARITY_V48_WIP09',baselineSimulator,simulator,checks,baseline,current }, null, 2)}\n`);
  expect(checks).toEqual({ baselineSelftests:true, currentSelftests:true, exactBehaviorParity:true });
});
