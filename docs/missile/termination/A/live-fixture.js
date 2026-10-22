// TEST ONLY. Inject into a disposable whole-game page; never ship this fixture.
// Native launch, INS, RF frontends/EKFs, allocation, B4, Kappa, forces and fuze
// are executed. Only the scenario's radar track and linear target motion are
// controlled here. RF denial removes receiver measurements, not track states.
let TERM_LIVE_LAST_MISSILE_A=null;
window.__TERM_LIVE_TEST__={run(c={}){
 const weapon=c.weapon??'SM2',seed=c.seed??1831565813;
 _wip75ResetCase(seed);nextTargetId=1;engagementControlMode='MANUAL';
 window.AEGIS_GAME_TERMINATION_ENABLED=c.enabled!==false;
 const ax=aircraft.x(),ay=aircraft.y(),brg=deg(c.bearingDeg??0);
 const t=makeBaseTarget(ax+Math.cos(brg)*kmToWorld(c.rangeKm??30),ay+Math.sin(brg)*kmToWorld(c.rangeKm??30),brg+Math.PI,c.targetSpeedMps??250);
 t.z=c.altM??5000;t.vz=0;t.acType='Su-35';t._testFixture=true;targetPool.push(t);
 const tid=trackIdForTruthV27('AIR',t.id,true);
 const sync=()=>{if(!t.alive)return;const tr=getOrMakeTrack(tid,t.x,t.y,t.vx,t.vy,t.z,0,trackTruthRefV27('AIR',t.id));Object.assign(tr,{x:t.x,y:t.y,z:t.z,vx:t.vx,vy:t.vy,vz:0,trackQuality:1,kinematicQuality:1,fireControlQuality:1,confirmed:true,sensorDetected:true,sensorAge:0,sensorHits:99,sensorSource:'TEST',classification:'FIGHTER',classificationConfidence:1,_lastMeasurementStep:simStepCounter,ttl:TRACK_HARD_TTL});tr._operatorIdentity='HOSTILE';tr.identity='HOSTILE';};
 sync();selectedLockId=tid;
 // Scenario loadout only: install the requested round in a real usable cell.
 vlsCells.fwd[0]=wip125MakeInstalledCell('fwd',0,weapon==='ESSM'?'ESSM4':weapon);
 if(c.useRequest){if(weapon==='ESSM')spawnESSM();else spawnMissile({weaponType:weapon});}
 else if(weapon==='ESSM')vlsReleaseEssmB1({});else vlsReleaseStandardB1({weaponType:weapon});
 const m=missiles.at(-1);if(!m)return {error:'NATIVE_RELEASE_BLOCKED',weapon,seed};TERM_LIVE_LAST_MISSILE_A=m;
 const originalArh=_arhBuildMeasurementSet,originalSarh=_sarhBuildMeasurementSet;
 let deny=c.scenario==='NO_ACQUISITION',firstTrackS=null,denialS=null,restoredS=null,removed=false,hadGap=false,reacquired=false;
 const empty=p=>({...p,physicalEchoes:[],echoes:[],clusters:[],measurements:[]});
 _arhBuildMeasurementSet=function(...a){const p=originalArh(...a);return deny&&c.denyKind!=='SARH'?empty(p):p;};
 _sarhBuildMeasurementSet=function(...a){const p=originalSarh(...a);return deny&&c.denyKind!=='ARH'?empty(p):p;};
 const samples=[],events=[];let lastKey='',apogeeM=m.z,checkpointApplied=false;
 const sample=()=>{const s=(m.isESSM||m.isSM6)?m._arhRfSeeker:m._sarhRfSeeker;return {lifeS:m.life,batteryRemainingS:m._gameBatteryRemainingS??null,positionM:[worldToMeters(m.x),worldToMeters(m.y),m.z],speedMps:Math.hypot(worldSpeedToMps(m.vx??0),worldSpeedToMps(m.vy??0),m.vz??0),rfMode:s?.mode??'OFF',rfValid:!!s?.trackValid,hitAgeS:s?.lastHitAgeS??null,confidence:s?.confidence??0,active:!!m.essmActiveSeeker,sarhAlive:!!m.sarhAlive,authority:m._v1GuidanceAuthority??null,term:m._gameFlightTerm?{...m._gameFlightTerm}:null,dead:!!m.dead,prox:!!m.proxDetonated,reason:m._deathReason??null,loft:m._loftB4?{mode:m._loftB4.mode,phase:m._loftB4.phase,shelfM:m._loftB4.shelfM,goalM:m._loftB4.gameDesiredShelfM,replans:m._loftB4.gameShelfReplans}:null};};
 try{
  for(let i=0;i<Math.ceil((c.maxTimeS??m.maxLife+1)/SIM_FIXED_DT)&&!m.dead;i++){
   if(c.checkpointLifeS!=null&&!checkpointApplied&&m.life>=(c.checkpointAtS??80)){
    events.push({type:'TEST_CLOCK_CHECKPOINT',fromS:m.life,toS:c.checkpointLifeS});
    m.life=c.checkpointLifeS;checkpointApplied=true;
   }
   sync();allocateDatalinks();spg62ServoStep(SIM_FIXED_DT);allocateSARH();
   if(c.dropDl&&(m.essmActiveSeeker||firstTrackS!=null)){m.dlAlive=false;}
   updateMissile(m,SIM_FIXED_DT);if(t.alive){t.x+=t.vx*SIM_FIXED_DT;t.y+=t.vy*SIM_FIXED_DT;sync();}simStepCounter++;
   apogeeM=Math.max(apogeeM,m.z);const s=(m.isESSM||m.isSM6)?m._arhRfSeeker:m._sarhRfSeeker;
   const fresh=s?.mode==='TRACK'&&s.trackValid&&(s.lastHitAgeS??999)<=.30&&(s.confidence??0)>=.13;
   if(fresh&&firstTrackS==null)firstTrackS=m.life;
   if(firstTrackS!=null&&denialS==null&&['LOSS','REACQUIRE'].includes(c.scenario)&&m.life>=firstTrackS+.3){deny=true;denialS=m.life;events.push({type:'RF_DENIED',lifeS:m.life});if(c.removeTarget){t.alive=false;tracks.delete(tid);removed=true;}}
   if(c.scenario==='REACQUIRE'&&denialS!=null&&restoredS==null&&m.life>=denialS+(c.gapS??.65)){deny=false;restoredS=m.life;events.push({type:'RF_RESTORED',lifeS:m.life});}
   if(deny&&!fresh)hadGap=true;if(restoredS!=null&&fresh)reacquired=true;
   const key=[s?.mode,m._v1GuidanceAuthority,m._loftB4?.phase,m.dead].join('/');
   if(key!==lastKey){events.push({...sample(),event:'STATE'});lastKey=key;}
   if(c.samples!==false&&i%6===0)samples.push(sample());
   if(m.proxDetonated||(!t.alive&&!removed))break;
  }
 }finally{_arhBuildMeasurementSet=originalArh;_sarhBuildMeasurementSet=originalSarh;}
 return {weapon,seed,scenario:c.scenario??'NORMAL',enabled:c.enabled!==false,rangeKm:c.rangeKm,altM:c.altM,targetSpeedMps:c.targetSpeedMps??250,maxLifeS:m.maxLife,releaseRequest:c.useRequest===true,releaseRecord:m._vlsReleaseB2??null,success:!t.alive&&!removed&&!!m.proxDetonated,reason:m._deathReason??'FIXTURE_TIMEOUT',flightTimeS:m.life,apogeeM,closestM:m._everClosest!=null?m._everClosest*1000:null,fuzeMissM:m._fuzeBurstMissM??null,firstTrackS,denialS,restoredS,hadGap,reacquired,final:sample(),events,samples};
}};
window.__TERM_LIVE_TEST__.observe=()=>{const m=TERM_LIVE_LAST_MISSILE_A;return m?{id:m.id,profileId:m._v1Profile?.id,lifeS:m.life,dead:!!m.dead,reason:m._deathReason??null,prox:!!m.proxDetonated,positionM:[worldToMeters(m.x),worldToMeters(m.y),m.z],term:m._gameFlightTerm??null}:null;};
window.__TERM_LIVE_TEST__.prepareObserved=c=>{
 _wip75ResetCase(c.seed??1831565813);nextTargetId=1;engagementControlMode='MANUAL';window.AEGIS_GAME_TERMINATION_ENABLED=c.enabled!==false;
 const brg=deg(c.bearingDeg??45),range=kmToWorld(c.rangeKm??30),t=makeBaseTarget(aircraft.x()+Math.cos(brg)*range,aircraft.y()+Math.sin(brg)*range,brg+Math.PI,250);t.z=5000;t.acType='Su-35';t._testFixture=true;t.chaffCooldown=10000;targetPool.push(t);
 vlsCells.fwd[0]=wip125MakeInstalledCell('fwd',0,c.weapon==='ESSM'?'ESSM4':c.weapon);
 return {targetCreated:true,syntheticTrackCreated:false};
};
window.__TERM_LIVE_TEST__.launchObserved=c=>{
 const candidates=[...tracks].filter(([id,tr])=>trackIsDisplayable(tr)&&trackIsFireControlQuality(tr)&&(tr.z??0)>1000&&!tr.isASM).sort((a,b)=>(b[1].trackQuality??0)-(a[1].trackQuality??0));
 if(!candidates.length)return {error:'NO_NATIVE_FCQ_TRACK',tracks:[...tracks].map(([id,t])=>({id,classification:t.classification,confirmed:t.confirmed,quality:t.trackQuality,fcq:t.fireControlQuality,age:t.sensorAge}))};
 const [id,tr]=candidates[0];setTrackOperatorIdentityA3(id,'HOSTILE');lockCursor.x=tr.x;lockCursor.y=tr.y;lockByCursor(id);
 if(c.weapon==='ESSM')spawnESSM();else spawnMissile({weaponType:c.weapon});
 TERM_LIVE_LAST_MISSILE_A=missiles.at(-1);
 return {trackId:id,localSensorSource:tr.sensorSource,trackQuality:tr.trackQuality,fireControlQuality:tr.fireControlQuality,launched:!!TERM_LIVE_LAST_MISSILE_A,releaseRecord:TERM_LIVE_LAST_MISSILE_A?._vlsReleaseB2??null};
};
window.__TERM_LIVE_TEST__.afterAction=()=>({tag:'AFTER_ACTION_TRUTH_TEST_ONLY',targetAlive:targetPool[0]?.alive??false,missile:window.__TERM_LIVE_TEST__.observe()});
window.__TERM_LIVE_TEST__.debugObserved=()=>({emconActive,equipmentOffline:shipEquipmentOfflineV1(),targets:targetPool.map(t=>({id:t.id,alive:t.alive,x:t.x,y:t.y,z:t.z})),spy:spySchedulerSnapshot(),los:targetPool[0]?window.__NAVAL_SIM_DIAG__.spyLosForTruth('AIR',targetPool[0].id):null});
