// GAME_ENGINE_COMPUTED. Runs only by an explicit diagnostic call/offline runner.
async function envSuiteA(create,{onProgress=()=>{},onlyWeapon=null}={}){
 const profiles=create().profiles(),weapons=profiles.map(p=>({profileId:p.id,name:p.name,weapon:p.id.startsWith('ESSM')?'ESSM':p.id.startsWith('SM6')?'SM6':p.id.startsWith('SM2ER')?'SM2ER':'SM2'}));
 const table=[],trajectories=[],cache=new Map(),model=create();let calls=0;
 function shot(c){const k=JSON.stringify(c);if(!cache.has(k)){const q=model.runCase({...c,samples:false});cache.set(k,q);calls++;}return cache.get(k);}
 for(const p of weapons.filter(p=>!onlyWeapon||p.weapon===onlyWeapon)){
  for(const altM of [30,1000,5000,10000,15000,20000])for(const targetSpeedMps of [0,250,680,-250]){
   const base={weapon:p.weapon,altM,targetSpeedMps};let lo=0,hi=300;
   // First locate a successful bracket; close-in launch dead zones are not assumed successful.
   const probes=[1,5,15,30,60,100,150,200,250,300].map(rangeKm=>({rangeKm,result:shot({...base,rangeKm})}));
   const successes=probes.filter(q=>q.result.success);
   let last=null,first=null;
   if(successes.length){lo=successes.at(-1).rangeKm;hi=probes.find(q=>q.rangeKm>lo&&!q.result.success)?.rangeKm??300;
    while(hi-lo>1){const mid=Math.floor((lo+hi)/2),q=shot({...base,rangeKm:mid});if(q.success)lo=mid;else hi=mid;}
    last=shot({...base,rangeKm:lo});if(lo<300)first=shot({...base,rangeKm:hi});
   }else {
    // Binary search has no valid bracket if all coarse probes miss. Verify the
    // integer grid instead of reporting an unproven zero.
    for(let r=300;r>=1;r--){const q=shot({...base,rangeKm:r});if(q.success){lo=r;last=q;first=r<300?shot({...base,rangeKm:r+1}):null;break;}}
    if(!last)first=probes[0].result;
   }
   // Native loft/terminal logic can have disconnected success intervals.
   // Verify every larger integer range, descending from the game cap. The
   // first success is therefore the global grid maximum, not a monotonic guess.
   let upperAuditCases=0;
   for(let r=300;r>lo;r--){const q=shot({...base,rangeKm:r});upperAuditCases++;if(q.success){lo=r;last=q;hi=r+1;first=r<300?shot({...base,rangeKm:r+1}):null;break;}}
   const seen=probes.map(q=>({rangeKm:q.rangeKm,success:q.result.success,reason:q.result.reason}));
   const row={...p,altM,targetSpeedMps,maxRangeKm:last?lo:0,upperCapReached:lo===300&&last?.success===true,resolutionKm:1,lastSuccess:last?{rangeKm:lo,result:last}:null,firstFailure:first?{rangeKm:last?(successes.length?hi:lo+1):first.rangeKm,result:first}:null,coarseProbes:seen,searchPolicy:'COARSE_BRACKET_THEN_INTEGER_BISECTION_PLUS_EXHAUSTIVE_UPPER_GRID',upperAuditCases,nonMonotonicCoarse:seen.some((q,i)=>!q.success&&seen.slice(i+1).some(z=>z.success)&&seen.slice(0,i).some(z=>z.success))};table.push(row);onProgress({part:'ENVELOPE',completed:table.length,total:96,weapon:p.weapon});
  }
  for(const altM of [30,5000,15000])for(const targetSpeedMps of [0,250])for(const rangeKm of [30,60,100,150,200]){
   const envelope=table.find(q=>q.weapon===p.weapon&&q.altM===altM&&q.targetSpeedMps===targetSpeedMps),q=model.runCase({weapon:p.weapon,altM,targetSpeedMps,rangeKm});calls++;
   trajectories.push({...q,beyondComputedEnvelope:rangeKm>envelope.maxRangeKm,label:rangeKm>envelope.maxRangeKm?'도달 불가':q.success?'요격 성공':'실패'});
  }
 }
 return {schema:'AEGIS_ENVELOPE_B_1',provenance:'GAME_ENGINE_COMPUTED',policy:'GAME_MODEL_ONLY_NO_REAL_WEAPON_PERFORMANCE_CLAIM',targetKind:'NATIVE_AIRCRAFT_POINT_TARGET',dtS:1/60,idealSupport:true,rangeCapKm:300,resolutionKm:1,seed:1831565813,table,trajectories,calls};
}
