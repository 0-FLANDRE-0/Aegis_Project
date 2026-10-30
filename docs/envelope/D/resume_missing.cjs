// Recovery only after a stopped process. Completed native cells are read and
// hashed, never fired again. Do not run alongside the original measurement.
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto');
const {Worker}=require('worker_threads'),{cells}=require('./suite.cjs'),{seeds}=require('./engine.cjs');
const H=__dirname,OUT=path.join(H,'results'),all=cells(),queue=[],rows=[];
const provenance=JSON.parse(fs.readFileSync(path.join(H,'PROVENANCE.json')));
for(const [f,sha]of Object.entries(provenance.files))if(crypto.createHash('sha256').update(fs.readFileSync(path.join(H,f))).digest('hex')!==sha)throw Error('MODEL_CHANGED:'+f);
if(fs.existsSync(path.join(OUT,'measurement.json')))throw Error('COMPLETE_SWEEP_ALREADY_EXISTS_DO_NOT_REPEAT');
if(!process.argv.includes('--confirmed-stopped'))throw Error('Confirm original process stopped; use --confirmed-stopped');
for(const cell of all){const file=path.join(OUT,'cells',cell.cellId+'.json.gz');
 if(!fs.existsSync(file)){queue.push(cell);continue;}
 const raw=zlib.gunzipSync(fs.readFileSync(file)),j=JSON.parse(raw);
 if(JSON.stringify(j.cell)!==JSON.stringify(cell)||JSON.stringify(j.seeds)!==JSON.stringify(seeds))throw Error('CELL_INPUT_MISMATCH:'+cell.cellId);
 rows.push({row:j.row,sha256:crypto.createHash('sha256').update(raw).digest('hex')});
}
const prior=fs.existsSync(path.join(OUT,'progress.json'))?JSON.parse(fs.readFileSync(path.join(OUT,'progress.json'))):{elapsedS:0};
const retained=rows.length,started=performance.now();let active=0;
fs.writeFileSync(path.join(OUT,'resume-receipt.json'),JSON.stringify({retainedCompletedCells:retained,missingCells:queue.map(q=>q.cellId),modelHashes:provenance.files,fullSweepRepeated:false},null,2));
(async()=>{await new Promise((resolve,reject)=>{function schedule(){if(!queue.length&&!active){resolve();return;}
 while(active<4&&queue.length){const cell=queue.shift();active++;const w=new Worker(path.join(H,'suite.cjs'),{workerData:{cell}});
  w.on('error',reject);w.on('message',r=>{active--;rows.push(r);fs.writeFileSync(path.join(OUT,'progress.json'),JSON.stringify({done:rows.length,total:all.length,elapsedS:prior.elapsedS+(performance.now()-started)/1000,rows}));console.log(rows.length+'/'+all.length,cell.cellId,r.row.maxRangeKm,r.row.effectiveRangeKm,true);schedule();});}}
 schedule();});
 rows.sort((a,b)=>all.findIndex(c=>c.cellId===a.row.cellId)-all.findIndex(c=>c.cellId===b.row.cellId));
 fs.writeFileSync(path.join(OUT,'measurement.json'),JSON.stringify({schema:'AEGIS_ENV_D_NATIVE_ASM_MEASUREMENT_1',seeds,rows:rows.map(r=>r.row),logicalHashes:rows.map(r=>({cellId:r.row.cellId,sha256:r.sha256})),calls:rows.reduce((s,r)=>s+r.row.calls,0),elapsedS:prior.elapsedS+(performance.now()-started)/1000,resumedMissingOnly:true}));
})().catch(e=>{console.error(e);process.exitCode=1;});
