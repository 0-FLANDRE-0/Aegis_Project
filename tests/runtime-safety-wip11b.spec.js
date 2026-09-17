const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const crypto = require('node:crypto');

const simulator = process.env.SIM_FILE || 'Aegis_SIM_v48_WIP11B.html';
const baselineSimulator = process.env.SAFETY_BASELINE_SIM_FILE || 'archive/v48/WIP11A/Aegis_SIM_v48_WIP11A.html';
const artifactDir = process.env.ARTIFACT_DIR || 'artifacts/runtime-safety-wip11b';

test.use({ viewport: { width: 1600, height: 900 } });

test('v48 WIP11B rejects active-ship destruction and invalid operational imports without mutation', async ({ page, browser }) => {
  test.setTimeout(240_000);
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', error => pageErrors.push(error.stack || String(error)));
  await page.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481120; });
  await page.goto(`http://127.0.0.1:4173/${simulator}`, { waitUntil:'load' });
  await page.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.operationalImportSafetyAuditV48Wip11B, null, { timeout:45_000 });

  const result = await page.evaluate(() => {
    const d = window.__NAVAL_SIM_DIAG__, clone = value => structuredClone(value);
    const ownershipA = d.runtimeOwnershipAuditV48Wip11A(), ownershipB = d.runtimeOwnershipAuditV48Wip11A();
    const registry = d.registryFoundationV48Wip11A(), authority = d.runtimeAuthorityManifestV48Wip11A(), update = d.simulationUpdateContractV48Wip11A();
    const safety = d.operationalImportSafetyV48Wip11B(), compatibility = d.operationalProfileCompatibilityV48Wip11B(), safetyAudit = d.operationalImportSafetyAuditV48Wip11B();

    const lifecycleContract = d.shipLifecycleContractV48Wip11A();
    const activeBefore = d.lifecycleStateV48Wip11A();
    const activeDestroy = d.destroyShipRuntimeV48Wip11A(window.__AEGIS_ACTIVE_SHIP_RUNTIME__.entityId);
    const activeDestroyOverrideAttempt = d.destroyShipRuntimeV48Wip11A(window.__AEGIS_ACTIVE_SHIP_RUNTIME__.entityId, { allowActive:true });
    const activeAfter = d.lifecycleStateV48Wip11A();
    const probeSpawn = d.spawnShipRuntimeV48Wip11A('DDG_119_LATE_FLIGHT_IIA', { entityId:'SHIP_WIP11B_LIFECYCLE_PROBE' });
    const probeDestroy = d.destroyShipRuntimeV48Wip11A(probeSpawn.entityId);

    const original = d.exportOperationalStateV48Wip11A(), originalValidation = d.validateOperationalStateV48Wip11B(original), modified = clone(original);
    const liquidId = Object.keys(modified.ship.liquidLoads)[0] ?? null;
    modified.ship.navigation.heading = 0.321;
    modified.ship.navigation.targetSpeedKt = 17;
    modified.ship.inventory.closeIn[0].ammo = Math.max(0, modified.ship.inventory.closeIn[0].ammo - 7);
    if (liquidId) modified.ship.liquidLoads[liquidId] = Math.max(0, modified.ship.liquidLoads[liquidId] - 1234);
    const imported = d.importOperationalStateV48Wip11B(modified), afterImport = d.exportOperationalStateV48Wip11A();
    d.importOperationalStateV48Wip11B(original);
    const restored = d.exportOperationalStateV48Wip11A();

    const fixture = d.createTerminalAsmFixture({ seed:481121, label:'Kh-35U', rangeKm:8, bearingDeg:0, altM:15, speedMps:280 });
    const interceptorId = d.fireESSM();
    const invalidCases = [
      { name:'profileRevision', code:'PROFILE_REVISION', mutate:s => { s.profileRevision += '_INCOMPATIBLE'; } },
      { name:'vlsShape', code:'VLS_LENGTH:aft', mutate:s => { s.ship.inventory.vls.aft.pop(); } },
      { name:'liquidLoadId', code:'LIQUID_LOAD_IDS', mutate:s => { const id=Object.keys(s.ship.liquidLoads)[0]; const value=s.ship.liquidLoads[id]; delete s.ship.liquidLoads[id]; s.ship.liquidLoads['rogue.load']=value; } },
      { name:'floodCellId', code:'FLOOD_CELL_ID:', mutate:s => { s.ship.damage.flooding.cells[0].id='rogue.cell'; } },
      { name:'crewShape', code:'CREW_GROUP_LENGTH', mutate:s => { s.ship.crew.groups.pop(); } },
      { name:'navigationFinite', code:'NAV_FINITE:speed', mutate:s => { s.ship.navigation.speed=null; } },
    ];
    const invalid = invalidCases.map(row => {
      const candidate=d.exportOperationalStateV48Wip11A();row.mutate(candidate);
      const before=d.operationalImportMutationFingerprintV48Wip11B(), validation=d.validateOperationalStateV48Wip11B(candidate);let rejected=false,message='';
      try{d.importOperationalStateV48Wip11B(candidate);}catch(err){rejected=true;message=String(err?.message??err);}
      const after=d.operationalImportMutationFingerprintV48Wip11B();
      return {name:row.name,code:row.code,rejected,message,validation,zeroMutation:JSON.stringify(before)===JSON.stringify(after)};
    });
    const entityOwnership = d.runtimeEntityOwnershipV48Wip11A();
    const lifecycleBeforeReset = d.lifecycleStateV48Wip11A(), lifecycleAfterReset = d.resetEngagementTransientV48Wip11A();

    d.profilerResetV48Wip11A();
    const profilerInitial = d.profilerSnapshotV48Wip11A();
    d.profilerEnableV48Wip11A(true); d.stepTicks(12); d.profilerEnableV48Wip11A(false);
    const profiler = d.profilerSnapshotV48Wip11A();
    return {
      ownershipA, ownershipB, registry, authority, update, safety, compatibility, safetyAudit,
      lifecycleFoundation:{contract:lifecycleContract,activeBefore,activeDestroy,activeDestroyOverrideAttempt,activeAfter,probeSpawn,probeDestroy},
      operational:{schema:original.schema,profileRevision:original.profileRevision,originalValidation,liquidId,importedValidation:imported.validation,afterImport:{heading:afterImport.ship.navigation.heading,targetSpeedKt:afterImport.ship.navigation.targetSpeedKt,ciwsAmmo:afterImport.ship.inventory.closeIn[0].ammo,liquidKg:liquidId?afterImport.ship.liquidLoads[liquidId]:null},expected:{ciwsAmmo:modified.ship.inventory.closeIn[0].ammo,liquidKg:liquidId?modified.ship.liquidLoads[liquidId]:null},restored:{heading:restored.ship.navigation.heading,targetSpeedKt:restored.ship.navigation.targetSpeedKt,ciwsAmmo:restored.ship.inventory.closeIn[0].ammo,liquidKg:liquidId?restored.ship.liquidLoads[liquidId]:null},original:{heading:original.ship.navigation.heading,targetSpeedKt:original.ship.navigation.targetSpeedKt,ciwsAmmo:original.ship.inventory.closeIn[0].ammo,liquidKg:liquidId?original.ship.liquidLoads[liquidId]:null},invalid},
      entity:{fixture,interceptorId,ownership:entityOwnership,lifecycleBeforeReset,lifecycleAfterReset},
      profiler:{initial:profilerInitial,final:profiler},
      selftestFailures:window.__CORE_SELFTEST_FAILURES__.slice(), logs:d.debugLogSnapshot(),
      globals:{runtimeSchema:window.__AEGIS_ACTIVE_SHIP_RUNTIME__?.schema,engagementSchema:window.__AEGIS_ENGAGEMENT_RUNTIME__?.schema,sameRegistered:window.__AEGIS_ENGAGEMENT_RUNTIME__?.ships?.get(window.__AEGIS_ACTIVE_SHIP_RUNTIME__?.entityId)===window.__AEGIS_ACTIVE_SHIP_RUNTIME__}
    };
  });

  const captureParity = async file => {
    const context = await browser.newContext({ viewport:{ width:1600, height:900 } });
    const p = await context.newPage(), errors = [];
    await p.addInitScript(() => { window.__NAVAL_SIM_SEED__ = 481120; });
    p.on('console', message => { if (message.type() === 'error') errors.push(`console:${message.text()}`); });
    p.on('pageerror', error => errors.push(`page:${error.stack || String(error)}`));
    await p.goto(`http://127.0.0.1:4173/${file}`, { waitUntil:'load' });
    await p.waitForFunction(() => Array.isArray(window.__CORE_SELFTEST_FAILURES__) && window.__NAVAL_SIM_DIAG__?.ciwsB1Closure, null, { timeout:45_000 });
    const capture = await p.evaluate(() => {
      const d=window.__NAVAL_SIM_DIAG__, api=d.ciwsB1Closure;
      d.setSeed(481128); const impactRaw=d.runV48Wip02ImpactProbe('Kh-35U');
      const impact={impact:{rawKineticEnergyMJ:impactRaw.impact.rawKineticEnergyMJ,impactMomentumNs:impactRaw.impact.impactMomentumNs,throughHull:impactRaw.impact.throughHull,physicalPenetrationM:impactRaw.impact.physicalPenetrationM,hullExitDistanceM:impactRaw.impact.hullExitDistanceM,exitEnergyMJ:impactRaw.impact.exitEnergyMJ,openings:impactRaw.impact.openings},rigidBodyDelta:impactRaw.rigidBodyDelta};
      api.prepare({ mount:'GUN', seed:481129, rangeKm:2.4, speedMps:300, altM:15 });
      const q=api.stepCiws(8), s=q.snapshot;
      return {selftests:window.__CORE_SELFTEST_FAILURES__.slice(),impact,steps:q.steps,simSeconds:q.simSeconds,track:s.track,gate:s.gate,mounts:s.mounts.map(m=>({type:m.type,state:m.state,ammo:m.ammo,spent:m.spent,firing:m.firing,tracking:m.tracking,trackingTrackId:m.trackingTrackId,source:m.source,localTrack:m.localTrack})),ramLaunched:s.ramLaunched,bullets:s.bullets,rngState:s.rngState,simStepCounter:s.simStepCounter};
    });
    await context.close();
    return {capture,errors};
  };

  const baseline = await captureParity(baselineSimulator), current = await captureParity(simulator);
  const prof = result.profiler.final.systems, allResetCounts = result.entity.lifecycleAfterReset.entityCounts;
  const checks = {
    pageLoad: consoleErrors.length === 0 && pageErrors.length === 0,
    coreSelftests: result.selftestFailures.length === 0 && result.logs.some(row => String(row?.text ?? row).includes('OPERATIONAL-IMPORT-SAFETY-V48-WIP11B SELFTEST PASS')),
    ownershipAudit: result.ownershipA.pass && Object.values(result.ownershipA.checks).every(Boolean),
    ownershipAuditReadOnly: JSON.stringify(result.ownershipA) === JSON.stringify(result.ownershipB),
    runtimeGlobals: result.globals.runtimeSchema === 'AEGIS_SHIP_RUNTIME_V48_WIP11A' && result.globals.engagementSchema === 'AEGIS_ENGAGEMENT_RUNTIME_V48_WIP11A' && result.globals.sameRegistered,
    ownershipFoundationsPreserved: result.authority.runtime.ACTIVE_SHIP_RUNTIME === 'LIVE_CANONICAL' && Object.values(result.registry.resolves).every(Boolean) && result.update.fixedTickHz === 60 && result.update.floodForceSubstepHz === 120,
    activeDestroyAlwaysRejected: result.lifecycleFoundation.contract.activeShipDestroyPolicy === 'REJECT' && result.lifecycleFoundation.activeDestroy.reason === 'ACTIVE_PLAYER_SHIP' && result.lifecycleFoundation.activeDestroyOverrideAttempt.reason === 'ACTIVE_PLAYER_SHIP' && JSON.stringify(result.lifecycleFoundation.activeBefore) === JSON.stringify(result.lifecycleFoundation.activeAfter) && result.lifecycleFoundation.probeDestroy.ok && result.lifecycleFoundation.probeDestroy.shipCount === 1,
    safetyContracts: result.safety.mode === 'CLONE_VALIDATE_NORMALIZE_THEN_APPLY' && result.safety.invalidInputMutationPolicy === 'ZERO_AUTHORITATIVE_MUTATION' && result.safety.exportIsolation === 'DETACHED_JSON_SNAPSHOT' && result.safety.activeShipDestroyPolicy === 'UNCONDITIONAL_REJECT' && result.safety.codecIds.join('|') === 'envelope|navigation|weapons|loads|damageFlooding|crew|aviation',
    compatibilityExact: result.compatibility.acceptedRevisions.DDG_119_LATE_FLIGHT_IIA.length === 1 && result.compatibility.acceptedRevisions.DDG_119_LATE_FLIGHT_IIA[0] === result.operational.profileRevision,
    safetyAudit: result.safetyAudit.pass && Object.values(result.safetyAudit.checks).every(Boolean),
    snapshotAccepted: result.operational.schema === 'AEGIS_OPERATIONAL_STATE_V48_WIP11A' && result.operational.originalValidation.ok && result.operational.originalValidation.codecs.every(row => row.ok) && result.operational.importedValidation.ok,
    snapshotMutationRestored: result.operational.afterImport.heading === 0.321 && result.operational.afterImport.targetSpeedKt === 17 && result.operational.afterImport.ciwsAmmo === result.operational.expected.ciwsAmmo && result.operational.afterImport.liquidKg === result.operational.expected.liquidKg,
    snapshotRoundTrip: JSON.stringify(result.operational.restored) === JSON.stringify(result.operational.original),
    invalidInputsRejected: result.operational.invalid.length === 6 && result.operational.invalid.every(row => row.rejected && !row.validation.ok && row.validation.errors.some(code => code.startsWith(row.code)) && row.message.includes('Operational state rejected')),
    invalidImportsZeroMutation: result.operational.invalid.every(row => row.zeroMutation),
    liveEntityOwnership: result.entity.interceptorId != null && result.entity.ownership.hostileMissiles.some(row => row.id === result.entity.fixture.enemyId && row.ownerEntityId === 'DIAGNOSTIC_FORCE') && result.entity.ownership.ordnance.some(row => row.id === result.entity.interceptorId && row.ownerEntityId === result.entity.ownership.shipId && row.entityClass === 'FRIENDLY_ORDNANCE'),
    lifecycleReset: result.entity.lifecycleAfterReset.revision > result.entity.lifecycleBeforeReset.revision && ['aircraft','surfaceContacts','hostileMissiles','ordnance','ramOrdnance','ciwsProjectiles','tracks','esmContacts'].every(key => allResetCounts[key] === 0),
    profilerDefaultOff: result.profiler.initial.enabled === false && Object.keys(result.profiler.initial.systems).length === 0,
    profilerOptIn: result.profiler.final.enabled === false && prof['tick.total']?.calls === 12 && ['damage_flood','scenario_ai','navigation_input','sensors_tracks_ew','world_entities','ordnance_guidance','close_in_terrain','cleanup'].every(key => prof[key]?.calls === 12),
    wip11aBehaviorParity: baseline.errors.length === 0 && current.errors.length === 0 && baseline.capture.selftests.length === 0 && current.capture.selftests.length === 0 && JSON.stringify(current.capture) === JSON.stringify(baseline.capture),
  };
  fs.mkdirSync(artifactDir,{recursive:true});
  const artifact={schema:'AEGIS_OPERATIONAL_IMPORT_SAFETY_BROWSER_V48_WIP11B',simulator,baselineSimulator,simulatorSha256:crypto.createHash('sha256').update(fs.readFileSync(simulator)).digest('hex'),baselineSha256:crypto.createHash('sha256').update(fs.readFileSync(baselineSimulator)).digest('hex'),checks,consoleErrors,pageErrors,result,parity:{baseline,current}};
  fs.writeFileSync(`${artifactDir}/runtime-safety-results.json`,`${JSON.stringify(artifact,null,2)}\n`);
  expect(checks).toEqual(Object.fromEntries(Object.keys(checks).map(key => [key,true])));
});
