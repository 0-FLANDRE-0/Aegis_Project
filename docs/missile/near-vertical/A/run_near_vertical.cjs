const fs=require('fs'),path=require('path'),zlib=require('zlib');
const H=__dirname,R=path.resolve(H,'../../../..'),{create,seeds,sourceFor}=require('../../launch-handoff/A/engine.cjs');
const build=JSON.parse(fs.readFileSync(path.join(H,'build.json'))),rows=[],start=performance.now();
function pathSeries(r){
  const out=[];
  for(const tick of r.telemetry?.ticks??[]){
    const q=tick.pre??tick.post,cmd=q?.chain?.autopilot?.command,pos=q?.positionM;
    if(!cmd||!pos||!Number.isFinite(cmd.gammaFDeg)||!cmd.pip)continue;
    const dx=cmd.pip.x-pos.x,dy=cmd.pip.y-pos.y,dz=cmd.pip.z-pos.z;
    out.push({lifeS:q.lifeS,owner:q.owner,guidance:q.guidance,source:q.source,policy:cmd.policy,preShapePipLosGammaDeg:Math.atan2(dz,Math.hypot(dx,dy))*180/Math.PI,usedGammaDeg:cmd.gammaFDeg,waypointB4:!!cmd.waypointB4,vFinal:cmd.vFinal,requestedG:q.rawDemandG,limitedG:q.limitedCommandG,actualG:q.actualNormalG,deliveredG:q.deliveredG,actuatorSaturated:q.actuatorSaturated,positionM:pos,pip:cmd.pip});
  }
  return out;
}
function concise(r){const p=pathSeries(r);return{success:r.success,lethal:r.lethal,outcome:r.outcome,reason:r.reason,closestM:r.closestM,fuzeMissM:r.fuzeMissM,fragmentArrivalMissM:r.fragmentArrivalMissM,flightTimeS:r.flightTimeS,handoffAtS:r.telemetry?.handoff?.timeS??null,firstTerminal:r.terminal?.timeS??null,pathSamples:p.length,firstPath:p[0]??null,lastPath:p.at(-1)??null,maxAbsPreShapeGammaDeg:p.reduce((v,x)=>Math.max(v,Math.abs(x.preShapePipLosGammaDeg)),0),maxAbsUsedGammaDeg:p.reduce((v,x)=>Math.max(v,Math.abs(x.usedGammaDeg)),0),maxRequestedG:p.reduce((v,x)=>Math.max(v,Math.abs(x.requestedG??0)),0),maxLimitedG:p.reduce((v,x)=>Math.max(v,Math.abs(x.limitedG??0)),0),maxActualG:p.reduce((v,x)=>Math.max(v,Math.abs(x.actualG??0)),0),saturatedSamples:p.filter(x=>x.actuatorSaturated).length};}
for(const variant of ['BASE','MIN','FINAL']){
  const file=build.variants[variant].file,e=create(file);
  for(let i=0;i<5;i++){
    const condition={weapon:'SM6',targetLabel:'Kh-35U',rangeKm:.1,altM:20000,targetSpeedMps:0,crossSpeedMps:0,...seeds[i],samples:true,trace:true};
    const result=e.runCase(condition);rows.push({variant,seedIndex:i+1,condition,result,summary:concise(result)});
    console.log(variant,i+1,result.reason,result.closestM,result.telemetry?.handoff?.timeS,rows.at(-1).summary.maxAbsUsedGammaDeg);
  }
}
const repeatEngine=create(build.variants.FINAL.file),repeatCondition={weapon:'SM6',targetLabel:'Kh-35U',rangeKm:.1,altM:20000,targetSpeedMps:0,crossSpeedMps:0,...seeds[0],samples:true,trace:true},repeat=repeatEngine.runCase(repeatCondition),first=rows.find(x=>x.variant==='FINAL'&&x.seedIndex===1).result;
const comparison=[];
for(let i=1;i<=5;i++){
  const base=rows.find(x=>x.variant==='BASE'&&x.seedIndex===i),minimum=rows.find(x=>x.variant==='MIN'&&x.seedIndex===i),final=rows.find(x=>x.variant==='FINAL'&&x.seedIndex===i);
  comparison.push({seedIndex:i,rngSeed:base.condition.rngSeed,navigationSeed:base.condition.navigationSeed,base:base.summary,minimum:minimum.summary,final:final.summary,minimumAndFinalFullResultExact:JSON.stringify(minimum.result)===JSON.stringify(final.result)});
}
const summary={schema:'AEGIS_NEAR_VERTICAL_PATH_FIX_A_FIXTURE_1',products:Object.fromEntries(['BASE','MIN','FINAL'].map(v=>[v,sourceFor(build.variants[v].file).product])),condition:{weapon:'SM6',targetLabel:'Kh-35U',rangeKm:.1,altM:20000,targetSpeedMps:0,crossSpeedMps:0},comparison,checks:{baseFailureReproduced:comparison.every(x=>!x.base.success&&x.base.reason==='TERMINAL_MISS_TRACKED_DIVERGENCE'),minimumFiveKills:comparison.every(x=>x.minimum.success&&x.minimum.lethal),finalFiveKills:comparison.every(x=>x.final.success&&x.final.lethal),handoffUnchanged:comparison.every(x=>x.base.handoffAtS===x.minimum.handoffAtS&&x.minimum.handoffAtS===x.final.handoffAtS),minimumAndFinalExact:comparison.every(x=>x.minimumAndFinalFullResultExact),finalDeterministic:JSON.stringify(first)===JSON.stringify(repeat)},elapsedS:(performance.now()-start)/1000,scope:'Controlled ASM/RF diagnostic capsule using live functions from each selected HTML; not natural-RF full-world results.'};
summary.pass=Object.values(summary.checks).every(Boolean);
fs.writeFileSync(path.join(H,'near-vertical-results.json.gz'),zlib.gzipSync(JSON.stringify({summary,rows,repeat}),{level:9,mtime:0}));
fs.writeFileSync(path.join(H,'near-vertical-summary.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify({pass:summary.pass,checks:summary.checks,elapsedS:summary.elapsedS},null,2));if(!summary.pass)process.exitCode=1;
