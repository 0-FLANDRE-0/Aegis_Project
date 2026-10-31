// GUN_B2: fictional game model. New constants are SIM_TUNED unless annotated.
const GUN_B2_SPEC=deepFreezeShipProfileV48Wip09({
 schema:'AEGIS_GUN_B2_1',provenance:'SIM_TUNED_GAME_ONLY',
 dispersion:{mvSigmaFrac:.0015,elevSigmaMrad:.10,trainSigmaMrad:.20,salt:0xB2D15001,
  calibration:{rangeM:16459,minSigmaM:44,maxSigmaM:55,reference:'USER_SPECIFIED_DTIC_ADA331645_ANCHOR',status:'PENDING_NATIVE_CALIBRATION'}},
 airWindow:{radiusFraction:.25,releaseAimMargin01:.78},
 fuze:{polarCenterDeg:70,polarHalfWidthDeg:20,processingDelayS:.002,referenceRadiusFraction:.5,referenceExposureS:.003,referencePd:.9,salt:0xB2F02901},
 fragments:{halfAngleDeg:20,outsidePk:0}
});
let gunB2Flags=/* B2_DEFAULT_FLAGS */{alignment:true,dispersion:false,airWindow:false,fuze:false,fragments:false};
const gunB2ReleaseCache=new WeakMap();
const gunB2Diagnostics={refreshAttempts:0,refreshMs:0,releases:[]};
function gunB2Configure(flags={}){for(const k of Object.keys(gunB2Flags))if(typeof flags[k]==='boolean')gunB2Flags[k]=flags[k];return {...gunB2Flags};}
function gunB2Pointing(spec,solution,az,el){return wip13b6GunPointingAssessment(spec,solution,az,el);}
function gunB2PrepareRelease(state,id,ammoId,solve,spec){
 if(!gunB2Flags.alignment||!state.solution?.airDomain)return null;
 // Solve only when the mount is ready to release on its current demand.
 // A fresh demand can move; the normal pointing/clearance checks run again.
 if(!gunB2Pointing(spec,state.solution,state.bodyAzRad,state.elevationRad).ok)return null;
 const cached=gunB2ReleaseCache.get(state),key=[simStepCounter,id,ammoId,state.bodyAzRad,state.elevationRad].join('|');
 if(cached?.key===key&&cached.solution===state.solution)return cached.failure;
 const at=performance.now(),fresh=solve(id,ammoId,{seedSolution:state.solution});
 gunB2Diagnostics.refreshAttempts++;gunB2Diagnostics.refreshMs+=performance.now()-at;
 const failure=fresh.ok?null:fresh;
 if(fresh.ok){state.solution=fresh;state.solutionRefreshRemainingS=spec.fireControl.solutionRefreshIntervalS;state.revision++;}
 gunB2ReleaseCache.set(state,{key,failure,solution:state.solution});
 return failure;
}
function gunB2RecordRelease(projectile,solution){
 if(!gunB2Flags.alignment||!solution?.airDomain)return;
 gunB2Diagnostics.releases.push({projectileId:projectile.id,step:simStepCounter,computedStep:solution.computedStep,ageS:(simStepCounter-solution.computedStep)*SIM_FIXED_DT,originM:{...projectile.positionM},timeOfFlightS:solution.timeOfFlightS});
 if(gunB2Diagnostics.releases.length>256)gunB2Diagnostics.releases.shift();
}
function gunB2PrivateStream(seed){
 let state=(seed>>>0)||1;const uniform=()=>{state=_xorshift32(state);return (state>>>0)/4294967296;};
 return {uniform,normal:()=>Math.sqrt(-2*Math.log(Math.max(1e-12,uniform())))*Math.cos(TAU*uniform())};
}
function gunB2ApplyDispersion(p,request,trunnion){
 const cfg=GUN_B2_SPEC.dispersion,serial=Number(String(p.id).split('-').at(-1))||1,prefix=String(p.id).split('MK45-')[0];let ownerSalt=0;
 for(let i=0;i<prefix.length;i++)ownerSalt=_mix32(ownerSalt^prefix.charCodeAt(i));
 const seed=_mix32((SIM_SEED_BASE>>>0)^Math.imul(serial,0x9e3779b1)^cfg.salt^ownerSalt)||1,random=gunB2PrivateStream(seed),normal={mv:random.normal(),elev:random.normal(),train:random.normal()},v=p.velocityMps,
 r={x:v.x-trunnion.vxMps,y:v.y-trunnion.vyMps,z:v.z-trunnion.vzMps},n=Math.hypot(r.x,r.y,r.z),d={x:r.x/n,y:r.y/n,z:r.z/n},h=Math.hypot(d.x,d.y),cross=h>1e-10?{x:-d.y/h,y:d.x/h,z:0}:{x:0,y:1,z:0},up={x:d.y*cross.z-d.z*cross.y,y:d.z*cross.x-d.x*cross.z,z:d.x*cross.y-d.y*cross.x},e=Math.tan(normal.elev*cfg.elevSigmaMrad*.001),t=Math.tan(normal.train*cfg.trainSigmaMrad*.001),j={x:d.x+up.x*e+cross.x*t,y:d.y+up.y*e+cross.y*t,z:d.z+up.z*e+cross.z*t},jn=Math.hypot(j.x,j.y,j.z),speed=request.ammo.muzzleVelocityMps*(1+normal.mv*cfg.mvSigmaFrac);
 p.velocityMps={x:trunnion.vxMps+j.x/jn*speed,y:trunnion.vyMps+j.y/jn*speed,z:trunnion.vzMps+j.z/jn*speed};
 p._gunB2Dispersion={seed,normal,mvSigmaFrac:cfg.mvSigmaFrac,elevSigmaMrad:cfg.elevSigmaMrad,trainSigmaMrad:cfg.trainSigmaMrad};
}
window.__GUN_B2__=Object.freeze({spec:GUN_B2_SPEC,configure:gunB2Configure,snapshot:()=>({flags:{...gunB2Flags},refreshAttempts:gunB2Diagnostics.refreshAttempts,refreshMs:gunB2Diagnostics.refreshMs,releases:gunB2Diagnostics.releases.map(r=>({...r,originM:{...r.originM}}))})});
