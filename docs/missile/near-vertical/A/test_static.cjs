const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {unpack,mainScope}=require('../../fuze-zem/A/source.cjs');
const {patchKappaPipState}=require('./patch.cjs');
const H=__dirname,R=path.resolve(H,'../../../..'),build=JSON.parse(fs.readFileSync(path.join(H,'build.json'))),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const base=fs.readFileSync(path.join(R,'Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html')),final=fs.readFileSync(path.join(R,'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html'));
const bs=unpack(base),fsrc=unpack(final),bm=mainScope(bs).symbols,fm=mainScope(fsrc).symbols,target='_wip79KappaPipState',changed=[];
if([...bm.keys()].join('\n')!==[...fm.keys()].join('\n'))throw Error('SYMBOL_SET_CHANGED');
for(const[n,b]of bm){const f=fm.get(n);if(b.code!==f.code)changed.push(n);}
if(JSON.stringify(changed)!==JSON.stringify([target]))throw Error('UNEXPECTED_CHANGED_SYMBOLS '+changed);
if(patchKappaPipState(bm.get(target).code,{stability:true})!==fm.get(target).code)throw Error('FINAL_NOT_DECLARED_PATCH');
const shell=x=>x.toString().replace(/data-c55-index="13">[^<]+<\/script>/,'data-c55-index="13">PAYLOAD</script>').replace(/const records=(\[.*?\]);/s,'const records=RECORDS;');
if(shell(base)!==shell(final))throw Error('OUTER_SHELL_CHANGED');
const preserved=['_arhV2MonopulseMeasurement','getSamArhProfile','computeTruePN3D','computeAPNCorrectionV1','computeZEMCorrectionV1','computeKappaMidcourseAccelV2','updateMissileBodyB3','updateSamSixDofLiteDynamics','gameFlightTerminationEvaluateV48','samFuzeSignalSweepA','loftB4ShapeWaypoint'];
const hashes=Object.fromEntries(preserved.map(n=>[n,{base:sha(bm.get(n).code),final:sha(fm.get(n).code),same:bm.get(n).code===fm.get(n).code}]));
if(Object.values(hashes).some(x=>!x.same))throw Error('PRESERVED_FUNCTION_CHANGED');
const out={schema:'AEGIS_NEAR_VERTICAL_PATH_FIX_A_STATIC_1',pass:true,baseHtmlSha256:sha(base),finalHtmlSha256:sha(final),finalHtmlBytes:final.length,expectedFinal:build.finalHtmlSha256===sha(final)&&build.finalHtmlBytes===final.length,changedSymbols:changed,allOtherMainSymbolsByteExact:true,outerShellByteExactAfterPayloadManifestNormalization:true,preservedFunctionHashes:hashes};
if(!out.expectedFinal)throw Error('BUILD_MISMATCH');fs.writeFileSync(path.join(H,'static.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));
