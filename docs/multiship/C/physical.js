// PHYSICAL ONLY: runtime identities and geometry stop at anonymous echo extraction.
function navalReflectorsC(){
  return physicalShipsB().filter(r=>!r.survival.snapshot().lost).map(r=>{
    const p=resolveShipProfile(r.profileId),n=r.navigation,id='NAVAL:'+r.entityId,beam=Math.max(...p.geometry.hullStations.map(q=>Math.abs(q[1])))*2;
    return {rfId:id,x:n.positionWorld.x,y:n.positionWorld.y,z:Math.max(.8,12-r.survival.snapshot().draftM),vx:n.vx,vy:n.vy,vz:0,
      physicalLengthM:p.geometry.lengthM,physicalBeamM:beam,headingRad:n.heading,extentRangeM:p.geometry.lengthM*.3,extentCrossM:beam*.45,extentVerticalM:12,dopplerSpreadMps:.8,
      _sourceSeed:rfSeedWip13A2(id),_truthObject:r,_physicsKind:'NAVAL_SHIP'};
  });
}
function navalRcsC(ref,band,x,y,z){
  // Geometry/aspect based SIM-TUNE; no real radar cross-section assertion.
  const r=ref._truthObject,p=resolveShipProfile(r.profileId),n=r.navigation,a=angNorm(Math.atan2(y-n.positionWorld.y,x-n.positionWorld.x)-n.heading),beam=ref.physicalBeamM;
  return Math.max(1,p.geometry.lengthM*beam*(.10+.36*Math.abs(Math.sin(a)))*({S:1,X:.82,IJ:.68}[rfBandKeyWip13A2(band)]??1));
}
function observerMountC(r,center){
  const p=shipBodyFrameB(r).pointToWorld(center),n=r.navigation;
  return {x:metersToWorld(p.x),y:metersToWorld(p.y),z:p.z,vxMps:worldSpeedToMps(n.vx??0),vyMps:worldSpeedToMps(n.vy??0),vzMps:0};
}
function observerMaskC(r,center,az,el,exclude){
  if(r.profileId!=='CG_52_LATE_TICONDEROGA')return null;
  const d=shipBodyFrameB(r).vectorToBody({x:Math.cos(el)*Math.cos(az),y:Math.cos(el)*Math.sin(az),z:Math.sin(el)});
  return bunkerRaySource(center,d,300,exclude);
}
function observerHealthC(r,name){
  if(shipEquipmentOfflineV1(r))return 0;
  const g=id=>clamp(1-shipSystemDamageB(r,id)/100,0,1),power=clamp((g('GEN_1')+g('GEN_2'))*.5+g('GEN_3')*.3,0,1);
  return clamp((1-r.flooding.readDamage(name)/100)*power*(1-shipSystemDamageB(r,'CDC')/100),0,1);
}
function observerPhysicalAuditC(options={}){
  const r=ACTIVE_SHIP_RUNTIME,o=observerC(r),receiver=observerMountC(r,o.profile.geometry.hardpoints.bridgeMasterE),rng={state:1831565813,spare:null};
  if(Number.isFinite(options.receiverHeightM)&&options.receiverHeightM>=.2&&options.receiverHeightM<=10000)receiver.z=options.receiverHeightM;
  const dwell=shipboardRadarEchoFieldWip13B13({radarId:'BRIDGEMASTER_E',band:'S',receiver,beamAz:0,beamEl:0,beamHalfAzRad:Math.PI,beamHalfElRad:Math.PI/2,maxRangeKm:80,minRangeM:120,maxDistributedEchoes:0,health:1,rngState:rng});
  return {naval:navalReflectorsC().map(q=>({x:q.x,y:q.y,z:q.z,owner:q._truthObject.entityId})),dwell,echoEvidence:dwell.echoes.map(q=>shipboardRadarDomainEvidenceWip13B13(q,{elevationObservable:false,surfaceBiased:true})),spy:spySchedulerSnapshot(),aux:spq9bHealth01(),nav:bridgeMasterEHealth01(),emcon:emconActive};
}
