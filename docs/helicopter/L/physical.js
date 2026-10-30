// RF_FRONTEND_ONLY. The sole ISAR reader of physical shape and target motion.
// Geometry caches are immutable derived data, not combat state or classification.
const ISAR_GEOMETRY_CACHE_F2=new WeakMap();
function isarPhysicalSourceF2(ref){
 const t=ref._truthObject;let g,boxes,pose={},heading=ref.headingRad??0;
 if(ref._physicsKind==='SHIP'||ref._physicsKind==='NAVAL_SHIP'){
  const r=ref._physicsKind==='SHIP'?ACTIVE_SHIP_RUNTIME:t,p=resolveShipProfile(r.profileId);g=p.geometry;boxes=geometryForShipProfileA(p).boxes;heading=r.navigation.heading;
  pose=r===ACTIVE_SHIP_RUNTIME?floodAttitudePreviewV1.snapshot():r.survival.snapshot();
 }else if(ref._physicsKind==='SURFACE_TARGET'){const p=surfaceTargetProfileWip13A(t.profileId);g=p?.geometry;boxes=g?.hitVolumes;pose=t.targetRuntime?.attitude??{};heading=t.heading??heading;}
 else if(ref._physicsKind==='ISAR_DIAGNOSTIC_GEOMETRY'){g=t.geometry;boxes=t.boxes;pose=t.pose??{};heading=t.heading??heading;}
 if(!g)return null;let shape=ISAR_GEOMETRY_CACHE_F2.get(g);if(!shape){shape=isarShapeFromGeometryF2(g,boxes);if(shape)ISAR_GEOMETRY_CACHE_F2.set(g,Object.freeze(shape));}
 return shape?{shape,pose,heading}:null;
}
function isarPhysicalSampleF2(ref,geometry,cfg,normal,snr){
 const src=isarPhysicalSourceF2(ref);if(!src)return null;const C=ISAR_F2,{shape,pose,heading}=src,t=cfg.atS,aspect=apsAngleF(geometry.azRad-heading),hs=cfg.hsM;
 // Existing survival pose supplies actual list/trim. It has no sea-frequency
 // rigid-body angular motion; estimate only that missing component. If a future
 // physical model supplies waveRoll/Pitch/YawRad, those replace the estimates.
 const phase=worldToMeters(ref.x)/Math.max(1,shape.lengthM)+worldToMeters(ref.y)/Math.max(1,shape.lengthM),wave=(key,amp,period,offset)=>Number.isFinite(pose[key])?pose[key]:apsRadF(amp)*hs*Math.sin(t*2*Math.PI/period+phase+offset),roll=(pose.heelRad??0)+wave('waveRollRad',C.seaRollDegPerM,C.seaRollPeriodS,0),pitch=(pose.trimRad??0)+wave('wavePitchRad',C.seaPitchDegPerM,C.seaPitchPeriodS,1),yaw=apsAngleF(heading-geometry.azRad)+wave('waveYawRad',C.seaYawDegPerM,C.seaYawPeriodS,2),scale=1/Math.sqrt(Math.max(1,snr));
 // Only receiver observables leave synthesis. Phase-derived angular signatures
 // use a geometric basis; class/profile/entity identity is never copied.
 return {lengthM:Math.max(1,shape.lengthM+normal()*C.rfLengthSigmaM*scale),heightsM:shape.heightsM.map(z=>Math.max(0,z+normal()*C.rfHeightSigmaM*scale)),mastPosition01:apsClampF(shape.mastPosition01+normal()*C.rfMastSigma01*scale,0,1),aspectUncertainty01:Math.abs(Math.sin(aspect)),angularSignatureRad:[roll*Math.sin(aspect),pitch*Math.cos(aspect),yaw]};
}
function isarReceiverF2(args){
 const {opts,signal,horizontalRangeM:r,rangeM,beamGain,weatherQ,localClutter,distributed}=args,cfg=opts.isarF,C=ISAR_F2,gain=APS_CALIBRATION_F.K*beamGain*weatherQ/Math.max(1,rangeM)**4,clutter=apsClutterRcsF('PERI',cfg.altitudeM,r,cfg.hsM)*C.rangeResolutionM/APS_MODES_F.PERI.resolutionM,background=1+gain*clutter*C.clutterScale+APS_F.sampledClutterFraction*localClutter,snr=distributed?0:signal/background,pd=distributed?0:1-Math.exp(-snr/C.pdSnrScale),scale=1/Math.sqrt(Math.max(1,snr));
 return {snr,pd,rangeSigmaM:Math.max(APS_F.rangeSigmaFloorM,C.rangeResolutionM/3*scale),azSigmaDeg:Math.max(APS_F.azimuthSigmaFloorDeg,APS_F.azimuthSigmaDeg*scale)};
}
