// Independent RF seeker. Diagnostic observation injection is never used by the live caller.
function harpoonSeekerA(m,dt,diagnosticObservations=null){
  const s=m.seeker,cfg=HARPOON_PROFILE_A.sim,nav=m.ins,pred=harpoonPredictionA(m.memory,m.ageS,m.navPositionM),
    time=harpoonMemoryElapsedC(m.memory,m.ageS),memoryNow={x:m.memory.positionM.x+m.memory.velocityMps.x*time,y:m.memory.positionM.y+m.memory.velocityMps.y*time},
    track=s.lock??s.candidate,cue=track?{x:track.x+track.vx*s.missedS,y:track.y+track.vy*s.missedS}:memoryNow,
    rangeToBasket=Math.hypot(pred.x-m.navPositionM.x,pred.y-m.navPositionM.y);
  if(!s.active&&m.ageS>=cfg.boosterBurnS&&rangeToBasket<=cfg.seekerActivationRangeM){s.active=true;s.mode='SEARCH';s.missedS=0;}
  if(!s.active)return;
  const P=m.memory.covariance,t=time,cxx=Math.max(0,P[0]+t*(P[3]+P[18])+t*t*P[21]),cyy=Math.max(0,P[7]+t*(P[10]+P[25])+t*t*P[28]),
    cxy=P[1]+t*(P[4]+P[19])+t*t*P[22],lambda=(cxx+cyy+Math.hypot(cxx-cyy,2*cxy))*.5,
    cueGate=Math.min(cfg.seekerSearchBasketM,Math.max(250,3*Math.sqrt(lambda+75**2+(t*t*.04)**2))),
    desired=angNorm(Math.atan2(cue.y-m.navPositionM.y,cue.x-m.navPositionM.x)-nav.yawRad),
    half=Math.min(cfg.seekerGimbalRad,Math.max(cfg.seekerMinSweepRad,Math.atan2(cueGate,Math.max(1000,rangeToBasket)))),
    lo=clamp(desired-half,-cfg.seekerGimbalRad,cfg.seekerGimbalRad),hi=clamp(desired+half,-cfg.seekerGimbalRad,cfg.seekerGimbalRad);
  s.scanBoundsRad=[lo,hi];
  let command=clamp(desired,-cfg.seekerGimbalRad,cfg.seekerGimbalRad);
  if(s.mode==='SEARCH'){
    command=clamp(s.azRelRad+s.scanDirection*cfg.seekerScanRadS*dt,lo,hi);
    if((s.scanDirection>0&&command>=hi-1e-10)||(s.scanDirection<0&&command<=lo+1e-10)){s.scanDirection*=-1;s.scanReversals++;}
  }
  s.azRelRad=clamp(s.azRelRad+clamp(command-s.azRelRad,-cfg.seekerSlewRadS*dt,cfg.seekerSlewRadS*dt),-cfg.seekerGimbalRad,cfg.seekerGimbalRad);
  const elCommand=clamp(Math.atan2(-m.radarAltitudeM,Math.max(100,rangeToBasket))-nav.pitchRad,-cfg.seekerElGimbalRad,cfg.seekerElGimbalRad);
  s.elRelRad=clamp(s.elRelRad+clamp(elCommand-s.elRelRad,-cfg.seekerSlewRadS*dt,cfg.seekerSlewRadS*dt),-cfg.seekerElGimbalRad,cfg.seekerElGimbalRad);
  s.timerS+=dt;s.missedS+=dt;
  if(s.lock&&s.missedS>=cfg.seekerCoastS){s.lock=null;s.lockCount=0;s.mode='SEARCH';}
  if(s.candidate&&s.missedS>=cfg.seekerAcquireGapS){s.candidate=null;s.lockCount=0;s.mode='SEARCH';}
  if(s.timerS+1e-10<cfg.seekerPeriodS)return;s.timerS-=cfg.seekerPeriodS;
  const obs=diagnosticObservations??harpoonRfObservationsA(m,m.yawRad+s.azRelRad,m.pitchRad+s.elRelRad),current=s.lock??s.candidate,
    gate=current?cfg.seekerTrackGateM+12*s.missedS:cueGate,
    reference=current?{x:current.x+current.vx*s.missedS,y:current.y+current.vy*s.missedS}:memoryNow,candidates=[];
  s.lastObservations=obs;s.observations+=obs.length;
  for(const o of obs){
    // Beam, both gimbals, range and measured surface/Doppler evidence apply in every mode.
    if(!Number.isFinite(o.rangeM)||o.rangeM<25||o.rangeM>cfg.seekerRangeM||Math.abs(o.bearingRad)>cfg.seekerGimbalRad||Math.abs(o.elevationRad)>cfg.seekerElGimbalRad||
      Math.abs(angNorm(o.bearingRad-s.azRelRad))>cfg.seekerBeamHalfRad||Math.abs(o.elevationRad-s.elRelRad)>cfg.seekerBeamHalfElRad||
      o.snr<cfg.seekerMinSnr||o.verticalExtentM<1.4||o.dopplerSpreadMps>4)continue;
    const bearing=angNorm(nav.yawRad+o.bearingRad),elevation=nav.pitchRad+o.elevationRad,horizontal=o.rangeM*Math.cos(elevation),
      x=m.navPositionM.x+horizontal*Math.cos(bearing),y=m.navPositionM.y+horizontal*Math.sin(bearing),error=Math.hypot(x-reference.x,y-reference.y);
    if(error>gate)continue;
    const expectedRadial=((current?.vx??m.memory.velocityMps.x)-nav.velocityMps.x)*Math.cos(bearing)+((current?.vy??m.memory.velocityMps.y)-nav.velocityMps.y)*Math.sin(bearing);
    if(Math.abs(o.radialMps-expectedRadial)>20+(current?0:10))continue;
    candidates.push({o,x,y,score:error/Math.max(35,gate)-.06*Math.log1p(o.snr)});
  }
  candidates.sort((a,b)=>a.score-b.score);const best=candidates[0];
  if(best){
    let file=current;
    if(!file)file={x:best.x,y:best.y,vx:m.memory.velocityMps.x,vy:m.memory.velocityMps.y};
    else{const h=Math.max(cfg.seekerPeriodS,s.missedS),px=file.x+file.vx*h,py=file.y+file.vy*h,ex=best.x-px,ey=best.y-py;
      file.x=px+.42*ex;file.y=py+.42*ey;file.vx=clamp(file.vx+.04*ex/h,-35,35);file.vy=clamp(file.vy+.04*ey/h,-35,35);}
    s.missedS=0;s.lockCount++;
    if(s.lock||s.lockCount>=cfg.seekerAcquireHits){s.lock=file;s.candidate=null;s.mode='TRACK';}
    else{s.candidate=file;s.mode='ACQUIRE';}
  }else if(s.lock)s.mode='COAST';
}
function harpoonSeekerCoreAuditC(){
  const cfg=HARPOON_PROFILE_A.sim,memory={positionM:{x:6000,y:0,z:10},velocityMps:{x:0,y:0,z:0},covariance:Array(36).fill(0),observationAgeS:0},
    make=()=>({memory,ageS:4,navPositionM:{x:0,y:0,z:15},radarAltitudeM:15,ins:{yawRad:0,pitchRad:0,velocityMps:{x:289,y:0,z:0}},yawRad:0,pitchRad:0,
      seeker:{active:false,mode:'OFF',timerS:0,azRelRad:0,elRelRad:0,scanDirection:1,scanReversals:0,scanBoundsRad:[0,0],candidate:null,lock:null,lockCount:0,missedS:0,lastObservations:[],observations:0}}),
    o={rangeM:6000,bearingRad:0,elevationRad:0,radialMps:-289,verticalExtentM:8,dopplerSpreadMps:.8,snr:30},m=make(),checks={};
  harpoonSeekerA(m,.1,[o]);checks.firstHitIsAcquisition=m.seeker.mode==='ACQUIRE'&&!m.seeker.lock;
  harpoonSeekerA(m,.1,[o]);checks.secondHitStillNoGuidanceLock=!m.seeker.lock;
  harpoonSeekerA(m,.1,[o]);checks.confirmedRepeatedObservationsTrack=m.seeker.mode==='TRACK'&&!!m.seeker.lock;
  harpoonSeekerA(m,.1,[]);checks.noReturnCoasts=m.seeker.mode==='COAST';
  for(let i=0;i<41;i++)harpoonSeekerA(m,.1,[]);checks.coastTimeoutReentersSearch=m.seeker.mode==='SEARCH'&&!m.seeker.lock;
  const scan=make();for(let i=0;i<100;i++)harpoonSeekerA(scan,.1,[]);
  checks.searchReversesBothDirections=scan.seeker.scanReversals>=6;checks.hardAzElStops=Math.abs(scan.seeker.azRelRad)<=cfg.seekerGimbalRad&&Math.abs(scan.seeker.elRelRad)<=cfg.seekerElGimbalRad;
  const far=make();far.memory={...memory,positionM:{x:25000,y:0,z:10}};harpoonSeekerA(far,.1,[o]);checks.noPrematureActivation=!far.seeker.active;
  const bad=make();harpoonSeekerA(bad,.1,[{...o,bearingRad:cfg.seekerGimbalRad+.001}]);checks.beyondGimbalCannotAcquire=!bad.seeker.candidate&&!bad.seeker.lock;
  const isolated=make();harpoonSeekerA(isolated,.1,[o]);for(let i=0;i<4;i++)harpoonSeekerA(isolated,.1,[]);checks.singleEchoExpires=isolated.seeker.mode==='SEARCH'&&!isolated.seeker.candidate;
  return {schema:'HARPOON_C_SEEKER_AUDIT',checks,pass:Object.values(checks).every(Boolean)};
}
