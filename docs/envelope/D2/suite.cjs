// Offline orchestration only; every shot executes the unmodified native game
// flight/fuze/ASM damage path. No monotonicity assumption is used for max range.
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto');
const {Worker,isMainThread,parentPort,workerData}=require('worker_threads');
const H=__dirname,{create,seeds}=require('./engine.cjs');
const motions=[{motion:'STATIONARY',targetSpeedMps:0},{motion:'INBOUND_250',targetSpeedMps:250},
 {motion:'INBOUND_680',targetSpeedMps:680},{motion:'OUTBOUND_250',targetSpeedMps:-250},
 {motion:'CROSS_250',targetSpeedMps:0,crossSpeedMps:250}];
const weapons=['SM2','SM2ER','SM6','ESSM'],altitudes=[30,1000,5000,10000,15000,20000];
function cells(){const rows=[];for(const weapon of weapons)for(const altM of altitudes)for(const motion of motions)rows.push({weapon,altM,...motion,targetLabel:'Kh-35U'});
 for(const weapon of ['SM2','SM6'])for(const [altM,motion]of [[30,motions[1]],[5000,motions[2]],[15000,motions[0]]])rows.push({weapon,altM,...motion,targetLabel:'Kh-32',auxiliary:true});
 return rows.map(c=>({...c,cellId:[c.targetLabel,c.weapon,c.altM,c.motion].join('_')}));}
function aggregate(shots){const good=shots.filter(s=>s.success),points=good.map(s=>s.interceptPointKm),targetPoints=good.map(s=>s.targetInterceptPointKm);
 const stat=a=>a.length?{meanKm:a.reduce((s,v)=>s+v,0)/a.length,minKm:Math.min(...a),maxKm:Math.max(...a)}:null;
 return {anyEffect:good.length>=1,effective:shots.filter(s=>s.lethal).length>=3,effectCount:good.length,lethalCount:shots.filter(s=>s.lethal).length,
  interceptPoint:stat(points),targetInterceptPoint:stat(targetPoints),closestRangeM:{min:Math.min(...shots.map(s=>s.closestM??Infinity)),max:Math.max(...shots.map(s=>s.closestM??-Infinity))},shots};}
function measure(cell){const e=create(),cache=new Map(),start=performance.now();let calls=0;
 function at(rangeKm){if(cache.has(rangeKm))return cache.get(rangeKm);
  const shots=seeds.map(seed=>{calls++;return e.runCase({...cell,rangeKm,...seed,samples:false});});
  const result={rangeKm,...aggregate(shots)};cache.set(rangeKm,result);return result;}
 const coarse=[5,15,30,60,100,150,200,250,300,350,400,450,500];
 for(const r of coarse)at(r);
 let low=coarse.filter(r=>at(r).anyEffect).at(-1)??0;
 if(low>0&&low<500){let high=coarse.find(r=>r>low&&!at(r).anyEffect)??500;
  while(high-low>1){const mid=Math.floor((low+high)/2);if(at(mid).anyEffect)low=mid;else high=mid;}}
 // A hit beyond a failed bracket must still count. Every farther integer is
 // actually fired; the cap cannot be inferred from a failed binary search.
 for(let r=Math.max(5,low+1);r<=500;r++)if(at(r).anyEffect)low=r;
 let effective=0,breakPoint=null;
 for(let r=5;r<=500;r+=5){const q=at(r);if(!q.effective){breakPoint=q;break;}effective=r;}
 const maxBoundary=low?at(low):null,nextBoundary=low<500?at(Math.max(5,low+1)):null;
 const effectiveBoundary=effective?at(effective):null;
 const row={...cell,maxRangeKm:low,effectiveRangeKm:effective,maxInterceptPoint:maxBoundary?.interceptPoint??null,
  effectiveInterceptPoint:effectiveBoundary?.interceptPoint??null,capReached:low===500,
  maxBoundary,nextBoundary,effectiveBoundary,breakPoint,uniqueDistances:cache.size,calls,elapsedS:(performance.now()-start)/1000};
 const all=[...cache].sort((a,b)=>a[0]-b[0]).map(([,v])=>v),raw=JSON.stringify({cell,seeds,row,distances:all});
 fs.mkdirSync(path.join(H,'results/cells'),{recursive:true});
 fs.writeFileSync(path.join(H,'results/cells',cell.cellId+'.json.gz'),zlib.gzipSync(raw,{level:9,mtime:0}));
 return {row,sha256:crypto.createHash('sha256').update(raw).digest('hex')};
}
if(!isMainThread){try{const result=measure(workerData.cell);parentPort.postMessage(result);}catch(error){throw error;}}
else if(require.main===module){
 const args=process.argv.slice(2),run=args.includes('--execute-full');
 if(!run){console.log(JSON.stringify({cells:cells().length,fullMeasurementStarted:false,instruction:'Read COST_ESTIMATE.json and use --execute-full only within authorized time/scope.'}));}
 else(async()=>{if(!require('./COST_ESTIMATE.json').fullAllowed||!require('./evidence/path.json').pass)throw Error('PREFLIGHT_REQUIRED');
  const all=cells(),rows=[],start=performance.now();let active=0,done=0;
  for(const cell of all){const f=path.join(H,'results/cells',cell.cellId+'.json.gz');if(fs.existsSync(f)){const raw=zlib.gunzipSync(fs.readFileSync(f)),j=JSON.parse(raw);rows.push({row:j.row,sha256:crypto.createHash('sha256').update(raw).digest('hex')});done++;}}
  const queue=all.filter(c=>!rows.some(r=>r.row.cellId===c.cellId));
  fs.mkdirSync(path.join(H,'results'),{recursive:true});
  await new Promise((resolve,reject)=>{function schedule(){while(active<4&&queue.length){const cell=queue.shift();active++;
    const w=new Worker(__filename,{workerData:{cell}});w.on('error',reject);w.on('message',r=>{active--;done++;rows.push(r);
     fs.writeFileSync(path.join(H,'results/progress.json'),JSON.stringify({done,total:all.length,elapsedS:(performance.now()-start)/1000,rows}));
     console.log(JSON.stringify({done,total:all.length,cellId:cell.cellId,max:r.row.maxRangeKm,effective:r.row.effectiveRangeKm,calls:r.row.calls,elapsedS:r.row.elapsedS}),true);
     if(done===all.length)resolve();else schedule();});}}
   if(done===all.length)resolve();else schedule();});
  rows.sort((a,b)=>all.findIndex(c=>c.cellId===a.row.cellId)-all.findIndex(c=>c.cellId===b.row.cellId));
  fs.writeFileSync(path.join(H,'results/measurement.json'),JSON.stringify({schema:'AEGIS_ENV_D_NATIVE_ASM_MEASUREMENT_1',seeds,rows:rows.map(r=>r.row),logicalHashes:rows.map(r=>({cellId:r.row.cellId,sha256:r.sha256})),calls:rows.reduce((s,r)=>s+r.row.calls,0),elapsedS:(performance.now()-start)/1000}));
 })().catch(e=>{console.error(e);process.exitCode=1;});
}
module.exports={cells,aggregate,motions};
