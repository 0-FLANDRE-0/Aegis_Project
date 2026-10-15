// LIVE_CANONICAL: ship aviation owns inventory/queue/doors; world owns helo poses.
// No targetPool, sensor reflector, offboard source, weapon, fuel or combat RNG path.
// All facility coordinates inherit SIM_TUNED; basis is offline source geometry.
const HELO_FACILITY_A=Object.freeze({source:'SIM_TUNED',basis:'SOURCE_C5_OFFLINE_REGISTRATION',
  doorXAtFloor:-48.224,doorSlope:1.047/6.185,doorPlaneAnchorZM:3.18,doorBottomM:2.997,doorTopM:8.43,
  bayOffsetM:5.03,doorHalfWidthM:2.24,hangarXM:-40.75,parkBayOffsetM:5.68,parkStarboardOffsetM:5.2,foldedCenterOffsetM:.367,throatClearXM:-56.5,deckXM:-65,deckZM:3.18,
  deckSlope:-1.203/24.432,deckPlaneXM:-48.228,deckPlaneZM:2.997,deckFootClearanceM:.04,
  deckMinXM:-75,deckMaxXM:-48.224,deckHalfWidthM:8.5,rotorRadiusM:HELO_VALUES_A.visualRotorDiameterM/2});
function heloSupportedA(){return ACTIVE_SHIP_RUNTIME.profileId==='DDG_119_LATE_FLIGHT_IIA';}
function heloWorldA(){return ENGAGEMENT_RUNTIME.world.entities.helicopters??(ENGAGEMENT_RUNTIME.world.entities.helicopters=new Map());}
function heloInventoryA(){return ACTIVE_SHIP_RUNTIME.aviation.inventory;}
function heloFreshA(slot){const bay=slot===0?'PORT':'STARBOARD',id=ACTIVE_SHIP_RUNTIME.entityId+':H'+(slot+1);return {
  id,ownerEntityId:ACTIVE_SHIP_RUNTIME.entityId,slot,bay,profileId:'MH60R_POINT_MASS_A1',state:'HANGARED',stateTick:0,
  visible:false,onboard:true,localM:{x:HELO_FACILITY_A.hangarXM,y:heloParkLateralC(slot),z:HELO_FACILITY_A.deckZM},
  positionM:{x:0,y:0,z:0},airVelocityMps:{x:0,y:0},groundVelocityMps:{x:0,y:0,z:0},headingRad:0,motionBearingRad:0,
  targetAltitudeM:HELO_VALUES_A.altitudeM,pitchRad:0,bankRad:0,engine01:[0,0],rotor01:0,rotorAngleRad:0,tail01:0,blades01:0,waypointM:null,departPointM:null,localYawRad:0,navigationMode:'ROUTE',route:[],routeIndex:0,holdPointM:null,followPointM:null,
  motion:{airSpeedMps:0,groundSpeedMps:0,stopDistanceM:0,braking:false,turnRateRadS:0,longitudinalAccelMps2:0}};}
function heloEnsureA(){
  const r=ACTIVE_SHIP_RUNTIME;if(r.aviation.heloLaunchA)return r.aviation.heloLaunchA;
  const launch={schema:'AEGIS_HELO_OPERATIONS_C1',queue:[],deckOwnerId:null,doors:[0,0],holdReason:''};r.aviation.heloLaunchA=launch;
  if(heloSupportedA()){r.aviation.inventory=[0,1].map(slot=>{const h=heloFreshA(slot);h.positionM=shipGameFrameV1().pointToWorld(h.localM);h.headingRad=heloAngleA(shipNav.heading+Math.PI);h.motionBearingRad=h.headingRad;heloWorldA().set(h.id,h);return {id:h.id,slot,bay:h.bay,profileId:h.profileId};});}
  return launch;
}
function heloTransitionA(h,state){if(h.state===state)return;const old=h.state;h.state=state;h.stateTick=0;debugLog(`HELO H${h.slot+1} ${old} → ${state}`);}
// SIM_TUNED, measured SOURCE_C5: flat hangar floor joins the aft deck slope.
function heloParkLateralC(slot){return slot===0?-HELO_FACILITY_A.parkBayOffsetM:HELO_FACILITY_A.parkStarboardOffsetM;}
function heloGroundHeightC(x){const F=HELO_FACILITY_A;return Math.max(F.deckZM,F.deckPlaneZM+(x-F.deckPlaneXM)*F.deckSlope+F.deckFootClearanceM);}
function heloGroundAttitudeC(h,lift01=0){const F=HELO_FACILITY_A,k=F.deckSlope*heloSmoothA(heloClampA((-h.localM.x-49)/3,0,1)),yaw=h.localYawRad||0,t=1-heloSmoothA(lift01),nx=-k*Math.cos(yaw),nz=k*Math.sin(yaw);h.pitchRad=Math.atan2(nx,1)*t;h.bankRad=-Math.asin(nz/Math.hypot(nx,1,nz))*t;}
// Leave the deep-bay fixtures before aligning with the doorway. Turn only after
// the folded tail has cleared the rear wall; follow the measured flight deck.
function heloGroundPathB(slot,u){
  const F=HELO_FACILITY_A,sign=slot===0?-1:1,bay=sign*F.bayOffsetM-F.foldedCenterOffsetM,alignX=F.hangarXM-5;
  let x,y,yaw=0;
  if(u<.1){const t=heloSmoothA(u/.1);x=F.hangarXM+(alignX-F.hangarXM)*t;y=heloParkLateralC(slot);}
  else if(u<.2){const t=heloSmoothA((u-.1)/.1);x=alignX;y=heloParkLateralC(slot)+(bay-heloParkLateralC(slot))*t;}
  else if(u<.62){const t=heloSmoothA((u-.2)/.42);x=alignX+(F.throatClearXM-alignX)*t;y=bay;}
  else{const t=heloSmoothA((u-.62)/.38),v=1-t;x=v*v*v*F.throatClearXM+3*v*v*t*(-59.8)+3*v*t*t*(-61.9)+t*t*t*F.deckXM;
    y=bay*(v*v*v+3*v*v*t);const dx=3*v*v*(-59.8-F.throatClearXM)+6*v*t*(-61.9+59.8)+3*t*t*(F.deckXM+61.9),dy=-6*bay*v*t;yaw=heloAngleA(Math.atan2(dy,dx)-Math.PI);}
  return {x,y,z:heloGroundHeightC(x),yaw};
}
function heloSyncRouteB(h){h.waypointM=h.route[h.routeIndex]?{...h.route[h.routeIndex]}:null;}
function heloFollowTargetB(h){
  const C=HELO_VALUES_A,f=shipGameFrameV1(),point=f.pointToWorld({x:-C.followAftM,y:(h.slot===0?-1:1)*C.followLateralM,z:0});point.z=h.targetAltitudeM;
  const origin=f.pointToWorld({x:0,y:0,z:0}),rate=shipNav.turnRate||0;
  return {point,velocity:{x:worldSpeedToMps(shipNav.vx)-rate*(point.y-origin.y),y:worldSpeedToMps(shipNav.vy)+rate*(point.x-origin.x)}};
}
function heloCommandA(id,action,point=null){
  const l=heloEnsureA(),h=heloWorldA().get(String(id)),bad=reason=>({ok:false,reason});
  if(!heloSupportedA()||!h||h.ownerEntityId!==ACTIVE_SHIP_RUNTIME.entityId)return bad('운용 가능한 자함 헬기를 선택하세요');
  if(wip125PreSailOpen)return bad('출항 후 항공 명령을 사용할 수 있어요');
  if(shipEquipmentOfflineV1())return bad('모함 항공 통제 불가');
  if(h.state==='LOST')return bad('운용 불가');
  if(action==='SET_ALTITUDE'){
    const altitudeM=point?.altitudeM,C=HELO_VALUES_A;
    if(typeof altitudeM!=='number'||!Number.isFinite(altitudeM)||altitudeM<C.minAltitudeM||altitudeM>C.maxAltitudeM)return bad(`고도는 ${C.minAltitudeM}~${C.maxAltitudeM} m 범위로 입력하세요`);
    // Command changes intent only. Position/velocity change solely at fixed simulation ticks.
    h.targetAltitudeM=altitudeM;for(const q of h.route)q.z=altitudeM;
    for(const name of ['departPointM','holdPointM','followPointM'])if(h[name])h[name].z=altitudeM;heloSyncRouteB(h);
    if(h.state==='ARRIVED_HOVER'&&Math.abs(h.positionM.z-altitudeM)>1e-7)heloTransitionA(h,'TRANSIT');
    return {ok:true,altitudeM};
  }
  if(action==='WAYPOINT'||action==='ROUTE_APPEND'){
    if(!point||!Number.isFinite(point.x)||!Number.isFinite(point.y)||Math.abs(point.x)>1e8||Math.abs(point.y)>1e8)return bad('이동 위치가 유효하지 않아요');
    if(action==='ROUTE_APPEND'&&h.navigationMode==='ROUTE'&&h.route.length>=HELO_VALUES_A.routeCapacity)return bad('경로는 최대 32개 · 경로 지우기 후 다시 지정하세요');
    if(action==='WAYPOINT'||h.navigationMode!=='ROUTE'){h.route=[];h.routeIndex=0;}
    h.navigationMode='ROUTE';h.followPointM=null;h.route.push({x:point.x,y:point.y,z:h.targetAltitudeM});heloSyncRouteB(h);
    if(['ARRIVED_HOVER','FOLLOW_SHIP'].includes(h.state))heloTransitionA(h,'TRANSIT');return {ok:true};
  }
  if(action==='UNDO_ROUTE'||action==='CLEAR_ROUTE'){
    if(action==='UNDO_ROUTE'&&(h.navigationMode!=='ROUTE'||h.routeIndex>=h.route.length))return bad('지울 웨이포인트가 없어요');
    if(action==='UNDO_ROUTE')h.route.pop();else{h.route=[];h.routeIndex=0;}
    h.navigationMode='ROUTE';h.followPointM=null;heloSyncRouteB(h);
    if(!h.waypointM)h.holdPointM=h.onboard?null:{...h.positionM,z:h.targetAltitudeM};
    if(['ARRIVED_HOVER','FOLLOW_SHIP'].includes(h.state))heloTransitionA(h,'TRANSIT');return {ok:true};
  }
  if(action==='FOLLOW_SHIP'){
    h.navigationMode='FOLLOW_SHIP';h.route=[];h.routeIndex=0;h.waypointM=null;h.holdPointM=null;h.followPointM=heloFollowTargetB(h).point;
    if(!h.onboard&&h.state!=='DEPART')heloTransitionA(h,'FOLLOW_SHIP');return {ok:true};
  }
  if(action==='LAUNCH'){
    if(h.state!=='HANGARED')return bad('이미 출격 요청이 진행 중이에요');
    heloTransitionA(h,'QUEUED');l.queue.push(h.id);return {ok:true,queued:true};
  }
  if(action==='CANCEL_QUEUE'){
    if(h.state!=='QUEUED')return bad('대기 중인 출격만 취소할 수 있어요');l.queue=l.queue.filter(v=>v!==h.id);heloTransitionA(h,'HANGARED');return {ok:true};
  }
  return bad('지원하지 않는 항공 명령');
}
function heloPlaceOnShipA(h,dt){
  const p=shipGameFrameV1().pointToWorld(h.localM),old=h.positionM;
  h.positionM=p;h.groundVelocityMps={x:(p.x-old.x)/dt,y:(p.y-old.y)/dt,z:(p.z-old.z)/dt};
  h.headingRad=heloAngleA(shipNav.heading+Math.PI+h.localYawRad);h.motionBearingRad=h.headingRad;
}
function heloBeginDepartA(h){
  const frame=shipGameFrameV1(),w=heloWindVectorA(maritimeEnvironmentSnapshotWip13A3());h.positionM=frame.pointToWorld(h.localM);
  h.groundVelocityMps={x:worldSpeedToMps(shipNav.vx),y:worldSpeedToMps(shipNav.vy),z:0};
  h.airVelocityMps={x:h.groundVelocityMps.x-w.x,y:h.groundVelocityMps.y-w.y};
  if(Math.hypot(h.airVelocityMps.x,h.airVelocityMps.y)>1e-8)h.motionBearingRad=Math.atan2(h.airVelocityMps.y,h.airVelocityMps.x);
  h.departPointM=frame.pointToWorld({x:HELO_FACILITY_A.deckXM,y:-HELO_VALUES_A.departOffsetM,z:h.targetAltitudeM});h.departPointM.z=h.targetAltitudeM;
  h.onboard=false;heloTransitionA(h,'DEPART');getShipMassLedgerV32().markDirty('HELO_DETACH');
}
function heloFixedStepA(dt){
  if(!heloSupportedA())return;const l=heloEnsureA(),world=heloWorldA(),w=heloWindVectorA(maritimeEnvironmentSnapshotWip13A3());
  l.holdReason=shipEquipmentOfflineV1()?'모함 항공 통제 불가':'';
  if(l.deckOwnerId){const h=world.get(l.deckOwnerId);if(h&&!h.onboard){const p=shipGameFrameV1().pointToBody(h.positionM),clear=HELO_FACILITY_A.deckHalfWidthM+HELO_FACILITY_A.rotorRadiusM+HELO_VALUES_A.deckClearMarginM;
    const margin=HELO_FACILITY_A.rotorRadiusM+HELO_VALUES_A.deckClearMarginM;
    if(Math.abs(p.y)>clear||p.x<HELO_FACILITY_A.deckMinXM-margin||p.x>HELO_FACILITY_A.deckMaxXM+margin){l.deckOwnerId=null;debugLog(`HELO H${h.slot+1} 갑판 이탈 · 다음 출격 가능`);}}
  }
  if(!l.deckOwnerId&&!l.holdReason&&l.queue.length){const h=world.get(l.queue.shift());if(h?.state==='QUEUED'){l.deckOwnerId=h.id;h.visible=true;heloTransitionA(h,'HANGAR_OPEN');}}
  for(const inv of heloInventoryA()){
    const h=world.get(inv.id);if(!h)continue;
    if(HELO_GROUND_STATES_A.includes(h.state)){
      if(l.holdReason){heloPlaceOnShipA(h,dt);continue;}
      h.stateTick++;const duration=HELO_VALUES_A[h.state+'_S'],u=heloClampA(h.stateTick*SIM_FIXED_DT/duration,0,1),t=heloSmoothA(u),sign=h.slot===0?-1:1;
      if(h.state==='HANGAR_OPEN'){l.doors[h.slot]=t;h.localM={x:HELO_FACILITY_A.hangarXM,y:heloParkLateralC(h.slot),z:HELO_FACILITY_A.deckZM};h.localYawRad=0;}
      else if(h.state==='TRAVERSE'){
        // Clear the doorway before moving sideways into the ONE shared deck spot.
        const pose=heloGroundPathB(h.slot,u);h.localM={x:pose.x,y:pose.y,z:pose.z};h.localYawRad=pose.yaw;
      }else if(h.state==='SPREAD'){const f=HELO_VALUES_A.tailSpreadFraction;h.tail01=heloSmoothA(u/f);h.blades01=heloSmoothA((u-f)/(1-f));}
      else if(h.state==='START'){const f=HELO_VALUES_A.engineTwoStartFraction,r=HELO_VALUES_A.rotorStartFraction;h.engine01=[heloSmoothA(u/HELO_VALUES_A.engineOneFraction),heloSmoothA((u-f)/(1-f))];h.rotor01=heloSmoothA((u-r)/(1-r));}
      else if(h.state==='LIFT_HOVER')h.localM.z=heloGroundHeightC(HELO_FACILITY_A.deckXM)+HELO_VALUES_A.liftHeightM*t;
      if(['SPREAD','START','PRE_LAUNCH_CHECK','LIFT_HOVER'].includes(h.state)){h.localM.x=HELO_FACILITY_A.deckXM;h.localM.y=0;h.localYawRad=0;if(h.state!=='LIFT_HOVER')h.localM.z=heloGroundHeightC(HELO_FACILITY_A.deckXM);}
      heloGroundAttitudeC(h,h.state==='LIFT_HOVER'?t:0);heloPlaceOnShipA(h,dt);
      if(h.stateTick>=Math.round(duration/SIM_FIXED_DT)){
        const index=HELO_GROUND_STATES_A.indexOf(h.state);
        if(index===HELO_GROUND_STATES_A.length-1)heloBeginDepartA(h);else heloTransitionA(h,HELO_GROUND_STATES_A[index+1]);
      }
      if(simStepCounter%30===0)getShipMassLedgerV32().markDirty('HELO_DECK_POSITION');
    }else if(['DEPART','TRANSIT','ARRIVED_HOVER','FOLLOW_SHIP'].includes(h.state)){
      if(h.state!=='DEPART'&&h.navigationMode==='FOLLOW_SHIP'){
        const target=heloFollowTargetB(h);h.followPointM=target.point;heloMoveA(h,target.point,w,dt,{targetVelocityMps:target.velocity,headingRad:shipNav.heading});
      }else{
        const next=h.route[h.routeIndex+1],goal=h.state==='DEPART'?h.departPointM:(h.waypointM??h.holdPointM??h.departPointM),
          pass=h.state!=='DEPART'&&!!h.waypointM&&!!next,q=heloMoveA(h,goal,w,dt,{passThrough:pass,nextPoint:next});
        if(h.state==='DEPART'&&q.horizontalArrived&&h.positionM.z>=Math.min(h.targetAltitudeM,HELO_VALUES_A.departMinAltitudeM)-1e-7){h.holdPointM={...goal};heloTransitionA(h,h.navigationMode==='FOLLOW_SHIP'?'FOLLOW_SHIP':h.waypointM||!q.arrived?'TRANSIT':'ARRIVED_HOVER');}
        else if(h.state==='TRANSIT'&&(pass?q.distanceM<=HELO_VALUES_A.waypointPassRadiusM:q.arrived)){
          if(h.waypointM){h.holdPointM={...h.waypointM};h.routeIndex++;heloSyncRouteB(h);}
          if(!h.waypointM)heloTransitionA(h,'ARRIVED_HOVER');
        }
      }
    }else if(h.onboard)heloPlaceOnShipA(h,dt);
    h.rotorAngleRad=(h.rotorAngleRad+HELO_VALUES_A.rotorRpm*2*Math.PI/60*h.rotor01*dt)%(2*Math.PI);
  }
  for(let i=0;i<2;i++){const h=world.get(heloInventoryA()[i]?.id);if(h&&!h.onboard)l.doors[i]=Math.max(0,l.doors[i]-dt/HELO_VALUES_A.HANGAR_OPEN_S);}
}
function heloMassNodeA(node){
  if(!heloSupportedA()||node.category!=='AIRCRAFT')return node;
  const slot=node.id==='helo.port'?0:node.id==='helo.starboard'?1:-1,inv=heloInventoryA()[slot],h=inv&&heloWorldA().get(inv.id);
  if(!h||h.state==='HANGARED'||h.state==='QUEUED')return node;
  return {...node,massKg:h.onboard?node.massKg:0,x:h.localM.x,y:h.localM.y,z:h.localM.z+1,model:'HELO_DECK_ATTACHED_A1'};
}
function heloResetA(){heloWorldA().clear();delete ACTIVE_SHIP_RUNTIME.aviation.heloLaunchA;ACTIVE_SHIP_RUNTIME.aviation.inventory=[];heloEnsureA();heloUiA.selectedId=null;getShipMassLedgerV32().markDirty('HELO_RESET');}
function heloSnapshotA(){
  const l=ACTIVE_SHIP_RUNTIME.aviation.heloLaunchA??{queue:[],deckOwnerId:null,doors:[0,0],holdReason:''},wind=heloWindVectorA(maritimeEnvironmentSnapshotWip13A3());return {schema:'AEGIS_HELO_C1',profileId:'MH60R_POINT_MASS_A1',supported:heloSupportedA(),fixedDtS:SIM_FIXED_DT,constants:HELO_SPEC_A,queue:[...l.queue],deckOwnerId:l.deckOwnerId,doors:[...l.doors],holdReason:l.holdReason,windMps:wind,
    aircraft:heloInventoryA().map(inv=>{const h=heloWorldA().get(inv.id),target=h.navigationMode==='FOLLOW_SHIP'?h.followPointM:(h.waypointM??h.holdPointM??h.departPointM),distance=target?Math.hypot(target.x-h.positionM.x,target.y-h.positionM.y):null,groundSpeed=Math.hypot(h.groundVelocityMps.x,h.groundVelocityMps.y),airSpeed=h.onboard?0:Math.hypot(h.airVelocityMps.x,h.airVelocityMps.y);
      return {...JSON.parse(JSON.stringify(h)),airSpeedKt:airSpeed/HELO_VALUES_A.knotMps,groundSpeedKt:h.onboard?0:groundSpeed/HELO_VALUES_A.knotMps,altitudeM:h.positionM.z,headingDeg:(h.headingRad*180/Math.PI+450)%360,distanceM:distance,etaS:distance==null?null:Math.max(h.state==='ARRIVED_HOVER'?0:distance/(!h.onboard&&groundSpeed>HELO_VALUES_A.arrivalSpeedMps?groundSpeed:HELO_VALUES_A.cruiseKt*HELO_VALUES_A.knotMps),h.onboard?0:Math.abs(h.targetAltitudeM-h.positionM.z)/Math.min(HELO_VALUES_A.verticalMps,HELO_VALUES_A.maxClimbMps)),remainingS:HELO_GROUND_STATES_A.includes(h.state)?Math.max(0,HELO_VALUES_A[h.state+'_S']-h.stateTick*SIM_FIXED_DT):null};})};
}
function heloExportA(){if(!heloSupportedA())return {inventory:[],facilities:ACTIVE_SHIP_RUNTIME.aviation.facilities};heloEnsureA();return JSON.parse(JSON.stringify({schema:'AEGIS_HELO_SAVE_C1',inventory:heloInventoryA(),facilities:ACTIVE_SHIP_RUNTIME.aviation.facilities,launch:ACTIVE_SHIP_RUNTIME.aviation.heloLaunchA,aircraft:[...heloWorldA().values()]}));}
function heloMigrateSaveA(src,migrations){
  if(!heloSupportedA())return;const a=src.ship?.aviation;
  if(a&&!a.schema&&Array.isArray(a.inventory)&&a.inventory.length===0){const fresh=[0,1].map(heloFreshA);src.ship.aviation={schema:'AEGIS_HELO_SAVE_C1',facilities:a.facilities,inventory:fresh.map(h=>({id:h.id,slot:h.slot,bay:h.bay,profileId:h.profileId})),launch:{schema:'AEGIS_HELO_OPERATIONS_C1',queue:[],deckOwnerId:null,doors:[0,0],holdReason:''},aircraft:fresh};migrations.push({id:'HELO_A_LEGACY_EMPTY_INVENTORY',policy:'TWO_STOWED_AIRFRAMES_NO_IN_FLIGHT_MIGRATION'});}
  const old=src.ship?.aviation;
  if(old?.schema==='AEGIS_HELO_SAVE_A1'&&Array.isArray(old.aircraft)&&old.launch?.schema==='AEGIS_HELO_OPERATIONS_A1'){
    const additions=['localYawRad','navigationMode','route','routeIndex','holdPointM','followPointM'];
    if(old.aircraft.some(h=>!h||typeof h!=='object'||Array.isArray(h)||additions.some(k=>Object.hasOwn(h,k))))return;
    for(const h of old.aircraft){h.localYawRad=0;h.navigationMode='ROUTE';h.route=h.waypointM===null||h.state==='ARRIVED_HOVER'?[]:[h.waypointM];h.routeIndex=0;h.holdPointM=h.state==='ARRIVED_HOVER'?(h.waypointM??h.departPointM):h.departPointM;if(h.state==='ARRIVED_HOVER')h.waypointM=null;h.followPointM=null;}
    old.schema='AEGIS_HELO_SAVE_B1';old.launch.schema='AEGIS_HELO_OPERATIONS_B1';migrations.push({id:'HELO_B_ROUTES_AND_LOCAL_YAW',policy:'PRESERVE_AIRBORNE_POSE; NEW_GROUND_LAYOUT_AT_NEXT_FIXED_TICK'});
  }
  if(old?.schema==='AEGIS_HELO_SAVE_B1'&&Array.isArray(old.aircraft)&&old.launch?.schema==='AEGIS_HELO_OPERATIONS_B1'){
    if(old.aircraft.some(h=>!h||typeof h!=='object'||Array.isArray(h)||Object.hasOwn(h,'targetAltitudeM')))return;
    for(const h of old.aircraft)h.targetAltitudeM=HELO_VALUES_A.altitudeM;
    old.schema='AEGIS_HELO_SAVE_C1';old.launch.schema='AEGIS_HELO_OPERATIONS_C1';migrations.push({id:'HELO_C_SELECTABLE_ALTITUDE',policy:'DEFAULT_50_M_MSL; PRESERVE_POSE_VELOCITY_AND_ROUTE'});
  }
}
function heloValidateSaveA(a,errors){
  if(!heloSupportedA())return;const fail=()=>errors.push('HELO_SAVE_A'),record=x=>x&&typeof x==='object'&&!Array.isArray(x),finite=x=>typeof x==='number'&&Number.isFinite(x),
    keys=(a,b)=>record(a)&&Object.keys(a).sort().join('|')===Object.keys(b).sort().join('|');
  if(!record(a)||a.schema!=='AEGIS_HELO_SAVE_C1'||!Array.isArray(a.inventory)||a.inventory.length!==2||!Array.isArray(a.aircraft)||a.aircraft.length!==2||!record(a.launch)){fail();return;}
  const l=a.launch,ids=a.aircraft.map(h=>h.id),active=a.aircraft.filter(h=>HELO_GROUND_STATES_A.includes(h.state));
  if(l.schema!=='AEGIS_HELO_OPERATIONS_C1'||!Array.isArray(l.queue)||new Set(l.queue).size!==l.queue.length||!Array.isArray(l.doors)||l.doors.length!==2||l.doors.some(x=>!finite(x)||x<0||x>1)||typeof l.holdReason!=='string'||l.holdReason.length>100||l.deckOwnerId!==null&&!ids.includes(l.deckOwnerId)||active.length>1||active.some(h=>h.id!==l.deckOwnerId))fail();
  for(let i=0;i<2;i++){const fresh=heloFreshA(i),h=a.aircraft[i],inv=a.inventory[i];
    if(!keys(h,fresh)||h.id!==fresh.id||h.ownerEntityId!==fresh.ownerEntityId||h.slot!==i||h.bay!==fresh.bay||h.profileId!==fresh.profileId||!HELO_STATES_A.includes(h.state)||h.state==='RECOVERY'||!Number.isInteger(h.stateTick)||h.stateTick<0||h.stateTick>1e7||typeof h.visible!=='boolean'||typeof h.onboard!=='boolean'){fail();continue;}
    if(!finite(h.targetAltitudeM)||h.targetAltitudeM<HELO_VALUES_A.minAltitudeM||h.targetAltitudeM>HELO_VALUES_A.maxAltitudeM)fail();
    if(!['ROUTE','FOLLOW_SHIP'].includes(h.navigationMode)||!Array.isArray(h.route)||h.route.length>HELO_VALUES_A.routeCapacity||!Number.isInteger(h.routeIndex)||h.routeIndex<0||h.routeIndex>h.route.length)fail();
    else{for(const q of h.route)if(!keys(q,{x:0,y:0,z:0})||!Object.values(q).every(finite)||q.z!==h.targetAltitudeM||Math.abs(q.x)>1e8||Math.abs(q.y)>1e8)fail();if(JSON.stringify(h.waypointM)!==JSON.stringify(h.route[h.routeIndex]??null))fail();}
    if(h.state==='FOLLOW_SHIP'&&(h.navigationMode!=='FOLLOW_SHIP'||h.onboard)||h.navigationMode==='FOLLOW_SHIP'&&(!Array.isArray(h.route)||h.route.length!==0||h.waypointM!==null||h.followPointM===null)||!finite(h.localYawRad)||Math.abs(h.localYawRad)>Math.PI)fail();
    if(!keys(inv,{id:0,slot:0,bay:0,profileId:0})||inv.id!==h.id||inv.slot!==i||inv.bay!==h.bay||inv.profileId!==h.profileId)fail();
    for(const k of ['localM','positionM','airVelocityMps','groundVelocityMps','motion'])if(!keys(h[k],fresh[k])||Object.entries(h[k]).some(([name,v])=>typeof fresh[k][name]==='boolean'?typeof v!=='boolean':!finite(v)||Math.abs(v)>1e8))fail();
    for(const k of ['waypointM','departPointM','holdPointM','followPointM'])if(h[k]!==null&&(!keys(h[k],{x:0,y:0,z:0})||!Object.values(h[k]).every(finite)||h[k].z!==h.targetAltitudeM||Math.abs(h[k].x)>1e8||Math.abs(h[k].y)>1e8))fail();
    if(!Array.isArray(h.engine01)||h.engine01.length!==2||h.engine01.some(v=>!finite(v)||v<0||v>1))fail();
    for(const k of ['localYawRad','headingRad','motionBearingRad','pitchRad','bankRad','rotorAngleRad','rotor01','tail01','blades01'])if(!finite(h[k])||Math.abs(h[k])>1e4)fail();
    for(const k of ['rotor01','tail01','blades01'])if(h[k]<0||h[k]>1)fail();
    if(Math.hypot(h.airVelocityMps.x,h.airVelocityMps.y)>HELO_VALUES_A.maxCruiseKt*HELO_VALUES_A.knotMps+1e-6||HELO_GROUND_STATES_A.includes(h.state)&&!h.onboard||['DEPART','TRANSIT','ARRIVED_HOVER','FOLLOW_SHIP'].includes(h.state)&&(h.onboard||!h.departPointM))fail();
    if((h.state==='QUEUED')!==l.queue.includes(h.id)||h.state==='HANGARED'&&h.visible)fail();
    if(HELO_GROUND_STATES_A.includes(h.state)&&h.stateTick>=Math.round(HELO_VALUES_A[h.state+'_S']/SIM_FIXED_DT))fail();
    if(['HANGARED','QUEUED'].includes(h.state)&&(!h.onboard||h.rotor01!==0||h.blades01!==0||h.tail01!==0))fail();
  }
  if(l.queue.some(id=>!ids.includes(id)))fail();
  if(l.deckOwnerId&&a.aircraft.some(h=>h.id===l.deckOwnerId&&!HELO_GROUND_STATES_A.includes(h.state)&&!['DEPART','TRANSIT','ARRIVED_HOVER','FOLLOW_SHIP'].includes(h.state)))fail();
  if(a.aircraft.some(h=>['DEPART','TRANSIT','ARRIVED_HOVER','FOLLOW_SHIP'].includes(h.state)&&(!Number.isFinite(h.positionM?.z)||h.positionM.z<0||h.positionM.z>HELO_VALUES_A.maxAltitudeM+1e-7||Math.abs(h.groundVelocityMps?.z)>Math.min(HELO_VALUES_A.verticalMps,HELO_VALUES_A.maxClimbMps)+1e-7)))fail();
}
function heloRestoreA(a){if(!heloSupportedA())return;heloWorldA().clear();ACTIVE_SHIP_RUNTIME.aviation.inventory=JSON.parse(JSON.stringify(a.inventory));ACTIVE_SHIP_RUNTIME.aviation.heloLaunchA=JSON.parse(JSON.stringify(a.launch));for(const h of a.aircraft)heloWorldA().set(h.id,JSON.parse(JSON.stringify(h)));heloUiA.selectedId=null;getShipMassLedgerV32().markDirty('HELO_IMPORT');}
window.__HELO__={snapshot:heloSnapshotA,command:heloCommandA};
