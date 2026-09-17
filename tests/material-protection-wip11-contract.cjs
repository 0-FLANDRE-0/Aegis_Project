const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');

const file = process.argv[2] || path.join(__dirname, '../Aegis_SIM_v48_WIP11.html');
const html = fs.readFileSync(file, 'utf8');
const section = (a, b) => {
  const i = html.indexOf(a), j = html.indexOf(b, i);
  assert(i >= 0 && j > i, `missing source section ${a}`);
  return html.slice(i, j);
};
const context = vm.createContext({ console, Math, WeakSet, Object, JSON, Number, Error,
  clamp: (value, lo, hi) => Math.max(lo, Math.min(hi, value)) });
vm.runInContext(
  section('function deepFreezeShipProfileV48Wip09(', 'function shipHdgDeg()') +
  section('// V48 WIP11 material contract.', 'function updateShipMovement(dt)') +
  '\nglobalThis.materials=V48_WIP11_MATERIAL_LIBRARY;globalThis.boundaries=V48_WIP11_BOUNDARY_LIBRARY;globalThis.profile=ACTIVE_SHIP_PROFILE;globalThis.metrics=wip11BoundaryMetrics;globalThis.ref=wip11BoundaryReferenceMetrics;',
  context,
);

const { materials, boundaries, profile, metrics, ref } = context;
const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps * Math.max(1, Math.abs(a), Math.abs(b));
const upper = ref('SHELL_UPPER'), bottom = ref('SHELL_BOTTOM_BILGE'), flight = ref('FLIGHT_DECK');
const cic = ref('CIC_LOCAL'), magazine = ref('MAGAZINE_LOCAL'), steering = ref('STEERING_CABLE_LOCAL');
const closedDoor = ref('WATERTIGHT_DOOR'), openDoor = ref('WATERTIGHT_DOOR', { open: true });
const area = Math.PI * Math.pow(.42 / 2, 2);

const checks = {
  contract: profile.protection.schema === 'AEGIS_MATERIAL_PROTECTION_V48_WIP11' && profile.protection.physicsCoupled === true,
  materialSet: ['HSLA_80', 'DH36', 'AH36', 'GRADE_A_STEEL', 'ARAMID_SPLINTER'].every(id => materials[id]),
  density: materials.HSLA_80.densityKgM3 === 7850 && materials.DH36.densityKgM3 === 7850 && materials.ARAMID_SPLINTER.densityKgM3 === 1440,
  yieldStrength: materials.HSLA_80.yieldStrengthMPa === 552 && materials.DH36.yieldStrengthMPa === 355 && materials.GRADE_A_STEEL.yieldStrengthMPa === 235,
  formula: near(upper.directResistanceMJ, area * .012 * 552) && near(flight.directResistanceMJ, area * .010 * 355),
  referenceRanges: upper.directResistanceMJ > .90 && upper.directResistanceMJ < .94 && bottom.directResistanceMJ > 1.09 && bottom.directResistanceMJ < 1.12 && magazine.directResistanceMJ > 1.03 && magazine.directResistanceMJ < 1.07,
  underwaterStronger: bottom.directResistanceMJ > upper.directResistanceMJ,
  aramidNoDirectResistance: [cic, magazine, steering].every(row => row.layers.find(q => q.materialId === 'ARAMID_SPLINTER').directResistanceMJ === 0),
  aramidHasMass: magazine.arealDensityKgM2 > 7850 * .012 && magazine.linerThicknessMm === 15,
  aramidAttenuates: magazine.fragmentTransmission01 < cic.fragmentTransmission01 && magazine.rearSpallTransmission01 < cic.rearSpallTransmission01,
  fragmentPropagationCoupling: html.includes('wip11InteriorFragmentTransfer(next,cur.f*ff') && html.includes("bypassReason:'SOURCE_ROOM_DETONATION'") && html.includes("bypassReason:'OPEN_BOUNDARY'"),
  openDoor: closedDoor.directResistanceMJ > 0 && openDoor.directResistanceMJ === 0 && openDoor.fragmentTransmission01 === 1,
  smallerProjectile: metrics('SHELL_UPPER', { diameterM: .127 }).directResistanceMJ < upper.directResistanceMJ,
  boundarySet: ['KEEL_CENTER_GIRDER', 'SHELL_WATERLINE', 'STRENGTH_MAIN_DECK', 'WATERTIGHT_MACHINERY', 'FIRE_BULKHEAD', 'HANGAR_DOOR', 'FUNNEL_SKIN', 'CIC_LOCAL', 'MAGAZINE_LOCAL'].every(id => boundaries[id]),
  noLegacyUnderwaterConstant: !html.includes('belowWaterResistanceMJ:0.65'),
  solverCoupling: html.includes("model:'MATERIAL_THICKNESS'") && html.includes('wip11PenetrationBarrier(profile,st,initialResistanceMJ'),
  massCoupling: html.includes("'material:'+boundaryId") && html.includes('structuralMaterialMassKg') && html.includes('residualOutfitMassKg'),
};

assert.deepEqual(checks, Object.fromEntries(Object.keys(checks).map(key => [key, true])));
console.log(JSON.stringify({ result: 'PASS', scope: 'MATERIAL_PROTECTION_V48_WIP11_STATIC_CONTRACT', checks,
  samples: { upperMJ: upper.directResistanceMJ, bottomMJ: bottom.directResistanceMJ, flightMJ: flight.directResistanceMJ, magazineMJ: magazine.directResistanceMJ } }, null, 2));
