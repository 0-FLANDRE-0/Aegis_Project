// Compare every frozen native flight function to the delivered game, without shots.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const H=__dirname,R=path.resolve(H,'../../..'),{sourceFor}=require('../../missile/launch-handoff/A/engine.cjs');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const q=sourceFor(path.join(R,'Aegis_SIM_v48_WIP_CLEAN_A.html'));
const p=require('../../envelope/D2/provenance.json');
const checks={frozenNativeByteExact:q.native===fs.readFileSync(path.join(R,'docs/envelope/D2/native-engine.js'),'utf8')};
for(const[k,v]of Object.entries(p.functionHashes))checks[k]=q.functionHashes[k]===v;
const out={pass:Object.values(checks).every(Boolean),checks,game:q.product,functions:Object.keys(p.functionHashes).length,nativeSha256:sha(q.native),frozenSha256:p.nativeSha256,scope:'Frozen D2 native flight code and every extracted game function; no private target approximation substituted'};
fs.writeFileSync(path.join(H,'evidence/native-equivalence.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify({pass:out.pass,functions:out.functions}));if(!out.pass)process.exitCode=1;
