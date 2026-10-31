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
function gunB2Pointing(spec,solution,az,el){
 if(!gunB2Flags.airWindow||!solution?.airDomain)return wip13b6GunPointingAssessment(spec,solution,az,el);
 const half=GUN_B1_SPEC.proxRadiusM*GUN_B2_SPEC.airWindow.radiusFraction,cov=solution.trackCovariance??{},tof=Number(solution.timeOfFlightS)||0,sigmaCross=Math.max(0,Number(solution.fireControlTrackQuality?.predictedImpactSigmaM?.cross)||0),sigmaVertical=Math.hypot(Number(cov.zSigmaM)||0,tof*(Number(cov.vzSigmaMps)||0)),uncertainty=Math.max(sigmaCross,sigmaVertical),floor=Math.max(.5,Number(spec.fireControl.maxPointingMissM)||1.5),limitM=Math.max(floor,half-uncertainty),impactWindow={schema:'AEGIS_GUN_B2_AIR_WINDOW',basis:'FUZE_RADIUS_FRACTION_SYMMETRIC',crossHalfM:half,verticalUpM:half,verticalDownM:half,uncertaintyM:uncertainty,effectiveHalfM:limitM,truthUsed:false};
 if(!solution.ok||![solution.azimuthRad,solution.elevationRad,solution.rangeM,az,el].every(Number.isFinite))return {ok:false,reason:'NO_FIRING_SOLUTION',limitM,predictedMissM:Infinity,impactWindow};
 const actual=shipGameAimWorldV1(az,el),azError=angNorm(actual.az-solution.azimuthRad),elError=actual.el-solution.elevationRad,rangeM=Math.max(1,solution.rangeM),slope=Math.max(1,Math.abs(solution.verticalSlopeMPerRad||rangeM)),crossMissM=Math.sin(azError)*Math.cos(solution.elevationRad)*rangeM,verticalMissM=elError*slope,predictedMissM=Math.hypot(crossMissM,verticalMissM),normalizedMiss=predictedMissM/Math.max(.1,limitM),releaseAimMargin01=GUN_B2_SPEC.airWindow.releaseAimMargin01,desired=shipGameVectorV1(solution.azimuthRad,solution.elevationRad),mounted=shipGameVectorV1(actual.az,actual.el),pointingErrorRad=Math.acos(clamp(desired.x*mounted.x+desired.y*mounted.y+desired.z*mounted.z,-1,1)),ok=normalizedMiss<=releaseAimMargin01;
 return {ok,reason:ok?null:'MOUNT_NOT_ON_SOLUTION',limitM,predictedMissM,crossMissM,verticalMissM,verticalLimitM:limitM,normalizedMiss,releaseAimMargin01,predictedCrossSigmaM:sigmaCross,impactWindow,pointingErrorRad,pointingErrorDeg:pointingErrorRad*180/Math.PI,actualWorldAzRad:actual.az,actualWorldElevationRad:actual.el};
}
function gunB2ReleaseInputs(state,id,spec,hp,environment){
 const tr=tracks.get(Number(id)),offset=spec.mount.trunnionOffsetM,az=state.bodyAzRad,origin=shipGamePointStateV1({x:hp.x+offset.x*Math.cos(az)-offset.y*Math.sin(az),y:hp.y+offset.x*Math.sin(az)+offset.y*Math.cos(az),z:hp.z+offset.z});
 // Value snapshot, not mutable track/pose references. A same-tick observation,
 // covariance, ownship trunnion/velocity or weather change invalidates reuse.
 return [origin.xM,origin.yM,origin.zM,origin.vxMps,origin.vyMps,origin.vzMps,tr?.x,tr?.y,tr?.z,tr?.vx,tr?.vy,tr?.vz,tr?._lastMeasurementStep,tr?.sensorAge,tr?.confirmed,tr?.sensorSource,tr?.identity,tr?._operatorIdentity,...Array.from(tr?._kfX??[]),...Array.from(tr?._kfP??[]),JSON.stringify(environment)];
}
function gunB2PrepareRelease(state,id,ammoId,solve,spec,hp){
 if(!gunB2Flags.alignment||!state.solution?.airDomain)return null;
 // Solve only when the mount is ready to release on its current demand.
 // A fresh demand can move; the normal pointing/clearance checks run again.
 if(!gunB2Pointing(spec,state.solution,state.bodyAzRad,state.elevationRad).ok)return null;
 const at=performance.now(),environment=maritimeEnvironmentSnapshotWip13A3(),inputs=gunB2ReleaseInputs(state,id,spec,hp,environment),cached=gunB2ReleaseCache.get(state),key=[simStepCounter,id,ammoId,state.bodyAzRad,state.elevationRad].join('|');
 if(cached?.key===key&&cached.solution===state.solution&&cached.inputs.length===inputs.length&&inputs.every((value,index)=>Object.is(value,cached.inputs[index])))return cached.failure;
 const fresh=solve(id,ammoId,{seedSolution:state.solution,environment});
 gunB2Diagnostics.refreshAttempts++;gunB2Diagnostics.refreshMs+=performance.now()-at;
 const failure=fresh.ok?null:fresh;
 if(fresh.ok){state.solution=fresh;state.solutionRefreshRemainingS=spec.fireControl.solutionRefreshIntervalS;state.revision++;}
 gunB2ReleaseCache.set(state,{key,inputs,failure,solution:state.solution});
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
function gunB2Roots(a,b,c){
 if(Math.abs(a)<1e-14)return Math.abs(b)>1e-14?[-c/b]:[];
 const d=b*b-4*a*c;if(d<0)return [];const s=Math.sqrt(Math.max(0,d));return [(-b-s)/(2*a),(-b+s)/(2*a)];
}
function gunB2TextSalt(text){let value=0;for(const c of String(text))value=_mix32(value^c.charCodeAt(0));return value;}
function gunB2FuzeIntervals(r,d,axis,armedFrom,radius){
 const norm=v=>v.x*v.x+v.y*v.y+v.z*v.z,dot=(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z,cfg=GUN_B2_SPEC.fuze,lo=deg(cfg.polarCenterDeg-cfg.polarHalfWidthDeg),hi=deg(cfg.polarCenterDeg+cfg.polarHalfWidthDeg),rr=norm(r),dd=norm(d),rd=dot(r,d),ar=-dot(r,axis),ad=-dot(d,axis),cuts=[armedFrom,1];
 const add=values=>{for(const t of values)if(t>armedFrom&&t<1)cuts.push(t);};
 const sphereRoots=gunB2Roots(dd,2*rd,rr-radius*radius),endInside=Math.hypot(r.x+d.x,r.y+d.y,r.z+d.z)<=radius,inSphere=sphereRoots.some(t=>t>=armedFrom&&t<=1)||Math.sqrt(rr)<=radius||endInside;
 // Exact broad phase: the caller discards intervals whenever inSphere=false.
 if(!inSphere)return {intervals:[],inSphere:false,endInside:false};
 add(sphereRoots);
 for(const angle of [lo,hi]){const c=Math.cos(angle)**2;add(gunB2Roots(ad*ad-c*dd,2*(ar*ad-c*rd),ar*ar-c*rr));}
 if(Math.abs(ad)>1e-14)add([-ar/ad]);cuts.sort((a,b)=>a-b);const intervals=[];
 for(let i=1;i<cuts.length;i++){const a=cuts[i-1],b=cuts[i];if(b-a<1e-12)continue;const t=(a+b)*.5,x={x:r.x+d.x*t,y:r.y+d.y*t,z:r.z+d.z*t},n=Math.sqrt(norm(x)),theta=Math.acos(clamp((-dot(x,axis))/Math.max(1e-12,n),-1,1));if(n<=radius+1e-9&&theta>=lo-1e-10&&theta<=hi+1e-10)intervals.push([a,b]);}
 return {intervals,inSphere,endInside};
}
function gunB2FuzeSignal(row,p,prev,next,dt,t){
 const cfg=GUN_B2_SPEC.fuze,target={...row.object,x:metersToWorld(row.positionM.x+row.velocityMps.x*dt*t),y:metersToWorld(row.positionM.y+row.velocityMps.y*dt*t),z:row.positionM.z+row.velocityMps.z*dt*t},at={x:lerp(prev.x,next.x,t),y:lerp(prev.y,next.y,t),z:lerp(prev.z,next.z,t)},dx=worldToMeters(target.x)-at.x,dy=worldToMeters(target.y)-at.y,dz=target.z-at.z,r=Math.hypot(dx,dy,dz),v=p.velocityMps,vn=Math.hypot(v.x,v.y,v.z),theta=Math.acos(clamp((dx*v.x+dy*v.y+dz*v.z)/Math.max(1e-12,r*vn),-1,1)),u=(theta-deg(cfg.polarCenterDeg))/deg(cfg.polarHalfWidthDeg);
 if(Math.abs(u)>1)return 0;
 const kind={ASM:'TARGET_ASM',AIR:'TARGET_AIR',HELO:'HELICOPTER'}[row.kind]??'RF_ORDNANCE',rcs=rfReflectorRcsM2Wip13A2({x:target.x,y:target.y,z:target.z,rcsM2:target.rcsM2,_truthObject:target,_physicsKind:kind},'X',metersToWorld(at.x),metersToWorld(at.y),at.z),reference=ASM_PROFILES['Kh-35U'].rcsSide,gain=Math.cos(u*Math.PI/2)**2;
 return rcs/reference*Math.pow(GUN_B1_SPEC.proxRadiusM*cfg.referenceRadiusFraction/Math.max(.5,r),4)*gain;
}
function gunB2FuzeIntegral(row,p,prev,next,dt,a,b){
 // Five-point Gauss quadrature on analytic sphere/cone intervals; no tick draw.
 const x=[0,-.5384693101056831,.5384693101056831,-.906179845938664,.906179845938664],w=[.5688888888888889,.4786286704993665,.4786286704993665,.2369268850561891,.2369268850561891],m=(a+b)*.5,h=(b-a)*.5;let sum=0;
 for(let i=0;i<5;i++)sum+=w[i]*gunB2FuzeSignal(row,p,prev,next,dt,m+h*x[i]);return sum*h*dt;
}
function gunB2ShellEvent(p,prev,next,dt){
 if(!p.mffB1)return null;const cfg=GUN_B1_SPEC,f=p.mffB1,travel=Math.hypot(next.x-prev.x,next.y-prev.y,next.z-prev.z),armedFrom=travel>0?clamp((cfg.armDistanceM-p.flightDistanceM)/travel,0,1):p.flightDistanceM>=cfg.armDistanceM?0:1;
 if(p.flightDistanceM+travel<cfg.armDistanceM)return null;
 let event=null;const offer=q=>{if(q&&q.t>=armedFrom-1e-12&&q.t<=1&&(!event||q.t<event.t))event=q;};
 const meta=p._gunB2Fuze??(p._gunB2Fuze={contacts:new WeakMap(),pending:null,passes:0}),v=p.velocityMps,n=Math.hypot(v.x,v.y,v.z),axis={x:v.x/n,y:v.y/n,z:v.z/n},fc=GUN_B2_SPEC.fuze;
 for(const row of gunB1PhysicalAir(dt)){
  const r={x:prev.x-row.positionM.x,y:prev.y-row.positionM.y,z:prev.z-row.positionM.z},d={x:next.x-prev.x-row.velocityMps.x*dt,y:next.y-prev.y-row.velocityMps.y*dt,z:next.z-prev.z-row.velocityMps.z*dt},geometry=gunB2FuzeIntervals(r,d,axis,armedFrom,cfg.proxRadiusM);
  let state=meta.contacts.get(row.object);if(!geometry.inSphere){if(state){state.inRange=false;state.exposure=0;}continue;}
  if(!state){state={pass:0,inRange:false,exposure:0,detected:false};meta.contacts.set(row.object,state);}
  if(!state.inRange){state.pass++;state.inRange=true;state.exposure=0;state.detected=false;const seed=_mix32((SIM_SEED_BASE>>>0)^gunB2TextSalt(p.id)^gunB2TextSalt(row.kind+':'+row.object.id)^Math.imul(state.pass,0x9e3779b1)^fc.salt)||1,uniform=gunB2PrivateStream(seed).uniform();state.uniform=uniform;state.budget=-Math.log(Math.max(1e-12,1-uniform))*fc.referenceExposureS/(-Math.log(1-fc.referencePd));meta.passes++;}
  if(!state.detected)for(const [a,b]of geometry.intervals){
   const exposure=gunB2FuzeIntegral(row,p,prev,next,dt,a,b);
   if(state.exposure+exposure>=state.budget&&exposure>0){let lo=a,hi=b;for(let i=0;i<18;i++){const m=(lo+hi)*.5;if(state.exposure+gunB2FuzeIntegral(row,p,prev,next,dt,a,m)>=state.budget)hi=m;else lo=m;}const detectedAgeS=p.ageS+hi*dt,pending={ageS:detectedAgeS+fc.processingDelayS,detectedAgeS,reason:'MFF_PROXIMITY',triggerKind:row.kind,triggerId:row.object.id,exposureAtDetection:state.budget,pass:state.pass};state.detected=true;if(!meta.pending||pending.ageS<meta.pending.ageS)meta.pending=pending;break;}state.exposure+=exposure;
  }
  if(!geometry.endInside){state.inRange=false;state.exposure=0;}
 }
 if(meta.pending&&meta.pending.ageS<=p.ageS+dt+1e-12)offer({...meta.pending,t:Math.max(armedFrom,(meta.pending.ageS-p.ageS)/dt)});
 // The original ET and sea-clutter hazard/budget equations are copied exactly.
 if(f.etTimeS!=null&&p.ageS+dt>=f.etTimeS)offer({t:Math.max(armedFrom,(f.etTimeS-p.ageS)/dt),reason:'MFF_ET_BACKUP'});
 const midAlt=Math.max(0,lerp(prev.z,next.z,(armedFrom+1)*.5)),speed=Math.hypot(p.velocityMps.x,p.velocityMps.y,p.velocityMps.z),incidence=Math.abs(p.velocityMps.z)/Math.max(1,speed),hazard=cfg.clutterHazardPerS*Math.exp(-midAlt/cfg.clutterAltitudeScaleM)*(cfg.clutterIncidenceFloor+(1-cfg.clutterIncidenceFloor)*incidence),exposure=hazard*dt*(1-armedFrom),before=f.clutterExposure;f.clutterExposure+=exposure;
 if(f.clutterExposure>=f.clutterBudget&&exposure>0)offer({t:armedFrom+(1-armedFrom)*clamp((f.clutterBudget-before)/exposure,0,1),reason:'MFF_SEA_CLUTTER'});
 return event;
}
function gunB2FragmentField(kin,vf){
 const data=kin.gunB2FieldInput;if(!data)return {ok:false,reason:'FRAGMENT_GEOMETRY_REQUIRED'};
 const r=data.offsetM,w=data.relativeVelocityMps,v=data.projectileVelocityMps,vm=Math.hypot(v.x,v.y,v.z),a=w.x*w.x+w.y*w.y+w.z*w.z-vf*vf,b=2*(r.x*w.x+r.y*w.y+r.z*w.z),c=r.x*r.x+r.y*r.y+r.z*r.z,roots=gunB2Roots(a,b,c).filter(t=>t>0),timeS=roots.length?Math.min(...roots):null;
 if(timeS==null||!(vm>0))return {ok:false,reason:'NO_FRAGMENT_INTERCEPT'};
 const field={x:r.x+w.x*timeS,y:r.y+w.y*timeS,z:r.z+w.z*timeS},radiusM=Math.hypot(field.x,field.y,field.z),cosine=(field.x*v.x+field.y*v.y+field.z*v.z)/Math.max(1e-12,radiusM*vm),theta=Math.acos(clamp(cosine,-1,1)),half=deg(GUN_B2_SPEC.fragments.halfAngleDeg),angles=[Math.PI/2-half,Math.PI/2+half].map(t=>Math.atan2(vf*Math.sin(t),vm+vf*Math.cos(t))),worldMinRad=Math.min(...angles),worldMaxRad=Math.max(...angles),ok=Math.abs(theta-Math.PI/2)<=half;
 // Normalize density on the translating Gurney sphere, in the body frame.
 // World angles are diagnostics; mixing their solid angle with body radius is invalid.
 const bodySolidAngleSr=2*Math.PI*(Math.cos(Math.PI/2-half)-Math.cos(Math.PI/2+half));
 return {ok,bodySolidAngleSr,reason:ok?null:'OUTSIDE_FRAGMENT_BAND',timeS,radiusM,bodyPolarDeg:rad2deg(theta),bodyHalfWidthDeg:GUN_B2_SPEC.fragments.halfAngleDeg,worldMinRad,worldMaxRad};
}
function gunB2FragmentDetail(distance,weapon,label,kin,rel,v,tv){
 if(!gunB2Flags.fragments)return gunB1FragmentationPk(distance,weapon,label,kin);
 return gunB2FragmentationPk(distance,weapon,label,{...kin,gunB2FieldInput:{offsetM:{...rel},projectileVelocityMps:{...v},relativeVelocityMps:{x:tv.x-v.x,y:tv.y-v.y,z:tv.z-v.z}}});
}
window.__GUN_B2__=Object.freeze({spec:GUN_B2_SPEC,configure:gunB2Configure,snapshot:()=>({flags:{...gunB2Flags},refreshAttempts:gunB2Diagnostics.refreshAttempts,refreshMs:gunB2Diagnostics.refreshMs,releases:gunB2Diagnostics.releases.map(r=>({...r,originM:{...r.originM}}))})});
