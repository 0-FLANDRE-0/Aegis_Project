// DERIVED ONLY. One last association kernel per observed track.
// Neither Kalman correction nor release authority consumes these cached values.
const trackRadarAssociationCachePerfC=new WeakMap();
function trackRadarAssociationKernelPerfC(tr,meas,cache=trackRadarAssociationCachePerfC){
  const x=tr._kfX,P=tr._kfP;
  const ox=meas.sensorXWorld??aircraft.x(),oy=meas.sensorYWorld??aircraft.y(),oz=meas.sensorZM??OWN_ALT_M;
  const ovx=meas.sensorVxMps??worldSpeedToMps(aircraft._vx??0),ovy=meas.sensorVyMps??worldSpeedToMps(aircraft._vy??0),ovz=meas.sensorVzMps??0;
  const old=cache.get(tr);
  let same=!!old&&x.length===6&&P.length===36&&Object.is(old.ox,ox)&&Object.is(old.oy,oy)&&Object.is(old.oz,oz)&&Object.is(old.ovx,ovx)&&Object.is(old.ovy,ovy)&&Object.is(old.ovz,ovz);
  if(same)for(let i=0;i<6;i++)if(!Object.is(old.x[i],x[i])){same=false;break;}
  if(same)for(let i=0;i<36;i++)if(!Object.is(old.P[i],P[i])){same=false;break;}
  if(same)return old;
  const pr=trackRadarPrediction(tr,{sensorXWorld:ox,sensorYWorld:oy,sensorZM:oz,sensorVxMps:ovx,sensorVyMps:ovy,sensorVzMps:ovz});
  const H=trackEkfRadarJacobian(pr),Ht=_matTranspose(H,4,6),PHt=_matMul(P,6,6,Ht,4),projected=_matMul(H,4,6,PHt,4);
  const entry={x:Array.from(x),P:Array.from(P),ox,oy,oz,ovx,ovy,ovz,pr,projected,noise:null,Sinv:null};
  cache.set(tr,entry);return entry;
}
function trackRadarAssociationInversePerfC(entry,R,sr,sa,se,sv){
  const noise=entry.noise;
  if(noise&&Object.is(noise[0],sr)&&Object.is(noise[1],sa)&&Object.is(noise[2],se)&&Object.is(noise[3],sv))return entry.Sinv;
  // Same matrix operations and summation order as the canonical association.
  const Sinv=_matInv(_matAdd(entry.projected,R),4);
  entry.noise=[sr,sa,se,sv];entry.Sinv=Sinv;return Sinv;
}
function performanceCSelfTest(){
  const cache=new WeakMap(),checks={},owner=()=>({_kfX:new Float64Array([12000,7000,1500,-240,30,-10]),_kfP:new Float64Array(Array.from({length:36},(_,i)=>i%7===0?500:0))}),tr=owner(),meas={sensorXWorld:0,sensorYWorld:0,sensorZM:22,sensorVxMps:2,sensorVyMps:1,sensorVzMps:0};
  let entry=trackRadarAssociationKernelPerfC(tr,meas,cache);
  checks.sameInputsReuse=entry===trackRadarAssociationKernelPerfC(tr,meas,cache);
  checks.trackObjectsSeparate=entry!==trackRadarAssociationKernelPerfC(owner(),meas,cache);
  for(const [field,count]of [['_kfX',6],['_kfP',36]]){
    let all=true;for(let i=0;i<count;i++){tr[field][i]+=.125;const next=trackRadarAssociationKernelPerfC(tr,meas,cache);all=all&&next!==entry;entry=next;}
    checks[field==='_kfX'?'allStateValuesInvalidate':'allCovarianceValuesInvalidate']=all;
  }
  let origins=true;for(const key of ['sensorXWorld','sensorYWorld','sensorZM','sensorVxMps','sensorVyMps','sensorVzMps']){meas[key]+=.125;const next=trackRadarAssociationKernelPerfC(tr,meas,cache);origins=origins&&entry!==next;entry=next;}checks.allSensorValuesInvalidate=origins;
  const R=new Float64Array(16);R[0]=16;R[5]=.001;R[10]=.002;R[15]=9;
  const inv=trackRadarAssociationInversePerfC(entry,R,4,.01,.02,3);
  checks.noiseInputsReuse=inv===trackRadarAssociationInversePerfC(entry,R,4,.01,.02,3);
  checks.noiseChangeInvalidates=inv!==trackRadarAssociationInversePerfC(entry,R,5,.01,.02,3);
  checks.detachedInputs=entry.x!==tr._kfX&&entry.P!==tr._kfP;
  return {checks,pass:Object.values(checks).every(Boolean)};
}
