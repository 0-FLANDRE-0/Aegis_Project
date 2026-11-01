// TRACK-B association policy only. No RF/EKF/IFF/authority/weapon coefficients.
// Geometry reads anonymous measurements and receiver-owned filter estimates.
const TRACK_B_IMPLEMENTATION_MODE='ACTIVE';
const TRACK_B_STABILIZATION_MODE='ACTIVE'; // SHADOW applies frozen B; ACTIVE applies the validated candidate.
const TRACK_B_STABLE_POLICY=Object.freeze({provenance:'SIM_TUNED',reference:'ASSOCIATION_POLICY_NOT_RF',maxCertifiedComponentSize:128,maxExactComponentSize:16}); // Computational work bound only; no NIS/measurement threshold change.
const TRACK_B_POLICY=Object.freeze({
  provenance:'SIM_TUNED', reference:'GAME_ASSOCIATION_POLICY_NOT_SENSOR_PHYSICS',
  ambiguityDeltaNis:1, // Near-equal native NIS cost heuristic, not a calibrated probability.
  maxPositionInnovationM:2500, maxRadialInnovationMps:180,
  // Existing networkAssociationNisG hard bounds, reused as association-only
  // sanity. Neither measurement nor track covariance can remove these caps.
  maxComponentSize:12, numericEpsilon:1e-9,
  defaultTraceCapacity:1024, minTraceCapacity:16, maxTraceCapacity:4096
});
const TRACK_B_DIAG={enabled:false,capacity:TRACK_B_POLICY.defaultTraceCapacity,records:[],serial:0,dropped:0,errors:0};
function trackBFiniteB(v){return typeof v==='number'&&Number.isFinite(v);}
function trackBIdCompareB(a,b){if(typeof a==='number'&&typeof b==='number')return a-b;const x=String(a),y=String(b);return x<y?-1:x>y?1:0;}
function trackBPairCompareB(a,b){return a.nis-b.nis||a.i-b.i||trackBIdCompareB(a.id,b.id);}
function trackBPairCopyB(p){
  const out={i:p.i,id:p.id,nis:p.nis};
  if(p.sanity&&typeof p.sanity==='object'){
    out.sanity={ok:p.sanity.ok!==false};
    for(const k of ['reason','distanceM','distanceGateM','measurementPositionSigmaM','radialInnovationMps','radialGateMps','positionDimensions'])if(typeof p.sanity[k]==='string'||trackBFiniteB(p.sanity[k])||p.sanity[k]===null)out.sanity[k]=p.sanity[k];
  }
  if(p.evidence&&typeof p.evidence==='object'){out.evidence={valid:p.evidence.valid===true};for(const k of ['dimensions','epochS','logDetS'])if(trackBFiniteB(p.evidence[k]))out.evidence[k]=p.evidence[k];}
  return out;
}
function trackBLegacyGreedyB(pairs){
  const rows=new Set(),cols=new Set(),out=[];
  for(const q of pairs.slice().sort(trackBPairCompareB))if(!rows.has(q.i)&&!cols.has(q.id)){out.push(q);rows.add(q.i);cols.add(q.id);}
  return out;
}
function trackBGeometryB(tr,meas,mode='AIR'){
  const x=tr?._kfX,surface=mode==='SURFACE',withZ=!surface;
  if(!x||x.length<6||![x[0],x[1],...(withZ?[x[2]]:[])].every(trackBFiniteB))return {ok:false,reason:'FILTER_POSITION_UNAVAILABLE'};
  if(!trackBFiniteB(meas?.x)||!trackBFiniteB(meas?.y)||(withZ&&!trackBFiniteB(meas?.z)))return {ok:false,reason:'MEASUREMENT_POSITION_UNAVAILABLE'};
  const px=worldToMeters(meas.x),py=worldToMeters(meas.y),distanceM=Math.hypot(px-x[0],py-x[1],withZ?meas.z-x[2]:0);
  let sigmaM=0;
  const C=meas.cartesianCovarianceM2;
  if(C?.length===9&&[C[0],C[4],...(withZ?[C[8]]:[])].every(v=>trackBFiniteB(v)&&v>=0))sigmaM=Math.sqrt(C[0]+C[4]+(withZ?C[8]:0));
  else{
    const r=trackBFiniteB(meas.rangeM)?Math.abs(meas.rangeM):0,sr=trackBFiniteB(meas.rangeSigmaM)?Math.max(0,meas.rangeSigmaM):0;
    const sa=trackBFiniteB(meas.azSigmaDeg)?Math.max(0,meas.azSigmaDeg)*Math.PI/180:0,se=withZ&&trackBFiniteB(meas.elSigmaDeg)?Math.max(0,meas.elSigmaDeg)*Math.PI/180:0;
    sigmaM=Math.hypot(sr,r*sa,r*se);
  }
  const distanceGateM=TRACK_B_POLICY.maxPositionInnovationM;
  let radialInnovationMps=null,radialGateMps=null;
  if(trackBFiniteB(meas.radialMps)&&[x[3],x[4],x[5],meas.sensorVxMps,meas.sensorVyMps].every(trackBFiniteB)){
    let ux=meas.losUx,uy=meas.losUy,uz=surface?0:meas.losUz;
    if(![ux,uy,uz].every(trackBFiniteB)&&trackBFiniteB(meas.azRad)&&(surface||trackBFiniteB(meas.elRad))){const el=surface?0:meas.elRad;ux=Math.cos(el)*Math.cos(meas.azRad);uy=Math.cos(el)*Math.sin(meas.azRad);uz=Math.sin(el);}
    if([ux,uy,uz].every(trackBFiniteB)){
      if(surface||uz===0||trackBFiniteB(meas.sensorVzMps)){
        const vertical=surface||uz===0?0:uz*(x[5]-meas.sensorVzMps);
        radialInnovationMps=Math.abs(meas.radialMps-(ux*(x[3]-meas.sensorVxMps)+uy*(x[4]-meas.sensorVyMps)+vertical));
        radialGateMps=TRACK_B_POLICY.maxRadialInnovationMps;
      }
    }
  }
  const ok=distanceM<=distanceGateM&&(radialInnovationMps===null||radialInnovationMps<=radialGateMps);
  return {ok,reason:distanceM>distanceGateM?'INDEPENDENT_POSITION_SANITY':radialInnovationMps!==null&&radialInnovationMps>radialGateMps?'INDEPENDENT_RADIAL_SANITY':'NATIVE_NIS_PLUS_SANITY',distanceM,distanceGateM,measurementPositionSigmaM:sigmaM,radialInnovationMps,radialGateMps,positionDimensions:surface?2:3};
}
function trackBLegacySolveStableB(input,assigner){
  const gate=input.gate,plotCount=input.plotCount,ambiguityDelta=trackBFiniteB(input.ambiguityDeltaCost)&&input.ambiguityDeltaCost>=0?input.ambiguityDeltaCost:TRACK_B_POLICY.ambiguityDeltaNis;
  // plotCount is an index bound, never an allocation size. Own RF extraction
  // has no 256-discrete-echo guarantee; connected components, not total echoes,
  // are bounded below. A valid dense sweep must not throw from updateRadar.
  if(!trackBFiniteB(gate)||gate<=0||!Number.isSafeInteger(plotCount)||plotCount<0)throw new Error('TRACK_B_INVALID_GRAPH');
  const pairs=[],seen=new Set(),rejected=[];
  for(const p of input.pairs??[]){
    if(!Number.isInteger(p.i)||p.i<0||p.i>=plotCount||!['number','string'].includes(typeof p.id)||!trackBFiniteB(p.nis)||p.nis<0||p.nis>gate)continue;
    const key=JSON.stringify([p.i,p.id]);if(seen.has(key))continue;seen.add(key);
    if(p.sanity?.ok===false){rejected.push(trackBPairCopyB(p));continue;}pairs.push(trackBPairCopyB(p));
  }
  const byRow=new Map(),byCol=new Map();
  for(const p of pairs){if(!byRow.has(p.i))byRow.set(p.i,[]);if(!byCol.has(p.id))byCol.set(p.id,[]);byRow.get(p.i).push(p);byCol.get(p.id).push(p);}
  const visited=new Set(),heldPlots=new Set(),heldTracks=new Set(),chosen=[],components=[];
  for(const start of [...byRow.keys()].sort((a,b)=>a-b)){
    if(visited.has(start))continue;
    const rows=new Set(),cols=new Set(),queue=[start];
    while(queue.length){const i=queue.pop();if(rows.has(i))continue;rows.add(i);visited.add(i);for(const q of byRow.get(i)??[]){if(cols.has(q.id))continue;cols.add(q.id);for(const other of byCol.get(q.id)??[])if(!rows.has(other.i))queue.push(other.i);}}
    const rr=[...rows].sort((a,b)=>a-b),cc=[...cols].sort(trackBIdCompareB),edges=pairs.filter(p=>rows.has(p.i)),component={plots:rr,tracks:cc,edgeCount:edges.length,ambiguous:false,reason:null};
    if(rr.length>TRACK_B_POLICY.maxComponentSize||cc.length>TRACK_B_POLICY.maxComponentSize){component.ambiguous=true;component.reason='BOUNDED_COMPONENT_HOLD';for(const i of rr)heldPlots.add(i);for(const id of cc)heldTracks.add(id);components.push(component);continue;}
    if(edges.length===1){chosen.push(edges[0]);components.push(component);continue;}
    if(typeof assigner!=='function')throw new Error('TRACK_B_ASSIGNER_REQUIRED');
    const rowIndex=new Map(rr.map((v,i)=>[v,i])),colIndex=new Map(cc.map((v,i)=>[v,i])),dummy=gate+.5,blocked=1e6;
    const costs=rr.map(()=>Array(cc.length).fill(blocked).concat(Array(rr.length).fill(dummy)));
    const edgeIndex=new Map();for(const p of edges){const a=rowIndex.get(p.i),b=colIndex.get(p.id);costs[a][b]=p.nis;edgeIndex.set(a+':'+b,p);}
    const evaluate=(matrix)=>{
      const solution=assigner(matrix),out=[],map=new Map();let total=0;
      for(let a=0;a<rr.length;a++){const b=solution[a];if(Number.isInteger(b)&&b>=0&&b<cc.length&&matrix[a][b]<=gate){out.push({a,b});map.set(a,b);total+=matrix[a][b];}}
      return {out,map,total,count:out.length};
    };
    const base=evaluate(costs);
    for(const edge of base.out){
      const matrix=costs.map(row=>row.slice());matrix[edge.a][edge.b]=blocked;const alternative=evaluate(matrix);
      if(alternative.count!==base.count||alternative.total-base.total>ambiguityDelta+TRACK_B_POLICY.numericEpsilon)continue;
      component.ambiguous=true;component.reason='NEAR_EQUAL_MATCHING_HOLD';
      for(let a=0;a<rr.length;a++)if(base.map.get(a)!==alternative.map.get(a)){heldPlots.add(rr[a]);if(base.map.has(a))heldTracks.add(cc[base.map.get(a)]);if(alternative.map.has(a))heldTracks.add(cc[alternative.map.get(a)]);}
    }
    for(const q of base.out)chosen.push(edgeIndex.get(q.a+':'+q.b));components.push(component);
  }
  return {pairs:chosen.filter(p=>!heldPlots.has(p.i)&&!heldTracks.has(p.id)).sort(trackBPairCompareB),heldPlots,heldTracks,components,rejected,ambiguous:components.some(c=>c.ambiguous)};
}
// No new filter/gain/noise model: S is formed by the same native H/P/R
// arithmetic and floors as the already-computed association NIS. Never init,
// predict, correct or read identity/hit/authority/truth while asking for it.
function trackBLogDetStableB(S,n){
  if(!S||S.length!==n*n||!Array.from(S).every(trackBFiniteB))return null;
  const L=new Float64Array(n*n);let value=0;
  for(let i=0;i<n;i++)for(let j=0;j<=i;j++){
    let q=S[i*n+j];for(let k=0;k<j;k++)q-=L[i*n+k]*L[j*n+k];
    if(i===j){if(!(q>0))return null;L[i*n+j]=Math.sqrt(q);value+=Math.log(q);}
    else L[i*n+j]=q/L[j*n+j];
  }
  return trackBFiniteB(value)?value:null;
}
function trackBEvidenceStableB(tr,meas,model,epochS,measurementEpochS=epochS){
  const invalid=reason=>({valid:false,reason});
  if(!trackBFiniteB(epochS)||!trackBFiniteB(measurementEpochS)||Math.abs(epochS-measurementEpochS)>TRACK_B_POLICY.numericEpsilon)return invalid('EPOCH_NOT_ALIGNED');
  const P=tr?._kfP,x=tr?._kfX;
  if(!P||P.length!==36||!x||x.length!==6||!Array.from(P).every(trackBFiniteB)||!Array.from(x).every(trackBFiniteB))return invalid('OWNED_PRIOR_UNAVAILABLE');
  let n,S;
  if(model==='AIR'){
    if(!['rangeM','azRad','elRad','radialMps','sensorXWorld','sensorYWorld','sensorZM','sensorVxMps','sensorVyMps','sensorVzMps'].every(k=>trackBFiniteB(meas?.[k])))return invalid('AIR_OBSERVABILITY_UNAVAILABLE');
    n=4;
    // The native NIS call populated/validated this derived-only cache before
    // this read. The kernel itself verifies all six state /36 P/origin values.
    const kernel=trackRadarAssociationKernelPerfC(tr,meas),R=new Float64Array(16);
    const sr=Math.max(1,meas.rangeSigmaM??40),sa=deg(Math.max(.002,meas.azSigmaDeg??.08)),se=deg(Math.max(.003,meas.elSigmaDeg??.10)),sv=Math.max(.5,meas.radialVelSigmaMps??6);
    R[0]=sr*sr;R[5]=sa*sa;R[10]=se*se;R[15]=sv*sv;S=_matAdd(kernel.projected,R);
  }else if(model==='SURFACE_POSITION'){
    if(!['rangeM','azRad','sensorXWorld','sensorYWorld'].every(k=>trackBFiniteB(meas?.[k])))return invalid('SURFACE_OBSERVABILITY_UNAVAILABLE');
    // Position association deliberately ignores Doppler even if the original
    // plot carries it. Vertical surface priors cannot become measurements.
    n=2;const pr=trackSurfaceRadarPrediction(tr,meas),H=trackEkfSurfaceRadarJacobian(pr,false),Ht=_matTranspose(H,n,6),PHt=_matMul(P,6,6,Ht,n),R=new Float64Array(4);
    const sr=Math.max(1,meas.rangeSigmaM??60),sa=deg(Math.max(.01,meas.azSigmaDeg??.15));R[0]=sr*sr;R[3]=sa*sa;S=_matAdd(_matMul(H,n,6,PHt,n),R);
  }else if(model==='CARTESIAN'){
    if(meas?._reportedSurface||!['x','y','z'].every(k=>trackBFiniteB(meas?.[k])))return invalid('CARTESIAN_OBSERVABILITY_UNAVAILABLE');
    n=3;const R=trackCartesianMeasurementCovarianceV33(meas);S=new Float64Array(9);
    for(let i=0;i<n;i++)for(let j=0;j<n;j++)S[i*n+j]=P[i*6+j]+R[i*n+j];
  }else return invalid('UNKNOWN_NATIVE_MODEL');
  const logDetS=trackBLogDetStableB(S,n);
  return logDetS===null?invalid('INNOVATION_NOT_POSITIVE_DEFINITE'):{valid:true,dimensions:n,epochS,logDetS};
}
// Secondary evidence may only lift an existing HOLD. It never replaces the
// native NIS winner, changes native gates, or invents a missing observation.
function trackBEvidenceCertificateStableB(edges,rr,cc,base,assigner,delta,gate){
  if(base.out.length!==rr.length)return false; // no cardinality approximation
  const ri=new Map(rr.map((v,i)=>[v,i])),ci=new Map(cc.map((v,i)=>[v,i]));
  const blocked=1e6,cost=rr.map(()=>Array(cc.length).fill(blocked).concat(Array(rr.length).fill(blocked))),rowMeta=new Map();
  for(const p of edges){
    const e=p.evidence;if(e?.valid!==true||!Number.isInteger(e.dimensions)||e.dimensions<1||e.dimensions>4||!trackBFiniteB(e.epochS)||!trackBFiniteB(e.logDetS))return false;
    const old=rowMeta.get(p.i);if(old&&(old.dimensions!==e.dimensions||Math.abs(old.epochS-e.epochS)>TRACK_B_POLICY.numericEpsilon))return false;
    rowMeta.set(p.i,e);cost[ri.get(p.i)][ci.get(p.id)]=p.nis+e.logDetS;
  }
  // Row constants do not affect any complete matching. Keep real costs small
  // and positive without manufacturing a false-alarm/clutter density model.
  for(const row of cost){const v=Math.min(...row);for(let b=0;b<cc.length;b++)if(row[b]<blocked)row[b]-=v;}
  const solve=matrix=>{const a=assigner(matrix);let sum=0;for(let i=0;i<rr.length;i++){if(!Number.isInteger(a[i])||a[i]<0||a[i]>=cc.length||matrix[i][a[i]]>=blocked)return null;sum+=matrix[i][a[i]];}return {a,sum};};
  const best=solve(cost);if(!best||base.out.some(q=>best.a[q.a]!==q.b))return false;
  for(const q of base.out){const next=cost.map(row=>row.slice());next[q.a][q.b]=blocked;const alt=solve(next);if(alt&&alt.sum-best.sum<=delta+TRACK_B_POLICY.numericEpsilon)return false;}
  return true;
}
function trackBSolveB(input,assigner){
  const gate=input.gate,plotCount=input.plotCount,delta=trackBFiniteB(input.ambiguityDeltaCost)&&input.ambiguityDeltaCost>=0?input.ambiguityDeltaCost:TRACK_B_POLICY.ambiguityDeltaNis;
  if(!trackBFiniteB(gate)||gate<=0||!Number.isSafeInteger(plotCount)||plotCount<0)throw new Error('TRACK_B_INVALID_GRAPH');
  const pairs=[],seen=new Set(),rejected=[];
  for(const p of input.pairs??[]){
    if(!Number.isInteger(p.i)||p.i<0||p.i>=plotCount||!['number','string'].includes(typeof p.id)||!trackBFiniteB(p.nis)||p.nis<0||p.nis>gate)continue;
    const key=JSON.stringify([p.i,p.id]);if(seen.has(key))continue;seen.add(key);if(p.sanity?.ok===false){rejected.push(trackBPairCopyB(p));continue;}pairs.push(trackBPairCopyB(p));
  }
  const rowsToEdges=new Map(),colsToEdges=new Map();for(const p of pairs){if(!rowsToEdges.has(p.i))rowsToEdges.set(p.i,[]);if(!colsToEdges.has(p.id))colsToEdges.set(p.id,[]);rowsToEdges.get(p.i).push(p);colsToEdges.get(p.id).push(p);}
  const visited=new Set(),heldPlots=new Set(),heldTracks=new Set(),chosen=[],components=[];
  for(const start of [...rowsToEdges.keys()].sort((a,b)=>a-b)){
    if(visited.has(start))continue;const rows=new Set(),cols=new Set(),queue=[start];
    while(queue.length){const i=queue.pop();if(rows.has(i))continue;rows.add(i);visited.add(i);for(const p of rowsToEdges.get(i)??[]){if(cols.has(p.id))continue;cols.add(p.id);for(const q of colsToEdges.get(p.id)??[])if(!rows.has(q.i))queue.push(q.i);}}
    const rr=[...rows].sort((a,b)=>a-b),cc=[...cols].sort(trackBIdCompareB),edges=rr.flatMap(i=>rowsToEdges.get(i)),c={plots:rr,tracks:cc,edgeCount:edges.length,ambiguous:false,reason:null,certifiedCount:0,evidenceResolved:false};
    if(rr.length>TRACK_B_STABLE_POLICY.maxCertifiedComponentSize||cc.length>TRACK_B_STABLE_POLICY.maxCertifiedComponentSize){c.ambiguous=true;c.reason='COMPUTATION_BOUND_HOLD';for(const i of rr)heldPlots.add(i);for(const id of cc)heldTracks.add(id);components.push(c);continue;}
    if(edges.length===1){chosen.push(edges[0]);c.certifiedCount=1;components.push(c);continue;}
    if(typeof assigner!=='function')throw new Error('TRACK_B_ASSIGNER_REQUIRED');
    const ri=new Map(rr.map((v,i)=>[v,i])),ci=new Map(cc.map((v,i)=>[v,i])),dummy=gate+.5,blocked=1e6,costs=rr.map(()=>Array(cc.length).fill(blocked).concat(Array(rr.length).fill(dummy))),index=new Map();
    for(const p of edges){const a=ri.get(p.i),b=ci.get(p.id);costs[a][b]=p.nis;index.set(a+':'+b,p);}
    const evaluate=matrix=>{const a=assigner(matrix),out=[],map=new Map();let total=0,fullTotal=0;for(let i=0;i<rr.length;i++){const b=a[i];if(!Number.isInteger(b)||b<0||b>=matrix[i].length)throw new Error('TRACK_B_INVALID_ASSIGNER');fullTotal+=matrix[i][b];if(b<cc.length&&matrix[i][b]<=gate){out.push({a:i,b});map.set(i,b);total+=matrix[i][b];}}return {out,map,total,count:out.length,fullTotal};};
    const base=evaluate(costs),componentHeldRows=new Set(),componentHeldCols=new Set();let exactNativeTie=false;
    // Complete small saturation batches can use the SAME native exact
    // forbidden-edge checks as <=12. A loose row-minimum lower bound is not
    // evidence of ambiguity. Limit this extra work to <=16 rows AND columns;
    // partial parents and larger batches retain the conservative R2 path.
    const boundedFullExact=base.count===rr.length&&rr.length<=TRACK_B_STABLE_POLICY.maxExactComponentSize&&cc.length<=TRACK_B_STABLE_POLICY.maxExactComponentSize;
    if((rr.length>TRACK_B_POLICY.maxComponentSize||cc.length>TRACK_B_POLICY.maxComponentSize)&&!boundedFullExact){
      // Global native optimum first. This is NOT mutual-best/greedy peeling.
      // Each row may reuse columns in this relaxation, hence its objective is
      // a lower bound on every feasible alternative (including dummy costs).
      const mins=costs.map(row=>Math.min(...row)),lower=mins.reduce((a,b)=>a+b,0),certifiedCols=new Set(),certifiedRows=new Set();
      for(const q of base.out){let next=Infinity;for(let b=0;b<costs[q.a].length;b++)if(b!==q.b)next=Math.min(next,costs[q.a][b]);const altLower=lower-mins[q.a]+next;if(altLower>base.fullTotal+delta+TRACK_B_POLICY.numericEpsilon){chosen.push(index.get(q.a+':'+q.b));certifiedRows.add(rr[q.a]);certifiedCols.add(cc[q.b]);}}
      c.lowerBoundCertifiedCount=certifiedRows.size;c.exactResidualCertifiedCount=0;c.residualComponentsSolved=0;c.residualRefinementRejected=0;
      // C is present in EVERY near-optimal global alternative. Fixing C leaves
      // independent residual components. Only small/full-parent subproblems
      // use the existing exact alternative-forbid policy; never recurse into
      // another large Hungarian problem or invent an unmatched/clutter prior.
      if(base.count===rr.length&&certifiedRows.size>0&&certifiedRows.size<rr.length){
        const refinement=trackBRefineResidualStableB(input,edges,certifiedRows,certifiedCols,base.map,ri,ci,assigner,delta);
        c.residualComponentsSolved=refinement.solved;c.residualRefinementRejected=refinement.rejected;
        for(const p of refinement.pairs){chosen.push(p);certifiedRows.add(p.i);certifiedCols.add(p.id);c.exactResidualCertifiedCount++;}
      }
      for(const i of rr)if(!certifiedRows.has(i))heldPlots.add(i);for(const id of cc)if(!certifiedCols.has(id))heldTracks.add(id);
      c.certifiedCount=certifiedRows.size;c.ambiguous=certifiedRows.size<rr.length;
      c.reason=c.exactResidualCertifiedCount>0?(c.ambiguous?'LARGE_COMPONENT_REFINED_PARTIAL_HOLD':'LARGE_COMPONENT_REFINED_EXACT'):(c.ambiguous?'LARGE_COMPONENT_UNCERTIFIED_HOLD':'LARGE_COMPONENT_CERTIFIED');components.push(c);continue;
    }
    for(const q of base.out){
      const matrix=costs.map(row=>row.slice());matrix[q.a][q.b]=blocked;const alt=evaluate(matrix);
      if(alt.count!==base.count||alt.total-base.total>delta+TRACK_B_POLICY.numericEpsilon)continue;
      if(Math.abs(alt.total-base.total)<=TRACK_B_POLICY.numericEpsilon)exactNativeTie=true;
      for(let a=0;a<rr.length;a++)if(base.map.get(a)!==alt.map.get(a)){componentHeldRows.add(rr[a]);if(base.map.has(a))componentHeldCols.add(cc[base.map.get(a)]);if(alt.map.has(a))componentHeldCols.add(cc[alt.map.get(a)]);}
    }
    // An exact native tie cannot be made into a numeric-ID-dependent winner.
    if(componentHeldRows.size&&!exactNativeTie&&trackBEvidenceCertificateStableB(edges,rr,cc,base,assigner,delta,gate)){componentHeldRows.clear();componentHeldCols.clear();c.evidenceResolved=true;c.reason='SAME_NIS_WINNER_INNOVATION_DENSITY_CERTIFIED';}
    if(componentHeldRows.size){c.ambiguous=true;c.reason='NEAR_EQUAL_MATCHING_HOLD';for(const i of componentHeldRows)heldPlots.add(i);for(const id of componentHeldCols)heldTracks.add(id);}
    for(const q of base.out)chosen.push(index.get(q.a+':'+q.b));c.certifiedCount=base.out.filter(q=>!componentHeldRows.has(rr[q.a])&&!componentHeldCols.has(cc[q.b])).length;components.push(c);
  }
  return {pairs:chosen.filter(p=>!heldPlots.has(p.i)&&!heldTracks.has(p.id)).sort(trackBPairCompareB),heldPlots,heldTracks,components,rejected,ambiguous:components.some(c=>c.ambiguous)};
}
// Pure bounded refinement; only precomputed native costs/metadata are read.
// Returned pairs must equal the ORIGINAL global native NIS winner, so a new
// local tie/dummy choice cannot silently replace the parent's selected edge.
function trackBRefineResidualStableB(input,edges,fixedRows,fixedCols,parentMap,rowIndex,colIndex,assigner,delta){
  const remaining=edges.filter(p=>!fixedRows.has(p.i)&&!fixedCols.has(p.id)),byRow=new Map(),byCol=new Map();
  for(const p of remaining){if(!byRow.has(p.i))byRow.set(p.i,[]);if(!byCol.has(p.id))byCol.set(p.id,[]);byRow.get(p.i).push(p);byCol.get(p.id).push(p);}
  const visited=new Set(),out=[];let solved=0,rejected=0;
  for(const start of [...byRow.keys()].sort((a,b)=>a-b)){
    if(visited.has(start))continue;const rows=new Set(),cols=new Set(),queue=[start];
    while(queue.length){const i=queue.pop();if(rows.has(i))continue;rows.add(i);visited.add(i);for(const p of byRow.get(i)??[]){if(cols.has(p.id))continue;cols.add(p.id);for(const q of byCol.get(p.id)??[])if(!rows.has(q.i))queue.push(q.i);}}
    if(rows.size>TRACK_B_POLICY.maxComponentSize||cols.size>TRACK_B_POLICY.maxComponentSize)continue;
    const subset=[...rows].flatMap(i=>byRow.get(i));
    const result=trackBSolveB({...input,pairs:subset,ambiguityDeltaCost:delta},assigner);solved++;
    if(result.pairs.some(p=>parentMap.get(rowIndex.get(p.i))!==colIndex.get(p.id))){rejected++;continue;}
    out.push(...result.pairs);
  }
  return {pairs:out,solved,rejected};
}
function trackBTraceB(event){
  if(!TRACK_B_DIAG.enabled)return;
  try{
    const out={serial:++TRACK_B_DIAG.serial};
    for(const k of ['route','observerShip','timeS','tick','decision','reason','trackId','plotIndex','mountId','nis','gate','distanceM','distanceGateM','radialInnovationMps','radialGateMps','measurementDimensions','active','sequential','commonEpoch','knownOwnLaunch','nativeTrackId','proposedTrackId','legacyCount','proposedCount','heldCount','mode','stabilizationMode','plotCount','trackCount','certifiedCount','evidenceResolved','lowerBoundCertifiedCount','exactResidualCertifiedCount','residualComponentsSolved','residualRefinementRejected'])if(['string','number','boolean'].includes(typeof event[k])&&(typeof event[k]!=='number'||Number.isFinite(event[k])))out[k]=event[k];
    TRACK_B_DIAG.records.push(out);if(TRACK_B_DIAG.records.length>TRACK_B_DIAG.capacity){TRACK_B_DIAG.records.shift();TRACK_B_DIAG.dropped++;}
  }catch(_){TRACK_B_DIAG.errors++;}
}
function trackBSelectB(input){
  // Preserve the original compile-time API contract for legacy test/build
  // consumers. New stabilization products pin IMPLEMENTATION_MODE=ACTIVE;
  // their separate STABILIZATION_MODE controls B-vs-candidate consumption.
  if(TRACK_B_IMPLEMENTATION_MODE!=='ACTIVE'){
    const proposal=trackBSolveB(input,bridgeMasterEMinCostAssignmentV35),legacy=Array.isArray(input.legacyPairs)?input.legacyPairs.map(trackBPairCopyB):trackBLegacyGreedyB(input.pairs??[]);
    return {...proposal,active:false,pairs:legacy,heldPlots:new Set(),heldTracks:new Set(),stabilizationActive:false};
  }
  const proposal=trackBSolveB(input,bridgeMasterEMinCostAssignmentV35),candidateActive=TRACK_B_STABILIZATION_MODE==='ACTIVE';
  const prior=(!candidateActive||TRACK_B_DIAG.enabled)?trackBLegacySolveStableB(input,bridgeMasterEMinCostAssignmentV35):null;
  const selected=candidateActive?proposal:prior;
  if(TRACK_B_DIAG.enabled){
    const native=new Map(prior.pairs.map(p=>[p.i,p.id])),next=new Map(proposal.pairs.map(p=>[p.i,p.id]));
    const context={route:input.route,observerShip:input.observerShip,timeS:input.timeS,tick:input.tick,active:true,mode:TRACK_B_IMPLEMENTATION_MODE,stabilizationMode:TRACK_B_STABILIZATION_MODE};
    trackBTraceB({...context,decision:'BATCH',legacyCount:prior.pairs.length,proposedCount:proposal.pairs.length,heldCount:proposal.heldPlots.size,reason:'FROZEN_B_VS_STABILIZATION'});
    for(const p of proposal.rejected)trackBTraceB({...context,plotIndex:p.i,trackId:p.id,nis:p.nis,gate:input.gate,...p.sanity,decision:'SANITY_REJECT',reason:p.sanity.reason});
    for(const c of proposal.components)trackBTraceB({...context,decision:'COMPONENT',reason:c.reason??'RESOLVED',plotCount:c.plots.length,trackCount:c.tracks.length,certifiedCount:c.certifiedCount??0,evidenceResolved:c.evidenceResolved===true,lowerBoundCertifiedCount:c.lowerBoundCertifiedCount,exactResidualCertifiedCount:c.exactResidualCertifiedCount,residualComponentsSolved:c.residualComponentsSolved,residualRefinementRejected:c.residualRefinementRejected});
    for(const i of new Set([...native.keys(),...next.keys(),...proposal.heldPlots]))trackBTraceB({...context,plotIndex:i,nativeTrackId:native.get(i),proposedTrackId:next.get(i),decision:proposal.heldPlots.has(i)?'HOLD':next.has(i)?'ASSIGN':'UNASSIGNED',reason:proposal.heldPlots.has(i)?'AMBIGUOUS_ASSOCIATION':native.get(i)===next.get(i)?'SAME_ASSIGNMENT':'ASSIGNMENT_CHANGED'});
  }
  return {...selected,active:true,stabilizationActive:candidateActive};
}
window.__TRACK_B__=Object.freeze({
  schema:'AEGIS_ASSOCIATION_TRACK_B_1',mode:TRACK_B_IMPLEMENTATION_MODE,policy:TRACK_B_POLICY,stabilizationMode:TRACK_B_STABILIZATION_MODE,stabilizationPolicy:TRACK_B_STABLE_POLICY,
  solve:trackBSolveB,legacySolve:trackBLegacySolveStableB,evidence:trackBEvidenceStableB,geometry:trackBGeometryB,
  configure(options={}){if(typeof options.enabled==='boolean')TRACK_B_DIAG.enabled=options.enabled;if(Number.isInteger(options.capacity))TRACK_B_DIAG.capacity=Math.max(TRACK_B_POLICY.minTraceCapacity,Math.min(TRACK_B_POLICY.maxTraceCapacity,options.capacity));while(TRACK_B_DIAG.records.length>TRACK_B_DIAG.capacity){TRACK_B_DIAG.records.shift();TRACK_B_DIAG.dropped++;}return {enabled:TRACK_B_DIAG.enabled,capacity:TRACK_B_DIAG.capacity};},
  clear(){TRACK_B_DIAG.records.length=0;TRACK_B_DIAG.serial=TRACK_B_DIAG.dropped=TRACK_B_DIAG.errors=0;},
  snapshot(){return {schema:'AEGIS_ASSOCIATION_TRACK_B_1',mode:TRACK_B_IMPLEMENTATION_MODE,stabilizationMode:TRACK_B_STABILIZATION_MODE,enabled:TRACK_B_DIAG.enabled,capacity:TRACK_B_DIAG.capacity,records:TRACK_B_DIAG.records.map(r=>({...r})),stats:{recorded:TRACK_B_DIAG.serial,retained:TRACK_B_DIAG.records.length,dropped:TRACK_B_DIAG.dropped,errors:TRACK_B_DIAG.errors}};}
});
