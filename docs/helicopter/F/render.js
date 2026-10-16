// Read-only helo render adapter. No simulation commands, integration or sensor updates.
const HELO_RIG_A=__HELO_RIG_JSON__;
let heloDecodedPromiseA=null;
function heloReadAssetA(){
  if(!heloDecodedPromiseA)heloDecodedPromiseA=(async()=>{const raw=Uint8Array.from(atob(document.getElementById('helo-render-a1').textContent.trim()),c=>c.charCodeAt(0)),bytes=new Uint8Array(await new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());return decodeSeahawkAssetA1(bytes);})();
  return heloDecodedPromiseA;
}
function heloModelA(view,h){
  const T=view.THREE,instance=view.heloLeaseA.build('deployed'),root=new T.Group(),normalizer=new T.Group();root.name='HELO:'+h.id;root.userData={presentationOnly:true,physicsFeedback:false,heloId:h.id};
  normalizer.scale.set(HELO_RIG_A.horizontalScale,HELO_RIG_A.verticalScale,HELO_RIG_A.horizontalScale);root.add(normalizer);normalizer.add(instance.root);instance.root.position.set(...HELO_RIG_A.origin.map(v=>-v));
  const sourceToBody=new T.Matrix4().makeScale(HELO_RIG_A.horizontalScale,HELO_RIG_A.verticalScale,HELO_RIG_A.horizontalScale).multiply(new T.Matrix4().makeTranslation(...HELO_RIG_A.origin.map(v=>-v))),ownedMaterials=[],rotors={},rotorById=new Map();
  // Rigid spin in METRIC body space, outside the nonuniform source normalizer.
  // Gearbox/pylon 12821 stays fixed; only the hub and its four blades rotate.
  for(const name of ['main','tail']){const config=HELO_RIG_A.rotors[name],spin=new T.Group(),center=new T.Vector3(...config.centerM),axis=new T.Vector3(...config.axis);spin.position.copy(center);root.add(spin);
    const inverse=new T.Matrix4().makeTranslation(...config.centerM.map(x=>-x)),blades=[];
    for(const id of config.movingPartIds){const g=instance.parts.get(id);spin.add(g);g.matrix.premultiply(sourceToBody).premultiply(inverse);rotorById.set(id,{spin,inverse});if(config.bladeIds.includes(id))g.traverse(o=>{if(o.isMesh){o.material=o.material.clone();o.material.transparent=true;ownedMaterials.push(o.material);blades.push({mesh:o,opacity:o.material.opacity});}});}
    const mat=new T.MeshStandardMaterial({color:0x6e777a,roughness:1,side:T.DoubleSide,transparent:true,opacity:0,depthWrite:false}),disk=new T.Mesh(view.heloRotorGeosB[name],mat);disk.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),axis);disk.visible=false;disk.name='HELO_'+name.toUpperCase()+'_BLUR';spin.add(disk);ownedMaterials.push(mat);rotors[name]={spin,axis,inverse,disk,blades,config};
  }
  for(const id of [12864,12866,12868,12870,12872,12874,12876,12878,12880])instance.parts.get(id).visible=false;
  const rigs=HELO_RIG_A.pairs.map(row=>{const opened=instance.parts.get(row.opened),folded=instance.parts.get(row.folded),rm=new T.Matrix4().set(row.rotation[0],row.rotation[3],row.rotation[6],0,row.rotation[1],row.rotation[4],row.rotation[7],0,row.rotation[2],row.rotation[5],row.rotation[8],0,0,0,0,1),q=new T.Quaternion().setFromRotationMatrix(rm),base=new T.Matrix4().fromArray(row.openedMatrix),pv=new T.Vector3(...row.pivot),shift=new T.Vector3(...row.shift),extra=row.sameGeometry?null:folded,fp=new T.Vector3(),fq=new T.Quaternion(),fs=new T.Vector3(),op=new T.Vector3(),oq=new T.Quaternion(),os=new T.Vector3();new T.Matrix4().fromArray(row.foldedMatrix).decompose(fp,fq,fs);base.decompose(op,oq,os);
    if(extra)for(const g of [opened,extra])g.traverse(o=>{if(o.isMesh){o.material=o.material.clone();o.material.transparent=true;ownedMaterials.push(o.material);}});
    return {row,opened,extra,q,base,pv,shift,matrix:new T.Matrix4(),rotation:new T.Quaternion(),translation:new T.Vector3(),rotatedPivot:new T.Vector3(),fp,fq,fs,op,oq,os,tempP:new T.Vector3(),tempQ:new T.Quaternion(),tempS:new T.Vector3()};});
  const proxy=new T.Mesh(view.heloProxyGeoA,view.heloProxyMatA);proxy.name='HELO_DISTANT_LOD';root.add(proxy);view.heloLayerA.add(root);
  return {root,instance,normalizer,proxy,rotors,spin:rotors.main.spin,tailSpin:rotors.tail.spin,sourceToBody,rotorById,rigs,poseMatrix:new T.Matrix4(),offsetMatrix:new T.Matrix4(),yawMatrix:new T.Matrix4(),pitchMatrix:new T.Matrix4(),bankMatrix:new T.Matrix4(),dispose(){instance.dispose();root.removeFromParent();for(const m of ownedMaterials)m.dispose();}};
}
function heloAnimateModelA(view,v,h){
  const T=view.THREE,parts=v.instance.parts;
  for(const r of v.rigs){const bladeIndex=[12746,12748,12750,12752].indexOf(r.row.opened),alpha=bladeIndex>=0?heloClampA(h.blades01*4-bladeIndex,0,1):h.tail01,fold=1-heloSmoothA(alpha);
    r.rotation.identity().slerp(r.q,fold);r.matrix.makeRotationFromQuaternion(r.rotation);r.translation.copy(r.pv).sub(r.rotatedPivot.copy(r.pv).applyMatrix4(r.matrix)).addScaledVector(r.shift,fold);r.matrix.setPosition(r.translation);r.opened.matrix.copy(r.matrix).multiply(r.base);
    const rotor=v.rotorById.get(r.row.opened);if(rotor)r.opened.matrix.premultiply(v.sourceToBody).premultiply(rotor.inverse);r.opened.matrixWorldNeedsUpdate=true;
    if(r.extra){const opacity=heloSmoothA(alpha);r.tempP.copy(r.fp).lerp(r.op,alpha);r.tempQ.copy(r.fq).slerp(r.oq,alpha);r.tempS.copy(r.fs).lerp(r.os,alpha);r.extra.matrix.compose(r.tempP,r.tempQ,r.tempS);r.extra.visible=alpha<1;r.opened.visible=alpha>0;r.extra.traverse(o=>{if(o.isMesh)o.material.opacity=1-opacity;});r.opened.traverse(o=>{if(o.isMesh)o.material.opacity=opacity;});}
  }
  parts.get(12767).visible=h.blades01===0;parts.get(12754).visible=h.blades01>0;
  v.rotors.main.spin.quaternion.setFromAxisAngle(v.rotors.main.axis,h.rotorAngleRad);v.rotors.tail.spin.quaternion.setFromAxisAngle(v.rotors.tail.axis,-h.rotorAngleRad*HELO_VALUES_A.tailRotorRatio);
  const blur=heloSmoothA((h.rotor01-.55)/.4);for(const r of Object.values(v.rotors)){r.disk.visible=blur>0;r.disk.material.opacity=HELO_VALUES_A.rotorDiskOpacity*blur;for(const b of r.blades)b.mesh.material.opacity=b.opacity*(1-.9*blur);}
  // The source poses contain TWO aft-wheel assemblies at different compression
  // heights. Keep the complete extended assembly 12704 and one upper link only.
  // Selecting a different authored pose alone would retain both rubber wheels.
  const moving=h.state==='LIFT_HOVER'||!h.onboard;for(const id of [12684,12689,12712])parts.get(id).visible=!moving;for(const id of [12722,12727,12719])parts.get(id).visible=moving;
  parts.get(12704).visible=true;parts.get(12708).visible=false;parts.get(12715).visible=false;
  const camera=view.camera.position,origin=view.renderOriginWip14A??{x:0,y:0,z:0},d=Math.hypot(h.positionM.x-camera.x-origin.x,h.positionM.z-camera.y-origin.y,h.positionM.y-camera.z-origin.z);v.normalizer.visible=d<HELO_VALUES_A.lodDistanceM||view.heloFocusA===h.id;for(const r of Object.values(v.rotors))r.spin.visible=v.normalizer.visible;v.proxy.visible=!v.normalizer.visible;
}
function heloBuildProxyA(view){
  const T=view.THREE;view.heloRotorGeosB={};for(const name of ['main','tail'])view.heloRotorGeosB[name]=new T.RingGeometry(name==='main'?.35:.1,HELO_RIG_A.rotors[name].radiusM,32);const items=[],body=new T.CylinderGeometry(.8,1,9,6);body.rotateZ(Math.PI/2);body.translate(-1,1.4,0);items.push(body);
  const tail=new T.CylinderGeometry(.14,.45,6,4);tail.rotateZ(Math.PI/2);tail.translate(5.7,2,0);items.push(tail);
  const fin=new T.BoxGeometry(.25,2.4,1);fin.translate(8.2,3,0);items.push(fin);
  const rotor=new T.CircleGeometry(HELO_VALUES_A.visualRotorDiameterM/2,12);rotor.rotateX(-Math.PI/2);rotor.translate(0,3.2,0);items.push(rotor);
  const positions=[],normals=[];for(const geo of items){const g=geo.index?geo.toNonIndexed():geo;positions.push(...g.attributes.position.array);normals.push(...g.attributes.normal.array);if(g!==geo)g.dispose();geo.dispose();}
  view.heloProxyGeoA=new T.BufferGeometry().setAttribute('position',new T.Float32BufferAttribute(positions,3)).setAttribute('normal',new T.Float32BufferAttribute(normals,3));view.heloProxyGeoA.computeBoundingSphere();view.heloProxyMatA=new T.MeshStandardMaterial({color:0x8c969b,roughness:.8,side:T.DoubleSide});
}
function heloCutDoorsA(view,root=view.shipRoot){
  if(view.heloDoorsA||!view._c5Asset||!root)return;const T=view.THREE,F=HELO_FACILITY_A,wallParts=['HULL_0','HULL_1','HULL_2','HULL_3','HULL_4','HULL_5','HULL_6','HULL_7','HANGAR','HANGAR_INNER','DECK_HATCHES'];let changed=0,removed=0,relocatedStairTriangles=0;
  // Subtract the two rectangles only from the measured rear-wall plane. Preserve
  // all other shell/interior vertices and interpolate every existing attribute.
  function split(poly,axis,bound,sign){const inside=[],outside=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length],da=(a.p[axis]-bound)*sign,db=(b.p[axis]-bound)*sign;
    (da>=0?inside:outside).push(a);if((da>=0)!==(db>=0)){const u=da/(da-db),p=a.p.map((v,j)=>v+(b.p[j]-v)*u),attrs={};for(const[k,v]of Object.entries(a.attrs))attrs[k]=v.map((x,j)=>x+(b.attrs[k][j]-x)*u);const v={p,attrs};inside.push(v);outside.push(v);}}
    return {inside,outside};}
  const doorPlane=y=>F.doorXAtFloor+(y-F.doorPlaneAnchorZM)*F.doorSlope;
  for(const key of wallParts){const part=view._c5Asset.parts.get(key);if(!part)continue;root.updateMatrixWorld(true);
    for(const mesh of part.children.filter(o=>o.isMesh)){
      const g=mesh.geometry,p=g.attributes.position,index=g.index,toRoot=root.matrixWorld.clone().invert().multiply(mesh.matrixWorld),fromRoot=toRoot.clone().invert(),point=new T.Vector3(),output={},attributes=Object.entries(g.attributes);for(const[k]of attributes)output[k]=[];
      let touched=false;const emit=poly=>{for(let j=1;j<poly.length-1;j++)for(const v of [poly[0],poly[j],poly[j+1]])for(const[k]of attributes)output[k].push(...v.attrs[k]);};
      for(let i=0,n=index?.count??p.count;i<n;i+=3){const poly=[];for(let j=0;j<3;j++){const vi=index?index.getX(i+j):i+j;point.fromBufferAttribute(p,vi).applyMatrix4(toRoot);const attrs={};for(const[k,a]of attributes)attrs[k]=Array.from(a.array.slice(vi*a.itemSize,(vi+1)*a.itemSize));poly.push({p:point.toArray(),attrs});}
        // The source port stair/handrail sits across the newly operational
        // doorway. Move only its complete stair/handrail assembly to the gunwale.
        // This happens before damage geometry capture; all other shell is kept.
        if(key==='HULL_1'&&poly.every(v=>v.p[0]>-52.6&&v.p[0]<-50.3&&v.p[1]>2.3&&v.p[1]<4.6&&v.p[2]>-4.9&&v.p[2]<-4.3)){
          for(const v of poly){v.p[2]-=3.5;point.set(...v.p).applyMatrix4(fromRoot);v.attrs.position=point.toArray();}touched=true;relocatedStairTriangles++;emit(poly);continue;
        }
        if(poly.some(v=>Math.abs(v.p[0]-doorPlane(v.p[1]))>.22)){emit(poly);continue;}let fragments=[poly];
        for(const sign of [-1,1]){const center=sign*F.bayOffsetM,next=[];for(const triangle of fragments){let remain=triangle;for(const[axis,bound,s]of [[1,F.doorBottomM,1],[1,F.doorTopM,-1],[2,center-F.doorHalfWidthM,1],[2,center+F.doorHalfWidthM,-1]]){if(remain.length<3)break;const q=split(remain,axis,bound,s);if(q.outside.length>=3)next.push(q.outside);remain=q.inside;}if(remain.length>=3){touched=true;removed++;}}fragments=next;}
        for(const polygon of fragments)emit(polygon);
      }
      if(touched){const next=new T.BufferGeometry();for(const[k,a]of attributes)next.setAttribute(k,new T.BufferAttribute(new a.array.constructor(output[k]),a.itemSize,a.normalized));next.computeBoundingBox();next.computeBoundingSphere();mesh.geometry=next;g.dispose();changed++;}
    }
  }
  const geo=new T.BoxGeometry(.075,1,1),mat=new T.MeshStandardMaterial({color:0x68787e,roughness:.88}),doors=[];
  for(let slot=0;slot<2;slot++){const mesh=new T.InstancedMesh(geo,mat,16);mesh.name='HELO_HANGAR_SHUTTER_'+slot;mesh.userData={presentationOnly:true,physicsFeedback:false,slot};root.add(mesh);mesh.frustumCulled=false;doors.push(mesh);}
  view.heloDoorsA={doors,geo,mat,changedMeshes:changed,removedPolygons:removed,relocatedStairTriangles,dummy:new T.Object3D()};
  heloSyncDoorsA(view,[0,0]);
}
function heloSyncDoorsA(view,values){
  const d=view.heloDoorsA;if(!d)return;const F=HELO_FACILITY_A,height=F.doorTopM-F.doorBottomM;
  for(let slot=0;slot<2;slot++){const open=values[slot]??0,mesh=d.doors[slot];let count=0;
    for(let i=0;i<16;i++){const bottom=F.doorBottomM+(i+open*16)*height/16,top=Math.min(F.doorTopM,bottom+height/16),visible=top-bottom-.012;if(visible<=0)continue;const y=(bottom+top)/2;d.dummy.position.set(F.doorXAtFloor+(y-F.doorPlaneAnchorZM)*F.doorSlope-.04,y,(slot===0?-1:1)*F.bayOffsetM);d.dummy.scale.set(1,visible,F.doorHalfWidthM*2);d.dummy.updateMatrix();mesh.setMatrixAt(count++,d.dummy.matrix);}
    mesh.count=count;mesh.visible=count>0;mesh.instanceMatrix.needsUpdate=true;
  }
}
function installHeloRendererA(view){
  view.heloVisualsA=new Map();view.heloFocusA=null;view.heloAssetLoadingA=false;view.heloRadarVisibleE=false;view.heloRadarResourcesE=null;
  // Partition clean source geometry before paint/damage capture it. Opening a
  // door never swaps/disposes a mesh that a live damage job still owns.
  const build=view.buildShip;view.buildShip=function(...args){const root=build.apply(this,args);if(root.userData.shipProfileId==='DDG_119_LATE_FLIGHT_IIA'&&!this.ownerRuntime)heloCutDoorsA(this,root);return root;};
  const fittings=view.syncShipFittings;view.syncShipFittings=function(st){fittings.call(this,st);const state=st.helicopters;heloSyncRadarVisualsE(this,state);if(!state?.supported)return;
    if(state.aircraft.length||state.doors.some(v=>v>0))heloCutDoorsA(this);heloSyncDoorsA(this,state.doors);
    if(!this.worldRoot)return;if(!this.heloLayerA){this.heloLayerA=new this.THREE.Group();this.heloLayerA.name='HELICOPTERS_A';this.worldRoot.add(this.heloLayerA);}
    if(state.aircraft.length&&!this.heloLeaseA&&!this.heloAssetLoadingA){this.heloAssetLoadingA=true;heloReadAssetA().then(source=>{this.heloLeaseA=createSeahawkAssetLeaseA1(this.THREE,source);heloBuildProxyA(this);this.heloAssetLoadingA=false;}).catch(e=>{this.heloAssetErrorA=String(e);this.heloAssetLoadingA=false;});}
    const wanted=new Set(state.aircraft.map(h=>h.id));for(const[id,v]of this.heloVisualsA)if(!wanted.has(id)){v.dispose();this.heloVisualsA.delete(id);}
    if(!wanted.size&&this.heloLeaseA){this.heloLeaseA.dispose();this.heloLeaseA=null;this.heloProxyGeoA.dispose();this.heloProxyMatA.dispose();for(const g of Object.values(this.heloRotorGeosB??{}))g.dispose();this.heloRotorGeosB=null;this.heloProxyGeoA=this.heloProxyMatA=null;}
    if(!this.heloLeaseA)return;
    for(const h of state.aircraft){let v=this.heloVisualsA.get(h.id);if(!v){v=heloModelA(this,h);this.heloVisualsA.set(h.id,v);}heloAnimateModelA(this,v,h);
      if(h.onboard){v.root.matrixAutoUpdate=false;v.offsetMatrix.makeTranslation(h.localM.x,h.localM.z,h.localM.y);v.yawMatrix.makeRotationY(-h.localYawRad);v.pitchMatrix.makeRotationZ(-h.pitchRad);v.bankMatrix.makeRotationX(-h.bankRad);v.poseMatrix.copy(this.shipRoot.matrix).multiply(v.offsetMatrix).multiply(v.yawMatrix).multiply(v.pitchMatrix).multiply(v.bankMatrix);v.root.matrix.copy(v.poseMatrix);v.root.matrixWorldNeedsUpdate=true;}
      // The source nose is -X; pitch/roll signs reverse relative to body +X.
      else{v.root.matrixAutoUpdate=true;v.root.position.set(h.positionM.x,h.positionM.z,h.positionM.y);v.root.rotation.set(0,Math.PI-h.headingRad,0);v.root.rotateZ(-h.pitchRad);v.root.rotateX(-h.bankRad);}
    }
  };
  const camera=view.syncCamera;view.syncCamera=function(...args){const v=this.heloVisualsA.get(this.heloFocusA);if(!v)return camera.apply(this,args);const T=this.THREE,o=this.orbit,target=v.root.getWorldPosition(new T.Vector3());target.y+=2;const d=o.distance;this.camera.position.set(target.x+Math.cos(o.yaw)*Math.cos(o.pitch)*d,target.y+Math.sin(o.pitch)*d,target.z+Math.sin(o.yaw)*Math.cos(o.pitch)*d);this.camera.lookAt(target);};
  const reset=view.resetCamera;view.resetCamera=function(...args){this.heloFocusA=null;return reset.apply(this,args);};
  const epoch=view.syncWorldEpochWip14A;view.syncWorldEpochWip14A=function(st){const e=st.sim?.presentationEpoch??0;if(this._heloEpochA!==e){heloDisposeRadarVisualsE(this);for(const v of this.heloVisualsA.values())v.dispose();this.heloVisualsA.clear();if(this._heloEpochA!==undefined)this.heloFocusA=null;this._heloEpochA=e;}return epoch.call(this,st);};
}
// Presentation constants only. Neither visualization visibility nor geometry
// feeds back into antenna phase, emission, probability, plots, or links.
const HELO_RADAR_VIEW_SPEC_E=Object.freeze(Object.fromEntries(Object.entries({
 circleSegments:96,seaLiftM:1,ringOpacity:.5,horizonOpacity:.25,sweepOpacity:.18,transitionOpacity:.18,trailOpacity:.045,elevationOpacity:.10,dashUnit:.025,gapUnit:.018,
 longTrailDeg:8,shortTrailDeg:54,periTrailDeg:54,sectorSegments:12,h1Color:0x7ae6da,h2Color:0x89bfff
}).map(([k,value])=>[k,{value,source:'SIM_TUNED',reference:'GENERIC_RADAR_PRINCIPLE',presentationOnly:true}])));
const HELO_RADAR_VIEW_VALUES_E=Object.freeze(Object.fromEntries(Object.entries(HELO_RADAR_VIEW_SPEC_E).map(([k,v])=>[k,v.value])));
function heloDisposeRadarVisualsE(view){const r=view.heloRadarResourcesE;if(!r)return;for(const v of r.visuals.values())v.root.removeFromParent();for(const g of r.geometries)g.dispose();for(const m of r.materials)m.dispose();r.visuals.clear();view.heloRadarResourcesE=null;}
function apsSectorGeometryViewF(T,segments){const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(new Float32Array(segments*18),3));return g;}
function apsFillSectorViewF(geometry,inner,outer,start,end,segments){const a=geometry.attributes.position.array;let at=0;for(let i=0;i<segments;i++){const x=start+(end-start)*i/segments,y=start+(end-start)*(i+1)/segments;for(const[r,phi]of [[inner,x],[outer,x],[outer,y],[inner,x],[outer,y],[inner,y]]){a[at++]=r*Math.cos(phi);a[at++]=0;a[at++]=r*Math.sin(phi);}}geometry.attributes.position.needsUpdate=true;geometry.computeBoundingSphere();}
function heloSyncRadarVisualsE(view,state){const aircraft=state?.supported?state.aircraft??[]:[];if(!aircraft.length||!view.worldRoot){heloDisposeRadarVisualsE(view);return;}if(!view.heloRadarVisibleE){if(view.heloRadarResourcesE)for(const v of view.heloRadarResourcesE.visuals.values())v.root.visible=false;return;}
 const T=view.THREE,C=HELO_RADAR_VIEW_VALUES_E;let resource=view.heloRadarResourcesE;
 if(!resource){const points=[],distances=[];for(let i=0;i<C.circleSegments;i++){const phi=i/C.circleSegments*2*Math.PI;points.push(Math.cos(phi),0,Math.sin(phi));distances.push(i*2*Math.sin(Math.PI/C.circleSegments));}const circle=new T.BufferGeometry().setAttribute('position',new T.Float32BufferAttribute(points,3)).setAttribute('lineDistance',new T.Float32BufferAttribute(distances,1));resource=view.heloRadarResourcesE={geometries:[circle],materials:[],visuals:new Map()};}
 const wanted=new Set();for(const h of aircraft){wanted.add(h.id);const radar=h.radar;let v=resource.visuals.get(h.id);
 if(!v){const root=new T.Group(),color=h.slot===0?C.h1Color:C.h2Color,solid=new T.LineBasicMaterial({color,transparent:true,opacity:C.ringOpacity,depthWrite:false,fog:false}),dashed=new T.LineDashedMaterial({color,transparent:true,opacity:C.horizonOpacity,dashSize:C.dashUnit,gapSize:C.gapUnit,depthWrite:false,fog:false}),beamMaterial=new T.MeshBasicMaterial({color,transparent:true,opacity:C.sweepOpacity,side:T.DoubleSide,depthWrite:false,fog:false}),trailMaterial=new T.MeshBasicMaterial({color,transparent:true,opacity:C.trailOpacity,side:T.DoubleSide,depthWrite:false,fog:false}),curtainMaterial=new T.MeshBasicMaterial({color,transparent:true,opacity:C.elevationOpacity,side:T.DoubleSide,depthWrite:false,fog:false}),instrument=new T.LineLoop(resource.geometries[0],solid),horizon=new T.LineLoop(resource.geometries[0],dashed),minimum=new T.LineLoop(resource.geometries[0],solid),blind=new T.LineLoop(resource.geometries[0],solid),beamGeo=apsSectorGeometryViewF(T,C.sectorSegments),trailGeo=apsSectorGeometryViewF(T,C.sectorSegments),curtainGeo=apsSectorGeometryViewF(T,1),beam=new T.Mesh(beamGeo,beamMaterial),trail=new T.Mesh(trailGeo,trailMaterial),curtain=new T.Mesh(curtainGeo,curtainMaterial);
 root.name='HELO_RADAR_F:'+h.id;root.userData={presentationOnly:true,physicsFeedback:false,heloId:h.id};root.add(instrument,horizon,minimum,blind,beam,trail,curtain);view.worldRoot.add(root);resource.geometries.push(beamGeo,trailGeo,curtainGeo);resource.materials.push(solid,dashed,beamMaterial,trailMaterial,curtainMaterial);v={root,instrument,horizon,minimum,blind,beam,trail,curtain,geometries:[beamGeo,trailGeo,curtainGeo],materials:[solid,dashed,beamMaterial,trailMaterial,curtainMaterial]};resource.visuals.set(h.id,v);}
 v.root.visible=!!radar?.emitting&&!h.onboard&&radar.mode!=='STBY';if(!v.root.visible)continue;v.root.position.set(h.positionM.x,C.seaLiftM,h.positionM.y);const transitioning=radar.status==='TRANSITION',alpha=transitioning?C.transitionOpacity:1;v.materials[0].opacity=C.ringOpacity*alpha;v.materials[1].opacity=C.horizonOpacity*alpha;
 for(const[line,radius]of [[v.instrument,radar.instrumentM],[v.horizon,radar.horizonM],[v.minimum,radar.minimumM],[v.blind,radar.blindM]]){line.scale.setScalar(Math.max(0,radius));line.visible=radius>0&&(line!==v.minimum||radar.mode==='PERI');}
 v.beam.visible=v.trail.visible=v.curtain.visible=!transitioning;const inner=Math.max(radar.blindM,radar.minimumM),outer=Math.max(inner,radar.effectiveM),half=radar.beamWidthRad/2,trail=apsRadF(radar.mode==='LONG'?C.longTrailDeg:radar.mode==='SHORT'?C.shortTrailDeg:C.periTrailDeg);apsFillSectorViewF(v.geometries[0],inner,outer,-half,half,C.sectorSegments);apsFillSectorViewF(v.geometries[1],inner,outer,-trail-half,-half,C.sectorSegments);
 const ca=v.geometries[2].attributes.position.array;ca.set([0,h.positionM.z-C.seaLiftM,0,inner,0,0,outer,0,0,0,h.positionM.z-C.seaLiftM,0,outer,0,0,inner,0,0]);v.geometries[2].attributes.position.needsUpdate=true;v.geometries[2].computeBoundingSphere();for(const mesh of [v.beam,v.trail,v.curtain])mesh.rotation.y=-radar.azimuthRad;
 v.root.userData.mode=radar.mode;v.root.userData.status=radar.status;v.root.userData.azimuthRad=radar.azimuthRad;v.root.userData.instrumentM=radar.instrumentM;v.root.userData.horizonM=radar.horizonM;v.root.userData.blindM=radar.blindM;
 }
 for(const[id,v]of resource.visuals)if(!wanted.has(id)){v.root.removeFromParent();for(const g of v.geometries){g.dispose();resource.geometries.splice(resource.geometries.indexOf(g),1);}for(const m of v.materials){m.dispose();resource.materials.splice(resource.materials.indexOf(m),1);}resource.visuals.delete(id);}
}
