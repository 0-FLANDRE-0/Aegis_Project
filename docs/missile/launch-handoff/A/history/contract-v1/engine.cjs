// DIAGNOSTIC_ONLY: every native function is extracted from the SELECTED HTML.
const{fs,path,acorn,H,R,TEMP,sha,load,basePath}=require('./source.cjs');
const D=path.join(R,'docs/envelope/D'),input=JSON.parse(fs.readFileSync(path.join(D,'inputs.json'))),boundaries=require(path.join(D,'diagnostic/boundaries.json'));
const template=fs.readFileSync(path.join(D,'diagnostic/native-engine.js'),'utf8'),originalPrivate=fs.readFileSync(path.join(D,'diagnostic/private.js'),'utf8'),oldHooks=fs.readFileSync(path.join(R,'docs/missile/fuze-zem/A/hooks.js'),'utf8'),hooks=oldHooks+'\n'+fs.readFileSync(path.join(H,'hooks.js'),'utf8');
const templateAst=acorn.parse(template,{ecmaVersion:'latest'});const templateNames=new Set(templateAst.body.flatMap(n=>n.type==='FunctionDeclaration'?[n.id.name]:n.type==='VariableDeclaration'?n.declarations.filter(d=>d.id.type==='Identifier').map(d=>d.id.name):[]));
function sourceFor(file=basePath()){
 const product=load(file),edits=[],functionHashes={},keptBoundaries=[];
 for(const n of templateAst.body){if(n.type!=='FunctionDeclaration')continue;const name=n.id.name,live=product.symbols.get(name);if(Object.hasOwn(boundaries,name)||!live){keptBoundaries.push(name);continue;}edits.push({start:n.start,end:n.end,code:live.code});functionHashes[name]=sha(live.code);}
 let native=template;for(const x of edits.sort((a,b)=>b.start-a.start))native=native.slice(0,x.start)+x.code+native.slice(x.end);
 const additions=[];for(const[name,v]of product.symbols)if(!templateNames.has(name)&&/^(samFuzeSignal|SAM_FUZE_SIGNAL|TRACKED_PASS|gameTrackedPass|samLaunchHandoff)/.test(name)){additions.push(v.type==='function'?v.code:'const '+v.code+';');functionHashes[name]=sha(v.code);}
 native=additions.join('\n')+'\n'+native;
 let priv=originalPrivate.replace('q._kfX.set([s.posM.x,s.posM.y,s.posM.z,s.velMps.x,s.velMps.y,s.velMps.z]);','q._kfP=new Float64Array(36);q._kfX.set([s.posM.x,s.posM.y,s.posM.z,s.velMps.x,s.velMps.y,s.velMps.z]);');
 priv=priv.replace('const samples=[],phases=[];let lastPhase',"handoffCaseA={ticks:[],current:null,handoff:null,at12:null,trace:c.trace!==false};diagCaseA={fuze:[],phases:[],passes:[],maxDemand:null,lastRange:null,lastSlope:0,lastPhase:''};\n const samples=[],phases=[];let lastPhase");
 priv=priv.replace('simStepCounter++;apogeeM=', 'handoffStepA(m,t);diagStepA(m,t);\n  simStepCounter++;apogeeM=');priv=priv.replace('targetAltitudeM:t.z,phase:phase()', 'targetAltitudeM:t.z,phase:phase(),telemetry:snapshotHandoffA(m)');
 priv=priv.replace('batteryRemainingS:m._gameBatteryRemainingS??null};',"batteryRemainingS:m._gameBatteryRemainingS??null,telemetry:handoffCaseA,diagnostic:diagCaseA,nativeCpa:{timeS:m.cpaTimeS??null,distanceM:m.cpaDistM??null,commandG:m.cpaCommandG??null,availableG:m.cpaAvailableG??null},fuzeState:Object.fromEntries(Object.entries(m).filter(([k])=>k.startsWith('_fuze')&&k!=='_fuzeSignalChannelsA'))};");
 priv=priv.replace('return {runCase,profiles:',"return {runCase,unit:{gate:typeof samLaunchHandoffGateA==='function'?samLaunchHandoffGateA:null,bridge:applyGuidanceKernelV1ToLegacyRates,profile:SAM_MISSILE_PROFILES.SM2MR_BLKIIIA_SIM,globalRng:()=>SIM_RNG_STATE>>>0},profiles:");
 const source=native+'\n'+hooks+'\n'+priv;acorn.parse(source,{ecmaVersion:'latest',allowReturnOutsideFunction:true});
 return {source,native,privateSource:priv,hooks,input,product:{file:product.file,htmlSha256:product.htmlSha256,mainSha256:sha(product.source)},functionHashes,keptBoundaries,hash:sha(source)};
}
function create(file=basePath()){const p=sourceFor(file);return new Function('DATA','SETTINGS','PROFILE','PRIVATE_SHIP',p.source)(structuredClone(input.data),structuredClone(input.settings),{},{entityId:'ENV_PRIVATE',navigation:{heading:0,speed:0,positionWorld:{x:0,y:0}},weapons:{}});}
const seeds=require(path.join(D,'engine.cjs')).seeds;module.exports={create,sourceFor,seeds,input};
