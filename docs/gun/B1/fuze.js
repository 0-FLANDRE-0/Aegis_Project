// PHYSICAL EFFECT ONLY. This file is not an observation or fire-control source.
// All GUN_B1 shell/fragment parameters are fictional game settings.
// Native tick order: AIR/Harpoon/NPC ordnance have already moved; ASM, own SAM/RAM and HELO have not.
// Reconstruct the linear swept interval start only for the former, without changing any entity.
function gunB1PhysicalAir(dt=0){
 const rows=[],seen=new Set(),add=(kind,o,si=false,atStepEnd=false)=>{if(!o||seen.has(o)||o.dead===true||o.alive===false)return;seen.add(o);const p=si?o.positionM:{x:worldToMeters(o.x),y:worldToMeters(o.y),z:Number(o.z)||0},v=si?(kind==='HARPOON'?o.velocityMps:o.groundVelocityMps):{x:worldSpeedToMps(o.vx??0),y:worldSpeedToMps(o.vy??0),z:Number(o.vz)||0};if(p&&v&&[p.x,p.y,p.z,v.x,v.y,v.z].every(Number.isFinite))rows.push({kind,object:o,positionM:atStepEnd?{x:p.x-v.x*dt,y:p.y-v.y*dt,z:p.z-v.z*dt}:{...p},velocityMps:{...v}});};
 for(const o of enemyMissiles)add('ASM',o);for(const o of targetPool)add('AIR',o,false,true);for(const o of missiles)add('SAM',o);for(const o of ramMissiles)add('RAM',o);for(const o of harpoonWorldA())add('HARPOON',o,true,true);
 for(const r of physicalShipsB()){for(const o of r.weapons.executionD?.sam??[])add('SAM',o,false,true);for(const o of r.weapons.executionD?.ram??[])add('RAM',o,false,true);}
 for(const o of ENGAGEMENT_RUNTIME.world.entities.helicopters?.values()??[])if(heloAirborneE(o))add('HELO',o,true);return rows;
}
function gunB1Uniform(p){p.mffB1.rng=_xorshift32(p.mffB1.rng);return (p.mffB1.rng>>>0)/4294967296;}
function gunB1ArmShell(p){const n=Number(String(p.id).split('-').at(-1))||1;p.mffB1={programmedTofS:p.solutionTimeOfFlightS,etTimeS:Number.isFinite(p.solutionTimeOfFlightS)?p.solutionTimeOfFlightS+GUN_B1_SPEC.etMarginS:null,rng:_mix32((SIM_SEED_BASE>>>0)^Math.imul(n,0x9e3779b1)^GUN_B1_SPEC.clutterSeedSalt)||1,clutterExposure:0};p.mffB1.clutterBudget=-Math.log(Math.max(1e-12,1-gunB1Uniform(p)));}
function gunB1ShellEvent(p,prev,next,dt){
 if(!p.mffB1)return null;const cfg=GUN_B1_SPEC,f=p.mffB1,d=Math.hypot(next.x-prev.x,next.y-prev.y,next.z-prev.z),armedFrom=d>0?clamp((cfg.armDistanceM-p.flightDistanceM)/d,0,1):p.flightDistanceM>=cfg.armDistanceM?0:1;
 if(p.flightDistanceM+d<cfg.armDistanceM)return null;
 let event=null;const offer=q=>{if(q&&q.t>=armedFrom-1e-12&&q.t<=1&&(!event||q.t<event.t))event=q;};
 for(const row of gunB1PhysicalAir(dt)){
  const a={x:prev.x-row.positionM.x,y:prev.y-row.positionM.y,z:prev.z-row.positionM.z},delta={x:next.x-prev.x-row.velocityMps.x*dt,y:next.y-prev.y-row.velocityMps.y*dt,z:next.z-prev.z-row.velocityMps.z*dt},den=delta.x**2+delta.y**2+delta.z**2,t=den>0?clamp(-(a.x*delta.x+a.y*delta.y+a.z*delta.z)/den,armedFrom,1):armedFrom,
   missM=Math.hypot(a.x+delta.x*t,a.y+delta.y*t,a.z+delta.z*t);
  if(missM<=cfg.proxRadiusM)offer({t,reason:'MFF_PROXIMITY',triggerKind:row.kind,triggerId:row.object.id,missM});
 }
 if(f.etTimeS!=null&&p.ageS+dt>=f.etTimeS)offer({t:Math.max(armedFrom,(f.etTimeS-p.ageS)/dt),reason:'MFF_ET_BACKUP'});
 const midAlt=Math.max(0,lerp(prev.z,next.z,(armedFrom+1)*.5)),speed=Math.hypot(p.velocityMps.x,p.velocityMps.y,p.velocityMps.z),incidence=Math.abs(p.velocityMps.z)/Math.max(1,speed),hazard=cfg.clutterHazardPerS*Math.exp(-midAlt/cfg.clutterAltitudeScaleM)*(cfg.clutterIncidenceFloor+(1-cfg.clutterIncidenceFloor)*incidence),exposure=hazard*dt*(1-armedFrom),before=f.clutterExposure;f.clutterExposure+=exposure;
 if(f.clutterExposure>=f.clutterBudget&&exposure>0)offer({t:armedFrom+(1-armedFrom)*clamp((f.clutterBudget-before)/exposure,0,1),reason:'MFF_SEA_CLUTTER'});
 return event;
}
function gunB1Detonate(p,event,dt){
 p.alive=false;p.retiredReason=event.reason;const at={...p.positionM},vf=_wip88GurneyFragmentSpeed(GUN_B1_SPEC.fragments),results=[];
 for(const row of gunB1PhysicalAir(dt)){
  const v=p.velocityMps,tv=row.velocityMps,rel={x:row.positionM.x+tv.x*dt*event.t-at.x,y:row.positionM.y+tv.y*dt*event.t-at.y,z:row.positionM.z+tv.z*dt*event.t-at.z},distanceM=Math.hypot(rel.x,rel.y,rel.z);if(distanceM>GUN_B1_SPEC.fragmentQueryRadiusM)continue;
  const flight=distanceM/Math.max(1,vf),arrival=_wip99FragmentArrivalGeometry(rel.x,rel.y,rel.z,tv.x-v.x,tv.y-v.y,tv.z-v.z,0,flight),kin=_wip88InterceptKinematics(v.x,v.y,v.z,tv.x,tv.y,tv.z),detail=gunB1FragmentationPk(arrival.missM,'MFF_127_SIM',row.object.label??'Kh-35U',kin);let result;
  if(row.kind==='ASM')result=applyInterceptResult(detail.pk,row.object,'5in MFF',p.trackId);
  else if(row.kind==='HELO')result='DEFERRED_HELO_DAMAGE';
  else if(simRandom()<detail.pk){
   if(row.kind==='SAM'){row.object.dead=true;row.object._deathReason='MFF_FRAGMENT_HIT';}
   else if(row.kind==='HARPOON')harpoonFinishA(row.object,'MFF_FRAGMENT_HIT');
   else{row.object.alive=false;if(row.kind==='AIR')retireTruthAssociationV27('AIR',row.object.id,'INTERCEPT_KILL');}
   result='KILL';
  }else result='MISS';
  results.push({kind:row.kind,id:row.object.id,distanceM,arrivalMissM:arrival.missM,result,pk:detail.pk});
  if(row.kind==='ASM'&&['KILL','STRUCT_FAIL','DAMAGED'].includes(result)){wip173RecordInterceptBurst({id:p.id,x:metersToWorld(at.x),y:metersToWorld(at.y),z:at.z,vx:mpsToWorldSpeed(v.x),vy:mpsToWorldSpeed(v.y),vz:v.z,assignedTargetId:p.trackId,_fuzeBurstMissM:distanceM},'MFF_127_SIM',row.object,result);}
 }
 const record={projectileId:p.id,ammoId:p.ammoId,trackId:p.trackId,outcome:event.reason,ageS:p.ageS,positionM:at,triggerKind:event.triggerKind??null,triggerId:event.triggerId??null,missM:event.missM??null,programmedTofS:p.mffB1.programmedTofS,results};mainGunImpactLogWip13B3.push(record);if(mainGunImpactLogWip13B3.length>128)mainGunImpactLogWip13B3.shift();gunB1Note('AIRBURST',record);
 wip173PushVisualEvent('SHELL_AIRBURST',{coordSpace:'WORLD',x:metersToWorld(at.x),y:metersToWorld(at.y),z:at.z,vxMps:p.velocityMps.x,vyMps:p.velocityMps.y,vzMps:p.velocityMps.z,massKg:p.massKg,explosiveMassKg:GUN_B1_SPEC.fragments.explosiveMassKg,sourceId:p.id,weaponType:p.ammoId});
}
