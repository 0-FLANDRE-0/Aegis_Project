// Read-only helo render adapter. No simulation commands, integration or sensors.
const HELO_RIG_A=__HELO_RIG_JSON__;
let heloDecodedPromiseA=null;
function heloReadAssetA(){
  if(!heloDecodedPromiseA)heloDecodedPromiseA=(async()=>{const raw=Uint8Array.from(atob(document.getElementById('helo-render-a1').textContent.trim()),c=>c.charCodeAt(0)),bytes=new Uint8Array(await new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());return decodeSeahawkAssetA1(bytes);})();
  return heloDecodedPromiseA;
}
function heloModelA(view,h){
  const T=view.THREE,lease=view.heloLeaseA,instance=lease.build('deployed'),root=new T.Group(),normalizer=new T.Group();root.name='HELO:'+h.id;root.userData={presentationOnly:true,physicsFeedback:false,heloId:h.id};normalizer.scale.set(HELO_RIG_A.horizontalScale,HELO_RIG_A.verticalScale,HELO_RIG_A.horizontalScale);root.add(normalizer);normalizer.add(instance.root);instance.root.position.set(...HELO_RIG_A.origin.map(v=>-v));
  const spin=new T.Group(),c=HELO_RIG_A.rotorCenter;spin.position.set(...c);instance.root.add(spin);
  const mainIds=[12746,12748,12750,12752,12754,12767],rigs=HELO_RIG_A.pairs.map(row=>{
    const opened=instance.parts.get(row.opened),folded=instance.parts.get(row.folded),rm=new T.Matrix4().set(row.rotation[0],row.rotation[3],row.rotation[6],0,row.rotation[1],row.rotation[4],row.rotation[7],0,row.rotation[2],row.rotation[5],row.rotation[8],0,0,0,0,1),q=new T.Quaternion().setFromRotationMatrix(rm),base=new T.Matrix4().fromArray(row.openedMatrix),pv=new T.Vector3(...row.pivot),shift=new T.Vector3(...row.shift);
    const extra=row.sameGeometry?null:folded,fp=new T.Vector3(),fq=new T.Quaternion(),fs=new T.Vector3(),op=new T.Vector3(),oq=new T.Quaternion(),os=new T.Vector3();new T.Matrix4().fromArray(row.foldedMatrix).decompose(fp,fq,fs);base.decompose(op,oq,os);return {row,opened,extra,q,base,pv,shift,matrix:new T.Matrix4(),rotation:new T.Quaternion(),translation:new T.Vector3(),rotatedPivot:new T.Vector3(),fp,fq,fs,op,oq,os,tempP:new T.Vector3(),tempQ:new T.Quaternion(),tempS:new T.Vector3()};
  });
  for(const id of mainIds){const g=instance.parts.get(id);if(g){spin.add(g);g.matrix.premultiply(new T.Matrix4().makeTranslation(-c[0],-c[1],-c[2]));}}
  const tailSpin=new T.Group(),tc=HELO_RIG_A.tailRotorCenter;tailSpin.position.set(...tc);instance.root.add(tailSpin);
  for(const id of [12821,12823,12825,12828,12831,12834]){const g=instance.parts.get(id);if(g){tailSpin.add(g);g.matrix.premultiply(new T.Matrix4().makeTranslation(-tc[0],-tc[1],-tc[2]));}}
  // Existing authored blur planes. Slow blade geometry stays visible during run-up.
  const blurIds=[12864,12866,12868,12870,12872,12874,12876,12878,12880],blur=[];
  for(const id of blurIds){const g=instance.parts.get(id);if(!g)continue;const parent=id>=12874?spin:tailSpin,center=id>=12874?c:tc;parent.add(g);g.matrix.premultiply(new T.Matrix4().makeTranslation(...center.map(x=>-x)));const clones=[];g.traverse(o=>{if(o.isMesh){o.material=o.material.clone();o.material.transparent=true;o.material.depthWrite=false;clones.push(o.material);}});blur.push({id,g,materials:clones,opacity:clones.map(m=>m.opacity)});}
  // Four tiny horizontal-tail variants have different buffers; preserve both
  // while cross-fading their reconstructed joint transforms through deployment.
  const fadeMaterials=[];for(const r of rigs)if(r.extra){for(const g of [r.opened,r.extra])g.traverse(o=>{if(o.isMesh){o.material=o.material.clone();o.material.transparent=true;fadeMaterials.push(o.material);}});}
  const proxy=new T.Mesh(view.heloProxyGeoA,view.heloProxyMatA);proxy.name='HELO_DISTANT_LOD';root.add(proxy);view.heloLayerA.add(root);return {root,instance,normalizer,proxy,spin,tailSpin,rigs,blur,fadeMaterials,inverseSpin:new T.Matrix4().makeTranslation(...c.map(x=>-x)),inverseTail:new T.Matrix4().makeTranslation(...tc.map(x=>-x)),poseMatrix:new T.Matrix4(),offsetMatrix:new T.Matrix4(),
    dispose(){instance.dispose();root.removeFromParent();for(const r of blur)for(const m of r.materials)m.dispose();for(const m of fadeMaterials)m.dispose();}};
}
function heloAnimateModelA(view,v,h){
  const T=view.THREE,parts=v.instance.parts,inverseSpin=v.inverseSpin,inverseTail=v.inverseTail;
  for(const r of v.rigs){const alpha=r.row.opened<12800?heloClampA(h.blades01*4-[12746,12748,12750,12752].indexOf(r.row.opened),0,1):h.tail01,
    fold=1-heloSmoothA(alpha);r.rotation.identity().slerp(r.q,fold);r.matrix.makeRotationFromQuaternion(r.rotation);
    r.translation.copy(r.pv).sub(r.rotatedPivot.copy(r.pv).applyMatrix4(r.matrix)).addScaledVector(r.shift,fold);r.matrix.setPosition(r.translation);r.opened.matrix.copy(r.matrix).multiply(r.base);
    if(r.row.opened<12800)r.opened.matrix.premultiply(inverseSpin);else if(r.opened.parent===v.tailSpin)r.opened.matrix.premultiply(inverseTail);
    r.opened.matrixWorldNeedsUpdate=true;
    if(r.extra){const opacity=heloSmoothA(alpha);r.tempP.copy(r.fp).lerp(r.op,alpha);r.tempQ.copy(r.fq).slerp(r.oq,alpha);r.tempS.copy(r.fs).lerp(r.os,alpha);r.extra.matrix.compose(r.tempP,r.tempQ,r.tempS);r.extra.visible=alpha<1;r.opened.visible=alpha>0;r.extra.traverse(o=>{if(o.isMesh)o.material.opacity=1-opacity;});r.opened.traverse(o=>{if(o.isMesh)o.material.opacity=opacity;});}
  }
  parts.get(12767).visible=h.blades01===0;parts.get(12754).visible=h.blades01>0;
  v.spin.rotation.y=h.rotorAngleRad;v.tailSpin.rotation.z=-h.rotorAngleRad*4.6;
  const moving=h.state==='LIFT_HOVER'||!h.onboard;for(const id of [12684,12689])parts.get(id).visible=!moving;for(const id of [12722,12727])parts.get(id).visible=moving;
  const blur=heloSmoothA((h.rotor01-.55)/.4);for(const b of v.blur){b.g.visible=blur>0;for(let i=0;i<b.materials.length;i++)b.materials[i].opacity=b.opacity[i]*blur;}
  // Hero mesh stays near the camera. Distant aircraft use a shared simple silhouette.
  const camera=view.camera.position,origin=view.renderOriginWip14A??{x:0,y:0,z:0},d=Math.hypot(h.positionM.x-camera.x-origin.x,h.positionM.z-camera.y-origin.y,h.positionM.y-camera.z-origin.z);
  v.normalizer.visible=d<1800||view.heloFocusA===h.id;v.proxy.visible=!v.normalizer.visible;
}
function heloBuildProxyA(view){
  const T=view.THREE,items=[],body=new T.CylinderGeometry(.8,1,9,6);body.rotateZ(Math.PI/2);body.translate(-1,1.4,0);items.push(body);
  const tail=new T.CylinderGeometry(.14,.45,6,4);tail.rotateZ(Math.PI/2);tail.translate(5.7,2,0);items.push(tail);
  const fin=new T.BoxGeometry(.25,2.4,1);fin.translate(8.2,3,0);items.push(fin);
  const rotor=new T.CircleGeometry(HELO_VALUES_A.visualRotorDiameterM/2,12);rotor.rotateX(-Math.PI/2);rotor.translate(0,3.2,0);items.push(rotor);
  const positions=[],normals=[];for(const geo of items){const g=geo.index?geo.toNonIndexed():geo;positions.push(...g.attributes.position.array);normals.push(...g.attributes.normal.array);if(g!==geo)g.dispose();geo.dispose();}
  view.heloProxyGeoA=new T.BufferGeometry().setAttribute('position',new T.Float32BufferAttribute(positions,3)).setAttribute('normal',new T.Float32BufferAttribute(normals,3));view.heloProxyGeoA.computeBoundingSphere();view.heloProxyMatA=new T.MeshStandardMaterial({color:0x8c969b,roughness:.8,side:T.DoubleSide});
}
function heloCutDoorsA(view,root=view.shipRoot){
  if(view.heloDoorsA||!view._c5Asset||!root)return;const T=view.THREE,F=HELO_FACILITY_A,wallParts=['HANGAR','HANGAR_INNER','DECK_HATCHES'];let changed=0,removed=0;
  // Subtract the two rectangles only from the measured rear-wall plane. Preserve
  // all other shell/interior vertices and interpolate every existing attribute.
  function split(poly,axis,bound,sign){const inside=[],outside=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],da=(a.p[axis]-bound)*sign,db=(b.p[axis]-bound)*sign;
    (da>=0?inside:outside).push(a);if((da>=0)!==(db>=0)){const u=da/(da-db),p=a.p.map((v,j)=>v+(b.p[j]-v)*u),attrs={};for(const[k,v]of Object.entries(a.attrs))attrs[k]=v.map((x,j)=>x+(b.attrs[k][j]-x)*u);const v={p,attrs};inside.push(v);outside.push(v);}}
    return {inside,outside};}
  const doorPlane=y=>F.doorXAtFloor+(y-F.doorBottomM)*F.doorSlope;
  for(const key of wallParts){const part=view._c5Asset.parts.get(key);if(!part)continue;root.updateMatrixWorld(true);
    for(const mesh of part.children.filter(o=>o.isMesh)){
      const g=mesh.geometry,p=g.attributes.position,index=g.index,toRoot=root.matrixWorld.clone().invert().multiply(mesh.matrixWorld),point=new T.Vector3(),output={},attributes=Object.entries(g.attributes);for(const[k]of attributes)output[k]=[];
      let touched=false;const emit=poly=>{for(let j=1;j<poly.length-1;j++)for(const v of [poly[0],poly[j],poly[j+1]])for(const[k]of attributes)output[k].push(...v.attrs[k]);};
      for(let i=0,n=index?.count??p.count;i<n;i+=3){const poly=[];for(let j=0;j<3;j++){const vi=index?index.getX(i+j):i+j;point.fromBufferAttribute(p,vi).applyMatrix4(toRoot);const attrs={};for(const[k,a]of attributes)attrs[k]=Array.from(a.array.slice(vi*a.itemSize,(vi+1)*a.itemSize));poly.push({p:point.toArray(),attrs});}
        if(poly.some(v=>Math.abs(v.p[0]-doorPlane(v.p[1]))>.22)){emit(poly);continue;}let fragments=[poly];
        for(const sign of [-1,1]){const center=sign*F.bayOffsetM,next=[];for(const triangle of fragments){let remain=triangle;for(const[axis,bound,s]of [[1,F.doorBottomM,1],[1,F.doorTopM,-1],[2,center-F.doorHalfWidthM,1],[2,center+F.doorHalfWidthM,-1]]){if(remain.length<3)break;const q=split(remain,axis,bound,s);if(q.outside.length>=3)next.push(q.outside);remain=q.inside;}if(remain.length>=3){touched=true;removed++;}}fragments=next;}
        for(const polygon of fragments)emit(polygon);
      }
      if(touched){const next=new T.BufferGeometry();for(const[k,a]of attributes)next.setAttribute(k,new T.BufferAttribute(new a.array.constructor(output[k]),a.itemSize,a.normalized));next.computeBoundingBox();next.computeBoundingSphere();mesh.geometry=next;g.dispose();changed++;}
    }
  }
  const geo=new T.BoxGeometry(.075,1,1),mat=new T.MeshStandardMaterial({color:0x68787e,roughness:.88}),doors=[];
  for(let slot=0;slot<2;slot++){const mesh=new T.InstancedMesh(geo,mat,16);mesh.name='HELO_HANGAR_SHUTTER_'+slot;mesh.userData={presentationOnly:true,physicsFeedback:false,slot};root.add(mesh);mesh.frustumCulled=false;doors.push(mesh);}
  view.heloDoorsA={doors,geo,mat,changedMeshes:changed,removedPolygons:removed,dummy:new T.Object3D()};
  heloSyncDoorsA(view,[0,0]);
}
function heloSyncDoorsA(view,values){
  const d=view.heloDoorsA;if(!d)return;const F=HELO_FACILITY_A,height=F.doorTopM-F.doorBottomM;
  for(let slot=0;slot<2;slot++){const open=values[slot]??0,mesh=d.doors[slot];let count=0;
    for(let i=0;i<16;i++){const bottom=F.doorBottomM+(i+open*16)*height/16,top=Math.min(F.doorTopM,bottom+height/16),visible=top-bottom-.012;if(visible<=0)continue;const y=(bottom+top)/2;d.dummy.position.set(F.doorXAtFloor+(y-F.doorBottomM)*F.doorSlope-.04,y,(slot===0?-1:1)*F.bayOffsetM);d.dummy.scale.set(1,visible,F.doorHalfWidthM*2);d.dummy.updateMatrix();mesh.setMatrixAt(count++,d.dummy.matrix);}
    mesh.count=count;mesh.visible=count>0;mesh.instanceMatrix.needsUpdate=true;
  }
}
function installHeloRendererA(view){
  view.heloVisualsA=new Map();view.heloFocusA=null;view.heloAssetLoadingA=false;
  // Partition clean source geometry before paint/damage capture it. Opening a
  // door never swaps/disposes a mesh that a live damage job still owns.
  const build=view.buildShip;view.buildShip=function(...args){const root=build.apply(this,args);if(root.userData.shipProfileId==='DDG_119_LATE_FLIGHT_IIA'&&!this.ownerRuntime)heloCutDoorsA(this,root);return root;};
  const fittings=view.syncShipFittings;view.syncShipFittings=function(st){fittings.call(this,st);const state=st.helicopters;if(!state?.supported)return;
    if(state.aircraft.length||state.doors.some(v=>v>0))heloCutDoorsA(this);heloSyncDoorsA(this,state.doors);
    if(!this.worldRoot)return;if(!this.heloLayerA){this.heloLayerA=new this.THREE.Group();this.heloLayerA.name='HELICOPTERS_A';this.worldRoot.add(this.heloLayerA);}
    if(state.aircraft.length&&!this.heloLeaseA&&!this.heloAssetLoadingA){this.heloAssetLoadingA=true;heloReadAssetA().then(source=>{this.heloLeaseA=createSeahawkAssetLeaseA1(this.THREE,source);heloBuildProxyA(this);this.heloAssetLoadingA=false;}).catch(e=>{this.heloAssetErrorA=String(e);this.heloAssetLoadingA=false;});}
    const wanted=new Set(state.aircraft.map(h=>h.id));for(const[id,v]of this.heloVisualsA)if(!wanted.has(id)){v.dispose();this.heloVisualsA.delete(id);}
    if(!wanted.size&&this.heloLeaseA){this.heloLeaseA.dispose();this.heloLeaseA=null;this.heloProxyGeoA.dispose();this.heloProxyMatA.dispose();this.heloProxyGeoA=this.heloProxyMatA=null;}
    if(!this.heloLeaseA)return;
    for(const h of state.aircraft){let v=this.heloVisualsA.get(h.id);if(!v){v=heloModelA(this,h);this.heloVisualsA.set(h.id,v);}heloAnimateModelA(this,v,h);
      if(h.onboard){v.root.matrixAutoUpdate=false;v.offsetMatrix.makeTranslation(h.localM.x,h.localM.z,h.localM.y);v.poseMatrix.copy(this.shipRoot.matrix).multiply(v.offsetMatrix);v.root.matrix.copy(v.poseMatrix);v.root.matrixWorldNeedsUpdate=true;}
      // The source nose is -X; pitch/roll signs reverse relative to body +X.
      else{v.root.matrixAutoUpdate=true;v.root.position.set(h.positionM.x,h.positionM.z,h.positionM.y);v.root.rotation.set(0,Math.PI-h.headingRad,0);v.root.rotateZ(-h.pitchRad);v.root.rotateX(-h.bankRad);}
    }
  };
  const camera=view.syncCamera;view.syncCamera=function(...args){const v=this.heloVisualsA.get(this.heloFocusA);if(!v)return camera.apply(this,args);const T=this.THREE,o=this.orbit,target=v.root.getWorldPosition(new T.Vector3());target.y+=2;const d=o.distance;this.camera.position.set(target.x+Math.cos(o.yaw)*Math.cos(o.pitch)*d,target.y+Math.sin(o.pitch)*d,target.z+Math.sin(o.yaw)*Math.cos(o.pitch)*d);this.camera.lookAt(target);};
  const reset=view.resetCamera;view.resetCamera=function(...args){this.heloFocusA=null;return reset.apply(this,args);};
  const epoch=view.syncWorldEpochWip14A;view.syncWorldEpochWip14A=function(st){const e=st.sim?.presentationEpoch??0;if(this._heloEpochA!==e){for(const v of this.heloVisualsA.values())v.dispose();this.heloVisualsA.clear();if(this._heloEpochA!==undefined)this.heloFocusA=null;this._heloEpochA=e;}return epoch.call(this,st);};
}
