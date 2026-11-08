// ESM_A Commit B — anonymous passive-RF measurement and honest local likelihood.
// RF detection, beam, LOS, weather and the owner EW RNG remain in the native
// electronicReceiverPlotsF path. This layer starts only after a native hit.
const ESM_A_RAW_SCHEMA='AEGIS_ESM_RAW_A_1';
const ESM_A_STATE_SCHEMA='AEGIS_ESM_RUNTIME_A_1';
const ESM_A_ESTIMATE_STATES=Object.freeze(['BEARING_ONLY','LIKELIHOOD_REGION','GEOLOCATED_ESTIMATE','COAST','LOST']);
const ESM_A_SPEC=Object.freeze({
  schema:'AEGIS_ESM_SPEC_A_1',historyMax:24,rangeHypothesisMinM:500,rangeHypothesisMaxM:200000,
  originBaselineMinM:500,crossingAngleMinDeg:12,geolocateMajor95MaxM:4000,coastAfterS:1,
  clockBiasSigmaS:2e-7,clockDriftSigmaSps:2e-9,arrivalTimeSigmaS:6e-8,
  frequencyReferenceSigmaHz:2,frequencyMeasurementSigmaHz:4,sourceMotionNuisanceSigmaMps:25,
  fingerprintGateNis:9,associationAmbiguityDeltaNis:1,rawPairWindowS:.21,performanceBudgetMs:2,
  speedOfLightMps:299792458,provenance:'SIM_TUNED_PREDECLARED_IN_PLAN_MD'
});
const ESM_A_REQUIRE_PROFILE=__ESM_A_REQUIRE_PROFILE__;
const ESM_A_RAW_KEYS=Object.freeze(['schema','revision','observationId','measuredAtS','receivedAtS','receiver','bearingRad','elevationRad','angleCovarianceRad2','frequencyHz','frequencySigmaHz','arrivalTimeS','arrivalTimeSigmaS','fingerprint','snr','quality','band','emitterClass','type','sourceTag']);
const ESM_A_RECEIVER_KEYS=Object.freeze(['platformId','receiverId','positionM','velocityMps','attitudeRad','positionCovarianceM2','velocityCovarianceM2ps2','attitudeCovarianceRad2','clockBiasS','clockBiasSigmaS','clockDriftSps','clockDriftSigmaSps','frequencyReferenceErrorHz','frequencyReferenceSigmaHz']);
const ESM_A_FINGERPRINT_KEYS=Object.freeze(['priS','priSigmaS','pulseWidthS','pulseWidthSigmaS','scanPeriodS','scanPeriodSigmaS','confidence']);
const ESM_A_AUDIT={accepted:0,rejected:0,created:0,associated:0,ambiguous:0,expired:0,truthFieldRejects:0,networkAccepted:0,networkRejected:0};

function esmKeysExactA(q,keys){return !!q&&typeof q==='object'&&!Array.isArray(q)&&Object.keys(q).sort().join('|')===keys.slice().sort().join('|');}
function esmVecExactA(q,keys){return esmKeysExactA(q,keys)&&keys.every(k=>Number.isFinite(q[k]));}
function esmFiniteOrNullA(q){return q===null||Number.isFinite(q);}
function esmSpdA(a,n){
  if(!Array.isArray(a)||a.length!==n*n||!a.every(Number.isFinite))return false;const L=new Array(n*n).fill(0);
  for(let i=0;i<n;i++)for(let j=0;j<=i;j++){
    if(Math.abs(a[i*n+j]-a[j*n+i])>1e-7*Math.max(1,Math.abs(a[i*n+j]),Math.abs(a[j*n+i])))return false;
    let s=a[i*n+j];for(let k=0;k<j;k++)s-=L[i*n+k]*L[j*n+k];
    if(i===j){if(!(s>1e-14))return false;L[i*n+j]=Math.sqrt(s);}else L[i*n+j]=s/L[j*n+j];
  }return true;
}
function esmJsonA(q){return JSON.parse(JSON.stringify(q));}
function esmHashA(text){let h=2166136261>>>0;for(const c of String(text)){h^=c.charCodeAt(0);h=Math.imul(h,16777619)>>>0;}return h>>>0;}
function esmUnitNoiseA(text){const a=(esmHashA(text)+.5)/4294967296,b=(esmHashA(text+'#')+.5)/4294967296;return Math.sqrt(-2*Math.log(Math.max(1e-12,a)))*Math.cos(TAU*b);}
function esmReceiverClockA(r){
  const state=prepareEsmA(r);if(state.clock)return state.clock;const key='ESM_A_CLOCK:'+BATTLESPACE_SEED+':'+r.entityId;
  return state.clock={biasS:esmUnitNoiseA(key)*ESM_A_SPEC.clockBiasSigmaS*.45,driftSps:esmUnitNoiseA(key+':D')*ESM_A_SPEC.clockDriftSigmaSps*.45,frequencyReferenceErrorHz:esmUnitNoiseA(key+':F')*ESM_A_SPEC.frequencyReferenceSigmaHz*.45,epochS:simStepCounter*SIM_FIXED_DT};
}
function esmReceiverProfileA(r){
  if(!r||sovHullA(r)||sovNoEquipmentA(r))return null;const declared=resolveShipProfile(r.profileId)?.equipment?.esmReceiver??null;
  if(declared)return declared;if(ESM_A_REQUIRE_PROFILE)return null;
  return Object.freeze({schema:'AEGIS_ESM_RECEIVER_PROFILE_A_1',profileId:r.profileId,receiverId:'LEGACY_COMMON_ESM_RECEIVER',capabilities:Object.freeze(['PASSIVE_ESM_RECEIVE','AOA','FREQUENCY','TIME','FINGERPRINT']),installed:true,enabled:true,provenance:'COMMIT_B_LEGACY_ADAPTER_REMOVED_BY_COMMIT_E'});
}
function esmReceiverOperationalA(r){
  const profile=esmReceiverProfileA(r);if(!profile||profile.installed!==true||profile.enabled===false||r.ew?.esmReceiverDisabledA===true||shipEquipmentOfflineV1(r))return {ok:false,reason:'RECEIVER_UNAVAILABLE',profile};
  const health=clamp(1-shipSystemDamageB(r,'CDC')/100,0,1);return health>.01?{ok:true,profile,health}:{ok:false,reason:'RECEIVER_DAMAGED',profile};
}
function prepareEsmA(r){
  if(r.ew.esmA)return r.ew.esmA;const restored=r.restoredEsmA??null;delete r.restoredEsmA;
  const q={schema:ESM_A_STATE_SCHEMA,revision:1,rawSerial:1,networkSequence:0,clock:null,outbox:[],networkQueue:[],networkSeen:new Map(),lastNetworkSendStep:-1,stats:{localAccepted:0,remoteAccepted:0,rejected:0,duplicates:0}};
  r.ew.esmA=q;claimShipMutableRootA(r,'esmA',q);if(restored)esmRestoreStateA(r,restored);return r.ew.esmA;
}
function esmReceiverSnapshotA(r,point,profile){
  const now=simStepCounter*SIM_FIXED_DT,clock=esmReceiverClockA(r),nav=r.navigation,pose=r.survival?.snapshot?.()??{heelRad:0,trimRad:0};
  return {platformId:String(r.entityId),receiverId:String(profile.receiverId),positionM:{x:worldToMeters(point.x),y:worldToMeters(point.y),z:Number(point.z)},velocityMps:{x:worldSpeedToMps(nav.vx??0),y:worldSpeedToMps(nav.vy??0),z:0},attitudeRad:{yaw:Number(nav.heading)||0,pitch:Number(pose.trimRad)||0,roll:Number(pose.heelRad)||0},positionCovarianceM2:[9,0,0,0,9,0,0,0,4],velocityCovarianceM2ps2:[.25,0,0,0,.25,0,0,0,.09],attitudeCovarianceRad2:[deg(.15)**2,0,0,0,deg(.15)**2,0,0,0,deg(.2)**2],clockBiasS:clock.biasS+clock.driftSps*(now-clock.epochS),clockBiasSigmaS:ESM_A_SPEC.clockBiasSigmaS,clockDriftSps:clock.driftSps,clockDriftSigmaSps:ESM_A_SPEC.clockDriftSigmaSps,frequencyReferenceErrorHz:clock.frequencyReferenceErrorHz,frequencyReferenceSigmaHz:ESM_A_SPEC.frequencyReferenceSigmaHz};
}
function esmCreateRawA(r,source,rx,az,el,sigmaDeg,snr,quality,rangeM,profile){
  const e=prepareEsmA(r),serial=e.rawSerial++,now=simStepCounter*SIM_FIXED_DT,receiver=esmReceiverSnapshotA(r,rx,profile),key=receiver.platformId+':'+serial+':'+simStepCounter+':'+source.band+':'+source.emitterClass+':'+az;
  const arrivalNoise=esmUnitNoiseA(key+':T')*ESM_A_SPEC.arrivalTimeSigmaS,baseHz=Number.isFinite(source.frequencyMHz)?source.frequencyMHz*1e6:null,u={x:Math.cos(az)*Math.cos(el),y:Math.sin(az)*Math.cos(el),z:Math.sin(el)},closing=receiver.velocityMps.x*u.x+receiver.velocityMps.y*u.y+receiver.velocityMps.z*u.z;
  const frequencyHz=baseHz==null?null:baseHz*(1+closing/ESM_A_SPEC.speedOfLightMps)+receiver.frequencyReferenceErrorHz+esmUnitNoiseA(key+':F')*ESM_A_SPEC.frequencyMeasurementSigmaHz;
  const scanPeriodS=Number.isFinite(source.rpm)&&source.rpm>0?60/source.rpm:null,scanSigma=scanPeriodS==null?null:Math.max(.002,scanPeriodS*.03),sigmaRad=deg(sigmaDeg);
  return {schema:ESM_A_RAW_SCHEMA,revision:1,observationId:receiver.platformId+':'+serial,measuredAtS:now,receivedAtS:now,receiver,bearingRad:az,elevationRad:el,angleCovarianceRad2:[sigmaRad*sigmaRad,0,0,Math.max(deg(.8)**2,sigmaRad*sigmaRad*2.25)],frequencyHz,frequencySigmaHz:frequencyHz==null?null:Math.hypot(ESM_A_SPEC.frequencyMeasurementSigmaHz,receiver.frequencyReferenceSigmaHz),arrivalTimeS:now+rangeM/ESM_A_SPEC.speedOfLightMps+receiver.clockBiasS+arrivalNoise,arrivalTimeSigmaS:ESM_A_SPEC.arrivalTimeSigmaS,fingerprint:{priS:null,priSigmaS:null,pulseWidthS:null,pulseWidthSigmaS:null,scanPeriodS,scanPeriodSigmaS:scanSigma,confidence:scanPeriodS==null?.25:.72},snr,quality,band:source.band,emitterClass:source.emitterClass,type:source.family,sourceTag:'PASSIVE_RF_ESM_A'};
}
function esmValidateRawA(q,now=simStepCounter*SIM_FIXED_DT,expectedPlatform=null){
  const fail=reason=>({ok:false,reason});if(!esmKeysExactA(q,ESM_A_RAW_KEYS))return fail('RAW_FIELDS');
  if(q.schema!==ESM_A_RAW_SCHEMA||q.revision!==1||typeof q.observationId!=='string'||!q.observationId||q.observationId.length>120)return fail('RAW_SCHEMA');
  if(!Number.isFinite(q.measuredAtS)||!Number.isFinite(q.receivedAtS)||q.measuredAtS<0||q.receivedAtS<q.measuredAtS-1e-8||q.receivedAtS>now+1e-8||q.measuredAtS>now+1e-8)return fail('RAW_TIME');
  const r=q.receiver;if(!esmKeysExactA(r,ESM_A_RECEIVER_KEYS)||typeof r.platformId!=='string'||!r.platformId||typeof r.receiverId!=='string'||!r.receiverId||expectedPlatform!=null&&r.platformId!==String(expectedPlatform))return fail('RECEIVER_ID');
  if(!esmVecExactA(r.positionM,['x','y','z'])||!esmVecExactA(r.velocityMps,['x','y','z'])||!esmVecExactA(r.attitudeRad,['yaw','pitch','roll']))return fail('RECEIVER_STATE');
  if(!esmSpdA(r.positionCovarianceM2,3)||!esmSpdA(r.velocityCovarianceM2ps2,3)||!esmSpdA(r.attitudeCovarianceRad2,3))return fail('RECEIVER_COVARIANCE');
  if(![r.clockBiasS,r.clockBiasSigmaS,r.clockDriftSps,r.clockDriftSigmaSps,r.frequencyReferenceErrorHz,r.frequencyReferenceSigmaHz].every(Number.isFinite)||r.clockBiasSigmaS<=0||r.clockDriftSigmaSps<=0||r.frequencyReferenceSigmaHz<=0)return fail('REFERENCE_STATE');
  if(!Number.isFinite(q.bearingRad)||Math.abs(q.bearingRad)>TAU||!Number.isFinite(q.elevationRad)||Math.abs(q.elevationRad)>Math.PI/2||!esmSpdA(q.angleCovarianceRad2,2))return fail('ANGLE');
  if(!esmFiniteOrNullA(q.frequencyHz)||!esmFiniteOrNullA(q.frequencySigmaHz)||q.frequencyHz!=null&&(q.frequencyHz<=0||!(q.frequencySigmaHz>0))||q.frequencyHz==null&&q.frequencySigmaHz!==null)return fail('FREQUENCY');
  if(!Number.isFinite(q.arrivalTimeS)||!Number.isFinite(q.arrivalTimeSigmaS)||q.arrivalTimeSigmaS<=0||Math.abs(q.arrivalTimeS-q.measuredAtS)>2)return fail('ARRIVAL_TIME');
  const f=q.fingerprint;if(!esmKeysExactA(f,ESM_A_FINGERPRINT_KEYS)||!['priS','priSigmaS','pulseWidthS','pulseWidthSigmaS','scanPeriodS','scanPeriodSigmaS'].every(k=>esmFiniteOrNullA(f[k]))||!Number.isFinite(f.confidence)||f.confidence<0||f.confidence>1)return fail('FINGERPRINT');
  for(const [value,sigma]of [[f.priS,f.priSigmaS],[f.pulseWidthS,f.pulseWidthSigmaS],[f.scanPeriodS,f.scanPeriodSigmaS]])if((value===null)!==(sigma===null)||value!==null&&(value<=0||sigma<=0))return fail('FINGERPRINT_PAIR');
  if(!Number.isFinite(q.snr)||q.snr<0||!Number.isFinite(q.quality)||q.quality<0||q.quality>1||!['S','IJ','X'].includes(q.band)||!['SEARCH_RADAR','ACTIVE_SEEKER','JAMMER'].includes(q.emitterClass)||typeof q.type!=='string'||!q.type||q.type.length>80||q.sourceTag!=='PASSIVE_RF_ESM_A')return fail('CLASSIFICATION');
  const forbidden=/truth|target|emitterid|entityid|object|faction|hostile|positiontruth/i,serialized=JSON.stringify(q);if(forbidden.test(Object.keys(q).concat(Object.keys(r),Object.keys(f)).join('|'))||/truthRef|targetId|emitterId|entityId|faction|hostile/i.test(serialized)){ESM_A_AUDIT.truthFieldRejects++;return fail('TRUTH_FIELD');}
  return {ok:true};
}
function esmFingerprintScoreA(a,b){
  if(a.band!==b.band||a.emitterClass!==b.emitterClass||a.emitterClass!=='ACTIVE_SEEKER'&&a.type!==b.type)return Infinity;let score=0,terms=0;
  if(a.frequencyHz!=null&&b.frequencyHz!=null){const corrected=q=>{const u={x:Math.cos(q.bearingRad)*Math.cos(q.elevationRad),y:Math.sin(q.bearingRad)*Math.cos(q.elevationRad),z:Math.sin(q.elevationRad)},v=q.receiver.velocityMps,doppler=1+(v.x*u.x+v.y*u.y+v.z*u.z)/ESM_A_SPEC.speedOfLightMps;return (q.frequencyHz-q.receiver.frequencyReferenceErrorHz)/doppler;},fa=corrected(a),fb=corrected(b),nuisance=Math.max(fa,fb)*ESM_A_SPEC.sourceMotionNuisanceSigmaMps/ESM_A_SPEC.speedOfLightMps,sigma2=a.frequencySigmaHz**2+b.frequencySigmaHz**2+nuisance*nuisance;score+=(fa-fb)**2/Math.max(1e-12,sigma2);terms++;}
  for(const [value,sigma]of [['scanPeriodS','scanPeriodSigmaS'],['priS','priSigmaS'],['pulseWidthS','pulseWidthSigmaS']]){const x=a.fingerprint?.[value],y=b.fingerprint?.[value];if(x!=null&&y!=null){score+=(x-y)**2/Math.max(1e-18,a.fingerprint[sigma]**2+b.fingerprint[sigma]**2);terms++;}}
  if(!terms)return a.type===b.type&&a.emitterClass===b.emitterClass?1:Infinity;return score;
}
function esmObservationCandidateScoreA(c,q){
  const p=c.history?.at(-1);if(!p)return Infinity;let score=esmFingerprintScoreA(p,q);if(!Number.isFinite(score)||score>ESM_A_SPEC.fingerprintGateNis)return Infinity;
  if(p.receiver.platformId===q.receiver.platformId){
    // A moving receiver can legitimately see a large bearing change. Accept
    // that change only when the two anonymous bearing rays intersect forward
    // of both historical origins and inside the declared hypothesis range.
    const baseline=esmOriginDistanceA(p,q),cross=baseline>=ESM_A_SPEC.originBaselineMinM?esmAoaSolveA([p,q]):null,point=cross?.point,
      forward=point&&[p,q].every(v=>(point.x-v.receiver.positionM.x)*Math.cos(v.bearingRad)+(point.y-v.receiver.positionM.y)*Math.sin(v.bearingRad)>0),
      bounded=point&&[p,q].every(v=>{const d=Math.hypot(point.x-v.receiver.positionM.x,point.y-v.receiver.positionM.y);return d>=ESM_A_SPEC.rangeHypothesisMinM&&d<=ESM_A_SPEC.rangeHypothesisMaxM;});
    if(!forward||!bounded){const variance=p.angleCovarianceRad2[0]+q.angleCovarianceRad2[0],d=angNorm(q.bearingRad-p.bearingRad);score+=d*d/Math.max(1e-12,variance);}
  }
  return score;
}
function esmSolve2A(a,b,c,d,e,f){const det=a*d-b*c;if(Math.abs(det)<1e-16)return null;return {x:(e*d-b*f)/det,y:(a*f-e*c)/det,det};}
function esmOriginDistanceA(a,b){return Math.hypot(a.receiver.positionM.x-b.receiver.positionM.x,a.receiver.positionM.y-b.receiver.positionM.y);}
function esmMaxCrossingA(rows){let best=0;for(let i=0;i<rows.length;i++)for(let j=i+1;j<rows.length;j++)best=Math.max(best,Math.abs(Math.sin(angNorm(rows[i].bearingRad-rows[j].bearingRad))));return Math.asin(clamp(best,0,1));}
function esmAoaSolveA(rows){
  const useful=rows.filter(q=>Math.sqrt(q.angleCovarianceRad2[0])<deg(45));if(useful.length<2)return null;let A=0,B=0,D=0,E=0,F=0;
  for(const q of useful){const n={x:-Math.sin(q.bearingRad),y:Math.cos(q.bearingRad)},o=q.receiver.positionM,w=1/Math.max(1e-8,q.angleCovarianceRad2[0]);A+=w*n.x*n.x;B+=w*n.x*n.y;D+=w*n.y*n.y;const h=n.x*o.x+n.y*o.y;E+=w*n.x*h;F+=w*n.y*h;}
  let point=esmSolve2A(A,B,B,D,E,F);if(!point)return null;
  // Reweight angular residuals in metres at the candidate range.
  A=B=D=E=F=0;for(const q of useful){const n={x:-Math.sin(q.bearingRad),y:Math.cos(q.bearingRad)},o=q.receiver.positionM,range=Math.max(ESM_A_SPEC.rangeHypothesisMinM,Math.hypot(point.x-o.x,point.y-o.y)),sigma2=range*range*q.angleCovarianceRad2[0]+Math.max(q.receiver.positionCovarianceM2[0],q.receiver.positionCovarianceM2[4]),w=1/Math.max(1,sigma2),h=n.x*o.x+n.y*o.y;A+=w*n.x*n.x;B+=w*n.x*n.y;D+=w*n.y*n.y;E+=w*n.x*h;F+=w*n.y*h;}
  point=esmSolve2A(A,B,B,D,E,F);if(!point)return null;const inv=esmSolve2A(A,B,B,D,1,0),inv2=esmSolve2A(A,B,B,D,0,1);if(!inv||!inv2)return null;
  return {point:{x:point.x,y:point.y},covarianceM2:[inv.x,inv2.x,inv.y,inv2.y],information:{a:A,b:B,d:D}};
}
function esmEllipseA(cov){const a=cov[0],b=(cov[1]+cov[2])*.5,d=cov[3],root=Math.hypot(a-d,2*b),l1=Math.max(1e-9,(a+d+root)/2),l2=Math.max(1e-9,(a+d-root)/2),scale=Math.sqrt(5.991);return {major95M:Math.sqrt(l1)*scale,minor95M:Math.sqrt(l2)*scale,angleRad:.5*Math.atan2(2*b,a-d)};}
function esmPairConstraintsA(rows){
  const pairs=[];for(let i=0;i<rows.length;i++)for(let j=i+1;j<rows.length;j++){const a=rows[i],b=rows[j];if(a.receiver.platformId===b.receiver.platformId||Math.abs(a.measuredAtS-b.measuredAtS)>ESM_A_SPEC.rawPairWindowS)continue;
    const ta=a.arrivalTimeS-a.receiver.clockBiasS,tb=b.arrivalTimeS-b.receiver.clockBiasS,dt=tb-ta,sigmaT=Math.hypot(a.arrivalTimeSigmaS,b.arrivalTimeSigmaS,a.receiver.clockBiasSigmaS,b.receiver.clockBiasSigmaS,Math.abs(dt)*a.receiver.clockDriftSigmaSps,Math.abs(dt)*b.receiver.clockDriftSigmaSps);
    const tdoa={a,b,deltaRangeM:dt*ESM_A_SPEC.speedOfLightMps,sigmaM:sigmaT*ESM_A_SPEC.speedOfLightMps};if(tdoa.sigmaM>ESM_A_SPEC.geolocateMajor95MaxM)continue;let fdoa=null;
    if(a.frequencyHz!=null&&b.frequencyHz!=null){const fa=a.frequencyHz-a.receiver.frequencyReferenceErrorHz,fb=b.frequencyHz-b.receiver.frequencyReferenceErrorHz,sigmaHz=Math.hypot(a.frequencySigmaHz,b.frequencySigmaHz,a.receiver.frequencyReferenceSigmaHz,b.receiver.frequencyReferenceSigmaHz),carrier=(fa+fb)/2,combined=Math.hypot(sigmaHz,carrier*ESM_A_SPEC.sourceMotionNuisanceSigmaMps/ESM_A_SPEC.speedOfLightMps);if(combined*ESM_A_SPEC.speedOfLightMps/carrier<=ESM_A_SPEC.sourceMotionNuisanceSigmaMps*4)fdoa={a,b,deltaHz:fb-fa,sigmaHz:combined,carrierHz:carrier};}
    pairs.push({tdoa,fdoa});
  }return pairs;
}
function esmConstraintResidualsA(point,pairs,useFdoa=true){
  const out=[];for(const pair of pairs){const {a,b,deltaRangeM,sigmaM}=pair.tdoa,oa=a.receiver.positionM,ob=b.receiver.positionM,ra=Math.max(1,Math.hypot(point.x-oa.x,point.y-oa.y)),rb=Math.max(1,Math.hypot(point.x-ob.x,point.y-ob.y));out.push({kind:'TDOA',r:(rb-ra-deltaRangeM)/Math.max(1,sigmaM)});
    const f=pair.fdoa;if(useFdoa&&f){const ua={x:(point.x-oa.x)/ra,y:(point.y-oa.y)/ra},ub={x:(point.x-ob.x)/rb,y:(point.y-ob.y)/rb},va=a.receiver.velocityMps,vb=b.receiver.velocityMps,pred=f.carrierHz*((vb.x*ub.x+vb.y*ub.y)-(va.x*ua.x+va.y*ua.y))/ESM_A_SPEC.speedOfLightMps;out.push({kind:'FDOA',r:(f.deltaHz-pred)/Math.max(.1,f.sigmaHz)});}
  }return out;
}
function esmRefineConstraintsA(seed,pairs){
  if(!seed||!pairs.length)return {point:seed,used:[],covarianceM2:null};let p={...seed},used=[],hessian=null;
  for(let iter=0;iter<8;iter++){let a=0,b=0,d=0,e=0,f=0;const base=esmConstraintResidualsA(p,pairs),eps=10;used=[...new Set(base.map(q=>q.kind))];for(let i=0;i<base.length;i++){const rx=esmConstraintResidualsA({x:p.x+eps,y:p.y},pairs)[i].r,ry=esmConstraintResidualsA({x:p.x,y:p.y+eps},pairs)[i].r,gx=(rx-base[i].r)/eps,gy=(ry-base[i].r)/eps;a+=gx*gx;b+=gx*gy;d+=gy*gy;e-=gx*base[i].r;f-=gy*base[i].r;}hessian={a,b,d};const step=esmSolve2A(a,b,b,d,e,f);if(!step)break;const mag=Math.hypot(step.x,step.y),scale=Math.min(1,20000/Math.max(1,mag));p.x+=step.x*scale;p.y+=step.y*scale;if(mag<.1)break;}let covarianceM2=null;if(hessian){const x=esmSolve2A(hessian.a,hessian.b,hessian.b,hessian.d,1,0),y=esmSolve2A(hessian.a,hessian.b,hessian.b,hessian.d,0,1);if(x&&y)covarianceM2=[x.x,y.x,x.y,y.y];}return {point:p,used,covarianceM2};
}
function esmTdoaSeedA(rows,pairs){
  const receivers=[...new Map(rows.map(q=>[q.receiver.platformId,q.receiver.positionM])).values()];if(receivers.length<3||pairs.length<2)return null;const cx=receivers.reduce((s,q)=>s+q.x,0)/receivers.length,cy=receivers.reduce((s,q)=>s+q.y,0)/receivers.length;
  let best=null;for(const radius of [ESM_A_SPEC.rangeHypothesisMinM,2000,5000,10000,20000,40000,80000,120000,ESM_A_SPEC.rangeHypothesisMaxM])for(let i=0;i<72;i++){const a=i*TAU/72,p={x:cx+Math.cos(a)*radius,y:cy+Math.sin(a)*radius},cost=esmConstraintResidualsA(p,pairs,false).reduce((s,q)=>s+q.r*q.r,0);if(!best||cost<best.cost)best={...p,cost};}return best&&{x:best.x,y:best.y};
}
function esmEstimateHistoryA(history,now=simStepCounter*SIM_FIXED_DT){
  const rows=history.slice(-ESM_A_SPEC.historyMax).sort((a,b)=>a.measuredAtS-b.measuredAtS||a.observationId.localeCompare(b.observationId)),latest=rows.at(-1);if(!latest)return {state:'LOST',measuredAtS:null,ageS:Infinity,methods:[],sourceCount:0,modes:[]};
  const age=Math.max(0,now-latest.measuredAtS),origins=[...new Set(rows.map(q=>q.receiver.platformId+':'+Math.round(q.receiver.positionM.x)+':'+Math.round(q.receiver.positionM.y)))],baseline=rows.reduce((m,a,i)=>Math.max(m,...rows.slice(i+1).map(b=>esmOriginDistanceA(a,b))),0),cross=esmMaxCrossingA(rows),aoa=baseline>=ESM_A_SPEC.originBaselineMinM&&cross>=deg(ESM_A_SPEC.crossingAngleMinDeg)?esmAoaSolveA(rows):null,pairs=esmPairConstraintsA(rows);
  let solve=aoa,methods=aoa?['AOA']:[];
  if(aoa&&pairs.length){const refined=esmRefineConstraintsA(aoa.point,pairs);solve={...aoa,point:refined.point,covarianceM2:refined.covarianceM2??aoa.covarianceM2};methods.push(...refined.used);}
  else if(!aoa&&pairs.length){const seed=esmTdoaSeedA(rows,pairs),refined=esmRefineConstraintsA(seed,pairs);if(seed&&refined.covarianceM2)solve={point:refined.point,covarianceM2:refined.covarianceM2};methods.push(...refined.used);}
  const base={measuredAtS:latest.measuredAtS,ageS:age,methods:[...new Set(methods)],sourceCount:new Set(rows.map(q=>q.receiver.platformId)).size,baselineM:baseline,crossingAngleDeg:rad2deg(cross),latestOriginM:{...latest.receiver.positionM},latestBearingRad:latest.bearingRad,historyCount:rows.length};
  if(!solve){const state=rows.length===1||baseline<ESM_A_SPEC.originBaselineMinM?'BEARING_ONLY':'LIKELIHOOD_REGION',mode={kind:'RAY',originM:{...latest.receiver.positionM},bearingRad:latest.bearingRad,sigmaRad:Math.sqrt(latest.angleCovarianceRad2[0]),minRangeM:ESM_A_SPEC.rangeHypothesisMinM,maxRangeM:ESM_A_SPEC.rangeHypothesisMaxM};return {...base,state:age>=ELECTRONIC_POLICY_F.holdS?'LOST':age>ESM_A_SPEC.coastAfterS?'COAST':state,modes:[mode],positionM:null,covarianceM2:null,ellipse95:null};}
  const forward=rows.every(q=>(solve.point.x-q.receiver.positionM.x)*Math.cos(q.bearingRad)+(solve.point.y-q.receiver.positionM.y)*Math.sin(q.bearingRad)>0),ellipse=esmEllipseA(solve.covarianceM2),bounded=Math.hypot(solve.point.x-latest.receiver.positionM.x,solve.point.y-latest.receiver.positionM.y)<=ESM_A_SPEC.rangeHypothesisMaxM,geolocated=forward&&bounded&&ellipse.major95M<=ESM_A_SPEC.geolocateMajor95MaxM;
  if(age>ESM_A_SPEC.coastAfterS){const growth=(age-ESM_A_SPEC.coastAfterS)*75,cov=[solve.covarianceM2[0]+growth*growth,solve.covarianceM2[1],solve.covarianceM2[2],solve.covarianceM2[3]+growth*growth],ce=esmEllipseA(cov);return {...base,state:age>=ELECTRONIC_POLICY_F.holdS?'LOST':'COAST',positionM:{x:solve.point.x,y:solve.point.y,z:0},covarianceM2:cov,ellipse95:ce,modes:[{kind:'ELLIPSE',centerM:{x:solve.point.x,y:solve.point.y},covarianceM2:cov,ellipse95:ce}]};}
  return {...base,state:geolocated?'GEOLOCATED_ESTIMATE':'LIKELIHOOD_REGION',positionM:{x:solve.point.x,y:solve.point.y,z:0},covarianceM2:solve.covarianceM2,ellipse95:ellipse,modes:[{kind:'ELLIPSE',centerM:{x:solve.point.x,y:solve.point.y},covarianceM2:solve.covarianceM2,ellipse95:ellipse}]};
}
function esmUpdateContactA(c,now=simStepCounter*SIM_FIXED_DT){c.estimate=esmEstimateHistoryA(c.history,now);c.state=c.estimate.state;c.rangeKm=c.estimate.positionM?Math.hypot(c.estimate.positionM.x-c.estimate.latestOriginM.x,c.estimate.positionM.y-c.estimate.latestOriginM.y)/1000:null;return c;}
function esmAcceptRawA(r,rows,origin='LOCAL'){
  const now=simStepCounter*SIM_FIXED_DT;if(!r||!Array.isArray(rows)||rows.length>ELECTRONIC_POLICY_F.maxContacts)return {ok:false,reason:'RAW_BATCH'};const validated=[];
  for(const q of rows){const v=esmValidateRawA(q,now,origin==='LOCAL'?r.entityId:null);if(!v.ok){ESM_A_AUDIT.rejected++;prepareEsmA(r).stats.rejected++;return {ok:false,reason:v.reason};}validated.push(esmJsonA(q));}
  const e=prepareElectronicF(r),state=prepareEsmA(r),used=new Set();
  for(const q of validated){
    if(state.networkSeen.has(q.observationId)){state.stats.duplicates++;continue;}if(origin!=='LOCAL')state.networkSeen.set(q.observationId,q.measuredAtS);
    const candidates=[];for(const [id,c]of e.contacts){if(used.has(id))continue;const score=esmObservationCandidateScoreA(c,q);if(score<=ESM_A_SPEC.fingerprintGateNis)candidates.push({id,c,score});}candidates.sort((a,b)=>a.score-b.score||a.id-b.id);
    let found=null;if(candidates.length===1||candidates.length>1&&candidates[1].score-candidates[0].score>ESM_A_SPEC.associationAmbiguityDeltaNis)found=candidates[0];else if(candidates.length>1)ESM_A_AUDIT.ambiguous++;
    if(!found){if(e.contacts.size>=ELECTRONIC_POLICY_F.maxContacts)continue;const id=600000000+e.serial++,c={contactId:id,bearing:q.bearingRad,bearingSigmaDeg:rad2deg(Math.sqrt(q.angleCovarianceRad2[0])),strength:q.quality,quality:q.quality,band:q.band,type:q.type,emitterClass:q.emitterClass,measuredAtS:q.measuredAtS,age:0,hits:1,rangeKm:null,identity:'UNKNOWN',threatLevel:q.emitterClass==='ACTIVE_SEEKER'?'HIGH':'LOW',source:'PASSIVE_RF_F',history:[q],state:'BEARING_ONLY',estimate:null,provenance:'ANONYMOUS_ESM_A'};esmUpdateContactA(c,now);e.contacts.set(id,c);used.add(id);ESM_A_AUDIT.created++;}
    else {const c=found.c;c.history.push(q);if(c.history.length>ESM_A_SPEC.historyMax)c.history.splice(0,c.history.length-ESM_A_SPEC.historyMax);c.bearing=angNorm(c.bearing+angNorm(q.bearingRad-c.bearing)*.45);Object.assign(c,{bearingSigmaDeg:rad2deg(Math.sqrt(q.angleCovarianceRad2[0])),strength:q.quality,quality:q.quality,type:q.type,measuredAtS:q.measuredAtS,age:0,hits:(c.hits??0)+1});esmUpdateContactA(c,now);used.add(found.id);ESM_A_AUDIT.associated++;}
    if(origin==='LOCAL'){state.outbox.push(q);if(state.outbox.length>ESM_A_SPEC.historyMax*4)state.outbox.splice(0,state.outbox.length-ESM_A_SPEC.historyMax*4);state.stats.localAccepted++;}else state.stats.remoteAccepted++;
    ESM_A_AUDIT.accepted++;delete e.contacts.get([...used].at(-1))?.truthRef;
  }return {ok:true,accepted:validated.length};
}
function electronicReceiverPlotsF(r,emitters){
  // PHYSICAL/SENSOR boundary: target ownership exists only long enough to reject self coupling.
  const e=prepareElectronicF(r),op=esmReceiverOperationalA(r);if(!op.ok)return [];const plots=[];
  for(const source of emitters){
    if(source.owner===r.entityId)continue;const receiverPod=electronicPodF(r,source.point);if(!receiverPod)continue;const rx=receiverPod.point,health=receiverPod.health,transmitterPod=source.ship?electronicPodF(source.ship,rx):null;if(source.ship&&!transmitterPod)continue;
    const point=transmitterPod?.point??source.point,dx=worldToMeters(point.x-rx.x),dy=worldToMeters(point.y-rx.y),dz=point.z-rx.z,range=Math.max(100,Math.hypot(dx,dy,dz)),los=terrainAwareRadarLOS(rx.x,rx.y,rx.z,point.x,point.y,point.z);if(los<=.005)continue;
    const az=Math.atan2(dy,dx),el=Math.atan2(dz,Math.hypot(dx,dy)),toward=angNorm(az+Math.PI),off=source.beamAz==null?0:Math.abs(angNorm(toward-source.beamAz)),gain=source.beamAz==null?1:source.emitterClass==='ACTIVE_SEEKER'?Math.max(.005,Math.exp(-((off/deg(25))**2))):source.double?Math.max(.015,Math.exp(-((Math.min(off,Math.abs(Math.PI-off))/deg(35))**2))):Math.max(.015,Math.exp(-((off/deg(35))**2)));
    const power=source.power*gain*(transmitterPod?.health??1)*.008*los*health*maritimeRfWeatherPathFactorWip13A3(source.band,range/1000)/(4*Math.PI*range*range),snr=power/ELECTRONIC_POLICY_F.esmReferenceNoiseW,pd=snr/(snr+1);if(observerRandomC(e.rng)>pd)continue;
    const quality=clamp(pd*health,.01,1),sigma=lerp(6,.6,quality),bearing=angNorm(az+observerNormalC(e.rng)*deg(sigma));plots.push(esmCreateRawA(r,source,rx,bearing,el,sigma,snr,quality,range,op.profile));
  }return plots;
}
function electronicAcceptPlotsF(r,plots){return esmAcceptRawA(r,plots,'LOCAL');}
function stepElectronicReceiversF(dt){
  const emitters=electronicPhysicalEmittersF(),now=simStepCounter*SIM_FIXED_DT;
  for(const r of electronicShipsF()){
    if(sovNoEquipmentA(r))continue;const e=prepareElectronicF(r),state=prepareEsmA(r);if(e.lastTick===simStepCounter)throw Error('EW_DOUBLE_TICK_F');e.lastTick=simStepCounter;e.ticks++;
    for(const [id,c]of e.contacts){c.age+=dt;esmUpdateContactA(c,now);if(c.age>ELECTRONIC_POLICY_F.holdS){c.state='LOST';e.contacts.delete(id);ESM_A_AUDIT.expired++;}}
    for(const [key,stamp]of state.networkSeen)if(now-stamp>ELECTRONIC_POLICY_F.holdS)state.networkSeen.delete(key);
    e.ageS+=dt;if(e.ageS+1e-9<ELECTRONIC_POLICY_F.revisitS)continue;e.ageS%=ELECTRONIC_POLICY_F.revisitS;const plots=electronicReceiverPlotsF(r,emitters);if(plots.length)electronicAcceptPlotsF(r,plots);e.receiver.lastAtS=now;
  }
}
function electronicCicTextF(){const e=prepareElectronicF(ACTIVE_SHIP_RUNTIME),fresh=[...e.contacts.values()].filter(c=>c.source==='PASSIVE_RF_F'),n=fresh.filter(c=>c.emitterClass==='JAMMER').length,g=fresh.filter(c=>c.state==='GEOLOCATED_ESTIMATE').length;return 'ESM '+fresh.length+' · 위치추정 '+g+' · RF 간섭 '+n;}
function esmContactViewA(c){return {contactId:c.contactId,state:c.state,ageS:c.age,bearingRad:c.bearing,bearingSigmaDeg:c.bearingSigmaDeg,band:c.band,type:c.type,emitterClass:c.emitterClass,quality:c.quality,hits:c.hits,historyCount:c.history?.length??0,estimate:esmJsonA(c.estimate),identity:'UNKNOWN',automaticEngagementAuthority:false};}
function esmSnapshotA(r=ACTIVE_SHIP_RUNTIME){const e=prepareElectronicF(r),s=prepareEsmA(r);return {schema:'AEGIS_ESM_SNAPSHOT_A_1',ownerEntityId:r.entityId,profileId:r.profileId,receiver:esmReceiverProfileA(r),operational:esmReceiverOperationalA(r).ok,contacts:[...e.contacts.values()].map(esmContactViewA),network:{queued:s.networkQueue.length,outbox:s.outbox.length},stats:{...s.stats},truthUsedByConsumer:false,observerTracksCreated:0,automaticEngagementAuthority:false};}
window.__ESM_A__=Object.freeze({schema:ESM_A_STATE_SCHEMA,spec:ESM_A_SPEC,states:ESM_A_ESTIMATE_STATES,snapshot:id=>esmSnapshotA(id?ENGAGEMENT_RUNTIME.ships.get(String(id)):ACTIVE_SHIP_RUNTIME),status:()=>({stage:'__ESM_A_STAGE__',release:false,audit:{...ESM_A_AUDIT}})});
