// Compare unresolved identifiers; baseline's historical host globals stay explicit.
const fs=require('node:fs'),acorn=require('acorn'),scope=require('eslint-scope');
function inspect(file){const ast=acorn.parse(fs.readFileSync(file,'utf8'),{ecmaVersion:2022,sourceType:'script',ranges:true});const s=scope.analyze(ast,{ecmaVersion:2022,sourceType:'script',optimistic:true,ignoreEval:false});return [...new Set(s.globalScope.through.map(q=>q.identifier.name))].sort();}
const base=inspect(process.argv[2]),candidate=inspect(process.argv[3]),added=candidate.filter(q=>!base.includes(q));
const result={baseline:base,candidate,added,pass:added.length===0};console.log(JSON.stringify(result));process.exit(result.pass?0:1);
