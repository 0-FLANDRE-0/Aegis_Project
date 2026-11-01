const fs=require('fs'),path=require('path'),crypto=require('crypto'),vm=require('vm');
const {load}=require('../phase1a/compact_source.cjs');
const P=__dirname,R=path.resolve(P,'../../../..'),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const a=load('/tmp/aegis-gun-b2/b2b-baseline.html'),b=load(path.join(R,'Aegis_SIM_v48_WIP_GUN_B2.html'));
const allowedExisting=new Set(['GUN_B1_SPEC','GUN_B2_SPEC','gunB2FragmentationPk','gunB1FragmentationPk','GUN_B2_RANGE_TABLE']);
const changedExisting=[...a.symbols].filter(([n,v])=>b.symbols.has(n)&&v.code!==b.symbols.get(n).code).map(([n])=>n);
const newSymbols=[...b.symbols].filter(([n])=>!a.symbols.has(n)).map(([n])=>n);
const allUnapprovedExistingExact=[...a.symbols].every(([n,v])=>allowedExisting.has(n)||!b.symbols.has(n)||v.code===b.symbols.get(n).code);
const protectedNames=['_wip88FragmentationPk','_wip88GurneyFragmentSpeed','gunB2FragmentField','gunB1Detonate','gunB1ShellEvent','gunB1ArmShell','gunB1SolveAirTrack','gunB2Pointing','spawnMainGunProjectileWip13B3','applyInterceptResult','shipboardRadarEchoFieldWip13B13','trackEkfUpdateRadar','getASMRcs','gunB1MigrateSave','SAM_MISSILE_PROFILES','INTERCEPT_FRAGMENT_WARHEADS'];
const preserved=Object.fromEntries(protectedNames.map(n=>[n,{same:a.symbols.get(n)?.code===b.symbols.get(n)?.code,sha256:sha(b.symbols.get(n).code)}]));
const ref=JSON.parse(fs.readFileSync(path.join(R,'docs/cleanup/B/fingerprint.json'))),protected281=Object.keys(ref.nativeSourceHashes).map(n=>({name:n,same:sha(b.symbols.get(n).code)===ref.nativeSourceHashes[n]})),approvedProtected=protected281.filter(x=>!x.same&&x.name==='gunB1FragmentationPk'),unexpectedProtected=protected281.filter(x=>!x.same&&x.name!=='gunB1FragmentationPk');
const env=s=>s.match(/\/\/ ENV_D_DATA_BEGIN[\s\S]*?\/\/ ENV_D_DATA_END/)[0];
const pattern=/data-c55-index="(\d+)">([^<]+)<\/script>/g,assets=q=>Object.fromEntries([...q.raw.toString().matchAll(pattern)].map(m=>[m[1],m[2]])),aa=assets(a),bb=assets(b);
let outside=b.raw.toString().replace(bb[13],aa[13]);const rec=/const records=(\[.*?\]);/s;outside=outside.replace(rec,'const records='+a.raw.toString().match(rec)[1]+';');
const spec=(q,n)=>vm.runInNewContext(q.symbols.get(n).code+';'+n,{deepFreezeShipProfileV48Wip09:x=>x});
const oldB1=spec(a,'GUN_B1_SPEC'),newB1=spec(b,'GUN_B1_SPEC'),oldB2=spec(a,'GUN_B2_SPEC'),newB2=spec(b,'GUN_B2_SPEC');
const restoredB1=JSON.parse(JSON.stringify(newB1));restoredB1.fragments=oldB1.fragments;
const restoredB2=JSON.parse(JSON.stringify(newB2));restoredB2.fuze.polarCenterDeg=oldB2.fuze.polarCenterDeg;
const checks={
 baselineB2A:sha(a.raw)==='9515e70cb88f7caac8dd9c0b618a104a878882a5a1c06f0967059150e2b7d516',
 onlyApprovedExisting:changedExisting.every(n=>allowedExisting.has(n)),
 onlyApprovedNew:newSymbols.length===1&&newSymbols[0]==='gunB15inMottFragmentationPk',
 allUnapprovedExistingExact,
 specsRestorable:JSON.stringify(restoredB1)===JSON.stringify(oldB1)&&JSON.stringify(restoredB2)===JSON.stringify(oldB2),
 allNamedProtectedExact:Object.values(preserved).every(x=>x.same),
 legacyProtectedUnexpected0:unexpectedProtected.length===0,
 legacyProtectedAll281Exact:protected281.length===281&&protected281.every(x=>x.same),
 envelope120Exact:env(a.source)===env(b.source),
 assets0to12Exact:Object.keys(aa).filter(i=>i!=='13').every(i=>aa[i]===bb[i]),
 outsideMainManifestExact:outside===a.raw.toString(),
 noTestHooks:!b.source.includes('__B2B_UNIT__')&&!b.source.includes('__B2_RANGE_PROBE__'),
 surfaceFirstHitFunctionsExact:['gunB1Detonate','gunB1ShellEvent','gunB1ArmShell','wip13b1SurfaceGunReleaseGate','wip13b10SurfaceFireControlQuality'].every(n=>a.symbols.get(n).code===b.symbols.get(n).code),
};
const result={pass:Object.values(checks).every(Boolean),checks,changedExisting,newSymbols,protected281:{total:protected281.length,unchanged:protected281.filter(x=>x.same).length,approvedChanged:approvedProtected,unexpected:unexpectedProtected},preserved,baselineSha256:sha(a.raw),productSha256:sha(b.raw),baselineMainSha256:sha(a.source),productMainSha256:sha(b.source)};
fs.mkdirSync(path.join(P,'evidence'),{recursive:true});fs.writeFileSync(path.join(P,'evidence/scope.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));process.exitCode=result.pass?0:1;
