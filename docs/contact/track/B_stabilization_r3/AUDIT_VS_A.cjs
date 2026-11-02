// TRACK-B scope gate. Explicit association allowlists cannot waive RF/EKF or
// weapon/physics kernels. No browser, diagnostic view or gameplay code runs.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root="/dev/shm/aegis-ciws-dmg-a",hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const{load}=require(path.join(root,'docs/gun/B2/phase1a/compact_source.cjs'));
const mode="ACTIVE";
const base="/dev/shm/aegis-ciws-dmg-a/Aegis_SIM_v48_WIP_TRACK_A.html",candidate="/dev/shm/aegis-ciws-dmg-a/Aegis_SIM_v48_WIP_TRACK_B_STABLE_C.html";
const buildPath="/dev/shm/aegis-ciws-dmg-a/docs/contact/track/B_stabilization_r3/AUDIT_INPUT_VS_A.json";
if(!fs.existsSync(buildPath)||!fs.existsSync(candidate))throw Error('No implemented TRACK-B artifact: build a reviewed nonempty patch manifest first');
const build=JSON.parse(fs.readFileSync(buildPath));
if(build.implementationMode!==mode)throw Error('CANDIDATE_MODE_MISMATCH');
if(hash(fs.readFileSync(base))!=="e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a")throw Error('PINNED_AUDIT_BASE_CHANGED');
if(hash(fs.readFileSync(candidate))!==build.htmlSha256)throw Error('CANDIDATE_BUILD_CHECKSUM_MISMATCH');
const a=load(base),b=load(candidate),inherited=JSON.parse(fs.readFileSync("/dev/shm/aegis-ciws-dmg-a/docs/contact/track/A/SCOPE.json"));
const allowed=new Set(build.allowedChangedSymbols||[]),allowedAdded=new Set(build.allowedAddedSymbols||[]),exceptions=new Set(build.allowedProtectedAssociationChanges||[]);
const eligibleProtectedExceptions=new Set(['trackMayAcceptSurfacePlotCrossDomainWip13B14','trackMayAcceptAirPlotCrossDomainWip13B14']);
const protectedNames=new Set(inherited.protectedSymbols.map(x=>x.name));
const invalidExceptions=[...exceptions].filter(n=>protectedNames.has(n)&&!eligibleProtectedExceptions.has(n));
const changed=[...a.symbols].filter(([n,v])=>b.symbols.get(n)?.code!==v.code).map(([n])=>n),added=[...b.symbols.keys()].filter(n=>!a.symbols.has(n));
const forbiddenChanged=changed.filter(n=>!allowed.has(n)),forbiddenAdded=added.filter(n=>!allowedAdded.has(n));
const protectedSymbols=inherited.protectedSymbols.map(({name})=>{const old=a.symbols.get(name)?.code,now=b.symbols.get(name)?.code;return{name,before:hash(old??''),after:hash(now??''),equal:old===now,explicitAssociationException:exceptions.has(name)&&eligibleProtectedExceptions.has(name)};});
// Nested copies are real owner-specific code too. Inspect named declarations
// recursively, retaining lexical named-function ancestry and duplicate order.
const immutableKernel=/^(trackEkf|trackRadarAssociationNis|trackSurfaceRadarAssociationNis|trackSurfacePositionAssociationNis|trackCartesianAssociationNis|trackRadarPrediction|trackSurfaceRadarPrediction|shipboardRadarEchoField|rf|computeInterceptPk|applyInterceptResult|networkIntersectionG|networkNisG|updateMissile|updateHarpoon|gameFlightTermination|computeZEM|_wip79|_arh|_sarh|wip99|_wip99|ciwsLocalMeasurement|c55UpdateFile|applyPhalanxProjectileHit)/;
function nestedProtected(q){const result=new Map(),counts=new Map();
 function walk(node,parents){if(!node||typeof node!=='object')return;let next=parents;
  if(node.type==='FunctionDeclaration'&&node.id){const stem=parents+'/'+node.id.name,n=counts.get(stem)||0;counts.set(stem,n+1);const key=stem+'#'+n;next=key;if(immutableKernel.test(node.id.name))result.set(key,q.source.slice(node.start,node.end));}
  for(const[k,v]of Object.entries(node))if(!['loc','range','start','end'].includes(k)){if(Array.isArray(v))for(const item of v)walk(item,next);else if(v&&typeof v==='object')walk(v,next);}
 }walk(q.main.body,'MAIN');return result;
}
const na=nestedProtected(a),nb=nestedProtected(b),nestedProtectedSymbols=[...na].map(([name,s])=>({name,before:hash(s),after:hash(nb.get(name)??''),equal:s===nb.get(name)}));
const addedNestedKernels=[...nb.keys()].filter(n=>!na.has(n));
const pass=build.inverseByteExact===true&&!forbiddenChanged.length&&!forbiddenAdded.length&&!invalidExceptions.length&&protectedSymbols.every(x=>x.equal||x.explicitAssociationException)&&nestedProtectedSymbols.every(x=>x.equal)&&!addedNestedKernels.length;
const out={schema:'AEGIS_TRACK_B_SCOPE_1',implementationMode:mode,baselineHtmlSha256:hash(a.raw),candidateHtmlSha256:hash(b.raw),pass,changed,added,forbiddenChanged,forbiddenAdded,invalidExceptions,protectedSymbols,nestedProtectedSymbols,addedNestedKernels};
fs.writeFileSync("/dev/shm/aegis-ciws-dmg-a/docs/contact/track/B_stabilization_r3/SCOPE_VS_A.json",JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({pass,mode,changed,added,protected:protectedSymbols.length,nestedProtected:nestedProtectedSymbols.length,forbiddenChanged,forbiddenAdded,invalidExceptions,addedNestedKernels}));if(!pass)process.exitCode=1;
