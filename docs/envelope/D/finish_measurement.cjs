// Only boundaries and thirty selected trajectories are repeated; four workers.
// Every flight uses the same frozen native capsule. No second envelope sweep.
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto');
const {Worker}=require('worker_threads'),{seeds}=require('./engine.cjs');
const H=__dirname,E=path.join(H,'evidence'),OUT=path.join(H,'results');
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
const m=JSON.parse(fs.readFileSync(path.join(OUT,'measurement.json')));
const checks={},boundaries=[],trajectories=[],historical=[],start=performance.now();let calls=0;
async function parallel(conditions){
 if(!conditions.length)return[];calls+=conditions.length;
 const groups=Array.from({length:Math.min(4,conditions.length)},()=>[]);
 conditions.forEach((condition,index)=>groups[index%groups.length].push({index,condition}));
 const source="const {parentPort,workerData}=require('worker_threads');const {create}=require(workerData.engine);const e=create();parentPort.postMessage(workerData.jobs.map(q=>({index:q.index,result:e.runCase(q.condition)})));";
 const parts=await Promise.all(groups.map(jobs=>new Promise((resolve,reject)=>{
  const w=new Worker(source,{eval:true,workerData:{engine:path.join(H,'engine.cjs'),jobs}});
  w.on('error',reject);w.on('message',result=>{resolve(result);w.terminate();});
 })));
 return parts.flat().sort((a,b)=>a.index-b.index).map(q=>q.result);
}
(async()=>{
 const boundaryConditions=[];
 for(const row of m.rows){const seen=new Set();for(const key of ['maxBoundary','nextBoundary','effectiveBoundary','breakPoint']){
  const b=row[key];if(!b||seen.has(b.rangeKm))continue;seen.add(b.rangeKm);
  const condition={weapon:row.weapon,altM:row.altM,targetSpeedMps:row.targetSpeedMps,crossSpeedMps:row.crossSpeedMps??0,targetLabel:row.targetLabel,rangeKm:b.rangeKm,samples:false};
  const offset=boundaryConditions.length;boundaryConditions.push(...seeds.map(s=>({...condition,...s})));
  boundaries.push({cellId:row.cellId,boundary:key,condition,expectedHashes:b.shots.map(hash),offset});
 }}
 const repeated=await parallel(boundaryConditions);
 for(const b of boundaries){b.shots=repeated.slice(b.offset,b.offset+5);b.actualHashes=b.shots.map(hash);b.same=b.actualHashes.map((s,i)=>s===b.expectedHashes[i]);checks[b.cellId+'.'+b.boundary]=b.same.every(Boolean);delete b.offset;}
 console.log('BOUNDARIES',boundaries.length,'distances',boundaryConditions.length,'shots',Object.values(checks).every(Boolean),true);
 function schedule(c){const envelope=m.rows.find(r=>!r.auxiliary&&r.weapon===c.weapon&&r.altM===c.altM&&r.targetSpeedMps===c.targetSpeedMps&&(r.crossSpeedMps??0)===(c.crossSpeedMps??0));
  const condition={...c,targetLabel:'Kh-35U',...seeds[0],samples:true};
  const id=[c.weapon,c.altM,c.targetSpeedMps,c.crossSpeedMps??0,c.rangeKm].join('_');
  return{id,condition,status:c.rangeKm>envelope.maxRangeKm?'UNREACHABLE_BY_MEASURED_OUTER_RANGE':'EXECUTED',maxRangeKm:envelope.maxRangeKm,result:null};
 }
 for(const weapon of ['SM2','SM2ER','SM6','ESSM'])for(const altM of [30,5000,15000])for(const targetSpeedMps of [0,250])for(const rangeKm of [30,60,100,150,200])trajectories.push(schedule({weapon,altM,targetSpeedMps,rangeKm}));
 for(const weapon of ['SM2','SM2ER','SM6','ESSM'])for(const altM of [30,5000,15000])for(const rangeKm of [30,60,100])trajectories.push(schedule({weapon,altM,targetSpeedMps:0,crossSpeedMps:250,rangeKm}));
 const active=trajectories.filter(t=>t.status==='EXECUTED'),flights=await parallel(active.map(t=>t.condition));active.forEach((t,i)=>t.result=flights[i]);
 console.log('TRAJECTORIES',active.length,'executed /',trajectories.length,'slots',true);
 const selectionSeed=0xD30A2026;let state=selectionSeed;
 function random(){state^=state<<13;state^=state>>>17;state^=state<<5;return(state>>>0)/4294967296;}
 const order=active.map(t=>t.id);for(let i=order.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[order[i],order[j]]=[order[j],order[i]];}
 const selectedIds=order.slice(0,30),selected=selectedIds.map(id=>trajectories.find(t=>t.id===id)),repeat=await parallel(selected.map(t=>t.condition));
 const replays=selected.map((t,i)=>{const actual=repeat[i],same=hash(actual)===hash(t.result);checks['trajectory.'+t.id]=same;return{id:t.id,expectedHash:hash(t.result),actualHash:hash(actual),same,result:actual};});
 const old=JSON.parse(fs.readFileSync(path.join(H,'../C/ENVELOPE_TABLE_C.json'))).rows,historicalConditions=[];
 for(const row of old){const condition={weapon:row.weapon,altM:row.altM,targetSpeedMps:row.targetSpeedMps,targetLabel:'Kh-35U',...seeds[0],samples:false},offset=historicalConditions.length;
  const ranges=[row.maxRangeKm,...(row.maxRangeKm<500?[row.maxRangeKm+1]:[])].filter(r=>r>=5);historicalConditions.push(...ranges.map(rangeKm=>({...condition,rangeKm})));
  historical.push({weapon:row.weapon,altM:row.altM,targetSpeedMps:row.targetSpeedMps,historicalMaxRangeKm:row.maxRangeKm,historicalTarget:'AIR_POINT',historicalGuidance:'PRE_KAPPA_PIP_LOS',currentTarget:'Kh-35U_ASM',currentGuidance:'KAPPA_PIP_LOS_A',ranges,offset});
 }
 const historicalFlights=await parallel(historicalConditions);for(const h of historical){h.firstSeedProbes=h.ranges.map((rangeKm,i)=>({rangeKm,result:historicalFlights[h.offset+i]}));delete h.offset;delete h.ranges;}
 checks['thirtyTrajectoryReplays']=replays.length===30;
 const raw={schema:'AEGIS_ENV_D_BOUNDARY_AND_TRAJECTORY_REPEAT_1',checks,pass:Object.values(checks).every(Boolean),selectionSeed,selectedIds,seeds,boundaries,trajectories,replays,historical,calls,elapsedS:(performance.now()-start)/1000,workers:4};
 fs.writeFileSync(path.join(OUT,'followup.json.gz'),zlib.gzipSync(JSON.stringify(raw),{level:9,mtime:0}));
 fs.writeFileSync(path.join(E,'determinism.json'),JSON.stringify({pass:raw.pass,checks,selectionSeed,selectedIds,boundaryDistances:boundaries.length,boundaryShots:boundaries.length*5,trajectorySlots:trajectories.length,executedTrajectories:active.length,trajectoryReplays:replays.length,calls,elapsedS:raw.elapsedS,workers:4},null,2));
 console.log(JSON.stringify({pass:raw.pass,calls,elapsedS:raw.elapsedS,trajectorySlots:trajectories.length}));if(!raw.pass)process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1;});
