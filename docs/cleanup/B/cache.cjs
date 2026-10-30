// Offline data provenance. No game-world or RNG state is read or changed.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),zlib=require('zlib');
const H=__dirname,R=path.resolve(H,'../../..'),A=path.join(R,'docs/cleanup/A'),D=path.join(R,'docs/envelope/D2');
const baseCommit='60a83ccfbde89ec26d927b2993f0a4a9585c98af';
const old=require(path.join(A,'ENVELOPE_TABLE_D.json')),d2=require(path.join(D,'results/measurement.json'));
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const blobReceipt=require('./evidence/base-cache-blobs.json');if(blobReceipt.commit!==baseCommit)throw Error('BASE_COMMIT_MISMATCH');const blobs=new Map(Object.entries(blobReceipt.blobs));
function grid(max){const a=[];for(let r=1;r<=Math.min(30,Math.floor(max));r++)a.push(r);for(let r=35;r<=max;r+=5)a.push(r);return a;}
function readCache(row){
 const f=path.join(D,'results/cells',row.cellId+'.json.gz'),raw=zlib.gunzipSync(fs.readFileSync(f));
 if(sha(raw)!==d2.logicalHashes.find(x=>x.cellId===row.cellId).sha256)throw Error('D2_LOGICAL_HASH_MISMATCH:'+row.cellId);
 const legacy=JSON.parse(raw),name='docs/cleanup/A/results/interval-cells/'+row.cellId+'.json.gz',buf=fs.readFileSync(path.join(R,name));
 if(crypto.createHash('sha1').update(Buffer.from('blob '+buf.length+'\0')).update(buf).digest('hex')!==blobs.get(name))throw Error('CLEAN_A_GIT_BLOB_MISMATCH:'+row.cellId);
 const prior=JSON.parse(zlib.gunzipSync(buf)),points=new Map();
 function add(q,origin){if(q.shots.length!==5)throw Error('SEED_COUNT');for(let i=0;i<5;i++){const s=q.shots[i],seed=d2.seeds[i];if(s.rngSeed!==seed.rngSeed||s.navigationSeed!==seed.navigationSeed||s.weapon!==row.weapon||s.altM!==row.altM||s.targetLabel!==row.targetLabel||s.rangeKm!==q.rangeKm||s.targetSpeedMps!==row.targetSpeedMps||(s.crossSpeedMps??0)!==(row.crossSpeedMps??0))throw Error('CACHE_CONDITION_MISMATCH');}
  const hash=sha(JSON.stringify(q.shots));if(points.has(q.rangeKm)&&points.get(q.rangeKm).shotsSha256!==hash)throw Error('CACHE_DUPLICATE_MISMATCH');points.set(q.rangeKm,{rangeKm:q.rangeKm,shots:q.shots,origin,shotsSha256:hash});}
 for(const q of legacy.distances)add(q,'ENV_D_REMEASURE_A');for(const q of prior.newDistances)add(q,'CLEAN_A');
 return{points,cell:legacy.cell,costPerTick:legacy.row.elapsedS/legacy.distances.reduce((s,q)=>s+q.shots.reduce((a,b)=>a+b.ticks,0),0),sourceHashes:{d2Logical:sha(raw),cleanAGzip:sha(buf)}};
}
function aggregate(q){const lethal=q.shots.filter(s=>s.lethal),effect=q.shots.filter(s=>s.success),stats=a=>a.length?{meanKm:a.reduce((s,x)=>s+x.interceptPointKm,0)/a.length,minKm:Math.min(...a.map(x=>x.interceptPointKm)),maxKm:Math.max(...a.map(x=>x.interceptPointKm)),shotCount:a.length}:null;return{...q,lethalCount:lethal.length,effectCount:effect.length,pass:lethal.length>=3,lethalInterceptPoint:stats(lethal),effectInterceptPoint:stats(effect)};}
module.exports={fs,path,zlib,H,R,A,D,baseCommit,old,d2,sha,grid,readCache,aggregate};
