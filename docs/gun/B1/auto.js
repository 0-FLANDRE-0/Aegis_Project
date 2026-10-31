// Own-ship mount autonomy only. No NPC context, SAM doctrine or EMCON write.
let gunB1AutoStates=new WeakMap(),gunB1ManualReservations=new WeakSet();
const gunB1Log=[];
function gunB1Note(kind,data={}){gunB1Log.push({step:simStepCounter,kind,...data});if(gunB1Log.length>GUN_B1_SPEC.diagnosticLogLimit)gunB1Log.shift();}
function gunB1AutoState(){const r=ACTIVE_SHIP_RUNTIME,epoch=ENGAGEMENT_RUNTIME.world.presentationEpoch??0;let s=gunB1AutoStates.get(r);if(!s||s.epoch!==epoch||simStepCounter<s.lastStep){s={enabled:true,epoch,lastStep:simStepCounter,mounts:new Map()};gunB1AutoStates.set(r,s);}s.lastStep=simStepCounter;return s;}
function gunB1ResetAuto(){gunB1AutoStates=new WeakMap();gunB1ManualReservations=new WeakSet();}
function gunB1OwnGuns(){return [...(ACTIVE_SHIP_RUNTIME.weapons.gunMounts??new Map([['MAIN',ACTIVE_SHIP_RUNTIME.weapons.mainGun]]))].filter(([,g])=>g?.solveAirTrack);}
function gunB1SetAuto(enabled){const s=gunB1AutoState();s.enabled=!!enabled;for(const[id,g]of gunB1OwnGuns()){const a=s.mounts.get(id);if(a?.owned){g.clear();a.owned=false;a.reason=enabled?null:'AUTO_OFF';}if(a)a.nextStep=simStepCounter;}gunB1Note('AUTO_SWITCH',{enabled:s.enabled});return s.enabled;}
function gunB1ManualIntent(g){const s=gunB1AutoState();for(const[id,q]of gunB1OwnGuns())if(q===g){const a=s.mounts.get(id);if(a?.owned){g.clear();a.owned=false;}if(a){a.nextStep=simStepCounter;a.reason='MANUAL_PRIORITY';}}}
function gunB1IsAutoOwned(g){const s=gunB1AutoState();for(const[id,q]of gunB1OwnGuns())if(q===g){const a=s.mounts.get(id);return !!a?.owned&&g.snapshot().commandTrackId===a.targetId;}return false;}
function gunB1ReserveManual(g,enabled){if(enabled){if(!gunB1ManualReservations.has(g)){gunB1ManualIntent(g);gunB1ManualReservations.add(g);}}else gunB1ManualReservations.delete(g);}
function gunB1AutoTick(){
 const s=gunB1AutoState();if(!s.enabled)return;
 for(const[id,g]of gunB1OwnGuns()){
  let a=s.mounts.get(id);if(!a){a={owned:false,targetId:null,reason:null,nextStep:simStepCounter};s.mounts.set(id,a);}
  const q=g.snapshot(),manual=gunB1ManualReservations.has(g)||q.pendingSingleFire.active||(q.continuousFire.active&&(!a.owned||q.continuousFire.trackId!==a.targetId));
  if(manual){a.owned=false;a.reason='MANUAL_PRIORITY';a.nextStep=simStepCounter;continue;}
  if(simStepCounter<a.nextStep)continue;a.nextStep=simStepCounter+Math.max(1,Math.round(g.spec.fireControl.solutionRefreshIntervalS/SIM_FIXED_DT));
  const stop=reason=>{if(a.owned)g.clear();a.owned=false;a.targetId=null;a.reason=reason;};
  if(shipEquipmentOfflineV1()||wip13b1GunHardwareHealth(g.spec)<=.02){stop('GUN_OFFLINE');continue;}
  if((q.magazine.MFF_127_SIM??0)<=0){stop('MFF_EMPTY');continue;}
  const rows=[];
  for(const[tid,tr]of tracks){
   if(!gunB1AirPolicy(tr,true).ok||!gunB1AirReady(tr).ok)continue;
   const dx=worldToMeters(tr.x-aircraft.x()),dy=worldToMeters(tr.y-aircraft.y()),rangeM=Math.hypot(dx,dy);if(rangeM>GUN_B1_SPEC.autoRangeM)continue;
   const solution=g.solveAirTrack(tid,'MFF_127_SIM',{seedSolution:a.targetId===tid?q.solution:null});if(!solution.ok||!gunB1AirReleaseGate(tid,solution,{module:g.spec,automatic:true}).ok)continue;
   const vx=worldSpeedToMps(tr.vx??0)-worldSpeedToMps(shipNav.vx??0),vy=worldSpeedToMps(tr.vy??0)-worldSpeedToMps(shipNav.vy??0),closure=-(dx*vx+dy*vy)/Math.max(1,rangeM),ttc=closure>0?rangeM/closure:Infinity;rows.push({id:tid,ttc,solution});
  }
  rows.sort((a,b)=>a.ttc-b.ttc||a.id-b.id);let best=rows[0];const current=rows.find(r=>r.id===a.targetId);if(current&&best&&(current.ttc<=best.ttc+GUN_B1_SPEC.autoTtcHysteresisS||!Number.isFinite(best.ttc)))best=current;
  if(!best){stop('NO_AUTHORIZED_AIR_TRACK');continue;}
  if(q.loadedAmmoId!=='MFF_127_SIM'){const f=g.selectAmmo('MFF_127_SIM');if(!f.ok){a.reason=f.reason;continue;}}
  if(!a.owned||a.targetId!==best.id||!q.continuousFire.active){
   const c=g.command(best.id,'MFF_127_SIM');if(!c.ok){stop(c.reason);continue;}
   const f=g.startContinuousFire(best.id,{mode:'MANUAL',ammoId:'MFF_127_SIM'});if(!f.ok){stop(f.reason);continue;}
   a.owned=true;a.targetId=best.id;a.reason=null;gunB1Note('AUTO_CUE',{mount:id,trackId:best.id,ttcS:Number.isFinite(best.ttc)?best.ttc:null});
  }else a.reason=null;
 }
}
function gunB1AutoSnapshot(){const s=gunB1AutoState();return {enabled:s.enabled,rangeM:GUN_B1_SPEC.autoRangeM,mounts:[...s.mounts].map(([id,a])=>({id,...a})),log:gunB1Log.map(x=>({...x}))};}
function gunB1MigrateSave(src,migrations){
 const migrate=(profileId,owner,rows)=>{const profile=SHIP_PROFILE_REGISTRY[profileId];if(!profile||!Array.isArray(rows))return;
  for(const q of rows){const install=(profile.weapons.gunMounts??[profile.weapons.mainGun]).find(i=>(i.id??'MAIN')===q?.id||i.hardpointId===q?.hardpointId);if(!install||q.hardpointId!==install.hardpointId)continue;const spec=SHIP_GUN_MODULE_REGISTRY_V48_WIP13B8[install.moduleId];if(!spec?.ammunition.MFF_127_SIM)continue;
   if(profileId==='CG_52_LATE_TICONDEROGA'&&q.moduleId==='MK45_MOD2_MK160_SURFACE_V1')q.moduleId=spec.id;
   if(q.magazine&&!Object.hasOwn(q.magazine,'MFF_127_SIM')&&Object.keys(q.magazine).length===2&&Number.isInteger(q.magazine.HE_127_SIM)&&q.magazine.HE_127_SIM>=0&&q.magazine.HE_127_SIM<=360){const n=Math.floor(q.magazine.HE_127_SIM*GUN_B1_SPEC.mffShareOfHe);q.magazine.HE_127_SIM-=n;q.magazine.MFF_127_SIM=n;migrations.push({id:'GUN_B1_MFF_ALLOCATION',owner,mount:q.id,policy:'SPLIT_REMAINING_HE_PRESERVE_TOTAL_AND_SAP',mffRounds:n});}
  }
 };
 migrate(src.profileId,src.shipId,src.ship?.inventory?.gunMounts);
 for(const r of src.fleet?.ships??[])migrate(r.profileId,r.entityId,r.ship?.inventory?.guns);
}

function gunB1AutoReasonText(){const s=gunB1AutoState();if(!s.enabled)return '';const codes=[...new Set([...s.mounts.values()].map(m=>m.reason))];return codes.filter(c=>['MFF_EMPTY','GUN_OFFLINE','FEED_CYCLING','MANUAL_PRIORITY'].includes(c)).map(c=>({MFF_EMPTY:'MFF 소진 · 자동 대공 중지',GUN_OFFLINE:'함포 운용 불가',FEED_CYCLING:'급탄 중',MANUAL_PRIORITY:'수동 사격 우선'}[c])).join(' · ');}
