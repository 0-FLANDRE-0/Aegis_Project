const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP11A.html';
const baselineSimulator = process.env.OWNERSHIP_BASELINE_SIM_FILE || 'archive/v48/WIP11/Aegis_SIM_v48_WIP11.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/runtime-ownership-wip11a';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP11A establishes ship/world ownership, lifecycle snapshots, registries and opt-in profiling without behavior drift', async ({ page, browser }) => {
  test.setTimeout(240_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481100; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.runtimeOwnershipAuditV48Wip11A, null, { timeout:45_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__;
    const ownershipA = d.runtimeOwnershipAuditV48Wip11A(), ownershipB = d.runtimeOwnershipAuditV48Wip11A();
    const registry = d.registryFoundationV48Wip11A(), authority = d.runtimeAuthorityManifestV48Wip11A(), update = d.simulationUpdateContractV48Wip11A();
    const lifecycleContract=d.shipLifecycleContractV48Wip11A(),probeSpawn=d.spawnShipRuntimeV48Wip11A('DDG_119_LATE_FLIGHT_IIA',{entityId:'SHIP_WIP11A_LIFECYCLE_PROBE'}),activeDestroy=d.destroyShipRuntimeV48Wip11A(window.__AEGIS_ACTIVE_SHIP_RUNTIME__.entityId),probeDestroy=d.destroyShipRuntimeV48Wip11A(probeSpawn.entityId);
    const original = d.exportOperationalStateV48Wip11A(), modified = structuredClone(original);
    const liquidId = Object.keys(modified.ship.liquidLoads)[0] ?? null;
    modified.ship.navigation.heading = 0.321;
    modified.ship.navigation.targetSpeedKt = 17;
    modified.ship.inventory.closeIn[0].ammo = Math.max(0, modified.ship.inventory.closeIn[0].ammo - 7);
    if (liquidId) modified.ship.liquidLoads[liquidId] = Math.max(0, modified.ship.liquidLoads[liquidId] - 1234);
    const imported = d.importOperationalStateV48Wip11A(modified), afterImport = d.exportOperationalStateV48Wip11A();
    d.importOperationalStateV48Wip11A(original);
    const restored = d.exportOperationalStateV48Wip11A();
    const bad = structuredClone(original); bad.schema = 'REJECT_ME';
    let badRejected = false; try { d.importOperationalStateV48Wip11A(bad); } catch { badRejected = true; }

    const fixture = d.createTerminalAsmFixture({ seed:481101, label:'Kh-35U', rangeKm:8, bearingDeg:0, altM:15, speedMps:280 });
    const interceptorId = d.fireESSM(), entityOwnership = d.runtimeEntityOwnershipV48Wip11A();
    const lifecycleBeforeReset = d.lifecycleStateV48Wip11A(), lifecycleAfterReset = d.resetEngagementTransientV48Wip11A();

    d.profilerResetV48Wip11A();
    const profilerInitial = d.profilerSnapshotV48Wip11A();
    d.profilerEnableV48Wip11A(true); d.stepTicks(12); d.profilerEnableV48Wip11A(false);
    const profiler = d.profilerSnapshotV48Wip11A();
    return {
      ownershipA, ownershipB, registry, authority, update,lifecycleFoundation:{contract:lifecycleContract,probeSpawn,activeDestroy,probeDestroy},
      operational:{schema:original.schema,liquidId,importedValidation:imported.validation,afterImport:{heading:afterImport.ship.navigation.heading,targetSpeedKt:afterImport.ship.navigation.targetSpeedKt,ciwsAmmo:afterImport.ship.inventory.closeIn[0].ammo,liquidKg:liquidId?afterImport.ship.liquidLoads[liquidId]:null},expected:{ciwsAmmo:modified.ship.inventory.closeIn[0].ammo,liquidKg:liquidId?modified.ship.liquidLoads[liquidId]:null},restored:{heading:restored.ship.navigation.heading,targetSpeedKt:restored.ship.navigation.targetSpeedKt,ciwsAmmo:restored.ship.inventory.closeIn[0].ammo,liquidKg:liquidId?restored.ship.liquidLoads[liquidId]:null},original:{heading:original.ship.navigation.heading,targetSpeedKt:original.ship.navigation.targetSpeedKt,ciwsAmmo:original.ship.inventory.closeIn[0].ammo,liquidKg:liquidId?original.ship.liquidLoads[liquidId]:null},badRejected},
      entity:{fixture,interceptorId,ownership:entityOwnership,lifecycleBeforeReset,lifecycleAfterReset},
      profiler:{initial:profilerInitial,final:profiler},
      selftestFailures:window.__CORE_SELFTEST_FAILURES__.slice(), logs:d.debugLogSnapshot(),
      globals:{runtimeSchema:window.__AEGIS_ACTIVE_SHIP_RUNTIME__?.schema,engagementSchema:window.__AEGIS_ENGAGEMENT_RUNTIME__?.schema,sameRegistered:window.__AEGIS_ENGAGEMENT_RUNTIME__?.ships?.get(window.__AEGIS_ACTIVE_SHIP_RUNTIME__?.entityId)===window.__AEGIS_ACTIVE_SHIP_RUNTIME__}
    };
  });

  const captureParity = async file => {
    const context = await browser.newContext({ viewport:{ width:1600, height:900 } });
    const p = await context.newPage(), errors = [];
    await p.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481100; });
    p.on('console', message => { if (message.type() === 'error') errors.push(`console:${message.text()}`); });
    p.on('pageerror', error => errors.push(`page:${error.stack || String(error)}`));
    await p.goto(`http://127.0.0.1:4173/${file}`, { waitUntil:'load' });
    await p.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.ciwsB1Closure, null, { timeout:45_000 });
    const capture = await p.evaluate(() => {
      const d=window.__NAVAL_SIM_DIAG__, api=d.ciwsB1Closure;
      d.setSeed(481198); const impactRaw=d.runV48Wip02ImpactProbe('Kh-35U');
      const impact={impact:{rawKineticEnergyMJ:impactRaw.impact.rawKineticEnergyMJ,impactMomentumNs:impactRaw.impact.impactMomentumNs,throughHull:impactRaw.impact.throughHull,physicalPenetrationM:impactRaw.impact.physicalPenetrationM,hullExitDistanceM:impactRaw.impact.hullExitDistanceM,exitEnergyMJ:impactRaw.impact.exitEnergyMJ,openings:impactRaw.impact.openings},rigidBodyDelta:impactRaw.rigidBodyDelta};
      api.prepare({ mount:'GUN', seed:481199, rangeKm:2.4, speedMps:300, altM:15 });
      const q=api.stepCiws(8), s=q.snapshot;
      return {selftests:window.__CORE_SELFTEST_FAILURES__.slice(),impact,steps:q.steps,simSeconds:q.simSeconds,track:s.track,gate:s.gate,mounts:s.mounts.map(m=>({type:m.type,state:m.state,ammo:m.ammo,spent:m.spent,firing:m.firing,tracking:m.tracking,trackingTrackId:m.trackingTrackId,source:m.source,localTrack:m.localTrack})),ramLaunched:s.ramLaunched,bullets:s.bullets,rngState:s.rngState,simStepCounter:s.simStepCounter};
    });
    await context.close();
    return {capture,errors};
  };
  const baseline = await captureParity(baselineSimulator), current = await captureParity(simulator);
  const prof = result.profiler.final.systems;
  const allResetCounts = result.entity.lifecycleAfterReset.entityCounts;
  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftestFailures.length === 0 && result.logs.some(row => String(row?.text ?? row).includes('RUNTIME-OWNERSHIP-V48-WIP11A SELFTEST PASS')),
    ownershipAudit: result.ownershipA.pass && Object.values(result.ownershipA.checks).every(Boolean),
    ownershipAuditReadOnly: JSON.stringify(result.ownershipA) === JSON.stringify(result.ownershipB),
    runtimeGlobals: result.globals.runtimeSchema === 'AEGIS_SHIP_RUNTIME_V48_WIP11A' && result.globals.engagementSchema === 'AEGIS_ENGAGEMENT_RUNTIME_V48_WIP11A' && result.globals.sameRegistered,
    authorityClassification: result.authority.runtime.ACTIVE_SHIP_RUNTIME === 'LIVE_CANONICAL' && result.authority.geometry.CANONICAL_SHIP_EXTERNAL_GEOMETRY === 'LIVE_CANONICAL' && result.authority.geometry.SHIP_EXTERNAL_GEOMETRY_WIP164_BASE === 'DIAGNOSTIC_ONLY' && result.authority.sarh.computeSarhIllumQ === 'COMPAT_REQUIRED_LIVE_LEGACY_AND_TELEMETRY',
    registryResolution: Object.values(result.registry.resolves).every(Boolean) && result.registry.ships.includes('DDG_119_LATE_FLIGHT_IIA') && result.registry.vlsWeapons.includes('SM2') && result.registry.vlsWeapons.includes('ESSM'),
    updateCadence: result.update.fixedTickHz === 60 && result.update.floodForceSubstepHz === 120 && result.update.hydrostaticQuadratureHz === 20 && result.update.policy.includes('MEASURE_BEFORE_OPTIMIZING'),
    lifecycleFoundation: result.lifecycleFoundation.contract.spawnState === 'UNBOUND' && result.lifecycleFoundation.contract.multiShipSimulation === 'DEFERRED' && result.lifecycleFoundation.probeSpawn.lifecycleState === 'UNBOUND' && result.lifecycleFoundation.probeSpawn.shipCount === 2 && result.lifecycleFoundation.activeDestroy.ok === false && result.lifecycleFoundation.activeDestroy.reason === 'ACTIVE_PLAYER_SHIP' && result.lifecycleFoundation.probeDestroy.ok === true && result.lifecycleFoundation.probeDestroy.shipCount === 1,
    snapshotAccepted: result.operational.schema === 'AEGIS_OPERATIONAL_STATE_V48_WIP11A' && result.operational.importedValidation.ok && result.operational.badRejected,
    snapshotMutationRestored: result.operational.afterImport.heading === 0.321 && result.operational.afterImport.targetSpeedKt === 17 && result.operational.afterImport.ciwsAmmo === result.operational.expected.ciwsAmmo && result.operational.afterImport.liquidKg === result.operational.expected.liquidKg,
    snapshotRoundTrip: JSON.stringify(result.operational.restored) === JSON.stringify(result.operational.original),
    liveEntityOwnership: result.entity.interceptorId != null && result.entity.ownership.hostileMissiles.some(row => row.id === result.entity.fixture.enemyId && row.ownerEntityId === 'DIAGNOSTIC_FORCE') && result.entity.ownership.ordnance.some(row => row.id === result.entity.interceptorId && row.ownerEntityId === result.entity.ownership.shipId && row.entityClass === 'FRIENDLY_ORDNANCE'),
    lifecycleReset: result.entity.lifecycleAfterReset.revision > result.entity.lifecycleBeforeReset.revision && ['aircraft','surfaceContacts','hostileMissiles','ordnance','ramOrdnance','ciwsProjectiles','tracks','esmContacts'].every(key => allResetCounts[key] === 0),
    profilerDefaultOff: result.profiler.initial.enabled === false && Object.keys(result.profiler.initial.systems).length === 0,
    profilerOptIn: result.profiler.final.enabled === false && prof['tick.total']?.calls === 12 && ['damage_flood','scenario_ai','navigation_input','sensors_tracks_ew','world_entities','ordnance_guidance','close_in_terrain','cleanup'].every(key => prof[key]?.calls === 12) && Object.values(prof).every(row => row.avgMs >= 0 && row.p95Ms >= 0),
    wip11BehaviorParity: baseline.errors.length === 0 && current.errors.length === 0 && baseline.capture.selftests.length === 0 && current.capture.selftests.length === 0 && JSON.stringify(current.capture) === JSON.stringify(baseline.capture),
  };
  fs.mkdirSync(artifactDir,{recursive:true});
  const artifact={schema:'AEGIS_RUNTIME_OWNERSHIP_BROWSER_V48_WIP11A',simulator,baselineSimulator,simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),baselineSha256:crypto.createHash('sha256').update(fs.readFileSync(baselineSimulator)).digest('hex'),checks,consoleErrors,pageErrors,result,parity:{baseline,current}};
  fs.writeFileSync(`${artifactDir}/runtime-ownership-results.json`,`${JSON.stringify(artifact,null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key,true])));
});
