// Small pre-measurement cost/seed probe. Not an envelope sweep.
const fs=require('fs'),path=require('path');
const {create,seeds}=require('./engine.cjs'),e=create(),records=[];
let batch=0;
for(const weapon of ['SM2','SM2ER','SM6','ESSM'])for(const [rangeKm,altM,speed,cross] of [[20,30,-250,0],[100,5000,250,0],[300,15000,0,0],[60,5000,0,250]]) {
 const shots=[];
 for(const seed of seeds){const c={weapon,rangeKm,altM,targetSpeedMps:speed,crossSpeedMps:cross,...seed,samples:true};
  const cpu=process.cpuUsage(),t=performance.now(),result=e.runCase(c),used=process.cpuUsage(cpu);
  shots.push({condition:c,cpuS:(used.user+used.system)/1e6,elapsedS:(performance.now()-t)/1000,result});
 }
 records.push({weapon,rangeKm,altM,speed,cross,shots});
 fs.writeFileSync(path.join(__dirname,'evidence/pilot.json'),JSON.stringify({method:'80 native ASM-target flights; no envelope search',seeds,records}));
 console.log(JSON.stringify({batch:++batch,weapon,rangeKm,altM,outcomes:shots.map(s=>s.result.reason),cpa:shots.map(s=>s.result.closestM),meanCpuS:shots.reduce((s,q)=>s+q.cpuS,0)/5}),true);
}
