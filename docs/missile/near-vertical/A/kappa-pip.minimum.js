function _wip79KappaPipState(m,targetState){
    if(!targetState?.isValid)return null;
    const own=targetState.selfStateM??samNavB1OwnState(m),mPos=_samB1VecCopy(own.posM),mVel=_samB1VecCopy(own.velMps);
    const fallbackRaw=targetState.rangeM/Math.max(200,Math.hypot(mVel.x-targetState.velMps.x,mVel.y-targetState.velMps.y,mVel.z-targetState.velMps.z));
    const baseTgoRaw=Number.isFinite(m._wip81KappaTgoRawS)?m._wip81KappaTgoRawS:(Number.isFinite(m._tgoIter)?m._tgoIter:fallbackRaw);
    const tgoRaw=weaponLinkB3AdvisedTgo(m,targetState,baseTgoRaw);
    const tgo=_wip81KappaTgoLimit(tgoRaw);
    const _w86az=Number(m._wip86KappaAzEst?.estMps2)||0;
    const pip={x:targetState.posM.x+targetState.velMps.x*tgo,
               y:targetState.posM.y+targetState.velMps.y*tgo,
               // WIP86: observation-derived vertical acceleration only. Clamp to a physical prediction envelope.
               z:clamp(targetState.posM.z+targetState.velMps.z*tgo+.5*_w86az*tgo*tgo,0,60000)};
    const dx=pip.x-mPos.x,dy=pip.y-mPos.y,dz=pip.z-mPos.z,rgoM=Math.max(1,Math.hypot(dx,dy,dz));
    const speed=Math.max(80,Math.hypot(mVel.x,mVel.y,mVel.z));
    // Game terminal-vector heading follows the observed/estimated PIP LOS.
    // Do not automatically reverse a retreating/crossing target's heading.
    let hx=dx,hy=dy;
    let hm=Math.max(1,Math.hypot(hx,hy));
    hx/=hm;hy/=hm;
    let gammaF=0;
    const policy=String(m._wip79KappaTerminalPolicy??window.WIP79_KAPPA_TERMINAL_POLICY??'PIP_LOS');
    if(policy==='PIP_LOS')gammaF=Math.atan2(dz,Math.max(1,Math.hypot(dx,dy)));
    else if(policy==='TARGET_GAMMA_OPPOSE_H'){
      gammaF=Math.atan2(-targetState.velMps.z,Math.max(1,Math.hypot(targetState.velMps.x,targetState.velMps.y)));
    }
    const c=Math.cos(gammaF);
    const vFinal={x:speed*c*hx,y:speed*c*hy,z:speed*Math.sin(gammaF)};
    return loftB4ShapeWaypoint(m,targetState,{tgo,tgoRaw,mPos,mVel,pip,rgoM,speed,vFinal,gammaF,policy});
  }
