// NEAR_VERTICAL_PATH_FIX_A: remove the policy-only ±60 degree path-angle wall.
// The optional numerical-stability step is kept separate so its contribution
// can be measured against the one-line policy change.
function patchKappaPipState(before,{stability=false}={}){
  const clampLine='    gammaF=clamp(gammaF,deg(-60),deg(60));\n';
  if(before.split(clampLine).length!==2)throw Error('PATH_ANGLE_CLAMP_SITE_NOT_UNIQUE');
  let after=before.replace(clampLine,'');
  if(stability){
    const old=`    let hx=dx,hy=dy;
    let hm=Math.max(1,Math.hypot(hx,hy));
    hx/=hm;hy/=hm;
    let gammaF=0;`;
    const replacement=`    const horizontalRangeM=Math.hypot(dx,dy);
    let hx=dx,hy=dy;
    if(horizontalRangeM>1e-9){hx/=horizontalRangeM;hy/=horizontalRangeM;}
    else{
      // A vertical or coincident PIP has no LOS azimuth. Preserve the current
      // horizontal heading when available; otherwise use a deterministic axis.
      const ownHorizontalSpeedMps=Math.hypot(mVel.x,mVel.y);
      if(ownHorizontalSpeedMps>1e-9){hx=mVel.x/ownHorizontalSpeedMps;hy=mVel.y/ownHorizontalSpeedMps;}
      else{hx=1;hy=0;}
    }
    let gammaF=0;`;
    if(after.split(old).length!==2)throw Error('HORIZONTAL_NORMALIZATION_SITE_NOT_UNIQUE');
    after=after.replace(old,replacement);
    const oldAngle="    if(policy==='PIP_LOS')gammaF=Math.atan2(dz,Math.max(1,Math.hypot(dx,dy)));";
    const newAngle="    if(policy==='PIP_LOS')gammaF=(horizontalRangeM>1e-9||Math.abs(dz)>1e-9)?Math.atan2(dz,horizontalRangeM):Math.atan2(mVel.z,Math.hypot(mVel.x,mVel.y));";
    if(after.split(oldAngle).length!==2)throw Error('PIP_LOS_ANGLE_SITE_NOT_UNIQUE');
    after=after.replace(oldAngle,newAngle);
  }
  return after;
}

module.exports={patchKappaPipState};
