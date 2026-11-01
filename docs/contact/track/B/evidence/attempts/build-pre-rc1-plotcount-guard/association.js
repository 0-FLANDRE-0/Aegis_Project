// TRACK-B association policy only. No RF/EKF/IFF/authority/weapon coefficients.
// Geometry reads anonymous measurements and receiver-owned filter estimates.
const TRACK_B_IMPLEMENTATION_MODE='ACTIVE'; // Build-time ACTIVE or SHADOW; never a UI/diagnostic switch.
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
function trackBSolveB(input,assigner){
  const gate=input.gate,plotCount=input.plotCount,ambiguityDelta=trackBFiniteB(input.ambiguityDeltaCost)&&input.ambiguityDeltaCost>=0?input.ambiguityDeltaCost:TRACK_B_POLICY.ambiguityDeltaNis;
  if(!trackBFiniteB(gate)||gate<=0||!Number.isInteger(plotCount)||plotCount<0||plotCount>256)throw new Error('TRACK_B_INVALID_GRAPH');
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
function trackBTraceB(event){
  if(!TRACK_B_DIAG.enabled)return;
  try{
    const out={serial:++TRACK_B_DIAG.serial};
    for(const k of ['route','observerShip','timeS','tick','decision','reason','trackId','plotIndex','mountId','nis','gate','distanceM','distanceGateM','radialInnovationMps','radialGateMps','measurementDimensions','active','sequential','commonEpoch','knownOwnLaunch','nativeTrackId','proposedTrackId','legacyCount','proposedCount','heldCount','mode'])if(['string','number','boolean'].includes(typeof event[k])&&(typeof event[k]!=='number'||Number.isFinite(event[k])))out[k]=event[k];
    TRACK_B_DIAG.records.push(out);if(TRACK_B_DIAG.records.length>TRACK_B_DIAG.capacity){TRACK_B_DIAG.records.shift();TRACK_B_DIAG.dropped++;}
  }catch(_){TRACK_B_DIAG.errors++;}
}
function trackBSelectB(input){
  const proposal=trackBSolveB(input,bridgeMasterEMinCostAssignmentV35),active=TRACK_B_IMPLEMENTATION_MODE==='ACTIVE',needsLegacy=!active||TRACK_B_DIAG.enabled,legacy=needsLegacy?(Array.isArray(input.legacyPairs)?input.legacyPairs.map(trackBPairCopyB):trackBLegacyGreedyB(input.pairs??[])):[];
  if(TRACK_B_DIAG.enabled){
    const native=new Map(legacy.map(p=>[p.i,p.id])),next=new Map(proposal.pairs.map(p=>[p.i,p.id]));
    const context={route:input.route,observerShip:input.observerShip,timeS:input.timeS,tick:input.tick,active,mode:TRACK_B_IMPLEMENTATION_MODE};
    trackBTraceB({...context,decision:'BATCH',legacyCount:legacy.length,proposedCount:proposal.pairs.length,heldCount:proposal.heldPlots.size,reason:'PRECOMPUTED_NATIVE_CANDIDATES'});
    for(const p of proposal.rejected)trackBTraceB({...context,plotIndex:p.i,trackId:p.id,nis:p.nis,gate:input.gate,...p.sanity,decision:'SANITY_REJECT',reason:p.sanity.reason});
    for(const i of new Set([...native.keys(),...next.keys(),...proposal.heldPlots]))trackBTraceB({...context,plotIndex:i,nativeTrackId:native.get(i),proposedTrackId:next.get(i),decision:proposal.heldPlots.has(i)?'HOLD':next.has(i)?'ASSIGN':'UNASSIGNED',reason:proposal.heldPlots.has(i)?'AMBIGUOUS_ASSOCIATION':native.get(i)===next.get(i)?'SAME_ASSIGNMENT':'ASSIGNMENT_CHANGED'});
  }
  return {...proposal,active,pairs:active?proposal.pairs:legacy,heldPlots:active?proposal.heldPlots:new Set(),heldTracks:active?proposal.heldTracks:new Set()};
}
window.__TRACK_B__=Object.freeze({
  schema:'AEGIS_ASSOCIATION_TRACK_B_1',mode:TRACK_B_IMPLEMENTATION_MODE,policy:TRACK_B_POLICY,
  solve:trackBSolveB,geometry:trackBGeometryB,
  configure(options={}){if(typeof options.enabled==='boolean')TRACK_B_DIAG.enabled=options.enabled;if(Number.isInteger(options.capacity))TRACK_B_DIAG.capacity=Math.max(TRACK_B_POLICY.minTraceCapacity,Math.min(TRACK_B_POLICY.maxTraceCapacity,options.capacity));while(TRACK_B_DIAG.records.length>TRACK_B_DIAG.capacity){TRACK_B_DIAG.records.shift();TRACK_B_DIAG.dropped++;}return {enabled:TRACK_B_DIAG.enabled,capacity:TRACK_B_DIAG.capacity};},
  clear(){TRACK_B_DIAG.records.length=0;TRACK_B_DIAG.serial=TRACK_B_DIAG.dropped=TRACK_B_DIAG.errors=0;},
  snapshot(){return {schema:'AEGIS_ASSOCIATION_TRACK_B_1',mode:TRACK_B_IMPLEMENTATION_MODE,enabled:TRACK_B_DIAG.enabled,capacity:TRACK_B_DIAG.capacity,records:TRACK_B_DIAG.records.map(r=>({...r})),stats:{recorded:TRACK_B_DIAG.serial,retained:TRACK_B_DIAG.records.length,dropped:TRACK_B_DIAG.dropped,errors:TRACK_B_DIAG.errors}};}
});
