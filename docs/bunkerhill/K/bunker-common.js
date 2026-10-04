// Immutable source geometry is used for masks in the simulation. Rendering can
// be disabled or moved without changing a firing/illumination decision.
const BUNKER_BVH=new Map();
function bunkerBuildBvh(row){
  const t=row.triangles;
  function build(ids){
    const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
    for(const i of ids)for(let j=0;j<9;j++){const k=j%3;min[k]=Math.min(min[k],t[i+j]);max[k]=Math.max(max[k],t[i+j]);}
    if(ids.length<=24)return {min,max,ids};
    const size=max.map((v,k)=>v-min[k]),axis=size.indexOf(Math.max(...size));
    ids.sort((a,b)=>(t[a+axis]+t[a+3+axis]+t[a+6+axis])-(t[b+axis]+t[b+3+axis]+t[b+6+axis]));
    const mid=ids.length>>1;return {min,max,left:build(ids.slice(0,mid)),right:build(ids.slice(mid))};
  }
  return build(Array.from({length:t.length/9},(_,i)=>i*9));
}
function bunkerRaySource(origin,direction,maxDistance=300,exclude=null,minDistance=.035){
  let best=maxDistance,result=null;
  const O=[origin.x,origin.y,origin.z],D=[direction.x,direction.y,direction.z];
  function box(min,max){let lo=minDistance,hi=best;
    for(let k=0;k<3;k++){if(Math.abs(D[k])<1e-12){if(O[k]<min[k]||O[k]>max[k])return false;}else{
      let a=(min[k]-O[k])/D[k],b=(max[k]-O[k])/D[k];if(a>b)[a,b]=[b,a];lo=Math.max(lo,a);hi=Math.min(hi,b);if(hi<lo)return false;}}
    return true;
  }
  for(const row of BUNKER_REGISTRATION.occluders){
    if(row.name===exclude)continue;
    if(!box([row.min.x,row.min.y,row.min.z],[row.max.x,row.max.y,row.max.z]))continue;
    let root=BUNKER_BVH.get(row.name);if(!root){root=bunkerBuildBvh(row);BUNKER_BVH.set(row.name,root);}
    const t=row.triangles;
    function visit(node){if(!box(node.min,node.max))return;if(node.left){visit(node.left);visit(node.right);return;}
      for(const i of node.ids){
        const ax=t[i],ay=t[i+1],az=t[i+2],ex=t[i+3]-ax,ey=t[i+4]-ay,ez=t[i+5]-az,
          fx=t[i+6]-ax,fy=t[i+7]-ay,fz=t[i+8]-az;
        const px=D[1]*fz-D[2]*fy,py=D[2]*fx-D[0]*fz,pz=D[0]*fy-D[1]*fx,det=ex*px+ey*py+ez*pz;
        if(Math.abs(det)<1e-10)continue;
        const inv=1/det,tx=O[0]-ax,ty=O[1]-ay,tz=O[2]-az,u=(tx*px+ty*py+tz*pz)*inv;if(u<0||u>1)continue;
        const qx=ty*ez-tz*ey,qy=tz*ex-tx*ez,qz=tx*ey-ty*ex,v=(D[0]*qx+D[1]*qy+D[2]*qz)*inv;if(v<0||u+v>1)continue;
        const distance=(fx*qx+fy*qy+fz*qz)*inv;if(distance>=minDistance&&distance<best){best=distance;result={name:row.name,distanceM:distance};}
      }
    }
    visit(root);
  }
  return result;
}
function bunkerRayAngles(origin,az,el,rangeM=300,exclude=null){
  return bunkerRaySource(origin,{x:Math.cos(el)*Math.cos(az),y:Math.cos(el)*Math.sin(az),z:Math.sin(el)},rangeM,exclude);
}
function bunkerGunAzimuth(spec,az){return (spec.mount.stowBodyAzRad??0)+angNorm(az-(spec.mount.stowBodyAzRad??0));}
function bunkerGunClearance(spec,bodyAz,bodyEl,maxDistanceM=300){
  const inst=spec.installation,hp=ACTIVE_SHIP_PROFILE.geometry.hardpoints[inst.hardpointId],off=spec.mount.trunnionOffsetM,
    az=bunkerGunAzimuth(spec,bodyAz),origin={x:hp.x+off.x*Math.cos(az)-off.y*Math.sin(az),y:hp.y+off.x*Math.sin(az)+off.y*Math.cos(az),z:hp.z+off.z};
  if(az<spec.mount.trainMinRad||az>spec.mount.trainMaxRad||bodyEl<spec.mount.elevationMinRad||bodyEl>spec.mount.elevationMaxRad)
    return {ok:false,reason:'MOUNT_ENVELOPE',mountId:inst.id};
  const hit=bunkerRayAngles(origin,bodyAz,bodyEl,maxDistanceM);
  return {ok:!hit,reason:hit?'MOUNT_OCCLUDED':null,obstruction:hit?.name??null,distanceM:hit?.distanceM??null,mountId:inst.id,originM:origin};
}
function createBunkerCiwsRuntime(template){
  return Object.values(ACTIVE_SHIP_PROFILE.weapons.closeIn.mounts).map((inst,i)=>{
    const E=SHIP_EQUIPMENT_PROFILE_REGISTRY[inst.moduleId],hp=ACTIVE_SHIP_PROFILE.geometry.hardpoints[inst.hardpointId];
    return {...template,id:i+1,installationId:inst.id,installation:inst,profileId:inst.moduleId,type:'GUN',
      label:inst.moduleName,moduleName:inst.moduleName,posOffsetM:hp.x,posOffsetYM:hp.y,heightM:hp.z,
      angleOffset:inst.neutralAzRad,arcCenter:inst.neutralAzRad,arcHalf:E.trainHalfRad,blindSectors:[],
      ammo:E.ammo,maxAmmo:E.ammo,fireRate:E.fireRateRps,searchRangeKm:E.searchRangeKm,trackRangeKm:E.trackRangeKm,
      cueTrackRangeKm:E.cueTrackRangeKm,engageRangeKm:E.engageRangeKm,maxTurretRate:E.trainRateRadS,turretAccel:E.trainAccelRadS2,
      turretAng:shipNav.heading+inst.neutralAzRad,_bodyYawV1:inst.neutralAzRad,turretEl:0,turretElRate:0,maxElevationRate:E.elevationRateRadS,elevationAccel:E.elevationAccelRadS2,
      _localTrack:null,trackingTarget:null,cuedTarget:null,geometryMask:true};
  });
}
function bunkerCiwsMuzzleOffset(registration,az,el){
  const q=registration.muzzleOffsetLocalM,ce=Math.cos(el),se=Math.sin(el),ca=Math.cos(az),sa=Math.sin(az),
    forward=ce*q.x-se*q.z;
  return {x:ca*forward-sa*q.y,y:sa*forward+ca*q.y,z:se*q.x+ce*q.z};
}
function bunkerCiwsMuzzleLocal(hardpointId,az,el){
  const r=BUNKER_REGISTRATION.ciws[hardpointId],d=bunkerCiwsMuzzleOffset(r,az,el);
  return {x:r.x+d.x,y:r.y+d.y,z:r.z+d.z};
}
function bunkerCiwsConstraints(mount){
  const E=SHIP_EQUIPMENT_PROFILE_REGISTRY[mount.profileId],R=BUNKER_REGISTRATION.ciws[mount.installation.hardpointId],
    origin={x:R.x,y:R.y,z:R.z},blind=[];
  // Near barrel sweep: actual structural triangles, independent of far beam masks.
  const step=Math.PI/180;let start=null;
  for(let a=-E.trainHalfRad;a<=E.trainHalfRad+step*.5;a+=step){
    const blocked=!!bunkerRayAngles(origin,mount.arcCenter+a,0,2.0);
    if(blocked&&start===null)start=a;
    if(!blocked&&start!==null){blind.push({center:mount.arcCenter+(start+a)/2,half:(a-start)/2});start=null;}
  }
  if(start!==null)blind.push({center:mount.arcCenter+(start+E.trainHalfRad)/2,half:(E.trainHalfRad-start)/2});
  const base=createGameMountConstraintsV1({name:mount.moduleName,center:mount.arcCenter,half:E.trainHalfRad,blind,origin,boxes:[]});
  const rayHit=(az,el,max=300)=>bunkerRayAngles(origin,az,el,max)?.name??null;
  return Object.freeze({...base,rayHit,direction:(az,el=0,max=300)=>{
    const r=base.direction(az,el,max),hit=rayHit(az,el,max),inElevation=el>=E.elevationMinRad&&el<=E.elevationMaxRad;
    return {...r,ok:r.ok&&!hit&&inElevation,inBlind:r.inBlind||!!hit||!inElevation,
      reason:hit?'구조물: '+hit:!inElevation?'고각 범위 밖':r.reason};
  }});
}
function bunkerSpgMask(ill,az,altM=ill.height,rangeKm=100){
  const E=SHIP_EQUIPMENT_PROFILE_REGISTRY.SPG62_V1,el=Math.atan2(altM-ill.height,Math.max(1,rangeKm*1000));
  if(el<E.elevationMinRad||el>E.elevationMaxRad)return {ok:false,reason:'MOUNT_ELEVATION'};
  const hit=bunkerRayAngles({x:ill.oX,y:ill.oY,z:ill.height},az,el,Math.min(300,rangeKm*1000));
  return {ok:!hit,reason:hit?'STRUCTURE_MASK':null,obstruction:hit?.name??null,elevationRad:el};
}
function bunkerSpgWorldMask(ill,x,y,z){
  const frame=shipGameFrameV1(),p=frame.pointToLocal({x:worldToMeters(x),y:worldToMeters(y),z:z??0}),
    dx=p.x-ill.oX,dy=p.y-ill.oY,dz=p.z-ill.height;
  const el=Math.atan2(dz,Math.hypot(dx,dy)),E=SHIP_EQUIPMENT_PROFILE_REGISTRY.SPG62_V1;
  if(el<E.elevationMinRad||el>E.elevationMaxRad)return false;
  return !bunkerRayAngles({x:ill.oX,y:ill.oY,z:ill.height},Math.atan2(dy,dx),el,Math.min(300,Math.hypot(dx,dy,dz)));
}
function bunkerEwEmitter(x,y,z=0){
  const f=shipGameFrameV1(),target=f.pointToLocal({x:worldToMeters(x),y:worldToMeters(y),z}),candidates=[];
  for(const pod of ACTIVE_SHIP_PROFILE.equipment.ew.pods){
    const d={x:target.x-pod.center.x,y:target.y-pod.center.y,z:target.z-pod.center.z},r=Math.hypot(d.x,d.y,d.z),
      az=Math.atan2(d.y,d.x),el=Math.atan2(d.z,Math.hypot(d.x,d.y)),h=clamp(1-getModuleDmg(pod.name)/85,0,1);
    if(h<=0||Math.abs(angNorm(az-pod.beamCenterRad))>pod.beamHalfRad||bunkerRayAngles(pod.center,az,el,Math.min(300,r)))continue;
    candidates.push({podId:pod.id,health01:h,point:shipGamePointStateV1(pod.center),rangeM:r});
  }
  candidates.sort((a,b)=>b.health01-a.health01||a.rangeM-b.rangeM);return candidates[0]??null;
}
function bunkerResetGunMounts(){for(const gun of ACTIVE_SHIP_RUNTIME.weapons.gunMounts?.values()??[])gun.reset();}
function bunkerMountInventorySnapshot(){return {
  guns:[...ACTIVE_SHIP_RUNTIME.weapons.gunMounts.values()].map(g=>g.snapshot()),
  closeIn:ciws.map(m=>({id:m.installationId,moduleId:m.profileId,hardpointId:m.installation.hardpointId,
    type:m.type,ammo:m.ammo,azRelRad:ciwsBodyYawV1(m),elRad:m.turretEl??0,firing:!!m.firing,tracking:!!m.tracking,state:m.state})),
  illuminators:SPG62_ILLUMINATORS.map(m=>({id:m.id,moduleName:m.moduleName,origin:{x:m.oX,y:m.oY,z:m.height}}))};}

function bunkerInitAuxNav(){
  if(!IS_BUNKER)return;
  ACTIVE_SHIP_RUNTIME.combatSystem.sensors.auxNav=[];
}
function bunkerAuxNavSnapshot(){
  return ACTIVE_SHIP_PROFILE.equipment.secondaryRadars.map(r=>({id:r.id,origin:r.center,rotorPivot:r.rotorPivot,
    angleRad:r.id==='SPQ9'?spq9bRotorAngle:bridgeMasterERotorAngle,
    health01:r.id==='SPQ9'?spq9bHealth01():bridgeMasterEHealth01(),
    provenance:SHIP_EQUIPMENT_PROFILE_REGISTRY[r.moduleId].provenance}));
}
function bunkerUpdateAuxNav(){} // compatibility hook; the two primary runtime scanners own the phases.
