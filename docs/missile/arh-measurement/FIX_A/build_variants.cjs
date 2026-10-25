const fs=require('fs'),path=require('path'),crypto=require('crypto'),zlib=require('zlib');
const {unpack,mainScope}=require('../../fuze-zem/A/source.cjs');
const {patchMeasurement}=require('./patch.cjs');
const H=__dirname,R=path.resolve(H,'../../../..'),input=path.join(R,'Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html');
const EXPECTED='e42a2e05b8ff2096dfb334e7b9427cd2cd6da46d567083f06620ffdf35729ed7';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const raw=fs.readFileSync(input);if(sha(raw)!==EXPECTED)throw Error('UNEXPECTED_HANDOFF_INPUT');
const source=unpack(raw),scope=mainScope(source),sym=scope.symbols.get('_arhV2MonopulseMeasurement');if(!sym)throw Error('NO_MEASUREMENT_FUNCTION');
const variants={N:{angle:false,uncertainty:false},A:{angle:true,uncertainty:false},U:{angle:false,uncertainty:true},AU:{angle:true,uncertainty:true}};
const outDir='/tmp/aegis-arh-measurement-fix-a/variants';fs.mkdirSync(outDir,{recursive:true});
const rows={};
for(const [name,flags] of Object.entries(variants)){
  const after=patchMeasurement(sym.code,flags);let next=source.slice(0,sym.start)+after+source.slice(sym.end);
  if(name==='N'&&next!==source)throw Error('N_NOT_EXACT');
  if(name!=='N'){
    const restored=source.slice(0,sym.start)+sym.code+source.slice(sym.end);
    if(restored!==source)throw Error('OUT_OF_SCOPE_CHANGE');
  }
  let html=raw.toString(),packed=zlib.gzipSync(next,{level:9,mtime:0});
  const payload=html.match(/data-c55-index="13">([^<]+)<\/script>/);if(!payload)throw Error('NO_PAYLOAD');
  html=html.replace(payload[1],packed.toString('base64'));
  const manifest=html.match(/const records=(\[.*?\]);/s);if(!manifest)throw Error('NO_RECORDS');
  const records=JSON.parse(manifest[1]);Object.assign(records[13],{rawBytes:Buffer.byteLength(next),gzipBytes:packed.length,sha256:sha(next)});
  html=html.replace(manifest[0],'const records='+JSON.stringify(records)+';');
  const file=path.join(outDir,`Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A_${name}.html`);fs.writeFileSync(file,html);
  rows[name]={...flags,file,htmlBytes:Buffer.byteLength(html),htmlSha256:sha(html),mainBytes:Buffer.byteLength(next),mainSha256:sha(next),measurementBeforeSha256:sha(sym.code),measurementAfterSha256:sha(after)};
}
if(rows.N.htmlSha256!==EXPECTED)throw Error('N_HTML_NOT_BYTE_EXACT');
const final=path.join(R,'Aegis_SIM_v48_WIP_ARH_MEASUREMENT_FIX_A.html');fs.copyFileSync(rows.AU.file,final);rows.AU.finalFile=final;
fs.writeFileSync(path.join(H,'build.json'),JSON.stringify({schema:'AEGIS_ARH_MEASUREMENT_FIX_A_BUILD_1',baseCommit:'ef38c738e2d2d3b262d36d3a2001d0e903c969bf',input,inputHtmlSha256:EXPECTED,changedFunctions:['_arhV2MonopulseMeasurement'],variants:rows,finalHtmlSha256:rows.AU.htmlSha256,finalHtmlBytes:rows.AU.htmlBytes},null,2)+'\n');
console.log(JSON.stringify(rows,null,2));
