let bunkerRenderLoadB=null;
function ensureBunkerRenderAssetsB(){if(BUNKER_RENDER_META)return Promise.resolve();if(!bunkerRenderLoadB)bunkerRenderLoadB=Promise.all([readBunkerAsset('cg52-meta'),readBunkerAsset('cg52-geo',false),readBunkerAsset('cg52-components')]).then(([meta,buffer,components])=>{BUNKER_RENDER_META=meta;BUNKER_RENDER_BUFFER=buffer;BUNKER_RENDER_COMPONENTS=components;});return bunkerRenderLoadB;}
// Each presenter owns its meshes, materials, jobs and interior caches. The
// original profile builders are reused; camera/geometry never integrate physics.
function physicalShipRenderStateB(r){
  const p=resolveShipProfile(r.profileId),n=r.navigation,t=simStepCounter*SIM_FIXED_DT,cg=p.id==='CG_52_LATE_TICONDEROGA';
  const damage=createShipDamageVisualStateV1(r.flooding.snapshot(),r.damage.control.snapshot(),r.hitHistory,r.geometry.boxes,{terminalEvents:[]});
  return {contract:'NAVAL_RENDER_STATE_V2',ownerEntityId:r.entityId,shipProfile:{id:p.id,revision:p.revision},timeS:t,
    ship:{headingRad:n.heading,speedMps:n.speed,targetSpeedKt:n.targetSpeedKt,shaftRpm:n.shaftRpm??0,propPitch:n.propPitch??0,worldXM:worldToMeters(n.positionWorld.x),worldYM:worldToMeters(n.positionWorld.y)},
    shipBodyFrame:shipBodyFrameB(r).snapshot(),floodAttitudePreview:r.survival.snapshot(),shipDynamicsV15:r.dynamics.snapshot(),
    shipDamageVisual:damage,shipInteriorTopology:r.interior.snapshot(),shipCrewSpatial:r.crew.snapshot(),terminalImpacts:[],armorDamagePatches:[],missiles:[],harpoons:[],visualEvents:[],
    mainGun:r.weapons.mainGun.snapshot(),ciws:{phalanx:{azRelRad:0,elRad:0,state:'IDLE'},seaRam:cg?null:{azRelRad:0,elRad:0,state:'IDLE'}},
    mountInventory:{guns:[...r.weapons.gunMounts.values()].map(g=>g.snapshot()),closeIn:r.weapons.closeIn.map(m=>({hardpointId:m.installation?.hardpointId,azRelRad:0,elRad:0,type:m.type}))},
    vls:{cells:Object.entries(r.weapons.vls).flatMap(([section,cells])=>cells.map(c=>({section,row:c.row,col:c.col,state:c.destroyed?'DESTROYED':'READY',fire:0})))},
    harpoonInventory:{tubes:r.weapons.harpoon.tubes.map(t=>({...t}))},
    // Antennas stay parked while per-observer radar execution is deferred.
    radar:{emconActive:true,mastLostV12:shipSystemDamageB(r,'MAST')>=80,spq9bLostV12:false,bridgeMasterELostV48Wip08:false,spq9bAngleRad:0,bridgeMasterEAngleRad:0},
    illum:{spg62Mounts:[]},auxNav:[],sim:{step:simStepCounter,presentationEpoch:ENGAGEMENT_RUNTIME.world.presentationEpoch??0}};
}
function createPhysicalShipPresenterB(view,r){
  const v=Object.create(null),p=resolveShipProfile(r.profileId);
  for(const [k,q]of Object.entries(MULTISHIP_RENDER_BASE_B)){
    if(typeof q==='function'||q==null||typeof q!=='object')v[k]=q;
    else if(q instanceof Map)v[k]=new Map();else if(q instanceof Set)v[k]=new Set();else if(Array.isArray(q))v[k]=[];
    else if(Object.getPrototypeOf(q)===Object.prototype)v[k]=jsonSafeCloneV48Wip11A(q);
  }
  // Later common presentation helpers are shared as functions, never as state.
  for(const [k,q]of Object.entries(view))if(typeof q==='function'&&!(k in v))v[k]=q;
  Object.assign(v,{THREE:view.THREE,ownerId:r.entityId,ownerRuntime:r,ownerProfile:p,scene:view.navalShipLayerB,renderer:view.renderer,root:null,canvas:null,
    c12Options:{...view.c12Options},c13MeshStats:{...view.c13MeshStats},_c12BudgetOwner:view,_c12DamageShareMs:1.5,
    damageOriginalMeshesV2:new Map(),damageSurfaceBindingsV2:new Map(),damageScarVisuals:new Map(),damageDetachedLinesV10:new Map(),damageDetachedBoxesV10:[],
    damageSurfaceToolsV2:createDamageSurfaceToolsV2(view.THREE,{profile:p})});
  if(p.id==='CG_52_LATE_TICONDEROGA')installBunkerRenderer(v,p);
  else {wip13c51InstallRenderer(v,p);wip13c52InstallRenderer(v,p);}
  // All clipping/envelope queries use the same owner geometry as physics.
  const L=r.geometry.layout;
  v.upperStructureIntervalsV48Wip06=(x,z)=>L.intervals(x,z,'all');
  v.interiorEnvelopeOverlapV48Wip12B=function(s,x,z,y0=s?.y0,y1=s?.y1,inset=.16){let best=null,width=0;for(const row of L.intervals(x,z,s.envelopeKind??(this.isUpperInteriorSpaceV48Wip12B(s)?'all':'HULL'),inset)){const a=Math.max(y0,row[0]),b=Math.min(y1,row[1]);if(b-a>width){best=[a,b];width=b-a;}}return width>.04?best:null;};
  v.shipRoot=v.buildShip();view.navalShipLayerB.add(v.shipRoot);Object.assign(v.shipRoot.userData,{entityId:r.entityId,ownerEntityId:r.entityId,navalPhysicalShip:true});
  const st=physicalShipRenderStateB(r);v.buildInteriorTopologyV48Wip06(v.shipRoot,st.shipInteriorTopology);v.buildCrewInteriorV48Wip07(v.shipRoot,st.shipCrewSpatial);v.applyShipBodyFrame(st);
  if(p.id!=='CG_52_LATE_TICONDEROGA')v.contractAudit=function(){const a=this._c5Asset,checks={profile:this.shipRoot.userData.shipProfileId===p.id,sourceGeometry:!!a?.parts.get('HULL'),vlsRegistration:this.vlsLids.size===96,spg:this.spgMounts.size===3,closeIn:!!this.phalanxYawGroup&&!!this.seaRamYawGroup,interior:this.interiorTopologyLayer.userData.spaceIds.length===p.interior.expected.spaces,readOnly:this.shipRoot.userData.physicsFeedback===false};return {checks,pass:Object.values(checks).every(Boolean)};};
  r.modelRoots.world=v.shipRoot;return v;
}
function disposePhysicalShipPresenterB(v){
  v._damageJobV3?.return?.();v._interiorJobV8?.return?.();
  const geos=new Set(),mats=new Set(),add=o=>{if(o?.geometry)geos.add(o.geometry);for(const m of Array.isArray(o?.material)?o.material:[o?.material])if(m)mats.add(m);};
  v.shipRoot.traverse(add);for(const [mesh,row]of v.damageOriginalMeshesV2??[]){add(mesh);if(row.geometry)geos.add(row.geometry);}
  for(const g of geos)g.dispose();for(const m of mats)m.dispose();const owner=v._c12BudgetOwner,record=owner?._c11Ships?.get('NAVAL:'+v.ownerId);if(record){c11DisposeProxy(record);owner._c11Ships.delete('NAVAL:'+v.ownerId);}v.shipRoot.removeFromParent();if(v.ownerRuntime.modelRoots.world===v.shipRoot)v.ownerRuntime.modelRoots.world=null;
}
function installPhysicalFleetRendererB(view){
  view.navalShipPresentersB=new Map();view.navalFocusB=null;
  view.syncPhysicalFleetB=function(ownState){
    if(!this.worldRoot)return;if(!this.navalShipLayerB){this.navalShipLayerB=new this.THREE.Group();this.navalShipLayerB.name='PHYSICAL_NAVAL_SHIPS_B';this.worldRoot.add(this.navalShipLayerB);}
    const ships=physicalShipsB(),wanted=new Set(ships.map(r=>r.entityId));
    for(const [id,v]of this.navalShipPresentersB)if(!wanted.has(id)||!ships.includes(v.ownerRuntime)){disposePhysicalShipPresenterB(v);this.navalShipPresentersB.delete(id);}
    for(const r of ships){if(r.profileId==='CG_52_LATE_TICONDEROGA'&&!BUNKER_RENDER_META){if(!this.bunkerLoadPendingB){this.bunkerLoadPendingB=true;ensureBunkerRenderAssetsB().then(()=>{this.bunkerLoadPendingB=false;}).catch(e=>{this.bunkerLoadErrorB=String(e.message);});}continue;}let v=this.navalShipPresentersB.get(r.entityId);if(!v){v=createPhysicalShipPresenterB(this,r);this.navalShipPresentersB.set(r.entityId,v);}
      const st=physicalShipRenderStateB(r);v.applyShipBodyFrame(st);v.shipRoot.updateWorldMatrix(true,true);v.syncShipFittings(st);v.syncMainGunVisualWip13B1(st);v.syncCiwsVisuals(st);
      // Borrow unused work budget while preserving a share for damaged ownship.
      // The common frame allowance stays unchanged; native rendering alone
      // advances these cooperative jobs, never the simulation clock.
      const work=this.c12FrameWork,left=Math.max(.25,(work?.allowanceMs??6)-(work?.usedMs??0)),ownPending=!!this._damageJobV3||!!ownState?.shipDamageVisual?.scars?.length;
      v._c12DamageShareMs=Math.min(5,ownPending?left*.5:left);
      v.syncDamageScarsV1(st);v.syncCompartmentInteriorV8(st);v.syncInteriorHazardsV48Wip12B(st);v.syncCrewInteriorV48Wip07(st);
      v.interiorTopologyVisible=this.navalFocusB===r.entityId&&this.interiorTopologyVisible;v.syncDetailedInteriorDamageVisibilityV48Wip12B(st);v.setInteriorExteriorTransparencyV48Wip06(v.interiorTopologyVisible);if(this._c11Ships)c11ShipPolicy(this,v.shipRoot,'NAVAL:'+r.entityId,(r.geometry.bow-r.geometry.stern)*.55,v.interiorTopologyVisible);
    }
    if(this.navalFocusB&&!wanted.has(this.navalFocusB))this.navalFocusB=null;
  };
  const camera=view.syncCamera;view.syncCamera=function(...args){
    const v=this.navalShipPresentersB.get(this.navalFocusB);if(!v)return camera.apply(this,args);
    const T=this.THREE,o=this.orbit,tgt=v.shipRoot.getWorldPosition(new T.Vector3());tgt.y+=o.targetY||10;
    this.camera.position.set(tgt.x+Math.cos(o.yaw)*Math.cos(o.pitch)*o.distance,tgt.y+Math.sin(o.pitch)*o.distance,tgt.z+Math.sin(o.yaw)*Math.cos(o.pitch)*o.distance);this.camera.lookAt(tgt);
  };
  const reset=view.resetCamera;view.resetCamera=function(...args){this.navalFocusB=null;return reset.apply(this,args);};
  view.focusPhysicalShipB=function(id=null){if(id&&!physicalShipsB().some(r=>r.entityId===id))return false;this.navalFocusB=id;this.follow.enabled=false;this.surfaceFocus.enabled=false;this.orbit.distance=280;this.orbit.targetY=10;return true;};
  view.physicalFleetAuditB=function(){return {schema:'AEGIS_PHYSICAL_FLEET_RENDER_B',ready:this.ready,roots:[...this.navalShipPresentersB.values()].map(v=>({entityId:v.ownerRuntime.entityId,profileId:v.shipRoot.userData.shipProfileId,
    lidCount:v.vlsLids.size,spgCount:v.spgMounts.size,seaRamPresent:!!v.seaRamYawGroup,root:v.shipRoot.position.toArray(),matrix:v.shipRoot.matrix.toArray(),parent:v.shipRoot.parent.name,
    damage:v.damageBuildStatsV3??null,scars:v.damageScarVisuals.size,holes:[...v.damageScarVisuals.values()].map(q=>({id:q.scar.id,role:q.scar.impactRole,actualHole:!!q.group.userData.actualHole,attached:!!q.group.parent})),unmatched:v.damageUnmatchedCountV2??0,interiorSpaces:v.interiorTopologyLayer?.userData?.spaceIds?.size??v.interiorTopologyLayer?.userData?.spaceIds?.length,
    contract:v.contractAudit?.()??null})),physicsFeedback:false};};
  const root=view.root,toolbar=root?.querySelector('.external3d-toolbar');if(toolbar){const button=document.createElement('button');button.id='external3DNavalShipBtn';button.className='external3d-btn';button.textContent='배치 함정 보기';button.onclick=()=>{
    if(view.navalFocusB){view.focusPhysicalShipB(null);button.textContent='배치 함정 보기';}
    else {const r=physicalShipsB()[0];if(!r){notify('배치한 함정이 없습니다.');return;}view.focusPhysicalShipB(r.entityId);button.textContent='자함 보기';}
  };toolbar.appendChild(button);}
}
installPhysicalFleetRendererB(WIP148_EXTERNAL_3D);
