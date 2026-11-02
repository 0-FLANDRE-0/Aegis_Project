  function c55AssociateCms(rec,rows){
    const s=rec.st,rank=[];
    for(const q of rows){const c=q.state,dist=Math.hypot(s.rxM-c.rxM,s.ryM-c.ryM,s.rzM-c.rzM),gate=clamp(q.sigmaM*3+60,90,650);
      if(dist>gate)continue;
      const dv=Math.hypot(s.rvxMps-c.rvxMps,s.rvyMps-c.rvyMps,s.rvzMps-c.rvzMps);
      if(s.localHits>8&&dv>300)continue;rank.push({q,dist});
    }
    rank.sort((a,b)=>a.dist-b.dist);const matched=rank[0]?.q;
    // A nearby protected observed file vetoes release conservatively. It is not
    // obtained by resolving a track's hidden world/truth identity.
    const protectedRow=rank.find(r=>CIWS_C55_POLICY.protectedIdentities.includes(r.q.identity));
    rec.cmsTrackId=matched?.trackId??null;rec.hasCue=!!matched?.cueEligible;
    if(protectedRow)rec.protectedIdentity=protectedRow.q.identity;
    else if(matched&&rec.protectedCmsId===matched.trackId)rec.protectedIdentity=null;
    if(protectedRow)rec.protectedCmsId=protectedRow.q.trackId;
    if(rec.ownFireEvidence)rec.protectedIdentity='FRIEND';
    rec.cmsIdentity=matched?.identity??'UNKNOWN';
  }
