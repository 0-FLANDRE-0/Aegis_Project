// Regenerate pinned function provenance from a decoded baseline, never at runtime.
const fs=require('node:fs'),crypto=require('node:crypto'),acorn=require('acorn');
const s=fs.readFileSync(process.argv[2],'utf8'),ast=acorn.parse(s,{ecmaVersion:2022,ranges:true});
const names=new Set(['shipSystemDamageB','electronicJammerSampleF','buildKh32VisualMesh']),out={};
function walk(n){
 if(!n||typeof n!=='object')return;
 const name=n.type==='FunctionDeclaration'?n.id?.name:n.type==='Property'&&n.method?n.key.name:null;
 if(names.has(name)){if(out[name])throw Error('Duplicate '+name);out[name]={start:[...s.slice(0,n.start)].length,end:[...s.slice(0,n.end)].length,sha256:crypto.createHash('sha256').update(s.slice(n.start,n.end)).digest('hex')};}
 for(const [k,v]of Object.entries(n)){if(['start','end','range'].includes(k))continue;if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}
}
walk(ast);if(Object.keys(out).length!==names.size)throw Error('Missing functions');fs.writeFileSync(process.argv[3],JSON.stringify(out,null,2)+'\n');
