// Original third regression: ideal-observation native Kh-35U, 100m/20km seed1.
const fs=require('fs'),path=require('path'),zlib=require('zlib'),H=__dirname,R=path.resolve(H,'../../..');
const {create,seeds,sourceFor}=require('../../missile/launch-handoff/A/engine.cjs'),versions=require('./builds.json').versions,rows=[];
for(const v of ['KAPPA','DZT','HANDOFF','ARH','VERTICAL','LATEST']){
 const file=path.resolve(R,versions[v].file),condition={weapon:'SM6',rangeKm:.1,altM:20000,targetSpeedMps:0,...seeds[0],samples:true,trace:false},e=create(file),result=e.runCase(condition);
 rows.push({variant:v,condition,result,product:sourceFor(file).product});console.log(JSON.stringify({variant:v,success:result.success,outcome:result.outcome,reason:result.reason,closestM:result.closestM}));
}
fs.writeFileSync(path.join(H,'results/part2-near.json.gz'),zlib.gzipSync(JSON.stringify({rows}),{level:9,mtime:0}));
