// Presentation only. Project the fixed-tick raft XY onto the existing visual
// Gerstner water surface; shader waves are not the simulation's sea spectrum.
(function installRescueRaftRendererK(view){
  view.rescueRaftVisualsK=new Map();
  view.rescueWaterPoseK=function(q,st){
    const rot=(st.sea?.environment?.wave?.directionRad??0)-Math.atan2(.37,.93),c=Math.cos(rot),s=Math.sin(rot),sea=clamp((st.sea?.environment?.wave?.hsM??0)/6.2,0,1.05),time=st.timeS;
    const camera=this.camera.position,origin=this.renderOriginWip14A??{x:0,z:0},distance=Math.hypot(q.xM-origin.x-camera.x,q.zM-origin.z-camera.z),u=clamp((distance-120)/105,0,1),lod=1-u*u*(3-2*u);
    const waves=[[.93,.37,93,.72,.20,.4],[.61,.79,57,.38,.14,2.3],[-.28,.96,31,.19,.10,4.1],[.87,-.49,19,.095,.06,1.2]];
    const sample=(x,z)=>{let ox=0,oz=0,height=0;for(const [ax,az,length,a,steep,phase]of waves){const n=Math.hypot(ax,az),dx=(c*ax-s*az)/n,dz=(s*ax+c*az)/n,k=TAU/length,t=k*(dx*x+dz*z)-Math.sqrt(9.81*k)*time+phase,b=steep*(.08+sea)*lod/k;
        ox+=b*dx*Math.cos(t);oz+=b*dz*Math.cos(t);height+=a*(.08+sea)*lod*Math.sin(t);}return {ox,oz,height};};
    const heightAt=(x,z)=>{let px=x,pz=z;for(let i=0;i<4;i++){const a=sample(px,pz);px=x-a.ox;pz=z-a.oz;}return sample(px,pz).height;};
    const h=q.headingRad,dx=Math.cos(h),dz=Math.sin(h),sx=-dz,sz=dx;
    return {y:heightAt(q.xM,q.zM)+SHIP_RESCUE_MK7_K.freeboardM,
      pitch:clamp(Math.atan((heightAt(q.xM+dx,q.zM+dz)-heightAt(q.xM-dx,q.zM-dz))/2),-deg(18),deg(18)),
      roll:clamp(Math.atan((heightAt(q.xM+sx,q.zM+sz)-heightAt(q.xM-sx,q.zM-sz))/2),-deg(18),deg(18))};
  };
  view.rescueResourcesK=function(){
    if(this._rescueResourcesK)return this._rescueResourcesK;const T=this.THREE;
    // Small reusable meshes, retained once per renderer. Each raft owns only its
    // root and instance transforms; deleting a raft never disposes shared assets.
    return this._rescueResourcesK={tube:new T.TorusGeometry(2.4,.25,6,8),floor:new T.CylinderGeometry(2.25,2.25,.08,8),
      roof:new T.ConeGeometry(2.5,1.1,8),pole:new T.CylinderGeometry(.025,.025,1.1,5),head:new T.SphereGeometry(.11,6,4),jacket:new T.CylinderGeometry(.14,.19,.30,5),
      rubber:new T.MeshStandardMaterial({color:0x313937,roughness:.96}),canopy:new T.MeshStandardMaterial({color:0xd97324,roughness:1,side:T.DoubleSide}),
      skin:new T.MeshStandardMaterial({color:0xb68e70,roughness:1}),vest:new T.MeshStandardMaterial({color:0xf79430,roughness:1})};
  };
  view.createRescueRaftK=function(q){
    const T=this.THREE,r=this.rescueResourcesK(),root=new T.Group();root.name=q.id;
    for(const y of [.16,.55]){const tube=new T.Mesh(r.tube,r.rubber);tube.rotation.x=Math.PI/2;tube.position.y=y;root.add(tube);}
    const floor=new T.Mesh(r.floor,r.rubber);floor.position.y=.24;root.add(floor);
    const roof=new T.Mesh(r.roof,r.canopy);roof.position.y=1.75;roof.rotation.y=Math.PI/8;root.add(roof);
    for(let i=0;i<8;i++){const a=TAU*i/8,p=new T.Mesh(r.pole,r.rubber);p.position.set(2.18*Math.cos(a),.89,2.18*Math.sin(a));root.add(p);}
    const heads=new T.InstancedMesh(r.head,r.skin,25),jackets=new T.InstancedMesh(r.jacket,r.vest,25),dummy=new T.Object3D();
    for(let i=0;i<25;i++){const ring=i===0?0:i<9?1:2,n=ring===1?8:16,j=ring===1?i-1:i-9,a=n?TAU*j/n:0,radius=ring===0?0:ring===1?.75:1.55;
      dummy.position.set(radius*Math.cos(a),.88,radius*Math.sin(a));dummy.updateMatrix();heads.setMatrixAt(i,dummy.matrix);
      dummy.position.y=.63;dummy.updateMatrix();jackets.setMatrixAt(i,dummy.matrix);}
    heads.instanceMatrix.needsUpdate=jackets.instanceMatrix.needsUpdate=true;root.add(heads,jackets);this.rescueRaftLayerK.add(root);
    return {root,heads,jackets};
  };
  view.disposeRescueRaftK=function(v){v.root.removeFromParent();v.heads.dispose();v.jackets.dispose();};
  view.syncRescueRaftsK=function(st){
    const rows=st.lifeRafts??[];if(!this.rescueRaftLayerK&&rows.length){this.rescueRaftLayerK=new this.THREE.Group();this.rescueRaftLayerK.name='SURVIVAL_RAFTS_WORLD';this.worldRoot.add(this.rescueRaftLayerK);}
    const seen=new Set();for(const q of rows){seen.add(q.id);let v=this.rescueRaftVisualsK.get(q.id);if(!v){v=this.createRescueRaftK(q);this.rescueRaftVisualsK.set(q.id,v);}
      const p=this.rescueWaterPoseK(q,st);v.root.position.set(q.xM,p.y,q.zM);v.root.rotation.set(-p.roll,-q.headingRad,p.pitch,'YXZ');
      v.heads.count=v.jackets.count=q.persons;v.root.userData={id:q.id,ownerEntityId:q.ownerEntityId,persons:q.persons,capacityPersons:q.capacityPersons,
        phase:q.phase,presentationOnly:true,physicsFeedback:false,seaProjection:'EXISTING_GERSTNER_SHADER_PRESENTATION_ONLY'};
    }
    for(const [id,v]of this.rescueRaftVisualsK)if(!seen.has(id)){this.disposeRescueRaftK(v);this.rescueRaftVisualsK.delete(id);}
  };
  view.rescueRaftAuditK=function(){const st=get3DRenderState(),before=JSON.stringify(shipRescueK().snapshot());
    const rows=[...this.rescueRaftVisualsK].map(([id,v])=>({id,persons:v.heads.count,jackets:v.jackets.count,userData:{...v.root.userData},parent:v.root.parent?.name,
      worldParent:this.rescueRaftLayerK?.parent===this.worldRoot,position:{x:v.root.position.x,y:v.root.position.y,z:v.root.position.z}}));
    return {schema:'AEGIS_3D_SURVIVAL_RAFT_AUDIT_K_1',presentationOnly:true,physicsFeedback:false,rows,authoritative:st.lifeRafts,
      sharedResources:!!this._rescueResourcesK,readOnly:before===JSON.stringify(shipRescueK().snapshot())};
  };
})(WIP148_EXTERNAL_3D);
