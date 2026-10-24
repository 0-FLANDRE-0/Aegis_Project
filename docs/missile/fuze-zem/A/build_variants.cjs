const fs=require('fs'),path=require('path'),zlib=require('zlib');const {H,R,baseline,unpack,mainScope,sha}=require('./source.cjs'),{definitions}=require('./patches.cjs');
const raw=baseline(),old=unpack(raw),{symbols,main}=mainScope(old),dest=process.env.FZ_BUILD_DIR||'/tmp/aegis-fuze-zem/builds';fs.mkdirSync(dest,{recursive:true});fs.mkdirSync(path.join(H,'changes'),{recursive:true});const records=[];
for(const variant of ['BASE','F','Z','FZ','T','FZT','ZT','D','DZT']){
 const p=definitions(symbols,variant),edits=Object.entries(p.out).map(([name,code])=>({...symbols.get(name),name,newCode:code}));
 let at=main.body.start+1;for(const n of main.body.body){if(n.type==='ExpressionStatement'&&n.directive)at=n.end;else break;}
 const addition=p.constants.length?'\n'+p.constants.join('\n')+'\n':'';
 edits.push({start:at,end:at,newCode:addition});let source=old;for(const e of edits.sort((a,b)=>b.start-a.start))source=source.slice(0,e.start)+e.newCode+source.slice(e.end);
 let restored=source;if(addition)restored=restored.replace(addition,'');for(const [name,code]of Object.entries(p.out)){if(restored.split(code).length!==2)throw Error('PATCH_NOT_UNIQUE:'+name);restored=restored.replace(code,symbols.get(name).code);}if(restored!==old)throw Error('OUT_OF_SCOPE_MODIFICATION');
 let html=raw.toString();if(variant!=='BASE'){
  const m=html.match(/data-c55-index="13">([^<]+)<\/script>/),packed=zlib.gzipSync(source,{level:9,mtime:0});html=html.replace(m[1],packed.toString('base64'));
  const hit=html.match(/const records=(\[.*?\]);/s),assets=JSON.parse(hit[1]);Object.assign(assets[13],{rawBytes:Buffer.byteLength(source),gzipBytes:packed.length,sha256:sha(source)});html=html.replace(hit[0],'const records='+JSON.stringify(assets)+';');
 }
 const file=path.join(dest,'Aegis_SIM_v48_WIP_FUZE_ZEM_A_'+variant+'.html');fs.writeFileSync(file,html);
 fs.writeFileSync(path.join(H,'changes',variant+'.json'),JSON.stringify({variant,constants:p.constants,functions:Object.fromEntries(Object.entries(p.out).map(([k,v])=>[k,{line:symbols.get(k).line,before:symbols.get(k).code,after:v,beforeSha256:sha(symbols.get(k).code),afterSha256:sha(v)}]))},null,2));
 records.push({variant,file,htmlSha256:sha(html),mainSha256:sha(source),bytes:Buffer.byteLength(html),changedFunctions:Object.keys(p.out),existingCodeOtherwiseByteIdentical:true,oldEnvelopeTable:'HISTORICAL_ENV_D_RECALC_REQUIRED',newEnvelopeMeasurement:false});
}
fs.writeFileSync(path.join(H,'build-variants.json'),JSON.stringify({baseCommit:'058273c1f4b91c0d0c595e5399aaa967aa443f1c',baseHtmlSha256:sha(raw),records},null,2));console.log(JSON.stringify(records.map(r=>({variant:r.variant,bytes:r.bytes,changed:r.changedFunctions}))));
