// TEST ONLY: private paused page, actual spawn/acceleration/Euler update order.
window.__B2_CALIBRATE__=(count=400)=>{
 _wip75ResetCase(921001);const beforeRng=SIM_RNG_STATE,base=gunB1OwnGuns()[0][1].spec,
 module={...base,mount:{...base.mount,trunnionOffsetM:{x:0,y:0,z:0}}},ammo=module.ammunition.HE_127_SIM,hp={x:0,y:0,z:10.92},origin=shipGamePointStateV1(hp),environment={wind:{speedMps:0,directionRad:0}},
 target={xM:origin.xM+16459,yM:origin.yM,zM:0,vxMps:0,vyMps:0,vzMps:0},solution=wip13b1SolveTrackState(module,'HE_127_SIM',target,{originM:{x:origin.xM,y:origin.yM,z:origin.zM},platformVelocityMps:{x:origin.vxMps,y:origin.vyMps,z:origin.vzMps},environment});
 if(!solution.ok)throw Error('ANCHOR_SOLVE:'+solution.reason);
 function create({spread=false,mvFraction=0,angleRad=0}={}){
  __GUN_B2__.configure({dispersion:spread});const body=shipGameAimBodyV1(solution.azimuthRad,solution.elevationRad+angleRad),privateAmmo=mvFraction?{...ammo,muzzleVelocityMps:ammo.muzzleVelocityMps*(1+mvFraction)}:ammo,p=spawnMainGunProjectileWip13B3({module,ammo:privateAmmo,ammoId:'HE_127_SIM',trackId:-921,bodyAzRad:body.az,elevationRad:body.el,hardpoint:hp,solution});p.environment=environment;mainGunProjectilesWip13B3.pop();return p;
 }
 function flight(p){
  for(let i=0;i<12000;i++){
   const dt=SIM_FIXED_DT,a=wip13b5ProjectileAcceleration(p,module,ammo),prev={...p.positionM},v0={...p.velocityMps};p.velocityMps={x:v0.x+a.x*dt,y:v0.y+a.y*dt,z:v0.z+a.z*dt};const next={x:prev.x+p.velocityMps.x*dt,y:prev.y+p.velocityMps.y*dt,z:prev.z+p.velocityMps.z*dt};
   if(next.z<=0&&p.velocityMps.z<0){const u=prev.z/(prev.z-next.z),at={x:lerp(prev.x,next.x,u),y:lerp(prev.y,next.y,u),z:lerp(prev.z,next.z,u)};p.positionM=at;return {rangeM:at.x-origin.xM,crossM:at.y-origin.yM,positionM:at,timeS:(i+u)*dt};}p.positionM=next;
  }throw Error('CALIBRATION_NO_GROUND_CROSSING');
 }
 const nominal=flight(create()),plusMv=flight(create({mvFraction:.001})),minusMv=flight(create({mvFraction:-.001})),plusEl=flight(create({angleRad:.0001})),minusEl=flight(create({angleRad:-.0001})),gradients={rangePerMvFraction:(plusMv.rangeM-minusMv.rangeM)/.002,rangePerElevationRad:(plusEl.rangeM-minusEl.rangeM)/.0002};
 const saved={sea:wip13b5SeaContactFraction,terrain:wip13b5TerrainContactFraction,contact:surfaceTargetFirstAsmContactWip13A};let parity;
 try{
  wip13b5SeaContactFraction=(a,b)=>b.z<=0&&a.z>0?a.z/(a.z-b.z):null;wip13b5TerrainContactFraction=()=>null;surfaceTargetFirstAsmContactWip13A=()=>null;
  const p=create({spread:true}),ghost=structuredClone(p),expected=flight(ghost);mainGunProjectilesWip13B3.push(p);let ticks=0;while(p.alive&&ticks++<12000)updateMainGunProjectilesWip13B3(SIM_FIXED_DT);
  parity={differenceM:Math.hypot(p.positionM.x-expected.positionM.x,p.positionM.y-expected.positionM.y,p.positionM.z-expected.positionM.z),reason:p.retiredReason};
 }finally{wip13b5SeaContactFraction=saved.sea;wip13b5TerrainContactFraction=saved.terrain;surfaceTargetFirstAsmContactWip13A=saved.contact;}
 const serialStart=mainGunProjectileSerialWip13B3,samples=[];
 for(let i=0;i<count;i++){const p=create({spread:true}),initial={positionM:{...p.positionM},velocityMps:{...p.velocityMps}},f=flight(p);samples.push({id:p.id,...f,initial,dispersion:p._gunB2Dispersion});}
 const serialEnd=mainGunProjectileSerialWip13B3;mainGunProjectileSerialWip13B3=serialStart;const repeat=[];for(let i=0;i<Math.min(5,count);i++){const p=create({spread:true});repeat.push(flight(p));}mainGunProjectileSerialWip13B3=serialEnd;
 __GUN_B2__.configure({dispersion:false});const noSpread=create(),noSpreadVelocity={...noSpread.velocityMps},noSpread2=create(),unperturbedRepeatExact=JSON.stringify(noSpreadVelocity)===JSON.stringify(noSpread2.velocityMps);
 return {solution,origin,nominal,gradients,samples,repeat,parity,unperturbedRepeatExact,constants:__GUN_B2__.spec.dispersion,rngBefore:beforeRng,rngAfter:SIM_RNG_STATE,core:window.__CORE_SELFTEST_FAILURES__};
};
