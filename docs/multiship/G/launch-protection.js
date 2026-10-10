// Launch acknowledgement and anonymous radar evidence only. There is still no
// Harpoon DL, missile-world lookup, private navigation state, or seeker telemetry.
const HARPOON_CORRELATION_G=Object.freeze({reacquireS:8,visibleCoastS:4,maxPositionGateM:1800,maxCandidateAgeS:1});
function harpoonObservedSigmaG(tr){
  const P=tr._kfP,pos=P?Math.sqrt(Math.max(1,P[0]+P[7])):Number(tr.measurementSigmaM)||100,
    vel=P?Math.sqrt(Math.max(1,P[21]+P[28])):Number(tr.velocitySigmaMps)||60;
  return {pos:clamp(pos,10,600),vel:clamp(vel,5,500)};
}
function harpoonMatchLaunchC(record,tr,step,prior=null){
  const measurementStep=Number(tr._lastMeasurementStep),elapsed=(measurementStep-record.releaseStep)*SIM_FIXED_DT,
    X=tr._kfX??[worldToMeters(tr.x),worldToMeters(tr.y),tr.z??0,worldSpeedToMps(tr.vx??0),worldSpeedToMps(tr.vy??0),tr.vz??0],
    sample={x:X[0],y:X[1],z:X[2],vx:X[3],vy:X[4],vz:X[5]},speed=Math.hypot(sample.vx,sample.vy),sigma=harpoonObservedSigmaG(tr),age=(step-measurementStep)*SIM_FIXED_DT;
  if(tr._lastMeasurementStep==null||!Number.isFinite(measurementStep)||elapsed<=0||age<0||age>HARPOON_CORRELATION_G.maxCandidateAgeS||tr.sensorDetected===false||!(String(tr.sensorSource).startsWith('SPY1DV')||String(tr.sensorSource).startsWith('SPQ9B'))||record.excludedTrackIds.includes(tr.trackId)||speed>430||sample.z>600||sample.z< -50)return null;
  if(prior){
    const gap=(measurementStep-prior.lastStep)*SIM_FIXED_DT;if(gap<=0||gap>HARPOON_CORRELATION_G.reacquireS)return null;
    // Transverse velocity is weakly observed at a radar notch. Do not convert an
    // uncertain low speed or a programmed turn into affirmative hostile intent.
    if(speed<45&&!(prior.confirmed||prior.hits>=3))return null;
    const velSigma=Math.hypot(sigma.vel,prior.velSigma??60),turnAccel=19.62,
      error=Math.hypot(sample.x-prior.x-prior.vx*gap,sample.y-prior.y-prior.vy*gap),
      gate=Math.min(HARPOON_CORRELATION_G.maxPositionGateM,80+3*Math.hypot(sigma.pos,prior.posSigma??100)+velSigma*gap+.5*turnAccel*gap*gap),
      dv=Math.hypot(sample.vx-prior.vx,sample.vy-prior.vy),velocityGate=60+turnAccel*gap+3*velSigma;
    if(error>gate||dv>velocityGate)return null;
    return {...sample,posSigma:sigma.pos,velSigma:sigma.vel,lastStep:measurementStep,score:error/gate+dv/velocityGate*.1,hits:prior.hits+1,firstStep:prior.firstStep,continuedConfirmed:!!prior.confirmed};
  }
  if(speed<45||elapsed>12||record.claimedTrackId!=null&&record.claimedTrackId!==tr.trackId)return null;
  const p=harpoonLaunchPredictionC(record,elapsed),gate=Math.min(600,120+elapsed*25+2*Math.min(180,sigma.pos)),error=Math.hypot(sample.x-p.x,sample.y-p.y),velocityHeading=Math.atan2(sample.vy,sample.vx);
  if(error>gate||Math.abs(angNorm(velocityHeading-p.heading))>Math.PI/4)return null;
  return {...sample,posSigma:sigma.pos,velSigma:sigma.vel,lastStep:measurementStep,score:error/gate,hits:1,firstStep:measurementStep,continuedConfirmed:false};
}
function harpoonTrackIdentityC(tr,owner=ACTIVE_SHIP_RUNTIME){
  if(!tr)return null;
  const records=owner?.weapons?.harpoon?.launches;if(!records?.length)return null;
  const now=simStepCounter,prior=tr._harpoonOwnC,measurementStep=Number(tr._lastMeasurementStep),age=prior?(now-prior.lastStep)*SIM_FIXED_DT:Infinity;
  if(prior&&prior.lastStep===measurementStep){
    if(age<=HARPOON_CORRELATION_G.visibleCoastS)return {identity:prior.confirmed?'FRIEND':'UNKNOWN',reason:prior.confirmed?'OWN_LAUNCH_RADAR_CORRELATION':'POSSIBLE_OWN_LAUNCH'};
    if(prior.confirmed&&age<=HARPOON_CORRELATION_G.reacquireS)return {identity:'UNKNOWN',reason:'OWN_LAUNCH_COAST_UNCERTAIN'};
    tr._harpoonOwnC=null;return null;
  }
  const ranked=[];
  for(const record of records){
    const history=record.lastRadarSampleG,continuation=prior?.launchId===record.id&&prior.hits?prior:history?.confirmed?history:null,
      match=harpoonMatchLaunchC(record,tr,now,continuation);
    if(match)ranked.push({record,match});
  }
  ranked.sort((a,b)=>a.match.score-b.match.score||a.record.id-b.record.id);
  const best=ranked[0],competingFile=best&&[...observerC(owner).tracks.values()].some(q=>q!==tr&&q._harpoonOwnC?.launchId===best.record.id&&q._harpoonOwnC.confirmed&&(now-q._harpoonOwnC.lastStep)*SIM_FIXED_DT<=2),
    ambiguous=ranked.length>1&&ranked[1].match.score-best.match.score<.25||competingFile;
  if(!best){
    const sigma=harpoonObservedSigmaG(tr),X=tr._kfX,speed=X?Math.hypot(X[3],X[4]):0,
      clearlyInbound=prior&&X&&sigma.vel<45&&speed>120&&(X[3]*prior.vx+X[4]*prior.vy)<-.4*speed*Math.hypot(prior.vx,prior.vy);
    if(prior?.confirmed&&age<=HARPOON_CORRELATION_G.reacquireS&&!clearlyInbound)return {identity:'UNKNOWN',reason:'OWN_LAUNCH_CORRELATION_UNCERTAIN'};
    tr._harpoonOwnC=null;return null;
  }
  if(ambiguous){tr._harpoonOwnC={lastStep:measurementStep,confirmed:false,launchId:null,evidence:'AMBIGUOUS_LAUNCH_CORRELATION'};return {identity:'UNKNOWN',reason:'POSSIBLE_OWN_LAUNCH'};}
  const {record,match}=best,confirmed=match.continuedConfirmed||match.hits>=3&&(match.lastStep-match.firstStep)*SIM_FIXED_DT>=.15;
  tr._harpoonOwnC={...match,launchId:record.id,tubeId:record.tubeId,confirmed,evidence:'LAUNCH_CORRELATED_ANONYMOUS_RADAR'};
  if(confirmed){record.claimedTrackId=tr.trackId;record.lastRadarSampleG={...tr._harpoonOwnC};}
  return {identity:confirmed?'FRIEND':'UNKNOWN',reason:confirmed?'OWN_LAUNCH_RADAR_CORRELATION':'POSSIBLE_OWN_LAUNCH'};
}
