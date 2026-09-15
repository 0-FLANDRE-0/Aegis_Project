const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const file = process.argv[2] || path.join(__dirname, '../Aegis_SIM_v48_WIP09.html');
const html = fs.readFileSync(file, 'utf8');
let scripts = 0;
for (const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
  if (/\bsrc\s*=|application\/json/.test(m[1])) continue;
  new Function(m[2]);
  scripts++;
}

function section(a, b) {
  const i = html.indexOf(a), j = html.indexOf(b, i);
  assert(i >= 0 && j > i, a);
  return html.slice(i, j);
}

const context = vm.createContext({ console, Math, WeakSet, Object, JSON });
vm.runInContext(
  section('function deepFreezeShipProfileV48Wip09(', 'function shipHdgDeg()') +
  '\nglobalThis.profile=ACTIVE_SHIP_PROFILE;globalThis.runtime=ACTIVE_SHIP_RUNTIME_V48_WIP09;globalThis.registry=SHIP_PROFILE_REGISTRY_V48_WIP09;',
  context,
);

const profile = context.profile, runtime = context.runtime;
const deeplyFrozen = (value, seen = new WeakSet()) => {
  if (!value || typeof value !== 'object' || seen.has(value)) return true;
  seen.add(value);
  return Object.isFrozen(value) && Object.values(value).every(v => deeplyFrozen(v, seen));
};
const before = JSON.stringify(profile);
runtime.navigation.heading = 1.234;
runtime.navigation.trail.push({ x: 1, y: 2 });

const checks = {
  inlineJavaScript: scripts === 1,
  schema: profile.schema === 'AEGIS_SHIP_PROFILE_V48_WIP09' && profile.schemaVersion === 1,
  identity: profile.id === 'DDG_119_LATE_FLIGHT_IIA' && profile.identity.hullNumber === 'DDG-119' && profile.identity.flight === 'IIA',
  deeplyFrozen: deeplyFrozen(profile),
  registry: context.registry[profile.id] === profile && Object.keys(context.registry).length === 1,
  runtimeSeparated: runtime.profileId === profile.id && runtime !== profile && runtime.navigation !== profile.navigation && !Object.isFrozen(runtime.navigation),
  noRuntimeBackflow: JSON.stringify(profile) === before && runtime.navigation.heading === 1.234 && runtime.navigation.trail.length === 1,
  dimensions: profile.geometry.lengthM === 155.3 && profile.geometry.bowXM === 82 && profile.geometry.sternXM === -73.3 && profile.geometry.hullStations.length === 9,
  hardpoints: profile.geometry.hardpoints.bridgeMasterE.x === 15.75 && profile.geometry.hardpoints.bridgeMasterE.y === 5.15 && profile.geometry.hardpoints.bridgeMasterE.z === 31.78 && profile.geometry.hardpoints.spg62.length === 3,
  vls: profile.weapons.vls.sections.fwd.cells === 32 && profile.weapons.vls.sections.aft.cells === 64 && profile.weapons.vls.sections.aft.defaultLoadout[1].type === 'ESSM4' && profile.weapons.vls.sections.aft.defaultLoadout[1].cells === 24,
  mass: profile.mass.fullLoadTargetKg === 9652445.6336 && profile.mass.lightshipKg === 7085245.6336 && profile.mass.calibratedReferenceGMM === 1.5,
  crew: profile.crew.roster === 310 && profile.crew.departments.reduce((n, row) => n + row[2], 0) === 310,
  topology: profile.interior.expected.spaces === 138 && profile.interior.expected.portals === 160 && profile.interior.expected.equipment === 70,
  protectionDeferred: profile.protection.status === 'SCHEMA_ONLY_DEFERRED_TO_WIP10' && profile.protection.physicsCoupled === false && profile.protection.externalShell === null,
  rendererReadOnly: profile.renderer.contract === 'PRESENTATION_ONLY_PROFILE_CONSUMER' && profile.renderer.physicsFeedback === false,
  baseline: profile.parity.baselineId === 'V48_WIP08_BRIDGEMASTER_E' && profile.parity.expectedBehavior === 'NO_GAMEPLAY_CHANGE',
  consumersWired: html.includes('const shipNav = ACTIVE_SHIP_RUNTIME_V48_WIP09.navigation;') &&
    html.includes('const WIP199_HULL_STATIONS=ACTIVE_SHIP_PROFILE.geometry.hullStations;') &&
    html.includes('const SENSOR_MODEL=SHIP_SENSOR_MODEL_REGISTRY_V48_WIP09[ACTIVE_SHIP_PROFILE.sensors.modelId];') &&
    html.includes('const cfg=ACTIVE_SHIP_PROFILE.damage.flood;') &&
    html.includes('defs=ACTIVE_SHIP_PROFILE.crew.departments') &&
    html.includes('root.name=ACTIVE_SHIP_PROFILE.renderer.rootName'),
  diagnosticSurface: html.includes('shipProfileV48Wip09:()=>shipProfileSnapshotV48Wip09()') && html.includes('shipProfileAuditV48Wip09:(options={})=>shipProfileAuditV48Wip09(options)'),
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result: 'PASS', scope: 'SHIP_PROFILE_V48_WIP09_STATIC_CONTRACT', scripts, checks }, null, 2));
