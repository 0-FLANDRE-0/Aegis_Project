function c55SensorSweep(m,b,dt){
    const o=ciwsMountStateM(m),seen=new Set(),cfg=CIWS_LOCAL_TRACK_MODEL[m.type];
    const trackBShadow=TRACK_B_DIAG.enabled?trackBC55BeginB(b):null;
    // Range/LOS/RCS/noise are evaluated in this boundary. The combat controller
    // never selects directly from enemyMissiles. Known own-fire is an inventory
    // safety exclusion, not inferred hostile identity from a world class label.
    const sources=navalCiwsSourcesD(owner);
    for(const src of sources){
      const e=src.e,rx=worldToMeters(e.x)-o.xM,ry=worldToMeters(e.y)-o.yM,rz=(e.z??0)-o.zM;
      const cue=b.cues.find(q=>Math.hypot(rx-q.state.rxM,ry-q.state.ryM,rz-q.state.rzM)<clamp(q.sigmaM*4,200,1000));
      const selected=b.files.get(m.trackingTrackId),lock=selected&&CIWS_C55_SENSOR_LINKS.get(selected)?.key===src.key;
      const mode=lock&&m.state!=='IDLE'&&m.state!=='SEARCH'?'TRACK':'SEARCH';
      const meas=ciwsLocalMeasurement(m,e,mode,!!cue,dt,{key:src.key,rcs:src.rcs,random:()=>c55SensorRandom(b),normal:sigma=>c55SensorNormal(b,sigma)});
      if(TRACK_A_DIAG.enabled&&meas?.attempted)trackATraceEventA('RECEIVED',meas,{...trackATraceContextA('CIWS_LOCAL_RF','LOCAL_RF',owner.entityId),route:'C55',appliedModel:'RELATIVE_POSITION_DISTANCE',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'m',mountId:m.id,knownOwnLaunch:!!src.own,decision:meas.accepted?'DETECTED':'NO_DETECTION'});
      if(!meas?.attempted)continue;CIWS_C55.stats.attempted++;if(!meas.accepted)continue;CIWS_C55.stats.accepted++;
      const trackBShadowPlot=trackBShadow?trackBC55CaptureB(trackBShadow,meas,!!src.own,seen):null;
      let best=null,error=Infinity;
      for(const r of b.files.values()){
        if(seen.has(r.id)||!!r.ownFireEvidence!==!!src.own){if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',meas,{...trackATraceContextA('CIWS_LOCAL_RF','LOCAL_RF',owner.entityId),route:'C55',appliedModel:'RELATIVE_POSITION_DISTANCE',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'m',mountId:m.id,trackId:r.id,knownOwnLaunch:!!src.own,decision:'REJECT',reason:seen.has(r.id)?'NATIVE_ONE_TO_ONE':'NATIVE_OWN_FIRE_PARTITION'});continue;}const s=r.st,d=Math.hypot(s.rxM-meas.rxM,s.ryM-meas.ryM,s.rzM-meas.rzM);
        const gate=CIWS_C55_POLICY.associationBaseM+meas.rangeM*deg(cfg.searchAzSigmaDeg)*3+(s.localHits<5?2200:350)*Math.min(.35,s.localAgeS);
        if(TRACK_A_DIAG.enabled)trackATraceEventA('CANDIDATE',meas,{...trackATraceContextA('CIWS_LOCAL_RF','LOCAL_RF',owner.entityId),route:'C55',appliedModel:'RELATIVE_POSITION_DISTANCE',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'m',mountId:m.id,trackId:r.id,distanceM:d,gate,knownOwnLaunch:!!src.own,decision:d<gate?'ELIGIBLE':'REJECT',reason:'NATIVE_DISTANCE_GATE'});
        if(trackBShadowPlot)trackBShadowPlot.nativeCandidates.push({id:r.id,distanceM:d,gate});
        if(d<gate&&d<error){best=r;error=d;}
      }
      const trackABefore=TRACK_A_DIAG.enabled?trackAStateA(best):null;
      if(!best){if(b.files.size>=CIWS_C55_POLICY.maxFiles)continue;const id=-5500000-(++CIWS_C55.serial);
        best={id,st:c55BlankState(),proxy:{id:e.id,alive:true,_c55Id:id},firstSeenS:CIWS_C55.clockS,confirmed:false,approachS:0,samples:[],cmsTrackId:null,protectedIdentity:null,ownFireEvidence:false};b.files.set(id,best);CIWS_C55.stats.created++;
      }
      seen.add(best.id);CIWS_C55_SENSOR_LINKS.set(best,src);best.proxy.id=e.id;
      best.ownFireEvidence=best.ownFireEvidence||src.own;c55UpdateFile(best,meas,m,mode,dt);
      if(trackBShadowPlot)trackBShadowPlot.nativeTrackId=best.id;
      if(TRACK_A_DIAG.enabled)trackATraceEventA('UPDATE',meas,{...trackATraceContextA('CIWS_LOCAL_RF','LOCAL_RF',owner.entityId),route:'C55',appliedModel:'RELATIVE_POSITION_DISTANCE',appliedDimension:3,appliedFields:['rxM','ryM','rzM'],gateUnits:'m',mountId:m.id,trackId:best.id,knownOwnLaunch:!!src.own,decision:trackABefore?'ACCEPT':'CREATE',finalSource:'LOCAL_RF',before:trackABefore,after:trackAStateA(best)});
    }
    if(trackBShadow)trackBC55AnalyzeB(trackBShadow,cfg,{observerShip:owner.entityId,mountId:m.id,timeS:simStepCounter*SIM_FIXED_DT,tick:simStepCounter},bridgeMasterEMinCostAssignmentV35);
  }
