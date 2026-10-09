// Ship-owned knowledge: launch acknowledgement plus anonymous radar track evidence.
// No Harpoon world pool, physical owner IDs, survival, INS solution or seeker telemetry.
function harpoonLaunchRecordC(m,gate){
  return {id:m.id,tubeId:m.tubeId,releaseStep:simStepCounter,positionM:{...gate.muzzleM},axis:{...gate.axis},
    carrierVelocityMps:{...m.carrierVelocityMps},memory:gate.memory,
    excludedTrackIds:Array.from(tracks.keys()),claimedTrackId:null};
}
function harpoonLaunchPredictionC(record,elapsedS){
  // Nominal outbound corridor ONLY for radar association, never a live position symbol.
  const t=Math.max(0,elapsedS),burn=HARPOON_PROFILE_A.sim.boosterBurnS,b=Math.min(t,burn),
    axial=4*b+.5*70*b*b,extra=Math.max(0,t-burn),axis=record.axis,
    initialHeading=Math.atan2(axis.y,axis.x),aim=harpoonPredictionA(record.memory,t,record.positionM),
    desired=Math.atan2(aim.y-record.positionM.y,aim.x-record.positionM.x),
    heading=angNorm(initialHeading+clamp(angNorm(desired-initialHeading),-.15*extra,.15*extra)),
    horizontalExtra=225*extra,carrier=record.carrierVelocityMps;
  return {x:record.positionM.x+axis.x*axial+Math.cos(heading)*horizontalExtra+carrier.x*t,
    y:record.positionM.y+axis.y*axial+Math.sin(heading)*horizontalExtra+carrier.y*t,heading};
}
function harpoonMatchLaunchC(record,tr,step,prior=null){
  const measurementStep=Number(tr._lastMeasurementStep),elapsed=(measurementStep-record.releaseStep)*SIM_FIXED_DT,
    X=tr._kfX??[worldToMeters(tr.x),worldToMeters(tr.y),tr.z??0,worldSpeedToMps(tr.vx??0),worldSpeedToMps(tr.vy??0),tr.vz??0],
    sample={x:X[0],y:X[1],z:X[2],vx:X[3],vy:X[4],vz:X[5]},speed=Math.hypot(sample.vx,sample.vy),
    sigma=clamp(Number(tr.measurementSigmaM)||100,10,180),velSigma=clamp(Number(tr.velocitySigmaMps)||60,5,80),age=(step-measurementStep)*SIM_FIXED_DT;
  if(!Number.isFinite(measurementStep)||elapsed<=0||age<0||age>1||tr.sensorDetected===false||!(String(tr.sensorSource).startsWith('SPY1DV')||String(tr.sensorSource).startsWith('SPQ9B'))||
    record.excludedTrackIds.includes(tr.trackId)||speed<45||speed>430||sample.z>600||sample.z< -50)return null;
  if(prior){
    const gap=(measurementStep-prior.lastStep)*SIM_FIXED_DT;
    if(gap<=0||gap>4)return null;
    const error=Math.hypot(sample.x-prior.x-prior.vx*gap,sample.y-prior.y-prior.vy*gap),
      gate=Math.min(650,80+3*sigma+velSigma*gap+20*gap*gap),dv=Math.hypot(sample.vx-prior.vx,sample.vy-prior.vy);
    if(error>gate||dv>50+40*gap+2*velSigma)return null;
    return {...sample,lastStep:measurementStep,score:error/gate,hits:prior.hits+1,firstStep:prior.firstStep};
  }
  if(elapsed>12||record.claimedTrackId!=null&&record.claimedTrackId!==tr.trackId)return null;
  const p=harpoonLaunchPredictionC(record,elapsed),gate=Math.min(600,120+elapsed*25+2*sigma),error=Math.hypot(sample.x-p.x,sample.y-p.y),
    velocityHeading=Math.atan2(sample.vy,sample.vx);
  if(error>gate||Math.abs(angNorm(velocityHeading-p.heading))>Math.PI/4)return null;
  return {...sample,lastStep:measurementStep,score:error/gate,hits:1,firstStep:measurementStep};
}
function harpoonTrackIdentityC(tr){
  const runtime=ACTIVE_SHIP_RUNTIME?.weapons?.harpoon,records=runtime?.launches;
  if(!records?.length)return null;
  const now=simStepCounter,prior=tr._harpoonOwnC,measurementStep=Number(tr._lastMeasurementStep);
  if(prior&&prior.lastStep===measurementStep){
    return (now-prior.lastStep)*SIM_FIXED_DT<=4?{identity:prior.confirmed?'FRIEND':'UNKNOWN',reason:prior.confirmed?'OWN_LAUNCH_RADAR_CORRELATION':'POSSIBLE_OWN_LAUNCH'}:null;
  }
  const ranked=[];
  for(const record of records){
    const match=harpoonMatchLaunchC(record,tr,now,prior?.launchId===record.id&&prior.hits?prior:null);
    if(match)ranked.push({record,match});
  }
  ranked.sort((a,b)=>a.match.score-b.match.score);
  // Multiple compatible rounds/files are unresolved. Never guess a physical identity.
  const best=ranked[0],ambiguous=ranked.length>1&&ranked[1].match.score-best.match.score<.25;
  if(!best){tr._harpoonOwnC=null;return null;}
  if(ambiguous){tr._harpoonOwnC={lastStep:measurementStep,confirmed:false,launchId:null,evidence:'AMBIGUOUS_LAUNCH_CORRELATION'};return {identity:'UNKNOWN',reason:'POSSIBLE_OWN_LAUNCH'};}
  const {record,match}=best,confirmed=match.hits>=3&&(match.lastStep-match.firstStep)*SIM_FIXED_DT>=.15;
  tr._harpoonOwnC={...match,launchId:record.id,tubeId:record.tubeId,confirmed,evidence:'LAUNCH_CORRELATED_ANONYMOUS_RADAR'};
  if(confirmed)record.claimedTrackId=tr.trackId;
  return {identity:confirmed?'FRIEND':'UNKNOWN',reason:confirmed?'OWN_LAUNCH_RADAR_CORRELATION':'POSSIBLE_OWN_LAUNCH'};
}
function harpoonOperatorPictureC(){
  const rows=Array.from(tracks.values());
  return {schema:'HARPOON_SHIP_KNOWLEDGE_C1',dataLink:false,telemetryAvailable:false,
    launches:harpoonRuntimeA().launches.map(record=>{
      const tr=rows.find(t=>t._harpoonOwnC?.launchId===record.id&&t._harpoonOwnC.confirmed&&(simStepCounter-t._harpoonOwnC.lastStep)*SIM_FIXED_DT<=4),
        age=tr?(simStepCounter-tr._harpoonOwnC.lastStep)*SIM_FIXED_DT:null;
      return {id:record.id,tubeId:record.tubeId,elapsedS:Math.max(0,(simStepCounter-record.releaseStep)*SIM_FIXED_DT),
        trackId:tr?.trackId??null,source:tr?(age<=.35&&!tr.memActive?'RADAR':'ESTIMATE'):'NOT_OBSERVED',measurementAgeS:age,
        positionM:tr?{x:worldToMeters(tr.x),y:worldToMeters(tr.y),z:tr.z}:null,
        positionSigmaM:tr?trackCovarianceMetrics(tr).posSigmaM:null};
    })};
}
function harpoonKnowledgeCoreAuditC(){
  const record={id:1,releaseStep:0,positionM:{x:0,y:0,z:10},axis:{x:1,y:0,z:.55},carrierVelocityMps:{x:0,y:0,z:0},
    memory:{positionM:{x:8000,y:0,z:8},velocityMps:{x:0,y:0,z:0},observationAgeS:0},excludedTrackIds:[99],claimedTrackId:null},
    tr={trackId:1,_lastMeasurementStep:300,sensorDetected:true,sensorSource:'SPY1DV_SEARCH',measurementSigmaM:10,velocitySigmaMps:10,
      _kfX:[harpoonLaunchPredictionC(record,5).x,0,100,225,0,0]},match=harpoonMatchLaunchC(record,tr,300),checks={};
  checks.anonymousOutboundObservationMatches=!!match;
  checks.oldFileCannotBecomeOwn=harpoonMatchLaunchC(record,{...tr,trackId:99},300)==null;
  checks.inboundCrossingCannotBecomeOwn=harpoonMatchLaunchC(record,{...tr,_kfX:[tr._kfX[0],0,100,-225,0,0]},300)==null;
  checks.noMeasurementCannotBecomeOwn=harpoonMatchLaunchC(record,{...tr,_lastMeasurementStep:null},300)==null;
  checks.lateNewFileHasNoAutomaticFriendship=harpoonMatchLaunchC(record,{...tr,_lastMeasurementStep:900},900)==null;
  checks.noTruthInputs=record.memory.truthUsed!==true;
  return {schema:'HARPOON_C_KNOWLEDGE_AUDIT',checks,pass:Object.values(checks).every(Boolean)};
}
