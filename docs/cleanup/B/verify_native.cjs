const{fs,path,H,R,sha}=require('./cache.cjs'),{sourceFor}=require('../../missile/launch-handoff/A/engine.cjs');
const q=sourceFor(path.join(R,'Aegis_SIM_v48_WIP_CLEAN_B.html')),p=require('../../envelope/D2/provenance.json'),checks={frozenNativeByteExact:q.native===fs.readFileSync(path.join(R,'docs/envelope/D2/native-engine.js'),'utf8')};
for(const[k,v]of Object.entries(p.functionHashes))checks[k]=q.functionHashes[k]===v;
checks.frozenNativeManifestExact=sha(fs.readFileSync(path.join(R,'docs/envelope/D2/native-engine.js')))===p.nativeSha256;
checks.frozenPrivateManifestExact=sha(fs.readFileSync(path.join(R,'docs/envelope/D2/private.js')))===p.privateSha256;
const out={pass:Object.values(checks).every(Boolean),checks,game:q.product,functions:Object.keys(p.functionHashes).length,nativeSha256:sha(q.native)};fs.writeFileSync(path.join(H,'evidence/native-equivalence.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({pass:out.pass,functions:out.functions}));if(!out.pass)process.exitCode=1;
