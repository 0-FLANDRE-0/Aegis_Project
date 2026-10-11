// Pin BOTH foreign native-weapon closure and active-ship closure separately.
const fs=require('node:fs'),crypto=require('node:crypto'),acorn=require('acorn');
const s=fs.readFileSync(process.argv[2],'utf8'),ast=acorn.parse(s,{ecmaVersion:2022});
const names=new Set(['shipBodyFrameB','shipGameFrameV1','createShipBodyFrameV1','wip118FutureThreat','wip118NezPoint','wip118ReservationAtNezPoint','wip118FindNezPlan','wip118BuildEngagementControl']);
const out={};
function walk(n){
 if(!n||typeof n!=='object')return;
 if(n.type==='FunctionDeclaration'&&names.has(n.id.name)){
  (out[n.id.name]??=[]).push({start:[...s.slice(0,n.start)].length,end:[...s.slice(0,n.end)].length,sha256:crypto.createHash('sha256').update(s.slice(n.start,n.end)).digest('hex')});
 }
 for(const[k,v]of Object.entries(n)){if(['start','end','range'].includes(k))continue;if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}
}
walk(ast);
for(const name of names){const expected=name==='shipGameFrameV1'?3:name.startsWith('wip118')?2:1;if(out[name]?.length!==expected)throw Error(name+' provenance count');}
fs.writeFileSync(process.argv[3],JSON.stringify(out,null,2)+'\n');
