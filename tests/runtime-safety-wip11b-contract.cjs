const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const file = process.argv[2] || path.join(__dirname, '../Aegis_SIM_v48_WIP11B.html');
const baselineFile = process.argv[3] || path.join(__dirname, '../archive/v48/WIP11A/Aegis_SIM_v48_WIP11A.html');
const html = fs.readFileSync(file, 'utf8');
const baseline = fs.readFileSync(baselineFile, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(match => match[1]).filter(source => source.trim());
for (const [index, source] of scripts.entries()) new vm.Script(source, { filename: `${path.basename(file)}#inline-${index + 1}` });

const hasAll = (...needles) => needles.every(needle => html.includes(needle));
const baselineInvariant = needle => baseline.includes(needle) && html.includes(needle);
const destroyBody = html.match(/function destroyShipRuntime\(entityId\)\{([\s\S]*?)\n\}/)?.[1] ?? '';
const importBody = html.match(/function importOperationalState\(state,options=\{\}\)\{([^\n]+)\}/)?.[1] ?? '';

const checks = {
  title: html.includes('<title>AEGIS v48 WIP11B — Operational Import Safety Hardening</title>'),
  syntax: scripts.length > 0,
  wip11aOwnershipPreserved: baselineInvariant("schema:'AEGIS_SHIP_RUNTIME_V48_WIP11A'") && baselineInvariant("schema:'AEGIS_ENGAGEMENT_RUNTIME_V48_WIP11A'") && baselineInvariant("schema:'AEGIS_AUTHORITY_MANIFEST_V48_WIP11A'"),
  activeDestroyOverrideRemoved: html.includes('function destroyShipRuntime(entityId){') && !html.includes('function destroyShipRuntime(entityId,options') && destroyBody.includes("reason:'ACTIVE_PLAYER_SHIP'") && !destroyBody.includes('allowActive'),
  diagnosticCannotForwardOverride: html.includes('destroyShipRuntimeV48Wip11A:(entityId)=>({...destroyShipRuntime(entityId),shipCount:ENGAGEMENT_RUNTIME.ships.size})'),
  importSafetyContract: hasAll("schema:'AEGIS_OPERATIONAL_IMPORT_SAFETY_V48_WIP11B'", "mode:'CLONE_VALIDATE_NORMALIZE_THEN_APPLY'", "invalidInputMutationPolicy:'ZERO_AUTHORITATIVE_MUTATION'", "exportIsolation:'DETACHED_JSON_SNAPSHOT'", "activeShipDestroyPolicy:'UNCONDITIONAL_REJECT'", "unknownAuthoritativeIdPolicy:'REJECT'"),
  profileRevisionCompatibility: hasAll("schema:'AEGIS_OPERATIONAL_PROFILE_COMPATIBILITY_V48_WIP11B'", 'acceptedRevisions:Object.freeze({[ACTIVE_SHIP_PROFILE.id]:Object.freeze([ACTIVE_SHIP_PROFILE.revision])})', 'operationalProfileRevisionCompatibleV48Wip11B(src.profileId,src.profileRevision)', "operationalErrorV48Wip11B(errors,'PROFILE_REVISION')"),
  completePreflightCodecs: hasAll("Object.freeze({id:'envelope'", "Object.freeze({id:'navigation'", "Object.freeze({id:'weapons'", "Object.freeze({id:'loads'", "Object.freeze({id:'damageFlooding'", "Object.freeze({id:'crew'", "Object.freeze({id:'aviation'"),
  authoritativeIdsValidated: hasAll("operationalErrorV48Wip11B(errors,'VLS_LENGTH'", "operationalErrorV48Wip11B(errors,'LIQUID_LOAD_IDS'", "operationalErrorV48Wip11B(errors,'FLOOD_CELL_ID'", "operationalErrorV48Wip11B(errors,'CREW_GROUP_ID'"),
  cloneAndPreflightBeforeApply: hasAll('src=jsonSafeCloneV48Wip11A(state)', 'source:validation.ok?src:null', 'function applyPreparedOperationalStateV48Wip11B(src,validation,options={})') && importBody.indexOf('prepareOperationalStateV48Wip11B(state)') < importBody.indexOf('if(!validation.ok)throw') && importBody.indexOf('if(!validation.ok)throw') < importBody.indexOf('applyPreparedOperationalStateV48Wip11B'),
  mutationFingerprint: hasAll("schema:'AEGIS_OPERATIONAL_IMPORT_MUTATION_FINGERPRINT_V48_WIP11B'", 'operationalImportMutationFingerprintV48Wip11B:()=>operationalImportMutationFingerprintV48Wip11B()'),
  diagnosticSurface: hasAll('operationalImportSafetyV48Wip11B:()', 'operationalProfileCompatibilityV48Wip11B:()', 'validateOperationalStateV48Wip11B:(state)', 'importOperationalStateV48Wip11B:(state,options={})'),
  readOnlyAuditAndSelftest: hasAll('function operationalImportSafetyAuditV48Wip11B()', 'exportDetached,profileRevisionRejected:', 'activeDestroyUnconditional:', 'OPERATIONAL-IMPORT-SAFETY-V48-WIP11B SELFTEST PASS'),
  operationalSchemaStable: baselineInvariant("const OPERATIONAL_STATE_SCHEMA_V48_WIP11A='AEGIS_OPERATIONAL_STATE_V48_WIP11A'") && hasAll('profileRevision:ACTIVE_SHIP_PROFILE.revision', 'const validateOperationalStateV48Wip11A=validateOperationalStateV48Wip11B'),
  physicsCadenceParity: baselineInvariant('const SIM_FIXED_DT = 1 / 60;') && baselineInvariant('while(left>1e-10){const h=Math.min(left,1/120);left-=h;'),
  protectionContractPreserved: baselineInvariant("schema:'AEGIS_MATERIAL_PROTECTION_V48_WIP11'") && baselineInvariant("status:'ACTIVE_PHYSICS_COUPLED'"),
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result:'PASS', scope:'OPERATIONAL_IMPORT_SAFETY_V48_WIP11B_STATIC_CONTRACT', file:path.basename(file), baseline:path.basename(baselineFile), checks }, null, 2));
