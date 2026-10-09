// Ship-owned editable prelaunch program. No target truth, flight telemetry or uplink.
function harpoonRouteEditingE(){return inputMode==='AIM'&&harpoonRuntimeA().routeDraft.editing&&!harpoonRuntimeA().pending;}
function harpoonRouteToggleE(){
  const r=harpoonRuntimeA();if(!r.tubes.length||r.pending)return false;
  if(r.routeDraft.editing){r.routeDraft={editing:false,pointsM:[]};}
  else r.routeDraft.editing=true;
  harpoonUpdateUIA();return r.routeDraft.editing;
}
function harpoonRouteAddE(worldX,worldY){
  const r=harpoonRuntimeA(),cfg=HARPOON_PROFILE_A.sim;if(!harpoonRouteEditingE())return {ok:false,reason:'NOT_EDITING'};
  const point={x:worldToMeters(worldX),y:worldToMeters(worldY)},last=r.routeDraft.pointsM.at(-1)??shipGameFrameV1().pointToWorld({x:0,y:0,z:0});
  if(!Number.isFinite(point.x)||!Number.isFinite(point.y))return {ok:false,reason:'INVALID_COORDINATE'};
  if(r.routeDraft.pointsM.length>=cfg.routeMaxPoints)return {ok:false,reason:'WAYPOINT_LIMIT'};
  if(Math.hypot(point.x-last.x,point.y-last.y)<cfg.routeMinLegM){notify('하푼 경유점 간격은 2 km 이상');return {ok:false,reason:'WAYPOINT_TOO_CLOSE'};}
  r.routeDraft.pointsM.push(point);harpoonUpdateUIA();return {ok:true,count:r.routeDraft.pointsM.length};
}
function harpoonRouteProgramE(pointsM,startM){
  const cfg=HARPOON_PROFILE_A.sim;if(!Array.isArray(pointsM)||!pointsM.length||pointsM.length>cfg.routeMaxPoints)return null;
  const points=pointsM.map(p=>({x:Number(p.x),y:Number(p.y)}));if(points.some(p=>!Number.isFinite(p.x)||!Number.isFinite(p.y)))return null;
  let from=startM,pathM=0;for(const p of points){const d=Math.hypot(p.x-from.x,p.y-from.y);if(d<cfg.routeMinLegM)return null;pathM+=d;from=p;}
  const last=points.at(-1),prior=points.length>1?points.at(-2):startM,dx=last.x-prior.x,dy=last.y-prior.y,d=Math.hypot(dx,dy),
    searchCenterM={x:last.x+dx/d*cfg.routeSearchAheadM,y:last.y+dy/d*cfg.routeSearchAheadM,z:0};
  return deepFreezeShipProfileV48Wip09({schema:'HARPOON_PRELAUNCH_COORDINATE_ROUTE_E1',pointsM:points,startM:{x:startM.x,y:startM.y},
    searchCenterM,routeLengthM:pathM,plannedLengthM:pathM+cfg.routeSearchAheadM+cfg.routeTurnReserveM,
    seekerActivation:'AFTER_FINAL_INS_WAYPOINT_PLANE',dataLink:false,updatesAfterRelease:false,truthUsed:false});
}
function harpoonRouteGateE(trackId,tubeId,options={}){
  const r=harpoonRuntimeA(),spec=harpoonTubeSpecA(tubeId),tube=r.tubes.find(t=>t.id===tubeId),cfg=HARPOON_PROFILE_A.sim,
    bad=reason=>({ok:false,reason,truthUsed:false});
  if(!spec||!tube)return bad('MK141_NOT_INSTALLED');
  if(options.automatic===true||options.mode==='AUTO'||options.mode==='SEMIAUTO')return bad('MANUAL_SURFACE_AUTHORITY_REQUIRED');
  // Manual coordinate/search-area release: no invented radar contact or offboard estimate.
  // A selected protected surface file still blocks release. The onboard seeker has no IFF.
  const tr=tracks.get(Number(trackId));
  if(tr&&tr._surfaceExtentEstimateWip13B8){const a=surfaceMissileIdentityPolicyWip13C4(tr._operatorIdentity,'MANUAL',false);if(!a.ok)return bad(a.reason);}
  if(!tube.loaded)return bad('TUBE_EMPTY');if(r.pending&&!options.actualRelease)return bad('RELEASE_PENDING');
  if(r.releaseCooldownS>0&&!options.actualRelease)return bad('LAUNCHER_COOLDOWN');
  if(shipEquipmentOfflineV1())return bad('SHIP_EQUIPMENT_OFFLINE');if(getModuleDmg(spec.moduleName)>=75)return bad('MK141_LAUNCHER_DAMAGED');
  const frame=shipGameFrameV1(),muzzle=frame.pointToWorld(spec.muzzle),axis=frame.vectorToWorld(spec.axis);
  if(axis.z<.15||muzzle.z<=maritimeSeaLevelAtSimulationMetersWip13A3(muzzle.x,muzzle.y)+.7)return bad('LAUNCH_GEOMETRY_UNSAFE');
  const checked=harpoonRouteProgramE((options.routeProgram??r.routeDraft).pointsM,muzzle),program=options.routeProgram??checked;
  if(!checked)return bad('INVALID_WAYPOINT_ROUTE');if(checked.plannedLengthM>cfg.maxLaunchRangeKm*1000)return bad('ROUTE_EXCEEDS_140KM_BUDGET');
  // Fixed geographic search box, not a long extrapolation of an uncertain moving track.
  const memory=deepFreezeShipProfileV48Wip09({schema:'HARPOON_FROZEN_COORDINATE_CUE_E1',trackId:null,positionM:{...program.searchCenterM},
    velocityMps:{x:0,y:0,z:0},covariance:Array(36).fill(0),stateEpoch:'RELEASE_FIXED_COORDINATE',stateAgeS:0,observationAgeS:0,
    launchStep:simStepCounter,identity:'COORDINATE_SEARCH',truthUsed:false,updatesAfterRelease:false});
  return {ok:true,reason:null,trackId:tr?.trackId??null,tubeId,rangeKm:program.plannedLengthM/1000,memory,routeProgram:program,
    muzzleM:muzzle,axis,authority:{ok:true,mode:'MANUAL_COORDINATE_SEARCH'},truthUsed:false};
}
// Missile-owned execution: INS position and immutable program only, no ground truth.
function harpoonRouteStepE(m){
  const r=m.route;if(!r||r.completed)return;
  const now=m.navPositionM,old=r.previousInsM; r.previousInsM={x:now.x,y:now.y};
  if(m.boosterAttached||!m.tubeCleared)return;
  const points=r.program.pointsM,p=points[r.index],from=r.index?points[r.index-1]:r.program.startM,
    dx=p.x-from.x,dy=p.y-from.y,len=Math.hypot(dx,dy),ux=dx/len,uy=dy/len,
    before=(old.x-p.x)*ux+(old.y-p.y)*uy,after=(now.x-p.x)*ux+(now.y-p.y)*uy,
    f=before<=0&&after>=0?clamp(-before/Math.max(1e-9,after-before),0,1):null,
    crossing=f==null?null:{x:old.x+(now.x-old.x)*f,y:old.y+(now.y-old.y)*f},
    passed=!!crossing&&Math.hypot(crossing.x-p.x,crossing.y-p.y)<=HARPOON_PROFILE_A.sim.routePassCorridorM,
    captured=r.index<points.length-1&&Math.hypot(now.x-p.x,now.y-p.y)<=HARPOON_PROFILE_A.sim.routeCaptureM;
  if(!passed&&!captured)return;
  r.passes.push({index:r.index,ageS:m.ageS,insPositionM:{x:now.x,y:now.y},method:passed?'INS_PLANE_CROSSING':'INS_FLYBY_CAPTURE'});
  m.history.push({ageS:m.ageS,event:'INS_WAYPOINT_PASSED',index:r.index});r.index++;
  if(r.index===points.length){r.completed=true;r.completedAgeS=m.ageS;m.history.push({ageS:m.ageS,event:'FINAL_WAYPOINT_SEARCH_ENABLED'});}
}
function harpoonRouteAimE(m,fallback){return m.route&&!m.route.completed?m.route.program.pointsM[m.route.index]:fallback;}
// Prelaunch markers only. Never display flight route progress, seeker or missile position.
function harpoonDrawCicA(ctx,sym){
  const draft=harpoonRuntimeA().routeDraft;if(!draft.pointsM.length)return;
  const cfg=HARPOON_PROFILE_A.sim,origin={x:aircraft.x(),y:aircraft.y()},program=harpoonRouteProgramE(draft.pointsM,{x:worldToMeters(origin.x),y:worldToMeters(origin.y)});
  ctx.save();ctx.strokeStyle='#ffbf67';ctx.fillStyle='#ffda9a';ctx.lineWidth=tacticalLineWidthWorld(1.5,.42);ctx.setLineDash([7*sym,5*sym]);
  ctx.beginPath();ctx.moveTo(origin.x,origin.y);for(const p of draft.pointsM)ctx.lineTo(metersToWorld(p.x),metersToWorld(p.y));ctx.stroke();ctx.setLineDash([]);
  ctx.font=(10*sym)+'px monospace';ctx.textAlign='left';ctx.textBaseline='bottom';
  draft.pointsM.forEach((p,i)=>{const x=metersToWorld(p.x),y=metersToWorld(p.y);ctx.beginPath();ctx.arc(x,y,4*sym,0,Math.PI*2);ctx.stroke();ctx.fillText('H-WP'+(i+1)+(i===draft.pointsM.length-1?' · SEARCH':''),x+7*sym,y-5*sym);});
  if(program){const p=program.searchCenterM;ctx.globalAlpha=.45;ctx.setLineDash([4*sym,4*sym]);ctx.beginPath();ctx.arc(metersToWorld(p.x),metersToWorld(p.y),metersToWorld(cfg.seekerSearchBasketM),0,Math.PI*2);ctx.stroke();}
  ctx.restore();
}
