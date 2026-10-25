const fs=require('fs'),path=require('path'),crypto=require('crypto'),zlib=require('zlib'),childProcess=require('child_process');
const {unpack,mainScope}=require('../../fuze-zem/A/source.cjs');
const {patchKappaPipState}=require('./patch.cjs');
const H=__dirname,R=path.resolve(H,'../../../..');
const input=path.join(R,'Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html');
const output=path.join(R,'Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html');
const EXPECTED='900be4a2d146ecf33eff67f1719134b9a93eb58c3dc79fbc9b6a6cc813c3cfab';
const EXPECTED_FUNCTION='554775f6c4fcc3335170c9c3304a8f81940cf0d718889c74a2a75536cd32e480';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const raw=fs.readFileSync(input);if(sha(raw)!==EXPECTED)throw Error('UNEXPECTED_FIX_A_INPUT');
const source=unpack(raw),scope=mainScope(source),sym=scope.symbols.get('_wip79KappaPipState');
if(!sym||sha(sym.code)!==EXPECTED_FUNCTION)throw Error('UNEXPECTED_KAPPA_PIP_FUNCTION');
const outDir='/tmp/aegis-near-vertical-path-fix-a/variants';fs.mkdirSync(outDir,{recursive:true});
const variants={BASE:{patch:false,stability:false},MIN:{patch:true,stability:false},FINAL:{patch:true,stability:true}},rows={};
for(const[name,flags]of Object.entries(variants)){
  const after=flags.patch?patchKappaPipState(sym.code,{stability:flags.stability}):sym.code;
  let next=source.slice(0,sym.start)+after+source.slice(sym.end);
  let html=raw.toString();
  if(flags.patch){
    const payload=html.match(/data-c55-index="13">([^<]+)<\/script>/);if(!payload)throw Error('NO_PAYLOAD');
    const packed=zlib.gzipSync(next,{level:9,mtime:0});html=html.replace(payload[1],packed.toString('base64'));
    const manifest=html.match(/const records=(\[.*?\]);/s);if(!manifest)throw Error('NO_RECORDS');
    const records=JSON.parse(manifest[1]);Object.assign(records[13],{rawBytes:Buffer.byteLength(next),gzipBytes:packed.length,sha256:sha(next)});
    html=html.replace(manifest[0],'const records='+JSON.stringify(records)+';');
  }
  const file=name==='FINAL'?output:path.join(outDir,`Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A_${name}.html`);
  fs.writeFileSync(file,html);
  rows[name]={...flags,file,htmlBytes:Buffer.byteLength(html),htmlSha256:sha(html),mainBytes:Buffer.byteLength(next),mainSha256:sha(next),functionBeforeSha256:sha(sym.code),functionAfterSha256:sha(after)};
}
if(rows.BASE.htmlSha256!==EXPECTED)throw Error('BASE_NOT_BYTE_EXACT');
const result={schema:'AEGIS_NEAR_VERTICAL_PATH_FIX_A_BUILD_1',baseCommit:'759fcd94bfa1081b268bfff9967f0f97088b7078',mainObserved:'cb70a637105ce00e7c0619270237cc35a83d39c2',input,inputHtmlSha256:EXPECTED,inputFunctionSha256:EXPECTED_FUNCTION,changedFunctions:['_wip79KappaPipState'],variants:rows,finalFile:output,finalHtmlSha256:rows.FINAL.htmlSha256,finalHtmlBytes:rows.FINAL.htmlBytes};
fs.writeFileSync(path.join(H,'kappa-pip.before.js'),sym.code+'\n');
fs.writeFileSync(path.join(H,'kappa-pip.minimum.js'),patchKappaPipState(sym.code,{stability:false})+'\n');
fs.writeFileSync(path.join(H,'kappa-pip.final.js'),patchKappaPipState(sym.code,{stability:true})+'\n');
try{childProcess.execFileSync('diff',['-u','--label','ARH_FIX_A/_wip79KappaPipState','--label','NEAR_VERTICAL_PATH_FIX_A/_wip79KappaPipState',path.join(H,'kappa-pip.before.js'),path.join(H,'kappa-pip.final.js')],{encoding:'utf8'});}catch(e){if(e.status!==1)throw e;fs.writeFileSync(path.join(H,'kappa-pip.diff'),e.stdout);}
fs.writeFileSync(path.join(H,'build.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
