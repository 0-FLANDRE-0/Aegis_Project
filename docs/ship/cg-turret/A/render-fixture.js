// DIAGNOSTIC ONLY: inspect original mesh vertices and call native projectile spawn.
window.__CG_AUDIT__={
 specs:()=>gunB1OwnGuns().map(([id,g])=>({id,spec:g.spec})),
 scan(){return gunB1OwnGuns().map(([id,g])=>({id,rows:Array.from({length:17},(_,e)=>-15+e*5).flatMap(el=>Array.from({length:72},(_,a)=>{const az=a*5,r=wip13b1GunClearance(g.spec,deg(az),deg(el));return{az,el,ok:r.ok,reason:r.reason,obstruction:r.obstruction??null,distanceM:r.distanceM??null};}))}));},
 poses(){const view=WIP148_EXTERNAL_3D,T=view.THREE,asset=view._bunkerAsset,rows=[];__GB_TEST__.reset();
  for(const[id,g]of gunB1OwnGuns()){const reg=BUNKER_REGISTRATION.guns[g.installation.hardpointId],pitch=asset.parts.get(reg.pitchNode),mesh=pitch.children.find(o=>o.isMesh),p=mesh.geometry.attributes.position;
   const sign=Math.cos(reg.neutralAzRad),d=new T.Vector3(sign*Math.cos(reg.restElevationRad),Math.sin(reg.restElevationRad),0),points=[];let max=-Infinity;
   for(let i=0;i<p.count;i++){const v=new T.Vector3().fromBufferAttribute(p,i);max=Math.max(max,v.dot(d));points.push(v);}
   const tip=points.filter(v=>max-v.dot(d)<.002),unique=[...new Map(tip.map(v=>[v.toArray().join(','),v])).values()],center=unique.reduce((v,p)=>v.add(p),new T.Vector3()).multiplyScalar(1/unique.length);
   for(const el of[0,30,60])for(const relAz of[-90,0,90]){const az=reg.neutralAzRad+deg(relAz),st=get3DRenderState();st.mountInventory.guns=st.mountInventory.guns.map(q=>q.hardpointId===g.installation.hardpointId?{...q,bodyAzRad:az,elevationRad:deg(el)}:q);view.syncShipFittings(st);view.shipRoot.updateWorldMatrix(true,true);const point=view.shipRoot.worldToLocal(mesh.localToWorld(center.clone())),bodyMesh={x:point.x,y:point.z,z:point.y};
    const projectile=spawnMainGunProjectileWip13B3({module:g.spec,ammo:g.spec.ammunition.HE_127_SIM,ammoId:'HE_127_SIM',trackId:-1,bodyAzRad:az,elevationRad:deg(el),hardpoint:ACTIVE_SHIP_PROFILE.geometry.hardpoints[g.installation.hardpointId],solution:{timeOfFlightS:1,computedStep:simStepCounter}}),bodyLaunch=shipGameFrameV1().pointToBody(projectile.positionM);projectile.alive=false;
    rows.push({id,relativeAzDeg:relAz,elevationDeg:el,meshTipBodyM:bodyMesh,launchBodyM:bodyLaunch,errorM:Math.hypot(point.x-bodyLaunch.x,point.z-bodyLaunch.y,point.y-bodyLaunch.z),tipVertices:unique.length});
   }
  }resetMainGunProjectilesWip13B3();return{rows,maxErrorM:Math.max(...rows.map(x=>x.errorM)),renderAudit:view.contractAudit()};
 },
 camera(key){const v=WIP148_EXTERNAL_3D,T=v.THREE,h=ACTIVE_SHIP_PROFILE.geometry.hardpoints[key],at=new T.Vector3(h.x,h.z+2,h.y);v.syncCamera=function(){this.shipRoot.updateWorldMatrix(true,true);const target=this.shipRoot.localToWorld(at.clone()),offset=new T.Vector3(key==='mk45Aft'?-11:11,8,15).applyQuaternion(this.shipRoot.getWorldQuaternion(new T.Quaternion()));this.camera.position.copy(target).add(offset);this.camera.lookAt(target);};v.render(performance.now());return{profile:ACTIVE_SHIP_PROFILE.id,key};},
 signature(){const v=WIP148_EXTERNAL_3D,out=[];const root=v._bunkerAsset?.parts.get('mk45f_yaw')??v.mk45TraverseGroup;root.traverse(o=>{if(o.isMesh)out.push({name:o.name,position:Array.from(o.geometry.attributes.position.array),index:o.geometry.index?Array.from(o.geometry.index.array):null,visible:o.visible});});return out;}
};
