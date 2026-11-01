// TRACK-B C55 diagnostics only. Native RF order, local files and weapons stay live.
// No physical source key, proxy ID, label/faction, or true source velocity enters.
function trackBC55BeginB(bank){
  return {files:[...bank.files.values()].map(r=>({id:r.id,rxM:r.st.rxM,ryM:r.st.ryM,rzM:r.st.rzM,localHits:r.st.localHits,localAgeS:r.st.localAgeS,knownOwn:!!r.ownFireEvidence})),plots:[],accepted:0,overflow:0};
}
function trackBC55CaptureB(batch,meas,knownOwn,seen){
  batch.accepted++;
  // Independent diagnostic capture bound; never limits the native RF sweep.
  if(batch.plots.length>=256){batch.overflow++;return null;}
  const plot={i:batch.plots.length,rxM:meas.rxM,ryM:meas.ryM,rzM:meas.rzM,rangeM:meas.rangeM,knownOwn:!!knownOwn,nativeTrackId:null,nativeSeenBefore:new Set(seen),nativeCandidates:[]};
  batch.plots.push(plot);return plot;
}
function trackBC55AnalyzeB(batch,cfg,context,assigner){
  if(!TRACK_B_DIAG.enabled)return;
  try{
    const cx={...context,route:'C55_SHADOW',active:false,mode:'SHADOW_DISTANCE_ONLY',measurementDimensions:3,sequential:true,commonEpoch:true};
    if(batch.overflow){trackBTraceB({...cx,decision:'LIMIT',reason:'C55_SHADOW_MEASUREMENT_LIMIT',legacyCount:batch.accepted,proposedCount:batch.plots.length});return;}
    const pairs=[],existingIds=new Set(batch.files.map(f=>f.id));let maxGate=CIWS_C55_POLICY.associationBaseM;
    for(const p of batch.plots){
      if(![p.rxM,p.ryM,p.rzM,p.rangeM].every(trackBFiniteB)){trackBTraceB({...cx,plotIndex:p.i,knownOwnLaunch:p.knownOwn,decision:'REJECT',reason:'SHADOW_INVALID_MEASUREMENT'});continue;}
      for(const f of batch.files){
        if(f.knownOwn!==p.knownOwn){trackBTraceB({...cx,plotIndex:p.i,trackId:f.id,knownOwnLaunch:p.knownOwn,decision:'REJECT',reason:'NATIVE_OWN_FIRE_PARTITION'});continue;}
        const distanceM=Math.hypot(f.rxM-p.rxM,f.ryM-p.ryM,f.rzM-p.rzM),gate=CIWS_C55_POLICY.associationBaseM+p.rangeM*deg(cfg.searchAzSigmaDeg)*3+(f.localHits<5?2200:350)*Math.min(.35,f.localAgeS);
        if(![distanceM,gate].every(trackBFiniteB)||gate<=0){trackBTraceB({...cx,plotIndex:p.i,trackId:f.id,knownOwnLaunch:p.knownOwn,decision:'REJECT',reason:'SHADOW_INVALID_FILE_GEOMETRY'});continue;}
        maxGate=Math.max(maxGate,gate);
        const native=p.nativeCandidates.find(q=>q.id===f.id),seen=p.nativeSeenBefore.has(f.id);
        const reason=seen?'SHADOW_COUNTERFACTUAL_NATIVE_SEEN':native?(native.distanceM===distanceM&&native.gate===gate?'NATIVE_EVALUATED_DISTANCE':'SHADOW_NATIVE_GEOMETRY_MISMATCH'):'SHADOW_NOT_NATIVE_EVALUATED';
        trackBTraceB({...cx,plotIndex:p.i,trackId:f.id,knownOwnLaunch:p.knownOwn,distanceM,distanceGateM:gate,decision:distanceM<gate?'ELIGIBLE':'REJECT',reason});
        // `nis` is the shared solver's generic numeric-cost ABI, not an RF NIS.
        // Trace exposes only distanceM/distanceGateM; no C55 `nis` is published.
        if(distanceM<gate)pairs.push({i:p.i,id:f.id,nis:distanceM,nativeGateM:gate});
      }
    }
    const proposal=trackBSolveB({plotCount:batch.plots.length,pairs,gate:maxGate,costUnits:'m',ambiguityDeltaCost:0},assigner),next=new Map(proposal.pairs.map(p=>[p.i,p.id]));
    const legacyCount=batch.plots.filter(p=>existingIds.has(p.nativeTrackId)).length;
    trackBTraceB({...cx,decision:'BATCH',reason:'C55_COMMON_EPOCH_DISTANCE_SHADOW',legacyCount,proposedCount:proposal.pairs.length,heldCount:proposal.heldPlots.size});
    for(const c of proposal.components){
      const competing=c.edgeCount>c.plots.length||c.edgeCount>c.tracks.length;
      if(competing||c.ambiguous)trackBTraceB({...cx,decision:'COMPONENT',reason:c.ambiguous?'C55_SHARED_SOLVER_AMBIGUOUS':'C55_COMPETING_GEOMETRY',legacyCount:c.plots.length,proposedCount:c.tracks.length,heldCount:c.ambiguous?c.plots.filter(i=>proposal.heldPlots.has(i)).length:0});
    }
    for(const p of batch.plots){
      const isNew=p.nativeTrackId!==null&&!existingIds.has(p.nativeTrackId),held=proposal.heldPlots.has(p.i);
      trackBTraceB({...cx,plotIndex:p.i,knownOwnLaunch:p.knownOwn,nativeTrackId:p.nativeTrackId,proposedTrackId:next.get(p.i),decision:isNew?'NATIVE_NEW_FILE':held?'SHADOW_HOLD':next.has(p.i)?'SHADOW_ASSIGN':'SHADOW_UNASSIGNED',reason:p.nativeTrackId===null?'NATIVE_CAPACITY_NO_NEW_FILE':held?'SHADOW_AMBIGUOUS_NO_LIVE_EFFECT':p.nativeTrackId===next.get(p.i)?'SAME_EXISTING_ASSIGNMENT':'SHADOW_EXISTING_ASSIGNMENT_DIFFERS'});
    }
  }catch(_){TRACK_B_DIAG.errors++;trackBTraceB({...context,route:'C55_SHADOW',active:false,mode:'SHADOW_DISTANCE_ONLY',decision:'DIAGNOSTIC_ERROR',reason:'C55_SHADOW_ANALYSIS_ERROR'});}
}
