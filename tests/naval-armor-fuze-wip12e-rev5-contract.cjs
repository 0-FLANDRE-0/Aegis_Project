const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12E_REV5_NAVAL_ARMOR_FUZE_COUPLING.html');
const html = fs.readFileSync(file, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1])
  .filter(source => source.trim());

for (const [index, source] of scripts.entries()) {
  new vm.Script(source, { filename:`inline-${index + 1}.js` });
}

const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const solverStart = html.indexOf('function wip12eSolveCompartmentBlast');
const solverEnd = html.indexOf('function wip12eBlastTraceSummary', solverStart);
assert(solverStart >= 0 && solverEnd > solverStart, 'WIP12E blast solver bounds missing');
const solver = html.slice(solverStart, solverEnd);

const checks = {
  title: html.includes('<title>AEGIS v48 WIP12E REV5 — Naval Armor &amp; Fuze Coupling</title>'),
  syntax: scripts.length === 1,
  navalArmorFuzeContract: hasAll(
    "schema:'AEGIS_NAVAL_ARMOR_FUZE_COUPLING_V48_WIP12E_REV5'",
    "basis:'SIM_TUNED_RHA_EQUIVALENT_NORMALIZATION_NOT_CERTIFIED_FUZE_DATA'",
    "impactQualification:'RHAE_PLUS_NORMAL_IMPULSE_AND_PLATE_WORK'"
  ),
  thresholdProfiles: hasAll(
    "LIGHT_DELAY_8:{id:'LIGHT_DELAY_8'",
    "NAVAL_SHORT_DELAY_12:{id:'NAVAL_SHORT_DELAY_12'",
    "HARD_TARGET_DELAY_20:{id:'HARD_TARGET_DELAY_20'",
    'minNormalVelocityMps',
    'minNormalImpulseNs',
    'minPlateWorkJ',
    'maxObliquityDeg'
  ),
  antiShipProfile: hasAll(
    "ANTI_SHIP_DELAY_8:{id:'ANTI_SHIP_DELAY_8'",
    "qualificationProfileId:'ANTI_SHIP_DELAY_8'"
  ),
  kh32AndKh35U: hasAll(
    "WIP12B_LIVE_ORDNANCE.KH32",
    "WIP12B_LIVE_ORDNANCE.KH35U",
    "kh32AndKh35ShareAntiShipQualification"
  ),
  rhaeAndObliquity: hasAll(
    'fuzeStimulusRhaeMm',
    'pathMultiplierCap:1.35',
    "reason:'GRAZING_PATH_LENGTH_MUST_NOT_SELF_QUALIFY'",
    'normalVelocityMps',
    'normalImpulseNs',
    'plateWorkJ'
  ),
  armorSolvers: hasAll(
    "HOMOGENEOUS_ARMOR:'ACTIVE_NAVAL_SIM_TUNED'",
    "FACE_HARDENED_ARMOR:'ACTIVE_NAVAL_SIM_TUNED'",
    "'NAVAL_RHA'",
    "'NAVAL_FACE_HARDENED'"
  ),
  surfaceDamageStages: hasAll(
    "armorStages:Object.freeze(['SCORCH','DENT','CRATER','PERFORATED'])",
    "schema:'AEGIS_SURFACE_DAMAGE_RESPONSE_V48_WIP12E_REV5'",
    'residualThickness01',
    'rearSpallCoupling01'
  ),
  nonPerforatingExternal: hasAll(
    "mode=entryPerforated?'EXTERNAL_DETONATION_THROUGH_ENTRY':blastPerforated?'EXTERNAL_BLAST_BLOWOUT':'NON_PERFORATING_EXTERNAL_DETONATION'",
    "failureMode:'TRANSMITTED_SHOCK_NO_DIRECT_GAS_PATH'",
    'nonPerforatingExternal?0:'
  ),
  thinArmorBlastBlowout: hasAll(
    'function wip12eRev5ExternalBlastBlowout',
    "schema:'AEGIS_EXTERNAL_BLAST_PLATE_RESPONSE_V48_WIP12E_REV5'",
    "reason:failed?'CONTACT_HE_PRESSURE_IMPULSE_PLATE_FAILURE':'ARMOR_HELD_EXTERNAL_BLAST'",
    "kind:'BLAST_EXTERNAL_BLOWOUT'",
    'inwardEjection:true'
  ),
  externalBlowoutEnergyLedger: hasAll(
    'externalPlateWorkJ',
    'ventedBlastJ=Math.max(0,ventedBlastJ-externalPlateWorkJ)',
    'structuralWorkJ+=externalPlateWorkJ',
    'externalBlowoutEnergyClosed'
  ),
  directHotProductPath: hasAll(
    'externalDirectGasPath',
    'directHotProductTransferJ',
    'directHotProductContact',
    'sourceTransferCap01=externalDirectGasPath?.62:.38'
  ),
  genericCarriers: hasAll(
    'applicability:Object.freeze({missiles:true,rockets:true,shells:true,carrierNameBranching:false',
    'genericCarrierContract'
  ),
  weaponAgnosticBlastKernel: !solver.includes("label==='Kh-32'") && !solver.includes("label==='Kh-35U'") && !solver.includes('carrierLabel'),
  sharedDamageAuthority: hasAll(
    "couplingSchema:'AEGIS_BLAST_DAMAGE_COUPLING_V48_WIP12E_REV5'",
    'compartmentDamage',
    'moduleDamage',
    'crewExposure',
    'ignitionCandidates',
    'newBreaches:breaches'
  ),
  persistentScarAuthority: hasAll(
    "'WIP12E_EXTERNAL_BLAST_PLATE_FAILURE'",
    "openingKind==='BLAST_EXTERNAL_BLOWOUT'",
    'authoritativeExternalBlowoutScars',
    'allExternalBlowoutsAuthoritative',
    "persistent:true,ageFade:false,armorStages:true"
  ),
  diagnostics: hasAll(
    'function wip12eRev5NavalArmorFuzeDiagnostics',
    'thinArmorExternalBlastCanBlowHole',
    'thickArmorExternalBlastHolds',
    'wip12eRev5DamageCouplingStatus',
    'wip12eRev5TwoDScarAudit'
  )
};

const failed = Object.entries(checks).filter(([, value]) => !value).map(([key]) => key);
assert.deepEqual(failed, [], `WIP12E REV5 contract failures: ${failed.join(', ')}`);
console.log(JSON.stringify({ schema:'AEGIS_NAVAL_ARMOR_FUZE_STATIC_CONTRACT_V48_WIP12E_REV5', file:path.basename(file), passed:Object.keys(checks).length, failed:0, checks }, null, 2));
