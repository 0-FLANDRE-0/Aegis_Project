// ENV_C RANGE_A: continuous ideal RF observations also feed termination.
// DIAGNOSTIC_ONLY. This scope owns its clock, RNG, targets and missiles.
// The native source capsule is created with new Function: no live lexical scope.
function idealState(source='DL_TRACK') {const t=targetPool[0];return {isValid:!!t,source,confidence:1,posM:{x:worldToMeters(t.x),y:worldToMeters(t.y),z:t.z},velMps:{x:worldSpeedToMps(t.vx),y:worldSpeedToMps(t.vy),z:0},accMps2:{x:0,y:0,z:0},latencySec:0,noiseSigmaM:0,canAcquireAuthority:true,canHoldAuthority:true};}
function syncIdealRf(m){
 const t=targetPool[0];
 function fill(key){
  const s=m[key]??(m[key]={_kfX:new Float64Array(6)}),x=s._kfX;
  s.mode='TRACK';s.trackValid=true;s.lastHitAgeS=0;s.confidence=1;
  x[0]=worldToMeters(t.x);x[1]=worldToMeters(t.y);x[2]=t.z;
  x[3]=worldSpeedToMps(t.vx);x[4]=worldSpeedToMps(t.vy);x[5]=0;
 }
 fill('_sarhRfSeeker');if(m.essmActiveSeeker)fill('_arhRfSeeker');
}
function syncTarget(){const t=targetPool[0];const tr=tracks.get(1);Object.assign(tr,{x:t.x,y:t.y,z:t.z,vx:t.vx,vy:t.vy,vz:0,ttl:100,sensorAge:0,confirmed:true,sensorDetected:true,trackQuality:1,kinematicQuality:1,fireControlQuality:1,_lastMeasurementStep:simStepCounter});}
function runCase(c={}){
 simStepCounter=0;SIM_RNG_STATE=1831565813;missileSerial=1;missiles.length=0;targetPool.length=0;enemyMissiles.length=0;tracks.clear();
 const diagnosticTicks=[];
 const weapon=c.weapon??'SM2',rangeKm=c.rangeKm??30,altM=c.altM??5000,targetSpeedMps=c.targetSpeedMps??0;
 const crossMps=c.crossSpeedMps??0;
 targetPool.push({id:1,x:kmToWorld(rangeKm),y:0,z:altM,vx:mpsToWorldSpeed(-targetSpeedMps),vy:mpsToWorldSpeed(crossMps),vz:0,alive:true,heading:Math.atan2(crossMps,-targetSpeedMps),speedMps:Math.hypot(targetSpeedMps,crossMps),rcsM2:5});
 tracks.set(1,{trackId:1,trackNumber:1,classification:'AIR',domain:'AIR',identity:'HOSTILE',isASM:false,_operatorIdentity:'HOSTILE',_kfP:Array(36).fill(0)});syncTarget();
 if(weapon==='ESSM')vlsReleaseEssmB1({});else vlsReleaseStandardB1({weaponType:weapon});
 const m=missiles[0];if(!m)throw Error('ENV_LAUNCH_FAILED');
 const samples=[],phases=[];let apogeeM=m.z,burnout=null,lastPhase='',prevThrust=0;
 function sample(){const speedMps=Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0),phase=[m._loftB4?.mode??'UNSET',m._loftB4?.phase??'',m._v1GuidancePhase??'',m._samTrajPlan?.highTargetShelfAltM!=null?'HIGH_SHELF':''].filter(Boolean).join('/');
 if(phase!==lastPhase){if(phases.length)phases.at(-1).endS=m.life;phases.push({phase,startS:m.life,endS:m.life});lastPhase=phase;}
 const row={timeS:m.life,distanceKm:worldToKm(Math.hypot(m.x,m.y)),xM:worldToMeters(m.x),yM:worldToMeters(m.y),altitudeM:m.z,speedMps,mach:speedMps/speedOfSoundMps(m.z),targetXM:worldToMeters(targetPool[0].x),targetAltitudeM:altM,phase,loftDemand:m._samTrajPlan?.loftDemand??null,cruiseAltM:m._samTrajPlan?.cruiseAltM??null,shelfM:m._loftB4?.shelfM??null,highTargetShelfAltM:m._samTrajPlan?.highTargetShelfAltM??null};samples.push(row);return row;}
 sample();const maxTicks=Math.ceil((m.maxLife+1)/SIM_FIXED_DT);
 for(let i=0;i<maxTicks&&!m.dead&&targetPool[0].alive;i++){
 syncTarget();m.dlAlive=true;m.sarhAlive=true;m._illuminatorGuided=true;m._illuminatorId=0;m._illQuality=1;
 const previousKappaDebug=m._wip79Kappa;syncIdealRf(m);updateMissile(m,SIM_FIXED_DT);const t=targetPool[0];t.x+=t.vx*SIM_FIXED_DT;t.y+=t.vy*SIM_FIXED_DT;syncTarget();simStepCounter++;
 apogeeM=Math.max(apogeeM,m.z);const thrust=missileThrustN(m);if(thrust<=0&&prevThrust>0)burnout={timeS:m.life,distanceKm:worldToKm(Math.hypot(m.x,m.y)),altitudeM:m.z,speedMps:Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0)};prevThrust=thrust;
 if(c.telemetry){const p=m._samTrajPlan??{},k=m._wip79Kappa??{},st=m._v1TargetState??{};diagnosticTicks.push({timeS:m.life,xM:worldToMeters(m.x),yM:worldToMeters(m.y),altitudeM:m.z,vzMps:m.vz,speedMps:Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0),bodyPitchRad:m.pitch,velocityPitchRad:m.velPitch,cmdOmegaPit:m.cmdOmegaPit,actualOmegaPit:m.actOmegaPit,finPitchRad:m.finPitch,normalAccZ:m._samPrevNormalAccWorld?.z??null,guidance:m._v1GuidancePhase??null,source:st.source??null,terminalLatched:!!m._wip79KappaTerminalLatched,kappaActive:!!m._wip79KappaActive,kappaAz:k.az??null,kappaFresh:m._wip79Kappa!==previousKappaDebug,configuredPolicy:String(m._wip79KappaTerminalPolicy??window.WIP79_KAPPA_TERMINAL_POLICY??'PIP_LOS'),kappaPolicy:k.policy??null,kappaTgoS:k.tgo??null,kappaTgoCapS:k.tgoCapS??null,kappaPipM:structuredClone(k.pip??null),kappaTargetPipM:structuredClone(k.targetPip??k.pip??null),kappaVFinalMps:structuredClone(k.vFinal??null),waypointB4:!!k.waypointB4,targetEstimateAltitudeM:st.posM?.z??null,heightAboveTargetEstimateM:st.posM?.z!=null?m.z-st.posM.z:null,kappaPipZ:k.pip?.z??null,kappaGammaFDeg:k.gammaFDeg??null,kappaTgoS:k.tgo??null,rangeKm:m._rangeKmCached??null,mode:m._loftB4?.mode??null,phase:m._loftB4?.phase??null,loftTransitions:structuredClone(m._loftB4?.transitions??[]),cruiseAltM:p.cruiseAltM??null,loftDemand:p.loftDemand??null,seaMarginM:p.seaMarginM??null,seaGuardActive:!!m._v1SeaClearanceGuard,seaProjectedAltM:m._v1SeaProjectedAltM??null,softGuard:!!m._v1SoftGuard,targetXM:worldToMeters(t.x),targetYM:worldToMeters(t.y),targetAltitudeM:t.z,dead:!!m.dead});}
 if(c.samples!==false&&simStepCounter%6===0)sample();
 }
 const terminal=sample();if(phases.length)phases.at(-1).endS=m.life;
 const success=!targetPool[0].alive&&!!m.proxDetonated;
 return {weapon,profileId:m._v1Profile.id,rangeKm,altM,targetSpeedMps,crossSpeedMps:crossMps,interceptPointKm:success?terminal.distanceKm:null,terminationPointKm:terminal.distanceKm,diagnosticTicks:c.telemetry?diagnosticTicks:undefined,success,reason:success?'INTERCEPT_SUCCESS':m._deathReason??'DIAGNOSTIC_TIMEOUT',closestM:m._everClosest!=null?m._everClosest*1000:null,fuzeMissM:m._fuzeBurstMissM??null,apogeeM,flightTimeS:m.life,burnout,terminal,phases,samples:c.samples===false?undefined:samples,ticks:simStepCounter,rng:SIM_RNG_STATE>>>0,terminationReason:m._gameTermReason??null,batteryRemainingS:m._gameBatteryRemainingS??null};
}
return {runCase,profiles:()=>Object.entries(SAM_MISSILE_PROFILES).map(([id,q])=>({id,name:q.displayName})),snapshot:()=>({tick:simStepCounter,rng:SIM_RNG_STATE>>>0,missiles:missiles.length})};
