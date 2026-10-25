// ENV_D DIAGNOSTIC_ONLY. All clock, RNG, ASM targets and SAMs are detached.
// Native constructor, INS, flight, fuze, computeInterceptPk, applyInterceptResult
// and the native Kh-32 mission-kill layer are copied without source edits.
// Only ideal sensor/transport boundaries and straight target motion are imposed.
function idealState(source='DL_TRACK') {
 const t=enemyMissiles[0];
 return {isValid:!!t,source,confidence:1,
  posM:{x:worldToMeters(t.x),y:worldToMeters(t.y),z:t.z},
  velMps:{x:worldSpeedToMps(t.vx),y:worldSpeedToMps(t.vy),z:t.vz??0},
  accMps2:{x:0,y:0,z:0},latencySec:0,noiseSigmaM:0,
  canAcquireAuthority:true,canHoldAuthority:true};
}
function syncIdealRf(m) {
 const s=idealState();
 for(const key of ['_sarhRfSeeker',...(m.essmActiveSeeker?['_arhRfSeeker']:[])]) {
  const q=m[key]??(m[key]={_kfX:new Float64Array(6)});
  Object.assign(q,{mode:'TRACK',trackValid:true,lastHitAgeS:0,confidence:1});
  q._kfP=new Float64Array(36);q._kfX.set([s.posM.x,s.posM.y,s.posM.z,s.velMps.x,s.velMps.y,s.velMps.z]);
 }
}
function syncTarget() {
 const t=enemyMissiles[0];
 Object.assign(tracks.get(1),{x:t.x,y:t.y,z:t.z,vx:t.vx,vy:t.vy,vz:t.vz??0,
  ttl:100,sensorAge:0,confirmed:true,sensorDetected:true,trackQuality:1,
  kinematicQuality:1,fireControlQuality:1,_lastMeasurementStep:simStepCounter});
}
function runCase(c={}) {
 const weapon=c.weapon??'SM2',rangeKm=c.rangeKm??30,altM=c.altM??5000;
 const targetSpeedMps=c.targetSpeedMps??0,crossSpeedMps=c.crossSpeedMps??0;
 const rngSeed=(Number(c.rngSeed)>>>0)||1831565813;
 const navigationSeed=(Number(c.navigationSeed)>>>0)||2047861954;
 // Native SAM INS derives its stream from SIM_SEED_BASE, not BATTLESPACE_SEED.
 // Keep this independent of the global simRandom stream used for Pk/damage.
 SIM_SEED_BASE=navigationSeed;SIM_RNG_STATE=rngSeed;BATTLESPACE_SEED=navigationSeed;
 simStepCounter=0;missileSerial=1;enemyMslSerial=1;
 missiles.length=0;targetPool.length=0;enemyMissiles.length=0;tracks.clear();
 WIP88_LAST_PK_DETAIL=null;SIM_TEST_WIP87_PK_TRACE.length=0;
 WIP112_SYSTEM_HIT_LOG.length=0;WIP112_DIAG_ERRORS.length=0;
 const label=c.targetLabel??'Kh-35U';
 if(!Object.hasOwn(ASM_PROFILES,label))throw Error('UNKNOWN_NATIVE_ASM_LABEL:'+label);
 const heading=Math.hypot(targetSpeedMps,crossSpeedMps)>0?Math.atan2(crossSpeedMps,-targetSpeedMps):Math.PI;
 // Use the real ASM constructor and native damage-state initializer. No ASM AI
 // is stepped. Its launch transition/INS target do not drive diagnostic motion.
 spawnEnemyMissile({id:1,x:kmToWorld(rangeKm),y:0,z:altM,
  vx:mpsToWorldSpeed(-targetSpeedMps),vy:mpsToWorldSpeed(crossSpeedMps),
  heading,asmType:label,lastKnownShipX:0,lastKnownShipY:0});
 const t=enemyMissiles[0];
 Object.assign(t,{x:kmToWorld(rangeKm),y:0,z:altM,vz:0,
  vx:mpsToWorldSpeed(-targetSpeedMps),vy:mpsToWorldSpeed(crossSpeedMps),
  heading,speed:Math.hypot(mpsToWorldSpeed(targetSpeedMps),mpsToWorldSpeed(crossSpeedMps)),
  speedMps:Math.hypot(targetSpeedMps,crossSpeedMps)});
 wip112EnsureTargetState(t);
 tracks.set(1,{trackId:1,trackNumber:1,classification:'ASM',domain:'AIR',
  identity:'HOSTILE',isASM:true,_operatorIdentity:'HOSTILE',_kfP:Array(36).fill(0)});
 syncTarget();
 if(weapon==='ESSM')vlsReleaseEssmB1({});else vlsReleaseStandardB1({weaponType:weapon});
 const m=missiles[0];if(!m)throw Error('ENV_D_NATIVE_LAUNCH_FAILED');
 const samples=[],phases=[];let lastPhase='',apogeeM=m.z,burnout=null;
 let prevThrust=missileThrustN(m),prevVz=m.vz??0,descentStart=null;
 const phase=()=>[m._loftB4?.mode??'UNSET',m._loftB4?.phase??'',m._v1GuidancePhase??''].filter(Boolean).join('/');
 function row() {
  const speedMps=Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0);
  return {timeS:m.life,xM:worldToMeters(m.x),yM:worldToMeters(m.y),
   distanceKm:worldToKm(Math.hypot(m.x,m.y)),altitudeM:m.z,speedMps,
   mach:speedMps/speedOfSoundMps(m.z),targetXM:worldToMeters(t.x),
   targetYM:worldToMeters(t.y),targetAltitudeM:t.z,phase:phase()};
 }
 function markPhase() {
  const p=phase();if(p!==lastPhase){if(phases.length)phases.at(-1).endS=m.life;
   phases.push({phase:p,startS:m.life,endS:m.life});lastPhase=p;}
 }
 if(c.samples!==false)samples.push(row());markPhase();
 const maxTicks=Math.ceil((m.maxLife+1)/SIM_FIXED_DT);
 for(let i=0;i<maxTicks&&!m.dead&&t.alive;i++) {
  syncTarget();m.dlAlive=true;m.sarhAlive=true;m._illuminatorGuided=true;
  m._illuminatorId=0;m._illQuality=1;syncIdealRf(m);
  // Same lifecycle call and ordering as simulateFixedTick: observers are
  // installed before SAM flight; native ASM damage prefix runs after SAMs.
  wip112AttachObservers();
  updateMissile(m,SIM_FIXED_DT);
  if(t.alive)envNativeAsmDamagePrefixD(t,SIM_FIXED_DT);
  if(WIP112_DIAG_ERRORS.length)throw Error('NATIVE_ASM_OBSERVER_ERROR:'+WIP112_DIAG_ERRORS.join(';'));
  // Do not overwrite native damage/mission-kill changes on the terminal tick.
  if(t.alive){t.x+=mpsToWorldSpeed(-targetSpeedMps)*SIM_FIXED_DT;
   t.y+=mpsToWorldSpeed(crossSpeedMps)*SIM_FIXED_DT;}
  simStepCounter++;apogeeM=Math.max(apogeeM,m.z);markPhase();
  const thrust=missileThrustN(m);
  if(thrust<=0&&prevThrust>0)burnout=row();prevThrust=thrust;
  if(prevVz>=-.5&&(m.vz??0)<-.5)descentStart={...row(),mode:m._loftB4?.mode??null,
   stage:m._loftB4?.phase??null,guidance:m._v1GuidancePhase??null,
   cmdOmegaPit:m.cmdOmegaPit??null,kappaAz:m._wip79Kappa?.az??null,
   seaGuard:!!m._v1SeaClearanceGuard,seaMarginM:m._samTrajPlan?.seaMarginM??null};
  prevVz=m.vz??0;
  if(c.samples!==false&&simStepCounter%6===0)samples.push(row());
 }
 const terminal=row();if(phases.length)phases.at(-1).endS=m.life;
 if(c.samples!==false&&samples.at(-1)?.timeS!==terminal.timeS)samples.push(terminal);
 const reason=m._deathReason??'DIAGNOSTIC_TIMEOUT';
 const samResult=reason.startsWith('PROX_DETONATION_')?reason.slice('PROX_DETONATION_'.length):null;
 const retirementCause=t._wip11cRetirementQueued?.cause??null;
 // Encode already-resolved native destruction; no new kill threshold/model.
 const rawResult=!t.alive&&retirementCause==='WARHEAD_AIRBURST'?'KILL':
  !t.alive&&retirementCause==='DELAYED_STRUCTURAL_FAILURE'?'STRUCT_FAIL':samResult;
 const missionKills=[t._v1SeekerKilled?'SEEKER':null,t._v1CtrlDamaged?'CONTROL':null,t._v1StructDamaged?'STRUCT':null].filter(Boolean);
 const success=['KILL','STRUCT_FAIL','DAMAGED'].includes(rawResult)||missionKills.length>0;
 const lethal=rawResult==='KILL'||rawResult==='STRUCT_FAIL';
 return {weapon,profileId:m._v1Profile.id,targetLabel:label,rangeKm,altM,
  targetSpeedMps,crossSpeedMps,rngSeed,navigationSeed,success,lethal,
  outcome:rawResult??'FAILURE',samResult,missionKills,reason,retirementCause,
  closestM:m._everClosest!=null?m._everClosest*1000:null,
  fuzeMissM:m._fuzeBurstMissM??null,fragmentArrivalMissM:m._fuzeFragmentArrivalMissM??null,
  pk:WIP88_LAST_PK_DETAIL?.pk??null,fragmentPhysics:WIP88_LAST_PK_DETAIL,
  damage:{alive:!!t.alive,structuralDamage:t._structDmg??0,guidanceDegraded:!!t._guidanceDegraded,
   systemDamage:{...t._systemDamage},warheadState:t._warheadState,
   nativeOutcome:t._wip113Outcome??null,projectedImpactMassKg:t._wip112ProjectedImpactMassKg,
   behavior:wip113RefreshBehavior(t),fragmentEvents:WIP112_SYSTEM_HIT_LOG.length},
  interceptPointKm:success?terminal.distanceKm:null,
  targetInterceptPointKm:success?worldToKm(Math.hypot(t.x,t.y)):null,
  apogeeM,flightTimeS:m.life,burnout,terminal,phases,
  descentStart:reason==='SEA_IMPACT'?descentStart:null,
  samples:c.samples===false?undefined:samples,ticks:simStepCounter,
  rng:SIM_RNG_STATE>>>0,terminationReason:m._gameTermReason??null,
  batteryRemainingS:m._gameBatteryRemainingS??null};
}
return {runCase,profiles:()=>Object.keys(SAM_MISSILE_PROFILES),asmLabels:()=>Object.keys(ASM_PROFILES),
 snapshot:()=>({tick:simStepCounter,rng:SIM_RNG_STATE>>>0,missiles:missiles.length})};
