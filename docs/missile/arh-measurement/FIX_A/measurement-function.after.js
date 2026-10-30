function _arhV2MonopulseMeasurement(m,cluster,p=getSamArhProfile(m)){
    if(!cluster?.length)return null;
    const state=m._v1ArhState??'SEARCH',tracking=(state==='TRACK'||state==='ACQUIRE'||state==='REACQUIRE');
    const boresightAz=m.seekerAngle??m.heading??cluster[0].azRad,boresightEl=m.seekerEl??m.velPitch??cluster[0].elRad;
    const beam=Math.max(deg(1.2),deg(p.monopulseBeamWidthDeg??5.8)),squint=Math.max(deg(.2),deg(p.monopulseSquintDeg??1.65));
    const sigma2=2*beam*beam;let UL=0,UR=0,LL=0,LR=0,wr=0,wd=0,wTot=0,sumSnr=0,maxRangeExt=0,maxCrossExt=0,maxVertExt=0,maxDopExt=0;
    const response=(base,azErr,elErr,cx,cy)=>base*Math.exp(-(((azErr-cx)**2)+((elErr-cy)**2))/Math.max(1e-12,sigma2));
    for(const e of cluster){
      const azErr=angNorm((e.azRad??0)-boresightAz),elErr=(e.elRad??0)-boresightEl,base=Math.max(1e-18,e.baseReceivedPowerNorm??e.receivedPowerNorm??0);
      UL+=response(base,azErr,elErr,-squint,+squint);UR+=response(base,azErr,elErr,+squint,+squint);LL+=response(base,azErr,elErr,-squint,-squint);LR+=response(base,azErr,elErr,+squint,-squint);
      const w=Math.max(1e-18,e.receivedPowerNorm??base);wTot+=w;wr+=w*(e.rangeM??0);wd+=w*(e.dopplerPathRateMps??0);sumSnr+=Math.max(0,e.snr??0);
      maxRangeExt=Math.max(maxRangeExt,e.rangeExtentM??0);maxCrossExt=Math.max(maxCrossExt,e.crossExtentM??0);maxVertExt=Math.max(maxVertExt,e.verticalExtentM??0);maxDopExt=Math.max(maxDopExt,e.dopplerSpreadMps??0);
    }
    const sum=Math.max(1e-18,UL+UR+LL+LR);if(!(wTot>0)||!(sumSnr>0))return null;
    const dwell=tracking?p.trackDwellGain:p.searchDwellGain,pd=clamp(1-Math.exp(-sumSnr*dwell),.001,.999);if(_arhSeekerRandom(m)>pd)return null;
    const dAz=((UR+LR)-(UL+LL))/sum,dEl=((UL+UR)-(LL+LR))/sum,gate=deg(p.monopulseAngleGateDeg??4.8);
    // For the Gaussian four-quadrant response above, delta/sigma = tanh(error*squint/beam^2).
    // Invert that response so the generated measurement and the EKF absolute-angle model share units/meaning.
    const ratioLimit=1-1e-12,monopulseInverseScale=beam*beam/Math.max(deg(.2),squint);
    let azErr=clamp(Math.atanh(clamp(dAz,-ratioLimit,ratioLimit))*monopulseInverseScale,-gate,gate),elErr=clamp(Math.atanh(clamp(dEl,-ratioLimit,ratioLimit))*monopulseInverseScale,-gate,gate);
    const spreadSeed=clamp(.45*clamp(maxRangeExt/300,0,1)+.35*clamp(maxDopExt/72,0,1)+.20*clamp(Math.atan2(Math.max(maxCrossExt,maxVertExt),Math.max(1,wr/wTot))/deg(8),0,1),0,1);
    const snrQ=clamp(sum/Math.max(1e-9,p.monopulseSumMin??.058),0,12),noiseBase=deg(p.monopulseNoiseDeg??.10)/Math.sqrt(.35+snrQ),glint=deg(lerp(p.monopulseGlintDeg??.16,p.monopulseChaffGlintDeg??.74,spreadSeed));
    // This is the conditional standard deviation actually used by both angular draws.
    // Report the same quantity downstream; do not apply a fitted global multiplier.
    const angularNoiseSigmaRad=noiseBase+glint*lerp(.45,1.15,spreadSeed);
    azErr+=_arhSeekerRandn(m)*angularNoiseSigmaRad;elErr+=_arhSeekerRandn(m)*angularNoiseSigmaRad;
    const range0=wr/wTot,dop0=wd/wTot,q=Math.max(.28,Math.sqrt(clamp(sumSnr,.08,100))),h=Math.max(1,range0*Math.cos(boresightEl)),glintAng=180/Math.PI*Math.atan2(p.glintFraction*Math.max(maxCrossExt,maxVertExt),h);
    const sr=Math.hypot(Math.max(p.minRangeSigmaM,p.baseRangeSigmaM/q),p.glintFraction*maxRangeExt),sa=angularNoiseSigmaRad/deg(1),se=angularNoiseSigmaRad/deg(1),sd=Math.hypot(Math.max(p.minDopplerSigmaMps,p.baseDopplerSigmaMps/q),.35*maxDopExt);
    return {rangeM:Math.max(1,range0+_arhSeekerRandn(m)*sr),azRad:angNorm(boresightAz+azErr),elRad:clamp(boresightEl+elErr,-deg(89),deg(89)),dopplerPathRateMps:dop0+_arhSeekerRandn(m)*sd,
      rangeSigmaM:sr,azSigmaDeg:sa,elSigmaDeg:se,dopplerSigmaMps:sd,snr:sumSnr,pd,sigmaChannel:sum,deltaAzChannel:(UR+LR)-(UL+LL),deltaElChannel:(UL+UR)-(LL+LR),deltaAzOverSigma:dAz,deltaElOverSigma:dEl,memberCount:cluster.length,echoIds:cluster.map(e=>e.echoId),quadrants:{UL,UR,LL,LR},monopulseModel:'4Q_RF_V2'};
  }
