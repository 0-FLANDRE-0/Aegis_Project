function c55CmsRows(m){
    const rows=[];
    for(const [id,tr] of tracks){
      if(!tr||tr.sensorDetected===false||!tr.confirmed||tr.memActive||tr.reacquiring||(tr.sensorAge??tr.age??999)>CIWS_C55_POLICY.cueFreshS)continue;
      const c=ciwsTrackStateForTargetB1(id,m);if(!c)continue;
      const kin=ciwsRelativeKinematicsFromState(c.rxM,c.ryM,c.rzM,c.rvxMps,c.rvyMps,c.rvzMps);
      rows.push({trackId:id,state:c,kin,identity:tr.identity??'UNKNOWN',sigmaM:Math.max(15,Number(tr.measurementSigmaM)||100),
        cueEligible:!CIWS_C55_POLICY.protectedIdentities.includes(tr.identity)&&kin.closingMps>50&&trackKinematicThreatCue(tr).missileLike&&kin.rangeM<CIWS_C55_POLICY.searchHintRangeKm*1000});
    }
    return rows;
  }
