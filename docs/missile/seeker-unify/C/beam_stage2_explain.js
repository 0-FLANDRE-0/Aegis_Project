// SEEKER_UNIFY_C Stage-2 test-only numeric beam/LOS explanation probe.
// It observes the real measurement function and never feeds data back into the
// tactical path. Debug source tags are used only to select the ownship echo.
(() => {
  function summarize(rows){
    const quant=(values,q)=>{if(!values.length)return null;const a=values.slice().sort((x,y)=>x-y);return a[Math.min(a.length-1,Math.floor((a.length-1)*q))];};
    return {attempts:rows.length,detections:rows.filter(q=>q.detected).length,
      rangeKm:{min:quant(rows.map(q=>q.rangeKm),0),median:quant(rows.map(q=>q.rangeKm),.5),max:quant(rows.map(q=>q.rangeKm),1)},
      beamNorm:{azP50:quant(rows.map(q=>q.azNorm),.5),azP90:quant(rows.map(q=>q.azNorm),.9),elP50:quant(rows.map(q=>q.elNorm),.5),elP90:quant(rows.map(q=>q.elNorm),.9)},
      offGain:{min:quant(rows.map(q=>q.offGain),0),median:quant(rows.map(q=>q.offGain),.5),max:quant(rows.map(q=>q.offGain),1)},
      los:{min:quant(rows.map(q=>q.los),0),median:quant(rows.map(q=>q.los),.5),max:quant(rows.map(q=>q.los),1)},
      addedFactor:{min:quant(rows.map(q=>q.addedFactor),0),median:quant(rows.map(q=>q.addedFactor),.5),p90:quant(rows.map(q=>q.addedFactor),.9),max:quant(rows.map(q=>q.addedFactor),1)},
      cleanSnr:{stage1Median:quant(rows.map(q=>q.stage1CleanSnr),.5),stage2Median:quant(rows.map(q=>q.stage2CleanSnr),.5),stage1P90:quant(rows.map(q=>q.stage1CleanSnr),.9),stage2P90:quant(rows.map(q=>q.stage2CleanSnr),.9)}};
  }
  function runOne(job){
    const attempts=[],original=asmSeekerEchoMeasurement;
    asmSeekerEchoMeasurement=function(em,s,p,src){
      const g=src._g??asmSeekerReturnGeometry(em,src),rKm=g.rangeM/1000;
      // AFTER_ACTION_DIAGNOSTIC_ONLY: the synthetic stationary DDG range case
      // is merged with a sea cell before this hook and its raw member carries
      // no debug kind.  Select that composite only by the diagnostic's known
      // range and a deliberately broad ship-scale RCS floor.  Neither value is
      // returned to, or consumed by, the product seeker.
      const expectedRangeKm=Number(job?.setup?.rangeKm);
      const anonymousDiagnosticMember=src?._debugMembers?.some(member=>member==null)===true;
      const rangeComposite=src?._debugKind==='COMPOSITE'&&anonymousDiagnosticMember&&Number.isFinite(expectedRangeKm)
        &&Math.abs(rKm-expectedRangeKm)<=Math.max(2,expectedRangeKm*.05)&&(Number(src?.rcs)||0)>50;
      const ship=src?._debugKind==='SHIP'||src?._debugMembers?.includes('SHIP')||rangeComposite;
      if(!ship)return original.apply(this,arguments);
      const az01=clamp(src._offAz/Math.max(src._halfAz,1e-6),0,1),el01=clamp(src._offEl/Math.max(src._halfEl,1e-6),0,1);
      const offGain=Math.max(.08,Math.cos(az01*Math.PI/2)**2*Math.cos(el01*Math.PI/2)**2),los=Math.max(0,src._losQ??1);
      const lowAlt=clamp(((src.z??0)+8)/45,0,1),clutter=src._debugKind==='SEA_CLUTTER'?1:lerp(.88,1,lowAlt);
      const weather=maritimeRfWeatherPathFactorWip13A3('IJ',2*rKm),base=(src.rcs/p.refRcsM2)*Math.pow(p.snrRefKm/Math.max(.5,rKm),4)*clutter*weather;
      const stage1=base*offGain*los,stage2=stage1*offGain*los,out=original.apply(this,arguments);
      attempts.push({timeS:Number(em.life)||0,mode:s.mode,rangeKm:rKm,azNorm:az01,elNorm:el01,offGain,los,addedFactor:offGain*los,stage1CleanSnr:stage1,stage2CleanSnr:stage2,detected:!!out});
      return out;
    };
    let result;
    try{result=job.kind==='range'?__SEEKER_UNIFY_A_DIAG__.runRangeCase(job.setup):__SEEKER_UNIFY_B_DIAG__.runCueCase(job.setup);}
    finally{asmSeekerEchoMeasurement=original;}
    const byMode={};for(const mode of [...new Set(attempts.map(q=>q.mode))])byMode[mode]=summarize(attempts.filter(q=>q.mode===mode));
    return {kind:job.kind,setup:job.setup,result,summary:summarize(attempts),byMode,firstTen:attempts.slice(0,10)};
  }
  window.__SEEKER_UNIFY_C_BEAM_EXPLAIN__=Object.freeze({schema:'AEGIS_SEEKER_UNIFY_C_BEAM_EXPLAIN_DIAGNOSTIC_1',run:jobs=>jobs.map(runOne)});
})();
