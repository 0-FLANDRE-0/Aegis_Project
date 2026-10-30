// Operational ammunition persists; flying bodies, tracks, consent and AI memory reset.
function exportWeaponInventoryD(r){return {schema:'AEGIS_WEAPON_INVENTORY_D_1',
 vls:jsonSafeCloneV48Wip11A(r.weapons.vls),selectedGunId:r.weapons.selectedGunId,
 guns:[...r.weapons.gunMounts].map(([id,g])=>{const s=g.snapshot();return {id,moduleId:g.spec.id,hardpointId:g.installation.hardpointId,magazine:{...s.magazine},loadedAmmoId:s.loadedAmmoId,shotsFired:s.shotsFired};}),
 closeIn:r.weapons.closeIn.map(m=>({id:m.id,type:m.type,ammo:m.ammo,maxAmmo:m.maxAmmo,reloadTimer:m.reloadTimer??0})),
 harpoon:{schema:'MK141_INVENTORY_A1',selectedTubeId:r.weapons.harpoon.selectedTubeId,tubes:r.weapons.harpoon.tubes.map(t=>({id:t.id,loaded:t.loaded}))}};}
function validateWeaponInventoryD(r,q,errors){
 if(q==null)return; // Explicit migration of B/C saves, whose enemy weapons were inactive.
 const err=x=>errors.push('FLEET_WEAPON_D_'+x),integer=(x,max)=>Number.isSafeInteger(x)&&x>=0&&x<=max;
 if(q.schema!=='AEGIS_WEAPON_INVENTORY_D_1'){err('SCHEMA');return;}
 for(const section of ['fwd','aft']){const rows=q.vls?.[section],expected=r.weapons.vls[section];if(!Array.isArray(rows)||rows.length!==expected.length){err('VLS_LENGTH');continue;}
  rows.forEach((c,i)=>{const p=expected[i];if(!c||c.row!==p.row||c.col!==p.col||!['EMPTY','SM2','SM2ER','SM6','ESSM4'].includes(c.type)||typeof c.destroyed!=='boolean'||!integer(c.essmCount,4)||c.type!=='ESSM4'&&c.essmCount!==0)err('VLS_SLOT');
   if(c?.incident){let count=0;const valid=v=>++count<500&&(v==null||typeof v==='boolean'||typeof v==='string'||typeof v==='number'&&Number.isFinite(v)||typeof v==='object'&&Object.values(v).every(valid));if(!valid(c.incident))err('VLS_INCIDENT');}
  });
 }
 if(!r.weapons.gunMounts.has(q.selectedGunId)||!Array.isArray(q.guns)||q.guns.length!==r.weapons.gunMounts.size){err('GUN_COUNT');return;}
 const seen=new Set();for(const row of q.guns){const g=r.weapons.gunMounts.get(row?.id);if(!g||seen.has(row.id)){err('GUN_ID');continue;}seen.add(row.id);const keys=Object.keys(g.spec.magazine.initialRounds);
  if(row.moduleId!==g.spec.id||row.hardpointId!==g.installation.hardpointId||!row.magazine||Object.keys(row.magazine).length!==keys.length||keys.some(k=>!integer(row.magazine[k],g.spec.magazine.initialRounds[k]))||!keys.includes(row.loadedAmmoId)||!integer(row.shotsFired,Number.MAX_SAFE_INTEGER))err('GUN_STATE');
 }
 if(!Array.isArray(q.closeIn)||q.closeIn.length!==r.weapons.closeIn.length)err('CIWS_COUNT');else {const ids=new Set();for(const row of q.closeIn){const m=r.weapons.closeIn.find(m=>m.id===row?.id);if(!m||ids.has(row.id)||row.type!==m.type||row.maxAmmo!==m.maxAmmo||!integer(row.ammo,m.maxAmmo)||!Number.isFinite(row.reloadTimer)||row.reloadTimer<0)err('CIWS_STATE');ids.add(row?.id);}}
 harpoonValidateA(q,errors,r.weapons.harpoon.tubes);
}
function restoreWeaponInventoryD(r,q){
 if(!q)return;for(const section of ['fwd','aft'])for(let i=0;i<q.vls[section].length;i++)Object.assign(r.weapons.vls[section][i],jsonSafeCloneV48Wip11A(q.vls[section][i]));
 for(const row of q.guns)r.weapons.gunMounts.get(row.id).restoreInventory(row);
 r.weapons.selectedGunId=q.selectedGunId;r.weapons.mainGun=r.weapons.gunMounts.get(q.selectedGunId);
 for(const row of q.closeIn)Object.assign(r.weapons.closeIn.find(m=>m.id===row.id),{ammo:row.ammo,reloadTimer:row.reloadTimer});
 const h=r.weapons.harpoon;h.selectedTubeId=q.harpoon.selectedTubeId;h.pending=null;h.launches.length=0;h.routeDraft={editing:false,pointsM:[]};
 for(const t of h.tubes){t.loaded=q.harpoon.tubes.find(q=>q.id===t.id).loaded;t.capOpen01=t.loaded?0:1;}r.mass.markWeaponsDirty('OWNER_INVENTORY_RESTORE_D');
}
function ownerWeaponRenderD(r){const e=r.weapons.executionD,gun=r.weapons.closeIn.find(m=>m.type==='GUN'),ram=r.weapons.closeIn.find(m=>m.type==='RAM'),state=m=>m?{azRelRad:m._bodyYawV1??0,elRad:m.turretEl??0,firing:!!m.firing,tracking:!!e?.closeInPending,state:m.firing?'FIRE':e?.closeInPending?'TRACK':'IDLE'}:null;
 return {harpoonInventory:{tubes:r.weapons.harpoon.tubes.map(t=>({...t}))},ciws:{phalanx:state(gun),seaRam:state(ram)},illum:{spg62Mounts:(r.combatSystem.fireControl.spg62Servo?.mounts??[]).map(v=>({...v,azWorldRad:angNorm(r.navigation.heading+v.azRad)}))},
 mountInventory:{guns:[...r.weapons.gunMounts.values()].map(g=>g.snapshot()),closeIn:r.weapons.closeIn.map(m=>({hardpointId:m.installation?.hardpointId,...state(m),type:m.type}))},
 vls:{cells:Object.entries(r.weapons.vls).flatMap(([section,cells])=>cells.map(c=>({section,row:c.row,col:c.col,state:c.destroyed?'DESTROYED':c.type==='EMPTY'?'EMPTY':'READY',fire:c.incident?.fire??0})))}};
}

function ownerTerminalRenderD(r){return wip12bTerminalEventsSnapshot().filter(q=>q.targetEntityId===r.entityId).map(q=>({...q,coordinateSpace:'TARGET_LOCAL_METRES'}));}
function ownerArmorRenderD(r){const q=wip12fArmorPatchSnapshot();return {...q,patches:q.patches.filter(p=>p.targetEntityId===r.entityId)};}
function ownerHarpoonPointRenderD(id,p){const r=ENGAGEMENT_RUNTIME.ships.get(id)??ACTIVE_SHIP_RUNTIME,q=shipBodyFrameB(r).pointToWorld(p);return {xM:q.x,yM:q.z,zM:q.y};}
function syncOwnerHarpoonCapsD(v,st){for(const t of st.harpoonInventory?.tubes??[]){const cap=v.harpoonCapsA?.get(t.id);if(cap){cap.door.quaternion.setFromAxisAngle(cap.hinge,-1.8*(t.capOpen01??0));cap.rear.visible=t.loaded;}}}
function ownTerminalRenderD(){return wip12bTerminalEventsSnapshot().filter(q=>q.coordinateSpace!=='SHIP_LOCAL_METRES'||q.targetEntityId==='OWN_SHIP'||q.targetEntityId===ACTIVE_SHIP_RUNTIME.entityId);}
