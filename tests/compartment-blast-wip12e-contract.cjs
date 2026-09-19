const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12E.html');
const html = fs.readFileSync(file, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1])
  .filter(source => source.trim());

for (const [index, source] of scripts.entries()) {
  new vm.Script(source, { filename: `inline-${index + 1}.js` });
}

const start = html.indexOf('// ===== V48 WIP12E GENERIC COMPARTMENT BLAST / DAMAGE AUTHORITY =====');
const end = html.indexOf('function _wip143FuzeParamsForMissile', start);
assert(start >= 0 && end > start, 'WIP12E source bounds missing');
const source = html.slice(start, end);
const kernelStart = source.indexOf('function wip12eChargeSpec');
const kernelEnd = source.indexOf('function wip12eBlastTraceSummary', kernelStart);
assert(kernelStart >= 0 && kernelEnd > kernelStart, 'WIP12E kernel bounds missing');
const kernel = source.slice(kernelStart, kernelEnd);
const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const sourceHasAll = (...needles) => needles.every(needle => source.includes(needle));

const staticChecks = {
  title: html.includes('<title>AEGIS v48 WIP12E — Generic Compartment Blast Authority</title>'),
  syntax: scripts.length === 1,
  contract: sourceHasAll(
    "schema:'AEGIS_COMPARTMENT_BLAST_V48_WIP12E'",
    "coordinateSpace:'SHIP_LOCAL_METRES'",
    "units:'SI'",
    "solver:'BOUNDED_IMPACT_TIME_EVENT_GRAPH_NOT_CFD'"
  ),
  authorityModes: sourceHasAll(
    "'LEGACY_SCALAR_BLAST_COMPAT'",
    "'COMPARTMENT_BLAST_SHADOW'",
    "'COMPARTMENT_BLAST_AUTHORITY'",
    "defaultMode:'COMPARTMENT_BLAST_AUTHORITY'"
  ),
  hardCaps: sourceHasAll(
    'cells:96',
    'portalEvents:384',
    'surfaceLoads:512',
    'breaches:64',
    'timeSlices:32',
    'ventJets:32',
    'presentationKeyframes:256'
  ),
  physicalChargeContract: sourceHasAll(
    "schema:'AEGIS_BLAST_CHARGE_SPEC_V48_WIP12E'",
    'explosiveMassKg',
    'tntEquivalentFactor',
    'tntEquivalentKg',
    'caseMassKg',
    'detonationClass',
    'energyModel',
    'provenance',
    'confidence'
  ),
  detailedTopologyAdapter: sourceHasAll(
    'function wip12eBuildTopologyBase',
    'wip12cShipGeometryTemplate()',
    'getShipInteriorTopologyV48Wip06().snapshot()',
    'PERSISTENT_FLOOD_OPENING'
  ) && html.includes('CURRENT_DAMAGE_PACKET_BREACH'),
  separatedChannels: sourceHasAll(
    "'incidentPressure'",
    "'reflectedPressure'",
    "'positiveImpulse'",
    "'dynamicBlastWind'",
    "'hotGas'",
    "'fragments'",
    "'spall'",
    "'structuralShock'"
  ),
  pressureAndImpulseUnits: sourceHasAll(
    'incidentPeakKPa',
    'reflectedPeakKPa',
    'positivePhaseDurationMs',
    'positiveImpulseKPaMs',
    'dynamicImpulsePaS',
    'blastWindMps'
  ),
  remainingPulseAfterFailure: sourceHasAll(
    'remainingPulseEnergyJ:available',
    'remainingPulseOnly:true',
    'failedNow:!!route.response.failed'
  ),
  dynamicBreachCap: sourceHasAll(
    'dynamicBreachCount>=limits.breaches',
    "failureMode:'TRUNCATED_BY_BUDGET'",
    'breaches:dynamicBreachCount'
  ),
  propagationCap: sourceHasAll(
    'portalEvents.length>=limits.portalEvents',
    'budgetClipped=true',
    "terminationReason=!hasYield?'NO_EXPLOSIVE_CHARGE':clippedByBudget?'TRUNCATED_BY_BUDGET':'ENERGY_EXHAUSTED'"
  ),
  energyLedger: sourceHasAll(
    'chemicalInputJ:chemicalEnergyJ',
    'initialBlastEnergyJ:airBlastEnergyJ',
    'pressureWorkJ:absorbedBlastJ',
    'structuralAbsorptionJ:structuralWorkJ',
    'ventedEnergyJ:ventedBlastJ',
    'thermalRetainedJ:hotGasEnergyJ',
    'truncationDiscardJ:cutoffBlastJ',
    'closureErrorJ:airClosureErrorJ+totalPartitionErrorJ'
  ),
  deterministicKernel: !kernel.includes('Math.random(') && !kernel.includes('simRandom(') && !kernel.includes('rand('),
  weaponAgnosticKernel: !kernel.includes('carrierLabel') && !kernel.includes("label==='Kh-32'") && !kernel.includes("sourceClass==='"),
  occupancyNotResistance: sourceHasAll('crewOccupancyResistance:false', 'crewOccupancyZeroResistance:') && !kernel.includes('occupancyVolume'),
  singleDamageAuthority: hasAll(
    'function wip12eAuthorityParts',
    "trace?.mode==='COMPARTMENT_BLAST_AUTHORITY'",
    'function damageFloodImpactV48Wip12E',
    "WIP12E_COMPARTMENT_BLAST_AUTHORITY"
  ),
  acceptedBeforeVlsConsumer: hasAll(
    'const blastAccepted=',
    'const wip125CellDamage=blastAccepted?wip125ApplyImpactEffects'
  ),
  sharedCrewTrace: hasAll(
    "sharedTrace=event.blastTrace?.schema==='AEGIS_BLAST_TRACE_V48_WIP12E'",
    'rawSources=sharedTrace?[]:',
    'fatalChannels={PRESSURE:blastFatal,FRAGMENT:fragFatal,PENETRATOR:penetratorFatal,HOT_GAS:hotFatal}',
    "unit(id+':casualty:'+g.id+':'+channel+':fatal')"
  ),
  structureConsumesLoads: hasAll(
    'structuralShockEnergyJ:trace.damagePacket.structuralShock.energyJ',
    'blastSurfaceLoads:trace.damagePacket.structureLoads',
    'maxBlastSurfaceDemand'
  ),
  floodOnce: hasAll(
    "kind:'BLAST_SURFACE_RUPTURE'",
    'openingMap=new Map()',
    "holeAuthority=String(o.kind||'').includes('BLAST_SURFACE_RUPTURE')?'WIP12E_SURFACE_LOAD_FAILURE'"
  ),
  hotGasIgnitionOnly: hasAll(
    'function wip12eApplyHotGasIgnition',
    "source:'BLAST_HOT_GAS'",
    'genericBlastIgnition:false',
    'explosiveMassKg:0,tntEquivalentKg:0'
  ),
  eventAuthorityRecorded: hasAll(
    "WIP12E_COMPARTMENT_BLAST_PREACCOUNTED_OBSERVATION_ONLY",
    "primaryDamageAuthority=compartmentAuthority?'WIP12E_COMPARTMENT_BLAST_AUTHORITY':'LEGACY_ASM_DAMAGE_PATH'",
    "applicationAuthority:compartmentAuthority?'WIP12E_BLAST_OBSERVED_ALREADY_APPLIED':'OBSERVED_ALREADY_APPLIED'"
  ),
  presentationOnlyVfx: hasAll(
    'spawnShockwaveFront(pos,maxRadiusM,opt={})',
    'spawnBlastVentJet(q,opt={})',
    'spawnCompartmentBlastInterior(ev)',
    'seaSurfaceInteraction',
    "group.userData.presentationOnly=true",
    'renderFrameGeometryQueries:0'
  ),
  interiorVisibilityBound: hasAll(
    'group.visible=!!this.interiorTopologyVisible',
    'obj.visible=!!this.interiorTopologyVisible',
    'internalTraceVisibleOnlyInInterior:'
  ),
  diagnosticsExposed: hasAll(
    'wip12eCompartmentBlastContract:',
    'wip12eCompartmentBlastDiagnostics:',
    'wip12eBlastFixtureDiagnostics:',
    'wip12eKh32BlastShadowComparison:',
    'wip12eBlastAuthorityProbe:',
    'wip12eBlastIdempotenceProbe:',
    'wip12eBlastPerformanceProbe:',
    'wip12eBlastBudgetProbe:',
    'wip12eCompartmentBlast3DAudit:'
  ),
  legacyResidualPreserved: hasAll(
    "schema:'AEGIS_RESIDUAL_OVERPENETRATION_V48_WIP12D'",
    'function wip12dApplyResidualSupplement',
    'wip12dResidualOverpenetrationDiagnostics',
    'wip12dResidualOverpenetration3DAudit'
  ),
  bootSelftest: hasAll(
    'V48 WIP12E compartment blast ',
    'GENERIC-COMPARTMENT-BLAST-V48-WIP12E SELFTEST PASS'
  )
};

const clamp = (value, lo, hi) => Math.max(lo, Math.min(hi, value));
const finite = (value, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback;
const vector = (value = {}, fallback = { x:0, y:0, z:0 }) => ({
  x:finite(value?.x, fallback.x),
  y:finite(value?.y, fallback.y),
  z:finite(value?.z, fallback.z)
});
const magnitude = value => Math.hypot(value.x, value.y, value.z);
const unit = value => {
  const v = vector(value, { x:1, y:0, z:0 });
  const m = magnitude(v) || 1;
  return { x:v.x / m, y:v.y / m, z:v.z / m };
};

const context = {
  console,
  performance,
  Map,
  Set,
  Math,
  JSON,
  Date,
  Object,
  Array,
  String,
  Number,
  Boolean,
  Infinity,
  globalThis:null,
  deepFreezeShipProfileV48Wip09:value => value,
  SIM_RNG_STATE:0x481232,
  clamp,
  wip12aFinite:finite,
  wip12aVec:vector,
  wip12aUnit:unit,
  wip12aMag:magnitude,
  wip12aSub:(a, b) => ({ x:a.x - b.x, y:a.y - b.y, z:a.z - b.z }),
  wip12aScale:(value, scale) => ({ x:value.x * scale, y:value.y * scale, z:value.z * scale }),
  wip12aDistance:(a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z),
  wip12aPointInBounds:(point, bounds, epsilon = 0) =>
    point.x >= bounds.min.x - epsilon && point.x <= bounds.max.x + epsilon &&
    point.y >= bounds.min.y - epsilon && point.y <= bounds.max.y + epsilon &&
    point.z >= bounds.min.z - epsilon && point.z <= bounds.max.z + epsilon,
  wip12aDot:(a, b) => a.x * b.x + a.y * b.y + a.z * b.z,
  wip12aBoundarySurface:(profileId, options = {}) => ({
    ...options,
    profileId,
    thicknessM:options.thicknessM ?? .008,
    yieldStrengthMPa:options.yieldStrengthMPa ?? 355,
    fragmentTransmission01:options.fragmentTransmission01 ?? .3,
    watertight:true
  }),
  shipHitHistory:[],
  wip12aDamagePacketIdempotenceDiagnostic:() => ({ pass:true })
};
context.globalThis = context;
vm.createContext(context);
vm.runInContext(source + `
globalThis.__WIP12E_TEST_API__ = {
  contract:WIP12E_COMPARTMENT_BLAST_CONTRACT,
  core:wip12eRunDiagnostics,
  fixtures:wip12eBlastFixtureDiagnostics,
  authority:wip12eBlastAuthorityProbe,
  idempotence:wip12eBlastIdempotenceProbe,
  performance:wip12eBlastPerformanceProbe,
  budget:wip12eBlastBudgetProbe
};`, context, { filename:'wip12e-module.js' });

const api = context.__WIP12E_TEST_API__;
const runtime = {
  core:api.core(),
  fixtures:api.fixtures(),
  authority:api.authority(),
  idempotence:api.idempotence(),
  budget:api.budget(),
  performance:api.performance(64)
};
const runtimeChecks = {
  core:runtime.core.pass && Object.values(runtime.core.checks).every(Boolean),
  fixtures:runtime.fixtures.pass && Object.values(runtime.fixtures.checks).every(Boolean),
  authority:runtime.authority.pass && Object.values(runtime.authority.checks).every(Boolean),
  idempotence:runtime.idempotence.pass && Object.values(runtime.idempotence.checks).every(Boolean),
  hardBudget:runtime.budget.pass && Object.values(runtime.budget.checks).every(Boolean),
  performance:runtime.performance.impactTimeOnly && !runtime.performance.backlogCreated && runtime.performance.averageMs < 50,
  combatRng:runtime.performance.rngUnchanged && runtime.core.checks.combatRngUnchanged && runtime.fixtures.checks.combatRngUnchanged,
  genericCarrierEquivalence:runtime.core.checks.genericWeaponEquivalence && runtime.core.checks.allExplosivesUseOneKernel,
  timeScaleInvariant:runtime.fixtures.checks.timeScaleInvariant,
  dudZero:runtime.fixtures.checks.dudIsZero
};

const checks = { ...staticChecks, ...Object.fromEntries(Object.entries(runtimeChecks).map(([key, value]) => [`runtime_${key}`, value])) };
assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));

console.log(JSON.stringify({
  result:'PASS',
  scope:'GENERIC_COMPARTMENT_BLAST_V48_WIP12E_STATIC_AND_VM_CONTRACT',
  file:path.basename(file),
  checks,
  counts:{
    static:Object.keys(staticChecks).length,
    runtime:Object.keys(runtimeChecks).length,
    total:Object.keys(checks).length
  },
  performance:{
    iterations:runtime.performance.iterations,
    averageMs:runtime.performance.averageMs,
    rngUnchanged:runtime.performance.rngUnchanged
  },
  capEvidence:{
    dynamicBreaches:runtime.budget.breach.caps.breaches,
    portalEvents:runtime.budget.portalEvents.caps.portalEvents,
    breachTermination:runtime.budget.breach.terminationReason,
    portalTermination:runtime.budget.portalEvents.terminationReason
  }
}, null, 2));
