// MH-60R point-mass movement. Source tags apply to every tunable numeric constant.
const HELO_SPEC_A=Object.freeze(Object.fromEntries(Object.entries({
  knotMps:[1852/3600,'PUBLIC_SPEC','SI nautical mile/hour'],
  gravity:[9.80665,'PUBLIC_SPEC','standard gravity'],
  maxCruiseKt:[140,'PUBLIC_SPEC','user-supplied MH-60R public specification'],
  maxClimbMps:[8.4,'PUBLIC_SPEC','user-supplied MH-60R public specification'],
  cruiseKt:[120,'SIM_TUNED'],verticalMps:[3.5,'SIM_TUNED'],accel:[1.5,'SIM_TUNED'],decel:[2,'SIM_TUNED'],
  maxBankRad:[Math.PI/6,'SIM_TUNED'],hoverTurnRadS:[Math.PI/12,'SIM_TUNED'],hoverThresholdKt:[30,'SIM_TUNED'],
  holdGain:[.8,'SIM_TUNED'],arrivalRadiusM:[1.5,'SIM_TUNED'],arrivalSpeedMps:[.3,'SIM_TUNED'],
  holdZoneM:[8,'SIM_TUNED'],traverseExitFraction:[.7,'SIM_TUNED'],tailSpreadFraction:[.4,'SIM_TUNED'],
  engineOneFraction:[.45,'SIM_TUNED'],engineTwoStartFraction:[.35,'SIM_TUNED'],rotorStartFraction:[.12,'SIM_TUNED'],
  attitudeLagS:[.5,'SIM_TUNED'],altitudeM:[50,'SIM_TUNED'],minAltitudeM:[25,'SIM_TUNED'],
  maxAltitudeM:[3962.4,'PUBLIC_SPEC','US 7th Fleet Public Affairs 2014-03-10: MH-60R ceiling 13,000 ft (exact 0.3048 m/ft); https://www.cpf.navy.mil/Newsroom/News/Article/2750444/uss-kidd-joins-uss-pinckney-in-flight-mh370-search-effort/'],liftHeightM:[5,'SIM_TUNED'],
  rotorRpm:[258,'SIM_TUNED'],departOffsetM:[60,'SIM_TUNED'],departMinAltitudeM:[25,'SIM_TUNED'],deckClearMarginM:[2,'SIM_TUNED'],
  visualRotorDiameterM:[16.36,'SIM_TUNED','visual scale of supplied SH-60 model'],visualHeightM:[5.13,'SIM_TUNED'],
  turnSlowStartRad:[Math.PI/18,'SIM_TUNED'],turnSlowFullRad:[Math.PI*5/12,'SIM_TUNED'],turnSlowMinKt:[35,'SIM_TUNED'],
  waypointPassRadiusM:[20,'SIM_TUNED'],routeCapacity:[32,'SIM_TUNED'],followLateralM:[400,'SIM_TUNED'],followAftM:[100,'SIM_TUNED'],followGain:[.35,'SIM_TUNED'],
  tailRotorRatio:[4.6,'SIM_TUNED'],heroCameraDistanceM:[42,'SIM_TUNED'],lodDistanceM:[1800,'SIM_TUNED'],rotorDiskOpacity:[.12,'SIM_TUNED'],
  HANGAR_OPEN_S:[10,'SIM_TUNED'],TRAVERSE_S:[20,'SIM_TUNED'],SPREAD_S:[30,'SIM_TUNED'],
  START_S:[45,'SIM_TUNED'],PRE_LAUNCH_CHECK_S:[10,'SIM_TUNED'],LIFT_HOVER_S:[5,'SIM_TUNED']
}).map(([name,[value,source,reference]])=>[name,Object.freeze({value,source,...(reference?{reference}:{})})])));
const HELO_VALUES_A=Object.freeze(Object.fromEntries(Object.entries(HELO_SPEC_A).map(([k,v])=>[k,v.value])));
const HELO_GROUND_STATES_A=Object.freeze(['HANGAR_OPEN','TRAVERSE','SPREAD','START','PRE_LAUNCH_CHECK','LIFT_HOVER']);
const HELO_STATES_A=Object.freeze(['HANGARED','QUEUED',...HELO_GROUND_STATES_A,'DEPART','TRANSIT','ARRIVED_HOVER','FOLLOW_SHIP','RECOVERY','LOST']);
const heloClampA=(x,a,b)=>Math.max(a,Math.min(b,x));
const heloAngleA=x=>Math.atan2(Math.sin(x),Math.cos(x));
const heloSmoothA=x=>{x=heloClampA(x,0,1);return x*x*(3-2*x);};
function heloWindVectorA(environment){const w=environment?.wind??{},s=Number(w.speedMps)||0,d=Number(w.directionRad)||0;return {x:s*Math.cos(d),y:s*Math.sin(d)};}
function heloCornerSpeedB(angle){const C=HELO_VALUES_A,t=heloSmoothA((Math.abs(angle)-C.turnSlowStartRad)/(C.turnSlowFullRad-C.turnSlowStartRad));return (C.cruiseKt+(C.turnSlowMinKt-C.cruiseKt)*t)*C.knotMps;}
function heloMoveA(h,target,wind,dt,control={}){
  const C=HELO_VALUES_A,targetAltitudeM=target.z??h.targetAltitudeM??C.altitudeM,p=h.positionM,v=h.airVelocityMps,dx=target.x-p.x,dy=target.y-p.y,d=Math.hypot(dx,dy),
    oldSpeed=Math.hypot(v.x,v.y),gx=v.x+wind.x,gy=v.y+wind.y,groundSpeed=Math.hypot(gx,gy),
    maxSpeed=C.maxCruiseKt*C.knotMps,cruise=C.cruiseKt*C.knotMps,
    stopDistance=groundSpeed*groundSpeed/(2*C.decel),braking=d<=stopDistance+C.arrivalRadiusM;
  // Braking uses ground distance/speed; limits remain AIR speed, including in wind.
  let wantedGround=Math.min(cruise,Math.sqrt(2*C.decel*Math.max(0,d-C.arrivalRadiusM)));
  if(control.passThrough){const angle=control.nextPoint?heloAngleA(Math.atan2(control.nextPoint.y-target.y,control.nextPoint.x-target.x)-Math.atan2(dy,dx)):0,corner=heloCornerSpeedB(angle);wantedGround=Math.min(cruise,Math.sqrt(corner*corner+2*C.decel*Math.max(0,d-C.waypointPassRadiusM)));}
  else if(control.targetVelocityMps)wantedGround=Math.min(cruise,d*C.followGain);
  else if(d<C.holdZoneM)wantedGround=Math.min(wantedGround,d*C.holdGain);
  let tx=(d>1e-9?dx/d*wantedGround:0)+(control.targetVelocityMps?.x??0)-wind.x,ty=(d>1e-9?dy/d*wantedGround:0)+(control.targetVelocityMps?.y??0)-wind.y;
  const need=Math.hypot(tx,ty),bounded=Math.min(cruise,maxSpeed,need);if(need>bounded&&need>0){tx*=bounded/need;ty*=bounded/need;}
  const requestedSpeed=Math.hypot(tx,ty),desiredBearing=requestedSpeed>1e-8?Math.atan2(ty,tx):h.motionBearingRad,
    turnError=heloAngleA(desiredBearing-h.motionBearingRad),desiredSpeed=Math.min(requestedSpeed,heloCornerSpeedB(turnError));
  if(requestedSpeed>desiredSpeed&&requestedSpeed>0){tx*=desiredSpeed/requestedSpeed;ty*=desiredSpeed/requestedSpeed;}
  let turn=0;
  if(oldSpeed<C.hoverThresholdKt*C.knotMps){
    // Low-speed translation and nose yaw are independent. No velocity snapping.
    const deltaX=tx-v.x,deltaY=ty-v.y,length=Math.hypot(deltaX,deltaY),rate=desiredSpeed<oldSpeed?C.decel:C.accel,
      fraction=length>0?Math.min(1,rate*dt/length):0;
    v.x+=deltaX*fraction;v.y+=deltaY*fraction;
    h.headingRad=heloAngleA(h.headingRad+heloClampA(heloAngleA((control.headingRad??desiredBearing)-h.headingRad),-C.hoverTurnRadS*dt,C.hoverTurnRadS*dt));
    if(Math.hypot(v.x,v.y)>1e-6)h.motionBearingRad=Math.atan2(v.y,v.x);
  }else{
    const maxTurn=C.gravity*Math.tan(C.maxBankRad)/oldSpeed,
      delta=heloClampA(heloAngleA(desiredBearing-h.motionBearingRad),-maxTurn*dt,maxTurn*dt),
      speed=heloClampA(oldSpeed+heloClampA(desiredSpeed-oldSpeed,-C.decel*dt,C.accel*dt),0,maxSpeed);
    h.motionBearingRad=heloAngleA(h.motionBearingRad+delta);turn=delta/dt;
    h.headingRad=heloAngleA(h.headingRad+heloClampA(heloAngleA(h.motionBearingRad-h.headingRad),-maxTurn*dt,maxTurn*dt));
    v.x=speed*Math.cos(h.motionBearingRad);v.y=speed*Math.sin(h.motionBearingRad);
  }
  const airSpeed=Math.hypot(v.x,v.y);if(airSpeed>maxSpeed){v.x*=maxSpeed/airSpeed;v.y*=maxSpeed/airSpeed;}
  h.groundVelocityMps={x:v.x+wind.x,y:v.y+wind.y,z:heloClampA(targetAltitudeM-p.z,-Math.min(C.verticalMps,C.maxClimbMps)*dt,Math.min(C.verticalMps,C.maxClimbMps)*dt)/dt};
  p.x+=h.groundVelocityMps.x*dt;p.y+=h.groundVelocityMps.y*dt;p.z+=h.groundVelocityMps.z*dt;
  const a=(Math.hypot(v.x,v.y)-oldSpeed)/dt,alpha=1-Math.exp(-dt/C.attitudeLagS),
    pitch=-Math.atan(a/C.gravity),bank=heloClampA(Math.atan(turn*Math.max(oldSpeed,1e-6)/C.gravity),-C.maxBankRad,C.maxBankRad);
  h.pitchRad+=(pitch-h.pitchRad)*alpha;h.bankRad+=(bank-h.bankRad)*alpha;
  h.motion={airSpeedMps:Math.hypot(v.x,v.y),groundSpeedMps:Math.hypot(h.groundVelocityMps.x,h.groundVelocityMps.y),stopDistanceM:stopDistance,braking,turnRateRadS:turn,longitudinalAccelMps2:a};
  return {distanceM:Math.hypot(target.x-p.x,target.y-p.y),horizontalArrived:Math.hypot(target.x-p.x,target.y-p.y)<=C.arrivalRadiusM&&Math.hypot(h.groundVelocityMps.x,h.groundVelocityMps.y)<=C.arrivalSpeedMps,arrived:Math.hypot(target.x-p.x,target.y-p.y)<=C.arrivalRadiusM&&Math.hypot(h.groundVelocityMps.x,h.groundVelocityMps.y)<=C.arrivalSpeedMps&&Math.abs(p.z-targetAltitudeM)<1e-7};
}
