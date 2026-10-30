// PRESENTATION_ONLY: the ownship's original wave-conforming foam shader and
// speed/history kernel, with owner geometry and independent bounded histories.
function createShipOceanEffectsF(view,presenter){
  const T=view.THREE,source=view.oceanFx;if(!source?.wakes?.[0]?.mesh)return null;
  const layer=new T.Group();layer.name='NAVAL_OCEAN_F:'+presenter.ownerId;view.worldRoot.add(layer);
  const material=source.wakes[0].mesh.material.clone();material.uniforms=source.uniforms;
  const make=(name,rows,cols)=>{
    const g=new T.BufferGeometry(),count=rows*cols,indices=[];
    g.setAttribute('position',new T.BufferAttribute(new Float32Array(count*3),3).setUsage(T.DynamicDrawUsage));
    g.setAttribute('uv',new T.BufferAttribute(new Float32Array(count*2),2));
    g.setAttribute('foam',new T.BufferAttribute(new Float32Array(count),1).setUsage(T.DynamicDrawUsage));
    for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){g.attributes.uv.setXY(r*cols+c,c/(cols-1),r);if(r<rows-1&&c<cols-1){const a=r*cols+c,b=a+cols;indices.push(a,b,a+1,b,b+1,a+1);}}
    g.setIndex(indices);g.setDrawRange(0,0);const mesh=new T.Mesh(g,material);mesh.name=name+':'+presenter.ownerId;mesh.frustumCulled=false;mesh.renderOrder=2;layer.add(mesh);return mesh;
  };
  const L=presenter.ownerRuntime.geometry.layout;
  presenter.oceanFx={layer,material,history:[],last:null,uniforms:source.uniforms,registration:{...L.wake},sternHalfWidthM:L.wake.sternHalf,
    wakes:[-1,0,1].map(side=>({side,mesh:make('SHIP_WAKE_'+side,256,9)})),bows:[-1,1].map(side=>({side,mesh:make('BOW_WAVE_'+side,49,9)}))};
  presenter.renderOriginWip14A=view.renderOriginWip14A;return presenter.oceanFx;
}
// @ORIGINAL_OWNER_OCEAN_KERNEL_F@
function syncShipOceanEffectsF(view,presenter,state){
  if(!presenter.oceanFx&&!createShipOceanEffectsF(view,presenter))return;
  // Only the owning view updates sea/fog/camera uniforms. All ship foam follows
  // that same ocean surface; this call updates only the owner's display meshes.
  syncOceanEffectsOwnerF.call(presenter,state);
}
function disposeShipOceanEffectsF(presenter){
  const fx=presenter.oceanFx;if(!fx?.layer)return;
  for(const q of [...fx.wakes,...fx.bows])q.mesh.geometry.dispose();
  fx.material.dispose();fx.layer.removeFromParent();fx.history.length=0;presenter.oceanFx=null;
}
function shipOceanEffectsAuditF(){
  const view=WIP148_EXTERNAL_3D;return {physicsFeedback:false,ownKernelUnchanged:true,ships:[...view.navalShipPresentersB.values()].map(v=>{
    const f=v.oceanFx;return {entityId:v.ownerId,profileId:v.ownerRuntime.profileId,registration:f?.registration??null,history:f?.history.map(q=>({...q}))??[],last:f?.last?{...f.last}:null,
      layer:f?.layer?.name??null,meshes:f?[...f.wakes,...f.bows].map(q=>({name:q.mesh.name,drawCount:q.mesh.geometry.drawRange.count,vertices:q.mesh.geometry.attributes.position.count,finite:q.mesh.geometry.attributes.position.array.every(Number.isFinite),peakFoam:Math.max(...q.mesh.geometry.attributes.foam.array),materialOwn:q.mesh.material===f.material,shaderShared:q.mesh.material.uniforms===view.oceanFx.uniforms})):[]};
  })};
}
