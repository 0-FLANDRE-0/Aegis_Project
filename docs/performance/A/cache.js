// LIVE_CANONICAL, transient derived data only. Damage values remain owner-local reads.
// Registered boxes and their entries are deep-frozen. Unregistered mutable geometry
// retains the original scan, including strict system equality and Set name order.
const systemModuleIndexPerfA=new WeakMap();
function systemModuleNamesPerfA(boxes,system){
  let index=systemModuleIndexPerfA.get(boxes);
  if(!index){
    if(!Object.isFrozen(boxes)||!boxes.every(Object.isFrozen))return [...new Set(boxes.filter(b=>b.system===system).map(b=>b.name))];
    index=new Map();
    for(const box of boxes){let names=index.get(box.system);if(!names)index.set(box.system,names=new Set());names.add(box.name);}
    for(const [id,names]of index)index.set(id,Object.freeze([...names]));
    systemModuleIndexPerfA.set(boxes,index);
  }
  // Map uses SameValueZero; the existing scan uses === and never matches NaN.
  return system===system?(index.get(system)??[]):[];
}

// LIVE_CANONICAL presentation cache, separated by view/THREE context and paint input.
// Each geometry owns one idempotent lease; no geometry/material/plume is shared.
const kh32PaintViewsPerfA=new WeakMap();
function acquireKh32PaintPerfA(view,L,p,create){
  let cache=kh32PaintViewsPerfA.get(view);
  if(!cache||cache.three!==view.THREE){cache={three:view.THREE,entries:new Map()};kh32PaintViewsPerfA.set(view,cache);}
  const key=JSON.stringify(['KH32_PAINT_2048_V1',L,p.noseFrac,p.tailContour.at(-1)[0],p.bodyColor,p.panelStations,p.hatchStations]);
  let entry=cache.entries.get(key);
  if(!entry){entry={texture:create(),references:0};cache.entries.set(key,entry);}
  entry.references++;let released=false;
  return {texture:entry.texture,release(){
    if(released)return;released=true;
    if(--entry.references===0){if(cache.entries.get(key)===entry)cache.entries.delete(key);entry.texture.dispose();}
  }};
}

// DIAGNOSTIC_ONLY: isolated data and fake textures; no live owner writes or RNG.
function performanceASelfTest(){
  const checks={},boxes=Object.freeze([
    Object.freeze({system:'POWER',name:'A'}),Object.freeze({system:'POWER',name:'A'}),
    Object.freeze({system:'POWER',name:'B'}),Object.freeze({system:NaN,name:'N'})]);
  const values={A:10,B:40},r={geometry:{boxes},flooding:{readDamage:n=>values[n]??0}};
  checks.uniqueModules=JSON.stringify(systemModuleNamesPerfA(boxes,'POWER'))==='["A","B"]';
  checks.aggregates=shipSystemDamageB(r,'POWER')===40&&shipSystemDamageB(r,'POWER','AVG')===25&&shipSystemDamageB(r,'POWER','SUM')===50;
  values.A=80;checks.liveDamage=shipSystemDamageB(r,'POWER')===80&&shipSystemDamageB(r,'POWER','SUM')===120;
  const peer={geometry:{boxes},flooding:{readDamage:()=>7}};
  checks.ownerIsolation=shipSystemDamageB(peer,'POWER','SUM')===14&&shipSystemDamageB(r,'POWER','SUM')===120;
  checks.missingAndStrictEquality=shipSystemDamageB(r,'UNKNOWN')===0&&shipSystemDamageB(r,NaN)===0;
  r.geometry={boxes:Object.freeze([Object.freeze({system:'POWER',name:'B'})])};
  checks.replacement=shipSystemDamageB(r,'POWER','SUM')===40;
  const mutable=[{system:'POWER',name:'A'}];r.geometry={boxes:mutable};shipSystemDamageB(r,'POWER');mutable[0].name='B';mutable.push({system:'POWER',name:'A'});
  checks.mutableFallback=shipSystemDamageB(r,'POWER','SUM')===120;
  checks.activeDelegate=shipSystemDamageB(ACTIVE_SHIP_RUNTIME,'MAST','AVG')===getShipSystemDamage('MAST','AVG');
  let creates=0,disposes=0;const view={THREE:{}},p={noseFrac:.2,tailContour:[[-.4,1]],bodyColor:1,panelStations:[.1],hatchStations:[.2]},create=()=>({id:++creates,dispose(){disposes++;}});
  const a=acquireKh32PaintPerfA(view,10,p,create),b=acquireKh32PaintPerfA(view,10,p,create);
  checks.sharedPaint=a.texture===b.texture&&creates===1;a.release();a.release();
  checks.partialRelease=disposes===0;b.release();checks.finalRelease=disposes===1;
  const c=acquireKh32PaintPerfA(view,10,p,create),d=acquireKh32PaintPerfA(view,10,{...p,bodyColor:2},create);
  checks.recreateAndDistinctPaint=c.texture!==a.texture&&d.texture!==c.texture;
  view.THREE={};const e=acquireKh32PaintPerfA(view,10,p,create);checks.contextIsolation=e.texture!==c.texture;
  c.release();d.release();e.release();checks.allReleased=creates===4&&disposes===4;
  return {schema:'AEGIS_PERFORMANCE_A_SELFTEST',checks,pass:Object.values(checks).every(Boolean)};
}
