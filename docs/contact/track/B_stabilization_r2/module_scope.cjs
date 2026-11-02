// Static R1 -> R2 module proof. Parse source only; do not execute a game/solver.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
let acorn;try{acorn=require('acorn');}catch(_){acorn=require('/workspace/aegis-performance-c/docs/performance/C/node_modules/acorn');}
const P=__dirname,oldPath=path.join(P,'../B_stabilization/association.js'),newPath=path.join(P,'association.js');
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const old=fs.readFileSync(oldPath,'utf8'),now=fs.readFileSync(newPath,'utf8'),contract=JSON.parse(fs.readFileSync(path.join(P,'CHANGE_CONTRACT.json')));
if(hash(old)!=='ec66a28a8bb92888228a45a6a626007f288c440b3054e2e203730bbe9e8e4c71')throw Error('FROZEN_R1_MODULE_CHANGED');
function parse(source){const ast=acorn.parse(source,{ecmaVersion:'latest'});return new Map(ast.body.filter(n=>n.type==='FunctionDeclaration').map(n=>[n.id.name,{node:n,code:source.slice(n.start,n.end)}]));}
const a=parse(old),b=parse(now),changed=[...a.keys()].filter(n=>a.get(n).code!==b.get(n)?.code),added=[...b.keys()].filter(n=>!a.has(n)),removed=[...a.keys()].filter(n=>!b.has(n));
const forbiddenChanged=changed.filter(n=>!contract.allowedChangedSymbols.includes(n)),forbiddenAdded=added.filter(n=>!contract.allowedAddedSymbols.includes(n));
function normalized(source,functions,addedFunctions){const edits=[];
 for(const name of contract.allowedChangedSymbols){const n=functions.get(name)?.node;if(n)edits.push({start:n.start,end:n.end,text:'FUNCTION_ALLOWED_'+name});}
 for(const name of addedFunctions){const n=functions.get(name).node;let start=source.lastIndexOf('\n',n.start-1)+1,end=n.end;
  while(start>0){const previousEnd=start-1,previousStart=source.lastIndexOf('\n',previousEnd-1)+1,line=source.slice(previousStart,previousEnd);if(!line.startsWith('//'))break;start=previousStart;}
  if(source[end]==='\n')end++;edits.push({start,end,text:''});}
 for(const e of edits.sort((x,y)=>y.start-x.start))source=source.slice(0,e.start)+e.text+source.slice(e.end);return source;
}
const outsideAllowedFunctionsByteExact=normalized(old,a,[])===normalized(now,b,added);
const scalars=['lowerBoundCertifiedCount','exactResidualCertifiedCount','residualComponentsSolved','residualRefinementRejected'];
const traceOld=a.get('trackBTraceB').code,traceExpected=traceOld.replace("'certifiedCount','evidenceResolved']","'certifiedCount','evidenceResolved',"+scalars.map(s=>"'"+s+"'").join(',')+"]");
const selectOld=a.get('trackBSelectB').code,selectExpected=selectOld.replace('evidenceResolved:c.evidenceResolved===true});','evidenceResolved:c.evidenceResolved===true,'+scalars.map(s=>s+':c.'+s).join(',')+'});');
const checks={allowedExistingFunctionsOnly:!forbiddenChanged.length,oneApprovedResidualHelperOnly:added.length===1&&!forbiddenAdded.length,noRemovedFunctions:!removed.length,outsideAllowedFunctionsByteExact,traceOnlyFourDiagnosticScalars:b.get('trackBTraceB').code===traceExpected,selectOnlyFourDiagnosticScalars:b.get('trackBSelectB').code===selectExpected};
const result={schema:'AEGIS_TRACK_B_STABILIZATION_R2_MODULE_SCOPE_1',pass:Object.values(checks).every(Boolean),classification:'STATIC_SOURCE_ONLY_NOT_MATH_OR_GAMEPLAY_VALIDATION',r1ModuleSha256:hash(old),r2ModuleSha256:hash(now),changeContractSha256:hash(fs.readFileSync(path.join(P,'CHANGE_CONTRACT.json'))),changed,added,removed,forbiddenChanged,forbiddenAdded,checks,sharedFunctions:[...a].map(([name,value])=>({name,before:hash(value.code),after:hash(b.get(name)?.code??''),equal:value.code===b.get(name)?.code,explicitChange:contract.allowedChangedSymbols.includes(name)})),gameCodeExecuted:false,solverExecuted:false,releaseApproved:false};
fs.writeFileSync(path.join(P,'MODULE_SCOPE.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({pass:result.pass,changed,added,removed,checks,r2ModuleSha256:hash(now)}));if(!result.pass)process.exitCode=1;
