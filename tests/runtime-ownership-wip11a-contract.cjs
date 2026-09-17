const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const file = process.argv[2] || path.join(__dirname, '../Aegis_SIM_v48_WIP11A.html');
const baselineFile = process.argv[3] || path.join(__dirname, '../archive/v48/WIP11/Aegis_SIM_v48_WIP11.html');
const html = fs.readFileSync(file, 'utf8');
const baseline = fs.readFileSync(baselineFile, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(match => match[1]).filter(source => source.trim());
for (const [index, source] of scripts.entries()) new vm.Script(source, { filename: `${path.basename(file)}#inline-${index + 1}` });

const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const liveGeometryAssignment = html.match(/const SHIP_EXTERNAL_GEOMETRY=([^;]+);/)?.[1] ?? '';
const liveLaunchOwnershipTags = (html.match(/tagWorldEntityOwnershipV48Wip11A\((?:m|ram),'FRIENDLY_ORDNANCE',ACTIVE_SHIP_RUNTIME\.entityId\)/g) || []).length;
const baselineInvariant = needle => baseline.includes(needle) && html.includes(needle);

const checks = {
  title: html.includes('<title>AEGIS v48 WIP11A — Runtime Ownership Boundary Cleanup</title>'),
  syntax: scripts.length > 0,
  immutableProfilePreserved: hasAll("schema:'AEGIS_SHIP_PROFILE_V48_WIP11'", 'const ACTIVE_SHIP_PROFILE=', 'deepFreezeShipProfileV48Wip09'),
  shipRuntimeCanonical: hasAll("schema:'AEGIS_SHIP_RUNTIME_V48_WIP11A'", 'function createShipRuntime(profile,options={})', 'const ACTIVE_SHIP_RUNTIME=createShipRuntime(ACTIVE_SHIP_PROFILE)'),
  engagementOwnsWorld: hasAll("schema:'AEGIS_ENGAGEMENT_RUNTIME_V48_WIP11A'", 'ships:new Map([[ACTIVE_SHIP_RUNTIME.entityId,ACTIVE_SHIP_RUNTIME]])', 'e.world.entities.hostileMissiles=enemyMissiles'),
  compatibilityAliases: hasAll('const ACTIVE_SHIP_RUNTIME_V48_WIP09=ACTIVE_SHIP_RUNTIME', 'const createShipRuntimeV48Wip09=createShipRuntime', 'const aircraft=ownshipReference'),
  ownshipNameCanonical: hasAll('const ownshipReference = {', 'ACTIVE_SHIP_RUNTIME.worldReference=ownshipReference'),
  canonicalGeometryDirect: liveGeometryAssignment.trim() === 'CANONICAL_SHIP_EXTERNAL_GEOMETRY' && hasAll('const CANONICAL_SHIP_EXTERNAL_GEOMETRY=Object.freeze([', "SHIP_EXTERNAL_GEOMETRY_WIP164_BASE:'DIAGNOSTIC_ONLY'", "wip165CompactExteriorGeometry:'DIAGNOSTIC_ONLY'"),
  canonicalApiAliases: hasAll('const shipHullContainsPoint=wip199HullContainsPoint', 'const shipLocalToWorld=wip199ShipLocalWorldPoint', 'const boundaryMaterialMetrics=wip11BoundaryMetrics'),
  authorityManifest: hasAll("schema:'AEGIS_AUTHORITY_MANIFEST_V48_WIP11A'", "computeSarhIllumOpportunityV1:'LIVE_CANONICAL_GEOMETRY_OPPORTUNITY'", "computeSarhIllumQ:'COMPAT_REQUIRED_LIVE_LEGACY_AND_TELEMETRY'"),
  registryFacade: hasAll("schema:'AEGIS_REGISTRY_FACADE_V48_WIP11A'", 'function resolveShipProfile(id)', 'function resolveSensorSuite(id)', 'function resolveWeaponDefinition(id)'),
  lifecycleContract: hasAll("schema:'AEGIS_SHIP_RUNTIME_LIFECYCLE_V48_WIP11A'", 'function spawnShipRuntime(profileId,options={})', 'function destroyShipRuntime(entityId,options={})', 'function resetEngagementTransientV48Wip11A()', 'function resetShipNavigationV48Wip11A()', 'function resetScenarioWorldV48Wip11A(', 'function resetEntireSessionV48Wip11A()'),
  operationalBoundary: hasAll("const OPERATIONAL_STATE_SCHEMA_V48_WIP11A='AEGIS_OPERATIONAL_STATE_V48_WIP11A'", 'function exportOperationalState()', 'function importOperationalState(state,options={})', 'function enterCombat(operationalState)'),
  profilerOptIn: hasAll("schema:'AEGIS_SUBSYSTEM_PROFILER_V48_WIP11A'", 'let enabled=false,capacity=512', "phase(_wip11aProfileTick,'damage_flood')", "phase(_wip11aProfileTick,'ordnance_guidance')"),
  updateAuthorityUnchanged: hasAll("fixedTickHz:60", 'floodForceSubstepHz:120', 'hydrostaticQuadratureHz:20', "policy:'PRESERVE_CALL_ORDER_AND_RNG_CONSUMPTION__MEASURE_BEFORE_OPTIMIZING'"),
  liveOrdnanceOwnership: liveLaunchOwnershipTags >= 4 && hasAll("tagWorldEntityOwnershipV48Wip11A(em,'HOSTILE_ORDNANCE'"),
  diagnosticSurface: hasAll('runtimeOwnershipAuditV48Wip11A:()=>runtimeOwnershipAuditV48Wip11A()', 'exportOperationalStateV48Wip11A:()=>exportOperationalState()', 'profilerSnapshotV48Wip11A:()=>SIM_SUBSYSTEM_PROFILER_V48_WIP11A.snapshot()'),
  diagnosticRngIsolated: hasAll('_v1SarhState:\'TRACK\',_sarhRxRngState:1', '_v1ArhState:\'TRACK\',_arhRxRngState:1'),
  selftest: html.includes('RUNTIME-OWNERSHIP-V48-WIP11A SELFTEST PASS'),
  physicsCadenceParity: baselineInvariant('const SIM_FIXED_DT = 1 / 60;') && baselineInvariant('while(left>1e-10){const h=Math.min(left,1/120);left-=h;'),
  protectionContractPreserved: baselineInvariant("schema:'AEGIS_MATERIAL_PROTECTION_V48_WIP11'") && baselineInvariant("status:'ACTIVE_PHYSICS_COUPLED'"),
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result:'PASS', scope:'RUNTIME_OWNERSHIP_V48_WIP11A_STATIC_CONTRACT', file:path.basename(file), baseline:path.basename(baselineFile), checks }, null, 2));
