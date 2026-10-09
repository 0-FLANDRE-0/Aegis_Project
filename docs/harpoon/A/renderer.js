// Shared immutable geometry, private instances. All trajectories/staging read fixed-tick outputs.
function harpoonDetachSourceCapsA(T,source,root,view){
  const specs=ACTIVE_SHIP_PROFILE.weapons.harpoon.tubes,geometry=source.geometry,index=geometry.index.array,
    caps=new Set(specs.flatMap(t=>t.capFaces)),keep=[];
  view.harpoonCapsA=new Map();
  for(let i=0;i<index.length/3;i++)if(!caps.has(i))keep.push(index[3*i],index[3*i+1],index[3*i+2]);
  for(const spec of specs){
    const axis=new T.Vector3(spec.axis.x,spec.axis.z,spec.axis.y).normalize(),up=new T.Vector3(0,1,0),
      radial=up.clone().addScaledVector(axis,-up.dot(axis)).normalize(),hinge=axis.clone().cross(radial).normalize(),
      pivot=new T.Vector3(spec.muzzle.x,spec.muzzle.z,spec.muzzle.y).addScaledVector(radial,.30),
      ids=spec.capFaces.flatMap(i=>[index[3*i],index[3*i+1],index[3*i+2]]),used=[...new Set(ids)],map=new Map(used.map((id,i)=>[id,i])),g=new T.BufferGeometry();
    for(const [name,attribute]of Object.entries(geometry.attributes)){
      const data=new attribute.array.constructor(used.length*attribute.itemSize);
      for(let i=0;i<used.length;i++)for(let k=0;k<attribute.itemSize;k++)data[i*attribute.itemSize+k]=attribute.array[used[i]*attribute.itemSize+k];
      if(name==='position')for(let i=0;i<used.length;i++){data[3*i]-=pivot.x;data[3*i+1]-=pivot.y;data[3*i+2]-=pivot.z;}
      g.setAttribute(name,new T.BufferAttribute(data,attribute.itemSize,attribute.normalized));
    }
    g.setIndex(ids.map(id=>map.get(id)));g.computeBoundingBox();g.computeBoundingSphere();
    const door=new T.Group(),mesh=new T.Mesh(g,source.material);door.name='CG52_'+spec.id+'_CAP';door.position.copy(pivot);door.add(mesh);root.add(door);
    door.userData={physicsFeedback:false,sourceTriangleCount:spec.capFaces.length,tubeId:spec.id};mesh.castShadow=mesh.receiveShadow=true;
    view.harpoonCapsA.set(spec.id,{door,hinge});
  }
  geometry.setIndex(keep);source.userData.harpoonCapTrianglesDetached=caps.size;
}
function installHarpoonRendererA(view){
  const sync=view.syncEnemyAsmVisuals;
  view.syncEnemyAsmVisuals=function(st,dt){sync.call(this,st,dt);this.syncHarpoonVisualsA(st,dt);};
  const follow=view.setFollowKey;
  view.setFollowKey=function(key){const result=follow.call(this,key);if(result&&String(key).startsWith('HARPOON:'))this.orbit.distance=28;return result;};
  view.buildHarpoonMeshA=function(boosterOnly=false){
    const T=this.THREE,meta=HARPOON_MODEL_META_A,buf=HARPOON_MODEL_BUFFER_A;
    if(!this.harpoonAssetCacheA){
      const materials=meta.materials.map(m=>{const mat=new T.MeshStandardMaterial({roughness:m.roughness,metalness:m.metalness,side:T.DoubleSide});mat.color.setRGB(...m.color);return mat;});
      const meshes=meta.meshes.map(m=>{const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(new Float32Array(buf,m.pos[0],m.pos[1]),3));g.setAttribute('normal',new T.BufferAttribute(new Float32Array(buf,m.nor[0],m.nor[1]),3));g.setIndex(new T.BufferAttribute(new Uint32Array(buf,m.idx[0],m.idx[1]),1));g.computeBoundingBox();g.computeBoundingSphere();return {spec:m,geometry:g,material:materials[m.material]};});
      this.harpoonAssetCacheA={meshes,materials};
    }
    const root=new T.Group(),boost=new T.Group(),wings=[],tails=[];root.name=boosterOnly?'HARPOON_SEPARATED_BOOSTER':'RGM84D_BLOCK1C';
    root.add(boost);
    for(const row of this.harpoonAssetCacheA.meshes){
      const s=row.spec;if(boosterOnly&&s.role!=='BOOSTER')continue;
      const mesh=new T.Mesh(row.geometry,row.material);mesh.castShadow=mesh.receiveShadow=true;
      if(s.role==='WING'||s.role==='TAIL'){
        const pivot=new T.Group();pivot.position.fromArray(s.pivot);pivot.add(mesh);root.add(pivot);(s.role==='WING'?wings:tails).push(pivot);
      }else (s.role==='BOOSTER'?boost:root).add(mesh);
    }
    if(boosterOnly)boost.position.x=-meta.boosterCenterXM;
    Object.assign(root.userData,{booster:boost,wings,tails,sharedAsset:true,physicsFeedback:false});
    return root;
  };
  view.syncHarpoonVisualsA=function(st,dt){
    const T=this.THREE,layer=this.missileLayer;if(!T||!layer)return;
    for(const tube of st.harpoonInventory?.tubes??[]){const cap=this.harpoonCapsA?.get(tube.id);if(cap)cap.door.quaternion.setFromAxisAngle(cap.hinge,-1.8*(tube.capOpen01??0));}
    if(!this.harpoonVisualsA)this.harpoonVisualsA=new Map();
    const seen=new Set();
    for(const s of [...(st.harpoons??[]),...(st.harpoonBoosters??[])]){
      const booster=String(s.id).startsWith('HB-');if(this.distanceToViewAnchorWip14A(s.xM,s.zM)>180000)continue;
      seen.add(s.id);let v=this.harpoonVisualsA.get(s.id);
      if(!v){const mesh=this.buildHarpoonMeshA(booster);layer.add(mesh);v={mesh,smokeLastPose:null,smokeCarryM:0};this.harpoonVisualsA.set(s.id,v);
        if(!booster){
          const flame=new T.Mesh(new T.ConeGeometry(.16,2.5,10,1,true),new T.MeshBasicMaterial({color:0xffc975,transparent:true,opacity:.85,blending:T.AdditiveBlending,depthWrite:false}));
          flame.rotation.z=-Math.PI/2;flame.position.x=-3.55;mesh.add(flame);v.flame=flame;
          // Emit at the captured physical launch point, never a current ship point.
          if(s.launchRearM&&s.lifeS<1)this.spawnEventSmoke({xM:s.launchRearM.x,yM:s.launchRearM.z,zM:s.launchRearM.y},16,1.0,7,.4,.75,0,false);
        }
      }
      const dir=new T.Vector3(Math.cos(s.pitchRad)*Math.cos(s.headingRad),Math.sin(s.pitchRad),Math.cos(s.pitchRad)*Math.sin(s.headingRad)).normalize();
      v.mesh.position.set(s.xM,s.yM,s.zM);v.mesh.quaternion.setFromUnitVectors(new T.Vector3(1,0,0),dir);
      if(booster){v.mesh.quaternion.multiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(1,0,0),s.rollRad??0));continue;}
      v.mesh.userData.booster.visible=s.boosterAttached;
      for(const wing of v.mesh.userData.wings)wing.rotation.x=Math.PI*(1-s.wingDeploy01);
      for(const tail of v.mesh.userData.tails){tail.rotation.x=Math.PI*(1-s.tailDeploy01);tail.rotation.y=s.tailCommandRad;}
      v.flame.visible=s.motorActive;
      v.flame.position.x=s.boosterAttached?-3.55:-1.8;v.flame.scale.set(s.boosterAttached?1:.15,s.boosterAttached?1:.18,s.boosterAttached?1:.15);
      if(s.boosterAttached&&s.motorActive){
        for(const p of this.smokeTrailSamples(v,{x:s.xM,y:s.yM,z:s.zM,dir},1.8,72))this.spawnEventSmoke({xM:p.x-p.dir.x*2.315,yM:p.y-p.dir.y*2.315,zM:p.z-p.dir.z*2.315},1,.75,8,.25,.62,0,false,
          {velocity:{x:-p.dir.x*22,y:-p.dir.y*22,z:-p.dir.z*22},inheritFrac:.4});
      }else this.resetSmokeTrail(v);
    }
    for(const [id,v]of this.harpoonVisualsA)if(!seen.has(id)){layer.remove(v.mesh);if(v.flame){v.flame.geometry.dispose();v.flame.material.dispose();}this.harpoonVisualsA.delete(id);}
  };
  view.harpoonAuditA=function(){return {caps:[...(this.harpoonCapsA??[])].map(([id,q])=>({id,sourceTriangles:q.door.userData.sourceTriangleCount,quaternion:q.door.quaternion.toArray()})),
    instances:this.harpoonVisualsA?.size??0,cachedGeometries:this.harpoonAssetCacheA?.meshes.length??0,textureMaps:0,physicsFeedback:false};};
}
