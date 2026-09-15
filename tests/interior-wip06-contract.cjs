// Standalone contract/geometry test; does not claim a browser or WebGL render.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const file = process.argv[2] || path.join(__dirname, '../Aegis_SIM_v48_WIP08.html');
const html = fs.readFileSync(file, 'utf8');
let scripts = 0;
for (const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
  if (/\bsrc\s*=|application\/json/.test(m[1])) continue;
  new Function(m[2]); scripts++;
}
function section(a,b) {
  const i=html.indexOf(a), j=html.indexOf(b,i);
  assert(i>=0 && j>i, a); return html.slice(i,j);
}
const context = vm.createContext({
  getDamageFloodV1: () => ({cellAt: () => ({id:'fixture.cell'})}),
  SHIP_DECK_Z_M: 7,
});
vm.runInContext(section('const V48_WIP06_INTERIOR_MODEL=', '// FLOOD_HYDROSTATICS_V2.') +
  '\nglobalThis.model=createShipInteriorTopologyV48Wip06(getDamageFloodV1());globalThis.probe=runV48Wip06InteriorProbe();', context);
const model=context.model, state=model.snapshot();
assert(Object.values(context.probe.checks).every(Boolean), JSON.stringify(context.probe.checks));
assert.equal(state.summary.spaces,138);
assert.equal(state.audit.hangarClearance.clear,true);
assert.equal(state.audit.hangarClearance.bays,2);
assert.equal(state.audit.unreachable.length,0);
const bridge=state.spaces.filter(s=>s.id.includes('.bridge.') && s.kind!=='PASSAGE');
assert(new Set(bridge.map(s=>(s.x1-s.x0).toFixed(2))).size>=10);
assert(bridge.every(s=>s.z1-s.z0>=2.19), 'bridge headroom');
assert(state.spaces.some(s=>s.id==='s5.bridge.pilothouse' && s.y1-s.y0>9));
const before=model.performance().evaluations;
for(let i=0;i<20000;i++)assert.equal(model.snapshot(),state);
assert.equal(model.performance().evaluations,before);
model.step({spaceHazards:{[state.spaces.find(s=>s.routeable).id]:{fire01:.9,smoke01:.8}}});
model.reset();
assert.equal(JSON.stringify(model.snapshot()),JSON.stringify(state),'state recovery');
const badContext=vm.createContext({getDamageFloodV1:()=>({cellAt:()=>({id:'fixture.cell'})})});
const topologySource=section('const V48_WIP06_INTERIOR_MODEL=', '// FLOOD_HYDROSTATICS_V2.');
const injected=topologySource.replace('  const macroMembers=',
  "  room('fixture.obstruction','invalid deck','H0',-50,-40,2,6,'ROOM',null,8,9);\n  const macroMembers=");
assert.notEqual(injected,topologySource);
vm.runInContext(injected+'\nglobalThis.bad=createShipInteriorTopologyV48Wip06(getDamageFloodV1()).audit();',badContext);
assert.equal(badContext.bad.hangarClearance.clear,false,'obstructed hangar must fail');

// Minimal Three.js data sinks: execute the real renderer builder and inspect its output.
class Obj {
  constructor(){this.children=[];this.userData={};this.position={set:(...v)=>this.p=v};this.rotation={set:(...v)=>this.r=v};this.scale={set:(...v)=>this.s=v};}
  add(o){this.children.push(o);}
  updateMatrix(){this.matrix={position:this.p,scale:this.s,rotation:this.r};}
}
class Geometry {
  constructor(){this.attributes={};}
  setAttribute(k,v){this.attributes[k]=v;}
  setIndex(v){this.index=v;}
  computeVertexNormals(){}
}
class Mesh extends Obj {constructor(g,m){super();this.geometry=g;this.material=m;}}
class Instances extends Mesh {
  constructor(g,m,n){super(g,m);this.count=n;this.matrices=[];this.instanceMatrix={};}
  setMatrixAt(i,m){this.matrices[i]=m;}
}
class Color {constructor(){this.r=this.g=this.b=1;} multiplyScalar(){return this;} offsetHSL(){return this;}}
context.THREE={Group:Obj,Object3D:Obj,BufferGeometry:Geometry,Float32BufferAttribute:class {constructor(a,n){this.array=a;this.itemSize=n;}},Mesh,LineSegments:Mesh,InstancedMesh:Instances,BoxGeometry:Geometry,Color,MeshBasicMaterial:class {},LineBasicMaterial:class {},DoubleSide:2};
vm.runInContext(section('  const WIP165_SUPERSTRUCTURE_SCALE=', '  const WIP199_BRIDGE_GEOMETRY=')+
  section('  const WIP199_BRIDGE_GEOMETRY=', '  function wip199V3(')+
  section('  function wip199BridgeSectionAtY(', '  function wip199BridgeContainsPoint(')+
  '\nglobalThis.renderer={THREE,'+section('    upperStructureIntervalsV48Wip06(', '    interiorAuditV48Wip06(){')+'};', context);
const renderer=context.renderer, frozen=JSON.stringify(state), parent=new Obj();
const group=renderer.buildInteriorTopologyV48Wip06(parent,state);
assert.equal(JSON.stringify(state),frozen,'renderer must not mutate topology');
const missing=state.spaces.filter(s=>!group.userData.spaceIds.includes(s.id)).map(s=>s.id);
assert.equal(missing.length,0,JSON.stringify(missing));
assert.equal(group.userData.portalIds.length,state.portals.length);
assert.equal(group.userData.equipmentIds.length,state.equipmentNodes.length);
assert.equal(group.userData.renderStats.superstructureOutsideVertices,0);
assert(group.userData.renderStats.totalDrawables<=10);
const bay=state.spaces.find(s=>s.kind==='HANGAR_BAY');
const bayGroup=renderer.buildInteriorTopologyV48Wip06(new Obj(),{...state,spaces:[bay],portals:[],equipmentNodes:[]});
const geo=bayGroup.children.find(s=>s.name==='INTERIOR_SPACES_BATCH').geometry;
let horizontal=0;
for(let i=0;i<geo.index.length;i+=3){
  const z=geo.index.slice(i,i+3).map(k=>geo.attributes.position.array[k*3+1]);
  if(Math.max(...z)-Math.min(...z)<1e-7){horizontal++;assert(Math.abs(z[0]-bay.z0)<1e-7,'fake intermediate hangar floor');}
}
assert(horizontal>0);
const equipment=group.children.find(s=>s.name==='INTERIOR_EQUIPMENT_BATCH');
assert(new Set(equipment.matrices.map(m=>m.scale.join(','))).size>=4);
assert(state.equipmentNodes.every(e=>!state.spaces.find(s=>s.id===e.spaceId).kind.match(/HANGAR_BAY|PASSAGE|CATWALK/)));
console.log(JSON.stringify({result:'PASS',scope:'NODE_CONTRACT_AND_RENDER_GEOMETRY_SINK_NOT_WEBGL',scripts,probeChecks:context.probe.checks,summary:state.summary,audit:state.audit,render:group.userData.renderStats,hangarHorizontalTriangles:horizontal},null,2));
