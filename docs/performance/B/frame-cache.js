// PERF_B: one immutable derived frame per owner; compare every physical input.
// Live survival/navigation reads remain in the callers, including actual releases.
const shipFrameCachePerfB=new WeakMap();
function shipFrameForInputsPerfB(owner,pose,origin,heading,cache=shipFrameCachePerfB){
  const heel=pose.heelRad??0,trim=pose.trimRad??0,draft=pose.draftM??0,
    x=origin.x??0,y=origin.y??0,z=origin.z??0,old=cache.get(owner);
  if(old&&Object.is(old.heading,heading)&&Object.is(old.heel,heel)&&Object.is(old.trim,trim)&&Object.is(old.draft,draft)
    &&Object.is(old.x,x)&&Object.is(old.y,y)&&Object.is(old.z,z))return old.frame;
  // Invalid inputs still throw in the canonical constructor, without replacing a valid entry.
  const frame=createShipBodyFrameV1(pose,origin,heading);
  cache.set(owner,{heading,heel,trim,draft,x,y,z,frame});return frame;
}
function performanceBSelfTest(){
  const checks={},cache=new WeakMap(),owner={},other={},pose={heelRad:.2,trimRad:-.03,draftM:1.5},origin={x:17,y:-24,z:3},heading=.8;
  const get=(o=owner,p=pose,q=origin,h=heading)=>shipFrameForInputsPerfB(o,p,q,h,cache),first=get();
  checks.sameInputsReuse=get()===first;checks.ownerSeparated=get(other)!==first;
  checks.frozenDerivedFrame=Object.isFrozen(first);
  const point={x:43,y:-7,z:19};
  checks.canonicalTransformExact=JSON.stringify(first.pointToWorld(point))===JSON.stringify(createShipBodyFrameV1(pose,origin,heading).pointToWorld(point));
  for(const field of ['heelRad','trimRad','draftM']){
    get();const changed={...pose,[field]:pose[field]+.01},next=get(owner,changed);
    checks['invalidate_'+field]=next!==first&&JSON.stringify(next.snapshot())===JSON.stringify(createShipBodyFrameV1(changed,origin,heading).snapshot());
  }
  for(const field of ['x','y','z']){
    get();const changed={...origin,[field]:origin[field]+.01},next=get(owner,pose,changed);
    checks['invalidate_'+field]=next!==first&&JSON.stringify(next.snapshot())===JSON.stringify(createShipBodyFrameV1(pose,changed,heading).snapshot());
  }
  const base=get(),turned=get(owner,pose,origin,heading+.01);
  checks.headingImmediate=turned!==base&&JSON.stringify(turned.snapshot())===JSON.stringify(createShipBodyFrameV1(pose,origin,heading+.01).snapshot());
  const valid=get();let thrown=false;try{get(owner,{...pose,heelRad:NaN});}catch(e){thrown=e instanceof TypeError;}
  checks.invalidStillThrows=thrown;checks.failedBuildPreservesValidEntry=get()===valid;
  const zeroPose={heelRad:0,trimRad:0,draftM:0},zero=get(owner,zeroPose,{x:0,y:0,z:0},0);
  checks.signedZeroNotConflated=get(owner,zeroPose,{x:0,y:0,z:0},-0)!==zero;
  return {schema:'AEGIS_PERFORMANCE_B_SELFTEST',checks,pass:Object.values(checks).every(Boolean)};
}
