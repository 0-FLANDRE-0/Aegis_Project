const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const defaultCandidate = path.join(__dirname, '../Aegis_SIM_v48_WIP12A.html');
const archivedBaseline = path.join(__dirname, '../archive/v48/WIP11C/Aegis_SIM_v48_WIP11C.html');
const rootBaseline = path.join(__dirname, '../Aegis_SIM_v48_WIP11C.html');
const file = process.argv[2] || process.env.SIM_FILE || defaultCandidate;
const baselineFile = process.argv[3] || process.env.TERMINAL_BASELINE_SIM_FILE || (fs.existsSync(archivedBaseline) ? archivedBaseline : rootBaseline);
const html = fs.readFileSync(file, 'utf8');
const baseline = fs.readFileSync(baselineFile, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(match => match[1]).filter(source => source.trim());
for (const [index, source] of scripts.entries()) new vm.Script(source, { filename:`${path.basename(file)}#inline-${index + 1}` });

function functionSource(source, name) {
  const needle = `function ${name}(`, start = source.indexOf(needle);
  if (start < 0) return null;
  const open = source.indexOf('{', start);
  let depth = 1, state = 'code', escape = false;
  const templateTargets = [];
  for (let i = open + 1; i < source.length; i++) {
    const c = source[i], n = source[i + 1];
    if (state === 'line') { if (c === '\n') state = 'code'; continue; }
    if (state === 'block') { if (c === '*' && n === '/') { state = 'code'; i++; } continue; }
    if (state === 'single' || state === 'double') { if (escape) { escape = false; continue; } if (c === '\\') { escape = true; continue; } if ((state === 'single' && c === "'") || (state === 'double' && c === '"')) state = 'code'; continue; }
    if (state === 'template') { if (escape) { escape = false; continue; } if (c === '\\') { escape = true; continue; } if (c === '`') { state = 'code'; continue; } if (c === '$' && n === '{') { depth++; templateTargets.push(depth - 1); state = 'code'; i++; } continue; }
    if (c === '/' && n === '/') { state = 'line'; i++; continue; }
    if (c === '/' && n === '*') { state = 'block'; i++; continue; }
    if (c === "'") { state = 'single'; continue; }
    if (c === '"') { state = 'double'; continue; }
    if (c === '`') { state = 'template'; continue; }
    if (c === '{') { depth++; continue; }
    if (c === '}') { depth--; if (templateTargets.length && depth === templateTargets.at(-1)) { templateTargets.pop(); state = 'template'; continue; } if (depth === 0) return source.slice(start, i + 1); }
  }
  throw new Error(`unterminated function ${name}`);
}

const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const kernelStart = html.indexOf('// ===== V48 WIP12A COMMON TERMINAL-BALLISTICS FOUNDATION =====');
const kernelEnd = html.indexOf('// Get ASM RCS based on observer angle', kernelStart);
assert(kernelStart >= 0 && kernelEnd > kernelStart, 'WIP12A kernel source bounds missing');
const kernel = html.slice(kernelStart, kernelEnd);
const traceSource = functionSource(html, 'wip12aTraceTerminalProjectile') || '';
const compatStart = kernel.indexOf('function wip12aLegacyAsmPenetrationCompat');
const compatSource = kernel.slice(compatStart, kernel.indexOf('function wip12aTerminalBallistics', compatStart));
const liveImpact = functionSource(html, 'updateEnemyMissile') || '';
const exactLegacyFunctions = [
  'penetrationEnergyState',
  'solveResidualPenetration',
  'buildPenetrationBarrierEvents',
  'buildV48Wip02ImpactState',
  'v48Wip02TransferredImpulse',
  'wip113DudImpactProfile',
  'computeAsmBlastEffects',
  'damageFloodImpactV1'
];

const checks = {
  title: html.includes('<title>AEGIS v48 WIP12A — Common Terminal Ballistics Foundation</title>'),
  syntax: scripts.length > 0,
  exactWip11cBaselinePresent: baseline.includes('<title>AEGIS v48 WIP11C — ASM Wreckage and Water-Surface Effects</title>'),
  commonContract: hasAll("schema:'AEGIS_TERMINAL_BALLISTICS_V48_WIP12A'", "coordinateSpace:'SHIP_LOCAL_METRES'", "units:'SI'", "authority:'IMPACT_EVENT_ONLY'"),
  specSeparatesMass: hasAll("schema:'AEGIS_TERMINAL_PROJECTILE_SPEC_V48_WIP12A'", 'massKg,penetratorMassKg', 'penetratorMassKg<=WIP12A_DIAGNOSTIC_PROJECTILES[id].body.massKg'),
  bodyAxisAuthoritative: hasAll("stateAuthority:Object.freeze(['position','direction','bodyAxis'", "derivedState:Object.freeze(['kineticEnergyJ','coherentEnergyJ','momentumNs','yawRad'])", 'function wip12aYawRad(state)'),
  normalizedVectors: hasAll('direction=wip12aUnit(', 'bodyAxis=wip12aUnit(', 'normal:wip12aUnit('),
  distinctTraversalSpaces: hasAll("traversalSpaces:Object.freeze(['BOUNDARY','EMPTY','DAMAGE_VOLUME','CREW_EXPOSURE'])", "resistancePolicy:'ZERO_PROJECTILE_RESISTANCE'", 'WIP12A_DAMAGE_VOLUME_REQUIRES_EXPLICIT_MATERIAL'),
  emptyHasNoResistance: hasAll('function wip12aAdvanceEmpty(state,distanceM)', 'wip12aTickFuze(out,dt)', 'emptyPreservesProjectile:'),
  independentResultAxes: hasAll("traversalOutcome:Object.freeze(['RICOCHET','STOPPED','PARTIAL','PERFORATED'])", "projectileFailure:Object.freeze(['INTACT','DEFORMED','FRACTURED','SHATTERED'])", 'traversalOutcome,projectileFailure,plateFailureMode'),
  regimeRegistry: hasAll('const WIP12A_SOLVER_REGISTRY=Object.freeze({', 'THIN_DUCTILE_PLATE:wip12aThinPlateSolver', 'LIGHT_STRUCTURE:wip12aLightStructureSolver', "VOLUME_CRUSH:'wip12aVolumeCrushSolver'"),
  armorSolversRejectExplicitly: hasAll('HOMOGENEOUS_ARMOR:null,FACE_HARDENED_ARMOR:null', "trace.terminationReason='UNSUPPORTED_SOLVER'"),
  eventDrivenRequery: hasAll("mode:'REQUERY_AFTER_EVERY_STATE_CHANGE'", 'while(eventCount++<policy.maxEvents', 'trace.queryCount++;const next=wip12aNextMaterialEvent(state,geometry', 'W12A_REQUERIED_CONTACT'),
  fuzeEventCompetition: hasAll("candidates:Object.freeze(['BOUNDARY_CONTACT','VOLUME_ENTRY','VOLUME_EXIT','PROJECTILE_STOP','FUZE_EXPIRY'])", "coTimed:'FUZE_AT_CONTACT_AFTER_CONTACT_RESOLUTION'", "outcome='FUZE_EXPIRED'", "outcome='FUZE_AT_EXIT'"),
  impactBudget: hasAll('function wip12aImpactBudget(before,after,parts={})', 'energyClosureErrorJ', 'massClosureErrorKg', 'momentumClosureErrorNs'),
  damagePacketIdentity: hasAll("schema:'AEGIS_DAMAGE_PACKET_V48_WIP12A'", 'impactEventId:String(context.impactEventId)', "idempotenceKey:'impactEventId'", "'DUPLICATE_IMPACT_EVENT'"),
  damageChannelsSeparated: hasAll("channels:Object.freeze(['directPenetration','plugAndSpall','warheadFragments','blast','thermalIncendiary','breaches','structuralImpulse','crewExposure'])", 'directPenetration:[]', 'plugAndSpall:[]', 'warheadFragments:[]', 'thermalIncendiary:[]'),
  calculationSeparatedFromApplication: !traceSource.includes('damageFloodImpactV1(') && !traceSource.includes('addModuleDmg(') && hasAll('function wip12aApplyDamagePacket(packet,options={})', 'calculationSeparatedFromApplication:true'),
  aramidChannelOnly: hasAll('directPenetration:false,fragmentHalfValueMm:10,rearSpallHalfValueMm:7.5', 'directWorkUnchanged:', 'fragmentReduced:', 'rearSpallReduced:'),
  diagnosticPatchDeferred: hasAll('persistentDamagePatch:false', "diagnosticOnly:true", "'PERSISTENT_PATCH_LEDGER'"),
  sixDiagnosticFixtures: ['TEST_12P7_AP','TEST_30_AP','TEST_30_HEI','TEST_76_SAP','TEST_127_HE','TEST_127_SAP'].every(id => kernel.includes(`${id}:wip12aProjectileSpec`) && kernel.includes("sourceClass:'DIAGNOSTIC_SIM_TUNED'")),
  boundaryEnvelopeEachFixture: hasAll('function wip12aBoundaryEnvelopeForSpec(specId)', "STOPPED:wip12aFindBoundaryCase", "PARTIAL:wip12aFindBoundaryCase", "PERFORATED:wip12aFindBoundaryCase", "RICOCHET:wip12aFindBoundaryCase"),
  legacyAdapterIsActive: liveImpact.includes("mode:'LEGACY_ASM_PENETRATION_COMPAT'") && liveImpact.includes('const penSolve=penCompat.penetration;') && !liveImpact.includes('const penSolve=solveResidualPenetration('),
  legacyAdapterPreservesAuthority: compatSource.includes('solveResidualPenetration(') && !compatSource.includes('simRandom(') && !compatSource.includes('rand('),
  legacyFunctionsByteExact: exactLegacyFunctions.every(name => functionSource(html, name) === functionSource(baseline, name)),
  kernelDoesNotConsumeCombatRng: !kernel.includes('simRandom(') && !kernel.includes('rand('),
  liveMigrationDeferred: hasAll('liveAsmMigration:false', "mode:'LEGACY_ASM_PENETRATION_COMPAT'"),
  outOfScopeStaysExcluded: hasAll("exclusions:Object.freeze(['GUN_LAUNCH','EXTERIOR_BALLISTICS','FCS','PERSISTENT_PATCH_LEDGER','HOMOGENEOUS_ARMOR_LIVE_SOLVER','FACE_HARDENED_ARMOR_LIVE_SOLVER'])"),
  diagnosticsExposed: hasAll('wip12aTerminalBallisticsContract:()', 'wip12aRunFixture:', 'wip12aTerminalDiagnostics:()', 'wip12aDamagePacketIdempotence:()', 'wip12aPerformance:'),
  bootSelftest: hasAll('V48 WIP12A terminal ballistics ', 'TERMINAL-BALLISTICS-V48-WIP12A SELFTEST PASS')
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result:'PASS', scope:'COMMON_TERMINAL_BALLISTICS_V48_WIP12A_STATIC_CONTRACT', file:path.basename(file), baseline:path.basename(baselineFile), checks }, null, 2));
