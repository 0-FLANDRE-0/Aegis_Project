// MAP_E: transient own-ship command state; never serialized. Native SK AUTO
// resets its doctrine object, so legacy commands/load infer FULL automatically.
let ownEcmJamContextE=null;
function ownEcmLevelE(){return !softKillAutoDoctrine?'OFF':ownEcmJamContextE?.owner===ACTIVE_SHIP_RUNTIME&&ownEcmJamContextE.doctrine===softKillDoctrineState?'JAM':'FULL';}
function ownEcmCommandE(level){
 if(!['OFF','JAM','FULL'].includes(level))return {ok:false,reason:'ECM_LEVEL'};
 const on=level!=='OFF',q=electronicCommandF(ACTIVE_SHIP_RUNTIME.entityId,{auto:on,noiseRequested:on,deceptionRequested:on,autoAim:true});
 if(q.ok)ownEcmJamContextE=level==='JAM'?{owner:ACTIVE_SHIP_RUNTIME,doctrine:softKillDoctrineState}:null;return q;
}
