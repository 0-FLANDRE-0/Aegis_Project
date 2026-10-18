// PRESENTATION_ONLY. Original v9.1 buffers/hierarchy, all joints parked at rest.
// Authored Y (waterline) drives paint; world heave/heel never moves the boot band.
function installSovRendererA(view,profile){
 view.buildShip=function(){
  const T=this.THREE,meta=SOV_META_A,buf=SOV_BUFFER_A,PT=meta.paint,root=new T.Group(),nodes=new Map(),ownedTextures=new Set(),materials=new Map();
  root.name=profile.renderer.rootName;Object.assign(root.userData,{shipProfileId:profile.id,shipProfileRevision:profile.revision,physicsFeedback:false,sourceSha256:SOV_REG_A.sourceSha256,attribution:SOV_REG_A.attribution});
  const maps=SOV_TEXTURES_A.map(t=>{const q=new T.TextureLoader().load(t.uri);q.flipY=false;q.colorSpace=T.SRGBColorSpace;q.wrapS=q.wrapT=T.RepeatWrapping;q.anisotropy=Math.min(4,this.renderer.capabilities.getMaxAnisotropy());ownedTextures.add(q);return q;});
  function matFor(i,col){
   const key=i+':'+!!col;if(materials.has(key))return materials.get(key);
   const m=meta.materials[i],t=m.tex!=null?SOV_TEXTURES_A[m.tex]:null,bronze=m.name==='34_0',mat=new T.MeshStandardMaterial({side:T.DoubleSide,roughness:bronze?.45:.8,metalness:bronze?.55:.03,vertexColors:!!col,color:t?0xffffff:new T.Color(bronze?PT.bronze:PT.grey)});
   if(t){mat.map=maps[m.tex];if(t.alpha)mat.alphaTest=.5;}
   mat.onBeforeCompile=sh=>{
    Object.assign(sh.uniforms,{wlLo:{value:PT.lo},wlHi:{value:PT.hi},wlBoot:{value:new T.Color(PT.boot)},wlUnder:{value:new T.Color(PT.under)},monoCol:{value:new T.Color(PT.grey)},gunCol:{value:new T.Color(PT.gunmetal)}});
    sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nattribute vec3 sovPaint; varying float vGrad; varying float vFlags; varying float vSourceY;').replace('#include <begin_vertex>','#include <begin_vertex>\nvFlags=sovPaint.x;vGrad=sovPaint.y;vSourceY=sovPaint.z;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nuniform float wlLo,wlHi;uniform vec3 wlBoot,wlUnder,monoCol,gunCol;varying float vGrad;varying float vFlags;varying float vSourceY;').replace('#include <color_fragment>',`#include <color_fragment>
     bool fMono=mod(vFlags,2.)>.5,fHull=mod(floor(vFlags/2.+.01),2.)>.5,fFlat=mod(floor(vFlags/4.+.01),2.)>.5,fDark=mod(floor(vFlags/8.+.01),2.)>.5;
     if(vFlags>15.5){float g=pow(clamp(vGrad,0.,1.),1.35);diffuseColor.rgb=mix(monoCol*.93,gunCol*1.05,smoothstep(.05,1.,g));}
     else if(fDark){float l=dot(diffuseColor.rgb,vec3(.2126,.7152,.0722));diffuseColor.rgb=gunCol*clamp(.8+l*.6,.8,1.15);}
     else if(fFlat)diffuseColor.rgb=monoCol*.97;
     else if(fMono){float l=dot(diffuseColor.rgb,vec3(.2126,.7152,.0722));diffuseColor.rgb=monoCol*clamp(l/max(dot(monoCol,vec3(.2126,.7152,.0722)),.01),.22,1.25);}
     if(fHull){if(vSourceY<wlLo)diffuseColor.rgb=wlUnder;else if(vSourceY<wlHi)diffuseColor.rgb=wlBoot;else diffuseColor.rgb*=.86;}`);
   };mat.customProgramCacheKey=()=>'SOV_PAINT_A_'+key;materials.set(key,mat);return mat;
  }
  function mesh(m,name,cat){
   const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(new Float32Array(new Float32Array(buf,m.pos[0],m.pos[1])),3));g.setAttribute('normal',new T.BufferAttribute(new Int8Array(new Int8Array(buf,m.nor[0],m.nor[1])),3,true));g.setAttribute('flags',new T.BufferAttribute(new Uint8Array(buf.slice(m.flags[0],m.flags[0]+m.flags[1])),1));g.setAttribute('grad',new T.BufferAttribute(m.grad?new Uint8Array(buf.slice(m.grad[0],m.grad[0]+m.grad[1])):new Uint8Array(m.pos[1]/3),1,true));
   const paint=new Float32Array(m.pos[1]);for(let i=0;i<m.pos[1]/3;i++){paint[i*3]=g.attributes.flags.getX(i);paint[i*3+1]=g.attributes.grad.getX(i);paint[i*3+2]=g.attributes.position.getY(i);}g.setAttribute('sovPaint',new T.BufferAttribute(paint,3));
   if(m.uv)g.setAttribute('uv',new T.BufferAttribute(new Float32Array(new Float32Array(buf,m.uv[0],m.uv[1])),2));if(m.col)g.setAttribute('color',new T.BufferAttribute(new Uint8Array(buf.slice(m.col[0],m.col[0]+m.col[1])),3,true));
   const ids=m.i32?new Uint32Array(new Uint32Array(buf,m.idx[0],m.idx[1])):new Uint16Array(new Uint16Array(buf,m.idx[0],m.idx[1]));g.setIndex(new T.BufferAttribute(ids,1));g.computeBoundingBox();g.computeBoundingSphere();
   const o=new T.Mesh(g,matFor(m.mat,m.col));o.name=name;o.castShadow=o.receiveShadow=true;o.userData={sourceSovA:true,partId:name,category:cat,physicsFeedback:false,skipLegacyLargestIslandPrune:true,interiorEnvelopeV9:['hull','structure'].includes(cat)};return o;
  }
  for(const s of meta.statics)for(let i=0;i<s.meshes.length;i++)root.add(mesh(s.meshes[i],'SOV_'+s.cat+'_'+i,s.cat));
  function node(rec,parent,cat){const g=new T.Group();g.name=rec.name;g.position.fromArray(rec.local);g.userData={parked:true,sourceAxis:rec.axis};parent.add(g);nodes.set(g.name,g);for(let i=0;i<rec.meshes.length;i++)g.add(mesh(rec.meshes[i],rec.name+'_'+i,cat));for(const c of rec.children)node(c,g,cat);}
  for(const a of meta.assemblies)node(a.root,root,a.cat);
  this._sovAssetA={root,nodes,sourceTriangles:SOV_REG_A.sourceTriangles,ownedTextures};this.vlsLids=new Map();this.spgMounts=new Map();this.mainMastV12=new T.Group();root.add(this.mainMastV12);this.phalanxYawGroup=this.phalanxPitchGroup=this.seaRamYawGroup=this.seaRamPitchGroup=null;
  this.shipRoot=root;this.scene.add(root);root.updateWorldMatrix(true,true);return root;
 };
 view.syncShipFittings=function(){};view.syncMainGunVisualWip13B1=function(){};view.syncCiwsVisuals=function(){};view.pruneUnsupportedV10=function*(){};view.pruneMastAssemblyV13=function(){};
 view.isUpperInteriorSpaceV48Wip12B=s=>s?.envelopeKind!=='HULL';
 view.contractAudit=function(){let triangles=0;this.shipRoot.traverse(o=>{if(o.isMesh&&o.userData.sourceSovA){const g=this.damageOriginalMeshesV2.get(o)?.geometry??o.geometry;triangles+=(g.index?.count??g.attributes.position.count)/3;}});const checks={profile:this.shipRoot.userData.shipProfileId==='SOVREMENNY_956',sourcePreserved:triangles===SOV_REG_A.sourceTriangles,parked:[...this._sovAssetA.nodes.values()].every(n=>n.quaternion.x===0&&n.quaternion.y===0&&n.quaternion.z===0),noFunctionalMounts:this.spgMounts.size===0&&this.vlsLids.size===0,readOnly:this.shipRoot.userData.physicsFeedback===false};return {checks,sourceTriangles:triangles,pass:Object.values(checks).every(Boolean)};};
}
