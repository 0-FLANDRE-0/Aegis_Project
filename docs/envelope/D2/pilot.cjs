const fs=require('fs'),path=require('path'),{create,seeds}=require('./engine.cjs'),H=__dirname,e=create(),records=[];
for(const weapon of ['SM2','SM2ER','SM6','ESSM'])for(const [rangeKm,altM,targetSpeedMps,crossSpeedMps]of [[20,30,-250,0],[100,5000,250,0],[300,15000,0,0],[60,5000,0,250]]){
 const shots=[];for(const seed of seeds){const condition={weapon,rangeKm,altM,targetSpeedMps,crossSpeedMps,...seed,samples:false},a=performance.now(),cpu=process.cpuUsage(),result=e.runCase(condition),used=process.cpuUsage(cpu);shots.push({condition,cpuS:(used.user+used.system)/1e6,elapsedS:(performance.now()-a)/1000,result});}
 records.push({weapon,rangeKm,altM,targetSpeedMps,crossSpeedMps,shots});fs.writeFileSync(path.join(H,'evidence/pilot.json'),JSON.stringify({records,seeds}));console.log(JSON.stringify({weapon,rangeKm,altM,reasons:shots.map(x=>x.result.reason),meanCpuS:shots.reduce((s,x)=>s+x.cpuS,0)/5}));
}
const old=require('../D/ENVELOPE_TABLE_D.json'),costs=Object.fromEntries(['SM2','SM2ER','SM6','ESSM'].map(w=>[w,records.filter(r=>r.weapon===w).flatMap(r=>r.shots).reduce((s,x)=>s+x.cpuS,0)/20]));
// Reuse only historical search *sizes* as cost planning, not historical flights.
const jobs=old.rows.map(r=>({weapon:r.weapon,shots:Math.min(496,500-r.maxRangeKm+25+Math.floor(r.maxRangeKm/5))*5}));
const main=jobs.reduce((s,x)=>s+x.shots,0),aux=Math.round(main*.05),repeat=126*20+186,mean=Object.values(costs).reduce((a,b)=>a+b)/4;
const seconds=jobs.reduce((s,x)=>s+x.shots*costs[x.weapon],0)+(aux+repeat)*mean,fullHours=seconds/4/3600*1.25;
const cost={schema:'AEGIS_ENV_D_REMEASURE_A_COST_1',pilotShots:80,cpuSecondsPerShot:costs,expectedShots:main+aux+repeat,expectedHours:fullHours,reducedExpectedHours:fullHours*2/3*.5,workers:4,reserveFactor:1.25,planningSource:'HISTORICAL ENV_D search sizes only',fullAllowed:fullHours<=6,flightReuseAcrossSeeds:false};fs.writeFileSync(path.join(H,'COST_ESTIMATE.json'),JSON.stringify(cost,null,2)+'\n');console.log(JSON.stringify(cost,null,2));
