// Offline only: freeze the selected product's real functions for ENV_D replay.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const H=__dirname,R=path.resolve(H,'../../..'),{sourceFor}=require('../../missile/launch-handoff/A/engine.cjs');
const file=path.join(R,'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html'),q=sourceFor(file);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const privateSource=fs.readFileSync(path.join(R,'docs/envelope/D/diagnostic/private.js'),'utf8').replace('q._kfX.set([s.posM.x,s.posM.y,s.posM.z,s.velMps.x,s.velMps.y,s.velMps.z]);','q._kfP=new Float64Array(36);q._kfX.set([s.posM.x,s.posM.y,s.posM.z,s.velMps.x,s.velMps.y,s.velMps.z]);');
fs.mkdirSync(path.join(H,'evidence'),{recursive:true});fs.mkdirSync(path.join(H,'results'),{recursive:true});
fs.writeFileSync(path.join(H,'native-engine.js'),q.native);fs.writeFileSync(path.join(H,'private.js'),privateSource);
const dataKeys=Object.keys(q.input.data),settingsKeys=Object.keys(q.input.settings);
const helper='window.__ENV_D2_INPUT__={data:{'+dataKeys.join(',')+'},settings:Object.fromEntries('+JSON.stringify(settingsKeys)+'.map(k=>[k,window[k]]))};';
fs.writeFileSync(path.join(H,'capture-helper.js'),helper);
fs.writeFileSync(path.join(H,'provenance.json'),JSON.stringify({schema:'AEGIS_ENV_D_REMEASURE_A_PROVENANCE_1',baseCommit:'38a4f97527b48027fa64f0673cea14a9c83c116d',product:q.product,functionHashes:q.functionHashes,keptBoundaries:q.keptBoundaries,nativeSha256:sha(q.native),privateSha256:sha(privateSource),diagnosticOnly:true},null,2)+'\n');
console.log(JSON.stringify({product:q.product,functions:Object.keys(q.functionHashes).length,dataValues:dataKeys.length}));
