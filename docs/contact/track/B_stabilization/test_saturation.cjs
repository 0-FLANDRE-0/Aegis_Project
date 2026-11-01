// Isolated JS association saturation tests. No browser, world, RF or alternate
// assignment implementation: Hungarian and optional NIS kernels are extracted
// byte-for-byte from the real game main script supplied with --source.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{performance}=require('node:perf_hooks');
const ROOT=path.resolve(__dirname,'../../../..'),argv=process.argv.slice(2);
function arg(name,fallback){const i=argv.indexOf(name);return i<0?fallback:argv[i+1];}
const sourcePath=arg('--source','/dev/shm/track-b-baseline-source.js'),modulePath=path.resolve(arg('--module',path.join(ROOT,'docs/contact/track/B/association.js'))),phase=arg('--phase','baseline'),out=path.resolve(arg('--out',path.join(__dirname,'evidence','saturation-'+phase+'.json'))),samples=Number(arg('--samples','7'));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex'),source=fs.readFileSync(sourcePath,'utf8'),moduleSource=fs.readFileSync(modulePath,'utf8');
if(arg('--expect-module-sha',null)&&hash(moduleSource)!==arg('--expect-module-sha',null))throw Error('CANDIDATE_MODULE_CHANGED_AFTER_FREEZE');
function extract(name){
 const re=new RegExp('^( *)function '+name.replace(/[$]/g,'\\$')+'\\(','m'),m=re.exec(source);if(!m)throw Error('MISSING_NATIVE_FUNCTION:'+name);
 const end=new RegExp('^'+m[1]+'function [A-Za-z_$]','m').exec(source.slice(m.index+m[0].length));if(!end)throw Error('MISSING_NATIVE_SCOPE_END:'+name);
 return source.slice(m.index,m.index+m[0].length+end.index);
}
const names=['bridgeMasterEMinCostAssignmentV35','_mIdx','_matInv','_symmetrizeClampP','trackEkfInit','trackCartesianMeasurementCovarianceV33','trackCartesianAssociationNisV33'],native=Object.fromEntries(names.map(name=>[name,extract(name)]));
const scaleStart=source.indexOf('  const WORLD_UNITS_PER_KM_FIXED = 3.8;'),scaleEnd=source.indexOf('  let RADAR_RANGE_WORLD',scaleStart);if(scaleStart<0||scaleEnd<0)throw Error('MISSING_NATIVE_UNIT_CONSTANTS');
const unitSource=source.slice(scaleStart,scaleEnd)+['metersToWorld','worldToMeters'].map(name=>{const m=new RegExp('^  const '+name+' =.*$','m').exec(source);if(!m)throw Error('MISSING_NATIVE_UNIT_FUNCTION');return m[0];}).join('\n');
const loaded=new Function('window',unitSource+'\n'+Object.values(native).join('\n')+'\n'+moduleSource+'\nreturn {api:window.__TRACK_B_STABILIZATION__??window.__TRACK_B__,hungarian:bridgeMasterEMinCostAssignmentV35,nis:trackCartesianAssociationNisV33,toWorld:metersToWorld};')({});
if(!loaded.api||typeof loaded.api.solve!=='function')throw Error('CANDIDATE_SOLVER_API_REQUIRED: window.__TRACK_B_STABILIZATION__ or __TRACK_B__.solve(input,nativeHungarian)');
const GATE=64,DELTA=1,EPS=1e-9,DUMMY=GATE+.5,BLOCKED=1e6;
function matrixFor(input){const ids=[...new Set(input.pairs.map(p=>p.id))].sort((a,b)=>a-b),index=new Map(ids.map((id,i)=>[id,i])),matrix=Array.from({length:input.plotCount},()=>Array(ids.length).fill(BLOCKED).concat(Array(input.plotCount).fill(DUMMY)));for(const p of input.pairs)matrix[p.i][index.get(p.id)]=p.nis;return {ids,matrix};}
function oracle(input){const {ids,matrix}=matrixFor(input),start=performance.now(),assignment=loaded.hungarian(matrix),pairs=[];let fullCost=0;for(let i=0;i<matrix.length;i++){const j=assignment[i];if(!(j>=0))throw Error('NATIVE_HUNGARIAN_UNASSIGNED_ROW');fullCost+=matrix[i][j];if(j<ids.length&&matrix[i][j]<=GATE)pairs.push({i,id:ids[j],nis:matrix[i][j]});}return {ids,matrix,assignment,pairs,fullCost,wallMs:performance.now()-start};}
// Test-only mathematical certificate checker; never installed in a product.
function lowerBound(input,base){const minima=base.matrix.map(row=>Math.min(...row)),L=minima.reduce((a,b)=>a+b,0),certified=[];for(const p of base.pairs){const b=base.ids.indexOf(p.id),next=Math.min(...base.matrix[p.i].filter((_,j)=>j!==b)),bound=L-minima[p.i]+next;if(bound>base.fullCost+DELTA+EPS)certified.push({...p,bound});}return {L,baseFullCost:base.fullCost,certified,heldRows:input.plotCount-certified.length};}
const families=['sparse_chain_clear','dense_equal','dense_diagonal_clear','covariance_quality_gap','localized_ambiguity','embedded_greedy_trap','unbalanced_equal'];
function makeCase(family,n){
 const pairs=[],cols=family==='unbalanced_equal'?n-2:n,push=(i,j,nis)=>{if(nis<=GATE)pairs.push({i,id:1000+j,nis,sanity:{ok:true}});};let expected=new Map(),held=new Set(),covarianceFixture=null;
 if(family==='sparse_chain_clear')for(let i=0;i<n;i++){push(i,i,.05);if(i+1<n)push(i,i+1,10);expected.set(i,1000+i);}
 if(family==='dense_equal'||family==='unbalanced_equal'){for(let i=0;i<n;i++)for(let j=0;j<cols;j++)push(i,j,1);for(let i=0;i<n;i++)held.add(i);}
 if(family==='dense_diagonal_clear'){for(let i=0;i<n;i++)for(let j=0;j<n;j++)push(i,j,i===j?.1:10);for(let i=0;i<n;i++)expected.set(i,1000+i);}
 if(family==='localized_ambiguity'||family==='weak_ambiguity'){
  for(let i=0;i<n;i++)for(let j=0;j<n;j++)push(i,j,i<2&&j<2?(family==='weak_ambiguity'&&i!==j?1.2:1):i===j?.1:30);
  for(let i=2;i<n;i++)expected.set(i,1000+i);held.add(0);held.add(1);
 }
 if(family==='embedded_greedy_trap'){
  push(0,0,1600/450);push(0,1,12100/450);push(1,0,3600/450);push(1,2,63);
  for(let i=2;i<n;i++){push(i,i,.1);if(i+1<n)push(i,i+1,63);}push(2,1,63);
  // Global optimum needs row0->T1,row1->T0. The conservative row bound may
  // withhold row0, but must not revert to the original greedy row0->T0 steal.
  expected.set(1,1000);for(let i=2;i<n;i++)expected.set(i,1000+i);
 }
 if(family==='covariance_quality_gap'){
  const pv=[4,25,225,2500],rv=[2500,225,25,4],tracks=Array.from({length:n},(_,j)=>{const P=new Float64Array(36);for(let k=0;k<6;k++)P[k*6+k]=k<3?pv[j%4]:25;return {_kfX:Float64Array.from([j*100,0,8,0,0,0]),_kfP:P};});
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){const R=rv[i%4],meas={x:loaded.toWorld(i*100),y:loaded.toWorld(0),z:8,cartesianCovarianceM2:[R,0,0,0,R,0,0,0,16]},nis=loaded.nis(tracks[j],meas);push(i,j,nis);}for(let i=0;i<n;i++)expected.set(i,1000+i);
  covarianceFixture={classification:'EXPLICIT_ESTIMATOR_AND_MEASUREMENT_COVARIANCE_INPUT_NOT_RF_SNR_MODEL',trackPositionVarianceM2:pv,reportedHorizontalVarianceM2:rv,spacingM:100,nativeNis:true,productionPOrRChanged:false};
 }
 return {name:family+'_'+n,family,n,cols,input:{plotCount:n,pairs,gate:GATE,ambiguityDeltaCost:DELTA},expected,held,covarianceFixture};
}
function components(input){const rows=new Map(),cols=new Map();for(const p of input.pairs){if(!rows.has(p.i))rows.set(p.i,[]);rows.get(p.i).push(p.id);if(!cols.has(p.id))cols.set(p.id,[]);cols.get(p.id).push(p.i);}const seen=new Set(),out=[];for(const start of rows.keys()){if(seen.has(start))continue;const rr=new Set(),cc=new Set(),q=[start];while(q.length){const i=q.pop();if(rr.has(i))continue;rr.add(i);seen.add(i);for(const id of rows.get(i)){if(cc.has(id))continue;cc.add(id);for(const k of cols.get(id))q.push(k);}}out.push({rows:rr.size,cols:cc.size});}return out;}
function call(input){let calls=0,maxRows=0,maxCols=0,nativeWallMs=0;const before=JSON.stringify(input),start=performance.now(),result=loaded.api.solve(input,cost=>{calls++;maxRows=Math.max(maxRows,cost.length);maxCols=Math.max(maxCols,cost[0]?.length??0);const t=performance.now(),answer=loaded.hungarian(cost);nativeWallMs+=performance.now()-t;return answer;}),wallMs=performance.now()-start;return {result,wallMs,calls,maxRows,maxCols,nativeWallMs,inputUnchanged:JSON.stringify(input)===before};}
function canonical(result){return {pairs:result.pairs.map(p=>[p.i,p.id,p.nis]).sort((a,b)=>a[0]-b[0]),heldPlots:[...result.heldPlots].sort((a,b)=>a-b),heldTracks:[...result.heldTracks].sort((a,b)=>a-b)};}
const sizes=arg('--sizes','13,16,32,64').split(',').map(Number),selectedFamilies=arg('--families',families.join(',')).split(',');
if(sizes.some(n=>!Number.isSafeInteger(n)||n<2)||selectedFamilies.some(f=>![...families,'weak_ambiguity'].includes(f)))throw Error('INVALID_FIXTURE_SELECTION');
const rows=[],checks={},cases=sizes.flatMap(n=>selectedFamilies.map(family=>makeCase(family,n))).concat(argv.includes('--no-cap-cases')?[]:[129,257].flatMap(n=>['sparse_chain_clear','dense_equal'].map(family=>makeCase(family,n))));
for(const c of cases){
 const n=c.n,family=c.family,comp=components(c.input);if(comp.length!==1||comp[0].rows!==n)throw Error('FIXTURE_COMPONENT_PRECONDITION:'+c.name+JSON.stringify(comp));
 const base=oracle(c.input),bound=lowerBound(c.input,base),first=call(c.input);for(let i=1;i<2;i++)call(c.input);const times=[];for(let i=0;i<samples;i++)times.push(call(c.input).wallMs);times.sort((a,b)=>a-b);
 const result=canonical(first.result),permuted=canonical(call({...c.input,pairs:c.input.pairs.slice().reverse()}).result),oneToOne=new Set(result.pairs.map(p=>p[0])).size===result.pairs.length&&new Set(result.pairs.map(p=>p[1])).size===result.pairs.length;
 const oracleMap=new Map(base.pairs.map(p=>[p.i,p.id])),actualMap=new Map(result.pairs.map(p=>[p[0],p[1]])),requiredPairs=[...c.expected].every(([i,id])=>actualMap.get(i)===id),requiredHolds=[...c.held].every(i=>first.result.heldPlots.has(i));
 const safeRealPairs=result.pairs.every(([i,id])=>family==='dense_equal'||family==='unbalanced_equal'?false:oracleMap.get(i)===id),unmatchedHeld=Array.from({length:n},(_,i)=>i).every(i=>actualMap.has(i)||first.result.heldPlots.has(i));
 const saturatedWholeHold=result.pairs.length===0&&first.result.heldPlots.size===n&&first.calls===0;
 const declaredCap=loaded.api.stabilizationPolicy?.maxCertifiedComponentSize,overDeclaredCap=Number.isInteger(declaredCap)&&n>declaredCap,heldAssignedDisjoint=result.pairs.every(([i,id])=>!first.result.heldPlots.has(i)&&!first.result.heldTracks.has(id));
 const boundedReason=(first.result.components??[]).every(c=>c.reason==='COMPUTATION_BOUND_HOLD');
 const pass=phase==='baseline'?saturatedWholeHold:overDeclaredCap?saturatedWholeHold&&boundedReason:requiredPairs&&requiredHolds&&safeRealPairs&&unmatchedHeld&&first.calls<=1;
 checks[c.name]=pass&&oneToOne&&heldAssignedDisjoint&&first.inputUnchanged&&JSON.stringify(result)===JSON.stringify(permuted);
 rows.push({name:c.name,family,n,columns:c.cols,inputEdgeCount:c.input.pairs.length,components:comp,covarianceFixture:c.covarianceFixture,actual:result,componentReasons:(first.result.components??[]).map(c=>c.reason),declaredCap:declaredCap??null,overDeclaredCap,nativeHungarianCalls:first.calls,nativeLargestMatrix:[first.maxRows,first.maxCols],inputUnchanged:first.inputUnchanged,oneToOne,heldAssignedDisjoint,permutationExact:JSON.stringify(result)===JSON.stringify(permuted),requiredPairs,requiredHolds,safeRealPairs,unmatchedRowsHeld:unmatchedHeld,oldWholeComponentHoldReproduced:saturatedWholeHold,oracle:{pairs:base.pairs,fullRealPlusDummyCost:base.fullCost,wallMs:base.wallMs},certificate:{rowMinimumSum:bound.L,certifiedPairs:bound.certified,uncertifiedRows:bound.heldRows},timing:{warmupCalls:2,samples,postTimingPermutationValidationCalls:1,meanMs:times.reduce((a,b)=>a+b,0)/times.length,medianMs:times[Math.floor(times.length/2)],p95Ms:times[Math.min(times.length-1,Math.ceil(times.length*.95)-1)],nativeWallMs:first.nativeWallMs},pass:checks[c.name]});
}
// Exhaustive small-graph proof audit of the proposed lower-bound certificate.
let seed=0x51a7c0de,certifiedEdges=0,nearAssignments=0,graphs=0,actualLargeEdgesChecked=0,actualLargeGraphs=0;const proofErrors=[];
const rng=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};
for(let n=2;n<=5;n++)for(let trial=0;trial<30;trial++){
 const pairs=[];for(let i=0;i<n;i++)for(let j=0;j<n+1;j++){const values=[0,.5,1,4,30,63,1e6],cost=values[rng()%values.length];if(cost<=GATE)pairs.push({i,id:1000+j,nis:cost,sanity:{ok:true}});}if(!pairs.length)continue;
 const input={plotCount:n,pairs,gate:GATE},base=oracle(input),cert=lowerBound(input,base),near=[];
 function enumerate(i,used,assignment,total){if(total>base.fullCost+DELTA+EPS)return;if(i===n){near.push(assignment.slice());return;}enumerate(i+1,used,[...assignment,null],total+DUMMY);for(let j=0;j<base.ids.length;j++)if(!used.has(j)&&base.matrix[i][j]<=GATE){used.add(j);enumerate(i+1,used,[...assignment,base.ids[j]],total+base.matrix[i][j]);used.delete(j);}}
 enumerate(0,new Set(),[],0);graphs++;nearAssignments+=near.length;
 for(const edge of cert.certified){certifiedEdges++;if(!near.every(a=>a[edge.i]===edge.id))proofErrors.push({n,trial,edge,baseCost:base.fullCost,near});}
 if(phase==='candidate'){
  // Embed each exhaustively enumerated core in one >12 connected component.
  // Strong-row alternatives cost63 instead of.01; even replacing every core
  // dummy saves at most1.5 per core row, so no <=delta alternative uses them.
  const N=13,coreColumns=base.ids.length,large=pairs.map(p=>({...p})),firstStrongId=2000;
  for(let i=0;i<n;i++)large.push({i,id:firstStrongId,nis:63,sanity:{ok:true}});
  for(let i=n;i<N;i++){large.push({i,id:firstStrongId+i-n,nis:.01,sanity:{ok:true}});if(i+1<N)large.push({i,id:firstStrongId+i-n+1,nis:63,sanity:{ok:true}});}
  for(const id of base.ids)large.push({i:n,id,nis:63,sanity:{ok:true}});
  const largeInput={plotCount:N,pairs:large,gate:GATE,ambiguityDeltaCost:DELTA},largeBase=oracle(largeInput),expectedCost=base.fullCost+(N-n)*.01;
  if(Math.abs(largeBase.fullCost-expectedCost)>1e-6)throw Error('LARGE_EMBEDDING_OBJECTIVE_PRECONDITION');
  const actual=call(largeInput);actualLargeGraphs++;
  for(const edge of actual.result.pairs){actualLargeEdgesChecked++;const sound=edge.i<n?near.every(a=>a[edge.i]===edge.id):edge.id===firstStrongId+edge.i-n;if(!sound)proofErrors.push({n,trial,actualLargeEdge:edge,coreNear:near});}
 }
}
checks.lowerBoundCertificateSoundInExhaustiveGraphs=proofErrors.length===0;
const report={schema:'AEGIS_TRACK_B_SATURATION_ISOLATED_NATIVE_1',phase,status:Object.values(checks).every(Boolean)?phase==='baseline'?'BASELINE_DEFECT_REPRODUCED':'PASS':'FAIL',classification:'PURE_ASSOCIATION_GRAPH_AND_EXTRACTED_NATIVE_HUNGARIAN_NOT_NATURAL_RF_OR_BROWSER',commandArgs:argv,testSourceSha256:hash(fs.readFileSync(__filename)),sourcePath,nativeMainSha256:hash(source),modulePath,moduleSha256:hash(moduleSource),nativeFunctionSha256:Object.fromEntries(Object.entries(native).map(([k,v])=>[k,hash(v)])),nativeUnitContractSha256:hash(unitSource),mode:loaded.api.mode??null,policy:loaded.api.policy,stabilizationPolicy:loaded.api.stabilizationPolicy??null,productionPOrRModePhysicsChanged:false,checks,rows,lowerBoundProof:{deterministicTestSeed:'0x51a7c0de',graphs,nearOptimalAssignmentsEnumerated:nearAssignments,certifiedEdgesChecked:certifiedEdges,actualLargeGraphs,actualLargeEdgesChecked,errors:proofErrors},host:{node:process.version,platform:process.platform,architecture:process.arch,cpus:require('node:os').availableParallelism(),timingMeaning:'Same host, two separate browser lanes may be active; isolated Node wall/CPU diagnostic, not measured in-game FPS'},releaseApproved:false};
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,phase,moduleSha256:report.moduleSha256,cases:rows.length,failed:Object.entries(checks).filter(([,v])=>!v).map(([k])=>k),proof:report.lowerBoundProof,largest:rows.filter(r=>r.n===64).map(r=>({family:r.family,selected:r.actual.pairs.length,held:r.actual.heldPlots.length,calls:r.nativeHungarianCalls,meanMs:r.timing.meanMs,p95Ms:r.timing.p95Ms}))},null,2));
process.exitCode=Object.values(checks).every(Boolean)?0:1;
