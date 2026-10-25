// ARH_MEASUREMENT_FIX_A: restore the RF_V2 absolute-angle and uncertainty contracts.
// No profile coefficients, detection gates, RNG draws, guidance, propulsion, fuze, or damage code changes.
function patchMeasurement(before,{angle=false,uncertainty=false}={}){
  let after=before;
  if(angle){
    const old=`const dAz=((UR+LR)-(UL+LL))/sum,dEl=((UL+UR)-(LL+LR))/sum,k=clamp(beam/Math.max(deg(.2),squint),1.2,5.0)*.46,gate=deg(p.monopulseAngleGateDeg??4.8);\n    let azErr=clamp(dAz*squint*k,-gate,gate),elErr=clamp(dEl*squint*k,-gate,gate);`;
    const replacement=`const dAz=((UR+LR)-(UL+LL))/sum,dEl=((UL+UR)-(LL+LR))/sum,gate=deg(p.monopulseAngleGateDeg??4.8);\n    // For the Gaussian four-quadrant response above, delta/sigma = tanh(error*squint/beam^2).\n    // Invert that response so the generated measurement and the EKF absolute-angle model share units/meaning.\n    const ratioLimit=1-1e-12,monopulseInverseScale=beam*beam/Math.max(deg(.2),squint);\n    let azErr=clamp(Math.atanh(clamp(dAz,-ratioLimit,ratioLimit))*monopulseInverseScale,-gate,gate),elErr=clamp(Math.atanh(clamp(dEl,-ratioLimit,ratioLimit))*monopulseInverseScale,-gate,gate);`;
    if(after.split(old).length!==2)throw Error('ANGLE_SITE_NOT_UNIQUE');
    after=after.replace(old,replacement);
  }
  if(uncertainty){
    const old=`const snrQ=clamp(sum/Math.max(1e-9,p.monopulseSumMin??.058),0,12),noiseBase=deg(p.monopulseNoiseDeg??.10)/Math.sqrt(.35+snrQ),glint=deg(lerp(p.monopulseGlintDeg??.16,p.monopulseChaffGlintDeg??.74,spreadSeed));\n    azErr+=_arhSeekerRandn(m)*(noiseBase+glint*lerp(.45,1.15,spreadSeed));elErr+=_arhSeekerRandn(m)*(noiseBase+glint*lerp(.45,1.15,spreadSeed));`;
    const replacement=`const snrQ=clamp(sum/Math.max(1e-9,p.monopulseSumMin??.058),0,12),noiseBase=deg(p.monopulseNoiseDeg??.10)/Math.sqrt(.35+snrQ),glint=deg(lerp(p.monopulseGlintDeg??.16,p.monopulseChaffGlintDeg??.74,spreadSeed));\n    // This is the conditional standard deviation actually used by both angular draws.\n    // Report the same quantity downstream; do not apply a fitted global multiplier.\n    const angularNoiseSigmaRad=noiseBase+glint*lerp(.45,1.15,spreadSeed);\n    azErr+=_arhSeekerRandn(m)*angularNoiseSigmaRad;elErr+=_arhSeekerRandn(m)*angularNoiseSigmaRad;`;
    if(after.split(old).length!==2)throw Error('NOISE_SITE_NOT_UNIQUE');
    after=after.replace(old,replacement);
    const oldSigma=`const sr=Math.hypot(Math.max(p.minRangeSigmaM,p.baseRangeSigmaM/q),p.glintFraction*maxRangeExt),sa=Math.hypot(Math.max(p.minAzSigmaDeg,p.baseAzSigmaDeg/q),glintAng),se=Math.hypot(Math.max(p.minElSigmaDeg,p.baseElSigmaDeg/q),glintAng),sd=Math.hypot(Math.max(p.minDopplerSigmaMps,p.baseDopplerSigmaMps/q),.35*maxDopExt);`;
    const newSigma=`const sr=Math.hypot(Math.max(p.minRangeSigmaM,p.baseRangeSigmaM/q),p.glintFraction*maxRangeExt),sa=angularNoiseSigmaRad/deg(1),se=angularNoiseSigmaRad/deg(1),sd=Math.hypot(Math.max(p.minDopplerSigmaMps,p.baseDopplerSigmaMps/q),.35*maxDopExt);`;
    if(after.split(oldSigma).length!==2)throw Error('SIGMA_SITE_NOT_UNIQUE');
    after=after.replace(oldSigma,newSigma);
  }
  return after;
}

module.exports={patchMeasurement};
