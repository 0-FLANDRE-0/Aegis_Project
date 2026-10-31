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
window.__GUN_B2__=Object.freeze({spec:GUN_B2_SPEC,configure:gunB2Configure,snapshot:()=>({flags:{...gunB2Flags},refreshAttempts:gunB2Diagnostics.refreshAttempts,refreshMs:gunB2Diagnostics.refreshMs,releases:gunB2Diagnostics.releases.map(r=>({...r,originM:{...r.originM}}))})});
