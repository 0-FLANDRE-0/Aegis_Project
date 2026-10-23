const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {Worker,isMainThread,parentPort,workerData}=require('worker_threads');
const H=__dirname,D=path.join(H,'diagnostic');
if(isMainThread){(async()=>{
 const started=performance.now(),versions=await Promise.all(['CURRENT','PATCHED'].map(version=>new Promise((resolve,reject)=>{
  const w=new Worker(__filename,{workerData:{version}});w.on('error',reject);w.on('message',q=>q.progress?console.log(version,q.progress):resolve(q));
 })));
 const result={schema:'AEGIS_KAPPA_PIP_LOS_14_AB_1',provenance:'GAME_ENGINE_COMPUTED',seed:1831565813,fixedDtS:1/60,uniqueConditions:14,calls:28,fullEnvelopeSweep:false,versions};
 const raw=JSON.stringify(result),out=process.argv[2];if(!out)throw Error('Output required');fs.writeFileSync(out,raw);
 const receipt={sha256:crypto.createHash('sha256').update(raw).digest('hex'),bytes:Buffer.byteLength(raw),calls:28,elapsedMs:performance.now()-started,workers:2};fs.writeFileSync(out+'.receipt.json',JSON.stringify(receipt));console.log('DONE',JSON.stringify(receipt));
})().catch(e=>{console.error(e);process.exitCode=1;});}
else{
 const d=JSON.parse(fs.readFileSync(path.join(H,'inputs.json'))),native=fs.readFileSync(path.join(D,workerData.version==='CURRENT'?'current-native-engine.js':'native-engine.js'),'utf8'),source=native+'\n'+fs.readFileSync(path.join(D,'private.js'),'utf8');
 const factory=new Function('DATA','SETTINGS','PROFILE','PRIVATE_SHIP',source),engine=factory(structuredClone(d.data),structuredClone(d.settings),{},{entityId:'ENV_PRIVATE',navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}}),results=[];
 for(const c of JSON.parse(fs.readFileSync(path.join(H,'cases.json'))).cases){results.push({caseId:c.caseId,group:c.group,result:engine.runCase(c)});parentPort.postMessage({progress:results.length});}
 parentPort.postMessage({version:workerData.version,nativeSourceSha256:crypto.createHash('sha256').update(native).digest('hex'),results});
}
