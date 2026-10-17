// Presentation-only geometry authoring. Source vertex data never enters simulation.
function heloClipPolygonI(poly,axis,bound,sign){
  const inside=[],outside=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],da=(a.p[axis]-bound)*sign,db=(b.p[axis]-bound)*sign;
    (da>=0?inside:outside).push(a);if((da>=0)!==(db>=0)){const u=da/(da-db),p=a.p.map((v,j)=>v+(b.p[j]-v)*u),attrs={};for(const[k,v]of Object.entries(a.attrs))attrs[k]=v.map((x,j)=>x+(b.attrs[k][j]-x)*u);const v={p,attrs};inside.push(v);outside.push(v);}}
  return {inside,outside};
}
function heloDisposeDoorsI(view){const d=view.heloDoorsA;if(!d)return;for(const m of d.doors)m.removeFromParent();d.geo.dispose();d.mat.dispose();delete view.heloDoorsA;const interior=view.heloHangarInteriorI;if(interior){interior.root.removeFromParent();for(const g of interior.geometries)g.dispose();for(const m of interior.materials)m.dispose();delete view.heloHangarInteriorI;}}
function heloBuildCgHangarI(view,root,F){
  const T=view.THREE,group=new T.Group();group.name='CG52_HELO_HANGAR_INTERIOR';group.userData={presentationOnly:true,physicsFeedback:false,source:'SIM_TUNED',basis:F.basis};root.add(group);
  // Open both rectangles through every coincident layer of the authored rear wall.
  // Keep all source surfaces outside the single operational opening.
  root.updateWorldMatrix(true,true);const inverse=root.matrixWorld.clone().invert();let removed=0,changed=0;
  const meshes=[],seen=new Set();for(const[key,part]of view._bunkerAsset.parts)if(/^CG52_(structure|fittings)_/.test(key))part.traverse(m=>{if(m.isMesh&&!seen.has(m)){seen.add(m);meshes.push(m);}});
  for(const mesh of meshes){const g=mesh.geometry,index=g.index,p=g.attributes.position,attrs=Object.entries(g.attributes),out=Object.fromEntries(attrs.map(([k])=>[k,[]])),toRoot=inverse.clone().multiply(mesh.matrixWorld),point=new T.Vector3();let touched=false;
    const emit=poly=>{for(let i=1;i<poly.length-1;i++)for(const v of [poly[0],poly[i],poly[i+1]])for(const[k]of attrs)out[k].push(...v.attrs[k]);};
    for(let i=0;i<(index?.count??p.count);i+=3){const poly=[];for(let j=0;j<3;j++){const id=index?index.getX(i+j):i+j;point.fromBufferAttribute(p,id).applyMatrix4(toRoot);poly.push({p:point.toArray(),attrs:Object.fromEntries(attrs.map(([k,a])=>[k,Array.from(a.array.slice(id*a.itemSize,(id+1)*a.itemSize))]))});}
      if(poly.some(v=>v.p[0]<F.rearSlabMinXM||v.p[0]>F.rearSlabMaxXM)){emit(poly);continue;}
      let fragments=[poly];for(let slot=0;slot<heloDoorCountI(F);slot++){const center=heloDoorCenterI(slot,F),next=[];for(const triangle of fragments){let remain=triangle;for(const[axis,bound,sign]of [[1,F.doorBottomM,1],[1,F.doorTopM,-1],[2,center-F.doorHalfWidthM,1],[2,center+F.doorHalfWidthM,-1]]){if(remain.length<3)break;const q=heloClipPolygonI(remain,axis,bound,sign);if(q.outside.length>=3)next.push(q.outside);remain=q.inside;}if(remain.length>=3){removed++;touched=true;}}fragments=next;}for(const poly of fragments)emit(poly);
    }
    if(touched){const next=new T.BufferGeometry();for(const[k,a]of attrs)next.setAttribute(k,new T.BufferAttribute(new a.array.constructor(out[k]),a.itemSize,a.normalized));next.computeBoundingBox();next.computeBoundingSphere();mesh.geometry=next;g.dispose();changed++;}
  }
  const materials={wall:new T.MeshStandardMaterial({color:0x7f8d8e,roughness:.95,side:T.DoubleSide}),floor:new T.MeshStandardMaterial({color:0x414f52,roughness:1}),equipment:new T.MeshStandardMaterial({color:0x596d73,roughness:.9}),guide:new T.MeshBasicMaterial({color:0xc5bd76}),light:new T.MeshStandardMaterial({color:0xe0e4d9,emissive:0xb9c8c1,emissiveIntensity:.5})},geometries=[];
  const box=(name,x,z,y,l,h,w,mat)=>{const g=new T.BoxGeometry(l,h,w),m=new T.Mesh(g,materials[mat]);m.name=name;m.position.set(x,z,y);m.receiveShadow=true;m.castShadow=mat!=='guide';m.userData={presentationOnly:true,physicsFeedback:false,aviationInterior:true};group.add(m);geometries.push(g);return m;};
  const a=F.interiorAftXM,b=F.interiorFwdXM,z0=F.interiorFloorZM,z1=F.interiorCeilingZM;
  for(let slot=0;slot<F.interiorBaysM.length;slot++){const[lo,hi]=F.interiorBaysM[slot],mid=(lo+hi)/2,prefix='HELO_BAY_'+slot;
    box(prefix+'_FLOOR',(a+b)/2,z0-.03,mid,b-a,.06,hi-lo,'floor');box(prefix+'_CEILING',(a+b)/2,z1+.03,mid,b-a,.06,hi-lo,'wall');
    for(const y of [lo-.04,hi+.04])box(prefix+'_SIDE',(a+b)/2,(z0+z1)/2,y,b-a,z1-z0,.08,'wall');
    box(prefix+'_FORWARD_BULKHEAD',b+.04,(z0+z1)/2,mid,.08,z1-z0,hi-lo+.16,'wall');
    box(prefix+'_CABINET',b-.2,z0+.7,mid,.25,1.4,1.6,'equipment');
    // Guides and ceiling fittings are outside the folded swept volume.
    box(prefix+'_GUIDE',(a+b)/2,z0+.004,mid,b-a,.008,.06,'guide');
    for(const x of [a+3,b-2])box(prefix+'_LIGHT',x,z1-.015,slot===0?lo+.2:hi-.2,.7,.025,.08,'light');
  }
  // Frames sit outside each clear opening; doors share the existing slat adapter.
  for(let slot=0;slot<heloDoorCountI(F);slot++){const center=heloDoorCenterI(slot,F);for(const y of [center-F.doorHalfWidthM-.055,center+F.doorHalfWidthM+.055])box('HELO_DOOR_JAMB_'+slot,F.doorXAtFloor-.05,(F.doorBottomM+F.doorTopM)/2,y,.15,F.doorTopM-F.doorBottomM,.08,'wall');}
  const geo=new T.BoxGeometry(.075,1,1),mat=new T.MeshStandardMaterial({color:0x748489,roughness:.88}),doors=[];
  for(let slot=0;slot<heloDoorCountI(F);slot++){const m=new T.InstancedMesh(geo,mat,2);m.name='HELO_HANGAR_SHUTTER_'+slot;m.frustumCulled=false;m.userData={presentationOnly:true,physicsFeedback:false,slot};root.add(m);doors.push(m);}
  view.heloDoorsA={root,facility:F,doors,geo,mat,dummy:new T.Object3D(),changedMeshes:changed,removedPolygons:removed,relocatedStairTriangles:0};
  view.heloHangarInteriorI={root:group,geometries,materials:Object.values(materials),basis:F.basis};heloSyncDoorsA(view,Array(heloDoorCountI(F)).fill(0));
}

function heloSyncFoldingDoorI(view,values){
  const d=view.heloDoorsA,F=d.facility,theta=heloSmoothA(values[0]??0)*Math.PI/2,L=(F.doorHingeTopZM-F.doorBottomM)/2,top=F.doorHingeTopZM;
  const centers=[{x:F.doorXAtFloor-.12-L*.5*Math.sin(theta),y:top-L*.5*Math.cos(theta),angle:-theta},
    {x:F.doorXAtFloor-.12-L*.5*Math.sin(theta),y:top-1.5*L*Math.cos(theta)-.11*Math.sin(theta),angle:theta}];
  const mesh=d.doors[0];for(let i=0;i<2;i++){const q=centers[i];d.dummy.position.set(q.x,q.y,heloDoorCenterI(0,F));d.dummy.rotation.set(0,0,q.angle);d.dummy.scale.set(1,L-.025,F.doorHalfWidthM*2);d.dummy.updateMatrix();mesh.setMatrixAt(i,d.dummy.matrix);}mesh.count=2;mesh.instanceMatrix.needsUpdate=true;
}
