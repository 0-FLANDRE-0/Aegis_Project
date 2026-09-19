const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const file = process.argv[2] || process.env.SIM_FILE || path.join(__dirname, '../Aegis_SIM_v48_WIP12D.html');
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
  schema: profile.schema === 'AEGIS_SHIP_PROFILE_V48_WIP11' && profile.schemaVersion === 3 && profile.revision === 'V48_WIP11',
  identity: profile.id === 'DDG_119_LATE_FLIGHT_IIA' && profile.identity.hullNumber === 'DDG-119' && profile.identity.flight === 'IIA',
  deeplyFrozen: deeplyFrozen(profile),
  registry: context.registry[profile.id] === profile && Object.keys(context.registry).length === 1,
  runtimeSeparated: runtime.profileId === profile.id && runtime !== profile && runtime.navigation !== profile.navigation && !Object.isFrozen(runtime.navigation),
  noRuntimeBackflow: JSON.stringify(profile) === before && runtime.navigation.heading === 1.234 && runtime.navigation.trail.length === 1,
  dimensions: profile.geometry.lengthM === 155.3 && profile.geometry.bowXM === 82 && profile.geometry.sternXM === -73.3 && profile.geometry.hullStations.length === 10,
  hardpoints: profile.geometry.hardpoints.bridgeMasterE.x === 15.75 && profile.geometry.hardpoints.bridgeMasterE.y === 5.15 && profile.geometry.hardpoints.bridgeMasterE.z === 31.78 && profile.geometry.hardpoints.spg62.length === 3 && profile.geometry.hardpoints.mk45.x === 62,
  flatFlightDeck: profile.geometry.aft.flightDeckStations.length === 8 && profile.geometry.aft.flightDeckStations.every(row => row[2] === profile.geometry.aft.flightDeckPlaneZM) && profile.geometry.aft.flightDeckPlaneZM === 4.88,
  aftContinuity: Math.abs(profile.geometry.aft.hangar.doorSillZM - profile.geometry.aft.flightDeckPlaneZM) <= .03 && profile.geometry.aft.hangar.interiorCeilingZM - profile.geometry.aft.hangar.interiorFloorZM >= profile.geometry.aft.hangar.minClearHeightM,
  aftLowered: profile.geometry.aft.hangar.roofZM < profile.geometry.aft.drawingBaseline.hangarRoofZM && profile.geometry.aft.hangar.doorTopZM < profile.geometry.aft.drawingBaseline.doorTopZM,
  liferaftsGrounded: profile.geometry.aft.liferafts.xM.length === 3 && Math.abs((profile.geometry.aft.liferafts.centerZM - profile.geometry.aft.liferafts.canisterRadiusM) - (profile.geometry.aft.liferafts.supportDeckZM + profile.geometry.aft.liferafts.cradleHeightM)) < 1e-9,
  mk45Mod4: profile.geometry.mk45.basis === 'MK45_MOD4_PUBLIC_VISUAL_APPROX' && profile.geometry.mk45.exposedBarrelM === 7.05 && profile.geometry.mk45.baseDeckZM === 8.05,
  twoDDrawings: html.includes('"schema":"AEGIS_SHIP_DRAWINGS_V48_WIP11"') && html.includes('"revision":"V48_WIP11_MATERIAL_PROTECTION"') && html.includes("twoDProjection:WIP202_SHIP_DRAWINGS.schema==='AEGIS_SHIP_DRAWINGS_V48_WIP11'"),
  vls: profile.weapons.vls.sections.fwd.cells === 32 && profile.weapons.vls.sections.aft.cells === 64 && profile.weapons.vls.sections.aft.defaultLoadout[1].type === 'ESSM4' && profile.weapons.vls.sections.aft.defaultLoadout[1].cells === 24,
  mass: profile.mass.fullLoadTargetKg === 9652445.6336 && profile.mass.lightshipKg === 7085245.6336 && profile.mass.calibratedReferenceGMM === 1.5,
  stabilityIdentity: profile.hydrostatics.schema === 'AEGIS_INTACT_STABILITY_V48_WIP04' && profile.hydrostatics.modelId === 'SHIP_DYNAMIC_STABILITY_V48_WIP04',
  crew: profile.crew.roster === 310 && profile.crew.departments.reduce((n, row) => n + row[2], 0) === 310,
  topology: profile.interior.expected.spaces === 138 && profile.interior.expected.portals === 160 && profile.interior.expected.equipment === 70,
  protectionActive: profile.protection.schema === 'AEGIS_MATERIAL_PROTECTION_V48_WIP11' && profile.protection.status === 'ACTIVE_PHYSICS_COUPLED' && profile.protection.physicsCoupled === true && profile.protection.aramidDirectPenetrationContribution === false,
  rendererReadOnly: profile.renderer.contract === 'PRESENTATION_ONLY_PROFILE_CONSUMER' && profile.renderer.physicsFeedback === false,
  baseline: profile.parity.baselineId === 'V48_WIP10_AFT_GEOMETRY' && profile.parity.baselineSha256 === '2b33fe96d25ee65e4f195e5dd720f6a0d28a6d3ecdd85734976ea90456519cfa' && profile.parity.expectedBehavior === 'WIP10_COMBAT_PRESERVED__MATERIAL_PROTECTION_PHYSICS_COUPLED',
  consumersWired: (html.includes('const shipNav = ACTIVE_SHIP_RUNTIME.navigation;') || html.includes('const shipNav = ACTIVE_SHIP_RUNTIME_V48_WIP09.navigation;')) &&
    html.includes('const WIP199_HULL_STATIONS=ACTIVE_SHIP_PROFILE.geometry.hullStations;') &&
    html.includes('const SENSOR_MODEL=SHIP_SENSOR_MODEL_REGISTRY_V48_WIP09[ACTIVE_SHIP_PROFILE.sensors.modelId];') &&
    html.includes('const cfg=ACTIVE_SHIP_PROFILE.damage.flood;') &&
    html.includes('defs=ACTIVE_SHIP_PROFILE.crew.departments') &&
    html.includes('root.name=ACTIVE_SHIP_PROFILE.renderer.rootName'),
  diagnosticSurface: html.includes('shipProfileV48Wip11:()=>shipProfileSnapshotV48Wip09()') && html.includes('shipProfileAuditV48Wip11:(options={})=>shipProfileAuditV48Wip09(options)') && html.includes('materialProtectionAuditV48Wip11:()=>materialProtectionAuditV48Wip11()'),
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result: 'PASS', scope: 'SHIP_PROFILE_V48_WIP11_STATIC_CONTRACT', scripts, checks }, null, 2));
