// Display-only SH-60 asset decoder; geometry/material arrays are shared within a lease.
// The original Three.js engine is supplied by the caller. No new loader dependency.
function decodeSeahawkAssetA1(bytes){
 const d=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
 if(String.fromCharCode(...bytes.subarray(0,4))!=='HLA1')throw Error('HELI_ASSET_FORMAT');
 const n=d.getUint32(4,true),meta=JSON.parse(new TextDecoder().decode(bytes.subarray(8,8+n))),start=8+n+(4-n%4)%4;
 if(meta.schema!=='AEGIS_SH60_RENDER_ASSET_A1')throw Error('HELI_ASSET_SCHEMA');
 return {meta,bytes,start};
}
function createSeahawkAssetLeaseA1(T,source){
 const a=source.meta,attributes=a.accessors.map(r=>{const off=source.bytes.byteOffset+source.start+r.offset,n=r.count*r.itemSize;
  if(r.codec==='U16')return new T.BufferAttribute(new Uint16Array(source.bytes.buffer,off,n),r.itemSize);
  if(r.codec==='SNORM16')return new T.BufferAttribute(new Int16Array(source.bytes.buffer,off,n),r.itemSize,true);
  if(r.codec!=='Q16')throw Error('HELI_ATTRIBUTE_CODEC');
  const q=new Uint16Array(source.bytes.buffer,off,n),f=new Float32Array(n);for(let i=0;i<n;i++)f[i]=r.min[i%r.itemSize]+q[i]*r.scale[i%r.itemSize];return new T.BufferAttribute(f,r.itemSize);
 });
 const geometries=a.meshes.map(m=>m.primitives.map(p=>{const g=new T.BufferGeometry();g.setAttribute('position',attributes[p.attributes.POSITION]);g.setAttribute('normal',attributes[p.attributes.NORMAL]);g.setIndex(attributes[p.indices]);g.computeBoundingBox();g.computeBoundingSphere();return g}));
 const materials=a.materials.map(m=>{const p=m.pbrMetallicRoughness,c=p.baseColorFactor||[1,1,1,1];return new T.MeshStandardMaterial({color:new T.Color().setRGB(...c.slice(0,3)),metalness:p.metallicFactor??1,roughness:p.roughnessFactor??1,transparent:m.alphaMode==='BLEND',opacity:c[3],side:m.doubleSided?T.DoubleSide:T.FrontSide})});
 let retired=false;const roots=new Set();
 return {meta:a,geometries,materials,build(pose='deployed'){
  if(retired)throw Error('HELI_ASSET_RETIRED');const root=new T.Group();root.name='SH60:'+pose;root.userData={presentationOnly:true,physicsFeedback:false,assetSchema:a.schema};const parts=new Map();
  for(const p of a.parts){const g=new T.Group();g.name=p.name;g.matrix.fromArray(p.matrix);g.matrixAutoUpdate=false;g.userData={sourceNode:p.id};for(const r of p.primitives){const primitive=a.meshes[r.mesh].primitives[r.primitive];g.add(new T.Mesh(geometries[r.mesh][r.primitive],materials[primitive.material]))}root.add(g);parts.set(p.id,g)}
  const setPose=mode=>{const ids=mode==='all'?a.parts.map(p=>p.id):a.poses[mode];if(!ids)throw Error('HELI_POSE_UNKNOWN');const active=new Set(ids);for(const[id,p]of parts)p.visible=active.has(id);root.userData.pose=mode;return root};setPose(pose);roots.add(root);
  return {root,parts,setPose,dispose(){root.removeFromParent();roots.delete(root)}};
 },dispose(){if(retired)return;retired=true;for(const root of roots)root.removeFromParent();roots.clear();for(const g of geometries.flat())g.dispose();for(const m of materials)m.dispose();},get retired(){return retired}};
}
window.__SEAHawk_ASSET_A1__={decode:decodeSeahawkAssetA1,lease:createSeahawkAssetLeaseA1};
