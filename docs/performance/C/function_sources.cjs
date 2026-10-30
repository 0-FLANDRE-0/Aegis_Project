const fs=require('node:fs'),acorn=require('acorn');
const s=fs.readFileSync(process.argv[2],'utf8'),names=new Set(process.argv.slice(3)),out={};
function walk(n){if(!n||typeof n!=='object')return;if(n.type==='FunctionDeclaration'&&names.has(n.id.name))(out[n.id.name]??=[]).push(s.slice(n.start,n.end));for(const [k,v]of Object.entries(n)){if(['start','end'].includes(k))continue;if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}}
walk(acorn.parse(s,{ecmaVersion:2022}));process.stdout.write(JSON.stringify(out));
