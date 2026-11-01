const fs=require('fs'),crypto=require('crypto'),path=require('path');
const {load}=require('../phase1a/compact_source.cjs');
const P=__dirname,root=path.resolve(P,'../../../..'),product=path.join(root,'Aegis_SIM_v48_WIP_GUN_B2.html');
const q=load(product),prior=JSON.parse(fs.readFileSync(path.join(P,'../phase1a/measurement-build.json'))),build=JSON.parse(fs.readFileSync(path.join(P,'build.json')));
const sha=s=>crypto.createHash('sha256').update(s).digest('hex'),names=Object.keys(prior.modelFingerprints.nativeSourceHashes),nativeSourceHashes={};
for(const name of names){const symbol=q.symbols.get(name);if(!symbol)throw Error('MISSING:'+name);nativeSourceHashes[name]=sha(symbol.code);}
const modelFingerprints={nativeSourceHashes};
build.modelFingerprints=modelFingerprints;
fs.writeFileSync(path.join(P,'build.json'),JSON.stringify(build,null,2)+'\n');
fs.writeFileSync(path.join(P,'measurement-build.json'),JSON.stringify({htmlSha256:build.htmlSha256,mainSha256:build.mainSha256,modelFingerprints},null,2)+'\n');
console.log(JSON.stringify({htmlSha256:build.htmlSha256,nativeSourceHashes},null,2));
