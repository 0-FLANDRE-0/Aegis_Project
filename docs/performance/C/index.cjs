const fs=require('node:fs'),crypto=require('node:crypto'),acorn=require('acorn');
const s=fs.readFileSync(process.argv[2],'utf8'),out={};
const names=new Set(['trackRadarAssociationNisV31','trackRadarPrediction','trackEkfRadarJacobian','trackEkfInit','trackEkfUpdateRadar','spyGlobalAssignmentsV36','observerAcceptPlotsC']);
function walk(n){
 if(!n||typeof n!=='object')return;
 if(n.type==='FunctionDeclaration'&&names.has(n.id.name))(out[n.id.name]??=[]).push({start:[...s.slice(0,n.start)].length,end:[...s.slice(0,n.end)].length,sha256:crypto.createHash('sha256').update(s.slice(n.start,n.end)).digest('hex')});
 for(const[k,v]of Object.entries(n)){if(['start','end'].includes(k))continue;if(Array.isArray(v))v.forEach(walk);else if(v&&typeof v==='object')walk(v);}
}
walk(acorn.parse(s,{ecmaVersion:2022}));for(const n of names)if(out[n]?.length!==(n==='trackEkfInit'?2:1))throw Error(n+' canonical count');
fs.writeFileSync(process.argv[3],JSON.stringify(out,null,2)+'\n');
