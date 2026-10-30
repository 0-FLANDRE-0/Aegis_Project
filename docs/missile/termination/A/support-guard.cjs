// Whole-game regression correction to the supplied termination adapter ONLY.
// The dual-mode native guidance can still intercept on SARH or a valid delivered
// DL observation when ARH has no echo. Do not terminate while that support exists.
// No target coordinate from DL/truth is read here; only existing validity/source.
exports.apply=function(source){
 if(source.includes('// GAME-TERM-SUPPORT-GUARD-V2')){
  if(source.split('// GAME-TERM-SUPPORT-GUARD-V2').length-1!==2||source.split('const remaining=rng/closing; // SIM_TUNED policy').length-1!==2)throw Error('Incomplete support/uncapped-clock correction; refusing a partial transplant');
  return source;
 }
 function twice(a,b){const n=source.split(a).length-1;if(n!==2)throw Error('Guard anchor count '+n+': '+a.slice(0,90));source=source.split(a).join(b);}
 twice("    memo.lastState=String(ob.mode||'OFF');",`    // GAME-TERM-SUPPORT-GUARD-V2: preserve native SARH/DL fallback authority.
    memo.lastState=String(ob.mode||'OFF');
    if(ob.alternateGuidance===true)memo.lastSupportS=now;`);
 twice("    const searching=['SEARCH','COAST','REACQUIRE','LOST'].includes(String(ob.mode||'OFF'));",`    if(ob.alternateGuidance===true)return null;
    const supportGapS=memo.lastSupportS==null?Infinity:now-memo.lastSupportS;
    const searching=['SEARCH','COAST','REACQUIRE','LOST'].includes(String(ob.mode||'OFF'));`);
 twice("searching && sinceGood>=2.5 && pastCross", "searching && sinceGood>=2.5 && supportGapS>=2.5 && pastCross");
 twice("now-memo.firstActiveS>=12", "now-Math.max(memo.firstActiveS,memo.lastSupportS??memo.firstActiveS)>=12");
 // A termination clock is not the guidance TGO. Clipping 175s to 65s could
 // expire a still-approaching missile 110s before its observed crossing.
 twice("const remaining=Math.min(65,rng/closing);", "const remaining=rng/closing; // SIM_TUNED policy: no guidance-style TGO cap in the expiry clock");
 twice("    const s=hasArh?m._arhRfSeeker:m._sarhRfSeeker;",`    const primary=hasArh?m._arhRfSeeker:m._sarhRfSeeker;
    const secondary=hasArh?m._sarhRfSeeker:null;
    const fresh=s=>s?.mode==='TRACK'&&s.trackValid===true&&Number.isFinite(s.lastHitAgeS)&&s.lastHitAgeS<=.30&&Number.isFinite(s.confidence)&&s.confidence>=.13;
    const useSarh=hasArh&&!fresh(primary)&&m.sarhAlive===true&&fresh(secondary);
    const s=useSarh?secondary:primary;
    const alternateGuidance=m.dlAlive===true&&m._v1TargetState?.isValid===true&&m._v1TargetState.source==='DL_TRACK';`);
 twice("profileId:id,kind:hasArh?'ARH':'SARH',sensorActive,", "profileId:id,kind:hasArh?'ARH':'SARH',sensorActive,alternateGuidance,\n      observationKind:useSarh?'SARH':(hasArh?'ARH':'SARH'),");
 twice("      memo.everTracked=true;memo.lastGoodS=now;memo.lastRangeM=rng;", "      memo.everTracked=true;memo.lastGoodS=now;memo.lastRangeM=rng;memo.lastTrackKind=ob.observationKind??ob.kind;");
 return source;
};
