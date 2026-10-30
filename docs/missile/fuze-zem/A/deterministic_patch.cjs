// Frozen before deterministic-candidate flight tests. All numeric values below
// are SIM_TUNED normalized receiver assumptions, not published fuze specs.
const SPEC=`const SAM_FUZE_SIGNAL_SPEC_A=Object.freeze({
    provenance:'SIM_TUNED',referenceSnrAtGate:1,minSnr:1,maxExcessSnr:32,
    integrationExcessSnrSeconds:.004,coherentLookS:.0005,minValidS:.001,
    rangeCellM:2,clutterNoiseRatio:1,memoryDecayS:.008,resetGapS:.050,
    quadratureStepS:.00025,maxQuadratureSegments:4096
  });`;
const HELPERS=`function samFuzeSignalAppliesA(m){return !!m&&m.guidanceCore==='v1'&&['SM2MR_BLKIIIA_SIM','SM2ER_BLKIV_SIM','SM6_BLKIA_SIM','ESSM_BLK2_SIM'].includes(m._v1Profile?.id);}
  function samFuzeSignalBeginA(m,dt){
    if(!samFuzeSignalAppliesA(m))return;
    const f=m._fuzeSignalFrameA||(m._fuzeSignalFrameA={});
    f.startS=Number(m.life)||0;f.dtS=Math.max(0,Number(dt)||0);f.heading=Number(m.heading)||0;f.pitch=Number(m.pitch)||0;
  }
  function samFuzeSignalPowerA(m,target,rel,vel,body,rcsOverride=null){
    const p=_wip143FuzeParamsForMissile(m),spec=SAM_FUZE_SIGNAL_SPEC_A,r=Math.max(.25,Math.hypot(rel.x,rel.y,rel.z));
    const beam=_wip99TddBeamInfo(body,rel.x,rel.y,rel.z),radius=_wip143FuzeDetectRadiusM(m);
    const rcs=Number.isFinite(rcsOverride)?Math.max(0,rcsOverride):(target?.label!=null?getASMRcs(target,(target.x??0)+metersToWorld(rel.x),(target.y??0)+metersToWorld(rel.y),(target.z??0)+rel.z):targetRcsM2(target,(target.x??0)+metersToWorld(rel.x),(target.y??0)+metersToWorld(rel.y)));
    const rcsRef=Math.max(.005,Number(p.detectionReliability.rcsRefM2)||.3);
    const radialMps=(rel.x*vel.x+rel.y*vel.y+rel.z*vel.z)/r;
    // Linear RCS, inverse-fourth-power range; no Pd/exponent-to-threshold reuse.
    // Range migration during a coherent look degrades receiver coherence.
    const migrationM=Math.abs(radialMps)*spec.coherentLookS;
    const coherence=1/Math.sqrt(1+(migrationM/spec.rangeCellM)**2);
    const c=p.seaClutter,mz=Math.max(0,Number(m.z)||0),tz=Math.max(0,Number(target?.z)||0);
    const low=c.enabled&&tz<=c.targetMaxAltM&&mz<=c.missileMaxAltM&&r<=radius*Math.max(1,Number(c.activeRangeMultiplier)||1)?clamp((c.missileMaxAltM-mz)/Math.max(1,c.missileMaxAltM-c.fullEffectAltM),0,1):0;
    const rough=clamp((seaStateFactor-c.seaStateMin)/Math.max(.01,c.seaStateMax-c.seaStateMin),0,1);
    const horizontal=Math.hypot(rel.x,rel.y),grazingQ=horizontal/r;
    const clutterToNoise=spec.clutterNoiseRatio*low*(.45+.55*rough)*grazingQ;
    const rawSnr=spec.referenceSnrAtGate*(rcs/rcsRef)*(radius/r)**4*coherence/(1+clutterToNoise);
    const inBeam=!p.tddBeam.enabled||beam.covered;
    const snr=r<=radius&&inBeam?rawSnr:0;
    return {snr,rawSnr,rcsM2:rcs,rangeM:r,radialMps,coherence,clutterToNoise,beam,inBeam};
  }
  function samFuzeSignalSweepA(m,target,rel,vel,context,rcsOverride=null){
    const spec=SAM_FUZE_SIGNAL_SPEC_A,p=_wip143FuzeParamsForMissile(m),now=context.endS,start=context.startS,ref=context.referenceS;
    const body={_v1Profile:m._v1Profile,isESSM:m.isESSM,isRAM:m.isRAM,heading:m.heading??0,pitch:m.pitch??0};
    let channels=m._fuzeSignalChannelsA;if(!channels)channels=m._fuzeSignalChannelsA=new WeakMap();
    let s=channels.get(target);if(!s||now<s.cursorS){s={cursorS:start,energy:0,continuousS:0,detectedAtS:null,lastValidS:null};channels.set(target,s);}
    const before=s.energy;let exposureS=0,beamSeen=false,peakSnr=0,firstSignalS=null;
    const pose=(at)=>{
      const frame=m._fuzeSignalFrameA;
      if(frame&&context.bodyFrame!==false&&frame.dtS>0){const u=clamp((at-frame.startS)/frame.dtS,0,1);body.heading=frame.heading+angNorm((m.heading??frame.heading)-frame.heading)*u;body.pitch=lerp(frame.pitch,m.pitch??frame.pitch,u);}
      else{body.heading=m.heading??0;body.pitch=m.pitch??0;}
    };
    const sample=(at)=>{pose(at);const d=at-ref;return samFuzeSignalPowerA(m,target,{x:rel.x+vel.x*d,y:rel.y+vel.y*d,z:rel.z+vel.z*d},vel,body,rcsOverride);};
    const decay=(dt)=>{if(!(dt>0))return;s.energy*=Math.exp(-dt/spec.memoryDecayS);s.continuousS=0;if(s.lastValidS!=null&&s.cursorS+dt-s.lastValidS>=spec.resetGapS){s.energy=0;}};
    let a=Math.max(start,s.cursorS),b=now;
    if(start>s.cursorS){decay(start-s.cursorS);s.cursorS=start;}
    if(!context.armed){decay(Math.max(0,b-s.cursorS));s.cursorS=b;return {allow:false,reason:'not-armed',beam:{covered:false},detection:{model:'SAM_SIGNAL_A',detected:false,energy:s.energy}};}
    // Clip the same SI relative line r(t)=r_ref+v_rel*(t-reference) used by CPA.
    // Only elapsed exposure is integrated. Future [+dt] CPA is never credited.
    const radius=_wip143FuzeDetectRadiusM(m),vv=vel.x*vel.x+vel.y*vel.y+vel.z*vel.z;
    let lo=a,hi=b;
    if(vv>1e-12){const pv=rel.x*vel.x+rel.y*vel.y+rel.z*vel.z,rr=rel.x*rel.x+rel.y*rel.y+rel.z*rel.z,disc=pv*pv-vv*(rr-radius*radius);
      if(disc<0){lo=hi=b;}else{const root=Math.sqrt(Math.max(0,disc));lo=Math.max(a,ref+(-pv-root)/vv);hi=Math.min(b,ref+(-pv+root)/vv);if(hi<lo)lo=hi=b;}}
    else if(Math.hypot(rel.x,rel.y,rel.z)>radius)lo=hi=b;
    if(s.detectedAtS==null&&b>a){
      decay(Math.max(0,lo-a));s.cursorS=lo;
      const step=Math.max(spec.quadratureStepS,Math.max(0,hi-lo)/spec.maxQuadratureSegments);
      while(s.cursorS<hi-1e-12){
        const c=s.cursorS,grid=(Math.floor((c+1e-10)/step)+1)*step,e=Math.min(hi,Math.max(c+1e-12,grid)),dt=e-c,q=sample((c+e)/2);
        beamSeen=beamSeen||q.inBeam;peakSnr=Math.max(peakSnr,q.snr);
        if(q.snr>=spec.minSnr){
          if(firstSignalS==null)firstSignalS=c;
          const rate=Math.min(spec.maxExcessSnr,Math.max(0,q.snr-spec.minSnr));
          const needEnergy=rate>0?Math.max(0,spec.integrationExcessSnrSeconds-s.energy)/rate:Infinity;
          const needTime=Math.max(0,spec.minValidS-s.continuousS),cross=Math.max(needEnergy,needTime);
          exposureS+=dt;s.lastValidS=e;
          if(cross<=dt+1e-12){s.detectedAtS=c+Math.max(0,cross);s.energy+=rate*Math.max(0,cross);s.continuousS+=Math.max(0,cross);s.cursorS=e;break;}
          s.energy+=rate*dt;s.continuousS+=dt;
        }else decay(dt);
        s.cursorS=e;
      }
      if(s.detectedAtS==null){decay(Math.max(0,b-s.cursorS));s.cursorS=b;}
    }
    const instant=sample(now),detected=Number.isFinite(s.detectedAtS);
    s.cursorS=Math.max(s.cursorS,now);
    const reason=detected?null:!(hi>lo)?'range-out':!beamSeen?'beam-out':peakSnr<spec.minSnr?'signal-below-noise':s.continuousS<spec.minValidS?'signal-too-brief':'signal-integration-incomplete';
    const detection={model:'SAM_SIGNAL_A',detected,detectedAtS:s.detectedAtS,instantSnr:instant.snr,peakSnr,rcsM2:instant.rcsM2,radialMps:instant.radialMps,coherence:instant.coherence,clutterToNoise:instant.clutterToNoise,energyBefore:before,energy:s.energy,requiredEnergy:spec.integrationExcessSnrSeconds,continuousValidS:s.continuousS,requiredValidS:spec.minValidS,validExposureThisStepS:exposureS,firstSignalThisStepS:firstSignalS,intervalStartS:a,intervalEndS:b,quadratureStepS:spec.quadratureStepS};
    m._fuzeSignalLastA=detection;
    return {allow:detected,reason,beam:{...instant.beam,covered:beamSeen||(instant.inBeam&&instant.rangeM<=radius)},detection};
  }`;
function definitions(symbols){
 let body=symbols.get('updateMissileBodyB3').code;
 body=body.replace('    m.life += dt;','    samFuzeSignalBeginA(m,dt);\n    m.life += dt;');
 const old="if(_stage2SenseEnabled && m.proxArmed && dkm*1000 < fuzeDetectM){\n        const _sense=_wip99Stage2CandidateDecision(m,killTarget,relXm,relYm,relZm,dotPV);";
 const replacement="if(_stage2SenseEnabled && m.proxArmed && effDkm*1000 < fuzeDetectM){\n        const _sense=samFuzeSignalAppliesA(m)?samFuzeSignalSweepA(m,killTarget,{x:relXm,y:relYm,z:relZm},{x:relVxMps,y:relVyMps,z:relVzMps},{startS:m.life-dt,endS:m.life,referenceS:m.life,armed:m.proxArmed}):_wip99Stage2CandidateDecision(m,killTarget,relXm,relYm,relZm,dotPV);";
 if(!body.includes(old))throw Error('SAM_SENSE_CALL_MISSING');body=body.replace(old,replacement);
 body=body.replace("m._fuzeStage2LastRejectReason=m._fuzeStage2BeamSeen?'detection-failed':'beam-out';","m._fuzeStage2LastRejectReason=m._fuzeStage2LastDecision?.detection?.model==='SAM_SIGNAL_A'?m._fuzeStage2LastDecision.reason:(m._fuzeStage2BeamSeen?'detection-failed':'beam-out');");
 let surface=symbols.get('surfaceMissileSweptContactWip13C5').code;
 const call='const detection=_wip99Stage2CandidateDecision(m,entity,rel.x,rel.y,rel.z,dotPV,rcsM2);';
 const repl=`const senseStartS=simStepCounter*SIM_FIXED_DT+sensed.t*SIM_FIXED_DT,senseEndS=(simStepCounter+1)*SIM_FIXED_DT;
      const detection=samFuzeSignalAppliesA(m)?samFuzeSignalSweepA(m,entity,rel,relativeVelocity,{startS:senseStartS,endS:senseEndS,referenceS:senseStartS,armed:m._surfaceFuzeArmedWip13C22,bodyFrame:false},rcsM2):_wip99Stage2CandidateDecision(m,entity,rel.x,rel.y,rel.z,dotPV,rcsM2);`;
 if(!surface.includes(call))throw Error('SURFACE_SENSE_CALL_MISSING');surface=surface.replace(call,repl);
 surface=surface.replace('atS:simStepCounter*SIM_FIXED_DT+sensed.t*SIM_FIXED_DT','atS:Number.isFinite(detection.detection?.detectedAtS)?detection.detection.detectedAtS:simStepCounter*SIM_FIXED_DT+sensed.t*SIM_FIXED_DT');
 return {out:{updateMissileBodyB3:body,surfaceMissileSweptContactWip13C5:surface},constants:[SPEC,HELPERS]};
}
module.exports={definitions,SPEC,HELPERS};
