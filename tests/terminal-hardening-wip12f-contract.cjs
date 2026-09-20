const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12F.html');
const html = fs.readFileSync(file, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1])
  .filter(source => source.trim());

for (const [index, source] of scripts.entries()) {
  new vm.Script(source, { filename:`inline-${index + 1}.js` });
}

const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const start = html.indexOf("const WIP12F_TERMINAL_HARDENING_CONTRACT");
const end = html.indexOf("// ===== V48 WIP12E GENERIC COMPARTMENT BLAST / DAMAGE AUTHORITY =====", start);
assert(start >= 0 && end > start, 'WIP12F source bounds missing');
const source = html.slice(start, end);

const checks = {
  title:html.includes('<title>AEGIS v48 WIP12F — Terminal Ballistics Closure</title>'),
  syntax:scripts.length === 1,
  contract:hasAll(
    "schema:'AEGIS_TERMINAL_HARDENING_V48_WIP12F'",
    "safetyArming:'EXTERNAL_FLIGHT_STATE_ONLY'",
    "impactInitiation:'QUALIFYING_CONTACT_ONLY'",
    "subThresholdDelayedFuze:'NO_FUNCTION_CONTINUE'",
    "antiShipFallback:'EXPLICIT_INDEPENDENT_SUPERQUICK_EXTERNAL_SIM_ASSUMPTION'"
  ),
  safetySeparateFromImpact:hasAll(
    "flightArmed=flight.launchCleared===true",
    "if(qualification.qualified){if(!safetyArmed)",
    "dudReason='SAFETY_NOT_ARMED_AT_IMPACT'"
  ),
  delayContinuesPastThinPlate:hasAll(
    "LIGHT_DELAY_8:{id:'LIGHT_DELAY_8'",
    "fallbackMode:'NO_FUNCTION_CONTINUE'",
    "if(qualification.action==='NO_FUNCTION_CONTINUE')",
    "thinPlateDoesNotPrematurelyKillDelayFuze"
  ),
  directActionBeforeBodyFracture:hasAll(
    "directAction=profile.mode==='DIRECT_ACTION'",
    "failure!=='FRACTURED'||directAction||baseFuze",
    "directActionInitiatesBeforeBodyFracture"
  ),
  contactTimerStartsAtBoundary:hasAll(
    "timerStarted:false,impactInitiated:false,impactQualified:false",
    "contactTimerStartsAtBoundary"
  ),
  partialNeverOpens:hasAll(
    "holeAreaM2=surface.open?0:perforated?",
    "if(result.traversalOutcome==='PERFORATED'&&result.plate.perforated&&result.plate.holeAreaM2>0)",
    "partialTraversalCreatesOpening:false",
    "partialNeverCreatesOpening"
  ),
  rearSpallAttenuation:hasAll(
    'rearFaceThicknessAttenuation01',
    "PENETRATION_RATIO_X_THICKNESS_CALIBER_EXPONENTIAL",
    'rearSpallAttenuatesWithArmor'
  ),
  kineticSpallSingleApplication:hasAll(
    'function wip12fKineticSpallParts',
    "damageChannel='KINETIC_PLUG_AND_SPALL'",
    'kineticSpallSources:impactMeta?.kineticSpallSources??[]',
    'kineticSpallHasSingleModuleConsumer'
  ),
  authoritativeArmorPatchChannel:hasAll(
    'armorDamagePatches:[]',
    "schema:'AEGIS_ARMOR_DAMAGE_PATCH_V48_WIP12F'",
    'persistent:true,diagnosticOnly:false',
    'const patches=packet.armorDamagePatches?.length?packet.armorDamagePatches:packet.diagnosticPatches??[]'
  ),
  patchPersistenceAndReset:hasAll(
    'const WIP12F_ARMOR_PATCH_LEDGER=new Map()',
    'function wip12fSurfaceWithPersistentPatch',
    'function wip12fCommitArmorPatches',
    'function wip12fResetArmorPatches',
    'wip12fResetArmorPatches();'
  ),
  legacyAsmUsesPatches:hasAll(
    'patchedHitBox=wip12fLegacyBarrierWithPersistentPatch',
    'buildPenetrationBarrierEvents(impactOriginLocal,vdirLocal,shipBoxes,hitBox).map',
    "wip12fCommitLegacyArmorResponse(blastEventId,'OWN_SHIP'"
  ),
  postExitHandoff:hasAll(
    "schema:'AEGIS_POST_EXIT_PROJECTILE_HANDOFF_V48_WIP12F'",
    "trace.events.push({kind:'POST_EXIT_PROJECTILE_HANDOFF'",
    "trace.terminationReason='TARGET_EXIT'",
    'postExitLiveProjectileHandedOff'
  ),
  bothAsmDelayRanges:hasAll(
    "delayS:(ASM_PROFILES['Kh-32'].fuzeDelayMinS+ASM_PROFILES['Kh-32'].fuzeDelayMaxS)/2",
    "delayS:(ASM_PROFILES['Kh-35U'].fuzeDelayMinS+ASM_PROFILES['Kh-35U'].fuzeDelayMaxS)/2",
    'kh32AndKh35HaveExplicitDelay'
  ),
  genericExplosiveKernel:hasAll(
    "applicability:Object.freeze({missiles:true,rockets:true,shells:true,carrierNameBranching:false",
    "sourceClass:'DAMAGE_PACKET_GENERIC_EXPLOSIVE'"
  ),
  diagnostics:hasAll(
    'function wip12fTerminalHardeningDiagnostics',
    'wip12fTerminalHardeningContract:',
    'wip12fTerminalHardeningDiagnostics:',
    'wip12fArmorPatches:',
    'wip12fResetArmorPatches:'
  )
};

const failed = Object.entries(checks).filter(([, value]) => !value).map(([key]) => key);
assert.deepEqual(failed, [], `WIP12F contract failures: ${failed.join(', ')}`);
console.log(JSON.stringify({
  schema:'AEGIS_TERMINAL_HARDENING_STATIC_CONTRACT_V48_WIP12F',
  file:path.basename(file),
  passed:Object.keys(checks).length,
  failed:0,
  checks
}, null, 2));
