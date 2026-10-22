/**
 * AEGIS v48 GAME-ONLY Flight Termination Controller.
 * Source transform for the expanded c55-game-main JS, not a standalone plugin.
 * This game patch does not alter flight physics, sensor association, or warhead/fuze models.
 */
'use strict';
const fs=require('node:fs');
const ID='V48_GAME_POST_MISS_BATTERY_ALL4_V1';
const ANCHOR='function updateMissile(m,dt){\n    try{return updateMissileBodyB3(m,dt);}';
const BATTERY_OLD='effectiveRangeKmGameplay:260,maxFlightTimeS:450,';
const BATTERY_NEW='effectiveRangeKmGameplay:260,maxFlightTimeS:480,';
const LIFE_OLD=`    if(m.life > m.maxLife){\n      m._deathReason = 'MAX_LIFE';`;
const LIFE_NEW=`    if(m.guidanceCore==='v1')m._gameBatteryRemainingS=Math.max(0,m.maxLife-m.life);\n    if(m.life > m.maxLife){\n      m._deathReason = m.guidanceCore==='v1' ? 'BATTERY_EXHAUSTED' : 'MAX_LIFE';`;
const TICK_OLD=`      notify(\`⏱ 자폭: \${_mLbl}\${m.id}\${_closeInfo}\`);\n      return;\n    }\n\n    // WIP55: onboard SARH receiver`;
const TICK_NEW=`      notify(m.guidanceCore==='v1'?'⏱ 배터리 소진: '+_mLbl+m.id+_closeInfo:'⏱ 자폭: '+_mLbl+m.id+_closeInfo);\n      return;\n    }\n    if(gameFlightTerminationTickV48(m,dt)) return;\n\n    // WIP55: onboard SARH receiver`;
const MARKER='// GAME-TERM-V48: observation-only terminal expiry controller (no world-truth queries)';
const HELPER=String.raw`// GAME-TERM-V48: observation-only terminal expiry controller (no world-truth queries)
  // The physical-fuze/contact layer remains the only authority to determine hits.
  // Never read killTarget, targetPool, truthObjectForTrackV27, missedTarget,
  // proxMissDistKm or afterClosestTimer from this controller.
  function gameFlightTerminationEvaluateV48(m,ob){
    if(!m || !ob || !ob.profileId || !ob.sensorActive)return null;
    const now=Number(ob.nowS)||0;
    const memo=m._gameFlightTerm||(m._gameFlightTerm={firstActiveS:now,lastGoodS:null,predictedCrossS:null,lastRangeM:null,lastState:'',everTracked:false});
    memo.lastState=String(ob.mode||'OFF');
    const fresh=ob.mode==='TRACK' && ob.trackValid===true &&
      Number.isFinite(ob.hitAgeS) && ob.hitAgeS<=.30 &&
      Number.isFinite(ob.confidence) && ob.confidence>=.13;
    if(fresh && ob.trackPosM && ob.trackVelMps && ob.ownPosM && ob.ownVelMps){
      const dx=ob.trackPosM.x-ob.ownPosM.x,dy=ob.trackPosM.y-ob.ownPosM.y,dz=ob.trackPosM.z-ob.ownPosM.z;
      const rvx=ob.trackVelMps.x-ob.ownVelMps.x,rvy=ob.trackVelMps.y-ob.ownVelMps.y,rvz=ob.trackVelMps.z-ob.ownVelMps.z;
      const rng=Math.hypot(dx,dy,dz);
      const closing=rng>1?-(dx*rvx+dy*rvy+dz*rvz)/rng:0;
      memo.everTracked=true;memo.lastGoodS=now;memo.lastRangeM=rng;
      memo.lastClosingMps=closing;
      // Update predicted crossing time from current *observed local track*, not from Kappa's capped TGO.
      // Only use terminal-range track snapshots as a terminal-expiry clock.
      if(rng<=35000 && closing>120){
        const remaining=Math.min(65,rng/closing);
        memo.predictedCrossS=now+remaining;
        memo.lastTgoS=remaining;
      }
      return null;
    }
    const searching=['SEARCH','COAST','REACQUIRE','LOST'].includes(String(ob.mode||'OFF'));
    const sinceGood=memo.lastGoodS==null?Infinity:(now-memo.lastGoodS);
    const pastCross=memo.predictedCrossS!=null&&now>=memo.predictedCrossS+2.5;
    // A prior fresh terminal track, expired expected crossing, no physical fuze outcome,
    // and a continuous local observation gap together justify a game terminal miss.
    if(memo.everTracked && searching && sinceGood>=2.5 && pastCross && !ob.fuzeDetonated){
      return 'TERMINAL_MISS_POST_CROSS';
    }
    // Search-only missiles must not linger forever after *onboard seeker activation*.
    // This fallback is ARH-only: SARH still has ship-side guidance/illumination paths.
    if(ob.kind==='ARH' && !memo.everTracked && searching && now-memo.firstActiveS>=12 && !ob.fuzeDetonated){
      return 'TERMINAL_SEARCH_NO_ACQUISITION';
    }
    return null;
  }
  function gameFlightTerminationTickV48(m,dt){
    if(window.AEGIS_GAME_TERMINATION_ENABLED===false || m.dead || m.guidanceCore!=='v1' || !m._v1Profile)return false;
    const id=m._v1Profile.id;
    if(!['SM2MR_BLKIIIA_SIM','SM2ER_BLKIV_SIM','SM6_BLKIA_SIM','ESSM_BLK2_SIM'].includes(id))return false;
    const hasArh=id==='SM6_BLKIA_SIM'||id==='ESSM_BLK2_SIM';
    const sensorActive=hasArh?!!m.essmActiveSeeker:(!!m.sarhAlive||!!m._gameFlightTerm?.everTracked);
    if(!sensorActive)return false;
    const s=hasArh?m._arhRfSeeker:m._sarhRfSeeker;
    const aim=hasArh?(s?_arhEkfAim(s):null):(s?_sarhEkfAim(s):null);
    const own=samNavB1OwnState(m);
    const reason=gameFlightTerminationEvaluateV48(m,{
      profileId:id,kind:hasArh?'ARH':'SARH',sensorActive,
      nowS:m.life,mode:s?.mode||'OFF',trackValid:!!s?.trackValid,
      hitAgeS:Number(s?.lastHitAgeS??Infinity),confidence:Number(s?.confidence??0),
      trackPosM:aim?.posM??null,trackVelMps:aim?.velMps??null,
      ownPosM:own?.posM??null,ownVelMps:own?.velMps??null,
      // Read a *fuze outcome*, not truth-side CPA or physics collision state.
      fuzeDetonated:!!m.proxDetonated
    });
    if(!reason)return false;
    m._deathReason=reason;m._gameTermReason=reason;m.dead=true;
    debugLog('GAME_TERM: '+String(m.id)+' '+id+' '+reason+' life='+m.life.toFixed(2));
    return true;
  }
  // Game-only deterministic fixture: this exercises exactly the same evaluator as live missiles.
  function gameFlightTerminationFixturesV48(){
    const p={x:0,y:0,z:0},v={x:1000,y:0,z:0},target={x:8000,y:0,z:0},tv={x:0,y:0,z:0};
    const sample=(nowS,mode,tracked,override={})=>({profileId:'ESSM_BLK2_SIM',kind:'ARH',sensorActive:true,
      nowS,mode,trackValid:tracked,hitAgeS:tracked?.04:10,confidence:tracked?.85:0,
      trackPosM:tracked?target:null,trackVelMps:tracked?tv:null,ownPosM:p,ownVelMps:v,fuzeDetonated:false,...override});
    const cases=[];
    {const m={};gameFlightTerminationEvaluateV48(m,sample(0,'TRACK',true));
      const at8=gameFlightTerminationEvaluateV48(m,sample(8,'SEARCH',false));
      const at12=gameFlightTerminationEvaluateV48(m,sample(12,'SEARCH',false));
      cases.push({name:'track-lost-after-expected-cross',pass:at8===null&&at12==='TERMINAL_MISS_POST_CROSS',at8,at12});}
    {const m={};gameFlightTerminationEvaluateV48(m,sample(0,'TRACK',true));
      const at5=gameFlightTerminationEvaluateV48(m,sample(5,'SEARCH',false));
      const at6=gameFlightTerminationEvaluateV48(m,sample(6,'TRACK',true,{ownPosM:{x:5000,y:0,z:0}}));
      const at13=gameFlightTerminationEvaluateV48(m,sample(13,'TRACK',true,{ownPosM:{x:7000,y:0,z:0}}));
      cases.push({name:'track-reacquired-no-premature-exit',pass:at5===null&&at6===null&&at13===null});}
    {const m={};gameFlightTerminationEvaluateV48(m,sample(0,'SEARCH',false));
      const at11=gameFlightTerminationEvaluateV48(m,sample(11,'SEARCH',false));
      const at12=gameFlightTerminationEvaluateV48(m,sample(12.1,'SEARCH',false));
      cases.push({name:'arh-never-acquires-search-expires',pass:at11===null&&at12==='TERMINAL_SEARCH_NO_ACQUISITION'});}
    {const m={};gameFlightTerminationEvaluateV48(m,sample(0,'TRACK',true));
      const after=gameFlightTerminationEvaluateV48(m,sample(15,'SEARCH',false,{fuzeDetonated:true}));
      cases.push({name:'physical-fuze-outcome-blocks-miss-exit',pass:after===null});}
    {const m={};const at=gameFlightTerminationEvaluateV48(m,sample(20,'SEARCH',false,{kind:'SARH'}));
      cases.push({name:'sarh-not-misclassified-as-arh-search',pass:at===null});}
    {const m={};gameFlightTerminationEvaluateV48(m,sample(0,'TRACK',true));
      const at=gameFlightTerminationEvaluateV48(m,sample(7,'SEARCH',false));
      cases.push({name:'no-early-post-cross-termination',pass:at===null});}
    return {schema:'AEGIS_GAME_TERMINATION_FIXTURES_V48',pass:cases.every(x=>x.pass),cases};
  }
  window.__AEGIS_GAME_TERM_DIAG__=Object.freeze({id:'V48_GAME_POST_MISS_BATTERY_ALL4_V1',fixtures:gameFlightTerminationFixturesV48});
  `;
function count(s,t){return s.split(t).length-1;}
function assertCount(s,t,n){const k=count(s,t);if(k!==n)throw Error('Unsupported source: expected '+n+' occurrence(s) for '+t.slice(0,85)+', found '+k);}
function apply(source){
 if(typeof source!=='string')throw Error('Expected expanded main JS');
 if(source.includes(MARKER)){
   assertCount(source,MARKER,2);assertCount(source,BATTERY_NEW,1);assertCount(source,'if(gameFlightTerminationTickV48(m,dt)) return;',2);
   return {source,status:'already applied'};
 }
 assertCount(source,ANCHOR,2);assertCount(source,LIFE_OLD,2);assertCount(source,TICK_OLD,2);
 assertCount(source,BATTERY_OLD,1);
 let out=source.replace(BATTERY_OLD,BATTERY_NEW)
  .replaceAll(ANCHOR,HELPER+ANCHOR)
  .replaceAll(LIFE_OLD,LIFE_NEW)
  .replaceAll(TICK_OLD,TICK_NEW);
 assertCount(out,MARKER,2);assertCount(out,BATTERY_NEW,1);
 assertCount(out,'if(gameFlightTerminationTickV48(m,dt)) return;',2);
 return {source:out,status:'patched'};
}
module.exports={apply,ID};
if(require.main===module){const [,,input,output]=process.argv;
 if(!input||!output||input===output)throw Error('Usage: node AEGIS_PostMiss_Battery_source_patch.js INPUT_UNPACKED_JS OUTPUT_UNPACKED_JS');
 if(fs.existsSync(output))throw Error('Refusing to overwrite');const r=apply(fs.readFileSync(input,'utf8'));fs.writeFileSync(output,r.source);console.log(r.status);
}
