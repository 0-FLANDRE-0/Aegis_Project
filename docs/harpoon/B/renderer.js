// Geometry and exhaust presentation only; consume solved B1 flight states.
function harpoonLatheB(T,points,segments=48){
  const g=new T.LatheGeometry(points.map(([x,r])=>new T.Vector2(r,x)),segments);
  g.rotateZ(-Math.PI/2);g.computeBoundingBox();g.computeBoundingSphere();return g;
}
function harpoonDetachSourceCapsA(T,source,root,view){
  const specs=ACTIVE_SHIP_PROFILE.weapons.harpoon.tubes,geometry=source.geometry,index=geometry.index.array,
    reg=HARPOON_MOUTH_REGISTRATION_B.rows,detached=new Set(reg.flatMap(r=>[...r.doorFaces,...r.rearFaces])),
    cuts=HARPOON_MOUTH_REGISTRATION_B.supportBoreCuts,cutFaces=new Set(cuts.map(r=>r.sourceFace)),keep=[],c=HARPOON_VISUAL_PROFILE_B;
  view.harpoonCapsA=new Map();view.harpoonTubeCacheB={
    bore:new T.CylinderGeometry(c.tubeInnerRadiusM,c.tubeInnerRadiusM,1,36,1,true),
    rim:new T.RingGeometry(c.tubeInnerRadiusM,c.tubeOuterRadiusM,36),
    liner:new T.MeshStandardMaterial({color:0x202b30,roughness:.90,metalness:.12,side:T.DoubleSide}),
    rimMat:new T.MeshStandardMaterial({color:0x718084,roughness:.77,metalness:.24,side:T.DoubleSide})};
  for(let i=0;i<index.length/3;i++)if(!detached.has(i)&&!cutFaces.has(i))keep.push(index[3*i],index[3*i+1],index[3*i+2]);
  function extract(faces,pivot){
    const ids=faces.flatMap(i=>[index[3*i],index[3*i+1],index[3*i+2]]),used=[...new Set(ids)],map=new Map(used.map((id,i)=>[id,i])),g=new T.BufferGeometry();
    for(const [name,attribute]of Object.entries(geometry.attributes)){
      const data=new attribute.array.constructor(used.length*attribute.itemSize);
      for(let i=0;i<used.length;i++)for(let k=0;k<attribute.itemSize;k++)data[i*attribute.itemSize+k]=attribute.array[used[i]*attribute.itemSize+k];
      if(name==='position')for(let i=0;i<used.length;i++){data[3*i]-=pivot.x;data[3*i+1]-=pivot.y;data[3*i+2]-=pivot.z;}
      g.setAttribute(name,new T.BufferAttribute(data,attribute.itemSize,attribute.normalized));
    }
    g.setIndex(ids.map(id=>map.get(id)));g.computeBoundingBox();g.computeBoundingSphere();return g;
  }
  for(const spec of specs){
    const rows=reg.find(r=>r.tubeId===spec.id),axis=new T.Vector3(spec.axis.x,spec.axis.z,spec.axis.y).normalize(),up=new T.Vector3(0,1,0),
      radial=up.clone().addScaledVector(axis,-up.dot(axis)).normalize(),hinge=axis.clone().cross(radial).normalize(),
      mouth=new T.Vector3(spec.muzzle.x,spec.muzzle.z,spec.muzzle.y),pivot=mouth.clone().addScaledVector(radial,.30),
      rearPoint=new T.Vector3(spec.rear.x,spec.rear.z,spec.rear.y),door=new T.Group(),mesh=new T.Mesh(extract(rows.doorFaces,pivot),source.material),
      rear=new T.Mesh(extract(rows.rearFaces,rearPoint),source.material),cache=view.harpoonTubeCacheB;
    door.name='CG52_'+spec.id+'_FULL_CAP';door.position.copy(pivot);door.add(mesh);root.add(door);
    door.userData={physicsFeedback:false,sourceTriangleCount:rows.doorFaces.length,tubeId:spec.id};mesh.castShadow=mesh.receiveShadow=true;
    rear.position.copy(rearPoint);rear.name='CG52_'+spec.id+'_REAR_COVER';root.add(rear);
    const bore=new T.Mesh(cache.bore,cache.liner),length=spec.lengthM-c.tubeFrontDepthM-.018;
    bore.quaternion.setFromUnitVectors(up,axis);bore.scale.y=length;bore.position.copy(mouth).addScaledVector(axis,-c.tubeFrontDepthM-length*.5);root.add(bore);bore.receiveShadow=true;
    const rims=[];for(const offset of [-c.tubeFrontDepthM,-spec.lengthM+.01]){
      const rim=new T.Mesh(cache.rim,cache.rimMat);rim.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),axis);rim.position.copy(mouth).addScaledVector(axis,offset);root.add(rim);rims.push(rim);
    }
    view.harpoonCapsA.set(spec.id,{door,hinge,rear,bore,rims,innerRadiusM:c.tubeInnerRadiusM,boreDepthM:length});
  }
  // Authoring stores barycentric vertices so all source surface attributes survive
  // the small circular cuts in rack supports that otherwise block the hollow bore.
  const appended=cuts.flatMap(r=>r.triangles.flatMap(tri=>tri.map(weights=>({face:r.sourceFace,weights})))),first=geometry.attributes.position.count;
  for(const [name,attribute]of Object.entries(geometry.attributes)){
    const normal=name==='normal',size=attribute.itemSize,data=normal?new Float32Array((first+appended.length)*size):new attribute.array.constructor((first+appended.length)*size),
      read=(i,k)=>normal?(k===0?attribute.getX(i):k===1?attribute.getY(i):attribute.getZ(i)):attribute.array[i*size+k];
    if(normal){for(let i=0;i<first;i++)for(let k=0;k<size;k++)data[i*size+k]=read(i,k);}else data.set(attribute.array);
    for(let j=0;j<appended.length;j++){
      const q=appended[j];for(let k=0;k<size;k++){let value=0;for(let corner=0;corner<3;corner++)value+=q.weights[corner]*read(index[q.face*3+corner],k);data[(first+j)*size+k]=value;}
      if(normal){const at=(first+j)*size,n=Math.hypot(data[at],data[at+1],data[at+2])||1;for(let k=0;k<3;k++)data[at+k]/=n;}
    }
    geometry.setAttribute(name,new T.BufferAttribute(data,size,normal?false:attribute.normalized));
  }
  for(let i=0;i<appended.length;i++)keep.push(first+i);
  geometry.setIndex(keep);geometry.computeBoundingBox();geometry.computeBoundingSphere();
  source.userData.harpoonCapTrianglesDetached=detached.size;source.userData.harpoonBoreSupportFacesCut=cuts.length;
}
function harpoonPlumeGeometryB(T,points){return harpoonLatheB(T,points,32);}
function harpoonPlumeMaterialB(T,length,core,jet){
  return new T.ShaderMaterial({name:'HARPOON_'+(jet?'JET':'BOOST')+'_'+(core?'CORE':'SHEATH'),transparent:true,
    depthWrite:false,depthTest:true,toneMapped:false,blending:T.AdditiveBlending,side:T.DoubleSide,
    uniforms:{time:{value:0},power:{value:1},length:{value:length},alpha:{value:core?.86:(jet?.12:.26)},
      hot:{value:new T.Color(jet?(core?0xd5e9ff:0x789dff):(core?0xfff5d5:0xffa348))},cool:{value:new T.Color(jet?0x638fdc:0xe95e20)}},
    vertexShader:`#include <common>
      #include <logdepthbuf_pars_vertex>
      varying vec3 local;varying vec3 worldNormal;varying vec3 eye;
      void main(){local=position;worldNormal=normalize(normalMatrix*normal);vec4 mvPosition=modelViewMatrix*vec4(position,1.0);eye=-mvPosition.xyz;
      gl_Position=projectionMatrix*mvPosition;
      #include <logdepthbuf_vertex>
      }`,
    fragmentShader:`#include <common>
      #include <logdepthbuf_pars_fragment>
      uniform float time,power,length,alpha;uniform vec3 hot,cool;
      varying vec3 local,worldNormal,eye;
      void main(){
      #include <logdepthbuf_fragment>
      float u=clamp(-local.x/length,0.0,1.0),edge=pow(abs(dot(normalize(worldNormal),normalize(eye))),.55);
      float wav=.92+.08*sin(41.0*u-25.0*time)+.035*sin(93.0*u+19.0*time);
      float opacity=alpha*power*pow(1.0-u,1.35)*(.40+.60*edge)*wav;
      gl_FragColor=vec4(mix(hot,cool,smoothstep(.15,1.0,u)),opacity);}`});
}
function installHarpoonRendererA(view){
  const sync=view.syncEnemyAsmVisuals;
  view.syncEnemyAsmVisuals=function(st,dt){sync.call(this,st,dt);this.syncHarpoonVisualsA(st,dt);};
  const follow=view.setFollowKey;
  view.setFollowKey=function(key){const result=follow.call(this,key);if(result&&String(key).startsWith('HARPOON:'))this.orbit.distance=28;return result;};
  view.ensureHarpoonAssetB=function(){
    if(this.harpoonAssetCacheA)return this.harpoonAssetCacheA;
    const T=this.THREE,meta=HARPOON_MODEL_META_A,buf=HARPOON_MODEL_BUFFER_A,c=HARPOON_VISUAL_PROFILE_B,
      materials=meta.materials.map(m=>{const mat=new T.MeshStandardMaterial({roughness:m.roughness,metalness:m.metalness,side:T.DoubleSide});mat.color.setRGB(...m.color);return mat;}),
      meshes=meta.meshes.map(m=>{const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(new Float32Array(buf,m.pos[0],m.pos[1]),3));g.setAttribute('normal',new T.BufferAttribute(new Float32Array(buf,m.nor[0],m.nor[1]),3));g.setIndex(new T.BufferAttribute(new Uint32Array(buf,m.idx[0],m.idx[1]),1));g.computeBoundingBox();g.computeBoundingSphere();return {spec:m,geometry:g,material:materials[m.material]};}),
      paint=materials[8],metal=new T.MeshStandardMaterial({color:0x6a7174,roughness:.54,metalness:.46,side:T.DoubleSide}),
      throat=new T.MeshStandardMaterial({color:0x070a0d,roughness:.97,metalness:.08,side:T.DoubleSide}),
      circle=r=>{const g=new T.CircleGeometry(r,48);g.rotateY(-Math.PI/2);return g;};
    this.harpoonAssetCacheA={meshes,materials,extra:{
      bodyShell:harpoonLatheB(T,c.bodyShell),bodyBell:harpoonLatheB(T,c.bodyBell),bodyThroat:circle(.078),
      boosterShell:harpoonLatheB(T,c.boosterShell),boosterBell:harpoonLatheB(T,c.boosterBell),boosterThroat:circle(.075),paint,metal,throat,
      boostOuter:harpoonPlumeGeometryB(T,[[0,.139],[-.18,.158],[-.50,.204],[-.94,.163],[-1.40,.129],[-1.95,.073],[-2.60,0]]),
      boostCore:harpoonPlumeGeometryB(T,[[0,.083],[-.14,.108],[-.55,.104],[-.96,.074],[-1.44,.032],[-1.86,0]]),
      jetOuter:harpoonPlumeGeometryB(T,[[0,.113],[-.05,.121],[-.14,.094],[-.28,.052],[-.48,0]]),
      jetCore:harpoonPlumeGeometryB(T,[[0,.066],[-.04,.073],[-.12,.050],[-.24,0]])}};
    return this.harpoonAssetCacheA;
  };
  view.buildHarpoonMeshA=function(boosterOnly=false){
    const T=this.THREE,c=HARPOON_VISUAL_PROFILE_B,cache=this.ensureHarpoonAssetB(),root=new T.Group(),boost=new T.Group(),coupling=new T.Group(),wings=[],tails=[];
    root.name=boosterOnly?'HARPOON_SEPARATED_BOOSTER':'RGM84D_BLOCK1C';root.add(boost,coupling);
    for(const row of cache.meshes){
      const s=row.spec;if(boosterOnly&&s.role!=='BOOSTER')continue;
      if(s.role==='BODY'&&c.replacedBodySources.includes(s.sourceMesh)||s.role==='BOOSTER'&&c.replacedBoosterSources.includes(s.sourceMesh))continue;
      const mesh=new T.Mesh(row.geometry,row.material);mesh.castShadow=mesh.receiveShadow=true;mesh.name='HARPOON_SOURCE_'+s.sourceMesh+'_'+s.role;
      if(s.role==='WING'||s.role==='TAIL'){
        const pivot=new T.Group();pivot.position.fromArray(s.pivot);pivot.add(mesh);root.add(pivot);(s.role==='WING'?wings:tails).push(pivot);
      }else (s.role==='BOOSTER'?boost:c.couplingBodySources.includes(s.sourceMesh)?coupling:root).add(mesh);
    }
    const extra=cache.extra,add=(parent,name,g,mat,x=0)=>{const m=new T.Mesh(g,mat);m.name=name;m.position.x=x;m.castShadow=m.receiveShadow=true;parent.add(m);return m;};
    const bodyNozzle=new T.Group();bodyNozzle.name='HARPOON_TAPERED_AFT_AND_RECESSED_NOZZLE';
    if(!boosterOnly){root.add(bodyNozzle);add(root,'HARPOON_BODY_FAIRING',extra.bodyShell,extra.paint);add(bodyNozzle,'HARPOON_BODY_OPEN_BELL',extra.bodyBell,extra.metal);add(bodyNozzle,'HARPOON_BODY_RECESSED_THROAT',extra.bodyThroat,extra.throat,c.bodyThroatXM);}
    add(boost,'HARPOON_BOOSTER_FAIRING',extra.boosterShell,extra.paint);add(boost,'HARPOON_BOOSTER_OPEN_BELL',extra.boosterBell,extra.metal);add(boost,'HARPOON_BOOSTER_RECESSED_THROAT',extra.boosterThroat,extra.throat,-2.16);
    if(boosterOnly)boost.position.x=-HARPOON_MODEL_META_A.boosterCenterXM;
    Object.assign(root.userData,{booster:boost,bodyNozzle,coupling,wings,tails,sharedAsset:true,physicsFeedback:false});return root;
  };
  view.createHarpoonExhaustB=function(){
    const T=this.THREE,cache=this.ensureHarpoonAssetB().extra,g=new T.Group(),boost=new T.Group(),jet=new T.Group();
    g.add(boost,jet);boost.position.x=HARPOON_VISUAL_PROFILE_B.boosterExitXM;jet.position.x=HARPOON_VISUAL_PROFILE_B.bodyExitXM;
    const add=(parent,geometry,length,core,isJet)=>{const mat=harpoonPlumeMaterialB(T,length,core,isJet),mesh=new T.Mesh(geometry,mat);mesh.name=mat.name;parent.add(mesh);return mesh;};
    add(boost,cache.boostOuter,2.60,false,false);add(boost,cache.boostCore,1.86,true,false);
    add(jet,cache.jetOuter,.48,false,true);add(jet,cache.jetCore,.24,true,true);
    Object.assign(g.userData,{boost,jet,nozzleAnchored:true,physicsFeedback:false});return g;
  };
  view.spawnHarpoonLaunchB=function(s){
    const cfg=HARPOON_VISUAL_PROFILE_B;if(s.lifeS>=cfg.launchCloudLifeS)return;
    const spec=harpoonTubeSpecA(s.tubeId);if(!spec)return;
    if(!this.harpoonLaunchEmittersB)this.harpoonLaunchEmittersB=new Map();
    if(this.harpoonLaunchEmittersB.has(s.id))return;
    const now=c13Smoke(this).time,axis=shipGameFrameV1().vectorToWorld(spec.axis),e={id:s.id,tubeId:s.tubeId,age:s.lifeS,start:now-s.lifeS,
      spec,axis:new this.THREE.Vector3(axis.x,axis.z,axis.y),emitter:c13SmokeHash('HARPOON_LAUNCH_B:'+s.id),lastAge:Math.max(0,s.lifeS-.10),born:0,hotBorn:0};
    this.harpoonLaunchEmittersB.set(s.id,e);
    if(s.lifeS<.20){const p=shipGameRenderPointV1(spec.rear.x,spec.rear.y,spec.rear.z);this.spawnEventFlash(p,.66,0xffd09b,.085,.40);}
    while(this.harpoonLaunchEmittersB.size>cfg.maxLaunchEmitters)this.harpoonLaunchEmittersB.delete(this.harpoonLaunchEmittersB.keys().next().value);
  };
  view.updateHarpoonLaunchB=function(states){
    if(!this.harpoonLaunchEmittersB)return;const cfg=HARPOON_VISUAL_PROFILE_B,now=c13Smoke(this).time,r=()=>this.fxRandom();
    for(const [id,e]of this.harpoonLaunchEmittersB){
      const s=states.find(q=>q.id===id);e.age=Math.max(e.age,s?.lifeS??0,now-e.start);
      if(e.age>=cfg.launchCloudLifeS){this.harpoonLaunchEmittersB.delete(id);continue;}
      const delta=Math.min(.12,Math.max(0,e.age-e.lastAge));if(!delta)continue;e.lastAge=e.age;
      const p=shipGameRenderPointV1(e.spec.rear.x,e.spec.rear.y,e.spec.rear.z),d=e.axis,
        rear=new this.THREE.Vector3(p.xM,p.yM,p.zM),envelope=1-this.smooth01((e.age-.28)/.95),n=Math.min(20,Math.ceil(delta*125*envelope));
      for(let i=0;i<n;i++){
        const along=.06+r()*.55,pos=rear.clone().addScaledVector(d,-along),size=.80+r()*.80;
        if(c13EmitSmoke(this,{kind:3,emitter:e.emitter,x:pos.x,y:pos.y,z:pos.z,life:5.2+r()*2.8,base:size,growth:.45+r()*.25,
          alpha:(.65+r()*.20)*envelope,vx:-d.x*(9+r()*14)+(r()-.5)*3,vy:-d.y*(9+r()*14)+(r()-.5)*3,vz:-d.z*(9+r()*14)+(r()-.5)*3,
          drag:1.1,rise:.55,fade:1.9,color:c13SmokeColor(this,i%3?0xd9d6ce:0xaeb1b0),turbulence:1.1,rotation:r()*6.28}))e.born++;
      }
      // A brief mouth puff accompanies the solved tail leaving the canister;
      // the main hot gas remains the registered rear backblast above.
      if(s?.tubeCleared&&e.age<.68){
        const mouth=shipGameRenderPointV1(e.spec.muzzle.x,e.spec.muzzle.y,e.spec.muzzle.z);
        for(let i=0;i<Math.min(4,Math.ceil(delta*28));i++)c13EmitSmoke(this,{kind:3,emitter:e.emitter,
          x:mouth.xM+d.x*.10,y:mouth.yM+d.y*.10,z:mouth.zM+d.z*.10,life:1.2+r()*.7,base:.24+r()*.13,growth:.75,
          alpha:.24,vx:d.x*3+(r()-.5),vy:d.y*3+(r()-.5),vz:d.z*3+(r()-.5),drag:1.0,rise:.15,fade:1.9,
          color:c13SmokeColor(this,0xdadbd6),rotation:r()*6.28});
      }
      if(e.age<cfg.launchHotLifeS&&s?.motorActive){
        for(const core of [false,true]){
          const pos=rear.clone().addScaledVector(d,-(core?.34:.65));
          if(c13EmitSmoke(this,{kind:6,emitter:e.emitter,x:pos.x,y:pos.y,z:pos.z,life:.075,base:core?.23:.43,span:core?.58:1.0,
            ax:-d.x,ay:-d.y,az:-d.z,aspect:1,alpha:(core?.78:.48)*(1-e.age/cfg.launchHotLifeS),
            vx:-d.x*10,vy:-d.y*10,vz:-d.z*10,drag:2,rise:0,growth:.35,burst:true,fadeIn:.012,hold:.1,tile:1,
            color:c13SmokeColor(this,core?0xfff0cf:0xffa64a,core?1.4:1.1),endColor:c13SmokeColor(this,0xe55d24)}))e.hotBorn++;
        }
      }
    }
  };
  view.syncHarpoonVisualsA=function(st,dt){
    const T=this.THREE,layer=this.missileLayer;if(!T||!layer)return;const epoch=st.sim?.presentationEpoch??0;
    if(this._harpoonFxEpochB!==epoch){this.harpoonLaunchEmittersB?.clear();this._harpoonFxEpochB=epoch;}
    for(const tube of st.harpoonInventory?.tubes??[]){const cap=this.harpoonCapsA?.get(tube.id);if(cap){cap.door.quaternion.setFromAxisAngle(cap.hinge,-1.8*(tube.capOpen01??0));cap.rear.visible=tube.loaded;}}
    if(!this.harpoonVisualsA)this.harpoonVisualsA=new Map();const seen=new Set(),cfg=HARPOON_VISUAL_PROFILE_B;
    for(const s of [...(st.harpoons??[]),...(st.harpoonBoosters??[])]){
      const booster=String(s.id).startsWith('HB-');if(this.distanceToViewAnchorWip14A(s.xM,s.zM)>180000)continue;
      seen.add(s.id);let v=this.harpoonVisualsA.get(s.id);
      if(!v){const mesh=this.buildHarpoonMeshA(booster);layer.add(mesh);v={mesh,smokeLastPose:null,smokeCarryM:0};this.harpoonVisualsA.set(s.id,v);
        if(!booster){v.exhaust=this.createHarpoonExhaustB();mesh.add(v.exhaust);this.spawnHarpoonLaunchB(s);}}
      const dir=new T.Vector3(Math.cos(s.pitchRad)*Math.cos(s.headingRad),Math.sin(s.pitchRad),Math.cos(s.pitchRad)*Math.sin(s.headingRad)).normalize();
      v.mesh.position.set(s.xM,s.yM,s.zM);v.mesh.quaternion.setFromUnitVectors(new T.Vector3(1,0,0),dir);
      if(booster){v.mesh.quaternion.multiply(new T.Quaternion().setFromAxisAngle(new T.Vector3(1,0,0),s.rollRad??0));continue;}
      const data=v.mesh.userData;data.booster.visible=s.boosterAttached;data.coupling.visible=s.boosterAttached;data.bodyNozzle.visible=!s.boosterAttached;
      for(const wing of data.wings)wing.rotation.x=Math.PI*(1-s.wingDeploy01);
      for(const tail of data.tails){tail.rotation.x=Math.PI*(1-s.tailDeploy01);tail.rotation.y=s.tailCommandRad;}
      const exhaust=v.exhaust.userData;exhaust.boost.visible=!!s.motorActive&&s.boosterAttached;exhaust.jet.visible=!!s.motorActive&&!s.boosterAttached;
      const stage=s.boosterAttached?exhaust.boost:exhaust.jet,power=clamp(s.thrustN/(s.boosterAttached?HARPOON_PROFILE_A.sim.boosterAverageThrustN:HARPOON_PROFILE_A.public.jetMaxThrustN),0,1),flicker=.97+.03*Math.sin(s.lifeS*53+String(s.id).length);
      stage.scale.set(.72+.28*Math.sqrt(power),flicker,flicker);
      for(const group of [exhaust.boost,exhaust.jet])for(const mesh of group.children){mesh.material.uniforms.time.value=s.lifeS;mesh.material.uniforms.power.value=.40+.60*Math.sqrt(power);}
      if(s.boosterAttached&&s.motorActive){
        const smoke=cfg.boosterSmoke,nozzle={x:s.xM+dir.x*cfg.boosterExitXM,y:s.yM+dir.y*cfg.boosterExitXM,z:s.zM+dir.z*cfg.boosterExitXM,dir};
        for(const p of this.smokeTrailSamples(v,nozzle,smoke.spacingM,cfg.maxSmokeSamplesPerFrame)){
          const q=p.dir,emitter=c13SmokeHash('HARPOON_BOOST_B:'+s.id);
          c13EmitSmoke(this,{kind:1,birth:p.birth,emitter,x:p.x-q.x*.80,y:p.y-q.y*.80,z:p.z-q.z*.80,
            life:smoke.lifeS,base:smoke.baseM,growth:smoke.growthPerS,alpha:smoke.alpha,span:Math.min(2.2,p.segmentM||0),ax:q.x,ay:q.y,az:q.z,
            vx:-q.x*7,vy:-q.y*7,vz:-q.z*7,drag:.60,rise:.30,turbulence:1.0,fade:smoke.fadePower,color:c13SmokeColor(this,smoke.color),rotation:this.fxRandom()*6.28});
        }
      }else this.resetSmokeTrail(v);
    }
    this.updateHarpoonLaunchB(st.harpoons??[]);
    for(const [id,v]of this.harpoonVisualsA)if(!seen.has(id)){layer.remove(v.mesh);if(v.exhaust)for(const group of v.exhaust.children)for(const m of group.children)m.material.dispose();this.harpoonVisualsA.delete(id);}
  };
  view.harpoonAuditA=function(){return {schema:'HARPOON_VISUAL_B_AUDIT',caps:[...(this.harpoonCapsA??[])].map(([id,q])=>({id,sourceTriangles:q.door.userData.sourceTriangleCount,quaternion:q.door.quaternion.toArray(),rearVisible:q.rear.visible,boreDepthM:q.boreDepthM,innerRadiusM:q.innerRadiusM})),
    instances:this.harpoonVisualsA?.size??0,cachedGeometries:this.harpoonAssetCacheA?.meshes.length??0,textureMaps:0,
    launchEmitters:[...(this.harpoonLaunchEmittersB?.values()??[])].map(e=>({id:e.id,tubeId:e.tubeId,age:e.age,born:e.born,hotBorn:e.hotBorn})),
    visuals:[...(this.harpoonVisualsA??[])].filter(([,v])=>v.exhaust).map(([id,v])=>({id,bodyNozzleVisible:v.mesh.userData.bodyNozzle.visible,couplingVisible:v.mesh.userData.coupling.visible,
      boostPlume:v.exhaust.userData.boost.visible,jetPlume:v.exhaust.userData.jet.visible,boostExitXM:v.exhaust.userData.boost.position.x,jetExitXM:v.exhaust.userData.jet.position.x})),
    physicsFeedback:false};};
}
