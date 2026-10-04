function bunkerCanonicalExternal(){
  const hp=ACTIVE_SHIP_PROFILE.geometry.hardpoints,out=[],add=q=>out.push(Object.freeze(q));
  for(const [key,system]of [['mk45','MK45'],['mk45Aft','MK45_AFT'],['phalanx','CIWS_GUN'],['phalanxPort','CIWS_GUN_PORT'],
    ['spq9b','SPQ9B'],['bridgeMasterE','BRIDGEMASTER_E'],['vlsForward','VLS_FWD'],['vlsAft','VLS_AFT']]){
    const h=hp[key];add({name:h.name,system,oX:h.x,oY:h.y,hL:h.hL??h.spanX/2,hW:h.hW??h.spanY/2,
      zMin:h.z-(h.hH??.3),zMax:h.z+(h.hH??.3),renderClass:'EQUIPMENT'});
  }
  for(const q of WIP199_SPY_HITBOXES)add({...q});
  for(const q of SPG62_ILLUMINATORS)add({...spg62HitboxForIlluminator(q)});
  for(const r of [...BUNKER_REGISTRATION.ewPods])
    add({name:r.label??r.name,oX:r.center.x,oY:r.center.y,hL:r.half.x,hW:r.half.y,zMin:r.min.z,zMax:r.max.z,renderClass:'SENSOR'});
  for(const r of BUNKER_REGISTRATION.occluders.filter(r=>r.name.startsWith('STRUCTURE:')||r.name.startsWith('FUNNEL:')))
    add({name:r.name,oX:r.center.x,oY:r.center.y,hL:r.half.x,hW:r.half.y,zMin:r.min.z,zMax:r.max.z,
      geometryEnvelope:'CG52_ARCHITECTURE',renderClass:'STRUCT'});
  return out;
}
function bunkerExportGunInventory(){return [...ACTIVE_SHIP_RUNTIME.weapons.gunMounts].map(([id,g])=>{
  const q=g.snapshot();return {id,moduleId:g.spec.id,hardpointId:g.installation.hardpointId,
    magazine:{...q.magazine},loadedAmmoId:q.loadedAmmoId,shotsFired:q.shotsFired};});}
function bunkerValidateGunInventory(inventory,errors){
  const rows=inventory.gunMounts,live=ACTIVE_SHIP_RUNTIME.weapons.gunMounts,seen=new Set(),err=(code,id='')=>operationalErrorV48Wip11B(errors,code,id);
  if(!Array.isArray(rows)||rows.length!==live.size){err('GUN_MOUNT_COUNT');return;}
  if(!live.has(inventory.selectedGunId))err('SELECTED_GUN_ID');
  for(const q of rows){
    if(!operationalRecordV48Wip11B(q)||!live.has(q.id)||seen.has(q.id)){err('GUN_MOUNT_ID');continue;}seen.add(q.id);
    const g=live.get(q.id),keys=Object.keys(g.spec.magazine.initialRounds);
    if(q.moduleId!==g.spec.id||q.hardpointId!==g.installation.hardpointId)err('GUN_MOUNT_PROFILE',q.id);
    if(!operationalRecordV48Wip11B(q.magazine)||Object.keys(q.magazine).length!==keys.length||keys.some(k=>
      !operationalIntRangeV48Wip11B(q.magazine[k],0,g.spec.magazine.initialRounds[k])))err('GUN_MAGAZINE',q.id);
    if(!keys.includes(q.loadedAmmoId)||!operationalIntRangeV48Wip11B(q.shotsFired,0,Number.MAX_SAFE_INTEGER))err('GUN_STATE',q.id);
  }
}
function bunkerRestoreGunInventory(inventory){
  for(const q of inventory.gunMounts)ACTIVE_SHIP_RUNTIME.weapons.gunMounts.get(q.id).restoreInventory(q);
  ACTIVE_SHIP_RUNTIME.weapons.selectedGunId=inventory.selectedGunId;
  ACTIVE_SHIP_RUNTIME.weapons.mainGun=ACTIVE_SHIP_RUNTIME.weapons.gunMounts.get(inventory.selectedGunId);
  const select=document.getElementById('cg52GunSelect');if(select)select.value=inventory.selectedGunId;
}
function bunkerProfileAudit(){
  const p=ACTIVE_SHIP_PROFILE,r=ACTIVE_SHIP_RUNTIME,hp=p.geometry.hardpoints,R=BUNKER_REGISTRATION,
    deep=(q,seen=new WeakSet())=>!q||typeof q!=='object'||seen.has(q)||(seen.add(q),Object.isFrozen(q)&&Object.values(q).every(v=>deep(v,seen))),
    topo=getShipInteriorTopologyV48Wip06().audit(),boxes=buildShipHitBoxes(),full=getShipMassLedgerV32().snapshot(),
    checks={schema:p.schema==='AEGIS_SHIP_PROFILE_V48_WIP11'&&p.id==='CG_52_LATE_TICONDEROGA',deeplyFrozen:deep(p),
      registryIdentity:SHIP_PROFILE_REGISTRY[p.id]===p,geometry:shipGeometryLayout()===window.BunkerLayout&&shipAssetRegistration().id===R.id,
      separateInterior:topo.independentCG52Layout&&topo.centersInside&&topo.unreachable.length===0,
      separateCrew:p.crew.roster===330&&getShipCrewV21().snapshot().total===330,
      gunRegistry:p.weapons.gunMounts.every(i=>!!SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8[i.moduleId]&&!!SHIP_GUN_BUILDER_REGISTRY_V48_WIP13B8[i.builderId]),
      hardwareRegistry:Object.values(p.weapons.closeIn.mounts).every(i=>!!SHIP_EQUIPMENT_PROFILE_REGISTRY[i.moduleId]),
      runtimeSeparated:r!==p&&r.weapons.gunMounts.size===2&&r.weapons.closeIn===ciws,
      independentGuns:new Set([...r.weapons.gunMounts.values()]).size===2&&r.weapons.mainGun===r.weapons.gunMounts.get(r.weapons.selectedGunId),
      noRAM:ciws.length===2&&ciws.every(q=>q.type==='GUN'),vls:vlsCells.fwd.length===61&&vlsCells.aft.length===61,
      sparseCells:['fwd','aft'].every(sec=>vlsCells[sec].every((c,i)=>c.row===R.cells[sec][i].row&&c.col===R.cells[sec][i].col)),
      illuminators:SPG62_ILLUMINATORS.length===4&&SPG62_ILLUMINATORS.every((q,i)=>Math.abs(q.oX-R.spg[i][0])+Math.abs(q.oY-R.spg[i][1])+Math.abs(q.height-R.spg[i][2])<1e-7),
      spyVariant:p.identity.radarVariantFinding.startsWith('SPY-1A_MODERNIZED')&&SENSOR_MODEL===SHIP_SENSOR_MODEL_REGISTRY_V48_WIP09[p.sensors.modelId],
      secondaryRadars:p.equipment.secondaryRadars.length===2,ewPods:p.equipment.ew.pods.length===2,
      nulka:p.equipment.nulka.layout.launchers.length===4&&p.equipment.nulka.layout.launchers.every(l=>l.tubes.length===2),
      srboc:mk36LauncherState.length===4&&mk36LoadedRounds()===24,
      hitboxes:boxes.every(b=>b.targetId)&&new Set(boxes.map(b=>b.targetId)).size===boxes.length,
      massClosure:Math.abs(full.massKg-p.mass.fullLoadTargetKg)<.001,
      protectionActive:materialProtectionAuditV48Wip11().pass,
      rendererReadOnly:p.renderer.physicsFeedback===false&&R.liveMeshReads===false};
  return {schema:'AEGIS_CG52_PROFILE_AUDIT_V1',profileId:p.id,profileRevision:p.revision,checks,counts:{
    vls:122,guns:2,phalanx:2,spg62:4,nulkaTubes:8,srbocTubes:24,spaces:topo.spaceCount,crew:330},
    provenance:p.identity.basis,pass:Object.values(checks).every(Boolean)};
}
function bunkerMasksAudit(){
  const rows=[],E=SHIP_EQUIPMENT_PROFILE_REGISTRY;
  const scan=(id,fn)=>{const samples=[];for(let d=-180;d<180;d+=2){const q=fn(d*Math.PI/180);samples.push({azDeg:d,ok:q.ok,reason:q.reason,obstruction:q.obstruction??null});}
    rows.push({id,open:samples.filter(q=>q.ok).length,blocked:samples.filter(q=>!q.ok).length,samples});};
  for(const [id,g]of ACTIVE_SHIP_RUNTIME.weapons.gunMounts)scan(id,a=>bunkerGunClearance(g.spec,a,0));
  for(const m of ciws)scan(m.installationId,a=>{const q=ciwsGameConstraintsV1(m).direction(a,0);return {...q,obstruction:q.reason};});
  for(const q of SPG62_ILLUMINATORS)scan(q.id,a=>bunkerSpgMask(q,a,q.height,100));
  const checks={mounts:rows.length===8,everyMountHasOpenSector:rows.every(q=>q.open>0),
    everyMountHasMaskedSector:rows.every(q=>q.blocked>0),sourceDerived:BUNKER_REGISTRATION.occluders.length>0,
    mechanicalLimits:ciws.every(q=>E[q.profileId].trainHalfRad<Math.PI),rendererIndependent:BUNKER_REGISTRATION.liveMeshReads===false};
  return {schema:'AEGIS_CG52_MASKS_AUDIT_V1',checks,rows,pass:Object.values(checks).every(Boolean)};
}
if(IS_BUNKER){
  Object.assign(window.__NAVAL_SIM_DIAG__,{
    bunkerProfileAudit,bunkerMasksAudit,bunkerMountInventorySnapshot,bunkerRadarAudit,
    bunkerAuxNavSnapshot,bunkerRenderState:get3DRenderState,bunkerCiwsMuzzleLocal,bunkerGunInventory:()=>bunkerExportGunInventory(),
    bunkerSelectGun:id=>{const g=ACTIVE_SHIP_RUNTIME.weapons.gunMounts.get(id);if(!g)return {ok:false};
      ACTIVE_SHIP_RUNTIME.weapons.selectedGunId=id;ACTIVE_SHIP_RUNTIME.weapons.mainGun=g;return {ok:true,id};},
    bunkerGunClearance:(id,az,el=0)=>bunkerGunClearance(ACTIVE_SHIP_RUNTIME.weapons.gunMounts.get(id).spec,az,el),
    bunkerSpgMask:(id,az,alt,range)=>bunkerSpgMask(SPG62_ILLUMINATORS.find(q=>q.id===id),az,alt,range),
    bunkerEwEmitter:(x,y,z)=>bunkerEwEmitter(x,y,z)});
  window.__NAVAL_SIM_DIAG__.bunkerEwPathProbe=(bodyTarget={x:0,y:10000,z:10})=>{
    const point=shipGameFrameV1().pointToWorld(bodyTarget),receptor={x:metersToWorld(point.x),y:metersToWorld(point.y),z:point.z},
      profile={rfBandTag:'X',receiveApertureM2:.006,receiverNoiseBandwidthHz:12e6,receiverNoiseFigureDb:6};
    return {emitter:bunkerEwEmitter(receptor.x,receptor.y,receptor.z),
      noise:asmNoiseJammerAtSeeker(receptor,profile),deception:asmDeceptionJammerAtSeeker(receptor,profile)};
  };
}
