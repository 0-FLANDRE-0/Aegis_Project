const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12D.html');
const html = fs.readFileSync(file, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(match => match[1]).filter(Boolean);
for (const [index, source] of scripts.entries()) new vm.Script(source, { filename:`inline-${index + 1}.js` });

const start = html.indexOf('// ===== V48 WIP12C INTERNAL TERMINAL-EFFECT CASCADE =====');
const end = html.indexOf('function _wip143FuzeParamsForMissile', start);
assert(start >= 0 && end > start, 'WIP12C source bounds missing');
const source = html.slice(start, end);
const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const sourceHasAll = (...needles) => needles.every(needle => source.includes(needle));

const checks = {
  title: html.includes('<title>AEGIS v48 WIP12C — Internal Terminal Effects and Residual Bodies</title>') || html.includes('<title>AEGIS v48 WIP12D — Kh-32 Residual-Body Overpenetration</title>'),
  syntax: scripts.length > 0,
  contract: sourceHasAll("schema:'AEGIS_INTERNAL_TERMINAL_EFFECTS_V48_WIP12C'", "rootAuthority:'WIP12A_IMPACT_TRACE_AND_DAMAGE_PACKET'", "mode:'BOUNDED_DETERMINISTIC_MACRO_BODIES'"),
  boundedMacroBodies: sourceHasAll('maxBodies:4', 'minBodyMassKg:.12', 'minBodyEnergyJ:1200', "fineFragments:'STATISTICAL_DAMAGE_CHANNEL'"),
  deterministicHashOnly: sourceHasAll('function wip12cHash32', 'function wip12cUnit', 'function wip12cMacroDirection') && !source.includes('simRandom(') && !source.includes('rand(') && !source.includes('Math.random('),
  preDetonationStatePreserved: hasAll('stateBefore=wip12aStateSnapshot(state)', 'stateBefore,stateAfter:wip12aStateSnapshot(state)'),
  commonChildTraversal: sourceHasAll("sourceClass:'TERMINAL_MACRO_FRAGMENT_DETERMINISTIC'", 'wip12aTraceTerminalProjectile(plan.spec,plan.state', "payloadType:'INERT'", "fuzeType:'NONE'"),
  statePropagation: sourceHasAll('coherentMassKg:massKg*.86', 'integrity01:clamp(', 'bodyAxis:wip12aUnit(', 'initialSpeedMps:plan.state.speedMps'),
  massEnergyLedger: sourceHasAll('parentNonExplosiveMassKg', 'macroMassKg', 'statisticalFragmentMassKg', 'massClosureErrorKg', 'chemicalEnergyCoupledJ', 'macroInitialKineticJ', 'energyClosureSlackJ'),
  childChannelsFlattenedOnce: sourceHasAll("commonKernel:'FLATTEN_CHILD_CHANNELS_APPLY_PARENT_PACKET_ONCE'", 'function wip12cMergeChildPacket', 'mergeDamage=options.mergeDamage!==false', 'wip12cMergeChildPacket(trace.damagePacket'),
  legacyPreaccounted: sourceHasAll("legacyAsm:'OBSERVE_PREACCOUNTED_RESULT_NO_SECOND_DAMAGE'") && hasAll("applicationAuthority:'LEGACY_PREACCOUNTED_OBSERVATION_ONLY'", 'mergeDamage:false'),
  dynamicFarHullExit: sourceHasAll('function wip12cShipMacroGeometry', 'function wip12cRayHullExit', 'function wip12cHullSurfaceInfo', 'function wip12cDynamicHullEvent', "id:`W12C_FAR_HULL_", 'terminalExit:true', 'farHullExits'),
  indexedImpactTimeTraversal: sourceHasAll("queryMode:'IMPACT_TIME_DYNAMIC_QUERY'", "interiorBoundaries:'INDEXED_DETAILED_SPACE_MATERIALS'", 'function wip12cBuildSpatialBins', 'function wip12cDetailedBoundaryEvents', 'function wip12cIndexedVolumeEvents', 'renderFrameQueries:0'),
  shipTraversalBenchmark: sourceHasAll('function wip12cShipTraversalPerformance', "schema:'AEGIS_SHIP_TRAVERSAL_PERFORMANCE_V48_WIP12C'", 'candidateReduction01:', 'perImpactMs:totalMs/n'),
  materialSpecificInternalPath: sourceHasAll("'WATERTIGHT_MACHINERY'", "'WATERTIGHT_GENERAL'", "'MAGAZINE_LOCAL'", "'INTERNAL_DECK'", "'LIGHT_PARTITION'", 'function wip12cInteriorBoundaryProfile'),
  boundedTraversal: sourceHasAll('maxPathM:80', 'maxEventsPerBody:128', 'maxBodies:4') && hasAll('eventPolicy.positionEpsilonM', "trace.terminationReason='TARGET_EXIT'"),
  cachedDetailedMaterialVolumes: sourceHasAll('WIP12C_SHIP_GEOMETRY_CACHE', 'topology.equipmentNodes', "q.kind==='TANK'", 'volumeCandidatesScanned', 'candidateReduction01'),
  damagePacketCorridors: hasAll('penetrationCorridors:[]', 'packet.penetrationCorridors.push(', 'penetrationLines:corridors'),
  multiPathFloodConsumer: hasAll('function damageFloodImpactV48Wip12C', 'penetrationLines,additionalShellOpenings:', 'const sourceLines=Array.isArray(event.penetrationLines)'),
  multiPathCrewConsumer: hasAll('penetrationLineCount:lineRows.length', 'const sourceLines=Array.isArray(event.penetrationLines)&&event.penetrationLines.length', 'for(const line of lineRows)for(const s of spaces'),
  explicitIgnitionConsumer: hasAll('thermalIncendiaryMassKg:thermalMassKg', 'mechanicalIgnitionCandidates:wip12cMechanicalIgnitionCandidates(packet)', 'control.impact(id,impactMeta?.detonationPoint??stop??start,parts,false)', 'wip12cApplyTerminalIgnition'),
  rareMechanicalIgnition: sourceHasAll("mechanicalImpact:'RARE_DETERMINISTIC_VULNERABLE_MATERIAL_ONLY'", 'function wip12cMechanicalIgnitionDecision', 'probability01=Math.min(classCap,declaredCap)*energyFactor*speedFactor', 'structuralImpulseIgnition:false', 'genericImpactIgnition:false'),
  mechanicalIgnitionApplicationProbe: sourceHasAll('function wip12cMechanicalIgnitionApplicationProbe', "source==='MECHANICAL_IMPACT'", "reason:'NO_DETERMINISTIC_IGNITION_IN_SEARCH_BOUND'", 'beforeBurning:before.summary.burning', 'afterBurning:after.summary.burning'),
  ignitionCaps: sourceHasAll('FUEL_LUBE:.018', 'AVIATION_FUEL:.014', 'ELECTRICAL:.008', 'ORDNANCE:.006', 'INERT:0'),
  legacyDamageEntryPreserved: hasAll('function damageFloodImpactV1(', 'damageAppliedBy:\'LEGACY_ASM_DAMAGE_PATH\''),
  visualContract: sourceHasAll('function wip12cVisualFromCascade', 'secondaryPaths:', 'macroBodies:', "kind:'MACRO_EXIT'"),
  visualObjects: (hasAll("line.name='TERMINAL_MACRO_PATH'", "mesh.name='TERMINAL_MACRO_BODY'", "mesh.name='TERMINAL_MACRO_EXIT'") || hasAll("'TERMINAL_MACRO_PATH'", "mesh.name='TERMINAL_MACRO_BODY'", "mesh.name='TERMINAL_MACRO_EXIT'")),
  terminalInteriorOnly: hasAll('showTerminalEffects=!!this.interiorTopologyVisible', 'this.terminalImpactLayer.visible=showTerminalEffects'),
  exteriorCoarseView: hasAll('showCoarse=throughHole&&!this.interiorTopologyVisible', 'this.compartmentInteriorV8.visible=showCoarse', 'this.buildCompartmentInteriorV8(cells)'),
  explicitDetailedView: hasAll('showDetails=!!this.interiorTopologyVisible', 'this.interiorTopologyLayer.visible=showDetails', 'this.interiorHazardLayer.visible=showDetails', 'this.interiorCrewLayer.visible=showDetails'),
  exteriorTransparency: hasAll('setInteriorExteriorTransparencyV48Wip06(this.interiorTopologyVisible)', 'exteriorTransparentInInteriorMode:true'),
  presentationAudit: hasAll('internalEffectsAuditV48Wip12C()', "schema:'AEGIS_3D_INTERNAL_TERMINAL_EFFECTS_AUDIT_V48_WIP12C'", 'macroPathsRepresented:', 'farHullExitsRepresented:'),
  dudNoCascade: sourceHasAll("reason:'NO_FUNCTIONING_DETONATION'", 'dudCreatesNoCascade:'),
  rngInvariant: sourceHasAll('rngBefore=SIM_RNG_STATE>>>0', 'rngUnchanged:rngBefore===rngAfter', 'combatRngUnchanged:'),
  fixture: sourceHasAll('function wip12cFixtureGeometry()', "WIP12A_DIAGNOSTIC_PROJECTILES.TEST_127_SAP", 'function wip12cRunFixture'),
  diagnostics: sourceHasAll('function wip12cRunDiagnostics()', "schema:'AEGIS_INTERNAL_TERMINAL_EFFECTS_DIAGNOSTIC_V48_WIP12C'", 'presentationSplit:'),
  diagnosticsExposed: hasAll('wip12cInternalEffectsContract:()', 'wip12cRunFixture:', 'wip12cShipTraversalProbe:', 'wip12cShipTraversalPerformance:', 'wip12cIgnitionPolicyDiagnostics:()', 'wip12cMechanicalIgnitionApplicationProbe:()', 'wip12cInternalEffectsDiagnostics:()', 'wip12cInternalEffects3DAudit:()'),
  renderRevision: (hasAll("terminalEffectsRevision:'V48_WIP12C_INTERNAL_EFFECT_CASCADE'", 'cascadeSummary:e.cascade?') || hasAll("terminalEffectsRevision:'V48_WIP12D_RESIDUAL_OVERPENETRATION'", 'cascadeSummary:e.cascade?')),
  scopeHeld: sourceHasAll("'GUN_LAUNCH'", "'EXTERIOR_BALLISTICS'", "'SURFACE_FIRE_CONTROL'", "'PERSISTENT_PATCH_LEDGER'", "'LEGACY_ASM_SOLVER_MIGRATION'"),
  bootSelftest: hasAll('V48 WIP12C internal terminal effects ', 'INTERNAL-TERMINAL-EFFECTS-V48-WIP12C SELFTEST PASS')
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result:'PASS', scope:'INTERNAL_TERMINAL_EFFECTS_V48_WIP12C_STATIC_CONTRACT', file:path.basename(file), checks }, null, 2));
