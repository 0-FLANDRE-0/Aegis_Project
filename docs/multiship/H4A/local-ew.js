// Pure measured-data association. No runtime, sensor source objects or RNG.
function localDefenseTimingFusionH4A(raw,trackSeeds,activeEsm,usedEsm,origin){
  const groups=[];
  const same=(t,q)=>Math.hypot(t.xM-q.xM,t.yM-q.yM,t.zM-q.zM)<Math.max(60,3*Math.hypot(t.positionSigmaM,q.positionSigmaM))&&Math.hypot(t.vxMps-q.vxMps,t.vyMps-q.vyMps,t.vzMps-q.vzMps)<Math.max(30,3*Math.hypot(t.velocitySigmaMps,q.velocitySigmaMps));
  for(const q of raw){
    if(q.ageS<0||q.ageS>=CIWS_C55_POLICY.releaseFreshS)continue;
    if(trackSeeds.some(t=>t.id===q.cmsTrackId))continue;
    const matches=groups.filter(t=>t.mountId!==q.mountId&&same(t,q));
    // Collapse only an unambiguous cross-mount duplicate. Two files from one
    // mount, or many-to-one associations, stay separate and withhold timing.
    const duplicate=matches.length===1&&raw.filter(t=>t.mountId===q.mountId&&same(t,matches[0])).length===1;
    if(!duplicate)groups.push(q);
  }
  const candidates=[];
  for(const es of activeEsm){
    if(usedEsm.has(es.id))continue;
    const rows=[];
    for(const q of groups){
      const bearing=Math.atan2(q.yM-origin.yM,q.xM-origin.xM);
      const bearingSigmaDeg=Math.max(.35,Math.atan2(q.positionSigmaM,Math.max(1,q.rangeM))*180/Math.PI);
      const gateDeg=Math.max(SOFT_KILL_COORD.esmAssocMinGateDeg,(es.c.bearingSigmaDeg??5)*SOFT_KILL_COORD.esmAssocSigmaMult+2+bearingSigmaDeg*3),errDeg=Math.abs(angNorm(es.c.bearing-bearing))*180/Math.PI;
      if(errDeg<=gateDeg)rows.push({q,bearing,bearingSigmaDeg,norm:errDeg/gateDeg});
    }
    // Bearing alone cannot choose between multiple measured local contacts.
    if(rows.length===1)candidates.push({es,...rows[0]});
  }
  const out=[];
  for(const p of candidates){
    if(candidates.filter(t=>t.q===p.q).length!==1)continue;
    const {q,es}=p,c=es.c,activeConf=clamp(.58+.36*(c.strength??0)-.035*(c.age??0),0,1),missileConf=clamp(.72+.28*q.quality,0,1);
    usedEsm.add(es.id);
    out.push({key:`LOCAL_RF_ESM:${es.id}`,source:'LOCAL_RF_ESM_FUSED_H4A',trackId:null,emitterContactId:es.id,
      localId:q.localId,mountId:q.mountId,bearing:p.bearing,bearingSigmaDeg:p.bearingSigmaDeg,
      rangeKm:q.rangeM/1000,rangeSigmaM:q.positionSigmaM,closureMps:q.closingMps,ttcS:q.ttcS,
      missileLikeConfidence:missileConf,activeSeekerConfidence:activeConf,
      threatScore:40*missileConf+20*activeConf+16*clamp(1-q.rangeM/70000,0,1)+10*clamp(q.closingMps/650,0,1)+12*clamp(1-q.ttcS/120,0,1)+5*q.quality,
      freshnessS:Math.max(q.ageS,c.age??0)});
  }
  return out;
}
function localDefenseSelfTestH4A(){
  const q={localId:-5500001,mountId:1,cmsTrackId:null,xM:4000,yM:0,zM:5,vxMps:-280,vyMps:0,vzMps:0,rangeM:4000,closingMps:280,cpaM:0,ttcS:4000/280,positionSigmaM:10,velocitySigmaMps:5,quality:.9,ageS:.01},es={id:'MEASURED_EMITTER',c:{bearing:0,bearingSigmaDeg:1,age:.1,strength:.9}},checks={};
  const run=(raw,esm=[es],seeds=[])=>localDefenseTimingFusionH4A(raw,seeds,esm,new Set(),{xM:0,yM:0});
  checks.uniqueMeasuredTiming=run([q]).length===1&&run([q])[0].rangeKm===4;
  checks.bearingOnlyHasNoRange=run([]).length===0;
  checks.localOnlyHasNoActiveEvidence=run([q],[]).length===0;
  checks.staleLocalWithheld=run([{...q,ageS:CIWS_C55_POLICY.releaseFreshS}]).length===0;
  checks.sameMountAmbiguityWithheld=run([q,{...q,localId:-5500002,xM:4100}]).length===0;
  checks.crossMountDuplicateSingle=run([q,{...q,localId:-5500002,mountId:2}]).length===1;
  checks.crossMountManyToOneWithheld=run([q,{...q,localId:-5500002,xM:4010},{...q,localId:-5500003,mountId:2}]).length===0;
  checks.multipleEmitterAmbiguityWithheld=run([q],[es,{...es,id:'OTHER_EMITTER'}]).length===0;
  checks.cmsSeedNotDuplicated=run([{...q,cmsTrackId:71}],[es],[{id:71}]).length===0;
  checks.unmatchedBearingWithheld=run([q],[{...es,c:{...es.c,bearing:Math.PI}}]).length===0;
  checks.detachedAndNoIdAuthority=run([q])[0].trackId===null&&run([q])[0].source==='LOCAL_RF_ESM_FUSED_H4A';
  return {checks,pass:Object.values(checks).every(Boolean)};
}
