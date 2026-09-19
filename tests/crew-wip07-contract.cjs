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
  const i = html.indexOf(a);
  const j = html.indexOf(b, i);
  assert(i >= 0 && j > i, a);
  return html.slice(i, j);
}

const flood = {
  cellAt(point) {
    const section = Math.max(0, Math.min(7, Math.floor((76 - Number(point?.x || 0)) / 19)));
    const lane = Number(point?.y || 0) < -1 ? 'port' : Number(point?.y || 0) > 1 ? 'starboard' : 'center';
    return { id: `flood.s${String(section + 1).padStart(2, '0')}.${lane}` };
  },
};
const context = vm.createContext({
  getDamageFloodV1: () => flood,
  SHIP_DECK_Z_M: 7,
  clamp: (value, lo, hi) => Math.max(lo, Math.min(hi, value)),
  performance,
});
vm.runInContext(
  section('function deepFreezeShipProfileV48Wip09(', 'function shipHdgDeg()') +
  section('// V48 WIP11 material contract.', 'function updateShipMovement(dt)') +
  section('const V48_WIP06_INTERIOR_MODEL=', '// FLOOD_HYDROSTATICS_V2.') +
  section('// V48 WIP07: the WIP06 room/portal graph', 'let shipCrewV21=null;') +
  '\nglobalThis.topology=createShipInteriorTopologyV48Wip06(getDamageFloodV1());globalThis.topology.step({});globalThis.crew=createShipCrewV48Wip07(globalThis.topology,crewDutyPostsV48Wip07());globalThis.crew.syncTeams([{id:1,task:"FIRE",cellId:"flood.s01.center"}]);globalThis.crewState=globalThis.crew.snapshot();globalThis.probe=runV48Wip07CrewDamageProbe({readCount:20000});',
  context,
);

const probe = context.probe;
assert(Object.values(probe.checks).every(Boolean), JSON.stringify(probe.checks));
assert.equal(probe.base.total, 310);
assert.equal(probe.readPerformance.snapshotRebuilds, 0);
assert.equal(probe.readPerformance.routeEvaluations, 0);
assert.equal(probe.readPerformance.damageEvaluations, 0);
assert.equal(probe.performance.damageEvaluations, 1);
assert(probe.damage.affectedSpaces.length > 1);
assert(probe.damage.penetratedSpaceIds.length >= 1);
assert(probe.totals.dead + probe.totals.injured > 0);
assert(probe.totals.dead > 0 && probe.totals.injured > 0);
assert(probe.medical.routes > 0 && probe.medical.routes <= 4);
assert.deepEqual(Array.from(probe.medical.destinations), ['main.infirmary']);

class Obj {
  constructor() {
    this.children = [];
    this.userData = {};
    this.position = { set: (...v) => { this.p = v; } };
    this.rotation = { set: (...v) => { this.r = v; } };
    this.scale = { set: (...v) => { this.s = v; } };
  }
  add(o) { this.children.push(o); o.parent = this; }
  updateMatrix() { this.matrix = { position: this.p, rotation: this.r, scale: this.s }; }
}
class Geometry {
  constructor() { this.attributes = {}; this.drawRange = { start: 0, count: 0 }; }
  setAttribute(k, v) { this.attributes[k] = v; }
  setDrawRange(start, count) { this.drawRange = { start, count }; }
}
class Mesh extends Obj { constructor(g, m) { super(); this.geometry = g; this.material = m; } }
class Instances extends Mesh {
  constructor(g, m, n) { super(g, m); this.capacity = n; this.count = n; this.matrices = []; this.colors = []; this.instanceMatrix = { setUsage() {} }; }
  setMatrixAt(i, m) { this.matrices[i] = m; }
  setColorAt(i, c) { this.colors[i] = c; this.instanceColor = this.instanceColor || {}; }
}
class Attribute { constructor(array, size) { this.array = array; this.itemSize = size; } }
class Color { constructor(value) { this.value = value; } }
context.THREE = {
  Group: Obj,
  Object3D: Obj,
  CylinderGeometry: Geometry,
  BufferGeometry: Geometry,
  BufferAttribute: Attribute,
  MeshBasicMaterial: class {},
  LineBasicMaterial: class {},
  InstancedMesh: Instances,
  LineSegments: Mesh,
  Color,
  DynamicDrawUsage: 35048,
};
context.shipRoot = new Obj();
context.get3DRenderState = () => ({ shipCrewSpatial: context.crewState });
vm.runInContext(
  'globalThis.renderer={THREE,shipRoot,interiorTopologyVisible:true,' +
  section('    buildCrewInteriorV48Wip07(', '    interiorAuditV48Wip06(){') +
  '};globalThis.layer=globalThis.renderer.buildCrewInteriorV48Wip07(shipRoot,globalThis.crewState);globalThis.renderAudit=globalThis.renderer.crewAuditV48Wip07();',
  context,
);
assert.equal(context.renderAudit.instanceBatches, 1);
assert.equal(context.renderAudit.renderedPersonnel, 310);
assert.equal(context.renderAudit.allPersonnelRepresented, true);
assert(context.renderAudit.routeSegments > 0);

console.log(JSON.stringify({
  result: 'PASS',
  scope: 'NODE_CREW_ROUTE_BLAST_FRAGMENT_PENETRATOR_CONTRACT',
  scripts,
  checks: probe.checks,
  base: probe.base,
  route: {
    spaces: probe.route.spaces.length,
    distanceM: probe.route.distanceM,
    etaS: probe.route.etaS,
  },
  stretcherRoute: {
    spaces: probe.stretcherRoute.spaces.length,
    distanceM: probe.stretcherRoute.distanceM,
    etaS: probe.stretcherRoute.etaS,
  },
  damage: probe.damage,
  totals: probe.totals,
  medical: probe.medical,
  readPerformance: probe.readPerformance,
  performance: probe.performance,
  render: context.renderAudit,
}, null, 2));
