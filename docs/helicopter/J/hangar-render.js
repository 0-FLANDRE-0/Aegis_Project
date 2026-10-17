// Presentation-only source partition. Retain the original port leaf, facade,
// starboard stiffeners, window and flight-control structure. No sim writes.
function heloClipPolygonI(poly,axis,bound,sign){
  const inside=[],outside=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],da=(a.p[axis]-bound)*sign,db=(b.p[axis]-bound)*sign;
    (da>=0?inside:outside).push(a);if((da>=0)!==(db>=0)){const u=da/(da-db),p=a.p.map((v,j)=>v+(b.p[j]-v)*u),attrs={};for(const[k,v]of Object.entries(a.attrs))attrs[k]=v.map((x,j)=>x+(b.attrs[k][j]-x)*u);const v={p,attrs};inside.push(v);outside.push(v);}}
  return {inside,outside};
}
function heloDisposeDoorsI(view){const d=view.heloDoorsA;if(!d)return;for(const m of d.doors)m.removeFromParent();d.geo?.dispose();d.mat?.dispose();for(const g of d.sourceGeometries??[])g.dispose();delete view.heloDoorsA;const interior=view.heloHangarInteriorI;if(interior){interior.root.removeFromParent();for(const g of interior.geometries)g.dispose();for(const m of interior.materials)m.dispose();delete view.heloHangarInteriorI;}}
function heloBuildCgHangarI(view,root,F){
  const T=view.THREE,group=new T.Group();group.name='CG52_HELO_HANGAR_INTERIOR';group.userData={presentationOnly:true,physicsFeedback:false,source:'SIM_TUNED',basis:F.basis};root.add(group);
  const door=new T.Group();door.name='CG52_ORIGINAL_PORT_SLIDING_DOOR';door.userData={presentationOnly:true,physicsFeedback:false,source:'SOURCE_MODEL_REGISTRATION'};root.add(door);
  root.updateWorldMatrix(true,true);const inverse=root.matrixWorld.clone().invert();let removed=0,changed=0,sourceLeafTriangles=0;const sourceGeometries=[];
  const meshes=[],seen=new Set();for(const[key,part]of view._bunkerAsset.parts)if(/^CG52_(structure|fittings)_/.test(key))part.traverse(m=>{if(m.isMesh&&!seen.has(m)){seen.add(m);meshes.push(m);}});
  const center=heloDoorCenterI(0,F),lo=center-F.doorHalfWidthM,hi=center+F.doorHalfWidthM;
  for(const mesh of meshes){const g=mesh.geometry,index=g.index,p=g.attributes.position,attrs=Object.entries(g.attributes),out=Object.fromEntries(attrs.map(([k])=>[k,[]])),leaf=Object.fromEntries(attrs.map(([k])=>[k,[]])),toRoot=inverse.clone().multiply(mesh.matrixWorld),point=new T.Vector3();let touched=false;
    const emit=(poly,target=out)=>{for(let i=1;i<poly.length-1;i++)for(const v of [poly[0],poly[i],poly[i+1]])for(const[k]of attrs)target[k].push(...v.attrs[k]);};
    for(let i=0;i<(index?.count??p.count);i+=3){const poly=[];for(let j=0;j<3;j++){const id=index?index.getX(i+j):i+j;point.fromBufferAttribute(p,id).applyMatrix4(toRoot);poly.push({p:point.toArray(),attrs:Object.fromEntries(attrs.map(([k,a])=>[k,Array.from(a.array.slice(id*a.itemSize,(id+1)*a.itemSize))]))});}
      // Exact source port leaf is x[-30.6637,-30.413], lateral[-6.5801,-2.18],
      // z[9.8002,14.9002]. Carry its original personnel hatch/window with it.
      if(poly.every(v=>v.p[0]>=-30.75&&v.p[0]<=-30.40&&v.p[1]>=9.79&&v.p[1]<=14.91&&v.p[2]>=lo-.002&&v.p[2]<=hi+.002)){emit(poly,leaf);sourceLeafTriangles++;touched=true;continue;}
      if(poly.some(v=>v.p[0]<F.rearSlabMinXM||v.p[0]>F.rearSlabMaxXM)){emit(poly);continue;}
      // Subtract only the narrow original port doorway, not the whole rear wall.
      let remain=poly;for(const[axis,bound,sign]of [[1,F.doorBottomM,1],[1,F.doorTopM,-1],[2,lo,1],[2,hi,-1]]){if(remain.length<3)break;const q=heloClipPolygonI(remain,axis,bound,sign);if(q.outside.length>=3)emit(q.outside);remain=q.inside;}
      if(remain.length>=3){removed++;touched=true;}
    }
    const geometry=target=>{const next=new T.BufferGeometry();for(const[k,a]of attrs)next.setAttribute(k,new T.BufferAttribute(new a.array.constructor(target[k]),a.itemSize,a.normalized));next.computeBoundingBox();next.computeBoundingSphere();return next;};
    if(leaf.position.length){const dg=geometry(leaf),dm=new T.Mesh(dg,mesh.material);dm.name='CG52_SOURCE_LEAF_'+mesh.name;dm.matrixAutoUpdate=false;dm.matrix.copy(toRoot);dm.castShadow=mesh.castShadow;dm.receiveShadow=mesh.receiveShadow;dm.userData={presentationOnly:true,physicsFeedback:false,originalSourceLeaf:true};door.add(dm);sourceGeometries.push(dg);}
    if(touched){mesh.geometry=geometry(out);g.dispose();changed++;}
  }
  const materials={wall:new T.MeshStandardMaterial({color:0x7f8d8e,roughness:.95,side:T.DoubleSide}),floor:new T.MeshStandardMaterial({color:0x414f52,roughness:1}),equipment:new T.MeshStandardMaterial({color:0x596d73,roughness:.9}),guide:new T.MeshBasicMaterial({color:0xc5bd76}),light:new T.MeshStandardMaterial({color:0xe0e4d9,emissive:0xb9c8c1,emissiveIntensity:.5})},geometries=[];
  const box=(name,x,z,y,l,h,w,mat)=>{const g=new T.BoxGeometry(l,h,w),m=new T.Mesh(g,materials[mat]);m.name=name;m.position.set(x,z,y);m.receiveShadow=true;m.castShadow=mat!=='guide';m.userData={presentationOnly:true,physicsFeedback:false,aviationInterior:true};group.add(m);geometries.push(g);return m;};
  const a=F.interiorAftXM,b=F.interiorFwdXM,z0=F.interiorFloorZM,z1=F.interiorCeilingZM;
  for(let slot=0;slot<F.interiorBaysM.length;slot++){const[low,high]=F.interiorBaysM[slot],mid=(low+high)/2,prefix='HELO_BAY_'+slot;
    box(prefix+'_FLOOR',(a+b)/2,z0-.03,mid,b-a,.06,high-low,'floor');box(prefix+'_CEILING',(a+b)/2,z1+.03,mid,b-a,.06,high-low,'wall');
    for(const y of [low-.04,high+.04])box(prefix+'_SIDE',(a+b)/2,(z0+z1)/2,y,b-a,z1-z0,.08,'wall');
    box(prefix+'_FORWARD_BULKHEAD',b+.04,(z0+z1)/2,mid,.08,z1-z0,high-low+.16,'wall');
    box(prefix+'_CABINET',b-.2,z0+.7,mid,.25,1.4,1.6,'equipment');
    for(const y of [-F.parkBayOffsetM,F.parkStarboardOffsetM])box(prefix+'_GUIDE',(a+b)/2,z0+.004,y,b-a,.008,.06,'guide');
    for(const x of [a+3,b-2])box(prefix+'_LIGHT',x,z1-.015,low+.2,.7,.025,.08,'light');
  }
  view.heloDoorsA={root,facility:F,doors:[door],sourceGeometries,sourceLeafTriangles,changedMeshes:changed,removedPolygons:removed,relocatedStairTriangles:0};
  view.heloHangarInteriorI={root:group,geometries,materials:Object.values(materials),basis:F.basis};heloSyncDoorsA(view,[0]);
}
function heloSyncSourceDoorJ(view,values){
  const d=view.heloDoorsA;d.doors[0].position.z=heloSmoothA(values[0]??0)*d.facility.doorSlideM;
}
