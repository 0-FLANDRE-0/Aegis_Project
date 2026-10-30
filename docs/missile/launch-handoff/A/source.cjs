// Read the selected product HTML. Never select old main or infer a version.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),acorn=require('acorn'),zlib=require('zlib');
const H=__dirname,R=path.resolve(H,'../../../..'),TEMP='/tmp/aegis-launch-handoff-a';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const {mainScope,unpack}=require(path.join(R,'docs/missile/fuze-zem/A/source.cjs'));
function basePath(){const n='Aegis_SIM_v48_WIP_FUZE_ZEM_A.html',p=path.join(R,n);return fs.existsSync(p)?p:path.join(R,'archive/v48/WIP_FUZE_ZEM_A',n);}
function load(file=basePath()){const raw=fs.readFileSync(file),source=unpack(raw),scope=mainScope(source);return{file,raw,source,...scope,htmlSha256:sha(raw)};}
module.exports={fs,path,crypto,acorn,zlib,H,R,TEMP,sha,mainScope,unpack,basePath,load};
if(require.main===module){const q=load();for(const n of process.argv.slice(2)){const s=q.symbols.get(n);if(!s)throw Error(n);console.log('\n## '+n+' @live-main:'+s.line+'\n'+s.code);}}
