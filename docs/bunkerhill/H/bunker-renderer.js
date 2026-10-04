function installBunkerRenderer(view){
  if(!IS_BUNKER)return;
  // The CG source owns its envelopes. Newly authored B1/H1/H2 decks also
  // belong to the deckhouses; the shared DDG deck-name rule missed them.
  const classifyInterior=view.isUpperInteriorSpaceV48Wip12B;
  view.isUpperInteriorSpaceV48Wip12B=function(space){
    return space?.envelopeKind!=null?space.envelopeKind!=='HULL':classifyInterior.call(this,space);
  };
  const auditInterior=view.interiorAuditV48Wip06;
  view.interiorAuditV48Wip06=function(){
    const audit=auditInterior.call(this),state=get3DRenderState().shipInteriorTopology,
      ids=new Set(this.interiorTopologyLayer?.userData?.spaceIds??[]),spaces=state?.spaces??[],
      fore=['S1','S2','S3','S4','B1'],aft=['H0','H1','H2'],coverage=[...fore,...aft].map(deck=>{
        const expected=spaces.filter(s=>s.deck===deck);
        return {deck,expected:expected.length,represented:expected.filter(s=>ids.has(s.id)).length};
      });
    // Coverage is checked against rendered source-contained spaces, not DDG
    // exhaust/mast room counts. CG funnel ducts and lattice masts are voids.
    audit.verticalCoverageBasis='CG52_AUTHORED_UPPER_DECKS_SOURCE_ENVELOPE';
    audit.upperDeckCoverage=coverage;
    audit.representedBridgeDecks=coverage.filter(q=>fore.includes(q.deck)&&q.represented>0).length;
    audit.representedHangarDecks=coverage.filter(q=>aft.includes(q.deck)&&q.represented>0).length;
    audit.verticalShellFilled=coverage.every(q=>q.expected>0&&q.represented===q.expected)&&
      audit.allInteriorContained&&state?.audit?.hangarClearance?.clear===true&&
      spaces.filter(s=>s.kind==='HANGAR_BAY'&&ids.has(s.id)).length===2;
    return audit;
  };
  view.buildShip=function(){
    const T=this.THREE,meta=BUNKER_RENDER_META,buf=BUNKER_RENDER_BUFFER,R=BUNKER_REGISTRATION,
      root=new T.Group(),parts=new Map(),nodes=new Map(),pal=meta.palette.map(p=>new T.Color(p.color));
    root.name=ACTIVE_SHIP_PROFILE.renderer.rootName;
    Object.assign(root.userData,{shipProfileId:ACTIVE_SHIP_PROFILE.id,shipProfileRevision:ACTIVE_SHIP_PROFILE.revision,
      rendererBuilderId:ACTIVE_SHIP_PROFILE.renderer.builderId,physicsFeedback:false,sourceSha256:R.sourceHtmlSha256});
    const materials={std:new T.MeshStandardMaterial({vertexColors:true,side:T.DoubleSide,roughness:.86,metalness:.012}),
      glass:new T.MeshStandardMaterial({vertexColors:true,side:T.DoubleSide,roughness:.29,metalness:.045}),
      metal:new T.MeshStandardMaterial({vertexColors:true,side:T.DoubleSide,roughness:.58,metalness:.40}),
      chain:new T.MeshStandardMaterial({vertexColors:true,side:T.DoubleSide,roughness:.87,metalness:.01,alphaTest:.5}),
      lines:new T.LineBasicMaterial({vertexColors:true})};
    if(meta.chain){const texture=new T.TextureLoader().load(meta.chain);texture.wrapS=texture.wrapT=T.RepeatWrapping;texture.colorSpace=T.SRGBColorSpace;materials.chain.map=texture;}
    function geometry(m){
      const g=new T.BufferGeometry(),q=new Uint16Array(buf,m.pos[0],m.pos[1]),p=new Float32Array(q.length),n=q.length/3;
      for(let i=0;i<n;i++)for(let k=0;k<3;k++)p[3*i+k]=m.qmin[k]+q[3*i+k]*m.qscale[k];
      const pid=new Uint8Array(buf,m.pid[0],m.pid[1]),colors=new Float32Array(n*3);
      for(let i=0;i<n;i++){const c=pal[pid[i]];colors[3*i]=c.r;colors[3*i+1]=c.g;colors[3*i+2]=c.b;}
      g.setAttribute('position',new T.BufferAttribute(p,3));g.setAttribute('normal',new T.BufferAttribute(new Int8Array(buf,m.nor[0],m.nor[1]),3,true));
      g.setAttribute('color',new T.BufferAttribute(colors,3));g.setAttribute('pid',new T.BufferAttribute(pid,1));
      if(m.uv)g.setAttribute('uv',new T.BufferAttribute(new Float32Array(buf,m.uv[0],m.uv[1]),2));
      if(m.idx)g.setIndex(new T.BufferAttribute(m.i32?new Uint32Array(buf,m.idx[0],m.idx[1]):new Uint16Array(buf,m.idx[0],m.idx[1]),1));
      g.computeBoundingBox();g.computeBoundingSphere();return g;
    }
    function mesh(m,name,cat){
      const o=m.lines?new T.LineSegments(geometry(m),materials.lines):new T.Mesh(geometry(m),materials[m.cls]??materials.std);
      o.name=name;Object.assign(o.userData,{partId:name,category:cat,physicsFeedback:false,
        sourceCG52:true,skipLegacyLargestIslandPrune:true,interiorEnvelopeV9:['hull','structure'].includes(cat)});
      if(o.isMesh)o.castShadow=o.receiveShadow=true;return o;
    }
    const cats={};
    for(const cat of ['hull','structure','fittings','weapons','sensors']){cats[cat]=new T.Group();cats[cat].name='CG52_'+cat.toUpperCase();root.add(cats[cat]);}
    // Split only registered antenna components for motion; all other fixed
    // source triangles retain their authored position and materials.
    function moveComponent(source,component,radar){
      const labels=source.userData.cg52Labels??BUNKER_RENDER_COMPONENTS?.structure,idx=source.geometry.index;if(!labels||!idx)return;
      const keep=[],moving=[],keepLabels=[];for(let i=0;i<labels.length;i++){const dst=labels[i]===component?moving:keep;if(dst===keep)keepLabels.push(labels[i]);for(let j=0;j<3;j++)dst.push(idx.array[3*i+j]);}
      if(!moving.length)return;
      const g=source.geometry.clone();g.setIndex(moving);source.geometry.setIndex(keep);source.userData.cg52Labels=keepLabels;
      const o=new T.Mesh(g,source.material),rotor=new T.Group();rotor.name='CG52_'+radar.id+'_ROTOR';
      const pivot=radar.rotorPivot;rotor.position.set(pivot.x,pivot.z,pivot.y);o.position.copy(rotor.position).multiplyScalar(-1);rotor.add(o);root.add(rotor);
      o.name=rotor.name+'_ANTENNA';o.userData.sourceCG52=true;o.castShadow=o.receiveShadow=true;parts.set(radar.id,rotor);
    }
    // The viewer merged fittings over the whole ship into one mesh. Local
    // damage must not scan that complete mesh for every opening. Partition its
    // index by location, retaining every triangle and its exact attributes.
    function partitionStaticSource(source){
      const g=source.geometry,p=g.attributes.position,idx=g.index,bins=new Map(),group=new T.Group();group.name=source.name;
      for(let i=0;i<idx.count;i+=3){const ids=[idx.getX(i),idx.getX(i+1),idx.getX(i+2)],avg=axis=>ids.reduce((n,j)=>n+p.array[j*3+axis],0)/3,
        key=[Math.floor(avg(0)/24),Math.floor(avg(1)/6),Math.floor(avg(2)/8)].join(':');
        let row=bins.get(key);if(!row){row=[];bins.set(key,row);}row.push(...ids);}
      for(const [key,ids]of bins){const chunk=new T.BufferGeometry(),sourceIds=[],remap=new Map(),localIds=[];
        // Keep the indexed source triangles, but store only this chunk's used
        // vertices. Shared whole-ship attributes made each local damage job
        // traverse/copy unrelated vertices in bounds, scorch and GPU uploads.
        for(const id of ids){let local=remap.get(id);if(local==null){local=sourceIds.length;sourceIds.push(id);remap.set(id,local);}localIds.push(local);}
        for(const [name,attribute]of Object.entries(g.attributes)){
          const data=new attribute.array.constructor(sourceIds.length*attribute.itemSize);
          for(let i=0;i<sourceIds.length;i++)for(let k=0;k<attribute.itemSize;k++)data[i*attribute.itemSize+k]=attribute.array[sourceIds[i]*attribute.itemSize+k];
          chunk.setAttribute(name,new T.BufferAttribute(data,attribute.itemSize,attribute.normalized));
        }
        chunk.setIndex(localIds);const box=new T.Box3(),v=new T.Vector3();
        for(const id of sourceIds)box.expandByPoint(v.fromBufferAttribute(p,id));
        chunk.boundingBox=box;chunk.boundingSphere=box.getBoundingSphere(new T.Sphere());
        const o=new T.Mesh(chunk,source.material);o.name=source.name+':'+key;o.userData={...source.userData,partId:o.name};o.castShadow=o.receiveShadow=true;group.add(o);}
      group.userData={sourceTriangles:idx.count/3,spatialChunks:bins.size,physicsFeedback:false};return group;
    }
    for(const stat of meta.statics)for(let i=0;i<stat.meshes.length;i++){
      let o=mesh(stat.meshes[i],`CG52_${stat.cat}_${i}`,stat.cat);
      if(['hull','fittings','weapons'].includes(stat.cat)&&o.isMesh&&o.geometry.index?.count>30000)o=partitionStaticSource(o);
      cats[stat.cat].add(o);parts.set(o.name,o);
      if(stat.cat==='structure'&&i===2)for(const radar of R.radars)moveComponent(o,radar.component,radar);
    }
    function build(rec,parent,assembly){
      const g=new T.Group();g.name=rec.name;g.position.fromArray(rec.local);parent.add(g);parts.set(rec.name,g);
      nodes.set(rec.name,{rec,obj:g,axis:new T.Vector3().fromArray(rec.axis).normalize(),assembly});
      for(let i=0;i<rec.meshes.length;i++)g.add(mesh(rec.meshes[i],rec.name+'_mesh_'+i,assembly.cat));
      for(const child of rec.children)build(child,g,assembly);
      return g;
    }
    for(const asm of meta.assemblies)build(asm.root,cats[asm.cat],asm);
    this.spgMounts=new Map();
    for(let i=0;i<4;i++){
      const yaw=parts.get(`spg${i}_yaw`),pitch=new T.Group();pitch.name=`CG52_SPG_${i}_PITCH`;pitch.position.y=.95;yaw.add(pitch);
      // Source viewer had yaw only. Separate dish and upper carriage triangles
      // from the fixed pedestal at its authored pivot, without pitching the base.
      for(const o of [...yaw.children])if(o.isMesh){
        const g=o.geometry,idx=g.index,p=g.attributes.position,moving=[],keep=[];
        for(let n=0;n<idx.count;n+=3){const ids=[idx.getX(n),idx.getX(n+1),idx.getX(n+2)],dst=ids.every(k=>p.getY(k)>.70)?moving:keep;dst.push(...ids);}
        if(moving.length){const upper=new T.Mesh(g.clone(),o.material);upper.userData.sourceCG52=true;upper.geometry.setIndex(moving);upper.position.y=-.95;upper.name='CG52_SPG_DISH_'+i;pitch.add(upper);g.setIndex(keep);}
      }
      this.spgMounts.set(i,{yaw,pitch,neutral:i<2?0:Math.PI});
    }
    this.vlsLids=new Map();for(const sec of ['fwd','aft'])for(const c of R.cells[sec])this.vlsLids.set(sec+':'+c.row+':'+c.col,parts.get(c.lidId));
    const countNode=rec=>rec.meshes.reduce((n,m)=>n+(m.idx?m.idx[1]/3:0),0)+rec.children.reduce((n,c)=>n+countNode(c),0),
      sourceTriangles=meta.statics.reduce((n,s)=>n+s.meshes.reduce((a,m)=>a+(m.idx?m.idx[1]/3:0),0),0)+meta.assemblies.reduce((n,a)=>n+countNode(a.root),0);
    this._bunkerAsset={root,parts,nodes,sourceTriangles,declaredSourceTriangles:R.sourceTriangles};
    this.shipRoot=root;this.scene.add(root);
    this.mk45TraverseGroup=parts.get('mk45f_yaw');this.mk45ElevationGroup=parts.get('mk45f_pitch');
    this.phalanxYawGroup=parts.get('ciwss_yaw');this.phalanxPitchGroup=parts.get('ciwss_pitch');
    this.seaRamYawGroup=null;this.seaRamPitchGroup=null;
    this.mainMastV12=new T.Group();this.mainMastV12.name='CG52_LEGACY_MAST_PRESENTATION_ALIAS';root.add(this.mainMastV12);
    this.bridgeMasterERotor=parts.get('SPS73');this.bridgeMasterEMount=this.bridgeMasterERotor;
    this.spq9bRotor=parts.get('SPQ9');
    root.updateWorldMatrix(true,true);return root;
  };
  view.syncMainGunVisualWip13B1=function(){};view.syncCiwsVisuals=function(){};
  view.pruneUnsupportedV10=function*(){};view.pruneMastAssemblyV13=function(){};
  view.syncShipFittings=function(st){
    const asset=this._bunkerAsset;if(!asset)return;
    const rotate=(id,angle)=>{const n=asset.nodes.get(id);if(n)n.obj.quaternion.setFromAxisAngle(n.axis,angle);};
    for(const q of st.mountInventory?.guns??[]){const g=BUNKER_REGISTRATION.guns[q.hardpointId];
      rotate(g.yawNode,-(q.bodyAzRad-g.neutralAzRad));rotate(g.pitchNode,q.elevationRad-g.restElevationRad);}
    for(const q of st.mountInventory?.closeIn??[]){const g=BUNKER_REGISTRATION.ciws[q.hardpointId];
      rotate(g.yawNode,-(q.azRelRad-g.neutralAzRad));rotate(g.pitchNode,q.elRad);}
    const frame=shipGameFrameV1();
    for(const b of st.illum?.spg62Mounts??[]){const m=this.spgMounts.get(b.illId);if(!m)continue;
      const body=frame.vectorToBody({x:Math.cos(b.elRad)*Math.cos(b.azWorldRad),y:Math.cos(b.elRad)*Math.sin(b.azWorldRad),z:Math.sin(b.elRad)});
      const az=Math.atan2(body.y,body.x),el=Math.atan2(body.z,Math.hypot(body.x,body.y));m.yaw.rotation.y=-(az-m.neutral);m.pitch.rotation.z=(m.neutral? -1:1)*el;}
    c14SyncVlsLids(this,st);
    for(const [key,lid]of this.vlsLids){const n=asset.nodes.get(lid.name),q=this._c14LidAnimation?.cells?.get(key),now=Number(st.timeS)||0,
      f=c14VlsLidValue(q,now);lid.quaternion.setFromAxisAngle(n.axis,f*C14_LID_PRESENTATION.maxRad);}
    for(const radar of BUNKER_REGISTRATION.radars){
      const o=asset.parts.get(radar.id);if(o)o.rotation.y=-(st.auxNav?.find(q=>q.id===radar.id)?.angleRad??
        (radar.id==='SPQ9'?st.radar.spq9bAngleRad:st.radar.bridgeMasterEAngleRad)??0);}
    const now=Number(st.timeS)||0,pr=this._bunkerProp??(this._bunkerProp={time:now,angle:0}),dt=Math.max(0,Math.min(1,now-pr.time));
    pr.time=now;pr.angle=(pr.angle+(Number(st.ship.shaftRpm)||0)/60*2*Math.PI*dt)%(2*Math.PI);
    for(const id of ['propp','props']){const n=asset.nodes.get(id+'_spin')??[...asset.nodes.values()].find(n=>n.assembly.id===id);if(n)n.obj.quaternion.setFromAxisAngle(n.axis,pr.angle*(n.rec.dir??1));}
  };
  view.contractAudit=function(){
    const a=this._bunkerAsset,R=BUNKER_REGISTRATION,near=(a,b)=>Math.abs(a-b)<1e-6;
    let retainedTriangles=0;this.shipRoot?.traverse(o=>{if(o.isMesh&&o.userData.sourceCG52){
      const g=this.damageOriginalMeshesV2?.get(o)?.geometry??o.geometry;retainedTriangles+=(g.index?.count??g.attributes.position.count)/3;}});
    const at=(id,p)=>{const o=a?.parts.get(id);if(!o)return false;this.shipRoot.updateWorldMatrix(true,true);const q=this.shipRoot.worldToLocal(o.getWorldPosition(new this.THREE.Vector3()));return near(q.x,p.x)&&near(q.z,p.y)&&near(q.y,p.z);};
    const checks={profile:this.shipRoot?.userData.shipProfileId===ACTIVE_SHIP_PROFILE.id,
      guns:Object.values(R.guns).every(g=>at(g.yawNode,g.pivot)),
      closeIn:Object.values(R.ciws).every(g=>at(g.yawNode,g.pivot)&&at(g.pitchNode,g.pitchPivot)),
      spg:this.spgMounts?.size===4&&R.spg.every((p,i)=>at('spg'+i+'_yaw',{x:p[0],y:p[1],z:p[2]-.95})),
      vlsRegistration:this.vlsLids.size===122&&['fwd','aft'].every(sec=>R.cells[sec].every(c=>this.vlsLids.get(sec+':'+c.row+':'+c.col)===a.parts.get(c.lidId))),
      navigationAntennas:R.radars.every(r=>at(r.id,r.rotorPivot)),
      sourcePreserved:retainedTriangles===a.sourceTriangles,readOnly:this.shipRoot.userData.physicsFeedback===false};
    return {schema:'AEGIS_CG52_RENDERER_AUDIT_V1',checks,retainedTriangles,sourceTriangles:a.sourceTriangles,
      declaredSourceTriangles:a.declaredSourceTriangles,pass:Object.values(checks).every(Boolean),physicsFeedback:false};
  };
  view.phalanxMuzzlePose=function(st){const q=st.mountInventory?.closeIn?.[0];if(!q)return null;
    const m=BUNKER_REGISTRATION.ciws[q.hardpointId],d=bunkerCiwsMuzzleOffset(m,q.azRelRad,q.elRad),T=this.THREE;
    return {dir:new T.Vector3(Math.cos(q.elRad)*Math.cos(q.azRelRad),Math.sin(q.elRad),Math.cos(q.elRad)*Math.sin(q.azRelRad)),
      pos:new T.Vector3(m.x+d.x,m.z+d.z,m.y+d.y)};};
}
installBunkerRenderer(WIP148_EXTERNAL_3D);
if(IS_BUNKER){
  // Operator commands continue to use the selected instance; simulation steps,
  // damage and ammunition remain independent for every gun.
  const select=document.createElement('select');select.id='cg52GunSelect';select.setAttribute('aria-label','운용 함포');
  for(const inst of ACTIVE_SHIP_PROFILE.weapons.gunMounts){const o=document.createElement('option');o.value=inst.id;o.textContent=inst.hardpointId==='mk45'?'함수 Mk 45 Mod 2':'함미 Mk 45 Mod 2';select.appendChild(o);}
  select.addEventListener('change',()=>{ACTIVE_SHIP_RUNTIME.weapons.selectedGunId=select.value;
    ACTIVE_SHIP_RUNTIME.weapons.mainGun=ACTIVE_SHIP_RUNTIME.weapons.gunMounts.get(select.value);wip13b5UpdateGunButtonLabels();});
  const button=document.getElementById('mainGunCueBtn');
  button?.parentNode.insertBefore(select,button);
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT),rows=[];while(walker.nextNode())rows.push(walker.currentNode);
  for(const node of rows)if(!['SCRIPT','STYLE'].includes(node.parentElement?.tagName))node.textContent=node.textContent
    .replaceAll('DDG-119','CG-52').replaceAll('Delbert D. Black','Bunker Hill').replaceAll('SPY-1D(V)','SPY-1A')
    .replaceAll('SPQ-9B','SPQ-9').replaceAll('BridgeMaster E','AN/SPS-73').replaceAll('SeaRAM','Phalanx 좌현');
}
