const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12D.html');
const html = fs.readFileSync(file, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(match => match[1]).filter(Boolean);
for (const [index, source] of scripts.entries()) new vm.Script(source, { filename:`inline-${index + 1}.js` });

const start = html.indexOf('// ===== V48 WIP12D KH-32 RESIDUAL-BODY / OVERPENETRATION CORRECTION =====');
const end = html.indexOf('function _wip143FuzeParamsForMissile', start);
assert(start >= 0 && end > start, 'WIP12D source bounds missing');
const source = html.slice(start, end);
const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const sourceHasAll = (...needles) => needles.every(needle => source.includes(needle));
const exitOrder = html.indexOf("if(next.surface.terminalExit&&result.traversalOutcome==='PERFORATED')");
const shatterOrder = html.indexOf("if(result.projectileFailure==='SHATTERED')", exitOrder);

const checks = {
  title: html.includes('<title>AEGIS v48 WIP12D — Kh-32 Residual-Body Overpenetration</title>'),
  syntax: scripts.length > 0,
  contract: sourceHasAll("schema:'AEGIS_RESIDUAL_OVERPENETRATION_V48_WIP12D'", "primary:'KH32_HIGH_SPEED_POST_DETONATION_RESIDUAL_BODIES'", "commonKernel:'ALL_MACRO_FRAGMENT_CASCADES_OPT_IN'"),
  legacyAuthorityUnchanged: sourceHasAll("legacyAsmDamageAuthority:'UNCHANGED_WIP11B_WIP11C_PREACCOUNTED'", 'duplicateLegacyDamageApplication:false', 'residualMechanicalAndBreachSupplement:true') && hasAll("applicationAuthority:'LEGACY_PREACCOUNTED_OBSERVATION_ONLY'", 'mergeDamage:false'),
  physicalMotionAtDetonation: sourceHasAll("source:'LEGACY_RESIDUAL_ENERGY_AT_ACTUAL_DETONATION_DISTANCE'", "physicalKineticReconstruction:'ENTRY_RAW_KE_MULTIPLIED_BY_EFFECTIVE_ENERGY_RATIO'", 'function wip12dPreDetonationMotion') && hasAll('preDetonationResidualEnergyMJ', 'preDetonationResidualReached'),
  inheritedTranslationBounded: sourceHasAll("macroTranslation:'INHERIT_PARENT_VELOCITY_BY_MACRO_MASS'", 'translationRetention01:.92', 'chemicalCouplingFraction01:.024', 'Math.min(parentKineticJ,.5*macroBudgetKg*before.speedMps*before.speedMps'),
  boundedMacroBodies: sourceHasAll('maxBodies:4', 'generatedBodies:bodies.length', 'macroMassKg', 'statisticalFragmentMassKg', 'massClosureErrorKg', 'energyClosureSlackJ'),
  shatterAxesIndependent: sourceHasAll("requiresTraversalOutcome:'PERFORATED'", 'axesIndependent:true', 'function wip12dMacroContinuationPolicy') && hasAll("result.traversalOutcome==='PERFORATED'", "kind:'SHATTER_CONTINUATION'"),
  terminalExitWinsAfterPerforation: exitOrder >= 0 && shatterOrder > exitOrder,
  thicknessAwareShatter: hasAll('thicknessRatio=thicknessM/Math.max(.001,spec.geometry.caliberM)', 'macroThicknessSeverity', 'fullShatterThicknessRatio:.20', 'minThicknessSeverity01:.18'),
  continuationThresholds: sourceHasAll('maxPerBody:6', 'minResidualMassKg:.12', 'minCoherentMassKg:.035', 'minResidualSpeedMps:35', 'minResidualEnergyJ:15000'),
  optInOnly: hasAll("options.macroFragmentContinuation?.enabled&&spec.terminal.modelFamily==='MACRO_FRAGMENT'", 'macroFragmentContinuation:continuationPolicy'),
  eventDrivenRequeryRetained: hasAll('while(eventCount++<policy.maxEvents&&!trace.terminationReason)', 'trace.queryCount++;const next=wip12aNextMaterialEvent', 'state.position=wip12aPointAlong(state.position,state.direction,policy.positionEpsilonM)'),
  boundedReentry: sourceHasAll("mode:'BOUNDED_IMPACT_TIME_OUTSIDE_TO_INSIDE_REQUERY'", "envelope:'PHYSICAL_HULL_PLUS_DETAILED_STRUCTURE_SPACES'", 'maxReentriesPerBody:3', 'maxShellCrossingsPerBody:8', 'maxSamplesPerLeg:512', 'function wip12dFindOutsideEvent', 'function wip12dContinueBodyThroughReentries') && hasAll("crossingRole:'REENTRY'", "kind:'OUTSIDE_FLIGHT'"),
  postExitPrecomputed: sourceHasAll("mode:'PRECOMPUTED_BALLISTIC_ARC_AFTER_FINAL_EXIT'", 'function wip12dPostExitTrajectory', 'gravityMps2:9.80665', 'maxTimeS:8', 'maxDistanceM:1800', 'samples:18'),
  postExitNoFeedback: sourceHasAll('damageFeedback:false', 'renderFramePhysics:false', 'presentationOnly:true'),
  residualBreachSupplement: sourceHasAll("mode:'IDEMPOTENT_MECHANICAL_AND_BREACH_ONLY'", "eventSuffix:'RESIDUAL_SUPPLEMENT'", 'allPerforatedSeaBoundariesBecomeOpenings:true', 'legacyBlastReplay:false', 'genericImpactIgnition:false', 'function wip12dApplyResidualSupplement', 'additionalShellOpenings') && hasAll('damageFloodImpactV48Wip12C(plan.eventId'),
  authoritativeTeardrop: sourceHasAll("physicsAuthority:'WIP101_PATH_BASED_CONSERVATIVE_CHAIN_BLAST'", "shape:'SPEED_WEIGHTED_TEARDROP_MULTI_LOBE'", 'powerFractionConserved:true', 'function wip12dLegacyBlastEnvelope') && hasAll('speedFloor=pathLengthM>=.75', "mesh.name='TERMINAL_BLAST_ENVELOPE'", "'TERMINAL_BLAST_CORE'"),
  waterEntryKinds: sourceHasAll("kind:'SUBMERGED_WATER_ENTRY'", "kind:'SEA_ENTRY'", "termination:reachesSea?'SEA_ENTRY':'DISPLAY_LIMIT'"),
  deterministicNoCombatRng: sourceHasAll('wip12cHash32', 'wip12cUnit', 'rngUnchanged:rngBefore===rngAfter', 'combatRngConsumption:0') && !source.includes('Math.random(') && !source.includes('simRandom('),
  residualDiagnostics: sourceHasAll('function wip12dRunDiagnostics()', "schema:'AEGIS_RESIDUAL_OVERPENETRATION_DIAGNOSTIC_V48_WIP12D'", 'shatterAndTraversalIndependent:', 'massEnergyLedgersClosed:', 'combatRngUnchanged:'),
  liveEventDiagnostics: sourceHasAll('function wip12dResidualEventDiagnostics', "schema:'AEGIS_RESIDUAL_EVENT_DIAGNOSTIC_V48_WIP12D'", 'shatterContinuations:q.shatterContinuations'),
  visualTubesAndMarkers: hasAll("'TERMINAL_MACRO_PATH'", "'TERMINAL_POST_EXIT_PATH'", "mesh.name='TERMINAL_MACRO_BODY'", "mesh.name='TERMINAL_MACRO_EXIT'", "mesh.name='TERMINAL_MACRO_REENTRY'", "mesh.name='TERMINAL_SEA_ENTRY'", 'm.depthTest=false'),
  explicitInteriorOnly: sourceHasAll("visibility:'EXPLICIT_INTERIOR_MODE_ONLY'") && hasAll('this.terminalImpactLayer.visible=showTerminalEffects', 'showTerminalEffects=!!this.interiorTopologyVisible'),
  impactFocus: hasAll('external3DInteriorFocusBtn', 'toggleInteriorImpactFocusV48Wip12D', 'syncInteriorImpactFocusV48Wip12D', 'focusHalfExtentM:', "focusCulling:'OBJECT_AABB_PLUS_LOCAL_CLIPPING_PLANES'", 'this.renderer.localClippingEnabled=true', 'focusClippingPlanes:', 'focusCulledObjects:'),
  focusRebuildBounded: sourceHasAll("focusCullingRebuild:'EVENT_OR_DAMAGE_REVISION_ONLY'") && hasAll('this.interiorFocusSignatureV48Wip12D!==signature', 'box.intersectsBox(focusBox)', 'this.interiorFocusCulledObjectsV48Wip12D=culled'),
  fullInteriorFallback: sourceHasAll('fullInteriorFallback:true') && hasAll("fb.textContent=this.interiorImpactFocusV48Wip12D?'피격 중심':'전체 내부'"),
  hazardsBatched: hasAll("group.name='V48_WIP12D_BATCHED_INTERIOR_HAZARDS'", "WIP12D_HAZARD_BATCH:${kind}", 'group.userData.batchCount++', 'hazardBatchesMax:3'),
  funnelGeometryR2: hasAll("revision:'V48_WIP12D_FUNNEL_EXTENSION_R2'", 'aftExtensionM:3.50,forwardExtensionM:.50,xAftM:3.50,xFwdM:17.10', 'aftExtensionM:1.75,forwardExtensionM:2.25,xAftM:-18.15,xFwdM:-4.55', "schema:'AEGIS_FUNNEL_GEOMETRY_AUDIT_V48_WIP12D_R2'"),
  spg62ClearanceAndMask: hasAll("{id:1,oX:-20.0", 'baseBlindHalfDeg:45,funnelBlindHalfDeg:49,blindHalfDeg:49', 'function spg62FunnelTangentHalfDegV48Wip12D', 'spgPlanClearance:', 'spgLoftClearance:', "mask.join(',')==='41,49,54'"),
  geometryConsumersCoupled: hasAll('funnelForward.xAftM+.65', 'funnelAft.xFwdM-.65', "wip12bDrawCanonicalFunnelProjection(c,'top'", "wip12bDrawCanonicalFunnelProjection(c,'side'", 'AFT_HIGH_SPG_X_M-3.2', "hi.name='AFT_HIGH_SPG_PEDESTAL'", "schema:'AEGIS_FUNNEL_GEOMETRY_3D_AUDIT_V48_WIP12D_R2'"),
  presentationAudit: hasAll('residualOverpenetrationAuditV48Wip12D()', "schema:'AEGIS_3D_RESIDUAL_OVERPENETRATION_AUDIT_V48_WIP12D'", 'postExitRepresented:', 'seaEntriesRepresented:', 'hazardsBatched:'),
  diagnosticsExposed: hasAll('wip12dResidualOverpenetrationContract:()', 'wip12dResidualOverpenetrationDiagnostics:()', 'wip12dResidualEventDiagnostics:', 'wip12dResidualSupplementProbe:()', 'wip12dShipReentryProbe:()', 'wip12dResidualOverpenetration3DAudit:()'),
  renderRevision: hasAll("terminalEffectsRevision:'V48_WIP12D_RESIDUAL_OVERPENETRATION'", "schema:residualMode?'AEGIS_TERMINAL_EFFECT_CASCADE_V48_WIP12D'"),
  scopeHeld: sourceHasAll("'LEGACY_ASM_DAMAGE_RETUNE'", "'LEGACY_ASM_BLAST_REPLAY'", "'UNBOUNDED_FRAGMENT_ENTITIES'", "'RENDER_TIME_BALLISTICS'", "'PERSISTENT_DAMAGE_PATCH'", "'GUN_EXTERIOR_BALLISTICS'"),
  bootSelftest: hasAll('V48 WIP12D residual overpenetration ', 'RESIDUAL-OVERPENETRATION-V48-WIP12D SELFTEST PASS')
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result:'PASS', scope:'RESIDUAL_OVERPENETRATION_V48_WIP12D_STATIC_CONTRACT', file:path.basename(file), checks }, null, 2));
