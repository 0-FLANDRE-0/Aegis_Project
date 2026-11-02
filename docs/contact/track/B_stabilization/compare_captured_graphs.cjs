// AFTER_ACTION_DIAGNOSTIC_ONLY. No world/filter/RF calls or coefficient changes.
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const path=require('path'),P=__dirname;
const sourcePath='/dev/shm/track-b-baseline-source.js';
const source=fs.readFileSync(sourcePath,'utf8');
const a=source.indexOf('  function bridgeMasterEMinCostAssignmentV35(');
const b=source.indexOf('  function bridgeMasterEGlobalAssignmentsV35(',a);
if(a<0||b<0)throw Error('NATIVE_ASSIGNER_NOT_FOUND');
const native=source.slice(a,b),moduleText=fs.readFileSync(path.join(P,'association.js'),'utf8');
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
function load(text){const c={window:{},Math,Number,Map,Set,Float64Array,Int32Array,Uint8Array,Array,Object,JSON};vm.createContext(c);vm.runInContext(native+'\n'+text,c);return {api:c.window.__TRACK_B__,assign:vm.runInContext('bridgeMasterEMinCostAssignmentV35',c)};}
const current=load(moduleText);
if(moduleText.split('maxComponentSize:12,').length!==2)throw Error('REFERENCE_BOUND_TOKEN_NOT_UNIQUE');
// Only the PURE historical exact solver's computational ceiling is lifted.
// It receives the captured native NIS values; never generates a new NIS/S.
const exact=load(moduleText.replace('maxComponentSize:12,','maxComponentSize:128,'));
const inputPath=process.argv[2];if(!inputPath)throw Error('Usage: node compare_captured_graphs.cjs graph-array.json');
const raw=fs.readFileSync(inputPath),graphs=JSON.parse(raw),rows=[];
for(const [ordinal,g]of graphs.entries()){
 const input={...g.input,pairs:g.pairs},now=current.api.solve(input,current.assign),ref=exact.api.legacySolve(input,exact.assign);
 const key=p=>JSON.stringify([p.i,p.id]),ns=new Set(now.pairs.map(key)),rs=new Set(ref.pairs.map(key));
 rows.push({ordinal,step:g.step,timeS:g.timeS,route:input.route,plotCount:input.plotCount,
  components:now.components.map(c=>({rows:c.plots.length,cols:c.tracks.length,edges:c.edgeCount,reason:c.reason})),
  currentSelected:now.pairs.map(p=>({i:p.i,id:p.id,nis:p.nis})),currentHeld:[...now.heldPlots],
  exactNativeSelected:ref.pairs.map(p=>({i:p.i,id:p.id,nis:p.nis})),exactNativeHeld:[...ref.heldPlots],
  certifiedAcceptedAbsentFromExact:now.pairs.filter(p=>!rs.has(key(p))),
  conservativelyHeldButExactNativeResolved:ref.pairs.filter(p=>!ns.has(key(p))),
  originalCapturedSelected:g.selectedPairs,originalCapturedHeld:g.heldPlots});
}
const result={schema:'AEGIS_TRACK_B_CAPTURED_NATIVE_GRAPH_COMPARE_1',classification:'AFTER_ACTION_PURE_GRAPH_NO_NEW_MEASUREMENT',
 moduleSha256:hash(moduleText),sourcePath,nativeFunctionSha256:hash(native),inputSha256:hash(raw),
 computationalReference:'Frozen legacy exact alternative-forbid solver; only component ceiling12→128 in a test-only VM',
 physicalOrNisCoefficientsChanged:false,rows,releaseApproved:false};
const out=path.join(P,'evidence/ablation/GRAPH_EXACT_COMPARISON.json');fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({graphs:rows.length,large:rows.filter(r=>r.components.some(c=>c.rows>12||c.cols>12)).map(r=>({step:r.step,components:r.components,current:r.currentSelected.length,exact:r.exactNativeSelected.length,unnecessaryHolds:r.conservativelyHeldButExactNativeResolved.length,unsound:r.certifiedAcceptedAbsentFromExact.length}))}));
